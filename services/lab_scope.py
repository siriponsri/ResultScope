from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ScopeDecision:
    allowed: bool
    reason: str
    matched_terms: tuple[str, ...] = ()
    category: str = "unknown"


# Intentionally explicit: this is the symbolic half of the prototype.
LAB_TERMS: dict[str, tuple[str, ...]] = {
    "hematology": (
        "cbc", "complete blood count", "hemoglobin", "haemoglobin", "hb", "hct",
        "hematocrit", "rbc", "wbc", "platelet", "plt", "mcv", "mch", "mchc", "rdw",
        "reticulocyte", "neutrophil", "lymphocyte", "monocyte", "eosinophil", "basophil",
        "เม็ดเลือด", "ฮีโมโกลบิน", "เกล็ดเลือด",
    ),
    "kidney": (
        "creatinine", "egfr", "bun", "urea", "uric acid", "microalbumin", "acr",
        "albumin creatinine ratio", "ค่าไต",
    ),
    "liver": (
        "ast", "alt", "alp", "ggt", "bilirubin", "albumin", "total protein",
        "liver function", "lft", "ค่าตับ",
    ),
    "glucose": (
        "glucose", "fbs", "fasting blood sugar", "hba1c", "a1c", "ogtt", "น้ำตาล",
    ),
    "lipid": (
        "cholesterol", "ldl", "hdl", "triglyceride", "non-hdl", "lipid profile", "ไขมัน",
    ),
    "electrolyte": (
        "sodium", "potassium", "chloride", "bicarbonate", "calcium", "magnesium",
        "phosphate", "electrolyte", "anion gap", "โซเดียม", "โพแทสเซียม",
    ),
    "thyroid": (
        "tsh", "ft4", "free t4", "ft3", "free t3", "anti-tpo", "thyroglobulin",
        "thyroid panel", "thyroid test", "ผลไทรอยด์",
    ),
    "coagulation": (
        "pt", "inr", "aptt", "fibrinogen", "d-dimer", "coagulation", "การแข็งตัวของเลือด",
    ),
    "urinalysis": (
        "urinalysis", "urine", "specific gravity", "nitrite", "leukocyte esterase",
        "protein urine", "ketone", "ปัสสาวะ", "ผลปัสสาวะ",
    ),
    "inflammation": (
        "crp", "hs-crp", "esr", "procalcitonin", "inflammation", "การอักเสบ",
    ),
    "iron_vitamins": (
        "ferritin", "serum iron", "tibc", "transferrin", "vitamin b12", "folate",
        "vitamin d", "25-oh", "ธาตุเหล็ก", "เฟอร์ริติน", "วิตามิน",
    ),
    "cardiac": (
        "troponin", "ck-mb", "bnp", "nt-probnp", "cardiac marker",
    ),
    "acid_base": (
        "abg", "vbg", "ph", "pco2", "po2", "hco3", "base excess", "blood gas", "กรดด่าง",
    ),
    "hormone": (
        "cortisol", "testosterone", "estradiol", "lh", "fsh", "prolactin", "insulin",
        "hormone panel", "ผลฮอร์โมน",
    ),
    "microbiology": (
        "culture", "sensitivity", "susceptibility", "mic", "gram stain", "pcr", "antigen",
        "antibody", "serology", "hiv", "hbsag", "anti-hcv", "dengue", "เพาะเชื้อ",
        "ความไวต่อยา", "จุลชีววิทยา", "ผลเพาะเชื้อ",
    ),
    "general_lab": (
        "lab result", "lab results", "laboratory result", "blood test", "test result",
        "reference range", "normal range", "ผลแลป", "ผลแล็บ", "ผลตรวจเลือด", "ผลตรวจ",
        "ค่าแลป", "ค่าแล็บ", "ช่วงอ้างอิง", "ค่าปกติ",
    ),
}

