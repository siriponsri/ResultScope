# หลักฐานการตรวจสอบหน้า Admin Settings และภาษาเว็บแอป

วันที่: 3 ตุลาคม 2569  
สภาพแวดล้อม: FastAPI local server, Playwright, synthetic password และ synthetic provider key สำหรับการทดสอบเท่านั้น

## ผลการตรวจ

| กรณี | ผล | หลักฐาน |
|---|---|---|
| เปิด `/admin/settings` โดยยังไม่ login | PASS; เปลี่ยนเส้นทางไป `/admin/login` | Playwright navigation |
| Login local demo | PASS | Playwright snapshot |
| Settings desktop | PASS; แสดง provider cards 3 รายการ | `desktop-settings-en.png`, `desktop-settings-en.yml` |
| Settings mobile 390px | PASS; `scrollWidth=390` และไม่มี overflow | `mobile-settings-en.png`, `mobile-settings-en.yml` |
| หน้า home desktop | PASS; `lang=en` และไม่มีอักษรไทยใน UI | `desktop-home-en.png` |
| หน้า home mobile 390px | PASS; ไม่มี horizontal overflow | `mobile-home-en.png`, `mobile-home-en.yml` |
| Save settings | PASS; แสดง `Saved — no provider was called.` | Playwright evaluation และ network log |
| Mock provider test | PASS; แสดง `Mocked test used no provider request.` | `mobile-network-after-mock.txt` |
| Secret non-disclosure | PASS; key ไม่ปรากฏใน body และช่อง password ว่างหลัง reload | Playwright evaluation |
| Logout | PASS; กลับไป `/admin/login` | Playwright navigation |

การตรวจนี้ไม่ใช่ live provider verification และไม่ยืนยัน production readiness
