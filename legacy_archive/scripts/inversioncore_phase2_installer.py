import os

FILES = {}

# 1. BAGIMLILIKLAR (Faz 2)
FILES["requirements_phase2.txt"] = """litellm==1.51.2
valkey==6.0.2
cachetools==5.5.0
"""

# 2. CONFIG - SECRET YOK, PLACEHOLDER
FILES["config/secrets.py"] = '''# .env DOSYASINDAN YUKLENECEK - BURAYA GERCEK KEY YAZMA
import os
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_ENDPOINT = os.environ.get("DEEPSEEK_ENDPOINT", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
VALKEY_URL = os.environ.get("VALKEY_URL", "redis://localhost:6379")
CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", "86400"))  # 24 saat
'''

FILES["config/settings.py"] = '''from config.secrets import *
# Faz 1 ayarlari (korunuyor)
CACHE_ENABLED = True
LITELLM_TIMEOUT = 30
LITELLM_MAX_RETRIES = 3
MOTOR_VERSION = "v2.0"
ONTOLOGY_VERSION = "v1.0"
'''

# 3. CACHE ABSTRACTION LAYER (Valkey + Memory Fallback)
FILES["engine/cache/__init__.py"] = ""

FILES["engine/cache/deterministic_cache.py"] = '''"""
Deterministic Cache Layer
- Valkey (Redis fork) varsa onu kullanir (production)
- Yoksa cachetools TTLCache ile memory fallback (development)
- Her cache entry: (customer_id, problem_type, data_hash, motor_version, ontology_version)
"""
import hashlib
import json
import os
from functools import wraps
from typing import Any, Optional

try:
    import valkey
    VALKEY_AVAILABLE = True
except ImportError:
    VALKEY_AVAILABLE = False

from cachetools import TTLCache
import config.settings as settings


class DeterministicCache:
    def __init__(self, url: Optional[str] = None, ttl: int = 86400):
        self.ttl = ttl
        self.backend = None
        self.backend_type = "memory"
        
        if VALKEY_AVAILABLE:
            try:
                self.backend = valkey.from_url(url or settings.VALKEY_URL, decode_responses=True)
                self.backend.ping()
                self.backend_type = "valkey"
            except Exception:
                self.backend = TTLCache(maxsize=10000, ttl=ttl)
                self.backend_type = "memory"
        else:
            self.backend = TTLCache(maxsize=10000, ttl=ttl)
            self.backend_type = "memory"
    
    @staticmethod
    def make_key(prefix: str, data: Any) -> str:
        """Deterministik hash: sort_keys + sha256 + prefix"""
        serialized = json.dumps(data, sort_keys=True, default=str, ensure_ascii=False)
        digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:24]
        return f"ic:{prefix}:{settings.MOTOR_VERSION}:{settings.ONTOLOGY_VERSION}:{digest}"
    
    def get(self, key: str) -> Optional[dict]:
        if self.backend_type == "valkey":
            raw = self.backend.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        return self.backend.get(key)
    
    def set(self, key: str, value: dict) -> None:
        if self.backend_type == "valkey":
            self.backend.setex(key, self.ttl, json.dumps(value, default=str, ensure_ascii=False))
        else:
            self.backend[key] = value
    
    def stats(self) -> dict:
        return {
            "backend": self.backend_type,
            "ttl_seconds": self.ttl,
            "available": self.backend is not None
        }


# Singleton
_cache_instance: Optional[DeterministicCache] = None

def get_cache() -> DeterministicCache:
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = DeterministicCache()
    return _cache_instance


def cached(prefix: str):
    """Decorator: Fonksiyon cagrilarini deterministik cache'ler"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not settings.CACHE_ENABLED:
                return func(self, *args, **kwargs)
            
            cache = get_cache()
            key = cache.make_key(prefix, {"args": args, "kwargs": kwargs})
            
            hit = cache.get(key)
            if hit is not None:
                hit["_cache"] = "HIT"
                return hit
            
            result = func(self, *args, **kwargs)
            if isinstance(result, dict) and not result.get("error"):
                cache.set(key, result)
                result["_cache"] = "MISS"
            return result
        return wrapper
    return decorator
'''

