import json,sys,unittest,tempfile,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from guidance import GuidelineCorpus
from core import ROOT

class GuidelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.c=GuidelineCorpus()
    def test_thai_ferritin_has_page_and_license(self):
        rows=self.c.search('เฟอร์ริติน');self.assertEqual(len(rows),2)
        for r in rows:self.assertEqual(r['pdf_page'],37);self.assertEqual(r['license'],'CC BY-NC-SA 3.0 IGO');self.assertIsNone(r['clinical_classification'])
    def test_hb_never_matches_substring(self):
        self.assertEqual(self.c.search('flashback'),[]);self.assertEqual(len(self.c.search('Hb')),1)
    def test_guidelines_are_not_numeric_rules(self):
        for n in self.c.notes:self.assertFalse(n['numeric_rule']);self.assertFalse(n['release_eligible']);self.assertNotIn('lower',n)
    def test_tree_covers_every_note(self):
        ids={n['node_id'] for d in self.c.tree['children'] for n in d['children']};self.assertEqual(ids,{n['note_id'] for n in self.c.notes})
    def test_tampered_pdf_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);shutil.copytree(ROOT/'data/guidelines',root/'data/guidelines')
            (root/'data/guidelines/who-ferritin-2020.pdf').write_bytes(b'%PDF-changed')
            with self.assertRaisesRegex(ValueError,'guideline_checksum_mismatch'):GuidelineCorpus(root)
