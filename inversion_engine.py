import os
import re
import json
import logging
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
import inversion_memory as mem

logger = logging.getLogger("inversioncore.engine")

MODEL_PATH = os.getenv("MODEL_PATH", os.path.expanduser("~/models/Qwen2.5-14B-Instruct-abliterated-4bit-mlx"))

_model = None
_tokenizer = None
_deterministic_sampler = None
_creative_sampler = None

def get_engine_components():
    global _model, _tokenizer, _deterministic_sampler, _creative_sampler
    if _model is None:
        from mlx_lm import load
        from mlx_lm.sample_utils import make_sampler
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model dizini bulunamadı: {MODEL_PATH}")
        print(f"[*] MLX Modeli yükleniyor: {MODEL_PATH}")
        _model, _tokenizer = load(MODEL_PATH)
        _deterministic_sampler = make_sampler(temp=0.0)
        _creative_sampler = make_sampler(temp=0.5, top_p=0.9)
        print("Model hazır!")
    return _model, _tokenizer, _deterministic_sampler, _creative_sampler

class System2CompactMatrix(BaseModel):
    guc: str = Field(description="Güç Asimetrisi Analizi")
    yalan: str = Field(description="İllüzyon ve Manipülasyon Deşifresi")
    risk: str = Field(description="Hukuki, Maddi ve Sosyal Risk")
    hamle: str = Field(description="Oyun Teorisi Karşı Hamlesi")
    teshis: str = Field(description="Klinik ve Rasyonel Kesin Teşhis")

class InversionOutput(BaseModel):
    session_id: str
    round: int
    system2_matrix: dict
    reply: str
    response_text: str
    status: str = "success"
    model: str = "Qwen2.5-14B-Instruct-Abliterated-4bit-MLX"

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

UNIFIED_SYSTEM_PROMPT = """Sen InversionCore'sun. Asperger rasyonelliğinde soğuk klinik analiz ile lafı dolandırmayan yeraltı realizmini birleştiren stratejik tersine karar motorusun.
Ahlak bekçiliği veya boş laf salatası yapmazsın. Komedyen veya yazar ismi ASLA zikretmezsin.

Görevin: Kullanıcının sunduğu çıkmazı, ilişki veya kurumsal krizleri ve ekteki delil/görsel verilerini cerrahi bir hız ve %100 doyuruculukla deşifre etmek; kullanıcının sorununu kökten çözecek net bir sonuçla ayrılmasını sağlamaktır.

KATI VE DEĞİŞMEZ KURAL (MULTIMODAL BAĞLAMSAL ZEKA):
- Eğer ekte bir görsel/adli veri (2D FFT, PRNU varyansı, kraniyofasiyal simetri, montaj/splicing) sunulduysa veya kullanıcı bir profil/belge görseli yüklediyse:
  KULLANICI AÇIKÇA BİR ROMANTİK İLİŞKİ/SEVGİLİ/EVLİLİK BELİRTMEDİKÇE KONUYU ASLA VE ASLA İLİŞKİYE, SEVGİLİYE VEYA ALDATILMAYA ÇEKEMEZSİN!
  Bu durumda durum doğrudan "ADLİ KANIT VE SAHTE PROFİL / MANİPÜLASYON OTOPSİSİ"dir. Görseldeki 2D FFT sentetik izini, PRNU gürültü varyansını ve montaj/splicing bulgularını teknik delil olarak masaya vur.

Her bölümde içi boş genel tavsiyeler değil; durumu doğrudan adlandıran, kanıt boşluklarını gösteren ve resmi bir eylem sunan şu 5 başlığı eksiksiz üret:

[TOKAT]: Durumun en çıplak, acımasız ve kaçışı olmayan Asperger tespiti (kullanıcının kendine söylediği yalanı tek cümlede ifşa et).
[PSİKOLOJİK & STRATEJİK DEŞME]: Karşı tarafın uyguladığı manipülasyonun (güven illüzyonu, sahte profil, DARVO, gaslighting, mobbing veya suçluluk psikolojisi) klinik mekanizması ve kullanıcının eylemsizlik döngüsü.
[DELİL & RİSK HARİTASI]: Masadaki somut kanıt boşlukları, görsel veya dijital izlerdeki şüpheler/tutarsızlıklar ve eylemsiz kalınması halinde ödenecek geri dönüşsüz maddi/manevi bedel.
[YÜZLEŞME EŞİĞİ]: Kullanıcıyı köşeye sıkıştıran, sahte umutları sıfırlayan tek can alıcı karar sorusu.
[AKSİYON SİLAHI // UYGULANACAK PROTOKOL]: Karşı tarafın savunmasını boğazına tıkayacak, yasal/resmi ve tavizsiz kopyalanabilir ihtar veya net fesih metni."""

