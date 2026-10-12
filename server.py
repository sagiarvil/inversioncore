import os
import time
import asyncio
import uvicorn
from typing import Optional, Dict, Any
from collections import defaultdict
from fastapi import FastAPI, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from inversion_engine import InversionCoreEngine
from inversion_memory import InversionMemoryStore

PORT = int(os.getenv("PORT", "8888"))
HOST = os.getenv("HOST", "0.0.0.0")
INVERSION_API_KEY = os.getenv("INVERSION_API_KEY", "inv_prod_live_sec_key_2026")

app = FastAPI(
    title="InversionCore Cognitive Engine",
    description="Asperger rasyonelliği, yeraltı realizmi ve Letta bellek tabanlı tersine karar motoru",
    version="2.1.1"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. IP Tabanlı Rate Limiter (Token-Bucket: Dakikada max 15 istek)
_request_counts = defaultdict(list)
RATE_LIMIT_PER_MINUTE = 15

@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    # Sağlık kontrolünü ve CORS preflight isteklerini rate limit'ten muaf tut
    if request.method == "OPTIONS" or request.url.path in ["/api/health", "/docs", "/openapi.json"]:
        return await call_next(request)
        
    client_ip = request.headers.get("x-forwarded-for") or (request.client.host if request.client else "unknown")
    if "," in client_ip:
        client_ip = client_ip.split(",")[0].strip()
        
    now = time.time()
    # 60 saniyeden eski kayıtları sil
    _request_counts[client_ip] = [t for t in _request_counts[client_ip] if now - t < 60]
    
    if len(_request_counts[client_ip]) >= RATE_LIMIT_PER_MINUTE:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Çok fazla istek yapıldı. Sunucu ve model güvenliği için lütfen 1 dakika bekleyin."}
        )
        
    _request_counts[client_ip].append(now)
    return await call_next(request)

class AnalyzeRequest(BaseModel):
    decision: str = Field(..., description="Kullanıcının masaya yatırdığı ikilem veya karar")
    round: int = Field(default=1, ge=1, le=5, description="Diyalog turu")
    session_id: Optional[str] = Field(default=None, description="Letta durum oturum ID'si")

class AnalyzeResponse(BaseModel):
    status: str
    model: str
    round: int
    session_id: str
    system2_matrix: Optional[Dict[str, Any]] = None
    reply: str

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "engine": "FastAPI + MLX Qwen2.5-14B Abliterated",
        "port": PORT,
        "rate_limiting": "active (15 req/min)"
    }

@app.post("/api/inversion-analyze", response_model=AnalyzeResponse)
async def analyze_decision(req: AnalyzeRequest, request: Request):
    # API Anahtarı Kontrolü (Opsiyonel header denetimi)
    req_key = request.headers.get("X-API-Key")
    if req_key and req_key != INVERSION_API_KEY:
        raise HTTPException(status_code=403, detail="Geçersiz API Anahtarı.")
        
    try:
        # MLX model çıkarımı CPU/GPU yoğun olduğu için event loop'u bloklamamak adına threadpool'da çalıştırılır
        result = await asyncio.to_thread(
            InversionCoreEngine.process_turn,
            decision=req.decision,
            round_num=req.round,
            session_id=req.session_id
        )
        return AnalyzeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Çıkarım motoru hatası: {str(e)}")

@app.get("/api/memory/{session_id}")
async def get_session_memory(session_id: str):
    core = InversionMemoryStore.get_core_memory(session_id)
    history = InversionMemoryStore.get_recall_history(session_id)
    return {
        "session_id": session_id,
        "core_memory": core,
        "recall_history": history
    }

if __name__ == "__main__":
    print(f"InversionCore FastAPI Motoru Başlatılıyor (Async Worker Etkin): http://{HOST}:{PORT}")
    uvicorn.run("server:app", host=HOST, port=PORT, reload=False, workers=1)
