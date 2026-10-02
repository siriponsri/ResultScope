from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from services.lab_scope import ScopeDecision, classify_lab_scope

IntentKind = Literal["business", "lab", "mixed", "unsafe", "local", "unrelated"]

BUSINESS_HINTS = (
    "opening hours", "open today", "what time", "business hours", "price", "cost",
    "how much", "service", "package", "panel", "book", "booking", "appointment",
    "walk-in", "walk in", "turnaround", "refund", "cancel", "address", "location",
    "contact", "เวลาเปิด", "เปิดกี่โมง", "ราคา", "ค่าบริการ", "แพ็กเกจ", "บริการ",
    "จอง", "walk-in", "เตรียมตัว", "รับผล", "คืนเงิน", "ยกเลิก", "ที่อยู่", "ติดต่อ",
)
UNSAFE_HINTS = (
    "diagnose", "diagnosis", "prescribe", "prescription", "change my dose", "stop my medication",
    "วินิจฉัย", "สั่งยา", "ปรับยา", "หยุดยา", "เพิ่มยา", "ลดขนาดยา",
)
LAB_TERM_HINTS = (
    "hb", "hba1c", "cbc", "ferritin", "creatinine", "egfr", "cholesterol", "triglyceride",
    "alt", "ast", "tsh", "platelet", "ผลตรวจ", "ค่าเลือด", "ค่าแล็บ", "ผลแล็บ",
)


@dataclass(frozen=True)
class IntentDecision:
    kind: IntentKind
    reason: str
    allowed: bool
    scope: ScopeDecision


def _contains_hint(message: str, hints: tuple[str, ...]) -> bool:
    normalized = " ".join(message.casefold().split())
    for hint in hints:
        if hint.isascii() and hint.replace("-", "").replace(" ", "").isalnum():
            pattern = rf"(?<![a-z0-9]){re.escape(hint)}(?![a-z0-9])"
            if re.search(pattern, normalized):
                return True
        elif hint in normalized:
            return True
    return False


def route_intent(message: str, history: list[dict[str, str]] | None = None) -> IntentDecision:
    prior = history or []
    scope = classify_lab_scope(message, prior)
    has_business = _contains_hint(message, BUSINESS_HINTS)
    has_lab = scope.allowed or _contains_hint(message, LAB_TERM_HINTS)

    if _contains_hint(message, UNSAFE_HINTS):
        return IntentDecision("unsafe", "unsafe_medical_request", False, scope)
    if has_business and has_lab:
        return IntentDecision("mixed", "mixed_business_and_lab", True, scope)
    if has_business:
        return IntentDecision("business", "business_faq", True, scope)
    if scope.allowed:
        return IntentDecision("lab", scope.reason, True, scope)
    if scope.reason in {"greeting", "help", "closing", "ambiguous", "empty_message"}:
        return IntentDecision("local", scope.reason, False, scope)
    return IntentDecision("unrelated", "outside_lab_scope", False, scope)
