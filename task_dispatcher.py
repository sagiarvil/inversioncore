# task_dispatcher.py
import re
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class EngineRoute(str, Enum):
    BEHAVIORAL_TRIANGULATION = "behavioral_triangulation"  # 2-3 Görsel: Karakter, Big Five, Maske Makası
    DOCUMENT_FORENSICS       = "document_forensics"        # 1 Görsel/Belge: 2D FFT, PRNU, Sahtecilik
    WORKPLACE_LEGAL_MOBBING  = "workplace_legal_mobbing"   # Metin: İş Kanunu 24, TBK 417, Mobbing İhtarı
    RELATIONAL_GASLIGHTING   = "relational_gaslighting"    # Metin: Aldatma, DARVO, İlişki Feshi
    COGNITIVE_RED_TEAM       = "cognitive_red_team"        # Genel Karar Otopsisi / Pre-Mortem

class DispatcherDecision(BaseModel):
    selected_route: EngineRoute
    target_role: Optional[str] = "general"
    reasoning: str

class TaskDispatcher:
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

        # 1. Deterministik Veri Tipi Kuralı: 2 veya 3 görsel varsa doğrudan Karakter Motoru
        if img_count >= 2:
            return DispatcherDecision(
                selected_route=EngineRoute.BEHAVIORAL_TRIANGULATION,
                target_role=requested_role or "partner",
                reasoning=f"{img_count} durumsal görsel tespit edildi. 3-Nokta Karakter Penetrasyonu devrede."
            )

        # 2. Tek görsel kuralı: Belge/Montaj mı, tekil vesikalık mı?
        if img_count == 1:
            if any(w in q_lower for w in cls.PROFILE_KEYS) or requested_role in [
                "groom_candidate", "manager", "employee", "candidate_employee",
                "founder_bottleneck", "leadership_blindspot", "career_sabotage",
                "talent", "iq_cognition", "self", "partner", "business_partner", "friend"
            ]:
                return DispatcherDecision(
                    selected_route=EngineRoute.BEHAVIORAL_TRIANGULATION,
                    target_role=requested_role or "candidate_employee",
                    reasoning="Tekil portre profilleme talebi. Davranışsal analiz motoru devrede."
                )
            return DispatcherDecision(
                selected_route=EngineRoute.DOCUMENT_FORENSICS,
                target_role="document",
                reasoning="1 adet görsel/belge tespit edildi. 2D FFT ve PRNU Adli Tahrifat Motoru devrede."
            )

        # 3. Görselsiz Sadece Metin Girdisi: Anlamsal Yönlendirme
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
