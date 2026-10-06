# ResultScope deterministic rulebook

Documentation revision: **2026-10-04**. The runtime rule version remains owned by `services/deterministic_rules.py`.

## Purpose

ResultScope uses a deterministic pre-answer engine before every allowed LLM call. The engine owns decisions that must be explicit, reproducible, and testable. The LLM owns plain-language education and contextual explanation. It is never allowed to overwrite deterministic facts.

Runtime source of truth: `services/deterministic_rules.py`  
Runtime orchestration: `services/deterministic_engine.py`  
Inspectable endpoint: `GET /api/v1/rules`

## Execution order

1. **Scope** — decide whether the request belongs to laboratory-result education.
2. **Parse** — extract only literal marker, value, unit, and bracketed reference interval fields.
3. **Validate** — distinguish valid, missing, and reversed reference intervals.
4. **Compare** — compute low, high, or within only against a valid interval supplied in the current message.
5. **Lock facts** — serialize the values, statuses, and applied rule trace into an authoritative pre-answer contract.
6. **Explain** — place that contract before conversation history and the current user message in the LLM request.
7. **Render once** — combine the interactive deterministic view and streamed narrative into one analysis object. The detailed rule trace stays inside an optional disclosure.

## Rule groups

| Group | IDs | Deterministic responsibility |
|---|---|---|
| Scope | `SCOPE-001`–`004` | Lab vocabulary, uncommon marker syntax, context-bound follow-ups, and local refusal |
| Parsing | `PARSE-001`–`002` | Literal extraction and maximum result count |
| Range | `RANGE-001`–`005` | Missing/invalid interval handling and inclusive arithmetic comparison |
| Grounding | `GROUND-001`–`002` | Immutable facts and the rule that unknown must remain unknown |
| Safety | `SAFETY-001` | Educational-only boundary; no diagnosis or treatment direction |
| Output | `OUTPUT-001` | One integrated answer rather than competing symbolic and AI outputs |

## Range truth table

| Input state | Condition | Output |
|---|---|---|
| Missing interval | Either lower or upper bound is absent | `flag=unknown`, `range_state=missing` |
| Reversed interval | lower > upper | `flag=unknown`, `range_state=invalid` |
| Below | value < lower | `flag=low`, `range_state=valid` |
| Inside | lower ≤ value ≤ upper | `flag=within`, `range_state=valid` |
| Above | value > upper | `flag=high`, `range_state=valid` |

Boundary equality is deliberately inclusive. No population-level “normal” threshold is silently substituted for the reporting laboratory's interval.

## LLM obligations

The generated pre-answer contract contains the runtime facts, applicable rules, and these obligations:

- preserve every extracted number, unit, interval, range state, and flag exactly;
- integrate verified observations into one explanation;
- label general educational knowledge as general context;
- never convert `unknown` into a deterministic high, low, or normal status;
- separate direct observations from possible interpretations;
- never diagnose, prescribe, recommend dose changes, or invent emergency thresholds;
- keep rule IDs out of the prose unless the user explicitly asks how the engine reasoned.

## UI contract

Each analysis is rendered as one interactive result canvas:

- select a value to update its reference-range visualization;
- read the validated explanation in the same object (the SSE path validates the completed answer before displaying its deltas);
- open **Calculation details** to inspect the exact applied rule trace;
- follow-up questions create a new context-linked analysis object without pretending that a new numeric result was parsed.

The visual layer never computes a status. It only renders the server-issued deterministic analysis metadata.
