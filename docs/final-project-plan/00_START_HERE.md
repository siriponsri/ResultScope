# ResultScope แผนส่งการบ้านและพัฒนาผลิตภัณฑ์

จัดทำ 1 ตุลาคม 2569 สำหรับ Siripon และ local fo MAIN สถานะ: implementation plan ยังไม่ได้ลงมือพัฒนาหรือรับรองผลทดสอบระบบ

## ข้อสรุป

ใช้ ResultScope ต่อได้ และใช้ fo multiagent ช่วยพัฒนาได้ ผู้ใช้เลือกธุรกิจ **ห้องแล็บตรวจสุขภาพ** แล้ว ต้องเพิ่มงานบริการลูกค้าของแล็บเป็นเส้นทางหลัก ได้แก่ ข้อมูลบริการ ราคา เวลาเปิด การเตรียมตัว ขั้นตอนติดต่อ/จอง และนโยบายที่มีหลักฐาน ส่วนอธิบายผลแล็บเดิมเป็นความสามารถเสริมแบบมีขอบเขต ไม่เพียงเปลี่ยนหน้าตาแล้วส่งของเดิม

โจทย์ Final Project.docx วิชา 06048308 กำหนดแจ้งชื่อธุรกิจ 3 ต.ค. 2569 และส่ง 17 ต.ค. 2569 เป้าหมายพัฒนา 7 วันในแผนนี้คือ 2–8 ต.ค. เหลือ 9–16 ต.ค. สำหรับแก้ไข ซ้อม และเตรียมส่ง ไม่ใช่การรับประกันว่าจะทำ full commercial product เสร็จใน 7 วัน

## ลำดับอ่าน

1. [Master plan](01_MASTER_PLAN.md)
2. [ผลตรวจโค้ดและข้อกำหนด](02_SOURCE_AUDIT_AND_RUBRIC.md)
3. [วิธีใช้ fo multiagent](03_FO_WORKFLOW_AND_LOCAL_SETUP.md)
4. [สถาปัตยกรรมและ contracts](04_ARCHITECTURE_AND_CONTRACTS.md)
5. [แนวทาง UI](05_UI_DESIGN_SPEC.md)
6. [การเลือกใช้ repo อ้างอิง](06_REFERENCE_REPO_DECISIONS.md)
7. [แผนและชุดทดสอบ](07_EVALUATION_AND_SUBMISSION.md)
8. [แผนผลิตภัณฑ์ฉบับเต็ม](08_PRODUCT_CATALOG_ROADMAP.md)
9. อ่าน phase ตามลำดับในโฟลเดอร์ phases
10. ใช้ [คำสั่งเริ่มงาน MAIN](09_MAIN_START_PROMPT.md)

## วิธีนำไปใช้

Clone ResultScope ลงเครื่องแยกโฟลเดอร์ แล้วคัดลอกโฟลเดอร์เอกสารนี้ไปที่ `docs/final-project-plan/` โดยไม่ทับไฟล์แผนเดิม จากนั้นเปิด fo ใน root ของ ResultScope และใช้ prompt ในไฟล์ 09 เริ่ม Phase 0 ก่อน ตรวจรับ phase และลงมือ phase ถัดไปตาม dependency โดยไม่ต้องถาม owner ทุก implementation detail

เอกสารนี้ไม่มี source application ใหม่ ไม่มี API key ไม่มีผลทดสอบที่แต่งขึ้น และไม่เปลี่ยน GitHub หรือระบบบนเครื่อง Windows ของผู้ใช้ การตรวจ repository รอบนี้เป็น static inspection ไม่ใช่ runtime verification

## สิ่งที่ owner ต้องจัดหา แต่ไม่ขวางงานโครงสร้าง

- ชื่อธุรกิจจริงและข้อมูลที่ได้รับอนุญาตให้เผยแพร่; ใช้ชื่อทำงาน `ResultScope Lab Demo` ระหว่างพัฒนาเท่านั้น
- ถ้าจะใช้ธุรกิจสมมติทั้งธุรกิจ ต้องยืนยันกับอาจารย์ว่าเข้าเงื่อนไข “ข้อมูลจริงของร้าน” ไม่ตีความข้ออนุญาตข้อมูลจำลองว่าอนุญาตให้แต่งธุรกิจโดยอัตโนมัติ
- ข้อมูลบริการอย่างน้อย 15 รายการ หรือเอกสารเทียบเท่า 5 หน้า พร้อมที่มา; ภาพใช้ข้อมูลสังเคราะห์ที่ไม่อ้างว่าเป็นข้อมูลลูกค้าจริง
- API credentials และงบเรียกโมเดล ตั้งใน environment เอง ไม่ส่งผ่านแชต/commit
- ทำคนเดียวหรือคู่และชื่อผู้ส่ง เป็นเรื่องแยกจากจำนวน AI agents

งานที่ยังรอข้อมูลให้ใช้ fixture ติดป้าย synthetic และสถานะ BLOCKED เฉพาะงานนั้น ไม่บันทึกเป็นผ่านหรือข้อมูลจริง

## เอกสารราย phase

- [Phase 0 ตรวจฐานและเตรียมทำงาน](phases/PHASE_0_BASELINE.md)
- [Phase 1 กำหนดธุรกิจและคลังความรู้](phases/PHASE_1_BUSINESS_KB.md)
- [Phase 2 Business routing และ Thai RAG](phases/PHASE_2_RAG_AND_API.md)
- [Phase 3 รับภาพและตรวจยืนยันข้อมูล](phases/PHASE_3_VISION.md)
- [Phase 4 Safety และการทนต่อความผิดพลาด](phases/PHASE_4_SAFETY.md)
- [Phase 5 UI modern minimal และ catalog demo](phases/PHASE_5_UI_AND_CATALOG_DEMO.md)
- [Phase 6 ทดสอบจริงและแพ็กส่งการบ้าน](phases/PHASE_6_EVALUATION_RELEASE.md)
- [Phase 7 ขยายเป็น pilot ของแล็บ](phases/PHASE_7_PILOT_EXTENSIONS.md)
- [Phase 8 พัฒนาผลิตภัณฑ์เชิงพาณิชย์](phases/PHASE_8_COMMERCIAL_PRODUCT.md)
