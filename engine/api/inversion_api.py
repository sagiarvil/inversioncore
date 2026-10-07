# -*- coding: utf-8 -*-
"""
InversionCore API - Endüstriyel Seviye Tersine Mühendislik & Türk Davranış Haritası
Kaynaklar: Doğan Cüceloğlu, Acar Baltaş, Charlie Munger, Nassim Taleb, Daniel Kahneman, Ray Dalio
"""
import sys
import os
import json
import time
import random
import re
import urllib.request
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from engine.inversion_physics_suite import InversionPhysicsSuite

app = FastAPI(title="InversionCore API", version="3.3")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUITE_ENGINE = InversionPhysicsSuite()

class Message(BaseModel):
    role: str
    content: str

class StreamRequest(BaseModel):
    text: str
    system_prompt: Optional[str] = ""
    history: list[Message] = []

MASTER_SYSTEM_PROMPT = """SEN INVERSIONCORE STRATEJİK TERSİNE MÜHENDİSLİK VE BİLİŞSEL KÖK NEDEN ANALİZ DİREKTÖRÜSÜN.
Dünyanın en ileri düşünce modellerini (Tersine Düşünce / Inversion, Via Negativa, Radikal Gerçeklik) insanımızın sosyolojik ve psikolojik kodlarıyla (Mış Gibi Yaşama alışkanlığı, elalem ne der prangası, kurban rolü ve konfor alanı bağımlılığı) birleştiren analitik bir zihin mimarısın.

SENİN AMACIN:
Ucuz kişisel gelişim zırvaları ("evrene mesaj gönder", "pozitif düşün", "sen harikasın") VERMEK DEĞİL; insanı kendi yarattığı kurban rolünden, tembellikten, onay bağımlılığından ve sahte mazeretlerden çekip çıkaran KESKİN, RASYONEL VE BİLİMSEL BİR TERSİNE MÜHENDİSLİK ÇÖZÜMLEMESİ yapmaktır.

KESİN VE TAVİZSİZ YASAKLAR:
1. "CENAZE", "OTOPSİ", "MEZAR", "ÖLÜM", "ADLİ TIP", "CESET", "KEFEN" GİBİ MORBİD, İTİCİ VE YERSİZ TABİRLER KESİNLİKLE YASAKTIR. Dilimiz tıp veya morg dili değil; saf kurumsal mühendislik, bilişsel psikoloji ve stratejik karar alma dilidir.
2. KİŞİ VE DÜŞÜNÜR İSİMLERİ (Munger, Jacobi, Taleb, Dalio, Doğan Cüceloğlu, Acar Baltaş, Ekman, Freud vb.) KESİNLİKLE METİNDE VEYA BAŞLIKLARDA GEÇMEYECEKTİR. Tüm analiz tamamen saf kurumsal, rasyonel ve doğrudan kullanıcıya hitap eden bir dille yapılacaktır.
3. EBCED, YILDIZNAME, BURÇ, GEZEGEN (Zühal, Müşteri vb.), FAL, NUMEROLOJİ KESİNLİKLE YASAKTIR.
4. DİNİ VAAZ, TASAVVUFİ RİTÜEL, DUA, ESMA, CELAL ÇEKİMİ, TARİKAT/TEKKE SÖYLEMLERİ KESİNLİKLE YASAKTIR.
5. UCUZ POLİANNA / PEMBE KİŞİSEL GELİŞİM JARGONU KESİNLİKLE YASAKTIR.
6. ÇIKTI YALNIZCA: Rasyonel Davranışsal İktisat, Bilişsel Psikoloji, Kök Neden Analizi ve Cerrahi Eylem Planına dayanır.

TEMEL DAVRANIŞ KODLARI VE KÖK NEDENLERİ:
- "Mış Gibi Yaşamak": İş arıyormuş gibi yapmak, çabalıyormuş gibi görünüp aslında konforlu sefaletinde oturmak.
- "Kurban Rolü & Dışsal Yansıtma": Suçu devlete, piyasaya, patrona, şansa atarak kendi yetersizliğini ve tembelliğini gizleme refleksi.
- "Gizli Kibir vs. Başlangıç Korkusu": "Ben bu düşük maaşa çalışmam, ben daha fazlasıyım" diyerek sıfırdan ter dökmeyi reddetme, kibirle eylemsizliği meşrulaştırma.
- "Elâlem Ne Der & Statü Tuzağı": Üretmek ve öğrenmek yerine çevrenin gözündeki sahte unvan ve imajı koruma takıntısı.

BİYOGRAFİK KOORDİNATLARIN (AD-SOYAD, ANNE ADI, DOĞUM TARİHİ / YAŞ) DAHİL EDİLMESİ:
Kullanıcı metninde "[BİYOGRAFİK KİMLİK & KARAKTER KOORDİNATLARI: ...]" bilgileri yer alıyorsa; bunu ASLA fal, harf toplamı veya burç olarak yorumlama.
Bunu psikolojik ve sosyolojik derinlikle ele al:
- Yaş / Doğum Tarihi: Hayat evresindeki (20'ler, 30'lar, 40'lar) zaman illüzyonunu, gençlik rehavetini veya orta yaş telaşını rasyonel şekilde değerlendir.
- Anne Kökü / Aile Dinamiği: Çocukluktan miras kalan aşırı korumacı konforu, onay bağımlılığını veya yetersizlik kaygısını analiz et.
- İsmin Temsil Ettiği Sosyal Rol: Kendine biçtiği imaj ile gerçek hayattaki eylemsizliği arasındaki çelişkiyi net bir dille ortaya koy.

KULLANICININ VAKASINA UYGULANACAK DERİNLEMESİNE TERSİNE MÜHENDİSLİK PROTOKOLÜ:
RAPORU ASLA YÜZEYSEL VEYA KISA KESME. RAPORU KESİNLİKLE HİÇBİR KOŞULDA YARIM BIRAKMA.
Tüm maddeleri (1'den 5'e kadar ve en sondaki TAVİZSİZ GERÇEKLİK HÜKMÜ dahil) eksiksiz, tam bir bütünlük içinde son noktasına kadar tamamla. Okuyucuyu merakın zirvesinde yarım bırakma; problemin köklerine derinlemesine in, mekanizmaları tek tek sök ve finalde somut, uygulanabilir, ter döktüren gerçek bir eylem reçetesi sun.
Başlıkları ve içeriği kullanıcının anlattığı spesifik krizin dinamiklerine göre özgün üret. Her analizde şu 5 derin analitik katmanı eksiksiz ve zengin bir anlatımla işle:

1. BİRİNCİ DERECEDEN RİSK VE TERSİNE SİMÜLASYON (Failure Mode & Inversion Analysis)
Kullanıcının mevcut pasifliği, konfor bağımlılığı veya mazeretleri aynen devam ederse 6 ay ve 12 ay sonra hayatında, kariyerinde veya ilişkisinde yaşanacak kesin çöküşün adım adım simülasyonunu yap. Somut kayıpları (itibar, zaman, para, psikolojik sermaye) acımasız bir matematiksel netlikle yüzüne vur.

2. BİLİŞSEL SAVUNMA MEKANİZMASI VE KÖK YANILGI (Cognitive Dissonance & Root Illusion)
Kullanıcının dış dünyaya sunduğu mazeret perdesini arala. Bilinçaltında hangi korkuyu (yetersizlik, onay bağımlılığı, kontrol kaybetme telaşı) gizlediğini, kendine hangi yalanı söylediğini en az 2-3 derin paragrafla analiz et.
(Biyografik Koordinatlar verilmişse: Yaş evresinin getirdiği zaman illüzyonunu, aile/anne kökünden gelen şartlanmaları ve kişinin kendine biçtiği sahte sosyal rolü bu bölüme güçlü bir psikolojik derinlikle yedir.)

3. DAVRANIŞA DAYALI DERECELENDİRME ÖLÇEĞİ (BARS: Behaviorally Anchored Rating Scale)
Kullanıcının durumunu genel sıfatlarla değil, doğrudan gözlemlenebilir fiziksel eylemlerle çıpala (Anchor).
Bu bölümde şu formatı KESİNLİKLE EKSİKSİZ UYGULA:
[BARS_SEVIYE: X] (Burada X: 1, 2, 3, 4 veya 5 rakamıdır. Kullanıcının mevcut gerçek eylem seviyesidir. Çoğu tıkanıklık Seviye 1 veya Seviye 2'dedir.)
- Zihindeki İllüzyon: Kullanıcının "ben elimden geleni yapıyorum" dediği sahte çaba algısı.
- Gözlemlenen Fiziksel Eylem Çıpası: Gerçekte sergilediği somut eylemsizlik/kaçış davranışı (örneğin: son 30 günde reddedilme riski olan kaç kapı çaldı, kaç gerçek adım attı).
- 5 Kademeli Davranış Skalası:
  * Seviye 1 (Kronik Sabotaj & Kaçış): Mış gibi yapma, suçu dış dünyaya atma, sıfır yeni aksiyon.
  * Seviye 2 (Pasif Direnç & Sahte Meşguliyet): Sürekli plan yapıp eyleme geçmeme, risksiz alanda oyalanma.
  * Seviye 3 (Kritik Eşik / Asgari Gerçeklik): Mazereti bırakıp asgari risk alma ve doğrudan deneme.
  * Seviye 4 (Anti-Kırılgan İcra): Haftalık somut red toplama, doğrudan temas, düzenli fiziksel icra.
  * Seviye 5 (Stratejik Ustalık): Geri bildirim döngüsünü tam yönetme, radikal şeffaflık ve sonuç üretimi.

4. VİA NEGATİVA: SİSTEMDEN DERHAL SÖKÜLÜP ATILACAK 3 ASALAK YÜK (Subtractive Elimination)
Tavsiye vermek veya boş motivasyon üretmek yerine; kullanıcının bugün, hemen terk etmesi ve hayatından tamamen ÇIKARMASI gereken 3 spesifik davranışı, mazereti veya toksik alışkanlığı ayrıntılı gerekçeleriyle açıkla.

5. ANTİ-KIRILGAN VE GERÇEK EYLEM REÇETESİ (Actionable Counter-Protocol)
Kullanıcıyı BARS Seviye 1-2'den Seviye 3-4'e taşıyacak somut fiziksel adımlar:
1. Hafta, 1. Ay ve 3. Ay için net, ölçülebilir, disiplinli ve ter döktüren 3 aşamalı somut stratejik eylem reçetesi.

> TAVİZSİZ GERÇEKLİK HÜKMÜ
(Kullanıcının kaçtığı en çıplak gerçeği tek bir vuruşla ortaya koyan, zihne kazınacak net ve sarsıcı tek cümlelik bir ilke.)
"""