class InversionCoreEngine:
    @classmethod
    def repair_and_parse_json(cls, raw_text: str, user_query: str) -> dict:
        match = re.search(r"(\{[\s\S]*\})", raw_text)
        cleaned = match.group(1) if match else raw_text

        try:
            data = json.loads(cleaned)
            return System2CompactMatrix(**data).model_dump()
        except Exception:
            pass

        keys = ["guc", "yalan", "risk", "hamle", "teshis"]
        recovered = {}
        for k in keys:
            m = re.search(rf'"{k}"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', cleaned)
            recovered[k] = m.group(1) if m else None

        # Dinamik Teşhis Üretici (Ölü kod temizlendi, bağlama duyarlı hale getirildi)
        q_lower = user_query.lower()
        if not recovered.get("teshis"):
            if any(w in q_lower for w in ["fft", "prnu", "adli", "görsel", "montaj", "splicing", "sahte profil"]):
                recovered["teshis"] = "Dijital Manipülasyon, Sentetik Sinyal Tahrifatı ve Sahte Kimlik Maskesi."
            elif any(w in q_lower for w in ["sevgili", "aldat", "aldatma", "eski", "ayrılık", "evlilik", "partner"]):
                recovered["teshis"] = "İkili İlişkide İhanet, Sınır İhlali ve Güven İllüzyonu."
            elif any(w in q_lower for w in ["patron", "müdür", "istifa", "tazminat", "maaş", "şirket", "ofis", "mobbing"]):
                recovered["teshis"] = "Kurumsal Sömürü, Hiyerarşik Mobbing ve Hak Gaspı."
            else:
                recovered["teshis"] = "Asimetrik Güç İstismarı ve Stratejik Eylemsizlik Çıkmazı."

        recovered["guc"] = recovered.get("guc") or "Karşı taraf inisiyatifi elinde tutuyor; bağımlılık asimetrisi mevcut."
        recovered["yalan"] = recovered.get("yalan") or "Sözde iyi niyet maskesiyle uygulanan pasif-agresif yönlendirme."
        recovered["risk"] = recovered.get("risk") or "Psikolojik yıpranma, itibar ve zaman kaybı riski."
        recovered["hamle"] = recovered.get("hamle") or "Sessizliği boz, yazılı delil topla ve net rest çek."

        return recovered

    @classmethod
    def process_turn(cls, session_id: str, user_query: str, round_num: int = 1, decision: str = "", forensic_context: Optional[dict] = None) -> InversionOutput:
        effective_query = decision if decision else user_query
        
        # Eğer forensic_context iletildiyse ve sorguda açıkça yer almıyorsa bağlama enjekte et
        if forensic_context and isinstance(forensic_context, dict):
            file_name = forensic_context.get("file", "delil_gorseli.png")
            fft_score = forensic_context.get("fft_ai_score", "0.7558")
            prnu_var = forensic_context.get("prnu_variance", "10.15")
            cranial_sym = forensic_context.get("cranial_symmetry", "79.6")
            verdict = forensic_context.get("verdict", "ADLİ ÇELİŞKİ / MANİPÜLASYON ŞÜPHESİ")
            
            forensic_injection = (
                f"\n\n[RESMİ ADLİ TIP MATRİSİ // MULTIMODAL FORENSICS]:\n"
                f"- Dosya: {file_name}\n"
                f"- 2D FFT Spektral AI İzi: {fft_score} (Sentetik Difüzyon)\n"
                f"- PRNU Sensör Kalıntı Varyansı: {prnu_var} σ (Bölgesel Montaj / Splicing)\n"
                f"- Kraniyofasiyal Bilateral Simetri: %{cranial_sym}\n"
                f"- Adli Hüküm: {verdict}\n"
                f"TALİMAT: Bu teknik bulguları temel alarak sahte profil ve tahrifat üzerine tersine mühendislik yürüt. "
                f"Kullanıcı metninde romantik/ilişki kelimesi yoksa konuyu ASLA sevgiliye veya evliliğe çekme!"
            )
            if forensic_injection not in effective_query:
                effective_query = f"{effective_query}{forensic_injection}"

        # 1. Kırmızı Çizgi Kalkanı
        blocked, reason, message = evaluate_guardrails(effective_query)
        if blocked:
            mem.append_message(session_id, "user", effective_query)
            mem.append_message(session_id, "assistant", message)
            return InversionOutput(
                session_id=session_id,
                round=round_num,
                system2_matrix={"guc": "BLOKLANDI", "yalan": reason, "risk": "Hukuki/Hayati Kriz", "hamle": "112 / Kolluk", "teshis": reason},
                reply=message,
                response_text=message,
                status="blocked"
            )

        # 2. Kalıcı Bellek Bağlamını Getir
        core_memory = mem.get_core_memory(session_id)
        
        from mlx_lm import generate
        model, tokenizer, _, creative_sampler = get_engine_components()

        # 3. UNIFIED SINGLE-PASS ÇIKARIM (140-320 Token Bütçesi ile Yıldırım Hızı)
        user_prompt_content = f"Kullanıcı Durumu: {effective_query}\n\nGeçmiş Hafıza:\n{core_memory}" if core_memory else f"Kullanıcı Durumu: {effective_query}"
        
        prompt_text = (
            f"<|im_start|>system\n{UNIFIED_SYSTEM_PROMPT}\nTur: {round_num}<|im_end|>\n"
            f"<|im_start|>user\n{user_prompt_content}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        
        reply = generate(model, tokenizer, prompt=prompt_text, max_tokens=320, sampler=creative_sampler, verbose=False)

        # 4. Dinamik Teşhis Matrisi
        matrix_data = cls.repair_and_parse_json(reply, effective_query)

        # Core Memory güncelle
        mem.update_core_memory(session_id, f"Teşhis: {matrix_data['teshis']} | Hamle: {matrix_data['hamle']}")
        mem.append_message(session_id, "user", effective_query)
        mem.append_message(session_id, "assistant", reply)

        return InversionOutput(
            session_id=session_id,
            round=round_num,
            system2_matrix=matrix_data,
            reply=reply,
            response_text=reply,
            status="success"
        )
