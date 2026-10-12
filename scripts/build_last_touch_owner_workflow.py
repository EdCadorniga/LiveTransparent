"""Create the n8n-lt 14-day last-touch owner resolver/backfill workflow.

The PIT is read into a workflow-scoped Config node in memory and is never
printed. The workflow defaults to dry-run; writes require apply=true.
"""

from __future__ import annotations

import json
import pathlib
import ssl
import urllib.error
import urllib.request
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
N8N_HOST = "https://automations.livetransparent.com"
WORKFLOW_NAME = "LT - Last-Touch Owner Resolver + 14-Day Backfill"
EXISTING_WORKFLOW_ID = "KQjosWjChMYbhZkF"


def read_env() -> dict[str, str]:
    result: dict[str, str] = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


env = read_env()
n8n_key = env.get("N8N_LT_API_KEY")
ghl_key = env.get("GHL_PIT") or env.get("GHL_API_KEY")
if not n8n_key:
    raise SystemExit("N8N_LT_API_KEY is missing")
if not ghl_key:
    raise SystemExit("GHL_PIT/GHL_API_KEY is missing")

CODE = r'''try {
const cfg = $('Config').first().json;
const webhook = $('Backfill Webhook');
const body = webhook.isExecuted ? (webhook.first().json.body || {}) : {};
const locationId = String(cfg.locationId || 'Zwz4relUXVPxx8uohnjV');
const base = 'https://services.leadconnectorhq.com';
const headers = { Authorization: `Bearer ${cfg.ghlApiKey}`, Version: '2021-07-28', Accept: 'application/json', 'Content-Type': 'application/json' };
const apply = webhook.isExecuted ? body.apply === true : true;
const now = Date.now();
const fromMs = body.from ? Date.parse(body.from) : now - 14 * 86400000;
const toMs = body.to ? Date.parse(body.to) : now;
if (!Number.isFinite(fromMs) || !Number.isFinite(toMs) || fromMs >= toMs) throw new Error('Invalid date range');
const maxContacts = Math.max(1, Math.min(Number(body.maxContacts || 1000), 1000));
const offset = Math.max(0, Number(body.offset || 0));
const requestedContactIds = Array.isArray(body.contactIds) ? new Set(body.contactIds.map(String)) : null;

async function api(method, url, data) {
  let last;
  for (let i = 0; i < 4; i++) {
    try {
      return await this.helpers.httpRequest({ method, url, headers, ...(data ? { body: data, json: true } : { json: true }), timeout: 30000 });
    } catch (err) {
      last = err;
      const status = Number(err.statusCode || err.status || err.response?.statusCode || 0);
      if (status && status !== 429 && status < 500) throw err;
      await new Promise(r => setTimeout(r, 500 * (i + 1)));
    }
  }
  throw last;
}
const clean = v => String(v == null ? '' : v).trim();
const timestamp = v => { const n = typeof v === 'number' ? v : Date.parse(v || ''); return Number.isFinite(n) ? n : 0; };
const query = o => Object.entries(o).map(([k, v]) => encodeURIComponent(k) + '=' + encodeURIComponent(String(v))).join('&');
function getOwnerField(opp) {
  const f = (Array.isArray(opp.customFields) ? opp.customFields : []).find(x => clean(x.id) === 'Wpg7FGrQTgAY1GoKcdEJ');
  return clean(f?.fieldValue ?? f?.fieldValueString ?? f?.field_value ?? f?.value);
}
function getMessages(resp) {
  const value = resp?.messages ?? resp?.data?.messages;
  return Array.isArray(value) ? value : (Array.isArray(value?.messages) ? value.messages : []);
}
function isCall(m) { return String(m.messageType || '').toUpperCase() === 'TYPE_CALL' || (String(m.type) === '1' && Boolean(m.meta?.call)); }

const userResp = await api.call(this, 'GET', `${base}/users/?locationId=${encodeURIComponent(locationId)}`);
const userRows = Array.isArray(userResp.users) ? userResp.users : (Array.isArray(userResp.data?.users) ? userResp.data.users : []);
const users = new Map(userRows.filter(u => u && (u.id || u._id)).map(u => [clean(u.id || u._id), { id: clean(u.id || u._id), name: clean(u.name || `${u.firstName || ''} ${u.lastName || ''}`), active: u.isActive !== false && u.deleted !== true }]));

// Load all open opportunities, then restrict candidates locally by created or
// updated timestamp. This catches older opportunities updated during the window.
const allOpen = [];
let startAfter = '', startAfterId = '', oppPages = 0;
for (; oppPages < 200; oppPages++) {
  const q = { location_id: locationId, status: 'open', limit: '100' };
  if (startAfter) q.startAfter = startAfter;
  if (startAfterId) q.startAfterId = startAfterId;
  const page = await api.call(this, 'GET', `${base}/opportunities/search?${query(q)}`);
  const rows = Array.isArray(page.opportunities) ? page.opportunities : [];
  allOpen.push(...rows);
  const meta = page.meta || {};
  if (!meta.nextPageUrl || !meta.startAfter || !meta.startAfterId || rows.length === 0) break;
  startAfter = String(meta.startAfter);
  startAfterId = String(meta.startAfterId);
  await new Promise(r => setTimeout(r, 150));
}

const byContact = new Map();
const recentContactIds = new Set();
for (const opp of allOpen) {
  const contactId = clean(opp.contactId);
  if (!contactId) continue;
  const allRows = byContact.get(contactId) || [];
  allRows.push(opp);
  byContact.set(contactId, allRows);
  const touchedAt = Math.max(timestamp(opp.updatedAt), timestamp(opp.lastStageChangeAt), timestamp(opp.createdAt));
  if (touchedAt >= fromMs && touchedAt <= toMs) recentContactIds.add(contactId);
}
let candidateIds = [...recentContactIds];
if (requestedContactIds) candidateIds = candidateIds.filter(id => requestedContactIds.has(id));
const candidateTotal = candidateIds.length;
const candidates = candidateIds.slice(offset, offset + maxContacts).map(id => [id, byContact.get(id) || []]);
const report = { mode: apply ? 'apply' : 'dry_run', window: { from: new Date(fromMs).toISOString(), to: new Date(toMs).toISOString() }, scanned: { openOpportunities: allOpen.length, opportunityPages: oppPages, candidateContacts: recentContactIds.size, candidateContactsSelected: candidateTotal, offset, contactsThisRun: candidates.length }, proposedContacts: 0, opportunitiesUpdated: 0, contactsUpdated: 0, ownerFieldsSynced: 0, skippedNoAgentEvidence: 0, skippedInactiveOrUnknownUser: 0, conflictsPreserved: 0, errors: 0, results: [] };

for (const [contactId, opps] of candidates) {
  try {
    const targetOpps = opps.filter(o => {
      const t = Math.max(timestamp(o.updatedAt), timestamp(o.lastStageChangeAt), timestamp(o.createdAt));
      return t >= fromMs && t <= toMs;
    });
    const cResp = await api.call(this, 'GET', `${base}/contacts/${encodeURIComponent(contactId)}`);
    const contact = cResp.contact || cResp.data?.contact || cResp;
    const contactOwner = clean(contact.assignedTo);
    const newestAssignedOpp = opps.filter(o => clean(o.assignedTo)).sort((a,b) => timestamp(b.updatedAt || b.createdAt) - timestamp(a.updatedAt || a.createdAt))[0];
    const oppOwner = clean(newestAssignedOpp?.assignedTo);

    // Existing native assignments are not overwritten: an opportunity owner is
    // authoritative for its Owner custom field; contact assignedTo fills a
    // missing opportunity owner. Only when both are blank do we infer a new one.
    let inferred = null;
    if (!oppOwner && !contactOwner) {
      const params = { contactId, limit: '100', sortBy: 'last_message_date', sort: 'desc' };
      const convResp = await api.call(this, 'GET', `${base}/conversations/search?${query(params)}`);
      const conversations = Array.isArray(convResp.conversations) ? convResp.conversations : (Array.isArray(convResp.data?.conversations) ? convResp.data.conversations : []);
      let latestCall = null, latestHumanOutbound = null;
      for (const convo of conversations) {
        const convId = clean(convo.id || convo.conversationId);
        if (!convId || timestamp(convo.lastMessageDate || convo.dateUpdated) < fromMs) continue;
        const msgResp = await api.call(this, 'GET', `${base}/conversations/${encodeURIComponent(convId)}/messages?limit=100`);
        const messages = getMessages(msgResp);
        for (const msg of messages) {
          const at = timestamp(msg.dateAdded || msg.dateUpdated);
          const userId = clean(msg.userId);
          if (!userId || at < fromMs || at > toMs || String(msg.direction || '').toLowerCase() !== 'outbound') continue;
          const kind = String(msg.messageType || '').toUpperCase();
          const call = isCall(msg);
          const source = String(msg.source || '').toLowerCase();
          const human = !call && !['workflow', 'campaign', 'automation'].includes(source) && !kind.startsWith('TYPE_ACTIVITY_') && !kind.includes('INTERNAL');
          const row = { userId, at, evidenceId: clean(msg.id), conversationId: convId };
          if (call && (!latestCall || at > latestCall.at)) latestCall = row;
          if (human && (!latestHumanOutbound || at > latestHumanOutbound.at)) latestHumanOutbound = row;
        }
      }
      if (latestCall) inferred = { ...latestCall, source: 'outbound_call' };
      else if (latestHumanOutbound) inferred = { ...latestHumanOutbound, source: 'outbound_message' };
      else if (newestAssignedOpp) inferred = { userId: oppOwner, at: timestamp(newestAssignedOpp.updatedAt || newestAssignedOpp.createdAt), evidenceId: clean(newestAssignedOpp.id), source: 'latest_open_opportunity_owner' };
    }

    const targetOwnerId = oppOwner || contactOwner || clean(inferred?.userId);
    if (!targetOwnerId) { report.skippedNoAgentEvidence++; continue; }
    const targetUser = users.get(targetOwnerId);
    if (!targetUser || !targetUser.active || !targetUser.name) { report.skippedInactiveOrUnknownUser++; continue; }

    const contactConflict = Boolean(contactOwner && oppOwner && contactOwner !== oppOwner);
    if (contactConflict) report.conflictsPreserved++;
    const proposed = [];
    for (const opp of targetOpps) {
      const currentOwner = clean(opp.assignedTo);
      const finalOwnerId = currentOwner || contactOwner || targetOwnerId;
      const finalUser = users.get(finalOwnerId);
      if (!finalUser?.active || !finalUser.name) continue;
      const customOwner = getOwnerField(opp);
      const addAssignedTo = !currentOwner;
      const syncOwnerField = customOwner.toLowerCase() !== finalUser.name.toLowerCase();
      if (addAssignedTo || syncOwnerField) proposed.push({ opp, ownerId: finalOwnerId, ownerName: finalUser.name, addAssignedTo, syncOwnerField });
    }
    const fillContact = !contactOwner && Boolean(oppOwner || inferred?.userId || targetOwnerId);
    if (!proposed.length && !fillContact) continue;
    report.proposedContacts++;
    const row = { contactId, ownerId: targetOwnerId, ownerName: targetUser.name, selectedBy: inferred?.source || (oppOwner ? 'opportunity_assignedTo' : 'contact_assignedTo'), evidenceAt: inferred?.at ? new Date(inferred.at).toISOString() : null, evidenceId: inferred?.evidenceId || null, opportunityIds: proposed.map(x => clean(x.opp.id)), contactWasUnassigned: !contactOwner, contactConflict, updates: proposed.map(x => ({ opportunityId: clean(x.opp.id), assign: x.addAssignedTo, syncOwnerField: x.syncOwnerField })) };
    report.results.push(row);
    if (!apply) continue;

    for (const item of proposed) {
      const payload = { customFields: [{ id: 'Wpg7FGrQTgAY1GoKcdEJ', field_value: item.ownerName }] };
      if (item.addAssignedTo) payload.assignedTo = item.ownerId;
      await api.call(this, 'PUT', `${base}/opportunities/${encodeURIComponent(clean(item.opp.id))}`, payload);
      report.opportunitiesUpdated += item.addAssignedTo ? 1 : 0;
      report.ownerFieldsSynced += item.syncOwnerField ? 1 : 0;
    }
    if (fillContact && !contactConflict) {
      await api.call(this, 'PUT', `${base}/contacts/${encodeURIComponent(contactId)}`, { assignedTo: targetOwnerId });
      report.contactsUpdated++;
    }
    await new Promise(r => setTimeout(r, 200));
  } catch (err) {
    report.errors++;
    report.results.push({ contactId, error: String(err.message || err).slice(0, 240) });
  }
}
return [{ json: report }];
} catch (err) {
  let message = String(err?.message || err);
  try { const secret = String($('Config').first().json.ghlApiKey || ''); if (secret) message = message.split(secret).join('[redacted]'); } catch (_) {}
  return [{ json: { status: 'workflow_error', error: message.slice(0, 400) } }];
}'''

