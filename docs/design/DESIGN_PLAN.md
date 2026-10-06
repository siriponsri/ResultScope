# ResultScope design plan v2 (full system)

Design authority for this round: this file + `docs/design/FASTWORK_REFERENCE_AUDIT.md`.
Skills used as manual reference: anthropics/skills `frontend-design`, `pbakaus/impeccable` audit dimensions, `dataviz` for the dashboard charts.

## Brief

A simulated health-check business: individuals and organizations compare packages, request appointments, pay (test only), and understand lab reports with sources. Staff confirm everything that matters. The owner rejected the first chat design as generic ("AI slop") and asked for a full system inspired by Fastwork `/selling`, with a multi-role assistant that never slows customers down.

## Tokens

| Name | Hex | Use |
|---|---|---|
| Paper | `#F8F8FF` | page background |
| Ink | `#21172F` | text, dark panels |
| Night | `#170F22` | hero board, assistant dock header, staff rail |
| Primary | `#4B0082` | actions, selection, focus partner |
| Accent | `#8A2BE2` | focus ring, small highlights on dark |
| Line | `#E6E0EF` | borders |
| Tube amber | `#9A5B00` | "follow-up test" category strip and badge text |
| Tube teal | `#0F6B66` | "organization" category strip and badge text |

Category strips borrow the idea of colour-coded sample tube caps: every package card carries a thin cap colour (purple core, amber follow-up, teal organization) plus a text badge, so colour is never the only signal.

Type: IBM Plex Sans Condensed 600 for display and large numbers (tabular), IBM Plex Sans for reading, Noto Sans Thai for Thai. Sentence case labels; no all-caps eyebrows; no italic accent words.

## Layout principles

1. **Product objects first** (from the Fastwork audit): the home hero shows real objects — the assistant roles with their real availability, a real package card and the real appointment state vocabulary — instead of decorative art.
2. **One deep example per category**: "Browse by need" tabs switch a full package preview.
3. **Two-dimensional status everywhere**: appointment state × payment state, the same badges in the customer workspace and the staff dashboard.
4. **The assistant is a layer, not a destination**: a dock on every public page, aware of the page; answers include one-click shortcuts straight to the product. Two roles only, routed automatically.
5. **Back office is an instrument panel**: dark rail, dense tables, numbers from stored records, every chart has a text/table equivalent.

## Motion (PROVISIONAL_DESIGN until Fastwork motion is observed in a browser)

- One hero entrance: board items rise 12px and fade, 80ms stagger, 520ms total.
- Tabs: panel fades 160ms. Dock: slides 220ms. Status change: 200ms colour transition.
- `prefers-reduced-motion: reduce` removes all movement; content is never hidden behind animation.
- No looping motion, parallax, scroll hijacking or fake "thinking" sequences.

## Review against generic defaults

- Rejected: lavender tinted card grid with identical shadows (v1). Replaced by white cards with cap strips, hierarchy by radius (14/10/8) and a dark product board.
- Rejected: chat-first landing with four starter cards. The assistant became a dock; the landing leads with search, needs and the real flow.
- Kept: purple identity and Plex family from the owner's design system.
