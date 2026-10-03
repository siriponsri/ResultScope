"""Open-access WHO guidance summaries, separate from numeric reference records."""
import json
if __package__:
    from .core import ROOT, safe_file, digest, alias_matches
else:
    from core import ROOT, safe_file, digest, alias_matches

class GuidelineCorpus:
    def __init__(self, root=ROOT):
        self.root=root
        manifest=json.loads((root/'data/guidelines/source_manifest.json').read_text(encoding='utf-8'))
        self.sources={s['source_id']:s for s in manifest['sources']}
        self.notes=json.loads((root/'data/guidelines/notes.json').read_text(encoding='utf-8'))['notes']
        if manifest.get('schema_version')!='rs-guidance-1' or len(self.sources)!=len(manifest['sources']) or not self.notes:raise ValueError('invalid_guidelines')
        for s in self.sources.values():
            if s.get('release_eligible') is not False or s.get('commercial_use_approved') is not False:raise ValueError('guideline_approval_not_established')
            for path,sha in [('snapshot_path','sha256'),('text_path','text_sha256')]:
                if digest(safe_file(root,s[path]))!=s[sha]:raise ValueError('guideline_checksum_mismatch')
        ids=set()
        for n in self.notes:
            s=self.sources.get(n['source_id'])
            if not s or n['note_id'] in ids or n['source_sha256']!=s['sha256']:raise ValueError('invalid_guideline_provenance')
            if n.get('numeric_rule') is not False or n.get('release_eligible') is not False or not 1<=n['pdf_page']<=s['pdf_pages']:raise ValueError('invalid_guideline_boundary')
            ids.add(n['note_id'])
        self.tree={'node_id':'guidelines','kind':'guideline_corpus','title':'WHO open-access guidance (non-commercial)','children':[
            {'node_id':sid,'kind':'document','title':s['title'],'children':[
                {'node_id':n['note_id'],'kind':'educational_summary','title':n['title_th'],'pdf_page':n['pdf_page']}
                for n in self.notes if n['source_id']==sid]} for sid,s in self.sources.items()]}

    def search(self, query):
        if not isinstance(query,str) or not 1<=len(query.strip())<=1000:raise ValueError('invalid_guidance_query')
        out=[]
        for n in self.notes:
            if any(alias_matches(query,a) for a in n['aliases']):
                s=self.sources[n['source_id']]
                out.append({**n,'source_title':s['title'],'source_url':s['url']+'#page='+str(n['pdf_page']),'publication_url':s['publication_url'],'published':s['published'],'license':s['license'],'license_url':s['license_url'],'clinical_classification':None})
        return out
