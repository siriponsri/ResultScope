# Master plan ResultScope Lab Assistant

## เป้าหมายและขอบเขต

ต่อยอด `siriponsri/ResultScope` ให้เป็นผู้ช่วยลูกค้าของห้องแล็บตรวจสุขภาพขนาดเล็กหนึ่งแห่ง ตอบภาษาไทยจากคลังข้อมูลที่ธุรกิจรับรอง รับภาพเอกสารอย่างเหมาะสม แสดงแหล่งอ้างอิง ปฏิเสธการแต่งนโยบายและการขอข้อมูลคนอื่น มีผลทดสอบตรวจสอบย้อนกลับได้ และนำเสนอใน product catalog ด้วยสถานะ prototype

ฐานโค้ดที่ตรวจ: `78ae247d671d507cbf68225aa87a73621a7872e1` บน main วันที่ 1 ต.ค. 2569 ถ้า local HEAD ต่างไปให้ Phase 0 ทำ delta audit ไม่ reset ย้อนทับงานผู้ใช้ ชุดแผนนี้ไม่ได้ยืนยันว่ารุ่นดังกล่าวรันผ่าน

## ผู้ใช้และงานหลัก

| ผู้ใช้ | งาน | ความสำเร็จที่สังเกตได้ |
|---|---|---|
| ลูกค้าแล็บ | ถามบริการ ราคา เวลาเปิด เตรียมตัว | ได้คำตอบตรงข้อมูลที่เผยแพร่ พร้อมแหล่งอ้างอิง |
| ลูกค้าแล็บ | ส่งภาพใบรายการ/ผลแล็บจำลอง | เห็นข้อมูลที่อ่านได้ แก้ไขและยืนยันก่อนนำไปใช้ |
| ลูกค้าที่ข้อมูลไม่พอ | ถามสิ่งที่ไม่มีในคลัง | ได้คำตอบว่าไม่พบและทางติดต่อที่มีอยู่จริง |
| เจ้าของธุรกิจ | ตรวจคลังความรู้และคำถามที่ตอบไม่ได้ | สืบกลับได้ว่าใช้ source/version ใด ไม่มีตัวเลข dashboard สมมติ |
| ผู้สอน/ผู้ประเมิน | รันซ้ำและทดสอบโจมตี | มี source, setup, test evidence, diagrams ที่ตรงรุ่น |

## Release tiers

| ระดับ | สิ่งที่รวม | เป้าหมาย |
|---|---|---|
| R1 Coursework core | Business KB, Thai RAG + citations, image extraction/confirmation, safety, usable UI, evidence 10/5/5 + 3 improvements | ต้องเสร็จใน 7 วัน |
| R1 Plus catalog demo | Export, feedback, operator KB status, real usage counters, light/dark, branding configuration | ทำใน Phase 5 เมื่อ R1 core ผ่าน |
| R2 Pilot | Operator auth/RBAC, persistent audit, approval/publish KB, LINE OA, handoff ticket, deployment hardening | Phase 7 หลัง coursework release |
| R3 Commercial | Tenant isolation, billing, SSO, integrations, operational service levels, privacy/security/domain review | Phase 8 หลัง pilot evidence |

คำว่า full options หมายถึงมีแผนและ backlog ครบ ไม่เปิดทุกฟีเจอร์พร้อมกันจนส่งงานไม่ได้ ห้ามแสดงปุ่มที่ดูเหมือนใช้งานได้แต่เป็น mock แล้วนำเสนอว่า finished

## สถาปัตยกรรมที่เลือก

คง FastAPI `main.py`, Python, HTML/CSS/JS, OpenAI-compatible provider และ store abstraction เดิม เพิ่ม service modules ขนาดเล็ก ไม่ย้ายไป Chatbot UI/AionUi/Flowise ทั้งระบบ ไม่จำเป็นต้องมี runtime multiagent เพียงเพราะใช้ fo multiagent ในการพัฒนา

RAG ค่าเริ่มต้น: corpus แบบ versioned Markdown/JSON + multilingual embeddings ที่สร้างในขั้นเตรียมข้อมูล + vector retrieval ขนาดเล็กและ lexical match สำหรับชื่อบริการ/รหัส ก่อนเรียก LLM ต้องมี retrieval จริงและคืน source IDs ไม่ใช่ใส่เอกสารทั้งหมดลง prompt แล้วเรียก RAG ใช้ numeric facts ราคา/เวลาจาก structured records และตรวจคำตอบก่อนส่ง

LightRAG เป็นทางเลือก adapter เมื่อพิสูจน์ว่าจำเป็น/ผู้สอนยืนยัน ไม่เป็น dependency เริ่มต้นของ corpus 15 รายการ MCP และ LINE ไม่ใช่ข้อบังคับที่ปรากฏในไฟล์โจทย์

## แผน 7 วันและ gates

