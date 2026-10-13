# task_dispatcher.py
import re
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class EngineRoute(str, Enum):
    BEHAVIORAL_TRIANGULATION = "behavioral_triangulation"  # 2-3 Görsel: Karakter, Big Five, Maske Makası
    FINANCIAL_PHYSICS        = "financial_physics"         # Metin/Sayı: Rust & Python Diferansiyel İflas, Fat-Tail, FTA
    WORKPLACE_LEGAL_MOBBING  = "workplace_legal_mobbing"   # Metin: İş Kanunu 24, TBK 417, Mobbing İhtarı
    RELATIONAL_GASLIGHTING   = "relational_gaslighting"    # Metin: Aldatma, DARVO, İlişki Feshi
    COGNITIVE_RED_TEAM       = "cognitive_red_team"        # Genel Karar Otopsisi / Pre-Mortem

class DispatcherDecision(BaseModel):
    selected_route: EngineRoute
    target_role: Optional[str] = "general"
    reasoning: str

class TaskDispatcher:
    FINANCIAL_KEYS = [
        "nakit", "sermaye", "bütçe", "kira", "gider", "maliyet", "gelir", "para", "borç",
        "yatırım", "runway", "iflas", "zarar", "kar", "faiz", "kredi", "dolar", "tl", "euro"
    ]
    MOBBING_KEYS = [
        "patron", "müdür", "istifa", "tazminat", "maaş", "şirket", "ofis", 
        "amir", "mobbing", "ik", "işveren", "mesai", "çalışan", "baskı", "tutanak"
    ]
    RELATION_KEYS = [
        "sevgili", "aldatma", "eski", "ayrılık", "evlilik", "mesaj", "güven", 
        "yalan", "ihanet", "flört", "narsisist", "gaslighting", "darvo", "boşanma"
    ]
    PROFILE_KEYS = [
        "damat", "gelin", "ortak", "güvenilir mi", "karakteri nasıl", "kim bu", 
        "nasıl biri", "işe alım", "aday", "personel", "mülakat", "profil", "iq", "yetenek"
    ]

    @classmethod
    def resolve_route(cls, query: str, images: Optional[List[str]] = None, requested_role: Optional[str] = None) -> DispatcherDecision:
        images = [img for img in (images or []) if img]
        img_count = len(images)
        q_lower = (query or "").lower()

        # 1. Deterministik Kural: 2 veya 3 görsel varsa doğrudan Çoklu Karakter Penetrasyonu
        if img_count >= 2:
            return DispatcherDecision(
                selected_route=EngineRoute.BEHAVIORAL_TRIANGULATION,
                target_role=requested_role or "partner",
                reasoning=f"{img_count} durumsal görsel tespit edildi. Çapraz Maske Makası ve Karakter Penetrasyonu devrede."
            )

        if img_count == 1:
            return DispatcherDecision(
                selected_route=EngineRoute.COGNITIVE_RED_TEAM,
                target_role="general",
                reasoning="Yetersiz görsel sayısı (Tek görselle karakter penetrasyonu yapılamaz, en az 2 görsel şarttır)."
            )

        # 3. Görselsiz Sadece Metin Girdisi: Anlamsal Yönlendirme
        # Finansal / Sermaye / Gider rakamları veya anahtarları varsa Rust & Python Fizik Motoru
        if any(w in q_lower for w in cls.FINANCIAL_KEYS) or re.search(r'[0-9]+.*(?:tl|\$|usd|euro|nakit|kira|sermaye)', q_lower):
            return DispatcherDecision(
                selected_route=EngineRoute.FINANCIAL_PHYSICS,
                target_role="financial_strategist",
                reasoning="Finansal / Sermaye / Risk dinamikleri tespit edildi. Rust & Python Diferansiyel İflas ve Fat-Tail Motoru devrede."
            )

        if any(w in q_lower for w in cls.MOBBING_KEYS):
            return DispatcherDecision(
                selected_route=EngineRoute.WORKPLACE_LEGAL_MOBBING,
                target_role="employee",
                reasoning="İş yeri mobbingi ve hiyerarşik hak gasbı tespiti. İş Kanunu / TBK motoru devrede."
            )

        if any(w in q_lower for w in cls.RELATION_KEYS):
            return DispatcherDecision(
                selected_route=EngineRoute.RELATIONAL_GASLIGHTING,
                target_role="partner",
                reasoning="İkili ilişki, aldatma veya DARVO döngüsü tespiti. İlişki toksisite motoru devrede."
            )

        return DispatcherDecision(
            selected_route=EngineRoute.COGNITIVE_RED_TEAM,
            target_role="general",
            reasoning="Standart bilişsel karar otopsisi ve tersine mühendislik motoru."
        )
