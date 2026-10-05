"""
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
