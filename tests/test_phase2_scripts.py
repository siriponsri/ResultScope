import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def test_build_index_script_runs_from_repository_root():
    result = subprocess.run(
        [PYTHON, "scripts/build_index.py", "--mode", "synthetic"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "INDEX BUILD: PASS mode=synthetic demo=true" in result.stdout


def test_release_build_script_fails_closed_from_repository_root():
    result = subprocess.run(
        [PYTHON, "scripts/build_index.py", "--mode", "release"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "INDEX BUILD: BLOCKED (release_not_ready)" in result.stdout


def test_retrieval_evidence_script_runs_from_repository_root():
    output = ROOT / "docs" / "progress" / "evidence" / "phase2-script-test-retrieval.json"
    try:
        result = subprocess.run(
            [PYTHON, "scripts/evaluate_retrieval.py", "--mode", "synthetic", "--output", str(output)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, result.stderr
        assert "RETRIEVAL EVALUATION: PASS (5/5)" in result.stdout
        assert '"live_provider_or_embedding_call": false' in output.read_text(encoding="utf-8")
    finally:
        output.unlink(missing_ok=True)
