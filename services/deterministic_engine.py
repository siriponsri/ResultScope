from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from services.deterministic_rules import RULEBOOK_VERSION, RULES_BY_ID, public_rulebook
from services.lab_parser import ParsedLabValue, extract_lab_values
from services.lab_scope import ScopeDecision, classify_lab_scope


@dataclass(frozen=True)
class RuleTraceEntry:
    rule_id: str
    outcome: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        rule = RULES_BY_ID[self.rule_id]
        return {
            **asdict(self),
            "group": rule.group,
            "title": rule.title,
            "effect": rule.effect,
        }


@dataclass(frozen=True)
class DeterministicAnalysis:
    scope: ScopeDecision
    values: tuple[ParsedLabValue, ...]
    trace: tuple[RuleTraceEntry, ...]

    @property
    def flagged_count(self) -> int:
        return sum(item.flag in {"low", "high"} for item in self.values)

    def to_public_dict(self) -> dict:
        return {
            "rulebook_version": RULEBOOK_VERSION,
            "category": self.scope.category,
            "scope_reason": self.scope.reason,
            "count": len(self.values),
            "flagged_count": self.flagged_count,
            "values": [item.to_dict() for item in self.values],
            "trace": [item.to_dict() for item in self.trace],
            "contract": {
                "range_authority": "user_supplied_only",
                "unknown_means": "not deterministically flaggable",
                "llm_role": "integrated educational explanation",
            },
        }


def _scope_rule(decision: ScopeDecision) -> str:
    return {
        "lab_term": "SCOPE-001",
        "lab_value_pattern": "SCOPE-002",
        "lab_follow_up": "SCOPE-003",
    }.get(decision.reason, "SCOPE-004")


def _confirmed_values(extraction: dict | None) -> tuple[ParsedLabValue, ...]:
    """Convert user-confirmed OCR fields into the same server-owned value model."""
    values: list[ParsedLabValue] = []
    for field in (extraction or {}).get("fields", ()):
        if not isinstance(field, dict):
            continue
        numeric_text = field.get("numeric_value") or field.get("raw_value")
        if not isinstance(numeric_text, str):
            continue
        try:
            value = float(numeric_text.replace(",", "."))
        except ValueError:
            continue
        low_text = field.get("reference_low")
        high_text = field.get("reference_high")
        try:
            low = float(str(low_text).replace(",", ".")) if low_text is not None else None
            high = float(str(high_text).replace(",", ".")) if high_text is not None else None
        except ValueError:
            low = high = None
        range_state = (
            "missing"
            if low is None or high is None
            else "invalid"
            if low > high
            else "valid"
        )
        flag = field.get("flag") if field.get("flag") in {"low", "high", "within", "unknown"} else "unknown"
        marker = field.get("marker")
        if isinstance(marker, str) and marker.strip():
            values.append(ParsedLabValue(marker, value, field.get("unit"), low, high, flag, range_state))
    return tuple(values)


def analyze_message(
    message: str,
    history: list[dict[str, str]] | None = None,
    confirmed_extraction: dict | None = None,
) -> DeterministicAnalysis:
    confirmed = _confirmed_values(confirmed_extraction)
    marker_context = " ".join(
        str(field.get("marker", ""))
        for field in (confirmed_extraction or {}).get("fields", ())
        if isinstance(field, dict)
    )
    scoped_message = f"{message} {marker_context}".strip()
    decision = classify_lab_scope(scoped_message, history or [])
    trace: list[RuleTraceEntry] = [
        RuleTraceEntry(
            _scope_rule(decision),
            "allow" if decision.allowed else "local_response",
            f"scope reason={decision.reason}; category={decision.category}",
        )
    ]
    if not decision.allowed:
        return DeterministicAnalysis(decision, (), tuple(trace))

    values = confirmed or tuple(extract_lab_values(message))
    trace.append(
        RuleTraceEntry(
            "PARSE-001",
            "matched" if values else "no_match",
            f"Extracted {len(values)} explicit marker-value item(s) in message order."
            + (" Values came from user-confirmed image fields." if confirmed else ""),
        )
    )

    range_rule_ids: set[str] = set()
    for item in values:
        if item.range_state == "invalid":
            range_rule_ids.add("RANGE-002")
        elif item.flag == "unknown":
            range_rule_ids.add("RANGE-001")
        elif item.flag == "low":
            range_rule_ids.add("RANGE-003")
        elif item.flag == "high":
            range_rule_ids.add("RANGE-004")
        elif item.flag == "within":
            range_rule_ids.add("RANGE-005")

    for rule_id in sorted(range_rule_ids):
        affected = [item.marker for item in values if _rule_applies_to_value(rule_id, item)]
        trace.append(
            RuleTraceEntry(rule_id, "applied", f"Applied to: {', '.join(affected)}")
        )

    trace.extend(
        (
            RuleTraceEntry("GROUND-001", "enforced", "Extracted fields are immutable LLM inputs."),
            RuleTraceEntry("GROUND-002", "enforced", "Unknown flags cannot be upgraded by the LLM."),
            RuleTraceEntry("SAFETY-001", "enforced", "Educational response boundary attached."),
            RuleTraceEntry("OUTPUT-001", "enforced", "One integrated explanation requested."),
        )
    )
    return DeterministicAnalysis(decision, values, tuple(trace))


def _rule_applies_to_value(rule_id: str, item: ParsedLabValue) -> bool:
    return {
        "RANGE-001": item.range_state == "missing",
        "RANGE-002": item.range_state == "invalid",
        "RANGE-003": item.flag == "low",
        "RANGE-004": item.flag == "high",
        "RANGE-005": item.flag == "within",
    }.get(rule_id, False)


def build_rule_grounding(analysis: DeterministicAnalysis) -> str:
    """Render the exact pre-answer contract sent to every allowed LLM request."""
    applied_rules = []
    for entry in analysis.trace:
        rule = RULES_BY_ID[entry.rule_id]
        applied_rules.append(
            {
                "rule_id": rule.rule_id,
                "title": rule.title,
                "condition": rule.condition,
                "effect": rule.effect,
                "runtime_outcome": entry.outcome,
                "runtime_detail": entry.detail,
            }
        )

    facts = [item.to_dict() for item in analysis.values]
    return (
        "# AUTHORITATIVE DETERMINISTIC PRE-ANSWER CONTRACT\n"
        f"Rulebook version: {RULEBOOK_VERSION}\n\n"
        "You MUST read and follow this contract before answering the user. "
        "It is the tool-equivalent output of ResultScope's deterministic engine.\n\n"
        "## Runtime facts (immutable)\n"
        f"```json\n{json.dumps(facts, ensure_ascii=False, indent=2)}\n```\n\n"
        "## Rules applied before this call\n"
        f"```json\n{json.dumps(applied_rules, ensure_ascii=False, indent=2)}\n```\n\n"
        "## Response obligations\n"
        "1. Integrate the verified facts into one coherent educational explanation; do not produce a second competing verdict.\n"
        "2. Preserve every numeric value, unit, supplied interval, range_state, and deterministic flag exactly.\n"
        "3. If flag=unknown, say the report cannot be deterministically classified without a valid supplied range. General educational context must be labelled as general, not as this report's status.\n"
        "4. Separate direct observations from contextual possibilities. Do not expose rule IDs unless the user asks how the engine reasoned.\n"
        "5. Do not diagnose, prescribe, recommend dose changes, or invent clinical thresholds.\n"
    )


def get_rulebook() -> dict:
    return public_rulebook()
