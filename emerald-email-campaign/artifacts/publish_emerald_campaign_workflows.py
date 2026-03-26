import json
import os
from copy import deepcopy

import requests


API_KEY = os.environ.get("N8N_LT_API_KEY", "").strip()
API_BASE = "https://automations.livetransparent.com/api/v1"


HEADERS = {"X-N8N-API-KEY": API_KEY}


def get_workflow(workflow_id: str) -> dict:
    response = requests.get(f"{API_BASE}/workflows/{workflow_id}", headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def list_workflows() -> list[dict]:
    response = requests.get(f"{API_BASE}/workflows", headers=HEADERS, timeout=30)
    response.raise_for_status()
    data = response.json()
    if isinstance(data, dict) and "data" in data:
        return data["data"]
    return data


def upsert_workflow_by_name(name: str, payload: dict, existing_id: str | None = None) -> dict:
    if existing_id:
        response = requests.put(
            f"{API_BASE}/workflows/{existing_id}",
            headers={**HEADERS, "Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    for wf in list_workflows():
        if wf.get("name") == name:
            response = requests.put(
                f"{API_BASE}/workflows/{wf['id']}",
                headers={**HEADERS, "Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=30,
            )
            response.raise_for_status()
            return response.json()

    response = requests.post(
        f"{API_BASE}/workflows",
        headers={**HEADERS, "Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def workflow_payload(source: dict, *, name: str) -> dict:
    return {
        "name": name,
        "nodes": source["nodes"],
        "connections": source["connections"],
        "settings": source.get("settings") or {},
    }


def node_by_name(workflow: dict, name: str) -> dict:
    for node in workflow["nodes"]:
        if node["name"] == name:
            return node
    raise KeyError(name)


def build_snapshot_ingest_workflow(source: dict) -> dict:
    workflow = deepcopy(source)
    workflow["name"] = "LT - Emerald Campaign Snapshot -> Postgres Ingest (Staged)"

    node_by_name(workflow, "Webhook")["parameters"]["path"] = "lt-emerald-campaign-postgres-intake"

    config_assignments = node_by_name(workflow, "Config")["parameters"]["assignments"]["assignments"]
    for assignment in config_assignments:
        if assignment["name"] == "sourceLabel":
            assignment["value"] = "emerald_campaign_snapshot"
        if assignment["name"] == "tableName":
            assignment["value"] = "Emerald_Campaign_Contacts"

    node_by_name(workflow, "Ensure Emerald_Contacts Table")["name"] = "Ensure Emerald_Campaign_Contacts Table"
    node_by_name(workflow, "Upsert Into Emerald_Contacts")["name"] = "Upsert Into Emerald_Campaign_Contacts"

    workflow["connections"]["Build SQL (DryRun Safe)"]["main"][0][0]["node"] = "Ensure Emerald_Campaign_Contacts Table"
    workflow["connections"]["Ensure Emerald_Campaign_Contacts Table"] = workflow["connections"].pop("Ensure Emerald_Contacts Table")
    workflow["connections"]["Ensure Emerald_Campaign_Contacts Table"]["main"][0][0]["node"] = "Restore Build SQL Items"
    workflow["connections"]["Restore Build SQL Items"]["main"][0][0]["node"] = "Upsert Into Emerald_Campaign_Contacts"
    workflow["connections"]["Upsert Into Emerald_Campaign_Contacts"] = workflow["connections"].pop("Upsert Into Emerald_Contacts")
    workflow["connections"]["Upsert Into Emerald_Campaign_Contacts"]["main"][0][0]["node"] = "Summarize"

    node_by_name(workflow, "Ensure Emerald_Campaign_Contacts Table")["parameters"]["query"] = """CREATE TABLE IF NOT EXISTS "Emerald_Campaign_Contacts" (
  id BIGSERIAL PRIMARY KEY,
  record_key TEXT NOT NULL,
  ghl_contact_id TEXT,
  first_name TEXT,
  last_name TEXT,
  full_name TEXT,
  email TEXT,
  phone TEXT,
  created_at_source TIMESTAMPTZ,
  last_activity_source TIMESTAMPTZ,
  tags_raw TEXT,
  bucket TEXT,
  bucket_queue_tag TEXT,
  marketing_sender_email TEXT,
  email_campaign TEXT,
  release_status TEXT DEFAULT 'pending',
  release_tag TEXT,
  released_at TIMESTAMPTZ,
  sender_assigned_at TIMESTAMPTZ,
  raw_payload JSONB,
  ingested_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS record_key TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS ghl_contact_id TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS first_name TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS last_name TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS full_name TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS email TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS phone TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS created_at_source TIMESTAMPTZ;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS last_activity_source TIMESTAMPTZ;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS tags_raw TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS bucket TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS bucket_queue_tag TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS marketing_sender_email TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS email_campaign TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS release_status TEXT DEFAULT 'pending';
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS release_tag TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS released_at TIMESTAMPTZ;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS sender_assigned_at TIMESTAMPTZ;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS raw_payload JSONB;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS ingested_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
CREATE UNIQUE INDEX IF NOT EXISTS emerald_campaign_contacts_uidx_record_key ON "Emerald_Campaign_Contacts" (record_key);
CREATE INDEX IF NOT EXISTS emerald_campaign_contacts_idx_email ON "Emerald_Campaign_Contacts" (email);
CREATE INDEX IF NOT EXISTS emerald_campaign_contacts_idx_bucket ON "Emerald_Campaign_Contacts" (bucket);
"""

    node_by_name(workflow, "Upsert Into Emerald_Campaign_Contacts")["parameters"]["query"] = '={{$json.upsertSql}}'

    node_by_name(workflow, "Build SQL (DryRun Safe)")["parameters"]["jsCode"] = r"""
const input = $json || {};
const source = (input.body && typeof input.body === 'object') ? input.body : input;
const cfg = $item(0).$node['Config'].json || {};

function parseCsv(text) {
  const rows = [];
  let row = [];
  let cell = '';
  let inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    const next = text[i + 1];
    if (inQuotes) {
      if (ch === '"' && next === '"') { cell += '"'; i++; }
      else if (ch === '"') inQuotes = false;
      else cell += ch;
    } else {
      if (ch === '"') inQuotes = true;
      else if (ch === ',') { row.push(cell); cell = ''; }
      else if (ch === '\n') { row.push(cell); rows.push(row); row = []; cell = ''; }
      else if (ch === '\r') {}
      else cell += ch;
    }
  }
  if (cell.length || row.length) { row.push(cell); rows.push(row); }
  return rows;
}

function rowsToObjects(rows) {
  if (!rows.length) return [];
  const headers = rows[0].map((h) => String(h || '').trim());
  const out = [];
  for (let i = 1; i < rows.length; i++) {
    const r = rows[i];
    const obj = {};
    headers.forEach((h, idx) => { if (h) obj[h] = r[idx] ?? ''; });
    const hasAny = Object.values(obj).some((v) => String(v || '').trim() !== '');
    if (hasAny) out.push(obj);
  }
  return out;
}

function nk(s) {
  return String(s || '').toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '');
}

function pick(obj, aliases) {
  const wanted = new Set((aliases || []).map(nk));
  for (const [k, v] of Object.entries(obj || {})) {
    if (wanted.has(nk(k)) && String(v ?? '').trim() !== '') return String(v).trim();
  }
  return '';
}

function lit(v) {
  if (v === null || v === undefined || v === '') return 'NULL';
  if (typeof v === 'number') return Number.isFinite(v) ? String(v) : 'NULL';
  if (typeof v === 'boolean') return v ? 'TRUE' : 'FALSE';
  if (typeof v === 'object') {
    const s = JSON.stringify(v).replace(/'/g, "''");
    return `'${s}'::jsonb`;
  }
  const s = String(v).replace(/'/g, "''");
  return `'${s}'`;
}

function bucketFromTags(tags) {
  const raw = String(tags || '').toLowerCase();
  if (raw.includes('cannabis-retail-mso-executive-1') || raw.includes('cannabis-retail-mso-executive-2')) {
    return { bucket: 'executives_mso', queueTag: 'Enrollment Queue - Emerald - Executives MSO' };
  }
  if (raw.includes('cannabis-retail-sso-executive-1') || raw.includes('cannabis-retail-sso-executive-2')) {
    return { bucket: 'executives_sso', queueTag: 'Enrollment Queue - Emerald - Executives SSO' };
  }
  if (raw.includes('cannabis-retail-mso-marketing-1')) {
    return { bucket: 'marketing_mso', queueTag: 'Enrollment Queue - Emerald - Marketing MSO' };
  }
  if (raw.includes('cannabis-retail-sso-marketing-1')) {
    return { bucket: 'marketing_sso', queueTag: 'Enrollment Queue - Emerald - Marketing SSO' };
  }
  return { bucket: null, queueTag: null };
}

function parseTs(value) {
  const s = String(value || '').trim();
  return s ? s : null;
}

let records = [];
if (Array.isArray(source.records)) {
  records = source.records;
} else if (typeof source.csvText === 'string' && source.csvText.trim() !== '') {
  records = rowsToObjects(parseCsv(source.csvText));
}
if (!records.length) throw new Error('Provide body.records (array) or body.csvText (CSV string)');

const dryRun = (source.dryRun === undefined || source.dryRun === null) ? !!cfg.defaultDryRun : !!source.dryRun;
const tableName = String(source.tableName || cfg.tableName || 'Emerald_Campaign_Contacts').trim();

const cols = [
  'record_key','ghl_contact_id','first_name','last_name','full_name','email','phone',
  'created_at_source','last_activity_source','tags_raw','bucket','bucket_queue_tag',
  'marketing_sender_email','email_campaign','release_status','release_tag',
  'released_at','sender_assigned_at','raw_payload'
];

const updates = cols.filter((c) => !['record_key', 'raw_payload'].includes(c))
  .map((c) => `"${c}" = EXCLUDED."${c}"`)
  .concat(['"raw_payload" = EXCLUDED."raw_payload"', '"updated_at" = NOW()']);

return records.map((rec) => {
  const ghlContactId = pick(rec, ['Contact Id', 'contact_id']) || null;
  const firstName = pick(rec, ['First Name', 'first_name']) || null;
  const lastName = pick(rec, ['Last Name', 'last_name']) || null;
  const email = pick(rec, ['Email', 'email']) || null;
  const phone = pick(rec, ['Phone', 'phone']) || null;
  const tagsRaw = pick(rec, ['Tags', 'tags']) || null;
  const fullName = [firstName, lastName].filter(Boolean).join(' ') || null;
  const bucketMeta = bucketFromTags(tagsRaw);
  const recordKey = ghlContactId || (email ? `email::${email.toLowerCase()}` : `${firstName || ''}::${lastName || ''}::${phone || ''}`);
  const normalized = {
    record_key: recordKey,
    ghl_contact_id: ghlContactId,
    first_name: firstName,
    last_name: lastName,
    full_name: fullName,
    email,
    phone,
    created_at_source: parseTs(pick(rec, ['Created', 'created'])),
    last_activity_source: parseTs(pick(rec, ['Last Activity', 'last_activity'])),
    tags_raw: tagsRaw,
    bucket: bucketMeta.bucket,
    bucket_queue_tag: bucketMeta.queueTag,
    marketing_sender_email: null,
    email_campaign: null,
    release_status: 'pending',
    release_tag: null,
    released_at: null,
    sender_assigned_at: null,
    raw_payload: rec,
  };
  const values = cols.map((c) => lit(normalized[c]));
  const sql = dryRun
    ? 'SELECT 1 AS dry_run;'
    : `INSERT INTO "${tableName}" (${cols.map((c) => `"${c}"`).join(', ')}, "ingested_at", "updated_at")
VALUES (${values.join(', ')}, NOW(), NOW())
ON CONFLICT (record_key) DO UPDATE SET
${updates.join(',\n')};`;

  return { json: { dryRun, tableName, normalized, upsertSql: sql } };
});
"""

    node_by_name(workflow, "Summarize")["parameters"]["jsCode"] = """const sourceItems = $items('Build SQL (DryRun Safe)');
const writeItems = $input.all();
const dryRun = sourceItems.length ? !!sourceItems[0].json.dryRun : true;
const tableName = sourceItems.length ? sourceItems[0].json.tableName : 'Emerald_Campaign_Contacts';
const bucketed = sourceItems.filter((i) => i.json?.normalized?.bucket).length;
return [{ json: { ok: true, dryRun, table: tableName, rowsProcessed: sourceItems.length, rowsBucketed: bucketed, writesExecuted: dryRun ? 0 : writeItems.length, note: dryRun ? 'No rows were written. Set body.dryRun=false after validation to write.' : 'Campaign snapshot rows written to Postgres.' } }];"""

    return workflow


def build_dispatcher_workflow(source: dict) -> dict:
    workflow = deepcopy(source)
    workflow["name"] = "LT - Emerald Campaign Sender Release Dispatcher (Staged)"

    config_assignments = node_by_name(workflow, "Config")["parameters"]["assignments"]["assignments"]
    for assignment in config_assignments:
        if assignment["name"] == "defaultDryRun":
            assignment["value"] = True
        elif assignment["name"] == "queueTag":
            assignment["value"] = "Enrollment Queue - Emerald - Executives MSO"
        elif assignment["name"] == "candidateLimit":
            assignment["value"] = 500
        elif assignment["name"] == "safetyBufferPct":
            assignment["value"] = 0.05
        elif assignment["name"] == "minSafetyBuffer":
            assignment["value"] = 10
        elif assignment["name"] == "warmupStartDate":
            assignment["value"] = "2026-03-27"
        elif assignment["name"] == "warmupWeekOverride":
            assignment["value"] = 0
        elif assignment["name"] == "sendersJson":
            assignment["value"] = json.dumps([
                {"email": "cameron@livetransparent.com", "active": True, "weight": 1, "capWeek1": 300, "capWeek2": 400, "capWeek3": 500},
                {"email": "cameron@livetransparent.co", "active": True, "weight": 1, "capWeek1": 300, "capWeek2": 400, "capWeek3": 500},
                {"email": "cameron@livetransparent.agency", "active": True, "weight": 1, "capWeek1": 300, "capWeek2": 400, "capWeek3": 500},
                {"email": "cameron@livetransparent.org", "active": True, "weight": 1, "capWeek1": 300, "capWeek2": 400, "capWeek3": 500},
            ])

    node_by_name(workflow, "Ensure Release Log Table")["parameters"]["query"] = """CREATE TABLE IF NOT EXISTS "Emerald_Release_Log" (
  id BIGSERIAL PRIMARY KEY,
  campaign_row_id BIGINT UNIQUE,
  bucket TEXT,
  contact_email TEXT,
  ghl_contact_id TEXT,
  sender_email TEXT NOT NULL,
  release_date DATE NOT NULL DEFAULT CURRENT_DATE,
  release_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  status TEXT NOT NULL DEFAULT 'queued',
  run_id TEXT
);
ALTER TABLE "Emerald_Release_Log" ADD COLUMN IF NOT EXISTS campaign_row_id BIGINT;
ALTER TABLE "Emerald_Release_Log" ADD COLUMN IF NOT EXISTS bucket TEXT;
ALTER TABLE "Emerald_Release_Log" ADD COLUMN IF NOT EXISTS contact_email TEXT;
ALTER TABLE "Emerald_Release_Log" ADD COLUMN IF NOT EXISTS ghl_contact_id TEXT;
ALTER TABLE "Emerald_Release_Log" ADD COLUMN IF NOT EXISTS sender_email TEXT;
ALTER TABLE "Emerald_Release_Log" ADD COLUMN IF NOT EXISTS release_date DATE NOT NULL DEFAULT CURRENT_DATE;
ALTER TABLE "Emerald_Release_Log" ADD COLUMN IF NOT EXISTS release_ts TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE "Emerald_Release_Log" ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'queued';
ALTER TABLE "Emerald_Release_Log" ADD COLUMN IF NOT EXISTS run_id TEXT;
CREATE UNIQUE INDEX IF NOT EXISTS emerald_release_log_uidx_campaign_row_id ON "Emerald_Release_Log" (campaign_row_id);
CREATE INDEX IF NOT EXISTS emerald_release_log_idx_sender_date ON "Emerald_Release_Log" (sender_email, release_date);"""

    node_by_name(workflow, "Fetch Emerald Candidates")["parameters"]["query"] = """WITH ranked AS (
  SELECT
    e.id AS campaign_row_id,
    e.ghl_contact_id,
    e.first_name,
    e.last_name,
    e.full_name,
    e.email,
    e.phone,
    e.tags_raw,
    e.bucket,
    e.bucket_queue_tag,
    e.marketing_sender_email,
    e.email_campaign,
    ROW_NUMBER() OVER (
      PARTITION BY e.bucket
      ORDER BY e.id ASC
    ) AS bucket_rank
  FROM "Emerald_Campaign_Contacts" e
  WHERE COALESCE(e.email,'') <> ''
    AND COALESCE(e.bucket,'') <> ''
    AND COALESCE(e.release_status,'pending') <> 'released'
    AND NOT EXISTS (
      SELECT 1
      FROM "Emerald_Release_Log" r
      WHERE r.campaign_row_id = e.id
    )
)
SELECT
  campaign_row_id,
  ghl_contact_id,
  first_name,
  last_name,
  full_name,
  email,
  phone,
  tags_raw,
  bucket,
  bucket_queue_tag,
  marketing_sender_email,
  email_campaign
FROM ranked
ORDER BY
  bucket_rank ASC,
  CASE bucket
    WHEN 'executives_mso' THEN 1
    WHEN 'executives_sso' THEN 2
    WHEN 'marketing_mso' THEN 3
    WHEN 'marketing_sso' THEN 4
    ELSE 5
  END ASC,
  campaign_row_id ASC
LIMIT {{$item(0).$node["Config"].json.candidateLimit}};"""

    node_by_name(workflow, "Estimate InFlight Due Today")["parameters"]["query"] = """SELECT sender_email, due_today
FROM (
  SELECT sender_email, COUNT(*)::int AS due_today
  FROM "Emerald_Release_Log"
  WHERE release_date IN (
    CURRENT_DATE,
    CURRENT_DATE - INTERVAL '2 day',
    CURRENT_DATE - INTERVAL '4 day'
  )
  GROUP BY sender_email
  UNION ALL
  SELECT '__none__'::text AS sender_email, 0::int AS due_today
) x;"""

    node_by_name(workflow, "Count Unreleased Candidates")["parameters"]["query"] = """SELECT COUNT(*)::int AS total_unreleased
FROM "Emerald_Campaign_Contacts" e
WHERE COALESCE(e.email,'') <> ''
  AND COALESCE(e.bucket,'') <> ''
  AND COALESCE(e.release_status,'pending') <> 'released'
  AND NOT EXISTS (
    SELECT 1
    FROM "Emerald_Release_Log" r
    WHERE r.campaign_row_id = e.id
  );"""

    node_by_name(workflow, "Write Release Log")["parameters"]["query"] = """INSERT INTO "Emerald_Release_Log"
  (campaign_row_id, bucket, contact_email, ghl_contact_id, sender_email, release_date, release_ts, status, run_id)
VALUES
  ({{$json.campaign_row_id}}, {{$json.bucket ? "'" + $json.bucket.replace(/'/g, "''") + "'" : 'NULL'}}, {{$json.email ? "'" + $json.email.replace(/'/g, "''") + "'" : 'NULL'}}, {{$json.contact_id ? "'" + $json.contact_id.replace(/'/g, "''") + "'" : 'NULL'}}, {{$json.sender_email ? "'" + $json.sender_email.replace(/'/g, "''") + "'" : 'NULL'}}, CURRENT_DATE, NOW(), {{$json.status ? "'" + $json.status.replace(/'/g, "''") + "'" : "'queued'"}}, {{$json.run_id ? "'" + $json.run_id.replace(/'/g, "''") + "'" : 'NULL'}})
ON CONFLICT (campaign_row_id) DO NOTHING;"""

    node_by_name(workflow, "Dispatch + Queue (DryRun Safe)")["parameters"]["jsCode"] = r"""
const cfg = $item(0).$node['Config'].json || {};
const dryRun = !!cfg.defaultDryRun;
const locationId = String(cfg.locationId || '').trim();
const apiBaseUrl = String(cfg.apiBaseUrl || 'https://services.leadconnectorhq.com').replace(/\/$/, '');
const apiKey = String(cfg.apiKey || '').trim();
const senderFieldName = String(cfg.senderFieldName || 'marketing_sender_email').trim();
const queueTagByBucket = {
  executives_mso: 'Enrollment Queue - Emerald - Executives MSO',
  executives_sso: 'Enrollment Queue - Emerald - Executives SSO',
  marketing_mso: 'Enrollment Queue - Emerald - Marketing MSO',
  marketing_sso: 'Enrollment Queue - Emerald - Marketing SSO',
};

if (!locationId) throw new Error('Missing locationId');
if (!dryRun && !apiKey) throw new Error('Missing apiKey in live mode');

const nowEt = new Date(new Date().toLocaleString('en-US', { timeZone: 'America/New_York' }));
const nowPt = new Date(new Date().toLocaleString('en-US', { timeZone: 'America/Los_Angeles' }));
const etHour = nowEt.getHours();
const ptHour = nowPt.getHours();
const isSundayEt = nowEt.getDay() === 0;
const withinDispatchWindow = !isSundayEt && etHour >= 8 && ptHour < 17;

let senders = [];
try {
  senders = JSON.parse(String(cfg.sendersJson || '[]'));
} catch {
  throw new Error('Invalid sendersJson');
}

const warmupStartDate = String(cfg.warmupStartDate || '').trim();
const warmupWeekOverride = Number(cfg.warmupWeekOverride || 0);
function getWarmupStage() {
  if (warmupWeekOverride >= 1 && warmupWeekOverride <= 3) return Math.trunc(warmupWeekOverride);
  if (!warmupStartDate) return 1;
  const start = new Date(`${warmupStartDate}T00:00:00Z`);
  if (Number.isNaN(start.getTime())) return 1;
  const elapsedDays = Math.max(0, Math.floor((Date.now() - start.getTime()) / 86400000));
  if (elapsedDays < 7) return 1;
  if (elapsedDays < 14) return 2;
  return 3;
}
const warmupStage = getWarmupStage();

senders = senders.filter((s) => s && s.active !== false && s.email).map((s) => ({
  email: String(s.email).toLowerCase().trim(),
  weight: Math.max(1, Math.trunc(Number(s.weight || 1))),
  cap: warmupStage <= 1
    ? Number(s.capWeek1 || s.cap || 300)
    : warmupStage === 2
      ? Number(s.capWeek2 || s.cap || 400)
      : Number(s.capWeek3 || s.cap || 500),
}));
if (!senders.length) throw new Error('No active senders');

const candidates = $items('Fetch Emerald Candidates').map((i) => i.json || {});
const inflight = $items('Estimate InFlight Due Today').map((i) => i.json || {});
const backlogTotal = Number($items('Count Unreleased Candidates')[0]?.json?.total_unreleased || 0);
const inflightMap = new Map(inflight.map((r) => [String(r.sender_email || '').toLowerCase(), Number(r.due_today || 0)]));

const minSafety = Math.max(1, Math.trunc(Number(cfg.minSafetyBuffer || 10)));
const pctSafety = Number(cfg.safetyBufferPct || 0.05);
for (const s of senders) {
  const safety = Math.max(minSafety, Math.round(s.cap * pctSafety));
  s.remaining = Math.max(0, s.cap - Number(inflightMap.get(s.email) || 0) - safety);
  s.safetyBuffer = safety;
  s.inFlightDueToday = Number(inflightMap.get(s.email) || 0);
}

const ring = [];
for (const s of senders) for (let i = 0; i < s.weight; i++) ring.push(s.email);
function hashString(str) { let h = 0; const s = String(str || ''); for (let i = 0; i < s.length; i++) h = ((h << 5) - h + s.charCodeAt(i)) | 0; return Math.abs(h); }
function pickSender(seedRaw) {
  if (!ring.length) return '';
  const seed = Math.abs(Number(seedRaw || 0)) || 0;
  const start = seed % ring.length;
  for (let i = 0; i < ring.length; i++) {
    const email = ring[(start + i) % ring.length];
    const sender = senders.find((x) => x.email === email);
    if (sender && sender.remaining > 0) { sender.remaining -= 1; return sender.email; }
  }
  return '';
}

async function doHttpRequest(options) {
  if (typeof $httpRequest === 'function') return await $httpRequest(options);
  if (this?.helpers?.httpRequest) return await this.helpers.httpRequest(options);
  throw new Error('HTTP helper not available');
}
async function apiRequest(method, path, body) {
  const options = { method, url: `${apiBaseUrl}${path}`, headers: { Authorization: `Bearer ${apiKey}`, Version: '2021-07-28', 'Content-Type': 'application/json', Accept: 'application/json' }, json: true };
  if (body !== undefined) options.body = body;
  try {
    const data = await doHttpRequest.call(this, options);
    return { ok: true, data };
  } catch (err) {
    return { ok: false, data: err?.response?.body || err?.message || err };
  }
}

function normalizeTags(rawTags) {
  return Array.isArray(rawTags) ? rawTags : String(rawTags || '').split(',').map((t) => t.trim()).filter(Boolean);
}

function hasTag(tags, target) {
  const wanted = String(target || '').toLowerCase();
  return normalizeTags(tags).some((t) => String(t || '').toLowerCase() === wanted);
}

function customFieldValue(contact, fieldName) {
  const fields = Array.isArray(contact?.customFields) ? contact.customFields : [];
  const wanted = String(fieldName || '').trim().toLowerCase();
  const hit = fields.find((f) => String(f?.name || '').trim().toLowerCase() === wanted);
  return hit?.value ?? '';
}

let senderFieldId = '';
if (!dryRun) {
  const cf = await apiRequest('GET', `/locations/${locationId}/customFields?model=contact`);
  if (!cf.ok) throw new Error(`Failed custom fields lookup: ${JSON.stringify(cf.data)}`);
  const arr = Array.isArray(cf.data?.customFields) ? cf.data.customFields : Array.isArray(cf.data?.data?.customFields) ? cf.data.data.customFields : Array.isArray(cf.data?.data) ? cf.data.data : [];
  senderFieldId = arr.find((f) => String(f?.name || '').trim() === senderFieldName)?.id || '';
  if (!senderFieldId) throw new Error(`Missing GHL field: ${senderFieldName}`);
}

const runId = `${new Date().toISOString()}__emerald_campaign_sender_release`;
const out = [];
if (!withinDispatchWindow) {
  out.push({ json: { status: 'summary', summary: { ok: true, dryRun, runId, windowOpen: false, windowLabel: 'Mon-Sat, 8:00 AM ET to 5:00 PM PT', sundayBlocked: isSundayEt, currentEtHour: etHour, currentPtHour: ptHour, candidates: 0, totalUnreleased: backlogTotal, backlogBeyondBatch: backlogTotal, planned: 0, queued: 0, deferred: 0, errors: 0, warnings: [isSundayEt ? 'SUNDAY_BLOCKED: no dispatch on Sundays.' : 'DISPATCH_WINDOW_CLOSED: no contacts dispatched outside Mon-Sat 8:00 AM ET to 5:00 PM PT.'], senders: senders.map((s) => ({ email: s.email, cap: s.cap, inFlightDueToday: s.inFlightDueToday, safetyBuffer: s.safetyBuffer, remainingAfterPlan: s.remaining })) } } });
  return out;
}

for (const c of candidates) {
  const rowId = Number(c.campaign_row_id || 0);
  const email = String(c.email || '').trim();
  const bucket = String(c.bucket || '').trim();
  const queueTag = queueTagByBucket[bucket] || String(c.bucket_queue_tag || '').trim();
  const contactId = String(c.ghl_contact_id || '').trim();

  if (!email || !bucket || !queueTag || !contactId) {
    out.push({ json: { status: 'skipped_incomplete_candidate', campaign_row_id: rowId || null, email, bucket, contact_id: contactId } });
    continue;
  }

  const sender = pickSender(rowId || hashString(email));
  if (!sender) {
    out.push({ json: { status: 'deferred_no_capacity', campaign_row_id: rowId, email, bucket } });
    continue;
  }

  if (dryRun) {
    out.push({ json: { status: 'planned', campaign_row_id: rowId, email, bucket, queue_tag: queueTag, sender_email: sender, contact_id: contactId, run_id: runId } });
    continue;
  }

  const live = await apiRequest('GET', `/contacts/${contactId}`);
  if (!live.ok) {
    out.push({ json: { status: 'error_fetch_contact', campaign_row_id: rowId, email, bucket, sender_email: sender, contact_id: contactId, details: live.data } });
    continue;
  }

  const contact = live.data?.contact || live.data || {};
  const tags = contact.tags || [];
  const dnd = contact.dnd === true || contact.DND === true;
  const emailCampaign = String(customFieldValue(contact, 'Email Campaign') || contact.emailCampaign || '').trim();

  const blocked = (
    hasTag(tags, 'seq enrolled - cannabis ads') ||
    hasTag(tags, 'seq variant a') ||
    hasTag(tags, 'seq variant b') ||
    hasTag(tags, 'seq enrolled - emerald') ||
    hasTag(tags, 'do not nurture') ||
    emailCampaign.toLowerCase() === 'cannabis ads sequence' ||
    dnd
  );

  if (blocked) {
    out.push({ json: { status: 'suppressed_existing_campaign_state', campaign_row_id: rowId, email, bucket, contact_id: contactId } });
    continue;
  }

  const setField = await apiRequest('PUT', `/contacts/${contactId}`, { customFields: [{ id: senderFieldId, value: sender }] });
  if (!setField.ok) {
    out.push({ json: { status: 'error_set_sender', campaign_row_id: rowId, email, bucket, sender_email: sender, contact_id: contactId, details: setField.data } });
    continue;
  }

  const tag = await apiRequest('POST', `/contacts/${contactId}/tags`, { tags: [queueTag] });
  if (!tag.ok) {
    out.push({ json: { status: 'error_add_queue_tag', campaign_row_id: rowId, email, bucket, sender_email: sender, contact_id: contactId, details: tag.data } });
    continue;
  }

  out.push({ json: { status: 'queued', campaign_row_id: rowId, email, bucket, queue_tag: queueTag, sender_email: sender, contact_id: contactId, run_id: runId } });
}

const warnings = [];
if (dryRun) warnings.push('DRY_RUN_ACTIVE: no GHL writes or release log inserts are executed.');
warnings.push('GHL_WORKFLOWS_STILL_REQUIRE_QUEUE_TAG_TRIGGER_WIRING.');
out.push({ json: { status: 'summary', summary: { ok: true, dryRun, runId, windowOpen: true, windowLabel: 'Mon-Sat, 8:00 AM ET to 5:00 PM PT', sundayBlocked: isSundayEt, currentEtHour: etHour, currentPtHour: ptHour, candidates: candidates.length, totalUnreleased: backlogTotal, backlogBeyondBatch: Math.max(0, backlogTotal - candidates.length), planned: out.filter((x) => x.json.status === 'planned').length, queued: out.filter((x) => x.json.status === 'queued').length, deferred: out.filter((x) => String(x.json.status || '').startsWith('deferred_')).length, errors: out.filter((x) => String(x.json.status || '').startsWith('error_')).length, warnings, senders: senders.map((s) => ({ email: s.email, cap: s.cap, inFlightDueToday: s.inFlightDueToday, safetyBuffer: s.safetyBuffer, remainingAfterPlan: s.remaining })) } } });
return out;
"""

    node_by_name(workflow, "Only Queued")["parameters"]["jsCode"] = "return $input.all().filter(i => (i.json || {}).status === 'queued').map(i => ({ json: i.json }));"
    node_by_name(workflow, "Summary")["parameters"]["jsCode"] = """const rows = $items('Dispatch + Queue (DryRun Safe)').map((i) => i.json || {});
const summary = rows.find((r) => r.status === 'summary') || null;
const sample = rows.filter((r) => r.status !== 'summary').slice(0, 20);
return [{ json: { ok: true, summary: summary?.summary || null, sample } }];"""

    return workflow


def main() -> None:
    if not API_KEY:
        raise SystemExit("Missing N8N_LT_API_KEY environment variable")

    ingest_source = get_workflow("mSegmpMUd0DRwFEx")
    dispatcher_source = get_workflow("8UXlpoMJnQ229AuG")

    new_ingest = build_snapshot_ingest_workflow(ingest_source)
    updated_dispatcher = build_dispatcher_workflow(dispatcher_source)

    created_ingest = upsert_workflow_by_name(new_ingest["name"], workflow_payload(new_ingest, name=new_ingest["name"]))
    updated_dispatcher_result = upsert_workflow_by_name(
        updated_dispatcher["name"],
        workflow_payload(updated_dispatcher, name=updated_dispatcher["name"]),
        existing_id=dispatcher_source["id"],
    )

    print(json.dumps({
        "created_or_updated_snapshot_ingest": {
            "id": created_ingest.get("id"),
            "name": created_ingest.get("name"),
            "active": created_ingest.get("active"),
        },
        "updated_dispatcher": {
            "id": updated_dispatcher_result.get("id"),
            "name": updated_dispatcher_result.get("name"),
            "active": updated_dispatcher_result.get("active"),
        }
    }, indent=2))


if __name__ == "__main__":
    main()