FOLLOW_UP_HINTS = (
    "แล้ว", "อันนี้", "ค่านี้", "ค่าไหน", "หมายความว่า", "แปลว่า", "สูงไหม", "ต่ำไหม",
    "อันตรายไหม", "ต้องกังวลไหม", "เกี่ยวกันไหม", "ควรถาม", "ควรตรวจ", "ต่อไหม",
    "why", "what does", "is this high", "is this low", "should i worry", "what next",
    "tell me more", "explain more", "how about this",
)

GREETING_PATTERNS = (
    "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
    "สวัสดี", "สวัสดีครับ", "สวัสดีค่ะ",
)
HELP_PATTERNS = (
    "help", "what can you do", "how does this work", "what do you do",
    "ช่วยอะไรได้บ้าง", "ใช้งานอย่างไร",
)
CLOSING_PATTERNS = (
    "thanks", "thank you", "thankyou", "bye", "goodbye", "see you",
    "ขอบคุณ", "ขอบคุณครับ", "ขอบคุณค่ะ", "ลาก่อน",
)
AMBIGUOUS_PATTERNS = (
    "is this high", "is this low", "is this okay", "what does this mean",
    "what does it mean", "can you explain this", "help me understand",
    "ผลนี้", "ค่านี้", "สูงไหม", "ต่ำไหม", "แปลว่าอะไร",
)

# Recognize value-like lab syntax even when marker vocabulary is uncommon.
VALUE_PATTERN = re.compile(
    r"(?:\b[A-Za-z][A-Za-z0-9+\-]{1,15}\s*[:=]\s*-?\d+(?:\.\d+)?\b)"
    r"|(?:\b[A-Za-z][A-Za-z0-9+\-]{1,15}\s+-?\d+(?:\.\d+)?\s*"
    r"(?:mg/dl|mg/l|g/dl|g/l|mmol/l|umol/l|µmol/l|u/l|iu/l|ng/ml|pg/ml|%|10\^?\d+/l|fl|pg|miu/l|ml/min(?:/1\.73m²)?)\b)",
    flags=re.IGNORECASE,
)
RANGE_PATTERN = re.compile(r"\b\d+(?:\.\d+)?\s*[-–]\s*\d+(?:\.\d+)?\b")


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _term_present(normalized: str, term: str) -> bool:
    # Short English abbreviations such as pH/PT/Hb must match as tokens; plain
    # substring matching would incorrectly classify words like "python" as a lab query.
    if all(ord(ch) < 128 for ch in term):
        pattern = rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])"
        return re.search(pattern, normalized, flags=re.IGNORECASE) is not None
    return term in normalized


def _find_terms(text: str) -> tuple[str, tuple[str, ...]]:
    normalized = _normalize(text)
    matches: list[str] = []
    first_category = "unknown"
    for category, terms in LAB_TERMS.items():
        for term in terms:
            if _term_present(normalized, term):
                matches.append(term)
                if first_category == "unknown":
                    first_category = category
    return first_category, tuple(dict.fromkeys(matches))


def history_has_lab_context(history: list[dict[str, str]]) -> bool:
    for item in history[-6:]:
        if item.get("role") != "user":
            continue
        category, matches = _find_terms(item.get("content", ""))
        if matches or VALUE_PATTERN.search(item.get("content", "")):
            return True
    return False


def _matches_simple_intent(normalized: str, patterns: tuple[str, ...]) -> bool:
    stripped = normalized.strip(".!?,;: ")
    return any(stripped == pattern or stripped.startswith(f"{pattern} ") for pattern in patterns)


