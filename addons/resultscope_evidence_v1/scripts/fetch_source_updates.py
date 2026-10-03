"""Fetch allowlisted source URLs into a NEW review directory; never auto-promote."""
from pathlib import Path
import argparse,hashlib,json,urllib.request,urllib.parse,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import ROOT
HOSTS={'www.si.mahidol.ac.th','lab.md.kku.ac.th','iris.who.int'}
def valid(url):return urllib.parse.urlsplit(url).scheme=='https' and urllib.parse.urlsplit(url).hostname in HOSTS
class AllowedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if not valid(newurl):raise ValueError('redirect_outside_allowlist')
        return super().redirect_request(req,fp,code,msg,headers,newurl)
def main():
    p=argparse.ArgumentParser();p.add_argument('--destination',type=Path,required=True);a=p.parse_args()
    a.destination.mkdir(parents=True,exist_ok=False)
    m=json.loads((ROOT/'data/source_manifest.json').read_text(encoding='utf-8'));g=json.loads((ROOT/'data/guidelines/source_manifest.json').read_text(encoding='utf-8'));results=[]
    for s in [*m['sources'],*g['sources']]:
        try:
            if not valid(s['url']):raise ValueError('unapproved_source_host')
            with urllib.request.build_opener(AllowedRedirect).open(s['url'],timeout=30) as r:b=r.read(10*1024*1024+1)
            if len(b)>10*1024*1024 or not b.startswith(b'%PDF'):raise ValueError('invalid_pdf')
            (a.destination/(s['source_id']+'.pdf')).write_bytes(b);sha=hashlib.sha256(b).hexdigest()
            results.append({'source_id':s['source_id'],'sha256':sha,'status':'UNCHANGED' if sha==s['sha256'] else 'CHANGED_REQUIRES_REVIEW'})
        except Exception:results.append({'source_id':s['source_id'],'status':'FETCH_FAILED'})
    (a.destination/'fetch-report.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    print('Downloaded into review directory only; source manifest and records unchanged.')
    return int(any(x['status']=='FETCH_FAILED' for x in results))
if __name__=='__main__':raise SystemExit(main())
