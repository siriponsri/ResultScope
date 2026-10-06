# Replace the local repository

This ZIP contains the complete ResultScope source under one `ResultScope/` folder. Back up your repository and private state first. Extract to a temporary folder, then copy the CONTENTS of its `ResultScope/` folder over your local repository root. Do not create `ResultScope/ResultScope/`.

Preserve your existing `.env`, `data/`, business encryption key, provider-budget ledger and Git history. They are excluded from the ZIP. Do not delete private state to make a test pass. Review the new `.env.business.example` and merge missing settings; never overwrite a filled `.env` with an example. Install the updated Python dependencies in your existing environment.

Local v3 creates separate encrypted business tables; it does not migrate old v1 records into customer accounts. Existing v2 browser context is not imported as a durable patient record. Use only demonstration accounts/reports for coursework. Hosted databases are mandatory because local cloud filesystems are ephemeral.

Run the commands in README.md, inspect docs/business-v3/VERIFICATION.md, and then follow DEPLOYMENT.md. The deployment configuration is included. Database, LLM/guard, Redis, LINE, payment sandbox and map credentials are supplied by you. No real keys, patient data, actual payments, external deployment or provider spending is included in this package.

DELIVERY_MANIFEST.json records source hashes. Restore from your backup if replacing code creates an incompatible local customization. Never restore a database without the matching BUSINESS_DATA_KEY.
