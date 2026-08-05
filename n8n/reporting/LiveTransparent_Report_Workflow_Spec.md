# LiveTransparent Report Workflow Spec

## Purpose
This document turns the report plan into a concrete n8n build spec.
Use it to document the current GHL reporting pipeline first, with GA4 live and Search Console raw ingest active, in a way that is:

- source-isolated
- idempotent
- backfill-safe
- auditable back to raw rows

## Scope
The report pipeline is not a GHL-native dashboard.
The current phase is an n8n-orchestrated GHL ingestion and rollup system with Postgres as the reporting store and GHL as the CRM source of truth for leads and sales.
GA4 is live in the current build. Search Console raw ingest is also live, but the Executive Report search panel still needs summary-rollup wiring before it will show populated values.

## Repo Context

- Canonical status doc: `Project Status and Next Steps.md`
- Data contract: `GHL Live Transparent CRM/Report Data Contract.md`
- Postgres bootstrap: `postgres/reporting-bootstrap.sql`
- Embedded host spec: `n8n/reporting/Embedded_Report_Host_Spec.md`
- Reporting index: `n8n/reporting/README.md`
- Workflow shell index: `n8n/reporting/Workflow_Shell_Index.md`
- GA4 reference: `n8n/nodes/google-analytics/REFERENCE.md` (live)
- Search Console reference: `n8n/nodes/search-console/REFERENCE.md` (active raw ingest path)
- GHL reference: `n8n/nodes/ghl/REFERENCE.md`
- Postgres reference: `n8n/nodes/postgres/REFERENCE.md`

## Live n8n Context

The live workflow inventory now has the GHL reporting pipeline in place.
That means this build should extend the live reporting workflows rather than modifying the existing lead-intake or SMS workflows.

Current n8n conventions already in use:

- Webhook -> Config -> Code -> Write -> Summarize
- `Continue On Fail` style isolation for external calls
- Postgres upserts for durable staging
- `availableInMCP = true` on staged workflows when live verification is needed

## Live Outgoing Call Detail Endpoint

The Executive Report has a separate read-only detail workflow in addition to the aggregate summary workflow:

| Item | Value |
|------|-------|
| Workflow | `LT - Report Outgoing Calls Detail` |
| Workflow ID | `VXFHc8IrF9DDEEdj` |
| Production webhook | `GET /webhook/lt-report-outgoing-calls` |
| Report-host route | `GET /api/report/executive/outgoing-calls` |
| Status | Active and published |
| Published version | `d004556d-0b11-4a86-8827-f8f58a1eeee3` |
| Window | Seven most recent completed days, `America/Los_Angeles` |
| Page size | Client requests 100; server clamps to 1-100 |

Node chain:

1. `Outgoing Calls Webhook` accepts GET query parameters.
2. `Normalize Outgoing Calls Request` calculates the fixed completed-day window and clamps `limit`/`offset`.
3. `Query Outgoing Calls` runs parameterized Postgres SQL using the existing `Postgres account` credential.
4. `Build Outgoing Calls Response` maps rows to the stable `{ calls, total, limit, offset, range }` payload.
5. `Respond Outgoing Calls` returns JSON.

The query reads `voice_call_attempt` and joins `voice_call_queue` for campaign and phone context. It calculates duration from `started_at` and `ended_at`, identifies the first attempt per contact, and enriches from the latest `report_raw_ghl_contacts` snapshot. It never writes to the call, queue, GHL, or rollup tables. Empty results still return a valid JSON payload with `calls: []`.

## Design Rules

1. Keep GHL pulls isolated from traffic/search sources, even when those sources are live.
2. Write raw rows before any bridge or rollup work.
3. Use deterministic source keys so reruns do not duplicate rows.
4. Reprocess a small sliding window every day to absorb late-arriving CRM updates.
5. Keep unmatched source rows instead of forcing joins.
6. Push failures into ops tables and alerts, not into the main dashboard tables.

## Suggested Daily Schedule

Use the `America/Los_Angeles` timezone for all report windows.
Run on the most recent complete day by default, with a small backfill overlap:

