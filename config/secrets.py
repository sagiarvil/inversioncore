# .env DOSYASINDAN YUKLENECEK - YEREL ALFA MOTORU
import os
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "local-alfa-no-key-needed")
DEEPSEEK_ENDPOINT = os.environ.get("DEEPSEEK_ENDPOINT", "http://127.0.0.1:8081/v1")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "coder_candidate")
VALKEY_URL = os.environ.get("VALKEY_URL", "redis://localhost:6379")
CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", "86400"))  # 24 saat
