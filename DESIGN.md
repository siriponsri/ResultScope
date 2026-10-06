# ResultScope design (v3, owner direction 2026-10-06)

Direction source: the owner's reference image of the ResultScope chat page (light, editorial, serif, no chat bubbles), applied to the whole system at the owner's request. Fastwork `/selling` remains the structural reference for the marketplace pages (see `docs/design/FASTWORK_REFERENCE_AUDIT.md`). Filter: Anti-Slop (miqdadbadjuber/anti-slop @ 388cbe3, MIT), mode DURING, read as a manual reference, not installed.

Design Read: health-check booking and lab-report explanation service for individuals and HR coordinators in Thailand, in a light editorial (medical document) language, dial **ENERGY 1 / RHYTHM 2 / MOTION 2**.

- ENERGY 1: calm, the content (tests, values, prices, states) is the loudest thing on every screen.
- RHYTHM 2: consistent reading column with deliberate breaks (a catalog table, a value ruler, a timeline of real states).
- MOTION 2: short transitions only on state changes (panel opens, tab switches, a status changes). No scroll reveals, no loops, no fake thinking animation. Reduced motion removes all of it.

## Tokens and one-line reasons (R-31)

| Token | Value | Reason |
|---|---|---|
| Paper | `#FFFFFF` | Reports and explanations are read like documents; white keeps values legible. |
| Ink | `#21172F` | Brand ink from the original system; 15:1 on paper for long reading. |
| Muted | `#61586F` | Secondary text; 6.3:1 on paper. |
| Line | `#ECE8F3` | Hairline dividers separate turns and rows instead of cards and shadows. |
| Primary | `#4B0082` | Brand purple, used for the one primary action on a screen and for prices. |
| Lavender | `#6A5ACD` | Brand lavender for speaker names and text actions; 5.3:1 on paper. |
| Dot | `#9B87E0` | The identity motif: one small dot marks the ResultScope voice (wordmark and assistant turns). Non-text, 3:1. |
| Wash | `#F4F0FC` | Selected column or row in comparisons; the selection is real (what the user asked about), never "popular". |
| Status | ok `#1F6F4A`, warn `#7A4B00`, bad `#A4262C` on light tints | Real booking and payment states only, always with a text label. |

Palette = ink + purple + lavender, dot as the single accent (R-29). No gradients, no glow, no dark sections (R-01, R-13, R-21: the owner's direction is a light document surface; there is no theme toggle because no dark direction was supplied).

Type: **Source Serif 4** (with **Noto Serif Thai**) for headings, conversation and reading text, because the product explains documents and the owner's reference uses a book serif. **IBM Plex Sans** (existing brand font, with Noto Sans Thai) for controls, forms, badges and dense staff tables, so interface chrome is visually separate from the content being read. Sentence case everywhere; no tracked uppercase labels (R-06).

Shape: radius 6 on inputs and buttons, 12 on floating panels (comparison, dialogs), 999 only on the composer and send button, the two things you touch most in a conversation (R-11). Shadow only on panels that float above the page (comparison panel, dialog, assistant dock) (R-12).

Icons: small inline SVGs only where a text action benefits from recognition in a dense row (source, compare, calendar, message, attach, send). No sparkles or AI glyphs (R-04).

## Conflicts with the reference, resolved by the owner (R-37)

| Element in the reference | Rule | Decision |
|---|---|---|
| "Popular" badge on a package column | R-09, R-17: no popularity data exists | Dropped. The column the user asked about is highlighted instead. |
| Tracked uppercase tagline and "POSSIBLE NEXT STEPS" label | R-06 | Dropped. Sentence case. |
| Suggesting a follow-up test right after an abnormal value | Owner brief: no add-on sales from abnormal results | Dropped. The Report Explainer has no sales tools; packages appear only when the user asks the Health-check Advisor. |
| Em dashes in copy | R-02 | Dropped. |
| HK$ prices | Business data | Prices come from the catalog in THB. |

## Surfaces

- Public site: wordmark with dot, text navigation, search, catalog as a scannable table-list, package detail, compare, centers, organizations, help, privacy, sources. The assistant is a dock on every page.
- Customer workspace `/app`: top navigation (no sidebar), centered conversation in the reference layout: speaker row with time, serif turns separated by hairlines, numbered lists only when the content is a sequence, a row of real actions under each answer, a comparison panel that opens beside the answer, a round composer with attach and send.
- Staff `/staff`: light, dense operate mode with a left rail; the overview is built around the decision of the day (requests waiting for confirmation), then capacity and money.

Superseded: v1 Bloom/Genomic home, v2 dark product board. Kept: owner photographs (provenance in `static/img/health/ASSET_PROVENANCE.json`), the `/lab` workspace and its Hyperframes notice.
