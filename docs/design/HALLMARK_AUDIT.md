# Hallmark slop test, v4 (2026-10-06)

Skill: `.claude/skills/hallmark` (nutlope/hallmark @ 13ac0ec). Genre modern-minimal, verb redesign, multi-page. Checked on the rendered pages in both themes (58 screens each, `tests/browser/screens.cjs`) and on the CSS.

Pre-emit critique (1 to 5): Philosophy 4 · Hierarchy 4 · Execution 4 · Specificity 5 · Restraint 5 · Variety 3. Variety is intentionally low: on a multi-page product Hallmark asks for one shared system, not a different structure per page.

| Gate | Result | Note |
|---|---|---|
| 1 Display font is a default (Inter, Roboto…) | Pass | Geist |
| 2 Gradients, gradient text | Pass | None. A loading shimmer is the only gradient. |
| 3 Three equal icon-tile columns | Pass | Bento of working components, irregular spans |
| 4 Card inside a card | Pass after fix | Mini matrix, quotation versions, staff organization block and the sign-in step no longer draw their own card |
| 5 Side-stripe cards | Pass | |
| 6 Centred full-height hero | Pass | Title left, lede and actions right |
| 7 Pure black or white base | Pass (genre allows white surfaces) | Page background is tinted |
| 8 Generic hero → 3 features → CTA | Pass | Owner-directed Feature Stack with live components |
| 10 `transition: all` | Pass | Properties listed |
| 12 Bounce easing | Pass | Three named easings |
| 14 Animating layout properties | Pass after fix | Bar widths no longer animate |
| 15 Focus ring fades in | Pass | Instant outline |
| 20 Stamp | Pass | `rs.css`, `site.css`, `workspace.css` |
| 22 Zero-chroma neutrals | Pass | Neutrals tinted 0.002 to 0.012 toward hue 295 |
| 23 Accent area over 5 % of a viewport | Pass | Purple only on the brand dot, citations, focus, selection and the value band |
| 24 Spacing off the 4 px scale | Pass after fix | 186 values snapped (2 px and 1 px offsets kept for borders and icon alignment) |
| 27 Motion without reduced-motion fallback | Pass | Global reduce rule |
| 30 Mixed icon sets or emoji icons | Pass | One hand-drawn stroke set |
| 33 Decorative SVG without name or `aria-hidden` | Pass | |
| 34 Horizontal scroll 320 to 1920 px | Pass | Checked at 320, 375, 414 and 768 px on nine pages (seven public pages, `/app`, `/staff`), at 390 and 1440 px on all 58 bundle screens per theme, and at 1280 px on the home page; `overflow-x: clip` on `html` and `body` |
| 37 More than three font families | Pass | Geist, Geist Mono, Noto Sans Thai (script fallback) |
| 40 / 41 Contrast | Pass | Text 4.6:1 or better in both themes (soft text raised for this); heat-map text switches per step |
| 42 AI-default navigation | Pass | N5 floating pill |
| 43 Four-column footer | Pass | Ft1 mast-headed |
| 44 Hero fits 1280×800 | Pass | Headline, lede, both actions, search and the product panels are above the fold |
| 46 Invented metrics | Pass | All numbers computed from catalog, configuration or records; examples labelled |
| 47 Re-drawn browser or phone chrome | Pass | |
| 48 Colours or fonts outside tokens | Pass | One raw value removed from `workspace.css`. Legacy `/lab` CSS is out of scope. |
| 49 Two-line clickable text | Pass | Buttons, tabs, nav and footer links do not wrap |
| 51 Display headings without long-word wrap | Pass | |
| 54 Eyebrow beside heading | Pass | No eyebrows |
| 56 Two sticky elements at `top: 0` | Pass | Filters, price box and summary dock below the navigation |

Open items: Hallmark's root `tokens.css` export is not emitted because `/lab` already owns `static/css/tokens.css`; the v4 tokens are the first block of `static/css/rs.css` (see DESIGN.md).
