# LiveTransparent Report Plan

## Goal
Build the executive report in the mockup as a repeatable data pipeline:

- Traffic comes from GA4 and Search Console.
- Leads and sales come from GHL.
- Postgres is the reporting store.
- n8n orchestrates ingestion, normalization, rollups, and alerts.

## Build Principles

- Do not force traffic reporting to live only in GHL.
- Treat GHL as the source of truth for contacts, opportunities, pipeline movement, and revenue.
- Treat GA4 as the source of truth for sessions, channels, landing pages, and on-site events.
- Treat GSC as the source of truth for query visibility, clicks, impressions, and page performance.
- Preserve unmatched records instead of inventing joins.
- Keep every metric traceable back to a raw pull.

## Execution Split

### Can Execute Now

- GHL report shell, navigation, and operational config.
- Postgres schema, raw pulls, bridges, rollups, and QA tables.
- n8n workflow scaffolding for sync, rollup, alerting, and publish refresh.
- Any GHL-side report setup that does not require GA4 API access.

### Already Built or Prepared

- GHL report shell, navigation, and operational config.
- Live n8n starter chains for:
  - report config sync
  - GHL lead ingest
  - GHL sales ingest
  - GSC ingest scaffold
  - GA4 ingest scaffold
  - attribution bridge
  - daily rollups
  - QA and alerts
  - publish refresh
- Postgres reporting bootstrap schema and raw/bridge/rollup tables.
- Embedded report host contract and iframe URL pattern.
- GHL custom menu / sidebar entry is live in GHL as `Executive Report`.
- Report host scaffold is present in `reports/` with a Dockerfile and nginx config.

### Blocked

- GA4 Data API wiring.
- Any GA4 metric pull that depends on the property ID.

## Recommended Architecture

### Storage Layers

- Raw layer: append-only source pulls from GA4, GSC, and GHL.
- Bridge layer: attribution and identity matching between traffic and CRM data.
- Rollup layer: daily summary tables for the dashboard.
- Ops layer: workflow logs, sync checkpoints, and error rows.

### Orchestration Layer

- Use n8n for all scheduled pulls, transforms, retries, and alerting.
- Keep each source isolated so one failure does not block the others.
- Use Postgres for persistence and dashboard queries.
- Use a separate report surface for presentation, then load it in GHL through a Custom Menu Link iframe.

## Intended Workflow List

1. `LT - Report Config Sync`
   - Loads report settings, date windows, source IDs, and runtime flags.
   - Seeds or updates config rows in Postgres.

2. `LT - GA4 Daily Ingest`
   - Pulls GA4 sessions, channels, landing pages, and core event slices.
   - Writes raw rows to Postgres.

3. `LT - GSC Daily Ingest`
   - Pulls query, page, and site-level search performance data.
   - Writes raw rows to Postgres.

4. `LT - GHL Daily Leads Ingest`
   - Pulls new contacts, contact attribution fields, and form-origin data.
   - Writes raw rows to Postgres.

5. `LT - GHL Daily Sales Ingest`
   - Pulls opportunities, stage history, and closed-won revenue data.
   - Writes raw rows to Postgres.

6. `LT - Report Attribution Bridge`
   - Matches traffic to leads using UTM, landing page, and identity rules.
   - Produces bridge rows for matched and unmatched records.

7. `LT - Report Daily Rollups`
   - Aggregates raw and bridge data into dashboard-ready daily tables.
   - Upserts rollups by date, source, and dimension keys.

8. `LT - Report QA and Alerts`
   - Compares source totals to loaded totals.
   - Sends alerts on missing data, zero rows, schema drift, or stale syncs.

9. `LT - Report Publish Refresh`
   - Refreshes the dashboard surface or cache layer after successful rollups.
   - Can be the same workflow as rollups if the implementation stays small.

## Data Model

### Raw Tables

- `report_raw_ga4_sessions`
- `report_raw_ga4_pages`
- `report_raw_ga4_events`
- `report_raw_gsc_queries`
- `report_raw_gsc_pages`
- `report_raw_gsc_site`
- `report_raw_ghl_contacts`
- `report_raw_ghl_opportunities`
- `report_raw_ghl_pipeline_history`
- `report_raw_ghl_forms`

Recommended columns for raw tables:

- `id`
- `source_system`
- `source_key`
- `source_date`
- `payload_json`
- `dimensions_json`
- `metrics_json`
- `loaded_at`
- `batch_id`
- `run_id`

