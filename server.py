import os
import time
import asyncio
from collections import defaultdict
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional

from inversion_engine import InversionCoreEngine, InversionOutput
from inversion_memory import get_core_memory, get_recall_history

app = FastAPI(title="InversionCore Enterprise Engine", version="1.4.0")

# CORS Yapılandırması
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PORT = int(os.getenv("PORT", "8888"))
INVERSION_API_KEY = os.getenv("INVERSION_API_KEY", "inv_prod_live_sec_key_2026")

# In-Memory Token Bucket Rate Limiter
RATE_LIMIT_PER_MINUTE = 15
ip_request_history = defaultdict(list)

@app.middleware("http")
async def security_and_rate_limit_middleware(request: Request, call_next):
    # 1. OPTIONS (CORS preflight), statik dosyalar ve sağlık uç noktaları muaf
    if request.method == "OPTIONS" or request.url.path in ["/api/health", "/docs", "/openapi.json"]:
        return await call_next(request)
    
    # 2. Sıkı API Key Doğrulaması (Authentication Bypass Kökten Kapatıldı)
    if request.url.path.startswith("/api/"):
        req_key = request.headers.get("X-API-Key")
        # req_key yoksa VEYA eşleşmiyorsa kesinlikle reddet
        if not req_key or req_key != INVERSION_API_KEY:
            return Response(content='{"detail": "Yetkisiz Erişim: Geçersiz veya eksik API Anahtarı."}', 
                            status_code=403, media_type="application/json")

    # 3. IP Tabanlı Rate Limiting
    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()
    ip_request_history[client_ip] = [t for t in ip_request_history[client_ip] if current_time - t < 60]

    if len(ip_request_history[client_ip]) >= RATE_LIMIT_PER_MINUTE:
        return Response(content='{"detail": "Hız Sınırı Aşıldı: Dakikada maksimum 15 istek gönderebilirsiniz."}', 
                        status_code=429, media_type="application/json")

    ip_request_history[client_ip].append(current_time)
    return await call_next(request)

class AnalyzeRequest(BaseModel):
    decision: Optional[str] = Field(default="", description="Kullanıcı kararı")
    query: Optional[str] = Field(default="", description="Kullanıcı sorgusu")
    session_id: str = "default_session"
    round: int = 1

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "engine": "InversionCore Neural Engine",
        "architecture": "Single-Pass Fast Engine with SQLite WAL Memory",
        "timestamp": time.time()
    }

@app.post("/api/inversion-analyze", response_model=InversionOutput)
async def analyze_decision(req: AnalyzeRequest):
    try:
        user_input = req.decision if req.decision else req.query
        # MLX çıkarımı FastAPI event-loop'unu dondurmasın diye threadpool'a devredilir
        result = await asyncio.to_thread(
            InversionCoreEngine.process_turn,
            session_id=req.session_id,
            user_query=user_input,
            round_num=req.round,
            decision=req.decision
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inversion Engine Hatası: {str(e)}")

@app.get("/api/memory/{session_id}")
async def get_session_memory_endpoint(session_id: str):
    core = get_core_memory(session_id)
    history = get_recall_history(session_id)
    return {
        "session_id": session_id,
        "core_memory": core,
        "recall_history": history
    }

# Statik Dosyalar (En altta mount edilir)
if os.path.exists("public"):
    app.mount("/", StaticFiles(directory="public", html=True), name="public")

if __name__ == "__main__":
    import uvicorn
    print(f"InversionCore Enterprise Engine Başlatılıyor: http://0.0.0.0:{PORT}")
    uvicorn.run("server:app", host="0.0.0.0", port=PORT, reload=False)
