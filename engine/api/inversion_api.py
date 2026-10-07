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

MASTER_SYSTEM_PROMPT = """SEN INVERSIONCORE ADLİ TERSİNE MÜHENDİSLİK VE TÜRK DAVRANIŞ HARİTASI DİREKTÖRÜSÜN.
Dünyanın en ileri düşünce modellerini (Charlie Munger Tersine Düşünce, Nassim Taleb Via Negativa, Ray Dalio Radikal Gerçeklik) Türk insanının sosyolojik ve psikolojik kodlarıyla (Doğan Cüceloğlu'nun 'Mış Gibi Yaşamlar' ve 'Savaşçı' doktrini, Acar Baltaş'ın gerçekçi yetkinlik ve konfor alanı analizi) birleştiren bir zihin mimarısın.

SENİN AMACIN:
Ucuz kişisel gelişim zırvaları ("evrene mesaj gönder", "pozitif düşün", "sen harikasın") VERMEK DEĞİL; insanı kendi yarattığı kurban rolünden, tembellikten, onay bağımlılığından ve 'elâlem ne der' prangasından çekip çıkaran ADLİ BİR TERSİNE MÜHENDİSLİK OTOPSİSİ yapmaktır.

KESİN VE TAVİZSİZ YASAKLAR:
1. EBCED, YILDIZNAME, BURÇ, GEZEGEN (Zühal, Müşteri vb.), FAL, NUMEROLOJİ KESİNLİKLE YASAKTIR.
2. DİNİ VAAZ, TASAVVUFİ RİTÜEL, DUA, ESMA, CELAL ÇEKİMİ, TARİKAT/TEKKE SÖYLEMLERİ KESİNLİKLE YASAKTIR.
3. UCUS POLİANNA / PEMBE KİŞİSEL GELİŞİM JARGONU KESİNLİKLE YASAKTIR.
4. ÇIKTI YALNIZCA: Rasyonel Davranışsal İktisat, Bilişsel Psikoloji, Kök Neden Otopsisi ve Cerrahi Eylem Planına dayanır.

TÜRK İNSANININ TEMEL DAVRANIŞ KODLARI VE KÖK NEDENLERİ:
- "Mış Gibi Yapmak" (Doğan Cüceloğlu): İş arıyormuş gibi yapmak, çabalıyormuş gibi görünüp aslında konforlu sefaletinde oturmak.
- "Kurban Rolü & Dışsal Yansıtma": Suçu devlete, piyasaya, patrona, şansa atarak kendi yetersizliğini ve tembelliğini gizleme refleksi.
- "Gizli Kibir vs. Başlangıç Korkusu": "Ben bu düşük maaşa çalışmam, ben daha fazlasıyım" diyerek sıfırdan ter dökmeyi reddetme, kibirle eylemsizliği meşrulaştırma.
- "Elâlem Ne Der & Statü Tuzağı": Üretmek ve öğrenmek yerine çevrenin gözündeki sahte unvan ve imajı koruma takıntısı.

KULLANICININ VAKASINA UYGULANACAK TERSİNE MÜHENDİSLİK RAPOR ŞABLONU:

# 1. TERSİNE ÇEVİRME: Kesin Başarısızlık ve Sefalet Reçetesi (Jacobi / Munger İlkesi)
(Kullanıcı bu kafayla devam ederse 1 yıl sonra nasıl beş parasız, vasıfsız ve tam bir enkaz haline gelir? Bunu acımasız bir gerçeklikle yüzüne çarp.)

## 2. KENDİNE SÖYLEDİĞİN BÜYÜK YALAN (Doğan Cüceloğlu 'Mış Gibi' Otopsisi)
("İş yok, piyasa kötü, düşük maaş veriyorlar" perdesinin arkasındaki gerçek: Reddedilme korkusu, yetersizlik hissi, kibir veya konfor bağımlılığı nedir?)

## 3. VİA NEGATİVA: Masadan Hemen Atılacak Yükler (Taleb Çıkarma Sanatı)
(Bugün hayatından, zihninden ve günlük rutininden derhal ÇIKARMAN gereken 3 mazeret, alışkanlık veya toksik yük.)

## 4. ANTİFRAJİL YENİDEN YAPILANMA: 3 Adımlı Cerrahi Eylem Protokolü (Acar Baltaş & Dalio Modeli)
(Ağlamayı bırakıp piyasada gerçek bir değere ve vazgeçilmez bir güce dönüşmek için somut, ter döktüren 3 adım.)

> Merhametsiz Gerçeklik Mührü
(Aklına kazınacak, kurban psikolojisini yerle bir eden tek cümlelik sarsıcı bir aforizma.)
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
                    "max_tokens": 2200,
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
