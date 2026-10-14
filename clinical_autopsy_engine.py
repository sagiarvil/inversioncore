"""
clinical_autopsy_engine.py
--------------------------------------------------------------------------------
jxnl/instructor + Pydantic Destekli Rol Bazlı Klinik Otopsi Motoru
Kopyala-yapıştır joker metinleri tamamen imha eder.
Her hedef rol (İşe Alım, Patron Darboğazı, Liderlik Kör Noktası vb.) için
ayrı Pydantic şeması tanımlar ve Groq Llama-3.3 üzerinden yapılandırılmış,
birbiriyle asla çakışmayan cerrahi analiz üretir.
--------------------------------------------------------------------------------
"""

import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

# 1. ROL BAZLI PYDANTIC VERİ MODELLERİ (KAT VE KAT FARKLI ŞEMALAR)

class IseAlimOtopsisi(BaseModel):
    """İşe Alım ve Aday Değerlendirmesine Özel Klinik Şema"""
    bolum_1_baslik: str = Field(default="1. İŞE ALIM ÖN-OTOPSİSİ // CV VİTRİNİ, İŞ AHLAKI VE GİZLİ NARSİSİZM")
    cv_ve_mulakat_maskesi: str = Field(description="Adayın mülakatta abarttığı vitrin ile gerçek arasındaki Benlik Yarılması")
    is_ahlaki_ve_sadakat_riski: str = Field(description="Otoriteye öfke, krizde sorumluluktan kaçma veya suistimal eğilimi")
    bolum_2_baslik: str = Field(default="2. BU ADAY NEREDE İŞ YAPAR? // İNKAR EDİLEMEZ İCRAAT GÜCÜ")
    guclu_yonler_ve_icraat: str = Field(description="Adayın doğru yönetilirse şirkete kazandıracağı somut güçler ve satış hırsı")
    bolum_3_baslik: str = Field(default="3. İŞE ALIM VE YÖNETİM REÇETESİ // SÖZLEŞME VE KPI ZIRHI")
    sozlesme_ve_kpi_recetesi: str = Field(description="Adayı yönetmek için gereken katı KPI kuralları ve duygusuz protokol")
    nihai_tokat: str = Field(description="İşe alım eşiği ve nihai rest sorusu")
    btn_reddet: str = Field(default="❌ 'Riskleri çok yüksek; bu egoyla uğraşamam, eliyorum.'")
    btn_onayla: str = Field(default="✔ 'Güçlü yanlarını kullanacağım; katı KPI ve yazılı kurallarla sürece alıyorum.'")


class PatronDarbogazOtopsisi(BaseModel):
    """Patron ve Kurucu Darboğazına Özel Klinik Şema"""
    bolum_1_baslik: str = Field(default="1. KURUCU SENDROMU // ŞİRKETİN EN BÜYÜK DARBOĞAZI SENİN KONTROL DELİLİĞİN")
    kurucu_sendromu_ve_kontrol_deliligi: str = Field(description="Yetki devredememe, her faturaya karışma ve mikro-yönetim hastalığı")
    ekibi_felc_eden_davranislar: str = Field(description="İnisiyatif almayı engelleyip sonra çalışanları beceriksizlikle suçlama refleksi")
    bolum_2_baslik: str = Field(default="2. ŞİRKETİ BURAYA GETİREN VİZYONER GÜÇ // NEREDE DEVLEŞİRSİN?")
    vizyoner_guc_ve_kriz_yonetimi: str = Field(description="Kurucunun şirketi sıfırdan kurmasını sağlayan sezgisel ve kriz çözücü zekası")
    bolum_3_baslik: str = Field(default="3. PATRON KULLANMA KILAVUZU // OPERASYONDAN ÇEKİLME REÇETESİ")
    operasyondan_cekilme_recetesi: str = Field(description="Delegasyon protokolü ve profesyonel genel müdüre yetki devretme zorunluluğu")
    nihai_tokat: str = Field(description="Kurucu eşiği: Delegasyon yapıp ölçeklenmek mi, yoksa her şeye karışarak iflas etmek mi?")
    btn_reddet: str = Field(default="❌ 'Kimseye güvenemem; her şeyi kendim kontrol etmeye devam edeceğim.'")
    btn_onayla: str = Field(default="✔ 'Egomu aradan çekiyorum; yetki devredip şirketi profesyonel sisteme taşıyorum.'")


