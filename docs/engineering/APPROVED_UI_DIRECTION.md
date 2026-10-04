# Approved UI direction — revision 2

Owner decision, 2026-10-04 (Asia/Bangkok): **C + 2**.
Use a scroll-linked zoom-out introduction that continues into the chat workspace,
and a report drawer that opens when needed. The owner explicitly permits soft
purple gradients in both the hero and chat, overriding the no-slop gradient ban.
This is a pinned direction; do not reopen theme selection during implementation.

## Visual authority

- Palette supplied by the owner: #F8F8FF, #8A2BE2, #4B0082, #6A5ACD, #483D8B.
- Uploaded chatbot references: focused conversation, compact composer, suggestions.
- Uploaded flow-builder reference: grouped editable fields and clear state ownership;
  do not add a workflow-builder product or require users to connect nodes.
- Uploaded fourth reference: centered title and diffuse color. It is a cover image,
  not evidence of a complete landing layout or of a particular scroll interaction.
- Rule: https://github.com/LeoStehlik/no-slop-ui/blob/master/SKILL.md, version 0.3.0.
  Its banned-patterns and palette references were read before implementation.

## Approved exceptions

| Rule normally avoided | Owner-approved use | Boundary |
| --- | --- | --- |
| Decorative gradients | Diffuse purple/lavender in hero and chat | Text remains dark; answer and form surfaces remain solid and readable |
| Transform motion | Scroll-linked zoom-out between introduction and workspace | No hover scaling, bounce, scroll hijacking or repeating ambient animation |
| Large centered heading | Public introduction before the app | The chat itself has a concise operational header |

All other no-slop guidance remains in force: plain controls, modest radii, no
sparkle mascot, invented metrics, giant pills, decorative charts or glass panels.

## First viewport and signature interaction

The header identifies ResultScope Laboratory Assistant. One centered functional
headline, a short explanation and a direct Open workspace action make the purpose
clear immediately. A second action loads a labelled synthetic example without
submitting it. A short native scroll reveals the real workspace while the opening
composition recedes. Users can bypass this with the primary action or #workspace.

The workspace contains the current conversation, composer and a Report action.
Uploading opens a right-side report drawer on desktop. The drawer shows the selected
image, status, editable fields and explicit confirmation. Closing it preserves the
current report; Discard image cancels/removes it. The Report action remains available
while reading an answer. On small screens it becomes a full-screen dialog with
Escape/close and managed focus. There is no fake document history or multiple-report
feature. No PDF support is introduced.

Hyperframes informs the paused, seekable GSAP motion grammar. The web runtime uses
a local GSAP timeline controlled by native scroll; it does not run a video player.
The reduced-motion and no-GSAP paths expose the same working interface immediately.

## Product and verification boundaries

Preserve APIs, Python authority, extraction ownership/revision checks, confirmation,
scope/refusal, citations, fail-closed validation, provider guard and attempt ledger.
No provider calls or credentials are needed for this redesign. Screenshots of
successful OCR/answers must be visibly mocked and cannot become readiness evidence.
Update active docs, diagrams, branding, screenshot captions, HTML/PDF manual and
the Luna Max local-closeout contract to this actual implementation.
