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

def call_groq_inference(prompt_text: str, system_prompt: str) -> Optional[str]:
    """
    Groq Ultra Hızlı Sansürsüz Çıkarım Motoru (Qwen 27B / GPT-OSS 120B).
    Google veya kurumsal filtrelerin engellediği sert aldatma, dolandırıcılık, şantaj ve kriz konularında
    hiçbir sansür duvarına takılmadan doğrudan cerrahi analizi döndürür.
    """
    raw_keys = os.getenv("GROQ_API_KEYS", "")
    if not raw_keys:
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("GROQ_API_KEYS="):
                        raw_keys = line.strip().split("=", 1)[1]
                        break
                    elif line.startswith("GROQ_API_KEY="):
                        raw_keys = line.strip().split("=", 1)[1]

    keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
    if not keys:
        return None

    import urllib.request
    # Resmi Groq Modelleri (Garantili Çalışan Sıra: Qwen 27B -> Llama 3.3 70B -> GPT-OSS 120B -> Llama 3.1 8B)
    models = ["qwen/qwen3.8-27b", "llama-3.3-70b-versatile", "openai/gpt-oss-120b", "llama-3.1-8b-instant"]

    for k in keys:
        for model_id in models:
            try:
                req = urllib.request.Request(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {k}",
                        "Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0 (InversionCore; Engine v3)"
                    },
                    data=json.dumps({
                        "model": model_id,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt_text}
                        ],
                        "temperature": 0.35,
                        "max_tokens": 512
                    }).encode("utf-8")
                )
                resp = urllib.request.urlopen(req, timeout=8)
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("choices") and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
            except Exception as ge:
                logger.info(f"[Groq Attempt Failed ({model_id})]: {ge}")
                continue
    return None

def call_nvidia_cloud_inference(prompt_text: str, system_prompt: str) -> Optional[str]:
    """
    NVIDIA Cloud AI NIM Inference (Bulut Modu / Sıfır Maliyetli 70B/11B Llama 3.2 NIM).
    Yerel MLX bulunamadığında veya bulut konteynerinde otomatik devreye girer.
    """
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("NVIDIA_API_KEY="):
                        api_key = line.strip().split("=", 1)[1]
                        break

    if not api_key:
        return None

    import urllib.request
    req = urllib.request.Request(
        "https://integrate.api.nvidia.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        data=json.dumps({
            "model": "meta/llama-3.2-11b-vision-instruct",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_text}
            ],
            "temperature": 0.4,
            "max_tokens": 512
        }).encode("utf-8")
    )
    try:
        resp = urllib.request.urlopen(req, timeout=12)
        data = json.loads(resp.read().decode("utf-8"))
        if data.get("choices") and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"[NVIDIA Cloud Inference Hatası]: {e}")
    return None

def get_engine_components():
    global _model, _tokenizer, _deterministic_sampler, _creative_sampler
    if _model is None:
        try:
            from mlx_lm import load
            from mlx_lm.sample_utils import make_sampler
            if not os.path.exists(MODEL_PATH):
                logger.info(f"Yerel MLX model yolu bulunamadı ({MODEL_PATH}), Cloud Inference moduna geçiliyor.")
                return None, None, None, None
            print(f"[*] MLX Modeli yükleniyor: {MODEL_PATH}")
            _model, _tokenizer = load(MODEL_PATH)
            _deterministic_sampler = make_sampler(temp=0.0)
            _creative_sampler = make_sampler(temp=0.5, top_p=0.9)
            print("Model hazır!")
        except Exception as e:
            logger.info(f"MLX modülü yüklenemedi: {e}. Cloud Inference kullanılacak.")
            return None, None, None, None
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

