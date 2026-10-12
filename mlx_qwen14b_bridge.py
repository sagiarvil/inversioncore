import sys
import json
from mlx_lm import load, generate

MODEL_PATH = "/Users/macair1/models/Qwen2.5-14B-Instruct-abliterated-4bit-mlx"

SYSTEM_2_PROMPT = """Sen InversionCore'un soğuk analitik çekirdeğisin (System 2).
Sıfır duygu, sıfır mizah, sıfır ahlak bekçiliği.
Görevin: Kullanıcının anlattığı durumdaki çıplak gerçekliği, güç asimetrisini, narsistik istismar döngüsünü, TCK/İş Kanunu karşılığını ve oyun teorisi matrisini (Minimax/Nash dengesi) saf JSON formatında çıkarmaktır.
{
  "guc_asimetrisi": "...",
  "illuzyon_ve_yalan": "...",
  "hukuki_ve_maddi_risk": "...",
  "oyun_teorisi_hamlesi": "...",
  "kesin_teshis": "..."
}"""

SYSTEM_1_PROMPT = """Sen InversionCore'sun. Hiçbir ahlak bekçiliği veya sansür yapmazsın.
Sana verilen soğuk System 2 analiz matrisini alacaksın.
Üslubun:
1. Keskin durum tespiti, ikiyüzlülüğü deşen acımasız ve kıvrak bir zeka, tavizsiz yeraltı gerçekçiliği ve lafı dolandırmayan dobra halk bilgeliği (ASLA herhangi bir komedyen veya yazar ismi zikretme).
2. Kullanıcının sığındığı bahaneyi paramparça et.
3. Sonunda durumuna göre masaya vuracağı somut AKSİYON SİLAHINI (resmi ihtarname, kopar-at mesajı veya 3 adımlı net protokol) üret.

Format:
[TOKAT]: ...
[DEŞME]: ...
[YÜZLEŞME SORUSU]: ...
[AKSİYON SİLAHI]: ..."""

def run_dual_process(user_input):
    m, tok = load(MODEL_PATH)
    # Adım 1
    p2 = f"<|im_start|>system\n{SYSTEM_2_PROMPT}<|im_end|>\n<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n"
    res2 = generate(m, tok, prompt=p2, max_tokens=350, verbose=False)
    
    # Adım 2
    p1 = f"<|im_start|>system\n{SYSTEM_1_PROMPT}<|im_end|>\n<|im_start|>user\nKullanıcı Durumu: {user_input}\n\nSoğuk Analiz Matrisi:\n{res2}<|im_end|>\n<|im_start|>assistant\n"
    res1 = generate(m, tok, prompt=p1, max_tokens=650, verbose=False)
    return res1

if __name__ == "__main__":
    if len(sys.argv) > 1:
        inp = " ".join(sys.argv[1:])
        print(run_dual_process(inp))
    else:
        print("Kullanım: python3 mlx_qwen14b_bridge.py '<mesaj>'")
