"""Build an atomic full-source replacement ZIP, preserving private local state."""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, zipfile
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'.git', '.venv', 'venv', 'node_modules', '__pycache__', '.pytest_cache', '.vercel', '.hyperframes', '.playwright-mcp', 'build'}
ENV_EXAMPLES = {'.env.example', '.env.business.example'}

def included(path):
    return not (any(p in EXCLUDED for p in path.parts) or path.parts[0] == 'data'
        or path.name == 'PROMPT.md' or (path.name.startswith('.env') and path.name not in ENV_EXAMPLES)
        or path.suffix in {'.pyc', '.pyo', '.tmp'} or path.name == 'DELIVERY_MANIFEST.json')

def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def candidates():
    if (ROOT / '.git').exists():
        names = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=ROOT).decode().split('\0')
        return sorted({Path(n) for n in names if n and included(Path(n)) and (ROOT / n).is_file()})
    return sorted(p.relative_to(ROOT) for p in ROOT.rglob('*') if p.is_file() and included(p.relative_to(ROOT)))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    files = [p for p in candidates() if (ROOT / p).resolve() != output]
    assert all((ROOT / p).resolve().is_relative_to(ROOT) for p in files), 'External symlink excluded'
    assert ENV_EXAMPLES.issubset({p.as_posix() for p in files}), 'Both configuration examples required'
    demos = ROOT / 'examples/thai_lab_reference_v3'
    for entry in json.loads((demos / 'MANIFEST.json').read_text()):
        p = demos / entry['file']
        assert p.stat().st_size == entry['bytes'] and digest(p) == entry['sha256'], entry['file']
    candidate = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip() if (ROOT / '.git').exists() else None
    dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT).strip()) if candidate else None
    manifest = {'version': '3.0.0', 'created_utc': datetime.now(timezone.utc).isoformat(),
        'baseline_commit': '2069389d718c3bacbc6ef4a064a3d618ca96615f',
        'candidate_commit': candidate, 'working_tree_dirty': dirty, 'private_state_included': False,
        'verification': 'docs/business-v3/VERIFICATION.md',
        'files': [{'path': p.as_posix(), 'bytes': (ROOT / p).stat().st_size, 'sha256': digest(ROOT / p)} for p in files]}
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_name(output.name + '.tmp')
    try:
        with zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for p in files:
                archive.write(ROOT / p, 'ResultScope/' + p.as_posix())
            archive.writestr('ResultScope/DELIVERY_MANIFEST.json', json.dumps(manifest, indent=2) + '\n')
        with zipfile.ZipFile(temp) as archive:
            assert archive.testzip() is None, 'Archive CRC failure'
        os.replace(temp, output)
    finally:
        if temp.exists(): temp.unlink()
    print(json.dumps({'file': str(output), 'files': len(files) + 1, 'bytes': output.stat().st_size, 'sha256': digest(output), 'candidate_commit': candidate, 'dirty': dirty}))

if __name__ == '__main__': main()
