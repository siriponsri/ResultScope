# Phase 8 พัฒนาผลิตภัณฑ์เชิงพาณิชย์

เริ่มหลัง pilot evidence และ owner ตกลง scope/budget กำหนดเวลาใหม่จาก requirements จริง เป้าหมาย full options ที่เลือกใช้ ไม่ใช่ checklist ฟีเจอร์ที่ต้องยัดทั้งหมด

| ID | Workstream | Design tasks | Release evidence |
|---|---|---|---|
| P8-F01 | tenant isolation | tenant derived from auth, scoped DB queries/vector namespaces/object keys/cache/rate limits | negative tests ทุก data path รวม export/restore/background jobs |
| P8-F02 | commercial auth | organization roles, invite/revoke, optional SSO | offboarding/session revocation/audit tests |
| P8-F03 | billing/usage | meter definition, retries/dedup, payment webhook verification | duplicate/out-of-order/retry/reconciliation tests |
| P8-F04 | integrations | LIS/LIMS API contract, minimum data, consent/access boundaries | sandbox integration + provenance + error recovery |
| P8-F05 | operational reliability | load target/SLO, alerts, backup/restore, incident/rollback | measured load/cost/restore drills |
| P8-F06 | quality governance | versioned prompts/models/evals, regression gates, human feedback | canary evaluation and rollback evidence |
| P8-F07 | license/data review | upstream permission, dependencies/assets, terms/vendor/data mapping | reviewed inventory และ unresolved items ปิดก่อน relevant release |
| P8-F08 | product packaging | onboarding, operator guide, support, pricing hypothesis validation | pilot feedback และ claims tied to evidence |

## Isolation design ที่ห้ามข้าม

tenant_id จาก client ไม่เป็น authority บังคับ tenant scoping ใน repository layer และ retrieval index แยก tenants; shared cache key รวม tenant/corpus/policy; signed URLs/session/export ต้องตรวจ ownership; audit filter และ backup restore ห้ามดึงข้อมูลอีกองค์กรมา customer UI

## Integration decision

LIS/LIMS/patient profile คือการขยายข้อมูลจาก prototype อย่างมีนัยสำคัญ ต้องกำหนด purpose, field mapping, access, retention และ environment แยกก่อน ไม่ใช้ข้อมูลผู้ป่วยจริงเป็น test fixture Billing/subscription ไม่ได้แก้ upstream license หรือ clinical intended-use constraints

## Model/agent expansion

เลือก runtime agent framework ต่อเมื่อมี workflow ที่จำเป็นและวัดประโยชน์ได้ เปรียบเทียบ deterministic service orchestration กับ agent path ทั้ง latency/cost/failure/tool misuse ให้ tools least privilege และขอ human confirmation สำหรับ side effects ที่มีผลจริง ไม่ให้ LLM อนุมัติราคา/refund/access เอง

## Commercial gate G8

แต่ละ feature มี evidence ไม่ใช่ status จากแผน; licensing unresolved ปิดตามส่วนที่จะจำหน่าย; data/security/privacy/domain review เสร็จตาม intended use; operational owner/support/rollback พร้อม; customer terms/claims ไม่เกินผลที่พิสูจน์ ไม่ใช้คำ medical-grade หรือวินิจฉัยเพียงเพราะมี RAG และ guardrails

## สิ่งที่ยังอยู่นอก scope

การวินิจฉัยอัตโนมัติ การสั่งหรือปรับยา การใช้แทนผู้ประกอบวิชาชีพ และการนำข้อมูลคนจริงไปฝึกโมเดล เป็น project decision ใหม่ ไม่เกิด authorization จากคำว่า full options ในแผนนี้
