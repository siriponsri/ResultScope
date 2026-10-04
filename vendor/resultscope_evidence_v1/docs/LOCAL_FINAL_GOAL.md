# Owner instruction — integrate ResultScope public evidence and finish local candidate

คำสั่งนี้สำหรับ MAIN ใน repo `C:\Users\User\Desktop\myProject\ResultScope` บน local `main` เจ้าของอนุญาต implementation, tests, browser checks, reports, Project Brain และ local commits ตามขอบเขตนี้ ห้าม push/deploy เป้าหมายคือ integrated local candidate ที่ตรวจสอบได้ ไม่ใช่บังคับให้ทุก gate เป็น PASS

## 1. Read and establish actual state

อ่านไฟล์นี้ให้ครบก่อนลงมือ ถือเป็น owner communication ตาม workflow ที่เจ้าของกำหนด หากพบข้อขัดแย้งกับคำสั่งเจ้าของล่าสุด ให้ใช้คำสั่งล่าสุดและรายงานส่วนที่เปลี่ยน

อ่าน `AGENTS.md`, `DESIGN.md` (ถ้ามี), รายงาน Phase 4 และหลักฐาน, รายงานก่อนหน้าที่อ้างถึง, แผนเดิมที่เกี่ยวข้อง, Project Brain, และ docs ของ `addons/resultscope_evidence_v1` ให้ครบตามงาน ห้ามอาศัย report อย่างเดียวแทนอ่าน implementation

ตรวจ `git status`, branch, HEAD, tracked/untracked changes, active FO runs และไฟล์ที่ถูก ignore ก่อนแก้ application โครงการที่เจ้าของรายงานล่าสุดคือ HEAD `b9bc97d`, application candidate `45acba9`, 172 tests แต่ต้องตรวจสถานะจริงใหม่ อย่า reset/pull/rebase เพื่อให้ตรงค่าเก่า หาก HEAD ใหม่กว่านี้ให้อ่าน diff/reports แล้วทำต่อจากปัจจุบันโดยรักษางานเจ้าของ

สำคัญ: patch นี้ถูกทำโดยอ่าน GitHub ที่เก่าถึง `68b6e256ac074c0714e39aa5c0edd5d69ce936c9` จึงเป็น namespace เสริม ไม่ใช่ตัวแทน Phase 4 ห้ามเอา main.py/UI/services จาก GitHub เก่าทับ local ล่าสุด

`PROMPT.md` อยู่ root และ local-only ตรวจ exclusion ผ่าน `.git/info/exclude`; ถ้ายังไม่มีให้เพิ่มเฉพาะรายการ `PROMPT.md` โดยรักษา entries เดิม ห้าม stage/commit PROMPT.md และไม่เปลี่ยน .gitignore เพื่อเรื่องนี้ ตรวจไม่มี secret หรือไฟล์รายงานส่วนบุคคลปนอยู่ก่อน stage

## 2. Multiagent and execution budget

ใช้ FO จริงตาม configuration ของเครื่องหาก runtime พร้อม MAIN เป็นผู้ integrate และ stage/commit เท่านั้น แบ่งงานชัด: IMPLEMENT data/backend, IMPLEMENT UI ตามไฟล์ไม่ซ้อน, REVIEW independent ต่อ candidate ที่ระบุ SHA จริง อ่าน AGENTS/FO instructions ที่มีอยู่ก่อนเลือกวิธี dispatch

ห้ามสร้าง worker/receipt/review ปลอม ห้ามแก้ global settings หรือ retry loop เพื่อหลบ failure ถ้า dispatcher ล้มก่อน worker ให้บันทึก error โดยไม่เผย secrets, ระบุ independent FO review NOT_RUN และทำงานส่วนที่ MAIN ทำได้ต่อ หาก local rules กำหนดว่าบาง gate ต้องมี independent review ให้คง gate BLOCKED/NOT_CLAIMED ไม่แต่ง PASS แทน