| วัน | Phase | ผลส่งมอบ | Gate |
|---|---|---|---|
| 2 ต.ค. เช้า | P0 Baseline | inventory, tests, clean branch, evidence baseline | G0 รู้สถานะจริงและติดตั้งซ้ำได้ |
| 2 ต.ค. บ่าย | P1 Business/KB | business brief, corpus, FAQ, source manifest | G1 ข้อมูลครบและระบุ provenance |
| 3–4 ต.ค. | P2 RAG/API | routing, retrieval, citations, abstention, session fixes | G2 ถามไทยและอ้างแหล่งได้ |
| 4–5 ต.ค. | P3 Vision | upload, extract, review/confirm, retention | G3 ภาพ 5 กลุ่มทำงานครบ |
| 5–6 ต.ค. | P4 Safety | input/output policy, isolation, limits, failure handling | G4 adversarial tests ผ่าน |
| 6–7 ต.ค. | P5 UI/catalog | minimal UI, responsive states, Plus ที่เวลาเอื้อ | G5 journey ใช้เองได้ |
| 8 ต.ค. | P6 Release | testsจริง, 3 improvements, 2 diagrams, video plan, reproducible package | G6 พร้อมส่งตรวจ |

3 ต.ค. owner แจ้งชื่อธุรกิจแก่ผู้สอนเอง เอกสารไม่อ้างว่าส่งชื่อให้แล้ว 9–16 ต.ค. เป็น buffer เพื่อแก้ fail และซ้อมนำเสนอ 17 ต.ค. ส่งงานตามช่องทางผู้สอน

ประมาณการวางแผน: งาน owner/MAIN 6–8 ชั่วโมงต่อวัน ร่วมกับ agents แยก implementation/review; จัดเวลารวม 42–56 ชั่วโมง ไม่ใช่ benchmark ความเร็ว fo ถ้าเวลาจริงน้อยกว่า ให้ตัด R1 Plus ก่อนและใช้ buffer โดยไม่ตัด rubric

## Dependency และ parallel work

P0 → P1 → P2 → P3 → P4 → P5 → P6 เป็น integration order งาน UI shell เริ่มขนาน P2 ได้หลัง API contract ตกลง งาน safety tests เริ่ม P1 ได้ งาน Vision adapter เริ่มขนาน retrieval ได้หลัง schema lock แต่ MAIN รวมแต่ละ gate ตามลำดับ

REVIEW ต้องอ่าน diff และผลทดสอบจาก merged HEAD ไม่รับคำกล่าวของ IMPLEMENT อย่างเดียว แต่ละงานมีผู้เขียนหนึ่งรายต่อไฟล์ ใช้ worktree/branch ตามไฟล์ 03 ห้ามสอง agents แก้ `routers/chat.py` พร้อมกัน

## Decision authority

MAIN เลือก implementation ภายในขอบเขต ทดสอบ แก้ bug ปรับ schema แบบ compatible เพิ่ม dependency ที่มีเหตุผล และ commit local ได้ บันทึก ADR สั้นเมื่อเปลี่ยนทางเลือกสำคัญ ไม่ถามเรื่อง routine

ต้องรับข้อเท็จจริงจาก owner: ชื่อธุรกิจ/แหล่งข้อมูลจริง ค่าใช้จ่ายที่เพิ่ม การเชื่อมบัญชี การส่งข้อความถึงบุคคลอื่น ขยายข้อมูลส่วนบุคคลจริง และ public/production release การมีแผน deploy ไม่เท่ากับอนุมัติเผยแพร่ตอนนี้ งาน source/fixtures/tests ทำต่อได้ระหว่างรอ

## Cut rules และความเสี่ยง

- จบ 4 ต.ค. RAG ยังไม่ผ่าน: หยุด Plus ทั้งหมด ใช้ corpus สะอาดและ retrieval เดียว ตัด graph/MCP ออก
- จบ 5 ต.ค. Vision ยังไม่นิ่ง: จำกัด JPEG/PNG ทีละภาพ มี manual correction; การพิมพ์เองช่วยกู้ flow แต่ไม่ทดแทนข้อกำหนดรับภาพ
- จบ 6 ต.ค. safety ยัง fail: freeze features แก้ก่อนทำ polish; ห้ามปิด tests เพื่อผ่าน
- ติด provider: ทำ mocked transport tests ได้ แต่ live evidence ต้อง NOT_RUN/BLOCKED จนรันจริง ไม่มี API key ไม่ใช่เหตุให้อ้างว่าส่งการบ้านครบ
- ข้อมูลร้านยังไม่พร้อม: ใช้ synthetic สำหรับพัฒนา แต่ G1 ด้านข้อมูลธุรกิจและ G6 final remain blocked
- licensing ของ upstream ยังไม่ชัด: เก็บ attribution และแก้สิทธิ์ก่อน commercial release; catalog ใช้สถานะ demo พร้อมข้อจำกัด

## Definition of done

ครบ rubric ตามไฟล์ 02, tests ผ่านบน commit ที่ส่ง, ไม่มี high-severity defect ค้าง, ทำ fresh setup ได้, sources กับ image fixtures ไม่มีข้อมูลบุคคลจริง, clip ≤180 วินาที, diagrams ตรง route/service จริง, owner อธิบาย pipeline และข้อจำกัดได้ ผลที่ยังไม่รันหรือฟีเจอร์อนาคตแยกชัดเจน
