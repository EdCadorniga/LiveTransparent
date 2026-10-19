"""Harden and publish the existing all-vertical form MQL ingest receiver."""
import copy
import json
import secrets
import subprocess
from repair_v1_facts_sql import api
from fix_verified_booking_gate import save, parse

CODE=r"""
const cfg=$('Config').first().json;const src=$('Webhook').first().json;
const h=Object.fromEntries(Object.entries(src.headers||{}).map(([k,v])=>[k.toLowerCase(),String(v)]));
if(!cfg.ingestSecret||h['x-lt-mql-ingest-key']!==cfg.ingestSecret)return [{json:{ok:false,status:403,error:'unauthorized'}}];
const body=src.body||{};const id=String(body.contact_id||body.contactId||'').trim();const source=String(body.form_source||'').trim();
if(!/^[a-zA-Z0-9]{15,30}$/.test(id)||!['ghl_form','linkedin_form','meta_form'].includes(source))return [{json:{ok:false,status:400,error:'invalid_contact_or_form_source'}}];
const headers={Authorization:'Bearer '+cfg.ghlApiKey,Version:'2021-07-28',Accept:'application/json','Content-Type':'application/json'};
try{
 const result=await this.helpers.httpRequest({method:'POST',url:'https://services.leadconnectorhq.com/contacts/'+encodeURIComponent(id)+'/tags',headers,body:{tags:['mql']},json:true,timeout:20000});
 if(!result||(!Array.isArray(result.tags)&&!result.contact))throw Error('tag_response_unrecognized');
 const {Client}=require('pg');const pg=new Client({host:'postgres',port:5432,database:'postgres',user:'postgres',password:cfg.pgPassword});await pg.connect();
 try{await pg.query("INSERT INTO mql_tag_events(contact_id,tag,added_at,source,payload_json) VALUES($1,'mql',NOW(),$2,$3::jsonb) ON CONFLICT(contact_id,tag) DO NOTHING",[id,source,JSON.stringify({form_id:body.form_id||null,form_name:body.form_name||null,submission_id:body.submission_id||null,vertical:body.vertical||null})]);}finally{await pg.end();}
 return [{json:{ok:true,status:200,contact_id:id,source,tag:'mql'}}];
}catch(error){return [{json:{ok:false,status:502,error:'mql_apply_or_ledger_failed'}}];}
"""

if __name__=='__main__':
    harness=r"""
const fn=new (Object.getPrototypeOf(async function(){}).constructor)('$','require',CODE);
(async()=>{for(const [source,key,expected] of [['ghl_form','test',200],['linkedin_form','test',200],['meta_form','test',200],['other','test',400],['ghl_form','bad',403]]){
let calls=0;const $=name=>({first:()=>({json:name==='Config'?{ingestSecret:'test',ghlApiKey:'mock',pgPassword:'mock'}:{headers:{'x-lt-mql-ingest-key':key},body:{contact_id:'Abcdefghijklmnopqrst',form_source:source}}})});
class Client{async connect(){} async end(){} async query(){}}
const result=await fn.call({helpers:{httpRequest:async()=>{calls++;return{tags:['mql']};}}},$,()=>({Client}));if(result[0].json.status!==expected || (expected!==200 && calls!==0))throw Error(source+' '+key);console.log('PASS '+source+' '+expected);
}})().catch(e=>{console.error(e);process.exit(1)});
""".replace('CODE',json.dumps(CODE))
    subprocess.run(['node','-'],input=harness,text=True,encoding='utf-8',check=True)
    w=api('/api/v1/workflows/wBy0fi5lpFUMDS94');rev=copy.deepcopy(w)
    webhook=next(n for n in rev['nodes'] if n['name']=='Webhook')
    cfg=next(n for n in rev['nodes'] if n['name']=='Config')
    vals=cfg['parameters']['assignments']['assignments']
    secret=next((a for a in vals if a['name']=='ingestSecret'),None)
    if secret and secret['value']=='X-LT-MQL-Tag-Ingest':secret['value']=secrets.token_urlsafe(32)
    else:vals.append({'id':'form-ingest-key','name':'ingestSecret','type':'string','value':secrets.token_urlsafe(32)})
    click=api('/api/v1/workflows/1diZyFmTqWQUEny3')
    clickvals=next(n for n in click['nodes'] if n['name']=='Config')['parameters']['assignments']['assignments']
    password=next(a['value'] for a in clickvals if a['name']=='pgPassword')
    next(a for a in vals if a['name']=='pgPassword')['value']=password
    processor={'name':'Apply Verified Form MQL','id':'lt-form-mql-processor','type':'n8n-nodes-base.code','typeVersion':2,'position':[680,0],'parameters':{'mode':'runOnceForAllItems','jsCode':CODE}}
    response=next(n for n in rev['nodes'] if n['name']=='Respond')
    response['parameters']={'respondWith':'json','responseBody':'={{ $json }}','options':{'responseCode':'={{ $json.status || 500 }}'}}
    rev['nodes']=[webhook,cfg,processor,response]
    rev['connections']={'Webhook':{'main':[[{'node':'Config','type':'main','index':0}]]},'Config':{'main':[[{'node':processor['name'],'type':'main','index':0}]]},processor['name']:{'main':[[{'node':'Respond','type':'main','index':0}]]}}
    parse(CODE);save(w,rev)
    api('/api/v1/workflows/'+w['id']+'/activate','POST',{})
    after=api('/api/v1/workflows/'+w['id']);assert after['active'] and after['versionId']==after['activeVersionId']
    print('Form receiver active:',after['versionId'],'requires x-lt-mql-ingest-key; secret stored only in Config.')