เก็บ bounded handoff: scope, files, tests/exit codes, candidate SHA, open issues ให้ reviewer ตรวจ code/data/actual evidence ไม่ใช่เห็นจำนวน tests แล้วอนุมัติ

รัน focused tests หลังการเปลี่ยนแปลงแต่ละส่วน รัน full suite เมื่อ integrated candidate พร้อม และอีกครั้งเฉพาะเมื่อ remediation กระทบ behavior ไม่วน full tests/Brain refresh/commit จนไม่จบ ห้าม benchmark เพื่อให้ได้ตัวเลขสวยหรือแก้ expected outputs กลบ regression

## 3. Phase 4A — real public evidence

ทำตาม `PHASE_4A_REAL_DATA.md`, `SOURCE_AUDIT.md`, `OPEN_GUIDELINES.md` และ `INTEGRATION_CONTRACT.md`

เจ้าของอนุญาต guideline open data ประกอบแล้ว: patch มี WHO 2 ฉบับและบทสรุปไทย 3 รายการใน namespace open_guideline แยกจาก numeric reference และ business ใช้ GuidelineCorpus adapter ให้แสดง title/year/section/PDF page/license เสมอ ไม่มี numeric diagnostic rules ใน supplement ห้ามสลับเป็นค่าอ้างอิงรายบุคคล และห้ามถือ CC BY-NC-SA เป็นสิทธิ์เชิงพาณิชย์ที่ไม่จำกัด

เริ่มด้วย extension verify (offline, stdlib) อ่าน manifest/records/tree และดู sample PDF pages หากจะแก้ clinical fields อย่าถือ normalized English transcription ว่าเป็นคำพูดต้นฉบับ verbatim

เพิ่ม namespace public_reference แยกจาก synthetic และ approved business release ใน runtime จริง ไม่ย้าย source ไป release เพื่อผ่าน validator และไม่ทำให้ public_reference ถูกทดสอบด้วย business-approval gate ที่ไม่เกี่ยวกัน รายงานทั้ง structural integrity และ release readiness แยกกัน

เชื่อม retrieval ของ extension ผ่าน adapter ตามโครงสร้างแอปจริง ให้ตอบคำถามค่าอ้างอิงจากเอกสารจริงและแสดงองค์กร/หน้า/URL ได้ จัดการ source ไม่พบ/ไฟล์เสีย/คำถามไม่ตรงโดย abstain อย่างเข้าใจง่าย อย่าลด scope/output policy เดิม

รายการ 26 records ไม่ใช่ complete handbook: 17 analytes, 17 PDFs, 2 organisations; CBC มี PDF แต่ยังไม่มี numeric table ที่ index ส่วน PDF text ที่เหลือยังไม่เข้า search ไม่อ้างครอบคลุมทั้งโรงพยาบาลหรือราคาบริการ

คง reference range ในใบผลเป็นหลัก ไม่เลือกค่าอ้างอิงจากโรงพยาบาลใดโดยอัตโนมัติ ไม่เฉลี่ย source conflicts ไม่อนุมาน age/pregnancy/method/unit conversion ถ้าข้อมูลไม่พอให้ unknown/ขอข้อมูลเพิ่ม

ถ้าจำเป็นต้องปรับ extension ให้เข้ากับ repo ให้ถือ checksum เดิมเป็น delivery baseline เก็บ original manifest และบันทึก diff/new checksums อย่างตรงไปตรงมา ห้ามลบ hash check เพื่อให้ผ่านโดยไม่อธิบาย อย่าตั้ง tests ให้ล็อกเอกสารที่แก้ตามปกติแล้วต้อง refresh ทุก commit

## 4. Phase 4B — Tree evidence, model integration and optional Clef

ทำตาม `PHASE_4B_TREE_CLEF.md` ใช้ต้นไม้จริงจาก extension แต่เรียกให้ถูกว่า metadata/alias-guided hierarchical retrieval ไม่อ้าง embedding/RAPTOR/semantic tree ที่ยังไม่มี

