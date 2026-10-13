import urllib.request, json
prompt = 'Extract financial/business numbers from this text as pure JSON (no markdown). Focus on capital, monthly costs, and capacity.\n{"initial_cash": float, "monthly_burn": float, "capacity_units": float}\nText: "Bütçemiz 850000 TL, aylık 25000 TL giderimiz var."'
payload = {"model": "coder_candidate", "messages": [{"role": "user", "content": prompt}], "temperature": 0.0, "max_tokens": 150}
req = urllib.request.Request("http://localhost:8080/v1/chat/completions", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    print(resp.read().decode("utf-8"))
