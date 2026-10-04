"""Evaluate identical fixed cases on extension flat/tree methods, offline."""
import argparse,json,time
from pathlib import Path
from core import EvidenceCorpus,ROOT

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'evidence/retrieval-comparison.json');args=p.parse_args()
    c=EvidenceCorpus();cases=[json.loads(l) for l in (ROOT/'evaluation/retrieval_cases.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    report={'scope':'Extension flat versus hierarchical alias retrieval; NOT a benchmark of local Phase 2 code','provider_calls':0,'corpus_version':c.version,'results':[]}
    for method in ('flat','tree'):
        for case in cases:
            result=c.search(case['query'],method=method,organisation=case.get('organisation'),sex=case.get('sex'))
            actual={r['source_id'] for r in result['records']}
            passed=actual==set(case['expected_source_ids'])
            report['results'].append({'case_id':case['case_id'],'set':case['set'],'method':method,'query':case['query'],'expected_source_ids':case['expected_source_ids'],'actual_source_ids':sorted(actual),'latency_ms':result['latency_ms'],'result':'PASS' if passed else 'FAIL'})
    report['summary']={method:{'passed':sum(x['result']=='PASS' for x in report['results'] if x['method']==method),'total':len(cases)} for method in ('flat','tree')}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report['summary']))
    # The flat comparator is an observed baseline, not the implementation gate.
    return 0 if all(x['result']=='PASS' for x in report['results'] if x['method']=='tree') else 1
if __name__=='__main__':raise SystemExit(main())