workflow_path = "lt-last-touch-owner-backfill-" + uuid.uuid4().hex
nodes = [
    {"id": str(uuid.uuid4()), "webhookId": str(uuid.uuid4()), "name": "Backfill Webhook", "type": "n8n-nodes-base.webhook", "typeVersion": 2.1, "position": [240, 300], "parameters": {"httpMethod": "POST", "path": workflow_path, "responseMode": "lastNode", "options": {}}},
    {"id": str(uuid.uuid4()), "name": "Daily Last-Touch Owner Sweep", "type": "n8n-nodes-base.scheduleTrigger", "typeVersion": 1.2, "position": [240, 520], "parameters": {"rule": {"interval": [{"field": "cronExpression", "expression": "0 2 * * *"}]}}},
    {"id": str(uuid.uuid4()), "name": "Config", "type": "n8n-nodes-base.set", "typeVersion": 3.4, "position": [460, 300], "parameters": {"mode": "manual", "includeOtherFields": True, "assignments": {"assignments": [{"id": str(uuid.uuid4()), "name": "ghlApiKey", "value": ghl_key, "type": "string"}, {"id": str(uuid.uuid4()), "name": "locationId", "value": "Zwz4relUXVPxx8uohnjV", "type": "string"}]}}},
    {"id": str(uuid.uuid4()), "name": "Resolve and Apply Last-Touch Owners", "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [700, 300], "parameters": {"mode": "runOnceForAllItems", "jsCode": CODE}},
]
connections = {"Backfill Webhook": {"main": [[{"node": "Config", "type": "main", "index": 0}]]}, "Daily Last-Touch Owner Sweep": {"main": [[{"node": "Config", "type": "main", "index": 0}]]}, "Config": {"main": [[{"node": "Resolve and Apply Last-Touch Owners", "type": "main", "index": 0}]]}}
settings = {"executionOrder": "v1", "timezone": "America/Los_Angeles", "saveDataErrorExecution": "none", "saveDataSuccessExecution": "none", "saveManualExecutions": True, "executionTimeout": 300}


def api(path: str, method: str = "GET", body: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(N8N_HOST.rstrip("/") + path, data=data, method=method, headers={"X-N8N-API-KEY": n8n_key, "Accept": "application/json", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60, context=ssl.create_default_context()) as response:
            text = response.read().decode("utf-8")
            return response.status, json.loads(text) if text else {}
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"n8n API {exc.code}: {text[:1000]}") from exc


workflow_id = EXISTING_WORKFLOW_ID
try:
    api(f"/api/v1/workflows/{workflow_id}/deactivate", "POST")
except RuntimeError:
    pass
api(f"/api/v1/workflows/{workflow_id}", "PUT", {"name": WORKFLOW_NAME, "nodes": nodes, "connections": connections, "settings": settings})
_, readback = api(f"/api/v1/workflows/{workflow_id}")
if readback.get("name") != WORKFLOW_NAME or len(readback.get("nodes", [])) != 4:
    raise SystemExit("Workflow saved but graph readback failed; it remains inactive")
if any(node.get("type") == "n8n-nodes-base.code" and "lastMessageDate" not in node.get("parameters", {}).get("jsCode", "") for node in readback.get("nodes", [])):
    raise SystemExit("Code-node readback failed; it remains inactive")

api(f"/api/v1/workflows/{workflow_id}/activate", "POST")
_, readback = api(f"/api/v1/workflows/{workflow_id}")
print(json.dumps({"workflowId": workflow_id, "name": WORKFLOW_NAME, "active": bool(readback.get("active")), "webhookPath": workflow_path, "defaultMode": "dry-run unless apply=true"}, indent=2))
