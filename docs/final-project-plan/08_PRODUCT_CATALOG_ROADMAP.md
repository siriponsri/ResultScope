# Product catalog และ full options roadmap

## Product definition

ชื่อทำงาน ResultScope Lab Assistant ผู้ช่วยข้อมูลบริการและเอกสารของห้องแล็บตรวจสุขภาพ ลดภาระตอบคำถามซ้ำและช่วยลูกค้าอ่านข้อมูลที่แล็บอนุมัติ กลุ่มลูกค้าหลักคือห้องแล็บขนาดเล็ก/คลินิกที่มีบริการแล็บ เริ่มหนึ่งธุรกิจก่อน

จุดต่างที่ตั้งใจพิสูจน์: คำตอบอ้างแหล่งจริง, ภาพที่ผู้ใช้ตรวจแก้ได้, ราคา/นโยบายไม่เปลี่ยนตามคำสั่งลูกค้า, ขอบเขตคำอธิบายแล็บตรวจสอบได้ และ UI ไทยใช้งานเองได้ ทั้งหมดเป็น target จนมีผลทดสอบ

## Catalog entry หลัง R1 ผ่าน

ใช้สถานะ **Demonstrable prototype** ระบุ capabilities ที่เปิดจริง, deployment mode ที่ทดสอบ, demo screenshot, architecture, test run summary, integration options และ known limitations ไม่ใช้ production-ready/medical-grade/guaranteed accuracy ข้อมูลสังเคราะห์ต้องระบุใน demo

ข้อเสนอ commercial ยังเป็นสมมติฐาน: setup/configuration fee + usage-based service หรือ white-label subscription ไม่กำหนดราคาขาย/ROI/จำนวนผู้ใช้โดยไม่มีข้อมูลลูกค้าและ cost measurement

## Feature portfolio

| Capability | R1 core | R1 Plus | R2 pilot | R3 commercial |
|---|---|---|---|---|
| Thai business Q&A + citations/abstention | ทำ | — | ขยาย eval | service-level targets |
| JPEG/PNG extraction + correction | ทำ | — | PDF multi-page pipeline | throughput/security review |
| Lab numeric rules + bounded education | คง/ปรับ grounding | — | expert-reviewed KB | intended-use review ก่อนขยาย claims |
| Feedback/export | — | ทำเมื่อ gates ผ่าน | persistent workflow | configurable retention |
| KB administration | versioned files/CLI | local status | authenticated approve/publish/rollback | tenant workflow/permissions |
| Brand/light-dark | basic light | configuration/dark | per organization | tenant theming |
| Observability | request metadata | real counters | alerts/cost/quality trend | ops SLA/SLO |
| Channels | web | — | LINE OA/handoff | channel policy/quotas |
| Booking | อธิบายวิธีจอง | — | request ticket มี human confirmation | scheduler integration/idempotency |
| Auth | isolated anonymous sessions | — | operators/RBAC | SSO and access reviews |
| Tenancy | ธุรกิจเดียว | — | หนึ่ง pilot ต่อ deployment | tested tenant isolation |
| Payments | ไม่ทำ | — | ไม่จำเป็น | billing หลัง pricing validation |
| MCP/AgentScope | ไม่บังคับ | — | read-only adapter spike | workflow เฉพาะที่มีหลักฐานว่าคุ้ม |
| LIS/LIMS/patient integration | ไม่ทำ | — | discovery เท่านั้น | separate data/clinical/security gate |

## Pilot success criteria ที่ต้องตกลงก่อนใช้จริง

เจ้าของแล็บรับรอง corpus, operator อนุมัติการ publish, ไม่มี open critical/high defect, isolation/delete/audit tests ผ่าน, restore drill ทำได้, owner ของ incident ชัดเจน และใช้ข้อมูลตามขอบเขตที่อนุมัติ วัด unanswered rate และ correction rate จากการใช้งานจริงโดยไม่โฆษณาผลก่อนวัด

## Commercial gates

สิทธิ์ source/dependencies/assets ชัด, privacy/health-data handling และ vendor terms ได้รับการตรวจตาม use case จริง, expert review ตาม intended use, load/cost budgets วัดจริง, backup/restore/rollback, tenant isolation, support/incident process ครบ รายการนี้เป็นงานก่อน release ไม่ใช่คำรับรอง compliance ปัจจุบัน

Full roadmap ไม่มีวันที่ส่งมอบผูกมัดหลังสัปดาห์แรก P7 ประเมินใหม่หลัง core evidence (กรอบประมาณ 1–2 สัปดาห์สำหรับ pilot subset เมื่อข้อมูล/credentials พร้อม) P8 ต้อง estimate จาก integrations/requirements จริง ห้ามถือว่า agent เพิ่มทำให้ความเสี่ยงทั้งหมดหมดไป
