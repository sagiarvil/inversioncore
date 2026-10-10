# -*- coding: utf-8 -*-
"""
InversionCore NATO/Industrial Grade LangGraph Master Orchestrator
End-to-End Cyclical Adversarial State Machine:
Discovery -> Cognitive Bias -> Critic Inversion -> Deterministic Prover (Z3/Rust) -> Synthesis -> Forensic PDF.
"""

import os
import json
import time
from typing import TypedDict, Dict, Any, List, Optional
from langgraph.graph import StateGraph, END

from src.inversion_kernel.kvkk_guard import KVKKGuard
from src.inversion_kernel.cognitive_forensics import CognitiveForensicsKernel
from src.inversion_kernel.deterministic_prover import DeterministicProverKernel
from src.inversion_kernel.forensic_pdf_engine import ForensicPDFEngine


class DiagnosticState(TypedDict):
    raw_input: str
    masked_input: str
    pii_mapping: Dict[str, str]
    is_injection: bool
    injection_error: str
    discovery_data: Dict[str, Any]
    cognitive_audit: Dict[str, Any]
    critic_output: str
    deterministic_result: str
    rust_telemetry: Dict[str, Any]
    z3_telemetry: Dict[str, Any]
    ortools_telemetry: Dict[str, Any]
    via_negativa: List[str]
    final_verdict: str
    audit_hash: str
    pdf_path: str


# 1. DÜĞÜM: KVKK SANITIZE
def node_kvkk_sanitize(state: DiagnosticState) -> Dict[str, Any]:
    guard = KVKKGuard()
    raw = state.get("raw_input", "")
    is_inj, inj_err = guard.check_injection(raw)
    if is_inj:
        return {
            "is_injection": True,
            "injection_error": inj_err,
            "final_verdict": "RED",
            "deterministic_result": "INJECTION_BLOCKED"
        }
    masked, mapping = guard.mask_pii(raw)
    return {
        "masked_input": masked,
        "pii_mapping": mapping,
        "is_injection": False,
        "injection_error": ""
    }


# 2. DÜĞÜM: DISCOVERY (Yapılandırılmış Parametre Ayrıştırma)
def node_discovery(state: DiagnosticState) -> Dict[str, Any]:
    if state.get("is_injection"):
        return {"discovery_data": {}}

    text = state.get("masked_input", "")
    import re

    capital = 500000.0
    burn = 45000.0
    debt = 25.0
    delay = 1

    # Sıfır sermaye tespiti
    if re.search(r'(sıfır\s+para|paramız\s+yok|sermaye\s+yok|meteliksiz|nakit\s+yok|nakit\s+sıfır)', text, re.IGNORECASE):
        capital = 0.0

    # Borç tespiti
    if re.search(r'(borcumuz\s+yok|sıfır\s+borç|borç\s+yok)', text, re.IGNORECASE):
        debt = 0.0
    elif re.search(r'(\d+([.,]\d+)?)\s*(milyon|bin|tl|₺)?\s*(borç|kredi)', text, re.IGNORECASE):
        debt = 85.0 # Kritik borçluluk oranı

    # Sermaye / Nakit tutarı yakalama (Örn: 3 milyon TL nakit / 500 bin TL sermaye)
    cap_match = re.search(r'(\d+([.,]\d+)?)\s*(milyon|bin)?\s*(tl|₺)?\s*(nakit|sermaye|bütçe|para|kasa)', text, re.IGNORECASE)
    if cap_match:
        val = float(cap_match.group(1).replace(',', '.'))
        unit = (cap_match.group(3) or '').lower()
        if 'milyon' in unit or 'm' in unit:
            capital = val * 1_000_000
        elif 'bin' in unit or 'k' in unit:
            capital = val * 1_000
        else:
            capital = val

    # Aylık harcama tespiti
    burn_match = re.search(r'aylık\s*(\d+([.,]\d+)?)\s*(milyon|bin|tl|₺|k)', text, re.IGNORECASE)
    if burn_match:
        val = float(burn_match.group(1).replace(',', '.'))
        unit = burn_match.group(3).lower()
        if 'milyon' in unit or 'm' in unit:
            burn = val * 1_000_000
        elif 'bin' in unit or 'k' in unit:
            burn = val * 1_000

    disc = {
        "hedef": "İşletme Büyümesi ve Sermaye Tahsisi Kararı",
        "eylem": text[:180] if len(text) > 180 else text,
        "capital": capital,
        "burn": burn,
        "debt_ratio": debt,
        "delay_factor": delay
    }
    return {"discovery_data": disc}