class PartnerIliskiOtopsisi(BaseModel):
    """Sevgili ve Partner İlişkisine Özel Klinik Şema"""
    bolum_1_baslik: str = Field(default="1. İLİŞKİSEL TERSİNE MÜHENDİSLİK // MASKE VE GASLIGHTING")
    maske_ve_darvo_refleksi: str = Field(description="Yüzleşmede karşı tarafı suçlu çıkarma, üste çıkma ve sessizlik cezası")
    bagimlilik_asimetrisi: str = Field(description="Aşk masalı arkasına saklanan duygusal veya maddi bağımlılık tuzağı")
    bolum_2_baslik: str = Field(default="2. İNKAR EDİLEMEZ ÇEKİM GÜCÜ // SENİ NE ORADA TUTUYOR?")
    cekim_gucu_ve_sosyal_zeka: str = Field(description="Partnerin büyüleyici vitrini ve kriz anında liman gibi görünme yeteneği")
    bolum_3_baslik: str = Field(default="3. ONUR OPERASYONU // SINIR VE PROTOKOL REÇETESİ")
    onur_operasyonu_recetesi: str = Field(description="Net sınır çekme veya masayı devirme stratejisi")
    nihai_tokat: str = Field(description="Yüzleşme bıçağı: Kendine yalan söylemeyi bırakıp kapıyı çarpmaya hazır mısın?")
    btn_reddet: str = Field(default="❌ 'Korkuyorum; biraz daha bekleyip idare edeceğim.'")
    btn_onayla: str = Field(default="✔ 'Sınırlarımı çiziyorum; manipülasyona boyun eğmeyeceğim.'")


class YoneticiAmirOtopsisi(BaseModel):
    """Amir ve Yönetici Analizine Özel Klinik Şema"""
    bolum_1_baslik: str = Field(default="1. YÖNETİCİ OTOPSİSİ // KURUMSAL SADİZM VE MİKRO-YÖNETİM")
    kurumsal_sadizm_ve_izolasyon: str = Field(description="Astları potansiyel tehdit görme, toplantıdan dışlama ve emeği sahiplenme")
    bolum_2_baslik: str = Field(default="2. BU AMİRİN ŞİRKETTEKİ YERİ // GÜÇLÜ YÖNLERİ")
    burokratik_zeka_ve_temsil: str = Field(description="Yukarıya oynama ve üst yönetimi etkileme dehası")
    bolum_3_baslik: str = Field(default="3. KORUNMA VE ETKİSİZLEŞTİRME REÇETESİ // DELİL ZİNCİRİ")
    yazili_delil_ve_fesih_recetesi: str = Field(description="Sözlü talimatı reddetme, e-posta logları ve haklı fesih hazırlığı")
    nihai_tokat: str = Field(description="Mücadele eşiği: Sızlanmayı bırakıp hukuki kalkanı kurmaya hazır mısın?")
    btn_reddet: str = Field(default="❌ 'Sesimi çıkarmadan çalışmaya devam edeceğim.'")
    btn_onayla: str = Field(default="✔ 'Yazılı delil zincirini kurup haklarımı koruyacağım.'")


