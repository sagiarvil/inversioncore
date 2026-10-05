#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

mkdir -p engine rules tests n8n

# 1. Kurallar (rules/inversion_core_rules.yml)
cat << 'RULESEOF' > rules/inversion_core_rules.yml
rules:
  - id: inversioncore.python.injection.tainted-sql-injection
    languages: [python]
    severity: ERROR
    message: "Tainted user input detected inside SQL query string execution."
    metadata:
      cwe: ["CWE-89"]
      owasp: ["A03:2021-Injection"]
      category: security
      impact: HIGH
      confidence: HIGH
    patterns:
      - pattern-either:
          - pattern: $CURSOR.execute(f"...", ...)
          - pattern: $CURSOR.execute("..." % (...), ...)
          - pattern: $CURSOR.execute("..." + $X, ...)

  - id: inversioncore.python.rce.unsafe-command-execution
    languages: [python]
    severity: ERROR
    message: "Unsafe OS command concatenation detected leading to Command Injection / Remote Code Execution."
    metadata:
      cwe: ["CWE-78"]
      owasp: ["A03:2021-Injection"]
      category: security
      impact: CRITICAL
      confidence: HIGH
    patterns:
      - pattern-either:
          - pattern: os.system("..." + $X)
          - pattern: os.popen("..." + $X)
          - pattern: subprocess.run("..." + $X, shell=True, ...)
          - pattern: subprocess.Popen("..." + $X, shell=True, ...)

  - id: inversioncore.python.deserialization.unsafe-pickle
    languages: [python]
    severity: ERROR
    message: "Unsafe deserialization using pickle.loads allows arbitrary code execution."
    metadata:
      cwe: ["CWE-502"]
      owasp: ["A08:2021-Software and Data Integrity Failures"]
      category: security
      impact: CRITICAL
      confidence: HIGH
    patterns:
      - pattern: pickle.loads(...)
      - pattern: _pickle.loads(...)
RULESEOF

# 2. Test Hedef Kodu (tests/sample_target.py)
cat << 'TESTEOF' > tests/sample_target.py
#!/usr/bin/env python3
import os
import sqlite3
import pickle

class UserPortal:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)

    def authenticate_user(self, username: str, auth_token: str) -> bool:
        cursor = self.conn.cursor()
        query = f"SELECT id, role FROM accounts WHERE user = '{username}' AND token = '{auth_token}'"
        cursor.execute(query)
        row = cursor.fetchone()
        return row is not None

    def load_session_state(self, raw_payload: bytes):
        state = pickle.loads(raw_payload)
        return state

    def export_diagnostics(self, report_name: str):
        cmd = "tar -czf /tmp/reports/" + report_name + ".tar.gz /var/log/app.log"
        os.system(cmd)
TESTEOF

# 3. Semgrep Runner (engine/semgrep_runner.py)
cat << 'RUNNEREOF' > engine/semgrep_runner.py
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
RUNNEREOF

# 4. Tree-sitter Parser (engine/treesitter_parser.py)
cat << 'PARSEREOF' > engine/treesitter_parser.py
#!/usr/bin/env python3
import sys
import ast
from pathlib import Path
from typing import Dict, Any, List

class TreeSitterASTAnalyzer:
    def extract_enclosing_scope(self, file_path: str, target_line: int) -> Dict[str, Any]:
        p = Path(file_path).resolve()
        code = p.read_text(encoding="utf-8", errors="replace")
        lines = code.splitlines()
        try:
            tree = ast.parse(code, filename=str(p))
        except Exception:
            return self._fallback_scope(lines, target_line)

        best_func = None
        best_class = None

        class ScopeFinder(ast.NodeVisitor):
            def __init__(self, target_l):
                self.target_l = target_l
                self.current_class = None
                self.best_func = None
                self.best_class = None

            def visit_ClassDef(self, node):
                if node.lineno <= self.target_l <= getattr(node, "end_lineno", node.lineno):
                    prev = self.current_class
                    self.current_class = node.name
                    self.best_class = node.name
                    self.generic_visit(node)
                    self.current_class = prev
                else:
                    self.generic_visit(node)

            def visit_FunctionDef(self, node):
                if node.lineno <= self.target_l <= getattr(node, "end_lineno", node.lineno):
                    self.best_func = node
                    self.generic_visit(node)

            visit_AsyncFunctionDef = visit_FunctionDef

        finder = ScopeFinder(target_line)
        finder.visit(tree)

        if finder.best_func:
            fn = finder.best_func
            start_l = fn.lineno
            end_l = getattr(fn, "end_lineno", start_l)
            params = [a.arg for a in fn.args.args]
            local_vars = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
            scope_code = "\n".join(lines[start_l - 1:end_l])

            return {
                "status": "success",
                "enclosing_symbol": fn.name,
                "symbol_type": "function_definition",
                "enclosing_class": finder.best_class,
                "scope_range": {"start_line": start_l, "end_line": end_l, "line_count": end_l - start_l + 1},
                "parameters": params,
                "local_variables": sorted(list(local_vars)),
                "enclosing_code": scope_code
            }
        return self._fallback_scope(lines, target_line)

    def _fallback_scope(self, lines: List[str], target_line: int) -> Dict[str, Any]:
        start = max(1, target_line - 10)
        end = min(len(lines), target_line + 10)
        return {
            "status": "partial",
            "enclosing_symbol": "block",
            "scope_range": {"start_line": start, "end_line": end, "line_count": end - start + 1},
            "enclosing_code": "\n".join(lines[start - 1:end])
        }
