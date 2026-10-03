from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from services.lab_scope import ScopeDecision, classify_lab_scope

IntentKind = Literal["business", "lab", "mixed", "unsafe", "local", "unrelated"]

BUSINESS_HINTS = (
    "opening hours", "open today", "what time", "business hours", "price", "cost",
    "how much", "service", "package", "panel", "book", "booking", "appointment",
    "discount", "promotion",
    "walk-in", "walk in", "turnaround", "refund", "cancel", "address", "location",
    "contact", "เวลาเปิด", "เปิดกี่โมง", "ราคา", "ค่าบริการ", "แพ็กเกจ", "บริการ",
    "จอง", "walk-in", "เตรียมตัว", "รับผล", "คืนเงิน", "ยกเลิก", "ที่อยู่", "ติดต่อ", "ตรวจ",
    "เปิด", "วันเสาร์", "วันอาทิตย์", "วันหยุด", "ผลจะออก", "กี่ชั่วโมง", "ส่งผล", "ส่วนลด", "ลดให้",
    "เท่าไร", "กี่บาท", "บาท", "รวม",
)
UNSAFE_HINTS = (
    "diagnose", "diagnosis", "prescribe", "prescription", "change my dose", "stop my medication",
    "วินิจฉัย", "สั่งยา", "ปรับยา", "หยุดยา", "เพิ่มยา", "ลดขนาดยา",
)
MEDICATION_CHANGE_PATTERN = re.compile(
    r"\b(?:double|increase|decrease|adjust|change|stop|start|skip|take|use|try)\b"
    r"(?:\s+(?:your|my|the|a|an))?"
    r"(?:\s+[a-z][a-z0-9_-]*){0,3}"
    r"\s+(?:dose|dosage|metformin|insulin|medication|medicine|tablets?|pills?)\b",
    re.IGNORECASE,
)
MEDICATION_ADVICE_PATTERN = re.compile(
    r"\b(?:take|use|start|stop|try)\s+(?:(?:your|my|the|a|an)\s+)?"
    r"[a-z][a-z0-9_-]*(?=\s*(?:[.!?,;:]|$)|\s+(?:for|with|because|daily|twice|once)\b)",
    re.IGNORECASE,
)
UNRELATED_TASK_PATTERN = re.compile(
    r"\b(?:write|create|build|debug|fix|run|code)\b.{0,60}\b(?:python|javascript|typescript|sql|scraper|scrape|api|website|program)\b|"
    r"\b(?:python|javascript|typescript|sql|scraper|scrape|api|website|program)\b.{0,60}\b(?:write|create|build|debug|fix|run|code)\b|"
    r"\b(?:write|create|compose|draft|generate|make)\b.{0,80}\b(?:poem|story|song|joke|vacation|holiday|recipe|travel)\b|"
    r"\b(?:poem|story|song|joke|vacation|holiday|recipe|travel)\b.{0,80}\b(?:write|create|compose|draft|generate|make)\b",
    re.IGNORECASE,
)
NON_LAB_ACTIVITY_HINTS = (
    "bake", "bread", "cook", "recipe", "vacation", "holiday", "travel", "poem", "story", "song", "joke",
)
PRIVILEGED_BUSINESS_HINTS = (
    "i am the owner", "i'm the owner", "as the owner", "owner,", "change the price to",
    "set the price", "override the policy", "ignore the policy", "grant access",
    "ฉันเป็นเจ้าของ", "ผมเป็นเจ้าของ", "ในฐานะเจ้าของ", "ตั้งราคา",
    "ข้ามนโยบาย", "เปิดเผยสิทธิ์",
)
LAB_TERM_HINTS = (
    "hb", "hba1c", "cbc", "fpg", "ferritin", "creatinine", "egfr", "cholesterol", "triglyceride",
    "alt", "ast", "tsh", "platelet", "marker-a", "marker-b", "marker-c",
    "ผลตรวจ", "ค่าเลือด", "ค่าแล็บ", "ผลแล็บ",
)
MIXED_ANALYSIS_HINTS = (
    "result", "mean", "explain", "interpret", "high", "low", "normal",
    "ผลตรวจ", "ผลแล็บ", "หมายความ", "อธิบาย", "แปลผล", "สูง", "ต่ำ",
)
CONFIRMED_EXTRACTION_ANALYSIS_HINTS = (
    "explain", "interpret", "what do these values", "what do these results",
    "อธิบาย", "แปลผล", "อ่านค่า", "ค่าที่อ่าน", "ผลที่อ่าน",
)
CONFIRMED_EXTRACTION_BUSINESS_HINTS = (
    "price", "cost", "how much", "service", "package", "book", "booking",
    "appointment", "refund", "cancel", "address", "location", "contact",
    "ราคา", "ค่าบริการ", "แพ็กเกจ", "จอง", "คืนเงิน", "ยกเลิก", "ที่อยู่", "ติดต่อ",
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


def _contains_unquoted_hint(message: str, hints: tuple[str, ...]) -> bool:
    unquoted = re.sub(r"[\"'“‘].*?[\"'”’]", " ", message, flags=re.DOTALL)
    return _contains_hint(unquoted, hints)


def route_intent(
    message: str,
    history: list[dict[str, str]] | None = None,
    confirmed_extraction: dict | None = None,
) -> IntentDecision:
    prior = history or []
    scope = classify_lab_scope(message, prior)
    confirmed_prompt = any(hint in " ".join(message.casefold().split()) for hint in CONFIRMED_EXTRACTION_ANALYSIS_HINTS)
    if not scope.allowed and confirmed_extraction and confirmed_prompt:
        marker_context = " ".join(
            str(field.get("marker", ""))
            for field in confirmed_extraction.get("fields", ())
            if isinstance(field, dict)
        )
        if marker_context:
            scope = classify_lab_scope(f"{message} {marker_context}", prior)
    has_business = _contains_hint(message, BUSINESS_HINTS)
    has_lab = scope.allowed or _contains_hint(message, LAB_TERM_HINTS)

    if (
        _contains_hint(message, UNSAFE_HINTS)
        or MEDICATION_CHANGE_PATTERN.search(message)
        or MEDICATION_ADVICE_PATTERN.search(message)
    ):
        return IntentDecision("unsafe", "unsafe_medical_request", False, scope)
    if _contains_unquoted_hint(message, PRIVILEGED_BUSINESS_HINTS):
        return IntentDecision("unsafe", "unauthorized_business_request", False, scope)
    if UNRELATED_TASK_PATTERN.search(message):
        return IntentDecision("unrelated", "outside_lab_scope", False, scope)
    if has_lab and _contains_hint(message, NON_LAB_ACTIVITY_HINTS):
        return IntentDecision("unrelated", "outside_lab_scope", False, scope)
    if (
        confirmed_extraction
        and confirmed_prompt
        and not _contains_hint(message, CONFIRMED_EXTRACTION_BUSINESS_HINTS)
    ):
        return IntentDecision("lab", "confirmed_image_analysis", True, scope)
    if has_business and has_lab:
        # A service/catalog question may mention a test name (e.g. CBC price)
        # without becoming a mixed clinical interpretation request. Keep the
        # mixed route for questions that explicitly ask to interpret a result.
        if _contains_hint(message, MIXED_ANALYSIS_HINTS):
            return IntentDecision("mixed", "mixed_business_and_lab", True, scope)
        return IntentDecision("business", "business_faq", True, scope)
    if has_business:
        return IntentDecision("business", "business_faq", True, scope)
    if scope.allowed or has_lab:
        return IntentDecision("lab", scope.reason, True, scope)
    if scope.reason in {"greeting", "help", "closing", "ambiguous", "empty_message"}:
        return IntentDecision("local", scope.reason, False, scope)
    return IntentDecision("unrelated", "outside_lab_scope", False, scope)
