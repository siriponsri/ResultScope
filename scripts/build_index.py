from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.knowledge import knowledge_base_to_dict, load_knowledge_base


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a versioned local knowledge index.")
    parser.add_argument("--mode", choices=("release", "synthetic"), required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        base = load_knowledge_base(ROOT, mode=args.mode, environment=os.getenv("APP_ENV", "development"))
    except Exception as exc:
        print(f"INDEX BUILD: BLOCKED ({getattr(exc, 'code', 'knowledge_unavailable')})")
        return 1
    output = args.output or ROOT / "data" / "indexes" / f"{base.mode}-{base.corpus_version}.json"
    resolved_output = output.resolve()
    allowed_root = (ROOT / "data" / "indexes").resolve()
    try:
        resolved_output.relative_to(allowed_root)
    except ValueError:
        parser.error("--output must remain under data/indexes")
    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    resolved_output.write_text(
        json.dumps(knowledge_base_to_dict(base), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"INDEX BUILD: PASS mode={base.mode} demo={str(base.demo).lower()} records={len(base.records)}")
    print(f"CORPUS VERSION: {base.corpus_version}")
    print(f"OUTPUT: {resolved_output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
