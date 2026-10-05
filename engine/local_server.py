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
1. GÜÇ VE GEÇİŞ TAVANI: 2x120 kW ({cap['total_power_kw']} kW). Teorik Tavan: {cap['theoretical_monthly_kwh']:,} kWh/ay.
   - 148 Araç Hedefi: Kapasite Kullanımı %{cap['target_utilization_pct']} ({cap['verdict']}).
   - 190.000 kWh Filo Talebi: İstasyon tavanını tek başına %{cap['fleet_overload_pct']} aşmaktadır (Fiziksel Tavan İhlali).
2. HATA AĞACI (MCS): Asgari Kesme Kümeleri = {fta['minimal_cut_sets']}.
   - Risk Yayılım Hattı (Propagation Path): {fta['risk_propagation_paths']} (Şahsi kefaletin şirket iflasını kurucu evine bağlama hattı).
3. RUNWAY & ABSORBING BARRIER: {dyn['initial_runway_months']} ay (610k TL Kasa / -440k TL Yakım). Kasa Sıfırlanması: {dyn['absorbing_barrier_month']}. Ay.
4. OYUN TEORİSİ (NASH DENGESİ): {gt['equilibrium']} - {gt['strategic_finding']}
5. SÖZLEŞME TAVANI FORMÜLÜ: Efektif Kapasite (%75) x Max Konsantrasyon (%60) = {con['safe_max_single_contract_kwh']:,} kWh/ay ({con['safe_band_label']}).
6. GELİR ATFETME DİSİPLİNİ: Enerji katkısı 230.394 TL, enerji dışı faaliyet katkısı ≈430.000 TL.
   [Çıkarım Uyarısı]: 430k TL doğrudan detailing kârı değildir; detailing, seramik, lounge toplamıdır. Ayrı P&L olmadan sadece detailing'e atfedilemez.
"""

class ForensicStreamHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path == "/" or path == "/index.html":
            return os.path.abspath("public/index.html")
        elif path == "/logo.png":
            return os.path.abspath("public/logo.png")
        return super().translate_path(path)

    def do_POST(self):
        if self.path == "/api/inversion/stream":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body) if body else {}
            user_text = data.get("scenario", "").strip()

            evidence_dossier = generate_evidence_dossier(user_text)

            system_prompt = (
                "Sen INVERSIONCORE Baş Sistemik Güvenilirlik Mühendisi ve Kıdemli Adli Karar Analistisin. "
                "Havacılık (NTSB), Nükleer Güvenlik (PRA/Fault Tree) ve Nassim Taleb'in Via Negativa disipliniyle çalışırsın.\n\n"
                "TEMEL DİSİPLİNLERİN:\n"
                "1. KANIT İLE ÇIKARIMI BİRBİRİNE KARIŞTIRMA: Kanıtlanmış veriyle varsayımsal çıkarımları kesin olarak etiketle.\n"
                "2. KESİN TEKNİK TERMİNOLOJİ: 'Termodinamik' deme; 'Güç, Akış ve Kapasite Tavanı (Power / Throughput Capacity Ceiling)' de.\n"
                "3. FORMÜLE DAYALI SINIRLAR: Keyfî tavan belirleme; sınırları 'Efektif Kapasite x Müşteri Konsantrasyonu' formülüyle sun.\n"
                "4. DİNAMİK STOP-LOSS: Kaba OR mantığı kullanma; gerçekleşen KPI'lar ile ileri dönem imzalı kontratları birlikte değerlendir.\n"
                "5. ÜSLUP: Soğuk, net, analitik, sıfır yapay zeka gevezeliği, yüksek rütbeli adli kaza kırım raporu ciddiyetinde Türkçe."
            )

            forensic_prompt = f"""KULLANICI VAKA DOSYASI:
======================================================================
{user_text}
======================================================================

{evidence_dossier}

GÖREV:
Yukarıdaki doğrulanmış adli kanıt dosyasını kullanarak, 
aşağıdaki 5 bloklu 'PRODUCTION-GRADE ADLİ KAZA KIRIM VE TERSİNE ÇÖKÜŞ RAPORU'nu eksiksiz üret:

══════════════════════════════════════════════════════════════════════
INVERSIONCORE | PRODUCTION-GRADE ADLİ KAZA KIRIM RAPORU
DOSYA: BAYRAKLI EV & MULTI-SERVICE HUB | DEĞERLENDİRME: TERSİNE ÇÖZÜMLEME
══════════════════════════════════════════════════════════════════════

