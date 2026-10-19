"""Read-only native GHL form workflow inventory, credentials never printed."""
import json
import urllib.request
from repair_v1_facts_sql import ROOT

env=dict(line.split('=',1) for line in (ROOT/'.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
key=env['GHL_PIT'].strip().strip('"').strip("'")
req=urllib.request.Request('https://services.leadconnectorhq.com/workflows/?locationId=Zwz4relUXVPxx8uohnjV',headers={'Authorization':'Bearer '+key,'Version':'v3','User-Agent':'Mozilla/5.0','Accept':'application/json'})
with urllib.request.urlopen(req,timeout=30) as r:data=json.load(r)
for w in data['workflows']:
    if any(s in w['name'].lower() for s in ('form','linkedin','webinar','checklist')):
        print(json.dumps({k:w.get(k) for k in ('id','name','status','version')}))
