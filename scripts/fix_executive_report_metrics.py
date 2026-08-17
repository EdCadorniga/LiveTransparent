"""Repair Executive Report metric contracts in live n8n workflows."""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request
from pathlib import Path


BASE_URL = "https://automations.livetransparent.com/api/v1/workflows/"
WORKFLOW_IDS = {
    "campaign": "MvPLbUAN9IIQikxb",
    "executive": "Bukc0mgOD2r7V6ED",
    "linkedin_inbound": "7o5EBdvwAuIaWW7k",
    "instagram_inbound": "pISlgYUsyJIrLuJd",
    "social_outbound": "kqIi8i1RjFAZKrK3",
}
ALLOWED_SETTINGS = {
    "executionOrder",
    "timezone",
    "saveDataErrorExecution",
    "saveDataSuccessExecution",
    "saveManualExecutions",
    "saveExecutionProgress",
    "executionTimeout",
    "callerPolicy",
    "errorWorkflow",
    "binaryMode",
}


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    env_path = Path(__file__).resolve().parents[1] / ".env"
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def api_key() -> str:
    key = os.environ.get("N8N_API_KEY_LT") or load_env().get("N8N_API_KEY_LT", "")
    if not key:
        raise RuntimeError("N8N_API_KEY_LT is required")
    return key