- GHL leads ingest: re-pull the last 3 complete days plus watermark
- GHL sales ingest: re-pull the last 3 complete days plus watermark
- Bridge and rollups: recompute the last 7 days
- GA4 is live; Search Console raw ingest is active but not yet surfaced in the summary payload

Suggested order:

1. `LT - Report Config Sync`
2. `LT - GHL Daily Leads Ingest`
3. `LT - GHL Daily Sales Ingest`
4. `LT - Report Attribution Bridge`
5. `LT - Report Daily Rollups`
6. `LT - Report QA and Alerts`
7. `LT - Report Publish Refresh`
8. `LT - GA4 Daily Ingest` (active)
9. `LT - GSC Daily Ingest` (active raw ingest; summary pending)

## Workflow-by-Workflow Spec

### 1) `LT - Report Config Sync`

Purpose:
- Store all runtime settings in one place so the rest of the pipeline does not hardcode them.

Trigger:
- Manual run for setup
- Optional daily Cron for drift checks

Reads:
- `Project Status and Next Steps.md`
- `GHL Live Transparent CRM/Report Data Contract.md`

Writes:
- `report_config`
- `report_source_registry`
- `report_sync_watermarks`

Config values to store:
- GA4 property ID
- GA4 measurement ID
- GA4 stream ID
- GSC site property / coverage flag
- GHL location ID
- GHL company ID
- report timezone
- report lag days
- dashboard mode
- alert destination

Failure handling:
- Fail fast if required IDs are missing.
- Mark missing prerequisites explicitly in `report_source_health`.
- Do not start GA4 API pulls until the property ID is present.

Implementation shape:
- `Set` node for config values
- `Code` node to validate prerequisites
- `Postgres` node to upsert config rows
- `Respond to Webhook` or `NoOp` summary if manual

### 2) `LT - GA4 Daily Ingest` (Deferred)

Purpose:
- Pull traffic and engagement data from GA4 once that phase is re-enabled.

Trigger:
- Cron after the data-day boundary in `America/Los_Angeles`

Reads:
- GA4 Data API
- `report_config`
- `report_sync_watermarks`

Writes:
- `report_raw_ga4_sessions`
- `report_raw_ga4_pages`
- `report_raw_ga4_events`
- `report_sync_runs`
- `report_sync_errors`
- `report_source_health`

Data to pull:
- Sessions
- Users
- New users
- Engagement rate
- Channel grouping
- Source / medium / campaign
- Landing pages
- Core conversion events such as form submits and key CTA events

Recommended n8n structure:
- `Cron`
- `Postgres` load config
- `IF` guard for missing property ID
- `HTTP Request` nodes for GA4 reports
- `Code` node to normalize rows
- `Postgres` node to write raw rows
- `Code` node to summarize run

Failure handling:
- If the property ID is missing, write a config-prereq failure and stop.
- If one GA4 report slice fails, continue the other slices and mark the failed slice in ops tables.
- Keep the raw rows for successful slices even when one slice fails.
- Retry transient HTTP failures with a bounded retry count.

Windowing rule:
- Pull a 3-day overlap every day so late GA4 events can be corrected.

### 3) `LT - GSC Daily Ingest` (Active raw ingest, summary pending)

Purpose:
- Pull organic visibility and search performance data from Search Console.

Trigger:
- Cron

Reads:
- Search Console API
- `report_config`
- `report_sync_watermarks`

Writes:
- `report_raw_gsc_queries`
- `report_raw_gsc_pages`
- `report_raw_gsc_site`
- `report_sync_runs`
- `report_sync_errors`
- `report_source_health`

Data to pull:
- Clicks
- Impressions
- CTR
- Average position
- Query-level rows
- Page-level rows
- Site-level totals

Recommended n8n structure:
- `Cron`
- `Postgres` load config
- `IF` guard for missing GSC property/coverage
- `HTTP Request` nodes for query, page, and site analytics
- `Code` node to normalize and bucket dimensions
- `Postgres` node to write raw rows
- `Code` node to summarize run

Failure handling:
- If Search Console is not connected, record a source-health warning and stop only this workflow.
- Keep query/page/site pulls isolated so a failure in one slice does not block the others.
- Alert if the site property is present but returns zero rows for a normal reporting window.

