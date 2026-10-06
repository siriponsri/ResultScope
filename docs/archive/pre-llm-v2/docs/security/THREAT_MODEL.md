# Application threat model

Scope: the current local ResultScope Laboratory Assistant. This is an engineering
record, not a security certification or approval for patient records.

| Asset or boundary | Implemented control | Main evidence paths | Residual limitation |
| --- | --- | --- | --- |
| Scope and policy | Python routing; privileged requests refused; retrieved/OCR text treated as untrusted | lab_scope.py, intent_router.py; safety tests | Prompt boundaries cannot prove all live-model behavior |
| Numeric and business facts | Supplied-range calculations, release corpus gate, validated output | deterministic_engine.py, knowledge.py, output_validation.py | Source approval and business corpus remain incomplete |
| Citations and URLs | Bind source markers and links to current retrieval; reject unsupported output | answer_service.py, output_validation.py; public-reference tests | Post-remediation live validation is not complete |
| Conversation/extraction access | Signed session cookies, revision and ownership checks, reset | sessions.py, image_extraction.py; image/session tests | Not patient identity, RBAC, or multi-tenant authorization |
| Administrator configuration | Explicit local mode, password handling, CSRF, write-only key entry, encrypted local file | admin_auth.py, provider_config.py; admin tests | Demo fallback credentials and file persistence are unsuitable online |
| Provider quota | Offline guard and atomic SQLite reservation before HTTP, no refunds | provider_budget.py; budget and runner tests | One shared local filesystem, not a distributed cloud quota service |
| Browser content | DOM text nodes, sanitized Markdown, bounded error messages | chat.js; safety and API tests | Full accessibility/security penetration review remains open |
| Image input | Decoded-format and size/pixel checks, re-encoding, metadata removal | image_extraction.py; image tests | PDF unsupported; provider retention needs separate review |
| Availability | Message/history/output bounds, timeout, local rate limits | chat.py, request_limits.py | Local request limits and locks do not coordinate multiple hosts |

Code paths above are under services/ unless their UI/router names identify otherwise.

## Required boundaries during evaluation

Keep provider networking off for offline work. Do not use real patient identifiers,
edit stored secrets, reopen a budget cycle or expose local-demo administration to
obtain a prettier demonstration. Render an honest unavailable state when a dependency
is missing. Synthetic screenshot mocks must remain visibly identified.

The new UI serves its fonts, Markdown parser and sanitizer from the same origin.
This removes runtime CDN fetching but does not assert that dependencies have undergone
a vulnerability audit. The optional media composition is not loaded by the app.

## Open operational work

Production requires a defined identity/access model, consent and retention policy,
cloud secret storage, shared distributed limits, audit ownership, monitoring,
backup/restore and incident handling. Historical provider-budget overruns remain
in the [evidence history](../evidence/HISTORY.md). A new interface does not erase them.
