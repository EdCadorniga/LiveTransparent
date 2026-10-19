"""Measure real native reporting cache hits; never print payloads/secrets."""
import json
import time
import urllib.request
from repair_v1_facts_sql import api

if __name__=='__main__':
    for path in ('lt-report-executive-summary','lt-report-campaign-channel-summary','lt-report-executive-v1-facts'):
        for i in range(2):
            start=time.monotonic()
            with urllib.request.urlopen('https://automations.livetransparent.com/webhook/'+path+'?from=2026-10-04&to=2026-10-10',timeout=300) as r:
                raw=r.read();data=json.loads(raw)
            print(json.dumps({'path':path,'request':i+1,'seconds':round(time.monotonic()-start,3),'bytes':len(raw),'cache':data.get('cache')}),flush=True)