[1] GÜÇ, AKIŞ VE KAPASİTE TAVANI ANALİZİ (POWER / THROUGHPUT CAPACITY CEILING)
- 2x120 kW cihazın 172.800 kWh teorik tavanı karşısında 190.000 kWh'lik filo talebinin fiziksel imkânsızlığı (%109.9 tavan aşımı).
- 148 araç/gün seviyesinin teorik kapasitenin %97.64'ünü gerektirmesi; şarj eğrisi düşüşü, soket tak-çıkar süreleri ve talep dalgalanmaları nedeniyle operasyonel olarak neden sürdürülemez olduğu.

[2] BİRİM İKTİSAT VE GELİR ATFETME DİSİPLİNİ (ATTRIBUTION DISCIPLINE)
- 43 araç/gün ve 4.70 TL/kWh marj ile enerji katkısının 230.394 TL/ay oluşu.
- [Çıkarım Uyarısı]: ~430k TL enerji dışı katkının doğrudan detailing'e atfedilemeyeceği (seramik, lounge, AC şarj ayrımı yapılmadığı sürece yanıltıcı olacağı).

[3] HATA AĞACI VE ASGARİ KESME KÜMELERİ (MINIMAL CUT SETS & RISK PROPAGATION)
- MCS-1 (Sistemik Likidite Ölümü): [Negatif Katkı Açığı (-440k TL/ay)] ^ [Runway (1.39 ay) < Turnaround Süresi]
- MCS-2 / Risk Yayılım Hattı (Risk Propagation Path): [Negatif Operasyonel Nakit Akışı] ^ [Şahsi Kefaletli Kredi] -> Şirket başarısızlığının kurucuların şahsi bilançosuna ve evlerine sıçraması.
- MCS-3 (Zehirli Marj Kapanı): [12 Ay Sabit Fiyat (11.30 TL)] ^ [Volatil Elektrik Maliyeti (10.20 -> 12.00 TL)] -> Negatif katkı (-0.70 TL/kWh) ile satıldıkça iflası hızlandırma.

[4] SÖZLEŞME GÜVENLİK SINIRI VE VİA NEGATİVA PROTOKOLÜ
- Filo Karşı Teklif Formülü: Contract Cap = Efektif Kapasite (%75 = 129.600 kWh) x Maksimum Tek Müşteri Riski (%60) = 77.760 kWh (≈80-100 MWh/ay bandı).
- Fiyatlama Formülü: Fiyat = Efektif Enerji Maliyeti + minimum 3.00 TL/kWh (Aylık endeksli güncelleme, sabit fiyat YASAK).
- Derhal Kesilmesi Gereken Devreler: Şahsi kefaletli kredi KESİN RED; 11.50 TL fiyat kırma savaşı KESİN RED (Nash Dengesi gereği strictly dominated); kurucu maaşları derhal 0'a çekilmeli.

[5] DİNAMİK STOP-LOSS VE TASFİYE PROTOKOLÜ (REALIZED + FORWARD CONTRACTED ECONOMICS)
- Gün 60 Kapısı (Sermaye Dondurma): 4 şarttan en az 2'si sağlanmıyorsa yeni sermaye girişi kesin olarak yasaklanır (Araç >= 60, İmzalı Filo >= 75 MWh, Katkı Run-Rate >= 750k TL, Enerji Dışı Pozitif Marj).
- Gün 90 Kapısı (Tasfiye İnfazı): (Gerçekleşen Katkı + 90 Günlük İmzalı Sözleşme Katkısı) < Normalize Edilmiş OPEX ise; derhal donanım 2.05M TL'ye satılır, kira feshedilir ve şirket tasfiye edilir.
"""

            payload = {
                "model": "qwen2.5-coder-14b-abliterated",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": forensic_prompt}
                ],
                "temperature": 0.15,
                "max_tokens": 4096,
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
                with urllib.request.urlopen(req, timeout=300) as resp:
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
    print("==========================================================")
    print(f"    INVERSIONCORE + ALFA PHYSICAL PHYSICS ENGINE: http://localhost:{PORT}")
    print("    [6 Motor Aktif] FaultTree, Throughput, Dynamics, FatTail, Nashpy, ContractCap")
    print("    [Durum] Deterministik Adli Kanıt Zinciri Devrede")
    print("==========================================================")
    HTTPServer(("", PORT), ForensicStreamHandler).serve_forever()
