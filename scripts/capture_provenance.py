from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Sequence

SCHEMA_VERSION = "resultscope-capture-provenance-v1"
HASH_ALGORITHM = "sha256"
AGGREGATE_FORMAT = "path-nul-bytes-nul-v1"

# These are generated or owner-supplied artifacts, not application source inputs.
ROOT_ATTACHMENTS = frozenset(
    {
        "RESULTSCOPE_AUDIT_12ccb8a.md",
        "ResultScope_ Your lab results, explained-1.png",
        "Report canvas_ haemoglobin in context-2.png",
    }
)
GENERATED_DOC_PREFIXES = (
    "static/docs/",
    "docs/assets/screenshots/",
)
GENERATED_DOC_PATHS = frozenset(
    {
        "docs/assets/diagrams/architecture.png",
        "docs/assets/diagrams/message-flow.png",
        "docs/evidence/DOCUMENT_RENDER.json",
        "docs/evidence/PACKAGE_REHEARSAL.json",
        "docs/evidence/RUNTIME_FILE_HASHES.json",
    }
)
GENERATED_INDEX_PREFIX = "data/indexes/synthetic-"
BYTECODE_SUFFIXES = frozenset({".pyc", ".pyo", ".pyd"})


class ProvenanceError(RuntimeError):
    """Raised when a reproducible provenance record cannot be built."""


def _normalise_path(value: str | Path) -> str:
    return str(value).replace("\\", "/").lstrip("./")


def is_excluded_path(relative_path: str | Path) -> bool:
    """Return whether a tracked path is outside the source-manifest policy."""

    relative = _normalise_path(relative_path)
    name = relative.rsplit("/", 1)[-1]
    parts = set(relative.split("/"))
    if name in ROOT_ATTACHMENTS or "__pycache__" in parts:
        return True
    if Path(name).suffix.lower() in BYTECODE_SUFFIXES:
        return True
    if relative in GENERATED_DOC_PATHS:
        return True
    if relative.startswith(GENERATED_INDEX_PREFIX) and relative.casefold().endswith(".json"):
        return True
    return any(relative.startswith(prefix) for prefix in GENERATED_DOC_PREFIXES)


def _run_git(root: Path, args: Sequence[str], *, input_bytes: bytes | None = None) -> bytes:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            input=input_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", b"")
        if isinstance(detail, bytes):
            detail = detail.decode("utf-8", errors="replace")
        raise ProvenanceError(f"git command failed: {' '.join(args)}: {detail.strip()}") from exc
    return completed.stdout


def candidate_sha(root: Path, candidate_ref: str = "HEAD") -> str:
    return _run_git(root, ["rev-parse", candidate_ref]).decode("ascii").strip()


def _candidate_paths(root: Path, candidate_ref: str) -> list[str]:
    raw = _run_git(root, ["ls-tree", "-r", "--name-only", "-z", candidate_ref])
    paths = [item.decode("utf-8", errors="surrogateescape") for item in raw.split(b"\0") if item]
    return sorted(paths)


def _path_in_scope(relative: str, scopes: Sequence[str] | None) -> bool:
    if not scopes:
        return True
    normalised_scopes = [_normalise_path(scope).rstrip("/") for scope in scopes]
    return any(relative == scope or relative.startswith(scope + "/") for scope in normalised_scopes)


