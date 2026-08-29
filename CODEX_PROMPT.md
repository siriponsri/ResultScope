# Ready-to-paste Codex CLI prompt

อ่าน `README.md`, `AGENTS.md`, `ARCHITECTURE.md`, `BUSINESS_BRIEF.md` และ inspect code ทั้ง repo ก่อนแก้ไข

เป้าหมายคือยกระดับ ResultScope V0.1 ซึ่งต่อยอดจาก Week 7 FastAPI/Vercel chatbot ให้ดูเป็น early-stage health-tech product ที่ CEO/อาจารย์เห็นแล้วเข้าใจ business path ได้ทันที โดยห้ามทำให้ deployment ซับซ้อนเกินงาน

งานหลัก:
- audit UI/UX ด้วย Hallmark ถ้ามี skill ติดตั้งอยู่ แล้วแก้เฉพาะจุดที่ทำให้ hierarchy, trust, responsive, accessibility และ product identity ดีขึ้น
- รักษา visual direction แบบ clinical/editorial, typography-driven, no AI-slop
- ตรวจ symbolic lab-only scope gate ให้ถามเรื่องผลแลปได้กว้าง แต่คำถามนอก scope ต้องไม่เรียก LLM
- ตรวจ follow-up context เช่น “แล้วต้องกังวลไหม” หลังคุยเรื่อง lab ให้ทำงาน
- รักษา structured response policy และห้าม diagnosis/prescribing
- รักษา SQLite local + optional Upstash on Vercel; อย่าอ้างว่า SQLite durable บน serverless
- ทำ UI ให้แสดง `OWNER_NAME` ชัดเจนเพื่อใช้ส่งการบ้าน
- อย่าเพิ่ม OCR/RAG/auth/payment ใน iteration นี้
- เพิ่ม test เฉพาะเมื่อ behavior เปลี่ยน

ก่อนจบให้รัน compile/tests, audit security basics (API key/secret leakage), ตรวจ Vercel entrypoint และสรุปไฟล์ที่แก้ + manual smoke test ที่ผมต้องทำ
