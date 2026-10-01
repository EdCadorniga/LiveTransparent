"""Wire the dedicated Sales Navigator V2 routes on the n8n-lt instance.

This updates only the two dedicated Sales Navigator workflows. It does not
install the Marketplace app, register a Unipile endpoint, or send messages.
"""
from __future__ import annotations

import json
import uuid
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV: dict[str, str] = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        key, value = line.split("=", 1)
        ENV[key.strip()] = value.strip().strip('"').strip("'")
BASE = ENV.get("N8N_EDITOR_BASE_URL") or f"{ENV.get('N8N_PROTOCOL', 'https')}://{ENV['N8N_HOST']}"
API_KEY = ENV["N8N_LT_API_KEY"]
MEDIA_CREDENTIAL_ID = ENV.get("SN_MEDIA_CREDENTIAL_ID", "__UNCONFIGURED__")


def api(path: str, method: str = "GET", data: dict | None = None):
    request = urllib.request.Request(
        BASE.rstrip("/") + "/api/v1" + path,
        data=None if data is None else json.dumps(data).encode("utf-8"),
        method=method,
        headers={"X-N8N-API-KEY": API_KEY, "Accept": "application/json", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            raw = response.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        for secret in ENV.values():
            if len(secret) > 8:
                detail = detail.replace(secret, "[REDACTED]")
        raise RuntimeError(f"n8n-lt API returned HTTP {exc.code}: {detail[:1200]}") from None


def code(name: str, source: str, pos: list[int]) -> dict:
    return {"id": str(uuid.uuid4()), "name": name, "type": "n8n-nodes-base.code", "typeVersion": 2, "position": pos, "parameters": {"mode": "runOnceForAllItems", "jsCode": source}}


def postgres(name: str, query: str, replacements: str, pos: list[int], always: bool = False) -> dict:
    node = {"id": str(uuid.uuid4()), "name": name, "type": "n8n-nodes-base.postgres", "typeVersion": 2.6, "position": pos,
            "parameters": {"operation": "executeQuery", "query": query, "options": {"queryBatching": "independently", "queryReplacement": replacements}},
            "credentials": {"postgres": {"id": "pgAzUqpwOiGkGXzO", "name": "Postgres account"}}}
    if always:
        node["alwaysOutputData"] = True
    return node


def media_post(name: str, endpoint: str, body: str, pos: list[int]) -> dict:
    return {"id": str(uuid.uuid4()), "name": name, "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2, "position": pos,
            "parameters": {"method": "POST",
                           "url": "https://reports.livetransparent.com/sales-navigator-attachments/v1/" + endpoint,
                           "authentication": "predefinedCredentialType",
                           "nodeCredentialType": "httpHeaderAuth", "sendBody": True,
                           "contentType": "json", "specifyBody": "json", "jsonBody": body,
                           "options": {"response": {"response": {"neverError": True,
                                                                "responseFormat": "json", "fullResponse": True}}}},
            "credentials": {"httpHeaderAuth": {"id": MEDIA_CREDENTIAL_ID,
                                                "name": "LT Sales Navigator Media Service"}}}


def if_node(name: str, left: str, right: object, op: str, typ: str, pos: list[int]) -> dict:
    return {"id": str(uuid.uuid4()), "name": name, "type": "n8n-nodes-base.if", "typeVersion": 2.2, "position": pos,
            "parameters": {"conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                            "conditions": [{"id": str(uuid.uuid4()), "leftValue": left, "rightValue": right,
                                            "operator": {"type": typ, "operation": op, "singleValue": op in ("true", "false")}}], "combinator": "and"}}}


def respond_node() -> dict:
    return {"id": str(uuid.uuid4()), "name": "Respond Safely", "type": "n8n-nodes-base.respondToWebhook", "typeVersion": 1.5, "position": [2300, 400],
            "parameters": {"respondWith": "json", "responseBody": "={{ $json.response }}", "options": {"responseHeaders": {"entries": [{"name": "Content-Type", "value": "application/json"}]}, "responseCode": "={{ $json.status }}"}}}


def conn(target: str, output: int = 0) -> list[list[dict]]:
    return [[{"node": target, "type": "main", "index": output}]]


def update(workflow_id: str, nodes: list[dict], connections: dict) -> dict:
    workflow = api(f"/workflows/{workflow_id}")
    payload = {key: workflow[key] for key in ("name", "nodes", "connections", "settings") if key in workflow}
    payload["nodes"] = nodes
    payload["connections"] = connections
    # n8n 2.37.10 leaves executions stuck in `running` when saveDataSuccessExecution is
    # `none` (observed on the gateway/bridge/reconciler: rows accumulate and consume the
    # production concurrency budget). Save data so executions finalize; prune via n8n.
    settings = dict(payload.get("settings") or {})
    settings["saveDataSuccessExecution"] = "all"
    settings["saveDataErrorExecution"] = "all"
    payload["settings"] = settings
    if "staticData" in workflow:
        payload["staticData"] = workflow["staticData"]
    api(f"/workflows/{workflow_id}", "PUT", payload)
    readback = api(f"/workflows/{workflow_id}")
    return {"id": readback["id"], "active": readback.get("active"), "versionMatches": readback.get("versionId") == readback.get("activeVersionId"), "nodeCount": len(readback["nodes"])}


VALIDATE_OUTBOUND = r'''const src=$input.first()?.json||{},cfg=$items('Config')[0]?.json||{};
const fail=(status,error)=>[{json:{ok:false,status,response:{ok:false,error}}}];
const q=src.query&&typeof src.query==='object'?src.query:{};
if(q.code||q.error)return fail(409,'oauth_connection_managed_by_n8n_credential');
const headers=src.headers&&typeof src.headers==='object'?src.headers:{};
const signature=String(headers['x-ghl-signature']||headers['X-GHL-Signature']||'');
if(!signature)return fail(401,'signature_missing');
let rawBuffer;try{rawBuffer=await this.helpers.getBinaryDataBuffer(0,'data')}catch{return fail(401,'raw_body_missing')}
if(!rawBuffer?.length)return fail(401,'raw_body_missing');
const pem='-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEAi2HR1srL4o18O8BRa7gVJY7G7bupbN3H9AwJrHCDiOg=\n-----END PUBLIC KEY-----';
let ok=false;try{ok=require('crypto').verify(null,rawBuffer,pem,Buffer.from(signature,'base64'))}catch{}
if(!ok)return fail(401,'invalid_signature');
let body;try{body=JSON.parse(rawBuffer.toString('utf8'))}catch{return fail(400,'malformed_json')}
const contactId=String(body.contactId||'').trim(),messageId=String(body.messageId||'').trim(),locationId=String(body.locationId||'').trim(),text=String(body.message||'').trim(),replyToAltId=String(body.replyToAltId||'').trim();
const rawAttachments=Array.isArray(body.attachments)?body.attachments:[];
if(!cfg.ghlLocationId||locationId!==cfg.ghlLocationId)return fail(403,'location_mismatch');
if(String(body.type||'').toUpperCase()!=='SMS')return fail(400,'unsupported_message_type');
if(!contactId||!messageId||(!text&&!rawAttachments.length))return fail(400,'missing_required_fields');
if(rawAttachments.length>1)return fail(422,'too_many_attachments');
let attachments=[];
if(rawAttachments.length===1){
 const url=rawAttachments[0];
 if(typeof url!=='string'||url.length>2048||!/^https:\/\//i.test(url))return fail(422,'invalid_attachment_url');
 let host='';try{host=new URL(url).hostname.toLowerCase()}catch{return fail(422,'invalid_attachment_url')}
 const hosts=['.leadconnectorhq.com','.msgsndr.com','.gohighlevel.com','.googleapis.com','.googleusercontent.com','.amazonaws.com','.cloudfront.net'];
 if(!hosts.some(s=>host.endsWith(s)))return fail(422,'attachment_host_not_allowed');
 const filename=decodeURIComponent((url.split('?')[0].split('/').pop()||'').trim()).slice(0,180)||'attachment';
 attachments=[{url,filename}];
}
return [{json:{ok:true,status:200,contactId,messageId,text,attachments,replyToAltId,payloadSha256:require('crypto').createHash('sha256').update(rawBuffer).digest('hex'),accountId:cfg.unipileV2AccountId}}];'''

BUILD_V2_ATTACHMENT = r'''const v=$('Validate Callback or Provider').first().json,bin=$input.first()?.binary?.data;
const fail=reason=>[{json:{ready:false,reason}}];
if(!v.attachments||!v.attachments.length)return [{json:{ready:true,attachments:[]}}];
if(!bin||!bin.data)return fail('ghl_attachment_empty');
const size=Buffer.from(bin.data,'base64').length;
if(size<=0||size>4*1024*1024)return fail('ghl_attachment_too_large');
const content_type=String(bin.mimeType||'application/octet-stream').split(';')[0];
const filename=String(bin.fileName||v.attachments[0].filename||'attachment').slice(0,180)||'attachment';
return [{json:{ready:true,attachments:[{content:bin.data,content_type,filename}]}}];'''

RESOLVE_OUTBOUND = r'''const e=$('Validate Callback or Provider').first().json,rows=$input.all().map(x=>x.json).filter(x=>x&&x.unipile_chat_id);
if(!e.ok)return [{json:e}];
if(rows.length!==1)return [{json:{ok:false,status:rows.length?409:404,response:{ok:false,error:rows.length?'ambiguous_v2_chat_map':'v2_chat_map_not_found'}}}];
return [{json:{...e,chatId:String(rows[0].unipile_chat_id),profileId:String(rows[0].provider_profile_id)}}];'''

