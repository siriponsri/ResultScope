# Local agent acceptance handoff

Work from the extracted repository root. Preserve .env, data, keys and budget counters. Use a separate temporary test database. Never push, deploy, spend, send LINE messages or charge money solely because a checklist exists. The owner controls the external test cycle and credentials.

1. Read PRODUCT.md, 03_ARCHITECTURE.md, DEPLOYMENT.md and VERIFICATION.md. Record source manifest hash, OS, Python version and selected provider/model IDs.
2. Install requirements-dev.txt, run python -m compileall -q main.py config.py routers services tests and python -m pytest -q. On Windows run scripts/check.ps1; the bundled result was Linux only.
3. Run python scripts/verify_medical_sources.py. Verify all six supplied artifacts and keep expected_results.json outside runtime/RAG. Export LightRAG inputs only from the approved catalogue.
4. Install npm dependencies and Chromium, then npm run uat:business. This starts the isolated fixture server, not the real model. Inspect desktop/mobile report preview, composer/send visibility, staff queue and screenshots. Do not label these OCR/LLM quality results.
5. Configure an explicitly bounded live cycle. Confirm Typhoon, guard and optional OCR/LightRAG endpoints in setup status. Stop on unavailable guard, auth error or budget exhaustion; never turn safety off or reset counters to retry.
6. Execute tests/uat_cases.json: ten text questions, six image cases and five safety cases first. Record exact final answer, total elapsed milliseconds, model IDs, citations, expected/actual fields, pass/fail and evidence file. Use the test clock only as a fixture; choose valid future dates for live bookings.
7. For each image, submit actual pixels; compare returned fields to the oracle only in the evaluator. Never paste oracle rows into an OCR request. Confirm fields only after reviewing the source. A failed critical numeric/unit/range/flag field fails the image case even if prose sounds plausible.
8. Execute Week 11 G01–G08 against the teacher-compatible guard service using the supplied Postman collection. G07 needs an isolated service configured with a deliberately invalid upstream key; never alter the working service secret. Test CORS in a browser as well as HTTP headers.
9. Run live PostgreSQL, LINE, Stripe TEST mode, maps and LightRAG acceptance cases. Record signed-event dedup, expiry, consent/unlink, amount mismatch and worker failure. No real card/health data.
10. Complete three matched before/after model cases with the same inputs and model configuration. Report regressions too. Do not substitute the offline engineering changes for this coursework requirement.
11. Fill actual student names/IDs/roles; import the report DOCX into Google Docs, verify exported PDF and record the <=180-second demo. Delivery does not claim those submission actions were completed.

Use statuses PASS, FAIL, BLOCKED, NOT_RUN and REVIEW_REQUIRED. No actual answer or latency may be invented. A mock pass, code inspection or provider documentation is not a live pass. Stop the rollout on cross-customer disclosure, unguarded unsafe output, wrong critical OCR value, incorrect price/payment state, leaked credential or mixed-person report context.
