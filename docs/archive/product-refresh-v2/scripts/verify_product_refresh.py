"""Verify copied product-refresh bytes without changing files or making network calls."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--integrated', action='store_true', help='Also require listed legacy files to be absent.')
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        manifest = json.loads((root / 'scripts/product_refresh_manifest.json').read_text(encoding='utf-8'))
        if manifest['schema_version'] != 1:
            raise ValueError('Unsupported package manifest')
        failures = []
        for row in manifest['files']:
            name = row['path']; rel = PurePosixPath(name)
            if rel.is_absolute() or '..' in rel.parts or '\\' in name or ':' in name:
                raise ValueError('Invalid payload path')
            file = root.joinpath(*rel.parts)
            if not file.resolve().is_relative_to(root) or not file.is_file() or file.is_symlink():
                failures.append(name + ': missing or invalid path')
                continue
            data = file.read_bytes()
            if sha(data) != row['sha256']:
                # Only ordinary non-pinned text may be checked out with CRLF.
                normalized = row.get('lf_sha256')
                if not normalized or sha(data.replace(b'\r\n', b'\n')) != normalized:
                    failures.append(name + ': content differs from supplied package')
        if args.integrated:
            cleanup = json.loads((root / 'scripts/repo_cleanup_manifest.json').read_text(encoding='utf-8'))
            failures += [x['path'] + ': legacy file still present' for x in cleanup['removals'] if (root / x['path']).exists()]
        ancestry = subprocess.run(['git', 'merge-base', '--is-ancestor', manifest['baseline_commit'], 'HEAD'],
                                  cwd=root, capture_output=True)
        if ancestry.returncode:
            failures.append('Repository HEAD does not contain the required baseline commit')
        print(json.dumps({'status': 'BLOCKED' if failures else 'PASS', 'payload_files': len(manifest['files']),
                          'baseline_commit': manifest['baseline_commit'], 'integrated': args.integrated,
                          'failures': failures}, indent=2))
        return 2 if failures else 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'PACKAGE VERIFICATION BLOCKED: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
