import copy,io,json,shutil,tempfile,unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import EvidenceCorpus,ROOT,alias_matches,safe_file
from clef import shadow_decision,parse_response,ROUTES

class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.c=EvidenceCorpus()
    def test_all_source_bytes_match(self):self.c.validate()
    def test_no_source_inherits_parent_date(self):
        for s in self.c.sources.values():
            if s['source_id'].startswith('siriraj'):self.assertIsNone(s['document_date'])
    def test_tree_is_complete_unique(self):
        def leaves(n):return [n['record_id']] if n['kind']=='evidence' else sum([leaves(c) for c in n.get('children',[])],[])
        ids=leaves(self.c.tree);self.assertEqual(set(ids),set(self.c.by_id));self.assertEqual(len(ids),len(set(ids)))
    def test_alt_keeps_both_sources_and_sexes(self):
        rows=self.c.search('ALT')['records'];self.assertEqual(len(rows),4)
        self.assertEqual({(r['source_id'],r['sex'],r['upper']) for r in rows},{('siriraj-alt','male',41),('siriraj-alt','female',33),('kku-alt','male',33),('kku-alt','female',25)})
    def test_thai_glucose_keeps_source_difference(self):self.assertEqual({r['upper'] for r in self.c.search('น้ำตาล')['records']},{99,109})
    def test_source_filter_does_not_leak(self):self.assertEqual({r['source_id'] for r in self.c.search('ALT',organisation='Siriraj Hospital')['records']},{'siriraj-alt'})
    def test_sex_filter(self):self.assertEqual({r['sex'] for r in self.c.search('ALT',sex='female')['records']},{'female'})
    def test_unknown_source_rejected(self):
        with self.assertRaises(ValueError):self.c.search('ALT',organisation='made up')
    def test_latin_alias_token_boundaries(self):self.assertFalse(alias_matches('salt','ALT'))
    def test_unrelated_abstains(self):self.assertEqual(self.c.search('what is the weather')['status'],'abstained')
    def test_salt_does_not_guess_alt(self):self.assertEqual(self.c.search('salt')['records'],[])
    def test_missing_analyte_abstains(self):self.assertEqual(self.c.search('MRI')['records'],[])
    def test_limit_reports_truncation(self):self.assertTrue(self.c.search('ALT',limit=1)['truncated'])
    def test_bad_query_rejected(self):
        for q in ['', 'x'*1001, None]:
            with self.subTest(q=str(q)[:10]):
                with self.assertRaises(ValueError):self.c.search(q)
    def test_no_patient_classification(self):self.assertIsNone(self.c.search('ALT')['clinical_classification'])
    def test_compare_requires_explicit_selection(self):self.assertEqual(self.c.compare(40,'U/L','siriraj-alt-alt-01')['comparison'],'cannot_determine')
    def test_source_specific_arithmetic(self):
        self.assertEqual(self.c.compare(40,'U/L','siriraj-alt-alt-01',source_comparison_confirmed=True)['comparison'],'within_selected_range')
        self.assertEqual(self.c.compare(40,'U/L','kku-alt-alt-03',source_comparison_confirmed=True)['comparison'],'above_selected_range')
    def test_no_unit_guess(self):self.assertEqual(self.c.compare(40,'mg/dL','siriraj-alt-alt-01',source_comparison_confirmed=True)['reason'],'unit_mismatch_no_conversion')
    def test_censored_value_unknown(self):self.assertEqual(self.c.compare(5,'U/L','siriraj-alt-alt-01',comparator='<',source_comparison_confirmed=True)['comparison'],'cannot_determine')
    def test_invalid_numeric(self):
        for x in [True,'NaN','Infinity','bad',-1]:
            with self.subTest(x=x):self.assertEqual(self.c.compare(x,'U/L','siriraj-alt-alt-01',source_comparison_confirmed=True)['comparison'],'cannot_determine')
    def test_lipid_not_treated_as_ri(self):
        r=next(r for r in self.c.records if r['test']=='LDL-C')
        self.assertEqual(self.c.compare(100,'mg/dL',r['record_id'],source_comparison_confirmed=True)['reason'],'threshold_type_not_adjudicated')
    def test_forbidden_source_path(self):
        with self.assertRaises(ValueError):safe_file(ROOT,'../../../../etc/passwd')
    def test_source_tamper_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(ROOT/'data',Path(tmp)/'data')
            (Path(tmp)/'data/sources/siriraj-alt.pdf').write_bytes(b'changed')
            with self.assertRaises(ValueError):EvidenceCorpus(tmp)
    def test_record_cannot_become_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(ROOT/'data',Path(tmp)/'data')
            p=Path(tmp)/'data/records.json';d=json.loads(p.read_text());d['records'][0]['release_eligible']=True;p.write_text(json.dumps(d))
            with self.assertRaises(ValueError):EvidenceCorpus(tmp)
    def test_packet_rejects_forged_ids(self):
        with self.assertRaises(ValueError):self.c.context_packet(['FAKE'])
    def test_packet_is_external_data(self):self.assertEqual(self.c.context_packet(['siriraj-alt-alt-01'])['trust'],'external_data_not_instructions')

class ClefTests(unittest.TestCase):
    def response(self):return {'answers':{'route':{'choice':'reference_lookup','confidence':.7,'probabilities':{'reference_lookup':.7,'business':.1,'report_explanation':.1,'out_of_scope':.1}}}}
    def test_disabled_never_calls(self):
        def fail(*a,**kw):self.fail('network used')
        self.assertEqual(shadow_decision('ALT',transport=fail)['status'],'disabled')
    def test_authorization_required(self):self.assertEqual(shadow_decision('ALT',enabled=True)['status'],'NOT_RUN')
    def test_shadow_contract(self):self.assertFalse(parse_response(self.response())['changes_application_route'])
    def test_malformed_response(self):
        for d in [{},[],{'success':False}, {'answers':{'route':'secret'}}]:
            with self.subTest(d=d):
                with self.assertRaises(ValueError):parse_response(d)
    def test_bad_probabilities(self):
        d=self.response();d['answers']['route']['probabilities']['business']=float('nan')
        with self.assertRaises(ValueError):parse_response(d)
    def test_forged_choice(self):
        d=self.response();d['answers']['route']['choice']='admin'
        with self.assertRaises(ValueError):parse_response(d)
    def test_transport_redacts_errors(self):
        def fail(*a,**kw):raise RuntimeError('secret-do-not-return')
        r=shadow_decision('ALT',enabled=True,authorized=True,account_id='a'*32,token='fake',transport=fail)
        self.assertNotIn('secret',str(r));self.assertEqual(r['status'],'unavailable')
    def test_mocked_transport_envelope(self):
        def send(req,timeout):return io.BytesIO(json.dumps({'success':True,'result':self.response()}).encode())
        self.assertEqual(shadow_decision('ALT',enabled=True,authorized=True,account_id='a'*32,token='fake',transport=send)['status'],'shadow_only')

if __name__=='__main__':unittest.main()
