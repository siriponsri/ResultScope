# ResultScope local release checklist

This checklist describes a local coursework candidate. It is not a production
release approval.

| Area | Status | Evidence / blocker |
|---|---|---|
| FastAPI root `main.py` and Vercel zero-config shape | PASS | Root ASGI app remains; no legacy `api/index.py` or `vercel.json` added |
| Provider portability and server-only keys | PASS | Existing OpenAI-compatible client; no browser key path; `.env` excluded from artifacts |
| Scope gate before LLM | PASS | Existing scope/Phase 4 tests; unrelated browser probe refused locally |
| Public-reference integrity | PASS | Addon verifier + 50 addon tests |
| Public-reference release/business approval | BLOCKED | Owner-approved business identity, rights, and release corpus are absent |
| Image/OCR contract | PASS (mocked/local) | Phase 3 image and Vision adapter tests; live Vision NOT_RUN |
| First-use UI and mobile layout | PASS for local browser evidence | Phase 5 screenshots/probes; human usability NOT_RUN |
| Full project suite | PASS | `.venv\\Scripts\\python.exe -m pytest -q`: 182 passed, one existing warning |
| Required `scripts/check.ps1` | PASS | `powershell -ExecutionPolicy Bypass -File .\\scripts\\check.ps1`: compileall + 182 tests |
| Independent O1/O2 review | NOT_RUN | Previous dispatcher/runtime/account failures; no approval claim |
| Live LLM, live Vision, external guard | NOT_RUN | No authorized credentials/calls |
| HIS/pharmacy integration | PROPOSED / NOT_IMPLEMENTED | Requires approved contract, consent, and partner access |
| Deployment | NOT_DEPLOYED | Local only by owner instruction |
| Submission/video and human sign-off | NOT_RUN | Owner remains responsible for recording/submission |

Before any future release decision, supply approved business/source rights,
run live evaluations under explicit authorization, obtain independent review,
and update this checklist against that exact candidate SHA.