# 3. DÜĞÜM: COGNITIVE BIAS AUDIT (CoPoLLM + Rasch IRT)
def node_cognitive_audit(state: DiagnosticState) -> Dict[str, Any]:
    if state.get("is_injection"):
        return {"cognitive_audit": {}}

    forensics = CognitiveForensicsKernel()
    text = state.get("masked_input", "")
    audit = forensics.audit_text(text)
    return {"cognitive_audit": audit}


# 4. DÜĞÜM: CRITIC INVERSION (Pre-Mortem Çöküş Analizi & Qwen 14B Yerel Model)
def node_critic(state: DiagnosticState) -> Dict[str, Any]:
    cog = state.get("cognitive_audit", {})
    disc = state.get("discovery_data", {})
    masked_text = state.get("masked_input", "")
    findings = cog.get("tespit_edilen_carpitmalar", [])

    critic_points = []
    if cog.get("self_deception_index", 0) > 0.5:
        critic_points.append("Bilişsel savunma mekanizması gerçek piyasa kısıtlarını maskeliyor.")
    if disc.get("debt_ratio", 0) > 30:
        critic_points.append("Yüksek borç yükü beklenmeyen faiz şoklarında likiditeyi 60 gün içinde tüketir.")
    if not critic_points:
        critic_points.append("İyimserlik önyargısı nedeniyle alternatif başarısızlık senaryoları modellenmemiş.")

    # Çok Kademeli Dayanıklı LLM Ağ Geçidi (Yerel MLX -> Llama Metal -> NVIDIA NIM 26B -> Deterministik)
    try:
        from src.inversion_kernel.resilient_llm_gateway import ResilientLLMGateway
        gw = ResilientLLMGateway()
        bias_str = f"SDI: {cog.get('self_deception_index')}, Çarpıtmalar: {[f.get('carpitma_adi') for f in findings]}"
        fin_str = f"Sermaye: {disc.get('capital')} TL, Harcama: {disc.get('burn')} TL, Borç Oranı: %{disc.get('debt_ratio')}"
        critique_res = gw.generate_resilient_inversion(masked_text, bias_str, fin_str)
        llm_verdict = critique_res.get("verdict", "")
        if llm_verdict and len(llm_verdict.strip()) > 20:
            engine_tag = critique_res.get("engine", "LLM")
            critic_points.insert(0, f"[{engine_tag}]: {llm_verdict}")
    except Exception:
        pass

    via_negativa = [
        "Nakit akışı pozitifleşene kadar yeni sabit gider oluşturacak tüm alımları durdurun.",
        "Geri dönülmez hukuki taahhüt ve kefalet imzalarını askıya alın.",
        "Gereksiz danışmanlık ve pazarlama harcamalarını %40 oranında kesin."
    ]

    return {
        "critic_output": " | ".join(critic_points),
        "via_negativa": via_negativa
    }


# 5. DÜĞÜM: DETERMINISTIC PROVER (Z3 SMT + OR-Tools + Rust)
def node_deterministic(state: DiagnosticState) -> Dict[str, Any]:
    if state.get("is_injection"):
        return {"deterministic_result": "BLOCKED"}

    prover = DeterministicProverKernel()
    disc = state.get("discovery_data", {})

    cap = disc.get("capital", 500000.0)
    burn = disc.get("burn", 45000.0)
    debt = disc.get("debt_ratio", 25.0)
    delay = disc.get("delay_factor", 1)

    # 1. Rust Binary
    rust_res = prover.run_rust_engine(cap, burn, debt, delay)

    # 2. Z3 SMT
    z3_res = prover.solve_z3_stress_test(cap, burn, fixed_debt=cap * (debt / 100.0), stress_drop_pct=25.0)

    # 3. OR-Tools
    ortools_res = prover.solve_ortools_runway(int(cap), int(burn), min_required_months=6)

    # Sonuç Konsensüsü
    if z3_res.get("verdict") == "UNSAT" or rust_res.get("fragility_status", "").startswith("KIRILGAN"):
        final_det = "UNSAT"
        verdict = "RED"
    elif not ortools_res.get("asgari_sart_saglandi", True):
        final_det = "CONDITIONAL"
        verdict = "DOĞRULAMA GEREKLİ"
    else:
        final_det = "SAT"
        verdict = "GO"

    return {
        "deterministic_result": final_det,
        "rust_telemetry": rust_res,
        "z3_telemetry": z3_res,
        "ortools_telemetry": ortools_res,
        "final_verdict": verdict
    }


