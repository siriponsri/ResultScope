# ResultScope 2.0 verification

Date: 2026-10-05. Baseline: `4ac870a14bbd51dddaaeedc6b6c35498152d8654`.
`DELIVERY_MANIFEST.json` in the ZIP lists SHA-256 for each packaged file. The downloadable
ZIP has its own external SHA-256. No remote GitHub mutation or deployment was performed.

## Passed checks

- `python -m pytest -q`: **301 passed**, one upstream Starlette/httpx test-client
  deprecation warning. Includes 51 new v2 tests and preserved legacy regressions.
- Python compilation for main/config/routers/services/tests; JavaScript syntax check.
- Browser verification: **12 checks, 10 screenshots**, desktop 1440×1000, mobile 390×844,
  reduced-motion/keyboard, source library, reset, export and actual Hyperframes player.
- Browser model/report success paths use explicit API doubles. The screenshot manifest
  is `docs/assets/screenshots-v2/CAPTURE_MANIFEST.json`; captures are not model scores.
- Hyperframes 0.8.131 lint: no errors/warnings. Validation: no console errors, 38 text
  elements pass WCAG AA. Layout inspection at 2.8, 5.9, 9 and 11.8 seconds: no issues.
  Chromium Headless Shell worked after default download/full-browser paths failed.
- Six supplied individual PDFs rasterize. The combined six-page PDF is rejected by the
  three-page ingestion cap. Original artifact hashes match the supplied manifest.
- The current two-page printable guide was rendered and visually reviewed.

The skill's standalone animation-map helper could not load its missing
`@hyperframes/producer` dependency. Official lint/validate/inspect and the actual player
were used; no standalone helper success is claimed.

## Not run

Live provider/OCR/guard calls; model factuality/per-language benchmarks; provisioned
LightRAG; remote Upstash concurrency; actual Vercel build/deploy; native Windows execution;
clinical/independent FO review; full coursework video recording. Live call count: **0**.
The automated suite verifies boundaries and flow, not clinical accuracy or provider availability.

## Fixes found in verification

A report-selection variable shadowed the DOM document and blocked preview; browser tests
caught it and the handler was corrected. Responsive animation cleanup restores CSS
transforms. Byte-identical uploaded fixtures retain synthetic classification. Malformed
guard output and non-boolean evidence review results fail closed. DOMPurify was updated
to 3.4.16 with version/hash and license recorded.

## Archive rehearsal

All 423 archive entries were checked, each manifest hash matched, and the ZIP was
extracted into a clean directory. The same 301 tests passed there. A fresh process with
VERCEL=1 and network disabled served the app, settings, sources, demo PDF, guide and
Hyperframes assets successfully; the legacy API returned 410. This is a local cloud-mode
rehearsal, not an actual Vercel platform deployment.

The first clean-archive run exposed a legacy evaluator that required a Git checkout.
Both legacy evaluation writers now label source-archive provenance using the delivery
manifest SHA-256 when `.git` is absent; they do not invent a commit ID.
