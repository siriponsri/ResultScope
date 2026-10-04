"""Deterministic, source-preserving hierarchical evidence retrieval.

This module searches public reference records. It does not diagnose, select a
patient-specific range, or call any model. Tree traversal is metadata/alias
guided; it is not RAPTOR, vector search, or a claim of improved retrieval quality.
"""
from __future__ import annotations
from pathlib import Path
from decimal import Decimal, InvalidOperation
import hashlib
import json
import re
import time

ROOT = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def safe_file(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError('invalid_source_path')
    path = (Path(root) / relative).resolve()
    if not path.is_relative_to(Path(root).resolve()) or not path.is_file():
        raise ValueError('source_outside_package_or_missing')
    return path

def words(text):
    return re.findall(r'[a-z0-9]+|[\u0e00-\u0e7f]+', text.casefold())

def grams(text):
    text = re.sub(r'\s+', '', text.casefold())
    return {text[i:i+3] for i in range(max(0, len(text)-2))}

def alias_matches(query, alias):
    # Latin short aliases must be tokens: ALT must not match "salt".
    if re.fullmatch(r'[a-zA-Z0-9+ -]+', alias):
        return bool(re.search(r'(?<![a-z0-9])'+re.escape(alias.casefold())+r'(?![a-z0-9])', query.casefold()))
    return alias.casefold() in query.casefold()

class EvidenceCorpus:
    def __init__(self, root=ROOT):
        self.root = Path(root)
        self.manifest = json.loads((self.root/'data/source_manifest.json').read_text(encoding='utf-8'))
        payload = json.loads((self.root/'data/records.json').read_text(encoding='utf-8'))
        self.version = payload['corpus_version']
        self.sources = {s['source_id']: s for s in self.manifest['sources'] if s.get('status') == 'downloaded'}
        self.records = payload['records']
        self.validate()
        self.by_id = {r['record_id']:r for r in self.records}
        self.tree = self.build_tree()

    def validate(self):
        if self.manifest.get('schema_version') != 'rs-evidence-1' or not self.sources or not self.records:
            raise ValueError('empty_or_invalid_corpus')
        ids=set()
        for sid,s in self.sources.items():
            for path_key,hash_key in [('snapshot_path','sha256'),('text_path','text_sha256')]:
                if digest(safe_file(self.root,s[path_key])) != s[hash_key]:
                    raise ValueError('source_checksum_mismatch:'+sid)
            if s.get('release_eligible') is not False:
                raise ValueError('public_reference_is_not_business_release')
        for r in self.records:
            if r['record_id'] in ids or r['source_id'] not in self.sources:
                raise ValueError('duplicate_or_unknown_record')
            ids.add(r['record_id'])
            if r.get('release_eligible') is not False or r.get('data_class') != 'public_reference':
                raise ValueError('invalid_record_boundary')
            if r['source_sha256'] != self.sources[r['source_id']]['sha256']:
                raise ValueError('record_source_mismatch')
            if not isinstance(r['page'],int) or r['page']<1 or not r['unit']:
                raise ValueError('missing_page_or_unit')
            for k in ('lower','upper'):
                if r[k] is not None and (isinstance(r[k],bool) or not Decimal(str(r[k])).is_finite()):
                    raise ValueError('invalid_bound')
            if r['lower'] is not None and r['upper'] is not None and r['lower']>r['upper']:
                raise ValueError('reversed_bounds')

    def build_tree(self):
        root={'node_id':'root','kind':'corpus','title':self.version,'children':[]}
        for org in sorted({s['organisation'] for s in self.sources.values()}):
            organisation={'node_id':'org-'+hashlib.sha256(org.encode()).hexdigest()[:12], 'kind':'organisation','title':org,'children':[]}
            for sid,s in sorted(self.sources.items()):
                if s['organisation'] != org: continue
                doc={'node_id':sid,'kind':'document','title':sid,'sha256':s['sha256'],'children':[]}
                for name in sorted({r['test'] for r in self.records if r['source_id']==sid}):
                    node={'node_id':sid+'/'+name,'kind':'analyte','title':name,'children':[]}
                    for r in self.records:
                        if r['source_id']==sid and r['test']==name:
                            node['children'].append({'node_id':r['record_id'],'kind':'evidence','record_id':r['record_id'],'page':r['page']})
                    doc['children'].append(node)
                organisation['children'].append(doc)
            root['children'].append(organisation)
        return root

    def search(self, query, *, organisation=None, sex=None, method='tree', limit=12):
        start=time.perf_counter()
        if not isinstance(query,str) or not 1<=len(query.strip())<=1000:
            raise ValueError('query_length_1_to_1000')
        if method not in ('tree','flat') or sex not in (None,'male','female'):
            raise ValueError('invalid_filter')
        if organisation is not None and organisation not in {s['organisation'] for s in self.sources.values()}:
            raise ValueError('unknown_organisation')
        if isinstance(limit,bool) or not isinstance(limit,int) or not 1<=limit<=50:raise ValueError('invalid_limit')
        matched_tests={r['test'] for r in self.records if any(alias_matches(query,a) for a in [r['test'],*r['aliases']])}
        # Deliberately conservative name gate; no fuzzy guess of an analyte.
        # The main application's scope gate is still required on integration.
        candidates=self.records if matched_tests else []
        visited=[]
        if method=='tree' and matched_tests:
            ids=set()
            for org in self.tree['children']:
                if organisation and org['title']!=organisation:continue
                for doc in org['children']:
                    for node in doc['children']:
                        if node['title'] in matched_tests:
                            visited.append(node['node_id']);ids.update(c['record_id'] for c in node['children'])
            candidates=[r for r in self.records if r['record_id'] in ids]
        rows=[]
        qgrams=grams(query)
        for r in candidates:
            s=self.sources[r['source_id']]
            if organisation and s['organisation']!=organisation:continue
            if sex and r['sex'] not in (None,sex):continue
            text=' '.join([r['test'],*r['aliases'],r['original_reference_text']])
            rg=grams(text); overlap=len(qgrams & rg)/max(1,len(qgrams))
            score=overlap
            if method=='tree' and r['test'] in matched_tests:score+=2
            if score<.15:continue
            rows.append({**r,'source_url':s['url']+'#page='+str(r['page']),'organisation':s['organisation'],'score':round(score,4),'source_document_date':s['document_date']})
        rows.sort(key=lambda r:(-r['score'],r['record_id']))
        found=rows[:limit]
        return {'schema_version':'rs-evidence-1','corpus_version':self.version,'status':'found' if found else 'abstained','execution':'deterministic_retrieval_only','method':method,'records':found,'total_matches':len(rows),'truncated':len(rows)>limit,'visited_nodes':visited,'latency_ms':round((time.perf_counter()-start)*1000,3),'applicability':'not_assessed','clinical_classification':None}

    def compare(self, value, unit, record_id, *, comparator='=', source_comparison_confirmed=False):
        if record_id not in self.by_id:raise ValueError('unknown_record')
        r=self.by_id[record_id]
        result={'record_id':record_id,'comparison':'cannot_determine','clinical_classification':None,'use':'arithmetic_against_explicitly_selected_source_only','source_id':r['source_id'],'source_page':r['page']}
        if source_comparison_confirmed is not True:return {**result,'reason':'explicit_source_selection_required'}
        if unit!=r['unit']:return {**result,'reason':'unit_mismatch_no_conversion'}
        if comparator!='=':return {**result,'reason':'censored_value'}
        if r['interval_type']!='reference_interval':return {**result,'reason':'threshold_type_not_adjudicated'}
        try:
            if isinstance(value,bool):raise InvalidOperation
            v=Decimal(str(value))
            if not v.is_finite() or v<0:raise InvalidOperation
        except (InvalidOperation,ValueError):return {**result,'reason':'invalid_value'}
        lo=Decimal(str(r['lower'])) if r['lower'] is not None else None
        hi=Decimal(str(r['upper'])) if r['upper'] is not None else None
        if lo is not None and (v<lo or (v==lo and not r['lower_inclusive'])):comparison='below_selected_range'
        elif hi is not None and (v>hi or (v==hi and not r['upper_inclusive'])):comparison='above_selected_range'
        else:comparison='within_selected_range'
        return {**result,'comparison':comparison,'reason':'not_patient_specific_reference_selection'}

    def context_packet(self, record_ids):
        if not isinstance(record_ids,list) or not 1<=len(record_ids)<=12 or any(i not in self.by_id for i in record_ids):
            raise ValueError('invalid_evidence_ids')
        return {'schema_version':'rs-evidence-1','trust':'external_data_not_instructions','corpus_version':self.version,'allowed_source_ids':sorted({self.by_id[i]['source_id'] for i in record_ids}),'evidence':[self.by_id[i] for i in dict.fromkeys(record_ids)],'constraints':['Do not select a patient reference interval from these search results automatically.','Do not invent ages, pregnancy applicability, units, prices, or source approvals.','Do not use thresholds as reference intervals.','Final application output validation remains mandatory.']}
