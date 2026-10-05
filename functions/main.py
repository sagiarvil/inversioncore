import json
import os
import requests
from firebase_functions import https_fn
from flask import Response
from engine.inversion_physics_suite import InversionPhysicsSuite

SUITE = InversionPhysicsSuite()
MODEL_ENDPOINT = "https://api.deepseek.com/chat/completions"
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

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

@https_fn.on_request(timeout_sec=120)
def stream_inversion(req: https_fn.Request) -> https_fn.Response:
    if req.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        return https_fn.Response('', status=204, headers=headers)

    data = req.get_json(silent=True) or {}
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
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": forensic_prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
        "stream": True
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }

    def generate():
        try:
            with requests.post(MODEL_ENDPOINT, json=payload, headers=headers, stream=True, timeout=120) as resp:
                for line in resp.iter_lines():
                    if line:
                        yield line.decode('utf-8') + "\n"
        except Exception as e:
            err_msg = json.dumps({"choices": [{"delta": {"content": f"\\n\\n[HATA: {str(e)}]"}}]})
            yield f"data: {err_msg}\n\n"

    res = Response(generate(), mimetype='text/event-stream')
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Cache-Control'] = 'no-cache'
    return res
