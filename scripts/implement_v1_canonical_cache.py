"""Implement canonical V1 metrics and a read-through cache with native refresh.

No CRM writes. --apply publishes reporting workflows after read-only checks.
"""
import argparse
import copy
import json
import pathlib
import subprocess
import os
from datetime import datetime
from repair_v1_facts_sql import api, sql_read, sql_exec, ROOT
from fix_verified_booking_gate import save, parse

CACHE_CODE=r"""
const cfg=$('Report Cache Config').first().json;
const {Client}=require('pg');const pg=new Client({host:'postgres',port:5432,database:'postgres',user:'postgres',password:cfg.pgPassword});
await pg.connect();const outputs=[];
try{for(const item of $input.all()){
 const {startDate,endDate,queryText}=item.json;const key=startDate+'|'+endDate;
 const cached=await pg.query('SELECT payload,computed_at FROM v1_facts_cache WHERE window_key=$1',[key]);
 const row=cached.rows[0];const valid=row?.payload?.metricVersion==='verified-booking-v2';
 const fresh=valid && Date.now()-new Date(row.computed_at).getTime()<3600000;
 let payload;
 if(fresh){payload={...row.payload,cache:{status:'hit',computed_at:row.computed_at}};}
 else {await pg.query('SET jit=off; SET statement_timeout=240000');
   try{const result=await pg.query(queryText,[startDate,endDate]);payload=result.rows[0]?.payload;
     if(!payload?.funnel||payload.window?.from!==startDate||payload.window?.to!==endDate)throw Error('Invalid cache payload');
     await pg.query('INSERT INTO v1_facts_cache(window_key,payload,computed_at) VALUES($1,$2::jsonb,NOW()) ON CONFLICT(window_key) DO UPDATE SET payload=EXCLUDED.payload,computed_at=NOW()',[key,JSON.stringify(payload)]);
     payload={...payload,cache:{status:'refreshed',computed_at:new Date().toISOString()}};
   }catch(error){if(!valid)throw error;payload={...row.payload,cache:{status:'stale',computed_at:row.computed_at}};}
 }
 outputs.push({json:{payload}});
}}finally{await pg.end();}return outputs;
"""

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');args=p.parse_args()
    w=api('/api/v1/workflows/oxYDg6XnRBKhl1Xd');rev=copy.deepcopy(w)
    if any(n['name']=='Report Cache Config' for n in rev['nodes']):
        print('Canonical cache already installed. No repeat mutation; inspect live state before further edits.')
        raise SystemExit(0)
    builder=next(n for n in rev['nodes'] if n['name']=='Build V1 Facts Query')
    code=builder['parameters']['jsCode'];prefix=code.split('const queryText =',1)[0]
    query=code.split('const queryText = `',1)[1].rsplit('`;',1)[0]
    if '_live AS (' in query:
        original=query.split('_live AS (',1)[1].split('), _combined AS',1)[0].strip().rstrip(';')
    else:original=query.strip().rstrip(';')
    canonical='WITH _base AS (\n'+original+'\n),\n'+(ROOT/'reports/embed/executive-v1/canonical-metrics.sql').read_text()
    sql_read('EXPLAIN '+canonical.replace('$1',"'2026-10-04'").replace('$2',"'2026-10-10'")+';')
    print('Canonical full SQL EXPLAIN passed.')
    builder['parameters']['jsCode']=prefix+'const queryText = '+json.dumps(canonical)+';\nreturn [{json:{startDate:from,endDate:to,queryText}}];'
    click=api('/api/v1/workflows/1diZyFmTqWQUEny3')
    cfg=next(n for n in click['nodes'] if n['name']=='Config')
    password=next(a['value'] for a in cfg['parameters']['assignments']['assignments'] if a['name']=='pgPassword')
    config={'name':'Report Cache Config','id':'lt-v1-report-cache-config','type':'n8n-nodes-base.set','typeVersion':3.4,'position':[220,0],
        'parameters':{'assignments':{'assignments':[{'id':'pg','name':'pgPassword','value':password,'type':'string'}]},'includeOtherFields':True,'options':{}}}
    rev['nodes'].append(config)
    webhook=next(n for n in rev['nodes'] if n['type']=='n8n-nodes-base.webhook')['name']
    rev['connections'][webhook]={'main':[[{'node':'Report Cache Config','type':'main','index':0}]]}
    rev['connections']['Report Cache Config']={'main':[[{'node':builder['name'],'type':'main','index':0}]]}
    querynode=next(n for n in rev['nodes'] if n['name']=='Query V1 Facts')
    querynode.update(type='n8n-nodes-base.code',typeVersion=2,parameters={'mode':'runOnceForAllItems','jsCode':CACHE_CODE})
    querynode.pop('credentials',None)
    parse(CACHE_CODE);parse(builder['parameters']['jsCode'])
    for start,end in [('2026-10-04','2026-10-10'),('2026-09-27','2026-10-03')]:
        # Seed once directly in Postgres; this is reporting-only, not an n8n sender execution.
        if args.apply:
            sql_exec("SET jit=off; SET statement_timeout=240000; WITH fresh AS ("+canonical.replace('$1',"'"+start+"'").replace('$2',"'"+end+"'")+
                ") INSERT INTO v1_facts_cache(window_key,payload,computed_at) SELECT '"+start+'|'+end+"',payload,NOW() FROM fresh ON CONFLICT(window_key) DO UPDATE SET payload=EXCLUDED.payload,computed_at=NOW();")
            checks=sql_read("SELECT jsonb_build_object('window',payload->'window','funnel',payload->'funnel','sdrOutputs',payload->'sdrOutputs') FROM v1_facts_cache WHERE window_key='"+start+'|'+end+"';")
            print(checks)
    if args.apply:
        save(w,rev)
        # Native Schedule Trigger, reporting-only SQL refresh. Canonical SQL is captured in code.
        refreshcode=r"""
const cfg=$('Config').first().json;const {Client}=require('pg');const pg=new Client({host:'postgres',port:5432,database:'postgres',user:'postgres',password:cfg.pgPassword});
const sql=SQL_TEXT;
const pacific=new Intl.DateTimeFormat('en-CA',{timeZone:'America/Los_Angeles',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
const date=new Date(pacific+'T00:00:00Z');date.setUTCDate(date.getUTCDate()-date.getUTCDay()-1);
const end=date.toISOString().slice(0,10);date.setUTCDate(date.getUTCDate()-6);const start=date.toISOString().slice(0,10);
function offset(iso,days){const d=new Date(iso+'T00:00:00Z');d.setUTCDate(d.getUTCDate()+days);return d.toISOString().slice(0,10);}
await pg.connect();const out=[];
try{await pg.query('SET jit=off; SET statement_timeout=240000');
 const requested=await pg.query("SELECT window_key FROM v1_facts_cache WHERE window_key ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}\\|[0-9]{4}-[0-9]{2}-[0-9]{2}$' ORDER BY computed_at DESC LIMIT 4");
 const windows=new Set([start+'|'+end,offset(start,-7)+'|'+offset(end,-7),...requested.rows.map(r=>r.window_key)]);
 for(const key of windows){const [from,to]=key.split('|');const result=await pg.query(sql,[from,to]);const payload=result.rows[0]?.payload;
  if(!payload?.funnel||payload.window?.from!==from||payload.window?.to!==to)throw Error('Bad refresh payload');
  await pg.query('INSERT INTO v1_facts_cache(window_key,payload,computed_at) VALUES($1,$2::jsonb,NOW()) ON CONFLICT(window_key) DO UPDATE SET payload=EXCLUDED.payload,computed_at=NOW()',[key,JSON.stringify(payload)]);out.push({json:{window:key,refreshed:true}});
 }}finally{await pg.end();}return out;
""".replace('SQL_TEXT',json.dumps(canonical))
        parse(refreshcode)
        nodes=[{'name':'Hourly Report Refresh','id':'lt-v1-hourly','type':'n8n-nodes-base.scheduleTrigger','typeVersion':1.2,'position':[0,0],'parameters':{'rule':{'interval':[{'field':'cronExpression','expression':'15 * * * *'}]}}},
            {**config,'name':'Config'}, {'name':'Refresh Reporting Cache','id':'lt-cache-refresh','type':'n8n-nodes-base.code','typeVersion':2,'position':[440,0],'parameters':{'mode':'runOnceForAllItems','jsCode':refreshcode}}]
        name='LT - Executive V1 Reporting Cache Refresh'
        exists=next((x for x in api('/api/v1/workflows?limit=250')['data'] if x['name']==name),None)
        body={'name':name,'nodes':nodes,'connections':{'Hourly Report Refresh':{'main':[[{'node':'Config','type':'main','index':0}]]},'Config':{'main':[[{'node':'Refresh Reporting Cache','type':'main','index':0}]]}},'settings':{'executionOrder':'v1','timezone':'America/Los_Angeles','executionTimeout':1200,'saveDataSuccessExecution':'all','saveDataErrorExecution':'all'}}
        if exists:api('/api/v1/workflows/'+exists['id'],'PUT',body);wid=exists['id']
        else:wid=api('/api/v1/workflows','POST',body)['id']
        api('/api/v1/workflows/'+wid+'/activate','POST',{})
        after=api('/api/v1/workflows/'+wid);assert after['active'] and after['versionId']==after['activeVersionId']
        print('Cache refresh published:',wid,after['versionId'])
