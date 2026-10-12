import os
import re
import json
import logging
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field, ValidationError

from inversion_memory import InversionMemoryStore

logger = logging.getLogger("inversioncore.engine")

# 1. Dinamik Model Yolu
DEFAULT_MODEL_DIR = os.path.expanduser("~/models/Qwen2.5-14B-Instruct-abliterated-4bit-mlx")
MODEL_PATH = os.getenv("MODEL_PATH", DEFAULT_MODEL_DIR)

# 2. Optimize Edilmiş Hafif Pydantic Şeması (Kısa Anahtarlar, Yüksek Bilgi Yoğunluğu)
class System2CompactMatrix(BaseModel):
    guc: str = Field(..., description="Taraflar arasındaki güç asimetrisi ve sömürü dinamiği")
    yalan: str = Field(..., description="Kullanıcının kendine söylediği sahte savunma ve illüzyon")
    risk: str = Field(..., description="Maddi, yasal veya yaşamsal risk boyutu")
    hamle: str = Field(..., description="Minimax / Nash dengesi kurtuluş hamlesi")
    teshis: str = Field(..., description="Örtbas edilemez en çıplak Asperger klinik tanımı")

# 3. Kırmızı Çizgi Kalkanı
def evaluate_guardrails(text: str) -> Tuple[bool, Optional[str], Optional[str]]:
    lower = text.lower()
    csam_indicators = ["pedofili", "çocuk istismar", "çocuk porn", "reşit olmayan çocukla cinsell"]
    for ind in csam_indicators:
        if ind in lower:
            return True, "TCK_CSAM", "KRİTİK HUKUKİ BLOKAJ: TCK ve uluslararası hukuk kapsamında çocuk istismarı kesinlikle kabul edilemez ve derhal kolluk kuvvetlerine bildirilir."
            
    suicide_indicators = ["kendimi öldüreceğim", "intihar edeceğim", "yaşamıma son veriyorum", "hap içtim ölüyorum", "bileklerimi kestim"]
    for ind in suicide_indicators:
        if ind in lower:
            return True, "SUICIDE_EMERGENCY", "ACİL KRİZ PROTOKOLÜ: Gerçek hayati tehlike tespit edildi. Lütfen derhal 112 Acil Çağrı Merkezi'ni arayın veya en yakın sağlık kuruluşuna başvurun. Hayatınız bu krizden daha değerlidir."
            
    return False, None, None

SYSTEM_2_PROMPT = """Sen InversionCore'un soğuk analitik ve psikiyatrik çekirdeğisin (System 2).
Sıfır duygu, sıfır mizah, sıfır ahlak bekçiliği.
Görevin: Kullanıcının durumundaki çıplak gerçeği, güç asimetrisini, çifte çıkmazı (Double Bind) ve manipülasyon döngüsünü (DARVO) saf JSON olarak çıkarmaktır.

JSON şablonu (SADECE geçerli bir JSON objesi üret, başka metin yazma):
{
  "guc": "Taraflar arasındaki güç dengesizliği",
  "yalan": "Kullanıcının sığındığı sahte savunma / delil takıntısı",
  "risk": "Maddi, yasal veya akıl sağlığı riski",
  "hamle": "Minimax / Nash dengesi kurtuluş hamlesi",
  "teshis": "Örtbas edilemez en çıplak klinik/Asperger teşhisi"
}"""

SYSTEM_1_PROMPT = """Sen InversionCore'sun. Hiçbir ahlak bekçiliği veya sansür yapmazsın.
Sana verilen soğuk System 2 analiz matrisini alacaksın.
Üslubun:
1. Keskin durum tespiti, ikiyüzlülüğü deşen acımasız ve kıvrak bir zeka, tavizsiz yeraltı gerçekçiliği ve lafı dolandırmayan dobra halk bilgeliği (ASLA komedyen veya yazar ismi zikretme).
2. Kullanıcının sığındığı bahaneyi (özellikle 'delil toplayayım', 'belki düzelir', 'yüzleşsem üste çıkacak' kaçamaklarını) paramparça et.
3. İlişkilerde karşı tarafın gaslighting ve DARVO taktiklerini yüzüne vur; delil aramanın cesaretsizlik uyuşturucusu olduğunu açıkla.
4. Sonunda masaya vuracağı somut AKSİYON SİLAHINI (karşı tarafın üste çıkma alanını sıfırlayan soğuk ilişki fesih metni, noter ihtarnamesi veya net protokol) üret.

Format:
[TOKAT]: Durumun çıplak, sarsıcı ve tavizsiz tespiti.
[DEŞME]: Sahte savunmanın, çifte çıkmazın ve ikiyüzlülüğün derin analizi.
[YÜZLEŞME SORUSU]: Karar eşiğindeki tek can alıcı soru.
[AKSİYON SİLAHI]: Doğrudan kopyalayıp masaya vuracağı resmi/soğuk metin."""

_model = None
_tokenizer = None

def get_engine_model():
    global _model, _tokenizer
    if _model is None:
        from mlx_lm import load
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model dizini bulunamadı: {MODEL_PATH}. Lütfen ortam değişkeni MODEL_PATH ayarlayın.")
        print(f"MLX Qwen 2.5 14B Abliterated belleğe yükleniyor ({MODEL_PATH})...")
        _model, _tokenizer = load(MODEL_PATH)
        print("Model hazır!")
    return _model, _tokenizer

