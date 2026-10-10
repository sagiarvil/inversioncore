# -*- coding: utf-8 -*-
"""
InversionCore CoPoLLM Official Repository Adapter
Chips98/CoPoLLM-for-ACL-2026 ACL Paper Architecture Integration
8 Cognitive Bias Types + CBT State Machine Integration
"""

import os
import json
from typing import Dict, Any, List, Optional


class CoPoLLMAdapter:
    """CoPoLLM (ACL 2026) Resmi Depo ve Kural Adaptörü."""

    COPOLLM_REPO_PATH = "/Users/macair1/projects/inversioncore/external/CoPoLLM-for-ACL-2026"

    # CoPoLLM CBT Bilişsel Çarpıtma Sınıflandırması
    COPOLLM_BIAS_MAP = {
        "All-or-nothing thinking": "Ya Hep Ya Hiç Düşüncesi",
        "Overgeneralization": "Aşırı Genelleme",
        "Mental filter": "Zihinsel Filtreleme",
        "Disqualifying the positive": "Olumluyu Geçersiz Kılma",
        "Jumping to conclusions": "Peşin Hüküm / Zihin Okuma",
        "Magnification/Minimization": "Büyütme / Küçültme",
        "Emotional reasoning": "Duygusal Mantık Yürütme",
        "Should statements": "Katı Kurallar (-meli/-malı)",
        "Labeling and mislabeling": "Etiketleme",
        "Personalization": "Kişiselleştirme / Kurban Rolü"
    }

    def __init__(self):
        self.is_repo_cloned = os.path.exists(self.COPOLLM_REPO_PATH)
        self.dataset_sample_count = 0
        if self.is_repo_cloned:
            test_path = os.path.join(self.COPOLLM_REPO_PATH, "data", "test.json")
            if os.path.exists(test_path):
                try:
                    with open(test_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.dataset_sample_count = len(data) if isinstance(data, list) else 0
                except Exception:
                    pass

    def get_status(self) -> Dict[str, Any]:
        """CoPoLLM modül durumunu döndürür."""
        return {
            "status": "READY" if self.is_repo_cloned else "MISSING",
            "repo_path": self.COPOLLM_REPO_PATH,
            "dataset_samples": self.dataset_sample_count,
            "paper": "CoPoLLM: Cognitive Policy-Driven LLM for Diagnosis and Intervention (ACL 2026)",
            "supported_biases": list(self.COPOLLM_BIAS_MAP.keys())
        }
