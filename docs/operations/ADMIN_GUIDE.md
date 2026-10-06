# Operator guide

For v3 business operations, create staff accounts with scripts/create_staff.py and sign in at /staff. Take over a case before replying. Managers manage catalog availability/prices, organization quotations, sandbox refunds and delivery failures. Follow ../business-v3/DEPLOYMENT.md for database, worker and secret setup. Business roles do not grant access to the development provider-settings surface below.

Use `.env` locally and Vercel Environment Variables in the cloud. Never put API keys
in browser JavaScript, URLs, screenshots, model prompts or source control. The page
`/settings` contains instructions, not a server-side credential editor.

The retained local admin UI is a development-only configuration surface. It supports
conversation, OCR, guard and legacy SystemOne slots. v2 never calls SystemOne. Guard
uses a separate key and model. Existing saved configs acquire the guard default without
losing prior slots. Provider tests must remain mock unless a live cycle is explicitly
opened. A badge or mock test does not establish a working live model.

Local admin requires `LOCAL_DEMO_MODE`, `ADMIN_PASSWORD_HASH` and
`ADMIN_SECRET_STORAGE_KEY`; follow the environment settings in `config.py`. Local
stored settings can override `.env` provider choices, so inspect this if a model name
seems unexpected. Keep the encrypted settings file and its key together when backing up.
Cloud admin stays disabled. Never copy local settings/ledgers into a public deployment.

Read [local setup](LOCAL_SETUP.md) for cycle commands and [Vercel](VERCEL_PREVIEW.md)
for the shared cloud cap. Investigate request IDs and outcome codes without logging
patient content. Do not create new cycles just to hide failed attempts.
