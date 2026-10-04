# รายงาน Phase 6: Local Product และ Coursework Closeout

วันที่: 4 ตุลาคม 2569  
สาขา: `main` ภายในเครื่อง  
HEAD ที่ตรวจสอบ source และ `scripts/check.ps1`: `16c39a065b92dfabe8f7b12ec21e1d2b73b537c1`  
สถานะการเผยแพร่: ยังไม่มีการ push และยังไม่มีการ deploy; commit ถัดไปเป็น metadata ของรายงานเท่านั้น

## ขอบเขตที่ดำเนินการ

Phase 6 เป็นการรวบรวมหลักฐานของ candidate ภายในเครื่อง ไม่ใช่การอนุมัติ
production และไม่เปลี่ยน historical gates G0/G1/G3/G4 ให้เป็น PASS

| ส่วนงาน | สถานะ | หลักฐาน |
|---|---|---|
| Phase 4A: public reference | PASS แบบ offline/local | `addons/resultscope_evidence_v1/verify.py`, 50 addon tests, `tests/test_public_reference.py` |
| Phase 4B: evidence/provider boundary | PASS แบบ mocked/local | context packet เป็น untrusted data, server citation allowlist, sync/SSE parity, Clef disabled |
| Phase 5: first-use UX | PASS แบบ mocked/local | หน้า home จริง, PNG/JPEG upload review/correction, retry/reset, desktop/mobile evidence |
| Phase 6: เอกสารและ capability matrix | PASS แบบ local closeout | `RELEASE_CHECKLIST.md`, `docs/product/CAPABILITY_MATRIX.md`, architecture/message-flow, รายงานชุดนี้ และ `docs/progress/DEMO_SCRIPT_PHASE_6.md` |
| Live provider quality | PARTIAL / BLOCKED | ตรวจ live bounded แล้ว; รายละเอียดใน `docs/progress/LIVE_PROVIDER_VERIFICATION_20261004.md` |
| Human usability validation | NOT_RUN | ไม่มีผู้ทดสอบอิสระ; screenshot ไม่ใช่หลักฐานความเข้าใจของมนุษย์ |
| Independent O1/O2 final review | NOT_RUN | ต้องใช้ receipt ของ review exact SHA; ไม่อ้าง approval จาก MAIN inspection |

## หลักฐานการทดสอบ

- `powershell -ExecutionPolicy Bypass -File .\scripts\check.ps1`: PASS, exit 0,
  `195 passed`, 1 existing Starlette/httpx warning
- Addon `verify.py`: PASS, 50 tests; 17 source PDFs, 26 numeric records,
  2 guideline PDFs และ 3 educational notes
- Addon `evaluate.py`: tree `15/15`, flat baseline `12/15`; เป็น fixture
  retrieval-only comparison ไม่ใช่ live RAG quality หรือ clinical study
- Focused public-reference/Phase 4/Phase 5 suite: `53 passed`, 1 warning
- Python compileall, JavaScript syntax checks และ `git diff --check`: PASS
- Browser evidence: desktop และ 390px mobile ครอบคลุมหน้า home/Settings,
  upload boundary, source disclosure, reset/retry, no-hit และ mocked SSE

ชุดคำถาม Q01-Q10 ใน `docs/progress/evidence/phase4-6-cases-20261003.md`
ยังมีสถานะ `BLOCKED` ตามจริงเมื่อใช้ release corpus ที่ยังไม่มี owner-approved
business data; ไม่ใช้ public hospital references แทน business facts. ชุดภาพ I01-I05
เป็น synthetic fixtures และชุดความปลอดภัย S01-S05 เป็น deterministic/mocked
evidence ไม่ใช่ live-provider evidence

## สิทธิ์และข้อจำกัด

