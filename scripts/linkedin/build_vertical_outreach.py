"""Build the two vertical LinkedIn workflows on n8n-lt only.

Default is local validation. --deploy creates inactive workflows and additive tables.
--enable is a separate, explicitly requested launch, gated on both LinkedIn products.
There is no implicit execution of a send workflow.
"""
import argparse
import json
import subprocess
import uuid
from pathlib import Path

import requests
from vertical_outreach_ops import ROOT, ENV, Database, api

HERE = Path(__file__).resolve().parent
ACCOUNT = 'V9eiHiDpRmCtan0YNdzsQw'
V2_ACCOUNT = 'acc_01m3sefk22e8jvnmvvfx333pye'
LOCATION = 'Zwz4relUXVPxx8uohnjV'
OLD_SENDERS = ('fXxw5lanZcDmUrst','crKIsaL5k3YBfqDZ','Zt8p2aYtIuY0HK18',
               'd0tEtijajisIsYcs','nspggypNF245xzeL','pq7XVajNFnnwMUTr')
REGISTRY = json.loads((HERE / 'vertical_messages.json').read_text(encoding='utf-8'))
NAMES = {'invite':'LT - Vertical LinkedIn Connection Dispatcher',
         'dm':'LT - Vertical LinkedIn Sales Navigator DM Sequence'}


def seed_sql():
    registry = [{'vertical':v,'vertical_index':i,'tag':'lt_campaign_'+REGISTRY['messages'][v]['slug']+'_brands_oct_2026_enroll'}
                for i,v in enumerate(REGISTRY['order'])]
    values = json.dumps(registry).replace("'", "''")
    return f"""
WITH registry AS (SELECT * FROM jsonb_to_recordset('{values}'::jsonb) AS x(vertical text,vertical_index int,tag text)),
latest AS (
 SELECT DISTINCT ON (payload_json->>'id') payload_json AS c,loaded_at
 FROM report_raw_ghl_contacts
 WHERE loaded_at>now()-interval '3 days'
 ORDER BY payload_json->>'id',loaded_at DESC,id DESC
), cohort AS (
 SELECT c->>'id' AS contact_id,r.vertical,r.vertical_index,i.normalized_profile_slug AS slug,
   count(*) OVER(PARTITION BY i.normalized_profile_slug) AS identities,
   count(*) OVER(PARTITION BY c->>'id') AS contact_rows
 FROM latest l JOIN registry r ON l.c->'tags' ? r.tag
 JOIN linkedin_contact_profile_index i ON i.ghl_contact_id=l.c->>'id'
 WHERE l.c->>'locationId'='{LOCATION}' AND nullif(i.normalized_profile_slug,'') IS NOT NULL
   AND EXISTS(SELECT 1 FROM jsonb_array_elements(l.c->'customFields') f
     WHERE f->>'id'='ODs8fBt5te5HEfSJ91pY' AND f->>'value'=r.vertical)
), eligible AS (
 SELECT * FROM cohort q WHERE identities=1 AND contact_rows=1
 AND NOT EXISTS(SELECT 1 FROM linkedin_contact_profile_index i WHERE i.normalized_profile_slug=q.slug AND i.ghl_contact_id<>q.contact_id)
 AND NOT EXISTS(SELECT 1 FROM linkedin_invitation_withdrawals w WHERE w.dispatcher_hold AND
   (w.ghl_contact_id=q.contact_id OR w.candidate_contact_ids ? q.contact_id OR lower(w.invited_user_public_id)=q.slug))
)
INSERT INTO lt_li_vertical_queue(contact_id,account_id,vertical,vertical_index,profile_slug)
SELECT contact_id,'{ACCOUNT}',vertical,vertical_index,slug FROM eligible
ON CONFLICT(contact_id) DO UPDATE SET refreshed_at=now()
WHERE lt_li_vertical_queue.vertical=excluded.vertical AND lt_li_vertical_queue.profile_slug=excluded.profile_slug;
"""


def config(mode, secrets=True):
    values = {'workflowName':NAMES[mode], 'locationId':LOCATION,'accountId':ACCOUNT,
              'v2AccountId':V2_ACCOUNT,'ghlBase':'https://services.leadconnectorhq.com',
              'classicBase':ENV['UNIPILE_API_BASE_URL'].rstrip('/'),
              'v2Base':'https://api.unipile.com/v2',
              'bookingBase':'https://api.leadconnectorhq.com/widget/booking/SrtXcFVyea7pFl3nTiIK',
              'ghlApiKey':ENV['GHL_PIT'],'unipileApiKey':ENV['UNIPILE_TOKEN'],
              'unipileV2ApiKey':ENV['UNIPILE_v2_MIGRATION_SERVICE_API_KEY'],
              'pgPassword':ENV['POSTGRES_PASSWORD']}
    if not secrets:
        for key in ('ghlApiKey','unipileApiKey','unipileV2ApiKey','pgPassword'):
            values[key]='<runtime-only>'
    return {'mode':'manual','assignments':{'assignments':[
        {'id':key,'name':key,'type':'string','value':value} for key,value in values.items()]},'options':{}}


