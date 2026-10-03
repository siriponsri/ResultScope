import json,sys,threading,unittest,urllib.request,urllib.error
from pathlib import Path
from http.server import ThreadingHTTPServer
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from preview import make_handler
from core import EvidenceCorpus
from guidance import GuidelineCorpus

class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(EvidenceCorpus(),GuidelineCorpus()));cls.url='http://127.0.0.1:'+str(cls.server.server_port)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def request(self,path,body=None,headers=None):
        h={'Content-Type':'application/json',**(headers or {})}
        req=urllib.request.Request(self.url+path,data=json.dumps(body).encode() if body is not None else None,headers=h)
        try:r=urllib.request.urlopen(req,timeout=5)
        except urllib.error.HTTPError as e:r=e
        with r:return r.status,r.headers,r.read()
    def test_search_real_corpus(self):
        code,h,b=self.request('/api/search',{'query':'ALT'});self.assertEqual(code,200);self.assertEqual(len(json.loads(b)['records']),4)
    def test_host_header_rejected(self):self.assertEqual(self.request('/api/meta',headers={'Host':'evil.test'})[0],403)
    def test_cross_origin_rejected(self):self.assertEqual(self.request('/api/search',{'query':'ALT'},headers={'Origin':'https://evil.test'})[0],403)
    def test_invalid_body(self):self.assertEqual(self.request('/api/search',[])[0],400)
    def test_no_env_route(self):self.assertEqual(self.request('/.env')[0],404)
    def test_no_arbitrary_source_path(self):self.assertEqual(self.request('/source/../../core.py')[0],404)
    def test_pdf_snapshot(self):
        code,h,b=self.request('/source/siriraj-alt');self.assertEqual(code,200);self.assertTrue(b.startswith(b'%PDF'))
    def test_page_no_external_script(self):
        code,h,b=self.request('/');self.assertEqual(code,200);self.assertIn("script-src 'self'",h['Content-Security-Policy'])
    def test_no_mode_override(self):self.assertEqual(self.request('/api/search',{'query':'ALT','mode':'release'})[0],400)
    def test_guideline_search_is_separate(self):
        code,h,b=self.request('/api/search',{'query':'เฟอร์ริติน'});d=json.loads(b)
        self.assertEqual(code,200);self.assertEqual(d['records'],[]);self.assertEqual(len(d['guidance']),2);self.assertIsNone(d['clinical_classification'])
    def test_guideline_source_is_allowlisted(self):
        code,h,b=self.request('/source/who-haemoglobin-2024');self.assertEqual(code,200);self.assertTrue(b.startswith(b'%PDF'))
if __name__=='__main__':unittest.main()