# 4. COST LEDGER (SQLite tabanli maliyet takibi)
FILES["engine/cache/cost_ledger.py"] = '''"""
Cost Ledger - Her LLM cagrisinin maliyetini SQLite'a kaydeder
Token sayisi, USD maliyet, timestamp, motor, problem_tipi
"""
import sqlite3
import threading
import time
from pathlib import Path
from typing import Optional


class CostLedger:
    def __init__(self, db_path: str = "data/cost_ledger.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()
    
    def _init_db(self):
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS llm_calls (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        customer_id TEXT,
                        problem_type TEXT,
                        model TEXT,
                        prompt_tokens INTEGER,
                        completion_tokens INTEGER,
                        total_tokens INTEGER,
                        cost_usd REAL,
                        cache_status TEXT,
                        latency_ms REAL
                    )
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp ON llm_calls(timestamp)
                """)
                conn.commit()
    
    def record(self, customer_id: str, problem_type: str, model: str,
               prompt_tokens: int, completion_tokens: int, cost_usd: float,
               cache_status: str = "MISS", latency_ms: float = 0.0):
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO llm_calls 
                    (timestamp, customer_id, problem_type, model, 
                     prompt_tokens, completion_tokens, total_tokens, 
                     cost_usd, cache_status, latency_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (time.time(), customer_id, problem_type, model,
                      prompt_tokens, completion_tokens, 
                      prompt_tokens + completion_tokens,
                      cost_usd, cache_status, latency_ms))
                conn.commit()
    
    def summary(self, since: Optional[float] = None) -> dict:
        since = since or 0
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("""
                SELECT 
                    COUNT(*) as total_calls,
                    COALESCE(SUM(total_tokens), 0) as total_tokens,
                    COALESCE(SUM(cost_usd), 0) as total_cost_usd,
                    COALESCE(SUM(CASE WHEN cache_status = 'HIT' THEN 1 ELSE 0 END), 0) as cache_hits,
                    COALESCE(SUM(CASE WHEN cache_status = 'MISS' THEN 1 ELSE 0 END), 0) as cache_misses
                FROM llm_calls WHERE timestamp >= ?
            """, (since,)).fetchone()
            return {
                "total_calls": row[0],
                "total_tokens": row[1],
                "total_cost_usd": round(row[2], 6),
                "cache_hits": row[3],
                "cache_misses": row[4],
                "hit_rate": round(row[3] / max(row[0], 1) * 100, 2)
            }


_ledger_instance: Optional[CostLedger] = None

def get_ledger() -> CostLedger:
    global _ledger_instance
    if _ledger_instance is None:
        _ledger_instance = CostLedger()
    return _ledger_instance
'''

# 5. LITELLM PROXY WRAPPER
FILES["engine/llm/__init__.py"] = ""

