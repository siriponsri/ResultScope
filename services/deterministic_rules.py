from __future__ import annotations

from dataclasses import asdict, dataclass


RULEBOOK_VERSION = "2026.08"


@dataclass(frozen=True)
class RuleDefinition:
    rule_id: str
    group: str
    title: str
    condition: str
    effect: str
    rationale: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


RULES: tuple[RuleDefinition, ...] = (
    RuleDefinition(
        "SCOPE-001",
        "scope",
        "Recognized laboratory vocabulary",
        "The message contains a token from the explicit laboratory ontology.",
        "Allow the request into the laboratory workflow and record its first matched category.",
        "The model never decides the product boundary on its own.",
    ),
    RuleDefinition(
        "SCOPE-002",
        "scope",
        "Compact marker-value syntax",
        "The message contains a conservative marker/value pattern and is short or includes a numeric range.",
        "Allow an uncommon laboratory marker without requiring it to exist in the ontology.",
        "This supports real reports while limiting ordinary prose false positives.",
    ),
    RuleDefinition(
        "SCOPE-003",
        "scope",
        "Context-bound follow-up",
        "Recent user history contains laboratory context and the message contains an explicit follow-up cue.",
        "Attach the message to the existing laboratory analysis.",
        "Ambiguous follow-ups are safe only when a laboratory antecedent exists.",
    ),
    RuleDefinition(
        "SCOPE-004",
        "scope",
        "Local intent or out-of-scope refusal",
        "The message is empty, conversational-only, ambiguous without context, or outside laboratory results.",
        "Return a deterministic local response and do not invoke the LLM.",
        "Unrelated questions must not turn ResultScope into a general medical chatbot.",
    ),
    RuleDefinition(
        "PARSE-001",
        "parsing",
        "Explicit marker and numeric value",
        "A marker is followed by a numeric value, with an optional unit and optional bracketed low-high interval.",
        "Extract only the literal fields present in the user's message.",
        "The parser must not infer a missing unit, range, demographic, specimen, or fasting state.",
    ),
    RuleDefinition(
        "PARSE-002",
        "parsing",
        "Bounded extraction",
        "The message contains more than the configured maximum of parseable values.",
        "Stop after 30 values and preserve message order.",
        "A hard bound keeps the prototype predictable and prevents accidental report-scale overreach.",
    ),
    RuleDefinition(
        "RANGE-001",
        "range",
        "Missing supplied reference interval",
        "No paired low and high reference values were explicitly supplied for a result.",
        "Set deterministic status to unknown.",
        "A familiar population threshold is not a substitute for the reporting laboratory's interval.",
    ),
    RuleDefinition(
        "RANGE-002",
        "range",
        "Invalid supplied reference interval",
        "The supplied lower bound is greater than the supplied upper bound.",
        "Set deterministic status to unknown and mark the interval invalid.",
        "A malformed interval cannot safely support high, low, or within classification.",
    ),
    RuleDefinition(
        "RANGE-003",
        "range",
        "Below supplied interval",
        "The value is strictly lower than a valid user-supplied lower bound.",
        "Set deterministic status to low.",
        "The comparison is arithmetic and uses only the explicit interval.",
    ),
    RuleDefinition(
        "RANGE-004",
        "range",
        "Above supplied interval",
        "The value is strictly greater than a valid user-supplied upper bound.",
        "Set deterministic status to high.",
        "The comparison is arithmetic and uses only the explicit interval.",
    ),
    RuleDefinition(
        "RANGE-005",
        "range",
        "Inside supplied interval",
        "The value is greater than or equal to the lower bound and less than or equal to the upper bound.",
        "Set deterministic status to within.",
        "Boundary equality is treated as inside the supplied interval.",
    ),
    RuleDefinition(
        "GROUND-001",
        "grounding",
        "Immutable extracted facts",
        "The deterministic engine emits marker, value, unit, interval, and status fields.",
        "Require the LLM to preserve those fields exactly and integrate them into one explanation.",
        "Narrative fluency must not overwrite deterministic observations.",
    ),
    RuleDefinition(
        "GROUND-002",
        "grounding",
        "Unknown remains unknown",
        "A result has no valid user-supplied reference interval.",
        "The LLM may give general education but must not present high, low, or normal as a deterministic finding.",
        "This separates contextual medical knowledge from report-grounded classification.",
    ),
    RuleDefinition(
        "SAFETY-001",
        "safety",
        "Educational interpretation only",
        "Any allowed laboratory request reaches the explanation layer.",
        "Prohibit diagnosis, prescribing, dose changes, and treatment plans.",
        "ResultScope is an educational prototype, not a clinical decision system.",
    ),
    RuleDefinition(
        "OUTPUT-001",
        "output",
        "Single integrated answer",
        "The LLM receives the rule trace before the user message.",
        "Return one coherent explanation that incorporates verified facts; keep internal rule details in a disclosure view.",
        "Users should not reconcile a symbolic answer with a separate AI answer.",
    ),
)

RULES_BY_ID = {rule.rule_id: rule for rule in RULES}


def public_rulebook() -> dict:
    return {
        "name": "ResultScope deterministic rulebook",
        "version": RULEBOOK_VERSION,
        "principles": [
            "The deterministic engine controls scope, extraction, and arithmetic range flags.",
            "Only a reference interval supplied in the current user message can produce low/high/within.",
            "The LLM receives applicable rules and facts before it writes the explanation.",
            "The interface presents one integrated answer with an inspectable rule trace.",
        ],
        "rules": [rule.to_dict() for rule in RULES],
    }
