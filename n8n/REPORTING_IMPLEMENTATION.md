# LiveTransparent Reporting Implementation

## Purpose
This document is the build scaffold for the reporting stack in n8n.
It is operational, phase-based, and safe to use before the GA4 property ID arrives.

## Build Order
1. Lock report config sync and identifiers.
2. Stand up the GHL report shell and storage path.
3. Wire GHL leads and sales ingest.
4. Wire GA4 ingest once the property ID is available.
5. Wire Search Console ingest.
6. Build the bridge and rollups.
7. Add QA and publish refresh.

Report workflow shells have now been created in n8n, and the GHL-side reporting path is live. `LT - GHL Daily Leads Ingest`, `LT - GHL Daily Sales Ingest`, `LT - Report Attribution Bridge`, `LT - Report Daily Rollups`, `LT - Report QA and Alerts`, and `LT - Report Executive Summary API` are active.
Update: `LT - Report Postgres Bootstrap Apply` is also active and was used to initialize the reporting schema in Postgres.
Update: `LT - GSC Daily Ingest`, `LT - GA4 Daily Ingest`, `LT - Report Config Sync`, `LT - Report Publish Refresh`, and `LT - GHL Executive Report Menu Sync` remain staged or pending external inputs.
Current status: the patched GHL ingest workflows have already been rerun, and the report summary now shows different lead totals for `7d` / `30d` / `90d`.
Current remaining question: `opportunitiesCreated` still reads `193` across all windows while closed-won sales remain `0`, so the next step is to inspect whether that is intended, whether the sales ingest is truncating the opportunity set, or whether the opportunity date filter still needs tightening.

## Live Pattern To Reuse
The live workflows in this repo generally follow this shape:
1. `Cron` or `Webhook` trigger
2. `Set` node for config and runtime flags
3. `Code` node for normalization and validation
4. API write or read/write step
5. `Code` node for response shaping
6. Storage write or upsert
7. Conditional dry-run or error handling
8. Alert output on failure

The executive summary workflow currently returns the live dashboard JSON payload from Postgres and serves it through the report host proxy.

Keep that structure for reporting workflows so the nodes stay easy to inspect and patch.

## Workflow Chain
### 1. `LT - Report Config Sync`
- Status: first real reporting workflow in n8n.
- Purpose: keep all report identifiers and runtime flags in one place.
- Inputs:
  - GHL location id
  - GHL company id
  - report date window rule
  - timezone
  - refresh flags
  - GA4 property id when available
  - Search Console property or verified site
- Outputs:
  - config row in Postgres
  - config snapshot for downstream workflows
- Notes:
  - This workflow can be built and used now.
  - It should run before every ingest and before every publish refresh.

### 2. `LT - GHL Daily Leads Ingest`
- Status: not blocked by GA4.
- Purpose: pull contacts, forms, attribution fields, and routing metadata from GHL.
- Trigger: Cron.
- Outputs:
  - raw lead rows
  - contact-level attribution rows
  - form event rows
- Notes:
  - This can run now.
  - Use it to validate report shape before GA4 is connected.
  - The live workflow has been patched to derive `report_date` from source contact timestamps; rerun it before checking rollups.
  - The workflow has already been manually rerun after the patch.

### 3. `LT - GHL Daily Sales Ingest`
- Status: not blocked by GA4.
- Purpose: pull opportunities, stage movement, and revenue outcomes from GHL.
- Trigger: Cron.
- Outputs:
  - raw opportunity rows
  - stage history rows
  - sales outcome rows
- Notes:
  - This can run now.
  - Keep sales ingest separate from lead ingest.
  - The live workflow is now scaffolded in n8n and remains inactive.
  - The live workflow has been patched to derive row dates from opportunity timestamps; rerun it before checking rollups.
  - The workflow has already been manually rerun after the patch.

### 4. `LT - GA4 Daily Ingest`
- Status: blocked until GA4 property ID arrives.
- Purpose: pull sessions, channels, landing pages, and event data from GA4.
- Trigger: Cron.
- Outputs:
  - raw GA4 rows
  - traffic by day
  - traffic by channel
  - landing page and event rows
- Notes:
  - Build the workflow shell now.
  - Leave the property id field empty or disabled until Cameron provides it.

### 5. `LT - GSC Daily Ingest`
- Status: not blocked by GA4, but requires verified Search Console access.
- Purpose: pull search clicks, impressions, CTR, and position data.
- Trigger: Cron.
- Outputs:
  - raw GSC rows
  - query-level rows
  - page-level rows
- Notes:
  - This can be built in parallel with the GHL workflows.

### 6. `LT - Report Attribution Bridge`
- Status: partially blocked by GA4 for the traffic side.
- Purpose: join traffic, lead, and sales records into one report-ready bridge.
- Trigger: after raw ingest or on schedule.
- Outputs:
  - traffic-to-lead bridge rows
  - lead-to-sale bridge rows
  - attribution confidence rows
- Notes:
  - GHL-only bridging can start now.
  - GA4-backed bridging starts after the property ID arrives.
  - The live workflow is now scaffolded in n8n and writes GHL-only bridge rows.

### 7. `LT - Report Daily Rollups`
- Status: partially blocked by GA4 for full traffic metrics.
- Purpose: aggregate dashboard-ready metrics.
- Trigger: after bridge success.
- Outputs:
  - daily summary rows
  - channel summary rows
  - pipeline summary rows
  - traffic, lead, and sales KPI rows
- Notes:
  - GHL-only rollups can start now.
  - Full report rollups wait for GA4.
  - The live workflow is now scaffolded in n8n and writes GHL-only interim rollups.

