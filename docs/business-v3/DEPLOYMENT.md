# Deployment and local operations

## Preserve state

Merge .env.business.example into the existing .env. Never reset the provider ledger or replace BUSINESS_DATA_KEY on an existing database. Local default storage is data/business.sqlite3 with a generated data/business.key. Back up both together. Use Python 3.12 and requirements.txt; npm is optional browser-verification tooling.

## Required hosted settings

| Setting | Purpose |
|---|---|
| DATABASE_URL | PostgreSQL connection string with provider-required TLS, preferably a suitable pooled endpoint |
| BUSINESS_DATA_KEY | Stable Fernet key generated once with cryptography.fernet.Fernet.generate_key() |
| BUSINESS_PUBLIC_URL | Your HTTPS public origin, without a trailing slash |
| SESSION_SIGNING_KEY | Stable secret for retained v2 context; at least 32 characters |
| DEMO_ACCESS_CODE | Course AI access code of at least 12 characters; never publish in source |
| LLM_API_KEY and LLM_MODEL | Typhoon default; API base in .env.example |
| GUARD_API_KEY or GUARD_SERVICE_URL | Independent safety classifier; failures block AI output |
| PROVIDER_BUDGET_CYCLE_ID | Named, explicitly authorized test cycle |
| CLOUD_CALL_LIMIT | Shared maximum counted upstream attempts in that cycle |
| UPSTASH_REDIS_REST_URL and TOKEN | Durable atomic cloud call budget |
| PROVIDER_NETWORK_ENABLED | Keep false until keys, budget and test scope are ready |

BUSINESS_EXTERNAL_ENABLED is separate from provider AI permission. LINE/Stripe require it true. Set VISION_ENABLED=true for either OCR provider. Typhoon OCR also needs its configured vision key. For iApp, select REPORT_OCR_PROVIDER=iapp, IAPP_OCR_API_KEY and IAPP_OCR_MODE=text or layout; a Typhoon vision key is not required for that adapter. Both paths also need the conversation model for structuring and the independent guard. No fallback sends health documents to a second vendor silently.

## Vercel

Import the repository root with its existing pyproject.toml and vercel.json. The Python entrypoint is api.index:app; maxDuration is 240 seconds. Keep framework/build defaults for native FastAPI. Configure database/key before testing /api/business/session; hosted storage fails closed without them. The public homepage can still show the catalog in setup mode. Use /health for liveness and /api/v2/config for AI configuration status. These are not proof of every external dependency being healthy.

Provision PostgreSQL and Redis externally. Vercel's filesystem is not persistent business storage. Host LightRAG separately. For LINE, run the worker on a persistent service against the same database, or call POST /api/business/worker/run from a trusted scheduler with Authorization: Bearer BUSINESS_WORKER_SECRET (32+ characters). Vercel Hobby is for eligible personal non-commercial coursework, not a live commercial clinic.

.vercelignore excludes documentation, tests, research extractions and discovery-only raw sources; approved source PDFs required for hash checks remain included. No npm build is needed for runtime.

## Render

render.yaml defines a Python web service and health check. Set DATABASE_URL and BUSINESS_DATA_KEY in the service dashboard. scripts/run_business.py starts uvicorn; BUSINESS_WORKER_ENABLED=true also starts a persistent worker in the same service. Configure BUSINESS_EXTERNAL_ENABLED=true only for a deliberate integration cycle. Free service sleep/cold starts can delay LINE; free filesystem and expiring free PostgreSQL are not durable project storage. Measure RAM before adding LightRAG, which should remain a separate service.

## Staff and integrations

Run python scripts/create_staff.py --help, then create a staff/manager account interactively against the selected database. There are no default deployed staff credentials. The UI test harness credentials exist only in a temporary test database.

LINE: configure CHANNEL_SECRET and CHANNEL_ACCESS_TOKEN server-side, set webhook to /api/business/line/webhook, start worker, test signature and duplicate delivery before live conversation. Enable LINE_ALLOW_PUSH only after reviewing message quota and consent. Use account-link invitations generated inside the verified LINE chat.

Stripe: use sk_test credentials and STRIPE_WEBHOOK_SECRET. Point sandbox events at /api/business/payments/webhook. Card/PromptPay checkout redirects to the provider; the UI never collects card details. Verify success, expired, async, wrong-amount and replay events. Live keys are rejected. Real money is outside this coursework release.

Maps: set GOOGLE_MAPS_EMBED_KEY, restrict HTTP referrers to your deployment and restrict the API to Maps Embed. Without it, the app offers an ordinary Google Maps area link; that fallback is not proof of an active Embed API connection. Pins identify mock service areas, not real clinics.

## LightRAG

Run python scripts/export_lightrag.py --output knowledge/medical_sources/lightrag-import.json. Ingest texts with their matching file_sources into your pinned LightRAG service. Do not ingest discovery-report.md, raw PDFs wholesale, private reports or expected_results.json. Set LIGHTRAG_URL/API_KEY and LIGHTRAG_ENABLED=true only after /query/data returns file_path values beginning resultscope://evidence/ and matching known IDs. The application combines BM25 with mix graph/vector ranks. Pin the embedding model/dimension; rebuild the index if these change.

## Recovery and remaining production work

Back up encrypted DB plus keys; restore into an isolated environment and check customer ownership before switching traffic. Failed jobs appear in manager operations; investigate before manual requeue because a provider may already have received a request. Email verification/recovery, fine-grained clinical roles, retention automation, real merchant onboarding, independent security/clinical review and load tests remain production work. The current package is an operational coursework system, not a certified medical service.