def classify_lab_scope(message: str, history: list[dict[str, str]] | None = None) -> ScopeDecision:
    history = history or []
    normalized = _normalize(message)
    if not normalized:
        return ScopeDecision(False, "empty_message")

    category, matches = _find_terms(normalized)
    if matches:
        return ScopeDecision(True, "lab_term", matches, category)

    if VALUE_PATTERN.search(message) and (RANGE_PATTERN.search(message) or len(message) <= 500):
        return ScopeDecision(True, "lab_value_pattern", (), "unclassified_lab")

    if history_has_lab_context(history) and any(hint in normalized for hint in FOLLOW_UP_HINTS):
        return ScopeDecision(True, "lab_follow_up", (), "follow_up")

    if _matches_simple_intent(normalized, GREETING_PATTERNS):
        return ScopeDecision(False, "greeting", (), "local")

    if _matches_simple_intent(normalized, HELP_PATTERNS):
        return ScopeDecision(False, "help", (), "local")

    if _matches_simple_intent(normalized, CLOSING_PATTERNS):
        return ScopeDecision(False, "closing", (), "local")

    if any(pattern in normalized for pattern in AMBIGUOUS_PATTERNS):
        return ScopeDecision(False, "ambiguous", (), "needs_lab_detail")

    return ScopeDecision(False, "outside_lab_scope")


OUT_OF_SCOPE_MESSAGE_TH = (
    "ResultScope รับเฉพาะคำถามเกี่ยวกับผลตรวจทางห้องปฏิบัติการเท่านั้นครับ\n\n"
    "ลองส่งค่าแลปพร้อมหน่วยและช่วงอ้างอิง เช่น `Hb 10.8 g/dL (12–16)` "
    "หรือถามว่า `HbA1c 6.1% หมายความว่าอย่างไร`"
)

SCOPE_SUGGESTIONS = [
    "ช่วยอธิบาย CBC ชุดนี้",
    "ค่าไต Creatinine/eGFR ดูอย่างไร",
    "AST/ALT สูงควรอ่านร่วมกับค่าอะไร",
    "HbA1c คืออะไร",
]


def local_scope_reply(decision: ScopeDecision, message: str) -> str:
    """Return deterministic product copy for requests that should not reach the LLM."""
    thai = any("\u0e00" <= char <= "\u0e7f" for char in message)
    if thai:
        replies = {
            "greeting": "สวัสดีครับ ผมช่วยอธิบายผลตรวจทางห้องปฏิบัติการได้ ส่งชื่อการตรวจ ค่า หน่วย และช่วงอ้างอิงมาได้เลย",
            "help": "ResultScope ช่วยอ่านผลตรวจทางห้องปฏิบัติการที่คุณส่งมา โดยแสดงค่าที่แยกได้และอธิบายเชิงการศึกษา ใช้ได้ดีกับชื่อการตรวจ ค่า หน่วย และช่วงอ้างอิงจากรายงานของคุณ",
            "closing": "ยินดีครับ หากมีผลตรวจที่อยากอ่านเพิ่มเติม ส่งมาได้ทุกเมื่อ",
            "ambiguous": "ส่งชื่อการตรวจ ค่าที่ได้ หน่วย และช่วงอ้างอิงจากรายงานมาได้เลย แล้วผมจะช่วยอธิบายให้เป็นขั้นตอน",
            "empty_message": "ส่งผลตรวจหรือคำถามเกี่ยวกับการตรวจทางห้องปฏิบัติการมาได้เลย",
        }
    else:
        replies = {
            "greeting": "Hello. I can help you understand laboratory results in clear, practical language. Share the test name, value, unit, and reference range when you have them.",
            "help": "ResultScope explains laboratory results you provide. It can organize your values, compare them with the reference ranges from your report, and suggest useful questions to ask next. It does not diagnose or prescribe.",
            "closing": "You are welcome. Send any laboratory result when you would like to review it.",
            "ambiguous": "Please share the test name, result, unit, and reference range from your report. That gives me enough context to explain the value carefully.",
            "empty_message": "Share a laboratory result or a question about a test to begin.",
        }

    return replies.get(
        decision.reason,
        "ResultScope is focused on laboratory results. Share a test name, value, unit, and reference range, or ask about a lab panel such as CBC, kidney, liver, HbA1c, lipid, or thyroid testing.",
    )
