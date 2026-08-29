<p align="center">
  <img src="static/img/logo.svg" alt="ResultScope" width="280" />
</p>

<p align="center"><strong>Laboratory results, in context.</strong></p>

<p align="center">
A lab-only neuro-symbolic AI starter built from the KMITL Week 7 FastAPI/Vercel chatbot architecture — redesigned to look and behave like an early health-tech product rather than a generic chatbot.
</p>

---

## What this starter is

**ResultScope** is a coursework-ready product prototype that accepts laboratory-result questions, rejects unrelated prompts before they reach the LLM, and produces structured educational explanations through any OpenAI-compatible provider such as OpenRouter.

The code intentionally keeps the instructor starter's core deployment pattern:

`Browser → FastAPI → OpenAI-compatible LLM → Vercel`

and adds a product layer:

`UI → symbolic lab scope gate → session store → LLM explanation → structured result view`

> **Working brand only.** `ResultScope` is a provisional prototype name, not a trademark clearance. Do a proper legal/brand search before commercial launch.

## Why it feels more like a product

- **Lab-only by design** — unrelated prompts are blocked deterministically before an API call.
- **Neuro-symbolic split** — symbolic rules define scope **and deterministically parse supplied marker/value/range data**; the LLM handles language and contextual explanation.
- **Reference-range discipline** — prompt policy tells the model to use user-supplied ranges rather than inventing them.
- **Versioned deterministic rulebook** — scope, parsing, range, grounding, safety, and output rules are inspectable at `GET /api/v1/rules`.
- **Pre-answer contract** — applicable rules and immutable facts are placed before history and the current user message for every allowed LLM request.
- **One integrated analysis** — selectable values, supplied-range visualization, AI narrative, and optional rule provenance live in one result object rather than competing outputs.
- **Structured explanations** — Snapshot → What stands out → How values connect → Missing context → Questions to take forward.
- **Serverless-aware session layer** — SQLite for local development, optional Upstash Redis for durable Vercel sessions.
- **Business-oriented UI** — editorial/clinical visual system rather than a ChatGPT clone.
- **Provider-portable** — preserves the Week 7 OpenAI-compatible design.

## Scope examples

| Prompt | Behavior |
|---|---|
| `Hb 10.8, MCV 72, Ferritin 7 ช่วยดูให้หน่อย` | Allowed → LLM |
| `Creatinine 1.4, eGFR 58 แปลว่าอะไร` | Allowed → LLM |
| `แล้วต้องกังวลไหม` after a lab discussion | Allowed follow-up |
| `ช่วยเขียน Python` | Blocked locally by scope gate |
| `วันนี้กินอะไรดี` | Blocked locally by scope gate |

The gate lives in `services/lab_scope.py` so its policy is inspectable and testable instead of being hidden inside a prompt.

---

# Quick start — Windows / PowerShell

### 1. Extract the ZIP and open PowerShell in this folder

```powershell
cd path\to\resultscope-starter
```

### 2. One-command local setup

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start.ps1
```

The script creates `.venv`, installs dependencies, copies `.env.example` to `.env`, opens the browser, and starts FastAPI.

### 3. Add your OpenRouter/API key

Open `.env` and set:

```env
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=your_key_here
LLM_MODEL=openai/gpt-4o-mini
OWNER_NAME=Your Name
CORS_ALLOWED_ORIGINS=
```

`OWNER_NAME` is intentionally visible in the UI so the deployed coursework link clearly identifies the student/project owner.

Keep `CORS_ALLOWED_ORIGINS` empty for the bundled same-origin web app. If a separate trusted frontend must call the API, set an explicit comma-separated origin allowlist; wildcard credentialed CORS is intentionally disabled.

Then restart the server and open:

`http://127.0.0.1:8000`

---

