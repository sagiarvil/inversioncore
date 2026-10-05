#!/usr/bin/env python3
import os
import sys
import time
import json
import urllib.request
import urllib.error
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT / "engine"))
from premortem_engine import RealityInversionEngine

FIRESTORE_URL = "https://firestore.googleapis.com/v1/projects/dilekce-7956e/databases/(default)/documents/inversioncore_tasks"

class DualCoreWorker:
    def __init__(self, poll_interval: int = 2):
        self.poll_interval = poll_interval
        self.premortem_engine = RealityInversionEngine()
        self.running = True

    def _http_get(self, url: str) -> dict:
        req = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"error": str(e)}

    def _http_patch(self, doc_name: str, fields: dict, update_mask: list) -> dict:
        mask_params = "&".join([f"updateMask.fieldPaths={f}" for f in update_mask])
        url = f"https://firestore.googleapis.com/v1/{doc_name}?{mask_params}"
        body = json.dumps({"fields": fields}).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="PATCH")
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"error": str(e)}

    def poll_and_process(self):
        print("==========================================================")
        print("    InversionCore - Dual-Core Alfa Worker Başlatıldı")
        print("    [Core 01]: Fiziksel Kod Güvenliği (Semgrep/Tree-sitter)")
        print("    [Core 02]: İş ve Gerçeklik Pre-Mortem (DeepSeek Coder)")
        print("    Durum: Görev kuyruğu dinleniyor...")
        print("==========================================================")

        while self.running:
            try:
                res = self._http_get(FIRESTORE_URL)
                docs = res.get("documents", [])
                for doc in docs:
                    doc_name = doc.get("name")
                    fields = doc.get("fields", {})
                    status = fields.get("status", {}).get("stringValue")

                    if status == "PENDING":
                        doc_id = doc_name.split("/")[-1]
                        mode = fields.get("mode", {}).get("stringValue", "reality")
                        payload_text = fields.get("input", {}).get("stringValue", "") or fields.get("code", {}).get("stringValue", "")
                        print(f"\n[+] Yeni Görev [{mode.upper()}]: {doc_id}")
                        if mode == "reality":
                            self.process_reality_task(doc_name, payload_text)
                        else:
                            self.process_code_task(doc_name, payload_text)
                time.sleep(self.poll_interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                time.sleep(self.poll_interval)

    def process_reality_task(self, doc_name: str, text: str):
        self._http_patch(doc_name, {"status": {"stringValue": "ALFA_PROCESSING"}}, ["status"])
        print("  -> DeepSeek Coder Pre-Mortem çöküş simülasyonu çalıştırıyor...")
        analysis_res = self.premortem_engine.invert_problem(text, domain="Business & Strategy Inversion")
        if analysis_res.get("status") == "SUCCESS":
            analysis = analysis_res.get("analysis", {})
            self._http_patch(doc_name, {
                "status": {"stringValue": "COMPLETED"},
                "premortem_analysis": {
                    "mapValue": {
                        "fields": {
                            "catastrophe_vectors": {"arrayValue": {"values": [{"mapValue": {"fields": {"vector_id": {"stringValue": v.get("vector_id","")}, "name": {"stringValue": v.get("name","")}, "mechanism": {"stringValue": v.get("mechanism","")}, "lethality": {"stringValue": v.get("lethality","")}}}} for v in analysis.get("catastrophe_vectors", [])]}},
                            "anti_conditions": {"arrayValue": {"values": [{"mapValue": {"fields": {"id": {"stringValue": a.get("id","")}, "fatal_action": {"stringValue": a.get("fatal_action","")}, "impact": {"stringValue": a.get("impact","")}}}} for a in analysis.get("anti_conditions", [])]}},
                            "via_negativa_protocol": {"arrayValue": {"values": [{"mapValue": {"fields": {"rule_id": {"stringValue": r.get("rule_id","")}, "rule": {"stringValue": r.get("rule","")}, "rationale": {"stringValue": r.get("rationale","")}}}} for r in analysis.get("via_negativa_protocol", [])]}},
                            "survival_thresholds": {"arrayValue": {"values": [{"mapValue": {"fields": {"metric": {"stringValue": s.get("metric","")}, "fatal_limit": {"stringValue": s.get("fatal_limit","")}, "safe_operating_bound": {"stringValue": s.get("safe_operating_bound","")}}}} for s in analysis.get("survival_thresholds", [])]}}
                        }
                    }
                }
            }, ["status", "premortem_analysis"])
            print("  -> [✓] Pre-Mortem analizi tamamlandı ve Firestore'a yüklendi.")
        else:
            self._http_patch(doc_name, {"status": {"stringValue": "FAILED"}, "error": {"stringValue": analysis_res.get("error", "Unknown error")}}, ["status", "error"])

    def process_code_task(self, doc_name: str, code: str):
        self._http_patch(doc_name, {"status": {"stringValue": "PROCESSING"}}, ["status"])
        target_file = PROJECT_ROOT / "tests" / "incoming_scan.py"
        target_file.write_text(code, encoding="utf-8")
        findings_file = PROJECT_ROOT / "incoming_findings.json"
        alfa_results_file = PROJECT_ROOT / "incoming_alfa_results.json"
        subprocess.run([sys.executable, str(PROJECT_ROOT / "engine" / "core_analyzer.py"), "--target", str(target_file), "--config", "p/security-audit", "--output", str(findings_file)], check=True)
        scan_data = json.loads(findings_file.read_text(encoding="utf-8"))
        vuln_count = scan_data.get("summary", {}).get("total_vulnerabilities", 0)
        if vuln_count == 0:
            self._http_patch(doc_name, {"status": {"stringValue": "COMPLETED"}, "results": {"arrayValue": {"values": []}}}, ["status", "results"])
            return
        self._http_patch(doc_name, {"status": {"stringValue": "ALFA_PROCESSING"}}, ["status"])
        subprocess.run([sys.executable, str(PROJECT_ROOT / "engine" / "alfa_bridge.py"), str(findings_file), str(alfa_results_file)], check=True)
        alfa_data = json.loads(alfa_results_file.read_text(encoding="utf-8"))
        results_formatted = [{"mapValue": {"fields": {"vuln_id": {"stringValue": r.get("vuln_id","")}, "rule_id": {"stringValue": r.get("rule_id","")}, "ast_symbol": {"stringValue": r.get("ast_symbol","")}, "red_team_analysis": {"stringValue": r.get("red_team_analysis","")}, "blue_team_patch": {"stringValue": r.get("blue_team_patch","")}}}} for r in alfa_data.get("results", [])]
        self._http_patch(doc_name, {"status": {"stringValue": "COMPLETED"}, "results": {"arrayValue": {"values": results_formatted}}}, ["status", "results"])
        print(f"  -> [✓] Kod zafiyeti yamalandı: {doc_name.split('/')[-1]}")

if __name__ == "__main__":
    DualCoreWorker().poll_and_process()
