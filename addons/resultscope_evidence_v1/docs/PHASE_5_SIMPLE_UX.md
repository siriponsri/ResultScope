# Phase 5 — understandable on the first visit

Owner/teacher requirement: ผู้ใช้เปิดเว็บครั้งเดียวแล้วรู้ทันทีว่าทำอะไรได้ เริ่มตรงไหน และผลลัพธ์หมายถึงอะไร โดยไม่ต้องเรียน workflow

## Delivered reference preview

One visible search field, one action, three example queries. Results are rows with a clear source name and unit. Optional filters and detailed provenance are collapsed. An empty search result explains what happened; a server error allows retry; reset removes prior results. Tested at 1440px and 390px without horizontal overflow. This preview performs reference search only; it has no upload or conversational backend.

## Main application target

Reuse Phase 3's actual upload/OCR and question flow. Main headline: **อ่านผลแล็บของคุณให้เข้าใจง่าย**. Supporting line: **อัปโหลดใบผลตรวจ หรือพิมพ์คำถามเกี่ยวกับผลแล็บ**. Main action: **อัปโหลดใบผลตรวจ**. Adjacent text/question field must be usable immediately with one example. Do not add a fake upload control to the reference preview and present it as completed integration.

Keep the first screen short. No onboarding wizard, mandatory account for a local demo, pipeline rails, model selectors, tree diagrams, confidence meters or architecture terminology before the first answer. Put source browsing under **ดูข้อมูลอ้างอิง** and technical evidence under a developer/admin view. Keep any safety instruction short and directly relevant to uploading personal information.

After upload: show filename and readable processing state, allow correction of uncertain OCR, then show a short plain-language result with per-analyte details and sources on demand. Highlight missing data as a question to resolve. Never turn unknown into green/normal. Prevent duplicate submission, preserve entered text on failure and offer retry/reset. Reuse existing session signing and file validation.

Visual direction: neutral light background, restrained teal accent, strong readable Thai/Latin type, subtle borders, generous but useful spacing. No decorative gradients, fake dashboards, multiple equal-weight calls to action or decorative clinical confidence badges. Self-host licensed font assets; maintain keyboard focus, semantic labels and sufficient contrast.

## Acceptance with evidence

- A first-time tester can state the purpose and choose the first action within about 5 seconds; complete a sample task without explanation. Record observed time, not an assumed PASS. At least 3 people if available; otherwise usability validation NOT_RUN.
- Desktop and 390px mobile: upload/question, OCR correction, reply, citation, follow-up, reset, no-hit, invalid upload and provider failure all operable.
- Keyboard-only operation: visible focus; labels; Enter submits only intended form; status announced; no focus trap. Long Thai source names and citation URLs do not clip.
- No technical workflow knowledge required to obtain the first useful answer.
- Screenshots prove layout only. They do not prove live OCR, live LLM quality or user comprehension.

English/international readiness means externalized user copy, locale-aware numbers/dates and clear terminology. Do not claim full bilingual coverage unless each actual user-facing state is translated and tested. Keep Thai as default for this coursework.
