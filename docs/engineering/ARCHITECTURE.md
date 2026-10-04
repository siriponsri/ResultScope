# Application architecture

ResultScope Laboratory Assistant uses **FastAPI, Jinja templates, and vanilla JavaScript**. Python owns the scope, deterministic facts, retrieval, and validation boundaries. The current application does not contain an HIS connector, pharmacy backend, FHIR server, or hosted vector service.

![Architecture and proposed integration boundaries](../assets/diagrams/architecture.svg)

## Runtime and source ownership

| Area | Source | Responsibility |
|---|---|---|
| ASGI entry point | `main.py` | FastAPI app, same-origin static assets, template rendering, routers, health |
| Defaults | `config.py` | Product, provider, session, image, corpus, rate-limit, and budget settings |
| Chat API | `routers/chat.py` | Signed session resolution, bounded history, pipeline, persistence, JSON/SSE responses |
| Scope and intent | `services/lab_scope.py`, `services/intent_router.py` | Laboratory scope, local/unsafe/business/mixed routing |
| Deterministic facts | `services/lab_parser.py`, `services/deterministic_engine.py`, `services/deterministic_rules.py` | Supplied-value parsing, range flags, grounding contract, inspectable rules |
| Knowledge and retrieval | `services/knowledge.py`, `services/retrieval.py` | Corpus validation/provenance and lexical matching |
| Public reference bridge | `services/public_reference.py` | Translate pinned addon records into the application's evidence contract |
| Answer and validation | `services/answer_service.py`, `services/output_validation.py` | Source-bound prompting, fail-closed results, factual/citation/URL/safety checks |
| Providers | `services/llm_client.py`, `services/vision_client.py`, `services/systemone_client.py`, `services/provider_adapters.py` | Distinct LLM, image, shadow, and test transport boundaries |
| Attempts | `services/provider_budget.py` | Persistent cycle and atomic pre-transport attempt reservations |
| Image workflow | `routers/images.py`, `services/image_extraction.py`, `services/extraction_store.py` | Validate bytes, normalize fields, session-bound review and confirmation |
| Administration | `routers/admin.py`, `services/admin_auth.py`, `services/provider_config.py` | Local sign-in, CSRF, allowlisted settings, encrypted local secret persistence |
| Persistence | `services/store.py`, `services/sessions.py` | Conversation adapters, signed IDs, per-process session locking |
| UI | `templates/index.html`, `static/js/chat.js`, `static/js/admin.js`, `static/css/` | Render interaction and metadata; never invent server-owned flags |

Paths are relative to the repository root.

## Text request lifecycle

1. The browser posts a message, optionally with a confirmed extraction ID. The server validates the signed session cookie and bounds retained history.
2. Python classifies intent and analyzes supplied laboratory values. Unsafe and unrelated requests are handled before generation; mixed questions may require clarification.
3. The answer service retrieves relevant evidence. Missing sources, ambiguous matches, unavailable corpus, or absent approved content lead to an explicit local response.
4. The provider prompt includes deterministic facts and retrieved context as untrusted data. If transport is authorized, the relevant slot must reserve an attempt before HTTP.
5. The output validator checks the result against the request, facts, and retrieved sources. Invalid output fails closed. Rejection does not refund an attempt.
6. Validated results are persisted and returned with safe metadata and citations.

The SSE route (`/api/v1/chat/stream`) runs the pipeline and validation before emitting the answer text. Its name does not mean raw, unvalidated provider tokens are shown to the user. JSON and SSE use the same validated-result boundary.

## Evidence retrieval

The ordinary knowledge path uses a local manifest, source snapshots, structured records, and lexical scoring in `services/retrieval.py`. Release mode requires owner-approved eligible sources and fails closed if they are unavailable; synthetic fixtures are not an automatic production fallback.

