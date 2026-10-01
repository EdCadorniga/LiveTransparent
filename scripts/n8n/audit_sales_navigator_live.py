"""Read only n8n-lt workflow and Postgres state summary; never print Config values."""
from __future__ import annotations

import io
import json
import socket
from pathlib import Path

import paramiko

from wire_sales_navigator_v2_workflows import BASE, api
from inspect_sales_navigator_contact_map import query, CONTAINER

if socket.getfqdn("automations.livetransparent.com") and "automations.livetransparent.com" not in BASE:
    raise RuntimeError("Refusing non-n8n-lt connection")

for workflow_id in ("ZiYEBuP7xdddhnUB", "CfpedDQWxoJLEMdL", "7o5EBdvwAuIaWW7k"):
    workflow = api("/workflows/" + workflow_id)
    print(json.dumps({
        "workflow": workflow_id,
        "active": workflow.get("active"),
        "published": workflow.get("versionId") == workflow.get("activeVersionId"),
        "version": workflow.get("versionId"),
        "nodes": len(workflow.get("nodes", [])),
        "settings": {key: value for key, value in (workflow.get("settings") or {}).items() if key in ("saveDataSuccessExecution", "saveDataErrorExecution", "saveManualExecutions")},
        "relevant_connections": {key: value for key, value in (workflow.get("connections") or {}).items() if key in ("Acknowledge Claimed Inbound", "Acknowledge Claimed Outbound", "Post Inbound to GHL", "Post Outbound Mirror to GHL", "Send Existing V2 Chat Message")},
    }))

key = paramiko.Ed25519Key.from_private_key(io.StringIO((Path.home() / ".ssh" / "local-upload").read_text()))
ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
ssh.connect(socket.gethostbyname("automations.livetransparent.com"), username="root", pkey=key, timeout=10, look_for_keys=False)
try:
    for label, sql in {
        "event_status": "SELECT status,COUNT(*),COALESCE(MIN(updated_at)::text,''),COALESCE(MAX(updated_at)::text,'') FROM sales_navigator_v2_message_events GROUP BY status ORDER BY status;",
        "unresolved_events": "SELECT id,event_id,status,COALESCE(failure_code,''),COALESCE(to_jsonb(e)->>'held_reason',''),COALESCE((to_jsonb(e)->>'reconcile_attempts')::int,0),claimed_at,updated_at FROM sales_navigator_v2_message_events e WHERE status<>'posted' ORDER BY id DESC LIMIT 20;",
        "held_or_uncertain": "SELECT id,event_id,status,COALESCE(to_jsonb(e)->>'held_reason',''),COALESCE((to_jsonb(e)->>'reconcile_attempts')::int,0),updated_at FROM sales_navigator_v2_message_events e WHERE status IN ('processing','failed','held') ORDER BY id DESC LIMIT 50;",
        "maps": "SELECT COUNT(*),COUNT(DISTINCT ghl_contact_id),COUNT(DISTINCT unipile_chat_id) FROM sales_navigator_v2_conversation_map;",
        "duplicate_contact_maps": "SELECT ghl_contact_id,COUNT(*) FROM sales_navigator_v2_conversation_map GROUP BY ghl_contact_id HAVING COUNT(*)>1 ORDER BY COUNT(*) DESC LIMIT 10;",
        "pending_profile_claims": "SELECT status,COUNT(*) FROM linkedin_contact_profile_claims GROUP BY status ORDER BY status;",
        "recent_event_ids": "SELECT id,event_id,status,COALESCE(ghl_message_id,''),COALESCE(unipile_message_id,''),COALESCE(failure_code,''),COALESCE((to_jsonb(e)->>'reconcile_attempts')::int,0),updated_at FROM sales_navigator_v2_message_events e ORDER BY id DESC LIMIT 10;",
    }.items():
        status, result = query(ssh, "postgres", sql)
        print(json.dumps({"db_query": label, "status": status, "rows": result[:2000]}))
finally:
    ssh.close()
