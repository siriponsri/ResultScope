"""Loopback-only reference browser. No model, patient storage, or app mounting."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from pathlib import Path
import argparse,json,sys
if __package__:
    from .core import EvidenceCorpus,ROOT,safe_file
    from .guidance import GuidelineCorpus
else:
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from core import EvidenceCorpus,ROOT,safe_file
    from guidance import GuidelineCorpus

def make_handler(corpus, guidance=None):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def send_data(self,data,ctype='application/json; charset=utf-8',status=200):
            self.send_response(status)
            for k,v in {'Content-Type':ctype,'Content-Length':str(len(data)),'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"}.items():self.send_header(k,v)
            self.end_headers();self.wfile.write(data)
        def json(self,obj,status=200):self.send_data(json.dumps(obj,ensure_ascii=False).encode(),status=status)
        def valid_host(self):
            return self.headers.get('Host','') in ('127.0.0.1:'+str(self.server.server_port),'localhost:'+str(self.server.server_port))
        def do_GET(self):
            if not self.valid_host():return self.json({'error':'invalid_host'},403)
            path=urlsplit(self.path).path
            files={'/':('index.html','text/html; charset=utf-8'),'/app.js':('app.js','application/javascript; charset=utf-8'),'/style.css':('style.css','text/css; charset=utf-8')}
            if path in files:
                name,ct=files[path];return self.send_data((ROOT/'ui'/name).read_bytes(),ct)
            if path=='/fonts/NotoSansThai.ttf':return self.send_data((ROOT/'ui/fonts/NotoSansThai.ttf').read_bytes(),'font/ttf')
            if path=='/api/meta':return self.json({'sources':len(corpus.sources),'records':len(corpus.records),'guideline_sources':len(guidance.sources) if guidance else 0,'guideline_notes':len(guidance.notes) if guidance else 0,'guideline_tree':guidance.tree if guidance else None,'organisations':sorted({s['organisation'] for s in corpus.sources.values()}),'mode':'reference_browser_no_llm','tree':corpus.tree})
            if path.startswith('/source/'):
                sid=path.removeprefix('/source/')
                if sid in corpus.sources:return self.send_data(safe_file(corpus.root,corpus.sources[sid]['snapshot_path']).read_bytes(),'application/pdf')
                if guidance and sid in guidance.sources:return self.send_data(safe_file(guidance.root,guidance.sources[sid]['snapshot_path']).read_bytes(),'application/pdf')
            return self.json({'error':'not_found'},404)
        def do_POST(self):
            if not self.valid_host():return self.json({'error':'invalid_host'},403)
            origin=self.headers.get('Origin')
            if origin and origin not in ('http://127.0.0.1:'+str(self.server.server_port),'http://localhost:'+str(self.server.server_port)):
                return self.json({'error':'cross_origin_rejected'},403)
            try:
                if self.headers.get_content_type()!='application/json':raise ValueError('json_required')
                n=int(self.headers.get('Content-Length','0'))
                if not 0<n<=8000:raise ValueError('body_too_large_or_empty')
                body=json.loads(self.rfile.read(n))
                if not isinstance(body,dict):raise ValueError('object_required')
                path=urlsplit(self.path).path
                if path=='/api/search':
                    if set(body)-{'query','organisation','sex','method'}:raise ValueError('unknown_field')
                    result=corpus.search(**body)
                    result['guidance']=guidance.search(body['query']) if guidance and not body.get('organisation') and not body.get('sex') else []
                    if result['guidance']:result['status']='found'
                elif path=='/api/compare':
                    if set(body)-{'value','unit','record_id','comparator','source_comparison_confirmed'}:raise ValueError('unknown_field')
                    result=corpus.compare(**body)
                else:return self.json({'error':'not_found'},404)
                return self.json(result)
            except (ValueError,TypeError,KeyError):return self.json({'error':'invalid_request'},400)
    return Handler

def main():
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8765);args=p.parse_args()
    corpus=EvidenceCorpus();guidance=GuidelineCorpus()
    with ThreadingHTTPServer(('127.0.0.1',args.port),make_handler(corpus,guidance)) as server:
        print(f'Reference preview: http://127.0.0.1:{server.server_port} (no LLM / no patient data storage)',flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass
if __name__=='__main__':main()
