# Phase 1 กำหนดธุรกิจและคลังความรู้

เวลาเป้าหมาย: 2 ต.ค. บ่ายถึง 3 ต.ค. เช้า Owner: MAIN + backend/data; REVIEW ตรวจ sources เกี่ยวข้อง H01–H03, H08, H17

## Entry และข้อเท็จจริง

Business type ถูกเลือกเป็นห้องแล็บตรวจสุขภาพแล้ว ชื่อจริงยังรอ owner ไม่เปลี่ยนเป็นร้านยา/ธุรกิจอื่นเอง ชื่อทำงาน ResultScope Lab Demo ใช้เฉพาะ development วันที่ 3 ต.ค. ต้องพร้อมให้ owner แจ้งชื่อแก่ผู้สอน

## Work items

| ID | งาน | Output | Acceptance |
|---|---|---|---|
| P1-F01 | business brief | docs/business/BRIEF.md | ชื่อ/กลุ่มเป้าหมาย/pain points/ข้อมูลพื้นฐานพร้อม source |
| P1-F02 | source provenance | knowledge/source_manifest.json | origin/permission/status/version/checksum ครบ |
| P1-F03 | normalize service catalog | knowledge/services.json | ≥15 จริงและ distinct หรือพิสูจน์เอกสาร ≥5 หน้า |
| P1-F04 | policies + FAQ | knowledge/policies + FAQ.md | FAQ 10 ตอบได้จาก source หรือระบุ gap |
| P1-F05 | chatbot policy | docs/business/BOT_POLICY.md | must/must-not ชัด และทดสอบได้ |
| P1-F06 | gold set | evaluation/cases.jsonl | expected source/facts freeze ก่อน tuning |
| P1-F07 | corpus validation | validation script/test | invalid/duplicate/unapproved record ถูกจับ |

## รูปแบบคลังที่ควรสร้าง

`knowledge/business.md`, `knowledge/services.json`, `knowledge/policies/*.md`, `knowledge/education/*.md`, `knowledge/source_manifest.json` แยก public facts จาก personal session data ไม่ทำ index ประวัติลูกค้า

Service fields: service_id, name_th, aliases, description, price/currency ถ้ามีจริง, specimen/preparation/result turnaround เฉพาะที่ source ระบุ, source_id, version อย่าบังคับทุก field ต้องมีค่าจน agent เติมเอง Unknown=null พร้อม contact fallback

FAQ 10 หัวข้อ: เวลาเปิด, ที่ตั้ง/ติดต่อ, ราคา, เทียบบริการ, เตรียมตัว, จอง/walk-in, รับผล, ระยะเวลา, ยกเลิก/คืนเงิน, ข้อมูลไม่พบ ถ้าร้านไม่มีนโยบายคืนเงินจริง ให้ expected เป็น “ไม่มีข้อมูลยืนยัน” แทนสร้างนโยบาย

## ขั้นตอน

1. รวบรวมเฉพาะข้อมูล public/owner-authorized แยก original source กับ cleaned record เก็บ checksum และวันที่อ่าน
2. ทำ source_status draft/approved/retired ห้ามใช้ draft ใน retrieval release
3. ตรวจว่าจำนวนรายการตรงกันและไม่มีการแตกหนึ่งบริการเป็นชื่อซ้ำเพื่อให้ครบ 15 ถ้าเลือก ≥5 หน้า ให้เก็บวิธีนับและเอกสารต้นทางที่เพียงพอ
4. ราคา/เวลามี effective/version; conflict ระหว่าง sources ต้อง owner resolve ไม่เลือกเองตาม similarity score
5. สำหรับ education ให้ใช้ข้อมูลที่ business/domain owner ตรวจและรับรองเป็น KB ห้ามสร้างคำแนะนำทางการแพทย์ลอย ๆ เพื่อเติมเนื้อหา
6. สร้าง must-do: ตอบไทย, อ้างแหล่ง, ไม่รู้ให้บอก, ให้ตรวจ OCR, รักษาหน่วย; must-not: แต่งส่วนลด, เปิดข้อมูลผู้อื่น, วินิจฉัย, สั่งยา, รับรอง payment จากภาพ, อ้าง booking สำเร็จ
7. Freeze expected answers/source IDs ของ Q01–Q10 และ holdout อย่างน้อย 5 paraphrases ที่ไม่ใช้ tune

## Tests

ตรวจ unique IDs, numeric price/nonnegative เมื่อมีค่า, source FK, approved status, checksum, missing permissions, no PII, expired/conflicting policy มี safe handling Sources ที่ยังไม่ approved ต้องไม่เข้า release index

## Gate G1

ธุรกิจ/คลังมี provenance และ rubric quantity ผ่าน พร้อม FAQ/policy/gold set Owner source approval ที่ยังขาดให้ BLOCKED เฉพาะ G1-data เริ่ม P2 ด้วย fixtures ได้ แต่ยังไม่ปิด G1 หรืออ้าง final ready

## Handoff

ส่ง corpus version/hash, list approved source IDs, unknown facts ที่ต้อง abstain, gold set ให้ P2 UI ใช้ labels ที่ยืนยันแล้ว; ไม่ปล่อย agent แต่ละตัวแต่ง facts คนละชุด