CLAIM_OUTBOUND = r'''WITH attempt AS (
 INSERT INTO sales_navigator_v2_message_events(unipile_account_id,event_id,message_id,unipile_chat_id,status,claim_token,claimed_at,direction,message_text,payload_sha256,attachment_manifest,attempt_count)
 VALUES($1,'ghl:'||$2,'ghl:'||$2,$3,'processing',gen_random_uuid(),NOW(),'ghl_outbound',$4,$5,$6::jsonb,1)
 ON CONFLICT DO NOTHING
 RETURNING id,status,claim_token,message_id,unipile_chat_id
)
SELECT 'claimed'::text AS claim_action,id,status,claim_token,message_id,unipile_chat_id FROM attempt
UNION ALL
SELECT CASE WHEN COUNT(*)=1 AND BOOL_AND(message_id='ghl:'||$2 AND unipile_chat_id=$3) THEN 'duplicate' ELSE 'conflict' END,
       MIN(id),MAX(status),NULL::uuid,'ghl:'||$2,$3
FROM sales_navigator_v2_message_events
WHERE unipile_account_id=$1 AND (event_id='ghl:'||$2 OR message_id='ghl:'||$2)
HAVING NOT EXISTS (SELECT 1 FROM attempt);'''

CLAIM_DECISION = r'''const rows=$input.all().map(x=>x.json),r=rows[0];
if(rows.length!==1||!r)return [{json:{shouldSend:false,status:409,response:{ok:false,error:'idempotency_claim_conflict'}}}];
if(r.claim_action==='claimed')return [{json:{...r,shouldSend:true}}];
if(r.claim_action==='duplicate'&&r.status==='posted')return [{json:{shouldSend:false,status:200,response:{ok:true,duplicate:true}}}];
if(r.claim_action==='duplicate')return [{json:{shouldSend:false,status:503,response:{ok:false,error:'outbound_send_reconciliation_required'}}}];
return [{json:{shouldSend:false,status:409,response:{ok:false,error:'idempotency_claim_conflict'}}}];'''

CAPTURE_SENT_MESSAGE = r'''const r=$input.first()?.json||{},v=r.message_id??r.messageId??r.data?.message_id??r.data?.messageId??r.id;
const ids=Array.isArray(v)?v:[v],id=ids.length===1?String(ids[0]||'').trim():'';
return [{json:{unipileMessageId:id}}];'''

MARK_OUTBOUND = r'''UPDATE sales_navigator_v2_message_events
SET status=CASE WHEN $4<>'' THEN 'posted' ELSE 'processing' END,
    unipile_message_id=NULLIF($4,''),failure_code=CASE WHEN $4<>'' THEN NULL ELSE 'sent_message_id_missing' END,
    updated_at=NOW()
WHERE unipile_account_id=$1 AND event_id='ghl:'||$2 AND claim_token=$3
RETURNING status;'''

PREPARE_GHL_ATTACHMENTS = r'''const a=$('Validate Callback or Provider').first().json.attachments||[];
return a.length?[{json:{hasAttachment:true}}]:[{json:{hasAttachment:false}}];'''


PREPARE_V2_ATTACHMENTS = r'''const e=$('Verify HMAC + Allowlist').first().json,items=e.attachments||[];
const a=items[0]||{};
return [{json:{hasAttachment:items.length>0,account_id:e.accountId,chat_id:e.chatId,message_id:e.messageId,attachment_id:a.id,filename:a.filename,file_size:a.file_size}}];'''

COLLECT_V2_ATTACHMENTS = r'''const r=$input.first()?.json||{},b=r.body||r,url=String(b.url||'');
if(Number(r.statusCode||0)!==200||!/^https:\/\/reports\.livetransparent\.com\/sales-navigator-attachments\/[a-f0-9]{64}$/.test(url))
 return [{json:{ready:false,reason:'attachment_import_failed'}}];
return [{json:{ready:true,attachments:[url]}}];'''


MARK_V2_POST = r'''const e=$('Verify HMAC + Allowlist').first().json,claim=e.direction==='inbound'?$('Decide Inbound Claim').first().json:$('Decide Outbound Mirror Claim').first().json;
const r=$json||{},b=r.body||r,status=Number(r.statusCode||0),ok=status>=200&&status<300&&b.success!==false;
return [{json:{accountId:e.accountId,eventId:e.eventId,claimToken:claim.claim_token,posted:ok,
 ghlConversationId:b.conversationId||null,ghlMessageId:b.messageId||null,
 failureCode:ok?null:`ghl_http_${status||'error'}`}}];'''

DECIDE_GHL_ORIGIN = r'''const e=$('Prepare Outbound Mirror Context').first().json,r=$input.first()?.json||{};
if(r.origin_action==='echo')return [{json:{...e,shouldMirror:false,status:200,response:{ok:true,alreadyInGhl:true}}}];
if(r.origin_action==='uncertain')return [{json:{...e,shouldMirror:false,status:503,response:{ok:false,error:'ghl_origin_reconciliation_required'}}}];
if(r.origin_action!=='mirror')return [{json:{...e,shouldMirror:false,status:503,response:{ok:false,error:'message_origin_unresolved'}}}];
return [{json:{...e,shouldMirror:true}}];'''

VALIDATE_INBOUND = r'''const s=$input.first()?.json||{},cfg=$items('Config')[0]?.json||{},h=s.headers||{};
const fail=(status,error)=>[{json:{valid:false,status,response:{ok:false,error}}}];
const sig=String(h['unipile-signature']||h['Unipile-Signature']||'');
if(!cfg.unipileWebhookSecret)return fail(503,'signature_config_missing');
if(!sig)return fail(401,'signature_missing');
let rawBuffer;try{rawBuffer=await this.helpers.getBinaryDataBuffer(0,'data')}catch{return fail(503,'raw_body_missing')}
if(!rawBuffer?.length)return fail(503,'raw_body_missing');
const parts=Object.fromEntries(sig.split(',').map(p=>p.trim().split('='))),ts=String(parts.t||''),got=String(parts.v0||'');
if(!/^\d+$/.test(ts)||! /^[a-f0-9]{64}$/i.test(got))return fail(401,'invalid_signature_header');
if(Math.abs(Math.floor(Date.now()/1000)-Number(ts))>Number(cfg.maxSignatureAgeSeconds||300))return fail(401,'stale_signature');
const crypto=require('crypto'),expected=crypto.createHmac('sha256',cfg.unipileWebhookSecret).update(ts+'.').update(rawBuffer).digest('hex'),a=Buffer.from(got,'hex'),b=Buffer.from(expected,'hex');
if(a.length!==b.length||!crypto.timingSafeEqual(a,b))return fail(401,'invalid_signature');
let ev;try{ev=JSON.parse(rawBuffer.toString('utf8'))}catch{return fail(400,'malformed_json')};const p=ev.payload||{};
const text=typeof p.text==='string'?p.text:'',attachments=Array.isArray(p.attachments)?p.attachments:[];
if(ev.type!=='message.new'||ev.account_id!==cfg.unipileV2AccountId||typeof p.is_sender!=='boolean'||!ev.id||!p.id||!p.chat_id||!p.sender_id||(!text.trim()&&!attachments.length))return fail(400,'event_rejected');
const ALLOWED=['.jpg','.jpeg','.png','.gif','.heic','.webp','.bmp','.pdf','.doc','.docx','.xls','.xlsx','.ppt','.pptx','.txt','.csv','.rtf'];
const extOf=n=>{const s=String(n||''),i=s.lastIndexOf('.');return i>=0?s.slice(i).toLowerCase():''};
const mimeOk=m=>{m=String(m||'').toLowerCase();return m.startsWith('image/')||m.startsWith('application/pdf')||m.includes('word')||m.includes('excel')||m.includes('spreadsheet')||m.includes('presentation')||m.includes('powerpoint')||m.startsWith('text/')};
if(attachments.length>1||attachments.some(a=>!a||!a.id||!Number.isFinite(Number(a.file_size))||Number(a.file_size)<=0||Number(a.file_size)>4194304||a.is_unavailable===true||!(mimeOk(a.mimetype)||ALLOWED.includes(extOf(a.filename)))))return fail(422,'attachment_manifest_rejected');
const manifest=attachments.map(a=>({id:String(a.id),filename:String(a.filename||a.id),file_size:Number(a.file_size||0),mimetype:String(a.mimetype||''),type:String(a.type||'')}));
return [{json:{valid:true,status:200,direction:p.is_sender?'outbound':'inbound',eventId:String(ev.id),messageId:String(p.id),chatId:String(p.chat_id),profileId:String(p.sender_id),text,timestamp:p.timestamp||ev.created_at||new Date().toISOString(),payloadSha256:crypto.createHash('sha256').update(rawBuffer).digest('hex'),attachments:manifest,accountId:cfg.unipileV2AccountId,providerId:cfg.ghlProviderId}}];'''

