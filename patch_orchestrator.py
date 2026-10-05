import re

with open("engine/orchestrator_v2.py", "r") as f:
    code = f.read()

replacement = """        if cached_synth is not None:
            synthesis = cached_synth
            synthesis_cache_status = "HIT"
            get_ledger().record(
                customer_id=customer_id,
                problem_type=problem_type,
                model="cache-hit",
                prompt_tokens=0,
                completion_tokens=0,
                cost_usd=0.0,
                cache_status="HIT"
            )
"""
code = code.replace("""        if cached_synth is not None:
            synthesis = cached_synth
            synthesis_cache_status = "HIT\"""", replacement)

with open("engine/orchestrator_v2.py", "w") as f:
    f.write(code)
