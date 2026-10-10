# -*- coding: utf-8 -*-
"""
InversionCore Resilient Multi-Tier LLM Gateway
Kademeli, Kendi Kendini İyileştiren ve Tıkanma Önleyici LLM Yönlendiricisi.

Hiyerarşi Sıralaması:
1. SEVİYE: Apple MLX-LM Native (Port 8084 - Qwen 14B Coder) -> Sıfır Maliyet, Yerel Metal
2. SEVİYE: Metal Llama-Server (Port 8081 - Qwen 14B Coder) -> Yerel Yedek
3. SEVİYE: NVIDIA NIM Cloud (DiffusionGemma 26B) -> Bulut Yedek (0 Token Maliyeti)
4. SEVİYE: NVIDIA NIM Cloud (Llama 3.2 11B Vision) -> Alternatif Bulut
5. SEVİYE: Deterministik Kural Motoru (Fail-Safe) -> Asla Çökmez
"""

import os
import json
import urllib.request
import urllib.error
import time
from typing import Dict, Any, List, Optional


class ResilientLLMGateway:
    """Tıkanma Önleyici ve Otomatik Yük Devretmeli (Failover) LLM Ağ Geçidi."""

    def __init__(self):
        self.nv_api_key = os.environ.get("NVIDIA_API_KEY")
        if not self.nv_api_key and os.path.exists("/Users/macair1/projects/inversioncore/.env"):
            try:
                with open("/Users/macair1/projects/inversioncore/.env", "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("NVIDIA_API_KEY="):
                            self.nv_api_key = line.strip().split("=", 1)[1]
                            break
            except Exception:
                pass

    def call_local_endpoint(self, url: str, payload: Dict[str, Any], timeout: float = 8.0) -> Optional[str]:
        """Yerel portlara (8084 / 8081) çıkarım isteği atar."""
        try:
            req = urllib.request.Request(
                f"{url}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload).encode("utf-8")
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception:
            return None

    def call_nvidia_nim(self, model: str, messages: List[Dict[str, str]], timeout: float = 8.0) -> Optional[str]:
        """NVIDIA NIM API üzerinden model çağrısı yapar."""
        if not self.nv_api_key:
            return None

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 400
        }

        try:
            req = urllib.request.Request(
                "https://integrate.api.nvidia.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.nv_api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                data=json.dumps(payload).encode("utf-8")
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception:
            return None

    def generate_resilient_inversion(
        self,
        text: str,
        bias_summary: str,
        numbers_summary: str
    ) -> Dict[str, Any]:
        """
        Tıkanma anında sıradaki motora anında atlayan (Cascading Failover) Pre-Mortem üreticisi.
        """
        sys_prompt = (
            "Sen InversionCore Savunma Sanayii / B2B Karar Hakikat Masası Kıdemli Adli Denetçisisin. "
            "Görevin: Girişimcinin veya yöneticinin sunduğu iş fikrini ve yatırım planını acımasızca, "
            "Pre-Mortem (Ön-Otopsi) ilkeleriyle çürütmek, gizli iflas risklerini ve kör noktaları deşifre etmektir. "
            "Pazarlama süslemesi yapma. 3 maddelik cerrahi ve somut Türk Ticaret Kanunu / piyasa gerçekleri "
            "ile 'Neden batacak?' analizi yap."
        )
        user_prompt = (
            f"ANALİZ EDİLECEK YATIRIM / KARAR:\n{text}\n\n"
            f"BİLİŞSEL KÖRLÜK BULGULARI:\n{bias_summary}\n\n"
            f"FİNANSAL PARAMETRELER:\n{numbers_summary}\n\n"
            f"Lütfen 3 maddelik sert Pre-Mortem Inversion tespitini Türkçe yaz:"
        )

        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ]
        payload = {"messages": messages, "temperature": 0.1, "max_tokens": 350}

        # 1. KADEME: Apple MLX-LM Native (Port 8084)
        t0 = time.perf_counter()
        res = self.call_local_endpoint("http://127.0.0.1:8084", payload, timeout=5.0)
        if res and len(res.strip()) > 15:
            return {
                "verdict": res.strip(),
                "engine": "TIER-1: APPLE_MLX_LM_PORT_8084 (Qwen 14B Coder)",
                "latency_ms": int((time.perf_counter() - t0) * 1000),
                "failover_occurred": False
            }

        # 2. KADEME: Metal Llama-Server (Port 8081)
        t1 = time.perf_counter()
        res = self.call_local_endpoint("http://127.0.0.1:8081", payload, timeout=6.0)
        if res and len(res.strip()) > 15:
            return {
                "verdict": res.strip(),
                "engine": "TIER-2: METAL_LLAMA_SERVER_PORT_8081 (Qwen 14B Coder)",
                "latency_ms": int((time.perf_counter() - t1) * 1000),
                "failover_occurred": True
            }

        # 3. KADEME: NVIDIA NIM Cloud (DiffusionGemma 26B)
        t2 = time.perf_counter()
        res = self.call_nvidia_nim("google/diffusiongemma-26b-a4b-it", messages, timeout=7.0)
        if res and len(res.strip()) > 15:
            return {
                "verdict": f"[NVIDIA-NIM 26B]: {res.strip()}",
                "engine": "TIER-3: NVIDIA_NIM_DIFFUSION_GEMMA_26B",
                "latency_ms": int((time.perf_counter() - t2) * 1000),
                "failover_occurred": True
            }

        # 4. KADEME: NVIDIA NIM Cloud (Llama 3.2 11B Vision)
        t3 = time.perf_counter()
        res = self.call_nvidia_nim("meta/llama-3.2-11b-vision-instruct", messages, timeout=7.0)
        if res and len(res.strip()) > 15:
            return {
                "verdict": f"[NVIDIA-NIM 11B]: {res.strip()}",
                "engine": "TIER-4: NVIDIA_NIM_LLAMA_3.2_11B",
                "latency_ms": int((time.perf_counter() - t3) * 1000),
                "failover_occurred": True
            }

        # 5. KADEME: Deterministik Fail-Safe Kural Motoru
        return {
            "verdict": "Bilişsel savunma mekanizması ve aşırı iyimserlik nakit akışındaki 60 günlük iflas riskini gizliyor.",
            "engine": "TIER-5: DETERMINISTIC_RULE_FALLBACK",
            "latency_ms": 1,
            "failover_occurred": True
        }
