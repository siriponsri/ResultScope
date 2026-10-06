"""Offline harness for the design-approval screenshot bundle ONLY. Never deploy.

MOCKED_TEST_ONLY. Builds on tests/browser/fixture_server.py (same real routes, storage,
permissions and state machines) and replaces its one-line doubles with scripted replies
that have the same shape as real answers (inline [source-id] markers, sources, verified
report observations, page shortcuts, the verification receipt). The text is written by
hand to show layout. It is not model output and never evidence of answer quality.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fixture_server as fx  # noqa: E402  (applies the fixture patches and staff users)

b = fx.b
_base_agent = fx.agent

SOURCES = {
    "rs-p01": {"id": "rs-p01", "title": "Essential Check", "url": "/packages/P01", "publisher": "ResultScope demo", "data_class": "synthetic_business"},
    "rs-p02": {"id": "rs-p02", "title": "Workday Check", "url": "/packages/P02", "publisher": "ResultScope demo", "data_class": "synthetic_business"},
    "nlm-lipids": {"id": "nlm-lipids", "title": "Cholesterol levels", "url": "https://medlineplus.gov/lab-tests/cholesterol-levels/", "publisher": "MedlinePlus", "data_class": "public_education"},
    "nlm-reading-results": {"id": "nlm-reading-results", "title": "How to understand your lab results", "url": "https://medlineplus.gov/lab-tests/how-to-understand-your-lab-results/", "publisher": "MedlinePlus", "data_class": "public_education"},
    "siriraj-glucose-glucose-07": {"id": "siriraj-glucose-glucose-07", "title": "Siriraj Hospital: Glucose", "url": "https://www.si.mahidol.ac.th/th/manual/Project/pdf/glucose.pdf", "publisher": "Siriraj Hospital", "data_class": "public_reference"},
}
ADVISOR = {"id": "advisor", "name": "Health-check Advisor"}
EXPLAINER = {"id": "explainer", "name": "Report Explainer"}


def checks(n_sources: int, n_obs: int = 0) -> dict:
    return {"input_safety": "passed", "citations_validated": n_sources, "independent_review": "passed", "output_safety": "passed", "observations": n_obs}


def answer(reply, dot, sources=(), ui=(), followups=(), observations=(), action=None):
    src = [SOURCES[s] for s in sources]
    return {"reply": reply, "sources": src, "action": action, "dot": dot, "ui": list(ui), "followups": list(followups),
            "observations": list(observations), "checks": checks(len(src), len(observations))}


async def agent(message, context):
    text = message.lower()
    report = context.get("report") or {}
    fields = {f["name"].lower(): f for f in report.get("fields", [])}
    if "1,500" in text or "1500" in text:
        return answer(
            "Two packages sit near that budget. **Essential Check** is ฿1,190 and covers a blood count, fasting glucose, "
            "kidney function and urinalysis [rs-p01]. **Workday Check** is ฿1,690, about ฿190 over, and adds a lipid profile "
            "and the liver enzyme ALT [rs-p02].\n\nIf cholesterol is one of the things you want to know, the Workday Check is the "
            "one that measures it. Both can be booked directly; our team confirms the time before any payment.",
            ADVISOR, ["rs-p01", "rs-p02"],
            ui=[{"type": "open_compare", "args": {"package_ids": ["P01", "P02"]}},
                {"type": "prefill_booking", "args": {"package_id": "P01", "name": "Essential Check", "branch_id": "BKK01"}}],
            followups=["What does a lipid profile measure?", "Do I need to fast before the Workday Check?"])
    if "lipid profile" in text:
        return answer(
            "A lipid profile measures fats carried in your blood: total cholesterol, LDL cholesterol, HDL cholesterol and "
            "triglycerides [nlm-lipids]. LDL is the part most linked to build-up in blood vessels, while HDL helps carry "
            "cholesterol away [nlm-lipids].\n\nWhat counts as a healthy level depends on your age and other risk factors, so the "
            "laboratory range and your clinician's advice matter more than a single number [nlm-reading-results].",
            EXPLAINER, ["nlm-lipids", "nlm-reading-results"], followups=["How often should lipids be checked?"])
    if report and ("น้ำตาล" in message or "ldl" in text or "glucose" in text):
        obs = [{k: fields[n][k] for k in ("value", "unit", "reference", "status")} | {"field_id": fields[n]["id"], "name": fields[n]["name"]}
               for n in ("glucose", "ldl cholesterol") if n in fields]
        return answer(
            "จากรายงานที่คุณยืนยันแล้ว มีสองค่าที่อยู่นอกช่วงที่พิมพ์ไว้ในรายงานของคุณเอง\n\n"
            "1. **น้ำตาลในเลือดขณะอดอาหาร 101 mg/dL** สูงกว่าช่วง 70–99 เล็กน้อย ค่าเดียวยังไม่ใช่การวินิจฉัย "
            "แพทย์มักดูร่วมกับการตรวจซ้ำหรือ HbA1c [nlm-reading-results] [siriraj-glucose-glucose-07]\n"
            "2. **LDL cholesterol 162 mg/dL** สูงกว่าเกณฑ์ที่รายงานพิมพ์ไว้ (< 130) LDL เป็นไขมันส่วนที่สัมพันธ์กับการสะสมในหลอดเลือด [nlm-lipids]\n\n"
            "ค่าอื่น ๆ ในรายงานอยู่ในช่วงที่พิมพ์ไว้ หากต้องการคำแนะนำเฉพาะตัว ควรคุยกับแพทย์หรือเภสัชกรที่ดูแลคุณ",
            EXPLAINER, ["nlm-reading-results", "siriraj-glucose-glucose-07", "nlm-lipids"], observations=obs,
            followups=["HbA1c ต่างจากน้ำตาลขณะอดอาหารอย่างไร"])
    if "book" in text and "essential" in text:
        return answer("Here is the request. It holds the slot until our team confirms it; nothing is charged before that.",
                      ADVISOR, [], action={"type": "book", "quote": fx.db.quote(["P01"]), "branch_id": "BKK01", "date": fx._next_open_day(5), "time": "09:30"})
    return await _base_agent(message, context)


async def read(raw):
    rows = [("Glucose", "101", "mg/dL", "70–99", "H"), ("HbA1c", "5.4", "%", "4.0–5.6", ""), ("Total cholesterol", "228", "mg/dL", "< 200", "H"),
            ("LDL cholesterol", "162", "mg/dL", "< 130", "H"), ("HDL cholesterol", "52", "mg/dL", "> 40", ""), ("Triglycerides", "140", "mg/dL", "< 150", "")]
    return {"fields": fx.normalize([fx.ReportField(name=n, value=v, unit=u, reference=r, printed_flag=f) for n, v, u, r, f in rows]),
            "warnings": ["Offline test double: these values are scripted, not read by OCR."], "confirmed": False}


b.business_agent.run = agent
b.read_report = read

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fx.app, host="127.0.0.1", port=int(os.getenv("UI_TEST_PORT", "8098")), log_level="error")
