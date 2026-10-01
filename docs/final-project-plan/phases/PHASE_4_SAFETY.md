# Phase 4 Safety และการทนต่อความผิดพลาด

เวลาเป้าหมาย: 5–6 ต.ค. 6–8 ชั่วโมง Owner: REVIEW ออก cases; BACKEND แก้; MAIN integrate เกี่ยวข้อง H08/H09/H12

## Entry

P2/P3 pipeline ผ่าน functional checks Policy จาก P1 และ source IDs frozen เป้าหมายคือทดสอบ enforcement ไม่เพียงเพิ่ม disclaimer/system prompt

## Work items

| ID | งาน | Output | Acceptance |
|---|---|---|---|
| P4-F01 | threat model | docs/security/THREAT_MODEL.md | assets/trust boundaries/attacks/controls เชื่อม test IDs |
| P4-F02 | input policy | input validator | unrelated/unsafe route ไม่ถูก bypass ด้วย keyword lab |
| P4-F03 | output validation | output validator | unsupported facts/citations/numbers ถูก reject ก่อนส่ง |
| P4-F04 | session/ownership | integration security tests | text/image/export/reset ไม่รั่วข้าม session |
| P4-F05 | resource controls | size/rate/budget/timeouts | limits server-side; bounded retries/concurrency |
| P4-F06 | XSS/error/log hygiene | frontend/backend fixes | no unsafe HTML, no raw secret/error leakage |
| P4-F07 | adversarial evaluation | S01–S05 + extra | results ไม่แต่ง, reviewer reproduction |
| P4-F08 | guard adapter decision | ADR-guard | rule/output controls mandatory; model guard optional |

## Controls ที่ต้องมี

1. Business authorization อยู่ที่ code/data ไม่ใช่ LLM ลูกค้าบอกเป็น owner ไม่เปลี่ยนนโยบาย
2. อนุญาต citations เฉพาะ evidence ที่ retrieved ใน request นี้และ source ยัง approved
3. ราคา/หน่วย/range/status ใช้ canonical values; narrative ที่ขัด deterministic fact ต้อง fallback หรือ regenerate แบบ bounded หนึ่งครั้ง แล้ว safe response
4. ตรวจ output ทั้ง `/chat` และ `/chat/stream`; ไม่ส่ง content ออกไปก่อนตรวจ ข้อความใน status ต้องไม่เป็น draft answer
5. Session token/extraction ownership/export checks เหมือนกันทุกเส้นทาง; reset failure ไม่ส่ง “ลบแล้ว”
6. render user/LLM/source text แบบ escape หรือ sanitizer allowlist ไม่ `innerHTML` ตรง ๆ ตรวจ link protocol และไม่ใส่ event attributes
7. rate limits ต้อง shared เมื่อใช้หลาย serverless instances; per-process limit ใช้ได้เฉพาะ local demo และระบุขอบเขต
8. metadata logs มี request ID, outcome, source version, timings ไม่บันทึก raw image/keys/full reports โดย default

## Guard model

ใช้ pattern input/output/fail-closed จาก llama-guard-layer ได้ ถ้าเปิด optional guard และ call ล้มเหลว ต้องแสดง service unavailable/refusal ไม่ปล่อยผ่านว่า safe Guard model ไม่ตรวจราคา/clinical truth/tenant authorization ให้เอง อย่านำ categories จากตัวอย่างมาใช้โดยไม่ตรวจว่าครอบคลุม policy ของแล็บ

## Test execution

REVIEW เตรียม S01–S05 และ variants ก่อน IMPLEMENT แก้ ใช้ synthetic local fixtures บันทึก exact input/output/provider/commit ทดสอบทั้ง direct API และ browser เสริม encoded/mixed-language injection, OCR instructions, follow-up role spoof และ safe in-scope control เพื่อจับ false positives

Store/provider unavailable ต้องพิสูจน์จาก fault injection ที่ควบคุมเอง ไม่รอให้ของจริงพัง Test raw stream ต้องยืนยันว่าไม่มี unsafe token หลุดก่อน final verdict ไม่เพียงดูคำตอบสุดท้าย

## Gate G4

ทุก mandatory safety case ผ่านและมี evidence บน integrated HEAD; ไม่มี cross-session disclosure/output-before-check/XSS/secret leak ค้าง; false positive ที่ขวาง FAQ หลักแก้แล้ว การผ่านชุดทดสอบนี้ไม่ใช่การรับรองปลอดภัยทุกกรณี

## Handoff/rollback

ให้ P5 ใช้ error codes/refusal wording ที่ผ่าน review; ให้ P6 รับ test inventory และ residual risks หาก critical case ยัง fail ให้ freeze features และแก้ก่อน release ไม่ waive เพื่อทัน demo
