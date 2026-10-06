# ResultScope design (v5, owner direction 2026-10-06)

This file is the locked design system for every page. Page CSS reads tokens from `static/css/rs.css`; nothing else defines colours or fonts.

## Direction and sources

- **Owner direction (2026-10-06):** follow the UX of the Vertex landing template (Ruixen UI on 21st.dev, live demo `vertex-one-lovat.vercel.app`) with a light and a dark theme, keep the ResultScope palette but do not let purple dominate, and stay minimal. Apply it to the whole system: website, customer workspace and staff desk.
- **What was used from Vertex:** structure and UX patterns only, as observed in a text reading of the public demo and the 21st.dev listing (see `docs/design/VERTEX_REFERENCE.md`): pill navigation with two calls to action, a hero followed by real product components instead of illustrations, a bento of features shown as working UI, a numbers strip, a side-by-side comparison matrix with an audience toggle, a tabbed FAQ, a closing call to action, and light/dark themes on a near-black `#09090b`-class dark surface. The template is a paid product. No code, assets, copy, logos or testimonials were taken, and the page could not be loaded visually from the build environment.
- **Filter:** Hallmark (`nutlope/hallmark` @ 13ac0ec, MIT, installed as a project skill in `.claude/skills/hallmark`), genre **modern-minimal**, verb **redesign** (multi-page, so this one system for every page). Earlier filters (Anti-Slop by miqdadbadjuber, frontend-design) remain consistent with it.
- **Fastwork `/selling`** stays the reference for marketplace mechanics (search-first catalog, category switch, compare). See `docs/design/FASTWORK_REFERENCE_AUDIT.md`.

Inferred brief (stated because the owner asked us not to stop for every detail): audience = people in Thailand choosing a health check or reading a lab report, plus HR coordinators and clinic staff; use = compare, ask, request a time; tone = utilitarian, calm, technical.

## v5 changes (owner direction, later on 2026-10-06)

The owner supplied a PDF print and screenshots of the Vertex demo and asked for the UI to follow it more closely, with rich, modern motion (Three.js and Next.js allowed). What changed from v4:

- **Structure taken from the PDF:** full-width navigation bar (logo, centred links with a dropdown, search, theme, sign-in text link, primary button); two vertical rails framing every page, with dashed, hatched spacer bands between sections; a centred hero (pill badge, heavy serif headline, lede, two buttons, small underlined credit); a stacked card deck with a floating tab bar; a bordered source grid; single-column feature rows with dashed separators; a large centred statement; 2x2 numbers with left rules and a chart; a pricing matrix with grouped rows and a sticky header; a two-column FAQ with [+] and [−] toggles; a multi-column footer with serif group headings.
- **Display serif:** Source Serif 4 (variable, optical size 60, weight 700; SIL OFL) for `h1`, `h2` and display text through `--font-display`, with Noto Serif Thai for Thai. Body stays Geist.
- **Motion:** `static/js/motion.js` (split headline, scroll reveals, count-up, deck auto-advance that pauses on hover, focus and when off screen, scroll-lit statement, question marquee, in-card sequences, chart line drawing) and a Three.js helix in the hero (`static/js/src/hero3d.src.js`, bundled to `static/js/hero3d.js` by `npm run build:3d`, lazy-loaded after `load`, paused off screen and in hidden tabs, one still frame with reduced motion, skipped with Save-Data, absent without WebGL). Motion classes are set before first paint; a CSS fallback shows all content after 2.5 s if the script never runs. `prefers-reduced-motion` turns all of it off.
- **Next.js was not used.** It would add a second runtime and rewrite flows that are already tested end to end; the owner allowed it but did not require it.
- **Two products:** the home page presents health-check packages and the AI Lab Report side by side; `/lab-reports` is the product page; the workspace gains a Lab dashboard and a Plan view.
- **Text wrapping:** headings use `text-wrap: balance`, running text `text-wrap: pretty`, and short units are kept together with `.nowrap`. An automated browser check (one-word last lines) reports zero across the site and workspace at 360 to 1440 px.

## Tokens (OKLCH, light and dark)