FILES["engine/llm/deepseek_proxy.py"] = '''"""
LiteLLM Proxy Wrapper - DeepSeek cagrilari icin:
- Timeout (30s default)
- Exponential backoff retry (3 deneme)
- Token + cost tracking
- Sadece ceviri icin kullanilir, HESAPLAMA YOK
"""
import time
from typing import Optional
import litellm
from config import settings
from config.secrets import DEEPSEEK_API_KEY, DEEPSEEK_ENDPOINT, DEEPSEEK_MODEL
from engine.cache.cost_ledger import get_ledger


# LiteLLM config
litellm.num_retries = settings.LITELLM_MAX_RETRIES
litellm.request_timeout = settings.LITELLM_TIMEOUT


class DeepSeekProxy:
    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.model = DEEPSEEK_MODEL
        self.api_base = DEEPSEEK_ENDPOINT
    
    def synthesize(self, physical_findings: list, customer_id: str = "default",
                   problem_type: str = "unknown") -> dict:
        """
        Fiziksel motor ciktisini insan diline cevirir.
        ASLA hesaplamaz, ASLA yeni bilgi uremez.
        """
        start = time.time()
        
        if not self.api_key:
            return {
                "error": "DEEPSEEK_API_KEY ayarlanmamis",
                "fallback_synthesis": self._offline_fallback(physical_findings)
            }
        
        system_prompt = (
            "Sen InversionCore fiziksel motorlarinin ciktisini insan diline ceviren bir sentez motorusun. "
            "KURALLAR:\\n"
            "1. ASLA yeni bilgi ekleme, ASLA hesaplama yapma\\n"
            "2. Sadece verilen fiziksel bulgulari ozetle\\n"
            "3. Her bulgunun 'negatif bilgi' oldugunu vurgula\\n"
            "4. Turkce cevap ver\\n"
            "5. Kisa ve net ol (maksimum 200 kelime)"
        )
        
        user_prompt = (
            "Asagidaki fiziksel motor bulgularini sentezle:\\n\\n" +
            "\\n".join(f"- {f.get('motor', '?')}: {f.get('negative_finding', '?')}" 
                      for f in physical_findings)
        )
        
        try:
            response = litellm.completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                api_key=self.api_key,
                api_base=self.api_base,
                temperature=0.0,  # Deterministik cikti icin
                max_tokens=400
            )
            
            latency_ms = (time.time() - start) * 1000
            usage = response.usage
            cost = response._hidden_params.get("response_cost", 0.0) or 0.0
            
            get_ledger().record(
                customer_id=customer_id,
                problem_type=problem_type,
                model=self.model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                cost_usd=cost,
                cache_status="MISS",
                latency_ms=latency_ms
            )
            
            return {
                "synthesis": response.choices[0].message.content,
                "tokens": usage.total_tokens,
                "cost_usd": round(cost, 6),
                "latency_ms": round(latency_ms, 2),
                "source": "deepseek"
            }
        
        except Exception as e:
            get_ledger().record(
                customer_id=customer_id, problem_type=problem_type,
                model=self.model, prompt_tokens=0, completion_tokens=0,
                cost_usd=0.0, cache_status="ERROR",
                latency_ms=(time.time() - start) * 1000
            )
            return {
                "error": str(e),
                "fallback_synthesis": self._offline_fallback(physical_findings)
            }
    
    def _offline_fallback(self, findings: list) -> str:
        """API yoksa offline sentez (token maliyeti: 0)"""
        lines = ["[OFFLINE SENTEZ - DeepSeek API yok]"]
        for f in findings:
            lines.append(f"- {f.get('motor', '?')}: {f.get('negative_finding', '?')}")
        return "\\n".join(lines)
'''

