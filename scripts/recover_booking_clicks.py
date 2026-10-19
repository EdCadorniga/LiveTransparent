"""Recover verified retained booking-click receipts; default read-only manifest.

--apply: insert original receipt-time clicks and add MQL only to verified contacts.
Does not send messages, tag bookings/SQL, delete opportunities, or invent older clicks.
"""
import argparse
import ast
import base64
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime,timezone
from repair_v1_facts_sql import api,sql_read,sql_exec,ROOT

def identity(body):
    cd=body.get('customData') or {}
    if isinstance(cd,str):
        try:cd=json.loads(cd)
        except ValueError:return None
    if body.get('workflow',{}).get('id')!='44e3fa9b-e557-4099-bd74-b308d70f39bb' or cd.get('event')!='booking_link_click':return None
    contact=str(cd.get('contact_id') or body.get('contact_id') or '')
    if not re.fullmatch('[A-Za-z0-9]{15,30}',contact):return None
    url=body.get('contact',{}).get('lastAttributionSource',{}).get('url','')
    try:
        u=urllib.parse.urlsplit(url)
        if u.hostname not in ('services.leadconnectorhq.com','msgsndr.com','services.msgsndr.com'):return None
        token=u.path.rsplit('/',1)[1];parts=token.split('.')
        data=json.loads(base64.urlsafe_b64decode(parts[1]+'='*(-len(parts[1])%4)))
        if data.get('contact_id')!=contact:return None
        return contact,data.get('link_id'),data.get('messageId')
    except (ValueError,IndexError):return None

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');args=p.parse_args()
    path=ROOT/'local-scripts/booking-click-recovery-20261013.json'
    w=api('/api/v1/workflows/1diZyFmTqWQUEny3')
    cfg=next(n for n in w['nodes'] if n['name']=='Config')['parameters']['assignments']['assignments']
    registry=json.loads(next(a['value'] for a in cfg if a['name']=='linkRegistryJson'))
    code=next(n for n in w['nodes'] if n['name']=='Process Click')['parameters']['jsCode']
    verticals={m[0]:ast.literal_eval('['+m[1]+']')[0] for m in re.findall(r"'([A-Za-z0-9]{20})':\s*\[([^\]]+)\]",code)}
    if path.exists():manifest=json.loads(path.read_text())
    else:
        rows=json.loads(sql_read("SELECT COALESCE(json_agg(x),'[]'::json) FROM (SELECT id,\"createdAt\" AS received_at,status FROM execution_entity WHERE \"workflowId\"='1diZyFmTqWQUEny3' AND mode='webhook' AND \"createdAt\">='2026-10-04T07:00:00Z' ORDER BY id) x;",database='n8n'))
        events=[];unmatched=0
        for index,row in enumerate(rows):
            d=api('/api/v1/executions/'+str(row['id'])+'?includeData=true')
            hooks=d.get('data',{}).get('resultData',{}).get('runData',{}).get('Webhook',[])
            if not hooks:unmatched+=1;continue
            b=hooks[0]['data']['main'][0][0]['json'].get('body',{})
            match=identity(b)
            if not match or match[1] not in registry:unmatched+=1;continue
            contact,link,message=match;events.append({'execution_id':row['id'],'contact_id':contact,'link_id':link,'message_id':message,'received_at':row['received_at'],'vertical':verticals[link],**registry[link]})
        manifest={'captured_at':datetime.now(timezone.utc).isoformat(),'basis':'Original n8n webhook receipt createdAt; GHL click workflow identity and matching contact-bound known booking-link tracking URL. Not message sentAt or queue processing time.',
            'receipts_checked':len(rows),'ignored_or_missing_identity':unmatched,'events':events}
        path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'receipts_checked':manifest['receipts_checked'],'known_booking_clicks':len(manifest['events']),'distinct_contacts':len({e['contact_id'] for e in manifest['events']}),'first':min((e['received_at'] for e in manifest['events']),default=None),'last':max((e['received_at'] for e in manifest['events']),default=None)}),flush=True)
    if not args.apply:raise SystemExit(0)
    # Durable dedup of this recovery pass; original receipts are never replayed into automation.
    sql_exec('ALTER TABLE lt_booking_link_clicks ADD COLUMN IF NOT EXISTS source_event_id text; CREATE UNIQUE INDEX IF NOT EXISTS lt_booking_click_recovery_event_idx ON lt_booking_link_clicks(source_event_id) WHERE source_event_id IS NOT NULL;')
    env=dict(line.split('=',1) for line in (ROOT/'.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
    key=env['GHL_PIT'].strip().strip('"').strip("'")
    headers={'Authorization':'Bearer '+key,'Version':'2021-07-28','Accept':'application/json','Content-Type':'application/json','User-Agent':'Mozilla/5.0'}
    def ghl(path,body=None):
        req=urllib.request.Request('https://services.leadconnectorhq.com'+path,data=json.dumps(body).encode() if body else None,headers=headers,method='POST' if body else 'GET')
        with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
    q=lambda x:"'"+str(x).replace("'","''")+"'"
    added=0;already=0;checked={}
    for e in manifest['events']:
        cid=e['contact_id'];source='recovered:n8n:'+str(e['execution_id'])
        if cid not in checked:
            live=ghl('/contacts/'+cid)['contact']
            if live.get('locationId')!='Zwz4relUXVPxx8uohnjV':raise RuntimeError('Contact belongs to another location')
            present=any(str(t).lower()=='mql' for t in live.get('tags',[]))
            if not present:
                result=ghl('/contacts/'+cid+'/tags',{'tags':['mql']})
                if not any(str(t).lower()=='mql' for t in result.get('tags',[])):raise RuntimeError('MQL tag not confirmed')
                added+=1
            else:already+=1
            checked[cid]=present
        values=[cid,e['link_id'],e['name'],e['vertical'],e['utm_source'],e['utm_campaign'],e['utm_medium'],e['received_at'],e['utm_medium'],source]
        sql_exec('INSERT INTO lt_booking_link_clicks(contact_id,link_id,link_name,vertical,utm_source,utm_campaign,medium,clicked_at,utm_medium,source_event_id) VALUES('+','.join(q(v) for v in values)+') ON CONFLICT(source_event_id) WHERE source_event_id IS NOT NULL DO NOTHING;')
        # Backfill qualifying MQL time only for a genuinely missing tag; retain all prior ledger rows.
        if not checked[cid]:
            payload=json.dumps({'backfill':True,'source_event_id':source,'effective_qualification_at':e['received_at'],'applied_at':datetime.now(timezone.utc).isoformat(),'link_id':e['link_id'],'utm_source':e['utm_source'],'utm_medium':e['utm_medium'],'utm_campaign':e['utm_campaign']})
            sql_exec("INSERT INTO mql_tag_events(contact_id,tag,added_at,source,payload_json) VALUES("+q(cid)+",'mql',"+q(e['received_at'])+",'booking_link_click',"+q(payload)+"::jsonb) ON CONFLICT(contact_id,tag) DO UPDATE SET source=EXCLUDED.source,payload_json=EXCLUDED.payload_json,added_at=LEAST(mql_tag_events.added_at,EXCLUDED.added_at) WHERE mql_tag_events.source='ghl_automation' AND mql_tag_events.added_at>NOW()-INTERVAL '2 minutes';")
    print(json.dumps({'mql_tags_added':added,'already_mql':already,'verified_click_receipts_recovered':len(manifest['events'])}))
