# DESIGN.md — ResultScope spectral instrument direction

## Design thesis

ResultScope is an **interactive laboratory signal canvas**, not a chatbot wearing a health-tech theme.

The signature is a deep spectral field, instrument-like typography, hard-edged analysis surfaces, and direct manipulation of extracted values. Gradient and motion are allowed only when they communicate signal, depth, focus, or state change.

## Primary interaction

1. Paste a report or ask a laboratory question.
2. Watch one visible sequence: **Read → Verify → Explain**.
3. Receive one integrated analysis object, not a symbolic answer followed by a separate AI answer.
4. Select any extracted value to inspect its supplied range and deterministic status.
5. Open **How this answer was grounded** only when rule-level provenance is useful.
6. Ask a follow-up inside the current laboratory context.

## Anti-AI-slop guardrails

Avoid:

- generic beige SaaS composition;
- floating glass cards and decorative orbs;
- a Three.js wireframe/polyhedron used only to signal “AI”;
- pill-shaped controls everywhere;
- neon glow on every edge;
- robot, brain, sparkle, or magic-wand imagery;
- generic chat bubbles or a transcript as the primary product surface;
- grids of promotional feature cards;
- rounded rectangles without information hierarchy;
- continuous motion unrelated to user input or application state.

Prefer:

- one memorable domain-specific visual system: spectral lines and instrument readouts;
- asymmetrical, hard-edged composition with clipped corners;
- data typography and stable spatial relationships;
- direct value selection and a responsive range inspector;
- progressive disclosure for detailed rule traces;
- transitions that preserve object identity and explain state change;
- high-contrast long-form reading surfaces;
- reduced-motion and keyboard-complete behavior.

## Visual system

- Background: deep ink-to-violet spectral gradient with a pointer-responsive contour field.
- Data accent: cyan for active/verified, restrained red for outside range, green for within, amber for unknown.
- Surfaces: solid dark instrument console and light analysis canvas; no glassmorphism.
- Shape: square/low-radius controls, clipped top-right corners, circular geometry only for status and value markers.
- Typography: Manrope for display, IBM Plex Sans Thai for body, IBM Plex Mono for rules and data.
- Motion: short feedback for controls, interruptible value switching, staged Read/Verify/Explain progress, and no essential information conveyed by animation.

## Responsive contract

- Desktop: narrative introduction + intake instrument; analysis rail + integrated result canvas.
- Tablet: stacked intake; pipeline becomes a horizontal strip.
- Mobile: single column, horizontally selectable value deck, no hidden essential controls, touch targets at least 44 px where practical.

## Accessibility contract

- visible focus states;
- semantic buttons/details/headings;
- status always written in text, never color-only;
- `prefers-reduced-motion` disables nonessential animation;
- canvas is decorative and `aria-hidden`;
- the server owns all flags; JavaScript only visualizes returned metadata.
