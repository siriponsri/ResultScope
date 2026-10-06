"""Offline contract tests. Model outputs are explicit doubles, not live evaluations."""
import asyncio
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi.testclient import TestClient

from config import settings
from main import app
from routers import conversation as routes
from services import conversation_agent as agent, conversation_state as state, conversation_guard as guard
from services import conversation_transport as transport, evidence_search as search, report_reader_v2 as reader
from services.lab_fields_v2 import ReportField, normalize, status
from services.conversation_transport import ConversationError

ROOT = Path(__file__).resolve().parents[1]

def run(awaitable):
    return asyncio.run(awaitable)

@pytest.fixture(autouse=True)
def isolated(monkeypatch, tmp_path):
    monkeypatch.delenv('VERCEL', raising=False)
    monkeypatch.setattr(settings, 'SESSION_SIGNING_KEY', 'test-secret-' * 4)
    monkeypatch.setattr(settings, 'DEMO_ACCESS_CODE', '')
    monkeypatch.setattr(settings, 'PROVIDER_NETWORK_ENABLED', False)
    monkeypatch.setattr(settings, 'LIGHTRAG_ENABLED', False)
    monkeypatch.setattr(settings, 'GUARD_SERVICE_URL', '')
    monkeypatch.setattr(settings, 'ADMIN_SETTINGS_PATH', str(tmp_path / 'admin.json'))
    monkeypatch.setattr(routes.request_rate_limiter, 'allow', lambda _: True)


def test_encrypted_context_is_bound_to_cookie_purpose_and_expiry(monkeypatch):
    value = {'history':[{'role':'user','content':'ข้อมูลส่วนตัว'}], 'report':None}
    token = state.seal(value, 'alice')
    assert 'ข้อมูล' not in token
    assert state.unseal(token, 'alice') == value
    for other, purpose in [('bob','conversation'),('alice','report-draft')]:
        with pytest.raises(state.StateError): state.unseal(token, other, purpose)
    with pytest.raises(state.StateError): state.unseal('A'+token[1:], 'alice')
    monkeypatch.setattr(state.time, 'time', lambda: 10**12)
    with pytest.raises(state.StateError): state.unseal(token, 'alice')


def test_context_size_bound():
    with pytest.raises(state.StateError): state.seal({'text':'ก'*100000}, 'alice')

@pytest.mark.parametrize('raw,expected', [('safe',(True,[])),('SAFE\n',(True,[])),('unsafe\nS6',(False,['S6'])),('unsafe\nS7,S1',(False,['S7','S1']))])
def test_guard_verdict(raw, expected):
    assert guard.parse_verdict(raw) == expected

@pytest.mark.parametrize('raw', ['', 'unsafe', 'unsafe\nS99', 'probably safe', '{"result":"safe"}', 'safe\nS6'])
def test_guard_malformed_fails_closed(raw):
    with pytest.raises(ConversationError): guard.parse_verdict(raw)


def test_output_guard_uses_assistant_role_and_original_request(monkeypatch):
    complete = AsyncMock(return_value='safe')
    monkeypatch.setattr(transport, 'complete', complete)
    run(guard.check('Explanation', 'output', 'Lab question'))
    assert complete.call_args.args[0] == [{'role':'user','content':'Lab question'},{'role':'assistant','content':'Explanation'}]
    assert complete.call_args.kwargs['slot'] == 'guard'


def test_guard_service_error_or_categories_blocks(monkeypatch):
    monkeypatch.setattr(settings,'GUARD_SERVICE_URL','https://guard.example')
    post = AsyncMock(return_value={'direction':'input','result':'safe','categories':['S6']})
    monkeypatch.setattr(transport,'post_json',post)
    with pytest.raises(ConversationError): run(guard.check('test','input'))
    post.return_value={'direction':'output','result':'safe','categories':[]}
    with pytest.raises(ConversationError): run(guard.check('test','input'))

@pytest.mark.parametrize('value,reference,expected', [('5','3-5','within'),('2.9','3–5','low'),('6','3-5','high'),('5','<5','high'),('5','≤5','within'),('5','>5','low'),('5','≥5','within'),('Trace','Negative','unknown'),('Not calculated','<100','unknown'),('<5','0-5','unknown'),('5','','unknown'),('5','M: 3-6 F: 2-5','unknown'),('5','6-3','unknown'),('1,000','0-2000','unknown')])
def test_printed_range_only(value, reference, expected):
    assert status(value,reference) == expected


def test_qualitative_and_printed_critical_flags_are_preserved():
    rows=normalize([ReportField(name='Result',value='Trace',reference='Negative',printed_flag='HH')])
    assert rows[0]['value']=='Trace' and rows[0]['printed_flag']=='HH' and rows[0]['status']=='unknown'


