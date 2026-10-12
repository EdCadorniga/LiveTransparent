"""Reconcile report-only snapshots and validate/publish the V1 SDR facts extension."""
import argparse
import json
import os
import pathlib
from datetime import datetime
from repair_v1_facts_sql import api, sql_read, ROOT

def reconcile_email():
    logs = json.loads((ROOT/'local-scripts/vertical-campaign-log-audit-20261013.json').read_text())
    export = json.loads((ROOT/'local-scripts/vertical-email-message-export-20261013.json').read_text())
    assert export['complete']
    index = {r['id']:r for r in export['rows']}
    assert len(index)==len(export['rows'])
    seen = set()
    rows = []
    for s in logs['sources']:
        if s['actionType']!='email':
            continue
        assert s['complete']
        queued = [r for r in s['rows'] if r.get('queuedSuccessfully')]
        for r in queued:
            e = index[r['messageId']]
            assert e['contactId']==r['contactId'] and e['direction']=='outbound' and e['status']=='sent'
            assert r['messageId'] not in seen
            seen.add(r['messageId'])
            delta=abs((datetime.fromisoformat(e['dateAdded'].replace('Z','+00:00'))-datetime.fromisoformat(r['emailQueuedAt'].replace('Z','+00:00'))).total_seconds())
            assert delta<120, (s['label'],delta)
        sms=next(x for x in logs['sources'] if x['label']==s['label'] and x['actionType']=='webhook')
        rows.append({'campaign':s['label']+' Multi-Channel Outbound — Oct 2026', 'vertical':s['label'], 'workflow_id':s['key'].split('|')[0],
            'sent':len(queued),'queued':len(queued),'errors':sum(r['status']=='error' for r in s['rows']),
            'skipped':sum(r['status']=='skipped' for r in s['rows']),
            'delivered':None,'opened':None,'clicked':None,'replied':None,'bounced':None,
            'sms_attempts':len(sms['rows']), 'sms_unauthorized':sum(r.get('outcome')=='unauthorized' for r in sms['rows']),
            'sms_timeouts':sum(r.get('outcome')=='timeout' for r in sms['rows']),
            'sms_sent':None,'sms_delivered':None})
    assert len(seen)==1501
    return {'window':logs['window'],'complete':True,'basis':'Exact queue-message ID + contact ID + timestamp join to supported GHL Email export; outbound status sent. Delivery/engagement unavailable.', 'rows':rows,'matched_sent':len(seen)}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');p.add_argument('--snapshot',action='store_true');args=p.parse_args()
    snapshot=reconcile_email()
    print(json.dumps({'email_exact_sent':snapshot['matched_sent'],'campaigns':snapshot['rows']}))
    if args.snapshot:
        (ROOT/'reports/embed/executive-v1/vertical-campaign-evidence.json').write_text(json.dumps(snapshot,indent=2),encoding='utf-8')
    w=api('/api/v1/workflows/oxYDg6XnRBKhl1Xd')
    print(json.dumps({'active':w['active'],'version':w['versionId'],'published':w.get('activeVersionId')}))
    n=next(n for n in w['nodes'] if n['name']=='Build V1 Facts Query')
    code=n['parameters']['jsCode']
    if 'sdr_output_rows AS' not in code:
        at=code.rfind('\nSELECT jsonb_build_object(')
        assert at>=0
        code=code[:at]+',\n'+(ROOT/'reports/embed/executive-v1/lt-exec-v1-sdr-outputs.sql').read_text()+code[at:]
        code=code.replace("'verticalPerformance',", "'sourceBreakdown', (SELECT jsonb_agg(to_jsonb(s) ORDER BY source) FROM band_source_rows s),\n  'sdrOutputs', (SELECT jsonb_agg(to_jsonb(s) ORDER BY owner_name) FROM sdr_output_rows s),\n  'verticalPerformance',",1)
    query=code.split('const queryText = `',1)[1].rsplit('`;',1)[0]
    sql_read('EXPLAIN '+query.replace('$1',"'2026-10-04'").replace('$2',"'2026-10-10'"))
    for start,end in [('2026-10-04','2026-10-10'),('2026-09-27','2026-10-03')]:
        f=json.loads(sql_read(query.replace('$1',"'"+start+"'").replace('$2',"'"+end+"'")))
        rows=f['sdrOutputs'];totals={k:sum(r[k] for r in rows) for k in ('mqls','sqls','booked','converted')}
        assert totals['mqls']==f['funnel']['mqls_entered']
        assert totals['sqls']==f['funnel']['sqls_entered']
        assert totals['booked']==f['meetingSummary']['unique_contacts']
        for metric in ('opportunities','mqls','sqls'):
            assert sum(r[metric] for r in f['sourceBreakdown'])==f['funnel'][{'opportunities':'opportunities_created','mqls':'mqls_entered','sqls':'sqls_entered'}[metric]]
        print(json.dumps({'window':[start,end],'outputs':rows,'totals':totals}))
    if args.apply and code!=n['parameters']['jsCode']:
        backup=pathlib.Path(os.environ['LOCALAPPDATA'])/'Temp/opencode'
        assert backup.is_dir()
        (backup/f'v1-before-band-outputs-{datetime.now():%Y%m%dT%H%M%S}.json').write_text(json.dumps(w))
        n['parameters']['jsCode']=code
        settings={k:v for k,v in w['settings'].items() if k!='availableInMCP'}
        api('/api/v1/workflows/'+w['id'],'PUT',{k:w[k] for k in ('name','nodes','connections')}|{'settings':settings})
        after=api('/api/v1/workflows/'+w['id'])
        if after['versionId']!=after.get('activeVersionId'):
            api('/api/v1/workflows/'+w['id']+'/activate','POST',{})
            after=api('/api/v1/workflows/'+w['id'])
        assert after['active'] and after['versionId']==after['activeVersionId']
        assert next(x for x in after['nodes'] if x['name']==n['name'])['parameters']['jsCode']==code
        print(json.dumps({'published_version':after['versionId']}))
