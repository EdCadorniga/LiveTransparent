"""Add response caching to Summary/Channels without changing source queries."""
import copy
import json
from repair_v1_facts_sql import api
from fix_verified_booking_gate import save, parse

PROBE=r"""
const input=$json,cfg=$('Report Cache Config').first().json;
const key=PREFIX+'|'+input.startDate+'|'+input.endDate;
const headers=$('WEBHOOK').first().json.headers||{};
const forced=String(headers['x-lt-report-refresh-key']||'')===cfg.refreshSecret;
const {Client}=require('pg');const pg=new Client({host:'postgres',port:5432,database:'postgres',user:'postgres',password:cfg.pgPassword,connectionTimeoutMillis:10000});await pg.connect();
try{const r=await pg.query('SELECT payload,computed_at FROM v1_facts_cache WHERE window_key=$1',[key]);const row=r.rows[0];
 const usable=!forced && row?.payload && Object.keys(row.payload).length>3 && Date.now()-new Date(row.computed_at).getTime()<86400000;
 return [{json:{...input,reportCacheKey:key,cacheHit:!!usable,cachedPayload:usable?{...row.payload,cache:{status:Date.now()-new Date(row.computed_at).getTime()<3600000?'hit':'stale',computed_at:row.computed_at}}:null}}];
}finally{await pg.end();}
"""
STORE=r"""
const payload=$json,cfg=$('Report Cache Config').first().json,window=$('NORMALIZE').first().json;
if(!payload||Object.keys(payload).length<4||payload.error)throw Error('Invalid reporting response; not cached');
const {Client}=require('pg');const pg=new Client({host:'postgres',port:5432,database:'postgres',user:'postgres',password:cfg.pgPassword});await pg.connect();
try{await pg.query('INSERT INTO v1_facts_cache(window_key,payload,computed_at) VALUES($1,$2::jsonb,NOW()) ON CONFLICT(window_key) DO UPDATE SET payload=EXCLUDED.payload,computed_at=NOW()', [PREFIX+'|'+window.startDate+'|'+window.endDate,JSON.stringify(payload)]);}finally{await pg.end();}
return [{json:{...payload,cache:{status:'refreshed',computed_at:new Date().toISOString()}}}];
"""

