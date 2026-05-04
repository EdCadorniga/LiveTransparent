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
- **Meta Ads ingest** — API access validated on 2026-05-05. The Executive Report should prioritize attribution visibility first: which Meta-tagged ads/campaigns are driving website visits and downstream calls/opportunities. Spend/cost reporting can remain deferred.

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
   - Original workflow `OtqWjqGXZC3OcrXP` was later archived after editor corruption.
   - Replacement workflow `osIJOgBmWITF5Yuv` was rebuilt with the same node chain and renamed back to the canonical workflow name.

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

Meta attribution note for v1:

- The Executive Report can surface Meta results from the existing GA4 + GHL attribution path without waiting for spend rollups.
- Treat Meta raw API pulls as supporting truth and source-health validation.
- Treat GA4 UTM/session rows plus GHL bridge matches as the user-facing answer for “which ads are driving visits and calls.”

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
- Surface Meta-tagged UTM rows in the Executive Report as a dedicated attribution panel for visits and downstream opportunities/booked-intent.

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

## Next-Phase Reporting Roadmap

### Reporting Goals

- Measure ad performance separately from CRM performance.
- Measure how efficiently traffic becomes contacts inside GHL.
- Keep GA4 as traffic truth, GHL as CRM truth, and add ad-platform spend as a separate truth layer.

### Operating Questions

- Which channels and campaigns are bringing qualified traffic?
- How well are sessions turning into contacts in GHL?
- How well are GHL contacts turning into opportunities, meetings, and wins?
- Where is the funnel leaking: traffic, forms, contact creation, qualification, meetings, or sales?

### Phase 7: Funnel Efficiency Layer

- Add first-class conversion metrics to the executive summary:
  - `session_to_contact_rate`
  - `contact_to_opportunity_rate`
  - `opportunity_to_meeting_rate`
  - `meeting_to_closed_won_rate`
- Add a dedicated contact-capture panel:
  - sessions
  - form submissions
  - contacts created
  - opportunities created
  - meetings booked
  - closed won count
- Keep these metrics date-windowed and traceable to `report_daily_summary`.

### Phase 8: Attribution Quality Layer

- Add attribution coverage metrics:
  - percent of contacts with known source/medium
  - percent of opportunities tied back to an attributed contact
  - percent of revenue tied to an attributed path
- Distinguish true unattributed traffic from missing tracking data.

### Phase 9: Paid Ads Performance Layer

- Add Meta Ads ingest first, then Google Ads ingest.
- Store:
  - spend
  - impressions
  - clicks
  - CPC
  - CPM
  - CTR
  - campaign / ad set / ad names
- Add cost efficiency metrics:
  - cost per contact
  - cost per opportunity
  - cost per meeting
  - revenue per dollar / ROAS where possible

### Phase 10: Matched Funnel Views

- Build matched funnel views by:
  - channel
  - campaign
  - landing page
- Show:
  - sessions
  - contacts
  - opportunities
  - meetings
  - wins
  - revenue
- This becomes the main answer to: "How are the ads doing?" and "How good are we at bringing contacts into GHL?"

## External Dependencies

- GA4 property ID is waiting on Cameron.
- Do not start the GA4 Data API wiring until that property ID is confirmed.
- Keep the measurement ID and stream ID in the setup notes, but treat them as separate from the property ID.

### Meta Ads API access

- Access was validated on 2026-05-05 with system user token and active ad account `act_2186975138800404`.
- Required permissions are `ads_read` and `read_insights`.
- Root `.env` reference keys are `META_TOKEN` and `META_AD_ACCOUNT_ID`.
- Direct Graph API smoke tests succeeded for `/me`, `/act_2186975138800404`, and `/act_2186975138800404/insights`.

### GA4 service account & Coolify secrets

When GA4 ingest is enabled we require a GCP service account and a secure way to provide its JSON key to the runtime. Recommended delivery and runtime wiring:

- Create a service account (example name: `livetransparent-ga4-ingest`) in the GCP project that owns the GA4 property.
- Enable the Google Analytics Data API in that project.
- In the GA UI (Admin → Property → Property Access Management) add the service account email with role: Analytics Viewer.
- Create and download a JSON key for the service account. Do NOT commit this JSON to the repo or share it insecurely.
- In Coolify (n8n service) add the following environment entries (plain KEY=VALUE). Mark the JSON value as a secret/protected value and do not commit it:

  - GA4_PROPERTY_ID=434472183
  - GA4_MEASUREMENT_ID=G-YYF078K942
  - GA4_STREAM_ID=7792630179
  - GA4_SERVICE_ACCOUNT_JSON_PATH=/etc/ga4/sa.json
  - GA4_INGEST_ENABLED=false
  - GA4_USE_UNIPILE=false
  - UNIPILE_API_BASE=
  - GA4_SERVICE_ACCOUNT_JSON=<paste full service account JSON here; mark secret>