When `PUBLIC_REFERENCE_ENABLED` is enabled, the public-reference adapter uses `addons/resultscope_evidence_v1/core.py` and `guidance.py`. The numeric tree follows organization → document → analyte → evidence, guided by local metadata and aliases. It is not RAPTOR, vector search, an LLM agent, or a claim of universal retrieval superiority. Retrieved records preserve source identifiers, pages, checksums, and available rights metadata.

Public numeric ranges are source-comparison evidence. They do not replace the range on a user's report. Guideline notes are educational context, not numeric diagnostic rules. Clef remains off.

## Image lifecycle

`POST /api/v1/images/extract` checks signatures, decoded format, byte size, and pixel limits; it re-encodes the image and removes metadata before the OCR call. Defaults are 3 MiB, 12 million pixels, and at most 30 fields. JPEG and PNG are supported; PDF is not.

A successful extraction is stored in `review_required` state. Confirmation requires the same session, current revision, and complete field set. User corrections are normalized server-side. Chat accepts confirmed extraction context, not a client assertion that unreviewed OCR is trustworthy. Original and normalized image bytes are not persisted by the application; extracted text and fields are stored. Provider-side retention is a separate unresolved deployment concern.

## Sessions and stores

Conversation IDs are signed with a configured key or a per-process temporary key. Cookies are HttpOnly and SameSite Lax; production mode marks the conversation cookie Secure. This associates browser sessions with records but does not identify a patient or authorize an institutional role.

`STORAGE_BACKEND=auto` chooses Upstash if credentials exist, otherwise SQLite locally, otherwise memory on Vercel. The extraction store has corresponding adapters and fail-closed behavior. SQLite conversation data is local plaintext JSON in database rows. Memory is nondurable. Upstash support is an implementation option, not an approved production deployment.

Per-session locks are process-local. They are not a distributed locking scheme. The attempt ledger is a separate SQLite control, durable only where all participating processes share its file on one machine.

## Provider controls

`PROVIDER_NETWORK_ENABLED=false` is the default. A live path requires a configured provider, explicit opt-in, active cycle, available ledger, and quota. Reservations use SQLite transactions with `BEGIN IMMEDIATE`. Failed, malformed, timed-out, rejected, and unfinished attempts stay consumed; disabled redirects and no configured SDK retry help bound transport.

Typhoon LLM and OCR use separate contracts. SystemOne uses a distinct iApp typed-decision adapter and remains shadow-only. Catalog protocol labels do not establish live validation. The administrator **enabled** setting is not the global network switch: some runtime paths can fall back to environment configuration.

## API surface

| Endpoint | Purpose | Provider potential |
|---|---|---|
| `GET /health` | Process health metadata | None |
| `GET /api/v1/product` | Product metadata | None |
| `GET /api/v1/rules` | Versioned deterministic rules | None |
| `POST /api/v1/scope/check` | Scope check | None |
| `POST /api/v1/chat` | Validated JSON response | LLM; optional shadow |
| `POST /api/v1/chat/stream` | Validated SSE response | LLM; optional shadow |
| `POST /api/v1/chat/reset` | Clear current analysis/session records | None |
| `GET /api/v1/models` | Provider model listing | LLM slot; consumes a reserved attempt |
| `POST /api/v1/images/extract` | Image validation and extraction | OCR |
| `POST /api/v1/images/{id}/confirm` | Confirm edited extraction | None |
| `POST /api/v1/images/{id}/cancel` or `DELETE /api/v1/images/{id}` | Cancel extraction | None |
| `/api/v1/admin/*` | Local sign-in, CSRF, configuration, provider tests | Tests are mock by default; live requires all gates |

## Deployment and future boundaries

The root `main.py` ASGI entry point preserves the repository's simple FastAPI deployment structure. That compatibility is not evidence of a deployed or approved service. Local settings persistence and the SQLite attempt ledger are not suitable as cloud-wide controls. See [readiness](../operations/READINESS.md).

Proposed HIS and pharmacy interfaces must be shown as future, dashed boundaries in diagrams. No implemented integration, partner connection, patient record, or FHIR contract should be inferred from the architecture illustration.
