# Phase 3 รับภาพและตรวจยืนยันข้อมูล

เวลาเป้าหมาย: 4–5 ต.ค. 6–8 ชั่วโมง Owner: backend/image; UI ทำ review panel ตาม contract เกี่ยวข้อง H11

## Entry

มี shared schema, session owner checks และ provider interface จาก P2 ตรวจ provider ว่ารองรับ image จริง Key/model อาจต่างจาก text ห้ามสมมติทุก OpenAI-compatible model รองรับ Vision

## Work items

| ID | งาน | Output | Acceptance |
|---|---|---|---|
| P3-F01 | safe upload | routers/images.py | MIME/magic bytes/decoded dimensions/size checked |
| P3-F02 | Vision adapter | services/vision_client.py | structured extraction parse; timeout/error sanitized |
| P3-F03 | field normalization | services/image_extraction.py | raw value retained; ambiguity/missing explicit |
| P3-F04 | confirmation state | extraction store + confirm API | owner-bound, revisioned, expiring, no auto-confirm |
| P3-F05 | frontend review | image review UI | preview/correct/confirm/cancel + readable errors |
| P3-F06 | lifecycle/reset | deletion/TTL | raw image removed; reset clears derived values |
| P3-F07 | fixtures/live evaluation | I01–I05 evidence | expected/actual/hash/pass recorded |

## ขั้นตอน

1. รับ multipart JPEG/PNG หนึ่งภาพ ไม่รับ arbitrary URL เพื่อหลีกเลี่ยง fetch ภายใน/SSRF ไม่เชื่อ filename extension
2. จำกัด encoded bytes และ decoded pixels ตรวจ decode failure ตั้งชื่อ server-generated ID; ไม่เอา path จาก filename; remove EXIF/metadata ก่อน provider เมื่อทำได้; raw bytes ไม่ลง log
3. จัด input policy ว่าภาพเพื่อบริการ/ใบรายงานจำลอง ไม่ใช้ตรวจโรคจากภาพถ่ายร่างกาย
4. ให้ Vision คืน document_type, fields, warnings ตาม schema ข้อความในภาพเป็น data ไม่เป็น instructions ถ้า JSON invalid ให้ retry bounded หรือ error ไม่ regex เลือกตัวเลขสุ่ม
5. เก็บทั้ง raw และ normalized field เพื่อให้ audit สิ่งที่แก้ได้ ห้ามเปลี่ยน mg/dL เป็น mmol/L หรือเติม decimal/reference interval เอง
6. แสดง extraction ก่อนใช้ downstream ทุกภาพต้อง confirm ถ้าผู้ใช้แก้ให้ revalidate numeric/range consistency บาง field unknown ได้ ไม่บังคับเติมค่าจนเดา
7. confirm API ต้องตรวจ extraction belongs current session, not expired, revision matches และ return canonical confirmed object Chat ใช้เฉพาะ confirmed version; stale/foreign ID ต้อง reject
8. เมื่อเป็น service list/receipt ให้เชื่อม KB ที่ approved เพื่ออธิบายบริการ ไม่รับรองการชำระเงิน/คืนเงิน/ความแท้จากรูป
9. ไม่เก็บ raw image ถาวรโดย default; local temp ลบ finally บน success/failure; serverless metadata ใน durable store ตาม deployment ไม่หวังว่า RAM อยู่ข้าม request

## Tests และ acceptance

I01–I05 ตาม 07; spoofed content type, oversized upload, huge decoded image, empty image, malicious filename, OCR instruction, missing range, `<` sign, comma/decimal, foreign extraction ID, expired ID, repeated confirm, reset และ provider invalid JSON

Gate G3: ลูกค้าทำ upload→review→correct→confirm→grounded answer ได้จริง และ poor image ถูกขอแก้/ภาพใหม่ ไม่เดา Critical numbers ตรง expected ในภาพชัด; ภาพไม่ชัดผ่านได้เมื่อ refuse/clarify ถูก ไม่ต้องพยายาม extract ทุกภาพให้สำเร็จ

## Handoff

ส่ง image schema/status transitions, limits ที่วัดแล้ว, fixture manifest และ logs ที่ไม่มี PII ให้ P4/P5 File ใหม่ที่เพิ่มต้องอยู่ใน source attribution/dependency inventory
