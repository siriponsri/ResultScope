# Design research translated into ResultScope

Research date: 2026-08-29

## Findings used

1. Generative-AI interfaces do not have to be conversational. Current HCI literature distinguishes conversational, canvas, contextual, and modular layouts, plus selection and direct-manipulation techniques. ResultScope therefore uses selectable result objects and a range inspector while keeping free text for intake and follow-up.

2. Patient-facing laboratory interfaces benefit from graphical representations, plain-language takeaways, contextual information, clickable terms, and tools that help prepare questions. ResultScope prioritizes literal-value visualization and a grounded narrative, while leaving annotation/history outside V0.1 scope.

3. Human-AI UX should reveal what the system can do, make the current state visible, support correction, and behave predictably when AI is wrong. The visible Read → Verify → Explain sequence and inspectable rule trace make the system boundary observable.

4. Fluid interfaces respond immediately, preserve spatial relationships, and let users redirect attention without waiting for decorative animation. Value selection updates one stable inspector instead of opening disconnected cards.

5. Current “AI aesthetic” sameness is strongly associated with default beige palettes, repeated rounded cards, glow, decorative dots, and generic component-library composition. ResultScope uses a domain-specific spectral instrument language instead.

6. Motion must respect `prefers-reduced-motion`, and no status may rely on animation or color alone.

## Sources

- Adobe Research / arXiv, *Survey of User Interface Design and Interaction Techniques in Generative AI Applications*: https://arxiv.org/html/2410.22370v1
- Microsoft HAX Toolkit, *Guidelines for Human-AI Interaction*: https://www.microsoft.com/en-us/haxtoolkit/ai-guidelines/
- JMIR Human Factors, *User-Centered System Design for Communicating Clinical Laboratory Test Results*: https://humanfactors.jmir.org/2021/4/e26017/
- Apple Developer, *Designing Fluid Interfaces*: https://developer.apple.com/videos/play/wwdc2018/803/
- W3C, *Using the CSS prefers-reduced-motion query to prevent motion*: https://www.w3.org/WAI/WCAG21/Techniques/css/C39.html
- The New Yorker, *The A.I.-Design Aesthetic That’s Taking Over the Internet*: https://www.newyorker.com/culture/infinite-scroll/the-ai-design-aesthetic-thats-taking-over-the-internet
