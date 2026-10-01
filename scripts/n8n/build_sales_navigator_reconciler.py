"""Build a read-only external-write reconciler for the n8n-lt Sales Navigator bridge.

The workflow inspects uncertain writes and updates only the V2 ledger. It never
posts to GHL, sends through Unipile, or creates contacts. Run with --publish to
create it; the default mode only prints a structural summary.
"""
from __future__ import annotations

import argparse
import json
import uuid
from urllib.parse import urlparse

from wire_sales_navigator_v2_workflows import BASE, api, code, if_node, postgres

ACCOUNT = "acc_01m3sefk22e8jvnmvvfx333pye"
LOCATION = "Zwz4relUXVPxx8uohnjV"
PROVIDER = "6abd56db3e5dc9f056868ad2"
NAME = "LT - Sales Navigator V2 Uncertain Write Reconciler"
MAX_RECONCILE_ATTEMPTS = 10

CLAIM = """WITH due AS (
 SELECT id FROM sales_navigator_v2_message_events
 WHERE unipile_account_id='acc_01m3sefk22e8jvnmvvfx333pye'
   AND status IN ('processing','failed')
   AND COALESCE(last_reconciled_at,claimed_at,received_at)<NOW()-INTERVAL '2 minutes'
 ORDER BY COALESCE(last_reconciled_at,claimed_at,received_at),id
 LIMIT 1 FOR UPDATE SKIP LOCKED
)
UPDATE sales_navigator_v2_message_events e
SET last_reconciled_at=NOW(),updated_at=NOW(),reconcile_attempts=e.reconcile_attempts+1
FROM due WHERE e.id=due.id
RETURNING e.id,e.unipile_account_id,e.event_id,e.message_id,e.unipile_chat_id,
 e.status,e.claim_token,e.ghl_contact_id,e.ghl_conversation_id,
 e.direction,e.message_text,e.attachment_manifest,e.provider_timestamp,e.claimed_at,
 e.reconcile_attempts;
"""

RESOLVE_CONVERSATION = r"""const row=$('Claim Stale V2 Row').first().json,raw=$json||{},body=raw.body||raw;
const list=Array.isArray(body.conversations)?body.conversations:[];
if(Number(raw.statusCode||0)>=400)return [{json:{...row,match:false,reason:'ghl_conversation_lookup_http_error'}}];
const matches=list.filter(c=>String(c.contactId||'')===String(row.ghl_contact_id||'')&&String(c.locationId||'')==='Zwz4relUXVPxx8uohnjV');
if(matches.length!==1)return [{json:{...row,match:false,reason:matches.length?'ghl_conversation_ambiguous':'ghl_conversation_not_found'}}];
return [{json:{...row,match:true,conversationId:String(matches[0].id)}}];"""

MATCH_GHL = r"""const row=$('Resolve GHL Conversation').first().json,raw=$json||{},body=raw.body||raw;
if(Number(raw.statusCode||0)>=400)return [{json:{...row,matched:false,reason:'ghl_messages_lookup_http_error'}}];
const messages=Array.isArray(body.messages)?body.messages:Array.isArray(body.messages?.messages)?body.messages.messages:[];
const exact=messages.filter(m=>String(m.altId||'')===String(row.message_id)&&
 String(m.contactId||'')===String(row.ghl_contact_id||'')&&
 String(m.conversationProviderId||'')==='6abd56db3e5dc9f056868ad2'&&
 String(m.direction||'')===String(row.direction||''));
if(exact.length!==1)return [{json:{...row,matched:false,reason:exact.length?'ghl_message_identity_ambiguous':messages.length>=100?'ghl_scan_incomplete':'ghl_message_not_observed'}}];
return [{json:{...row,matched:true,ghlMessageId:String(exact[0].id),conversationId:String(row.conversationId)}}];"""

