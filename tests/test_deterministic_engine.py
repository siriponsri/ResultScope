from services.deterministic_engine import (
    analyze_message,
    build_rule_grounding,
    get_rulebook,
)
from services.llm_client import _build_messages


def test_engine_emits_range_rules_and_grounding_contract():
    analysis = analyze_message("Hb 10.8 g/dL (12-16), MCV 90 fL (80-100), LDL 162 mg/dL")
    ids = {entry.rule_id for entry in analysis.trace}
    assert {"RANGE-001", "RANGE-003", "RANGE-005", "GROUND-001", "OUTPUT-001"} <= ids
    assert analysis.flagged_count == 1

    grounding = build_rule_grounding(analysis)
    assert "AUTHORITATIVE DETERMINISTIC PRE-ANSWER CONTRACT" in grounding
    assert '"marker": "Hb"' in grounding
    assert "Unknown flags cannot be upgraded" in grounding


def test_engine_blocked_intent_never_builds_lab_values():
    analysis = analyze_message("ช่วยเขียน Python ให้หน่อย")
    assert analysis.scope.allowed is False
    assert analysis.values == ()
    assert [entry.rule_id for entry in analysis.trace] == ["SCOPE-004"]


def test_confirmed_extraction_uses_the_same_deterministic_value_path():
    analysis = analyze_message(
        "ช่วยอธิบายค่าจากภาพ",
        confirmed_extraction={
            "fields": [
                {
                    "marker": "Hb",
                    "numeric_value": "10.8",
                    "raw_value": "10.8",
                    "unit": "g/dL",
                    "reference_low": "12",
                    "reference_high": "16",
                    "flag": "low",
                }
            ]
        },
    )
    assert analysis.scope.allowed is True
    assert len(analysis.values) == 1
    assert analysis.values[0].marker == "Hb"
    assert analysis.values[0].flag == "low"
    assert analysis.values[0].range_state == "valid"


def test_rulebook_is_versioned_and_inspectable():
    rulebook = get_rulebook()
    assert rulebook["version"] == "2026.08"
    assert len(rulebook["rules"]) >= 15
    assert {rule["group"] for rule in rulebook["rules"]} >= {
        "scope",
        "parsing",
        "range",
        "grounding",
        "safety",
        "output",
    }


def test_llm_message_order_places_rule_output_before_history_and_user():
    messages = _build_messages(
        [{"role": "user", "content": "prior lab context"}],
        "current question",
        "DETERMINISTIC CONTRACT",
    )
    assert messages[0]["role"] == "system"
    assert messages[1] == {"role": "system", "content": "DETERMINISTIC CONTRACT"}
    assert messages[-2] == {"role": "user", "content": "prior lab context"}
    assert messages[-1] == {"role": "user", "content": "current question"}
