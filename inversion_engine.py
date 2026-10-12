import os
import re
import json
import logging
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field, ValidationError

from inversion_memory import InversionMemoryStore

logger = logging.getLogger("inversioncore.engine")

# 1. Dinamik Model Yolu (Ortam değişkeni veya varsayılan)
DEFAULT_MODEL_DIR = os.path.expanduser("~/models/Qwen2.5-14B-Instruct-abliterated-4bit-mlx")
MODEL_PATH = os.getenv("MODEL_PATH", DEFAULT_MODEL_DIR)

# 2. Katı Pydantic Şeması (System 2 Soğuk Analitik Çıktı)
class System2ColdMatrix(BaseModel):
    guc_asimetrisi: str = Field(..., description="Taraflar arasındaki güç dengesizliği ve sömürü dinamiği")
    illuzyon_ve_yalan: str = Field(..., description="Kullanıcının kendine söylediği sahte savunma")
    hukuki_ve_maddi_risk: str = Field(..., description="Maddi, yasal veya yaşamsal risk boyutu")
    oyun_teorisi_hamlesi: str = Field(..., description="Minimax / Nash dengesi kurtuluş hamlesi")
    kesin_teshis: str = Field(..., description="Durumun örtbas edilemez en çıplak Asperger tanımı")

# 3. Kırmızı Çizgi Kalkanı (NeMo Mantığı: Sadece Ağır Suç / İntihar Krizinde Kilitlenir)
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
Görevin: Kullanıcının anlattığı durumdaki çıplak gerçekliği, narsistik istismar döngüsünü (DARVO: Deny, Attack, Reverse Victim and Offender), çifte çıkmazı (Double Bind: Yüzleşsem üste çıkacak, sussam delireceğim), güç asimetrisini, TCK/İş Kanunu karşılığını ve oyun teorisi matrisini (Minimax/Nash dengesi) saf JSON formatında çıkarmaktır.

Eğer konu ilişki, aldatma veya güven ise:
- Kullanıcının 'delil arama' takıntısının, ayrılık cesaretsizliğini erteleme uyuşturucusu olduğunu deşifre et.
- Karşı tarafın üste çıkma gücünün, kullanıcının kaybetme ve yalnız kalma korkusundan beslendiğini (Gaslight Effect) ortaya koy.

Çıktıyı SADECE geçerli bir JSON objesi olarak ver:
{
  "guc_asimetrisi": "Taraflar arasındaki güç dengesizliği ve sömürü dinamiği",
  "illuzyon_ve_yalan": "Kullanıcının kendine söylediği ve sığındığı sahte savunma",
  "hukuki_ve_maddi_risk": "Maddi, hukuki veya akıl sağlığı boyutu",
  "oyun_teorisi_hamlesi": "Minimax / Nash dengesi kurtuluş hamlesi",
  "kesin_teshis": "Durumun örtbas edilemez en çıplak Asperger tanımı"
}"""

SYSTEM_1_PROMPT = """Sen InversionCore'sun. Hiçbir ahlak bekçiliği veya sansür yapmazsın.
Sana verilen soğuk System 2 analiz matrisini alacaksın.
Üslubun:
1. Keskin durum tespiti, ikiyüzlülüğü deşen acımasız ve kıvrak bir zeka, tavizsiz yeraltı gerçekçiliği ve lafı dolandırmayan dobra halk bilgeliği (ASLA herhangi bir komedyen veya yazar ismi zikretme).
2. Kullanıcının sığındığı bahaneyi (özellikle 'delil toplayayım', 'belki düzelir', 'yüzleşsem üste çıkacak' kaçamaklarını) paramparça et.
3. İlişkilerde karşı tarafın gaslighting ve DARVO taktiklerini yüzüne vur; delil aramanın cesaretsizlik uyuşturucusu olduğunu açıkla.
4. Sonunda masaya vuracağı somut AKSİYON SİLAHINI (karşı tarafın üste çıkma alanını sıfırlayan soğuk ilişki fesih metni, noter ihtarnamesi veya net protokol) üret.