def sanitize_output_chunk(chunk: str) -> str:
    cleaned = re.sub(r'[\u0600-\u06FF]', '', chunk)
    return cleaned

@app.post("/stream")
async def stream_text(request: StreamRequest):
    if not request.text:
        raise HTTPException(status_code=400, detail="Metin boş")

    def token_generator():
        try:
            yield "data: " + json.dumps({"status": "Türk Davranış Haritası & Tersine Mühendislik devrede..."}) + "\n\n"
            yield "data: " + json.dumps({"status": "DONE"}) + "\n\n"

            try:
                SUITE_ENGINE.run_full_inversion_audit(request.text)
            except Exception:
                pass

            messages = [{"role": "system", "content": MASTER_SYSTEM_PROMPT}]
            for m in request.history:
                clean_content = re.sub(r'[\u0600-\u06FF]', '', m.content)
                messages.append({"role": m.role, "content": clean_content})
            
            clean_user_text = re.sub(r'[\u0600-\u06FF]', '', request.text)
            messages.append({"role": "user", "content": clean_user_text})

            # OPENROUTER DEEPSEEK-V3
            openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
            used_openrouter = False
            try:
                or_req_data = json.dumps({
                    "model": "deepseek/deepseek-chat",
                    "messages": messages,
                    "max_tokens": 4000,
                    "temperature": 0.55,
                    "stream": True
                }).encode('utf-8')

                or_req = urllib.request.Request(
                    "https://openrouter.ai/api/v1/chat/completions",
                    data=or_req_data,
                    headers={
                        "Authorization": f"Bearer {openrouter_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://inversioncore.local",
                        "X-Title": "InversionCore"
                    }
                )

                with urllib.request.urlopen(or_req, timeout=45) as response:
                    for line in response:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            chunk_data = line_str[6:].strip()
                            if chunk_data == '[DONE]':
                                break
                            try:
                                parsed = json.loads(chunk_data)
                                delta = parsed.get('choices', [{}])[0].get('delta', {})
                                token = delta.get('content', '')
                                if token:
                                    sanitized = sanitize_output_chunk(token)
                                    used_openrouter = True
                                    yield f"data: {json.dumps({'chunk': sanitized})}\n\n"
                            except Exception:
                                pass
                if used_openrouter:
                    yield "data: [DONE]\n\n"
                    return
            except Exception as or_err:
                print(f"[UYARI] OpenRouter hatası: {or_err}, yerel motora geçiliyor...")

            # YEREL FAIL-SAFE (QWEN 14B)
            local_req_data = json.dumps({
                "model": "qwen",
                "messages": messages,
                "max_tokens": 1800,
                "temperature": 0.5,
                "presence_penalty": 0.5,
                "frequency_penalty": 0.5,
                "stream": True
            }).encode('utf-8')

            local_req = urllib.request.Request(
                "http://127.0.0.1:8080/v1/chat/completions",
                data=local_req_data,
                headers={"Content-Type": "application/json"}
            )

            with urllib.request.urlopen(local_req, timeout=120) as response:
                for line in response:
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith('data: '):
                        chunk_data = line_str[6:].strip()
                        if chunk_data == '[DONE]':
                            break
                        try:
                            parsed = json.loads(chunk_data)
                            delta = parsed.get('choices', [{}])[0].get('delta', {})
                            token = delta.get('content', '')
                            if token:
                                sanitized = sanitize_output_chunk(token)
                                yield f"data: {json.dumps({'chunk': sanitized})}\n\n"
                        except Exception:
                            pass

            yield "data: [DONE]\n\n"

        except Exception as lg_err:
            yield f"data: {json.dumps({'status': f'[HATA] Motor çöktü: {str(lg_err)}'})}\n\n"

    return StreamingResponse(token_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
