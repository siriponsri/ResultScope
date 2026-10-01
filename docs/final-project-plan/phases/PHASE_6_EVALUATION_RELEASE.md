# Phase 6 ทดสอบจริงและแพ็กส่งการบ้าน

เวลาเป้าหมาย: 8 ต.ค. 6–8 ชั่วโมง และ buffer 9–16 ต.ค. Owner: MAIN; REVIEW ตรวจหลักฐาน; owner บันทึกวิดีโอ/ส่งงาน อ่าน 07

## Entry

G0–G5 core ผ่านหรือระบุ blockers ที่ต้องแก้ก่อน release ชื่อธุรกิจ/approved corpus พร้อม Live provider พร้อม ไม่มีการอ้าง mock mode ว่าเป็น complete submission

## Work items

| ID | งาน | Output | Acceptance |
|---|---|---|---|
| P6-F01 | freeze candidate | release manifest | commit/deps/corpus/prompt/model versions exact |
| P6-F02 | full evaluation | Q/I/S results | ≥10/5/5 มี actual/pass/time ตามโจทย์ |
| P6-F03 | before/after audit | 3 improvement report | same case + baseline evidence preserved |
| P6-F04 | as-built diagrams | architecture/data-flow | ทุก endpoint ที่วาดมีผล smoke จริง |
| P6-F05 | fresh install | reproduce log | new venv/clean checkout ทำงานตาม README |
| P6-F06 | deployment verification | optional preview report | ถ้า deploy ได้รับอนุญาต ต้องตรวจ deployed URL จริง |
| P6-F07 | submission package | source/evidence/docs | ไม่มี secrets/real personal data/runtime junk |
| P6-F08 | video/oral prep | ≤180s clip + checklist | flow แสดงระบบจริงและผู้ส่งอธิบายได้ |

## ขั้นตอนและ evidence policy

1. Freeze candidate SHA และ corpus hash แยก dev/test inputs; REVIEW รัน regression suite และ live evaluation
2. เก็บ all runs ที่ใช้รายงาน ไม่แก้ cell actual ให้ตรง expected ถ้า fail เปิด defect, fix, rerun affected suite + integration risk ที่เกี่ยวข้อง
3. หลัง fix commit เปลี่ยน ต้อง update release manifest; evidence ที่ไม่ rerun ต้องบอกว่าเป็น earlier commit ไม่แปะว่าผ่าน final HEAD
4. ตรวจ Q01–Q10 และ I01–I05/S01–S05 พร้อม additional safety cases ผลผ่านทุก mandatory เป็น target ภายใน ถ้าไม่ครบยังไม่ปิด G6
5. Before/after ใช้ 3 จุดใน 07; B02 absent baseline ระบุ NOT_SUPPORTED ไม่สร้างภาพว่ารุ่นเก่าวิเคราะห์ผิด
6. ดึง OpenAPI/routes และอ่าน code flow จริง วาด as-built สองแบบให้ตรง รวม provider/storage ที่ใช้จริง ไม่แสดง LightRAG/MCP/LINE ถ้ายังไม่ได้ต่อ
7. ทำ fresh clone/checkout ใน directory ใหม่ติดตั้งด้วย lock แค่ env example + key ที่ owner ตั้ง ไม่พึ่ง state ในเครื่อง dev; check key missing error และ offline tests
8. Scan tracked files/ZIP for secrets and personal data ไม่ใช้ `.env`, logs หรือ database จริงเป็น artifact; อย่า delete หลักฐานเดิมเพื่อให้ report ดูสะอาด
9. เตรียม demo script 170 วินาที ให้ owner record และเช็ก duration จริง บันทึกชื่อสมาชิก/ส่วนรับผิดชอบมนุษย์

## Deployment decision

Local demo เป็น fallback ที่รันจริงได้ ไม่อ้างว่าโจทย์แนบระบุ hosting platform หากผู้สอนต้อง URL ให้ owner ยืนยันและขออนุมัติ deployment ตาม audience

คง `main.py` FastAPI deployment path เดิม Verify platform requirements ปัจจุบันก่อน deploy: runtime/dependency install, image payload limits, request duration, env, durable state, static index availability อย่าเพิ่ม legacy vercel.json เพราะ copy ต้นทางเก่า SQLite local ไม่ใช่ persistent serverless storage

เมื่อใช้ Vercel ให้เริ่ม preview เมื่อได้รับอนุญาต ไม่ deploy production โดยถือว่า “catalog” แปลว่าเผยแพร่ทันที ตรวจ direct API และ mobile บน URL ที่ deploy จริง cold start/state reset/error flows ถ้าไม่ deploy ให้ report NOT_DEPLOYED พร้อม local reproducibility

## Gate G6

Rubric H01–H19 มีหลักฐานหรือ N/A ที่อธิบายได้สำหรับงานคู่เมื่อทำเดี่ยว, live test ครบ, diagrams exact, reproducible setup, no critical/high defect, before/after 3, clip จริง ≤3 นาที และ source access เตรียมตามผู้สอน

วิดีโอที่ยังไม่อัดหรือข้อมูลธุรกิจที่ยังไม่รับรองคือ blocker ต่อ “ส่งครบ” แม้ code พร้อมแล้ว ให้ใช้สถานะ CODE_READY_EVIDENCE_PENDING ไม่อ้าง DONE

## Handoff

สร้าง RELEASE_REPORT และ catalog status จาก evidence เก็บ known limitations; owner เป็นผู้ส่งการบ้านเอง P7/P8 เริ่มหลัง R1 stable โดยไม่แก้ release evidence ย้อนหลัง