if __name__=='__main__':
    refresh=api('/api/v1/workflows/kBuW8Uq3EOJFQKNF')
    vals=next(n for n in refresh['nodes'] if n['name']=='Config')['parameters']['assignments']['assignments']
    password=next(a['value'] for a in vals if a['name']=='pgPassword');secret=next(a['value'] for a in vals if a['name']=='refreshSecret')
    jobs=[('Bukc0mgOD2r7V6ED','summary','Webhook Intake','Normalize Request','Build Query','Shape Response','Respond to Webhook'),
        ('MvPLbUAN9IIQikxb','channels','Campaign Summary Webhook','Normalize Campaign Window','Campaign Channel Query','Shape Campaign Response','Respond Campaign Summary')]
    for wid,prefix,webhook,normalize,build,shape,respond in jobs:
        w=api('/api/v1/workflows/'+wid);rev=copy.deepcopy(w)
        if any(n['name']=='Report Cache Config' for n in w['nodes']):print('Already cached:',wid);continue
        cfg={'name':'Report Cache Config','id':'lt-'+prefix+'-cache-config','type':'n8n-nodes-base.set','typeVersion':3.4,'position':[500,-200],
            'parameters':{'assignments':{'assignments':[{'id':'pg','name':'pgPassword','type':'string','value':password},{'id':'refresh','name':'refreshSecret','type':'string','value':secret}]},'includeOtherFields':True,'options':{}}}
        probe=PROBE.replace('PREFIX',json.dumps(prefix)).replace('WEBHOOK',webhook)
        store=STORE.replace('PREFIX',json.dumps(prefix)).replace('NORMALIZE',normalize)
        parse(probe);parse(store)
        rev['nodes'].extend([cfg,
            {'name':'Read Report Cache','id':'lt-'+prefix+'-cache-read','type':'n8n-nodes-base.code','typeVersion':2,'position':[720,-200],'parameters':{'mode':'runOnceForAllItems','jsCode':probe}},
            {'name':'Report Cache Hit?','id':'lt-'+prefix+'-cache-if','type':'n8n-nodes-base.if','typeVersion':2.2,'position':[940,-200],
                'parameters':{'conditions':{'combinator':'and','options':{'caseSensitive':True,'typeValidation':'strict','version':2},'conditions':[{'leftValue':'={{ String($json.cacheHit) }}','rightValue':'true','operator':{'type':'string','operation':'equals'}}]},'options':{}}},
            {'name':'Return Cached Report','id':'lt-'+prefix+'-cache-return','type':'n8n-nodes-base.code','typeVersion':2,'position':[1160,-400],'parameters':{'mode':'runOnceForAllItems','jsCode':'return [{json:$json.cachedPayload}];'}},
            {'name':'Store Report Cache','id':'lt-'+prefix+'-cache-store','type':'n8n-nodes-base.code','typeVersion':2,'position':[1160,200],'parameters':{'mode':'runOnceForAllItems','jsCode':store}}])
        def edge(a,b):rev['connections'][a]={'main':[[{'node':b,'type':'main','index':0}]]}
        edge(normalize,'Report Cache Config');edge('Report Cache Config','Read Report Cache');edge('Read Report Cache','Report Cache Hit?')
        rev['connections']['Report Cache Hit?']={'main':[[{'node':'Return Cached Report','type':'main','index':0}],[{'node':build,'type':'main','index':0}]]}
        edge('Return Cached Report',respond);edge(shape,'Store Report Cache');edge('Store Report Cache',respond)
        save(w,rev)
    # Read-only refresh service invokes only the two reporting APIs, with a protected bypass header.
    name='LT - Executive Summary and Channels Cache Refresh'
    code=r"""
const cfg=$('Config').first().json;
if($json.headers && String($json.headers['x-lt-report-refresh-key']||'')!==cfg.refreshSecret)return [{json:{ok:false,error:'unauthorized'}}];
const now=new Intl.DateTimeFormat('en-CA',{timeZone:'America/Los_Angeles',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
const d=new Date(now+'T00:00:00Z');d.setUTCDate(d.getUTCDate()-d.getUTCDay()-1);const to=d.toISOString().slice(0,10);d.setUTCDate(d.getUTCDate()-6);const from=d.toISOString().slice(0,10);
function offset(iso,days){const d=new Date(iso+'T00:00:00Z');d.setUTCDate(d.getUTCDate()+days);return d.toISOString().slice(0,10);}
const out=[];
for(const [start,end] of [[from,to],[offset(from,-7),offset(to,-7)]]){
 for(const path of ['lt-report-executive-summary','lt-report-campaign-channel-summary']){
  const result=await this.helpers.httpRequest({method:'GET',url:'https://automations.livetransparent.com/webhook/'+path+'?from='+start+'&to='+end,headers:{'x-lt-report-refresh-key':cfg.refreshSecret},json:true,timeout:240000});
  if(!result||Object.keys(result).length<4)throw Error('Invalid reporting refresh');out.push({json:{path,from:start,to:end,refreshed:true}});
 }}return out;
"""
    parse(code)
    nodes=[{'name':'Hourly Source Cache Refresh','id':'source-cache-clock','type':'n8n-nodes-base.scheduleTrigger','typeVersion':1.2,'position':[0,0],'parameters':{'rule':{'interval':[{'field':'cronExpression','expression':'25 * * * *'}]}}},
        {'name':'Protected Source Refresh','id':'source-cache-hook','type':'n8n-nodes-base.webhook','typeVersion':1.1,'position':[0,200],'parameters':{'httpMethod':'POST','path':'lt-report-source-cache-refresh','responseMode':'onReceived','options':{}}},
        {'name':'Config','id':'source-cache-config','type':'n8n-nodes-base.set','typeVersion':3.4,'position':[220,0],'parameters':{'assignments':{'assignments':[{'id':'refresh','name':'refreshSecret','type':'string','value':secret}]},'includeOtherFields':True,'options':{}}},
        {'name':'Refresh Summary and Channels','id':'source-cache-refresh','type':'n8n-nodes-base.code','typeVersion':2,'position':[440,0],'parameters':{'mode':'runOnceForAllItems','jsCode':code}}]
    body={'name':name,'nodes':nodes,'connections':{'Hourly Source Cache Refresh':{'main':[[{'node':'Config','type':'main','index':0}]]},'Protected Source Refresh':{'main':[[{'node':'Config','type':'main','index':0}]]},'Config':{'main':[[{'node':'Refresh Summary and Channels','type':'main','index':0}]]}},'settings':{'executionOrder':'v1','timezone':'America/Los_Angeles','saveDataSuccessExecution':'all','saveDataErrorExecution':'all','executionTimeout':1200}}
    existing=next((x for x in api('/api/v1/workflows?limit=250')['data'] if x['name']==name),None)
    if existing:wid=existing['id'];api('/api/v1/workflows/'+wid,'PUT',body)
    else:wid=api('/api/v1/workflows','POST',body)['id']
    api('/api/v1/workflows/'+wid+'/activate','POST',{})
    after=api('/api/v1/workflows/'+wid);assert after['active'] and after['versionId']==after['activeVersionId']
    print('Source cache refresher published:',wid,after['versionId'])
