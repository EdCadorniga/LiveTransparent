Idempotent SMS send workflow (n8n + Postgres)
============================================

Purpose
-------
Provide an idempotent HTTP endpoint for sending SMS so the same message is not sent multiple times to the same contact. The endpoint performs a single-row INSERT with a unique constraint and only calls SimpleTexting when the INSERT succeeds.

What this adds
- Postgres table: `report_sms_sent` (created in postgres/reporting-bootstrap.sql)
- n8n workflow shape to accept a send request, dedupe via Postgres, call SimpleTexting, and persist provider response.
- GHL-originated sends can use the same boundary by POSTing the contact ID, phone, template key or message, and a stable `campaignKey` / `externalId`.

Postgres contract (already added)
--------------------------------
Table: report_sms_sent

Columns of interest:
- id (uuid)
- contact_id (text)
- phone (text)
- workflow_id (text)
- template_id (text)
- message_hash (text) -- deterministic hash used for idempotency
- sent_at (timestamptz)
- provider_response (jsonb)

Unique constraint: (contact_id, workflow_id, message_hash)

SQL snippets
------------
-- Try to claim this send; if it succeeds we should perform the send.
-- Parameters: $1=contact_id, $2=phone, $3=workflow_id, $4=template_id, $5=message_hash

INSERT INTO report_sms_sent (contact_id, phone, workflow_id, template_id, message_hash)
VALUES ($1, $2, $3, $4, $5)
ON CONFLICT (contact_id, workflow_id, message_hash) DO NOTHING
RETURNING id, sent_at;

-- After sending, update provider_response where id = $1
UPDATE report_sms_sent SET provider_response = $1 WHERE id = $2;

n8n workflow shape (recommended)
--------------------------------
1) HTTP Request Trigger (webhook)
   - Receives JSON: {
       contact_id, phone, workflow_id, template_id, message_body
     }

GHL-originated version of the same contract should also include:
- `source: "ghl_workflow"`
- `campaignKey`
- `externalId`
- `contact` object for note enrichment

2) Function / Code node (compute message_hash)
   - Compute a short deterministic hash of contact_id + workflow_id + template_id + date_bucket
   - Use date_bucket if you want daily dedupe; omit if you want absolute dedupe.

Example node code (Node.js) to compute a truncated sha1 hash and attach to `items[0].json`:

const crypto = require('crypto');
const contactId = $json.contact_id || $json.contactId || items[0].json.contact_id;
const wf = items[0].json.workflow_id;
const tmpl = items[0].json.template_id || '';
// date bucket (YYYYMMDD) prevents more than one send per day for identical template
const dateBucket = new Date().toISOString().slice(0,10).replace(/-/g,'');
const raw = `${contactId}|${wf}|${tmpl}|${dateBucket}`;
const hash = crypto.createHash('sha1').update(raw).digest('hex').slice(0,12);
items[0].json.message_hash = hash;
return items;

3) Postgres node: INSERT ... ON CONFLICT DO NOTHING RETURNING id
   - Use the SQL snippet above; bind parameters from the webhook payload and computed message_hash

4) IF node: check if the INSERT returned a row
   - If yes (new claim) → proceed to send
   - If no (duplicate) → respond with 200 and a body `{ status: 'duplicate', sent_at: existing_sent_at }`

5) HTTP Request node: call SimpleTexting API
   - URL: https://api.simpletexting.com/v1/messages
   - Method: POST
   - Headers: Authorization: Bearer $SIMPLETEXTING_API_KEY
   - Body: JSON { to: phone, message: message_body }

6) Postgres UPDATE node: write provider_response JSON into report_sms_sent for the inserted id

7) Respond node: return JSON with { status: 'sent', id, provider_response }

Notes and recommendations
-------------------------
- Use a short message_hash (12 hex chars) to keep unique constraint values small.
- Date-bucket the hash if you want to allow a contact to receive the same template once per day; omit the bucket for one-time dedupe.
- Keep SIMPLETEXTING_API_KEY in n8n environment (already present in repo root .env).
- Replace any direct SimpleTexting send nodes in GHL workflows with a call to this n8n webhook. This centralizes dedupe logic.
- If GHL must initiate the send, have the GHL workflow POST to this webhook and let n8n call SimpleTexting. Do not try to bypass the webhook with a direct provider call from GHL.

Rollback / re-sends
-------------------
- To re-send a message for a contact+template, delete the matching row from report_sms_sent or insert a new row with a different message_hash (e.g., change date_bucket).

Monitoring
----------
- Add a small QA workflow that checks report_sms_sent for unexpected duplicates (group by contact_id, workflow_id, message_hash count>1) and alerts if found.

If you want, I can create an n8n workflow JSON export matching this shape and add it to the repo; tell me whether you want daily dedupe (one send per day) or absolute dedupe (send only once ever per template per contact).
