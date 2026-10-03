from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import EvidenceCorpus,ROOT
from guidance import GuidelineCorpus
if __name__=='__main__':
    c=EvidenceCorpus();(ROOT/'data/tree.json').write_text(json.dumps(c.tree,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    g=GuidelineCorpus();(ROOT/'data/guidelines/tree.json').write_text(json.dumps(g.tree,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Tree rebuilt from verified public-reference records. No model calls.')