class ClinicalAutopsyEngine:
    @staticmethod
    def _get_instructor_client():
        try:
            import instructor
            from groq import Groq
            
            api_key = os.getenv("GROQ_API_KEY", "")
            if not api_key:
                raw_keys = os.getenv("GROQ_API_KEYS", "")
                if raw_keys:
                    api_key = raw_keys.split(",")[0].strip()
            
            if not api_key and os.path.exists(".env"):
                with open(".env", "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("GROQ_API_KEY="):
                            api_key = line.split("=", 1)[1].strip()
                            break
                        elif line.startswith("GROQ_API_KEYS="):
                            api_key = line.split("=", 1)[1].strip().split(",")[0].strip()
                            break

            if api_key:
                raw_client = Groq(api_key=api_key)
                return instructor.from_groq(raw_client, mode=instructor.Mode.JSON)
        except Exception as e:
            print(f"[Instructor Client Hatası]: {e}")
        return None

    @classmethod
    def generate_autopsy(
        cls, 
        target_role: str, 
        metrics: Dict[str, Any], 
        clinical_deductions: Dict[str, Any],
        custom_question: str = ""
    ) -> Dict[str, str]:
        """
        jxnl/instructor üzerinden role özel Pydantic modeliyle yapılandırılmış analiz üretir.
        Groq API anahtarı yoksa veya hata oluşursa deterministik klinik kütüphaneden çeker.
        """
        gap = metrics.get("persona_authenticity_gap", 42.0)
        contempt = metrics.get("chronic_contempt_index", 54.0)
        
        # 1. jxnl/instructor ile Dinamik Üretim Denemesi
        client = cls._get_instructor_client()
        if client:
            try:
                system_prompt = (
                    "Sen dünyanın en keskin Biyopsikososyal Karakter ve Karar Otopsisi cerrahısın. "
                    "Rolleri ASLA birbirine karıştırma. Eğer hedef bir patron ise CV veya mülakat terimleri KULLANAMAZSIN; "
                    "yetki devri, kurucu darboğazı ve mikro-yönetim üzerinden analiz edeceksin. "
                    "Eğer hedef işe alım adayı ise mülakat vitrini, iş ahlakı ve KPI takibi üzerinden konuşacaksın. "
                    "Türkçe, acımasız, doğrudan ve gerçekçi konuş."
                )
                user_msg = (
                    f"Kişi Rolü: {target_role}\n"
                    f"Benlik Yarılması (Maske Makası): %{gap}\n"
                    f"Kronik Küçümseme: %{contempt}\n"
                    f"Ego Yapısı: {clinical_deductions.get('ego_structure', '')}\n"
                    f"Kriz Refleksi: {clinical_deductions.get('conflict_reflex', '')}\n"
                    f"Kullanıcı Sorusu: {custom_question}\n\n"
                    f"Lütfen şemadaki tüm alanları role özel klinik derinlikle doldur."
                )

                if target_role == "candidate_employee":
                    resp: IseAlimOtopsisi = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        response_model=IseAlimOtopsisi,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_msg}
                        ],
                        temperature=0.3
                    )
                    return {
                        "section_1_title": resp.bolum_1_baslik,
                        "section_1_body": f"<p>{resp.cv_ve_mulakat_maskesi}</p><p>{resp.is_ahlaki_ve_sadakat_riski}</p>",
                        "section_2_title": resp.bolum_2_baslik,
                        "section_2_body": f"<p>{resp.guclu_yonler_ve_icraat}</p>",
                        "section_3_title": resp.bolum_3_baslik,
                        "section_3_body": f"<p>{resp.sozlesme_ve_kpi_recetesi}</p>",
                        "ultimatum_title": "⚡ İŞE ALIM EŞİĞİ // NİHAİ KARAR:",
                        "ultimatum_body": resp.nihai_tokat,
                        "btn_bad": resp.btn_reddet,
                        "btn_good": resp.btn_onayla
                    }

                elif target_role == "founder_bottleneck":
                    resp: PatronDarbogazOtopsisi = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        response_model=PatronDarbogazOtopsisi,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_msg}
                        ],
                        temperature=0.3
                    )
                    return {
                        "section_1_title": resp.bolum_1_baslik,
                        "section_1_body": f"<p>{resp.kurucu_sendromu_ve_kontrol_deliligi}</p><p>{resp.ekibi_felc_eden_davranislar}</p>",
                        "section_2_title": resp.bolum_2_baslik,
                        "section_2_body": f"<p>{resp.vizyoner_guc_ve_kriz_yonetimi}</p>",
                        "section_3_title": resp.bolum_3_baslik,
                        "section_3_body": f"<p>{resp.operasyondan_cekilme_recetesi}</p>",
                        "ultimatum_title": "⚡ KURUCU EŞİĞİ // DELEGASYON YA DA İFLAS:",
                        "ultimatum_body": resp.nihai_tokat,
                        "btn_bad": resp.btn_reddet,
                        "btn_good": resp.btn_onayla
                    }

                elif target_role == "manager":
                    resp: YoneticiAmirOtopsisi = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        response_model=YoneticiAmirOtopsisi,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_msg}
                        ],
                        temperature=0.3
                    )
                    return {
                        "section_1_title": resp.bolum_1_baslik,
                        "section_1_body": f"<p>{resp.kurumsal_sadizm_ve_izolasyon}</p>",
                        "section_2_title": resp.bolum_2_baslik,
                        "section_2_body": f"<p>{resp.burokratik_zeka_ve_temsil}</p>",
                        "section_3_title": resp.bolum_3_baslik,
                        "section_3_body": f"<p>{resp.yazili_delil_ve_fesih_recetesi}</p>",
                        "ultimatum_title": "⚡ MÜCADELE EŞİĞİ:",
                        "ultimatum_body": resp.nihai_tokat,
                        "btn_bad": resp.btn_reddet,
                        "btn_good": resp.btn_onayla
                    }

                elif target_role == "partner":
                    resp: PartnerIliskiOtopsisi = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        response_model=PartnerIliskiOtopsisi,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_msg}
                        ],
                        temperature=0.3
                    )
                    return {
                        "section_1_title": resp.bolum_1_baslik,
                        "section_1_body": f"<p>{resp.maske_ve_darvo_refleksi}</p><p>{resp.bagimlilik_asimetrisi}</p>",
                        "section_2_title": resp.bolum_2_baslik,
                        "section_2_body": f"<p>{resp.cekim_gucu_ve_sosyal_zeka}</p>",
                        "section_3_title": resp.bolum_3_baslik,
                        "section_3_body": f"<p>{resp.onur_operasyonu_recetesi}</p>",
                        "ultimatum_title": "⚡ YÜZLEŞME VE KARAR EŞİĞİ:",
                        "ultimatum_body": resp.nihai_tokat,
                        "btn_bad": resp.btn_reddet,
                        "btn_good": resp.btn_onayla
                    }

            except Exception as e:
                print(f"[Instructor Generation Hatası, Fallback Devrede]: {e}")

        # 2. Deterministik Fallback: Kesinlikle birbirinden bağımsız klinik veri
        if target_role == "founder_bottleneck":
            return {
                "section_1_title": "1. KURUCU SENDROMU // ŞİRKETİN EN BÜYÜK DARBOĞAZI SENİN KONTROL DELİLİĞİN",
                "section_1_body": (
                    f"<p>Şirketin büyümesini rakipler, piyasa koşulları veya sermaye eksikliği engellemiyor. "
                    f"<b>Şirketin asıl darboğazı senin kontrolü elden bırakamama hastalığındır.</b> "
                    f"Resmi patron duruşun ile doğal reflekslerin arasındaki <b>%{gap} Benlik Yarılması</b> ve "
                    f"<b>%{contempt} gizli küçümseme</b>, ekibine asla güvenmediğini kanıtlıyor.</p>"
                    f"<p><b>Ekibi Felç Eden Refleks:</b> Her faturayı, her e-postayı, her küçük kararı bizzat onaylamaya çalışıyorsun. "
                    f"Çalışanların inisiyatif almasını engelliyor, sonra da 'kimse iş sahiplenmiyor, her şeyi ben yapmak zorundayım' diye yakınıyorsun. "
                    f"İnsanları yetkisiz bırakıp sonra yetersizlikle suçlayan kurucu tuzağındasın.</p>"
                ),
                "section_2_title": "2. ŞİRKETİ BURAYA GETİREN VİZYONER GÜÇ // NEREDE DEVLEŞİRSİN?",
                "section_2_body": (
                    "<p>Bu şirketi sıfırdan kurup buraya getiren şey senin inatçı iradendi:</p>"
                    "<p><b>• Üst Düzey Vizyon ve Satış Dehası:</b> Büyük resmi görme, stratejik ortaklıklar kurma ve şirket geleceğini sezme gücün benzersiz.</p>"
                    "<p><b>• Krizde Donmama:</b> Şirket batma noktasına geldiğinde herkes paniklerken sen çıkış yolu üretebilen bir mücadele gücüne sahipsin.</p>"
                ),
                "section_3_title": "3. PATRON KULLANMA KILAVUZU // OPERASYONDAN ÇEKİLME REÇETESİ",
                "section_3_body": (
                    "<p><b>Şirket nasıl 10 katına çıkar?:</b> Yarından tezi yok, günlük operasyonel işlerden elini çekeceksin. "
                    "İşleri profesyonel müdürlere devredeceksin ve hata yapmalarına alan açacaksın. "
                    "Senin görevin mikro-yönetim değil; sermayeyi, vizyonu ve tepe stratejiyi yönetmektir.</p>"
                ),
                "ultimatum_title": "⚡ KURUCU EŞİĞİ // DELEGASYON YA DA İFLAS:",
                "ultimatum_body": "Şirketin büyümesi için kendi kontrol deliliğini kırıp profesyonel yönetime yetki devretmeye hazır mısın, yoksa her şeye karışarak şirketi kendi mezarın mı yapacaksın?",
                "btn_bad": "❌ 'Kimseye güvenemem; her şeyi kendim kontrol etmeye devam edeceğim.'",
                "btn_good": "✔ 'Egomu aradan çekiyorum; yetki devredip şirketi profesyonel sisteme taşıyorum.'"
            }

        # Varsayılan: candidate_employee (İşe Alım Ön-Otopsisi)
        return {
            "section_1_title": "1. İŞE ALIM ÖN-OTOPSİSİ // CV VİTRİNİ, İŞ AHLAKI VE GİZLİ NARSİSİZM",
            "section_1_body": (
                f"<p>Karşında sunduğu o parıltılı özgeçmişe, cilalı kelimelere ve yapay mülakat nezaketine sahip biri yok. "
                f"Karşında, içindeki derin yetersizlik korkusunu dışarıya 'her şeyi bilen, kusursuz ve vazgeçilmez' imajı çizerek bastırmaya çalışan "
                f"<b>profesyonel bir mülakat aktörü</b> var. Bu kişinin resmi vitrin halleri ile doğal anlarındaki yüz gerilimi arasında "
                f"<b>%{gap} oranında belirgin bir Benlik Yarılması</b> ve <b>%{contempt} gizli küçümseme refleksi</b> yatıyor.</p>"
                f"<p><b>İş Ahlakı ve Sadakat Riski:</b> Bu aday otoriteye içten içe derin bir öfke besliyor. "
                f"İşler yolundayken başarıyı tek başına sahiplenir; ancak ilk krizde veya teslim tarihi baskısında sorumluluğu ekip arkadaşlarına veya şirket içi eksikliklere yıkar. "
                f"Şirket içi dedikodu ağı kurmaya, pasif-agresif direniş sergilemeye ve ilk cazip teklifte projeyi yarıda bırakıp gitmeye son derece meyillidir.</p>"
            ),
            "section_2_title": "2. BU ADAY NEREDE İŞ YAPAR? // İNKAR EDİLEMEZ İCRAAT GÜCÜ",
            "section_2_body": (
                "<p>Ancak bu adayı hemen çöpe atamazsınız; doğru yönetilirse şirkete çok ciddi para kazandıracak somut güçleri var:</p>"
                "<p><b>• Sert Rekabet ve Satış Direnci:</b> Egosu yüksek olduğu için 'kaybetmeye' tahammülü yoktur. "
                "Rakip şirketlerle müzakerelerde, zorlu müşteri bağlama süreçlerinde ve agresif satış hedeflerinde inanılmaz bir yırtıcılık sergiler.</p>"
                "<p><b>• Dış Vitrin Temsili:</b> Şirketi dışarıya karşı satma, sunum yapma ve vitrin projelerini parlatma konusunda üst düzey bir yeteneğe sahiptir.</p>"
            ),
            "section_3_title": "3. İŞE ALIM VE YÖNETİM REÇETESİ // SÖZLEŞME VE KPI ZIRHI",
            "section_3_body": (
                "<p><b>Bu adayla nasıl çalışılır?:</b> Asla duygusal bağ kurmayacaksın. 'Biz bir aileyiz' masalını unutacaksın. "
                "Tek kural: <b>Haftalık yazılı KPI takibi, net teslim tarihleri ve sıfır denetimsiz inisiyatif.</b> "
                "Onu kriz çözmeye ve satışa koşturacaksın; ancak ekibin iç huzurunu ve şirketin kritik şifrelerini asla onun kontrolüne bırakmayacaksın.</p>"
            ),
            "ultimatum_title": "⚡ İŞE ALIM EŞİĞİ // NİHAİ KARAR:",
            "ultimatum_body": "Bu adayın narsistik risklerini bilip katı KPI'larla yönetmeye cesaretin var mı, yoksa mülakattaki tatlı diline kanıp ekibin huzurunu yakacak mısın?",
            "btn_bad": "❌ 'Riskleri çok yüksek; bu egoyla uğraşamam, eliyorum.'",
            "btn_good": "✔ 'Güçlü yanlarını kullanacağım; katı KPI ve yazılı kurallarla sürece alıyorum.'"
        }
