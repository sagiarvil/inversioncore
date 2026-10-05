import re
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
