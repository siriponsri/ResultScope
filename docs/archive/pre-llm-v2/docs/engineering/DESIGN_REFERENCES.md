# Design references and attribution

Reviewed on 2026-10-04. This is a purpose-built redesign of the existing FastAPI
application, not an imported healthcare template.

| Reference | Applied idea | Boundary |
| --- | --- | --- |
| https://github.com/AHMAD-JX/Website-HealthHup | Familiar healthcare navigation and readable light surfaces | No borrowed logo, images, clinical claims or appointment workflow |
| https://github.com/creativetimofficial/ui | Consistent form states and component spacing | No framework migration, remote registry execution or wholesale component import |
| https://github.com/cathrynlavery/diagram-design | Editorial SVG diagrams, orthogonal paths, limited focal nodes | Customized ResultScope palette; original artwork; no global plugin install |

## Approved v2 references

The owner approved **C + 2** on 2026-10-04: a minimal landing page that recedes on
native desktop scroll into the same-page conversation, with a report drawer. The
owner explicitly permits diffuse gradients in both hero and chat above the
no-slop rule. Ordinary controls and results remain solid, readable surfaces.

| Reference | Applied idea | Inspection and boundary |
| --- | --- | --- |
| https://github.com/LeoStehlik/no-slop-ui/blob/master/SKILL.md | Direct labels, restrained controls, no invented metrics, no decorative dashboard rails | Skill and supporting rules read; owner gradient/scroll exceptions recorded |
| https://cdn.prod.website-files.com/66671b800c367e1fd46c54bc/671ffd42450295fc9c4639ec_airtable-347e0061dcde082e225cbad514a709f5-dcifw6fy.jpeg | #F8F8FF, #8A2BE2, #4B0082, #6A5ACD, #483D8B | Supplied palette image inspected; adapted to readable contrast |
| https://www.figma.com/community/file/1428252899173730213/ai-chatbot-ui | Spare conversation and bottom composer with diffuse atmosphere | User-supplied screenshots inspected; full Figma file inaccessible |
| https://www.figma.com/community/file/1514208823046545953/chatbot-flow-builder-ui-visual-sequence-editor-for-saas | Grouped uploaded-document content | Screenshot inspected; no workflow editor or fake node execution added |
| https://www.figma.com/community/file/778961842657921355/free-figma-website-landing-pages-startup-app | Centered title and diffuse landing atmosphere | User screenshot is a cover, not a complete page design; implementation is original |

Motion uses local GSAP 3.14.2 following Hyperframes timeline authoring guidance.
The live page uses native scroll, not a video player, scroll trap, or autoplay
sequence. The optional composition is separate from the application. See
[Motion](MOTION.md) and the supplied GSAP license notice.

Brand direction: ResultScope Laboratory Assistant. The repository and technical
identifiers remain ResultScope. The brand name is a working product identity;
trademark and domain clearance have not been performed.

An AI-generated symbol concept informed the original vector mark. Production SVGs
are small, explicit vector geometry: a report frame and three range markers.
No certification, hospital affiliation or regulatory clearance is implied.

Self-hosted dependencies: marked 15.0.12 (MIT), DOMPurify 3.1.7 (Apache-2.0 OR MPL-2.0),
IBM Plex Sans (OFL), and the pre-existing Noto Sans Thai (OFL). Full upstream license
texts for those dependencies are included next to vendor/font files. GSAP 3.14.2
uses its separate standard license; its original header and license pointer are
preserved in static/vendor/GSAP-NOTICE.md. No newly imported healthcare UI code.

The code and dataset licenses are separate. Preserve NOTICE.md and the evidence
addon's existing rights register. A public guideline is not automatically licensed
for commercial reuse; the commercial data review remains open.

Whitespace and line endings in copied notice files were normalized for repository
formatting; copyright and license wording is preserved. Original pinned source
bundles remain governed by their byte-level manifests.
