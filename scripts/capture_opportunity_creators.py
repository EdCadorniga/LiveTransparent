"""Capture actual creator mechanism via official v3 opportunity.internalSource.

Reports-only upsert. Acquisition fields (Apollo/CSV) are not treated as creators.
"""
import json
import time
import urllib.request
import urllib.error
from repair_v1_facts_sql import ROOT,sql_read,sql_exec

env=dict(line.split('=',1) for line in (ROOT/'.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
key=env['GHL_PIT'].strip().strip('"').strip("'")
headers={'Authorization':'Bearer '+key,'Version':'v3','Accept':'application/json','User-Agent':'Mozilla/5.0'}
def get(path):
    req=urllib.request.Request('https://services.leadconnectorhq.com'+path,headers=headers)
    with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
names={w['id']:w['name'] for w in get('/workflows/?locationId=Zwz4relUXVPxx8uohnjV')['workflows']}
rows=json.loads(sql_read("SELECT json_agg(x) FROM (SELECT DISTINCT source_key AS id FROM report_raw_ghl_opportunities WHERE (COALESCE(NULLIF(dimensions_json->>'source_created_at','')::timestamptz,NULLIF(payload_json->>'createdAt','')::timestamptz,NULLIF(payload_json->>'dateAdded','')::timestamptz,report_date::timestamptz) AT TIME ZONE 'America/Los_Angeles')::date BETWEEN '2026-09-27' AND '2026-10-10') x;"))
sql_exec('CREATE TABLE IF NOT EXISTS v1_opportunity_creator_evidence(opportunity_id text PRIMARY KEY,creator_kind text NOT NULL,workflow_id text,workflow_name text,lookup_status text NOT NULL,captured_at timestamptz NOT NULL DEFAULT NOW());')
q=lambda s:"'"+str(s).replace("'","''")+"'"
cached={r['opportunity_id']:r for r in json.loads(sql_read("SELECT COALESCE(json_agg(x),'[]'::json) FROM v1_opportunity_creator_evidence x;"))}
counts={};pending=[]
for row in rows:
    oid=row['id'];kind='Creation metadata unavailable';wid='';name='';status='unavailable'
    if oid in cached and cached[oid]['lookup_status'] in ('verified','deleted_404','missing_internal_source'):
        saved=cached[oid];label=saved['workflow_name'] or saved['creator_kind'];counts[label]=counts.get(label,0)+1;continue
    try:
        obj=get('/opportunities/'+oid);o=obj.get('opportunity',obj);source=o.get('internalSource') or {}
        sid=str(source.get('id') or '')
        if 'WORKFLOW' in str(source.get('source','')):
            kind='Workflow automation';wid=sid;name=names.get(sid,'Workflow '+sid);status='verified'
        elif source.get('source'):
            kind=str(source['source']);status='verified'
        else:status='missing_internal_source'
    except urllib.error.HTTPError as e:
        status='deleted_404' if e.code==404 else 'lookup_http_'+str(e.code)
        if e.code==404:kind='Deleted record — retained history only'
    pending.append('('+','.join(q(v) for v in (oid,kind,wid,name,status))+',NOW())')
    label=name or kind;counts[label]=counts.get(label,0)+1
    time.sleep(0.1)
if pending:
    sql_exec('INSERT INTO v1_opportunity_creator_evidence(opportunity_id,creator_kind,workflow_id,workflow_name,lookup_status,captured_at) VALUES '+','.join(pending)+' ON CONFLICT(opportunity_id) DO UPDATE SET creator_kind=EXCLUDED.creator_kind,workflow_id=EXCLUDED.workflow_id,workflow_name=EXCLUDED.workflow_name,lookup_status=EXCLUDED.lookup_status,captured_at=NOW();')
print(json.dumps({'opportunities_checked':len(rows),'creators':counts}))