NORMALIZE_V2_PROFILE = r'''const e=$('Verify HMAC + Allowlist').first().json,raw=$json||{},p=raw.body||raw.data||raw;
const fail=(status,error)=>[{json:{valid:false,status,response:{ok:false,error}}}];
if(!e.valid)return [{json:e}];
if(Number(raw.statusCode||0)>=400||!p||!p.profile_url)return fail(502,'sender_profile_lookup_failed');
const profileUrl=String(p.profile_url||'').trim(),m=profileUrl.match(/linkedin\.com\/in\/([^/?#]+)/i),profileSlug=m?decodeURIComponent(m[1]).toLowerCase().replace(/\/+$/,''):'';
const firstName=String(p.first_name||'').trim(),lastName=String(p.last_name||'').trim(),displayName=String(p.display_name||[firstName,lastName].filter(Boolean).join(' ')||'LinkedIn Contact').trim();
return [{json:{...e,profileUrl,profileSlug,firstName,lastName,displayName}}];'''

RESOLVE_INBOUND = r'''const r=$input.first()?.json||{};
if(Object.prototype.hasOwnProperty.call(r,'mapped')){
  const event=$('Verify HMAC + Allowlist').first().json;
  if(!r.valid)return [{json:r}];
  return [{json:{...event,valid:true,contactId:String(r.contactId),needsCreate:false,
    identityKey:'provider:'+String(event.profileId).toLowerCase(),claimToken:'',
    profileSlug:'',profileUrl:'',displayName:''}}];
}
const e=$('Normalize V2 Sender Profile').first().json;
if(!e.valid)return [{json:e}];
const action=String(r.claim_action||''),contactId=String(r.ghl_contact_id||'');
if(action==='matched'&&contactId)return [{json:{...e,valid:true,contactId,needsCreate:false,identityKey:e.profileSlug||('provider:'+e.profileId),claimToken:''}}];
if(action==='owner'&&r.claim_token)return [{json:{...e,valid:true,contactId:'',needsCreate:true,identityKey:e.profileSlug||('provider:'+e.profileId),claimToken:String(r.claim_token)}}];
const error=action==='ambiguous'?'ambiguous_linkedin_profile_match':action==='busy'?'linkedin_contact_create_in_progress':'linkedin_identity_unresolved';
return [{json:{...e,valid:false,status:action==='busy'?409:action==='ambiguous'?409:503,response:{ok:false,error}}}];'''

RESOLVE_INBOUND_MAP = r'''const e=$('Verify HMAC + Allowlist').first().json;
const rows=$input.all().map(x=>x.json).filter(x=>x&&x.ghl_contact_id);
if(rows.length===0)return [{json:{...e,mapped:false}}];
if(rows.length!==1||String(rows[0].provider_profile_id)!==String(e.profileId))
  return [{json:{...e,mapped:true,valid:false,status:409,
    response:{ok:false,error:'sales_navigator_chat_identity_conflict'}}}];
return [{json:{...e,mapped:true,valid:true,contactId:String(rows[0].ghl_contact_id)}}];'''

CLAIM_INBOUND = r'''WITH attempt AS (
 INSERT INTO sales_navigator_v2_message_events(unipile_account_id,event_id,message_id,unipile_chat_id,status,claim_token,claimed_at,ghl_contact_id,direction,message_text,provider_timestamp,provider_profile_id,attachment_manifest,payload_sha256,attempt_count)
 VALUES($1,$2,$3,$4,'processing',gen_random_uuid(),NOW(),$5,$6,$7,NULLIF($8,'')::timestamptz,$9,$10::jsonb,$11,1)
 ON CONFLICT DO NOTHING
 RETURNING id,status,claim_token,event_id,message_id,unipile_chat_id,ghl_contact_id
)
SELECT 'claimed'::text AS claim_action,id,status,claim_token,event_id,message_id,unipile_chat_id,ghl_contact_id FROM attempt
UNION ALL
SELECT CASE WHEN COUNT(*)=1 AND BOOL_AND(event_id=$2 AND message_id=$3 AND unipile_chat_id=$4 AND ghl_contact_id=$5) THEN 'duplicate' ELSE 'conflict' END,
       MIN(id),MAX(status),NULL::uuid,$2,$3,$4,$5
FROM sales_navigator_v2_message_events
WHERE unipile_account_id=$1 AND (event_id=$2 OR message_id=$3)
HAVING NOT EXISTS (SELECT 1 FROM attempt);'''

CLAIM_INBOUND_DECISION = r'''const rows=$input.all().map(x=>x.json),r=rows[0];
if(rows.length!==1||!r)return [{json:{claimed:false,status:409,response:{ok:false,error:'idempotency_claim_conflict'}}}];
if(r.claim_action==='claimed')return [{json:{...r,claimed:true}}];
if(r.claim_action==='duplicate'&&r.status==='posted')return [{json:{claimed:false,status:200,response:{ok:true,duplicate:true}}}];
if(r.claim_action==='duplicate'&&r.status==='processing')return [{json:{claimed:false,status:202,response:{ok:true,accepted:true,pendingReconciliation:true}}}];
if(r.claim_action==='duplicate'&&r.status==='failed')return [{json:{claimed:false,status:503,response:{ok:false,error:'delivery_reconciliation_required'}}}];
return [{json:{claimed:false,status:409,response:{ok:false,error:'idempotency_claim_conflict'}}}];'''

MARK_INBOUND = r'''const claim=$('Decide Inbound Claim').first().json,resp=$json.body||$json;
const status=Number($json.statusCode||$json.status||0),ok=status>=200&&status<300&&resp.success!==false;
return [{json:{accountId:claim.accountId||$('Config').first().json.unipileV2AccountId,eventId:claim.eventId,messageId:claim.messageId,claimToken:claim.claim_token,posted:ok,ghlConversationId:resp.conversationId||null,ghlMessageId:resp.messageId||null,failureCode:ok?null:`ghl_http_${status||'error'}`}}];'''

RESOLVE_OUTBOUND_CHAT = r'''const e=$('Verify HMAC + Allowlist').first().json,rows=$input.all().map(x=>x.json).filter(r=>r.ghl_contact_id);
if(!e.valid||e.direction!=='outbound')return [{json:{...e,valid:false,status:400,response:{ok:false,error:'outbound_event_invalid'}}}];
if(rows.length!==1)return [{json:{...e,valid:false,status:rows.length?409:503,response:{ok:false,error:rows.length?'sales_navigator_chat_map_ambiguous':'sales_navigator_chat_not_mapped'}}}];
return [{json:{...e,valid:true,contactId:String(rows[0].ghl_contact_id),conversationId:String(rows[0].ghl_conversation_id||''),chatId:e.chatId}}];'''

EXTRACT_OUTBOUND_PEER = r'''const e=$('Verify HMAC + Allowlist').first().json,raw=$json||{},body=raw.body||raw.data||raw,list=Array.isArray(body)?body:(Array.isArray(body.data)?body.data:[]);
if(Number(raw.statusCode||0)>=400)return [{json:{...e,valid:false,status:503,response:{ok:false,error:'outbound_chat_history_lookup_failed'}}}];
const ids=[...new Set(list.filter(m=>m&&m.is_sender===false&&m.sender_id).map(m=>String(m.sender_id)))];
if(ids.length!==1)return [{json:{...e,valid:false,status:ids.length?409:503,response:{ok:false,error:ids.length?'outbound_chat_peer_ambiguous':'outbound_chat_peer_unresolved'}}}];
return [{json:{...e,valid:true,peerProfileId:ids[0]}}];'''

NORMALIZE_OUTBOUND_PEER_PROFILE = r'''const e=$('Resolve Outbound Peer').first().json,raw=$json||{},p=raw.body||raw.data||raw;
if(!e.valid)return [{json:e}];
if(Number(raw.statusCode||0)>=400||!p||!p.profile_url)return [{json:{...e,valid:false,status:503,response:{ok:false,error:'outbound_peer_profile_lookup_failed'}}}];
const profileUrl=String(p.profile_url||'').trim(),m=profileUrl.match(/linkedin\.com\/in\/([^/?#]+)/i),profileSlug=m?decodeURIComponent(m[1]).toLowerCase().replace(/\/+$/,''):'';
if(!profileSlug)return [{json:{...e,valid:false,status:503,response:{ok:false,error:'outbound_peer_profile_invalid'}}}];
return [{json:{...e,profileUrl,profileSlug,peerName:String(p.display_name||[p.first_name,p.last_name].filter(Boolean).join(' ')||'').trim()}}];'''

RESOLVE_OUTBOUND_INDEX = r'''const e=$('Normalize Outbound Peer Profile').first().json,rows=$input.all().map(x=>x.json).filter(r=>r.ghl_contact_id);
if(!e.valid)return [{json:e}];
const ids=[...new Set(rows.map(r=>String(r.ghl_contact_id)))];
if(ids.length!==1)return [{json:{...e,valid:false,status:ids.length?409:404,response:{ok:false,error:ids.length?'outbound_peer_profile_ambiguous':'outbound_peer_not_in_ghl'}}}];
return [{json:{...e,contactId:ids[0]}}];'''

CONFIRM_OUTBOUND_MAP = r'''const rows=$input.all().map(x=>x.json).filter(r=>r.id),e=$('Resolve Outbound Index').first().json;
if(rows.length!==1)return [{json:{...e,valid:false,status:409,response:{ok:false,error:'outbound_chat_map_conflict'}}}];
return [{json:{...e,valid:true}}];'''

