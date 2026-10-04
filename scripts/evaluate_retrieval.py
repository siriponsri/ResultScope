from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.knowledge import load_knowledge_base
from services.retrieval import retrieve


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate retrieval against a separate synthetic dev set.")
    parser.add_argument("--mode", choices=("release", "synthetic"), required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs" / "evidence" / "runs" / "phase2-retrieval-run.json",
    )
    args = parser.parse_args()
    if args.mode == "release":
        print("RETRIEVAL EVALUATION: BLOCKED (live/release evaluation requires approved data)")
        return 2
    try:
        base = load_knowledge_base(ROOT, mode="synthetic", environment=os.getenv("APP_ENV", "development"))
    except Exception as exc:
        print(f"RETRIEVAL EVALUATION: BLOCKED ({getattr(exc, 'code', 'knowledge_unavailable')})")
        return 2

    cases_path = ROOT / "evaluation" / "retrieval_cases.jsonl"
    cases = [json.loads(line) for line in cases_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = []
    for case in cases:
        result = retrieve(case["query"], base, top_k=4)
        actual_ids = [item.record.data.get("service_id") for item in result.items]
        expected_ids = case["expected_record_ids"]
        rows.append(
            {
                "case_id": case["case_id"],
                "query": case["query"],
                "expected_record_ids": expected_ids,
                "actual_record_ids": actual_ids,
                "top_k": 4,
                "source_ids": sorted({source for item in result.items for source in item.record.source_ids}),
                "reason": result.reason,
                "latency_ms": result.latency_ms,
                "passed": actual_ids[: len(expected_ids)] == expected_ids if expected_ids else not actual_ids,
            }
        )
    passed = sum(row["passed"] for row in rows)
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    report = {
        "schema_version": "retrieval-evidence-v1",
        "run_id": "phase2-dev-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "repository_revision": revision,
        "mode": base.mode,
        "demo": base.demo,
        "retrieval_method": "lexical-char-ngram-v1",
        "corpus_version": base.corpus_version,
        "corpus_source_ids": sorted(base.sources),
        "live_provider_or_embedding_call": False,
        "cases_passed": passed,
        "cases_total": len(rows),
        "cases": rows,
    }
    output = args.output.resolve()
    try:
        output.relative_to((ROOT / "docs" / "evidence" / "runs").resolve())
    except ValueError:
        parser.error("--output must remain under docs/evidence/runs")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"RETRIEVAL EVALUATION: {'PASS' if passed == len(rows) else 'FAIL'} ({passed}/{len(rows)})")
    print(f"REVISION: {revision}")
    print(f"METHOD: {report['retrieval_method']} (synthetic development data; no live embedding/provider call)")
    print(f"EVIDENCE: {output.relative_to(ROOT)}")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
