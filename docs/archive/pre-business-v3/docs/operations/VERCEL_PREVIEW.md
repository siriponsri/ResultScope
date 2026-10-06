# Vercel deployment — ResultScope 2.0

This package uses Vercel's native FastAPI support, checked against the official
[FastAPI documentation](https://vercel.com/docs/frameworks/backend/fastapi) on 2026-10-05.
The application remains in `main.py`. `[tool.vercel] entrypoint="api.index:app"` selects
the cloud startup guard. `cdn=false` retains the FastAPI static mount. No catch-all
rewrites or hard-coded environment overrides are required. Python 3.12 is pinned;
`api/index.py` has a 240-second function allowance and chat has a 220-second application timeout.

## Replace and import

Back up your existing folder. Extract `ResultScope/` from the ZIP and replace tracked
project files. Keep your existing `.env`, `data/`, keys and provider ledger outside the
replacement step; none are included in the ZIP. Install with the supplied requirements.
Import this repository/folder in Vercel with project root `.` and Framework Preset
**Other**. Keep default build/output commands. Do not configure a static-only deployment.
The first deployment can show the complete setup-mode UI without provider secrets.

## Environment variables

Configure these in Vercel Project Settings → Environment Variables for the intended
Preview/Production environment, then redeploy. Values below are descriptions, not keys.

| Variable | Required for live chat | Meaning |
|---|---|---|
| `PROVIDER_NETWORK_ENABLED` | Yes | Set `true` only when authorizing live calls. Default false. |
| `LLM_BASE_URL` | Yes | HTTPS OpenAI-compatible API base, e.g. `https://api.opentyphoon.ai/v1`. |
| `LLM_API_KEY` / `LLM_MODEL` | Yes | Server-side key and JSON-capable conversation model. |
| `GUARD_BASE_URL` | Direct guard | HTTPS chat API serving Llama Guard. |
| `GUARD_API_KEY` / `GUARD_MODEL` | Direct guard | Default model ID `meta-llama/llama-guard-4-12b`; verify provider availability. |
| `GUARD_SERVICE_URL` | Alternative | Teacher-compatible service base exposing `/check`; omit for direct guard. |
| `GUARD_SERVICE_TOKEN` | If needed | Bearer credential expected by your service/proxy. |
| `SESSION_SIGNING_KEY` | Yes | Random secret, at least 32 characters, stable across instances. |
| `DEMO_ACCESS_CODE` | Yes | Random shared demo code, at least 12 characters; give it to authorized testers. |
| `UPSTASH_REDIS_REST_URL` / `UPSTASH_REDIS_REST_TOKEN` | Yes | Shared Redis REST store for atomic usage limits. |
| `PROVIDER_BUDGET_CYCLE_ID` | Yes | Explicit cycle name, e.g. `resultscope-review-20261005`. |
| `CLOUD_CALL_LIMIT` | Yes | Total upstream HTTP attempts across LLM/guard/vision/retrieval; default 200. |
| `VISION_ENABLED` | Optional | `true` to activate report reading. |
| `VISION_BASE_URL` / `VISION_API_KEY` / `VISION_MODEL` | For reports | HTTPS vision/OCR model configuration. |
| `LIGHTRAG_ENABLED` | Optional | `true` after provisioning and importing trusted sources. |
| `LIGHTRAG_URL` / `LIGHTRAG_API_KEY` | For hybrid search | Dedicated service base and `X-API-Key`. |
| `CONTEXT_TTL_SECONDS` | Optional | Encrypted context lifetime; default 3600. |
| `STORAGE_BACKEND` | Legacy only | Leave `auto`; do not select SQLite on Vercel. |

Enabling cloud network access without the required secret, code, Redis or named cycle
fails at startup. The first authorized request atomically creates the named Redis
counter at the configured cap. Later cap mismatches or exhaustion block calls. There
is no expiry and no automatic refund. Changing a cycle ID authorizes another allowance;
do not rotate it accidentally on every deploy. Five calls normally produce one chat turn.
This is an attempt cap, not a currency budget or per-user entitlement system.

## Verify after deployment

Open `/health`, `/`, `/settings`, the sample gallery and introduction. The config route
reports presence of settings, never secrets. Enter the demo access code and make one
small question, then a follow-up in another language. Test one synthetic report through
read → review → confirm. Check the Redis counter and compare actual provider billing.
Check `/api/v1/chat` returns 410 and local admin routes are unavailable. Check an
exhausted cycle with a separate authorized test configuration; never reset the real counter.

The supplied verification covers local ASGI and fresh cloud-entrypoint subprocesses.
Actual Vercel build, deployment, remote Redis and live-model compatibility are **NOT_RUN**
in this delivery because credentials and an authorized live cycle were not supplied.
A successful build alone is not clinical, privacy or operational approval for real patients.
