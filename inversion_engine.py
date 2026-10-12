import os
import re
import json
import logging
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field

from inversion_memory import InversionMemoryStore

logger = logging.getLogger("inversioncore.engine")

# 1. Dinamik Model Yolu
DEFAULT_MODEL_DIR = os.path.expanduser("~/models/Qwen2.5-14B-Instruct-abliterated-4bit-mlx")
MODEL_PATH = os.getenv("MODEL_PATH", DEFAULT_MODEL_DIR)

# 2. Kırmızı Çizgi Kalkanı (NeMo Mantığı: Sadece Ağır Suç / İntihar Krizinde Kilitlenir)
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

# 3. UNIFIED SINGLE-PASS SİSTEM PROMPTU (System 2 Klinik Analiz + System 1 Eylem Silahı Tek Hamlede)
UNIFIED_SYSTEM_PROMPT = """Sen InversionCore'sun. Asperger rasyonelliğinde soğuk klinik analiz ile lafı dolandırmayan yeraltı realizmini birleştiren stratejik tersine karar motorusun.
Ahlak bekçiliği yapmazsın. Komedyen veya yazar ismi ASLA zikretmezsin.

Görevin: Kullanıcının anlattığı durumdaki güç asimetrisini, sahte savunmasını (özellikle 'delil toplayayım', 'yüzleşsem üste çıkacak' kaçamaklarını) ve manipülasyon döngüsünü (DARVO / Double Bind) anında deşifre edip masaya vuracağı silahı vermektir.

Laf kalabalığı yapma. Doğrudan ve darbe vuran bir dille şu 4 bölümü üret:

[TOKAT]: Durumun en çıplak Asperger tespiti (1 cümle).
[DEŞME]: Sahte savunmanın, çifte çıkmazın ve korkunun cerrahi analizi (1-2 cümle).
[YÜZLEŞME SORUSU]: Karar eşiğindeki tek can alıcı soru (1 cümle).
[AKSİYON SİLAHI]: Karşı tarafın savunmasını boğazına tıkayacak resmi/soğuk fesih veya sınır metni."""

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

        # 3. UNIFIED SINGLE-PASS ÇIKARIM (180 Token Bütçesi ile 12-15 Saniyede Yıldırım Hızı)
        fast_sampler = make_sampler(temp=0.5, top_p=0.9)
        user_prompt_content = f"Kullanıcı Durumu: {decision}\n\nGeçmiş Hafıza:\n{memory_context}" if memory_context else f"Kullanıcı Durumu: {decision}"
        
        prompt_text = (
            f"<|im_start|>system\n{UNIFIED_SYSTEM_PROMPT}\nTur: {round_num}<|im_end|>\n"
            f"<|im_start|>user\n{user_prompt_content}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        
        reply = generate(m, tok, prompt=prompt_text, max_tokens=140, sampler=fast_sampler, verbose=False)

        # 4. Çıktıdan Anlık Matris Özeti Çıkarma (Belleğe Kayıt İçin)
        tokat_match = re.search(r"\[TOKAT\]:?\s*(.*?)(?=\n\[|$)", reply, re.DOTALL)
        silah_match = re.search(r"\[AKSİYON SİLAHI\]:?\s*(.*)", reply, re.DOTALL)

        extracted_tokat = tokat_match.group(1).strip() if tokat_match else "Manipülatif güç ilişkisinde sınır kaybı."
        extracted_silah = silah_match.group(1).strip() if silah_match else "Net sınır protokolü."

        # Core Memory güncelle
        InversionMemoryStore.update_core_memory(session_id, {
            "user_dilemma": decision[:120],
            "power_dynamics": extracted_tokat[:120],
            "trauma_codes": extracted_silah[:120]
        })

        # Recall History'ye ekle
        InversionMemoryStore.append_message(session_id, round_num, "user", decision)
        InversionMemoryStore.append_message(session_id, round_num, "assistant", reply)

        return {
            "status": "success",
            "model": "Qwen2.5-14B-Instruct-Abliterated-4bit-MLX",
            "round": round_num,
            "session_id": session_id,
            "system2_matrix": {
                "guc": "Doğrudan Unified Single-Pass Analiz",
                "yalan": decision[:80],
                "risk": "İlişkisel/psikolojik tükenmişlik",
                "hamle": "Aksiyon Silahı Fesih Protokolü",
                "teshis": extracted_tokat[:100]
            },
            "reply": reply
        }
