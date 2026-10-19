"""Install a protected reporting-only refresh trigger and verify its execution."""
import copy
import json
import secrets
import time
import urllib.request
from repair_v1_facts_sql import api
from fix_verified_booking_gate import save, parse

wid='kBuW8Uq3EOJFQKNF'
w=api('/api/v1/workflows/'+wid);rev=copy.deepcopy(w)
cfg=next(n for n in rev['nodes'] if n['name']=='Config')
assignments=cfg['parameters']['assignments']['assignments']
secret=next((a for a in assignments if a['name']=='refreshSecret'),None)
if not secret:
    secret={'id':'cache-refresh-key','name':'refreshSecret','type':'string','value':secrets.token_urlsafe(32)};assignments.append(secret)
if not any(n['name']=='Protected Cache Refresh' for n in rev['nodes']):
    rev['nodes'].append({'name':'Protected Cache Refresh','id':'lt-cache-refresh-hook','type':'n8n-nodes-base.webhook','typeVersion':1.1,'position':[0,220],
        'parameters':{'httpMethod':'POST','path':'lt-exec-v1-cache-refresh','responseMode':'onReceived','options':{}}})
    rev['connections']['Protected Cache Refresh']={'main':[[{'node':'Config','type':'main','index':0}]]}
n=next(n for n in rev['nodes'] if n['name']=='Refresh Reporting Cache')
if 'refresh_unauthorized' not in n['parameters']['jsCode']:
    n['parameters']['jsCode']=n['parameters']['jsCode'].replace("const cfg=$('Config').first().json;", "const cfg=$('Config').first().json;\nif($json.headers && String($json.headers['x-lt-report-refresh-key']||'')!==cfg.refreshSecret)return [{json:{ok:false,error:'refresh_unauthorized'}}];",1)
    # Bound each runner task to the two canonical completed weeks.
    n['parameters']['jsCode']=n['parameters']['jsCode'].replace('for(const key of windows)', 'for(const key of [...windows].slice(0,2))')
parse(n['parameters']['jsCode'])
if rev!=w:save(w,rev)
req=urllib.request.Request('https://automations.livetransparent.com/webhook/lt-exec-v1-cache-refresh',data=b'{}',method='POST',
    headers={'Content-Type':'application/json','x-lt-report-refresh-key':secret['value']})
with urllib.request.urlopen(req,timeout=30) as r:print('Refresh accepted:',r.status)
for _ in range(100):
    rows=api('/api/v1/executions?workflowId='+wid+'&limit=3')['data']
    latest=rows[0] if rows else {}
    status=latest.get('status');print(json.dumps({'execution':latest.get('id'),'status':status}))
    if status in ('success','error','crashed','canceled'):
        if status!='success':raise RuntimeError('Reporting refresh did not succeed')
        break
    time.sleep(5)
else:raise RuntimeError('Reporting refresh completion not observed')
