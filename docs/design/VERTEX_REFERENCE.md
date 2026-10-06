# Vertex template reference (owner request 2026-10-06)

Status labels: **TEXT_OBSERVED** (read from the public page text), **INFERRED** (likely from the stack, not seen), **NOT_OBSERVED** (could not be checked), **ADOPTED** / **NOT_ADOPTED** (what ResultScope does with it).

## Access

| Source | Result |
|---|---|
| `https://vertex-one-lovat.vercel.app/` in a browser from the build environment | NOT_OBSERVED. The environment's egress proxy refuses the host (HTTP 403 on CONNECT). The owner's computer was not linked to this session. |
| Same URL through the web reader | TEXT_OBSERVED: section order, headings, labels and meta tags. No CSS, fonts or visuals. |
| `skillui --url` (installed for this task) | Ran, extracted nothing (0 colours, 0 fonts): the network was blocked. |
| 21st.dev listing | TEXT_OBSERVED: Next.js 15, Tailwind, shadcn/ui, light and dark themes, dark colour `#09090b`, 10 sections, pricing matrix, bento layouts. Paid template ($49, one payment). |

Licensing: Vertex is a paid template. ResultScope takes **no** code, assets, copy, logos, avatars or testimonials from it. Only general layout and interaction patterns, which are common to the shadcn/ui ecosystem, are used as direction. Hallmark's own `study` verb refuses template-marketplace URLs, so no DNA file was extracted from it.

## Observed structure and what ResultScope did with it

| Vertex (TEXT_OBSERVED) | ResultScope v4 | Decision |
|---|---|---|
| Top navigation: four sections, "Start free trial" and "Book a demo" | Floating pill navigation: Health checks, Organizations, Centers, Help, theme button, My appointments, "Request a time" | ADOPTED as pattern (two actions, one primary) |
| Hero headline, subhead, two buttons | "Know every test before you book." with lede, "Request a time", "Ask a question" and a test search | ADOPTED |
| Prospect cards with activity feeds under the hero (product UI as the visual) | Three live components: an answer with citations and its checks, an appointment with its states, a value on the printed range | ADOPTED with honest labels ("Example", "Synthetic") |
| Logo strip of partner companies | Publishers of the 58 cited public records with record counts | ADOPTED as pattern; logos NOT_ADOPTED (no endorsement exists) |
| "Everything you need..." with dashboard mockups | Bento "From a question to a confirmed visit": comparison matrix, time picker, staff confirmation, report value, test payments, quotation versions | ADOPTED, each tile a real product component |
| Metrics strip (850M+, 120+, 12,000+, 99.99 %) | 18 packages, 3 centers, 58 cited records, 2 assistant roles, all computed | ADOPTED as pattern; invented-style figures NOT_ADOPTED |
| Use-case tabs (Sales, Marketing, Customer, Operations) | Need tabs: core checks, follow-up tests, organizations, under ฿1,000 | ADOPTED |
| Testimonial carousel | None | NOT_ADOPTED: no real reviews exist; fabricated reviews are not allowed |
| Pricing table with Monthly/Annual toggle and feature matrix | "Packages side by side" with an Individuals/Organizations toggle; rows are included tests; each column has its own action | ADOPTED |
| FAQ with tabs (General, Workflows, Pricing) | FAQ with tabs (General, Booking and payment, Reports) | ADOPTED |
| Closing call to action | "Ask a question, or request a time." | ADOPTED |
| Multi-column footer with social links | Mast-headed footer (Hallmark Ft1): wordmark, one line, one row of links, small print | Changed: the four-column footer is a recognised template tell |
| Light theme default, dark theme available | Light and dark token sets, system default, persistent toggle | ADOPTED |
| Fonts, exact colours, motion | Geist, OKLCH palette tuned to ResultScope, 120 to 260 ms transitions | INFERRED from the shadcn/Next stack; NOT_OBSERVED on the page |

## To close the gap

A screen recording or screenshots of the live demo (light and dark, desktop and phone) would let the rhythm, spacing and motion be compared directly. Until then the comparison above is text-only.
