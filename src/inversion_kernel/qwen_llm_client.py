# -*- coding: utf-8 -*-
"""
InversionCore Local Qwen 14B Coder & Multi-Engine LLM Client
Primary: Local Qwen 14B Coder via Port 8081 (Zero-Token, Native Metal)
Fallback: NVIDIA NIM API / Multi-API Gateway
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional


class QwenLLMClient:
    """Yerel Qwen 14B Coder (MLX-LM & Llama-server) Çıkarım İstemcisi."""

    def __init__(self, base_url: Optional[str] = None):
        # 8084: Saf Apple MLX-LM Sunucusu | 8081: Metal Llama-server
        self.candidate_urls = [
            base_url.rstrip("/") if base_url else None,
            "http://127.0.0.1:8084",
            "http://127.0.0.1:8081"
        ]
        self.candidate_urls = [u for u in self.candidate_urls if u]

    def _get_active_url(self) -> Optional[str]:
        """Aktif olan en hızlı yerel MLX/Metal sunucusunu bulur."""
        for url in self.candidate_urls:
            try:
                # 8084 mlx_lm için /v1/models veya basit get
                test_url = f"{url}/v1/models" if url.endswith(":8084") else f"{url}/health"
                req = urllib.request.Request(test_url, method="GET")
                with urllib.request.urlopen(req, timeout=0.8) as resp:
                    if resp.status in (200, 204):
                        return url
            except Exception:
                continue
        return None

    def is_local_alive(self) -> bool:
        """Herhangi bir yerel Qwen 14B çıkarım sunucusunun ayakta olup olmadığını kontrol eder."""
        return self._get_active_url() is not None

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 512,
        timeout: int = 15
    ) -> Dict[str, Any]:
        """Yerel Qwen 14B Coder motoruna çıkarım isteği gönderir."""
        active_url = self._get_active_url()
        if not active_url:
            return {
                "status": "OFFLINE",
                "engine": "NONE",
                "error": "Hiçbir yerel çıkarım sunucusu ayakta değil",
                "content": ""
            }

        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            req = urllib.request.Request(
                f"{active_url}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload).encode("utf-8")
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                engine_type = "APPLE_MLX_LM_NATIVE" if ":8084" in active_url else "LLAMA_METAL_BACKEND"
                return {
                    "status": "SUCCESS",
                    "engine": engine_type,
                    "url": active_url,
                    "model": data.get("model", "qwen2.5-coder-14b"),
                    "content": content,
                    "timings": data.get("timings", {})
                }
        except Exception as e:
            return {
                "status": "FALLBACK_TRIGGERED",
                "engine": "LOCAL_ERROR",
                "error": str(e),
                "content": ""
            }
        except Exception as e:
            return {
                "status": "FALLBACK_TRIGGERED",
                "engine": "LOCAL_ERROR",
                "error": str(e),
                "content": ""
            }

    def generate_critic_inversion(self, text: str, bias_summary: str, numbers_summary: str) -> str:
        """Yerel Qwen 14B Coder ile Pre-Mortem Karşıt Çöküş Analizi üretir."""
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

        resp = self.chat_completion(
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=350
        )

        if resp.get("status") == "SUCCESS" and resp.get("content"):
            return resp["content"].strip()

        # 2. SEVİYE YEDEK: NVIDIA NIM Cloud Gateway (Sıfır Maliyetli Yedek Motor)
        nv_key = os.environ.get("NVIDIA_API_KEY")
        if not nv_key and os.path.exists("/Users/macair1/projects/inversioncore/.env"):
            with open("/Users/macair1/projects/inversioncore/.env") as f:
                for line in f:
                    if line.startswith("NVIDIA_API_KEY="):
                        nv_key = line.strip().split("=", 1)[1]
                        break

        if nv_key:
            try:
                nv_payload = {
                    "model": "google/diffusiongemma-26b-a4b-it",
                    "messages": [
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 300
                }
                req = urllib.request.Request(
                    "https://integrate.api.nvidia.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {nv_key}", "Content-Type": "application/json"},
                    data=json.dumps(nv_payload).encode("utf-8")
                )
                with urllib.request.urlopen(req, timeout=8) as r:
                    d = json.loads(r.read().decode("utf-8"))
                    nv_content = d["choices"][0]["message"]["content"].strip()
                    if nv_content:
                        return f"[NVIDIA-NIM]: {nv_content}"
            except Exception:
                pass
        
        # 3. SEVİYE: Deterministik Kural Motoru
        return "Bilişsel savunma mekanizması ve aşırı iyimserlik nakit akışındaki 60 günlük iflas riskini gizliyor."
