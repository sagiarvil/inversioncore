# ============================================================
# INVERSIONCORE v2 TEK PARÇA KURULUMCU (Hata Düzeltmeli & Üretim Sürümü)
# Kullanım:
#   1) python inversioncore_installer.py
#   2) pip install -r requirements.txt
#   3) python main.py
# ============================================================
import os

FILES = {}

# 1. BAĞIMLILIKLAR
FILES["requirements.txt"] = """z3-solver
ortools
networkx
scipy
SALib
pysd
nashpy
dowhy
numpy
pandas
"""

FILES["engine/__init__.py"] = ""
FILES["engine/motors/__init__.py"] = ""

# 2. AYARLAR
FILES["config/settings.py"] = '''DEEPSEEK_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-coder"
CACHE_ENABLED = False
VALKEY_URL = "redis://localhost:6379"
# Faz 2: LiteLLM + Valkey + DeepSeek entegrasyonu buradan açılacak
'''

# 3. ONTOLOJİ
FILES["engine/ontology.py"] = '''class ProblemOntology:
    RULES = {
        "LOGICAL": ["çelişki", "ispat", "doğru", "yanlış", "aksiyom", "mantık", "tutarlılık"],
        "NETWORK": ["ilişki", "bağlantı", "ağ", "ortak", "aracı", "düğüm", "grafik"],
        "PROBABILISTIC": ["olasılık", "anomali", "dağılım", "manipülasyon", "istatistik", "organik"],
        "OPTIMIZATION": ["kısıt", "kaynak", "kapasite", "optimum", "maliyet", "darboğaz"],
        "GAME": ["rekabet", "strateji", "denge", "oyun", "fiyat"],
        "CAUSAL": ["neden", "sonuç", "etki", "korelasyon", "sebep"],
        "DYNAMIC": ["zaman", "değişim", "gecikme", "büyüme", "çöküş", "dinamik"],
        "RISK": ["hata", "risk", "güvenlik", "zafiyet", "kritik", "kesme"]
    }

    def classify(self, text):
        text_lower = text.lower()
        scores = {}
        for problem_type, keywords in self.RULES.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            scores[problem_type] = score
        if max(scores.values()) == 0:
            return "UNKNOWN"
        return max(scores, key=scores.get)
'''

# 4. MOTOR 1: Z3 (Mantıksal Cerrahi)
FILES["engine/motors/z3_surgeon.py"] = '''import re
import z3 as z3mod

BASE = {k: getattr(z3mod, k) for k in dir(z3mod) if not k.startswith("_")}
PY_WORDS = set(["and", "or", "not", "True", "False", "in", "is", "if", "else"])


def declare(stmt, namespace):
    for token in re.findall(r"[A-Za-z_][A-Za-z_0-9]*", stmt):
        if token in BASE or token in namespace or token in PY_WORDS:
            continue
        namespace[token] = z3mod.Int(token)
    return namespace


class Z3Surgeon:
    def __init__(self):
        self.solver = None
        self.namespace = {}

    def _load(self, statements):
        self.solver = z3mod.Solver()
        self.namespace = {}
        for stmt in statements:
            declare(stmt, self.namespace)
            env = dict(BASE)
            env.update(self.namespace)
            self.solver.add(eval(stmt, {"__builtins__": None}, env))

    def find_contradictions(self, statements):
        self._load(statements)
        if self.solver.check() == z3mod.unsat:
            try:
                core = [str(s) for s in self.solver.unsat_core()]
            except Exception:
                core = []
            return {
                "motor": "Z3",
                "contradiction_found": True,
                "unsat_core": core,
                "negative_finding": "Bu sistem mantıksal olarak tutarsız"
            }
        return {"motor": "Z3", "contradiction_found": False}

    def find_hidden_assumptions(self, conclusion, premises):
        critical = []
        for i in range(len(premises)):
            subset = [p for j, p in enumerate(premises) if j != i]
            self.solver = z3mod.Solver()
            self.namespace = {}
            declare(conclusion, self.namespace)
            for p in subset:
                declare(p, self.namespace)
            env = dict(BASE)
            env.update(self.namespace)
            self.solver.add(z3mod.Not(eval(conclusion, {"__builtins__": None}, env)))
            for p in subset:
                self.solver.add(eval(p, {"__builtins__": None}, env))
            if self.solver.check() == z3mod.sat:
                critical.append(premises[i])
        return {
            "motor": "Z3",
            "critical_premises": critical,
            "hidden_assumption_found": len(critical) > 0,
            "negative_finding": "Sonuç bu öncüllere gizlice bağımlı: " + str(critical) if critical else "Gizli bağımlılık yok"
        }
'''

