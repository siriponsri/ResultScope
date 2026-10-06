"""Configured iApp document OCR adapter, counted against the existing OCR call budget."""
from __future__ import annotations
import asyncio,json,os
import httpx
from services.conversation_transport import ConversationError,reserve,finish

async def transcribe(images):
    key=os.getenv('IAPP_OCR_API_KEY','')
    if not key:raise ConversationError('ocr_setup','Configure IAPP_OCR_API_KEY before using iApp OCR.')
    layout=os.getenv('IAPP_OCR_MODE','text')=='layout';endpoint='layout' if layout else 'ocr';pages=[]
    for n,(raw,mime) in enumerate(images,1):
        reservation=await reserve('vision')
        try:
            async with httpx.AsyncClient(timeout=65,follow_redirects=False) as client:
                async with client.stream('POST','https://api.iapp.co.th/v3/store/ocr/document/'+endpoint,headers={'apikey':key},files={'file':('page.png' if mime=='image/png' else 'page.jpg',raw,mime)}) as response:
                    if response.status_code!=200:raise ConversationError('ocr_rejected','iApp OCR rejected the request. Check the account, key and credits.',502)
                    data=bytearray()
                    async for part in response.aiter_bytes():
                        data.extend(part)
                        if len(data)>1000000:raise ConversationError('ocr_response_large','OCR returned too much data.',502)
                    body=json.loads(data)
            text=body if layout else body.get('text')
            if not isinstance(text,(list,dict,str)):raise ValueError()
            pages.append('Page '+str(n)+'\n'+json.dumps(text,ensure_ascii=False))
            finish(reservation,'succeeded')
        except asyncio.CancelledError:finish(reservation,'failed','cancelled');raise
        except Exception as e:
            finish(reservation,'failed','ocr_failed')
            if isinstance(e,ConversationError):raise
            raise ConversationError('ocr_failed','The document reader could not complete this request.',502) from None
    return '\n\n'.join(pages)
