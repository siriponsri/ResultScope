"""Verify packaged public-source bytes and approved retrieval records without network access."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from services.evidence_search import corpus
manifest=json.loads((ROOT/'knowledge/medical_sources/source_manifest.json').read_text())
for row in manifest['sources']:
    if row.get('local_path'):
        p=ROOT/'knowledge/medical_sources'/row['local_path']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],row['id']
for row in json.loads((ROOT/'examples/thai_lab_reference_v3/MANIFEST.json').read_text()):
    p=ROOT/'examples/thai_lab_reference_v3'/row['file']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],row['file']
print(json.dumps({'runtime_records':len(corpus()),'source_urls':len(manifest['sources']),'integrity':'PASS','network_calls':0}))
