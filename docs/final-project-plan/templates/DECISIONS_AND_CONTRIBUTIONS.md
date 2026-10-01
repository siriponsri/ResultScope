# บันทึก decisions และการมีส่วนร่วม

## Decisions

| ID | Decision | Current position | Owner/status |
|---|---|---|---|
| D01 | ธุรกิจประเภทใด | ห้องแล็บตรวจสุขภาพ | ผู้ใช้เลือกแล้ว 1 ต.ค. 2569 |
| D02 | ชื่อธุรกิจจริง/permission | ยังไม่ทราบ | PENDING_OWNER ก่อนแจ้งชื่อ 3 ต.ค. |
| D03 | รายการ/นโยบายร้าน | ยังไม่มี approved source ในแพ็กเกจ | PENDING_OWNER |
| D04 | Stack | reuse FastAPI/HTML/CSS/JS | proposed implementation default |
| D05 | RAG | small corpus retrieval; LightRAG optional | MAIN verify P2 |
| D06 | Provider/model/budget | ใช้ที่ owner ตั้งและทดสอบ capability | PENDING_CONFIGURATION |
| D07 | สมาชิกผู้ส่ง | เดี่ยวหรือคู่ยังไม่ยืนยัน | PENDING_OWNER |
| D08 | Publish audience/hosting | local first; external publish ยังไม่อนุมัติในแผน | PENDING_RELEASE_DECISION |

## Human contribution log

| Date | Human name | Task IDs | Work performed | Review/learning evidence | Commit/artifact |
|---|---|---|---|---|---|
| — | — | — | ยังไม่เริ่ม | — | — |

## AI assistance log

| Date | Tool/agent role | Tasks assisted | Human verification | Limitations |
|---|---|---|---|---|
| 1 ต.ค. 2569 | ChatGPT planning assistant | อ่านโจทย์/static repo inspection/จัดแผน | owner เลือก business type | ยังไม่ implement/run tests |

## ADR template

Decision ID/title; context; options considered; selected approach; reason; consequences; affected files/contracts; verification; rollback เปลี่ยนข้อเท็จจริงของธุรกิจไม่ได้ด้วย ADR ทางเทคนิค