# 5. MOTOR 2: OR-Tools (Kısıt Cerrahisi)
FILES["engine/motors/ortools_surgeon.py"] = '''import re
from ortools.sat.python import cp_model

PY_WORDS = set(["and", "or", "not", "True", "False", "in", "is", "if", "else"])


class ORToolsSurgeon:
    def find_infeasible(self, variables, constraints):
        model = cp_model.CpModel()
        namespace = {}
        for name, bounds in variables.items():
            namespace[name] = model.NewIntVar(int(bounds[0]), int(bounds[1]), name)
        for constraint in constraints:
            for token in re.findall(r"[A-Za-z_][A-Za-z_0-9]*", constraint):
                if token not in namespace and token not in PY_WORDS:
                    namespace[token] = model.NewIntVar(0, 1000000, token)
        for constraint in constraints:
            model.Add(eval(constraint, {"__builtins__": None}, namespace))
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        if status == cp_model.INFEASIBLE:
            return {
                "motor": "OR-Tools",
                "infeasible": True,
                "negative_finding": "Bu sistem matematiksel olarak çalışamaz"
            }
        return {"motor": "OR-Tools", "infeasible": False}
'''

# 6. MOTOR 3: NetworkX (Ağ Cerrahisi)
FILES["engine/motors/network_surgeon.py"] = '''import networkx as nx


class NetworkSurgeon:
    def find_hidden_connections(self, nodes, edges):
        G = nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        centrality = nx.betweenness_centrality(G)
        hidden_brokers = [n for n, c in centrality.items() if c > 0.5]
        communities = list(nx.community.greedy_modularity_communities(G))
        return {
            "motor": "NetworkX",
            "hidden_brokers": hidden_brokers,
            "communities_count": len(communities),
            "negative_finding": "Bu ağda gizli aracılar var" if hidden_brokers else "Ağ temiz"
        }
'''

# 7. MOTOR 4: SciPy + SALib (İstatistiksel Cerrahi - Düzeltilmiş)
FILES["engine/motors/stats_surgeon.py"] = '''from scipy import stats
import numpy as np


class StatsSurgeon:
    def find_manipulation(self, data, distribution="poisson"):
        observed = np.array(data, dtype=float)
        if distribution == "poisson":
            mu = max(float(np.mean(observed)), 0.0001)
            # DÜZELTME: Frekans toplamı kuralı gereği normalizasyon
            pmf = stats.poisson.pmf(range(len(observed)), mu)
            expected = (pmf / np.sum(pmf)) * np.sum(observed)
            chi2, p_value = stats.chisquare(observed, expected)
        elif distribution == "normal":
            _, p_value = stats.normaltest(observed)
        else:
            p_value = 1.0
        return {
            "motor": "SciPy",
            "organic": bool(p_value > 0.05),
            "p_value": float(p_value),
            "manipulation_score": float(1 - p_value),
            "negative_finding": "Bu veri organik değil, manipüle edilmiş" if p_value < 0.05 else "Veri organik"
        }

    def find_sensitivity(self, problem, model_func):
        from SALib.sample import saltelli
        from SALib.analyze import sobol
        param_values = saltelli.sample(problem, 1024)
        Y = np.array([model_func(row) for row in param_values])
        si = sobol.analyze(problem, Y)
        return {
            "motor": "SALib",
            "first_order": list(si["S1"]),
            "total_order": list(si["ST"]),
            "names": problem["names"],
            "negative_finding": "Sonucu en çok bozan değişken: " + problem["names"][int(np.argmax(si["ST"]))]
        }
'''