def _ignored_paths(root: Path, paths: Sequence[str]) -> set[str]:
    if not paths:
        return set()
    payload = b"\0".join(path.encode("utf-8", errors="surrogateescape") for path in paths) + b"\0"
    try:
        completed = subprocess.run(
            ["git", "check-ignore", "--no-index", "--stdin", "-z"],
            cwd=root,
            input=payload,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        raise ProvenanceError(f"cannot inspect Git ignore rules: {exc}") from exc
    if completed.returncode not in (0, 1):
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ProvenanceError(f"git ignore inspection failed: {detail}")
    return {
        item.decode("utf-8", errors="surrogateescape")
        for item in completed.stdout.split(b"\0")
        if item
    }


def _git_blob(root: Path, candidate_ref: str, relative: str) -> bytes:
    return _run_git(root, ["show", f"{candidate_ref}:{relative}"])


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _aggregate(records: Iterable[tuple[str, bytes]]) -> str:
    digest = hashlib.sha256()
    for relative, content in records:
        digest.update(relative.encode("utf-8", errors="surrogateescape"))
        digest.update(b"\0")
        digest.update(content)
        digest.update(b"\0")
    return digest.hexdigest()


def hash_output_files(root: Path, paths: Iterable[str | Path]) -> list[dict[str, str]]:
    """Hash generated capture outputs separately from the source fingerprint."""

    records: list[dict[str, str]] = []
    root = root.resolve()
    for value in paths:
        path = Path(value)
        if not path.is_absolute():
            path = root / path
        path = path.resolve()
        try:
            relative = path.relative_to(root).as_posix()
        except ValueError as exc:
            raise ProvenanceError(f"output path is outside repository: {path}") from exc
        if not path.is_file():
            raise ProvenanceError(f"output path is not a file: {relative}")
        records.append({"path": relative, "sha256": _sha256_file(path)})
    return sorted(records, key=lambda item: item["path"])


def build_manifest(
    root: Path,
    *,
    candidate_ref: str = "HEAD",
    scopes: Sequence[str] | None = None,
    output_paths: Iterable[str | Path] = (),
) -> dict:
    """Build a deterministic candidate manifest from Git blob bytes.

    The aggregate fingerprint is always based on the sorted candidate tree at
    ``candidate_ref``. Working-tree hashes are recorded only as diagnostics and
    never affect that aggregate, so ignored caches and local edits cannot make a
    candidate fingerprint appear reproducible when they are not.
    """

    root = root.resolve()
    ref_sha = candidate_sha(root, candidate_ref)
    paths = [
        relative
        for relative in _candidate_paths(root, candidate_ref)
        if _path_in_scope(relative, scopes) and not is_excluded_path(relative)
    ]
    ignored = _ignored_paths(root, paths)
    paths = [relative for relative in paths if relative not in ignored]

    records: list[dict] = []
    aggregate_inputs: list[tuple[str, bytes]] = []
    for relative in paths:
        content = _git_blob(root, candidate_ref, relative)
        candidate_hash = _sha256_bytes(content)
        working_path = root / Path(relative)
        working_hash = _sha256_file(working_path) if working_path.is_file() else None
        records.append(
            {
                "path": relative,
                "git_blob_sha256": candidate_hash,
                "working_tree_sha256": working_hash,
                "working_tree_matches_candidate": working_hash == candidate_hash,
            }
        )
        aggregate_inputs.append((relative, content))

    scope = [_normalise_path(scope).rstrip("/") for scope in scopes or ()]
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "candidate_sha": ref_sha,
        "candidate_ref": candidate_ref,
        "hash_algorithm": HASH_ALGORITHM,
        "aggregate_format": AGGREGATE_FORMAT,
        "content_policy": "git_blob_bytes_at_candidate_ref",
        "working_tree_policy": "diagnostic_sha256_only; excluded_from_aggregate",
        "tracked_file_policy": {
            "source": "git ls-tree -r --name-only -z candidate_ref",
            "sorted": True,
            "scopes": scope,
            "ignored_paths_excluded": True,
            "bytecode_excluded": True,
            "generated_docs_excluded": True,
            "root_attachments_excluded": True,
        },
        "source_fingerprint": _aggregate(aggregate_inputs),
        "files": records,
        "output_hashes": hash_output_files(root, output_paths),
    }
    return manifest


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a deterministic Git-tracked capture provenance manifest.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--candidate-ref", default="HEAD")
    parser.add_argument("--path", dest="scopes", action="append", help="Limit the manifest to a tracked path or directory.")
    parser.add_argument("--output-hash", dest="output_paths", action="append", default=[])
    parser.add_argument("--output", type=Path, help="Write JSON to this path instead of stdout.")
    args = parser.parse_args(argv)
    try:
        manifest = build_manifest(
            args.root,
            candidate_ref=args.candidate_ref,
            scopes=args.scopes,
            output_paths=args.output_paths,
        )
    except ProvenanceError as exc:
        print(f"CAPTURE PROVENANCE: BLOCKED ({exc})", file=sys.stderr)
        return 1

    rendered = json.dumps(manifest, ensure_ascii=True, indent=2) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else args.root / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
