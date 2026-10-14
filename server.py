import os
import time
import json
import re
import asyncio
from collections import defaultdict
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional

from inversion_engine import InversionCoreEngine, InversionOutput, get_engine_components
from inversion_memory import get_core_memory, get_recall_history

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Model Warmup (Sunucu ayağa kalkarken modeli RAM'e yükler)
    try:
        print("[*] Model RAM'e yükleniyor (Warmup)...")
        get_engine_components()
        print("[*] Model Warmup Başarıyla Tamamlandı!")
    except Exception as e:
        print(f"[!] Warmup hatası: {e}")
    yield

app = FastAPI(title="InversionCore Enterprise Engine", version="1.4.0", lifespan=lifespan)

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
RATE_LIMIT_PER_MINUTE = 60
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
    decision_text: Optional[str] = Field(default="", description="Kullanıcı karar metni (alias)")
    query: Optional[str] = Field(default="", description="Kullanıcı sorgusu")
    role: Optional[str] = Field(default="", description="Seçilen analiz rolü")
    session_id: str = "default_session"
    round: int = 1
    forensic_context: Optional[dict] = Field(default=None, description="Adli görsel ve sinyal matrisi")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "engine": "InversionCore Neural Engine",
        "architecture": "Single-Pass Fast Engine with SQLite WAL Memory",
        "timestamp": time.time()
    }

from forensic_engine import ProfessionalForensicEngine
from behavioral_profiler import HumanBehavioralProfiler
from task_dispatcher import TaskDispatcher, EngineRoute
import base64

class TriangulationRequest(BaseModel):
    formal_image: Optional[str] = Field(default=None, description="Slot 1: Vitrin / Resmi poz (Base64)")
    candid_image: Optional[str] = Field(default=None, description="Slot 2: Doğal / Spontan an (Base64)")
    social_image: Optional[str] = Field(default=None, description="Slot 3: Sosyal / Beden dili (Base64)")
    target_role: str = Field(default="partner", description="Hedef rol")
    custom_question: Optional[str] = Field(default="", description="Kullanıcının özel sorusu veya şüphesi")
    session_id: Optional[str] = Field(default="default_session", description="Oturum kimliği")

@app.post("/api/triangulation-audit")
async def triangulation_personality_audit(req: TriangulationRequest):
    try:
        # Çift / Aynı Görsel Yükleme Koruması (Deduplication Check)
        if req.formal_image and req.candid_image:
            f_clean = req.formal_image.split(",", 1)[-1].strip()[:200]
            c_clean = req.candid_image.split(",", 1)[-1].strip()[:200]
            if f_clean == c_clean:
                raise HTTPException(
                    status_code=400, 
                    detail="Aynı görseli iki kez yükleyemezsiniz. Maske Makasını hesaplamak için 1 Vitrin ve 1 Doğal olmak üzere 2 farklı durumsal fotoğraf şarttır."
                )

        result = await asyncio.to_thread(
            HumanBehavioralProfiler.analyze_triangulation,
            formal_img=req.formal_image,
            candid_img=req.candid_image,
            social_img=req.social_image,
            target_role=req.target_role,
            custom_question=req.custom_question or ""
        )
        
        # 2. Görsel Hafızanın Metin Sohbetine Akması (Cross-Modal Memory Bridge)
        # Karakter otopsisi tamamlandığında özet ve profil doğrudan core_memory tablosuna işlenir
        # 3. Gerçek Nöral Multimodal AI Vision (Llama 3.2 Vision ile fotoğrafların doğrudan analizi)
        try:
            from multimodal_vision_engine import MultimodalVisionEngine
            imgs_to_send = [img for img in [req.formal_image, req.candid_image, req.social_image] if img]
            mm_result = await asyncio.to_thread(
                MultimodalVisionEngine.analyze_character_from_images,
                images_base64=imgs_to_send,
                target_role=req.target_role,
                custom_question=req.custom_question or ""
            )
            if mm_result and "section_1_title" in mm_result:
                result["autopsy_sections"] = mm_result
                if "mask_gap_percent" in mm_result and "metrics" in result:
                    result["metrics"]["persona_authenticity_gap"] = mm_result["mask_gap_percent"]
                if "contempt_percent" in mm_result and "metrics" in result:
                    result["metrics"]["chronic_contempt_index"] = mm_result["contempt_percent"]
        except Exception as mm_err:
            print(f"[Multimodal Vision Hatası]: {mm_err}")

        if req.session_id:
            summary = result.get("summary", "")
            metrics = result.get("metrics", {})
            big5 = metrics.get("big_five_ocean", {})
            profile_snapshot = (
                f"Karakter Profili [{result.get('role_label')}]: "
                f"Maske Makası %{metrics.get('persona_authenticity_gap')}, "
                f"Küçümseme %{metrics.get('chronic_contempt_index')}, "
                f"Açıklık %{big5.get('openness')}, Sorumluluk %{big5.get('conscientiousness')}, "
                f"Uyumluluk %{big5.get('agreeableness')}. "
                f"Ego: {result.get('clinical_deductions', {}).get('ego_structure')}. "
                f"Risk: {result.get('clinical_deductions', {}).get('risk_level')}"
            )
            from inversion_memory import update_core_memory, append_message
            update_core_memory(req.session_id, {
                "opponent_profile": profile_snapshot,
                "trauma_codes": f"Maske Makası: %{metrics.get('persona_authenticity_gap')}"
            })
            append_message(req.session_id, "system", f"[GÖRSEL KARAKTER OTOPSİSİ TAMAMLANDI]: {summary}", round_num=1)
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Davranış ve Karakter Analiz Motoru Hatası: {str(e)}")

