# ResultScope Coursework Demo Data v1

ชุดข้อมูลสมมติ พร้อมแล็บ สำหรับนำเข้าหลัง Phase 2 ปิด goal แล้ว ใช้เป็น canonical demo facts ภายในสถานการณ์สมมติเท่านั้น ไม่ใช่ข้อมูลร้านจริงหรือ clinical guidance การยอมรับธุรกิจสมมติตามโจทย์ยัง PENDING_INSTRUCTOR_CONFIRMATION

## ติดตั้ง
แตกโฟลเดอร์นี้ที่ `docs/coursework-demo/ResultScope_Coursework_Demo_v1/` ใน repo อย่าคัดลอกทับ knowledge/, evaluation/ หรือ source เดิม ให้ MAIN อ่าน 01_INTEGRATION.md แล้วทำ mapping ตาม schema ของ Phase 2 จริง

## สิ่งที่มี
corpus มี business/policy/document guide และ 15 services ราคาสมมติ; evaluation มีคำถาม 10 + holdout 5, safety 5, expected images 5; images มี PNG สังเคราะห์ 5 ภาพ ไม่มีข้อมูลบุคคลจริง ไม่มีผลทดสอบสำเร็จล่วงหน้า

ตัวแปร Marker-A/B/C ไม่ใช่ analytes จริง มีไว้ทดสอบ OCR/หน่วย/ช่วงเท่านั้น Corpus ไม่ให้คำแนะนำการเตรียมตรวจ งดอาหาร ปรับยา หรือแปลผลทางคลินิก รายการบริการใช้ชื่อทั่วไป แต่ราคาทั้งหมดเป็นตัวเลขแต่งขึ้น

## ขอบเขตหลักฐาน
ข้อมูลนี้เป็นแหล่งข้อเท็จจริงของ demo ไม่พิสูจน์ runtime capability, clinical validity, หรือการยอมรับของผู้สอน การทดสอบภาพภาษาอังกฤษไม่พิสูจน์ OCR ภาษาไทย ถ้าจะอ้างรองรับภาพไทยต้องเพิ่มภาพไทยและทดสอบจริง ภาพเป็นเอกสารเรียบที่สร้างจากโค้ด ไม่ใช่ภาพถ่ายมือถือหลายสภาพแสง

## Source separation
index ได้เฉพาะ canonical source paths ใน manifest ห้าม index README, integration plan, evaluation, expected answers, images injection หรือ manifest เป็น business knowledge services.json และ 04_SERVICES.md เป็นข้อมูลเดียวกัน ให้เลือก representation เดียวต่อ source ID ไม่เพิ่มเป็นเอกสารคนละแหล่ง

ชุดนี้ไม่ได้แก้ schema/code ของ repo โดยตรง ทุก record ยัง synthetic ไม่ owner_approved_real และ commercial_release_eligible=false
