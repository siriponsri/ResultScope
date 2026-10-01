# Phase 0 ตรวจฐานและเตรียมทำงาน

เวลาเป้าหมาย: 2 ต.ค. เช้า 3–4 ชั่วโมง Owner: MAIN; reviewer: REVIEW อ่าน 00–03 ก่อนเริ่ม

## Entry

มี local clone และสิทธิ์อ่าน repo; ยังไม่ต้องมี API key เพื่อทำ inventory/mock baseline ห้ามเรียก external provider โดยไม่ทราบ credentials/budget ที่ผู้ใช้ตั้ง

## Work items

| ID | งาน | Output | Acceptance |
|---|---|---|---|
| P0-F01 | อ่าน instructions และตรวจ git | docs/progress/BASELINE.md | branch/HEAD/status/remotes และ uncommitted work ถูกบันทึก |
| P0-F02 | เทียบ pinned commit กับ HEAD | delta audit | แยกสิ่งเปลี่ยน ไม่ถือว่าแผนเก่าตรงทุกไฟล์ |
| P0-F03 | venv/install/test | environment + baseline log | ระบุ Python/resolved deps/exit code; fail บันทึกตามจริง |
| P0-F04 | inventory routes/config/UI | route table และ screenshots | route ตรง OpenAPI; ไม่มี secret value ในเอกสาร |
| P0-F05 | เก็บก่อนปรับ 3 จุด | evidence/baseline/<run_id> | raw inputs/outputs/time/NOT_SUPPORTED มี timestamp |
| P0-F06 | reconcile AGENTS | scoped diff | อนุญาต business RAG/Vision ตามงานใหม่ ไม่ปลด safety |
| P0-F07 | split tasks/worktrees | task board/file ownership | ไม่มี simultaneous writers บน shared files |
| P0-F08 | lock decisions | ADR-001 + owner list | stack และ business type ชัด; unresolved data ไม่แอบ approve |

## ขั้นตอน

1. ตรวจ `git status --short`, `git rev-parse HEAD`, branch และ AGENTS ใน scope เก็บรายงานก่อน mutation ถ้า working tree สกปรก ห้ามลบ/overwrite ให้สร้างงานแยกหรือเก็บงานตาม owner intent
2. อ่าน `main.py`, router, config, services, tests, scripts ที่จะรัน ตรวจ script ก่อน execute โดยเฉพาะ install-hallmark ไม่รัน global installer
3. สร้าง venv ตาม 03 ติดตั้ง requirements รัน existing tests บันทึก stdout/stderr ที่ redacted ถ้าทดสอบ fail ให้แยก existing defect กับ regression จากงานใหม่
4. เปิด local port ที่ไม่ชนงานอื่น เก็บ desktop/mobile baseline และ positive/negative flows จาก AGENTS
5. เก็บ B01/B02/B03 ตาม 07 ก่อนแก้ กรณีไม่มี Vision ให้บันทึก capability absence ไม่สร้าง latency/output ปลอม
6. สร้าง feature branch และ progress ledger; pin versions หลัง resolve สำเร็จ ห้าม freeze environment ที่มี dependencies โครงการอื่น
7. ปรับ AGENTS minimal: coursework RAG/Vision และ business scope; ไม่แก้ global config ใช้ current instructions ที่สัมพันธ์งาน
8. บันทึก risk จาก session/raw streaming/storage errors เป็นงานใน P2/P4

## Gate G0

รู้ exact HEAD และสถานะ test ทุกชุด; baseline evidence อยู่แล้ว; branch isolated; setup มีเหตุผล reproducible; งานขาด key ระบุชัด; task ownership พร้อม ถ้า runtime ยังตั้งไม่ได้ให้แก้ installation blocker ก่อนอ้างผ่าน แต่ corpus planning สามารถทำคู่ขนาน

## Handoff

MAIN ส่ง PHASE_0_REPORT, baseline commit/hash, instruction diff และคำถามรวม owner เรื่องชื่อธุรกิจจริง/แหล่งข้อมูล/สมาชิก/credentials แล้วเริ่ม P1 ไม่รอให้ owner ตัดสินใจทุกเทคนิค
