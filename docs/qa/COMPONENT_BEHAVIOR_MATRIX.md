# Component behavior matrix (v4, 2026-10-06)

Every visible control, what it does, the server state behind it, and the evidence that it works. Evidence keys: **UI-nn** = browser check in `tests/browser/uat.cjs` (27/27 pass), **S-nn** = screen in the approval bundle (`tests/browser/screens.cjs`, real clicks, both themes), **py** = pytest file. Assistant and OCR text in browser evidence comes from labelled test doubles (MOCKED_TEST_ONLY); it proves the UI and flows, not answer quality.

## Website

| Component | Behavior | Server / state | Evidence |
|---|---|---|---|
| Floating navigation, menu button (≤960 px) | Opens and closes the menu, Escape and outside click close it | none | UI-21, S-63 |
| Theme button (site, workspace, staff) | Switches light/dark, stored per browser, applied before paint | `localStorage rs-theme` (optional) | UI-01, both bundles |
| Hero "Request a time" | Opens the booking view | `/app?view=book` | UI-04, S-30 |
| Hero "Ask a question", closing "Ask a question" | Opens the assistant dock | dock | S-12 |
| Hero search | Submits to the catalog with the query | `GET /packages?q=` | UI-01 |
| Example panels (answer, appointment, report value) | Read-only illustrations, labelled; no buttons | catalog prices via template | S-01 |
| Sources strip | Publishers and counts from the evidence catalog | `knowledge/evidence/catalog.json` | S-01 |
| Bento tiles | Read-only; prices and tests from the catalog; "Request a quotation" link | catalog | S-01 |
| Numbers strip | Counts from catalog, centers, evidence, roles | computed per request | S-01, test_api_contract |
| Need tabs | Switch panels, arrow keys move between tabs | none | UI-01 |
| Comparison matrix tabs | Individuals / Organizations; each column links to booking or quotation | catalog | UI-01, S-01 |
| FAQ tabs and disclosures | Switch topic, open/close answers | policies | S-01 |
| Catalog filters, sort, chips, reset | Live results, URL state, back/forward, empty and error states | `GET /api/business/catalog/search` | UI-02, UI-02b, S-02, S-03 |
| Compare checkbox and tray | Up to three, tray actions, clear | sessionStorage | UI-03, S-02b |
| Compare page | Included tests, prices, differences | `GET /catalog/compare` | UI-03, S-05 |
| Package detail actions | Request an appointment, ask the assistant, add to comparison | catalog | UI-04, S-04 |
| Organization form | Sign-in step, validation, submit inquiry | `POST /organizations/inquiries` | UI-10, S-07 |
| Center actions | Request a time here, packages offered, map link | branches | S-06 |
| Assistant dock | Page-aware context, send, stop, retry, shortcuts, action previews, staff handoff link | `/chat`, `/chat/retry`, `/stop`, `/confirm` | UI-24, S-12, S-64 |
| Payment simulator | Signed success, failure, expiry, cancel; event log | `/payments/simulator/*` | UI-15, S-33, S-34, test_business_full |
| 404 page | Website paths show a page with ways back; API keeps JSON | exception handler | test_business_backoffice, S-11 |

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
| My reports | Review fields against the source image, confirm with consent, use, use as previous, delete with history | `/reports/*` | UI-09, S-25 to S-27 |
| Notifications | Real event list, open link, mark all read | `/notifications` | UI-14, S-37 |
| Past conversations | Read archived conversations | `/history` | covered by `/new-chat` tests |
| Connection status | Integration modes, access code for the tab | `/modes` | S-20 |

## Staff desk (`/staff`)

| Component | Behavior | Server / state | Evidence |
|---|---|---|---|
| Sign-in | Staff accounts only; branch staff cannot see manager tools | session, role | UI-11, UI-17, UI-19, S-40 |
| Nav counts | Requests awaiting confirmation, cases waiting | `/staff/dashboard` | S-41 |
| Overview: requests waiting | Oldest first; Confirm, Decline with a reason shown to the customer | `/staff/bookings/{id}/decision` | UI-13, S-41, S-42 |
| Overview numbers and charts | Computed from records; capacity heat map with legend; links to views | `/staff/dashboard` | UI-23, S-45 |
| Inbox | Filter, open case, take over, return to assistant, close, reply, organization details, quotation versions | `/staff/tickets/*`, `/staff/quotes` | UI-11, UI-12, UI-16, S-43, S-44 |
| Appointments | Filter by state, confirm, decline, record center payment, approve refund (manager) | `/staff/operations`, `/settle`, `/refund` | UI-13, S-46 |
| Customers | Search by email, history dialog (appointments, cases, quotations, payments, report counts only), open case; audited | `/staff/customers`, `/staff/customers/{id}` | UI-25, test_business_backoffice, S-47, S-48 |
| Payments | Totals, state filter, signed-event counts, center receipts | `/staff/payments` | UI-25, test_business_backoffice, S-49 |
| Catalog and prices (manager) | Edit price and availability, reaches site and assistant | `PUT /staff/catalog/{id}` | UI-17, S-50 |
| Centers and capacity (manager) | Visits per slot, applies to new requests | `PUT /staff/branches/{id}` | UI-23, S-51 |
| Assistant roles (manager) | Pause and resume a role | `PUT /staff/dots/{id}` | UI-23, S-52 |
| Channels and budget (manager) | Integration modes, AI budget (project total), LINE simulator send and run | `/modes`, `/staff/budget`, `/staff/line-simulator/*` | UI-18, S-53 |
| Audit log (manager) | Who did what, no message contents | `/staff/audit` | UI-23, S-54 |