Windowing rule:
- Re-pull the last 7 complete days daily.

### 4) `LT - GHL Daily Leads Ingest`

Purpose:
- Pull contacts, form submissions, and attribution fields from GHL.

Trigger:
- Cron after the config sync or the previous GHL reporting stage

Reads:
- GHL API
- `report_config`
- `report_sync_watermarks`

Writes:
- `report_raw_ghl_contacts`
- `report_raw_ghl_forms`
- `report_bridge_identity_map`
- `report_sync_runs`
- `report_sync_errors`
- `report_source_health`

Data to pull:
- New and updated contacts
- First-touch and last-touch UTM fields
- Warm routing metadata
- Lead temperature
- Form submissions
- Contact creation timestamps
- Contact status / tag context relevant to reporting

Recommended n8n structure:
- `Cron`
- `Postgres` load config
- `HTTP Request` or built-in GHL node for contact search
- `HTTP Request` for form submissions
- `Code` node to normalize contact identity and UTM fields
- `Postgres` node to write raw rows
- `Code` node to update identity map candidates

Failure handling:
- Keep contact ingestion and form ingestion separate inside the workflow.
- If one endpoint fails, write the failure to ops tables and continue the other endpoint if possible.
- Use deterministic keys so reruns do not duplicate contacts or forms.

Windowing rule:
- Re-pull the last 3 complete days plus the watermark overlap.

### 5) `LT - GHL Daily Sales Ingest`

Purpose:
- Pull opportunities, pipeline changes, and revenue events from GHL.

Trigger:
- Cron after leads ingest

Reads:
- GHL API
- `report_config`
- `report_sync_watermarks`

Writes:
- `report_raw_ghl_opportunities`
- `report_raw_ghl_pipeline_history`
- `report_bridge_lead_to_sale`
- `report_sync_runs`
- `report_sync_errors`
- `report_source_health`

Data to pull:
- Opportunities
- Opportunity values
- Pipeline
- Stage
- Stage transition timestamps
- Closed won / closed lost outcomes
- Assigned user where relevant for reporting

Recommended n8n structure:
- `Cron`
- `Postgres` load config
- `HTTP Request` or built-in GHL node for opportunity search
- `Code` node to flatten stage history
- `Postgres` node to write raw opportunity rows
- `Postgres` node to write pipeline history rows
- `Code` node to update sale-bridge candidates
- Paginate the opportunity search until the source set is exhausted; do not assume the first page is complete.

Failure handling:
- Keep opportunity data and stage history separate.
- Continue writing what is available if one slice fails.
- Alert if closed-won revenue is present but stage history cannot be loaded.

Windowing rule:
- Re-pull the last 3 complete days plus the watermark overlap.

### 6) `LT - Report Attribution Bridge`

Purpose:
- Match GHL source and attribution records to leads and leads to sales.

Trigger:
- Run after all raw ingest workflows succeed or partially succeed

Reads:
- `report_raw_ghl_contacts`
- `report_raw_ghl_forms`
- `report_raw_ghl_opportunities`
- `report_raw_ghl_pipeline_history`

Writes:
- `report_bridge_lead_to_sale`
- `report_bridge_identity_map`
- `report_sync_runs`
- `report_sync_errors`

Matching rules:
- Prefer exact email or phone matches when available.
- Fall back to GHL source / medium / campaign plus landing page.
- Use time-window logic when the source signals are strong but the identity is partial.
- Preserve unmatched rows with a reason code.

Recommended n8n structure:
- `Cron` or downstream trigger from rollup workflow
- `Postgres` load the latest raw windows
- `Code` node for join scoring
- `Postgres` write bridge rows
- `Code` node to summarize match rates

Failure handling:
- Do not block on unmatched data.
- Do not force a low-confidence match into a high-confidence bucket.
- Write explicit reason codes such as `missing_email`, `missing_utm`, `landing_page_mismatch`, or `time_window_outside_range`.

### 7) `LT - Report Daily Rollups`

Purpose:
- Build dashboard-ready tables from raw and bridge data.

Trigger:
- After the attribution bridge completes

Reads:
- All raw tables
- All bridge tables

