# Troubleshooting

| Symptom | Action |
|---|---|
| Models unavailable | Inspect /settings and /api/v2/config; configure keys, guard, access code and a bounded provider cycle. Do not disable safety. |
| Hosted account storage unavailable | Configure DATABASE_URL and the stable BUSINESS_DATA_KEY. Vercel/Render local files are not durable storage. |
| Session or CSRF error | Reload and sign in again. Do not copy another browser's token. |
| Preview expired or price changed | Request a fresh preview; the server does not silently accept a new price. |
| Slot full | Choose a different available date/time. Capacity is checked atomically. |
| Report unreadable | Use clearer pixels or fewer pages; confirm exact fields against the original. Do not use test oracle answers as OCR input. |
| LINE silent | Check webhook signature configuration, worker state, reply expiry, push permission and manager delivery status. Avoid blind replay of uncertain sends. |
| Payment pending | Verify the signed test-mode webhook and order amount. A redirect is not settlement. |
| Map embed missing | Configure a referrer/API-restricted Google Maps Embed key. The link fallback is only an area map. |
| Browser UAT cannot start | Install requirements-dev.txt and Playwright Chromium. Set TEST_PYTHON if your Python environment is outside .venv. |
| Key lost | Restore the matching encryption key from a secure backup. Generating a new key cannot decrypt existing records. |
