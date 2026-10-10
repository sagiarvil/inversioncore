# -*- coding: utf-8 -*-
"""
InversionCore Executive Cognitive Forensics & Bias Auditing Kernel
CoPoLLM 8 Bilişsel Çarpıtma Taksonomisi, Rasch Madde Tepki Teorisi (IRT)
ve Türkçe Karar Rasyonelleştirme / Kendini Kandırma Forensics Motoru.
"""

import re
import math
from typing import Dict, Any, List


class CognitiveBiasType:
    ALL_OR_NOTHING = "Ya Hep Ya Hiç Düşüncesi (Polarized Thinking)"
    OVERGENERALIZATION = "Aşırı Genelleme (Overgeneralization)"
    MENTAL_FILTERING = "Zihinsel Filtreleme / Negatif Odak (Mental Filtering)"
    MIND_READING = "Zihin Okuma & Peşin Hüküm (Mind Reading / Jumping to Conclusions)"
    CATASTROPHIZING = "Felaketleştirme & Büyütme (Catastrophizing)"
    EMOTIONAL_REASONING = "Duygusal Mantık Yürütme (Emotional Reasoning)"
    SHOULD_STATEMENTS = "-Meli/-Malı Katı Kuralları (Rigid Should Statements)"
    VICTIM_PERSONALIZATION = "Kurban Rolü & Kişiselleştirme (Victim Stance & Personalization)"


COGNITIVE_BIAS_LEXICON = {
    CognitiveBiasType.ALL_OR_NOTHING: [
        r'\b(ya\s+.*\s+ya\s+da|hep\s+ya\s+da\s+hiç|ya\s+tamamen|ya\s+hep|kesinlikle\s+tek\s+yol|başka\s+yol\s+yok|ya\s+kazanırız\s+ya\s+batarız)\b',
        r'\b(sıfır\s+ihtimal|ya\s+mükemmel|ya\s+çöp|hiçbir\s+zaman\s+olmaz|her\s+zaman\s+böyle)\b'
    ],
    CognitiveBiasType.OVERGENERALIZATION: [
        r'\b(herkes|hiç\s+kimse|tüm\s+insanlar|her\s+zaman|asla|hiçbir\s+zaman|daima|istisnasız)\b',
        r'\b(türkiye\'de\s+iş\s+yapılmaz|kimseye\s+güvenilmez|ortaklık\s+asla\s+yürümez)\b'
    ],
    CognitiveBiasType.MENTAL_FILTERING: [
        r'\b(iyi\s+ama|fakat\s+tek\s+sorun|onun\s+bir\s+önemi\s+yok|başarı\s+tesadüf|bunu\s+sayma|şans\s+eseri)\b',
        r'\b(her\s+şey\s+berbat|tek\s+bir\s+hata\s+yetti|bütün\s+emek\s+boşa\s+gitti)\b'
    ],
    CognitiveBiasType.MIND_READING: [
        r'\b(biliyorum\s+bana\s+karşı|arkamdan\s+iş\s+çeviriyorlar|kesin\s+böyle\s+düşünüyor|beni\s+küçümsüyor|niyeti\s+kötü)\b',
        r'\b(anladım\s+ben\s+onun\s+ne\s+yapacağını|bana\s+kastı\s+var|hissediyorum\s+böyle\s+olacak)\b'
    ],
    CognitiveBiasType.CATASTROPHIZING: [
        r'\b(mahvolduk|bittik|kesin\s+iflas|hayatım\s+kaydı|dünyanın\s+sonu|kıyamet\s+koptu|toparlanamayız)\b',
        r'\b(her\s+şeyimizi\s+kaybederiz|geri\s+dönüşü\s+yok|felaket\s+olacak|asla\s+kurtulamayız)\b'
    ],
    CognitiveBiasType.EMOTIONAL_REASONING: [
        r'\b(içimden\s+geliyor|öyle\s+hissediyorum\s+demek\s+ki\s+doğru|içime\s+doğdu|hissiyatım\s+yanıltmaz)\b',
        r'\b(korktuğuma\s+göre\s+tehlikeli|kendimi\s+suçlu\s+hissediyorsam\s+ben\s+hatalıyım)\b'
    ],
    CognitiveBiasType.SHOULD_STATEMENTS: [
        r'\b(yapmak\s+zorundaydım|mecburum|etmek\s+zorundalar|böyle\s+olmalıydı|şart|başka\s+çare\s+yok)\b',
        r'\b(hata\s+yapmamalıyım|herkes\s+dürüst\s+olmalı|bana\s+saygı\s+duymak\s+zorundalar)\b'
    ],
    CognitiveBiasType.VICTIM_PERSONALIZATION: [
        r'\b(hep\s+benim\s+yüzümden|bana\s+komplo\s+kurdular|kaderim\s+böyle|elim\s+kolum\s+bağlı|kurban\s+seçildim)\b',
        r'\b(bana\s+yapıldı|herkes\s+bana\s+düşman|ben\s+olmasaydım\s+böyle\s+olmazdı|haksızlığa\s+uğradım)\b'
    ]
}


