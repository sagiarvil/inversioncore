import z3, sys
from scipy import stats
import numpy as np

print("--- Z3 UNSAT CORE VERIFICATION ---")
s = z3.Solver()
x = z3.Int('x')
s.add(x > 0)
s.add(x < 0)
print(f"Z3 unsat check: {s.check()}")
print(f"Z3 unsat core (without tracking labels): {s.unsat_core()}")

print("\n--- SCIPY P-VALUE VERIFICATION ---")
data = [1, 2, 3, 100, 2, 1, 2, 3]
observed = np.array(data, dtype=float)
mu = max(float(np.mean(observed)), 0.0001)
pmf = stats.poisson.pmf(range(len(observed)), mu)
expected = (pmf / np.sum(pmf)) * np.sum(observed)
chi2, p_value = stats.chisquare(observed, expected)
print(f"Chi2 statistic: {chi2}")
print(f"p_value exact repr: {repr(p_value)}")

print("\n--- PYSD COLLAPSE TIME VERIFICATION ---")
import pysd
model = pysd.read_xmile('data/cash_model.xmile')
result = model.run()
for t, val in result['cash'].items():
    print(f"t={t} -> cash={val}")