DECIDE_OUTBOUND_MIRROR_CLAIM = r'''const rows=$input.all().map(x=>x.json),r=rows[0],e=$('Prepare Outbound Mirror Context').first().json;
if(rows.length!==1||!r)return [{json:{...e,claimed:false,status:409,response:{ok:false,error:'idempotency_claim_conflict'}}}];
if(r.claim_action==='claimed')return [{json:{...r,...e,claim_token:r.claim_token,claimed:true}}];
if(r.claim_action==='duplicate'&&r.status==='posted')return [{json:{...e,claimed:false,status:200,response:{ok:true,duplicate:true}}}];
if(r.claim_action==='duplicate'&&r.status==='processing')return [{json:{...e,claimed:false,status:202,response:{ok:true,accepted:true,pendingReconciliation:true}}}];
if(r.claim_action==='duplicate'&&r.status==='failed')return [{json:{...e,claimed:false,status:503,response:{ok:false,error:'delivery_reconciliation_required'}}}];
return [{json:{...e,claimed:false,status:409,response:{ok:false,error:'idempotency_claim_conflict'}}}];'''

MARK_OUTBOUND_MIRROR = r'''const claim=$('Decide Outbound Mirror Claim').first().json,resp=$json.body||$json;
const status=Number($json.statusCode||$json.status||0),ok=status>=200&&status<300&&resp.success!==false;
return [{json:{accountId:claim.accountId,eventId:claim.eventId,messageId:claim.messageId,claimToken:claim.claim_token,posted:ok,ghlConversationId:resp.conversationId||null,ghlMessageId:resp.messageId||null,failureCode:ok?null:`ghl_http_${status||'error'}`}}];'''

MARK_ATTACHMENT_FAILURE = """UPDATE sales_navigator_v2_message_events
SET status='held',held_reason=$4,failure_code=$4,updated_at=NOW()
WHERE unipile_account_id=$1 AND event_id=$2 AND claim_token=$3::uuid AND status='processing'
RETURNING status;"""

BUILD_ATTACHMENT_UPLOAD = r'''const e=$('Verify HMAC + Allowlist').first().json,bin=$input.first()?.binary?.data;
if(!e.attachments||!e.attachments.length)return [{json:{attachmentFetchFailed:true,reason:'attachment_missing'}}];
if(!bin||!bin.data)return [{json:{attachmentFetchFailed:true,reason:'attachment_fetch_failed'}}];
return [{json:{filename:String(bin.fileName||e.attachments[0].filename||'attachment'),content_type:String(bin.mimeType||'application/octet-stream').split(';')[0],data:bin.data,attachmentFetchFailed:false}}];'''


def build_gateway() -> dict:
    w = api("/workflows/ZiYEBuP7xdddhnUB")
    generated = {"Validate Callback or Provider", "Valid Signed Outbound?", "Find V2 Contact Chat", "Resolve V2 Chat", "Unique V2 Chat?", "Claim GHL Outbound", "Decide Outbound Claim", "New Outbound Claim?", "Send Existing V2 Chat Message", "Mark GHL Outbound Posted", "Outbound Success Response", "Respond Safely"}
    generated.update({"Capture Sent V2 Message", "Prepare GHL Attachments", "GHL Attachment Present?",
                      "Prepare GHL Attachment File", "Collect GHL Attachments", "No GHL Attachments",
                      "Ready to Send V2?", "Mark GHL Attachment Failure", "Outbound Attachment Failure Response",
                      "Fetch GHL Attachment", "Build V2 Attachment"})
    nodes = [n for n in w["nodes"] if n["name"] not in generated]
    for node in nodes:
        if node["name"] == "Config":
            node["parameters"].setdefault("options", {})["includeBinary"] = True
    nodes.extend([
        code("Validate Callback or Provider", VALIDATE_OUTBOUND, [650, 200]),
        if_node("Valid Signed Outbound?", "={{ $json.ok }}", True, "true", "boolean", [900, 200]),
        postgres("Find V2 Contact Chat", """SELECT m.provider_profile_id,m.unipile_chat_id
FROM sales_navigator_v2_conversation_map m
WHERE m.unipile_account_id=$1 AND m.ghl_contact_id=$2
  AND ($3='' OR m.unipile_chat_id=$3 OR EXISTS (
    SELECT 1 FROM sales_navigator_v2_message_events e
    WHERE e.unipile_account_id=$1 AND e.message_id=$3
      AND e.unipile_chat_id=m.unipile_chat_id AND e.status='posted'
      AND e.event_id NOT LIKE 'ghl:%'
  ))""", "={{ [ $json.accountId, $json.contactId, $json.replyToAltId ] }}", [1150, 80], True),
        code("Resolve V2 Chat", RESOLVE_OUTBOUND, [1400, 80]),
        if_node("Unique V2 Chat?", "={{ $json.ok }}", True, "true", "boolean", [1650, 80]),
        postgres("Claim GHL Outbound", CLAIM_OUTBOUND, "={{ [ $json.accountId, $json.messageId, $json.chatId, $('Validate Callback or Provider').first().json.text, $('Validate Callback or Provider').first().json.payloadSha256, JSON.stringify($('Validate Callback or Provider').first().json.attachments || []) ] }}", [1900, -40], True),
        code("Decide Outbound Claim", CLAIM_DECISION, [2150, -40]),
        if_node("New Outbound Claim?", "={{ $json.shouldSend }}", True, "true", "boolean", [2400, -40]),
        code("Prepare GHL Attachments", PREPARE_GHL_ATTACHMENTS, [2650, -40]),
        if_node("GHL Attachment Present?", "={{ $json.hasAttachment }}", True, "true", "boolean", [2900, -40]),
        {"id": str(uuid.uuid4()), "name": "Fetch GHL Attachment", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": [3150, -120],
         "parameters": {"method": "GET", "url": "={{ $('Validate Callback or Provider').first().json.attachments[0].url }}", "options": {"timeout": 30000, "response": {"response": {"responseFormat": "file", "neverError": True}}}}},
        code("Build V2 Attachment", BUILD_V2_ATTACHMENT, [3400, -120]),
        code("No GHL Attachments", "return [{json:{ready:true,attachments:[]}}];", [3150, 80]),
        if_node("Ready to Send V2?", "={{ $json.ready }}", True, "true", "boolean", [3650, -40]),
        postgres("Mark GHL Attachment Failure", """UPDATE sales_navigator_v2_message_events
SET status='failed',failure_code=$4,updated_at=NOW()
WHERE unipile_account_id=$1 AND event_id='ghl:'||$2 AND claim_token=$3::uuid
  AND status='processing' RETURNING status;""",
                 "={{ [ $('Validate Callback or Provider').first().json.accountId, $('Validate Callback or Provider').first().json.messageId, $('Decide Outbound Claim').first().json.claim_token, $json.reason || 'attachment_prepare_failed' ] }}", [3900, 80]),
        code("Outbound Attachment Failure Response",
             "return [{json:{status:503,response:{ok:false,error:'attachment_prepare_failed'}}}];",
             [4150, 80]),
        {"id": str(uuid.uuid4()), "name": "Send Existing V2 Chat Message", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": [2650, -180],
         "parameters": {"method": "POST", "url": "={{ 'https://api.unipile.com/v2/' + $('Config').first().json.unipileV2AccountId + '/chats/' + $('Resolve V2 Chat').first().json.chatId + '/messages/send' }}", "authentication": "predefinedCredentialType", "nodeCredentialType": "httpHeaderAuth", "sendBody": True, "contentType": "json", "specifyBody": "json", "jsonBody": "={{ { text: $('Validate Callback or Provider').first().json.text, attachments: $json.attachments } }}", "options": {}},
         "credentials": {"httpHeaderAuth": {"id": "calCid5lrBNnl78y", "name": "LT Sales Navigator Unipile V2 API (verified)"}}},
        code("Capture Sent V2 Message", CAPTURE_SENT_MESSAGE, [2900, -180]),
        postgres("Mark GHL Outbound Posted", MARK_OUTBOUND, "={{ [ $('Validate Callback or Provider').first().json.accountId, $('Validate Callback or Provider').first().json.messageId, $('Decide Outbound Claim').first().json.claim_token, $json.unipileMessageId ] }}", [3150, -180]),
        code("Outbound Success Response", "const rows=$input.all(),posted=rows.length===1&&rows[0].json?.status==='posted'; return [{json:{status:posted?200:503,response:{ok:posted,accepted:posted,error:posted?undefined:'outbound_send_reconciliation_required'}}}];", [3400, -180]),
        respond_node(),
    ])
    connections = {
        "GET Sales Navigator OAuth Callback": {"main": conn("Config")},
        "POST Sales Navigator Provider": {"main": conn("Config")},
        "Config": {"main": conn("Validate Callback or Provider")},
        "Validate Callback or Provider": {"main": conn("Valid Signed Outbound?")},
        "Valid Signed Outbound?": {"main": [[conn("Find V2 Contact Chat")[0][0]], [conn("Respond Safely")[0][0]]]},
        "Find V2 Contact Chat": {"main": conn("Resolve V2 Chat")},
        "Resolve V2 Chat": {"main": conn("Unique V2 Chat?")},
        "Unique V2 Chat?": {"main": [[conn("Claim GHL Outbound")[0][0]], [conn("Respond Safely")[0][0]]]},
        "Claim GHL Outbound": {"main": conn("Decide Outbound Claim")},
        "Decide Outbound Claim": {"main": conn("New Outbound Claim?")},
        "New Outbound Claim?": {"main": [[conn("Prepare GHL Attachments")[0][0]], [conn("Respond Safely")[0][0]]]},
        "Prepare GHL Attachments": {"main": conn("GHL Attachment Present?")},
        "GHL Attachment Present?": {"main": [[conn("Fetch GHL Attachment")[0][0]], [conn("No GHL Attachments")[0][0]]]},
        "Fetch GHL Attachment": {"main": conn("Build V2 Attachment")},
        "Build V2 Attachment": {"main": conn("Ready to Send V2?")},
        "No GHL Attachments": {"main": conn("Ready to Send V2?")},
        "Ready to Send V2?": {"main": [[conn("Send Existing V2 Chat Message")[0][0]], [conn("Mark GHL Attachment Failure")[0][0]]]},
        "Mark GHL Attachment Failure": {"main": conn("Outbound Attachment Failure Response")},
        "Outbound Attachment Failure Response": {"main": conn("Respond Safely")},
        "Send Existing V2 Chat Message": {"main": conn("Capture Sent V2 Message")},
        "Capture Sent V2 Message": {"main": conn("Mark GHL Outbound Posted")},
        "Mark GHL Outbound Posted": {"main": conn("Outbound Success Response")},
        "Outbound Success Response": {"main": conn("Respond Safely")},
    }
    return {"workflow_id": "ZiYEBuP7xdddhnUB", "nodes": nodes, "connections": connections}


