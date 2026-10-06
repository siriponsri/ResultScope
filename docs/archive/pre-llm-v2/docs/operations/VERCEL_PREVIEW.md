# Vercel preview preparation

This document describes the staged Vercel preview boundary for ResultScope Laboratory Assistant. It is an offline, synthetic demonstration setup. It is not a production, clinical, privacy, compliance, or availability approval.

## What is included

- `api/index.py` exports the existing FastAPI `app` from `main.py`.
- `vercel.json` identifies the Python function and supplies non-secret preview defaults.
- FastAPI keeps ownership of `/`, `/health`, `/api/v1/*`, and `/static/*`; the existing `main.py` static mount must remain in the function bundle.
- The Vercel entrypoint applies safe defaults before importing `main.py` and rejects unsafe cloud settings instead of silently changing them.

Vercel's Python runtime can load an ASGI application named `app`. The current configuration intentionally keeps the application as one FastAPI surface rather than introducing a second router or a frontend framework.

## Preview defaults

Set these values in the Vercel project. The same safe values are present in `vercel.json` so a new preview does not inherit a live or release-oriented local configuration:

| Variable | Preview value | Why |
|---|---|---|
| `APP_ENV` | `preview` | Identifies the staged cloud environment. |
| `KNOWLEDGE_MODE` | `synthetic` | Keeps the preview on synthetic business/demo knowledge. |
| `PROVIDER_NETWORK_ENABLED` | `false` | Preserves the deny-by-default network guard; no LLM, OCR, fallback, or SystemOne request is made. |
| `LOCAL_DEMO_MODE` | `false` | Prevents local administration from being enabled by configuration. |
| `STORAGE_BACKEND` | `auto` | Selects Upstash when both Upstash variables exist; otherwise uses the existing non-file fallback for Vercel. |

`api/index.py` also requires a non-empty `SESSION_SIGNING_KEY` and rejects `STORAGE_BACKEND=sqlite` or `PROVIDER_NETWORK_ENABLED=true` on Vercel. This is a fail-closed deployment boundary: an unsafe explicit setting stops import rather than causing local SQLite or provider-ledger writes in a serverless function.

## Vercel Environment Variables

Configure variables in the Vercel Dashboard under Project Settings -> Environment Variables. Use Preview for the staged demonstration. Do not commit values to `vercel.json`, `.env`, screenshots, receipts, or documentation.

Required secret:

- `SESSION_SIGNING_KEY`: a long, random secret used to sign conversation cookies. The Vercel entrypoint refuses to start without it; the process-local fallback remains available only for local development.

Required for durable preview session and extraction state:

- `UPSTASH_REDIS_REST_URL`: the Upstash Redis REST endpoint.
- `UPSTASH_REDIS_REST_TOKEN`: the Upstash REST token, stored as a secret.

With `STORAGE_BACKEND=auto`, the existing stores select Upstash when both values are configured. Conversation history and confirmed image-extraction records use TTLs already defined by the application. If Upstash is not configured, conversation state falls back to process memory and extraction confirmation is unavailable on Vercel; that is suitable only for an intentionally limited smoke check, not a durable report workflow.

Optional provider secrets are not needed for the offline preview. If a separately authorized bounded provider cycle is ever considered, provider credentials belong only in Vercel Environment Variables and must remain server-side. This document does not authorize that cycle, enable network access, or establish a cloud quota ledger.

## Administration and secrets

The existing local-only guard remains authoritative. `services.admin_auth.local_demo_enabled()` requires explicit local-demo mode, a local development/test environment, and no `VERCEL` environment marker. Therefore these routes are unavailable on Vercel, including when a caller submits `admin / 1234`:

- `/admin/login`
- `/admin/settings`
- `/api/v1/admin/*`

Do not set `LOCAL_DEMO_MODE=true` on Vercel. The entrypoint does not import or use the local encrypted provider-settings file as an alternative secret store. API keys, Upstash tokens, and the session-signing key must never be returned to the browser or written to the repository filesystem.

## Storage boundary

Vercel function filesystems are not the durable application database. This preparation therefore makes no attempt to use the local SQLite conversation store, SQLite extraction store, admin settings file, or SQLite provider-budget ledger as cloud persistence. Upstash is the intended preview persistence adapter for conversations and extraction confirmations; it is not an identity system, consent system, healthcare record, or distributed quota-control approval.

The provider network remains disabled. The application must not be presented as a live provider integration merely because an API key exists in the Vercel dashboard. Synthetic data and de-identified fixtures are the only permitted preview inputs.

## Deployment and smoke check

1. Import the repository into Vercel without adding a build command.
2. Add the non-secret preview values above and create a random `SESSION_SIGNING_KEY` secret.
3. Add both Upstash variables when testing durable session or extraction behavior.
4. Deploy a Preview, not a production release.
5. Check the deployed URL with synthetic data:
   - `GET /` returns the ResultScope workspace.
   - `GET /health` returns `status: ok` and `environment: preview`.
   - `GET /static/docs/user-guide.html` returns the maintained guide.
   - `/admin/login` and `/api/v1/admin/config` remain unavailable.
   - No external provider request is made while `PROVIDER_NETWORK_ENABLED=false`.
6. Record the deployment URL, candidate SHA, environment scope, test inputs, and any unavailable storage state in a sanitized receipt. Never record secret values, patient data, provider bodies, or raw exceptions.

The repository tests cover entrypoint import, safe preview defaults, the fail-closed storage/network checks, the existing Vercel admin guard, and local static routing. A deployed smoke check is not run by these tests and must not be described as complete without a real Preview URL and receipt.

## Readiness boundary

This is staged preview preparation only. It does not claim production readiness, clinical readiness, customer adoption, compliance, privacy approval, or operational support. Before any broader deployment, separately resolve identity and roles, consent and retention, privacy review, durable quota control, monitoring and incident response, backups/recovery, provider quality evaluation, human usability/accessibility evidence, and owner approval.
