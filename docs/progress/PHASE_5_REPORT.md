# Phase 5 report — first-use UX

Date: 2026-10-03  
Branch: local `main`

## Delivered on the real home

- The first screen now uses English UI copy and presents one primary action:
  upload a report image or type a question. The LLM is not forced to answer in
  English and may converse in the user's language.
- English examples populate the existing question field. JPEG/PNG upload
  remains real, with server validation, editable OCR fields, confirm/discard,
  and a session-bound extraction ID.
- Results keep the integrated value/range/explanation object. Server-owned
  citation metadata can be opened to see title, organization, page, section,
  version, class, license, and safe original link.
- Duplicate submission is guarded by `requestInFlight`; active SSE requests can
  be stopped; provider/stream/upload/reset failures retain a retry path or
  clear recovery state. Missing ranges remain unknown rather than green.

## Browser evidence

| Check | Status | Evidence |
|---|---|---|
| Desktop first-use home | PASS | `docs/progress/evidence/admin-settings-browser-20261003/desktop-home-en.png`; English UI and real controls rendered |
| Narrow mobile at 390px | PASS | `docs/progress/evidence/admin-settings-browser-20261003/mobile-home-en.png`; no horizontal overflow |
| Out-of-scope refusal | PASS | Local Chrome probe; deterministic refusal rendered without provider |
| Invalid upload | PASS | Local Chrome probe; non-image returned server validation text beside upload |
| Reset | PASS | Local Chrome probe; returned to `data-view=intake` with empty input |
| Missing-corpus/provider recovery | PASS | Local Chrome probe; error visible, retry button present, surface not loading |
| Mock citation disclosure | PASS | Local SSE route probe; organization/page/license/link rendered and surface completed |
| Human first-use comprehension | NOT_RUN | No independent human testers were available; screenshots do not prove comprehension |
| Live OCR/LLM answer quality | NOT_RUN | Owner did not authorize live provider calls |

The existing deep spectral field is retained as the product identity; no glass
cards, fake dashboard, confidence meter, or browser API key was added. Admin
Settings browser checks are recorded separately in
`docs/progress/evidence/admin-settings-browser-20261003.md`.
