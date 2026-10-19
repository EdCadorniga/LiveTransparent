const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'vertical_runtime.js'),'utf8');
const pure=source.split('// RUNTIME_START')[0];
const context={Date,Intl,console};vm.createContext(context);vm.runInContext(pure,context);
const {asciiField,renderMessage,relationship,pacificOpen,dueStep,contactBlock}=context;
const registry=JSON.parse(fs.readFileSync(path.join(__dirname,'vertical_messages.json'),'utf8'));
let checks=0;
function test(name,fn){fn();checks++;console.log('PASS',name);}
test('all 24 templates render with no apostrophes, garbage, or unresolved tokens',()=>{
 for(const row of Object.values(registry.messages))for(const kind of ['invite','dm1','dm2']){
  const text=renderMessage(row[kind],'Andre',"OBrien Wellness",'https://example.com/book');
  assert(!/[^\x20-\x7E\n]|['{}\\]/.test(text));if(kind==='invite')assert(text.length<=300);
 }
});
test('personalization diacritics and apostrophes normalized without corrupting copy',()=>{
 assert.equal(asciiField('Andr\u00e9'), 'Andre');assert.equal(asciiField("D'Andre"),'DAndre');
 assert.equal(asciiField('O\u2019Brien'),'OBrien');
});
test('mojibake, replacement chars, control chars, and placeholders rejected',()=>{
 for(const bad of ['Jo\u00c3\u00a3o','Hi\ufffd','Name\u0000','{first}','<script>','Name\\x'])
  assert.throws(()=>asciiField(bad));
 assert.throws(()=>renderMessage("Hi {first_name} - don't",'Andre','Team','url'));
 assert.throws(()=>renderMessage('Hi {unknown}','Andre','Team','url'));
});
test('provider name required and absent company uses your team',()=>{
 assert.throws(()=>renderMessage('Hi {first_name}','','','url'));
 assert.equal(renderMessage('Hi {first_name}, {company}','Andre','','url'),'Hi Andre, your team');
});
test('Pacific weekdays and DST hours are enforced',()=>{
 assert(pacificOpen(new Date('2026-10-15T16:00:00Z')));
 assert(!pacificOpen(new Date('2026-10-15T15:59:00Z')));
 assert(!pacificOpen(new Date('2026-10-16T00:00:00Z')));
 assert(!pacificOpen(new Date('2026-10-17T18:00:00Z')));
 assert(pacificOpen(new Date('2026-12-15T17:00:00Z')));
});
test('acceptance day 9 and day 17, never before, late DM1 spaces DM2 eight days',()=>{
 const q={status:'connected',dm_step:0,accepted_at:'2026-10-01T18:00:00Z'};
 assert.equal(dueStep(q,new Date('2026-10-10T17:59:59Z')),0);
 assert.equal(dueStep(q,new Date('2026-10-10T18:00:00Z')),1);
 q.dm_step=1;q.dm1_sent_at='2026-10-13T18:00:00Z';
 assert.equal(dueStep(q,new Date('2026-10-18T18:00:00Z')),0);
 assert.equal(dueStep(q,new Date('2026-10-21T18:00:00Z')),2);
 q.status='suppressed';assert.equal(dueStep(q,new Date('2026-10-25T18:00:00Z')),0);
});
test('first degree proof required in both API versions',()=>{
 assert(relationship({network_distance:'FIRST_DEGREE'}));
 assert(relationship({specifics:{network_distance:'FIRST_DEGREE'}}));
 assert(!relationship({specifics:{network_distance:'SECOND_DEGREE'}}));assert(!relationship({}));
});
test('live cohort, vertical, DND, completed and reply gates',()=>{
 const c={locationId:'Zwz4relUXVPxx8uohnjV',tags:['lt_campaign_crypto_brands_oct_2026_enroll'],
 customFields:[{id:'ODs8fBt5te5HEfSJ91pY',value:'Crypto'}]};
 assert.equal(contactBlock(c,'Crypto','crypto'), '');
 assert.equal(contactBlock(c,'Peptides','peptides'),'vertical_changed');
 c.tags.push('linkedin_dm_sequence_completed');assert.equal(contactBlock(c,'Crypto','crypto'),'suppressed');
 c.tags.pop();c.dnd=true;assert.equal(contactBlock(c,'Crypto','crypto'),'suppressed');
 c.dnd=false;c.tags=[];assert.equal(contactBlock(c,'Crypto','crypto'),'not_in_october_cohort');
});
async function guardTest(name,options,expected){
 const queries=[],http=[];
 class Client{
  async connect(){}async end(){}
  async query(sql){queries.push(sql);
   if(sql.includes('pg_try_advisory_lock'))return {rows:[{ok:options.lock!==false}]};
   if(sql.includes('FROM lt_li_vertical_control'))return {rows:[{enabled:options.enabled!==false,dm_enabled:true}]};
   return {rows:[],rowCount:0};}
 }
 const cfg={accountId:'test',v2AccountId:'acc_test',v2Base:'https://api.unipile.com/v2'};
 const box={MODE:'invite',MESSAGES:registry,SEED_SQL:'SEED',Date,Intl,console,
  require:m=>{assert.equal(m,'pg');return {Client};},$:()=>({first:()=>({json:cfg})})};
 vm.createContext(box);
 const call=vm.runInContext('(async function(){'+source+'})',box);
 const result=await call.call({helpers:{httpRequest:async o=>{http.push(o);return {metadata:{products_connection_status:{classic:'running',sales_navigator:'disconnected'}}};}}});
 assert.equal(result[0].json.reason,expected);assert(!http.some(o=>o.method==='POST'));
 assert(!queries.includes('SEED'));checks++;console.log('PASS',name);
}
async function invitePathTest(options={}){
 const trace=[];
 const q={contact_id:'c1',account_id:'a1',vertical:'Alcohol',vertical_index:0,profile_slug:'prospect',status:'ready',dm_step:0,enrolled_at:'2026-10-15T00:00:00Z'};
 class Client{
  async connect(){}async end(){}
  async query(sql,params){trace.push({sql,params});
   if(sql.includes('pg_try_advisory_lock'))return {rows:[{ok:true}]};
   if(sql.includes('FROM lt_li_vertical_control'))return {rows:[{enabled:true,dm_enabled:true,next_vertical:0}]};
   if(sql.includes("SELECT q.*"))return {rows:[q]};
   if(sql.startsWith('SELECT normalized_profile_slug'))return {rows:[{normalized_profile_slug:'prospect',linkedin_provider_ids:[]}]};
   if(sql.startsWith('SELECT * FROM linkedin_connection_state'))return {rows:[]};
   if(sql.includes('SELECT lt_li_reserve_invite'))return {rows:[{id:options.cap?null:1}]};
   return {rows:[],rowCount:0};}
 }
 class Clock extends Date{constructor(...args){super(...(args.length?args:['2026-10-15T18:00:00Z']));}static now(){return new Date('2026-10-15T18:00:00Z').getTime();}}
 const cfg={accountId:'a1',v2AccountId:'acc_test',workflowName:'LT - Vertical LinkedIn Connection Dispatcher',
  v2Base:'https://v2',ghlBase:'https://ghl',classicBase:'https://classic',locationId:'Zwz4relUXVPxx8uohnjV',bookingBase:'https://book'};
 const box={MODE:'invite',MESSAGES:registry,SEED_SQL:'SEED',Date:Clock,Intl,console,
  require:m=>m==='pg'?{Client}:require(m),$:()=>({first:()=>({json:cfg})})};
 vm.createContext(box);
 const fn=vm.runInContext('(async function(){'+source+'})',box);
 const result=await fn.call({helpers:{httpRequest:async o=>{
  trace.push({http:o});
  if(o.method==='POST'){
   assert(trace.some(t=>t.sql?.includes('SELECT lt_li_reserve_invite')),'intent must precede POST');
   assert(!/[^\x20-\x7E\n]|['{}\\]/.test(o.body.message));
   if(options.uncertain)throw new Error('timeout');return {invitation_id:'invite_1'};
  }
  if(o.url.includes('/accounts/'))return {metadata:{products_connection_status:{classic:'running',sales_navigator:'running'}}};
  if(o.url.endsWith('/contacts/c1'))return {contact:{id:'c1',locationId:cfg.locationId,companyName:'Brand',
   tags:['lt_campaign_alcohol_brands_oct_2026_enroll'],customFields:[{id:'ODs8fBt5te5HEfSJ91pY',value:'Alcohol'}]}};
  if(o.url.endsWith('/conversations/search'))return {conversations:options.reply?[{id:'reply'}]:[]};
  if(o.url.endsWith('/users/prospect'))return {provider_id:'pid',public_identifier:'prospect',first_name:'Andre',network_distance:options.connected?'FIRST_DEGREE':'SECOND_DEGREE'};
  if(o.url.endsWith('/users/invite/sent'))return {items:options.pending?[{id:'existing',invited_user_id:'pid',date:'2026-10-01'}]:[]};
  throw new Error('Unexpected HTTP route');
 }}});
 return {trace,result:result[0].json};
}
async function dmPathTest(options={}){
 const trace=[];
 const q={contact_id:'c1',account_id:'a1',vertical:'Crypto',vertical_index:3,profile_slug:'prospect',provider_id:'pid',
  status:'connected',dm_step:options.step||0,enrolled_at:'2026-10-01T18:00:00Z',accepted_at:'2026-10-01T18:00:00Z',
  dm1_sent_at:options.step?'2026-10-10T18:00:00Z':null,chat_id:options.step?'chat_1':null};
 class Client{
  async connect(){}async end(){}
  async query(sql,params){trace.push({sql,params});
   if(sql.includes('pg_try_advisory_lock'))return {rows:[{ok:true}]};
   if(sql.includes('FROM lt_li_vertical_control'))return {rows:[{enabled:true,dm_enabled:true}]};
   if(sql.startsWith('SELECT * FROM lt_li_vertical_queue'))return {rows:[q]};
   if(sql.startsWith('SELECT normalized_profile_slug'))return {rows:[{normalized_profile_slug:'prospect',linkedin_provider_ids:['pid']}]};
   if(sql.startsWith('SELECT * FROM linkedin_connection_state'))return {rows:[]};
   if(sql.startsWith('SELECT * FROM sales_navigator_v2_conversation_map'))return {rows:[]};
   if(sql.startsWith('INSERT INTO lt_li_outbound_attempts'))return {rows:options.duplicate?[]:[{id:5}]};
   return {rows:[],rowCount:0};}
 }
 class Clock extends Date{constructor(...args){super(...(args.length?args:[options.beforeDue?'2026-10-08T18:00:00Z':'2026-10-20T18:00:00Z']));}}
 const cfg={accountId:'a1',v2AccountId:'acc_test',workflowName:'LT - Vertical LinkedIn Sales Navigator DM Sequence',
  v2Base:'https://v2',ghlBase:'https://ghl',classicBase:'https://classic',locationId:'Zwz4relUXVPxx8uohnjV',bookingBase:'https://book'};
 const box={MODE:'dm',MESSAGES:registry,SEED_SQL:'SEED',Date:Clock,Intl,console,
  require:m=>m==='pg'?{Client}:require(m),$:()=>({first:()=>({json:cfg})})};
 vm.createContext(box);
 const fn=vm.runInContext('(async function(){'+source+'})',box);
 const result=await fn.call({helpers:{httpRequest:async o=>{
  trace.push({http:o});
  if(o.method==='POST'){
   assert(trace.some(t=>t.sql?.startsWith('INSERT INTO lt_li_outbound_attempts')));
   assert(!/[^\x20-\x7E\n]|['{}\\]/.test(o.body.text));
   assert(!('subject' in o.body));assert(!('specifics' in o.body));
   if(!options.step)assert.equal(o.body.users_ids,'sn_pid');
   return {object:options.step?'MessageSent':'ChatStarted',message_id:'mid_1',chat_id:'chat_1'};
  }
  if(o.url.includes('/accounts/'))return {metadata:{products_connection_status:{classic:'running',sales_navigator:'running'}}};
  if(o.url.endsWith('/contacts/c1'))return {contact:{id:'c1',locationId:cfg.locationId,companyName:'Brand',
   tags:['lt_campaign_crypto_brands_oct_2026_enroll'],customFields:[{id:'ODs8fBt5te5HEfSJ91pY',value:'Crypto'}]}};
  if(o.url.endsWith('/conversations/search'))return {conversations:[]};
  if(o.url==='https://classic/users/prospect')return {provider_id:'pid',public_identifier:'prospect',first_name:'Andre',network_distance:'FIRST_DEGREE'};
  if(o.url==='https://v2/acc_test/users/prospect')return {id:'sn_pid',public_identifier:'prospect',specifics:{network_distance:options.notConnected?'SECOND_DEGREE':'FIRST_DEGREE'}};
  if(o.url.endsWith('/inboxes/SALES_NAVIGATOR_PRIMARY/chats'))return {data:options.step||options.reply?[{id:'chat_1',user_id:'sn_pid',is_1to1:true}]:[],next_cursor:null};
  if(o.url.endsWith('/chats/chat_1/messages'))return {data:options.reply?[{id:'reply',is_sender:false}]:[{id:'dm1',is_sender:true}],next_cursor:null};
  throw new Error('Unexpected HTTP route: '+o.url);
 }}});
 return {trace,result:result[0].json};
}
(async()=>{
 await guardTest('concurrent worker exits before any external call',{lock:false},'another_worker_running');
 await guardTest('disabled controls prevent provider access',{enabled:false},'disabled_by_control');
 await guardTest('disconnected Sales Navigator prevents all writes',{},'account_not_ready');
 let r=await invitePathTest();assert.equal(r.result.sent,1);assert.equal(r.trace.filter(x=>x.http?.method==='POST').length,1);
 assert(r.trace.some(x=>x.sql?.includes('next_vertical=$2')&&x.params[1]===1));checks++;console.log('PASS successful invite: durable intent, exactly one POST, next vertical advances');
 for(const options of [{cap:true},{reply:true},{pending:true},{connected:true}]){
  r=await invitePathTest(options);assert.equal(r.trace.filter(x=>x.http?.method==='POST').length,0);
 }checks++;console.log('PASS cap, inbound reply, existing invitation, and existing connection never send an invite');
 r=await invitePathTest({uncertain:true});assert.equal(r.trace.filter(x=>x.http?.method==='POST').length,1);
 assert(r.trace.some(x=>x.sql?.includes("status='uncertain'")));
 assert(r.trace.some(x=>x.sql?.includes('enabled=false,dm_enabled=false')));
 checks++;console.log('PASS uncertain provider write holds both senders without a retry');
 r=await dmPathTest();assert.equal(r.result.sent,1);
 assert(r.trace.some(x=>x.http?.method==='POST'&&x.http.url.endsWith('/inboxes/SALES_NAVIGATOR_PRIMARY/chats/send')));
 checks++;console.log('PASS DM1 starts a Sales Navigator 1to1 thread with scalar recipient, no subject/InMail');
 r=await dmPathTest({step:1});assert.equal(r.result.sent,1);
 assert(r.trace.some(x=>x.http?.method==='POST'&&x.http.url.endsWith('/chats/chat_1/messages/send')));
 assert(r.trace.some(x=>x.sql?.includes('dm_step=$2')&&x.params[1]===2));
 checks++;console.log('PASS DM2 uses existing Sales Navigator thread and terminalizes step 2');
 for(const options of [{beforeDue:true},{notConnected:true},{reply:true},{duplicate:true}]){
  r=await dmPathTest(options);assert.equal(r.trace.filter(x=>x.http?.method==='POST').length,0);
 }checks++;console.log('PASS not-due, non-connection, inbound reply and duplicate DM all send zero messages');
 console.log(checks+' test groups passed');
})().catch(e=>{console.error(e);process.exitCode=1;});