Reuse provider abstraction และ safe answer path ของ Phase 2/4 นำ context_packet เป็น external data ผ่าน citation allowlist/output validation ไม่ concat เป็น trusted system instruction แสดง source refs ที่ resolve ฝั่ง server ห้าม arbitrary URL จาก LLM

ทดสอบ sync/SSE parity, session signing/reset, wrong citations, injection, no-hit, source conflict, unknown context และ existing contextual follow-up รวมทั้ง supported synthetic Marker-A/B/C รักษาเดโมเดิมที่ยังใช้งานอยู่

วัด old runtime retrieval vs new runtime retrieval ด้วย query/corpus เดียวกัน แยก retrieval latency กับ provider latency ผล extension flat12/15/tree15/15 เป็นแค่ small internal fixture comparison ใช้แทน runtime baseline หรือ live RAG quality ไม่ได้

Clef ปิดหรือ shadow-only เป็นค่าเริ่มต้น ห้ามเปลี่ยน permission/safety/clinical route จาก score ไม่มี live evidence ก็ระบุ NOT_RUN ไม่ต้องเพิ่ม live dependency ให้เดโมทำงานได้ ห้ามลง paid provider หรือส่งข้อมูลผู้ป่วยไป Clef โดยอนุมานสิทธิ์จากการใช้ Typhoon

เจ้าของเลือก Typhoon API ฟรีไว้ก่อน: ใช้ key/config ที่เจ้าของเตรียมไว้ฝั่ง server หากมีและอยู่ในสิทธิ์ที่อนุญาต ตรวจ model/base URL/current compatibility จาก config/official docs ห้ามเดา model ID, quota หรือราคา ห้ามพิมพ์ key ใน output หากไม่มี credentials ให้ทำ mocked+offline paths ครบและ live NOT_RUN; อย่ากรอก placeholder แล้วเรียกว่าทดสอบจริง

## 5. Phase 5 — first-use UX (highest product priority)

อาจารย์กำหนด: เปิดเว็บแล้วเข้าใจทันที ใช้ง่าย ไม่ซับซ้อน ไม่ต้องเรียน workflow

อ่าน `PHASE_5_SIMPLE_UX.md` และ UI preview แล้วปรับ **UI หลักจริง** ไม่ใช่แค่เปิด preview แยกเป็นผลงานจบ ใช้ Phase 3 upload/OCR และช่องคำถามเดิมให้เกิด first useful answer ได้จากหน้าแรก

หน้าแรก: headline ภาษาไทยสั้น, action อัปโหลดใบผลตรวจ, ช่องพิมพ์คำถามและตัวอย่างที่กดได้จริง ห้ามบังคับเข้า pipeline dashboard/model selector/tree ก่อนเริ่มใช้ ส่วนแหล่งอ้างอิง/รายละเอียดเทคนิคซ่อนไว้ตามต้องการ ห้าม fake upload/chart/status/live badge

หลัง OCR ต้องแก้ค่าที่อ่านไม่ชัดได้ ผลลัพธ์อ่านรู้เรื่องบนมือถือ แยกข้อมูลไม่พอกับค่าปกติ ให้ดูแหล่งที่มา/reset/retry ได้ รักษา keyboard labels/focus, long Thai wrapping, request cancellation และ duplicate submit prevention

ใช้ design tokens และ components เท่าที่จำเป็นใน stack เดิม ไม่ migrate framework เพราะความสวยอย่างเดียว ไม่เพิ่ม global SaaS chrome, decorative gradients, AI sparkles หรือ clinical confidence meter

ตรวจ desktop และ 390px: upload, OCR correction, question, follow-up, sources, reset, no-hit, invalid file, provider error; ถ้า live OCR/LLM ไม่ได้รันต้อง label mock evidence ให้ตรง ถ้าไม่มีคนทดสอบ first-use จริงให้ usability validation NOT_RUN ห้ามอ้างมนุษย์เข้าใจจาก screenshot อย่างเดียว

## 6. Phase 6 — local product/coursework closeout

ทำ `RELEASE_CHECKLIST.md` ให้สอดคล้อง rubric จริง ไม่อ้างว่างาน public-reference แทน business facts แล้วผ่านครบ

