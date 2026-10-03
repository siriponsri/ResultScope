# Phase 4 Browser Evidence — Remediation Run

Date: 2026-10-03. Local app was served from `127.0.0.1:8051` with
`KNOWLEDGE_MODE=synthetic`, `STORAGE_BACKEND=memory`, and an empty
`LLM_API_KEY`. System Chrome was driven through the already-installed external
Playwright 1.63.0 tool. No credential or live provider call was used.

| Scenario | Result | Evidence |
|---|---|---|
| Desktop intake at 1440px | PASS; `scrollWidth=1440`, viewport `1440` | `phase4-browser-20261003-remediation/desktop-intake.png` |
| Narrow mobile intake at 390px | PASS; `scrollWidth=390`, viewport `390` | `phase4-browser-20261003-remediation/mobile-intake.png` |
| Out-of-scope prompt | PASS; HTTP 200, `intent=unrelated`, `status=refused` | Playwright API probe |
| Missing API key | PASS; HTTP 503, `provider_unavailable`, message contained no key value | Playwright API probe |
| In-scope mocked lab response | PASS; analysis view completed with no error and `unsafe=0` | Playwright mocked SSE probe |
| Lab follow-up | PASS; two analysis surfaces remained visible | Playwright mocked SSE probe |
| New-analysis reset | PASS; starter view returned and response count became zero | Playwright UI probe |
| Vercel environment assumption | PASS; no Upstash values selected `MemoryConversationStore` and `UnavailableExtractionStore` | Local import probe with `VERCEL=1` |

The mocked provider text included an attempted `<img src=x onerror=...>` payload;
the rendered page had zero unsafe `onerror` nodes. The temporary local server
and browser helper were stopped or removed after the run.
