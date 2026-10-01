# Phase 5 UI modern minimal และ catalog demo

เวลาเป้าหมาย: 6–7 ต.ค. 6–8 ชั่วโมง งาน shell เริ่มขนาน P2 ได้ Owner: IMPLEMENT_UI; REVIEW visual/functional; MAIN integrate อ่าน 05 ก่อนแก้ UI

## Entry

Contract จาก P2/P3 stable; final integration ต้อง G4 ผ่าน แยก customer UI กับ operator tooling ไม่มี admin route สาธารณะเพียงเพราะต้องการ screenshot dashboard

## Work items

| ID | งาน | Files | Acceptance |
|---|---|---|---|
| P5-F01 | simplify customer workspace | templates/index.html | first use บอกงานที่ทำได้ มี primary action ชัด |
| P5-F02 | tokens/layout/Thai typography | static/css/tokens.css, style.css | 320–1440 px usable, contrast measured |
| P5-F03 | chat/status/error/source UX | static/js/chat.js | states จาก 05 ครบ citation เปิด excerpt จริง |
| P5-F04 | image review integration | UI image module | edit/confirm/cancel ไม่สูญเสีย field/units |
| P5-F05 | legacy result presentation | result view | one integrated object; unknown ไม่ถูกตกแต่งเป็น normal |
| P5-F06 | Plus actions | export/feedback/theme | เฉพาะเวลาพอ; ปุ่มที่เปิดต้องทำงานจริง |
| P5-F07 | accessibility/browser QA | screenshots + findings | keyboard, zoom, mobile, long Thai, recovery ผ่าน |
| P5-F08 | catalog demo assets | docs/product/DEMO.md | claims ตรง implemented/tested features |

## ขั้นตอน

1. เก็บภาพ baseline เดิมเพื่อเทียบ อ่าน existing tokens และ DESIGN.md เลือกคง identity ที่ใช้งานได้ ตัด scene/animation ที่รบกวนโดยมีเหตุผล
2. ทำ one-page workflow: ถามบริการ→อ่านคำตอบ→เปิดแหล่ง, แนบภาพ→review→confirm, reset/error recovery
3. เก็บรายละเอียดทางเทคนิคใน collapsible inspector เฉพาะผู้ตรวจ ไม่ใช้ rule IDs/embedding เป็น microcopy ลูกค้า
4. Source drawer ต้องแสดง title/version/excerpt ที่ request ใช้ ไม่เปิด source ล่าสุดจนขัดกับคำตอบเก่า
5. กระบวนการระหว่างรอใช้ status ชัดเจน ปิด double-submit และยกเลิก request อย่างถูกต้อง Retry ไม่ duplicate history
6. ปรับ mobile input/evidence/image table ให้ไม่ล้น ใช้ proper labels/aria status และ focus return
7. เมื่อ core ผ่านและมีเวลา ทำ Plus ตามลำดับ feedback→session export→dark theme→local KB status/counters โดยเก็บข้อมูลจริงเท่านั้น ตัดได้พร้อมรายงาน deferred
8. นำเสนอ product catalog เป็น prototype มี screenshot ที่ถ่ายจริง ไม่ fake dashboard หรือ testimonial

## Browser verification

ต้องทดสอบบน API จริง local ที่ integration HEAD mocks ใช้ทดสอบ error states เพิ่มได้แต่แยกไว้ ทำ acceptance tasks 6 ข้อใน 05 เก็บ outcome และ defects ถ้ามีผู้ลองใช้ใหม่ได้ให้จด observation โดยไม่อ้างจำนวนผู้ทดสอบเกินจริง

เช็ก narrow 320 px, 390 px, 768 px, 1440 px และ 200% zoom ไม่มี horizontal overflow ของหน้าทั้งหน้า ตาราง scroll เฉพาะ container ได้ ข้อความไทยไม่ตัดเกินเหตุ ปุ่มแตะง่าย Keyboard ทุก action เข้าถึงได้

## Gate G5

Customer journey ครบ loading/error/refusal/no evidence/review states ไม่เหลือ broken mock CTA; visual review มี screenshots และแก้ defects สำคัญ; UI claims ไม่เกินขอบเขต เวลาหมดให้ defer Plus ไม่ลด safety หรือ evidence core

## Handoff

ส่ง design decisions, screenshot paths, browser environment, UX defects ที่เหลือ, Plus implemented/deferred matrix ให้ P6 อัปเดต catalog card ตามสิ่งที่ทำจริง