# 6. ORKESTRATOR GUNCELLEMESI (cache-first strategy)
FILES["engine/orchestrator_v2.py"] = '''"""
Orkestrator v2 - Cache-first strategy
1. Cache kontrol (0 token)
2. Cache miss -> fiziksel motorlar calisir (0 token)
3. Motor sonuclari cache'e yazilir
4. DeepSeek sadece sentez icin cagirilir (minimum token)
5. Sentez de cache'e yazilir -> sonraki ayni sorguda 0 token
"""

class MockMotor:
    def find_contradictions(self, st): return {"motor": "Z3Surgeon", "negative_finding": "Tutarsizlik tespit edildi"}
    def find_infeasible(self, v, c): return {"motor": "ORToolsSurgeon", "negative_finding": "Kapasite asimi"}
    def find_hidden_connections(self, n, e): return {"motor": "NetworkSurgeon", "negative_finding": "Gizli araci bulundu"}
    def find_manipulation(self, d, e=None): return {"motor": "StatsSurgeon", "negative_finding": "Manipulasyon tespit edildi"}
    def find_collapse(self, f, c): return {"motor": "DynamicsSurgeon", "negative_finding": "Sistem cokus noktasinda"}
    def find_minimal_cut_sets(self, c): return {"motor": "RiskSurgeon", "negative_finding": "Kritik zafiyet (Cut Set)"}
    def find_spurious_correlation(self, d, t, o): return {"motor": "CausalSurgeon", "negative_finding": "Korelasyon nedensellik degil"}

class ProblemOntology:
    def classify(self, text):
        if "celiski" in text.lower(): return "LOGICAL"
        if "ag" in text.lower(): return "NETWORK"
        return "UNKNOWN"

from engine.cache.deterministic_cache import get_cache, cached
from engine.cache.cost_ledger import get_ledger
from engine.llm.deepseek_proxy import DeepSeekProxy
import config.settings as settings


class InversionOrchestratorV2:
    def __init__(self):
        self.ontology = ProblemOntology()
        self.deepseek = DeepSeekProxy()
        self.motors = {
            "LOGICAL": MockMotor(),
            "OPTIMIZATION": MockMotor(),
            "NETWORK": MockMotor(),
            "PROBABILISTIC": MockMotor(),
            "DYNAMIC": MockMotor(),
            "GAME": MockMotor(),
            "RISK": MockMotor(),
            "CAUSAL": MockMotor()
        }
    
    def invert_motors(self, problem_type: str, data: dict) -> list:
        """Fiziksel motorlari calistirir (0 token maliyeti)"""
        motor = self.motors.get(problem_type)
        if not motor:
            return [{"error": "Bilinmeyen problem tipi: " + str(problem_type)}]
        
        if problem_type == "LOGICAL":
            result = motor.find_contradictions(data.get("statements", []))
        elif problem_type == "OPTIMIZATION":
            result = motor.find_infeasible(data.get("variables", {}), data.get("constraints", []))
        elif problem_type == "NETWORK":
            result = motor.find_hidden_connections(data.get("nodes", []), data.get("edges", []))
        elif problem_type == "PROBABILISTIC":
            result = motor.find_manipulation(data.get("data", []))
        elif problem_type == "DYNAMIC":
            result = motor.find_collapse(data.get("model_file"), data.get("initial_conditions"))
        elif problem_type == "GAME":
            result = motor.find_manipulation(data.get("payoff_A", []), data.get("payoff_B", []))
        elif problem_type == "RISK":
            result = motor.find_minimal_cut_sets(data.get("cut_sets", []))
        elif problem_type == "CAUSAL":
            result = motor.find_spurious_correlation(data.get("dataframe"), data.get("treatment"), data.get("outcome"))
        else:
            result = {"error": "Motor bulunamadi"}
        return [result]
    
    def auto_invert(self, text: str, data: dict, customer_id: str = "default") -> dict:
        """
        TAM AKIS:
        1. Ontoloji siniflandirma (0 token)
        2. Motor cache kontrol (0 token)
        3. Motor calistirma (0 token)
        4. Sentez cache kontrol (0 token)
        5. DeepSeek sentez (minimum token, sadece cevirir)
        """
        problem_type = self.ontology.classify(text)
        cache = get_cache()
        
        # Motor sonuclari icin cache
        motor_key = cache.make_key(f"motor:{problem_type}", data)
        cached_motor_result = cache.get(motor_key)
        
        if cached_motor_result is not None:
            motor_results = cached_motor_result
            motor_cache_status = "HIT"
        else:
            motor_results = self.invert_motors(problem_type, data)
            if motor_results and isinstance(motor_results[0], dict) and not motor_results[0].get("error"):
                cache.set(motor_key, motor_results)
            motor_cache_status = "MISS"
        
        # Sentez icin cache
        synthesis_key = cache.make_key(f"synth:{problem_type}", {"data": data, "results": motor_results})
        cached_synth = cache.get(synthesis_key)
        
        if cached_synth is not None:
            synthesis = cached_synth
            synthesis_cache_status = "HIT"
        else:
            if any(r.get("error") for r in motor_results):
                synthesis = {"synthesis": "Motor hatasi, sentez atlandi", "source": "error"}
            else:
                synthesis = self.deepseek.synthesize(
                    motor_results, customer_id=customer_id, problem_type=problem_type
                )
                if "error" not in synthesis:
                    cache.set(synthesis_key, synthesis)
            synthesis_cache_status = "MISS"
        
        return {
            "problem_type": problem_type,
            "motor_results": motor_results,
            "synthesis": synthesis,
            "cache_stats": {
                "motor": motor_cache_status,
                "synthesis": synthesis_cache_status,
                "backend": cache.stats()["backend"]
            },
            "cost_summary": get_ledger().summary()
        }
'''

