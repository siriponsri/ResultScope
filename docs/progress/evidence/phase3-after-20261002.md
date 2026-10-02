# Phase 3 After Evidence

Date: 2026-10-02  
Repository: `C:\Users\User\Desktop\myProject\ResultScope`  
Branch: `main`  
Candidate base: `f9d27dd6cea707783262ddb8c237193c90f9bd0b`

## Automated implementation evidence

| Acceptance area | Status | Evidence |
|---|---|---|
| Image and Vision focused tests | **PASS** | `.venv\\Scripts\\python.exe -m pytest tests/test_phase3_images.py tests/test_phase3_vision_client.py -q` — 16 passed. |
| Full regression | **PASS** | `.venv\\Scripts\\python.exe -m pytest -q` — 127 passed, one existing Starlette/httpx deprecation warning. |
| Project check | **PASS** | `powershell -ExecutionPolicy Bypass -File .\\scripts\\check.ps1` — Checks passed. |
| JavaScript syntax | **PASS** | `node --check static/js/chat.js`. |
| Whitespace | **PASS** | `git diff --check`. |

The full regression includes the image upload, normalization, extraction-store, provider-error, session-isolation, reset, confirmation, and canonical-price protection tests. No raw image, base64 payload, secret, or provider response was written to logs by the application tests.

## Browser evidence

Playwright was installed outside the repository at `C:\Users\User\.agent-kit\tools\resultscope-phase3-browser` with `playwright@1.63.0` and `@browserbasehq/stagehand@4.1.0`. Stagehand ESM import passed. The Playwright Chromium bundle download was **NOT_RUN/PARTIAL** because the CDN download failed; the installed system Chrome `154.0.8037.58` was used through Playwright `executablePath`.

| Scenario | Status | Evidence |
|---|---|---|
| Desktop intake | **PASS** | `desktop-intake.png`; title, upload control, JPEG/PNG accept list, and layout rendered. |
| Narrow mobile intake | **PASS** | `mobile-intake.png`; `scrollWidth=390`, `clientWidth=390`, no horizontal overflow. |
| Provider unavailable upload | **PASS** | `desktop-image-unavailable.png`; error is visible beside the image control on the intake screen. |
| Local mocked upload review | **PASS** | `desktop-image-review.png`; one extracted field rendered, preview is a `blob:` URL, and no base64 image appears in the page. |
| Local mocked correction/confirmation | **PASS** | `desktop-image-confirmed.png`; `12.5` corrected to `12,5`, then status became `Confirmed for this session`. |
| Local mocked discard | **PASS** | Browser assertion confirmed `#image-review` returned to hidden state after discard. |

The mocked browser run used a local OpenAI-compatible response on `127.0.0.1:8022` and app port `8012`. It did not contact a live provider.

## Repository-required manual checks

Using a separate local synthetic app on `127.0.0.1:8013` and a local mock OpenAI-compatible endpoint on `127.0.0.1:8023`:

| Scenario | Status | Evidence |
|---|---|---|
| In-scope synthetic lab prompt | **PASS** | `Marker-A 12.5 demo-unit (10-15)` rendered an integrated result with `Sources: DEMO-READING`; exactly one mock provider request was observed. |
| Lab follow-up | **PASS** | `Why does that matter?` rendered `Contextual follow-up` with `Sources: DEMO-READING`; one additional mock provider request was observed. |
| New-analysis reset | **PASS** | Intake view returned and message input cleared after `New analysis`. |
| Out-of-scope prompt | **PASS** | `Help me write Python` rendered the outside-lab deterministic response and did not increment the mock provider request count. |
| Missing API key | **PASS** | Separate app on `127.0.0.1:8014` displayed `LLM_API_KEY is not configured...` in the visible error banner. |
| Vercel environment assumption | **PASS** | With `VERCEL=1`, `STORAGE_BACKEND=auto`, and no Upstash values, imports selected `UnavailableExtractionStore` for image extraction and `MemoryConversationStore` for conversations. |

The first manual probe used a generic `Hb` prompt and correctly abstained because the synthetic education corpus is intentionally about `Marker-A/B/C`; that was not counted as a passing grounded prompt. The rerun used the corpus-supported synthetic marker and passed.

## Provider and review boundaries

- Live Vision/OCR provider: **NOT_RUN**. No paid provider call or credential use was authorized for this round.
- Live LLM answer provider: **NOT_RUN**. Grounded answer behavior is covered by mocked API tests, not live evidence.
- Independent FO REVIEW: **NOT_RUN**. The authorized helper failed before dispatch because the loaded PowerShell/.NET runtime lacked `System.IO.Path.IsPathFullyQualified`; it was not retried unchanged and no review receipt exists.
- G3 upload-to-grounded-answer gate: **NOT_CLAIMED**. The mocked API path and browser upload-to-confirm path pass, but live provider evidence and a browser-grounded answer run are absent.
- Historical G0 and G1-data/release readiness: **BLOCKED**, preserved from earlier reports.

## Scope and privacy checks

- Work remained on local `main`; no push or deploy was performed.
- `PROMPT.md` remains untracked and excluded through `.git/info/exclude`; `.gitignore` was not changed.
- Upload accepts only JPEG/PNG content after signature/decode checks, rejects remote URLs, and does not retain raw image bytes by default.
- Image text is treated as untrusted data. Image values cannot overwrite canonical business prices, and confirmed extraction is session-bound and revisioned.