Public hospital records อยู่ใน namespace `public_reference` และ WHO notes อยู่ใน
namespace `open_guideline`; ทั้งสองยัง `release_eligible=false`. WHO supplement
ระบุใบอนุญาต `CC BY-NC-SA 3.0 IGO` และไม่ใช่สิทธิ์เชิงพาณิชย์แบบไม่จำกัด
จึงยังไม่ถือเป็น approved business corpus หรือ commercial release data.

Typhoon LLM ใช้สำหรับสร้างคำตอบ, Typhoon OCR ใช้ผ่าน adapter แยกสำหรับภาพ PNG/JPEG,
และ OpenThai-SystemOne ผ่าน iApp เป็น shadow observer เท่านั้น. Python routing,
safety และ output validation ยังคงมีอำนาจตัดสินใจหลัก. Clef และ paid fallback
ยังถูกปิดใช้งาน. PDF OCR ยัง `NOT_RUN/BLOCKED` เพราะ raw HTTP contract และ runtime
สำหรับ PDF ยังไม่ได้ยืนยัน.

## Readiness decision

**Local-demo readiness: READY แบบมีเงื่อนไข** สำหรับ Admin Settings, public-reference
lookup แบบ offline, mocked provider tests และ image workflow ที่มีอยู่ โดยต้องเปิด
โหมด local-demo อย่างชัดเจนและใช้ข้อมูลสังเคราะห์เมื่อทดสอบ provider.

**Online readiness: BLOCKED.** ยังไม่มี durable secret store ที่อนุมัติสำหรับ
Vercel/cloud, live provider contract/quality evidence, PDF OCR transport,
independent review ของ final SHA, owner-approved business data/rights และ
operational controls สำหรับหลาย instance. จึงห้ามอ้าง production-ready.

## วิธีรัน local candidate

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
powershell -ExecutionPolicy Bypass -File .\scripts\check.ps1
uvicorn main:app --reload
```

สำหรับ Admin Settings ให้เปิด `LOCAL_DEMO_MODE=true` เฉพาะ local และเข้าที่
`/admin/login`. ห้ามใส่ key ใน chat, Git, report หรือ Project Brain. ไม่มีการเติม
เครดิต เปิด auto top-up หรือ deploy.

## Live verification addendum วันที่ 4 ตุลาคม 2569

Owner อนุญาต live calls แบบจำกัดด้วยข้อมูลสังเคราะห์และ key จาก local Admin
Settings เท่านั้น ผลจริงถูกบันทึกใน `docs/progress/LIVE_PROVIDER_VERIFICATION_20261004.md`.
Typhoon LLM ใช้ `5/5` attempts และ live transport ผ่าน; public-reference
generated answers ใน main app 3 ครั้งถูก output validation ปฏิเสธ แต่ direct
evidence-packet response ครั้งสุดท้ายผ่าน validator พร้อม citation. Typhoon OCR ใช้
`6/5` attempts ซึ่งเกินงบหนึ่งครั้งและหยุดทันที;
มีทั้ง malformed extraction หนึ่งครั้ง และ extraction ที่อ่านค่า/หน่วย/ช่วงอ้างอิง
ตรง expected พร้อม review/confirm ผ่านในครั้งต่อมา. SystemOne ใช้ `6/5` attempts
เมื่อนับ Admin probe, main-app shadow calls และ runner; ผล typed choice จาก runner
เป็น `lab` ตรง expected และยังเป็น shadow-only.

ข้อค้นพบนี้ไม่ใช่ clinical validation และยังไม่เปลี่ยน online readiness จาก
`BLOCKED`. ไม่มีการเติมเครดิต เปิด auto top-up push หรือ deploy.

หลังปิด live cycle มี offline remediation ใน commit `24b1783` ซึ่งเพิ่มคำสั่งให้
provider ระบุ source IDs แบบ bracketed และห้ามสร้าง citation/URL เอง พร้อมผล
`scripts/check.ps1` `196 passed`. Live re-validation หลัง remediation เป็น
`NOT_RUN` เพราะ LLM budget ถูกใช้ครบแล้ว.
