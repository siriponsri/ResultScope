# Motion implementation

The active introduction is a real Hyperframes 0.8.131 composition in
`static/motion/introduction/index.html`, embedded with the self-hosted
`@hyperframes/player` web component. The 1280×720, 12-second scene declares composition
metadata and registers a paused finite GSAP timeline in `window.__timelines`.
Palette/typography are documented in the adjacent DESIGN.md. All scripts/fonts are local.

Playback is user-controlled, silent and stops when its dialog closes. Reduced-motion
users open the held frame at 11.8 seconds. Normal UI entry/message animations also honor
reduced motion. No audio, autoplay, infinite timeline or model-progress simulation is used.
The composition is illustrative, not a live model recording or the full coursework video.

From that directory run the pinned package scripts for lint, validate, inspect or render.
For an existing Chromium use `HYPERFRAMES_BROWSER_PATH`. A browser/sandbox limitation
must be reported rather than disguised as successful rendering. The separate old
`docs/media/resultscope-intro` is retained historical media, not the current player.
