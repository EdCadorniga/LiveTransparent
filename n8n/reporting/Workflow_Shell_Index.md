# LiveTransparent Report Workflow Shell Index

This file is the short checklist of reporting workflows that should exist in n8n.
Use it together with the workflow spec and the Postgres bootstrap.

## Current Status (2026-05-13)
All report workflows are active and published in n8n:
- `LT - GHL Daily Leads Ingest` (`osIJOgBmWITF5Yuv`) — rebuilt replacement
- `LT - GHL Daily Sales Ingest` (`aYT5oHcgmBALzHy5`)
- `LT - Report Attribution Bridge` (`Y0TU7Il71JswxOBp`)
- `LT - Report Daily Rollups` (`EUeOiRttoVLQ9zF9`)
- `LT - Report Executive Summary API` (`Bukc0mgOD2r7V6ED`)
- `LT - Report QA and Alerts` (`M5mXcDTFSko6EdHb`)
- `LT - Report Config Sync` (`aomO3Z4AXJIgEvvN`)
- `LT - Report Publish Refresh` (`3gXztCnBEN6sGINb`)
- `LT - Report Postgres Bootstrap Apply` (`3XHThUiUSNa4sTb9`)

Deferred: `LT - GHL Executive Report Menu Sync`.
`LT - GSC Daily Ingest` is active raw ingest; its raw rows are live, but the Executive Report search section still needs summary-rollup wiring.

Known cleanup completed: `LT - Report Daily Rollups` was restored, republished, and verified on 2026-05-02 with the daily-summary correction logic folded back into the main workflow.

## Shells To Create

### `LT - Report Config Sync`
- Trigger: Manual or daily Cron
- Live n8n ID: `aomO3Z4AXJIgEvvN`
- Status: active

### `LT - GHL Daily Leads Ingest`
- Trigger: Cron
- Live n8n ID: `osIJOgBmWITF5Yuv`
- Status: active (rebuilt replacement for archived `OtqWjqGXZC3OcrXP`)

### `LT - GHL Daily Sales Ingest`
- Trigger: Cron
- First nodes: Trigger -> Set Config -> Code Normalize -> GHL Read -> Postgres Upsert
- Live n8n ID: `aYT5oHcgmBALzHy5`
- Status: created in n8n, active, real starter chain

### `LT - GSC Daily Ingest`
- Trigger: Cron
- First nodes: Trigger -> Set Config -> Code Normalize -> HTTP Request -> Postgres Upsert
- Live n8n ID: `xHqmCC1vOeZ11gCd`
- Status: active raw ingest, writing query/page/site rows and source health

### `LT - GA4 Daily Ingest`
- Trigger: Cron
- First nodes: Trigger -> Set Config -> Code Guard -> HTTP Request -> Postgres Upsert
- Live n8n ID: `6pCSGzFmrMDFL5Yq`
- Status: active in production

### `LT - Report Attribution Bridge`
- Trigger: After raw ingest
- First nodes: Trigger -> Set Config -> Code Match -> Postgres Upsert
- Live n8n ID: `Y0TU7Il71JswxOBp`
- Status: created in n8n, active, real starter chain, ready now for GHL-only bridging

### `LT - Report Daily Rollups`
- Trigger: After bridge success
- First nodes: Trigger -> Set Config -> Code Aggregate -> Postgres Upsert
- Live n8n ID: `EUeOiRttoVLQ9zF9`
- Status: active, republished on 2026-05-02 with integrated daily-summary fix logic

### `LT - Report Rollup Corrections`
- Trigger: After main rollup or daily Cron
- First nodes: Trigger -> Config -> Code Fixes -> Postgres Execute
- Live n8n ID: `5u70GKgWzEHJ5l4B`
- Status: inactive
- Purpose: retired handoff workflow previously used to patch `report_daily_summary` before the fix was folded into Rollups

### `LT - Report QA and Alerts`
- Trigger: After rollups and on schedule
- First nodes: Trigger -> Set Config -> Code Check -> Alert
- Live n8n ID: `M5mXcDTFSko6EdHb`
- Status: created in n8n, active, real starter chain

### `LT - Report Publish Refresh`
- Trigger: After successful rollups
- Live n8n ID: `3gXztCnBEN6sGINb`
- Status: active

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
- First nodes: Trigger -> Config -> Normalize -> Build Query -> Query Summary -> Shape Response -> Respond
- Live n8n ID: `Bukc0mgOD2r7V6ED`
- Status: created in n8n, active, returns the dashboard JSON payload
- Sections added 2026-07-21: email metrics, LinkedIn funnel, Vapi campaign/queue, MQL/SQL, pool distribution, stage mover fix

### `LT - Report Postgres Bootstrap Apply`
- Trigger: Webhook
- First nodes: Trigger -> Apply Bootstrap SQL -> Respond
- Live n8n ID: `3XHThUiUSNa4sTb9`
- Status: created in n8n, active, initializes the reporting schema in Postgres

## Preparation Rule

- Keep the GHL reporting path live and treat GA4/GSC as separate live sources when summary surfacing needs to be rechecked.
- The GHL reporting path and summary API are live and can continue to evolve independently.
