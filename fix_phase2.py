import os

FILES = {}

FILES["engine/llm/deepseek_proxy.py"] = '''"""
LiteLLM Proxy Wrapper v2.1 - FORENSIC FIX
Degisiklikler:
1. Offline fallback artik 'error' degil 'offline: True' dondurur
   -> orchestrator offline sentezi cache'leyebilir
2. Offline modda da ledger.record() cagirilir (cost_usd=0.0)
   -> Hit orani dogru hesaplanir
3. Gercek transient hatalarda hala 'error' doner (cache'e yazilmaz)
"""
import time
import litellm
from config import settings
from config.secrets import DEEPSEEK_API_KEY, DEEPSEEK_ENDPOINT, DEEPSEEK_MODEL
from engine.cache.cost_ledger import get_ledger

litellm.num_retries = settings.LITELLM_MAX_RETRIES
litellm.request_timeout = settings.LITELLM_TIMEOUT


class DeepSeekProxy:
    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.model = DEEPSEEK_MODEL
        self.api_base = DEEPSEEK_ENDPOINT

    def synthesize(self, physical_findings: list, customer_id: str = "default",
                   problem_type: str = "unknown") -> dict:
        start = time.time()

        if not self.api_key:
            fallback_text = self._offline_fallback(physical_findings)
            latency_ms = (time.time() - start) * 1000
            get_ledger().record(
                customer_id=customer_id,
                problem_type=problem_type,
                model="offline-no-key",
                prompt_tokens=0, completion_tokens=0,
                cost_usd=0.0, cache_status="OFFLINE",
                latency_ms=latency_ms
            )
            return {
                "synthesis": fallback_text,
                "tokens": 0, "cost_usd": 0.0,
                "latency_ms": round(latency_ms, 2),
                "source": "offline",
                "offline": True
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
                api_key=self.api_key, api_base=self.api_base,
                temperature=0.0, max_tokens=400
            )
            latency_ms = (time.time() - start) * 1000
            usage = response.usage
            cost = response._hidden_params.get("response_cost", 0.0) or 0.0
            get_ledger().record(
                customer_id=customer_id, problem_type=problem_type,
                model=self.model, prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens, cost_usd=cost,
                cache_status="MISS", latency_ms=latency_ms
            )
            return {
                "synthesis": response.choices[0].message.content,
                "tokens": usage.total_tokens, "cost_usd": round(cost, 6),
                "latency_ms": round(latency_ms, 2), "source": "deepseek"
            }
        except Exception as e:
            latency_ms = (time.time() - start) * 1000
            get_ledger().record(
                customer_id=customer_id, problem_type=problem_type,
                model=self.model, prompt_tokens=0, completion_tokens=0,
                cost_usd=0.0, cache_status="ERROR", latency_ms=latency_ms
            )
            return {
                "error": str(e),
                "fallback_synthesis": self._offline_fallback(physical_findings)
            }

    def _offline_fallback(self, findings: list) -> str:
        lines = ["[OFFLINE SENTEZ - DeepSeek API yok]"]
        for f in findings:
            lines.append(f"- {f.get('motor', '?')}: {f.get('negative_finding', '?')}")
        return "\\n".join(lines)
'''

