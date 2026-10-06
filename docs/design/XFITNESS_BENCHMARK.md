# Benchmark: X Fitness (another student team), 2026-10-06

Purpose: the owner asked for ResultScope to reach a better level than this project. Labels: **TEXT_OBSERVED**, **NOT_OBSERVED**, **INFERRED**.

## Access

| Target | Result |
|---|---|
| `https://x-fitness-chatbot.onrender.com` in a browser | NOT_OBSERVED: the build environment's egress proxy refuses the host. |
| Same page through the web reader | TEXT_OBSERVED (structure and labels). |
| `/admin` after signing in | NOT_OBSERVED: the dashboard is rendered in the browser after login, which the text reader cannot do. Only the sign-in screen and the page description were read. The credentials the owner shared were not used anywhere else and are not stored in this repository. |

## What X Fitness shows (TEXT_OBSERVED)

- One long landing page: membership plans, class schedule, personal training, points, promotions, location and hours, FAQ.
- A floating chatbot ("X, X Fitness assistant") labelled as simulation mode answering from a knowledge base: 500-character input with a counter, image upload (JPG/PNG/WEBP up to 5 MB, used for payment slips), five sample images, visible processing steps (safety check, retrieval, response), rule codes such as "N-02", source display.
- Member identification by member ID plus the last four phone digits; four test accounts printed on the page.
- A developer panel on the customer page: simulate network failure, simulate a 15-second timeout, show processing steps, show rule codes, API base URL.
- Admin (`/admin`): sign-in with the test account shown on the screen; description says chat inbox, members, payments and chatbot settings; role "Admin · Branch manager".

## Comparison

| Area | X Fitness | ResultScope v4 |
|---|---|---|
| Public site | One page | Ten pages: home, catalog with filters and URL state, package detail, compare, centers, organizations, help, privacy, medical sources, 404 |
| Assistant | One bot, knowledge-base answers | Two roles routed automatically with server-enforced permissions; page-aware dock on every page; full workspace |
| Answer trust | Processing steps shown while waiting; rule codes | Numbered inline citations matched to sources; a "How this was checked" receipt built only after input safety, citation validation, an independent review and output safety have all passed; report values drawn on the range printed on the user's own report |
| Failure handling | Developer toggles on the customer page | Failed turns are kept and offered a Retry without retyping; Stop; staff handoff. Failure simulation stays in the test harness, not on the customer page |
| Images | Slip upload | Lab-report upload with OCR, field-by-field review and explicit confirmation before use; synthetic samples |
| Booking | Class booking rules in text | Live half-hour capacity per center, request, staff confirmation or decline with a reason, reschedule, withdraw, calendar file |
| Payments | Slip image check | Signed test-payment simulator (success, failure, expiry, cancel, refund), idempotent events, amount checks; payment opens only after confirmation |
| Organizations | Not observed | Inquiry form, versioned quotations with PDF, accept latest |
| Staff back office | Inbox, members, payments, chatbot settings (described, NOT_OBSERVED) | Overview that starts with requests waiting for a person, inbox with take-over and reply, appointments, customers with history, payments with state filter, notifications, catalog prices, center capacity, assistant roles, channels and AI budget, audit log |
| Themes | Not observed | Light and dark |
| Evidence | Not observed | 386 automated tests, 27 browser checks, 58-screen approval bundle per theme |

## Taken from the benchmark

1. Character counter on the composer (shown near the 8,000-character limit).
2. A visible account of the checks behind an answer, implemented as a receipt of checks that actually ran rather than an animation while waiting.
3. Staff views for customers and payments (new endpoints `/staff/customers`, `/staff/customers/{id}`, `/staff/payments`).

## Deliberately not taken

- Test accounts and passwords printed on public pages.
- Developer controls on the customer page.
- Identity by member ID plus phone digits; ResultScope uses accounts and keeps report values private to the owner.