# Manual local setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn main:app --reload
```

Health endpoint:

```text
GET /health
```

Product metadata:

```text
GET /api/v1/product
```

Scope test endpoint:

```text
POST /api/v1/scope/check
{"message":"HbA1c 6.1% หมายความว่าอย่างไร"}
```

---

# Storage modes

ResultScope separates conversation persistence from the router.

### Local default — SQLite

`STORAGE_BACKEND=auto` uses `data/resultscope.db` when running locally. This is intentionally simple and requires no extra database service.

### Vercel without external storage — memory fallback

The app will still deploy and chat, but conversation memory may disappear between serverless instances. This is acceptable for a classroom demo, not for a real product.

### Vercel with durable sessions — Upstash Redis

Set:

```env
UPSTASH_REDIS_REST_URL=https://...
UPSTASH_REDIS_REST_TOKEN=...
STORAGE_BACKEND=auto
```

The app detects the credentials and stores session history with a TTL. No additional Python Redis package is required because the adapter uses the REST API through `httpx`.

> For a real healthcare product, do not treat this prototype storage design as compliance-ready. Add authentication, encryption strategy, data-retention controls, audit logging, consent, legal review, PDPA/HIPAA assessment, and vendor agreements as applicable.

---

# Deploy to Vercel

1. Create your own GitHub repository and push this project.
2. In Vercel: **New Project → Import repository**.
3. Add Environment Variables:

```text
APP_NAME
APP_TAGLINE
OWNER_NAME
APP_ENV=production
LLM_BASE_URL
LLM_API_KEY
LLM_MODEL
```

Optional persistent session variables:

```text
UPSTASH_REDIS_REST_URL
UPSTASH_REDIS_REST_TOKEN
```

4. Deploy. Vercel's current FastAPI zero-config path discovers the root `main.py` ASGI `app`; this repo intentionally does not carry the removed legacy `api/index.py` adapter or `vercel.json`.
5. Open the generated URL and verify `/health`, an in-scope lab question, and an out-of-scope question.

## Recommended pre-submission smoke test

```text
1. Open deployed URL on phone + desktop.
2. Confirm your name is visible.
3. Ask: HbA1c 6.1% หมายความว่าอย่างไร
4. Ask: ช่วยเขียน Python ให้หน่อย
5. Confirm #4 is blocked without an LLM answer.
6. Start a new analysis and confirm reset works.
```

---

# Design workflow with Codex + Hallmark

This package is prepared for local Codex iteration. Install/update Hallmark with:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-hallmark.ps1
```

Hallmark describes itself as an anti-AI-slop design skill compatible with Codex. Use it as a **design critic**, not as permission to rewrite the backend architecture.

Recommended Codex entry prompt is already included in `CODEX_PROMPT.md`, and project constraints live in `AGENTS.md`.

### Useful design loop

```text
1. hallmark audit templates/index.html + static/css/style.css
2. Review the punch list.
3. Redesign only where it improves hierarchy, trust, accessibility, or product clarity.
4. Run tests.
5. Verify mobile layout.
6. Do not add decorative AI gradients, glassmorphism, random blobs, or feature-card spam.
```

---

# Tests

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check.ps1
```

Current tests cover:

- common lab prompts are allowed;
- unrelated programming prompts are blocked;
- contextual lab follow-ups work;
- ambiguous follow-ups without lab context are blocked;
- generic marker/value syntax can enter the lab workflow;
- supplied ranges generate deterministic low/high/within flags;
- missing ranges remain explicitly unknown;
- conversation-store basic behavior.

---

# Project structure

```text
main.py                    FastAPI ASGI entrypoint + static/template serving
config.py                  Product/LLM/storage configuration
routers/chat.py            Session, scope gate, streaming API
services/llm_client.py     OpenAI-compatible LLM transport
services/lab_scope.py      Symbolic lab-domain classifier
services/lab_parser.py     Deterministic marker/value/range parser
services/deterministic_rules.py Versioned inspectable rule definitions
services/deterministic_engine.py Runtime analysis + pre-answer LLM contract
services/store.py          Memory / SQLite / Upstash adapters
templates/index.html       Product UI
static/css/style.css       Visual system
static/js/chat.js          Streaming chat + guardrail UX
static/img/                ResultScope SVG identity
tests/                     Scope/store/engine/API-contract tests
docs/DETERMINISTIC_RULEBOOK.md Human-readable engine contract
scripts/                   Windows local workflow
BUSINESS_BRIEF.md          Commercialization hypothesis
ARCHITECTURE.md            Technical/product boundaries
AGENTS.md                  Local Codex rules
CODEX_PROMPT.md            Ready-to-paste continuation prompt
NOTICE.md                  Upstream / licensing note
```

---

# Product boundary

ResultScope is an **educational laboratory-result explanation prototype**. It must not represent itself as a diagnostic device, prescribe treatment, or replace a licensed healthcare professional.

For coursework, this boundary also improves the demo: the product has a clear identity, a clear refusal policy, and a clear reason to exist beyond “a chatbot with a new color theme.”

## Business direction

The strongest commercial path is not “sell another AI chatbot.” It is a **white-label explanation layer for labs/clinics**:

`Result issued → branded explanation → questions to ask → longitudinal follow-up → re-engagement`

See `BUSINESS_BRIEF.md` for ICP, value proposition, defensibility, revenue hypotheses, and the V0.1→V1 roadmap.

---

## Upstream attribution and licensing

This starter is derived for coursework from the public repository `chacharin/chatbot-it-kmitl`. The upstream repository did not show an explicit software license in the inspected root at the time this starter was prepared. **Do not assume public GitHub visibility grants commercial redistribution rights.**

For class use: keep attribution. For a real commercial product: obtain permission or reimplement the small generic architecture cleanly under an appropriate license before shipping.

See `NOTICE.md`.