Format:
[TOKAT]: Durumun çıplak, sarsıcı ve tavizsiz tespiti.
[DEŞME]: Sahte savunmanın, çifte çıkmazın ve ikiyüzlülüğün derin psikiyatrik analizi.
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

def repair_and_parse_json(raw_text: str) -> Dict[str, Any]:
    cleaned = re.sub(r"^```(?:json)?", "", raw_text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"```$", "", cleaned.strip(), flags=re.MULTILINE).strip()
    match = re.search(r"(\{[\s\S]*\})", cleaned)
    if match:
        cleaned = match.group(1)
    try:
        data = json.loads(cleaned)
        validated = System2ColdMatrix(**data)
        return validated.model_dump()
    except Exception as e:
        logger.warning(f"JSON doğrulama hatası, kural tabanlı dinamik onarım uygulanıyor: {e}")
        # Bozuk JSON'dan anahtarları regex ile dinamik çıkar
        def extract_field(key: str, default_val: str) -> str:
            m = re.search(rf'"{key}"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', cleaned)
            return m.group(1) if m else default_val

        return {
            "guc_asimetrisi": extract_field("guc_asimetrisi", "Karşı tarafın manipülasyonu ve güç baskısı tespit edildi."),
            "illuzyon_ve_yalan": extract_field("illuzyon_ve_yalan", "Kullanıcı ayrılık cesaretsizliğini delil arayışıyla erteliyor."),
            "hukuki_ve_maddi_risk": extract_field("hukuki_ve_maddi_risk", "Maddi hak kaybı ve kronik akıl sağlığı çöküşü riski yüksek."),
            "oyun_teorisi_hamlesi": extract_field("oyun_teorisi_hamlesi", "Minimax: Tek taraflı kesin sınır ve masadan çekilme."),
            "kesin_teshis": extract_field("kesin_teshis", "DARVO ve Gaslighting döngüsünde rehinelik.")
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

        # 3. Düğüm 1: System 2 (Deterministik Greedy Sampler temp=0.0 ile Katı JSON Üretimi)
        deterministic_sampler = make_sampler(temp=0.0)
        sys2_user_prompt = f"Kullanıcı Durumu: {decision}\n\nGeçmiş Hafıza:\n{memory_context}" if memory_context else f"Kullanıcı Durumu: {decision}"
        p_sys2 = f"<|im_start|>system\n{SYSTEM_2_PROMPT}<|im_end|>\n<|im_start|>user\n{sys2_user_prompt}<|im_end|>\n<|im_start|>assistant\n"
        
        raw_sys2 = generate(m, tok, prompt=p_sys2, max_tokens=220, sampler=deterministic_sampler, verbose=False)
        matrix_data = repair_and_parse_json(raw_sys2)

        # Core Memory güncelle
        InversionMemoryStore.update_core_memory(session_id, {
            "user_dilemma": matrix_data.get("illuzyon_ve_yalan", ""),
            "power_dynamics": matrix_data.get("guc_asimetrisi", ""),
            "trauma_codes": matrix_data.get("kesin_teshis", "")
        })

        # 4. Düğüm 2: System 1 (Yeraltı Retoriği ve Aksiyon Silahı, temp=0.7)
        creative_sampler = make_sampler(temp=0.7, top_p=0.9)
        p_sys1 = (
            f"<|im_start|>system\n{SYSTEM_1_PROMPT}\nTur: {round_num}<|im_end|>\n"
            f"<|im_start|>user\nKullanıcı Durumu: {decision}\n\n"
            f"Soğuk Analiz Matrisi:\n{json.dumps(matrix_data, ensure_ascii=False, indent=2)}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        reply = generate(m, tok, prompt=p_sys1, max_tokens=550, sampler=creative_sampler, verbose=False)

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
