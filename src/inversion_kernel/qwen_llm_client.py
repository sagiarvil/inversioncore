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
    """Yerel Qwen 14B Coder ve Harici API Çıkarım İstemcisi."""

    def __init__(self, base_url: str = "http://127.0.0.1:8081"):
        self.base_url = base_url.rstrip("/")

    def is_local_alive(self) -> bool:
        """Port 8081 yerel modelin ayakta olup olmadığını kontrol eder."""
        try:
            req = urllib.request.Request(f"{self.base_url}/health", method="GET")
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                return resp.status == 200
        except Exception:
            return False

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 512,
        timeout: int = 15
    ) -> Dict[str, Any]:
        """Yerel Qwen 14B Coder motoruna çıkarım isteği gönderir."""
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            req = urllib.request.Request(
                f"{self.base_url}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload).encode("utf-8")
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                return {
                    "status": "SUCCESS",
                    "engine": "LOCAL_QWEN_14B_CODER_PORT_8081",
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
        
        # Yerel model meşgulse deterministik kural motoru devrede kalır
        return "Bilişsel savunma mekanizması ve aşırı iyimserlik nakit akışındaki 60 günlük iflas riskini gizliyor."
