#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional

ALFA_LOCAL_ENDPOINT = os.getenv("ALFA_LOCAL_ENDPOINT", "http://127.0.0.1:8081/v1/chat/completions")

class AlfaBridge:
    def __init__(self, alfa_endpoint: str = ALFA_LOCAL_ENDPOINT):
        self.alfa_endpoint = alfa_endpoint

    def _call_llm(self, endpoint: str, messages: list, model: str = "coder_candidate", temperature: float = 0.0) -> Dict[str, Any]:
        payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": 1024}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(endpoint, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"status": "error", "error": f"Yerel Alfa motoruna bağlanılamadı ({endpoint}): {str(e)}"}

    def analyze_vulnerability_poc(self, vuln_data: Dict[str, Any]) -> str:
        ast_scope = vuln_data.get("ast_scope", {})
        messages = [
            {"role": "system", "content": "Sen InversionCore Adli Güvenlik Mimarı Alfa motorusun. AST kapsamını incele, zafiyet mekanizmasını ve kaza kırım senaryosunu Türkçe olarak açıkla."},
            {"role": "user", "content": json.dumps({"rule_id": vuln_data.get("rule_id"), "symbol": ast_scope.get("enclosing_symbol"), "code": ast_scope.get("full_scope_code"), "params": ast_scope.get("parameters", [])})}
        ]
        resp = self._call_llm(self.alfa_endpoint, messages)
        return resp.get("choices", [{}])[0].get("message", {}).get("content", f"[Alfa Red Error] {resp.get('error')}")

    def generate_ast_patch(self, vuln_data: Dict[str, Any]) -> str:
        ast_scope = vuln_data.get("ast_scope", {})
        messages = [
            {"role": "system", "content": "Sen InversionCore Savunma Mühendisi Alfa motorusun. Fonksiyon imzasını ve iş mantığını koruyarak bildirilen zafiyeti gideren güvenli bir kod yaması üret."},
            {"role": "user", "content": json.dumps({"rule_id": vuln_data.get("rule_id"), "symbol": ast_scope.get("enclosing_symbol"), "code": ast_scope.get("full_scope_code"), "params": ast_scope.get("parameters", [])})}
        ]
        resp = self._call_llm(self.alfa_endpoint, messages)
        return resp.get("choices", [{}])[0].get("message", {}).get("content", f"[Alfa Blue Error] {resp.get('error')}")

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
