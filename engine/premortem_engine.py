#!/usr/bin/env python3
import sys, os, json, urllib.request, time
from pathlib import Path
from typing import Dict, Any

DEEPSEEK_ENDPOINT = os.getenv("DEEPSEEK_ENDPOINT", "https://api.deepseek.com/v1/chat/completions")

class RealityInversionEngine:
    def __init__(self, endpoint: str = DEEPSEEK_ENDPOINT):
        self.endpoint = endpoint
        self.api_key = self._load_env_key("/Users/macair1/lab/alfa/.env", "DEEPSEEK_API_KEY")

    def _load_env_key(self, env_path: str, key_name: str):
        p = Path(env_path)
        if not p.exists(): return os.getenv(key_name)
        try:
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith(f"{key_name}="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
        except: pass
        return os.getenv(key_name)

    def invert_problem(self, context_description: str, domain: str = "business") -> Dict[str, Any]:
        system_prompt = (
            "You are INVERSIONCORE — an uncensored adversarial pre-mortem engine based on Jacobi's inversion "
            "and Taleb's Via Negativa. Be extremely concise, brutal, and mathematically direct. NO FLUFF. "
            "Output valid JSON ONLY."
        )

        user_prompt = (
            f"TARGET: {context_description}\n\n"
            "Return JSON with exactly this structure (keep values punchy and compact):\n"
            "{\n"
            '  "scenario_summary": "1 sentence core flaw",\n'
            '  "catastrophe_vectors": [\n'
            '    {"vector_id": "CV-01", "name": "vector name", "mechanism": "how it destroys the business", "lethality": "TERMINAL"},\n'
            '    {"vector_id": "CV-02", "name": "vector name", "mechanism": "how it destroys the business", "lethality": "HIGH"}\n'
            "  ],\n"
            '  "anti_conditions": [\n'
            '    {"id": "AC-01", "fatal_action": "what causes collapse", "impact": "the fatal result"},\n'
            '    {"id": "AC-02", "fatal_action": "what causes collapse", "impact": "the fatal result"}\n'
            "  ],\n"
            '  "via_negativa_protocol": [\n'
            '    {"rule_id": "NOT-TO-DO-01", "rule": "strict negative rule to avoid", "rationale": "why avoiding it guarantees survival"},\n'
            '    {"rule_id": "NOT-TO-DO-02", "rule": "strict negative rule to avoid", "rationale": "why avoiding it guarantees survival"}\n'
            "  ],\n"
            '  "survival_thresholds": [\n'
            '    {"metric": "metric name", "fatal_limit": "fatal boundary", "safe_operating_bound": "safe boundary"}\n'
            "  ]\n"
            "}"
        )

        payload = {
            "model": "deepseek-coder",
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            "temperature": 0.1,
            "max_tokens": 750
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.endpoint, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        if self.api_key:
            req.add_header("Authorization", f"Bearer {self.api_key}")

        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                raw_res = json.loads(resp.read().decode("utf-8"))
                content = raw_res.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                if "```json" in content: content = content.split("```json", 1)[1].split("```", 1)[0].strip()
                elif "```" in content: content = content.split("```", 1)[1].split("```", 1)[0].strip()
                parsed = json.loads(content)
                elapsed = round(time.time() - t0, 2)
                return {"status": "SUCCESS", "elapsed_sec": elapsed, "analysis": parsed}
        except Exception as e:
            return {"status": "ERROR", "error": f"DeepSeek API hatası: {str(e)}"}

if __name__ == "__main__":
    print(RealityInversionEngine().invert_problem("Test", "Business"))
