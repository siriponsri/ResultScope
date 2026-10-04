# รายงานการตรวจสอบ Live Provider แบบจำกัด

วันที่: 4 ตุลาคม 2569  
สาขา: `main` ภายในเครื่อง  
HEAD ที่ตรวจสอบ: `16c39a065b92dfabe8f7b12ec21e1d2b73b537c1`  
สถานะการเผยแพร่: ไม่มีการ push และไม่มีการ deploy

## ขอบเขตและการคุ้มครองข้อมูล

Owner อนุญาตการเรียก live เฉพาะ Typhoon LLM, Typhoon OCR และ OpenThai-SystemOne
ผ่าน key ที่เก็บใน Admin Settings ฝั่ง server ใช้ข้อมูลสังเคราะห์เท่านั้น ไม่มีข้อมูล
ผู้ป่วยจริง ไม่มีการเติมเครดิต เปิด auto top-up หรือใช้ paid fallback และปุ่ม
`Test with mock` ไม่ได้ถูกเปลี่ยนแปลงหรือใช้แทน live evidence.

ค่า key ไม่ถูกอ่านออกมาแสดง ไม่ถูกเขียนลง report, log, Brain หรือ Git รายงานนี้บันทึก
เฉพาะ provider/model, สถานะ, latency, จำนวน attempt และผลที่จำเป็นต่อการตรวจสอบ.

## Contract และสิทธิ์ที่ตรวจเอกสาร

- Typhoon official documentation ที่ `https://docs.opentyphoon.ai/en/authentication/`
  ยืนยัน Bearer authentication และ base URL `https://api.opentyphoon.ai/v1`.
- Typhoon model/OCR/rate-limit documentation ยืนยัน model IDs
  `typhoon-v2.5-30b-a3b-instruct` และ `typhoon-ocr`, chat path
  `/chat/completions`, รวมถึง rate limits ที่แสดงในเอกสารปัจจุบัน.
- Typhoon overview ระบุ free tier สำหรับการใช้งานเบา; สิทธิ์คงเหลือของ account
  และ billing dashboard ไม่ได้ถูกตรวจผ่าน management API.
- iApp OpenThai-SystemOne documentation ที่
  `https://iapp.co.th/docs/llm/openthai-systemone` ยืนยัน `POST
  https://api.iapp.co.th/v3/store/openthai/systemone`, header `apikey`, typed
  `state`/`questions` contract, model `openthai-systemone` และ free preview 0 IC
  พร้อม daily limit ตามเอกสารปัจจุบัน.
- SystemOne ใช้ adapter/parser แยก และถูกเรียกเป็น shadow observer เท่านั้น.
  Python routing, safety และ output validation ยังเป็น authority หลัก.

## Usage และผลจริง

| Provider | Budget | ใช้จริง | ผลรวม |
|---|---:|---:|---|
| Typhoon LLM | 5 | 5 | Live transport ผ่าน; app-route answer 3 ครั้งถูก output validation ปฏิเสธ แต่ direct evidence-packet response ผ่าน validator ในครั้งสุดท้าย |
| Typhoon OCR | 5 | 6 | **เกิน budget 1 attempt**; ไม่มีการเรียกเพิ่มหลังพบเหตุการณ์ |
| OpenThai-SystemOne | 5 | 6 | **เกิน budget 1 attempt**; ไม่มีการเรียกเพิ่มหลังพบเหตุการณ์ |

การนับ SystemOne รวม shadow calls ที่เกิดตาม main-app flow ทุกครั้ง ไม่ได้จำกัด
เฉพาะ runner หรือ Admin probe. ความคลาดเคลื่อนของ budget นี้ถูกบันทึกตามจริงและ
ห้ามนำรอบนี้เป็นแบบอย่างสำหรับการทดสอบครั้งถัดไป.

### Typhoon LLM

- Admin-bound live probe: `PASS`, model `typhoon-v2.5-30b-a3b-instruct`,
  network/quota flags เป็นจริง, latency `1467 ms`.
- Public-reference query 1: transport และ retrieval `public_reference/matched`,
  latency `5886 ms`, แต่ผลถูก fail-closed เป็น `abstained` เพราะไม่ผ่าน output
  validation และไม่มี citation ถูกส่งออก.
- Public-reference query 2: `public_reference/matched`, latency `3273 ms`,
  output validation `FAIL`, ไม่มี citation ถูกส่งออก.
- Public-reference query 3: `public_reference/matched`, latency `2397 ms`,
  output validation `FAIL`, ไม่มี citation ถูกส่งออก.
- Direct provider call ครั้งสุดท้ายใช้ evidence packet เดิมและไม่ผ่าน main app route
  เพื่อไม่เรียก SystemOne เพิ่ม: latency `915 ms`, output ระบุหน่วย `mg/dL` และ
  citations `[kku-glucose, siriraj-glucose]`; existing `validate_provider_text`
  ให้ `PASS`.
