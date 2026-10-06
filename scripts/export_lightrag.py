"""Export verified public evidence only; never connects to a service or imports demos."""
from pathlib import Path
import argparse
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from services.evidence_search import corpus

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    rows=corpus()
    payload={'texts':[r['title']+'\n'+r['content'] for r in rows],
             'file_sources':['resultscope://evidence/'+r['id'] for r in rows]}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Exported {len(rows)} verified public records; no network calls.')
if __name__=='__main__':main()