MATCH_UNIPILE = r"""const row=$('Claim Stale V2 Row').first().json,raw=$json||{},body=raw.body||raw;
if(Number(raw.statusCode||0)>=400)return [{json:{...row,matched:false,reason:'unipile_chat_lookup_http_error'}}];
const list=Array.isArray(body.data)?body.data:Array.isArray(body.messages)?body.messages:[];
if(Array.isArray(row.attachment_manifest)&&row.attachment_manifest.length)return [{json:{...row,matched:false,reason:'attachment_send_requires_manual_match'}}];
const at=Date.parse(row.claimed_at||'');
const exact=list.filter(m=>m.is_sender===true&&String(m.text||'')===String(row.message_text||'')&&
 Number.isFinite(at)&&Math.abs(Date.parse(m.timestamp||'')-at)<=120000);
if(exact.length!==1)return [{json:{...row,matched:false,reason:exact.length?'unipile_send_ambiguous':list.length>=100?'unipile_scan_incomplete':'unipile_send_not_observed'}}];
return [{json:{...row,matched:true,unipileMessageId:String(exact[0].id)}}];"""

FINALIZE = """UPDATE sales_navigator_v2_message_events SET
 status=CASE WHEN $3::boolean THEN 'posted'
             WHEN $8::int >= $9::int THEN 'held'
             ELSE 'failed' END,
 ghl_message_id=CASE WHEN $3::boolean THEN COALESCE(NULLIF($4,''),ghl_message_id) ELSE ghl_message_id END,
 ghl_conversation_id=CASE WHEN $3::boolean THEN COALESCE(NULLIF($5,''),ghl_conversation_id) ELSE ghl_conversation_id END,
 unipile_message_id=CASE WHEN $3::boolean THEN COALESCE(NULLIF($6,''),unipile_message_id) ELSE unipile_message_id END,
 failure_code=CASE WHEN $3::boolean THEN NULL ELSE $7 END,
 held_reason=CASE WHEN $3::boolean THEN NULL
                  WHEN $8::int >= $9::int THEN $7
                  ELSE held_reason END,
 updated_at=NOW()
WHERE id=$1 AND claim_token=$2::uuid AND status IN ('processing','failed')
RETURNING id,status,failure_code,held_reason;
"""


def http_node(name: str, url: str, credential_type: str, credential_id: str,
              credential_name: str, position: list[int], *, query: list[dict] | None = None,
              version: str | None = None) -> dict:
    params: dict = {"method": "GET", "url": url, "authentication": "predefinedCredentialType",
                    "nodeCredentialType": credential_type,
                    "options": {"timeout": 15000,
                                "response": {"response": {"neverError": True,
                                                 "responseFormat": "json", "fullResponse": True}}}}
    if query:
        params.update({"sendQuery": True, "queryParameters": {"parameters": query}})
    if version:
        params.update({"sendHeaders": True, "specifyHeaders": "keypair",
                       "headerParameters": {"parameters": [{"name": "Version", "value": version},
                                                           {"name": "Accept", "value": "application/json"}]}})
    return {"id": str(uuid.uuid4()), "name": name, "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2, "position": position, "parameters": params,
            "credentials": {credential_type: {"id": credential_id, "name": credential_name}}}


def link(name: str, *targets: str) -> tuple[str, dict]:
    return name, {"main": [[{"node": target, "type": "main", "index": 0}] for target in targets]}


