---
name: ResultScope Laboratory Assistant
description: A clear laboratory conversation with diffuse violet atmosphere and solid reading surfaces.
colors:
  paper: "#F8F8FF"
  surface: "#FFFFFF"
  ink: "#21172F"
  muted: "#61586F"
  primary: "#4B0082"
  primary-hover: "#390064"
  accent: "#8A2BE2"
  lavender: "#6A5ACD"
  secondary: "#483D8B"
  tint: "#F1EBFC"
  line: "#DED8E9"
  control-line: "#8D819D"
  amber: "#8A521D"
  amber-tint: "#FFF5E8"
  red: "#A62E4A"
  red-tint: "#FFF1F4"
  focus: "#6A5ACD"
typography:
  display:
    fontFamily: '"Plex", "Noto Thai", sans-serif'
    fontSize: "clamp(48px, 6.3vw, 88px)"
    fontWeight: 500
    lineHeight: 1.06
    letterSpacing: "-0.04em"
  headline:
    fontFamily: '"Plex", "Noto Thai", sans-serif'
    fontSize: "24px"
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: "-0.025em"
  title:
    fontFamily: '"Plex", "Noto Thai", sans-serif'
    fontSize: "17px"
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: "-0.025em"
  body:
    fontFamily: '"Plex", "Noto Thai", sans-serif'
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: '"Plex", "Noto Thai", sans-serif'
    fontSize: "14px"
    fontWeight: 500
    lineHeight: 1.6
  compact-label:
    fontFamily: '"Plex", "Noto Thai", sans-serif'
    fontSize: "13px"
    fontWeight: 500
    lineHeight: 1.6
  narrative:
    fontFamily: '"Plex", "Noto Thai", sans-serif'
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.8
rounded:
  textarea: "2px"
  progress: "4px"
  compact: "6px"
  control: "7px"
  surface: "8px"
  admin: "10px"
spacing:
  small: "8px"
  compact: "12px"
  medium: "16px"
  reading: "20px"
  large: "24px"
  shell: "32px"
  section: "48px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "10px 18px"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-hero:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "12px 22px"
  button-send:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "8px 14px"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "10px 18px"
  button-secondary-hover:
    backgroundColor: "{colors.tint}"
  button-report:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.compact-label}"
    rounded: "{rounded.control}"
    padding: "8px 12px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.compact}"
    padding: "12px 14px"
  composer:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.surface}"
    padding: "16px"
  analysis-surface:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.surface}"
  metric-selected:
    backgroundColor: "{colors.tint}"
    textColor: "{colors.ink}"
    rounded: "{rounded.compact}"
    padding: "13px"
---

# Design System: ResultScope Laboratory Assistant

## Overview

**Creative North Star: "The Violet Laboratory Workspace"**

ResultScope is a calm, formal medical workspace with a diffuse violet introduction and a focused laboratory conversation. Ghost-white paper, dark purple ink, and solid white reading surfaces keep supplied information easy to inspect. Deep indigo identifies the main action and selected values; violet and lavender provide atmosphere around the work.

The approved C + 2 direction lets the centered introduction recede into the real workspace on native desktop scroll. Conversation, report review, explanation, and sources remain ordinary, readable controls. Diffuse gradients in the hero and chat, the large introductory heading, and the bounded scroll transform are explicit owner-approved exceptions; they do not extend to glass panels, decorative canvas, a workflow editor, or continuous ambient animation.

**Key Characteristics:**

- Ghost-white paper, dark purple ink, and solid answer and form surfaces.
- Diffuse violet and lavender atmosphere confined to the hero and chat.
- A native-scroll introduction with static mobile, reduced-motion, and no-GSAP timeline fallbacks.
- A compact composer and a report drawer that preserves the current conversation.
- Self-hosted English and Thai typography with visible keyboard focus.

This document records the implementation in `static/css/tokens.css`, `static/css/style.css`, `static/css/admin.css`, `templates/index.html`, `static/js/experience.js`, and `static/js/chat.js`. The [approved direction](docs/engineering/APPROVED_UI_DIRECTION.md) supplies visual authority. Retained screenshots illustrate the interface; labelled mocked OCR and answers are not live-validation evidence. This design description makes no readiness claim.

