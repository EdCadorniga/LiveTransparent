"""Execute the live click parser with mocked GHL/PG; no external side effects."""
import copy
import json
import subprocess
from repair_v1_facts_sql import api
from fix_verified_booking_gate import save,parse
w=api('/api/v1/workflows/1diZyFmTqWQUEny3');rev=copy.deepcopy(w)
node=next(n for n in rev['nodes'] if n['name']=='Process Click');code=node['parameters']['jsCode']
cfg=next(n for n in rev['nodes'] if n['name']=='Config')
registry=next(a['value'] for a in cfg['parameters']['assignments']['assignments'] if a['name']=='linkRegistryJson')
harness=r"""
const fn=new (Object.getPrototypeOf(async function(){}).constructor)('$input','$','require',CODE);
const registry=REGISTRY;
(async()=>{let inserts=0,lookups=0;class Client{async connect(){}async end(){}async query(q){if(q.startsWith('INSERT'))inserts++;return{rows:[]};}}
const $=()=>({first:()=>({json:{pgPassword:'mock',ghlApiKey:'mock',linkRegistryJson:registry}})});
for(const[kind,expected]of [['known',true],['unknown',false],['mismatch',false]]){
 const contact='Abcdefghijklmnopqrst';const token='a.'+Buffer.from(JSON.stringify({contact_id:kind==='mismatch'?'other':contact,link_id:kind==='unknown'?'not-a-booking':'rmFtop1jXctXpz4kJa1l'})).toString('base64url')+'.s';
 const input={all:()=>[{json:{body:{contact_id:contact,customData:{event:'booking_link_click',link_id:''},contact:{lastAttributionSource:{url:'https://services.leadconnectorhq.com/links/r/2/'+token}}}}}]};
 const result=await fn.call({helpers:{httpRequest:async()=>{lookups++;return{contact:{tags:[]}};}}},input,$,()=>({Client}));
 if(!!result[0].json.apply_mql!==expected)throw Error(kind);if(expected && result[0].json.utm_medium!=='email')throw Error('UTM medium');console.log('PASS live parser '+kind);
}if(inserts!==1||lookups!==1)throw Error('unexpected I/O for ignored clicks');})().catch(e=>{console.error(e);process.exit(1)});
""".replace('CODE',json.dumps(code)).replace('REGISTRY',json.dumps(registry))
subprocess.run(['node','-'],input=harness,text=True,encoding='utf-8',check=True)
utm=next(n for n in rev['nodes'] if n['name']=='Update Contact Last UTM Fields')
utm['parameters']['jsonBody']=utm['parameters']['jsonBody'].replace('field_value:','fieldValue:')
utm['onError']='continueRegularOutput'
if rev!=w:save(w,rev)