def request(workflow_id: str, method: str = "GET", payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload, ensure_ascii=True).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL + workflow_id,
        data=body,
        method=method,
        headers={
            "X-N8N-API-KEY": api_key(),
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def node_map(workflow: dict) -> dict[str, dict]:
    return {node["name"]: node for node in workflow.get("nodes", [])}


def code_summary(node: dict) -> dict:
    code = str((node.get("parameters") or {}).get("jsCode") or "")
    return {
        "name": node.get("name"),
        "type": node.get("type"),
        "codeLength": len(code),
        "hasDateRange": "days - 1" in code or "days-1" in code,
        "hasInterestUnknown": "interest_unknown" in code,
        "hasInstagram": "instagram" in code.lower(),
    }


def inspect() -> None:
    for label, workflow_id in WORKFLOW_IDS.items():
        workflow = request(workflow_id)
        summaries = [code_summary(node) for node in workflow.get("nodes", []) if node.get("type") == "n8n-nodes-base.code"]
        print(json.dumps({
            "label": label,
            "id": workflow_id,
            "name": workflow.get("name"),
            "active": workflow.get("active"),
            "versionId": workflow.get("versionId"),
            "activeVersionId": workflow.get("activeVersionId"),
            "nodes": [{"name": node.get("name"), "type": node.get("type")} for node in workflow.get("nodes", [])],
            "codeNodes": summaries,
        }))


def snippets() -> None:
    requests = {
        "campaign": {
            "Normalize Campaign Window": [],
            "Shape Campaign Response": [],
        },
        "executive": {
            "Normalize Request": [],
            "Build Query": ["vapi_weekly AS", "linkedin_weekly AS", "email_direct AS"],
            "Shape Response": [],
        },
        "linkedin_inbound": {
            "Normalize Unipile Message Event": [],
            "Build Reply Events SQL": [],
        },
        "instagram_inbound": {
            "Persist and Claim Instagram Reply": ["CREATE TABLE", "INSERT INTO", "instagram_conversation_map", "last_inbound_at", "return"],
        },
        "social_outbound": {
            "Route Outbound to Unipile": ["provider", "return", "message"],
        },
    }
    for label, node_requests in requests.items():
        workflow = request(WORKFLOW_IDS[label])
        nodes = node_map(workflow)
        for node_name, needles in node_requests.items():
            code = str((nodes[node_name].get("parameters") or {}).get("jsCode") or "")
            print(f"\n===== {label}: {node_name} =====")
            if not needles:
                print(code)
                continue
            lines = code.splitlines()
            selected: set[int] = set()
            for index, line in enumerate(lines):
                if any(needle.lower() in line.lower() for needle in needles):
                    selected.update(range(max(0, index - 3), min(len(lines), index + 5)))
            for index in sorted(selected):
                print(f"{index + 1}: {lines[index]}")
    campaign = request(WORKFLOW_IDS["campaign"])
    query = str((node_map(campaign)["Campaign Channel Query"].get("parameters") or {}).get("query") or "")
    print("\n===== campaign: Campaign Channel Query =====")
    for needle in ["vapi_events AS", "linkedin_events AS", "campaign_opportunities AS", "json_build_object("]:
        index = query.find(needle)
        print(f"\n--- {needle} @ {index} ---")
        if index >= 0:
            print(query[max(0, index - 500):index + 1800])


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def replace_count(text: str, old: str, new: str, expected: int, label: str) -> str:
    count = text.count(old)
    if count != expected:
        raise RuntimeError(f"{label}: expected {expected} matches, found {count}")
    return text.replace(old, new)


def update_workflow(workflow: dict) -> dict:
    settings = {key: value for key, value in (workflow.get("settings") or {}).items() if key in ALLOWED_SETTINGS}
    payload = {
        "name": workflow.get("name"),
        "nodes": workflow.get("nodes") or [],
        "connections": workflow.get("connections") or {},
        "settings": settings,
    }
    return request(workflow["id"], method="PUT", payload=payload)


CAMPAIGN_NORMALIZE = r"""const query = $json.query || {};
const timezone = 'America/New_York';
function isoDateInTimezone(date) {
  const parts = new Intl.DateTimeFormat('en-CA', { timeZone: timezone, year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(date);
  const values = Object.fromEntries(parts.filter((p) => p.type !== 'literal').map((p) => [p.type, p.value]));
  return values.year + '-' + values.month + '-' + values.day;
}
function shiftDate(value, days) {
  const parts = String(value).split('-').map(Number);
  const date = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2]));
  date.setUTCDate(date.getUTCDate() + days);
  return date.toISOString().slice(0, 10);
}
const today = isoDateInTimezone(new Date());
const end = String(query.to || shiftDate(today, -1)).slice(0, 10);
const range = String(query.range || '30d');
const days = range === '7d' ? 7 : range === '90d' ? 90 : 30;
const start = String(query.from || shiftDate(end, -(days - 1))).slice(0, 10);
return [{ json: { startDate: start, endDate: end } }];"""


EXECUTIVE_NORMALIZE = r"""const req = $node['Webhook Intake'].json || {};
const q = req.query || {};
const cfg = $node['Config'].json || {};
const timezone = String(cfg.timezone || 'America/Los_Angeles');
const view = String(q.view || 'overview');
const range = String(q.range || '30d');
const from = q.from ? String(q.from).slice(0, 10) : '';
const to = q.to ? String(q.to).slice(0, 10) : '';
const map = { '7d': 7, '30d': 30, '90d': 90 };
function isoDateInTimezone(date) {
  const parts = new Intl.DateTimeFormat('en-CA', { timeZone: timezone, year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(date);
  const values = Object.fromEntries(parts.filter((part) => part.type !== 'literal').map((part) => [part.type, part.value]));
  return `${values.year}-${values.month}-${values.day}`;
}
function validDate(value) {
  return /^\d{4}-\d{2}-\d{2}$/.test(value) && !Number.isNaN(Date.parse(`${value}T00:00:00Z`));
}
function shiftDate(value, days) {
  const parts = String(value).split('-').map(Number);
  const date = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2]));
  date.setUTCDate(date.getUTCDate() + days);
  return date.toISOString().slice(0, 10);
}
const today = isoDateInTimezone(new Date());
let endDate = validDate(to) ? to : shiftDate(today, -1);
let startDate = validDate(from) ? from : '';
if (Date.parse(`${startDate || endDate}T00:00:00Z`) > Date.parse(`${endDate}T00:00:00Z`)) startDate = '';
if (!startDate) startDate = shiftDate(endDate, -((map[range] || 30) - 1));
return [{ json: { workflowName: String(cfg.workflowName || 'LT - Report Executive Summary API'), timezone, view, range, from, to, startDate, endDate } }];"""


INSTAGRAM_TABLE_DDL = """CREATE TABLE IF NOT EXISTS instagram_activity_events (
  event_id BIGSERIAL PRIMARY KEY,
  event_key TEXT NOT NULL UNIQUE,
  event_type TEXT NOT NULL,
  event_at TIMESTAMPTZ NOT NULL,
  ghl_contact_id TEXT NOT NULL DEFAULT '',
  campaign_key TEXT NOT NULL DEFAULT 'instagram',
  chat_id TEXT NOT NULL DEFAULT '',
  message_id TEXT NOT NULL DEFAULT '',
  provider_id TEXT NOT NULL DEFAULT '',
  workflow_name TEXT NOT NULL DEFAULT '',
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS instagram_activity_events_at_idx ON instagram_activity_events (event_at DESC);
CREATE INDEX IF NOT EXISTS instagram_activity_events_type_at_idx ON instagram_activity_events (event_type, event_at DESC);"""


LINKEDIN_REPLY_EVENT_CODE = r"""function esc(v) {
  if (v === null || v === undefined) return 'NULL';
  return "'" + String(v).replace(/\\/g, '\\\\').replace(/'/g, "''") + "'";
}

const row = $input.first().json;
const shouldUpdate = !!row.should_update;
const contactId = row.contact_id || '';
const providerId = row.provider_id || '';
const chatId = row.chat_id || '';
const reason = row.reason || '';
const sourceTable = row.source_table || '';
const messageId = row.message_id || '';
const eventAt = $node['Normalize Unipile Message Event'].json.timestamp || row.timestamp || '';

if (!shouldUpdate || !contactId) {
  return [{ json: { ...row, sqlQuery: `SELECT ${esc(contactId)}::text AS contact_id;` } }];
}

const sql = `INSERT INTO linkedin_activity_events (event_key,event_type,event_at,ghl_contact_id,location_id,source_key,campaign_key,channel,linkedin_provider_id,unipile_account_id,workflow_id,workflow_name,status,error_code,error_detail,payload_json,metadata_json)
SELECT CONCAT('reply_received:', ${esc(contactId)}, ':', COALESCE(NULLIF(${esc(messageId)}, ''), 'unknown')), 'reply_received', COALESCE(NULLIF(${esc(eventAt)}, '')::timestamptz, NOW()), NULLIF(${esc(contactId)}, ''), 'Zwz4relUXVPxx8uohnjV', CASE WHEN ${esc(sourceTable)} = 'partnership_linkedin_connection_state' THEN 'partnership' ELSE 'dan_linkedin' END, CASE WHEN ${esc(sourceTable)} = 'partnership_linkedin_connection_state' THEN 'partnership_linkedin' ELSE 'dan_linkedin' END, 'linkedin', NULLIF(${esc(providerId)}, ''), 'V9eiHiDpRmCtan0YNdzsQw', '7o5EBdvwAuIaWW7k', 'LT - LinkedIn Unipile New Messages', 'replied', NULL, NULL, jsonb_build_object('chat_id', ${esc(chatId)}, 'message_id', ${esc(messageId)}), jsonb_build_object('source', 'unipile_new_messages_webhook')
WHERE ${shouldUpdate}::boolean AND NULLIF(${esc(contactId)}, '') IS NOT NULL
ON CONFLICT (event_key) DO NOTHING;
SELECT ${esc(contactId)}::text AS contact_id;`;

return [{ json: { ...row, sqlQuery: sql } }];"""


def patch_campaign(workflow: dict) -> None:
    nodes = node_map(workflow)
    nodes["Normalize Campaign Window"]["parameters"]["jsCode"] = CAMPAIGN_NORMALIZE

    query = str(nodes["Campaign Channel Query"]["parameters"]["query"]).replace("\r\n", "\n").replace("\r", "\n")
    if "CREATE TABLE IF NOT EXISTS instagram_activity_events" not in query:
        query = INSTAGRAM_TABLE_DDL + "\n" + query
    query = query.replace(
        "IN ('connected', 'qualified', 'qualified_booked', 'booked')",
        "IN ('connected', 'qualified', 'qualified_booked', 'booked', 'human_answered', 'interest_unknown')",
    )
    if "'instagramActivity'" not in query:
        marker = "  'campaignOpportunities',"
        insert = """  'instagramActivity', (SELECT json_build_object(
    'dmsSent', COUNT(*) FILTER (WHERE event_type = 'dm_sent')::int,
    'inboundReplies', COUNT(*) FILTER (WHERE event_type IN ('reply_received', 'inbound_reply'))::int,
    'eventCount', COUNT(*)::int,
    'coverage', 'ledger'
  ) FROM instagram_activity_events WHERE event_at >= $1::date AND event_at < ($2::date + INTERVAL '1 day')),
  'attributionAsOf', (SELECT MAX(report_date)::text FROM report_raw_ghl_opportunities),
"""
        query = replace_once(query, marker, insert + marker, "campaign instagram aggregate")
    nodes["Campaign Channel Query"]["parameters"]["query"] = query

    code = nodes["Shape Campaign Response"]["parameters"]["jsCode"]
    code = replace_once(
        code,
        "const rows = Array.isArray(payload.campaignChannelBreakdown) ? payload.campaignChannelBreakdown : [];",
        "const rows = Array.isArray(payload.campaignChannelBreakdown) ? payload.campaignChannelBreakdown : [];\nconst instagramActivity = payload.instagramActivity || { dmsSent: 0, inboundReplies: 0, eventCount: 0, coverage: 'ledger' };",
        "campaign shape instagram source",
    )
    code = replace_once(
        code,
        "const requiredCampaigns = [\n  { channel: 'linkedin', campaign: 'Partnership LinkedIn' },\n];",
        "const requiredCampaigns = [\n  { channel: 'linkedin', campaign: 'Partnership LinkedIn' },\n  { channel: 'instagram', campaign: 'Instagram via Unipile', instagram_dms: Number(instagramActivity.dmsSent || 0), instagram_replies: Number(instagramActivity.inboundReplies || 0) },\n];",
        "campaign required rows",
    )
    code = replace_once(
        code,
        "normalizedRows.push({ channel: required.channel, campaign: required.campaign });",
        "normalizedRows.push({ ...required });",
        "campaign required row values",
    )
    code = replace_once(
        code,
        "  'vapi_calls', 'vapi_answered', 'vapi_qualified', 'vapi_booked',\n];",
        "  'vapi_calls', 'vapi_answered', 'vapi_qualified', 'vapi_booked',\n  'instagram_dms', 'instagram_replies',\n];",
        "campaign instagram metrics",
    )
    code = replace_once(
        code,
        "  if (channel === 'vapi') {",
        "  if (channel === 'instagram') return 'Instagram';\n  if (channel === 'vapi') {",
        "campaign instagram group",
    )
    code = replace_once(
        code,
        "const campaignOrder = ['DAN', 'Emerald', 'Partnership', 'Vapi Brand', 'Vapi Dispensary', 'Vapi'];",
        "const campaignOrder = ['DAN', 'Emerald', 'Partnership', 'Instagram', 'Vapi Brand', 'Vapi Dispensary', 'Vapi'];\nfor (const campaign of campaignOrder.slice(0, 6)) if (!grouped[campaign]) grouped[campaign] = { campaign };",
        "campaign stable order",
    )
    code = replace_once(
        code,
        "campaignOpportunities: payload.campaignOpportunities || [], campaignChannelBreakdown, campaignBreakdown",
        "campaignOpportunities: payload.campaignOpportunities || [], attributionAsOf: payload.attributionAsOf || null, instagramActivity, campaignChannelBreakdown, campaignBreakdown",
        "campaign metadata response",
    )
    nodes["Shape Campaign Response"]["parameters"]["jsCode"] = code


def patch_executive(workflow: dict) -> None:
    nodes = node_map(workflow)
    nodes["Normalize Request"]["parameters"]["jsCode"] = EXECUTIVE_NORMALIZE
    code = nodes["Build Query"]["parameters"]["jsCode"]
    if "CREATE TABLE IF NOT EXISTS instagram_activity_events" not in code:
        code = replace_once(code, " WITH meta_ads_raw AS", " " + INSTAGRAM_TABLE_DDL + " WITH meta_ads_raw AS", "executive instagram ddl")
    code = replace_count(
        code,
        "IN ('connected', 'qualified_booked')",
        "IN ('connected', 'qualified_booked', 'human_answered', 'interest_unknown')",
        2,
        "executive weekly answered",
    )
    code = replace_once(
        code,
        "IN ('connected', 'qualified_booked', 'human_answered')",
        "IN ('connected', 'qualified_booked', 'human_answered', 'interest_unknown')",
        "executive campaign answered",
    )
    if "instagram_weekly_activity AS" not in code:
        marker = "vapi_campaign_breakdown AS ("
        insert = """instagram_weekly_activity AS (  SELECT jsonb_build_object(    'dmsSent', COUNT(*) FILTER (WHERE event_type = 'dm_sent')::int,    'inboundReplies', COUNT(*) FILTER (WHERE event_type IN ('reply_received', 'inbound_reply'))::int,    'eventCount', COUNT(*)::int,    'coverage', 'ledger'  ) AS payload  FROM instagram_activity_events  WHERE event_at >= $1::date::timestamptz AND event_at < ($2::date + INTERVAL '1 day')),"""
        code = replace_once(code, marker, insert + marker, "executive instagram cte")
        code = replace_once(
            code,
            "'vapiCampaignBreakdown', COALESCE((SELECT items FROM vapi_campaign_breakdown), '[]'::jsonb)",
            "'instagramWeeklyActivity', COALESCE((SELECT payload FROM instagram_weekly_activity), '{}'::jsonb),  'vapiCampaignBreakdown', COALESCE((SELECT items FROM vapi_campaign_breakdown), '[]'::jsonb)",
            "executive instagram response",
        )
    rate_patterns = [
        r"'emailOpenRate', \(SELECT CASE WHEN COALESCE\(ed\.emails_sent, 0\) = 0 THEN 0::numeric\(10,4\) ELSE ROUND\(ed\.emails_opened::numeric / NULLIF\(ed\.emails_sent, 0\), 4\) END FROM email_direct ed\)",
        r"'emailClickRate', \(SELECT CASE WHEN COALESCE\(ed\.emails_sent, 0\) = 0 THEN 0::numeric\(10,4\) ELSE ROUND\(ed\.emails_clicked::numeric / NULLIF\(ed\.emails_sent, 0\), 4\) END FROM email_direct ed\)",
        r"'emailBounceRate', \(SELECT CASE WHEN COALESCE\(ed\.emails_sent, 0\) = 0 THEN 0::numeric\(10,4\) ELSE ROUND\(ed\.emails_bounced::numeric / NULLIF\(ed\.emails_sent, 0\), 4\) END FROM email_direct ed\)",
    ]
    for key, pattern in zip(["emailOpenRate", "emailClickRate", "emailBounceRate"], rate_patterns):
        code, count = re.subn(pattern, f"'{key}', NULL::numeric", code, count=1)
        if count != 1:
            raise RuntimeError(f"executive {key}: expected one formula")
    code = replace_once(
        code,
        "'emailBounceRate', NULL::numeric,      'sessionToContactRate'",
        "'emailBounceRate', NULL::numeric,      'emailRateBasis', 'event_counts_without_matching_send_denominator',      'sessionToContactRate'",
        "executive email rate basis",
    )
    nodes["Build Query"]["parameters"]["jsCode"] = code

    shape = nodes["Shape Response"]["parameters"]["jsCode"]
    shape = replace_once(
        shape,
        "  openRate: Number(summary.emailsSent ?? 0) > 0 ? Number(summary.emailOpenRate ?? 0) : null,\n  clickRate: Number(summary.emailsSent ?? 0) > 0 ? Number(summary.emailClickRate ?? 0) : null,\n  bounceRate: Number(summary.emailsSent ?? 0) > 0 ? Number(summary.emailBounceRate ?? 0) : null,",
        "  openRate: summary.emailOpenRate == null ? null : Number(summary.emailOpenRate),\n  clickRate: summary.emailClickRate == null ? null : Number(summary.emailClickRate),\n  bounceRate: summary.emailBounceRate == null ? null : Number(summary.emailBounceRate),\n  rateBasis: String(summary.emailRateBasis || 'event_counts_without_matching_send_denominator'),",
        "executive email shape",
    )
    shape = replace_once(
        shape,
        "  linkedinWeeklyActivity: payload.linkedinWeeklyActivity || {},",
        "  linkedinWeeklyActivity: payload.linkedinWeeklyActivity || {},\n  instagramWeeklyActivity: payload.instagramWeeklyActivity || { dmsSent: 0, inboundReplies: 0, eventCount: 0, coverage: 'ledger' },",
        "executive instagram shape",
    )
    shape = replace_once(
        shape,
        "  emailBounceRate: emailCampaignTotals.bounceRate,",
        "  emailBounceRate: emailCampaignTotals.bounceRate,\n  emailRateBasis: emailCampaignTotals.rateBasis,",
        "executive email basis shape",
    )
    nodes["Shape Response"]["parameters"]["jsCode"] = shape


def patch_linkedin_inbound(workflow: dict) -> None:
    nodes = node_map(workflow)
    code = nodes["Normalize Unipile Message Event"]["parameters"]["jsCode"]
    old = r"""function formPayloadText(value) {
  if (!value || typeof value !== 'object') return '';
  const container = value.body && typeof value.body === 'object' ? value.body : value;
  const keys = Object.keys(container);
  if (keys.length !== 1 || !clean(keys[0]).startsWith('{')) return '';
  let text = String(keys[0]) + String(container[keys[0]] ?? '');
  try { text = decodeURIComponent(text.replace(/\+/g, ' ')); } catch (e) {}
  return text;
}"""
    new = r"""function formPayloadText(value) {
  if (!value || typeof value !== 'object') return '';
  const container = value.body && typeof value.body === 'object' ? value.body : value;
  const entries = Object.entries(container);
  if (!entries.length || !clean(entries[0][0]).startsWith('{')) return '';
  let text = entries.map(([key, val], index) => {
    const suffix = val === undefined || val === null || String(val) === '' ? '' : '=' + String(val);
    return (index === 0 ? '' : '&') + String(key) + suffix;
  }).join('');
  try { text = decodeURIComponent(text.replace(/\+/g, ' ')); } catch (e) {}
  return text;
}"""
    nodes["Normalize Unipile Message Event"]["parameters"]["jsCode"] = replace_once(code, old, new, "linkedin form reconstruction")

    nodes["Build Reply Events SQL"]["parameters"]["jsCode"] = LINKEDIN_REPLY_EVENT_CODE


def pg_client_config(code: str) -> str:
    match = re.search(r"const client = new Client\((\{[\s\S]*?\})\);", code)
    if not match:
        raise RuntimeError("Could not locate pg client configuration")
    return match.group(1)


def patch_instagram_inbound(workflow: dict) -> str:
    nodes = node_map(workflow)
    code = nodes["Persist and Claim Instagram Reply"]["parameters"]["jsCode"]
    config = pg_client_config(code)
    if "CREATE TABLE IF NOT EXISTS instagram_activity_events" not in code:
        code = replace_once(
            code,
            "  const mapResult = await client.query(`",
            "  await client.query(`" + INSTAGRAM_TABLE_DDL + "`);\n\n  const mapResult = await client.query(`",
            "instagram inbound ledger ddl",
        )
        code = replace_once(
            code,
            "  await client.query('COMMIT');",
            """  await client.query(`INSERT INTO instagram_activity_events (
    event_key, event_type, event_at, ghl_contact_id, campaign_key, chat_id,
    message_id, provider_id, workflow_name, payload_json
  ) VALUES ($1, 'reply_received', COALESCE(NULLIF($2, '')::timestamptz, NOW()), $3, $4, $5, $6, $7,
    'LT - Instagram Unipile New Messages', $8::jsonb)
  ON CONFLICT (event_key) DO NOTHING`, [
    'reply_received:' + messageId,
    clean(d.message_timestamp),
    mappedContactId,
    campaignKey || 'instagram_unattributed',
    clean(d.instagram_chat_id),
    messageId,
    clean(d.instagram_profile_provider_id),
    JSON.stringify({ username: clean(d.instagram_username), company_name: companyName || clean(d.display_name) }),
  ]);

  await client.query('COMMIT');""",
            "instagram inbound ledger insert",
        )
    nodes["Persist and Claim Instagram Reply"]["parameters"]["jsCode"] = code
    return config


def patch_social_outbound(workflow: dict, config: str) -> None:
    nodes = node_map(workflow)
    node_name = "Log Instagram Outbound Activity"
    if node_name not in nodes:
        code = f"""const {{ Client }} = require('pg');
const crypto = require('crypto');
const item = $input.first()?.json || {{}};
const routing = item.routing || {{}};
if (!routing.routed || String(routing.provider_type || '').toUpperCase() !== 'INSTAGRAM') return [{{ json: item }}];
const client = new Client({config});
try {{
  await client.connect();
  await client.query(`{INSTAGRAM_TABLE_DDL}`);
  const messageId = String(routing.unipile_message_id || '').trim();
  const chatId = String(routing.chat_id || '').trim();
  const messageText = String(routing.message_text || '').trim();
  const fallback = crypto.createHash('sha256').update(chatId + '\\n' + messageText).digest('hex');
  const eventKey = 'dm_sent:' + (messageId || fallback);
  await client.query(`INSERT INTO instagram_activity_events (
    event_key, event_type, event_at, ghl_contact_id, campaign_key, chat_id,
    message_id, provider_id, workflow_name, payload_json
  ) VALUES ($1, 'dm_sent', NOW(), $2, $3, $4, $5, $6,
    'LT - Social Provider Outbound Router', $7::jsonb)
  ON CONFLICT (event_key) DO NOTHING`, [eventKey, String(routing.contact_id || item.contact_id || ''),
    String(item.campaign_key || 'instagram_operator'), chatId, messageId,
    String(routing.provider_id || ''), JSON.stringify({{ source: 'ghl_conversation_provider' }})]);
  return [{{ json: {{ ...item, instagram_activity_logged: true }} }}];
}} catch (error) {{
  return [{{ json: {{ ...item, instagram_activity_logged: false, instagram_activity_error: String(error.message || error).slice(0, 300) }} }}];
}} finally {{
  await client.end().catch(() => {{}});
}}"""
        new_node = {
            "id": "b9c7e7a2-fc43-4f63-9e27-8d537ac5ca11",
            "name": node_name,
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1740, 560],
            "parameters": {"mode": "runOnceForAllItems", "language": "javaScript", "jsCode": code},
        }
        workflow["nodes"].append(new_node)
        workflow.setdefault("connections", {})["Route Outbound to Unipile"] = {
            "main": [[{"node": node_name, "type": "main", "index": 0}]]
        }


