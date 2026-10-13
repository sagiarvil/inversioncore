import re
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
