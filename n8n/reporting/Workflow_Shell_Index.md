# LiveTransparent Report Workflow Shell Index

This file is the short checklist of reporting workflows that should exist in n8n.
Use it together with the workflow spec and the Postgres bootstrap.

Note:
- Several reporting workflows are now live and active in n8n.
- `LT - GHL Daily Leads Ingest`, `LT - GHL Daily Sales Ingest`, `LT - Report Attribution Bridge`, `LT - Report Daily Rollups`, `LT - Report QA and Alerts`, and `LT - Report Executive Summary API` are active.
- `LT - Report Postgres Bootstrap Apply` is active as the one-time bootstrap helper.
- `LT - GSC Daily Ingest`, `LT - GA4 Daily Ingest`, `LT - Report Config Sync`, `LT - Report Publish Refresh`, and `LT - GHL Executive Report Menu Sync` remain staged or pending their external inputs.
- Keep GA4 and GSC deferred until the corresponding property/access inputs are finalized.

## Shells To Create

### `LT - Report Config Sync`
- Trigger: Manual or daily Cron
- First nodes: Trigger -> Set Config -> Code Validate -> Postgres Upsert
- Live n8n ID: `aomO3Z4AXJIgEvvN`
- Status: created in n8n, inactive, real starter chain, still missing a trigger node for activation

### `LT - GHL Daily Leads Ingest`
- Trigger: Cron
- First nodes: Trigger -> Set Config -> Code Normalize -> GHL Read -> Postgres Upsert
- Live n8n ID: `OtqWjqGXZC3OcrXP`
- Status: created in n8n, active

### `LT - GHL Daily Sales Ingest`
- Trigger: Cron
- First nodes: Trigger -> Set Config -> Code Normalize -> GHL Read -> Postgres Upsert
- Live n8n ID: `aYT5oHcgmBALzHy5`
- Status: created in n8n, active, real starter chain

### `LT - GSC Daily Ingest`
- Trigger: Cron
- First nodes: Trigger -> Set Config -> Code Normalize -> HTTP Request -> Postgres Upsert
- Live n8n ID: `if0Siw6KzlBItEbd`
- Status: created in n8n, inactive, blocked pending Search Console property access

### `LT - GA4 Daily Ingest`
- Trigger: Cron
- First nodes: Trigger -> Set Config -> Code Guard -> HTTP Request -> Postgres Upsert
- Live n8n ID: `6pCSGzFmrMDFL5Yq`
- Status: created in n8n, inactive, blocked on GA4 property ID

### `LT - Report Attribution Bridge`
- Trigger: After raw ingest
- First nodes: Trigger -> Set Config -> Code Match -> Postgres Upsert
- Live n8n ID: `Y0TU7Il71JswxOBp`
- Status: created in n8n, active, real starter chain, ready now for GHL-only bridging

### `LT - Report Daily Rollups`
- Trigger: After bridge success
- First nodes: Trigger -> Set Config -> Code Aggregate -> Postgres Upsert
- Live n8n ID: `EUeOiRttoVLQ9zF9`
- Status: created in n8n, active, real starter chain, ready now for GHL-only rollups

### `LT - Report QA and Alerts`
- Trigger: After rollups and on schedule
- First nodes: Trigger -> Set Config -> Code Check -> Alert
- Live n8n ID: `M5mXcDTFSko6EdHb`
- Status: created in n8n, active, real starter chain

### `LT - Report Publish Refresh`
- Trigger: After successful rollups
- First nodes: Trigger -> Set Config -> Code Refresh -> Publish marker
- Live n8n ID: `3gXztCnBEN6sGINb`
- Status: created in n8n, inactive, real starter chain, no trigger node yet

### `LT - GHL Executive Report Menu Sync`
- Trigger: Webhook or manual provision call
- First nodes: Trigger -> Set Config -> Code Create/Update Menu -> Response
- Live n8n ID: `8YtaPmPnTXUkBDAd`
- Status: created in n8n, inactive, provisioner for the GHL custom menu entry
- Notes:
  - Requires a valid agency token in the request body.
  - Creates or updates the `Executive Report` menu link that points to the embedded report host.

### `LT - Report Executive Summary API`
- Trigger: Webhook
- First nodes: Trigger -> Config -> Normalize -> Build Query -> Query Summary -> Respond
- Live n8n ID: `Bukc0mgOD2r7V6ED`
- Status: created in n8n, active, returns the dashboard JSON payload

### `LT - Report Postgres Bootstrap Apply`
- Trigger: Webhook
- First nodes: Trigger -> Apply Bootstrap SQL -> Respond
- Live n8n ID: `3XHThUiUSNa4sTb9`
- Status: created in n8n, active, initializes the reporting schema in Postgres

## Preparation Rule

- Keep GA4 and GSC staged until the external inputs arrive.
- The GHL reporting path and summary API are live and can continue to evolve independently.
