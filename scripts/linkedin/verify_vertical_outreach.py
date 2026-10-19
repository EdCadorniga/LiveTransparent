"""Non-sending integration checks, including the real n8n external JS runner.

The temporary webhook checks a random request header and only reads account/queue
health. It is removed in a finally block. No real invitation or DM is submitted.
"""
import json
import secrets
import time
import uuid

import requests
from build_vertical_outreach import ACCOUNT, build
from vertical_outreach_ops import BASE, Database, api


def sql_checks():
    with Database() as db:
        result=db.execute("""BEGIN;
DO $$ DECLARE x bigint; n integer; BEGIN
 FOR i IN 1..5 LOOP
   x:=lt_li_reserve_invite('test:lt-vertical-pacing','p:'||i,'c:'||i,'isolated_rollback');
   IF x IS NULL THEN RAISE EXCEPTION 'First five reservations must pass'; END IF;
 END LOOP;
 x:=lt_li_reserve_invite('test:lt-vertical-pacing','p:6','c:6','isolated_rollback');
 IF x IS NOT NULL THEN RAISE EXCEPTION 'Sixth hourly reservation must fail'; END IF;
 x:=lt_li_reserve_invite('test:lt-vertical-pacing','p:1','c:duplicate','isolated_rollback');
 IF x IS NOT NULL THEN RAISE EXCEPTION 'Duplicate identity must fail'; END IF;
 -- Clear only this transaction's test rows, then exercise daily capacity.
 DELETE FROM lt_li_outbound_attempts WHERE account_id='test:lt-vertical-pacing';
 FOR i IN 1..20 LOOP
   INSERT INTO lt_li_outbound_attempts(account_id,identity_key,contact_id,kind,source,reserved_at)
   VALUES('test:lt-vertical-pacing','daily:'||i,'c:'||i,'invite','isolated_rollback',
     ((now() AT TIME ZONE 'America/Los_Angeles')::date::timestamp AT TIME ZONE 'America/Los_Angeles')+interval '1 second');
 END LOOP;
 x:=lt_li_reserve_invite('test:lt-vertical-pacing','daily:21','c:21','isolated_rollback');
 IF x IS NOT NULL THEN RAISE EXCEPTION 'Twenty-first daily reservation must fail'; END IF;
 SELECT count(*) INTO n FROM lt_li_vertical_control WHERE enabled OR dm_enabled;
 IF n<>0 THEN RAISE EXCEPTION 'Non-sending checks require disabled sender controls'; END IF;
END $$;
SELECT 'hourly_daily_identity_caps_passed';
ROLLBACK;""")
        print(result)
        assert db.rows("SELECT count(*)::int AS n FROM lt_li_outbound_attempts WHERE account_id='test:lt-vertical-pacing'")[0]['n']==0
        print('Rollback verified: zero residual test attempts.')


def runner_check():
    wf=build('invite');wf['name']='LT - Vertical LinkedIn Readonly Runner Verification (temporary)'
    path='lt-li-verify-'+str(uuid.uuid4())
    key=secrets.token_urlsafe(32)
    wf['nodes'][0]={'id':str(uuid.uuid4()),'name':'Webhook','type':'n8n-nodes-base.webhook','typeVersion':2,
                    'position':[0,0],'parameters':{'httpMethod':'GET','path':path,'responseMode':'lastNode','options':{}}}
    wf['connections']['Webhook']=wf['connections'].pop('Schedule Trigger')
    assignments=wf['nodes'][1]['parameters']['assignments']['assignments']
    assignments.extend([{'id':'verifyOnly','name':'verifyOnly','type':'boolean','value':True},
                        {'id':'verifySecret','name':'verifySecret','type':'string','value':key}])
    wid=None
    try:
        created=api('POST','/workflows',wf);wid=created['id']
        api('POST','/workflows/'+wid+'/activate')
        time.sleep(2)
        r=requests.get(BASE+'/webhook/'+path,headers={'X-LT-Verify':key},timeout=120)
        if not r.ok or not r.content:raise RuntimeError('Runner verification did not return a populated successful response')
        data=r.json()
        if isinstance(data,list):data=data[0]
        assert data.get('ok') and data.get('verify_only') and data.get('provider_writes')==0
        print('Real runner verification:',json.dumps(data))
        runs=api('GET','/executions?workflowId='+wid+'&limit=5')['data']
        print('Verification executions:',json.dumps([{'id':x['id'],'status':x['status']} for x in runs]))
    finally:
        if wid:
            api('POST','/workflows/'+wid+'/deactivate')
            api('DELETE','/workflows/'+wid)
            print('Temporary verification workflow removed.')


if __name__=='__main__':
    sql_checks();runner_check()
