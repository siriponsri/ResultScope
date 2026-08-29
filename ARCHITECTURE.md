# ResultScope architecture

## Product invariant

The LLM is **not** the policy engine.

```text
User input
  ↓
Symbolic lab scope gate
  ├─ out of scope → deterministic product response (no LLM call)
  └─ in scope
       ↓
Deterministic marker/value/range parser
       ↓
Session context + symbolic facts
       ↓
OpenAI-compatible LLM
       ↓
Grounded educational explanation
```

## Why neuro-symbolic here

The symbolic layer handles things that should be explicit and testable:

- whether the product should answer at all;
- known laboratory vocabulary and panels;
- marker/value/reference-range-like syntax;
- high/low/within flags computed only from the user-supplied reference interval;
- whether an ambiguous follow-up is attached to existing lab context.

The neural layer handles things it is good at:

- plain-language explanation;
- contextual relationships among supplied values;
- uncertainty-aware wording;
- generating useful follow-up questions.

## Storage strategy

```text
Local
  → SQLite (default)

Vercel + no external store
  → memory (works, non-durable)

Vercel + Upstash credentials
  → Upstash Redis REST + TTL
```

This is a starter abstraction, not a compliance architecture.

## Business-scale evolution

V0.1
- manual paste/text input
- symbolic scope gate
- deterministic marker/value/unit/range parser
- structured LLM response
- temporary session history

V0.5
- authenticated users
- richer report parser + normalized marker ontology
- report schema + trend model
- organization-specific ranges
- audit/provenance events

V1
- PDF/image ingestion with validation
- longitudinal patient/lab timeline
- white-label organization console
- policy/version registry
- human escalation / clinician review
- analytics and re-engagement workflows

## Non-goals for the coursework branch

- diagnosis
- medication recommendations
- medical-device claims
- autonomous emergency triage
- storing identifiable patient records
- OCR of arbitrary clinical documents
- guideline RAG without a governed source set