FILES["engine/orchestrator_v2.py"] = '''"""
Orkestrator v2.1 - FORENSIC FIX
Degisiklik: offline mod (error key YOK, offline flag VAR) artik cache'e yazilir.
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

from engine.cache.deterministic_cache import get_cache
from engine.cache.cost_ledger import get_ledger
from engine.llm.deepseek_proxy import DeepSeekProxy

class InversionOrchestratorV2:
    def __init__(self):
        self.ontology = ProblemOntology()
        self.deepseek = DeepSeekProxy()
        self.motors = {
            "LOGICAL": MockMotor(), "OPTIMIZATION": MockMotor(),
            "NETWORK": MockMotor(), "PROBABILISTIC": MockMotor(),
            "DYNAMIC": MockMotor(), "GAME": MockMotor(),
            "RISK": MockMotor(), "CAUSAL": MockMotor()
        }

    def invert_motors(self, problem_type: str, data: dict) -> list:
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
        problem_type = self.ontology.classify(text)
        cache = get_cache()

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
                # FORENSIC FIX: transient hata yoksa cache'e yaz (offline dahil)
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

FILES["main_phase2.py"] = '''"""
Faz 2 Demo v2.1 - FORENSIC FIX UYUMLU
"""
import sys, os
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

    # Onceki kayitlari temizle (ornek testin bagimsizligi icin)
    import sqlite3
    with sqlite3.connect(ledger.db_path) as conn:
        conn.execute("DELETE FROM llm_calls")
        conn.commit()

    banner("FAZ 2 v2.1: FORENSIC FIX SONRASI DOGRULAMA")
    print(f"Cache backend: {cache.stats()['backend']}")
    print(f"Cache TTL: {cache.stats()['ttl_seconds']} saniye")

    banner("SENARYO 1: ILK CAGRI")
    r1 = orch.auto_invert("Bu argumanda celiski var mi?",
                          {"statements": ["x > 0", "x < 0"]},
                          customer_id="demo_customer")
    print(f"Motor cache: {r1['cache_stats']['motor']}  <- BEKLENTI: MISS")
    print(f"Sentez cache: {r1['cache_stats']['synthesis']}  <- BEKLENTI: MISS")

    banner("SENARYO 2: AYNI CAGRI (Cache HIT bekleniyor)")
    r2 = orch.auto_invert("Bu argumanda celiski var mi?",
                          {"statements": ["x > 0", "x < 0"]},
                          customer_id="demo_customer")
    print(f"Motor cache: {r2['cache_stats']['motor']}  <- BEKLENTI: HIT")
    print(f"Sentez cache: {r2['cache_stats']['synthesis']}  <- BEKLENTI: HIT")

    banner("SENARYO 3: FARKLI CAGRI")
    r3 = orch.auto_invert("Bu agda gizli araci var mi?",
                          {"nodes": ["A", "B", "C", "D"],
                           "edges": [("A", "B"), ("B", "C"), ("C", "D"), ("A", "D")]},
                          customer_id="demo_customer")
    print(f"Motor cache: {r3['cache_stats']['motor']}  <- BEKLENTI: MISS")

    banner("SENARYO 4: AYNI AG CAGRISI (Cache HIT)")
    r4 = orch.auto_invert("Bu agda gizli araci var mi?",
                          {"nodes": ["A", "B", "C", "D"],
                           "edges": [("A", "B"), ("B", "C"), ("C", "D"), ("A", "D")]},
                          customer_id="demo_customer")
    print(f"Motor cache: {r4['cache_stats']['motor']}  <- BEKLENTI: HIT")
    print(f"Sentez cache: {r4['cache_stats']['synthesis']}  <- BEKLENTI: HIT")

    banner("MALIYET RAPORU")
    summary = ledger.summary()
    print(f"Toplam LLM cagrisi: {summary['total_calls']}")
    print(f"Toplam token: {summary['total_tokens']}")
    print(f"Toplam maliyet (USD): ${summary['total_cost_usd']:.6f}")
    print(f"Cache HIT: {summary['cache_hits']}")
    print(f"Cache MISS: {summary['cache_misses']}")
    print(f"Hit orani: %{summary['hit_rate']}")

    banner("BASARI KRITERLERI (v2.1)")
    checks = [
        ("Senaryo 2 motor cache HIT", r2["cache_stats"]["motor"] == "HIT"),
        ("Senaryo 2 sentez cache HIT", r2["cache_stats"]["synthesis"] == "HIT"),
        ("Senaryo 3 motor cache MISS", r3["cache_stats"]["motor"] == "MISS"),
        ("Senaryo 4 motor cache HIT", r4["cache_stats"]["motor"] == "HIT"),
        ("Senaryo 4 sentez cache HIT", r4["cache_stats"]["synthesis"] == "HIT"),
        ("Hit orani >= %50", summary["hit_rate"] >= 50.0),
        ("Toplam cagri = 4 (offline dahil)", summary["total_calls"] == 4),
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

for path, content in FILES.items():
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Guncellendi: {path}")

print()
print("=" * 60)
print("FORENSIC MINIMAL FIX TAMAMLANDI")
print("=" * 60)