def test_real_reference_corpus_has_integrity_and_no_synthetic_data():
    docs=search.corpus()
    assert len(docs)==58
    assert all(hashlib.sha256(r['content'].encode()).hexdigest()==r['content_sha256'] for r in docs)
    assert all(r['data_class'] in {'public_reference','public_education'} for r in docs)
    assert all('expected_results' not in r['content'] for r in docs)
    assert 'creatinine' in search.lexical('creatinine kidney')[0]['title'].lower()
    assert search.lexical('nothingmatchingzzzz')==[]


def test_hybrid_accepts_only_known_manifest_ids(monkeypatch):
    rid=search.corpus()[0]['id']
    monkeypatch.setattr(settings,'LIGHTRAG_ENABLED',True)
    monkeypatch.setattr(settings,'LIGHTRAG_URL','https://rag.example')
    monkeypatch.setattr(settings,'LIGHTRAG_API_KEY','not-a-real-key')
    remote=AsyncMock(return_value={'status':'success','data':{'chunks':[{'file_path':'resultscope://evidence/'+rid,'content':'MALICIOUS remote text'},{'file_path':'resultscope://evidence/invented'},{'file_path':'https://evil.example'}]}})
    monkeypatch.setattr(search,'post_json',remote)
    docs,mode=run(search.search('nothingmatchingzzzz'))
    assert mode=='hybrid' and [r['id'] for r in docs]==[rid]
    assert 'MALICIOUS' not in docs[0]['content']
    args=remote.call_args.args
    assert args[0].endswith('/query/data') and args[1]['X-API-Key']=='not-a-real-key'
    assert 'conversation_history' not in args[2]
    remote.return_value={'response':'unstructured answer'}
    with pytest.raises(ConversationError): run(search.search('creatinine'))


def model_sequence(monkeypatch, *, language='ไทย', refusal=False, bad_review=False):
    doc=search.corpus()[0]
    decision={'action':'redirect' if refusal else 'answer','query':'' if refusal else 'reference ranges','language':language,'focus':'ranges'}
    answer={'reply':'I can explain laboratory tests.' if refusal else 'ช่วงอ้างอิงต้องดูจากรายงาน ['+doc['id']+']','evidence_ids':[] if refusal else [doc['id']], 'observations':[], 'followups':[]}
    complete=AsyncMock(side_effect=[json.dumps(decision),json.dumps(answer),json.dumps({'supported':not bad_review,'values_preserved':True,'within_scope':True})])
    monkeypatch.setattr(transport,'complete',complete)
    monkeypatch.setattr(guard,'check',AsyncMock())
    monkeypatch.setattr(search,'search',AsyncMock(return_value=([doc],'lexical')))
    return complete


def test_multilingual_planner_answer_critic_and_followup_context(monkeypatch):
    complete=model_sequence(monkeypatch)
    context={'history':[{'role':'user','content':'What is a reference range?'},{'role':'assistant','content':'A range printed by a lab.'}], 'report':None}
    result=run(agent.run('ช่วยอธิบายให้ง่ายขึ้น',context,AsyncMock()))
    assert result['action']=='answer' and result['reply'].startswith('ช่วง')
    assert result['sources'][0]['url'].startswith('https://')
    assert complete.call_count==3 and guard.check.call_count==2
    assert complete.call_args_list[0].args[0][1:3]==context['history']
    assert result['state']['history'][-2]['content']=='ช่วยอธิบายให้ง่ายขึ้น'


def test_llm_decides_redirect_without_keyword_router(monkeypatch):
    model_sequence(monkeypatch,refusal=True)
    result=run(agent.run('Write a poem about the moon',{'history':[],'report':None},AsyncMock()))
    assert result['action']=='redirect'
    search.search.assert_not_called()


def test_unsupported_draft_is_not_released(monkeypatch):
    model_sequence(monkeypatch,bad_review=True)
    with pytest.raises(ConversationError,match='verify'): run(agent.run('Question',{},AsyncMock()))
    assert guard.check.call_count==1


def test_missing_evidence_changes_to_clarification(monkeypatch):
    complete=model_sequence(monkeypatch,refusal=True)
    complete.side_effect=[json.dumps({'action':'answer','query':'unknown','language':'English','focus':''}),json.dumps({'reply':'Could you share which test?','evidence_ids':[],'observations':[],'followups':[]}),json.dumps({'supported':True,'values_preserved':True,'within_scope':True})]
    search.search.return_value=([],'lexical')
    result=run(agent.run('unknown',{},AsyncMock()))
    assert result['action']=='clarify' and result['sources']==[]


