#!/usr/bin/env python3
import sys, os, json, urllib.request, time
from pathlib import Path
from typing import Dict, Any

ALFA_ENDPOINT = "http://localhost:8080/v1/chat/completions"

class RealityInversionEngine:
    def __init__(self, endpoint: str = ALFA_ENDPOINT):
        self.endpoint = endpoint

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
            "model": "qwen2.5-coder-14b-abliterated",
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            "temperature": 0.1,
            "max_tokens": 750
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.endpoint, data=data, method="POST")
        req.add_header("Content-Type", "application/json")

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
            return {"status": "ERROR", "error": f"Yerel Alfa (localhost:8080) hatası: {str(e)}"}

if __name__ == "__main__":
    print(RealityInversionEngine().invert_problem("Test", "Business"))
