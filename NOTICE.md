# NOTICE

## Upstream coursework starter

This package was prepared from the architecture and source layout of:

- Repository: `chacharin/chatbot-it-kmitl`
- Purpose: KMITL Week 7 chatbot / Cloud LLM / Vercel coursework starter

The inspected upstream repository did not expose an explicit root software license at preparation time. This package therefore does **not** grant new rights to the upstream code.

Use this derivative for the intended coursework/demo context and preserve attribution. Before commercial distribution, either:

1. obtain explicit permission/licensing from the upstream author, or
2. reimplement the generic architecture independently and license the clean implementation appropriately.

## Historical design tooling

The earlier optional Hallmark installer and its run metadata are preserved in the
historical archive. They are not required by the current application and are removed
from the active tree by the explicit cleanup procedure. No Hallmark code is bundled.

At the owner's request (2026-10-06) the Hallmark design skill (nutlope/hallmark @ 13ac0ec, MIT,
license in `.claude/skills/hallmark/LICENSE`) is installed as a project skill for development
assistants. It is Markdown guidance only, is not served by the application and is not part of the runtime.

## Current third-party assets

The product refresh includes local copies of marked, DOMPurify, IBM Plex Sans, Noto Sans Thai,
Geist and Geist Mono (Vercel, SIL OFL 1.1, `static/fonts/Geist-OFL.txt`), Source Serif 4 (Adobe, SIL OFL 1.1,
variable optical-size file `static/fonts/source-serif-4-opsz.woff2`, license `static/fonts/SourceSerif4-OFL.txt`) and
Noto Serif Thai (SIL OFL 1.1), used again for display headings from v5. The website hero bundles Three.js r0.186.1
(MIT, license in `static/vendor/three/LICENSE`, legal comments kept at the end of `static/js/hero3d.js`). Their upstream notices and licenses accompany the files under
static/vendor and static/fonts. The approved native-scroll transition and optional presentation composition include
local GSAP copies with the original copyright header and license pointer. See
[design attribution](docs/engineering/DESIGN_REFERENCES.md) and
[presentation dependency](docs/media/resultscope-intro/THIRD_PARTY.md).

The new name, logo, interface and documentation do not grant additional rights to
upstream code or source datasets. Preserve all separate notices and source terms.


## ResultScope 2.0 additions

The Hyperframes player is @hyperframes/player 0.8.131, MIT licensed; the license is in static/vendor/HYPERFRAMES-LICENSE. The original 12-second composition uses the existing GSAP and font notices, copied alongside its runtime assets. DOMPurify is updated to 3.4.16, with its full license in static/vendor/dompurify-LICENSE. Exact source URLs and hashes are in static/vendor/SOURCES.json. Teacher repositories inform the independently authored integration patterns; their server source has not been bundled as a local runtime. Source-specific laboratory manuals retain the existing vendor bundle notices.