| Token | Light | Dark | Reason |
|---|---|---|---|
| `--color-bg` | `oklch(99.3% 0.002 295)` | `oklch(14.5% 0.004 295)` | Near-white and near-black with a trace of the brand hue, so neutrals are not flat grey. |
| `--color-surface` | `oklch(100% 0 0)` | `oklch(17.5% 0.006 295)` | Cards and panels lift by surface, not by shadow. |
| `--color-border` | `oklch(91.5% 0.006 295)` | `oklch(26.5% 0.01 295)` | Visible thin borders (modern-minimal), not editorial hairlines. |
| `--color-fg` / `-muted` / `-soft` | 20.5% / 48% / 56% | 96.5% / 71% / 60% | 17.6:1, 6.4:1 and 4.6:1 on the page in light; 17.9:1, 7.7:1 and 5.0:1 in dark. |
| `--color-primary` | ink | near-white | The main action is monochrome (ink-filled pill in light, white pill in dark), as in the reference. |
| `--color-accent` | `oklch(46% 0.17 297)` | `oklch(76% 0.12 295)` | ResultScope purple, kept for the brand dot, citations, focus rings, selected states and the value band. Never a fill for large areas. |
| status ok / warn / bad | text 45–48% on 96% tints | text 76–82% on 26–27% tints | Real booking and payment states only, always with a text label (6.0:1 or better). |
| heat 0–4 | 97% → 45% purple | 21% → 78% purple | One-hue sequential ramp for capacity; text colour switches per step to keep contrast. |

Theme selection: the site follows the system setting until the visitor presses the theme button; the choice is stored per browser (`static/js/theme.js`, loaded in `<head>` so there is no flash). Both themes are complete token sets; nothing is auto-inverted.

## Type

**Geist** (variable, OFL) for body and interface, with **Noto Sans Thai** for Thai script through `unicode-range`; **Source Serif 4** for display headings (v5); **Geist Mono** for references and small labels. Headings 600, tight tracking (`-0.02` to `-0.03em`), always upright. Sizes come from the `--text-*` scale; the display size is `clamp(2.5rem, 4.2vw + .6rem, 4.25rem)`.

## Shape, depth and motion

- Radius: 8 to 14 px on fields and cards, 20 px on large panels, pill on buttons, chips, tabs, the navigation and the composer.
- Depth: borders and surface steps. A soft shadow only on things that float (navigation pill, dock, dialogs, compare tray, dropdowns); in dark mode floating things get a border ring instead.
- Motion: interface feedback 120 to 260 ms; website choreography up to 1.4 s (reveals, headline, chart lines), `transform` and `opacity` only, named easings, no bounce. `prefers-reduced-motion` removes all of it, and the Three.js hero shows one still frame.

## Structure (Hallmark stamps)

- Website (v5): macrostructure **Railed Feature Stack** (centred hero with helix, product deck, source grid, two products, feature rows, statement, numbers with price ladder, needs tabs, question marquee, pricing matrix, two-column FAQ, closing call to action), nav **full-width bar with dropdown and search**, footer **multi-column**.
- Customer workspace: **Workbench**. Header with pill links, a centred conversation column, the composer as a pill, the comparison panel beside the answer.
- Staff desk: **Workbench** with a quiet side rail; the overview starts with the requests that need a person.

## Honest content rules (kept from v3)

- Every number on a page is computed from the catalog, configuration or stored records. No invented metrics, logos, testimonials or ratings.
- Example panels are labelled "Example" or "Synthetic". They never contain buttons that do nothing.
- No add-on selling after an abnormal value: the Report Explainer has no sales tools; packages appear only when the Health-check Advisor is asked.
- No em dashes, no tracked uppercase labels, no gradient text, no glow, no fake browser or phone frames.
- The question marquee shows real prompts that open the assistant, not testimonials. The sources grid shows real publishers and record counts, not customer logos.

## Known deviations (recorded for the slop test)

- v5 centres the hero and uses rich motion. Hallmark's modern-minimal genre prefers a left-aligned hero and restrained motion; this is the owner's explicit direction and is recorded here.

- Spacing values are mostly on the 4 px scale; a number of component paddings (7, 9, 18 px) predate the scale and are listed in `docs/design/HALLMARK_AUDIT.md`.
- Hallmark asks for a root `tokens.css`; tokens live at the top of `static/css/rs.css` instead because the legacy `/lab` workspace already owns `static/css/tokens.css`.

Superseded: v1 Bloom/Genomic home, v2 dark product board, v3 editorial serif (owner reference image). Kept: owner photographs (provenance in `static/img/health/ASSET_PROVENANCE.json`), the `/lab` workspace and its notice.