# 8. MOTOR 5: PySD (Sistem Dinamikleri)
FILES["engine/motors/dynamics_surgeon.py"] = '''import pysd


class DynamicsSurgeon:
    def find_collapse(self, model_file, initial_conditions=None):
        if not model_file:
            return {"motor": "PySD", "error": "model_file gerekli"}
        model = pysd.load(model_file)
        if initial_conditions:
            result = model.run(initial_condition=initial_conditions)
        else:
            result = model.run()
        col = "cash" if "cash" in result.columns else result.columns[0]
        collapse_time = None
        for t, val in result[col].items():
            if val < 0:
                collapse_time = float(t)
                break
        return {
            "motor": "PySD",
            "collapse_detected": collapse_time is not None,
            "collapse_time": collapse_time,
            "negative_finding": "Sistem " + str(collapse_time) + " anında çökecek" if collapse_time else "Sistem stabil"
        }
'''

# 9. MOTOR 6: Nashpy (Oyun Teorisi)
FILES["engine/motors/game_surgeon.py"] = '''import nashpy as nash
import numpy as np


class GameSurgeon:
    def find_manipulation(self, payoff_A, payoff_B):
        A = np.array(payoff_A)
        B = np.array(payoff_B)
        game = nash.Game(A, B)
        equilibria = list(game.support_enumeration())
        return {
            "motor": "Nashpy",
            "equilibrium_found": len(equilibria) > 0,
            "equilibria_count": len(equilibria),
            "negative_finding": "Bu oyunda denge yok, manipülasyon var" if not equilibria else "Oyun dengede"
        }
'''

# 10. MOTOR 7: Risk MCS (Hata Ağacı / Kesme Kümeleri)
FILES["engine/motors/risk_surgeon.py"] = '''class RiskSurgeon:
    def find_minimal_cut_sets(self, cut_sets):
        sets = [frozenset(cs) for cs in cut_sets]
        minimal = []
        for cs in sets:
            is_minimal = True
            for other in sets:
                if other != cs and other.issubset(cs):
                    is_minimal = False
                    break
            if is_minimal and cs not in minimal:
                minimal.append(cs)
        return {
            "motor": "RiskMCS",
            "minimal_cut_sets": [sorted(list(cs)) for cs in minimal],
            "count": len(minimal),
            "negative_finding": "Bu sistemin çökmesi için bu olay kümeleri YETERLİ"
        }
'''

# 11. MOTOR 8: DoWhy (Nedensellik)
FILES["engine/motors/causal_surgeon.py"] = '''from dowhy import CausalModel


class CausalSurgeon:
    def find_spurious_correlation(self, data, treatment, outcome, graph=None):
        if data is None or treatment is None or outcome is None:
            return {"motor": "DoWhy", "error": "dataframe, treatment, outcome gerekli"}
        if graph is None:
            graph = "digraph { X -> Y; Z -> X; Z -> Y; }"
        model = CausalModel(data=data, treatment=treatment, outcome=outcome, graph=graph)
        identified = model.identify_effect()
        estimate = model.estimate_effect(identified)
        refute = model.refute_estimate(identified, estimate, method_name="placebo_treatment_refuter")
        return {
            "motor": "DoWhy",
            "causal_effect": float(estimate.value),
            "spurious": bool(refute.new_effect < 0.05),
            "negative_finding": "Bu ilişki nedensel değil, sahte korelasyon" if refute.new_effect < 0.05 else "Nedensel ilişki var"
        }
'''

# 12. ORKESTRATÖR
FILES["engine/orchestrator.py"] = '''from engine.ontology import ProblemOntology
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
'''