def build() -> dict:
    nodes = [
        {"id": str(uuid.uuid4()), "name": "Every Minute", "type": "n8n-nodes-base.scheduleTrigger",
         "typeVersion": 1.2, "position": [200, 300],
         "parameters": {"rule": {"interval": [{"field": "minutes", "minutesInterval": 1}]}}},
        postgres("Claim Stale V2 Row", CLAIM, "={{ [] }}", [450, 300]),
        if_node("Has Stale Row?", "={{ !!$json.id }}", True, "true", "boolean", [600, 300]),
        if_node("GHL Origin?", "={{ $json.event_id.startsWith('ghl:') }}", True, "true", "boolean", [700, 300]),
        http_node("Search GHL Conversation", "https://services.leadconnectorhq.com/conversations/search",
                  "oAuth2Api", "zuOARvZFtLm6iIWu", "LT Sales Navigator GHL OAuth2", [950, 80],
                  query=[{"name": "locationId", "value": LOCATION},
                         {"name": "contactId", "value": "={{ $('Claim Stale V2 Row').first().json.ghl_contact_id }}"},
                         {"name": "limit", "value": "20"}], version="2021-07-28"),
        code("Resolve GHL Conversation", RESOLVE_CONVERSATION, [1200, 80]),
        if_node("Conversation Found?", "={{ $json.match }}", True, "true", "boolean", [1450, 80]),
        http_node("Fetch GHL Conversation Messages",
                  "={{ 'https://services.leadconnectorhq.com/conversations/' + encodeURIComponent($json.conversationId) + '/messages' }}",
                  "oAuth2Api", "zuOARvZFtLm6iIWu", "LT Sales Navigator GHL OAuth2", [1700, -40],
                  query=[{"name": "limit", "value": "100"}], version="2021-07-28"),
        code("Match Exact GHL Message", MATCH_GHL, [1950, -40]),
        http_node("Inspect Unipile Chat",
                  "={{ 'https://api.unipile.com/v2/' + $('Claim Stale V2 Row').first().json.unipile_account_id + '/chats/' + encodeURIComponent($('Claim Stale V2 Row').first().json.unipile_chat_id) + '/messages' }}",
                  "httpHeaderAuth", "calCid5lrBNnl78y", "LT Sales Navigator Unipile V2 API (verified)", [950, 520],
                  query=[{"name": "limit", "value": "100"}]),
        code("Match Exact Unipile Send", MATCH_UNIPILE, [1200, 520]),
        postgres("Record Reconciliation", FINALIZE,
                 "={{ [ $json.id, $json.claim_token, Boolean($json.matched), $json.ghlMessageId || '', $json.conversationId || '', $json.unipileMessageId || '', $json.reason || 'reconciliation_unresolved', $json.reconcile_attempts || 0, %d ] }}" % MAX_RECONCILE_ATTEMPTS,
                 [2200, 300]),
    ]
    connections = dict([
        link("Every Minute", "Claim Stale V2 Row"),
        link("Claim Stale V2 Row", "Has Stale Row?"),
        link("Has Stale Row?", "GHL Origin?"),
        link("GHL Origin?", "Inspect Unipile Chat", "Search GHL Conversation"),
        link("Search GHL Conversation", "Resolve GHL Conversation"),
        link("Resolve GHL Conversation", "Conversation Found?"),
        link("Conversation Found?", "Fetch GHL Conversation Messages", "Record Reconciliation"),
        link("Fetch GHL Conversation Messages", "Match Exact GHL Message"),
        link("Match Exact GHL Message", "Record Reconciliation"),
        link("Inspect Unipile Chat", "Match Exact Unipile Send"),
        link("Match Exact Unipile Send", "Record Reconciliation"),
    ])
    return {"name": NAME, "nodes": nodes, "connections": connections,
            # `saveDataSuccessExecution: none` leaves executions stuck in `running` on
            # n8n 2.37.10 (row accumulates each minute and consumes the production
            # concurrency budget). Save success data so runs finalize; it is tiny when idle.
            "settings": {"executionOrder": "v1", "saveDataSuccessExecution": "all",
                         "saveDataErrorExecution": "all",
                         "saveManualExecutions": False, "saveExecutionProgress": False}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    workflow = build()
    if not args.publish:
        print(json.dumps({"name": NAME, "node_count": len(workflow["nodes"]), "writes_external_messages": False}))
        return
    if urlparse(BASE).hostname != "automations.livetransparent.com":
        raise RuntimeError("Refusing non-n8n-lt connection")
    created = api("/workflows", "POST", workflow)
    api(f"/workflows/{created['id']}/activate", "POST", {})
    readback = api(f"/workflows/{created['id']}")
    print(json.dumps({"id": created["id"], "active": readback.get("active"),
                      "published": readback.get("versionId") == readback.get("activeVersionId")}))


if __name__ == "__main__":
    main()
