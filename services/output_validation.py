from __future__ import annotations

import json
import re
from typing import Any, Iterable

from config import settings

NUMBER_PATTERN = re.compile(r"(?<![\w])\d+(?:[.,]\d+)?(?![\w])")
SOURCE_MARKER_PATTERN = re.compile(r"\[((?:SRC|DEMO)-[A-Z0-9_-]+)\]", re.IGNORECASE)
SOURCE_ID_PATTERN = re.compile(r"\b(?:SRC|DEMO)-[A-Z0-9_-]+\b", re.IGNORECASE)
BRACKETED_SOURCE_PATTERN = re.compile(r"\[((?:[A-Za-z][A-Za-z0-9]*)-[A-Za-z0-9_-]{1,80})\]")
URL_PATTERN = re.compile(r"https?://[^\s<>\]\)\"']+", re.IGNORECASE)
SOURCE_ATTRIBUTION_PATTERN = re.compile(
    r"\b(?:source|sources|citation|citations|reference|references|from|แหล่ง(?:ที่มา|ข้อมูล)?|"
    r"อ้างอิง|ข้อมูลจาก|จาก)\s*(?:is|are|คือ|ได้แก่|:)?\s*((?:SRC|DEMO)-[A-Z0-9_-]+)\b",
    re.IGNORECASE,
)
SOURCE_CUE_PATTERN = re.compile(
    r"\b(?:source|sources|citation|citations|reference|references)\b|"
    r"แหล่ง(?:ที่มา|ข้อมูล)?|อ้างอิง|ข้อมูลจาก",
    re.IGNORECASE,
)
UNBRACKETED_SOURCE_CUE_PATTERN = re.compile(
    r"\b(?:according\s+to|as\s+reported\s+by|from)\s+"
    r"[A-Z][A-Za-z0-9-]*(?:\.[A-Za-z0-9-]+)*(?:\s+[A-Z][A-Za-z0-9-]*(?:\.[A-Za-z0-9-]+)*)*\b",
    re.IGNORECASE,
)
SOURCE_NON_ATTRIBUTION_PATTERN = re.compile(
    r"\b(?:source|sources|citation|citations|reference|references)\b\s+"
    r"(?:does not|do not|is not|are not|was not|were not|is unavailable|are unavailable|"
    r"not available|not provided|not specified)\b|"
    r"(?:ไม่มี|ไม่พบ|ยังไม่มี)\s*(?:แหล่ง|ข้อมูลอ้างอิง|ข้อมูลจาก)",
    re.IGNORECASE,
)
UNSAFE_OUTPUT_PATTERN = re.compile(
    r"\b(?:diagnos\w*|prescri\w*|change your dose|stop your medication)\b|"
    r"วินิจฉัย|สั่งยา|ปรับยา|หยุดยา",
    re.IGNORECASE,
)
SAFE_DIAGNOSIS_DISCLAIMER_PATTERN = re.compile(
    r"\b(?:not|no|without)\s+(?:a\s+)?diagnos(?:is|e|ing|tic|ed)?\b|"
    r"\b(?:educational|general)\s+(?:information|explanation),?\s+not\s+(?:a\s+)?diagnos(?:is|tic)\b|"
    r"ไม่ใช่(?:การ)?วินิจฉัย",
    re.IGNORECASE,
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
CLINICAL_TREATMENT_PATTERN = re.compile(
    r"\b(?:you should|you need to|consider|recommended to|advised to)\s+"
    r"(?:undergo|have|get|start|begin|receive|seek)\s+"
    r"(?:surgery|an operation|treatment|therapy|chemotherapy|radiation)\b",
    re.IGNORECASE,
)
THAI_MEDICATION_ADVICE_PATTERN = re.compile(
    r"(?:ควร|แนะนำ(?:ให้)?|สามารถ)\s*(?:เพิ่ม|ลด|ปรับ|หยุด|เริ่ม|เปลี่ยน)\s*(?:ขนาด)?\s*ยา|"
    r"(?:เพิ่ม|ลด|ปรับ|หยุด|เริ่ม|เปลี่ยน)\s*(?:ขนาด)?\s*ยา(?:ได้|เลย|นะ|ครับ|ค่ะ)?",
    re.IGNORECASE,
)
UNSUPPORTED_DIAGNOSIS_PATTERN = re.compile(
    r"\b(?:you have|you are(?:\s+a)?|this (?:means|shows|is))\s+(?:cancer|diabetes|anemic|anaemic|diabetic|leukemia|tumou?r|hiv|โรค)\b|"
    r"\b(?:you have|you've got|(?:your|the)\s+(?:result|results|labs?)\s+(?:show|shows|indicate|indicates|confirm|confirms|prove|proves|is\s+consistent\s+with)|"
    r"your\s+[a-z0-9_-]+\s+(?:show|shows|indicate|indicates|confirm|confirms|prove|proves|suggest|suggests|is\s+consistent\s+with)|"
    r"this\s+(?:means|shows|indicates|confirms))\s+(?:cancer|diabetes|hiv|kidney failure|renal failure|liver failure|"
    r"heart failure|heart attack|sepsis|leukemia|an infection|a disease|a disorder|a syndrome|"
    r"kidney disease|renal disease|liver disease|heart disease)\b|"
    r"คุณเป็น(?:โรค|มะเร็ง|เบาหวาน)|"
    r"คุณ(?<!ไม่)(?<!ไม่ได้)(?:มี|เป็น)\s*(?:โรค)?(?:ไต|ตับ|หัวใจ|มะเร็ง|เบาหวาน|โลหิตจาง|เอชไอวี|hiv)|"
    r"(?:ผล(?:ตรวจ)?|ผลนี้|ค่านี้)[^.!?\n]{0,40}(?<!ไม่)(?<!ไม่ได้)"
    r"(?:ยืนยัน|บ่งชี้|แสดง|หมายความว่า|แปลว่า)(?:ว่า)?[^.!?\n]{0,20}"
    r"(?:เป็น)?(?:โรค)?(?:มะเร็ง|เบาหวาน|โลหิตจาง|โรคไต|โรคตับ|โรคหัวใจ|เอชไอวี|hiv)",
    re.IGNORECASE,
)
HEDGED_DIAGNOSIS_PATTERN = re.compile(
    r"\b(?:"
    r"you\s+(?:could|may|might)\s+have\s+|"
    r"(?:this|the|these)\s+(?:result|results|finding|findings)?\s*"
    r"(?:raises?\s+(?:a\s+)?concern\s+for|is\s+suggestive\s+of|"
    r"are\s+suggestive\s+of|suggests?|may\s+indicate|might\s+indicate|"
    r"could\s+indicate|is\s+indicative\s+of|are\s+indicative\s+of)\s+|"
    r"(?:possible|suspected)\s+)"
    r"(?:cancer|diabetes|anemia|anaemia|diabetic|leukemia|tumou?r|hiv|"
    r"kidney\s+(?:failure|disease)|renal\s+(?:failure|disease)|"
    r"liver\s+(?:failure|disease)|heart\s+(?:failure|disease|attack)|"
    r"sepsis|an\s+infection|a\s+disease|a\s+disorder|a\s+syndrome)\b",
    re.IGNORECASE,
)
LAB_BUSINESS_CLAIM_PATTERN = re.compile(
    r"\b(?:price|cost|discount|promotion|refund|opening\s+hours?|business\s+hours?|"
    r"booking|appointment|walk[- ]?in|turnaround(?:\s+time)?|result\s+time|"
    r"home\s+collection|credit\s+cards?|visa|mastercard|payment|free|complimentary|"
    r"doctor|nurse|pharmacist|staff)\b|"
    r"ราคา|ค่าบริการ|ส่วนลด|โปรโมชั่น|โปรโมชัน|คืนเงิน|เวลาเปิด|เวลาบริการ|"
    r"จอง|นัดหมาย|คิวว่าง|รับบัตรเครดิต|เก็บตัวอย่างถึงบ้าน|ฟรี|แพทย์|หมอ|พยาบาล|บุคลากร",
    re.IGNORECASE,
)
LAB_MARKER_DIAGNOSIS_PATTERN = re.compile(
    r"\b[a-z][a-z0-9_-]*\s+(?:show|shows|indicate|indicates|confirm|confirms|prove|proves|suggest|suggests|"
    r"is\s+consistent\s+with)\s+(?:cancer|diabetes|anemia|anaemia|leukemia|tumou?r|hiv|"
    r"kidney failure|renal failure|liver failure|heart failure|heart attack|sepsis|a disease|a disorder|a syndrome)\b",
    re.IGNORECASE,
)
UNAUTHORIZED_TRANSACTION_PATTERN = re.compile(
    r"\b(?:booking|appointment)\s+(?:is\s+)?confirmed\b|\b(?:booked|paid|refunded)\b|"
    r"\b(?:payment|refund)\s+(?:was\s+)?(?:completed|processed)\b|\b(?:database|record)\s+updated\b|"
    r"จองสำเร็จ|ยืนยันนัดหมาย|ชำระเงินแล้ว|คืนเงินแล้ว|แก้ฐานข้อมูลแล้ว",
    re.IGNORECASE,
)


class OutputValidationError(ValueError):
    """Raised when provider output cannot be proven safe for this request."""


BUSINESS_CONCEPT_HINTS: dict[str, tuple[str, ...]] = {
    "price": ("price", "cost", "บาท", "ราคา", "ค่าบริการ"),
    "discount": ("discount", "promotion", "ส่วนลด", "โปรโมชั่น", "โปรโมชัน"),
    "refund": ("refund", "refunds", "return", "คืนเงิน"),
    "hours": ("opening hours", "business hours", "open", "closed", "เวลาเปิด", "เวลาบริการ", "เวลาทำการ", "เปิด", "ปิด", "เปิดกี่โมง"),
    "booking": ("booking", "appointment", "จอง", "นัดหมาย"),
    "preparation": ("preparation", "fasting", "specimen", "เตรียมตัว", "งดอาหาร"),
    "turnaround": ("turnaround", "result time", "รับผล", "ออกผล", "ใช้เวลา"),
}

THAI_BUSINESS_CLAIM_HINTS: tuple[str, ...] = (
    "ฟรี",
    "ส่วนลด",
    "ลดราคา",
    "โปรโมชั่น",
    "โปรโมชัน",
    "คิวว่าง",
    "รับประกันคิว",
    "จองได้",
    "คืนเงิน",
    "โอนคืน",
    "แพทย์",
    "หมอ",
    "พยาบาล",
    "บุคลากร",
    "บัตรเครดิต",
)


NEGATIVE_BUSINESS_FACTS: dict[str, tuple[str, ...]] = {
    "discount": ("ไม่มีโปรโมชั่น", "ไม่มีส่วนลด", "no confirmed discount", "no promotion"),
    "refund": ("ไม่มีนโยบายคืนเงินจริง", "ไม่มีการคืนเงินจริง", "no real refund policy"),
    "preparation": ("ยังไม่มีข้อมูลการเตรียมตัว", "no confirmed preparation"),
    "turnaround": ("ยังไม่มีข้อมูลการเตรียมตัว", "ไม่มีข้อมูล.*ระยะเวลา", "no confirmed result time"),
}

HOURS_EVIDENCE_HINTS = (
    "วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์", "วันอาทิตย์", "ปิด",
    "เวลาบริการ", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "closed",
)
HOURS_DAY_ALIASES: dict[str, tuple[str, ...]] = {
    "monday": ("monday", "วันจันทร์"),
    "tuesday": ("tuesday", "วันอังคาร"),
    "wednesday": ("wednesday", "วันพุธ"),
    "thursday": ("thursday", "วันพฤหัสบดี"),
    "friday": ("friday", "วันศุกร์"),
    "saturday": ("saturday", "วันเสาร์"),
    "sunday": ("sunday", "วันอาทิตย์"),
}
HOURS_DAY_RANGE_PATTERN = re.compile(
    r"(?P<start>monday|วันจันทร์|tuesday|วันอังคาร|wednesday|วันพุธ|"
    r"thursday|วันพฤหัสบดี|friday|วันศุกร์|saturday|วันเสาร์|sunday|วันอาทิตย์)"
    r"\s*(?:ถึง|to|through|[-–—])\s*"
    r"(?P<end>monday|วันจันทร์|tuesday|วันอังคาร|wednesday|วันพุธ|"
    r"thursday|วันพฤหัสบดี|friday|วันศุกร์|saturday|วันเสาร์|sunday|วันอาทิตย์)",
    re.IGNORECASE,
)
HOURS_TIME_RANGE_PATTERN = re.compile(
    r"(?P<start_hour>\d{1,2})[:.](?P<start_minute>\d{2})\s*(?:ถึง|to|through|[-–—])\s*"
    r"(?P<end_hour>\d{1,2})[:.](?P<end_minute>\d{2})",
    re.IGNORECASE,
)
HOURS_DAY_ORDER = tuple(HOURS_DAY_ALIASES)
UNSUPPORTED_HOURS_CLAIM_PATTERN = re.compile(
    r"เปิดทุกวัน|ทุกวันตลอดคืน|ตลอดคืน|ตลอดวัน|24\s*(?:ชั่วโมง|ชั่?วโมง)|24/7|open\s+(?:every|all)\s+day|open\s+24",
    re.IGNORECASE,
)
BOOKING_AVAILABILITY_PATTERN = re.compile(
    r"รับประกันคิวว่าง|รับรองคิวว่าง|คิวว่างแน่นอน|"
    r"(?:booking|appointment|walk[- ]?in|slot).{0,24}(?:guaranteed|available)|"
    r"(?:guaranteed|available).{0,24}(?:booking|appointment|walk[- ]?in|slot)",
    re.IGNORECASE,
)

LAB_STATUS_HINTS: dict[str, tuple[str, ...]] = {
    "high": ("high", "elevated", "above range", "สูง", "สูงกว่าช่วง"),
    "low": ("low", "below range", "ต่ำ", "ต่ำกว่าช่วง"),
    "within": ("normal", "within range", "in range", "อยู่ในช่วง", "ปกติ"),
}

BUSINESS_CONNECTOR_WORDS = {
    "a", "an", "and", "are", "as", "at", "baht", "between", "by", "can", "cost",
    "costs", "difference", "different", "for", "from", "in", "includes", "is", "item",
    "items", "of", "on", "or", "per", "price", "requested", "service", "the", "this",
    "thb", "to", "total", "with",
    "answer", "grounded",
}

BUSINESS_THAI_CONNECTOR_WORDS = {
    "ราคา", "บาท", "และ", "ต่างกัน", "เท่าไร",
}


def _normalized(text: str) -> str:
    return " ".join(text.casefold().split())


def _has_hint(text: str, hint: str) -> bool:
    normalized = _normalized(text)
    if not hint.isascii():
        return hint in normalized
    pattern = rf"(?<![a-z0-9]){re.escape(hint.casefold())}(?![a-z0-9])"
    return re.search(pattern, normalized) is not None


def _business_concepts(text: str) -> set[str]:
    return {
        concept
        for concept, hints in BUSINESS_CONCEPT_HINTS.items()
        if any(_has_hint(text, hint) for hint in hints)
    }


def _business_terms(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z]{3,}", text.casefold()))


def _thai_runs(text: str) -> tuple[str, ...]:
    return tuple(re.findall(r"[ก-๙]{3,}", text))


def _has_positive_localized_claim(text: str, hints: tuple[str, ...]) -> bool:
    normalized = _normalized(text)
    negative_markers = ("ไม่รับประกัน", "ไม่รับรอง", "ไม่มี", "ยังไม่มี", "ไม่ได้", "ห้ามให้", "ห้าม", "ไม่")
    positive_markers = ("มี", "รับประกัน", "จองได้", "โอนคืน", "คืนเงินได้")
    for hint in hints:
        start = normalized.find(hint)
        while start >= 0:
            prefix = normalized[max(0, start - 20) : start]
            cues: list[tuple[int, bool]] = []
            negative_spans: list[tuple[int, int]] = []
            for marker in negative_markers:
                marker_start = prefix.rfind(marker)
                if marker_start >= 0:
                    negative_spans.append((marker_start, marker_start + len(marker)))
                    cues.append((marker_start, False))
            for marker in positive_markers:
                marker_start = prefix.rfind(marker)
                if marker_start < 0:
                    continue
                if any(
                    negative_start <= marker_start <= negative_end + 2
                    for negative_start, negative_end in negative_spans
                ):
                    continue
                cues.append((marker_start, True))
            if not cues or max(cues, key=lambda cue: cue[0])[1]:
                return True
            start = normalized.find(hint, start + len(hint))
    return False


def _has_positive_thai_medication_advice(text: str) -> bool:
    normalized = _normalized(text)
    negative_markers = ("ไม่", "อย่า", "ห้าม", "หลีกเลี่ยง")
    for match in THAI_MEDICATION_ADVICE_PATTERN.finditer(normalized):
        prefix = normalized[max(0, match.start() - 12) : match.start()]
        if not any(marker in prefix for marker in negative_markers):
            return True
    return False


def _business_evidence_terms(items: tuple[Any, ...]) -> set[str]:
    values = []
    for item in items:
        values.append(item.record.content)
        values.append(json.dumps(item.record.data, ensure_ascii=False))
    return _business_terms(" ".join(values))


def _business_anchors(item: Any) -> tuple[str, ...]:
    data = item.record.data if isinstance(item.record.data, dict) else {}
    values = [data.get("service_id"), data.get("name_en"), data.get("name_th")]
    aliases = data.get("aliases", [])
    if isinstance(aliases, list):
        values.extend(aliases)
    return tuple(value for value in values if isinstance(value, str) and value.strip())


def _validate_business_numbers(candidate: str, query: str, items: tuple[Any, ...]) -> None:
    relevant = _business_relevant_items(query, items)
    if not relevant:
        requested = _business_concepts(query)
        relevant = (
            tuple(item for item in items if item.record.kind == "service")
            if "price" in requested
            else items
        )
    requested = _business_concepts(query)
    canonical_fact_numbers = set(NUMBER_PATTERN.findall(" ".join(item.record.content for item in relevant)))
    canonical_numbers = {
        str(int(amount)) if float(amount).is_integer() else str(amount)
        for item in relevant
        for amount in [_price_amount(item.record.data)]
        if amount is not None
    }
    derived = _derived_allowed_numbers(relevant) - canonical_numbers
    for sentence in re.split(r"[.!?\n]+", candidate):
        number_matches = list(NUMBER_PATTERN.finditer(sentence))
        if not number_matches:
            continue
        mentioned = tuple(
            item for item in relevant
            if any(_has_hint(sentence, anchor) for anchor in _business_anchors(item))
        )
        if not mentioned and len(relevant) == 1:
            mentioned = relevant
        for number_match in number_matches:
            number = number_match.group(0)
            prefix = sentence[:number_match.start()]
            anchor_positions = []
            for item in relevant:
                for anchor in _business_anchors(item):
                    match = re.search(
                        rf"(?<![a-z0-9]){re.escape(anchor.casefold())}(?![a-z0-9])",
                        prefix.casefold(),
                    )
                    if match:
                        anchor_positions.append((match.start(), item))
            nearest = max(anchor_positions, key=lambda value: value[0])[1] if anchor_positions else None
            direct = {
                str(int(amount)) if float(amount).is_integer() else str(amount)
                for item in ((nearest,) if nearest else mentioned)
                for amount in [_price_amount(item.record.data)]
                if amount is not None
            }
            if number in direct:
                continue
            if number in derived and len(mentioned) >= 2:
                continue
            if requested.intersection({"hours", "turnaround"}) and number in canonical_fact_numbers:
                continue
            raise OutputValidationError("provider_output_mismatched_business_number")


def _validate_business_claims(candidate: str, query: str, items: tuple[Any, ...]) -> None:
    requested = _business_concepts(query)
    evidence = " ".join(
        line.strip()
        for item in items
        for line in item.record.content.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )
    for hint in THAI_BUSINESS_CLAIM_HINTS:
        if _has_positive_localized_claim(candidate, (hint,)) and not _has_positive_localized_claim(evidence, (hint,)):
            raise OutputValidationError("provider_output_unsupported_business_claim")
    if _positive_booking_claim(candidate) and not _positive_booking_claim(evidence):
        raise OutputValidationError("provider_output_unsupported_booking_claim")
    for concept in _business_concepts(candidate):
        if concept not in requested:
            raise OutputValidationError("provider_output_unrequested_business_claim")
        if any(
            re.search(pattern, _normalized(evidence))
            for pattern in NEGATIVE_BUSINESS_FACTS.get(concept, ())
        ) and not any(_has_hint(candidate, hint) for hint in NEGATIVE_BUSINESS_FACTS.get(concept, ())):
            raise OutputValidationError("provider_output_contradicts_business_fact")


def _positive_booking_claim(text: str) -> bool:
    for sentence in re.split(r"[.!?\n]+", text):
        if not BOOKING_AVAILABILITY_PATTERN.search(sentence):
            continue
        normalized = _normalized(sentence)
        if "ไม่รับประกัน" in normalized or "ไม่รับรอง" in normalized:
            continue
        if re.search(r"\b(?:not|no|without)\b.{0,24}\b(?:guaranteed|available)\b", normalized):
            continue
        return True
    return False


def _hours_range_excerpt(evidence: str, day: str) -> str | None:
    day_index = HOURS_DAY_ORDER.index(day)
    for match in HOURS_DAY_RANGE_PATTERN.finditer(evidence):
        aliases = {alias.casefold(): key for key, values in HOURS_DAY_ALIASES.items() for alias in values}
        start_day = aliases[match.group("start").casefold()]
        end_day = aliases[match.group("end").casefold()]
        start_index = HOURS_DAY_ORDER.index(start_day)
        end_index = HOURS_DAY_ORDER.index(end_day)
        if start_index > end_index or not start_index <= day_index <= end_index:
            continue
        following = [position for position, _ in _evidence_day_positions(evidence) if position > match.end()]
        end = min(following) if following else None
        return evidence[match.start() : end]
    return None


def _evidence_day_positions(evidence: str) -> list[tuple[int, str]]:
    positions = []
    for day, aliases in HOURS_DAY_ALIASES.items():
        for alias in aliases:
            position = evidence.find(alias.casefold())
            if position >= 0:
                positions.append((position, day))
                break
    return sorted(positions)


def _validate_business_hours_claims(candidate: str, query: str, items: tuple[Any, ...]) -> None:
    if "hours" not in _business_concepts(query):
        return
    evidence = _normalized(" ".join(item.record.content for item in items))
    for match in UNSUPPORTED_HOURS_CLAIM_PATTERN.finditer(candidate):
        if not _has_hint(evidence, match.group(0)):
            raise OutputValidationError("provider_output_unsupported_hours_claim")
    evidence_day_positions = _evidence_day_positions(evidence)
    for sentence in re.split(r"[.!?\n]+", candidate):
        candidate_days = {
            day
            for day, aliases in HOURS_DAY_ALIASES.items()
            if any(_has_hint(sentence, alias) for alias in aliases)
        }
        if not candidate_days and "hours" not in _business_concepts(sentence):
            continue
        if not candidate_days and not any(
            _has_hint(sentence, hint) and _has_hint(evidence, hint) for hint in HOURS_EVIDENCE_HINTS
        ):
            raise OutputValidationError("provider_output_unsupported_hours_claim")
        for day in candidate_days:
            positions = [position for position, value in evidence_day_positions if value == day]
            if not positions:
                raise OutputValidationError("provider_output_unsupported_hours_claim")
            start = positions[-1]
            following = [position for position, _ in evidence_day_positions if position > start]
            excerpt = _hours_range_excerpt(evidence, day)
            if excerpt is None:
                excerpt = evidence[start : min(following) if following else None]
            candidate_numbers = set(NUMBER_PATTERN.findall(sentence))
            evidence_numbers = set(NUMBER_PATTERN.findall(excerpt))
            evidence_closed = any(_has_hint(excerpt, hint) for hint in ("closed", "ปิด"))
            candidate_open = any(_has_hint(sentence, hint) for hint in ("open", "เปิด"))
            candidate_closed = any(_has_hint(sentence, hint) for hint in ("closed", "ปิด"))
            if evidence_closed and (candidate_numbers or candidate_open):
                raise OutputValidationError("provider_output_unsupported_hours_claim")
            if candidate_closed and not evidence_closed:
                raise OutputValidationError("provider_output_unsupported_hours_claim")
            if candidate_numbers and not candidate_numbers.issubset(evidence_numbers):
                raise OutputValidationError("provider_output_unsupported_hours_claim")
            candidate_ranges = {
                (
                    int(match.group("start_hour")),
                    int(match.group("start_minute")),
                    int(match.group("end_hour")),
                    int(match.group("end_minute")),
                )
                for match in HOURS_TIME_RANGE_PATTERN.finditer(sentence)
            }
            evidence_ranges = {
                (
                    int(match.group("start_hour")),
                    int(match.group("start_minute")),
                    int(match.group("end_hour")),
                    int(match.group("end_minute")),
                )
                for match in HOURS_TIME_RANGE_PATTERN.finditer(excerpt)
            }
            if candidate_ranges and not candidate_ranges.issubset(evidence_ranges):
                raise OutputValidationError("provider_output_unsupported_hours_claim")


def _positive_status_present(text: str, hints: tuple[str, ...]) -> bool:
    normalized = _normalized(text)
    if re.search(r"\b(?:not|no|without|cannot|can't)\s+(?:be\s+)?(?:high|low|elevated|normal|within|in)\b", normalized):
        return False
    if any(phrase in normalized for phrase in ("ไม่สูง", "ไม่ต่ำ", "ไม่ปกติ", "ไม่อยู่ในช่วง")):
        return False
    return any(_has_hint(normalized, hint) for hint in hints)


def _validate_lab_claims(candidate: str, analysis: Any) -> None:
    values = tuple(getattr(analysis, "values", ()) or ())
    if not values:
        return
    sentences = tuple(part for part in re.split(r"[.!?\n]+", candidate) if part.strip())
    for value in values:
        marker = str(getattr(value, "marker", ""))
        if not marker:
            continue
        contexts = [sentence for sentence in sentences if _has_hint(sentence, marker)]
        if not contexts and len(values) == 1:
            contexts = list(sentences)
        if not contexts:
            continue
        flag = getattr(value, "flag", "unknown")
        forbidden = {
            "low": ("high", "within"),
            "high": ("low", "within"),
            "within": ("high", "low"),
            "unknown": ("high", "low", "within"),
        }.get(flag, ())
        if any(_positive_status_present(" ".join(contexts), LAB_STATUS_HINTS[name]) for name in forbidden):
            raise OutputValidationError("provider_output_contradicts_lab_status")


def _validate_source_attributions(candidate: str, allowed_sources: set[str]) -> None:
    allowed = {source.casefold() for source in allowed_sources}
    for sentence in re.split(r"[.!?\n]+", candidate):
        if not (SOURCE_CUE_PATTERN.search(sentence) or UNBRACKETED_SOURCE_CUE_PATTERN.search(sentence)):
            continue
        if SOURCE_NON_ATTRIBUTION_PATTERN.search(sentence):
            continue
        if not any(source in sentence.casefold() for source in allowed):
            raise OutputValidationError("provider_output_forged_citation")


def _validate_source_urls(candidate: str, items: tuple[Any, ...]) -> None:
    allowed = set()
    for item in items:
        data = item.record.data if isinstance(item.record.data, dict) else {}
        for key in ("source_url", "origin", "publication_url"):
            value = data.get(key)
            if isinstance(value, str):
                allowed.add(value.rstrip(".,;"))
    for url in URL_PATTERN.findall(candidate):
        if url.rstrip(".,;") not in allowed:
            raise OutputValidationError("provider_output_forged_source_url")


def _price_amount(data: dict[str, Any]) -> float | int | None:
    price = data.get("price")
    amount = price.get("amount") if isinstance(price, dict) else price
    return amount if isinstance(amount, (int, float)) and not isinstance(amount, bool) else None


def _derived_allowed_numbers(items: Iterable[Any]) -> set[str]:
    amounts = [
        amount
        for amount in (_price_amount(item.record.data) for item in items)
        if amount is not None
    ]
    allowed: set[str] = set()
    for index, amount in enumerate(amounts):
        allowed.add(str(int(amount)) if float(amount).is_integer() else str(amount))
        for other in amounts[index + 1 :]:
            for value in (amount + other, abs(amount - other)):
                allowed.add(str(int(value)) if float(value).is_integer() else str(value))
    if len(amounts) > 2:
        total = sum(amounts)
        allowed.add(str(int(total)) if float(total).is_integer() else str(total))
    return allowed


def _business_relevant_items(query: str, items: tuple[Any, ...]) -> tuple[Any, ...]:
    normalized_query = re.sub(r"\s+", "", query.casefold())
    relevant = []
    for item in items:
        data = item.record.data if isinstance(item.record.data, dict) else {}
        candidates = [data.get("service_id"), data.get("name_th"), data.get("name_en")]
        aliases = data.get("aliases", [])
        if isinstance(aliases, list):
            candidates.extend(aliases)
        if any(
            isinstance(candidate, str)
            and candidate.strip()
            and re.sub(r"\s+", "", candidate.casefold()) in normalized_query
            for candidate in candidates
        ):
            relevant.append(item)
    return tuple(relevant)


def _allowed_numbers(
    query: str,
    items: tuple[Any, ...],
    analysis: Any,
    intent: str,
    confirmed_extraction: dict[str, Any] | None,
) -> set[str]:
    # A business question may contain a requested or attacker-supplied price.
    # Only retrieved canonical records may authorize business numbers.
    if intent == "business":
        requested = _business_concepts(query)
        relevant_items = _business_relevant_items(query, items)
        if not relevant_items:
            if "price" in requested:
                service_items = tuple(item for item in items if item.record.kind == "service")
                if len(service_items) == 1:
                    relevant_items = service_items
            else:
                relevant_items = items
        if not relevant_items:
            return set()
        allowed = set(NUMBER_PATTERN.findall(" ".join(item.record.content for item in relevant_items)))
        allowed.update(_derived_allowed_numbers(relevant_items))
        return allowed
    allowed = set(NUMBER_PATTERN.findall(query))
    allowed.update(NUMBER_PATTERN.findall(" ".join(item.record.content for item in items)))
    allowed.update(_derived_allowed_numbers(items))
    if hasattr(analysis, "to_public_dict"):
        allowed.update(NUMBER_PATTERN.findall(json.dumps(analysis.to_public_dict(), ensure_ascii=False)))
    if intent == "lab" and confirmed_extraction:
        allowed.update(NUMBER_PATTERN.findall(json.dumps(confirmed_extraction, ensure_ascii=False)))
    return allowed


def _known_lab_units(analysis: Any, confirmed_extraction: dict[str, Any] | None) -> set[str]:
    units: set[str] = set()
    for value in tuple(getattr(analysis, "values", ()) or ()):
        unit = getattr(value, "unit", None)
        if isinstance(unit, str) and unit.strip():
            units.add(unit.casefold())
    if isinstance(confirmed_extraction, dict):
        for field in confirmed_extraction.get("fields", ()):
            if isinstance(field, dict):
                unit = field.get("unit")
                if isinstance(unit, str) and unit.strip():
                    units.add(unit.casefold())
    return units


def validate_provider_text(
    text: str,
    query: str,
    items: tuple[Any, ...],
    analysis: Any,
    intent: str,
    confirmed_extraction: dict[str, Any] | None = None,
) -> str:
    candidate = text.strip() if isinstance(text, str) else ""
    if not candidate or len(candidate) > settings.MAX_PROVIDER_OUTPUT_CHARS:
        raise OutputValidationError("provider_output_invalid")
    if UNSAFE_OUTPUT_PATTERN.search(SAFE_DIAGNOSIS_DISCLAIMER_PATTERN.sub(" ", candidate)):
        raise OutputValidationError("provider_output_unsafe")
    if (
        MEDICATION_CHANGE_PATTERN.search(candidate)
        or MEDICATION_ADVICE_PATTERN.search(candidate)
        or CLINICAL_TREATMENT_PATTERN.search(candidate)
        or _has_positive_thai_medication_advice(candidate)
    ):
        raise OutputValidationError("provider_output_medication_change")
    diagnosis_candidate = SAFE_DIAGNOSIS_DISCLAIMER_PATTERN.sub(" ", candidate)
    if (
        UNSUPPORTED_DIAGNOSIS_PATTERN.search(diagnosis_candidate)
        or HEDGED_DIAGNOSIS_PATTERN.search(diagnosis_candidate)
        or LAB_MARKER_DIAGNOSIS_PATTERN.search(diagnosis_candidate)
    ):
        raise OutputValidationError("provider_output_diagnosis")
    if UNAUTHORIZED_TRANSACTION_PATTERN.search(candidate):
        raise OutputValidationError("provider_output_unauthorized_transaction")
    allowed_numbers = _allowed_numbers(query, items, analysis, intent, confirmed_extraction)
    if not set(NUMBER_PATTERN.findall(candidate)).issubset(allowed_numbers):
        raise OutputValidationError("provider_output_ungrounded_number")
    if intent == "business":
        _validate_business_numbers(candidate, query, items)
        _validate_business_claims(candidate, query, items)
        _validate_business_hours_claims(candidate, query, items)
        evidence_text = " ".join(
            line.strip()
            for item in items
            for line in item.record.content.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
        evidence_thai_runs = set(_thai_runs(evidence_text))
        unsupported_thai_runs = set(_thai_runs(candidate)) - evidence_thai_runs - BUSINESS_THAI_CONNECTOR_WORDS
        if unsupported_thai_runs:
            raise OutputValidationError("provider_output_unsupported_business_claim")
        evidence_terms = _business_evidence_terms(items)
        for sentence in re.split(r"[.!?\n]+", candidate):
            terms = _business_terms(sentence)
            if not terms:
                continue
            unsupported = terms - evidence_terms - BUSINESS_CONNECTOR_WORDS
            if unsupported:
                raise OutputValidationError("provider_output_unsupported_business_claim")
            if (
                len(terms & evidence_terms) < 2
                and not NUMBER_PATTERN.search(sentence)
                and _business_concepts(sentence)
            ):
                raise OutputValidationError("provider_output_unsupported_business_claim")
    else:
        # Lab answers must not smuggle in a business fact merely because the
        # query was routed to the health-information path.
        if intent in {"lab", "mixed"} and LAB_BUSINESS_CLAIM_PATTERN.search(candidate):
            raise OutputValidationError("provider_output_unrequested_business_claim")
        _validate_business_claims(candidate, query, items)
    if intent in {"lab", "mixed"}:
        _validate_lab_claims(candidate, analysis)
    allowed_sources = {source.casefold() for item in items for source in item.record.source_ids}
    known_lab_units = _known_lab_units(analysis, confirmed_extraction)
    mentioned = {
        source.casefold()
        for pattern in (SOURCE_MARKER_PATTERN, SOURCE_ID_PATTERN, BRACKETED_SOURCE_PATTERN, SOURCE_ATTRIBUTION_PATTERN)
        for source in pattern.findall(candidate)
        if source.casefold() not in known_lab_units
    }
    if not mentioned.issubset(allowed_sources):
        raise OutputValidationError("provider_output_forged_citation")
    _validate_source_attributions(candidate, allowed_sources)
    _validate_source_urls(candidate, items)
    return candidate


def validate_answer_result(
    result: Any,
    query: str,
    items: tuple[Any, ...],
    analysis: Any,
    confirmed_extraction: dict[str, Any] | None = None,
) -> Any:
    """Re-check an answer at the route boundary before persistence/output."""
    if not isinstance(result.text, str) or len(result.text.strip()) > settings.MAX_PROVIDER_OUTPUT_CHARS + 500:
        raise OutputValidationError("answer_result_invalid")
    if result.status == "answered":
        body = result.text.split("\n\nSources:", 1)[0]
        validate_provider_text(body, query, items, analysis, result.intent, confirmed_extraction)
        allowed_citations = {
            (source.casefold(), item.record.record_id, item.record.chunk_id)
            for item in items
            for source in item.record.source_ids
        }
        if any(
            (
                str(getattr(citation, "source_id", "")).casefold(),
                str(getattr(citation, "record_id", "")),
                str(getattr(citation, "chunk_id", "")),
            )
            not in allowed_citations
            for citation in result.citations
        ):
            raise OutputValidationError("citation_not_retrieved")
    return result
