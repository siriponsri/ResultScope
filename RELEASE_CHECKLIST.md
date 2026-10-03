# รายการตรวจสอบความพร้อมของ ResultScope

เอกสารนี้เป็นรายการตรวจสอบสำหรับ candidate ภายในเครื่อง ไม่ใช่การอนุมัติ
สำหรับ production และไม่อนุญาตให้ตีความว่าเป็น production-ready

| รายการ | สถานะ | หลักฐานหรือข้อจำกัด |
|---|---|---|
| FastAPI root `main.py` และรูปแบบ Vercel zero-config | PASS | ยังคงใช้ root ASGI app และไม่มี `api/index.py` หรือ `vercel.json` ที่ถูกลบกลับมา |
| Scope gate ก่อนเรียก LLM | PASS | Python routing และ safety tests ผ่าน; คำถามนอกขอบเขตไม่เรียก provider |
| Typhoon LLM สำหรับสร้างคำตอบ | PASS แบบ mocked/local | Live contract, quota และคุณภาพยัง NOT_RUN |
| Typhoon OCR สำหรับอ่านภาพ/PDF | PASS แบบ adapter/local | Live OCR และคุณภาพการอ่านยัง NOT_RUN |
| OpenThai-SystemOne ผ่าน iApp | PASS แบบ shadow boundary | ใช้ adapter/parser แยก; ไม่แทน Python rules หรือ output validation; live ยัง NOT_RUN |
| Clef และ paid fallback | PASS | Clef ปิดใช้งานและไม่มี fallback ไป provider ที่มีค่าใช้จ่าย |
| Provider compatibility catalog | PASS แบบ server allowlist | มี slot สำหรับ OpenRouter, OpenAI, Groq, DeepSeek, Hugging Face, LM Studio, OpenCode-compatible, Gemini, Claude และ MaxPlus; การยืนยัน live ยัง NOT_RUN |
| English web UI | PASS | ตรวจ desktop และ mobile แล้วไม่พบข้อความภาษาไทยใน UI |
| LLM รองรับการสนทนาหลายภาษา | PASS ตาม system contract | ยังไม่มี live language-quality evaluation |
| Upload/OCR review flow | PASS แบบ mocked/local | มีการตรวจไฟล์ แก้ไขค่า ยืนยัน/ยกเลิก และ session-bound extraction |
| Public reference และ citation allowlist | PASS แบบ offline/local | สิทธิ์และ corpus ธุรกิจที่อนุมัติยังเป็นข้อจำกัดแยกต่างหาก |
| Admin Settings local-demo | READY สำหรับ local demo | มี auth, HttpOnly/SameSite/Secure cookie, expiration, CSRF, rate limit และ logout |
| Secret write-only และ local persistence | PASS สำหรับ local demo | key เดิมไม่ส่งกลับ browser; cloud/Vercel durable persistence ยัง BLOCKED |
| Save/Test separation | PASS | Save ไม่เรียก provider; mock test ไม่ใช้โควตาและไม่ retry |
| Full project test suite | PENDING final run | ต้องยืนยันกับ candidate SHA หลังการแก้ภาษาและเอกสารรอบนี้ |
| `scripts/check.ps1` | PENDING final run | ต้องรันก่อน commit ปิดงาน |
| Independent O1/O2 review | NOT_RUN | runtime/account ยังไม่พร้อม จึงไม่มี approval claim |
| Live provider verification | NOT_RUN | ไม่มี key จริงตาม owner instruction และไม่มี external call |
| Deployment | NOT_DEPLOYED | owner ระบุให้ทำ local main เท่านั้น |

## Readiness decision

- **Local-demo readiness:** READY สำหรับการสาธิตภายในเครื่องแบบ mocked/local เมื่อเปิด local-demo mode อย่างชัดเจนและไม่ใช้ live provider
- **Online readiness:** BLOCKED เนื่องจาก cloud secret persistence, live provider verification, independent review และ operational controls สำหรับหลาย instance ยังไม่ครบ

ก่อนพิจารณา release ในอนาคต ต้องจัดหา durable secret store ที่เหมาะสม ยืนยัน provider contracts ด้วยสิทธิ์ที่อนุมัติ ทดสอบคุณภาพแบบ live ตามงบที่อนุมัติ และได้รับ independent review ของ candidate SHA ที่แน่นอน
