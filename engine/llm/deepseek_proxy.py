"""
LiteLLM Proxy Wrapper - DeepSeek cagrilari icin:
- Timeout (30s default)
- Exponential backoff retry (3 deneme)
- Token + cost tracking
- Sadece ceviri icin kullanilir, HESAPLAMA YOK
"""
import time
from typing import Optional
import litellm
from config import settings
from config.secrets import DEEPSEEK_API_KEY, DEEPSEEK_ENDPOINT, DEEPSEEK_MODEL
from engine.cache.cost_ledger import get_ledger


# LiteLLM config
litellm.num_retries = settings.LITELLM_MAX_RETRIES
litellm.request_timeout = settings.LITELLM_TIMEOUT


class DeepSeekProxy:
    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.model = DEEPSEEK_MODEL
        self.api_base = DEEPSEEK_ENDPOINT
    
    def synthesize(self, physical_findings: list, customer_id: str = "default",
                   problem_type: str = "unknown") -> dict:
        """
        Fiziksel motor ciktisini insan diline cevirir.
        ASLA hesaplamaz, ASLA yeni bilgi uremez.
        """
        start = time.time()
        
        if not self.api_key:
            return {
                "error": "DEEPSEEK_API_KEY ayarlanmamis",
                "fallback_synthesis": self._offline_fallback(physical_findings)
            }
        
        system_prompt = (
            "Sen InversionCore fiziksel motorlarinin ciktisini insan diline ceviren bir sentez motorusun. "
            "KURALLAR:\n"
            "1. ASLA yeni bilgi ekleme, ASLA hesaplama yapma\n"
            "2. Sadece verilen fiziksel bulgulari ozetle\n"
            "3. Her bulgunun 'negatif bilgi' oldugunu vurgula\n"
            "4. Turkce cevap ver\n"
            "5. Kisa ve net ol (maksimum 200 kelime)"
        )
        
        user_prompt = (
            "Asagidaki fiziksel motor bulgularini sentezle:\n\n" +
            "\n".join(f"- {f.get('motor', '?')}: {f.get('negative_finding', '?')}" 
                      for f in physical_findings)
        )
        
        try:
            response = litellm.completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                api_key=self.api_key,
                api_base=self.api_base,
                temperature=0.0,  # Deterministik cikti icin
                max_tokens=400
            )
            
            latency_ms = (time.time() - start) * 1000
            usage = response.usage
            cost = response._hidden_params.get("response_cost", 0.0) or 0.0
            
            get_ledger().record(
                customer_id=customer_id,
                problem_type=problem_type,
                model=self.model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                cost_usd=cost,
                cache_status="MISS",
                latency_ms=latency_ms
            )
            
            return {
                "synthesis": response.choices[0].message.content,
                "tokens": usage.total_tokens,
                "cost_usd": round(cost, 6),
                "latency_ms": round(latency_ms, 2),
                "source": "deepseek"
            }
        
        except Exception as e:
            get_ledger().record(
                customer_id=customer_id, problem_type=problem_type,
                model=self.model, prompt_tokens=0, completion_tokens=0,
                cost_usd=0.0, cache_status="ERROR",
                latency_ms=(time.time() - start) * 1000
            )
            return {
                "error": str(e),
                "fallback_synthesis": self._offline_fallback(physical_findings)
            }
    
    def _offline_fallback(self, findings: list) -> str:
        """API yoksa offline sentez (token maliyeti: 0)"""
        lines = ["[OFFLINE SENTEZ - DeepSeek API yok]"]
        for f in findings:
            lines.append(f"- {f.get('motor', '?')}: {f.get('negative_finding', '?')}")
        return "\n".join(lines)