def build_inbound() -> dict:
    w = api("/workflows/CfpedDQWxoJLEMdL")
    generated = {"Verify HMAC + Allowlist", "Valid Inbound Event?", "Inbound Direction?", "Fetch V2 Sender Profile", "Normalize V2 Sender Profile", "Resolve Existing LinkedIn Contact", "Resolve Inbound Contact", "Unique Existing Contact?", "Needs Contact Creation?", "Create Sales Navigator GHL Contact", "Extract Created Contact", "GHL Contact Created?", "Resolve Created Profile Claim", "Confirm Profile Index Write", "Profile Index Write Successful?", "Record Existing Contact in Shared Index", "Upsert Sales Navigator Conversation Map", "Confirm Sales Navigator Map", "Sales Navigator Map Ready?", "Claim V2 Inbound Event", "Decide Inbound Claim", "New Inbound Claim?", "Respond Safely", "Acknowledge Claimed Inbound", "Post Inbound to GHL", "Prepare Inbound Result", "Finalize Inbound Event", "Find Outbound Chat Map", "Resolve Outbound Chat", "Outbound Chat Mapped?", "Fetch Outbound Chat Messages", "Resolve Outbound Peer", "Outbound Peer Found?", "Fetch Outbound Peer Profile", "Normalize Outbound Peer Profile", "Outbound Peer Profile Valid?", "Lookup Outbound Contact Index", "Resolve Outbound Index", "Outbound Peer Matched?", "Upsert Outbound Chat Map", "Confirm Outbound Chat Map", "Outbound Chat Map Ready?", "Prepare Outbound Mirror Context", "Claim V2 Outbound Mirror Event", "Decide Outbound Mirror Claim", "New Outbound Mirror Claim?", "Acknowledge Claimed Outbound", "Post Outbound Mirror to GHL", "Prepare Outbound Mirror Result", "Finalize V2 Outbound Mirror"}
    generated.update({"Find Inbound Chat Map", "Resolve Inbound Map", "Mapped Inbound Chat?", "Find GHL Origin Message", "Decide GHL Origin", "Mirror External Message?"})
    generated.update({"Inbound Attachment Present?", "Prepare Inbound Attachment", "Collect Inbound Attachment",
                      "Inbound Attachment Ready?", "Mark Inbound Attachment Failure", "Inbound Attachment Failure Response",
                      "Outbound Attachment Present?", "Prepare Outbound Attachment", "Collect Outbound Attachment",
                      "Outbound Attachment Ready?", "Mark Outbound Attachment Failure", "Outbound Attachment Failure Response",
                      "Fetch Inbound Attachment", "Build Inbound Upload", "Store Inbound Attachment",
                      "Fetch Outbound Attachment", "Build Outbound Upload", "Store Outbound Attachment"})
    nodes = [n for n in w["nodes"] if n["name"] not in generated]
    for node in nodes:
        if node["name"] == "Config":
            node["parameters"].setdefault("options", {})["includeBinary"] = True
    nodes.extend([
        code("Verify HMAC + Allowlist", VALIDATE_INBOUND, [650, 200]),
        if_node("Valid Inbound Event?", "={{ $json.valid }}", True, "true", "boolean", [900, 200]),
        if_node("Inbound Direction?", "={{ $json.direction }}", "inbound", "equals", "string", [1050, 200]),
        postgres("Find Inbound Chat Map", "SELECT ghl_contact_id,provider_profile_id FROM sales_navigator_v2_conversation_map WHERE unipile_account_id=$1 AND unipile_chat_id=$2", "={{ [ $json.accountId, $json.chatId ] }}", [1150, 80], True),
        code("Resolve Inbound Map", RESOLVE_INBOUND_MAP, [1400, 80]),
        if_node("Mapped Inbound Chat?", "={{ $json.mapped }}", True, "true", "boolean", [1650, 80]),
        {"id": str(uuid.uuid4()), "name": "Fetch V2 Sender Profile", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": [1150, 80],
         "parameters": {"method": "GET", "url": "={{ 'https://api.unipile.com/v2/' + $('Verify HMAC + Allowlist').first().json.accountId + '/users/' + encodeURIComponent($('Verify HMAC + Allowlist').first().json.profileId) }}", "authentication": "predefinedCredentialType", "nodeCredentialType": "httpHeaderAuth", "sendQuery": True, "queryParameters": {"parameters": [{"name": "variant", "value": "linkedin_sales_navigator"}]}, "options": {"response": {"response": {"neverError": True, "responseFormat": "json", "fullResponse": True}}}},
         "credentials": {"httpHeaderAuth": {"id": "calCid5lrBNnl78y", "name": "LT Sales Navigator Unipile V2 API (verified)"}}},
        code("Normalize V2 Sender Profile", NORMALIZE_V2_PROFILE, [1400, 80]),
        postgres("Resolve Existing LinkedIn Contact", "SELECT * FROM linkedin_claim_contact_profile($1,$2,$3,'sales_navigator_v2');", "={{ [ $json.profileSlug, $json.profileId, $json.accountId + ':' + $json.eventId ] }}", [1650, 80], True),
        code("Resolve Inbound Contact", RESOLVE_INBOUND, [1900, 80]),
        if_node("Unique Existing Contact?", "={{ $json.valid }}", True, "true", "boolean", [2150, 80]),
        if_node("Needs Contact Creation?", "={{ $json.needsCreate }}", True, "true", "boolean", [2400, 80]),
        {"id": str(uuid.uuid4()), "name": "Create Sales Navigator GHL Contact", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": [2650, -80],
         "parameters": {"method": "POST", "url": "https://services.leadconnectorhq.com/contacts/", "authentication": "predefinedCredentialType", "nodeCredentialType": "oAuth2Api", "sendHeaders": True, "specifyHeaders": "keypair", "headerParameters": {"parameters": [{"name": "Version", "value": "2021-07-28"}, {"name": "Accept", "value": "application/json"}]}, "sendBody": True, "contentType": "json", "specifyBody": "json", "jsonBody": "={{ { locationId: 'Zwz4relUXVPxx8uohnjV', firstName: $('Normalize V2 Sender Profile').first().json.firstName || $('Normalize V2 Sender Profile').first().json.displayName, lastName: $('Normalize V2 Sender Profile').first().json.lastName || '', name: $('Normalize V2 Sender Profile').first().json.displayName, source: 'Sales Navigator via Unipile', website: $('Normalize V2 Sender Profile').first().json.profileUrl, tags: ['linkedin_inbound','sales_navigator'] } }}", "options": {"response": {"response": {"neverError": True, "responseFormat": "json", "fullResponse": True}}}},
         "credentials": {"oAuth2Api": {"id": "zuOARvZFtLm6iIWu", "name": "LT Sales Navigator GHL OAuth2"}}},
        code("Extract Created Contact", r'''const r=$json||{},b=r.body||r,c=$('Resolve Inbound Contact').first().json,status=Number(r.statusCode||200),contactId=String(b.contact?.id||b.id||b.contactId||''); if(status<200||status>=300||!contactId)return [{json:{...c,valid:false,status:status>=400?status:502,response:{ok:false,error:'ghl_contact_create_failed'}}}]; return [{json:{...c,contactId,createdContact:true}}];''', [2900, -80]),
        if_node("GHL Contact Created?", "={{ $json.valid }}", True, "true", "boolean", [3150, -80]),
        postgres("Resolve Created Profile Claim", "SELECT linkedin_resolve_contact_profile_claim($1,$2::uuid,$3,$4,$5,$6,$7) AS resolved;", "={{ [ $json.identityKey, $json.claimToken, $json.contactId, $json.profileSlug, $json.profileUrl, $json.displayName, $json.profileId ] }}", [3150, -80]),
        code("Confirm Profile Index Write", r'''const r=$input.first()?.json||{},c=$('Extract Created Contact').first().json; if(r.resolved!==true)return [{json:{...c,valid:false,status:503,response:{ok:false,error:'profile_index_write_failed'}}}]; return [{json:{...c,needsCreate:false,valid:true}}];''', [3400, -80]),
        if_node("Profile Index Write Successful?", "={{ $json.valid }}", True, "true", "boolean", [3650, -80]),
        postgres("Record Existing Contact in Shared Index", """INSERT INTO linkedin_contact_profile_index(ghl_contact_id,normalized_profile_slug,profile_url,contact_name,linkedin_provider_ids,refreshed_at)
VALUES($1,COALESCE(NULLIF($2,''),'provider:'||lower($3)),NULLIF($4,''),NULLIF($5,''),ARRAY[$3]::text[],NOW())
ON CONFLICT(ghl_contact_id,normalized_profile_slug) DO UPDATE SET profile_url=COALESCE(EXCLUDED.profile_url,linkedin_contact_profile_index.profile_url),contact_name=COALESCE(EXCLUDED.contact_name,linkedin_contact_profile_index.contact_name),linkedin_provider_ids=ARRAY(SELECT DISTINCT unnest(linkedin_contact_profile_index.linkedin_provider_ids||EXCLUDED.linkedin_provider_ids)),refreshed_at=NOW()
RETURNING ghl_contact_id;""", "={{ [ $json.contactId, $json.profileSlug, $json.profileId, $json.profileUrl, $json.displayName ] }}", [2900, 220]),
        postgres("Upsert Sales Navigator Conversation Map", """WITH inserted AS (
 INSERT INTO sales_navigator_v2_conversation_map(unipile_account_id,provider_profile_id,unipile_chat_id,ghl_contact_id)
 VALUES($1,$2,$3,$4)
 ON CONFLICT(unipile_account_id,unipile_chat_id) DO UPDATE SET updated_at=NOW()
 WHERE sales_navigator_v2_conversation_map.provider_profile_id=EXCLUDED.provider_profile_id
   AND sales_navigator_v2_conversation_map.ghl_contact_id=EXCLUDED.ghl_contact_id
 RETURNING id
)
SELECT id FROM inserted;""", "={{ [ $('Resolve Inbound Contact').first().json.accountId, $('Resolve Inbound Contact').first().json.profileId, $('Resolve Inbound Contact').first().json.chatId, $('Resolve Inbound Contact').first().json.contactId ] }}", [3900, 80], True),
        code("Confirm Sales Navigator Map", r'''const rows=$input.all(),e=$('Resolve Inbound Contact').first().json; if(rows.length!==1||!rows[0].json?.id)return [{json:{valid:false,status:409,response:{ok:false,error:'sales_navigator_chat_contact_conflict'}}}]; return [{json:{...e,valid:true}}];''', [4150, 80]),
        if_node("Sales Navigator Map Ready?", "={{ $json.valid }}", True, "true", "boolean", [4400, 80]),
        postgres("Claim V2 Inbound Event", CLAIM_INBOUND, "={{ [ $('Resolve Inbound Contact').first().json.accountId, $('Resolve Inbound Contact').first().json.eventId, $('Resolve Inbound Contact').first().json.messageId, $('Resolve Inbound Contact').first().json.chatId, $('Resolve Inbound Contact').first().json.contactId, $('Verify HMAC + Allowlist').first().json.direction, $('Verify HMAC + Allowlist').first().json.text, $('Verify HMAC + Allowlist').first().json.timestamp, $('Verify HMAC + Allowlist').first().json.profileId, JSON.stringify($('Verify HMAC + Allowlist').first().json.attachments || []), $('Verify HMAC + Allowlist').first().json.payloadSha256 ] }}", [4650, 80], True),
        code("Decide Inbound Claim", CLAIM_INBOUND_DECISION, [4900, 80]),
        if_node("New Inbound Claim?", "={{ $json.claimed }}", True, "true", "boolean", [5150, 80]),
        respond_node(),
        {"id": str(uuid.uuid4()), "name": "Acknowledge Claimed Inbound", "type": "n8n-nodes-base.respondToWebhook", "typeVersion": 1.5, "position": [2650, -320],
         "parameters": {"respondWith": "json", "responseBody": "={\"ok\":true,\"accepted\":true}", "options": {"responseHeaders": {"entries": [{"name": "Content-Type", "value": "application/json"}]}, "responseCode": 202}}},
        {"id": str(uuid.uuid4()), "name": "Post Inbound to GHL", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": [2650, -180],
         "parameters": {"method": "POST", "url": "https://services.leadconnectorhq.com/conversations/messages/inbound", "authentication": "predefinedCredentialType", "nodeCredentialType": "oAuth2Api", "sendHeaders": True, "specifyHeaders": "keypair", "headerParameters": {"parameters": [{"name": "Version", "value": "2021-07-28"}, {"name": "Accept", "value": "application/json"}]}, "sendBody": True, "contentType": "json", "specifyBody": "json", "jsonBody": "={{ { type: 'Custom', contactId: $('Resolve Inbound Contact').first().json.contactId, conversationProviderId: $('Config').first().json.ghlProviderId, altId: $('Verify HMAC + Allowlist').first().json.messageId, message: $('Verify HMAC + Allowlist').first().json.text, direction: 'inbound', date: $('Verify HMAC + Allowlist').first().json.timestamp, attachments: $json.attachments || [] } }}", "options": {"response": {"response": {"neverError": True, "responseFormat": "json", "fullResponse": True}}}},
         "credentials": {"oAuth2Api": {"id": "zuOARvZFtLm6iIWu", "name": "LT Sales Navigator GHL OAuth2"}}},
        code("Prepare Inbound Result", MARK_INBOUND, [2900, -180]),
        postgres("Finalize Inbound Event", """UPDATE sales_navigator_v2_message_events SET status=CASE WHEN $4::boolean THEN 'posted' ELSE 'failed' END,
 ghl_conversation_id=$5,ghl_message_id=$6,failure_code=$7,updated_at=NOW()
WHERE unipile_account_id=$1 AND event_id=$2 AND claim_token=$3 RETURNING status;""", "={{ [ $json.accountId, $json.eventId, $json.claimToken, $json.posted, $json.ghlConversationId, $json.ghlMessageId, $json.failureCode ] }}", [3150, -180]),
        postgres("Find Outbound Chat Map", "SELECT ghl_contact_id,ghl_conversation_id FROM sales_navigator_v2_conversation_map WHERE unipile_account_id=$1 AND unipile_chat_id=$2", "={{ [ $json.accountId, $json.chatId ] }}", [1150, 500], True),
        code("Resolve Outbound Chat", RESOLVE_OUTBOUND_CHAT, [1400, 500]),
        if_node("Outbound Chat Mapped?", "={{ $json.valid }}", True, "true", "boolean", [1650, 500]),
        {"id": str(uuid.uuid4()), "name": "Fetch Outbound Chat Messages", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": [1900, 760],
         "parameters": {"method": "GET", "url": "={{ 'https://api.unipile.com/v2/' + $('Verify HMAC + Allowlist').first().json.accountId + '/chats/' + encodeURIComponent($('Verify HMAC + Allowlist').first().json.chatId) + '/messages' }}", "sendQuery": True, "queryParameters": {"parameters": [{"name": "limit", "value": "50"}]}, "authentication": "predefinedCredentialType", "nodeCredentialType": "httpHeaderAuth", "options": {"response": {"response": {"neverError": True, "responseFormat": "json", "fullResponse": True}}}},
         "credentials": {"httpHeaderAuth": {"id": "calCid5lrBNnl78y", "name": "LT Sales Navigator Unipile V2 API (verified)"}}},
        code("Resolve Outbound Peer", EXTRACT_OUTBOUND_PEER, [2150, 760]),
        if_node("Outbound Peer Found?", "={{ $json.valid }}", True, "true", "boolean", [2400, 760]),
        {"id": str(uuid.uuid4()), "name": "Fetch Outbound Peer Profile", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": [2650, 760],
         "parameters": {"method": "GET", "url": "={{ 'https://api.unipile.com/v2/' + $('Verify HMAC + Allowlist').first().json.accountId + '/users/' + encodeURIComponent($('Resolve Outbound Peer').first().json.peerProfileId) }}", "authentication": "predefinedCredentialType", "nodeCredentialType": "httpHeaderAuth", "sendQuery": True, "queryParameters": {"parameters": [{"name": "variant", "value": "linkedin_sales_navigator"}]}, "options": {"response": {"response": {"neverError": True, "responseFormat": "json", "fullResponse": True}}}},
         "credentials": {"httpHeaderAuth": {"id": "calCid5lrBNnl78y", "name": "LT Sales Navigator Unipile V2 API (verified)"}}},
        code("Normalize Outbound Peer Profile", NORMALIZE_OUTBOUND_PEER_PROFILE, [2900, 760]),
        if_node("Outbound Peer Profile Valid?", "={{ $json.valid }}", True, "true", "boolean", [3150, 760]),
        postgres("Lookup Outbound Contact Index", """SELECT DISTINCT ghl_contact_id FROM linkedin_contact_profile_index
WHERE ghl_contact_id ~ '^[A-Za-z0-9]{20}$'
  AND (normalized_profile_slug=$1 OR $2=ANY(linkedin_provider_ids));""", "={{ [ $json.profileSlug, $('Resolve Outbound Peer').first().json.peerProfileId ] }}", [3400, 760], True),
        code("Resolve Outbound Index", RESOLVE_OUTBOUND_INDEX, [3650, 760]),
        if_node("Outbound Peer Matched?", "={{ $json.valid }}", True, "true", "boolean", [3900, 760]),
        postgres("Upsert Outbound Chat Map", """WITH inserted AS (
 INSERT INTO sales_navigator_v2_conversation_map(unipile_account_id,provider_profile_id,unipile_chat_id,ghl_contact_id)
 VALUES($1,$2,$3,$4)
 ON CONFLICT(unipile_account_id,unipile_chat_id) DO UPDATE SET updated_at=NOW()
 WHERE sales_navigator_v2_conversation_map.provider_profile_id=EXCLUDED.provider_profile_id
   AND sales_navigator_v2_conversation_map.ghl_contact_id=EXCLUDED.ghl_contact_id
 RETURNING id
)
SELECT id FROM inserted;""", "={{ [ $json.accountId, $('Resolve Outbound Peer').first().json.peerProfileId, $json.chatId, $json.contactId ] }}", [4150, 760], True),
        code("Confirm Outbound Chat Map", CONFIRM_OUTBOUND_MAP, [4400, 760]),
        if_node("Outbound Chat Map Ready?", "={{ $json.valid }}", True, "true", "boolean", [4650, 760]),
        code("Prepare Outbound Mirror Context", "return [{json:$input.first()?.json||{}}];", [4900, 760]),
        postgres("Find GHL Origin Message", """SELECT CASE
 WHEN EXISTS(SELECT 1 FROM sales_navigator_v2_message_events
   WHERE unipile_account_id=$1 AND unipile_message_id=$2 AND status='posted') THEN 'echo'
 WHEN EXISTS(SELECT 1 FROM sales_navigator_v2_message_events
   WHERE unipile_account_id=$1 AND unipile_chat_id=$3
     AND event_id LIKE 'ghl:%' AND status='processing') THEN 'uncertain'
 ELSE 'mirror' END AS origin_action;""", "={{ [ $json.accountId, $json.messageId, $json.chatId ] }}", [5150, 760]),
        code("Decide GHL Origin", DECIDE_GHL_ORIGIN, [5400, 760]),
        if_node("Mirror External Message?", "={{ $json.shouldMirror }}", True, "true", "boolean", [5650, 760]),
        postgres("Claim V2 Outbound Mirror Event", CLAIM_INBOUND, "={{ [ $json.accountId, $json.eventId, $json.messageId, $json.chatId, $json.contactId, $json.direction, $json.text, $json.timestamp, $json.profileId, JSON.stringify($json.attachments || []), $json.payloadSha256 ] }}", [1900, 500], True),
        code("Decide Outbound Mirror Claim", DECIDE_OUTBOUND_MIRROR_CLAIM, [2150, 500]),
        if_node("New Outbound Mirror Claim?", "={{ $json.claimed }}", True, "true", "boolean", [2400, 500]),
        {"id": str(uuid.uuid4()), "name": "Acknowledge Claimed Outbound", "type": "n8n-nodes-base.respondToWebhook", "typeVersion": 1.5, "position": [2650, 340],
         "parameters": {"respondWith": "json", "responseBody": "={\"ok\":true,\"accepted\":true}", "options": {"responseHeaders": {"entries": [{"name": "Content-Type", "value": "application/json"}]}, "responseCode": 202}}},
        {"id": str(uuid.uuid4()), "name": "Post Outbound Mirror to GHL", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": [5150, 760],
         "parameters": {"method": "POST", "url": "https://services.leadconnectorhq.com/conversations/messages/inbound", "authentication": "predefinedCredentialType", "nodeCredentialType": "oAuth2Api", "sendHeaders": True, "specifyHeaders": "keypair", "headerParameters": {"parameters": [{"name": "Version", "value": "2021-07-28"}, {"name": "Accept", "value": "application/json"}]}, "sendBody": True, "contentType": "json", "specifyBody": "json", "jsonBody": "={{ { type: 'Custom', contactId: $('Prepare Outbound Mirror Context').first().json.contactId, conversationProviderId: $('Config').first().json.ghlProviderId, altId: $('Verify HMAC + Allowlist').first().json.messageId, message: $('Verify HMAC + Allowlist').first().json.text, direction: 'outbound', date: $('Verify HMAC + Allowlist').first().json.timestamp, attachments: $json.attachments || [] } }}", "options": {"response": {"response": {"neverError": True, "responseFormat": "json", "fullResponse": True}}}},
         "credentials": {"oAuth2Api": {"id": "zuOARvZFtLm6iIWu", "name": "LT Sales Navigator GHL OAuth2"}}},
        code("Prepare Outbound Mirror Result", MARK_OUTBOUND_MIRROR, [3150, 500]),
        postgres("Finalize V2 Outbound Mirror", """UPDATE sales_navigator_v2_message_events SET status=CASE WHEN $4::boolean THEN 'posted' ELSE 'failed' END,
 ghl_conversation_id=$5,ghl_message_id=$6,failure_code=$7,updated_at=NOW()
WHERE unipile_account_id=$1 AND event_id=$2 AND claim_token=$3 RETURNING status;""", "={{ [ $json.accountId, $json.eventId, $json.claimToken, $json.posted, $json.ghlConversationId, $json.ghlMessageId, $json.failureCode ] }}", [3400, 500]),
        if_node("Inbound Attachment Present?", "={{ $('Verify HMAC + Allowlist').first().json.attachments.length > 0 }}", True, "true", "boolean", [2900, -320]),
        {"id": str(uuid.uuid4()), "name": "Fetch Inbound Attachment", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": [3150, -400],
         "parameters": {"method": "GET", "url": "={{ 'https://api.unipile.com/v2/' + $('Verify HMAC + Allowlist').first().json.accountId + '/chats/' + encodeURIComponent($('Verify HMAC + Allowlist').first().json.chatId) + '/messages/' + encodeURIComponent($('Verify HMAC + Allowlist').first().json.messageId) + '/attachments/' + encodeURIComponent($('Verify HMAC + Allowlist').first().json.attachments[0].id) }}", "authentication": "predefinedCredentialType", "nodeCredentialType": "httpHeaderAuth", "options": {"timeout": 60000, "response": {"response": {"responseFormat": "file", "neverError": True}}}},
         "credentials": {"httpHeaderAuth": {"id": "calCid5lrBNnl78y", "name": "LT Sales Navigator Unipile V2 API (verified)"}}},
        code("Build Inbound Upload", BUILD_ATTACHMENT_UPLOAD, [3400, -400]),
        media_post("Store Inbound Attachment", "store", "={{ $json }}", [3650, -400]),
        code("Collect Inbound Attachment", COLLECT_V2_ATTACHMENTS, [3900, -400]),
        if_node("Inbound Attachment Ready?", "={{ $json.ready }}", True, "true", "boolean", [4150, -400]),
        postgres("Mark Inbound Attachment Failure", MARK_ATTACHMENT_FAILURE, "={{ [ $('Verify HMAC + Allowlist').first().json.accountId, $('Verify HMAC + Allowlist').first().json.eventId, $('Decide Inbound Claim').first().json.claim_token, $json.reason || 'attachment_import_failed' ] }}", [3400, -500]),
        code("Inbound Attachment Failure Response", "return [{json:{status:503,response:{ok:false,error:'attachment_import_failed'}}}];", [3650, -500]),
        if_node("Outbound Attachment Present?", "={{ $('Verify HMAC + Allowlist').first().json.attachments.length > 0 }}", True, "true", "boolean", [2900, 340]),
        {"id": str(uuid.uuid4()), "name": "Fetch Outbound Attachment", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": [3150, 260],
         "parameters": {"method": "GET", "url": "={{ 'https://api.unipile.com/v2/' + $('Verify HMAC + Allowlist').first().json.accountId + '/chats/' + encodeURIComponent($('Verify HMAC + Allowlist').first().json.chatId) + '/messages/' + encodeURIComponent($('Verify HMAC + Allowlist').first().json.messageId) + '/attachments/' + encodeURIComponent($('Verify HMAC + Allowlist').first().json.attachments[0].id) }}", "authentication": "predefinedCredentialType", "nodeCredentialType": "httpHeaderAuth", "options": {"timeout": 60000, "response": {"response": {"responseFormat": "file", "neverError": True}}}},
         "credentials": {"httpHeaderAuth": {"id": "calCid5lrBNnl78y", "name": "LT Sales Navigator Unipile V2 API (verified)"}}},
        code("Build Outbound Upload", BUILD_ATTACHMENT_UPLOAD, [3400, 260]),
        media_post("Store Outbound Attachment", "store", "={{ $json }}", [3650, 260]),
        code("Collect Outbound Attachment", COLLECT_V2_ATTACHMENTS, [3900, 260]),
        if_node("Outbound Attachment Ready?", "={{ $json.ready }}", True, "true", "boolean", [4150, 260]),
        postgres("Mark Outbound Attachment Failure", MARK_ATTACHMENT_FAILURE, "={{ [ $('Verify HMAC + Allowlist').first().json.accountId, $('Verify HMAC + Allowlist').first().json.eventId, $('Decide Outbound Mirror Claim').first().json.claim_token, $json.reason || 'attachment_import_failed' ] }}", [3400, 160]),
        code("Outbound Attachment Failure Response", "return [{json:{status:503,response:{ok:false,error:'attachment_import_failed'}}}];", [3650, 160]),
    ])
    # Preserve event data across the contact-index and idempotency database nodes.
    claim_decision = next(n for n in nodes if n["name"] == "Decide Inbound Claim")
    claim_decision["parameters"]["jsCode"] = CLAIM_INBOUND_DECISION.replace("if(r.claim_action==='claimed')return [{json:{...r,claimed:true}}];", "if(r.claim_action==='claimed')return [{json:{...r,claimed:true,accountId:$('Resolve Inbound Contact').first().json.accountId,eventId:$('Resolve Inbound Contact').first().json.eventId,messageId:$('Resolve Inbound Contact').first().json.messageId,chatId:$('Resolve Inbound Contact').first().json.chatId,contactId:$('Resolve Inbound Contact').first().json.contactId}}];")
    connections = {
        "Unipile V2 Webhook": {"main": conn("Config")},
        "Config": {"main": conn("Verify HMAC + Allowlist")},
        "Verify HMAC + Allowlist": {"main": conn("Valid Inbound Event?")},
        "Valid Inbound Event?": {"main": [[conn("Inbound Direction?")[0][0]], [conn("Respond Safely")[0][0]]]},
        "Inbound Direction?": {"main": [[conn("Find Inbound Chat Map")[0][0]], [conn("Find Outbound Chat Map")[0][0]]]},
        "Find Inbound Chat Map": {"main": conn("Resolve Inbound Map")},
        "Resolve Inbound Map": {"main": conn("Mapped Inbound Chat?")},
        "Mapped Inbound Chat?": {"main": [[conn("Resolve Inbound Contact")[0][0]], [conn("Fetch V2 Sender Profile")[0][0]]]},
        "Fetch V2 Sender Profile": {"main": conn("Normalize V2 Sender Profile")},
        "Normalize V2 Sender Profile": {"main": conn("Resolve Existing LinkedIn Contact")},
        "Resolve Inbound Contact": {"main": conn("Unique Existing Contact?")},
        "Resolve Existing LinkedIn Contact": {"main": conn("Resolve Inbound Contact")},
        "Unique Existing Contact?": {"main": [[conn("Needs Contact Creation?")[0][0]], [conn("Respond Safely")[0][0]]]},
        "Needs Contact Creation?": {"main": [[conn("Create Sales Navigator GHL Contact")[0][0]], [conn("Record Existing Contact in Shared Index")[0][0]]]},
        "Create Sales Navigator GHL Contact": {"main": conn("Extract Created Contact")},
        "Extract Created Contact": {"main": conn("GHL Contact Created?")},
        "GHL Contact Created?": {"main": [[conn("Resolve Created Profile Claim")[0][0]], [conn("Respond Safely")[0][0]]]},
        "Resolve Created Profile Claim": {"main": conn("Confirm Profile Index Write")},
        "Confirm Profile Index Write": {"main": conn("Profile Index Write Successful?")},
        "Profile Index Write Successful?": {"main": [[conn("Upsert Sales Navigator Conversation Map")[0][0]], [conn("Respond Safely")[0][0]]]},
        "Record Existing Contact in Shared Index": {"main": conn("Upsert Sales Navigator Conversation Map")},
        "Upsert Sales Navigator Conversation Map": {"main": conn("Confirm Sales Navigator Map")},
        "Confirm Sales Navigator Map": {"main": conn("Sales Navigator Map Ready?")},
        "Sales Navigator Map Ready?": {"main": [[conn("Claim V2 Inbound Event")[0][0]], [conn("Respond Safely")[0][0]]]},
        "Claim V2 Inbound Event": {"main": conn("Decide Inbound Claim")},
        "Decide Inbound Claim": {"main": conn("New Inbound Claim?")},
        "New Inbound Claim?": {"main": [[conn("Acknowledge Claimed Inbound")[0][0]], [conn("Respond Safely")[0][0]]]},
        "Acknowledge Claimed Inbound": {"main": conn("Inbound Attachment Present?")},
        "Inbound Attachment Present?": {"main": [[conn("Fetch Inbound Attachment")[0][0]], [conn("Post Inbound to GHL")[0][0]]]},
        "Fetch Inbound Attachment": {"main": conn("Build Inbound Upload")},
        "Build Inbound Upload": {"main": conn("Store Inbound Attachment")},
        "Store Inbound Attachment": {"main": conn("Collect Inbound Attachment")},
        "Collect Inbound Attachment": {"main": conn("Inbound Attachment Ready?")},
        "Inbound Attachment Ready?": {"main": [[conn("Post Inbound to GHL")[0][0]], [conn("Mark Inbound Attachment Failure")[0][0]]]},
        "Mark Inbound Attachment Failure": {"main": conn("Inbound Attachment Failure Response")},
        "Inbound Attachment Failure Response": {"main": conn("Respond Safely")},
        "Post Inbound to GHL": {"main": conn("Prepare Inbound Result")},
        "Prepare Inbound Result": {"main": conn("Finalize Inbound Event")},
        "Find Outbound Chat Map": {"main": conn("Resolve Outbound Chat")},
        "Resolve Outbound Chat": {"main": conn("Outbound Chat Mapped?")},
        "Fetch Outbound Chat Messages": {"main": conn("Resolve Outbound Peer")},
        "Resolve Outbound Peer": {"main": conn("Outbound Peer Found?")},
        "Outbound Peer Found?": {"main": [[conn("Fetch Outbound Peer Profile")[0][0]], [conn("Respond Safely")[0][0]]]},
        "Fetch Outbound Peer Profile": {"main": conn("Normalize Outbound Peer Profile")},
        "Normalize Outbound Peer Profile": {"main": conn("Outbound Peer Profile Valid?")},
        "Outbound Peer Profile Valid?": {"main": [[conn("Lookup Outbound Contact Index")[0][0]], [conn("Respond Safely")[0][0]]]},
        "Lookup Outbound Contact Index": {"main": conn("Resolve Outbound Index")},
        "Resolve Outbound Index": {"main": conn("Outbound Peer Matched?")},
        "Outbound Peer Matched?": {"main": [[conn("Upsert Outbound Chat Map")[0][0]], [conn("Respond Safely")[0][0]]]},
        "Upsert Outbound Chat Map": {"main": conn("Confirm Outbound Chat Map")},
        "Confirm Outbound Chat Map": {"main": conn("Outbound Chat Map Ready?")},
        "Outbound Chat Map Ready?": {"main": [[conn("Prepare Outbound Mirror Context")[0][0]], [conn("Respond Safely")[0][0]]]},
        "Outbound Chat Mapped?": {"main": [[conn("Prepare Outbound Mirror Context")[0][0]], [conn("Fetch Outbound Chat Messages")[0][0]]]},
        "Prepare Outbound Mirror Context": {"main": conn("Find GHL Origin Message")},
        "Find GHL Origin Message": {"main": conn("Decide GHL Origin")},
        "Decide GHL Origin": {"main": conn("Mirror External Message?")},
        "Mirror External Message?": {"main": [[conn("Claim V2 Outbound Mirror Event")[0][0]], [conn("Respond Safely")[0][0]]]},
        "Claim V2 Outbound Mirror Event": {"main": conn("Decide Outbound Mirror Claim")},
        "Decide Outbound Mirror Claim": {"main": conn("New Outbound Mirror Claim?")},
        "New Outbound Mirror Claim?": {"main": [[conn("Acknowledge Claimed Outbound")[0][0]], [conn("Respond Safely")[0][0]]]},
        "Acknowledge Claimed Outbound": {"main": conn("Outbound Attachment Present?")},
        "Outbound Attachment Present?": {"main": [[conn("Fetch Outbound Attachment")[0][0]], [conn("Post Outbound Mirror to GHL")[0][0]]]},
        "Fetch Outbound Attachment": {"main": conn("Build Outbound Upload")},
        "Build Outbound Upload": {"main": conn("Store Outbound Attachment")},
        "Store Outbound Attachment": {"main": conn("Collect Outbound Attachment")},
        "Collect Outbound Attachment": {"main": conn("Outbound Attachment Ready?")},
        "Outbound Attachment Ready?": {"main": [[conn("Post Outbound Mirror to GHL")[0][0]], [conn("Mark Outbound Attachment Failure")[0][0]]]},
        "Mark Outbound Attachment Failure": {"main": conn("Outbound Attachment Failure Response")},
        "Outbound Attachment Failure Response": {"main": conn("Respond Safely")},
        "Post Outbound Mirror to GHL": {"main": conn("Prepare Outbound Mirror Result")},
        "Prepare Outbound Mirror Result": {"main": conn("Finalize V2 Outbound Mirror")},
    }
    # The response node follows claim decision to acknowledge durably before the GHL API call.
    # It also receives fail-closed branches. The new-claim success path continues independently.
    return {"workflow_id": "CfpedDQWxoJLEMdL", "nodes": nodes, "connections": connections}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build the n8n-lt Sales Navigator workflows")
    parser.add_argument("--publish", action="store_true", help="Write and publish both workflows")
    args = parser.parse_args()
    specs = {"gateway": build_gateway(), "inbound": build_inbound()}
    if args.publish:
        print(json.dumps({name: update(spec["workflow_id"], spec["nodes"], spec["connections"])
                          for name, spec in specs.items()}, indent=2))
    else:
        print(json.dumps({name: {"workflow_id": spec["workflow_id"], "node_count": len(spec["nodes"])}
                          for name, spec in specs.items()}, indent=2))
