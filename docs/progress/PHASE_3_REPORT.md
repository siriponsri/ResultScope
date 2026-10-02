# ResultScope Phase 3 Report - Vision/OCR

Date: **2026-10-02**  
Branch: local `main`  
Base HEAD: `f9d27dd6cea707783262ddb8c237193c90f9bd0b`

## Scope

Phase 3 adds a bounded synthetic-document image path while preserving the existing FastAPI/Vercel entrypoint, provider portability, session boundary, and synthetic/release separation. The implementation covers safe JPEG/PNG upload, opt-in Vision provider adaptation, normalized extraction, review/correction/confirmation, session-bound TTL storage, reset cleanup, and the review UI.

No OCR framework, remote image fetch, authentication, patient profile, diagnosis, prescribing, or deployment behavior was added.

## Gate summary

| Gate | Status | Evidence |
|---|---|---|
| Safe upload and image lifecycle | **PASS for tested local scope** | Magic-byte/decode/pixel/size checks, temporary normalized bytes, deletion/reset, and focused tests. |
| Vision adapter contract | **PASS for mocked/local contract** | Structured schema, timeout/provider/invalid JSON sanitization, and focused tests. |
| Extraction review and confirmation | **PASS for mocked/local scope** | Revisioned session store, correction API, browser review/confirm/discard run, and focused tests. |
| Synthetic fixtures I01-I05 plus Thai fixture | **PASS for fixture boundary** | Coursework images are accepted by the upload boundary; Thai extraction fixture is covered separately. Provider quality is not inferred. |
| Browser desktop/mobile | **PASS for local browser evidence** | See `evidence/phase3-after-20261002.md` and `evidence/phase3-browser-20261002/`. |
| Live Vision/OCR | **NOT_RUN** | No paid provider call or credential use was authorized. |
| G3 upload-to-grounded-answer | **NOT_CLAIMED** | Mocked API and browser upload-to-confirm evidence exist; live provider and browser-grounded answer evidence are absent. |
| Independent FO REVIEW | **NOT_RUN** | The configured helper failed before dispatch; no receipt exists. |
| Historical G0 / G1-data / release readiness | **BLOCKED** | Preserved from Phase 0-2; Phase 3 does not change approval or source status. |

## Implemented behavior

- `routers/images.py` accepts one multipart image and validates actual JPEG/PNG content, encoded size, decoded pixel count, and decode integrity before calling Vision.
- `services/vision_client.py` is opt-in and OpenAI-compatible. Provider unavailable, timeout, authorization, rate-limit, transport, and malformed extraction responses become sanitized application errors.
- `services/image_extraction.py` retains raw values and normalizes comparator, numeric text, unit, supplied reference range, and explicit `unknown` states without inventing missing data.
- `services/extraction_store.py` binds extraction records to the current session, tracks revisions, expires records, confirms only current revisions, and clears records on reset/cancel.
- Chat accepts only a confirmed extraction from the same session. Image-derived service prices remain untrusted and cannot replace canonical business corpus values.
- The UI previews a selected image, renders extracted fields for correction, supports confirm/discard, and now shows image-provider errors beside the upload control while still on the intake view.

## Verification

See [`evidence/phase3-after-20261002.md`](evidence/phase3-after-20261002.md) for exact commands and browser artifacts.

- Full pytest: **126 passed**, one existing Starlette/httpx deprecation warning.
- `scripts/check.ps1`: **PASS**.
- `node --check static/js/chat.js`: **PASS**.
- `git diff --check`: **PASS**.
- Local Playwright with system Chrome: desktop/mobile intake and mocked review/correction/confirmation/discard **PASS**.
- Playwright package install: **PASS** outside repo. Chromium bundle download: **FAILED at CDN**, so system Chrome was used.

## Orchestration and limitations

The Phase 3 FO IMPLEMENT/REVIEW helper was invoked once under the configured role ownership. It failed before dispatch because the loaded PowerShell/.NET runtime did not provide `System.IO.Path.IsPathFullyQualified`. It was not retried unchanged, no global Agent Kit settings were modified, and no independent review receipt was produced. MAIN's verification is not independent review.

The mocked provider and synthetic fixtures establish contract behavior only. They do not establish OCR accuracy, Thai-language quality, poor-image recovery quality, semantic LLM quality, live latency, or release readiness.

## Closeout constraints

- Local `main` only; no push and no deploy.
- `PROMPT.md` remains local-only, untracked, and listed in `.git/info/exclude`; `.gitignore` is unchanged.
- No credentials, raw image/base64 payloads, or provider secrets were committed or logged.
- Phase 4/5 work is not started.
