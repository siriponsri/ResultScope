"""Honest provenance for a Git checkout or the distributed source archive."""
from pathlib import Path
import hashlib
import subprocess


def source_revision(root: Path) -> str:
    if (root / '.git').exists():
        try:
            return subprocess.run(['git','rev-parse','HEAD'],cwd=root,check=True,
                                  capture_output=True,text=True).stdout.strip()
        except (OSError,subprocess.CalledProcessError):
            pass
    manifest=root/'DELIVERY_MANIFEST.json'
    if manifest.is_file():
        return 'source-archive-sha256:'+hashlib.sha256(manifest.read_bytes()).hexdigest()
    return 'unversioned-source'
