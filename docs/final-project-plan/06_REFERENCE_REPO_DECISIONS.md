# การเลือกใช้ repositories อ้างอิง

ตรวจวันที่ 1 ต.ค. 2569 จาก GitHub metadata/README และ source เฉพาะจุด ระดับการตรวจนี้ไม่ใช่ security audit หรือการทดลองติดตั้งทุกโครงการ URL ซ้ำของ chatbot-ui นับเป็นโครงการเดียว ข้อเลือกใช้เป็น engineering recommendation สำหรับ ResultScope ไม่ใช่ข้อกำหนดของผู้สอน

## ฐานที่ใช้จริง

[ResultScope](https://github.com/siriponsri/ResultScope/tree/78ae247d671d507cbf68225aa87a73621a7872e1) คงเป็นฐานเดียว ใช้ FastAPI และ frontend เดิม อ้างไฟล์ที่ตรวจใน 02 แทนการประกอบหลาย chatbot frameworks เป็นระบบใหม่

## Repo อาจารย์

| Repository | หลักฐานและแนวคิดที่ใช้ | การตัดสินใจ |
|---|---|---|
| [light-rag](https://github.com/chacharin/light-rag) | README มี config LLM/embedding สำหรับ OpenAI-compatible provider และ embedding dimension | ศึกษา configuration; ไม่ถือว่า README สั้นนี้ยืนยัน runtime/graph capability ทั้งระบบแล้ว |
| [mcp-lightrag](https://github.com/chacharin/mcp-lightrag) | README อธิบาย MCP bridge ไป LightRAG HTTP, auth/error handling, version compatibility | Phase 7 optional read-only retrieval adapter; อย่าเปิด ingest/delete tools ให้ customer chatbot |
| [chatbot-with-image-bill](https://github.com/chacharin/chatbot-with-image-bill) | README แบ่ง image upload, prompts, receipt parsing, normalization, CSV persistence | ใช้แนวคิด extract→normalize→validate; ไม่ยกการเก็บ CSV/uploads มา serverless โดยตรง |
| [LineOA-LLM-Chatbot](https://github.com/chacharin/LineOA-LLM-Chatbot/blob/main/api/index.py) | ไม่มี root README; อ่าน api/index.py พบ signature validation, webhook, reply/admin notification design | Phase 7 channel adapter; ไม่ยกการแจ้ง admin อัตโนมัติมาเปิดใช้โดยไม่กำหนดสิทธิ์/consent |
| [chatbot-it-kmitl](https://github.com/chacharin/chatbot-it-kmitl) | README FastAPI/OpenAI-compatible/Vercel; upstream ที่ ResultScope ระบุ | เก็บ attribution; ไม่คืน legacy api/index.py/vercel.json จากตัวอย่างเก่าโดยไม่มีเหตุ |
| [llama-guard-layer](https://github.com/chacharin/llama-guard-layer) | README แยก input/output check, blocklist+model, fail-closed | นำ pattern input/output/failure handling มาใช้; guard model เป็น optional adapter ไม่แทน groundedness/authorization |

ข้อสังเกตสำคัญ: source ที่ guard ระบุ safe หมายถึงผ่านหมวด policy ที่เปิดไว้ ไม่ได้พิสูจน์ว่าราคา/นโยบาย/หน่วย/ผลแล็บถูกต้อง ต้องมี business validation แยก

## Repo ผลิตภัณฑ์และ framework

| Repository | บทบาทตามข้อมูลที่ตรวจ | ใช้กับแผนนี้ |
|---|---|---|
| [chatbot-ui](https://github.com/mckaywrigley/chatbot-ui) | AI chat app; README setup มี Supabase | ศึกษา interaction เท่านั้น การย้าย stack เพิ่ม migration โดยไม่ช่วย rubric โดยตรง |
| [AionUi](https://github.com/iOfficeAI/AionUi/blob/main/readme.md) | Cowork app สำหรับ AI agents บนหลายแพลตฟอร์ม | reference workspace UX; ไม่ใช้เป็น customer lab app runtime |
| [AgentScope](https://github.com/agentscope-ai/agentscope) | Python agent framework/pipelines | defer runtime orchestration จนมี workflow ที่ต้องใช้; fo team ไม่ต้องติดตั้ง AgentScope |
| [llm-app](https://github.com/pathwaycom/llm-app) | templates สำหรับ live-data RAG/indexing | ศึกษา freshness/deletion propagation; เลื่อน live connectors หลัง corpus static ผ่าน |
| [Flowise](https://github.com/FlowiseAI/Flowise) | visual agent builder; metadata archived=true และ README แจ้ง archived วันที่ตรวจ | ไม่เลือกเป็น dependency ใหม่ของแผนนี้ |
| [Chatbox](https://github.com/chatboxai/chatbox) | desktop AI client community edition | ศึกษา attachment/chat UX; ไม่ fork เป็น web lab assistant |
| [AstrBot](https://github.com/AstrBotDevs/AstrBot) | IM/LLM/plugin agent framework | ศึกษา channel separation สำหรับ roadmap ไม่เพิ่ม plugin runtime ในสัปดาห์แรก |
| [FastChat](https://github.com/lm-sys/FastChat) | model training/serving/evaluation + OpenAI-compatible APIs | defer self-host/GPU; ใช้ provider abstraction เดิม |

## Design references

[no-slop-ui](https://github.com/LeoStehlik/no-slop-ui) README และ SKILL.md ให้แนวทางหน้าทำงานที่ชัดเจน ลด decorative gradients, cards และ fake metrics ใช้เป็น checklist ใน P5; [Anti-AI-UI](https://github.com/Vanszs/Anti-AI-UI) README อธิบาย filter/palette/research เป็นกรอบเรื่อง intent/brand/accessibility แปลงเป็นเกณฑ์ใน 05 ไม่ติดตั้งทุก skill หรือคัดลอกทุกข้อโดยไม่เทียบ product needs

## License preflight

ค่าต่อไปนี้เป็น metadata GitHub ที่พบ ไม่ใช่การตรวจสิทธิ์ทุกไฟล์/transitive dependency หรือคำรับรองการใช้เชิงพาณิชย์:

| กลุ่ม | Identifier ที่พบ |
|---|---|
| light-rag, mcp-lightrag, chatbot-ui, llm-app, no-slop-ui, Anti-AI-UI | MIT |
| AionUi, AgentScope, FastChat | Apache-2.0 |
| Chatbox | GPL-3.0 |
| AstrBot | AGPL-3.0 |
| Flowise | NOASSERTION |
| chatbot-it-kmitl, chatbot-with-image-bill, LineOA-LLM-Chatbot, llama-guard-layer | ไม่รายงาน license identifier |

ก่อนนำ code มาใช้ MAIN บันทึก repo/path/commit/ส่วนที่นำมา/LICENSE ที่อ่านจริง เก็บ notices และตรวจ dependency licenses แยกกัน Metadata ที่ไม่ระบุไม่ได้แปลว่าไม่มีสิทธิ์ใด ๆ หรืออนุญาตอัตโนมัติ ให้ unresolved จนอ่านเงื่อนไข/ได้คำตอบ สิทธิ์ส่วน commercial อยู่ใน release gate หลัง coursework