def test_fake_citation_changed_value_and_nonboolean_review_rejected():
    with pytest.raises(ConversationError): agent.validate_answer(agent.Answer(reply='Hello [invented]',evidence_ids=['invented']),[],None)
    rows=normalize([ReportField(name='ALT',value='30',unit='U/L',reference='0-40')])
    with pytest.raises(ConversationError): agent.validate_answer(agent.Answer(reply='Observation',observations=[agent.Observation(field_id='r1',value='300',unit='U/L',reference='0-40',status='within')]),[],{'fields':rows})
    with pytest.raises(ConversationError): agent.parse_model('{"supported":"true","values_preserved":true,"within_scope":true}',agent.EvidenceReview)


def test_network_disabled_prevents_transport(monkeypatch):
    with pytest.raises(ConversationError,match='not connected'): run(transport.reserve('llm'))


def test_cloud_budget_reserves_atomic_counter_and_fails_exhausted(monkeypatch):
    monkeypatch.setenv('VERCEL','1')
    for key,value in {'PROVIDER_NETWORK_ENABLED':True,'DEMO_ACCESS_CODE':'demo-code-long-enough','UPSTASH_REDIS_REST_URL':'https://redis.example','UPSTASH_REDIS_REST_TOKEN':'test','PROVIDER_BUDGET_CYCLE_ID':'cycle-1','CLOUD_CALL_LIMIT':10}.items(): monkeypatch.setattr(settings,key,value)
    redis=AsyncMock(return_value=1);monkeypatch.setattr(transport,'redis_command',redis)
    run(transport.reserve('guard'))
    cmd=redis.call_args.args[0]
    assert cmd[0]=='EVAL' and cmd[3]=='resultscope:v2:budget:cycle-1'
    assert 'EXPIRE' not in cmd[1] and "HINCRBY" in cmd[1]
    redis.return_value=-1
    with pytest.raises(ConversationError) as error:run(transport.reserve('llm'))
    assert error.value.status==429


def test_provider_http_contract_and_truncation(monkeypatch):
    provider=SimpleNamespace(enabled=True,api_key='test',model='test-model',base_url='https://model.example/v1',timeout_seconds=20,protocol='openai_chat')
    monkeypatch.setattr(transport,'provider_for',lambda _:provider)
    post=AsyncMock(return_value={'choices':[{'message':{'content':'{"action":"social"}'},'finish_reason':'stop'}]})
    monkeypatch.setattr(transport,'post_json',post)
    assert run(transport.complete([{'role':'user','content':'สวัสดี'}],json_mode=True)).startswith('{')
    assert post.call_args.args[2]['response_format']=={'type':'json_object'}
    post.return_value={'choices':[{'message':{'content':'partial'},'finish_reason':'length'}]}
    with pytest.raises(ConversationError):run(transport.complete([]))


def test_bounded_http_response_and_sanitized_error(monkeypatch):
    real_client=httpx.AsyncClient
    calls=[]
    def handler(request):
        calls.append(request)
        return httpx.Response(503,text='secret patient data here')
    monkeypatch.setattr(transport,'reserve',AsyncMock(return_value=None))
    monkeypatch.setattr(transport.httpx,'AsyncClient',lambda **kw:real_client(transport=httpx.MockTransport(handler),**kw))
    with pytest.raises(ConversationError) as exc:run(transport.post_json('https://model.example',{}, {},'llm',10))
    assert len(calls)==1 and 'secret' not in str(exc.value)

@pytest.mark.parametrize('url',['http://example.com','https://x:y@example.com','https://example.com?key=abc','file:///etc/passwd'])
def test_provider_urls_are_fixed_server_https(url):
    with pytest.raises(ConversationError):transport.validate_server_url(url)


def test_demo_assets_and_evaluator_separation():
    c=TestClient(app)
    demos=c.get('/api/v2/demos').json()
    assert len(demos['reports'])==6 and demos['data_class']=='synthetic'
    for report in demos['reports']:
        for fmt in ('png','pdf'):
            response=c.get(report['image' if fmt=='png' else 'pdf'])
            assert response.status_code==200
            assert response.content==routes.demo_path(report['id'],fmt).read_bytes()
    assert c.get('/api/v2/demos/expected_results/json').status_code==404
    assert c.get('/examples/thai_lab_reference_v3/expected_results.json').status_code==404
    assert c.get('/static/../examples/thai_lab_reference_v3/expected_results.json').status_code==404