# 13. SENTEZ (zsh Token Maliyeti)
FILES["engine/synthesis.py"] = '''class SynthesisEngine:
    def synthesize(self, findings):
        lines = []
        for f in findings:
            motor = str(f.get("motor", "bilinmiyor"))
            finding = str(f.get("negative_finding", "bulgu yok"))
            lines.append("- " + motor + ": " + finding)
        return "\n".join(lines)
'''

# 14. XMILE MODEL DOSYASI
FILES["data/cash_model.xmile"] = '''<?xml version="1.0" encoding="utf-8"?>
<xmile version="1.0" xmlns="http://docs.oasis-open.org/xmile/ns/XMILE/v1.0">
  <model>
    <variables>
      <stock name="cash">
        <initial>500000</initial>
        <inflow>net_flow</inflow>
      </stock>
      <flow name="net_flow">-burn</flow>
      <aux name="burn">50000</aux>
    </variables>
  </model>
</xmile>
'''

# 15. MAIN DOĞRULAMA ÇALIŞTIRICISI
FILES["main.py"] = '''from engine.orchestrator import InversionOrchestrator
from engine.synthesis import SynthesisEngine


def main():
    orchestrator = InversionOrchestrator()
    synthesis = SynthesisEngine()

    print("=== TEST 1: Mantıksal Çelişki (Z3) ===")
    ptype, result = orchestrator.auto_invert(
        "Bu argümanda çelişki var mı?",
        {"statements": ["x > 0", "x < 0"]}
    )
    print("Tip:", ptype)
    print("Sonuç:", result)
    print(synthesis.synthesize(result))
    print()

    print("=== TEST 2: Kısıt Çelişkisi (OR-Tools) ===")
    ptype, result = orchestrator.auto_invert(
        "Bu kaynak kısıtları altında optimum çözüm var mı?",
        {"variables": {"x": [0, 10], "y": [0, 10]}, "constraints": ["x + y <= 5", "x >= 8"]}
    )
    print("Tip:", ptype)
    print("Sonuç:", result)
    print()

    print("=== TEST 3: Ağ Analizi (NetworkX) ===")
    ptype, result = orchestrator.auto_invert(
        "Bu şirketler arasındaki gizli bağlantıları bul",
        {
            "nodes": ["A", "B", "C", "D", "E"],
            "edges": [("A", "B"), ("B", "C"), ("C", "D"), ("A", "D"), ("D", "E")]
        }
    )
    print("Tip:", ptype)
    print("Sonuç:", result)
    print()

    print("=== TEST 4: İstatistiksel Anomali (SciPy) ===")
    ptype, result = orchestrator.auto_invert(
        "Bu veri dağılımı organik mi yoksa manipüle mi?",
        {"data": [1, 2, 3, 100, 2, 1, 2, 3]}
    )
    print("Tip:", ptype)
    print("Sonuç:", result)
    print()

    print("=== TEST 5: Dinamik Çöküş (PySD) ===")
    ptype, result = orchestrator.auto_invert(
        "Bu dinamik sistem ne zaman çöküş yaşar?",
        {"model_file": "data/cash_model.xmile"}
    )
    print("Tip:", ptype)
    print("Sonuç:", result)
    print()

    print("=== TEST 6: Risk Kesme Kümeleri (RiskMCS) ===")
    ptype, result = orchestrator.auto_invert(
        "Bu sistemin kritik risk kesme kümeleri neler?",
        {"cut_sets": [["e1", "e2"], ["e1"], ["e2", "e3"], ["e1", "e2", "e3"]]}
    )
    print("Tip:", ptype)
    print("Sonuç:", result)


if __name__ == "__main__":
    main()
'''

# DOSYALARI DİSKE YAZMA DÖNGÜSÜ
for path, content in FILES.items():
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Oluşturuldu: {path}")

print("\n[+] Kurulum tamamlandı. Sırasıyla çalıştırınız:")
print("    pip install -r requirements.txt")
print("    python main.py")
