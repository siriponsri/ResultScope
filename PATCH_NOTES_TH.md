# ResultScope deterministic-first + spectral UI patch

Patch baseline: GitHub `siriponsri/ResultScope` commit `beffd5b`

## วิธีแตกทับ

1. Commit หรือสำรองงาน local ปัจจุบันก่อน
2. เปิด ZIP แล้วนำไฟล์และโฟลเดอร์ทั้งหมดไปวางที่ **repo root** ของ ResultScope
3. เลือก Replace/Overwrite เมื่อ Windows ถาม
4. ตรวจ `git diff` ก่อน commit
5. รัน:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check.ps1
```

6. เปิด `CODEX_TERRA_GOAL.md` แล้วนำข้อความทั้งหมดไปใช้กับ Codex Terra High

ZIP นี้ไม่มี `.env`, `.env.local`, `.venv`, `.vercel`, SQLite database, cache หรือข้อมูลลับ และไม่สร้าง legacy `api/index.py` / `vercel.json` กลับมา

## สิ่งที่เปลี่ยน

- เพิ่ม deterministic rulebook แบบ versioned ครอบคลุม scope, parsing, range, grounding, safety และ integrated output
- เพิ่ม deterministic engine ที่สร้าง immutable pre-answer contract ให้ LLM อ่านก่อน history และคำถามปัจจุบัน
- เพิ่ม `GET /api/v1/rules` สำหรับตรวจ rulebook ทั้งชุด
- range flag ใช้เฉพาะ valid reference interval ที่ user ส่งมา; reversed range เป็น invalid และ missing range เป็น unknown
- รวมค่าที่ parse, range visualization, streamed LLM narrative และ rule trace ไว้ใน analysis object เดียว
- เปลี่ยน UI เป็น spectral laboratory instrument พร้อม pointer-responsive field, Read → Verify → Explain transition, selectable metrics และ progressive rule disclosure
- ตัด Three.js wireframe และ chat-bubble transcript แบบเดิม
- รองรับ reduced motion, keyboard focus, mobile value deck และ safe Markdown fallback
- ปิด wildcard credentialed CORS; same-origin เป็นค่า default และรองรับ explicit allowlist ผ่าน `CORS_ALLOWED_ORIGINS`
- อัปเดต architecture, design research, deployment checklist และ prompt ส่งต่อ Terra High

## Verification ที่รันแล้ว

- Pytest: **23 passed**
- Python compile: passed
- JavaScript syntax (`chat.js`, `scene.js`): passed
- `git diff --check`: passed
- API smoke: `/health`, `/api/v1/rules`, scope gate และ out-of-scope SSE passed

มี warning หนึ่งรายการจาก dependency ของ Starlette TestClient เรื่อง httpx API รุ่นอนาคต ไม่ใช่ test failure หรือ defect ใน application code
