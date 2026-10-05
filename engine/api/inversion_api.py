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
