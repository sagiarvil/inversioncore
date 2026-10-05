import sys, os
sys.path.insert(0, os.getcwd())
from engine.llm.deepseek_proxy import DeepSeekProxy

proxy = DeepSeekProxy()
print("API KEY:", repr(proxy.api_key))
res = proxy.synthesize([{"motor": "Z3", "negative_finding": "X"}])
print("RESULT:", res)