def apply_repairs(dry_run: bool = False) -> None:
    workflows = {label: request(workflow_id) for label, workflow_id in WORKFLOW_IDS.items()}
    for workflow in workflows.values():
        if workflow.get("versionId") != workflow.get("activeVersionId"):
            raise RuntimeError(f"Refusing to patch unpublished draft: {workflow.get('id')}")
    patch_campaign(workflows["campaign"])
    patch_executive(workflows["executive"])
    patch_linkedin_inbound(workflows["linkedin_inbound"])
    pg_config = patch_instagram_inbound(workflows["instagram_inbound"])
    patch_social_outbound(workflows["social_outbound"], pg_config)
    if dry_run:
        for label, workflow in workflows.items():
            print(json.dumps({"label": label, "nodes": len(workflow.get("nodes", [])), "dryRun": True}))
        return
    for label in ["instagram_inbound", "social_outbound", "linkedin_inbound", "campaign", "executive"]:
        updated = update_workflow(workflows[label])
        print(json.dumps({
            "label": label,
            "id": updated.get("id"),
            "versionId": updated.get("versionId"),
            "activeVersionId": updated.get("activeVersionId"),
            "active": updated.get("active"),
        }))


def patch_linkedin_schema_only() -> None:
    workflow = request(WORKFLOW_IDS["linkedin_inbound"])
    node_map(workflow)["Build Reply Events SQL"]["parameters"]["jsCode"] = LINKEDIN_REPLY_EVENT_CODE
    updated = update_workflow(workflow)
    print(json.dumps({
        "id": updated.get("id"),
        "versionId": updated.get("versionId"),
        "activeVersionId": updated.get("activeVersionId"),
        "active": updated.get("active"),
    }))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inspect", action="store_true")
    parser.add_argument("--snippets", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--patch-linkedin-schema", action="store_true")
    args = parser.parse_args()
    if args.inspect:
        inspect()
        return
    if args.snippets:
        snippets()
        return
    if args.apply:
        apply_repairs()
        return
    if args.dry_run:
        apply_repairs(dry_run=True)
        return
    if args.patch_linkedin_schema:
        patch_linkedin_schema_only()
        return
    raise RuntimeError("Choose --inspect, --snippets, or --apply")


if __name__ == "__main__":
    main()
