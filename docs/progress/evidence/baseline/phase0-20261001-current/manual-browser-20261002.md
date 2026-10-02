# ResultScope Phase 0 browser/manual evidence

- Run ID: `phase0-20261002-browser`
- Local timestamp: 2026-10-02 (Asia/Bangkok; screenshots captured between 13:29 and 13:33)
- Candidate revision: `134c9b6bbb0f2f74c1c14687b2264ea0ba121104`
- Runtime: project `.venv`, `uvicorn main:app --host 127.0.0.1 --port 8011`
- Browser: Chrome DevTools isolated context `resultscope-phase0-20261002`
- Provider credentials: not read, not set, and no external provider call was authorized

## Captures

| Artifact | What it proves |
|---|---|
| `desktop-home-20261002.png` | Initial intake view rendered on desktop before interaction |
| `desktop-out-of-scope-20261002.png` | Local out-of-scope response rendered after an unrelated prompt |
| `mobile-analysis-20261002.png` | Narrow viewport analysis view rendered at 390x844 |

## Manual flow record

1. **Initial desktop view — PASS**
   - The intake page rendered with the `ResultScope` identity, visible `Lab-only system` boundary, `Your Name` owner placeholder, laboratory-result textarea, and signal presets.
   - Screenshot: `desktop-home-20261002.png`.

2. **Out-of-scope prompt — PASS**
   - Input: `ช่วยเขียน Python ให้หน่อย`
   - Observed output heading: `Outside the lab boundary`.
   - Observed response: a deterministic local response in Thai stating that ResultScope accepts laboratory-result questions and suggesting lab examples.
   - Browser network list showed only the local `POST /api/v1/chat/stream` request for this action; no external provider request was observed.
   - Screenshot: `desktop-out-of-scope-20261002.png`.

3. **New-analysis reset — PASS**
   - Action: click `New analysis` after the out-of-scope response.
   - Observed output: intake view returned, textarea cleared, character count reset to `0 / 12,000`, and analysis workspace hidden.
   - Local request observed: `POST /api/v1/chat/reset` returned HTTP 200.

4. **In-scope lab prompt with missing API key — PASS for deterministic/error path**
   - Input: `HbA1c 6.1%. What additional information affects interpretation?`
   - Observed deterministic layer: `1 literal value found`, `HbA1c`, `6.1 %`, `RANGE UNKNOWN`, and `Not supplied` report reference.
   - Observed error: `LLM_API_KEY is not configured. Add it in .env or Vercel Environment Variables before requesting an AI explanation.`
   - Provider-backed narrative: `NOT_RUN` by constraint; no key was read or used.

5. **Lab follow-up — PARTIAL / provider path NOT_RUN**
   - Input: `Should I be concerned?`
   - Observed local request: `POST /api/v1/chat/stream` returned HTTP 200.
   - Because the initial lab request could not establish a provider-backed explanation without `LLM_API_KEY`, the UI rendered the follow-up as an outside-lab local response. A successful provider-backed contextual follow-up remains `NOT_RUN`.

6. **Narrow mobile view — PASS**
   - Viewport: `390x844`.
   - The rendered page remained readable and interactive overall: analysis heading, pipeline rail, extracted-value card, local response, and follow-up form were visible in the captured full-page image.
   - Limitation observed by independent review: the pipeline rail is wider than the 390px viewport, so some rail text is visibly clipped/overflowed. This is recorded as a responsive follow-up issue, not a PASS claim for complete mobile layout.
   - Browser console: no messages found.

## Before/after baseline status

- **B01 business RAG:** `NOT_RUN` — no approved business corpus or RAG route exists in Phase 0 scope.
- **B02 Vision:** `VERIFIED BASELINE LIMITATION` — no upload control or upload route is present; the route inventory and current UI contain no image pipeline. Vision implementation is deferred to a later phase.
- **B03 output/session hardening:** `NOT_RUN` as a before/after security evaluation; this run records only the existing local scope/reset behavior and missing-key guard.

## Measurement limits

- Per-case monotonic latency was not captured by the available browser evidence path; latency metrics remain `NOT_RUN`.
- Live provider, deployment, real business data, and credential-backed flows remain `NOT_RUN`.