# 7. MAIN PHASE 2 - DEMO VE DOGRULAMA
FILES["main_phase2.py"] = '''"""
Faz 2 Demo - Sifir Token Kalkani Dogrulama
3 senaryo:
1. Ilk cagri: motor + sentez (DeepSeek varsa token tuketir)
2. Ayni cagri: %100 cache hit (0 token)
3. Farkli cagri: yeni motor + sentez
"""
import sys
import os

sys.path.insert(0, os.getcwd())

from engine.orchestrator_v2 import InversionOrchestratorV2
from engine.cache.deterministic_cache import get_cache
from engine.cache.cost_ledger import get_ledger


def banner(title):
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main():
    orch = InversionOrchestratorV2()
    cache = get_cache()
    ledger = get_ledger()
    
    banner("FAZ 2: SIFIR TOKEN KALKANI DOGRULAMA")
    print(f"Cache backend: {cache.stats()['backend']}")
    print(f"Cache TTL: {cache.stats()['ttl_seconds']} saniye")
    
    # SENARYO 1: Ilk cagri (motor + sentez)
    banner("SENARYO 1: ILK CAGRI (Motor + Sentez)")
    r1 = orch.auto_invert(
        "Bu argumanda celiski var mi?",
        {"statements": ["x > 0", "x < 0"]},
        customer_id="demo_customer"
    )
    print(f"Problem tipi: {r1['problem_type']}")
    print(f"Motor sonuclari: {r1['motor_results']}")
    print(f"Sentez kaynagi: {r1['synthesis'].get('source', 'offline')}")
    if "synthesis" in r1["synthesis"]:
        print(f"Sentez: {r1['synthesis']['synthesis'][:200]}...")
    print(f"Motor cache: {r1['cache_stats']['motor']}")
    print(f"Sentez cache: {r1['cache_stats']['synthesis']}")
    
    # SENARYO 2: AYNI cagri (cache hit bekleniyor)
    banner("SENARYO 2: AYNI CAGRI (Cache HIT bekleniyor)")
    r2 = orch.auto_invert(
        "Bu argumanda celiski var mi?",
        {"statements": ["x > 0", "x < 0"]},
        customer_id="demo_customer"
    )
    print(f"Motor cache: {r2['cache_stats']['motor']}  <- BEKLENTI: HIT")
    print(f"Sentez cache: {r2['cache_stats']['synthesis']}  <- BEKLENTI: HIT")
    
    # SENARYO 3: Farkli cagri
    banner("SENARYO 3: FARKLI CAGRI (Yeni motor + sentez)")
    r3 = orch.auto_invert(
        "Bu agda gizli araci var mi?",
        {"nodes": ["A", "B", "C", "D"], "edges": [("A", "B"), ("B", "C"), ("C", "D"), ("A", "D")]},
        customer_id="demo_customer"
    )
    print(f"Problem tipi: {r3['problem_type']}")
    print(f"Motor sonuclari: {r3['motor_results']}")
    print(f"Motor cache: {r3['cache_stats']['motor']}  <- BEKLENTI: MISS (yeni veri)")
    
    # SENARYO 4: Ayni ag cagrisi (cache hit)
    banner("SENARYO 4: AYNI AG CAGRISI (Cache HIT)")
    r4 = orch.auto_invert(
        "Bu agda gizli araci var mi?",
        {"nodes": ["A", "B", "C", "D"], "edges": [("A", "B"), ("B", "C"), ("C", "D"), ("A", "D")]},
        customer_id="demo_customer"
    )
    print(f"Motor cache: {r4['cache_stats']['motor']}  <- BEKLENTI: HIT")
    
    # MALIYET RAPORU
    banner("MALIYET RAPORU")
    summary = ledger.summary()
    print(f"Toplam LLM cagrisi: {summary['total_calls']}")
    print(f"Toplam token: {summary['total_tokens']}")
    print(f"Toplam maliyet (USD): ${summary['total_cost_usd']:.6f}")
    print(f"Cache HIT: {summary['cache_hits']}")
    print(f"Cache MISS: {summary['cache_misses']}")
    print(f"Hit orani: %{summary['hit_rate']}")
    
    # BASARI KRITERLERI
    banner("BASARI KRITERLERI KONTROL")
    checks = [
        ("Senaryo 2 motor cache HIT", r2["cache_stats"]["motor"] == "HIT"),
        ("Senaryo 2 sentez cache HIT", r2["cache_stats"]["synthesis"] == "HIT"),
        ("Senaryo 3 motor cache MISS", r3["cache_stats"]["motor"] == "MISS"),
        ("Senaryo 4 motor cache HIT", r4["cache_stats"]["motor"] == "HIT"),
        ("Hit orani >= %50", summary["hit_rate"] >= 50.0),
    ]
    for label, passed in checks:
        status = "GECTI" if passed else "BASARISIZ"
        print(f"[{status}] {label}")
    
    all_passed = all(p for _, p in checks)
    print()
    if all_passed:
        print("TUM KRITERLER GECTI - FAZ 2 VERIFIED_COMPLETE")
    else:
        print("BIR VEYA DAHA FAZLA KRITER BASARISIZ - INCELE")


if __name__ == "__main__":
    main()
'''

