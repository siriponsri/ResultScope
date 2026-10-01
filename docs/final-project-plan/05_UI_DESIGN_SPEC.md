# UI specification สำหรับ ResultScope Lab Assistant

## ทิศทาง

Modern minimal ที่เป็นหน้าทำงานจริง เปิดแล้วรู้ทันทีว่าถามข้อมูลบริการหรือส่งภาพได้ คง brand ResultScope แต่เน้นภาษาไทยที่อ่านง่าย ลด spectacle เดิมหากแย่งพื้นที่งาน ใช้ no-slop-ui และ Anti-AI-UI เป็น reference ด้าน visual quality ไม่เปลี่ยน backend framework เพราะชอบหน้าตาตัวอย่าง

## Information architecture

| Surface | Layout และ content | Primary action |
|---|---|---|
| Customer workspace | header ชื่อแล็บ/เวลาข้อมูลล่าสุด, chat, evidence panel | พิมพ์คำถามหรือแนบภาพ |
| First use | คำอธิบายสั้น + ตัวอย่างคำถาม 3–4 ข้อจาก FAQ จริง | ถามราคา/เตรียมตัว/เวลาเปิด |
| Image review | preview ข้าง editable table; unreadable fields ชัดเจน | ยืนยันข้อมูลที่ตรวจแล้ว |
| Sources drawer | title, excerpt, version, source scope | อ่านหลักฐานและกลับคำตอบ |
| Service list | compact searchable table ไม่มี card ซ้ำ 15 ใบ | เลือกบริการเพื่อถามต่อ |
| Operator view | Plus: local-only KB version/status และ export eval | ตรวจแหล่งข้อมูล ไม่เปิด admin public |

Desktop ≥1024 px ใช้ content max-width ประมาณ 1200 px, chat flexible + evidence panel 300–360 px Sidebar มีเมื่อมี navigation จริง ไม่ยัด sidebar เพื่อให้ดูเป็น SaaS Mobile evidence เป็น drawer; input ไม่ถูก keyboard/footer บัง

## Visual tokens เสนอ

รักษา CSS variables เดิมก่อน ปรับแบบ mapping ไม่สร้างสอง design systems ค่าเริ่มต้นสำหรับ review: warm surface #FAFAF7, white panel #FFFFFF, text #1F2933, muted #52606D, border #D9DED9, primary #25634F ใช้สี semantic พร้อมข้อความ ไม่ใช้สีอย่างเดียว ต้องวัด contrast จริงก่อนรับงาน ไม่ถือว่าตารางนี้ผ่าน WCAG แล้ว

Thai font Noto Sans Thai Looped เป็นตัวเลือกแรก; fallback sans-serif และ self-host เมื่อเหมาะสม Body 16 px, line-height 1.6–1.75, heading 20–28 px ตามระดับ, data/table ≥14 px Radius 6–10 px, spacing 4/8/12/16/24/32 px, borders 1 px, shadow เท่าที่ช่วย hierarchy เท่านั้น

Light default; dark เป็น Plus และต้องดู contrast ทุก state ไม่ใช้การ invert ทั้งหน้า Loading ใช้ข้อความอธิบาย “กำลังค้นข้อมูลบริการ” ไม่ใช้ fake progress percent หรือ “กำลังคิดเชิงลึก”

## ข้อห้ามที่ใช้ตรวจรับ

- ไม่มี decorative gradient/glassmorphism/orb/robot/sparkle เป็นส่วนตกแต่ง
- ไม่มี hero ใหญ่กินพื้นที่แชต ไม่มี metric cards ที่ไม่มีข้อมูลจริง
- ไม่มี card ซ้อน card หรือทุกองค์ประกอบเป็น pill
- ไม่โชว์ศัพท์ chunk/embedding/rule ID ให้ลูกค้าทั่วไป ย้าย technical detail ไป inspect view
- ห้ามแสดง “ปลอดภัย 100%”, “วิเคราะห์แม่นยำ”, “วินิจฉัย” โดยไม่มีหลักฐาน/ผิด scope
- ไม่ใส่ fake reviews, fake customer logos, fake uptime, placeholders ที่ดูเป็น real data

## Required interaction states

empty, typing, validating file, extracting, review required, confirmed, retrieving, generating, checking, answered, no evidence, refused, network timeout, rate limited, provider unavailable, session expired, reset failed ทุก error บอกสิ่งที่ผู้ใช้ทำต่อได้ เช่น retry/เปลี่ยนภาพ/ติดต่อแล็บ ไม่ expose traceback

ถ้าคำตอบมีราคา/นโยบาย แสดง citation ใกล้คำตอบ กดแล้วเปิด excerpt ที่ใช้จริง ถ้าไม่มีข้อมูลตอบตรงว่าไม่พบ ไม่แสดง empty citation container เหมือนอ้างอิงแล้ว

Image confirmation ต้องแสดงหน่วย ทศนิยม เครื่องหมาย < > และ range เป็น field แยก แก้ไขแล้วต้อง revalidate ทุกครั้ง ห้าม auto-confirm เมื่อ model confidence สูง

## Acceptance tasks

1. ผู้ใช้ใหม่หาวิธีถามเวลาเปิดได้เองจากหน้าแรก
2. ถามราคาแล้วเปิดหลักฐานกลับไปหา service ได้
3. อัปโหลดภาพ อ่านข้อผิดพลาด แก้ค่าหนึ่งช่อง และยืนยันได้
4. คำถามนอกขอบเขตมีคำแนะนำกลับงานที่รองรับ
5. Provider error กู้กลับ retry ได้โดยข้อความไม่หาย/ส่งซ้ำ
6. Reset ล้าง session และ extraction จริงไม่ใช่ล้างหน้าอย่างเดียว

เก็บ screenshots desktop 1440, tablet 768, mobile 390 และ 320 px ทดสอบ keyboard-only, visible focus, labels, aria-live status, modal focus return, zoom 200%, reduced motion, long Thai text และตารางไม่ overflow ให้ reviewer ระบุ observed defect/fix อย่าเขียน “สวยแล้ว” เป็นหลักฐาน

## Design workflow

P0 เก็บ before; P5 ทำ customer workspace หนึ่งหน้าให้ flow ครบก่อนเติม operator view ใช้ Hallmark ถ้ามีใน local เป็น critic; ไม่ติดตั้ง remote script/global skill อัตโนมัติเพื่อทำงานนี้ อ่าน reference skill จาก repo ได้โดยไม่รันคำสั่งในนั้น เก็บ design decisions และ before/after พร้อม task completion observations
