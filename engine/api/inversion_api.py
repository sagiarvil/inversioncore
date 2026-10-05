"""
InversionCore API - Frontend → Backend köprüsü
Kullanıcı metin yükler → ontoloji sınıflandırır → motorlar işler → negatif bilgi döner
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from engine.orchestrator_v2 import InversionOrchestratorV2

app = FastAPI(title="InversionCore API", version="2.1")

# CORS - Frontend erişimine izin ver
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = InversionOrchestratorV2()


class AnalyzeRequest(BaseModel):
    text: str
    customer_id: Optional[str] = "web_user"


class AnalyzeResponse(BaseModel):
    problem_type: str
    motor_results: list
    synthesis: dict
    cache_stats: dict
    cost_summary: dict


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest):
    """
    Kullanıcı metni gönderir → sistem tersine mühendislik yapar → negatif bilgi döner
    """
    if not request.text or len(request.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Metin çok kısa (minimum 10 karakter)")
    
    result = orchestrator.auto_invert(
        text=request.text,
        data={"raw_text": request.text},  # Motorlar bu veriyi işleyecek
        customer_id=request.customer_id
    )
    
    return AnalyzeResponse(**result)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.1"}


# Çalıştırma
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


from fastapi.responses import StreamingResponse
import litellm
import os

class StreamRequest(BaseModel):
    text: str
    system_prompt: str

@app.post("/stream")
async def stream_text(request: StreamRequest):
    if not request.text:
        raise HTTPException(status_code=400, detail="Metin boş")
        
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Backend'de DEEPSEEK_API_KEY bulunamadı!")

    messages = [
        {"role": "system", "content": request.system_prompt},
        {"role": "user", "content": request.text}
    ]

    def token_generator():
        try:
            response = litellm.completion(
                model="deepseek/deepseek-chat",
                messages=messages,
                api_key=api_key,
                api_base="https://api.deepseek.com",
                temperature=0.1,
                max_tokens=750,
                stream=True
            )
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield f"data: {content}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [HATA] {str(e)}\n\n"

    return StreamingResponse(token_generator(), media_type="text/event-stream")