### Bridge Tables

- `report_bridge_traffic_to_lead`
- `report_bridge_lead_to_sale`
- `report_bridge_identity_map`

Recommended bridge keys:

- `report_date`
- `ga_session_id`
- `utm_source`
- `utm_medium`
- `utm_campaign`
- `landing_page`
- `ghl_contact_id`
- `ghl_opportunity_id`
- `match_confidence`
- `match_rule`

### Rollup Tables

- `report_daily_summary`
- `report_channel_daily_summary`
- `report_funnel_daily_summary`
- `report_pipeline_daily_summary`
- `report_stage_daily_summary`
- `report_utm_daily_summary`
- `report_landing_page_daily_summary`

Recommended rollup dimensions:

- `report_date`
- `traffic_source`
- `channel`
- `source`
- `medium`
- `campaign`
- `landing_page`
- `pipeline`
- `stage`
- `lead_temperature`
- `geo`

### Operations Tables

- `report_sync_runs`
- `report_sync_errors`
- `report_sync_watermarks`
- `report_source_health`

Recommended operational fields:

- `workflow_name`
- `source_system`
- `status`
- `started_at`
- `finished_at`
- `row_count`
- `error_count`
- `cursor_value`
- `error_message`
- `retry_count`

## Failure Handling

### Source Pull Rules

- Pull each source independently.
- Write raw data first, then compute bridge rows, then rollups.
- Use idempotent upserts keyed by source record identity plus report date.
- If a source fails, mark only that source failed for the run.
- Do not block GA4, GSC, or GHL together unless the shared config step fails.

### Retry Rules

- Retry transient API failures with bounded exponential backoff.
- Stop after a small fixed retry count.
- Capture the final error in `report_sync_errors`.
- Keep the failed raw batch isolated for reprocessing.

### Backfill Rules

- Support daily backfill by date range.
- Backfill should be safe to re-run.
- Backfill should not overwrite unmatched bridge rows without a reason code.

### Data Quality Rules

- Flag zero-row pulls.
- Flag schema drift when a payload changes shape.
- Flag missing UTM values separately from true unmatched traffic.
- Flag stale data when the last successful sync exceeds the allowed window.

## Execution Order

### Phase 1: Lock Scope

- Confirm whether v1 includes GSC on day one or starts with GA4 + GHL.
- Confirm that the dashboard is embedded in GHL through a Custom Menu Link.
- Confirm the date granularity for v1: daily only.

### Phase 2: Stand Up Storage

- Create raw tables.
- Create bridge tables.
- Create rollup tables.
- Create ops tables.

### Phase 3: Build Source Ingest Workflows

- Build GA4 ingest.
- Build GSC ingest.
- Build GHL lead ingest.
- Build GHL sales ingest.

### Phase 4: Build Bridges and Rollups

- Map traffic to leads with UTM and landing-page logic.
- Map leads to sales with contact and opportunity logic.
- Aggregate daily summary tables.

### Phase 5: Add QA and Alerts

- Compare loaded totals against source totals.
- Alert on missing data or stale refreshes.
- Log all workflow runs.

### Phase 6: Publish the Dashboard

- Render the executive headline cards.
- Render the channel breakdown, drop-off, and quality panels.
- Expose source labels on every widget.
- Publish the dashboard through the `Executive Report` custom menu link in GHL.

## v1 Minimum

- GA4 sessions by channel
- GA4 landing pages
- GSC clicks and impressions
- GHL contacts created
- GHL opportunities created
- GHL closed won revenue
- One dashboard surface with source labels

## Acceptance Criteria

- Every metric in the dashboard can be traced to a raw source row.
- GA4, GSC, and GHL pulls run independently.
- Failed runs are visible and retryable.
- Daily rollups can be regenerated safely.
- The report can be audited without manual spreadsheet steps.

## External Dependency

- GA4 property ID is waiting on Cameron.
- Do not start the GA4 Data API wiring until that property ID is confirmed.
- Keep the measurement ID and stream ID in the setup notes, but treat them as separate from the property ID.

## Current Status

- The reporting stack is now live for the GHL side end to end, including the executive summary webhook and Postgres bootstrap.
- GHL-only bridge, rollup, QA, and summary logic are active in n8n.
- The remaining work after the property ID arrives is to enable the GA4 ingest path, backfill, and verify the traffic-side joins.
- The preferred GHL delivery pattern is now fixed: custom menu link, embedded iframe, external report host, Postgres-backed data.
