from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_health():
    r=client.get('/healthz')
    assert r.status_code==200
    assert r.json()['status']=='ok'

def test_idempotency():
    k={'Idempotency-Key':'abc123'}
    payload={'amount_cents':1000,'currency':'USD','card_last4':'4242','merchant_id':'m1'}
    r1=client.post('/charge',headers=k,json=payload)
    r2=client.post('/charge',headers=k,json=payload)
    assert r1.status_code==200 and r2.status_code==200
    assert r1.json()['charge_id']==r2.json()['charge_id']
    assert r2.json()['status'] in ('processed','duplicate')
