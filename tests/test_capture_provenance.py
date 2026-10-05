from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from scripts.capture_provenance import (
    AGGREGATE_FORMAT,
    SCHEMA_VERSION,
    build_manifest,
    hash_output_files,
    is_excluded_path,
)

ROOT = Path(__file__).resolve().parents[1]


def _git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _fixture_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "--quiet")
    _git(root, "config", "user.name", "ResultScope test")
    _git(root, "config", "user.email", "test@example.invalid")
    (root / "README.md").write_text("tracked source\n", encoding="utf-8")
    (root / "knowledge").mkdir()
    (root / "knowledge" / "source.txt").write_bytes(b"synthetic source bytes\n")
    (root / "static" / "docs").mkdir(parents=True)
    (root / "static" / "docs" / "user-guide.html").write_text("generated guide\n", encoding="utf-8")
    (root / "docs" / "assets" / "screenshots").mkdir(parents=True)
    (root / "docs" / "assets" / "screenshots" / "capture.png").write_bytes(b"capture")
    (root / "__pycache__").mkdir()
    (root / "__pycache__" / "module.pyc").write_bytes(b"bytecode")
    (root / "data" / "indexes").mkdir(parents=True)
    (root / "data" / "indexes" / "synthetic-future-v2.json").write_text("{}\n", encoding="utf-8")
    (root / "RESULTSCOPE_AUDIT_12ccb8a.md").write_text("attachment\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "add", "-f", "__pycache__/module.pyc", "static/docs/user-guide.html", "docs/assets/screenshots/capture.png", "RESULTSCOPE_AUDIT_12ccb8a.md")
    _git(root, "commit", "--quiet", "-m", "fixture")
    return root


def test_manifest_is_deterministic_and_records_candidate_blob_hashes(tmp_path: Path):
    root = _fixture_repo(tmp_path)

    first = build_manifest(root)
    second = build_manifest(root)

    assert first == second
    assert first["schema_version"] == SCHEMA_VERSION
    assert first["aggregate_format"] == AGGREGATE_FORMAT
    assert first["files"] == sorted(first["files"], key=lambda item: item["path"])
    assert first["source_fingerprint"]
    assert all(item["git_blob_sha256"] for item in first["files"])


def test_manifest_excludes_generated_docs_bytecode_ignored_files_and_attachments(tmp_path: Path):
    root = _fixture_repo(tmp_path)
    manifest = build_manifest(root)
    paths = {item["path"] for item in manifest["files"]}

    assert paths == {"README.md", "knowledge/source.txt"}
    assert "data/indexes/synthetic-future-v2.json" not in paths
    assert is_excluded_path("static/docs/user-guide.html")
    assert is_excluded_path("docs/assets/screenshots/capture.png")
    assert is_excluded_path("__pycache__/module.pyc")
    assert is_excluded_path("RESULTSCOPE_AUDIT_12ccb8a.md")


def test_candidate_fingerprint_ignores_working_tree_edits_but_records_them(tmp_path: Path):
    root = _fixture_repo(tmp_path)
    before = build_manifest(root)
    (root / "knowledge" / "source.txt").write_bytes(b"local edit, not candidate bytes\n")
    (root / "ignored-cache.txt").write_text("ignored\n", encoding="utf-8")
    _git(root, "config", "core.excludesfile", str(root / ".gitignore-local"))
    (root / ".gitignore-local").write_text("ignored-cache.txt\n", encoding="utf-8")

    after = build_manifest(root)

    assert after["candidate_sha"] == before["candidate_sha"]
    assert after["source_fingerprint"] == before["source_fingerprint"]
    edited = next(item for item in after["files"] if item["path"] == "knowledge/source.txt")
    assert edited["working_tree_matches_candidate"] is False
    assert edited["working_tree_sha256"] != edited["git_blob_sha256"]


def test_output_hashes_are_separate_and_sorted(tmp_path: Path):
    root = _fixture_repo(tmp_path)
    first = root / "capture-b.png"
    second = root / "capture-a.png"
    first.write_bytes(b"b")
    second.write_bytes(b"a")

    hashes = hash_output_files(root, [first, second])
    manifest = build_manifest(root, output_paths=[first, second])

    assert [item["path"] for item in hashes] == ["capture-a.png", "capture-b.png"]
    assert manifest["output_hashes"] == hashes
    assert all(set(item) == {"path", "sha256"} for item in hashes)


def test_cli_writes_json_without_timestamp_or_working_tree_path(tmp_path: Path):
    root = _fixture_repo(tmp_path)
    output = tmp_path / "provenance.json"
    result = subprocess.run(
        [os.fspath(Path(os.sys.executable)), "scripts/capture_provenance.py", "--root", os.fspath(root), "--output", os.fspath(output)],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert result.stdout == ""
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert "generated_at" not in payload
    assert all("\\" not in item["path"] for item in payload["files"])