def build(mode, secrets=True):
    runtime = (HERE/'vertical_runtime.js').read_text(encoding='utf-8')
    source = 'const MODE='+json.dumps(mode)+';\nconst MESSAGES='+json.dumps(REGISTRY)+';\nconst SEED_SQL='+json.dumps(seed_sql())+';\n'+runtime
    nodes = [
        {'id':str(uuid.uuid4()),'name':'Schedule Trigger','type':'n8n-nodes-base.scheduleTrigger','typeVersion':1.2,
         'position':[0,0],'parameters':{'rule':{'interval':[{'field':'cronExpression','expression':'*/15 9-16 * * 1-5'}]}}},
        {'id':str(uuid.uuid4()),'name':'Config','type':'n8n-nodes-base.set','typeVersion':3.4,
         'position':[240,0],'parameters':config(mode,secrets)},
        {'id':str(uuid.uuid4()),'name':'Dispatch One Invite' if mode=='invite' else 'Verify Acceptance and Send Due DMs',
         'type':'n8n-nodes-base.code','typeVersion':2,'position':[500,0],
         'parameters':{'mode':'runOnceForAllItems','jsCode':source}},
    ]
    return {'name':NAMES[mode],'nodes':nodes,
            'connections':{'Schedule Trigger':{'main':[[{'node':'Config','type':'main','index':0}]]},
                           'Config':{'main':[[{'node':nodes[2]['name'],'type':'main','index':0}]]}},
            'settings':{'executionOrder':'v1','timezone':'America/Los_Angeles',
                        'executionTimeout':240,'saveDataSuccessExecution':'all',
                        'saveDataErrorExecution':'all','saveManualExecutions':False}}


def inventory():
    rows=[]; cursor=None
    while True:
        suffix='?limit=100'+('&cursor='+requests.utils.quote(cursor) if cursor else '')
        data=api('GET','/workflows'+suffix);rows.extend(data['data']);cursor=data.get('nextCursor')
        if not cursor:return rows


def validate_local():
    for v,row in REGISTRY['messages'].items():
        for kind in ('invite','dm1','dm2'):
            text=row[kind]
            assert text.isascii() and "'" not in text and '\\' not in text,(v,kind)
            assert '{first_name}' in text,(v,kind)
    for mode in NAMES:
        wf=build(mode,False)
        js=wf['nodes'][2]['parameters']['jsCode']
        result=subprocess.run(['node','-e',"const fs=require('fs');new (Object.getPrototypeOf(async function(){}).constructor)(fs.readFileSync(0,'utf8'));console.log('parse passed')"],
                              input=js,text=True,capture_output=True)
        if result.returncode:raise RuntimeError(result.stderr)
        assert len(wf['nodes'])==3 and len(wf['connections'])==2
    print('Local validation: 24 ASCII/apostrophe-free templates; both Code nodes parse; graph structure passed.')


def deploy(enable=False):
    validate_local()
    for wid in OLD_SENDERS:
        w=api('GET','/workflows/'+wid)
        if w.get('active') or w.get('activeVersionId'):raise RuntimeError('Old LinkedIn sender must stay unpublished: '+wid)
    with Database() as db:
        db.execute('BEGIN;\n'+(HERE/'vertical_outreach.sql').read_text(encoding='utf-8')+
                   f"\nINSERT INTO lt_li_vertical_control(account_id) VALUES('{ACCOUNT}') ON CONFLICT DO NOTHING;\n"+
                   seed_sql()+'\nCOMMIT;')
        counts=db.rows('SELECT vertical,status,count(*) FROM lt_li_vertical_queue GROUP BY 1,2 ORDER BY 1,2')
        print('queue',json.dumps(counts))
    rows=inventory();ids={}
    for mode,name in NAMES.items():
        matches=[w for w in rows if w['name']==name]
        if len(matches)>1:raise RuntimeError('Duplicate vertical workflows; reconcile before deployment')
        if matches:
            w=api('GET','/workflows/'+matches[0]['id'])
            if w['active']:raise RuntimeError('Do not overwrite an active sender')
            # Local-only pre-edit backup, including restricted Config secrets.
            backup=ROOT/'local-scripts'/('vertical-pre-edit-'+w['id']+'.json')
            if not backup.exists():backup.write_text(json.dumps(w),encoding='utf-8')
            result=api('PUT','/workflows/'+w['id'],build(mode))
        else:
            result=api('POST','/workflows',build(mode))
        wid=result['id'];readback=api('GET','/workflows/'+wid)
        assert readback['active'] is False and not readback.get('activeVersionId')
        assert readback['nodes'][2]['parameters']['jsCode']==build(mode)['nodes'][2]['parameters']['jsCode']
        ids[mode]=wid
    if enable:
        r=requests.get('https://api.unipile.com/v2/accounts/'+V2_ACCOUNT,
                       headers={'X-API-KEY':ENV['UNIPILE_v2_MIGRATION_SERVICE_API_KEY']},timeout=30)
        r.raise_for_status();products=r.json().get('metadata',{}).get('products_connection_status',{})
        if any(products.get(k)!='running' for k in ('classic','sales_navigator')):
            raise RuntimeError('Drafts saved, but launch blocked: Classic and Sales Navigator must both be running')
        with Database() as db:
            db.execute(f"UPDATE lt_li_vertical_control SET enabled=true,dm_enabled=true,stopped_reason=NULL WHERE account_id='{ACCOUNT}'")
        for wid in ids.values():
            api('POST','/workflows/'+wid+'/activate')
            w=api('GET','/workflows/'+wid)
            assert w['active'] and w['versionId']==w['activeVersionId']
    print(json.dumps({'workflows':ids,'activated':enable},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--deploy',action='store_true');parser.add_argument('--enable',action='store_true')
    args=parser.parse_args()
    if args.enable and not args.deploy:parser.error('--enable requires --deploy')
    deploy(args.enable) if args.deploy else validate_local()
