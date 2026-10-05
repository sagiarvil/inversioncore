"""
Deterministic Cache Layer
- Valkey (Redis fork) varsa onu kullanir (production)
- Yoksa cachetools TTLCache ile memory fallback (development)
- Her cache entry: (customer_id, problem_type, data_hash, motor_version, ontology_version)
"""
import hashlib
import json
import os
from functools import wraps
from typing import Any, Optional

try:
    import valkey
    VALKEY_AVAILABLE = True
except ImportError:
    VALKEY_AVAILABLE = False

from cachetools import TTLCache
import config.settings as settings


class DeterministicCache:
    def __init__(self, url: Optional[str] = None, ttl: int = 86400):
        self.ttl = ttl
        self.backend = None
        self.backend_type = "memory"
        
        if VALKEY_AVAILABLE:
            try:
                self.backend = valkey.from_url(url or settings.VALKEY_URL, decode_responses=True)
                self.backend.ping()
                self.backend_type = "valkey"
            except Exception:
                self.backend = TTLCache(maxsize=10000, ttl=ttl)
                self.backend_type = "memory"
        else:
            self.backend = TTLCache(maxsize=10000, ttl=ttl)
            self.backend_type = "memory"
    
    @staticmethod
    def make_key(prefix: str, data: Any) -> str:
        """Deterministik hash: sort_keys + sha256 + prefix"""
        serialized = json.dumps(data, sort_keys=True, default=str, ensure_ascii=False)
        digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:24]
        return f"ic:{prefix}:{settings.MOTOR_VERSION}:{settings.ONTOLOGY_VERSION}:{digest}"
    
    def get(self, key: str) -> Optional[dict]:
        if self.backend_type == "valkey":
            raw = self.backend.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        return self.backend.get(key)
    
    def set(self, key: str, value: dict) -> None:
        if self.backend_type == "valkey":
            self.backend.setex(key, self.ttl, json.dumps(value, default=str, ensure_ascii=False))
        else:
            self.backend[key] = value
    
    def stats(self) -> dict:
        return {
            "backend": self.backend_type,
            "ttl_seconds": self.ttl,
            "available": self.backend is not None
        }


# Singleton
_cache_instance: Optional[DeterministicCache] = None

def get_cache() -> DeterministicCache:
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = DeterministicCache()
    return _cache_instance


def cached(prefix: str):
    """Decorator: Fonksiyon cagrilarini deterministik cache'ler"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not settings.CACHE_ENABLED:
                return func(self, *args, **kwargs)
            
            cache = get_cache()
            key = cache.make_key(prefix, {"args": args, "kwargs": kwargs})
            
            hit = cache.get(key)
            if hit is not None:
                hit["_cache"] = "HIT"
                return hit
            
            result = func(self, *args, **kwargs)
            if isinstance(result, dict) and not result.get("error"):
                cache.set(key, result)
                result["_cache"] = "MISS"
            return result
        return wrapper
    return decorator
