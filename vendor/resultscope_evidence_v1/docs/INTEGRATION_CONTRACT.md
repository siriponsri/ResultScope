# Integration contract and future product boundary

## Today

The delivered runnable interface is a loopback reference browser. Python imports provide `EvidenceCorpus.search`, `context_packet`, `compare` and optional `clef.shadow_decision`. **No FastAPI router has been mounted in the owner's Phase 4 application. No HIS, pharmacy database, live provider or patient DB is connected.**

## Main application adapter

1. Instantiate `EvidenceCorpus` once on startup. A corpus validation error disables this optional public-reference path with a safe message; do not relax clinical policies to compensate.
2. Run existing input/scope/file validation and context handling first. Route business questions to approved business data; public manual references are not business policies or price evidence.
3. Call `search` on the bounded normalized question. An abstention should produce a helpful follow-up or existing refusal according to policy, never invented evidence.
4. Use `context_packet` for at most 12 returned record IDs. Attach human citation metadata from the manifest on the server. Keep URL/page/hash/version through any schema conversion.
5. Feed the packet as external data through the existing provider abstraction. Model prompts must preserve: report ranges first; no diagnosis/prescribing; source disagreements explicit; missing applicability unknown. The text constraints in the packet are advisory; enforce output/citation validation in code.
6. Reject fabricated source IDs/pages/claims. Resolve URLs on the server from the source allowlist, not arbitrary LLM output. Never expose credentials, raw provider bodies, report images or patient identifiers in logs.
7. Use the same answer construction and policy validation for JSON and SSE. Stream only validated content or use the existing buffered policy boundary. Preserve session signing, reset, size/rate controls and error handling.

Recommended feature flag in the actual application: `PUBLIC_REFERENCE_ENABLED=false` by default until integration tests pass; use project conventions instead of adding a second config framework. Keep Clef independently disabled. The local demo can explicitly enable public references and must label the dataset.

## Proposed portable product contract (design, not an implemented adapter)

Keep `ReportInput`, `Observation`, `Evidence`, `Explanation` independent of provider and UI. A normalized observation needs a stable external ID, test name/code, exact value/comparator, unit, source-provided reference interval, specimen/time and explicit unknown context. Record mapping provenance; preserve source raw values. Separate external patient identifiers from model-bound content.

HIS/FHIR adapter work should initially be read-only and use synthetic fixtures: e.g. map `DiagnosticReport` and referenced `Observation` into the internal contract, retain identifiers/code systems/units and avoid guessing mappings. Pin the partner's actual FHIR version/profile. Do not label the app 'FHIR compliant' based on these notes. There is no universal HIS endpoint. Pharmacy integration needs its own vendor schema, authentication, consent, tenancy and mapping tests; prescribing/dispensing remains outside this assistant's scope.

Before live integration: partner contract and sandbox, authorization, de-identification rules, tenant isolation, retention/deletion, auditable access, least privilege, encrypted transport/storage where used, rollback and real integration evidence. Do not add arbitrary external connectors just to make a catalog checklist look complete.

## Product catalog wording now

Accurate: 'ResultScope prototype for understandable lab explanations with source-linked public-reference lookup; local integration and clinical/business release approval in progress.'

Unsupported now: 'production ready', 'clinically validated', 'connected to every HIS', 'automatically selects correct patient ranges', 'Clef verified medical answers', or 'approved by Siriraj/KKU'. A visual demo can be presented now; those claims cannot.