## Colors

The owner palette combines ghost white, vivid violet, deep indigo, slate lavender, and dark slate violet. Frontmatter is the normative token inventory; keys match the CSS custom properties in `static/css/tokens.css`. Component-specific alpha blends and one-off surface shades remain in CSS and the sidecar snippets.

### Primary

- **Deep indigo — primary:** Solid primary actions, ordinary links, selected values, and active/complete workflow states. **Primary hover** deepens the button fill without scaling it.
- **Vivid violet — accent:** Diffuse hero and chat atmosphere, used through alpha gradients rather than as a text backdrop that competes with the content.
- **Pale violet — tint:** Selected values and quiet hover feedback. The active implementation uses solid white composers, including follow-up.

### Secondary

- **Slate lavender — lavender:** A second atmospheric hue. The separate **focus** token shares this value and identifies keyboard focus.
- **Dark slate violet — secondary:** Header links, attachment actions, suggestion labels, and report-related secondary text.

### Neutral

- **Ghost white — paper:** Page background and quiet inset areas.
- **White — surface:** Workspace framing, composers, report drawer, responses, and administration.
- **Purple ink — ink:** General content and controls. **Muted** supports helper text and metadata.
- **Quiet lavender line — line:** Fine section borders. **Control line** is darker and marks editable fields and composer edges.

Amber and its tint identify supplied-range exceptions and synthetic-data notices. Red and its tint identify errors. These are operational labels, not diagnoses or urgency scores. Existing `--teal`, `--teal-dark`, and `--teal-tint` names are compatibility aliases to the purple primary, hover, and tint tokens; they do not define an additional palette.

**The Written Status Rule.** Every meaningful range, error, or workflow state has a text label; color alone never carries the decision.

## Typography

**Display and body font:** The local CSS alias **Plex** loads IBM Plex Sans from `static/fonts/plex-400.woff2`, `plex-500.woff2`, `plex-600.woff2`, and `plex-700.woff2`. **Noto Thai** loads Noto Sans Thai from `static/fonts/NotoSansThai.ttf` for Thai text. The shared stack ends with `sans-serif`; there is no separate promotional display face. A system monospace alias exists for technical content, but it does not define the visible conversation's main hierarchy.

The frontmatter records the actual default ramp. Most headings and action labels use medium weight; selected large readings and some form labels use semibold. The introductory display is centered, tightly tracked, and balanced across lines. Operational titles are smaller and left aligned. Body copy uses a relaxed reading rhythm; supporting metadata remains subordinate.

- **Display:** Hero heading at the fluid desktop size in the frontmatter; it changes to `clamp(48px, 7vw, 76px)` at 1050px and below, then `clamp(40px, 10vw, 58px)` at 760px and below.
- **Headline and title:** Base second- and third-level headings use the frontmatter ramp. The welcome heading is larger (28px desktop, 25px at the intermediate breakpoint, 24px mobile); conversation and drawer headings use 20px.
- **Body and narrative:** General interface text uses the body role. Rendered explanations use the narrative role with a line height of 1.8; mobile narrative text is 14px. The conversation's starter width is capped at 820px and its analysis at 860px.
- **Labels:** Buttons normally use the label role; composer and report labels use the compact role. Small helpers and metadata range from 11px to 13px and do not replace the primary instructions.
- **Values:** The inspector's large numeric reading uses tabular numerals. A selected metric uses a medium 16px value on desktop, reducing to 15px on mobile.

**The Plain Label Rule.** Keep operational labels in sentence case and name the action directly: Open workspace, Send, Report, Confirm values, and Start a new analysis.

## Layout

The page has a centered public introduction followed by a real conversation workspace. The header is capped at 1440px with 48px horizontal desktop padding. The hero is bounded by a 660px minimum and 1000px maximum height, with a viewport-relative height between them. The hero's content caps at 900px and its heading at 880px. The workspace section has 32px horizontal padding; its bordered shell caps at 1320px. The chat has 32px internal padding and uses the available width beside the optional report drawer. The starter and explanation widths remain bounded for reading.

