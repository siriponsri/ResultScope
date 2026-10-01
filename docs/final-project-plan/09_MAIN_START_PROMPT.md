# Prompt เริ่มงานสำหรับ local fo MAIN

คัดลอกข้อความใน block นี้ไปให้ fo ที่เปิดอยู่ใน root ResultScope หลังวางชุดแผนที่ docs/final-project-plan/

```text
คุณคือ MAIN ของ ResultScope Final Project ใช้ multiagent ที่มีอยู่ใน fo ช่วย implementation และ independent review ให้ทำงานตามเอกสาร ไม่เริ่มวางแผนกว้างใหม่

อ่าน AGENTS.md และคำสั่งที่มีผลใน repo แล้วอ่าน docs/final-project-plan/00_START_HERE.md, 01_MASTER_PLAN.md, 02_SOURCE_AUDIT_AND_RUBRIC.md, 03_FO_WORKFLOW_AND_LOCAL_SETUP.md และ Phase 0

ธุรกิจที่เลือกแล้วคือห้องแล็บตรวจสุขภาพขนาดเล็ก เป้าหมายคือผู้ช่วยตอบลูกค้าจาก business KB ภาษาไทย มี RAG/citations, รับภาพและให้ตรวจแก้, safety และ UI modern minimal พร้อม evidence ตามโจทย์ 10 คำถาม/5 ภาพ/5 safety/3 improvements/2 diagrams/video ≤3 นาที

ฐานที่ผู้ช่วยจัดแผนตรวจคือ commit 78ae247d671d507cbf68225aa87a73621a7872e1 หาก HEAD ต่างให้ทำ delta audit อย่า reset งานเดิม อ่านเอกสารจริงและรัน baseline ไม่ถือคำกล่าวใน README ว่าคือผลทดสอบ

เริ่ม Phase 0 แล้วดำเนิน P1–P6 ตาม dependencies เป็นช่วง ๆ เก็บ report ทุก phase เมื่อ gate ผ่านให้เริ่ม phase ถัดไปได้ ไม่ต้องถาม owner ทุก implementation detail ใช้ branch/worktree แยกและ file ownership ชัดเจน REVIEW ตรวจ integrated commit จริงก่อนปิด phase

คำขอนี้อนุญาตขยาย coursework เดิมเพื่อ RAG และ image/Vision ปรับ AGENTS.md เฉพาะข้อจำกัดที่ขัดกับขอบเขตใหม่นี้ได้ แต่รักษา FastAPI main.py, OpenAI-compatible provider, secret isolation, Windows setup และข้อห้ามวินิจฉัย/สั่งยา ห้ามแก้ global .codex/.agent หรือ project อื่น

ยังไม่มีชื่อธุรกิจจริง/ข้อมูลร้านที่รับรองในแพ็กเกจนี้ ใช้ synthetic fixtures สำหรับพัฒนาโดยติดป้าย ห้ามแต่งราคา/นโยบายเป็นของจริง รวบรวม owner questions ครั้งเดียวก่อน deadline แจ้งชื่อธุรกิจ 3 ต.ค. 2569 ข้อมูลไม่พร้อมให้ BLOCKED เฉพาะ acceptance นั้น งานโครงสร้างและ tests ทำต่อได้

ทำ full roadmap ตาม P7/P8 ไว้ แต่เป้าหมาย 7 วันคือ P0–P6 และ R1 Plus เฉพาะเมื่อ core ผ่าน อย่าสร้าง billing, multi-tenant, runtime agents หรือย้าย stack ก่อนจำเป็น

ห้ามอ้าง PASS หากไม่รันจริง ห้ามอ้างควบคุม agent/เครื่องมือที่ไม่มี ให้ระบุข้อจำกัด เก็บ before evidence ก่อนแก้จริง และแยก mocked tests จาก live provider tests

งานใน local และ local commits ทำต่อได้ การ push, external deployment, ส่งข้อความ, ซื้อบริการหรือใช้ข้อมูลบุคคลจริงต้องอยู่ใน authorization ที่ได้รับจริง ไม่ถือว่าเอกสารนี้อนุมัติ public/production release

ผลรายงานแต่ละ phase: work item IDs, commit, changed files, commands/tests/evidence, rubric coverage, blockers/owner decisions, gate verdict และ next phase ใช้ templates/PHASE_REPORT_TEMPLATE.md

ลงมือ Phase 0 ได้เลย
```
