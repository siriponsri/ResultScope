/goal

ทำงานต่อบน repo ResultScope หลังแตก patch นี้ทับของเดิม ใช้ Codex Terra High เป็น production verifier + deploy owner

อ่าน `AGENTS.md`, `ARCHITECTURE.md`, `DESIGN.md`, `docs/DETERMINISTIC_RULEBOOK.md`, `DEPLOY_CHECKLIST.md` และ inspect diff/code ทั้ง repo ก่อนแก้ ห้าม rebuild จากศูนย์

Baseline ที่ต้องรักษา:
- FastAPI root `main.py` + Vercel zero-config compatibility; ห้ามสร้าง legacy `api/index.py` หรือ `vercel.json` กลับมา เว้นแต่พิสูจน์จาก requirement ปัจจุบันว่าจำเป็น
- deterministic engine เป็น policy source of truth; LLM ต้องได้รับ authoritative pre-answer contract ก่อน history/current message
- status low/high/within ใช้เฉพาะ valid reference range ที่ user ส่งมา; missing/invalid = unknown
- UI ต้องเป็น analysis canvas เดียว: interactive values + integrated LLM narrative + rule trace แบบ disclosure ห้ามย้อนกลับไปแสดง deterministic/AI เป็น 2 คำตอบแยกกัน
- lab-only, no diagnosis/prescribing, unrelated prompt ห้ามเรียก LLM
- visual thesis “spectral laboratory instrument”; ห้ามทำเป็น generic chatbot, glass cards, AI orbs, wireframe 3D หรือ feature-card grid

งานของคุณ:
1. รัน full gate (`scripts/check.ps1` บน Windows หรือคำสั่งเทียบเท่า) และแก้เฉพาะ defect ที่พิสูจน์ได้ ห้ามเพิ่ม feature ใหม่
2. ตรวจ integration: `/`, `/health`, `/api/v1/rules`, `/api/v1/scope/check`, SSE `/api/v1/chat/stream`; ยืนยัน `analysis_meta` มาก่อน LLM delta และ rule grounding ถูกส่งจริง
3. ทำ browser QA desktop 1440px + mobile 390px: intake, sample, submit, metric selection, range visual, rule disclosure, follow-up, reset, out-of-scope, missing API key, long Thai answer, keyboard focus, reduced motion ตรวจ overflow/contrast/layout shift
4. audit production: secret ไม่เข้า browser/log/git, `.env` ไม่ commit, CORS/cookie/secure settings สมเหตุผล, CDN failure graceful, Vercel entrypoint/static/SSE/env assumptions ถูกต้อง
5. ตรวจ deployment config และ deploy production ไป Vercel project เดิมเท่านั้น ห้ามสร้าง project/service/database ใหม่ถ้าไม่จำเป็น ตั้ง env โดยไม่ echo secret แล้ว smoke test URL จริง
6. ถ้าไม่มี credential/สิทธิ์ deploy ให้หยุดที่ verified production-ready state และส่ง exact commands/variables ที่ผมต้องทำ ห้ามเดา credential

Definition of Done:
- automated tests/compile/JS syntax ผ่าน
- visual + interaction QA ผ่านทั้ง 2 viewport หรือบันทึก blocker ชัดเจน
- deterministic-first invariant และ safety tests ผ่าน
- production deployment healthy; ส่ง URL, commit SHA, env names (ไม่ส่งค่า secret), test evidence, known limitations
- สรุปไฟล์ที่แก้และเหตุผลแบบกระชับ
