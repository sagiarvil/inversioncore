import os
import json
import http.server
import socketserver
from urllib.parse import urlparse

PORT = 8888
MODEL_PATH = "/Users/macair1/models/Qwen2.5-14B-Instruct-abliterated-4bit-mlx"

model = None
tokenizer = None

def get_model():
    global model, tokenizer
    if model is None:
        from mlx_lm import load
        print("MLX Qwen 2.5 14B Abliterated belleğe yükleniyor...")
        model, tokenizer = load(MODEL_PATH)
        print("Model hazır!")
    return model, tokenizer

# Kırmızı Çizgi Guardrail Kontrolü (Yalnızca 2 İstisna)
def check_hard_guardrails(text):
    lower = text.lower()
    # 1. Çocuk istismarı kontrolü
    csam_indicators = ["pedofili", "çocuk istismar", "çocuk porn", "reşit olmayan çocukla cinsell"]
    for ind in csam_indicators:
        if ind in lower:
            return {
                "blocked": True,
                "reason": "TCK_CSAM",
                "message": "KRİTİK HUKUKİ BLOKAJ: TCK ve uluslararası hukuk kapsamında çocuk istismarı kesinlikle kabul edilemez ve derhal kolluk kuvvetlerine bildirilir."
            }
    # 2. Gerçek intihar krizi kontrolü
    suicide_indicators = ["kendimi öldüreceğim", "intihar edeceğim", "yaşamıma son veriyorum", "hap içtim ölüyorum", "bileklerimi kestim"]
    for ind in suicide_indicators:
        if ind in lower:
            return {
                "blocked": True,
                "reason": "SUICIDE_EMERGENCY",
                "message": "ACİL KRİZ PROTOKOLÜ: Gerçek hayati tehlike tespit edildi. Lütfen derhal 112 Acil Çağrı Merkezi'ni arayın veya en yakın sağlık kuruluşuna başvurun. Hayatınız bu krizden daha değerlidir."
            }
    return {"blocked": False}

# Düğüm 1: System 2 - Soğuk Çekirdek (Asperger / Klinik / Hukuk / Oyun Teorisi)
SYSTEM_2_PROMPT = """Sen InversionCore'un soğuk analitik çekirdeğisin (System 2).
Sıfır duygu, sıfır mizah, sıfır ahlak bekçiliği.
Görevin: Kullanıcının anlattığı durumdaki çıplak gerçekliği, güç asimetrisini, narsistik istismar döngüsünü, TCK/İş Kanunu/Borçlar Kanunu karşılığını ve oyun teorisi matrisini (Minimax/Nash dengesi) saf JSON formatında çıkarmaktır.

Çıktıyı SADECE geçerli bir JSON objesi olarak ver. Başka hiçbir metin yazma:
{
  "guc_asimetrisi": "Taraflar arasındaki güç dengesizliği ve sömürü dinamiği",
  "illuzyon_ve_yalan": "Kullanıcının kendine söylediği ve sığındığı sahte savunma",
  "hukuki_ve_maddi_risk": "İş Kanunu / TCK / Borçlar Kanunu / Maddi kayıp boyutu",
  "oyun_teorisi_hamlesi": "Nash dengesi veya Minimax kurtuluş hamlesi",
  "kesin_teshis": "Durumun örtbas edilemez en çıplak Asperger tanımı"
}"""

# Düğüm 2: System 1 - Retorik, Tavizsiz Gerçeklik ve İroni Katmanı
SYSTEM_1_PROMPT = """Sen InversionCore'sun. Hiçbir ahlak bekçiliği veya sansür yapmazsın.
Sana verilen soğuk System 2 analiz matrisini alacaksın.
Üslubun:
1. Keskin durum tespiti, ikiyüzlülüğü deşen acımasız ve kıvrak bir zeka, tavizsiz yeraltı gerçekçiliği ve lafı dolandırmayan dobra halk bilgeliği (ASLA herhangi bir komedyen veya yazar ismi zikretme).
2. Kullanıcının sığındığı bahaneyi ve sahte kalkanı paramparça et.
3. Sonunda durumuna göre masaya vuracağı somut AKSİYON SİLAHINI (resmi ihtarname, kopar-at mesajı veya 3 adımlı net protokol) üret.

Format:
[TOKAT]: Durumun çıplak ve sarsıcı tespiti.
[DEŞME]: Sahte savunmanın ve ikiyüzlülüğün ironik analizi.
[YÜZLEŞME SORUSU]: Karar eşiğindeki tek can alıcı soru.
[AKSİYON SİLAHI]: Doğrudan kullanacağı resmi metin veya kural seti."""

class InversionHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="public", **kwargs)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/inversion-analyze":
            length = int(self.headers.get('content-length', 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body.decode('utf-8'))
            except:
                data = {}

            decision = data.get("decision", "")
            round_num = data.get("round", 1)
            
            # Kırmızı çizgi kontrolü
            guardrail = check_hard_guardrails(decision)
            if guardrail["blocked"]:
                response_payload = {
                    "status": "blocked",
                    "reason": guardrail["reason"],
                    "reply": guardrail["message"],
                    "weapon": guardrail["message"]
                }
            else:
                try:
                    from mlx_lm import generate
                    m, tok = get_model()

                    # Adım 1: System 2 (Soğuk Analiz)
                    p_sys2 = f"<|im_start|>system\n{SYSTEM_2_PROMPT}<|im_end|>\n<|im_start|>user\n{decision}<|im_end|>\n<|im_start|>assistant\n"
                    raw_sys2 = generate(m, tok, prompt=p_sys2, max_tokens=350, verbose=False)
                    
                    # Adım 2: System 1 (Retorik + İroni + Aksiyon Silahı)
                    p_sys1 = f"<|im_start|>system\n{SYSTEM_1_PROMPT}\nTur: {round_num}<|im_end|>\n<|im_start|>user\nKullanıcı Durumu: {decision}\n\nSoğuk Analiz Matrisi:\n{raw_sys2}<|im_end|>\n<|im_start|>assistant\n"
                    reply = generate(m, tok, prompt=p_sys1, max_tokens=650, verbose=False)

                    response_payload = {
                        "status": "success",
                        "model": "Qwen2.5-14B-Instruct-Abliterated-4bit-MLX",
                        "round": round_num,
                        "system2_matrix": raw_sys2,
                        "reply": reply
                    }
                except Exception as e:
                    response_payload = {
                        "status": "fallback",
                        "error": str(e),
                        "reply": f"Yerel çıkarım motoru hatası: {str(e)}"
                    }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_payload, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    print(f"InversionCore Dual-Process Motoru Başlatıldı: http://localhost:{PORT}")
    with socketserver.TCPServer(("", PORT), InversionHandler) as httpd:
        httpd.serve_forever()
