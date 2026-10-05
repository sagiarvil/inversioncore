import sys, os
sys.path.insert(0, os.getcwd())
from engine.orchestrator_v2 import InversionOrchestratorV2
from engine.cache.deterministic_cache import get_cache

cache = get_cache()
orch = InversionOrchestratorV2()

data = {"statements": ["x > 0", "x < 0"]}

r1 = orch.auto_invert("celiski", data)
print("Sentez Key 1:", cache.make_key(f"synth:{r1['problem_type']}", {"data": data, "results": r1['motor_results']}))
print("Cache Keys:", list(cache.backend.keys()) if hasattr(cache.backend, 'keys') else 'No keys()')

r2 = orch.auto_invert("celiski", data)
print("Sentez Key 2:", cache.make_key(f"synth:{r2['problem_type']}", {"data": data, "results": r2['motor_results']}))

print("R1 Sentez Cache:", r1['cache_stats']['synthesis'])
print("R2 Sentez Cache:", r2['cache_stats']['synthesis'])
