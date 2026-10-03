# ResultScope architecture

## Product invariant

The LLM is **not** the policy engine.

```text
User input
  ↓
Versioned deterministic engine
  ├─ scope denied → local product response (no LLM call)
  └─ scope allowed
       ↓
literal parser → range validation → arithmetic flags → applied-rule trace
       ↓
authoritative pre-answer contract (facts + rules + safety obligations)
       ↓
OpenAI-compatible LLM reads contract before history and current message
       ↓
one integrated interactive analysis surface
  ├─ selectable values + supplied-range visualization
  ├─ grounded educational narrative
  └─ progressively disclosed rule trace
```

## Current local extension boundary (Phase 4A/4B)

The optional `PUBLIC_REFERENCE_ENABLED` path adds a server-owned adapter for
the pinned `addons/resultscope_evidence_v1` package. Its numeric hospital
records use `public_reference`; its WHO educational notes use the separate
`open_guideline` namespace. Neither namespace is merged into the approved
business release corpus or used to select a patient-specific interval.

```text
scope gate
  ↓
public-reference adapter (offline hash-checked corpus)
  ├─ no hit/corrupt package → clear abstention, no provider call
  └─ matched records → untrusted external context + citation allowlist
                              ↓
                     existing output validation → provider → sync/SSE metadata
```

The extension's tree is deterministic metadata/alias-guided hierarchical
retrieval. It is not embedding retrieval, RAG infrastructure, or a learned
clinical decision tree. Source IDs, URLs, PDF pages, hashes, versions,
licenses, and release flags remain server-resolved at the answer boundary.

## Current local intake boundary (Phase 3/5)

The first screen is the real intake surface: typed result/question, JPEG/PNG
upload, server-side Vision extraction when explicitly enabled, editable OCR
fields, confirmation, then chat. Image bytes and extracted fields remain
untrusted user data; confirmation is session-bound and revisioned. The browser
does not calculate flags, authorize citations, or expose provider keys.

## Why neuro-symbolic here

The symbolic layer handles things that should be explicit and testable:

- whether the product should answer at all;
- known laboratory vocabulary and panels;
- marker/value/reference-range-like syntax;
- high/low/within flags computed only from the user-supplied reference interval;
- whether an ambiguous follow-up is attached to existing lab context.
- the exact rule trace supplied to the LLM before it answers.

The browser never calculates a medical status. It visualizes analysis metadata returned by the server.

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
