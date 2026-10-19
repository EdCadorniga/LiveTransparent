"""Read documented opportunity creator metadata, not acquisition labels."""
import json
import urllib.request
from repair_v1_facts_sql import ROOT
env=dict(line.split('=',1) for line in (ROOT/'.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
key=env['GHL_PIT'].strip().strip('"').strip("'")
req=urllib.request.Request('https://services.leadconnectorhq.com/opportunities/48gqEAcG7b5mMjrJSX5C',headers={'Authorization':'Bearer '+key,'Version':'v3','Accept':'application/json','User-Agent':'Mozilla/5.0'})
with urllib.request.urlopen(req,timeout=30) as r:data=json.load(r)
o=data.get('opportunity',data)
print(json.dumps({k:v for k,v in o.items() if any(s in k.lower() for s in ('created','source','workflow'))}))
print('Keys:',list(o))
