"""Run the coursework demo cases without treating expected answers as index data."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services import answer_service
from services.answer_service import answer_query
from services.intent_router import route_intent
from services.knowledge import load_knowledge_base
from services.retrieval import retrieve


DEMO_QUESTIONS = ROOT / "docs" / "coursework-demo" / "ResultScope_Coursework_Demo_v1" / "evaluation" / "questions.jsonl"


async def _mock_chat(history: list[dict[str, str]], prompt: str, rule_grounding: str) -> str:
    if "SVC-001" in prompt and "SVC-003" in prompt:
        return "CBC 250 THB และ HbA1c 350 THB ต่างกัน 100 บาท"
    if "SVC-001" in prompt and "SVC-002" in prompt:
        return "CBC 250 THB และ FPG 120 THB รวม 370 บาท"
    if "HbA1c" in prompt and "350" in prompt:
        return "HbA1c ราคา 350 THB"
    return "คำตอบนี้อ้างอิงเฉพาะข้อมูลธุรกิจสมมติที่ค้นพบใน corpus"


def _load_cases() -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in DEMO_QUESTIONS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _retrieval_query(case: dict[str, Any], question: str) -> str:
    prior = case.get("messages", [])[:-1]
    return " ".join(
        [item.get("content", "") for item in prior if isinstance(item, dict) and isinstance(item.get("content"), str)]
        + [question]
    ).strip()


def _run_case(case: dict[str, Any], base: Any) -> dict[str, Any]:
    messages = case.get("messages")
    if not isinstance(messages, list) or not messages:
        raise ValueError(f"{case.get('case_id')} has no messages")
    history = messages[:-1]
    question = messages[-1].get("content")
    if not isinstance(question, str) or not question.strip():
        raise ValueError(f"{case.get('case_id')} has no final question")
    intent = route_intent(question, history)
    retrieval = retrieve(_retrieval_query(case, question), base)
    result = asyncio.run(answer_query(question, intent, history, None, base=base))
    expected_sources = set(case.get("expected_source_ids", []))
    retrieved_sources = {source_id for item in retrieval.items for source_id in item.record.source_ids}
    cited_sources = {citation.source_id for citation in result.citations}
    source_pass = expected_sources.issubset(retrieved_sources | cited_sources)
    status_pass = case.get("expected_status") is None or result.status == case["expected_status"]
    if case.get("case_id") == "Q09":
        roles = [item.get("role") for item in history]
        history_pass = len(history) >= 2 and roles[0] == "user" and roles[-1] == "assistant" and question not in {
            item.get("content") for item in history
        }
    else:
        history_pass = True
    return {
        "case_id": case.get("case_id"),
        "set": case.get("set"),
        "intent": intent.kind,
        "status": result.status,
        "expected_status": case.get("expected_status"),
        "retrieval_reason": retrieval.reason,
        "retrieved_source_ids": sorted(retrieved_sources),
        "citation_source_ids": sorted(cited_sources),
        "citations_count": len(result.citations),
        "passed": bool(source_pass and status_pass and history_pass and result.status != "error"),
        "history_contract_passed": history_pass,
        "evidence_class": "retrieval_only_plus_mocked_provider",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("mocked", "live"), default="mocked")
    parser.add_argument("--output", type=Path, default=ROOT / "docs" / "progress" / "evidence" / "coursework-demo-evaluation.json")
    args = parser.parse_args()
    if args.provider == "live":
        print("COURSEWORK DEMO EVALUATION: NOT_RUN (live provider evaluation is not authorized/configured)")
        return 2

    base = load_knowledge_base(ROOT, mode="synthetic", environment=os.getenv("APP_ENV", "development"))
    cases = _load_cases()
    mandatory = [case for case in cases if case.get("set") == "mandatory"]
    holdouts = [case for case in cases if case.get("set") == "holdout"]
    if len(mandatory) != 10 or len(holdouts) < 5:
        raise ValueError("coursework demo case counts are outside the declared contract")
    q09 = next(case for case in mandatory if case.get("case_id") == "Q09")
    if len(q09.get("messages", [])) < 3:
        raise ValueError("Q09 must contain prior messages and a separate follow-up")

    original_chat = answer_service.llm_client.chat
    answer_service.llm_client.chat = _mock_chat
    try:
        rows = [_run_case(case, base) for case in cases]
    finally:
        answer_service.llm_client.chat = original_chat

    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    mandatory_passed = sum(row["passed"] for row in rows if row["set"] == "mandatory")
    holdout_passed = sum(row["passed"] for row in rows if row["set"] == "holdout")
    report = {
        "schema_version": "coursework-demo-evidence-v1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "repository_revision": revision,
        "mode": base.mode,
        "data_class": "synthetic",
        "corpus_version": base.corpus_version,
        "provider_mode": "mocked",
        "live_provider_or_embedding_call": False,
        "mandatory_passed": mandatory_passed,
        "mandatory_total": len(mandatory),
        "holdout_passed": holdout_passed,
        "holdout_total": len(holdouts),
        "cases": rows,
        "release_readiness": "BLOCKED",
        "independent_review": "NOT_RUN",
    }
    output = args.output.resolve()
    output.relative_to((ROOT / "docs" / "progress" / "evidence").resolve())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    passed = all(row["passed"] for row in rows)
    print(f"COURSEWORK DEMO EVALUATION: {'PASS' if passed else 'FAIL'} ({mandatory_passed}/{len(mandatory)} mandatory, {holdout_passed}/{len(holdouts)} holdout)")
    print("EVIDENCE: retrieval-only plus mocked provider; live provider/embedding call=false")
    print(f"OUTPUT: {output.relative_to(ROOT)}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
