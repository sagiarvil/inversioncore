import os

FILES = {}

FILES["engine/llm/deepseek_proxy.py"] = '''"""
LiteLLM Proxy Wrapper v2.1 - FORENSIC FIX
Degisiklikler:
1. Offline fallback artik 'error' degil 'offline: True' dondurur
   -> Bu sayede orchestrator offline sentezi cache'leyebilir
2. Offline modda da ledger.record() cagirilir (cost_usd=0.0)
   -> Hit orani dogru hesaplanir
3. Gercek transient hatalarda hala 'error' doner (cache'e yazilmaz)
"""
import time
from typing import Optional
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
        """
        Fiziksel motor ciktisini insan diline cevirir.
        ASLA hesaplamaz, ASLA yeni bilgi uretmez.
        """
        start = time.time()

        if not self.api_key:
            # OFFLINE MOD: deterministik sentez, cache'lensin
            fallback_text = self._offline_fallback(physical_findings)
            latency_ms = (time.time() - start) * 1000
            get_ledger().record(
                customer_id=customer_id,
                problem_type=problem_type,
                model="offline-no-key",
                prompt_tokens=0,
                completion_tokens=0,
                cost_usd=0.0,
                cache_status="OFFLINE",
                latency_ms=latency_ms
            )
            return {
                "synthesis": fallback_text,
                "tokens": 0,
                "cost_usd": 0.0,
                "latency_ms": round(latency_ms, 2),
                "source": "offline",
                "offline": True  # orchestrator bunu cache'leyecek
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
                temperature=0.0,
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
            # TRANSIENT HATA: cache'e yazilmasin (tekrar denenebilir)
            latency_ms = (time.time() - start) * 1000
            get_ledger().record(
                customer_id=customer_id,
                problem_type=problem_type,
                model=self.model,
                prompt_tokens=0,
                completion_tokens=0,
                cost_usd=0.0,
                cache_status="ERROR",
                latency_ms=latency_ms
            )
            return {
                "error": str(e),
                "fallback_synthesis": self._offline_fallback(physical_findings)
            }

    def _offline_fallback(self, findings: list) -> str:
        """API yoksa offline sentez (token maliyeti: 0, deterministik)"""
        lines = ["[OFFLINE SENTEZ - DeepSeek API yok]"]
        for f in findings:
            lines.append(f"- {f.get('motor', '?')}: {f.get('negative_finding', '?')}")
        return "\\n".join(lines)
'''

FILES["engine/orchestrator_v2.py"] = '''"""
Orkestrator v2.1 - FORENSIC FIX
Degisiklik:
- Cache write mantigi guncellendi:
  * "error" key var = transient hata -> cache YAZMA
  * "error" key YOK = offline veya success -> cache YAZ
"""
from engine.ontology import ProblemOntology
from engine.motors.z3_surgeon import Z3Surgeon
from engine.motors.ortools_surgeon import ORToolsSurgeon
from engine.motors.network_surgeon import NetworkSurgeon
from engine.motors.stats_surgeon import StatsSurgeon
from engine.motors.dynamics_surgeon import DynamicsSurgeon
from engine.motors.game_surgeon import GameSurgeon
from engine.motors.risk_surgeon import RiskSurgeon
from engine.motors.causal_surgeon import CausalSurgeon
from engine.cache.deterministic_cache import get_cache
from engine.cache.cost_ledger import get_ledger
from engine.llm.deepseek_proxy import DeepSeekProxy
import config.settings as settings


class InversionOrchestratorV2:
    def __init__(self):
        self.ontology = ProblemOntology()
        self.deepseek = DeepSeekProxy()
        self.motors = {
            "LOGICAL": Z3Surgeon(),
            "OPTIMIZATION": ORToolsSurgeon(),
            "NETWORK": NetworkSurgeon(),
            "PROBABILISTIC": StatsSurgeon(),
            "DYNAMIC": DynamicsSurgeon(),
            "GAME": GameSurgeon(),
            "RISK": RiskSurgeon(),
            "CAUSAL": CausalSurgeon()
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

        # MOTOR CACHE
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

        # SENTEZ CACHE
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
                # FORENSIC FIX: transient hata yoksa cache'e yaz
                # (offline mod dahil - cunku offline deterministik)
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
Degisiklikler:
- Hit orani artik offline modda da dogru hesaplanir
- OFFLINE senaryolar acikca etiketlenir
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

    banner("FAZ 2 v2.1: FORENSIC FIX SONRASI DOGRULAMA")
    print(f"Cache backend: {cache.stats()['backend']}")
    print(f"Cache TTL: {cache.stats()['ttl_seconds']} saniye")

    # SENARYO 1: Ilk cagri (motor + sentez OFFLINE)
    banner("SENARYO 1: ILK CAGRI (Motor MISS + Sentez OFFLINE/MISS)")
    r1 = orch.auto_invert(
        "Bu argumanda celiski var mi?",
        {"statements": ["x > 0", "x < 0"]},
        customer_id="demo_customer"
    )
    print(f"Problem tipi: {r1['problem_type']}")
    print(f"Motor sonuclari: {r1['motor_results']}")
    print(f"Sentez kaynagi: {r1['synthesis'].get('source', 'unknown')}")
    print(f"Sentez offline: {r1['synthesis'].get('offline', False)}")
    print(f"Motor cache: {r1['cache_stats']['motor']}")
    print(f"Sentez cache: {r1['cache_stats']['synthesis']}")

    # SENARYO 2: AYNI cagri -> IKI cache de HIT olmali
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
    print(f"Motor cache: {r3['cache_stats']['motor']}  <- BEKLENTI: MISS")

    # SENARYO 4: Ayni ag cagrisi
    banner("SENARYO 4: AYNI AG CAGRISI (Cache HIT)")
    r4 = orch.auto_invert(
        "Bu agda gizli araci var mi?",
        {"nodes": ["A", "B", "C", "D"], "edges": [("A", "B"), ("B", "C"), ("C", "D"), ("A", "D")]},
        customer_id="demo_customer"
    )
    print(f"Motor cache: {r4['cache_stats']['motor']}  <- BEKLENTI: HIT")
    print(f"Sentez cache: {r4['cache_stats']['synthesis']}  <- BEKLENTI: HIT")

    # MALIYET RAPORU
    banner("MALIYET RAPORU (FORENSIC FIX SONRASI)")
    summary = ledger.summary()
    print(f"Toplam LLM cagrisi: {summary['total_calls']}")
    print(f"Toplam token: {summary['total_tokens']}")
    print(f"Toplam maliyet (USD): ${summary['total_cost_usd']:.6f}")
    print(f"Cache HIT: {summary['cache_hits']}")
    print(f"Cache MISS: {summary['cache_misses']}")
    print(f"Hit orani: %{summary['hit_rate']}")

    # BASARI KRITERLERI
    banner("BASARI KRITERLERI KONTROL (v2.1)")
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
print("FORENSIC FIX TAMAMLANDI")
print("=" * 60)
