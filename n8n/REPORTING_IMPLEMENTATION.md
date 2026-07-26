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

Current live status as of 2026-07-21:
- **Active**: `LT - GHL Daily Leads Ingest`, `LT - GHL Daily Sales Ingest`, `LT - Report Attribution Bridge`, `LT - Report Daily Rollups`, `LT - Report Executive Summary API`, `LT - Report QA and Alerts`, `LT - Report Config Sync`, `LT - Report Publish Refresh`, `LT - Report Postgres Bootstrap Apply`.
- **GA4 Active**: `LT - GA4 Daily Ingest` (`6pCSGzFmrMDFL5Yq`), `LT - GA4 Traffic Rollup Bridge` (`0P2AZcQYWYZjXbRi`).
- **GSC Active**: `LT - GSC Daily Ingest` (`xHqmCC1vOeZ11gCd`) writes raw query/page/site rows.
- **Email Events Active**: `LT - Email Event Ingest` (`ZrqFN8qLKO8eVHDc`) receives GHL email event webhooks (opens, clicks, bounces, unsubscribes, spam) and stores in `Email_Events`. Email campaign metrics (sent, opened, clicked, bounced) are now rolled into `report_daily_summary` and surfaced in the Executive Report.
- **Inactive/deferred**: `LT - GHL Executive Report Menu Sync` (one-time provision, inactive).
Current status: GA4 is live, GSC raw ingest is live, the rollups draft has been restored from the active workflow definition, and the published Rollups workflow now includes the daily-summary correction logic directly.
The published Rollups workflow preserves GA-backed summary, channel, UTM, and landing-page rows so Channel Breakdown and traffic totals survive the CRM rollup pass. GSC search metrics now render in the Executive Report, with GA4 Organic Search users used as the unique-visitor proxy.

### New Sections Added 2026-07-21
- **Email campaign metrics**: `emails_sent`, `emails_opened`, `emails_clicked`, `emails_bounced`, `emails_unsubscribed`, `emails_complained` columns added to `report_daily_summary`. Populated from `DAN_Release_Log`, `Emerald_Release_Log`, and `Email_Events`.
- **LinkedIn outreach funnel**: `linkedinFunnel` key in the Executive Report; aggregated from `linkedin_connection_state` (ready → requested → connected → DM active → completed).
- **Vapi campaign breakdown**: `vapiCampaignBreakdown` (all-time call metrics by campaign) and `vapiQueueDistribution` (pending queue by campaign) from `voice_call_attempt` JOIN `voice_call_queue`.
- **MQL/SQL tracking**: `mqlSummary` (opportunities in Warm pipeline Qualified (MQL) stage) and `sqlContacts` (contacts with SQL tag) surfaced in the report.
- **AI qualification and SDR boundary**: report Janvi-qualified cannabis contacts promoted to Sales Outreach, AI-pending/unverified contacts remaining in Warm/Vapi, rejected contacts suppressed from Vapi, and Sales Outreach owner-alignment outcomes.
- **Pool distribution**: `poolDistribution` with counts for brands_pool, dispensaries_pool, vapi_campaign_brand, vapi_campaign_dispensary.
- **Stage name resolution**: Pipeline and stage names now resolved from GHL stage IDs via CASE mapping, fixing stagemover count (was 0, now 93+).
- **Voice dialer**: `GHL - Create Call Note` node set to `onError: continueRegularOutput` to prevent execution errors from blocking calls.

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
  - On 2026-07-25, the live `Fetch + Normalize Leads` node was hardened against GHL HTTP 429 responses with direct `this.helpers.httpRequest` calls, bounded `Retry-After`/exponential backoff, and a 500 ms delay between pagination pages.
  - Validation execution `241894` completed successfully with 500 contacts and all downstream writes successful.

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
   - The live workflow is active and derives row dates from opportunity timestamps.

### 4. `LT - GA4 Daily Ingest`
- Status: active in production.
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
- Status: active raw ingest; summary surfacing is still pending.
- Purpose: pull search clicks, impressions, CTR, and position data.
- Trigger: Cron.
- Outputs:
  - raw GSC rows
  - query-level rows
  - page-level rows
