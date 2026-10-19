"""Record a click as MQL provenance only after confirmed new tag application."""
import copy
from repair_v1_facts_sql import api
from fix_verified_booking_gate import save,parse

w=api('/api/v1/workflows/1diZyFmTqWQUEny3');rev=copy.deepcopy(w)
proc=next(n for n in rev['nodes'] if n['name']=='Process Click');code=proc['parameters']['jsCode']
if 'mql_already_present' not in code:
    anchor="await client.query('INSERT INTO lt_booking_link_clicks"
    at=code.find(anchor);assert at>=0
    lookup=r"""const contactResponse=await this.helpers.httpRequest({method:'GET',url:'https://services.leadconnectorhq.com/contacts/'+encodeURIComponent(contactId),headers:{Authorization:'Bearer '+cfgValues.ghlApiKey,Version:'2021-07-28',Accept:'application/json'},json:true,timeout:20000});
    if(!contactResponse?.contact || !Array.isArray(contactResponse.contact.tags))throw Error('contact_lookup_unverified');
    const mqlAlreadyPresent=contactResponse.contact.tags.some(t=>String(t).toLowerCase()==='mql');
    """
    code=code[:at]+lookup+code[at:]
    code=code.replace('apply_mql: true','apply_mql: true, mql_already_present: mqlAlreadyPresent')
    proc['parameters']['jsCode']=code
record=r"""
const item=$('Process Click').first().json,cfg=$('Config').first().json;
if(!$json.tags || !Array.isArray($json.tags) || !$json.tags.some(t=>String(t).toLowerCase()==='mql'))throw Error('MQL application not confirmed');
if(!item.mql_already_present){
const {Client}=require('pg');const pg=new Client({host:'postgres',port:5432,database:'postgres',user:'postgres',password:cfg.pgPassword});await pg.connect();
try{await pg.query("INSERT INTO mql_tag_events(contact_id,tag,added_at,source,payload_json) VALUES($1,'mql',NOW(),'booking_link_click',$2::jsonb) ON CONFLICT(contact_id,tag) DO UPDATE SET source=EXCLUDED.source,payload_json=EXCLUDED.payload_json WHERE mql_tag_events.source='ghl_automation' AND mql_tag_events.added_at>NOW()-INTERVAL '2 minutes'",[item.contact_id,JSON.stringify({utm_source:item.utm_source,utm_medium:item.utm_medium,utm_campaign:item.utm_campaign,vertical:item.vertical})]);}finally{await pg.end();}}
return [{json:{...item,mql_applied:true}}];
"""
if not any(n['name']=='Record Click MQL Provenance' for n in rev['nodes']):
    rev['nodes'].append({'name':'Record Click MQL Provenance','id':'lt-click-mql-proof','type':'n8n-nodes-base.code','typeVersion':2,'position':[1300,0],'parameters':{'mode':'runOnceForAllItems','jsCode':record}})
rev['connections']['Apply MQL Tag']={'main':[[{'node':'Record Click MQL Provenance','type':'main','index':0}]]}
rev['connections']['Record Click MQL Provenance']={'main':[[{'node':'Respond','type':'main','index':0}]]}
parse(code);parse(record)
if rev!=w:save(w,rev)
