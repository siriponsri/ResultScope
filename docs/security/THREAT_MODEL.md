# ResultScope Phase 4 Threat Model

Status: local Phase 4 prototype hardening. This document describes implemented
controls and residual risks; it is not a security certification.

## Assets and trust boundaries

| Asset | Boundary / attacker-controlled input | Control | Evidence |
|---|---|---|---|
| System policy and mode | User text, history, corpus text, and OCR text are untrusted | Server selects mode; prompt sections separate policy from data; privileged business changes are refused | P4-T01, P4-S01, P4-S04 |
| Canonical prices/policies | User claims, image values, and provider output | Retrieval selects approved current records; image values are never business facts; unsupported business numbers abstain | P4-T02, P4-S01, P4-S03, P4-SYNC |
| Citation provenance | Provider-generated source markers | Marker IDs are checked against current retrieved source IDs; application appends citations from retrieved records | P4-T02, P4-SYNC |
| Session history/extractions | Cookie tampering, foreign IDs, reset races | Signed session cookie, session locks, ownership checks, revision/expiry, reset clears and rotates | Existing Phase 3 tests; P4-S02 |
| Provider and image secrets | Error payloads, logs, browser state | Friendly provider errors; no raw provider payload/image/base64 in responses; browser renders image via blob URL | Existing Phase 3 tests; P4-T03 |
| Browser output | User, OCR, corpus, and provider text | Text nodes for dynamic metrics; Markdown path uses DOMPurify or escaped fallback; no dynamic range HTML interpolation | P4-T03, P4-B01 |
| Service capacity | Large message/history/provider output and repeated requests | Pydantic message bound, bounded history, provider output bound, image limits, timeout, local fixed-window limiter | P4-T04, P4-T05 |

## Attack cases

1. Direct prompt injection asks the user to change mode, reveal keys, or override
   policy. The application does not treat user text as authority; business
   authorization and source selection remain server-controlled.
2. Indirect injection appears in retrieved text or confirmed OCR. Those values
   are labeled untrusted in the provider prompt and cannot authorize a source,
   change a price, or change a session.
3. A provider fabricates a number, citation, medical instruction, or business
   fact. Numeric and citation checks fail closed; unsafe clinical language is
   rejected; business facts still require current retrieval and the canonical
   source path.
4. A client reuses an extraction ID or session cookie from another session.
   Existing ownership and signed-cookie checks return not-found without data.
5. A stream fails after provider timeout, malformed output, store failure, or
   cancellation. Validation happens before the answer delta; handled failures
   emit a safe error and terminal event, while client cancellation stops the
   generator.
6. An attacker supplies HTML/script or unsafe links in a value or answer.
   Dynamic metric values use DOM text nodes; rich answers pass through the
   existing sanitizer path or escaped fallback.

## Residual risks and limits

- Mocked provider tests validate application controls, not the behavior of a
  live model. Live LLM/Vision safety evaluation is `NOT_RUN` by owner policy.
- The fixed-window rate limiter is process-local and keyed by client address.
  A multi-instance deployment requires a shared limiter before production use.
- No authentication or patient identity layer exists; this is a lab-only
  prototype and must not be used as a cross-user clinical record system.
- Provider model quality, OCR quality, browser CDN availability, and real
  release-corpus readiness remain outside this evidence bundle.
