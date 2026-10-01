# Phase 2 Business routing และ Thai RAG

เวลาเป้าหมาย: 3–4 ต.ค. 10–12 ชั่วโมง implementation/integration Owner: IMPLEMENT_BACKEND; MAIN ครอง router/config; REVIEW ตรวจ grounding เกี่ยวข้อง H04/H05/H07

## Entry

G0 ผ่าน; corpus schema/fixtures และ expected sources พร้อม P1-data อาจ blocked แต่ต้องแสดง synthetic mode Contracts 04 เป็น target ให้วาง schema migration ก่อน UI เริ่มผูก API

## Work items

| ID | งาน | Files เป้าหมาย (ใหม่ถ้ายังไม่มี) | Acceptance |
|---|---|---|---|
| P2-F01 | business/lab intent routing | services/intent_router.py + scope tests | Q01/Q03 ไม่ถูก lab-only block; unrelated ไม่เรียก LLM |
| P2-F02 | ingestion/chunking | services/knowledge.py + scripts/build_index.py | source boundaries/version/hash คงอยู่ |
| P2-F03 | retrieval | services/retrieval.py | Thai query คืน expected sources; threshold calibrated |
| P2-F04 | answer grounding | services/answer_service.py | citation IDs มาจาก evidence; unknown abstains |
| P2-F05 | API integration | routers/chat.py + contracts | sync/streamใช้ pipeline เดียวกัน |
| P2-F06 | session integrity | services/store.py + session helper | token tampering/cross-session ไม่ผ่าน |
| P2-F07 | provider failures | services/llm_client.py | sanitize errors/timeout/config check |
| P2-F08 | retrieval evidence | evaluation/retrieval runs | capture query/top-k/source/latency แยกจาก answer |

## Implementation sequence

1. Define stable `RetrievedEvidence` และ `Answer` ให้ UI/REVIEW ใช้ร่วม MAIN ตัดสินใจ compatibility ของ reply/scope
2. Build index จาก approved corpus นอก request path หนึ่ง service/policy section ต่อ chunk ใช้ deterministic chunk IDs ไม่ตัดราคาออกจากชื่อบริการ
3. เลือก multilingual embedding provider/model ที่ account ใช้ได้จริงและบันทึก dimensions ตรวจ index/query model ตรงกันและ fail เมื่อไม่ตรง ไม่อ้างรุ่นที่มีในตัวอย่างว่ายังใช้ได้โดยไม่ตรวจ
4. สำหรับ corpus เล็กใช้ immutable vector artifact และ cosine search ใน process ร่วม exact/alias lexical match บันทึก top-k เริ่มเสนอ 4 แล้ว calibrate กับ dev queries Thai ไม่มีเว้นวรรคต้องทดสอบ alias/normalization ไม่ใช้ English whitespace tokenizer อย่างเดียว
5. Similarity threshold ใช้ dev set กำหนด ไม่ hard-code “0.8 แปลว่าถูก” ข้อมูลไม่พบ/คะแนนใกล้กัน/ชื่อบริการไม่ชัดให้ clarify/abstain
6. Business route ให้ facts ราคา/เวลา/นโยบายจาก structured source ที่ดึงมา LLM ทำภาษาและสรุปได้ แต่ validator ห้ามตัวเลข/นโยบายใหม่ที่ไม่มีหลักฐาน
7. Lab route คง parser/flags แต่ narrative ต้อง grounded กับ approved educational KB และข้อมูลยืนยันของผู้ใช้ ไม่มี KB ที่รองรับให้ตอบข้อจำกัด แยก fact ของผู้ใช้จากความรู้ร้าน
8. Mixed query แบ่งส่วนตอบที่มี evidence และบอกส่วนขาด ห้าม citation หนึ่งอันครอบคลุม claims ที่ไม่ได้อยู่ใน source
9. ปรับ stream ให้ status→validated answer→done เพียงครั้งเดียว ความรู้สึกเร็วจาก status ไม่ส่ง unverified content
10. Session signing/validation และ reset rotation; concurrent requests ไม่ overwrite history แบบเงียบ ใช้ serialization/revision ตาม store

## Meaningful tests

Q01–Q10, follow-up ambiguity, duplicate service names, old/new prices, retired source, embedding mismatch, no retrieval hits, fabricated citation, mixed benign+unsafe, cookie tampering, missing API key, provider 401/429/timeout, stream interruption ทดสอบ callback/provider spy ว่า unrelated bypass LLM จริง

Unit mocks พิสูจน์ transport/error branches; live runs พิสูจน์คำตอบไทยจริง บันทึกทั้งคู่ ถ้า key ไม่พร้อม G2-live BLOCKED ไม่เอา canned answer มาแทน

## Gate G2

UI/API ถามไทย→retrieve→answer→citation ทำงานครบ; sources resolve จริง; ราคาไม่หลุด facts; abstention ถูก; session tests ผ่าน; sync/streamไม่ bypass policy มี trace โดยไม่เก็บ secret/raw private data

## Rollback/handoff

คง index versions และ config ที่สลับกลับได้ ไม่ delete old corpus ใน migration ส่ง contracts + sample safe responses + error shapes ให้ P3/P5; freeze schema revision ใน report
