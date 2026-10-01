# ผลตรวจ source และการผูกเกณฑ์การบ้าน

## หลักฐานที่อ่าน

อ่านข้อความทั้งหมดจาก `Final Project.docx` รวม OOXML ตรวจแล้วไม่มีรูปแนบหรือ table เพิ่ม ในหัวข้อ “ต้นแบบประกอบด้วยส่วนต่อไปนี้” ไม่มีรายการต่อท้ายในไฟล์ จึงใช้ checklist LLM/API/UI/RAG/Prompt/Safety ด้านท้ายเป็นข้อกำหนดที่มองเห็น ไม่เพิ่มข้อบังคับ MCP, LINE หรือ Llama Guard เอง

อ่าน GitHub repository tree, README, AGENTS, BUSINESS_BRIEF, NOTICE และ source สำคัญของ ResultScope ที่ commit `78ae247d671d507cbf68225aa87a73621a7872e1` รวม `routers/chat.py`, `config.py`, `services/llm_client.py`, `services/store.py`, `services/deterministic_engine.py`, requirements ไม่ได้ติดตั้ง dependencies เรียก provider หรือทดสอบเว็บไซต์ในรอบจัดแผนนี้

## Fit และ gap

| จุดตรวจ | สิ่งที่พบใน source | งานที่ต้องทำ |
|---|---|---|
| FastAPI/API | มี chat/stream, reset, rules, models, scope/product | reuse เพิ่ม contract และ route สำหรับภาพ/citations |
| Lab domain | deterministic parser/flag + lab scope ก่อน LLM | คงแกนเดิม เพิ่ม business routing ไม่ให้ราคา/เวลาเปิดถูก block |
| RAG | request ปัจจุบันส่ง history + rule grounding; tree ที่ตรวจไม่มี retrieval service | สร้าง corpus/index/retrieval + source provenance |
| Vision | ChatRequest มี message อย่างเดียว ไม่มี upload route ใน router ที่อ่าน | เพิ่ม validated image pipeline แยก extract และ confirm |
| Grounding | rules ใส่เป็น system contract แต่ไม่เห็น post-generation validator ใน chat path | ข้อความว่า enforced ใน trace ไม่พิสูจน์ว่า LLM ทำตาม ต้องตรวจจริง |
| Session | รับค่า cookie เดิมมาใช้เป็น store key ตรง ๆ | เซ็น/ตรวจ session token; ทดสอบ tampering/ข้าม session |
| Storage | SQLite local; Upstash; memory fallback | persistence errors ต้องแสดง/ตรวจพบ; ห้ามส่ง success ลบทั้งที่ลบไม่สำเร็จ |
| Streaming | ส่ง delta ให้ client ก่อนตรวจผลรวม | buffer ก่อน output validation หรือแสดงเฉพาะ status ระหว่างรอ |
| Provider errors | บาง path ส่ง raw provider detail ไป client | map error เป็นข้อความปลอดภัย เก็บ correlation ID |
| Dependencies | requirements เป็น lower bounds แบบ >= | resolve ใน clean environment แล้ว lock รุ่นที่ทดสอบจริง |
| UI | template + CSS/JS มีอยู่แล้ว | static source ไม่พิสูจน์หน้าตาจริง ต้องถ่าย before/after ใน P0/P5 |
| Tests | มี parser/scope/engine/store/API contract files ใน tree | รัน baseline จริง; เพิ่ม retrieval, vision, security, end-to-end |
| Product | brief วาง white-label lab education ไว้แล้ว | ขยาย customer service ที่ตรงโจทย์ และระบุ prototype status |

## ข้อกำหนดจาก repo ที่ต้อง reconcile

`AGENTS.md` เดิมบอกไม่เพิ่ม OCR/RAG/auth/billing/full profiles ถ้าไม่ถูกขอ คำขอ Final Project นี้เป็น authorization สำหรับ RAG + image/Vision และแผนผลิตภัณฑ์ ไม่ใช่เหตุให้หยุดถามซ้ำ ให้ P0 ปรับบรรทัดนี้เฉพาะ coursework expansion และ domain gate จาก lab-only เป็นบริการแล็บ + education ที่คุมขอบเขต ห้ามปลดข้อจำกัดวินิจฉัย/สั่งยา/เปิด key ห้ามแก้ global fo configuration

`NOTICE.md` เตือนว่าต้นทาง `chacharin/chatbot-it-kmitl` ไม่ปรากฏ explicit root software license ณ ตอนเตรียม starter Metadata ต้นทางที่อ่านครั้งนี้ก็ไม่ให้ license identifier จึงบันทึก permission status เป็น unresolved ก่อน commercial distribution ห้ามเติม MIT ทับทั้ง repo แล้วถือว่าแก้สิทธิ์ครบ

## Requirement traceability

| ID | เกณฑ์จากโจทย์ | Phase | หลักฐานรับงาน |
|---|---|---|---|
| H01 | ธุรกิจบริการ/ค้าปลีกขนาดเล็กหนึ่งราย | P1 | business brief + source/permission register |
| H02 | KB ≥5 หน้า หรือ ≥15 รายการบริการ | P1/P2 | corpus manifest พร้อม count และ version |
| H03 | ไม่ใช้ข้อมูลส่วนบุคคลจริง | ทุก phase | synthetic fixture manifest + data review |
| H04 | LLM ตอบตรงคำถาม | P2/P6 | Q01–Q10 output จริง |
| H05 | API ทุก endpoint ที่ใส่ใน diagram ทำงาน | P2–P6 | route inventory/OpenAPI + endpoint smoke |
| H06 | UI ใช้เองได้ มี loading/error | P5 | usability tasks + screenshots |
| H07 | RAG ตอบจากคลังเป็นภาษาไทย | P2 | retrieved chunks + citations + answers |
| H08 | Prompt ต้องทำ/ห้ามทำ | P1/P4 | policy spec + sampled cases |
| H09 | Safety | P4 | S01–S05 และ regression cases |
| H10 | 10 คำถาม + answer/pass/time | P6 | evaluation table ทุกแถวมี run_id |
| H11 | 5 ภาพ + analysis/pass | P3/P6 | fixture hash + expected/actual |
| H12 | 5 security cases | P4/P6 | attack/output/pass + reason |
| H13 | 3 improvements + before/after | P0–P6 | immutable baseline และ after same case |
| H14 | Architecture diagram | P6 | as-built diagram + commit |
| H15 | Data flow ของหนึ่งข้อความ | P6 | as-built trace + diagram |
| H16 | Demo video ≤3 นาที | P6 | MP4 duration + walkthrough |
| H17 | FAQ 10 และ must/must-not | P1 | FAQ + policy |
| H18 | Source code ทำงานซ้ำได้ | P0/P6 | lock/setup/env example + fresh run |
| H19 | บทบาท/ความก้าวหน้าคนทำงานคู่ | P0/P6 | human contribution log; ถ้าเดี่ยวระบุเดี่ยว |

ทุกแถวสถานะเริ่ม NOT_RUN หรือ PLANNED จนมีหลักฐานจริง Requirements traceability เป็นเกณฑ์ตรวจ ไม่ใช่ผลสอบที่รับประกันว่าอาจารย์จะให้ผ่าน