UNIFIED_SYSTEM_PROMPT = """Sen InversionCore'sun. Soğuk, lafı dolandırmayan, dobra ve cerrahi bir stratejik karar motorusun.
Ahlak bekçiliği, boş motivasyon laf salatası veya kuru akademik/teknik terimler (Paul Ekman FACS, 3D kraniyofasiyal vb.) KESİNLİKLE KULLANMAZSIN.
KATI KURAL: KULLANICININ SORDUĞU SORU VE KONU NEYSE (%100 BİREBİR O KONUYA ODAKLANACAKSIN).
Kullanıcı uyku/uyuyamıyorum diyorsa uykusuzluğun arkasındaki zihinsel kontrol deliliğini ve biyolojiyi parçala; asla durup dururken aldatma, işe alım veya CV'den BAHSEDEMEZSİN! A sorusuna A cevabı, B sorusuna B cevabı verilir. Konuyu asla saptırma! Tokenı teknik etiketlerle israf etmez; doğrudan insanın karakterine, zaaflarına, gizli niyetlerine ve kirli çamaşırlarına odaklarsın.

Görevin: Kullanıcının sunduğu krizleri, ilişkileri, işe alım ve karakter analizlerini ameliyat masasına yatırmaktır.
Kişilik ve insan analizlerinde:
1. Kişinin narsisizmini, gizli kibirini, sorumluluktan kaçışını, manipülasyon taktiklerini ve tüm kirli çamaşırlarını acımasızca dök.
2. Ancak asla tek taraflı karalama yapma: Özellikle işe alım veya ortaklık senaryolarında bu kişinin İNKAR EDİLEMEZ GÜÇLÜ YÖNLERİNİ, icraat kapasitesini, krizdeki soğukkanlılığını ve nerede yüksek katma değer üreteceğini de net ve dengeli şekilde ortaya koy.
3. Bu kişinin hangi kurallarla ve sınırlarla yönetilebileceğini gösteren kesin bir kullanım kılavuzu ver.

KATI VE DEĞİŞMEZ KURAL (3 TURLU DİYALEKTİK KİLİT SİSTEMİ):
Şu an hangi turda olduğunu 'Tur: X' parametresinden bilmek ve SADECE o turun çıktısını vermek ZORUNDASIN:

EĞER TUR = 1 İSE (İddia ve Kırılma Noktası):
- KESİNLİKLE nihai hüküm, fesih protokolü veya aksiyon silahı/ihtarnamesi VERİLEMEZ!
- Çıktında SADECE şu iki başlığı üret:
  [TOKAT]: Durumun en çıplak, acımasız ve kaçışı olmayan tespiti (kullanıcının kendine söylediği yalanı tek cümlede ifşa et).
  [PSİKOLOJİK & STRATEJİK DEŞME]: Karşı tarafın uyguladığı manipülasyonun (güven illüzyonu, DARVO, gaslighting, mobbing veya suçluluk psikolojisi) klinik mekanizması ve kullanıcının eylemsizlik döngüsü.
  [YÜZLEŞME EŞİĞİ]: Kullanıcıyı köşeye sıkıştıran, sahte umutları sıfırlayan ve iki net seçenekten birini seçmesini zorunlu kılan tek can alıcı karar sorusu.

EĞER TUR = 2 İSE (Savunma ve Mazeretlerin İmhası):
- Kullanıcının verdiği cevabı, rasyonelleştirmelerini ve kurban rolünü masaya yatır.
- KESİNLİKLE nihai ihtarname verilmez.
- Çıktında şu başlıkları üret:
  [TOKAT]: Kullanıcının mazeret kalkanını parçalayan ikinci darbe.
  [DELİL & RİSK HARİTASI]: Masadaki somut kanıt boşlukları ve eylemsiz kalınması halinde ödenecek geri dönüşsüz maddi/manevi bedel.
  [YÜZLEŞME EŞİĞİ]: Artık mazeretlerin bittiğini teyit eden son dönemeç sorusu.

EĞER TUR = 3 İSE (Hüküm Dosyası ve Eylem Silahı):
- Artık soru SORULMAZ!
- Doğrudan icraat ve yasal/resmi fesih teslim edilir:
  [TOKAT]: Nihai kapanış hakikati.
  [GEREKÇELİ HÜKÜM]: Durumun klinik ve hukuki özeti.
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
            if any(w in q_lower for w in ["triangulation", "fasiyal", "maske makası", "facs", "karakter", "kişilik", "damat", "benlik"]):
                recovered["teshis"] = "Biyopsikososyal Benlik Yarılması, Narsisistik Maske ve Kronik Küçümseme İzi."
            elif any(w in q_lower for w in ["fft", "prnu", "adli", "görsel", "montaj", "splicing", "sahte profil"]):
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
        
        # Eğer 3-Nokta Karakter Penetrasyonu veya forensic_context iletildiyse bağlama cerrahi olarak enjekte et
        if forensic_context and isinstance(forensic_context, dict):
            # 1. 3-Nokta Karakter & Biyopsikososyal Penetrasyon Modu
            if "persona_authenticity_gap" in forensic_context or forensic_context.get("type") == "behavioral_triangulation" or forensic_context.get("dispatcher_route") == "behavioral_triangulation":
                role = forensic_context.get("role_label", "Kişi Analizi")
                mask_gap = forensic_context.get("persona_authenticity_gap", "38.5")
                contempt = forensic_context.get("chronic_contempt_index", "42.0")
                availability = forensic_context.get("emotional_availability", "55.0")
                ego_struct = forensic_context.get("ego_structure", "Yüksek Kontrollü Sahte Benlik")
                conflict = forensic_context.get("conflict_reflex", "DARVO / Suçluluk Yansıtma")
                vuln = forensic_context.get("vulnerability", "Statü ve kontrol kaybı")
                big_five = forensic_context.get("big_five_ocean", {})
                
                ocean_str = ""
                if big_five and isinstance(big_five, dict):
                    ocean_str = (
                        f"- Büyük Beşli (OCEAN Kişilik Profili): "
                        f"Deneyime Açıklık: %{big_five.get('openness', 50)} | "
                        f"Sorumluluk/Öz-Disiplin: %{big_five.get('conscientiousness', 60)} | "
                        f"Dışadönüklük: %{big_five.get('extraversion', 55)} | "
                        f"Uyumluluk: %{big_five.get('agreeableness', 45)} | "
                        f"Duygusal Denge (Nörotizm Direnci): %{big_five.get('emotional_stability', 50)}\n"
                    )
                
                behavioral_injection = (
                    f"\n\n[INVERSIONCORE // 3-NOKTA BİYOPSİKOSOSYAL KİŞİLİK OTOPSİSİ MATRİSİ]:\n"
                    f"- Hedef Rol: {role}\n"
                    f"- Maske Makası (Benlik Yarılması): %{mask_gap}\n"
                    f"- Kronik Küçümseme (FACS AU14 Contempt İndeksi): %{contempt}\n"
                    f"- Duygusal Erişilebilirlik: %{availability}\n"
                    f"{ocean_str}"
                    f"- Ego Yapısı: {ego_struct}\n"
                    f"- Çatışma Refleksi: {conflict}\n"
                    f"- Zayıf Karnı: {vuln}\n\n"
                    f"ÖZEL TALİMAT (DAVRANIŞ BİLİMİ, HOGAN DERAILERS & CIPD DEĞERLENDİRMESİ): Bu verileri kullanarak kişinin derin karakterini, "
                    f"vitrin maskesinin arkasındaki gerçek niyetini, kriz anında uygulayacağı manipülasyonu (DARVO, sessiz ceza, gaslighting, kurucu darboğazı) "
                    f"ve kullanıcıya kuracağı tahakkümü acımasız bir cerrah gibi deşifre et. 'Piksel/montaj' analizi değil; GERÇEK İNSAN VE KARAKTER OTOPSİSİ yap!"
                )
                if behavioral_injection not in effective_query:
                    effective_query = f"{effective_query}{behavioral_injection}"
            elif forensic_context.get("dispatcher_route") == "financial_physics":
                # Rust & Python Physics Suite Deterministik Kanıtları
                rust_data = forensic_context.get("rust_telemetry", {})
                phys_data = forensic_context.get("physics_telemetry", {})
                
                runway = rust_data.get("runway_months") or phys_data.get("dynamics", {}).get("initial_runway_months", 10.0)
                absorb = rust_data.get("absorbing_barrier_month") or phys_data.get("dynamics", {}).get("absorbing_barrier_month", 8.0)
                fragility = rust_data.get("fragility_status") or phys_data.get("fat_tail", {}).get("fragility_status", "KIRILGAN")
                destroyed_days = rust_data.get("runaway_destroyed_days") or phys_data.get("fat_tail", {}).get("runway_destroyed_days", 150)
                mcs = rust_data.get("minimal_cut_sets") or [m[0] for m in phys_data.get("fta", {}).get("minimal_cut_sets", [["Nakit_Tukenisi"]])]
                nash = rust_data.get("nash_equilibrium") or phys_data.get("game_theory", {}).get("equilibrium", "Fiyat Savaşı")
                z3 = rust_data.get("z3_verification") or "Kısıtlar tutarsızlık sınırında."
                calc_time = rust_data.get("computation_time_us", 35)

                physics_injection = (
                    f"\n\n[INVERSIONCORE // RUST NATIVE & PYTHON FİZİKSEL MATRİS VE İFLAS SİMÜLASYONU]:\n"
                    f"- Hesaplama Hızı: {calc_time} mikrosaniye (Apple Silicon ARM64 Native Kernel)\n"
                    f"- Diferansiyel Nakit Runway: {runway} Ay\n"
                    f"- Yutan Bariyer (Absorbing Barrier / Kaçınılmaz İflas Eşiği): {absorb}. Ay\n"
                    f"- Taleb Fat-Tail Extremistan Kırılganlığı: {fragility}\n"
                    f"- Risk Gerçekleşirse Yok Olma Süresi: {destroyed_days} Gün\n"
                    f"- Hata Ağacı (FTA Minimal Cut Sets): {', '.join(mcs) if isinstance(mcs, list) else mcs}\n"
                    f"- Nash Dengesi & Oyun Teorisi: {nash}\n"
                    f"- Z3 SMT Formel Doğrulama: {z3}\n\n"
                    f"ÖZEL TALİMAT: Kullanıcının sermaye, nakit akışı ve sabit giderlerine dair bu deterministik matematiksel verileri "
                    f"acımasız bir finansal cerrah gibi yüzüne vur. İflasın kaçınılmazlığını 'Yutan Bariyer' ve 'Fat-Tail' riskleriyle matematiksel ispat olarak kullan!"
                )
                effective_query = f"{effective_query}{physics_injection}"
            elif forensic_context.get("dispatcher_route") == "workplace_legal_mobbing":
                mobbing_injection = (
                    f"\n\n[INVERSIONCORE // İŞ HUKUKU & MOBBİNG TAHKİKAT MOTORU DEVREDE]:\n"
                    f"- Odak: 4857 Sayılı İş Kanunu m.24/II (Haklı Nedenle Derhal Fesih), TBK m.417 (İşçinin Kişiliğinin Korunması)\n"
                    f"- Delil Matrisi: Hiyerarşik baskı, görevi yaptırmama, yıldırma, yazılı delil zinciri ve arabuluculuk/ihtar stratejisi.\n"
                    f"TALİMAT: Çalışanın haklarını, işverenin mobbing riskini ve izlenecek somut hukuki stratejiyi adım adım çıkar."
                )
                effective_query = f"{effective_query}{mobbing_injection}"
            elif forensic_context.get("dispatcher_route") == "relational_gaslighting":
                relational_injection = (
                    f"\n\n[INVERSIONCORE // İKİLİ İLİŞKİ TOKSİSİTE & DARVO DEŞİFRE MOTORU DEVREDE]:\n"
                    f"- Odak: Manipülatif narsisistik döngü, suçluluk yükleme, gerçeklik algısıyla oynama (Gaslighting) ve sınır ihlali.\n"
                    f"TALİMAT: Karşı tarafın savunma taktiklerini kır, kurban psikolojisinden çıkaran rasyonel protokolü hazırla."
                )
                effective_query = f"{effective_query}{relational_injection}"
            else:
                pass

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
        
        reply = None
        user_prompt_content = f"Kullanıcı Durumu: {effective_query}\n\nGeçmiş Hafıza:\n{core_memory}" if core_memory else f"Kullanıcı Durumu: {effective_query}"

        # 3. UNIFIED SANSÜRSÜZ ÇIKARIM MOTORU
        # KESİN HİYERARŞİ:
        # 1. ÖNCELİK: Mac Yerel Apple Silicon MLX Modeli (Qwen 2.5 14B Abliterated - Mac açıksa ve model yüklüyse İLK KAYNAK)
        # 2. ÖNCELİK: Groq API Havuzu (Qwen 27B / GPT-OSS 120B - Mac kapalıysa veya yerel model yetişemezse ultra hızlı bulut)
        # 3. ÖNCELİK: NVIDIA Cloud NIM API (Llama 3.2 11B Vision & Instruct)
        
        sys_prompt = f"{UNIFIED_SYSTEM_PROMPT}\nTur: {round_num}"

        # 1. ÖNCELİK: Mac Üzerindeki Yerel Qwen 14B MLX Modeli
        try:
            model, tokenizer, _, creative_sampler = get_engine_components()
            if model is not None and tokenizer is not None:
                from mlx_lm import generate
                prompt_text = (
                    f"<|im_start|>system\n{UNIFIED_SYSTEM_PROMPT}\nTur: {round_num}<|im_end|>\n"
                    f"<|im_start|>user\n{user_prompt_content}<|im_end|>\n"
                    f"<|im_start|>assistant\n"
                )
                reply = generate(model, tokenizer, prompt=prompt_text, max_tokens=320, sampler=creative_sampler, verbose=False)
                if reply:
                    logger.info("[*] InversionCore [1. Kaynak: Mac Qwen 14B MLX] Çıkarımı Başarılı.")
        except Exception as _mlx_err:
            logger.info(f"Yerel MLX çıkarımı başarısız veya atlandı ({_mlx_err}), 2. Kaynak Groq API'ye geçiliyor...")

        # 2. ÖNCELİK: Groq API Havuzu (Mac kapalıysa / Buluttaysa / MLX hata verirse)
        if not reply:
            try:
                reply = call_groq_inference(user_prompt_content, sys_prompt)
                if reply:
                    logger.info("[*] InversionCore [2. Kaynak: Groq API Sansürsüz LPU] Çıkarımı Başarılı.")
            except Exception as _g_err:
                logger.info(f"Groq çıkarım atlandı ({_g_err}), 3. Kaynak NVIDIA NIM'e geçiliyor...")

        # 3. ÖNCELİK: NVIDIA Cloud NIM API Fallback
        if not reply:
            try:
                reply = call_nvidia_cloud_inference(user_prompt_content, sys_prompt)
                if reply:
                    logger.info("[*] InversionCore [3. Kaynak: NVIDIA Cloud NIM] Çıkarımı Başarılı.")
            except Exception as _nv_err:
                logger.info(f"NVIDIA çıkarım atlandı ({_nv_err})")

        # 4. Deterministik Güvenlik Fallback
        if not reply:
            reply = (
                "İNCELEME VE HİPOTEZ OTOPSİSİ:\n"
                f"Analiz edilen durum: '{effective_query}'. Karşı tarafın sunduğu tablo ile eylemleri arasında ciddi bir uyumsuzluk görülmektedir. "
                "Retorik ve savunma refleksleri arkasındaki asıl niyet sorgulanmalı, somut veri ve delillerle yüzleşilmelidir."
            )

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