- Notes:
  - This can be built in parallel with the GHL workflows.

### 6. `LT - Report Attribution Bridge`
- Status: active.
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
- Status: active.
- Purpose: aggregate dashboard-ready metrics.
- Trigger: after bridge success.
- Outputs:
  - daily summary rows
  - channel summary rows
  - pipeline summary rows
  - traffic, lead, and sales KPI rows
- Notes:
- GHL-only rollups are live.
- GA4 and GSC are both live in raw form, and the Executive Report now shows GSC clicks/impressions/CTR/position plus an estimated unique visitors proxy from GA4 Organic Search users.
- The live workflow draft was restored on 2026-05-02 after a broken `PLACEHOLDER_SQL_CODE` save.
- The active workflow remains safe.
- The Rollups draft was manually validated on 2026-05-02 after integrating the same logic into `Build Rollup SQL`.
- The updated Rollups version was published and verified successfully on 2026-05-02.

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
### Already built and running
- report config sync
- GHL leads ingest
- GHL sales ingest
- attribution bridge (GHL-only)
- daily rollups (GHL-only)
- executive summary API
- QA and alerts
- publish refresh
- Postgres bootstrap apply
- embedded report shell and sidebar launch point
- GSC raw ingest writes Search Console rows and source health; GA4 ingest and the GA4 bridge are live.

### Current Live Sources
- GA4 daily ingest (live data)
- GA4 side of attribution bridge
- GA4 traffic rollups
- Search Console raw ingest (live; proxy surfaced in report)
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
### Current Live Checklist
- [x] Create the report config row and runtime flags.
- [x] Create and publish the GHL leads ingest.
- [x] Create and publish the GHL sales ingest.
- [x] Create and publish the QA workflow.
- [x] Create and publish the report publish refresh.
- [x] Decide where report snapshots will live in GHL.
- [x] Search Console raw ingest is active; the Executive Report now surfaces an estimated unique visitors proxy from GA4 Organic Search users.
- [x] Define the daily report date window and timezone rule.
- [x] Fix `opportunitiesCreated` inflation with `LT - Report Rollup Corrections`.
- [x] Verify `closed_won = 0` is genuine.

### Live Verification
- [x] Enable GA4 ingest with the property id.
- [x] Test GA4 raw pull with one known date window.
- [x] Connect GA4 rows into the bridge workflow.
- [x] Verify rollups against GHL contact and opportunity totals.
- [x] Turn on publish refresh for the report surface.

## What Is Already Prepared
- All report workflows are active and published in n8n (leads ingest, sales ingest, attribution bridge, daily rollups, executive summary API, QA and alerts, config sync, publish refresh, Postgres bootstrap apply).
- `LT - GSC Daily Ingest` writes raw Search Console rows and source health, while `LT - GA4 Daily Ingest` and the GA4 bridge are live; the Executive Report search section now includes an estimated unique visitors proxy from GA4 Organic Search users.
- The Postgres reporting bootstrap exists in `postgres/reporting-bootstrap.sql`.
- The embedded report host contract exists in `reporting/Embedded_Report_Host_Spec.md`.
- The report workflow inventory is tracked in `reporting/Workflow_Shell_Index.md`.
- The sidebar custom menu entry is already live; keep the menu sync workflow for future updates.

## Error Handling
- Do not let one source block the others.
- Write raw data first, bridge second, rollups third.
- Use idempotent upserts keyed by source plus report date.
- Mark missing or empty pulls explicitly.
- Record schema drift, stale data, and partial run status.
- Skip GA4-dependent steps when the property id is missing.

## Reference Files
- `../Project Status and Next Steps.md`
- `../GHL Live Transparent CRM/Report Data Contract.md`
- `../GHL Live Transparent CRM/Operating Snapshot.md`
- `../postgres/reporting-bootstrap.sql`
- `reporting/README.md`
- `reporting/Embedded_Report_Host_Spec.md`
- `reporting/Workflow_Shell_Index.md`
- `nodes/google-analytics/REFERENCE.md`
- `nodes/search-console/REFERENCE.md`
- `nodes/ghl/REFERENCE.md`
