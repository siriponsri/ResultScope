# Fastwork `/selling` reference audit

Reference URL: https://fastwork.com/selling (owner-designated primary UI inspiration).
ResultScope keeps its own brand, purple palette and health-check business. Nothing below is copied: no Fastwork text, images, logos, seller names or source code.

## Evidence status

| Method | Date | Result | Status |
|---|---|---|---|
| `curl` from the cloud sandbox | 2026-10-06 | Proxy refused CONNECT (organization egress policy) | BLOCKED |
| WebFetch text extraction (markdown summary, no pixels) | 2026-10-06 | Section order, headings, CTA labels and component types described | TEXT_OBSERVED |
| Real browser screenshots at 390 / 768 / 1440 | — | Requires the owner's linked computer or an owner screen recording | NOT_RUN |
| Motion (timing, easing, scroll behaviour) | — | Not observable from text extraction; no library names were exposed | NOT_OBSERVED |

Everything marked *Observed* below comes from the text extraction only. Visual sizes, colours, spacing, motion and responsive behaviour are **not** observed and are recorded as `PROVISIONAL_DESIGN` in ResultScope until a browser inspection is done.

## Observed → interpreted → applied

| Observed (text) | Interpreted principle | Application in ResultScope | What we do not do | Evidence |
|---|---|---|---|---|
| Hero shows a row of creator profiles with name, profession, location and online status, then the headline and a single "Get started" CTA | Show the product's real objects in the first screen instead of abstract illustration | Hero shows live objects from the database: the assistant roles (Dots) with their availability, a real package card and a real appointment card with server status | No fake people, no invented online counts | WebFetch 2026-10-06 |
| Tabs by profession switch a full profile card (stats, cover, services, gallery, tabs for Portfolio/Services/Reviews/About) | Let a visitor explore one concrete example deeply, by category | "Browse by need" tabs switch a full package preview (included tests, centers, price, booking route) fetched from the catalog | No ratings, review counts or earnings figures | WebFetch |
| Fee comparison: own clients 0 % vs platform clients 18 % then 0 % | Make the money model explicit and comparable | "How booking and payment work" comparison: request → staff confirmation → pay at center or test payment; organization quotation path | No discounts or fee claims | WebFetch |
| Order cards with status pairs (Held/New, Paid/In progress, Unpaid/New, Paid/Delivered) and a quotation card | Status is two-dimensional (money × work); show it as compact cards | Appointment cards show booking state × payment state separately; quotation cards show version and validity; the same components appear in the customer workspace and staff dashboard | No "urgent" styling to pressure payment | WebFetch |
| Headline sequence: capability → people need people → pain → fees → one platform → portfolio → discovery → secure payment | Narrative goes from identity, to reassurance, to mechanics, to trust | Home sequence: find/ask → people + AI roles → browse by need → how it works → reports with sources → centers → organizations → questions | — | WebFetch |
| Countdown timer in hero | Promotional urgency | **Not applied** (owner brief forbids urgency timers) | Countdown, scarcity | WebFetch |
| Rotating testimonial cards with 5.0★ | Social proof | **Not applied** (no fake reviews); replaced by source transparency and simulation labels | Testimonials, star ratings | WebFetch |
| Terms-update banner with "Accept and continue" | Persistent, dismissible notice | Simulation strip on every page with a real link to /help#simulation | — | WebFetch |

## Motion plan (PROVISIONAL_DESIGN, not derived from observation)

Purpose-only motion, all under 300 ms except one hero entrance, disabled by `prefers-reduced-motion`:
- Tab switch: content cross-fade 160 ms; indicator slides under the active tab.
- Card state change (e.g. booking confirmed): status badge colour transition 200 ms plus a single highlight pulse on the changed record.
- Assistant dock open/close: 220 ms slide from the bottom-right; focus moves into the dock.
- Hero: one staggered entrance of the live objects (≤ 600 ms total), no looping animation.
- No scroll hijacking, parallax or progress animations that imitate AI thinking.

Replace this section with observed timings after browser inspection.