# 8. FORENSIC DOGRULAMA SCRIPTI
FILES["debug_phase2.py"] = '''"""
Faz 2 Adli Dogrulama Scripti
"""
import sys, os
sys.path.insert(0, os.getcwd())

from engine.cache.deterministic_cache import DeterministicCache
from engine.cache.cost_ledger import CostLedger

def banner(t):
    print("\\n" + "=" * 60)
    print(f"  {t}")
    print("=" * 60)

banner("1. CACHE KEY DETERMINIZMI")
cache = DeterministicCache()
data1 = {"a": 1, "b": 2, "c": [3, 4]}
data2 = {"c": [3, 4], "b": 2, "a": 1}  # Ayni veri, farkli siralama
k1 = cache.make_key("test", data1)
k2 = cache.make_key("test", data2)
print(f"Key 1: {k1}")
print(f"Key 2: {k2}")
print(f"Esit mi? {k1 == k2}  (Beklenen: True - sort_keys nedeniyle)")

banner("2. CACHE SET/GET")
cache.set("test:key1", {"result": "OK", "value": 42})
retrieved = cache.get("test:key1")
print(f"Set: {{'result': 'OK', 'value': 42}}")
print(f"Get: {retrieved}")
print(f"Dogru mu? {retrieved == {'result': 'OK', 'value': 42}}")

banner("3. BACKEND BILGISI")
print(f"Backend: {cache.stats()['backend']}")
print(f"TTL: {cache.stats()['ttl_seconds']}s")
print(f"Valkey kurulu mu? {__import__('engine.cache.deterministic_cache', fromlist=['VALKEY_AVAILABLE']).VALKEY_AVAILABLE}")

banner("4. MALIYET LEDGER WRITE/READ")
ledger = CostLedger(db_path="data/test_ledger.db")
ledger.record("cust1", "LOGICAL", "deepseek-chat", 100, 50, 0.000150, "MISS", 1234.5)
ledger.record("cust1", "LOGICAL", "deepseek-chat", 0, 0, 0.0, "HIT", 0.0)
summary = ledger.summary()
print(f"Toplam cagri: {summary['total_calls']}")
print(f"Toplam token: {summary['total_tokens']}")
print(f"Toplam maliyet: ${summary['total_cost_usd']:.6f}")
print(f"Cache hit: {summary['cache_hits']}, miss: {summary['cache_misses']}")

import os
try: os.remove("data/test_ledger.db")
except: pass

banner("TUM ADLI DOGRULAMALAR TAMAMLANDI")
'''

# DOSYALARI DISKE YAZ
for path, content in FILES.items():
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Olusturuldu: {path}")

print("\nFAZ 2 KURULUM TAMAMLANDI")
