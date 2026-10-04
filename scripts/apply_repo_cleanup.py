"""Archive-verified, explicit-path cleanup for the product refresh. Dry-run by default."""
from __future__ import annotations

import argparse
import hashlib
import json
import stat
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

PREFIXES = ('docs/final-project-plan/', 'docs/progress/', 'docs/business/', 'docs/architecture/', '.hallmark/')
EXACT = frozenset({
    'CODEX_PROMPT.md', 'CODEX_TERRA_GOAL.md', 'PATCH_MANIFEST.txt', 'PATCH_NOTES_TH.md',
    'ARCHITECTURE.md', 'DEPLOY_CHECKLIST.md', 'RELEASE_CHECKLIST.md',
    'docs/DESIGN_RESEARCH.md', 'docs/product/CAPABILITY_MATRIX.md',
    'static/js/scene.js', 'scripts/install-hallmark.ps1',
})
ARCHIVE = 'docs/archive/pre-redesign-c9236f5.zip'


class CleanupBlocked(ValueError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_target(root: Path, name: str) -> Path:
    rel = PurePosixPath(name)
    if (not isinstance(name, str) or '\\' in name or ':' in name or rel.is_absolute()
            or '..' in rel.parts or name != rel.as_posix()
            or not (name in EXACT or name.startswith(PREFIXES))):
        raise CleanupBlocked(f'Path is outside the explicit cleanup scope: {name}')
    target = root.joinpath(*rel.parts)
    current = target
    while current != root:
        if current.is_symlink() or (hasattr(current, 'is_junction') and current.is_junction()):
            raise CleanupBlocked(f'Symlink/junction is not allowed: {name}')
        current = current.parent
    try:
        target.resolve().relative_to(root)
    except ValueError as exc:
        raise CleanupBlocked(f'Path escapes repository: {name}') from exc
    return target


def matches(data: bytes, row: dict) -> bool:
    if digest(data) == row['sha256']:
        return True
    if row.get('lf_sha256'):
        try:
            data.decode('utf-8')
        except UnicodeDecodeError:
            return False
        return digest(data.replace(b'\r\n', b'\n')) == row['lf_sha256']
    return False


def plan(root: Path, manifest: dict) -> tuple[list[tuple[Path, bytes]], list[str]]:
    root = root.resolve()
    if manifest.get('schema_version') != 1 or manifest.get('archive') != ARCHIVE:
        raise CleanupBlocked('Unsupported cleanup manifest.')
    archive = root / ARCHIVE
    if archive.is_symlink() or not archive.is_file() or digest(archive.read_bytes()) != manifest['archive_sha256']:
        raise CleanupBlocked('Historical archive is missing or its SHA-256 does not match.')
    pending, missing, seen = [], [], set()
    with zipfile.ZipFile(archive) as z:
        for row in manifest['removals']:
            name = row['path']
            target = safe_target(root, name)
            if name in seen:
                raise CleanupBlocked(f'Duplicate cleanup path: {name}')
            seen.add(name)
            # Every deletion must already have its exact original bytes preserved.
            if digest(z.read(name)) != row['sha256']:
                raise CleanupBlocked(f'Archive does not preserve the expected original: {name}')
            if not target.exists():
                missing.append(name)
                continue
            if not stat.S_ISREG(target.stat().st_mode):
                raise CleanupBlocked(f'Not a regular file: {name}')
            data = target.read_bytes()
            if not matches(data, row):
                raise CleanupBlocked(f'Changed file; preserve and inspect before cleanup: {name}')
            pending.append((target, data))
    return pending, missing


def cleanup(root: Path, manifest: dict, apply: bool = False) -> dict:
    root = root.resolve()
    pending, missing = plan(root, manifest)
    result = {'mode': 'apply' if apply else 'dry_run', 'eligible': len(pending),
              'already_absent': len(missing), 'removed': 0, 'backup': None,
              'paths': [p.relative_to(root).as_posix() for p, _ in pending]}
    if not apply or not pending:
        return result
    # A unique sibling directory avoids overwriting any existing owner backup.
    backup_dir = Path(tempfile.mkdtemp(prefix=f'{root.name}-pre-refresh-backup-', dir=root.parent))
    backup = backup_dir / 'removed-files.zip'
    rows = []
    with zipfile.ZipFile(backup, 'x', zipfile.ZIP_DEFLATED) as z:
        for target, data in pending:
            name = target.relative_to(root).as_posix()
            z.writestr(name, data)
            rows.append({'path': name, 'sha256': digest(data), 'size': len(data)})
        z.writestr('BACKUP_MANIFEST.json', json.dumps({
            'created_utc': datetime.now(timezone.utc).isoformat(),
            'baseline_commit': manifest['baseline_commit'], 'files': rows,
        }, indent=2) + '\n')
    with zipfile.ZipFile(backup) as z:
        for row in rows:
            if digest(z.read(row['path'])) != row['sha256']:
                raise CleanupBlocked('Backup verification failed; no files have been removed.')
    # Recheck the full plan before the first unlink. Never run concurrently with editing.
    refreshed, _ = plan(root, manifest)
    if [(p, digest(d)) for p, d in refreshed] != [(p, digest(d)) for p, d in pending]:
        raise CleanupBlocked('Files changed during backup; no files have been removed.')
    for target, data in pending:
        if target.read_bytes() != data:
            raise CleanupBlocked(f'Concurrent edit detected. Stop and recover from {backup}')
        target.unlink()
        result['removed'] += 1
    result['backup'] = str(backup)
    # Keep directories and every unlisted item. No recursive directory deletion.
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Back up and remove only verified listed files.')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        manifest = json.loads((root / 'scripts/repo_cleanup_manifest.json').read_text(encoding='utf-8'))
        print(json.dumps(cleanup(root, manifest, args.apply), indent=2))
        return 0
    except (CleanupBlocked, OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print(f'CLEANUP BLOCKED: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
