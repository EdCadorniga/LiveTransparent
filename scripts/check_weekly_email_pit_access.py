"""Check PIT access to the exact date-filtered route observed in native GHL UI."""
import json
import urllib.parse
import urllib.request
from repair_v1_facts_sql import ROOT

env=dict(line.split('=',1) for line in (ROOT/'.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
key=env['GHL_PIT'].strip().strip('"').strip("'")
params=urllib.parse.urlencode({'locationId':'Zwz4relUXVPxx8uohnjV','sourceId':'2e8c2d78-aaec-4591-9b53-b0715be8c4ce','source':'workflow','startDate':'2026-10-04T00:00:00-07:00','endDate':'2026-10-10T23:59:59.999-07:00','groupBy':'createdAt'})
for host in ('https://services.leadconnectorhq.com','https://backend.leadconnectorhq.com'):
    req=urllib.request.Request(host+'/conversations-reporting/emails/aggregate?'+params,headers={'Authorization':'Bearer '+key,'Version':'v3','User-Agent':'Mozilla/5.0','Accept':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=30) as r:data=json.load(r)
        print(json.dumps({'host':host,'status':r.status,'total':data.get('total'),'keys':list(data)}))
    except urllib.error.HTTPError as e:print(json.dumps({'host':host,'status':e.code}))
