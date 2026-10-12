import os
import uvicorn
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from inversion_engine import InversionCoreEngine
from inversion_memory import InversionMemoryStore

PORT = int(os.getenv("PORT", "8888"))
HOST = os.getenv("HOST", "0.0.0.0")

app = FastAPI(
    title="InversionCore Cognitive Engine",
    description="Asperger rasyonelliği, yeraltı realizmi ve Letta bellek tabanlı tersine karar motoru",
    version="2.0.0"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "port": PORT
    }

@app.post("/api/inversion-analyze", response_model=AnalyzeResponse)
async def analyze_decision(req: AnalyzeRequest):
    try:
        result = InversionCoreEngine.process_turn(
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

# Statik dosyaları sun (public dizini)
if os.path.exists("public"):
    app.mount("/", StaticFiles(directory="public", html=True), name="static")

if __name__ == "__main__":
    print(f"InversionCore FastAPI Motoru Başlatılıyor: http://{HOST}:{PORT}")
    uvicorn.run("server:app", host=HOST, port=PORT, reload=False)