- จึงยืนยันได้เฉพาะ contract/validator path แบบ bounded นี้ ไม่อ้าง LLM quality หรือ
  clinical validation. App route ยังมี output-validation failures ที่ต้องแก้ไขก่อน
  online readiness.

### Typhoon OCR

1. Admin-bound live probe: `PASS`, model `typhoon-ocr`, latency `1135 ms`.
2. ภาพ PNG สังเคราะห์แรก: HTTP `200`, latency `2608 ms`, ได้ field ผิดเป็น
   `x1=0` และไม่มีช่วงอ้างอิง จัดเป็น `FAIL` และไม่นำไปใช้.
3. ภาพ PNG สังเคราะห์ตามรูปแบบ parser contract: HTTP `200`, latency `1768 ms`,
   อ่านได้ตรง expected 3 แถว ได้แก่ `Hb 10.8 g/dL (12-16)`, `Glucose 95 mg/dL
   (70-99)` และ `MCV 72 fL (80-100)`; สถานะยังเป็น `review_required`.
4. Flow PNG สังเคราะห์: OCR `200`, latency `1982 ms`; owner-review payload
   ผ่าน confirm เป็น `200`, revision `2`, provenance `user`.
5. Flow PNG สังเคราะห์ใน main app: OCR และ confirm ผ่าน แต่ข้อความทดสอบมีคำที่
   deterministic safety gate ปฏิเสธ จึงไม่มี LLM/SystemOne call ในขั้นนั้น.
6. Flow PNG สังเคราะห์สุดท้าย: OCR และ confirm ผ่าน แต่ main app ตอบ
   `503 release_not_ready` เพราะ release corpus ยังไม่พร้อม จึงไม่มี LLM call.

ผล OCR ข้อ 1-6 รวมเป็น `6/5` ซึ่งเป็น budget breach ที่เกิดขึ้นแล้วและถูกบันทึก
ตามจริง การทดสอบหยุดทันทีหลัง attempt ที่หก ไม่มี retry หรือ call เพิ่มเติม.
ข้อมูลที่อ่านได้ถูกส่งผ่าน review/confirm ก่อนใช้; ไม่มีการอ้างว่าภาพแรกผ่าน.

### OpenThai-SystemOne

- Admin-bound live probe: `PASS`, model `openthai-systemone`, network/quota flags
  เป็นจริง, latency `1135 ms`.
- Public-reference และ main-app lab requests เรียก shadow path ตาม implementation;
  shadow result ไม่ถูกเปิดเผยจาก main response และไม่มี error ที่เปลี่ยน Python
  route.
- Local runner ใช้ encrypted provider store เดิมและ adapter/parser เดิมกับคำถามไทย
  สังเคราะห์เรื่อง `Hb`; actual choice `lab`, expected `lab`, `PASS`, latency
  `482 ms`, `output_tokens=0`.
- SystemOne ไม่ได้แทน Python routing และไม่มีการเพิ่ม public test endpoint.
- จำนวนรวมที่นับจาก Admin probe, shadow calls ใน live app และ runner คือ `6/5`.

## Main-app และ failure handling

- ภาพสังเคราะห์ผ่านลำดับ `extract -> review_required -> confirm -> chat` จริง.
- ขั้น OCR และ confirm เป็น live/deterministic ตามลำดับ; ขั้น chat ถูกหยุดโดย
  deterministic safety หรือ `release_not_ready` ตาม input/runtime จึงไม่ใช้ผลลัพธ์
  ที่ไม่มีหลักฐาน.
- Public-reference retrieval ทำงานและคืน `matched` แต่ generated output ถูก
  fail-closed เมื่อ validation ไม่ผ่าน; citation ไม่ถูกปล่อยออก.
- Out-of-scope, auth boundary, mock separation, secret non-disclosure และ rate-limit
  focused tests ยังคงผ่านจากชุดเดิม.

## Verification หลังการตรวจ

คำสั่ง focused offline tests:

```text
tests/test_admin_settings.py
tests/test_public_reference.py
tests/test_phase3_images.py
tests/test_phase3_vision_client.py
tests/test_phase4_safety.py
```

ผล: `77 passed`, warning เดิมจาก Starlette/httpx `1` รายการ. ไม่มี runtime source
change ในรอบนี้ จึงไม่ได้รัน `scripts/check.ps1` ซ้ำ.

## Readiness และ residual blockers

**Local-demo readiness: READY แบบมีเงื่อนไข** สำหรับการสาธิตที่คุมข้อมูลสังเคราะห์,
Admin Settings, OCR review/confirm และ SystemOne shadow. Live provider transport
ทำงานได้ตาม contract และ direct LLM evidence response ผ่าน validator แต่ app-route
ยังมี output-validation failures และ OCR/SystemOne budget ถูกใช้เกิน provider ละหนึ่ง
attempt ในรอบนี้.

**Online readiness: BLOCKED.** ยังขาด durable cloud secret store, independent review
ของ exact HEAD, release/approved corpus, operational controls, account-specific
quota verification และ remediation ของ output-validation failure. ห้ามอ้าง
production-ready หรือ clinical validation.
