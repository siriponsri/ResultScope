# Presentation media

`resultscope-intro/index.html` is a 12-second Hyperframes-format introductory
composition. It uses the ResultScope visual identity from DESIGN.md and the real
workspace screenshot. The controls allow replay in a browser. It is a title sequence,
not a recording of OCR or LLM performance and not the course's complete demonstration.

The GSAP timeline is deterministic, paused and registered at
window.__timelines['resultscope-intro']. There are no remote media dependencies.
The repository app itself does not import Hyperframes or GSAP.

Optional rendering with the Hyperframes CLI, in a separate tooling environment:

```sh
npx hyperframes lint docs/media/resultscope-intro
npx hyperframes inspect docs/media/resultscope-intro
npx hyperframes render docs/media/resultscope-intro
```

Check the installed CLI's help before rendering; export invocation may vary by
version. This package supplies an editable composition, not an MP4 export or a claim
that the Hyperframes CLI validation passed. Browser seek/render verification is
recorded in the redesign verification report. The vendored GSAP copyright header is preserved; its license link and source version are recorded in THIRD_PARTY.md.

Use docs/product/DEMO_SCRIPT_180S.md for the full product walkthrough. Keep provider
usage disabled unless a new live cycle has been explicitly authorized.