class CognitiveForensicsKernel:
    """Bilişsel Çarpıtma ve Karar Rasyonelleştirme Analiz Çekirdeği."""

    def __init__(self):
        self.compiled_lexicon = {
            bias: [re.compile(p, re.IGNORECASE) for p in patterns]
            for bias, patterns in COGNITIVE_BIAS_LEXICON.items()
        }

    def audit_text(self, text: str) -> Dict[str, Any]:
        """
        Metin üzerindeki bilişsel çarpıtmaları, delil cümlelerini ve şiddetini çıkarır.
        """
        findings = []
        total_hits = 0
        sentences = [s.strip() for s in re.split(r'[.!?\n]+', text) if len(s.strip()) > 5]

        bias_scores = {}
        for bias_name, regex_list in self.compiled_lexicon.items():
            hits = []
            for sent in sentences:
                for regex in regex_list:
                    match = regex.search(sent)
                    if match:
                        hits.append({
                            "delil_cumlesi": sent,
                            "yakalanan_ifade": match.group(0)
                        })
                        break
            count = len(hits)
            bias_scores[bias_name] = count
            total_hits += count
            if count > 0:
                findings.append({
                    "carpitma_adi": bias_name,
                    "frekans": count,
                    "ornekler": hits[:3]
                })

        # Rasch IRT (Item Response Theory) Bilişsel Savunma / Rasyonelleştirme Endeksi Hesabı
        num_sentences = max(len(sentences), 1)
        p_raw = min(total_hits / (num_sentences * 1.5), 0.98)
        p_clamped = max(p_raw, 0.02)
        
        # Theta (Bilişsel Çarpıtma Yetenek / Direnç Derecesi: logit ölçeği)
        theta_logit = round(math.log(p_clamped / (1.0 - p_clamped)), 2)
        
        # Self-Deception Index (0.0 - 1.0)
        sdi = round(1.0 / (1.0 + math.exp(-theta_logit)), 3)

        # Karar Körlüğü Şiddeti (Executive Blindness Level)
        if sdi > 0.70:
            severity = "YÜKSEK BİLİŞSEL KÖRLÜK (Kritik Karar Çarpıtması)"
            verdict = "RED"
        elif sdi > 0.40:
            severity = "ORTA DÜZEY RASYONELLEŞTİRME (Kör Noktalar Mevcut)"
            verdict = "DOĞRULAMA GEREKLİ"
        else:
            severity = "DÜŞÜK ÇARPITMA (Rasyonel ve Nesnel Akıl Yürütme)"
            verdict = "GO"

        return {
            "toplam_cumle": num_sentences,
            "toplam_carpitma_vuruşu": total_hits,
            "self_deception_index": sdi,
            "rasch_theta_logit": theta_logit,
            "karar_korlugu_derecesi": severity,
            "on_oneri_karari": verdict,
            "tespit_edilen_carpitmalar": findings,
            "detayli_skorlar": bias_scores
        }