@app.post("/api/dispatcher-route")
async def route_task_endpoint(query: Optional[str] = "", images_count: int = 0, requested_role: Optional[str] = None):
    decision = TaskDispatcher.resolve_route(
        query=query or "",
        images=["img"] * images_count if images_count > 0 else [],
        requested_role=requested_role
    )
    return decision

@app.post("/api/inversion-analyze", response_model=InversionOutput)
async def analyze_decision(req: AnalyzeRequest):
    try:
        user_input = req.decision or req.decision_text or req.query
        active_role = req.role or (req.forensic_context.get("target_role") if req.forensic_context else None)
        
        # Görev ve Niyet Yönlendirme Analizi (TaskDispatcher)
        detected_images = []
        if req.forensic_context and isinstance(req.forensic_context, dict):
            if req.forensic_context.get("image_base64"):
                detected_images.append(req.forensic_context.get("image_base64"))
            if req.forensic_context.get("formal_image"):
                detected_images.append(req.forensic_context.get("formal_image"))
            if req.forensic_context.get("candid_image"):
                detected_images.append(req.forensic_context.get("candid_image"))
            if req.forensic_context.get("social_image"):
                detected_images.append(req.forensic_context.get("social_image"))
        
        dispatch = TaskDispatcher.resolve_route(
            query=user_input,
            images=detected_images,
            requested_role=active_role
        )

        # Dispatcher kararı forensic_context içine enjekte edilerek LLM'in doğru motora odaklanması sağlanır
        active_context = dict(req.forensic_context or {})
        active_context["dispatcher_route"] = dispatch.selected_route.value
        active_context["dispatcher_reasoning"] = dispatch.reasoning
        active_context["dispatcher_target_role"] = dispatch.target_role
        active_context["target_role"] = active_role or dispatch.target_role

        # FINANCIAL_PHYSICS seçildiyse: Apple Silicon ARM64 Rust Kernel ve Python Physics Suite çalıştır
        if dispatch.selected_route == EngineRoute.FINANCIAL_PHYSICS:
            # 1. Python Physics Suite (Dinamik Regex & Sistem Dinamikleri)
            try:
                from engine.inversion_physics_suite import InversionPhysicsSuite
                phys_suite = InversionPhysicsSuite()
                active_context["physics_telemetry"] = phys_suite.run_full_inversion_audit(user_input)
            except Exception as p_err:
                print(f"[PHYSICS SUITE HATA]: {p_err}")

            # 2. Rust Native Kernel (Apple Silicon ARM64 Ultra Hızlı Simülasyon)
            rust_bin = os.path.join(os.path.dirname(__file__), "engine", "rust_binary", "target", "release", "inversion_rust_engine")
            if os.path.exists(rust_bin):
                try:
                    import subprocess
                    import re
                    # Kullanıcı metninden tahmini sermaye ve gider ayıklama
                    cash_m = re.search(r'([0-9]+(?:\.[0-9]+)*)\s*(?:tl|\$|usd|euro|nakit|sermaye)', user_input, re.IGNORECASE)
                    burn_m = re.search(r'([0-9]+(?:\.[0-9]+)*)\s*(?:tl|\$|usd|euro)?\s*(?:kira|gider|masraf|maliyet)', user_input, re.IGNORECASE)
                    c_val = float(cash_m.group(1).replace('.', '')) if cash_m else 50000.0
                    b_val = float(burn_m.group(1).replace('.', '')) if burn_m else 5000.0
                    
                    rust_payload = json.dumps({
                        "capital": c_val,
                        "burn": b_val,
                        "debt": 25.0,
                        "delay": 2
                    })
                    proc = subprocess.run([rust_bin, rust_payload], capture_output=True, text=True, timeout=2)
                    if proc.returncode == 0 and proc.stdout:
                        active_context["rust_telemetry"] = json.loads(proc.stdout.strip())
                except Exception as r_err:
                    print(f"[RUST KERNEL HATA]: {r_err}")

        # MLX çıkarımı FastAPI event-loop'unu dondurmasın diye threadpool'a devredilir
        result = await asyncio.to_thread(
            InversionCoreEngine.process_turn,
            session_id=req.session_id,
            user_query=user_input,
            round_num=req.round,
            decision=req.decision,
            forensic_context=active_context
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
    # Başlangıçta MLX Modelini RAM'e yükle (Warmup - İlk istek gecikmesini sıfırlar)
    try:
        from inversion_engine import get_engine_components
        print("[*] Model RAM'e yükleniyor (Warmup)...")
        get_engine_components()
    except Exception as _werr:
        print(f"[!] Warmup atlandı: {_werr}")

    print(f"InversionCore Enterprise Engine Başlatılıyor: http://0.0.0.0:{PORT}")
    uvicorn.run("server:app", host="0.0.0.0", port=PORT, reload=False)
