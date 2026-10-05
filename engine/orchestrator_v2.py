"""
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
