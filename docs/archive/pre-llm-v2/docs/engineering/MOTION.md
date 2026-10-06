# Motion and interaction contract

The approved C + 2 direction is implemented in `static/js/experience.js`. It is
presentation code. Provider requests, extraction state and streaming stay in
`static/js/chat.js` and the existing Python boundaries.

## Landing to conversation

Normal page scrolling drives a paused GSAP timeline named `resultscope-entry` in
`window.__timelines`. The hero scales from 1 to 0.88, rises 24px and fades while
the workspace settles from 1.035 to 1. The progress is bounded by the workspace
position. No wheel event is intercepted; there is no sticky pin or forced wait.
Open workspace is an ordinary same-page action with a direct `#workspace` target.
Try an example loads the existing synthetic text without sending a request.

Mobile screens at or below 760px and `prefers-reduced-motion: reduce` use the static
layout. If GSAP is missing, every control and section is still available. The
page has no repeating ambient animation. Diffuse color is CSS background paint.

## Document drawer

Desktop: a right-hand panel beside the conversation. Mobile: a full-screen modal
with background inertness, contained keyboard focus, Escape-to-close and focus
restoration. Closing the panel retains the pending report. Discard image clears
it. After sending an analysis, replacing/discarding its report is disabled until
a new analysis, matching the conversation boundary. A confirmed extraction is
read-only. State labels are driven by the actual extraction lifecycle, never timers.

The drawer does not fetch a provider by opening. Selecting an image uses the
existing OCR endpoint, subject to configuration, offline guard and the shared
budget. Confirmation uses the existing review endpoint. No percentages or
multi-file capability are invented.

## Optional Hyperframes composition

`docs/media/resultscope-intro/index.html` is a separately editable title sequence,
not the website runtime and not a complete walkthrough. Its paused registered
timeline can be sought deterministically. It uses actual v2 screenshots. Browser
seek validation and CLI/export status are recorded in the verification report.

## Verification

`scripts/capture_product_docs.cjs` checks native-scroll progress, reduced motion,
missing-GSAP fallback, mobile dialog semantics, focus containment and restoration,
confirmed read-only fields, discard cleanup and report locking after analysis.
Mocked successful OCR/answer stages are labeled in screenshots. These checks do
not establish live provider quality, clinical validity or assistive-technology
coverage beyond the tested keyboard interactions.