สร้าง/อัปเดตเอกสาร architecture และ message flow ให้แยก implemented vs proposed ชัดเจน สรุป prompt/provider/KB design, sources, setup Windows, source licenses, limitations, known blockers และ demo steps ที่ทำตามได้

เก็บหลักฐานคำถามอย่างน้อย 10, image cases 5, safety cases 5 ตาม rubric พร้อม actual output, expected criteria, PASS/FAIL/NOT_RUN และเวลา ระบุ mocked/live/retrieval-only ทุกกลุ่ม ทำ 3 before/after improvements จากหลักฐานที่มีจริง ไม่ผลิตเลขย้อนหลัง ถ้า sample ภาพเป็น synthetic ต้องเขียนว่า synthetic ไม่อ้าง real patient

เตรียม report-ready Markdown และ script วิดีโอเดโมไม่เกิน 3 นาที; ถ้าเครื่องมีเครื่องมือ export PDF ให้สร้างและตรวจอ่านจริง ไม่อ้างส่ง Google Drive/อาจารย์โดยไม่มีการส่ง เจ้าของยังเป็นผู้ส่งการบ้าน

จัด product capability matrix: implemented local / verified live / proposed / blocked ให้แสดงทีมได้อย่างตรงไปตรงมา เตรียม integration contracts สำหรับ HIS/pharmacy ตามเอกสาร แต่ไม่เชื่อม production patient database ไม่มี credential/partner schema ให้ใช้ synthetic fixtures และ label proposed/contract-only

ตรวจ configuration, secret handling, upload limits/content types, logs, dependency/runtime compatibility ตาม source จริง; ไม่ทำ deployment และไม่ส่งข้อมูลจริงออกนอกระบบโดยไม่มีสิทธิ์ อย่าเรียก preview.py ว่า production server

## 7. Verification and closure

ต้องมี:

- Extension source/tree/hash tests และ focused integration/UI regression tests ที่ตรวจ behavior จริง
- Full existing suite + `scripts/check.ps1` ตาม environment, compile/syntax/diff checks ที่โปรเจกต์กำหนด; เครื่องมือรันไม่ได้ให้รายงาน NOT_RUN พร้อมเหตุผล
- Browser evidence desktop/mobile พร้อม actual errors/limitations; server ที่เปิดต้องปิดเมื่อจบ
- Independent review จริงถ้า FO พร้อม พร้อม candidate SHA; otherwise NOT_RUN และห้ามให้ gate ที่บังคับ review ผ่าน
- Reports แยก 4A/4B/5/6 หรือรวม INDEX ที่ชี้หลักฐานและ statuses ชัด, จัด business/source rights/live provider/HIS blockers แยกจาก code tests
- MAIN inspect diff, stage เฉพาะงานนี้, local commit checkpoint(s), no PROMPT/secrets/unrelated files; ไม่ push/deploy
- Project Brain refresh ตามเครื่องมือจริง หลัง final commit และตรวจ HEAD match; หากเครื่องมือไม่มีให้ NOT_RUN ไม่สร้างสถานะ FRESH เอง

G0/G1/G3/G4 เป็น historical gates: อย่าเขียนทับอดีตเป็น PASS เพราะ patch ใหม่ผ่าน offline tests ถ้าเปิด re-audit ให้มีหลักฐานและรายงาน gate ใหม่แยกต่างหาก

Final response ต้องบอก exact HEAD, branch/worktree state, changed capabilities, commands/test counts/exit codes, live versus mocked evidence, review/Brain status, how to launch actual app และ residual blockers รวมถึง permissions/approved business data ถ้ายังขาด

เมื่อ nonblocked scope ทำครบและ blocker ถูกบันทึก ให้ปิดเป็น **completed documented local closeout** ได้ แต่ห้ามเรียก production-ready, passed all gates หรือ integrated HIS ถ้าไม่จริง ไม่เริ่ม deployment goal อัตโนมัติ และไม่วนงานต่อเพียงเพื่อเปลี่ยน status ให้เขียว