- Startup snippet (prepend to the service start command) to write the secret JSON to a file before n8n starts:

  /bin/sh -lc 'mkdir -p /etc/ga4 && if [ -n "$GA4_SERVICE_ACCOUNT_JSON" ]; then printf "%s" "$GA4_SERVICE_ACCOUNT_JSON" > /etc/ga4/sa.json && chmod 600 /etc/ga4/sa.json; fi; export GA4_SERVICE_ACCOUNT_JSON_PATH=/etc/ga4/sa.json; exec <ORIGINAL_CMD>'

  Replace `<ORIGINAL_CMD>` with the existing container start command. This writes the secret into `/etc/ga4/sa.json` and sets `GA4_SERVICE_ACCOUNT_JSON_PATH` so the ingest workflow can authenticate.

- Verification: after deploy confirm the container starts, then (if you have shell access) run `ls -l /etc/ga4 && jq -r .client_email /etc/ga4/sa.json` to confirm the key is present and readable only by the container.

This ensures the GA4 service account key is available to n8n without committing secrets to source control and aligns with the ingest wiring described elsewhere in this plan.

## Current Status (updated 2026-04-30)

- The report host is live and secure; the GHL `Executive Report` menu entry points at it.
- The executive summary webhook is live and returns GHL-first report JSON from Postgres.
- All report workflows are now active and published in n8n:
  - `LT - GHL Daily Leads Ingest` (`osIJOgBmWITF5Yuv`) — rebuilt replacement for archived `OtqWjqGXZC3OcrXP`
  - `LT - GHL Daily Sales Ingest` (`aYT5oHcgmBALzHy5`)
  - `LT - Report Attribution Bridge` (`Y0TU7Il71JswxOBp`)
  - `LT - Report Daily Rollups` (`EUeOiRttoVLQ9zF9`)
  - `LT - Report Executive Summary API` (`Bukc0mgOD2r7V6ED`)
  - `LT - Report QA and Alerts` (`M5mXcDTFSko6EdHb`)
  - `LT - Report Config Sync` (`aomO3Z4AXJIgEvvN`)
  - `LT - Report Publish Refresh` (`3gXztCnBEN6sGINb`)
  - `LT - Report Postgres Bootstrap Apply` (`3XHThUiUSNa4sTb9`)
- Current live summary example after the GA4 + rollup fixes:
  - `7d` leads: live endpoint dependent
  - `30d` leads: `111`
  - `30d` opportunitiesCreated: `1344`
  - `closed_won`: `0`
  - `sessions`: `1626`
- `closed_won = 0` has been verified as genuine against the current data.
- GA4 is live and feeding the executive report.
- `LT - Report Daily Rollups` was restored, republished, and verified on 2026-05-02 with the daily-summary correction logic integrated into production.
- `LT - Report Daily Rollups` now preserves GA-backed channel, UTM, landing-page, and daily traffic rows so the executive report keeps Channel Breakdown after rollups run.
- Funnel-efficiency metrics are now live in the executive summary API and embedded report: `sessionToFormRate`, `sessionToContactRate`, `contactToOpportunityRate`, `opportunityToMeetingRate`, and `meetingToClosedWonRate`.
- `contactToOpportunityRate` now uses a contact-safe cohort metric instead of the raw multi-opportunity rollup total.
- Current cohort result: the 30-day new-contact cohort is presently returning `0` matched contact-to-opportunity progression, so the next cleanup is attribution and identity coverage rather than funnel math itself.
- Current attribution coverage result: the same 30-day cohort now has `97` contacts, `45` with usable source fields, `45` with attributed bridge matches, and `22` with lead-to-sale matches after rebuilding the bridge with normalized raw contact ids and stored-field fallbacks.
- The preferred GHL delivery pattern: custom menu link, embedded iframe, external report host, Postgres-backed data.

## Immediate Execution Sequence

1. Expand the contact-capture panel to break conversion by channel and landing page.
2. Build matched funnel views by channel, campaign, and landing page.
3. Build Meta Ads ingest for spend, clicks, impressions, and cost metrics using the validated system user token and active ad account `act_2186975138800404`.
4. Finish SimpleTexting secret hardening.
5. Build GHL-to-LinkedIn automation.
6. GSC — retry access and enable the blocked ingest workflow.