# 6. DÜĞÜM: SYNTHESIS & FORENSIC PDF GENERATION
def node_synthesis(state: DiagnosticState) -> Dict[str, Any]:
    guard = KVKKGuard()
    pdf_engine = ForensicPDFEngine()

    disc = state.get("discovery_data", {})
    cog = state.get("cognitive_audit", {})
    rust_t = state.get("rust_telemetry", {})
    z3_t = state.get("z3_telemetry", {})
    ortools_t = state.get("ortools_telemetry", {})

    audit_payload = {
        "discovery": disc,
        "verdict": state.get("final_verdict", "DOĞRULAMA GEREKLİ"),
        "z3": z3_t.get("verdict"),
        "sdi": cog.get("self_deception_index")
    }
    audit_hash = guard.generate_audit_hash(audit_payload)

    reports_dir = "/Users/macair1/projects/inversioncore/data/reports"
    os.makedirs(reports_dir, exist_ok=True)
    pdf_filename = f"Forensic_Report_{int(time.time())}.pdf"
    pdf_full_path = os.path.join(reports_dir, pdf_filename)

    report_payload = {
        "karar": state.get("final_verdict", "DOĞRULAMA GEREKLİ"),
        "hedef": disc.get("hedef", "Yatırım / Sermaye Kararı"),
        "eylem": disc.get("eylem", "İş Planı"),
        "capital": disc.get("capital", 0),
        "burn": disc.get("burn", 0),
        "debt_ratio": disc.get("debt_ratio", 0),
        "delay_factor": disc.get("delay_factor", 0),
        "cognitive_audit": cog,
        "rust_telemetry": rust_t,
        "z3_telemetry": z3_t,
        "ortools_telemetry": ortools_t,
        "via_negativa": state.get("via_negativa", []),
        "audit_hash": audit_hash
    }

    pdf_engine.generate_report(report_payload, pdf_full_path)

    return {
        "audit_hash": audit_hash,
        "pdf_path": pdf_full_path
    }


# MİMARİ LANGGRAPH STATEGRAPH KURULUMU
def build_inversion_graph():
    workflow = StateGraph(DiagnosticState)

    workflow.add_node("kvkk_sanitize", node_kvkk_sanitize)
    workflow.add_node("discovery", node_discovery)
    workflow.add_node("cognitive_bias", node_cognitive_audit)
    workflow.add_node("critic", node_critic)
    workflow.add_node("deterministic", node_deterministic)
    workflow.add_node("synthesis", node_synthesis)

    workflow.set_entry_point("kvkk_sanitize")

    # Akış
    workflow.add_edge("kvkk_sanitize", "discovery")
    workflow.add_edge("discovery", "cognitive_bias")
    workflow.add_edge("cognitive_bias", "critic")
    workflow.add_edge("critic", "deterministic")
    workflow.add_edge("deterministic", "synthesis")
    workflow.add_edge("synthesis", END)

    return workflow.compile()


if __name__ == "__main__":
    print("LangGraph Inversion Core Workflow Derleniyor...")
    app = build_inversion_graph()
    sample_input = """
    Bizim şirket için kesinlikle tek yol 3 milyon TL kredi çekip yeni fabrika açmak.
    Başka hiçbir çaremiz yok, herkes böyle yapıyor. Eğer bunu yapmazsak mahvolduk, bittik.
    Bize komplo kurdular ama ben hissediyorum bu sefer kesinlikle zengin olacağız.
    """
    initial_state: DiagnosticState = {
        "raw_input": sample_input,
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
    res = app.invoke(initial_state)
    print("\n=== LANGGRAPH TESTİ BAŞARILI ===")
    print("Karar:", res.get("final_verdict"))
    print("Bilişsel Çarpıtma Endeksi (SDI):", res.get("cognitive_audit", {}).get("self_deception_index"))
    print("Z3 Kararı:", res.get("z3_telemetry", {}).get("verdict"))
    print("Rust Gecikmesi:", res.get("rust_telemetry", {}).get("computation_time_us"), "µs")
    print("Oluşturulan Adli PDF:", res.get("pdf_path"))
