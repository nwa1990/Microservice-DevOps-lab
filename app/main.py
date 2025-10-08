from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import hashlib
import time

app = FastAPI(title='Payments API (Demo)', version='0.1.0')
PROCESSED={}
class ChargeRequest(BaseModel):
    amount_cents:int=Field(...,gt=0)
    currency:str=Field(default='USD',min_length=3,max_length=3)
    card_last4:str=Field(...,min_length=4,max_length=4)
    merchant_id:str
    description: Optional[str]=None

@app.get('/healthz')
def healthz():
    return {'status':'ok'}

@app.get('/readyz')
def readyz():
    return {'status':'ready'}

@app.post('/charge')
def charge(req:ChargeRequest, idempotency_key: Optional[str]=Header(default=None)):
    if not idempotency_key:
        raise HTTPException(status_code=400, detail='Missing Idempotency-Key header')
    key=hashlib.sha256(idempotency_key.encode()).hexdigest()
    if key in PROCESSED:
        return {'status':'duplicate','charge_id':PROCESSED[key]['charge_id'],'result':PROCESSED[key]['result']}
    time.sleep(0.2)
    approved = True if req.amount_cents <= 500000 else False
    charge_id = hashlib.md5(f"{req.merchant_id}:{req.amount_cents}:{time.time()}".encode()).hexdigest()[:12]
    result={'approved':approved,'amount_cents':req.amount_cents,'currency':req.currency,'card_last4':req.card_last4,'merchant_id':req.merchant_id,'description':req.description}
    PROCESSED[key]={'charge_id':charge_id,'result':result}
    return {'status':'processed','charge_id':charge_id,'result':result}
