# สคริปต์วิดีโอสาธิต ResultScope: local candidate 3 นาที

เอกสารนี้ใช้สำหรับการบันทึกวิดีโอสาธิต local candidate เท่านั้น ไม่ใช่หลักฐาน
ของ live provider, clinical validation หรือ production readiness. Web app ใช้
ภาษาอังกฤษ ส่วนคำอธิบายสคริปต์ใช้ภาษาไทยทางการ.

## ก่อนเริ่ม

- รัน `uvicorn main:app --reload` ใน local environment ที่ติดตั้ง dependencies แล้ว
- ใช้ภาพ PNG/JPEG สังเคราะห์เท่านั้น และไม่ใส่ API key จริงในวิดีโอ
- เปิด `LOCAL_DEMO_MODE=true` เฉพาะเมื่อจะสาธิต Admin Settings
- เตรียมหน้าต่าง browser ขนาด desktop และ 390px mobile

## ลำดับการสาธิต

| เวลา | การสาธิต | สิ่งที่ต้องกล่าวให้ตรงหลักฐาน |
|---|---|---|
| 0:00–0:20 | เปิดหน้าแรก | หน้าเว็บเป็นภาษาอังกฤษและมีเพียงสองทางเริ่มต้น: `Upload a report image` หรือพิมพ์คำถามเกี่ยวกับผลแล็บ ไม่ต้อง login สำหรับผู้ใช้ทั่วไป |
| 0:20–0:45 | กดตัวอย่างคำถามและส่ง | ระบบใช้ scope gate และ deterministic rules ก่อน provider; คำถามนอกขอบเขตจะถูกปฏิเสธโดยไม่เรียก LLM |
| 0:45–1:10 | อัปโหลดภาพ PNG/JPEG สังเคราะห์ | แสดงการตรวจชนิดไฟล์และ OCR review; ค่าที่อ่านไม่ชัดแก้ไขได้ก่อนยืนยัน และ PDF ยังไม่อยู่ในขอบเขต |
| 1:10–1:35 | แสดงผลลัพธ์และ source disclosure | ช่วงอ้างอิงในใบผลมีลำดับความสำคัญ; ค่าไม่พอไม่ถูกแปลงเป็นปกติ และ source metadata ถูก resolve โดย server |
| 1:35–1:55 | ถาม follow-up แล้วกด reset | แสดง session context, retry/reset และการป้องกัน duplicate submit; ใช้ผลลัพธ์ mocked/local ไม่อ้าง live quality |
| 1:55–2:20 | เปิด `/admin/settings` ใน local-demo mode | Settings แยกจากหน้าใช้งานหลักและป้องกันด้วย server-side authentication; ไม่แสดง key เดิมกลับ browser |
| 2:20–2:40 | แสดง provider cards และ Save/Test | Typhoon LLM, Typhoon OCR และ OpenThai-SystemOne แยก config; Save ไม่เรียก provider และ Test ใช้ mocked/synthetic path แบบ bounded |
| 2:40–2:55 | แสดงหลักฐานและข้อจำกัด | Clef และ paid fallback ปิด; SystemOne เป็น shadow observer; live provider, cloud secret persistence และ PDF OCR เป็น `NOT_RUN/BLOCKED` |
| 2:55–3:00 | ปิดการสาธิต | สรุปว่าเป็น local-demo readiness แบบมีเงื่อนไข ไม่ใช่ production-ready และไม่มีการ deploy/push |

## หลักฐานที่อ้างระหว่างวิดีโอ

- หน้าแรก desktop/mobile และ Settings desktop/mobile: `docs/progress/evidence/admin-settings-browser-20261003.md`
- Q01–Q10, I01–I05 และ S01–S05: `docs/progress/evidence/phase4-6-cases-20261003.md`
- รายละเอียดสถานะและ blockers: `docs/progress/PHASE_6_REPORT.md`

ห้ามบันทึก API key, password, patient identifier หรือข้อมูลผู้ป่วยจริงในภาพหน้าจอ
เสียงบรรยาย หรือไฟล์วิดีโอ.
