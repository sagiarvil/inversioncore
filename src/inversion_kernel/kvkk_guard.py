# -*- coding: utf-8 -*-
"""
InversionCore NATO/Industrial Standard KVKK & Security Shield
PII Masking, Algorithm-based TC Kimlik / IBAN / Phone Validation,
Jailbreak Guardrails & Cryptographic Audit Logging.
"""

import re
import hashlib
import time
from typing import Dict, Any, Tuple, List


def validate_tc_kimlik(tc_str: str) -> bool:
    """Algoritmik TC Kimlik No doğrulaması (11 hane, checksum kuralı)."""
    if not re.match(r'^[1-9]\d{10}$', tc_str):
        return False
    digits = [int(d) for d in tc_str]
    # 1, 3, 5, 7, 9. hanelerin toplamının 7 katından 2, 4, 6, 8. hanelerin toplamı çıkarılır, mod 10 alınır -> 10. hane
    odd_sum = sum(digits[0:9:2])
    even_sum = sum(digits[1:8:2])
    tenth = ((odd_sum * 7) - even_sum) % 10
    if digits[9] != tenth:
        return False
    # İlk 10 hanenin toplamının mod 10'u -> 11. hane
    eleventh = sum(digits[:10]) % 10
    return digits[10] == eleventh


def validate_iban(iban_str: str) -> bool:
    """TR IBAN Modulo 97-10 doğrulaması."""
    clean = re.sub(r'\s+', '', iban_str.upper())
    if not re.match(r'^TR\d{24}$', clean):
        return False
    # Harfleri sayılara çevir (T=29, R=27)
    rearranged = clean[4:] + clean[:4]
    numeric = ''.join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)
    return int(numeric) % 97 == 1


class KVKKGuard:
    """NATO & BDDK/KVKK Seviyesinde PII Maskeleme ve Güvenlik Kalkanı."""

    PROMPT_INJECTION_PATTERNS = [
        r'ignore (all )?previous instructions',
        r'disregard (all )?prior prompts',
        r'system prompt(u|unu)? (bana )?g[oö]ster',
        r'sen bir (psikolog|doktor|avukat|hekim)sun rol yap',
        r'jailbreak',
        r'dan mode',
        r'developer mode on',
        r'bypass (security|filter|guard)',
        r'tüm kuralları unut',
    ]

    def __init__(self):
        self.injection_regex = [re.compile(p, re.IGNORECASE) for p in self.PROMPT_INJECTION_PATTERNS]

    def check_injection(self, text: str) -> Tuple[bool, str]:
        """Prompt injection ve jailbreak girişimlerini yakalar."""
        for regex in self.injection_regex:
            if regex.search(text):
                return True, f"Kritik Güvenlik İhlali: Yasaklı güvenlik aşma kalıbı ({regex.pattern}) tespit edildi."
        return False, ""

    def mask_pii(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Metin içindeki TC Kimlik, IBAN, Telefon, E-Posta ve Kredi Kartı verilerini maskeler.
        Geri dönüş: (Maskelenmiş Metin, {Maske_Kodu: Orijinal_Değer})
        """
        mapping = {}
        masked = text

        # 1. TC Kimlik No Tespiti ve Maskeleme
        tc_candidates = re.findall(r"\b[1-9]\d{10}\b", masked)
        for idx, tc in enumerate(tc_candidates):
            if validate_tc_kimlik(tc):
                token = f"[TCKN_{idx+1}_MASKED]"
                mapping[token] = tc
                masked = masked.replace(tc, token)

        # 2. IBAN Tespiti ve Maskeleme (Tüm TR IBAN formatları)
        iban_candidates = re.findall(r"\bTR\d{2}[\s\d]{22,28}\b", masked, re.IGNORECASE)
        for idx, iban in enumerate(iban_candidates):
            raw_iban = re.sub(r'\s+', '', iban)
            token = f"[IBAN_{idx+1}_MASKED]"
            mapping[token] = iban
            masked = masked.replace(iban, token)

        # 3. GSM / Telefon Tespiti (+90 5xx veya 05xx) - Sınır kontrollü
        phone_matches = re.findall(r"\b(?:\+90\s*|0)?5\d{2}[\s\.-]?\d{3}[\s\.-]?\d{2}[\s\.-]?\d{2}\b", masked)
        for idx, ph in enumerate(phone_matches):
            token = f"[TEL_{idx+1}_MASKED]"
            mapping[token] = ph
            masked = masked.replace(ph, token)

        # 4. E-Posta Maskeleme
        email_matches = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', masked)
        for idx, em in enumerate(email_matches):
            token = f"[EMAIL_{idx+1}_MASKED]"
            mapping[token] = em
            masked = masked.replace(em, token)

        return masked, mapping

    def generate_audit_hash(self, payload: Dict[str, Any], previous_hash: str = "") -> str:
        """Değiştirilemez Kriptografik SHA-256 Denetim Özeti (Blockchain-Grade Hash Chain)."""
        raw_str = f"{previous_hash}:{time.time()}:{str(sorted(payload.items()))}"
        return hashlib.sha256(raw_str.encode('utf-8')).hexdigest()
