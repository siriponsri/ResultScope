from __future__ import annotations

import json
import os
import subprocess
import sys

from services import provider_adapters

def test_verification_runner_is_mock_only_by_default_and_never_prints_key():
    environment = os.environ.copy()
    environment.update(
        {
            "PROVIDER_NETWORK_ENABLED": "false",
            "PROVIDER_BUDGET_CYCLE_ID": "",
            "LLM_API_KEY": "",
            "VISION_API_KEY": "",
            "VISION_ENABLED": "false",
        }
    )
    completed = subprocess.run(
        [sys.executable, "scripts/provider_verification_runner.py"],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    )
    payload = json.loads(completed.stdout)
    assert payload["live_requested"] is False
    assert {row["status"] for row in payload["results"]} == {"mocked"}
    assert all(row["network_called"] is False for row in payload["results"])
    assert all(row["quota_used"] is False for row in payload["results"])
    assert "api_key" not in completed.stdout.lower()
    assert "authorization" not in completed.stdout.lower()


def test_explicit_live_runner_stops_at_disabled_network_guard(tmp_path):
    environment = os.environ.copy()
    environment.update(
        {
            "PROVIDER_NETWORK_ENABLED": "false",
            "PROVIDER_BUDGET_CYCLE_ID": "offline-test-cycle",
            "PROVIDER_BUDGET_PATH": str(tmp_path / "runner.sqlite3"),
            "LLM_API_KEY": "synthetic-test-token",
            "LLM_BASE_URL": "http://127.0.0.1:9/v1",
        }
    )
    completed = subprocess.run(
        [sys.executable, "scripts/provider_verification_runner.py", "--live", "--slot", "llm"],
        capture_output=True,
        text=True,
        env=environment,
    )
    payload = json.loads(completed.stdout)
    assert completed.returncode == 1
    assert payload["live_requested"] is True
    assert payload["results"] == [
        {
            "slot": "llm",
            "status": "error",
            "error_code": "provider_network_disabled",
            "network_called": False,
            "quota_used": False,
        }
    ]


def test_runner_error_projection_preserves_consumed_attempt_facts():
    attempt = provider_adapters.AttemptReceipt("attempt", "cycle", "llm", "runner", "failed", "provider_unavailable")
    error = provider_adapters.ProviderAdapterError(
        "provider_unavailable",
        "safe provider failure",
        provider_attempt=attempt,
    )
    from scripts.provider_verification_runner import _error_result

    assert _error_result("llm", error) == {
        "slot": "llm",
        "status": "error",
        "error_code": "provider_unavailable",
        "network_called": True,
        "quota_used": True,
    }