### 8. `LT - Report QA and Alerts`
- Status: not blocked by GA4.
- Purpose: validate totals, freshness, schema shape, and missing identifiers.
- Trigger: after rollups and on schedule.
- Outputs:
  - sync health rows
  - error rows
  - alert payloads
- Notes:
  - This now exists as a real starter chain in n8n.

### 9. `LT - Report Publish Refresh`
- Status: not blocked by GA4 if the publish surface is GHL-centric.
- Purpose: refresh the visible report surface after a good run.
- Trigger: after rollups or on demand.
- Outputs:
  - dashboard refresh marker
  - cache invalidation marker
  - optional GHL note or task if needed
- Notes:
  - This now exists as a real starter chain in n8n.
  - The publish target should be the embedded dashboard host used by GHL.
  - Recommended stable path pattern: `https://reports.livetransparent.com/embed/executive`
  - Keep query parameters for view, date range, and embed mode stable so the iframe URL does not churn.

### 10. `LT - GHL Executive Report Menu Sync`
- Status: created in n8n and inactive.
- Purpose: create or update the GHL `Executive Report` custom menu link that launches the embedded report host.
- Trigger: manual webhook/provision call.
- Outputs:
  - created or updated custom menu response from GHL
- Inputs:
  - agency token
  - location id
  - menu title
  - embedded report URL
  - optional menu id for updates
- Notes:
  - This is the live automation path for getting the report entry into GHL.
  - It still requires a valid agency token to succeed.

## Operational Scope By Phase
### Can start now
- report config sync
- GHL lead ingest
- GHL sales ingest
- GSC ingest, if the property is already verified
- bridge table design
- rollup table design
- QA and alert scaffolding
- publish refresh scaffolding
- embedded report shell and sidebar launch point

### Wait for GA4 property ID
- GA4 daily ingest
- GA4 side of attribution bridge
- GA4 traffic rollups
- any metrics that depend on GA4 session or landing page data

## Node Shape
Use this generic pattern for each workflow:
1. `Cron` or `Webhook`
2. `Set Config`
3. `Code Normalize / Validate`
4. `HTTP Request` or built-in app read
5. `Code` reshape step
6. `Postgres` insert, update, or upsert
7. `IF` or `Switch` for dry-run, gating, or failure routing
8. `Slack` or other alert output if needed

For GHL workflows, the read step can be the GHL app node or an HTTP Request to the GHL API.
For GA4 and GSC, prefer HTTP Request plus a normalization Code step.

## Minimal Execution Checklist
### Before GA4 property ID arrives
- [x] Create the report config row and runtime flags.
- [x] Create the GHL leads ingest shell.
- [x] Create the GHL sales ingest shell.
- [x] Create the QA workflow skeleton.
- [x] Create the report publish refresh shell.
- [ ] Decide where report snapshots will live in GHL, if any.
- [ ] Confirm the Search Console property and access level.
- [ ] Define the daily report date window and timezone rule.
- [ ] Inspect whether `opportunitiesCreated` should stay at `193` across all ranges or be range-filtered, and verify the sales ingest is not dropping later pages.
- [ ] Confirm whether the zero sales total is expected for the current dataset.

### After GA4 property ID arrives
- [ ] Enable GA4 ingest with the property id.
- [ ] Test GA4 raw pull with one known date window.
- [ ] Connect GA4 rows into the bridge workflow.
- [ ] Verify rollups against GHL contact and opportunity totals.
- [ ] Turn on publish refresh for the report surface.

## What Is Already Prepared
- `LT - Report Config Sync` now writes the runtime report config and source health rows.
- `LT - Report QA and Alerts` now checks source-health freshness and blocked states.
- `LT - Report Publish Refresh` now writes the latest publish refresh marker into Postgres.
- `LT - GHL Daily Leads Ingest` now writes raw GHL contact rows into the reporting tables.
- `LT - GHL Daily Sales Ingest` now writes raw GHL opportunity rows into the reporting tables.
- `LT - GSC Daily Ingest` now records a blocked pending-state run until Search Console access is confirmed.
- `LT - GA4 Daily Ingest` now records a blocked pending-state run until the GA4 property ID arrives.
- `LT - Report Attribution Bridge` now writes GHL-only bridge rows and run status.
- `LT - Report Daily Rollups` now writes GHL-only interim rollups and run status.
- The Postgres reporting bootstrap exists in `postgres/reporting-bootstrap.sql`.
- The embedded report host contract exists in `reporting/Embedded_Report_Host_Spec.md`.
- The report workflow inventory is tracked in `reporting/Workflow_Shell_Index.md`.
- The sidebar custom menu entry is already live; keep this workflow as the sync mechanism for future updates.

## Error Handling
- Do not let one source block the others.
- Write raw data first, bridge second, rollups third.
- Use idempotent upserts keyed by source plus report date.
- Mark missing or empty pulls explicitly.
- Record schema drift, stale data, and partial run status.
- Skip GA4-dependent steps when the property id is missing.

## Reference Files
- `../LiveTransparent Report Plan.md`
- `../GHL Live Transparent CRM/Report Data Contract.md`
- `../GHL Live Transparent CRM/Operating Snapshot.md`
- `../postgres/reporting-bootstrap.sql`
- `reporting/README.md`
- `reporting/Embedded_Report_Host_Spec.md`
- `reporting/Workflow_Shell_Index.md`
- `nodes/google-analytics/REFERENCE.md`
- `nodes/search-console/REFERENCE.md`
- `nodes/ghl/REFERENCE.md`
