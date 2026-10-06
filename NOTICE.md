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

## Current third-party assets

The product refresh includes local copies of marked, DOMPurify, IBM Plex Sans and
Noto Sans Thai. Their upstream notices and licenses accompany the files under
static/vendor and static/fonts. The approved native-scroll transition and optional presentation composition include
local GSAP copies with the original copyright header and license pointer. See
[design attribution](docs/engineering/DESIGN_REFERENCES.md) and
[presentation dependency](docs/media/resultscope-intro/THIRD_PARTY.md).

The new name, logo, interface and documentation do not grant additional rights to
upstream code or source datasets. Preserve all separate notices and source terms.


## ResultScope 2.0 additions

The Hyperframes player is @hyperframes/player 0.8.131, MIT licensed; the license is in static/vendor/HYPERFRAMES-LICENSE. The original 12-second composition uses the existing GSAP and font notices, copied alongside its runtime assets. DOMPurify is updated to 3.4.16, with its full license in static/vendor/dompurify-LICENSE. Exact source URLs and hashes are in static/vendor/SOURCES.json. Teacher repositories inform the independently authored integration patterns; their server source has not been bundled as a local runtime. Source-specific laboratory manuals retain the existing vendor bundle notices.