The report drawer is part of the desktop workspace flow, with a white surface and a left divider. It is 400px wide with a maximum of 42% of the shell; its body scrolls independently within a viewport-based height. At 1050px and below, the drawer becomes 360px with a 45% maximum, chat padding becomes 24px, suggestion actions stack, response headers can wrap, and the composer character count is hidden. This is a layout adjustment, not removal of essential actions.

At 760px and below:

- Header padding becomes 18px by 20px; the redundant header Open workspace link hides while the hero action and User guide remain available.
- Hero height is bounded from 540px to 800px, its explicit line break is hidden, and its actions wrap when needed.
- Workspace outer horizontal padding becomes 12px; chat padding becomes 20px by 16px. Composers use 12px padding and preserve a 16px initial text-entry size.
- The report drawer becomes a fixed full-screen dialog (`100dvh`) with an independently scrolling body. Background content is inert while it is open, page scrolling is locked, and keyboard focus stays within the dialog.
- Metric buttons use a two-column grid. Report editing retains side-by-side value and unit fields with the reference-range field spanning the full row; it does not collapse every report field into a single column.
- Response sections reduce to 16px padding. Long tables scroll within the narrative. Footer and contextual actions wrap.
- Administration uses a single-column provider form, smaller shell padding, and a full-width save action.

Default buttons have a minimum height of 44px; hero actions use 48px. Compact Send, Report, attachment, and close controls use 40px in the implemented workspace, and mobile suggestion actions also use 40px. Preserve these distinctions when documenting the UI rather than claiming a universal 44px minimum. The skip link is exposed on keyboard focus.

## Elevation & Depth

The interface uses a hybrid of diffuse background color and flat foreground surfaces. Hero and chat gradients create atmosphere; white forms, responses, drawer, and admin remain solid. Fine borders and spacing define content groups. There is no box-shadow vocabulary in the active workspace or admin styles, and no backdrop blur or glass treatment.

**The Solid Reading Surface Rule.** Keep answer, form, report, and administration surfaces solid; diffuse color belongs behind the hero and chat content.

The introductory transition is a paused local GSAP timeline, advanced by native scroll progress through `requestAnimationFrame`. It scales the hero from 1 to 0.88 while fading it to zero and moving it upward by 24px; the workspace shell settles from 1.035 to 1. Progress is linear and clamped against the workspace's vertical position. There is no scroll hijacking, pinning, looping, bounce, or hover scaling.

The timeline is created only above 760px when GSAP is available and reduced motion is not requested. Crossing either media condition kills the timeline and clears its inline transforms/opacity. Mobile, reduced-motion, and missing-GSAP paths keep the hero and workspace in normal document flow without the scroll transform. Open workspace still navigates to the workspace, and action-driven scrolling is smooth unless reduced motion is requested. Reduced motion also removes CSS transitions and animations. The hero and conversation stay usable without the animation.

## Shapes

Use modest rounded rectangles and thin borders. Shared workspace, composer, and response surfaces use the surface radius; fields, suggestion actions, and selected-value buttons use the compact radius; ordinary buttons use the control radius. Administration retains its slightly larger panel radius. Progress markers use small rounded squares, and the borderless composer textarea has a small radius for focus visibility. The frontmatter records the observed values without promoting them to a new ornamental shape language.

Icons are simple stroke drawings with rounded ends. They support written actions, and icon-only close controls have an accessible name. Avoid giant pills, decorative badges, ornamental corners, and affiliation or certification imagery.

## Components

### Buttons

Solid indigo actions with white text identify the immediate task. Open workspace uses the roomier hero variant; Send uses the compact composer variant. Secondary actions use white, a quiet line border, and dark ink. Their hover changes to the pale violet tint and a stronger border. Report uses a compact secondary button with a document icon; its label becomes Your report after file selection. Underlined text actions serve subordinate choices such as Load example and Start a new analysis.

Global focus is a 3px solid focus-token outline with a 4px offset. The composer textarea uses a 2px outline with a 3px offset. Button color, background, and border feedback lasts 160ms; reduced motion removes it. Disabled buttons reduce opacity to 0.55 and use the waiting cursor. There is no hover transform.

### Composer and fields

