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
    def __init__(self, config: str = "p/security-audit"):
        self.semgrep = SemgrepRunner(config=config)
        self.ast = TreeSitterASTAnalyzer()

    def analyze(self, target_path: str, config: str = None) -> dict:
        target = Path(target_path).resolve()
        scan_res = self.semgrep.run_scan(str(target), custom_rules_path=config)
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
                    "red_team_deepseek": {
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
    parser.add_argument("--config", "--semgrep-config", "--custom-rules", dest="config", default="p/security-audit", help="Semgrep ruleset")
    parser.add_argument("--output", default="findings.json", help="Output JSON path")
    args = parser.parse_args()

    analyzer = InversionCoreAnalyzer(config=args.config)
    res = analyzer.analyze(args.target, config=args.config)
    formatted = json.dumps(res, indent=2, ensure_ascii=False)
    
    Path(args.output).write_text(formatted, encoding="utf-8")
    print(f"[InversionCore] Tarama tamamlandı. {res['summary']['total_vulnerabilities']} zafiyet bulundu -> {args.output}")
