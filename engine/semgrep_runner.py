#!/usr/bin/env python3
import sys
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional

class SemgrepRunner:
    def __init__(self, config: str = "p/security-audit", timeout_sec: int = 300):
        self.config = config
        self.timeout_sec = timeout_sec
        proj_bin = Path(__file__).parent.parent / "bin" / "semgrep"
        self.semgrep_bin = str(proj_bin) if proj_bin.is_file() else (shutil.which("semgrep") or "/opt/homebrew/bin/semgrep")

    def run_scan(self, target_path: str, custom_rules_path: Optional[str] = None) -> Dict[str, Any]:
        target = Path(target_path).resolve()
        if not target.exists():
            return {"status": "error", "error": f"Target not found: {target_path}", "findings": []}

        rule_config = custom_rules_path if custom_rules_path and Path(custom_rules_path).exists() else self.config

        cmd = [self.semgrep_bin, "scan", "--config", rule_config, "--json", "--quiet", str(target)]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout_sec)
            if res.returncode not in (0, 1) and not res.stdout:
                return {"status": "error", "error": f"Semgrep exit code {res.returncode}: {res.stderr.strip()}", "findings": []}
            raw = json.loads(res.stdout) if res.stdout else {"results": []}
            return self._normalize(raw, str(target))
        except Exception as e:
            return {"status": "error", "error": str(e), "findings": []}

    def _normalize(self, raw: Dict[str, Any], target_str: str) -> Dict[str, Any]:
        findings = []
        for it in raw.get("results", []):
            ext = it.get("extra", {})
            findings.append({
                "engine": "semgrep",
                "rule_id": it.get("check_id", "rule"),
                "severity": ext.get("severity", "WARNING").upper(),
                "message": ext.get("message", "").strip(),
                "file_path": it.get("path", ""),
                "start": it.get("start", {}),
                "end": it.get("end", {}),
                "code_snippet": ext.get("lines", ""),
                "metadata": ext.get("metadata", {})
            })
        return {"status": "success", "engine": "semgrep", "target": target_str, "total_findings": len(findings), "findings": findings}