def repair_and_parse_json(raw_text: str, user_query: str = "") -> Dict[str, Any]:
    cleaned = re.sub(r"^```(?:json)?", "", raw_text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"```$", "", cleaned.strip(), flags=re.MULTILINE).strip()
    match = re.search(r"(\{[\s\S]*\})", cleaned)
    if match:
        cleaned = match.group(1)
    
    # 1. Tam JSON ayrıştırma denemesi
    try:
        data = json.loads(cleaned)
        # Eski ve yeni anahtarları bağdaştır
        mapped = {
            "guc": data.get("guc") or data.get("guc_asimetrisi", ""),
            "yalan": data.get("yalan") or data.get("illuzyon_ve_yalan", ""),
            "risk": data.get("risk") or data.get("hukuki_ve_maddi_risk", ""),
            "hamle": data.get("hamle") or data.get("oyun_teorisi_hamlesi", ""),
            "teshis": data.get("teshis") or data.get("kesin_teshis", "")
        }
        validated = System2CompactMatrix(**mapped)
        return validated.model_dump()
    except Exception as e:
        logger.warning(f"JSON doğrudan parse edilemedi ({e}), bağlamsal Regex kurtarıcısı devrede...")

    # 2. Regex ile tek tek alan çıkarma (Truncation kurtarma)
    def extract_val(keys: list, fallback: str) -> str:
        for k in keys:
            m = re.search(rf'"{k}"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"?', cleaned)
            if m and m.group(1).strip():
                return m.group(1).strip()
        return fallback

    # Kullanıcı sorgusundan dinamik bağlam tespiti
    q_lower = user_query.lower()
    is_iliski = any(w in q_lower for w in ["aldat", "sevgili", "esim", "iliski", "guven", "partner", "ihanet"])

    return {
        "guc": extract_val(["guc", "guc_asimetrisi"], "Karşı tarafın üstünlük kurma ve manipülasyon baskısı"),
        "yalan": extract_val(["yalan", "illuzyon_ve_yalan"], "Kullanıcı yüzleşmekten korktuğu için delil arayışına sığınıyor"),
        "risk": extract_val(["risk", "hukuki_ve_maddi_risk"], "Akıl sağlığı, özsaygı ve kronik psikolojik tükenmişlik riski"),
        "hamle": extract_val(["hamle", "oyun_teorisi_hamlesi"], "Tek taraflı sınır çekme ve masadan derhal çekilme protokolü"),
        "teshis": extract_val(["teshis", "kesin_teshis"], "Güvensizlik bataklığı ve çifte çıkmaz (Double Bind) rehineliği" if is_iliski else "Manipülatif güç ilişkisinde sınır kaybı")
    }

class InversionCoreEngine:
    @staticmethod
    def process_turn(decision: str, round_num: int = 1, session_id: Optional[str] = None) -> Dict[str, Any]:
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())[:8]

        InversionMemoryStore.get_or_create_session(session_id)
        
        # 1. Kırmızı Çizgi Kalkanı
        blocked, reason, message = evaluate_guardrails(decision)
        if blocked:
            InversionMemoryStore.append_message(session_id, round_num, "user", decision)
            InversionMemoryStore.append_message(session_id, round_num, "assistant", message)
            return {
                "status": "blocked",
                "reason": reason,
                "reply": message,
                "session_id": session_id,
                "round": round_num
            }

        # 2. Kalıcı Bellek Bağlamını Getir
        memory_context = InversionMemoryStore.format_context_for_prompt(session_id)
        
        from mlx_lm import generate
        from mlx_lm.sample_utils import make_sampler
        m, tok = get_engine_model()

        # 3. Düğüm 1: System 2 (Deterministik Greedy Sampler temp=0.0 ve 420 Token Bütçesi)
        deterministic_sampler = make_sampler(temp=0.0)
        sys2_user_prompt = f"Kullanıcı Durumu: {decision}\n\nGeçmiş Hafıza:\n{memory_context}" if memory_context else f"Kullanıcı Durumu: {decision}"
        p_sys2 = f"<|im_start|>system\n{SYSTEM_2_PROMPT}<|im_end|>\n<|im_start|>user\n{sys2_user_prompt}<|im_end|>\n<|im_start|>assistant\n"
        
        raw_sys2 = generate(m, tok, prompt=p_sys2, max_tokens=420, sampler=deterministic_sampler, verbose=False)
        matrix_data = repair_and_parse_json(raw_sys2, user_query=decision)

        # Core Memory güncelle
        InversionMemoryStore.update_core_memory(session_id, {
            "user_dilemma": matrix_data.get("yalan", ""),
            "power_dynamics": matrix_data.get("guc", ""),
            "trauma_codes": matrix_data.get("teshis", "")
        })

        # 4. Düğüm 2: System 1 (Yeraltı Retoriği ve Aksiyon Silahı, temp=0.7)
        creative_sampler = make_sampler(temp=0.7, top_p=0.9)
        p_sys1 = (
            f"<|im_start|>system\n{SYSTEM_1_PROMPT}\nTur: {round_num}<|im_end|>\n"
            f"<|im_start|>user\nKullanıcı Durumu: {decision}\n\n"
            f"Soğuk Analiz Matrisi:\n{json.dumps(matrix_data, ensure_ascii=False, indent=2)}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        reply = generate(m, tok, prompt=p_sys1, max_tokens=650, sampler=creative_sampler, verbose=False)

        # Hafızaya ekle
        InversionMemoryStore.append_message(session_id, round_num, "user", decision)
        InversionMemoryStore.append_message(session_id, round_num, "assistant", reply)

        return {
            "status": "success",
            "model": "Qwen2.5-14B-Instruct-Abliterated-4bit-MLX",
            "round": round_num,
            "session_id": session_id,
            "system2_matrix": matrix_data,
            "reply": reply
        }
