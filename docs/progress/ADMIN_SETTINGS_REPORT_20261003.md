# รายงานการดำเนินงาน Admin Settings และ Provider Boundary

วันที่: 3 ตุลาคม 2569  
สาขา: `main` ภายในเครื่อง  
สถานะการเผยแพร่: ยังไม่มีการ push และยังไม่มีการ deploy

## สรุปสถานะ

ระบบรองรับหน้า Admin Settings แยกจากหน้าใช้งานหลัก โดยหน้าใช้งานหลักยังเปิดให้ผู้ใช้ทั่วไปเริ่มใช้งานได้โดยไม่ต้องเข้าสู่ระบบ และไม่แสดงการตั้งค่าโมเดลก่อนเริ่มวิเคราะห์ หน้า Settings และ API ที่เกี่ยวข้องถูกจำกัดไว้ภายใต้ local-demo mode ที่เปิดใช้อย่างชัดเจนเท่านั้น

การกำหนด provider ปัจจุบันเป็นดังนี้:

- Typhoon LLM ใช้สำหรับสร้างคำตอบผ่านสัญญา OpenAI-compatible
- Typhoon OCR ใช้สำหรับอ่านภาพเอกสารแล็บผ่าน adapter แยกต่างหาก
- OpenThai-SystemOne ผ่าน iApp ใช้เป็น decision/routing observer ใน shadow mode เท่านั้น
- Python rules ยังคงเป็นผู้ตัดสินใจหลัก และ safety/output validation ยังคงทำงานหลัง provider boundary
- Clef ถูกปิดใช้งาน และไม่มี fallback ไปยัง provider ที่มีค่าใช้จ่าย
- มี catalog และ adapter compatibility สำหรับ OpenRouter, OpenAI, Groq, DeepSeek, Hugging Face, LM Studio, OpenCode-compatible, Gemini compatibility path, Claude native path และ MaxPlus ตามข้อจำกัดของ protocol แต่ยังไม่มีการยืนยัน live ในรอบนี้

## การควบคุมความปลอดภัย

| รายการ | สถานะ | หลักฐาน |
|---|---|---|
| การเข้าถึงหน้า Settings โดยไม่ยืนยันตัวตน | PASS | `/admin/settings` เปลี่ยนเส้นทางไป `/admin/login` |
| การป้องกัน API config/test/logout | PASS | `tests/test_admin_settings.py` ครอบคลุม anonymous access และ CSRF |
| Session cookie | PASS | HttpOnly, SameSite และ Secure เมื่อใช้ HTTPS |
| Session expiration และ login rate limit | PASS | focused tests ผ่าน |
| Default password `admin / 1234` | PASS เฉพาะ local-demo | production/staging และ Vercel ถูกปิดก่อน authentication |
| Key write-only | PASS | browser เห็นเฉพาะ `configured/not configured`; key เดิมไม่ถูกส่งกลับ |
| การเก็บ key | PASS สำหรับ local-demo | เก็บแบบเข้ารหัสในไฟล์ที่ถูก ignore; cloud persistence ยัง BLOCKED |
| Provider endpoint | PASS | browser เลือกได้เฉพาะ provider catalog ที่ server allowlist |
| Save กับ Test connection | PASS | Save ไม่เรียก provider; mock test ไม่ใช้โควตาและไม่เปิด network |

## การเปลี่ยนภาษาเว็บแอป

ข้อความที่ระบบแสดงในหน้า home, upload/review, result surface, citation disclosure, error state และ Admin Settings ถูกปรับเป็นภาษาอังกฤษทั้งหมด การตรวจภาษาใน browser ที่ desktop และ viewport กว้าง 390px ไม่พบอักษรไทยใน UI และไม่พบ horizontal overflow

การปรับนี้ไม่จำกัดภาษาของผู้ใช้หรือภาษาของคำตอบจาก LLM โดย system prompt ระบุให้โมเดลสนทนาได้ทุกภาษาและรักษาภาษาที่ผู้ใช้เลือก คำภาษาไทยที่ยังอยู่ใน source เป็น keyword สำหรับตรวจ scope หรือเป็นข้อมูลทดสอบ ไม่ใช่ข้อความ UI

## ผลการตรวจสอบ

| การตรวจสอบ | ผล |
|---|---|
| focused admin/provider/UI suite | PASS: 56 tests |
| browser desktop home | PASS |
| browser desktop Settings | PASS |
| browser mobile home ที่ 390px | PASS |
| browser mobile Settings ที่ 390px | PASS |
| Save โดยไม่เรียก provider | PASS |
| Mock provider test | PASS; ไม่ใช้โควตาและไม่เรียก external provider |
| Secret non-disclosure ใน browser | PASS |
| Live Typhoon LLM | NOT_RUN ตาม owner instruction |
| Live Typhoon OCR | NOT_RUN ตาม owner instruction |
| Live OpenThai-SystemOne | NOT_RUN ตาม owner instruction |
| Independent O1/O2 review ของ candidate สุดท้าย | NOT_RUN; runtime/account ยังไม่พร้อม |

## Readiness decision

### Local-demo readiness

**READY สำหรับการสาธิตภายในเครื่องแบบ mocked/local** ภายใต้เงื่อนไขต่อไปนี้: เปิด `LOCAL_DEMO_MODE` อย่างชัดเจน ใช้ synthetic/mock provider test เท่านั้น ไม่ใส่ key จริงใน repository และตรวจว่าไฟล์ local secret ไม่ถูกนำไป commit

### Online readiness

**BLOCKED** และห้ามอ้างว่า production-ready เนื่องจากยังไม่มี durable secret store ที่ยืนยันสำหรับ Vercel/cloud, ยังไม่มี live provider contract/quality verification, ยังไม่มี independent review ของ candidate สุดท้าย และยังไม่มี operational controls สำหรับการใช้งานจริงหลาย instance

ไม่มีการเติมเครดิต เปิด auto top-up เรียก live provider หรือ deploy ในรอบนี้
