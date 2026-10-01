# Phase 7 ขยายเป็น pilot ของแล็บ

อยู่นอก critical path 7 วัน Entry: G6 ผ่านและ owner เลือก pilot subset; ประเมินกรอบ 1–2 สัปดาห์เมื่อข้อมูล/accounts พร้อม ไม่รับประกันเวลา Owner: MAIN + operator/domain owner

## เป้าหมาย

เปลี่ยน prototype ที่ดูแลผ่านไฟล์เป็นระบบที่เจ้าของแล็บควบคุมข้อมูลได้ มี operator authentication และ audit พร้อมรับคำถามจริงตาม data scope ที่อนุมัติ เริ่มหนึ่งแล็บต่อ deployment ก่อน multitenant

| ID | งาน | Implementation detail | Acceptance |
|---|---|---|---|
| P7-F01 | operator auth/RBAC | session-based auth, editor/reviewer roles, CSRF protections | unauthorized/role escalation tests ผ่าน |
| P7-F02 | KB lifecycle | draft→review→publish→retire, index build job, atomic version switch | ลูกค้าไม่เห็น draft; rollback index/corpus พร้อมกัน |
| P7-F03 | durable operations | persistence migration, audit events, backup/restore | store outage visible; restore drill verified |
| P7-F04 | feedback queue | answer_id/source versions/reviewer correction | feedback ไม่แก้ KB อัตโนมัติ; audit และ ownership |
| P7-F05 | LINE OA adapter | webhook signature, replay/idempotency, reply lifecycle | invalid signature rejected; duplicate event ไม่ตอบซ้ำ |
| P7-F06 | human handoff | explicit request ticket, status tracking | ไม่อ้าง booking/ติดต่อแล้วก่อนส่งสำเร็จและได้รับสิทธิ์ |
| P7-F07 | observability/cost | latency/error/abstention/token counters | metrics จาก events จริง พร้อม retention/redaction |
| P7-F08 | optional LightRAG/MCP spike | isolated read-only retrieval adapter | เทียบ quality/latency/costกับ simple RAG ก่อนเลือก |

## ขั้นตอน

ทำ auth ก่อนเปิด operator writes จากนั้น KB approval/publish, persistence/audit และ monitoring ทดสอบหนึ่ง end-to-end pilot journey ก่อนเพิ่มช่องทาง LINE ใช้ same answer service ไม่ copy policy คนละเวอร์ชันใน webhook

LINE ต้องใช้ credentials ที่ owner ตั้งและบัญชีทดสอบที่อนุญาต ข้อความถึงลูกค้า/admin เป็น external action ต้องกำหนดว่าใครได้รับและเมื่อใด ไม่เปิด automatic push จากตัวอย่างโดยปริยาย

LightRAG/MCP ใช้เมื่อ corpus/quality requirement มีเหตุผล เก็บ direct HTTP alternative ไม่เพิ่ม tool ingestion/deletion ให้ customer assistant Auth/error semantics ต้องทดสอบกับ version ที่ pin ปัจจุบันตาม documentation ของ server ไม่อ้าง README ว่าทุก endpoint ตรงเสมอ

PDF multi-page ถ้าต้องทำให้เป็นงานแยก: bounds pages/bytes/time, page provenance, queue, cancel และ user confirmation ไม่เพิ่มโดยหลบ image limits

## Gate G7

มี pilot owner และ source approvals, auth/role/isolation/deletion tests, KB rollback, backup restore, monitored failures, real usage evaluation ภายในขอบเขตที่ตกลง และ no unresolved high-risk defect ก่อนใช้ข้อมูลจริงต้องผ่าน data permission/security/privacy work ตาม intended use ไม่ถือว่าผ่านการบ้านแทน pilot review

## Rollback

Feature flags ปิด LINE/operator writes ได้ คืน published KB version เก่าและ verify retrieval/session schema compatibility เก็บ audit ไม่ rewrite ประวัติ
