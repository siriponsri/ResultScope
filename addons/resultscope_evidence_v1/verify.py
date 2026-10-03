"""Offline corpus/package checks; emits actual results only."""
import hashlib,json,sys,subprocess
from pathlib import Path
from core import EvidenceCorpus,ROOT
from guidance import GuidelineCorpus
def main():
    c=EvidenceCorpus();g=GuidelineCorpus()
    p=ROOT/'PACKAGE_CHECKSUMS.json'
    if p.exists():
        for name,sha in json.loads(p.read_text(encoding='utf-8'))['files'].items():
            f=(ROOT/name).resolve()
            if not f.is_relative_to(ROOT.resolve()) or not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=sha:
                print('PACKAGE_CHECKSUM_FAILED',name);return 1
    if json.loads((ROOT/'data/tree.json').read_text(encoding='utf-8'))!=c.tree:
        print('TREE_STALE');return 1
    if json.loads((ROOT/'data/guidelines/tree.json').read_text(encoding='utf-8'))!=g.tree:
        print('GUIDELINE_TREE_STALE');return 1
    print('CORPUS_HASH_AND_STRUCTURE_PASS',len(c.sources),'sources',len(c.records),'records')
    print('GUIDELINE_HASH_AND_STRUCTURE_PASS',len(g.sources),'sources',len(g.notes),'educational notes')
    return subprocess.call([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-v'])
if __name__=='__main__':raise SystemExit(main())
