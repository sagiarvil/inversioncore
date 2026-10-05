from engine.ontology import ProblemOntology
from engine.motors.z3_surgeon import Z3Surgeon
from engine.motors.ortools_surgeon import ORToolsSurgeon
from engine.motors.network_surgeon import NetworkSurgeon
from engine.motors.stats_surgeon import StatsSurgeon
from engine.motors.dynamics_surgeon import DynamicsSurgeon
from engine.motors.game_surgeon import GameSurgeon
from engine.motors.risk_surgeon import RiskSurgeon
from engine.motors.causal_surgeon import CausalSurgeon


class InversionOrchestrator:
    def __init__(self):
        self.ontology = ProblemOntology()
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

    def invert(self, problem_type, data):
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
            result = {"error": "Motor bulunamadı"}
        return [result]

    def auto_invert(self, text, data):
        problem_type = self.ontology.classify(text)
        return problem_type, self.invert(problem_type, data)
