import json
import os
import sys
import time
import urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler
from engine.inversion_physics_suite import InversionPhysicsSuite

PORT = 8085
MODEL_ENDPOINT = "http://localhost:8080/v1/chat/completions"
SUITE = InversionPhysicsSuite()

def generate_evidence_dossier(text):
    audit = SUITE.run_full_inversion_audit(text)
    fta = audit["fta"]
    cap = audit["capacity"]
    dyn = audit["dynamics"]
    gt = audit["game_theory"]
    con = audit["contract_cap"]

    return f"""[DETERMİNİSTİK HESAPLANMIŞ KANIT ZİNCİRİ]
1. KAPASİTE TAVANI: Teorik Tavan: {cap['theoretical_monthly_kwh']:,} Birim/Ay. Durum: {cap['verdict']}.
2. HATA AĞACI (MCS): Asgari Kesme Kümeleri = {fta['minimal_cut_sets']}.
   - Risk Yayılım Hattı (Propagation Path): {fta['risk_propagation_paths']}.
3. RUNWAY (NAKİT YAKIM HIZI): {dyn['initial_runway_months']} ay (Kasa Sıfırlanması: {dyn['absorbing_barrier_month']}. Ay).
4. OYUN TEORİSİ: {gt['equilibrium']} - {gt['strategic_finding']}
5. RİSK TAVANI: {con['safe_max_single_contract_kwh']:,} Birim ({con['safe_band_label']}).
"""

class ForensicStreamHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path == "/" or path == "/index.html":
            return os.path.abspath("public/index.html")
        elif path == "/logo.png":
            return os.path.abspath("public/logo.png")
        return super().translate_path(path)


    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):

        if self.path == "/api/inversion/stream":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body) if body else {}
            user_text = data.get("scenario", "").strip()

            evidence_dossier = generate_evidence_dossier(user_text)

            system_prompt = (
                "Sen INVERSIONCORE Baş Sistemik Güvenilirlik Mühendisi ve Kıdemli Adli Karar Analistisin. "
                "Havacılık (NTSB), Nükleer Güvenlik (PRA/Fault Tree) disipliniyle çalışırsın.\n\n"
                "ÜSLUP: Soğuk, net, analitik, sıfır yapay zeka gevezeliği, yüksek rütbeli adli kaza kırım raporu ciddiyetinde Türkçe."
            )

            forensic_prompt = f"""KULLANICI VAKA DOSYASI:
======================================================================
{user_text}
======================================================================

{evidence_dossier}

GÖREV: Yukarıdaki doğrulanmış adli kanıt dosyasını kullanarak 'ADLİ KAZA KIRIM VE TERSİNE ÇÖKÜŞ RAPORU'nu eksiksiz üret.
Aşırı kibar olmadan, rakamları ve sınırları doğrudan ver.
"""
            payload = {
                "model": "coder_candidate",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": forensic_prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 1024,
                "stream": True
            }

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            req = urllib.request.Request(
                MODEL_ENDPOINT,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    for line in resp:
                        self.wfile.write(line)
                        self.wfile.flush()
            except Exception as e:
                err_msg = json.dumps({"choices": [{"delta": {"content": f"\n\n[HATA: {str(e)}]"}}]})
                self.wfile.write(f"data: {err_msg}\n\n".encode("utf-8"))
                self.wfile.flush()
        else:
            self.send_error(404)

if __name__ == "__main__":
    HTTPServer.allow_reuse_address = True
    HTTPServer(("", PORT), ForensicStreamHandler).serve_forever()