The initial and follow-up composers are white bordered containers with a visible label, a borderless multiline field, and a toolbar. The toolbar keeps the attachment/report action and Send distinct. The initial form offers labelled synthetic examples and a reference-range reminder; choosing an example fills the field without submitting. The character count is shown on wide layouts and omitted at the intermediate breakpoint. Follow-up preserves the current report context.

Standalone fields use a darker control border, white fill, a compact radius, and primary-colored caret. Report review groups value, unit, and supplied range under a named measurement. Unconfirmed extracted values are editable; confirmed values are read-only. Do not substitute a visual success treatment for the explicit confirmation step.

### Navigation

The ghost-white header pairs the ResultScope wordmark and Laboratory Assistant subtitle with User guide and Open workspace text links. Header links use dark slate violet and gain an underline on hover; there is no persistent active-tab underline in this implementation. The linked brand returns to the top. The footer provides Scope and privacy and Administrator links. The workspace header remains concise, showing Laboratory conversation and the Report action.

### Suggestions and work surfaces

Suggested laboratory questions are rectangular bordered buttons with text and a small directional icon. They share the white surface and secondary text color; hover strengthens the border. They are input shortcuts, not category chips or navigation pills.

The conversation response is a white bordered surface organized into header, supplied-value comparison, explanation, and optional source/rule disclosures. Response and result content remain solid over the chat atmosphere. Administration uses the same palette, typography, borders, and buttons on a solid paper background; provider sections are separated by rules rather than floating cards.

### Selectable values and range inspector

Each metric is a button showing measurement, value/unit, and written comparison state. Selection uses both the primary border and pale tint. The inspector uses a very pale solid inset, a large tabular reading, supplied reference text, and a restrained range track. Missing-range state stays explicitly unknown. The browser displays server metadata; the design adds no clinical interpretation.

### Report drawer

The Report, Attach report, and View report controls open the same drawer. Desktop keeps it beside the conversation. Mobile changes its role to a modal dialog, sets `aria-modal`, makes the background inert, traps Tab focus, and locks background scroll. Opening focuses Close report panel. Escape and close dismiss it and restore the invoking control when available; Return to conversation focuses the current composer. Closing preserves the selected report. Discard image cancels/removes the image when that action is available; it is distinct from closing the panel.

The drawer shows JPEG/PNG upload guidance, filename and size, state text, preview, grouped editable extracted fields, and explicit Confirm values. PDF is not supported. Upload and discard are unavailable while busy or once an analysis owns the report; the interface explains that a different report needs a new analysis. Confirmation closes the mobile drawer and returns focus to the initial composer, while desktop retains the side panel. Do not imply document history or multiple-report management.

### Sources, rules, and feedback

Sources and calculation details use semantic disclosures, ordinary links, and small readable metadata. Errors use red-tinted blocks with written recovery actions; outside-scope replies offer relevant question buttons. Synthetic notices use amber and remain explicit. Loading placeholders are quiet solid shapes rather than an animated spectacle. These states describe the interface and its evidence boundaries, not production or clinical approval.

## Do's and Don'ts

### Do:

- Do use the shared purple tokens and self-hosted English/Thai font stack.
- Do confine diffuse gradients to the hero and chat while keeping reading and form surfaces solid.
- Do preserve native scrolling and the static mobile, reduced-motion, and no-GSAP timeline paths.
- Do keep values, units, supplied ranges, and written status legible together.
- Do preserve visible keyboard focus, mobile drawer focus management, and explicit report confirmation.
- Do keep Send, Open workspace, Report, and source/rule actions clear and available at narrow widths.

### Don't:

- Don't restore the superseded teal identity or interpret compatibility token names as teal colors.
- Don't add glass panels, decorative canvas, science-fiction HUDs, AI mascots, giant pills, or invented metrics.
- Don't extend the approved scroll transition into hover scaling, bounce, scroll hijacking, or repeating ambient animation.
- Don't use color alone for low, high, within-range, unknown, or error states.
- Don't confuse closing the drawer with discarding a report or imply PDF and multiple-report support.
- Don't describe mocked captures, visual review, or this design system as live, production, or clinical validation.
