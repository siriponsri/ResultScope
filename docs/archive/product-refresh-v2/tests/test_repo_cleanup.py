"""Destructive cleanup must refuse drift and preserve recoverable owner bytes."""
import json
import zipfile
from pathlib import Path
import pytest
from scripts.apply_repo_cleanup import ARCHIVE, CleanupBlocked, cleanup, digest


def fixture(tmp_path, paths=None):
    root = tmp_path / 'repo'
    root.mkdir()
    paths = paths or {'CODEX_PROMPT.md': b'old instructions\n', 'static/js/scene.js': b'old scene\n'}
    archive = root / ARCHIVE
    archive.parent.mkdir(parents=True)
    rows = []
    with zipfile.ZipFile(archive, 'w') as z:
        for name, data in paths.items():
            z.writestr(name, data)
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            rows.append({'path': name, 'sha256': digest(data), 'lf_sha256': digest(data)})
    manifest = {'schema_version': 1, 'archive': ARCHIVE, 'archive_sha256': digest(archive.read_bytes()),
                'baseline_commit': 'fixture', 'removals': rows}
    return root, manifest


def test_dry_run_is_read_only(tmp_path):
    root, manifest = fixture(tmp_path)
    result = cleanup(root, manifest)
    assert result['eligible'] == 2 and result['removed'] == 0
    assert (root / 'CODEX_PROMPT.md').exists()
    assert list(tmp_path.iterdir()) == [root]


def test_apply_backs_up_exact_crlf_bytes_and_is_idempotent(tmp_path):
    root, manifest = fixture(tmp_path)
    (root / 'CODEX_PROMPT.md').write_bytes(b'old instructions\r\n')
    private = root / '.env'
    private.write_text('unchanged owner data')
    result = cleanup(root, manifest, apply=True)
    assert result['removed'] == 2
    assert Path(result['backup']).parent.parent == root.parent
    with zipfile.ZipFile(result['backup']) as z:
        assert z.read('CODEX_PROMPT.md') == b'old instructions\r\n'
        assert '.env' not in z.namelist()
    assert private.read_text() == 'unchanged owner data'
    assert cleanup(root, manifest, apply=True)['removed'] == 0


def test_one_changed_file_blocks_all_deletions(tmp_path):
    root, manifest = fixture(tmp_path)
    (root / 'static/js/scene.js').write_text('owner change')
    with pytest.raises(CleanupBlocked, match='Changed file'):
        cleanup(root, manifest, apply=True)
    assert (root / 'CODEX_PROMPT.md').exists()
    assert list(tmp_path.iterdir()) == [root]


def test_corrupt_archive_blocks_cleanup(tmp_path):
    root, manifest = fixture(tmp_path)
    (root / ARCHIVE).write_bytes(b'corrupt')
    with pytest.raises(CleanupBlocked, match='archive'):
        cleanup(root, manifest, apply=True)
    assert (root / 'CODEX_PROMPT.md').exists()


@pytest.mark.parametrize('name', ['.env', 'data/admin_settings.key', '../outside.md', '/tmp/any',
                                 'docs/progress/../../.env', 'docs/progress/x:ads', r'docs\progress\x.md'])
def test_protected_and_escaping_paths_are_rejected(tmp_path, name):
    root, manifest = fixture(tmp_path)
    manifest['removals'][0]['path'] = name
    with pytest.raises(CleanupBlocked, match='scope'):
        cleanup(root, manifest, apply=True)
    assert (root / 'CODEX_PROMPT.md').exists()


def test_symlink_is_rejected(tmp_path):
    root, manifest = fixture(tmp_path)
    target = root / 'CODEX_PROMPT.md'
    target.unlink()
    outside = tmp_path / 'outside.md'
    outside.write_bytes(b'old instructions\n')
    try:
        target.symlink_to(outside)
    except OSError:
        pytest.skip('Host cannot create symlinks')
    with pytest.raises(CleanupBlocked, match='Symlink'):
        cleanup(root, manifest, apply=True)
    assert outside.read_bytes() == b'old instructions\n'
