import litellm
import os

try:
    response = litellm.completion(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "hi"}],
        api_key=os.environ.get('DEEPSEEK_API_KEY'),
        api_base="https://api.deepseek.com",
    )
    print(response)
except Exception as e:
    print("ERROR:", str(e))
