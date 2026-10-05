from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]


def _run_entrypoint(**updates: str | None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.pop("VERCEL", None)
    env.pop("SESSION_SIGNING_KEY", None)
    env.update({key: value for key, value in updates.items() if value is not None})
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-c", "import api.index; print('entrypoint-ok')"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_entrypoint_exports_the_existing_fastapi_application(monkeypatch):
    monkeypatch.delenv("VERCEL", raising=False)
    from api.index import app as vercel_app
    from main import app as main_app

    assert vercel_app is main_app
    assert vercel_app.title == "ResultScope Laboratory Assistant"


def test_vercel_config_keeps_fastapi_static_mount_in_the_function():
    config = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))

    assert config["functions"]["api/index.py"]["maxDuration"] == 60
    assert config["rewrites"] == [
        {"source": "/api/:path*", "destination": "/api/index.py"},
        {"source": "/static/:path*", "destination": "/api/index.py"},
        {"source": "/health", "destination": "/api/index.py"},
        {"source": "/", "destination": "/api/index.py"},
    ]
    assert config["env"] == {
        "APP_ENV": "preview",
        "KNOWLEDGE_MODE": "synthetic",
        "LOCAL_DEMO_MODE": "false",
        "PROVIDER_NETWORK_ENABLED": "false",
        "STORAGE_BACKEND": "auto",
    }
    # Static files are served by main.py's FastAPI mount, so they must not be
    # excluded from the Python function bundle.
    assert "excludeFiles" not in config["functions"]["api/index.py"]


def test_vercel_preview_import_uses_synthetic_offline_defaults():
    result = _run_entrypoint(
        VERCEL="1",
        SESSION_SIGNING_KEY="synthetic-session-signing-key",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "entrypoint-ok"


def test_vercel_requires_a_server_side_session_secret():
    result = _run_entrypoint(VERCEL="1")

    assert result.returncode != 0
    assert "SESSION_SIGNING_KEY" in result.stderr
    assert "synthetic-session-signing-key" not in result.stderr


@pytest.mark.parametrize(
    ("setting", "value", "message"),
    [
        ("STORAGE_BACKEND", "sqlite", "STORAGE_BACKEND=sqlite"),
        ("PROVIDER_NETWORK_ENABLED", "true", "Provider network access is disabled"),
    ],
)
def test_vercel_rejects_local_filesystem_or_network_modes(setting, value, message):
    result = _run_entrypoint(
        VERCEL="1",
        SESSION_SIGNING_KEY="synthetic-session-signing-key",
        **{setting: value},
    )

    assert result.returncode != 0
    assert message in result.stderr


def test_admin_routes_remain_disabled_by_the_existing_vercel_guard(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("SESSION_SIGNING_KEY", "synthetic-session-signing-key")
    monkeypatch.setattr("config.settings.LOCAL_DEMO_MODE", True)
    monkeypatch.setattr("config.settings.APP_ENV", "development")

    from api.index import app

    client = TestClient(app)
    assert client.get("/admin/login").status_code == 404
    assert client.get("/admin/settings").status_code == 404
    assert client.get("/api/v1/admin/config").status_code == 404
    assert client.post("/api/v1/admin/login", json={"username": "admin", "password": "1234"}).status_code == 404


def test_entrypoint_serves_application_and_static_routes_locally(monkeypatch):
    monkeypatch.delenv("VERCEL", raising=False)
    from api.index import app

    client = TestClient(app)
    assert client.get("/").status_code == 200
    assert client.get("/health").status_code == 200
    assert client.get("/static/docs/user-guide.html").status_code == 200
