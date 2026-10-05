import sys, os
sys.path.insert(0, os.getcwd())
from engine.orchestrator_v2 import InversionOrchestratorV2
from engine.cache.deterministic_cache import get_cache

cache = get_cache()
orch = InversionOrchestratorV2()

data = {"statements": ["x > 0", "x < 0"]}
problem_type = "LOGICAL"

m1 = orch.invert_motors(problem_type, data)
k1 = cache.make_key(f"synth:{problem_type}", {"data": data, "results": m1})
print("Key 1 (direct):", k1)
cache.set(k1, {"synth": "dummy"})

m2 = orch.invert_motors(problem_type, data)
k2 = cache.make_key(f"synth:{problem_type}", {"data": data, "results": m2})
print("Key 2 (re-eval):", k2)

print("Key 1 == Key 2:", k1 == k2)
