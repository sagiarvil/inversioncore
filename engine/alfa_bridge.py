#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional

ALFA_LOCAL_ENDPOINT = os.getenv("ALFA_LOCAL_ENDPOINT", "http://localhost:8080/v1/chat/completions")
DEEPSEEK_ENDPOINT = os.getenv("DEEPSEEK_ENDPOINT", "https://api.deepseek.com/v1/chat/completions")

class AlfaBridge:
    def __init__(self, alfa_endpoint: str = ALFA_LOCAL_ENDPOINT, deepseek_endpoint: str = DEEPSEEK_ENDPOINT, alfa_env_path: str = "/Users/macair1/lab/alfa/.env"):
        self.alfa_endpoint = alfa_endpoint
        self.deepseek_endpoint = deepseek_endpoint
        self.deepseek_api_key = self._load_env_key(alfa_env_path, "DEEPSEEK_API_KEY")

    def _load_env_key(self, env_path: str, key_name: str) -> Optional[str]:
        p = Path(env_path)
        if not p.exists():
            return os.getenv(key_name)
        try:
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith(f"{key_name}="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
        return os.getenv(key_name)

    def _call_llm(self, endpoint: str, messages: list, model: str, temperature: float = 0.0, api_key: Optional[str] = None) -> Dict[str, Any]:
        payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": 2048}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(endpoint, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        if api_key:
            req.add_header("Authorization", f"Bearer {api_key}")
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"status": "error", "error": f"Connection failed to {endpoint}: {str(e)}"}

    def analyze_vulnerability_poc(self, vuln_data: Dict[str, Any]) -> str:
        ast_scope = vuln_data.get("ast_scope", {})
        messages = [
            {"role": "system", "content": "You are InversionCore Red Team Security Agent powered by DeepSeek. Analyze the AST scope and explain the vulnerability mechanics and exploit scenario conceptually."},
            {"role": "user", "content": json.dumps({"rule_id": vuln_data.get("rule_id"), "symbol": ast_scope.get("enclosing_symbol"), "code": ast_scope.get("full_scope_code"), "params": ast_scope.get("parameters", [])})}
        ]
        resp = self._call_llm(self.deepseek_endpoint, messages, model="deepseek-coder", api_key=self.deepseek_api_key)
        return resp.get("choices", [{}])[0].get("message", {}).get("content", f"[DeepSeek Red Error] {resp.get('error')}")

    def generate_ast_patch(self, vuln_data: Dict[str, Any]) -> str:
        ast_scope = vuln_data.get("ast_scope", {})
        messages = [
            {"role": "system", "content": "You are InversionCore Blue Team Defense Agent. Provide a safe code patch preserving exact function signatures and eliminating the reported vulnerability."},
            {"role": "user", "content": json.dumps({"rule_id": vuln_data.get("rule_id"), "symbol": ast_scope.get("enclosing_symbol"), "code": ast_scope.get("full_scope_code"), "params": ast_scope.get("parameters", [])})}
        ]
        resp = self._call_llm(self.deepseek_endpoint, messages, model="deepseek-coder", api_key=self.deepseek_api_key)
        return resp.get("choices", [{}])[0].get("message", {}).get("content", f"[DeepSeek Blue Error] {resp.get('error')}")

    def process_findings_file(self, findings_json_path: str, output_path: str) -> Dict[str, Any]:
        p = Path(findings_json_path).resolve()
        findings = json.loads(p.read_text(encoding="utf-8"))
        results = []
        for v in findings.get("vulnerabilities", []):
            print(f"[InversionCore -> Alfa] İşleniyor: {v.get('vuln_id')} ({v.get('rule_id')})...")
            poc = self.analyze_vulnerability_poc(v)
            patch = self.generate_ast_patch(v)
            results.append({"vuln_id": v.get("vuln_id"), "rule_id": v.get("rule_id"), "red_team_analysis": poc, "blue_team_patch": patch})
        out = {"alfa_status": "COMPLETED", "processed": len(results), "results": results}
        Path(output_path).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
        return out

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Kullanım: python3 alfa_bridge.py <findings.json> <output.json>")
        sys.exit(1)
    AlfaBridge().process_findings_file(sys.argv[1], sys.argv[2])
