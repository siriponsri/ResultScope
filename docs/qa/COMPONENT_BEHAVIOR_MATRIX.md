# Component behavior matrix (v5, 2026-10-06)

Every visible control, what it does, the server state behind it, and the evidence that it works. Evidence keys: **UI-nn** = browser check in `tests/browser/uat.cjs` (29/29 pass on the v5 candidate, `docs/evidence/cowork-20261006/browser-v5`), **S-nn** = screen in the v4 approval bundle (`tests/browser/screens.cjs`; not re-shot for v5 at the owner's request), **py** = pytest file. Assistant and OCR text in browser evidence comes from labelled test doubles (MOCKED_TEST_ONLY); it proves the UI and flows, not answer quality.

## Website

| Component | Behavior | Server / state | Evidence |
|---|---|---|---|
| Navigation bar, menu button (≤960 px) | Opens and closes the menu, Escape and outside click close it | none | UI-21, UI-27 |
| Health checks dropdown | Hover or click opens, Escape and outside click close, arrow keys move through links | none | UI-27 |
| Search dialog (button, Ctrl/Cmd K, /) | Live package search, page shortcuts, "Ask the assistant" with the query; arrows and Enter | `GET /catalog/search` | UI-27 |
| Theme button (site, workspace, staff) | Switches light/dark, stored per browser, applied before paint | `localStorage rs-theme` (optional) | UI-01 |
| Hero buttons | "Request a time" opens booking, "Read my lab report" opens the Lab dashboard | `/app?view=book`, `/app?view=labs` | UI-04, UI-26 |
| Hero search | Submits to the catalog with the query | `GET /packages?q=` | UI-01 |
| Hero helix (Three.js) | Decorative, `aria-hidden`; lazy-loaded, paused off screen, still frame with reduced motion, absent without WebGL | none | self-check screenshots |
| Product deck tabs | Click or arrow keys bring a card forward; auto-advance every 6.5 s, paused on hover, focus and off screen | none (labelled examples) | UI-27 |
| Sources grid | Publishers and record counts from the evidence catalog | `knowledge/evidence/catalog.json` | test_api_contract |
| Two products section | Package counts and lowest price from the catalog; Plus price and limits from `plans.json` | catalog, `business_data/plans.json` | test_business_plans |
| Feature rows, statement | Read-only, labelled synthetic examples; play when scrolled into view | none | UI-01 (no overflow) |
| Numbers and price ladder | Counts and core prices from the catalog; count-up on view | catalog | test_api_contract |
| Need tabs | Switch panels, arrow keys move between tabs | none | UI-01 |
| Question marquee | Each chip opens the assistant with that question; pauses on hover and focus; static with reduced motion | `/app?q=` | manual |
| Pricing matrix tabs | AI Lab Report plans, Individuals, Organizations; each column links to plan, booking or quotation | `plans.json`, catalog | UI-01 |
| FAQ categories and answers | Category tabs (up/down arrows on desktop), [+] and [−] answers | policies, plans | manual |
| AI Lab Report page (`/lab-reports`) | Steps, limits, Free and Plus plans, links to the dashboard and plan | `plans.json` | UI-27, test_business_plans |
| Printable Lab Report (`/lab-report/{id}`) | Loads with the owner's session; print or save as PDF; previous-report column only on Plus | `GET /reports/{id}/lab-report` | UI-26, test_business_plans |
| Payment simulator | Signed success, failure, expiry, cancel; event log; returns to the plan for Plus | `/payments/simulator/*` | UI-15, UI-26, test_business_full |
| 404 page | Website paths show a page with ways back; API keeps JSON | exception handler | test_business_backoffice |
| Catalog filters, sort, chips, reset | Live results, URL state, back/forward, empty and error states | `GET /api/business/catalog/search` | UI-02, UI-02b, S-02, S-03 |
| Compare checkbox and tray | Up to three, tray actions, clear | sessionStorage | UI-03, S-02b |
| Compare page | Included tests, prices, differences | `GET /catalog/compare` | UI-03, S-05 |
| Package detail actions | Request an appointment, ask the assistant, add to comparison | catalog | UI-04, S-04 |
| Organization form | Sign-in step, validation, submit inquiry | `POST /organizations/inquiries` | UI-10, S-07 |
| Center actions | Request a time here, packages offered, map link | branches | S-06 |
| Assistant dock | Page-aware context, send, stop, retry, shortcuts, action previews, staff handoff link | `/chat`, `/chat/retry`, `/stop`, `/confirm` | UI-24, S-12, S-64 |

## Customer workspace (`/app`)

| Component | Behavior | Server / state | Evidence |
|---|---|---|---|
| Header links, menu (≤1100 px), bell, avatar | Navigate views, notifications, account dialog | session | UI-05, UI-14, UI-21, S-21 |
| Conversation bar | Next appointment and its state (links to My appointments); "New conversation" archives the current one | `/workspace`, `/new-chat` | S-36 |
| Welcome prompts and skip links | Send a prompt, or go straight to catalog, booking or reports | `/chat` | S-20 |
| Composer | Enter sends, Shift+Enter new line, grows to 200 px, counter after 6,000 characters, Stop | `/chat`, `/stop` | UI-07, UI-08, S-22 |
| Attach menu | Upload a report or try a synthetic sample | `/reports/read`, `/demos/*` | UI-09, S-29 |
| Answer: inline citation numbers and source list | Numbers match the source list; links open the source | message `sources` | UI-08, S-24 |
| Answer: "How this was checked" | Shows the checks that ran (input safety, citations, independent review, output safety, report values) | message `checks`, stored only after all checks pass | test_business_backoffice, S-22 |
| Answer: report values on the printed range | Value, printed range, state label, ruler drawn only for simple numeric ranges | message `observations`, matched exactly to the confirmed report | test_business_backoffice, S-28 |
| Answer shortcuts | Compare panel, open package, prefill booking, open view, highlight report field; never confirm anything | whitelisted `ui` commands | UI-24, S-23 |
| Action preview card | Send appointment request, keep selection, open test payment, request team; needs an account | `/confirm` | UI-07 |
| Failed turn | Message kept, Retry without retyping, no duplicate | `/chat/retry` | UI-08, S-67 |
| Comparison panel | Opens beside the answer (overlay on narrow screens), Escape closes | `/catalog/compare` | S-23, S-66 |
| Talk to our team | Dialog, queue, assistant pauses, staff reply appears | `/handoffs` | UI-16, S-35, S-36 |
| Health checks view | Search, segment, sort, reset, empty state, request a time, ask | `/catalog/search` | S-38 |
| Booking view | Package, center, date, live capacity per half hour, summary, idempotent submit | `/slots`, `/bookings` | UI-06, S-30, S-68 |
| My appointments | Withdraw, change time, pay (test PromptPay, test card), calendar file, cancel or refund request, decline reason, quotation PDF and accept | `/bookings/*`, `/payments/checkout`, `/quotes/accept` | UI-06, UI-14, UI-15, S-31, S-32 |
| My reports | Review fields against every source page, confirm with consent, open Lab Report, use, use as previous, delete with history | `/reports/*` | UI-09, UI-26 |
| Add a report (Free, Plus) | Free: one AI reading of one image; Plus: up to 3 files or pages at once; over the limit opens the upgrade dialog; a failed reading is returned | `POST /reports/read` (402 `subscription_required`) | UI-26, test_business_plans |
| Lab dashboard | Latest confirmed report with status counts and flagged values; Plus: one chart per test over time, change since the previous report, table view; Free: locked panel | `/reports/{id}/lab-report`, `/reports/trends` | UI-26, test_business_plans |
| Plan | Free and Plus cards, current plan, subscribe or renew (last 7 days) with a test payment, usage | `/plans`, `/subscription`, `/subscriptions/checkout` | UI-26, test_business_plans |
| Notifications | Real event list, open link, mark all read | `/notifications` | UI-14, S-37 |
| Past conversations | Read archived conversations | `/history` | covered by `/new-chat` tests |
| Connection status | Integration modes, access code for the tab | `/modes` | S-20 |

## Staff desk (`/staff`)

| Component | Behavior | Server / state | Evidence |
|---|---|---|---|
| Sign-in | Staff accounts only; branch staff cannot see manager tools | session, role | UI-11, UI-17, UI-19, S-40 |
| Nav counts | Requests awaiting confirmation, cases waiting | `/staff/dashboard` | S-41 |
| Overview: requests waiting | Oldest first; Confirm, Decline with a reason shown to the customer | `/staff/bookings/{id}/decision` | UI-13, S-41, S-42 |
| Overview numbers and charts | Computed from records; capacity heat map with legend; links to views; managers see AI Lab Report metrics (Plus active, revenue, readings) | `/staff/dashboard` | UI-23, test_business_plans |
| Inbox | Filter, open case, take over, return to assistant, close, reply, organization details, quotation versions | `/staff/tickets/*`, `/staff/quotes` | UI-11, UI-12, UI-16, S-43, S-44 |
| Appointments | Filter by state, confirm, decline, record center payment, approve refund (manager) | `/staff/operations`, `/settle`, `/refund` | UI-13, S-46 |
| Customers | Search by email, history dialog (appointments, cases, quotations, payments, report counts only), open case; audited | `/staff/customers`, `/staff/customers/{id}` | UI-25, test_business_backoffice, S-47, S-48 |
| Payments | Totals (including Plus), state filter, signed-event counts, center receipts; manager refund of a Plus period | `/staff/payments`, `/staff/subscriptions/{id}/refund` | UI-25, test_business_backoffice, test_business_plans |
| Catalog and prices (manager) | Edit price and availability, reaches site and assistant | `PUT /staff/catalog/{id}` | UI-17, S-50 |
| Centers and capacity (manager) | Visits per slot, applies to new requests | `PUT /staff/branches/{id}` | UI-23, S-51 |
| Assistant roles (manager) | Pause and resume a role | `PUT /staff/dots/{id}` | UI-23, S-52 |
| Channels and budget (manager) | Integration modes, AI budget (project total), LINE simulator send and run | `/modes`, `/staff/budget`, `/staff/line-simulator/*` | UI-18, S-53 |
| Audit log (manager) | Who did what, no message contents | `/staff/audit` | UI-23, S-54 |
