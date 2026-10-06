# Local setup for ResultScope 3

Use Python 3.12 and install requirements.txt. On Windows use START.bat from the repository root. On macOS/Linux follow README.md. Preserve your existing .env and data folder when replacing code. Merge .env.business.example for the new account and business features.

Without credentials, catalog, account, booking and staff records run with local encrypted SQLite. AI conversation and OCR require configured providers and a bounded budget cycle. They never simulate a model answer silently. Create a staff account with scripts/create_staff.py, then sign in at /staff. Keep the generated data/business.key with its database backup.

For hosted PostgreSQL, provider budgets, LINE, Stripe sandbox and maps, follow [the complete deployment guide](../business-v3/DEPLOYMENT.md). For tests, follow [the local-agent handoff](../business-v3/LOCAL_AGENT_HANDOFF.md). The retained /lab workspace uses the v2 configuration and guard pipeline; private browser context is not automatically migrated into a business account.
