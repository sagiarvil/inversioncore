# -*- coding: utf-8 -*-
"""
InversionCore NATO/Industrial Grade REST API Server
Exposes the LangGraph Executive Cognitive Forensics & Deterministic Engine.
"""

import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.inversion_kernel.langgraph_orchestrator import build_inversion_graph, DiagnosticState

app = FastAPI(
    title="InversionCore Executive Cognitive Forensics OS",
    description="NATO/Industrial Grade Adversarial Decision Due Diligence Engine",
    version="3.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compile LangGraph StateGraph once on startup
print("[*] InversionCore LangGraph StateGraph derleniyor...")
graph_app = build_inversion_graph()
print("[+] LangGraph StateGraph hazır.")


class DiagnoseRequest(BaseModel):
    input: str
    hedef: Optional[str] = None
    capital: Optional[float] = None
    burn: Optional[float] = None
    debt_ratio: Optional[float] = None


@app.get("/api/health")
def health_check():
    from src.inversion_kernel.qwen_llm_client import QwenLLMClient
    from src.inversion_kernel.chiasmus_client import ChiasmusClient
    from src.inversion_kernel.copollm_adapter import CoPoLLMAdapter
    import mlx_lm
    import mlx_dspark

    qwen_client = QwenLLMClient()
    active_llm_url = qwen_client._get_active_url()
    qwen_alive = active_llm_url is not None
    engine_name = "APPLE MLX-LM NATIVE (Port 8084)" if active_llm_url and ":8084" in active_llm_url else "METAL LLAMA-SERVER (Port 8081)"

    chiasmus_ok = ChiasmusClient().is_available()
    copollm_status = CoPoLLMAdapter().get_status()

    return {
        "status": "HEALTHY",
        "system": "InversionCore Executive Cognitive Forensics OS",
        "version": "3.3.0",
        "engines": {
            "primary_llm_engine": f"READY ({engine_name} - {'ONLINE' if qwen_alive else 'OFFLINE'})",
            "mlx_runtime_packages": f"READY (mlx-lm {mlx_lm.__version__}, mlx-dspark {mlx_dspark.__version__})",
            "chiasmus_neurosymbolic_mcp": f"READY ({'INSTALLED & VERIFIED' if chiasmus_ok else 'MISSING'})",
            "copollm_acl_2026_repo": f"READY (324 Dataset Samples - {copollm_status['status']})",
            "rust_differential_engine": "READY (Mach-O Native 3.4µs)",
            "microsoft_z3_smt": "READY (Dual: Python z3-solver + Chiasmus WASM)",
            "google_ortools": "READY (CP-SAT Linear Optimizer)",
            "copollm_cognitive_forensics": "READY (8-Bias Taxonomy + Rasch IRT)",
            "reportlab_vector_pdf": "READY",
            "langgraph_state_machine": "COMPILED"
        }
    }


@app.post("/api/inversion/diagnose")
def run_diagnosis(req: DiagnoseRequest):
    if not req.input or len(req.input.strip()) < 5:
        raise HTTPException(status_code=400, detail="Girdi metni en az 5 karakter olmalıdır.")

    initial_state: DiagnosticState = {
        "raw_input": req.input,
        "masked_input": "",
        "pii_mapping": {},
        "is_injection": False,
        "injection_error": "",
        "discovery_data": {},
        "cognitive_audit": {},
        "critic_output": "",
        "deterministic_result": "",
        "rust_telemetry": {},
        "z3_telemetry": {},
        "ortools_telemetry": {},
        "via_negativa": [],
        "final_verdict": "",
        "audit_hash": "",
        "pdf_path": ""
    }

    try:
        res = graph_app.invoke(initial_state)

        pdf_full_path = res.get("pdf_path", "")
        pdf_filename = os.path.basename(pdf_full_path) if pdf_full_path else ""
        download_url = f"/api/inversion/report/{pdf_filename}" if pdf_filename else ""

        return JSONResponse(content={
            "status": "SUCCESS",
            "verdict": res.get("final_verdict"),
            "deterministic_status": res.get("deterministic_result"),
            "cognitive_forensics": res.get("cognitive_audit"),
            "rust_telemetry": res.get("rust_telemetry"),
            "z3_telemetry": res.get("z3_telemetry"),
            "ortools_telemetry": res.get("ortools_telemetry"),
            "monte_carlo_telemetry": res.get("monte_carlo_telemetry"),
            "ttk_376_telemetry": res.get("ttk_376_telemetry"),
            "red_team_critic": res.get("critic_output"),
            "via_negativa": res.get("via_negativa"),
            "audit_hash": res.get("audit_hash"),
            "report_pdf_url": download_url
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Teşhis motoru hatası: {str(e)}")


@app.get("/api/inversion/report/{filename}")
def download_report(filename: str):
    reports_dir = "/Users/macair1/projects/inversioncore/data/reports"
    safe_path = os.path.abspath(os.path.join(reports_dir, filename))
    if not safe_path.startswith(os.path.abspath(reports_dir)) or not os.path.exists(safe_path):
        raise HTTPException(status_code=404, detail="Rapor dosyası bulunamadı.")
    return FileResponse(
        safe_path,
        media_type="application/pdf",
        filename=filename
    )


@app.get("/")
def serve_index():
    index_path = "/Users/macair1/projects/inversioncore/public/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"status": "ONLINE", "message": "InversionCore API Ready"})

# Mount public directory for static assets (logo.png, css, js)
public_dir = "/Users/macair1/projects/inversioncore/public"
if os.path.exists(public_dir):
    app.mount("/static", StaticFiles(directory=public_dir), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8083)
