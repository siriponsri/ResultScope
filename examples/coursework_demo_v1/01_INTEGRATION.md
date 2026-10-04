# Integration หลัง Phase 2

1. อ่าน Phase 2 report, HEAD และ diff ก่อน patch ห้าม reset และห้ามเปิด Phase 3 อัตโนมัติ
2. เพิ่ม explicit mode coursework_demo หรือใช้ mode เดิมที่มีความหมายเทียบเท่า พร้อม corpus namespace/version แยกจาก release อย่าสร้างซ้ำถ้ามีแล้ว Source authority หมายถึง canonical facts ของ demo ไม่ใช่ร้านจริง
3. ให้ runtime เลือก corpus ฝั่ง server; client ห้ามเปลี่ยน source policy/tenant/mode โดยพลการ มี banner ภาษาไทย “ข้อมูลธุรกิจสมมติสำหรับการเรียน ไม่รับบริการจริง” และ response metadata data_class=synthetic, corpus_version, mode ถ้า release source ไม่พร้อมให้ fail/abstain ไม่ fallback demo
4. รักษา historical G0/G1-data blockers เพิ่มเกณฑ์ demo_data_ready แยกจาก real_business_data_ready และ instructor_acceptance ห้าม rename G1-data เป็น PASS ทั้งหมดเพื่อให้ดูจบ
5. แปลง exchange schema ให้ตรง validator ล่าสุด รักษา source IDs/checksums/ค่าขาด null; public contact example.invalid ต้องระบุ non-deliverable ไม่เปิดการส่งจริง
6. แยก corpus/index/cache ของ demo จาก release ตรวจ citation source/version ของคำตอบจริง ห้าม index test set/expected answers, source instructions หรือ image attacks
7. Q09 เป็น history จริง; holdouts ไม่ใช้ tune; expected source IDs คือ evidence ที่ต้องรองรับคำตอบ ไม่บังคับเรียก source เมื่อปฏิเสธก่อน retrieval กำหนด rubric ให้เหมาะ route
8. รัน 10 mandatory text cases + retrieval checks และ mode-isolation regression ด้วยข้อมูลนี้; แยก fake embeddings/LLM จาก live result ไม่มี key ยัง NOT_RUN สำหรับ live tests
9. ภาพเตรียมไว้สำหรับ Phase 3 เท่านั้น ไม่จำเป็นต้องเพิ่ม Vision ใน patch นี้ บันทึก compatibility ของ synthetic marker parser เมื่อเริ่ม P3 ห้าม hardcode เฉลยตามชื่อภาพ
10. Before/after 3 จุดต้องวัดจริง เก็บ raw runs/commit/model/prompt/corpus/time ไม่เอา expected เป็น actual
11. MAIN commit local เฉพาะงานนี้ อัปเดต report/Brain และให้ REVIEW ตาม capabilities จริง ห้ามอ้าง independent approval หาก worker ไม่ได้อ่าน

## Acceptance ของ data patch
- 15 distinct services มี source และราคาเดียวกันใน JSON/Markdown
- โหมด demo ค้นและอ้าง corpus ได้; release ไม่โหลด synthetic
- ราคา CBC=250, HbA1c=350, ผลต่าง=100, CBC+FPG=370
- ไม่มี preparation/turnaround policy ให้เดา; unknown เป็น abstain
- Q09 ผูก HbA1c จาก prior turn; ไม่ได้เติมคำว่า “หลังถาม A” ใน current message
- banner/metadata ชัด ไม่มีข้ออ้างส่งการบ้านครบหรือพร้อม commercial

## Business choice note
ชื่อ “พร้อมแล็บ” เป็น working fictional label ไม่ใช่การตรวจเครื่องหมายการค้าและไม่อ้างการอนุมัติจากเจ้าของธุรกิจจริง Owner อนุญาตสร้างตัวอย่างสำหรับพัฒนาแล้ว แต่ผู้สอนยังต้องยืนยันว่าใช้ธุรกิจสมมติทั้งแห่งได้
