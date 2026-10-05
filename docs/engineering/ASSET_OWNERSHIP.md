# Asset ownership and evidence policy

Status: maintained English guidance. Prepared 2026-10-05 for the documentation-only
sidecar on repository HEAD `12ccb8a27428f819386fa17c4412c764de0f1867`.

This record names the assets that may be used as current product evidence, the
assets that are historical or synthetic, and the notices that must travel with
third-party material. It does not grant a license, certify a source, or approve
production or clinical use.

## Ownership rules

- Maintained product and developer guidance is English. Thai corpus, evaluation
  fixtures, source snapshots, and historical evidence remain in their original
  language and are not rewritten by asset maintenance.
- Every screenshot, diagram, poster, or media composition must have an owner,
  source or generation method, data mode, candidate association, and license or
  rights note before it is used as evidence.
- A screenshot may show the actual interface while still containing mocked OCR,
  mocked answer data, synthetic sources, or offline provider states. Captions and
  manifests must identify those boundaries.
- Asset provenance does not change application authority. Python remains the
  authority for scope, supplied ranges, evidence checks, and output validation.
- Do not remove a notice, replace a source license with a project license, or
  describe a historical or mocked asset as live validation.

## Maintained asset register

| Asset area | Canonical paths | Status and permitted use | Owner / maintenance rule |
|---|---|---|---|
| Application identity | `static/img/mark.svg`, `static/img/logo.svg`, `static/img/favicon.svg`, and their raster companions | Current ResultScope identity assets; no hospital, certification, or affiliation claim | ResultScope maintainers; update only with the approved product identity |
| Self-hosted fonts | `static/fonts/plex-*.woff2`, `static/fonts/NotoSansThai.ttf`, `static/fonts/*-OFL.txt` | Runtime fonts; licenses travel with the files | ResultScope maintainers; preserve the OFL notices and source attribution |
| Self-hosted browser dependencies | `static/vendor/marked.min.js`, `static/vendor/purify.min.js`, `static/vendor/gsap.min.js`, `static/vendor/*LICENSE*`, `static/vendor/GSAP-NOTICE.md`, `static/vendor/SOURCES.json` | Local runtime dependencies; no remote CDN is required by the application | ResultScope maintainers; preserve upstream headers, versions, notices, and source records |
| Active application UI | `templates/`, `static/css/`, `static/js/` | Current implementation; behavior and accessibility are established by code and focused checks, not by screenshots alone | ResultScope maintainers; review changed behavior against the product and safety contracts |
| Current UI screenshots | `docs/assets/screenshots/` and `docs/assets/screenshots/CAPTURE_MANIFEST.json` | Maintained evidence of the interface. The manifest distinguishes actual UI, synthetic values, mocked OCR, mocked SSE, offline states, and mobile behavior | ResultScope maintainers; bind captures to a candidate and keep captions honest |
| Current diagrams and manuals | `docs/assets/diagrams/`, `docs/user/`, `static/docs/`, and `docs/user/ResultScope_User_Guide.pdf` | Maintained English explanatory material; diagrams and manuals describe current boundaries and proposed integrations separately | ResultScope maintainers; regenerate only when the described implementation changes |
| Capture fixtures | `docs/assets/capture-fixtures/` and `examples/coursework_demo_v1/` | Synthetic or de-identified demonstration/evaluation material; never patient evidence or release content | ResultScope maintainers; preserve synthetic labels and fixture provenance |
| Optional presentation source | `docs/media/resultscope-intro/`, `docs/media/intro-poster.png`, and `docs/media/README.md` | Editable presentation reference using local GSAP. HyperFrames player/artifact integration is unavailable; HyperFrames CLI/render validation is `NOT_RUN` | ResultScope maintainers; do not present this source as a deployed HyperFrames runtime or provider evidence |
| Pinned public-reference evidence | `vendor/resultscope_evidence_v1/` | Pinned source package with its own manifests, rights notes, and verifier; not automatically approved commercial content | ResultScope maintainers; preserve bytes, manifests, attribution, and non-commercial restrictions |
| Historical archive | `docs/archive/`, historical evidence indexes, and retained source snapshots | Historical record only; useful for provenance and prior decisions, not current setup or approval | ResultScope maintainers; preserve original language and evidence meaning |

## Reference-only material

The following root attachments are retained as references and are not maintained
product evidence, source corpus, or release inputs:

- `RESULTSCOPE_AUDIT_12ccb8a.md`
- `ResultScope_ Your lab results, explained-1.png`
- `Report canvas_ haemoglobin in context-2.png`

They must not be staged as part of this documentation sidecar, used as proof of
live provider behavior, or deleted by a broad cleanup. Their presence does not
change the ownership or review status of the maintained assets above.

## License and rights register

The maintained notices are part of the asset set and must remain available:

- `NOTICE.md` records the upstream coursework starter limitation and current
  third-party asset boundary.
- `static/fonts/Plex-OFL.txt` and `static/fonts/NotoSansThai-OFL.txt` accompany
  the self-hosted fonts.
- `static/vendor/marked-LICENSE.md` and `static/vendor/dompurify-LICENSE`
  accompany the marked and DOMPurify copies.
- `static/vendor/GSAP-NOTICE.md` and
  `docs/media/resultscope-intro/THIRD_PARTY.md` preserve the GSAP version,
  source pointer, and standard-license pointer. GSAP is not represented as MIT.
- `vendor/resultscope_evidence_v1/README.md` and its rights/source documents
  govern the pinned public-reference material. Public availability is not a
  commercial redistribution grant.

No asset register entry supersedes an upstream license or source-specific rights
record. Before publication or commercial distribution, resolve open rights with
the relevant owner.

## Change and review protocol

1. Add the asset to the appropriate canonical area rather than a root or
   temporary folder.
2. Record the source, generation method, data mode, candidate SHA when available,
   and license or rights basis.
3. For screenshots, update the manifest and state whether the page, OCR, answer,
   source, and provider stages are actual, synthetic, mocked, unavailable, or
   live. Live wording requires a retained sanitized receipt.
4. For third-party assets, retain the original notice and update the local source
   inventory without rewriting the license text.
5. For historical material, preserve the original bytes and label it as
   historical. Do not convert it into current product or readiness evidence.
6. If no verifiable receipt exists for an exact candidate review, record
   `NOT_VERIFIABLE_FROM_REPOSITORY` instead of inferring review from a nearby
   commit, screenshot, or documentation-only change.

This register is an ownership and evidence boundary, not a production-readiness
statement.
