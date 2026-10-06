"""Offline UI harness ONLY. Never deploy. Model/OCR doubles; real business routes and DB."""
import os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from datetime import datetime,timedelta
from main import app
from routers import business as b
from services import business_store as db
from services.lab_fields_v2 import normalize,ReportField
from config import settings
settings.PROVIDER_NETWORK_ENABLED=False
b.provider_authorize=lambda request:None
b.request_rate_limiter.allow=lambda request:True
async def agent(message,context):
    # Explicit test double, not product routing or an LLM quality evaluation.
    if message=='UI_TEST_BOOK':
        day=datetime.now(b.TZ)+timedelta(days=3)
        while day.weekday()==6:day+=timedelta(days=1)
        return {'reply':'Offline UI test double: please review your appointment.','sources':[],'action':{'type':'book','quote':db.quote(['P02']),'branch_id':'BKK01','date':day.strftime('%Y-%m-%d'),'time':'09:00'}}
    return {'reply':'Offline UI test double: your question was received.','sources':[],'action':None}
b.business_agent.run=agent
async def read(raw):
    return {'fields':normalize([ReportField(name='Glucose',value='100',unit='mg/dL',reference='70–99',printed_flag='H')]),'warnings':['OFFLINE UI TEST DOUBLE — not measured OCR output.'],'confirmed':False}
b.read_report=read
with db.transaction() as tx:
    uid='ui_test_manager';tx.put(uid,'user',uid,{'email':'staff@example.invalid','password':db.password_hash('ui-test-only-password'),'role':'manager','branch':'BKK01'})
    tx.put('email_'+db.digest('staff@example.invalid'),'email',uid,{})
if __name__=='__main__':
    import uvicorn
    uvicorn.run(app,host='127.0.0.1',port=int(os.getenv('UI_TEST_PORT','8098')),log_level='error')