def test_six_pdf_documents_render_but_combined_pdf_exceeds_limit():
    for rid,*_ in routes.DEMOS:
        pages=reader.document_images(routes.demo_path(rid,'pdf').read_bytes())
        assert len(pages)==1 and pages[0][1]=='image/jpeg'
    with pytest.raises(ConversationError) as exc:reader.document_images((routes.DEMO_ROOT/'Thai_Lab_Reports_Reference_v3_A4.pdf').read_bytes())
    assert exc.value.code=='pdf_page_limit'


def test_vision_reads_pixels_not_answer_key_and_rejects_nonreport(monkeypatch):
    monkeypatch.setattr(settings,'VISION_ENABLED',True)
    monkeypatch.setattr(reader,'provider_for',lambda _:SimpleNamespace(protocol='openai_chat',model='vision-model'))
    complete=AsyncMock(return_value=json.dumps({'document_type':'laboratory_report','fields':[{'name':'ALT','value':'42','unit':'U/L','reference':'0-40'}],'warnings':[]}))
    monkeypatch.setattr(reader,'complete',complete);monkeypatch.setattr(reader,'check',AsyncMock())
    raw=routes.demo_path('01_A_Liver','png').read_bytes()
    result=run(reader.read_report(raw))
    assert result['fields'][0]['value']=='42' and result['confirmed'] is False
    payload=complete.call_args.args[0][0]['content']
    assert payload[1]['image_url']['url'].startswith('data:image/')
    assert 'expected_results' not in json.dumps(payload)
    complete.return_value=json.dumps({'document_type':'other','fields':[],'warnings':[]})
    with pytest.raises(ConversationError):run(reader.read_report(raw))


def test_report_confirmation_is_cookie_bound_and_preserves_corrections(monkeypatch):
    rows=normalize([ReportField(name='ALT',value='42',unit='U/L',reference='0-40')])
    monkeypatch.setattr(routes,'read_report',AsyncMock(return_value={'fields':rows,'warnings':[],'confirmed':False}))
    c=TestClient(app);c.post('/api/v2/session')
    draft=c.post('/api/v2/demos/01_A_Liver/read').json()
    assert draft['report']['data_class']=='synthetic'
    corrected=[{'name':'ALT','value':'32','unit':'U/L','reference':'0-40','printed_flag':''}]
    result=c.post('/api/v2/reports/confirm',json={'draft_token':draft['draft_token'],'fields':corrected})
    assert result.status_code==200 and result.json()['report']['fields'][0]['status']=='within'
    other=TestClient(app);other.post('/api/v2/session')
    assert other.post('/api/v2/reports/confirm',json={'draft_token':draft['draft_token'],'fields':corrected}).status_code==409
    c.post('/api/v2/reset')
    assert c.post('/api/v2/reports/confirm',json={'draft_token':draft['draft_token'],'fields':corrected}).status_code==409


def test_stream_only_sends_final_guarded_answer(monkeypatch):
    model_sequence(monkeypatch)
    c=TestClient(app);c.post('/api/v2/session')
    r=c.post('/api/v2/chat/stream',json={'message':'ช่วยอธิบาย'})
    assert r.status_code==200 and 'text/event-stream' in r.headers['content-type']
    assert r.text.count('event: answer')==1 and 'event: delta' not in r.text
    assert r.text.index('Checking the answer')<r.text.index('event: answer')
    data=[json.loads(x[6:]) for x in r.text.splitlines() if x.startswith('data: ')][-1]
    assert data['state_token'] and 'state' not in data
    model_sequence(monkeypatch,bad_review=True)
    rejected=c.post('/api/v2/chat/stream',json={'message':'Explain'})
    assert 'event: answer' not in rejected.text and 'event: error' in rejected.text


def test_access_origin_body_limit_and_cloud_legacy_block(monkeypatch):
    c=TestClient(app);c.post('/api/v2/session')
    monkeypatch.setattr(settings,'DEMO_ACCESS_CODE','a-demo-code')
    assert c.post('/api/v2/chat',json={'message':'test'}).status_code==401
    assert c.post('/api/v2/chat',json={'message':'test'},headers={'Origin':'https://evil.example','X-ResultScope-Access':'a-demo-code'}).status_code==403
    assert c.post('/api/v2/chat',content='x'*(4*1024*1024+1)).status_code==413
    monkeypatch.setenv('VERCEL','1')
    assert c.post('/api/v1/chat',json={'message':'test'}).status_code==410
    assert c.get('/').status_code==200


def test_model_failure_has_no_exception_or_data_leak(monkeypatch):
    monkeypatch.setattr(agent,'run',AsyncMock(side_effect=RuntimeError('secret patient detail')))
    c=TestClient(app);c.post('/api/v2/session')
    r=c.post('/api/v2/chat',json={'message':'test'})
    assert r.status_code==502 and 'secret' not in r.text