Writes:
- `report_daily_summary`
- `report_channel_daily_summary`
- `report_funnel_daily_summary`
- `report_pipeline_daily_summary`
- `report_stage_daily_summary`
- `report_utm_daily_summary`
- `report_landing_page_daily_summary`
- `report_sync_runs`
- `report_sync_errors`

Rollup outputs to include:
- Lead headline cards
- Sales headline cards
- Channel breakdown
- Funnel conversion rates
- Pipeline stage drop-off
- UTM performance
- Capture and attribution quality metrics

Recommended n8n structure:
- `Cron` or chained execution
- `Postgres` read raw/bridge windows
- `Code` node for aggregation logic
- `Postgres` node for rollup upserts
- `Code` node for summary and row counts

Failure handling:
- Recompute a sliding 7-day window so late-arriving rows are corrected.
- Keep day-level rollups idempotent by primary key.
- If one rollup table fails, record the partial failure and continue the independent rollups where possible.

### 8) `LT - Report QA and Alerts`

Purpose:
- Validate the pipeline and surface failures quickly.

Trigger:
- Immediately after rollups
- Optional standalone nightly check

Reads:
- `report_sync_runs`
- `report_sync_errors`
- `report_sync_watermarks`
- `report_source_health`
- rollup tables

Writes:
- `report_sync_errors`
- `report_source_health`
- optional GHL note/task or Slack alert

Checks to run:
- Zero-row detection
- Stale watermark detection
- Schema drift detection
- Unexpected row-count drop
- Failed source-slice detection

Recommended n8n structure:
- `Cron`
- `Postgres` read last runs and watermarks
- `Code` node to compare thresholds
- `IF` node for alert conditions
- `HTTP Request` or GHL action for alert delivery

Failure handling:
- QA should never suppress a source failure.
- If alert delivery fails, still persist the QA error row.

### 9) `LT - Report Publish Refresh`

Purpose:
- Refresh the user-facing surface after data is complete.

Trigger:
- After QA passes

Reads:
- `report_daily_summary`
- `report_channel_daily_summary`
- `report_funnel_daily_summary`
- `report_pipeline_daily_summary`

Writes:
- dashboard cache refresh signal
- optional GHL-facing link or custom object record

Recommended implementation:
- Keep the executive dashboard outside GHL if the rendering layer is not already built.
- In GHL, surface the dashboard through a custom menu link or embedded page.
- If the report is mirrored into GHL, only mirror the summary data, not the full raw dataset.

Failure handling:
- If refresh fails, do not mark the data pipeline itself as broken.
- Data freshness and dashboard publishing should be separate statuses.

## Table Contract Summary

Raw tables:
- append-only logical snapshots with deterministic upsert keys

Bridge tables:
- explicit matched and unmatched rows

Rollup tables:
- idempotent daily summaries

Ops tables:
- source health, run status, errors, and watermark tracking

## Implementation Order

1. Create the Postgres schema and operational tables.
2. Build `LT - Report Config Sync`.
3. Build `LT - GHL Daily Leads Ingest`.
4. Build `LT - GHL Daily Sales Ingest`.
5. Build `LT - Report Attribution Bridge`.
6. Build `LT - Report Daily Rollups`.
7. Build `LT - Report QA and Alerts`.
8. Build `LT - Report Publish Refresh`.
9. `LT - GA4 Daily Ingest` is already live in the current build.
10. `LT - GSC Daily Ingest` is already live as raw ingest; add summary-rollup wiring if the search section needs to render.
11. Connect the dashboard surface to GHL.

## Missing Inputs

- GA4 property ID, only if traffic reporting needs to be revalidated
- GSC property / site coverage confirmation, only if Search Console ingest needs to be revalidated
- final dashboard host choice
- whether the dashboard is embedded in GHL or linked out

## Acceptance Criteria

- Every dashboard metric can be traced to a raw record.
- GHL ingest independently now; GA4 and GSC raw ingest are already live, and the remaining work is summary surfacing.
- A failure in one source does not block the others.
- Backfills are safe to rerun.
- Rollups can be regenerated from raw data.
- The report can be audited without spreadsheet reconstruction.