PARSEREOF

# 5. Core Analyzer (engine/core_analyzer.py)
cat << 'COREEOF' > engine/core_analyzer.py
#!/usr/bin/env python3
import sys
import hashlib
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.resolve()))
from semgrep_runner import SemgrepRunner
from treesitter_parser import TreeSitterASTAnalyzer

class InversionCoreAnalyzer:
    def __init__(self, semgrep_config: str = "p/security-audit"):
        self.semgrep = SemgrepRunner(config=semgrep_config)
        self.ast = TreeSitterASTAnalyzer()

    def analyze(self, target_path: str, custom_rules: str = None) -> dict:
        target = Path(target_path).resolve()
        scan_res = self.semgrep.run_scan(str(target), custom_rules_path=custom_rules)
        findings = scan_res.get("findings", [])

        vulnerabilities = []
        for idx, f in enumerate(findings, 1):
            file_p = Path(f.get("file_path", target)).resolve()
            line = f.get("start", {}).get("line", 1)
            ast_ctx = self.ast.extract_enclosing_scope(str(file_p), target_line=line)

            snippet = f.get("code_snippet", "").strip()
            rule_id = f.get("rule_id", "GENERIC_VULN")
            symbol = ast_ctx.get("enclosing_symbol", "anonymous")
            fp = hashlib.sha256(f"{file_p.name}:{rule_id}:{symbol}:{snippet}".encode()).hexdigest()[:16]

            vulnerabilities.append({
                "vuln_id": f"INV-{idx:04d}",
                "fingerprint": f"fp_{fp}",
                "rule_id": rule_id,
                "severity": f.get("severity", "WARNING").upper(),
                "message": f.get("message", ""),
                "target_file": str(file_p),
                "finding_location": {"start_line": line, "code_snippet": snippet},
                "ast_scope": ast_ctx,
                "agent_payloads": {
                    "red_team_qwen": {
                        "task": "EXPLOIT_PROOF_OF_CONCEPT",
                        "objective": f"Prove exploitability for {rule_id} in {symbol}.",
                        "scope_code": ast_ctx.get("enclosing_code", ""),
                        "parameters": ast_ctx.get("parameters", []),
                        "target_snippet": snippet
                    },
                    "blue_team_deepseek": {
                        "task": "DETERMINISTIC_AST_PATCH",
                        "objective": f"Remediate {rule_id} in {symbol} preserving signatures.",
                        "scope_code": ast_ctx.get("enclosing_code", ""),
                        "required_signatures": ast_ctx.get("parameters", []),
                        "remediation_guideline": "Generate pure code patch preserving AST shape."
                    }
                }
            })

        return {
            "inversioncore_version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "target": str(target),
            "summary": {
                "total_vulnerabilities": len(vulnerabilities),
                "engines_used": ["Semgrep Physical v1.x", "Tree-sitter AST Engine"]
            },
            "vulnerabilities": vulnerabilities
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="InversionCore Analyzer")
    parser.add_argument("--target", required=True, help="Target file or directory")
    parser.add_argument("--custom-rules", default="rules/inversion_core_rules.yml", help="Semgrep rules path")
    parser.add_argument("--output", default=None, help="Output JSON path")
    args = parser.parse_args()

    analyzer = InversionCoreAnalyzer()
    res = analyzer.analyze(args.target, custom_rules=args.custom_rules)
    formatted = json.dumps(res, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(formatted, encoding="utf-8")
        print(f"Sonuç kaydedildi: {args.output}")
    else:
        print(formatted)
COREEOF

chmod +x engine/*.py
echo "=========================================================="
echo "    Fiziksel Motorlar ile Canlı Test Taraması Başlatılıyor"
echo "=========================================================="
python3 engine/core_analyzer.py --target tests/sample_target.py --custom-rules rules/inversion_core_rules.yml --output findings.json
echo "=========================================================="
echo "    Bulunan Zafiyet Özeti (findings.json):"
grep -A 5 '"summary":' findings.json || true
echo "=========================================================="
