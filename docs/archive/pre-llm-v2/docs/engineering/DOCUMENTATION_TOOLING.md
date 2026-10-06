# Maintaining the illustrated documentation

The package already contains reviewed screenshots, diagrams and a 16-page PDF.
No browser-tool installation is needed to read them. The HTML guide embeds its
images and font and opens directly from disk; its return link targets a running app.

## Source ownership

| Output | Source |
| --- | --- |
| 16 actual UI captures and provenance | scripts/capture_product_docs.cjs |
| Synthetic capture report/analysis | docs/assets/capture-fixtures/ |
| User guide Markdown and standalone HTML | scripts/build_product_manual.py |
| Printable guide PDF | scripts/export_product_manual.cjs |
| Architecture and message-flow artwork | docs/assets/diagrams/*.svg; editable original vector text |
| Optional introduction composition | docs/media/resultscope-intro/index.html |
| Diagram PNGs, intro poster and combined render evidence | scripts/render_product_assets.cjs |

Keep new captures attached to their candidate and data mode. Browser mocks must
remain visibly labelled. Never capture a real API key or patient-identifying data.
Do not present fixed generated-answer fixtures as end-to-end live validation.

## Optional capture prerequisites

Use a separate tooling directory with Node and Playwright. This is not an
application npm dependency and must not introduce a frontend build migration.
Set PLAYWRIGHT_MODULE to the installed module's absolute path if it is not on the
normal Node resolution path. CHROMIUM_PATH optionally selects an existing browser.
Installing tools/browsers may need package-network access, which does not authorize
provider transport. Preserve existing tooling; inspect versions before installing.

Start an isolated ResultScope process on loopback with process-only settings:

- PROVIDER_NETWORK_ENABLED=false; no active live cycle;
- APP_ENV=development; LOCAL_DEMO_MODE=true; STORAGE_BACKEND=memory;
- KNOWLEDGE_MODE=synthetic; PUBLIC_REFERENCE_ENABLED=true;
- LLM_API_KEY and VISION_API_KEY empty;
- ADMIN_PASSWORD_HASH empty only in the isolated child process for demo login;
- ADMIN_SETTINGS_PATH and PROVIDER_BUDGET_PATH under a new temporary directory;
- no VERCEL runtime flag; no owner keys loaded from the local settings file.

Do not rewrite .env or existing settings. Keep the isolated process lifetime short.
After confirming the guard, set DOCS_OFFLINE_CONFIRMED=true for the capture process
and DOCS_BASE_URL to that loopback origin. Run `node scripts/capture_product_docs.cjs`.
The tool reads settings only, blocks external browser origins, labels mocked stages,
and refuses horizontal overflow, JavaScript errors or external browser requests. It also checks native-scroll motion, reduced-motion behavior, missing-GSAP fallback and mobile drawer keyboard behavior.
Server-side safety depends on the explicit offline process settings above.

Review the manifest and screenshots. Then regenerate the textual guide and PDF:

```powershell
python scripts/build_product_manual.py
node scripts/export_product_manual.cjs
```

Visually inspect every changed PDF page for clipping, incomplete screenshots,
incorrect captions and unreadable scaling. Update the verification report with
actual results and stop the temporary server. Do not replace reviewed captures or
manifests simply to obtain a newer timestamp.

SVG and HTML diagrams are editable assets. If code boundaries change, update both
source diagrams and their PNG exports, then inspect node labels and connectors.
The README architecture is conceptual: source and code mapping live in
[ARCHITECTURE.md](ARCHITECTURE.md), not in a decorative illustration.
