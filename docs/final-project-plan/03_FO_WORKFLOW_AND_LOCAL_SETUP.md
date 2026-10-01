# วิธีทำงาน fo multiagent และเริ่ม local project

## Clone หรือ pull

ถ้ายังไม่มี repo บนเครื่อง ให้ใช้ **clone** ถ้ามีอยู่แล้วจึง fetch/pull ห้าม clone ทับ directory ที่มีงาน และห้าม reset --hard เพื่อให้ตรงแผน

ตัวอย่าง PowerShell ใน parent directory ที่ผู้ใช้เลือก ไม่ได้สมมติว่าผู้ช่วยเข้าถึงเครื่อง Windows นี้ได้:

```powershell
git clone https://github.com/siriponsri/ResultScope.git
Set-Location ResultScope
git status --short
git rev-parse HEAD
git switch -c feat/final-project-lab-assistant
```

ถ้ามี clone อยู่แล้ว:

```powershell
Set-Location C:\path\to\ResultScope
git status --short
git branch --show-current
git remote -v
git fetch origin
```

เมื่อ working tree สะอาดและต้องการตั้งฐานจาก main ให้ `git switch main` แล้ว `git pull --ff-only origin main` จากนั้นสร้าง feature branch ถ้ามี local changes ให้ commit งานที่ตั้งใจเก็บหรือสำรองแยกก่อน ห้าม agent stash/delete งานโดยไม่บันทึก local branch ที่ diverged ต้องวิเคราะห์ก่อน merge

คัดลอกชุดแผนนี้ไว้ `docs/final-project-plan/` และเปิด fo จาก root ResultScope อ่าน AGENTS ของ repo และ parent ที่มีผลจริง ห้ามเขียนทับ `.codex`, `.agent`, global skills หรือ configuration ของ project อื่น การตั้งค่า fo ที่มีอยู่ใช้ต่อได้ ไม่สร้างคำสั่ง CLI fo ที่ยังไม่ทราบ syntax

## Environment isolation

P0 ตรวจ Python ที่ installed แล้วใช้รุ่นที่ dependencies รองรับจริง สร้าง venv เฉพาะโครงการ ไม่แก้ global Python/Node environment:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8011
```

ตรวจ port 8011 ว่างก่อนใช้ อย่าปิด service อื่นเพื่อแย่ง port ตั้ง API key ผ่าน `.env` local เท่านั้น คำสั่งเป็นขั้นตอน baseline ตาม repo ไม่รับประกัน package resolution ก่อนรัน หาก requirements ใช้รุ่นที่หาไม่ได้ให้ MAIN ตรวจ registry และแก้แบบมีเหตุผล ไม่อ้างว่าติดตั้งผ่าน

## บทบาท agents

| บทบาท | ความรับผิดชอบ | ขอบเขตเขียน |
|---|---|---|
| MAIN | contracts, task split, integration, decisions, acceptance | integration branch; shared config/router หลัง review |
| IMPLEMENT_BACKEND | retrieval, image services, persistence | service module/test ที่มอบหมาย |
| IMPLEMENT_UI | templates/CSS/JS, interaction/accessibility | frontend files และ browser tests |
| REVIEW | source review, adversarial tests, evidence audit | review report; regression tests ใน branch แยก |

2 implementers + 1 reviewer มักพอสำหรับขนาดนี้ เพิ่ม agent เมื่อมีงานอิสระจริงเท่านั้น ห้ามเชื่อว่า fo development agents ต้องกลายเป็น agents ใน runtime ของ chatbot

## Worktrees และ integration

MAIN สร้าง worktree จาก integration HEAD เดียวกัน ตั้งชื่อไม่ซ้ำ:

```powershell
git worktree add ..\ResultScope-backend -b work/p2-backend
git worktree add ..\ResultScope-ui -b work/p5-ui
```

ติดตั้ง venv แยกเมื่อจำเป็น ไม่แชร์ SQLite file หรือพอร์ตระหว่าง tests กำหนด file ownership ใน task brief ก่อนเริ่ม คนแก้ router/config/requirements มีได้หนึ่งรายในช่วงเดียวกัน IMPLEMENT commit เฉพาะงานตน; MAIN ตรวจ diff แล้ว merge หรือ cherry-pick ตามประวัติจริง ไม่ใช้ทั้งสองแบบซ้ำ commit เดียวกัน ทดสอบ integrated HEAD หลังรวม

REVIEW ไม่รับงานตัวเอง ถ้ามีเพียง agent เดียวให้ทำ review pass แยกและบอกข้อจำกัด ไม่อ้างว่ามี independent reviewer

## Task brief มาตรฐาน

ทุกงานระบุ ID เช่น P2-F03, goal, inputs/source version, files allowed, forbidden scope, dependency, exact acceptance cases, commands, expected artifacts, report location ผู้รับงานตอบ changes/commit/tests/limitations ห้ามส่งเพียง “done”

## State machine

PLANNED → IN_PROGRESS → READY_FOR_REVIEW → VERIFIED → INTEGRATED งานที่ล้มเหลวกลับ IN_PROGRESS; รอ owner/credential ใช้ BLOCKED พร้อม unblock condition; NOT_RUN เป็นสถานะผลทดสอบ ไม่ใช่ PASS

เมื่อ phase ผ่านให้ MAIN เขียน `docs/progress/PHASE_N_REPORT.md` ตาม template สรุป commit/evidence/gate และเริ่ม phase ถัดไปได้ ไม่ถามอนุมัติรายไฟล์ งานเผยแพร่ภายนอก/เพิ่มค่าใช้จ่าย/ข้อมูลจริงให้แยก approval ตามขอบเขตที่ owner อนุมัติจริง

## งานเรียนและการใช้ AI

ใช้ agents ช่วยพัฒนา ทดสอบ อธิบายโค้ดได้ แต่โจทย์ที่แนบไม่ได้ระบุนโยบายการใช้ AI จึงห้ามอ้างว่าอาจารย์อนุมัติแล้ว เก็บ AI assistance log ตามนโยบายรายวิชา ผู้ส่งต้องอ่านและอธิบายทุกส่วนได้ ถ้าทำคู่ ให้บันทึกงานของมนุษย์สองคน ไม่เอาชื่อ agents ไปแทนสมาชิกกลุ่ม
