# LiveTransparent Report Host

This folder holds the external dashboard surface that GHL will load inside an iframe.

## Canonical Route

- `https://reports.livetransparent.com/embed/executive`

## Current Status

- The host shell is prepared in repo.
- The public host serves build stamp `2026-07-31-v10-partnership`; the campaign/channel table, selected-period controls, prior-period comparison, and partnership attribution are live.
- The report host is now deployment-ready with `docker-compose.yml`, `Dockerfile`, `nginx.conf`, and `index.html`.
- The preferred GHL entry point is a Custom Menu Link that opens this page in an embedded iframe.
- The report data store remains Postgres.
- n8n writes the raw data, bridge rows, rollups, QA rows, and publish markers.
- The live executive summary webhook is wired to the report host and serves JSON from the Postgres reporting tables. GA4 traffic is ingested daily and bridged into the rollup tables (recorded visits, users, engaged_sessions, engagement_rate) alongside GHL CRM data.
- The Executive Report now surfaces a Meta attribution panel using the live summary payload. It is intentionally focused on which Meta-tagged ads/campaigns are driving recorded visits and downstream opportunities, not spend.
- The Postgres reporting bootstrap has been applied to the live database.
- GHL leads/sales/report workflows are live and active.
- GA4 is now live and flowing to the executive report (recorded visits, users, engagement by channel). GSC raw ingest is also live, and the search section now shows native GSC performance plus an estimated unique visitors proxy from GA4 Organic Search users.
- `LT - Report Daily Rollups` was restored, republished, and verified on 2026-05-02 with the daily-summary dedupe and stage-aware win logic integrated into production.
- `LT - Report Daily Rollups` now preserves GA-backed channel, UTM, landing-page, and daily traffic rows so the report host keeps live Channel Breakdown after rollups run.
- `LT - Report Rollup Corrections` has been deactivated because the production Rollups workflow now owns those fixes.
- The Executive Report now surfaces email campaign metrics (sent, opened, clicked, bounced, unsubscribed, complained) with computed engagement rates. Data sourced from `report_daily_summary` (emails_* columns), populated from `DAN_Release_Log`, `Emerald_Release_Log`, and `Email_Events`.
- LinkedIn outreach funnel metrics (`linkedinFunnel`) are now available, aggregated from `linkedin_connection_state` showing the full funnel: ready → requested → connected → DM active → completed.
- Vapi voice campaign breakdown (`vapiCampaignBreakdown`) and queue distribution (`vapiQueueDistribution`) are now surfaced from `voice_call_attempt` and `voice_call_queue`.
- A separate live campaign-channel endpoint (`/webhook/lt-report-campaign-channel-summary`) returns date-filtered named rows for DAN, Emerald, SMS, LinkedIn, and Vapi. DAN uses release-log campaign fields, Emerald uses bucket/enrollment data, SMS uses `campaign_key`, LinkedIn uses append-only activity events joined to Brand/Dispensary source pools, and Vapi uses queue campaign IDs.
- The campaign-channel endpoint returns its selected `window`, channel, campaign, SMS metrics, email metrics/rates, LinkedIn DM/reply metrics, and Vapi metrics. Rates are deliberately `null` when the campaign sent denominator is unavailable; the report renders those as `—` rather than inventing a percentage.
- Catalog rows for `General outbound`, `Partnership emails`, `xyz`, and `abc` are intentionally present but remain zero until matching source events exist. Historical email events can also have opens/clicks without a matching send row; those are retained as source-coverage limitations.
- Historical campaign engagement is limited by `Email_Events` coverage. The event-ingest path had no executions for the tested 2026-07-20 through 2026-07-26 window, while later windows contain live opened/bounced events. The report therefore preserves zero counts for periods with no stored events instead of fabricating rates.
- A parallel native GHL custom report was created at report ID `6a67dce4a51a4360c60963a3`. It is intended for Campaign Opportunities, Accepted emails, Opened emails, SMS by status, and Outgoing calls by status. Its current widget configuration has not been verified because the authenticated browser URL returned 404 plus Firebase token/permission errors. Do not treat the native report as campaign-level verified until an authenticated GHL UI session confirms the widgets.
- MQL summary (`mqlSummary`) tracks active and total opportunities in the Warm pipeline Qualified (MQL) stage. SQL contacts (`sqlContacts`) counts contacts with the SQL tag.
- AI qualification reporting must distinguish Janvi-qualified cannabis contacts promoted to Sales Outreach from AI-pending/unverified contacts remaining in Warm and Vapi.
- SDR reporting must capture assignment source, owner-alignment result, conflicts, and unassigned Sales Outreach records.
- Pool distribution (`poolDistribution`) shows brand, dispensary, and Vapi campaign pool tag counts.
- Stage mover count was fixed (was 0) by resolving pipeline/stage names from GHL stage IDs when name fields are NULL and by removing the date filter from `opportunity_traces` to detect transitions across all history.
- `LT - Report Executive Summary API` now uses a contact-safe cohort definition for `contactToOpportunityRate` so the embedded funnel is not inflated by multi-opportunity rollup semantics.
- `LT - Report Executive Summary API` now also exposes attribution-coverage metrics for the new-contact cohort so the report can separate funnel weakness from matching weakness.
- Meta reporting in the Executive Report is currently attribution-first:
  - Traffic and campaign rows come from GA4 UTM/session reporting.
  - Downstream lead/opportunity counts come from the GHL bridge and rollup tables.
  - Meta spend, clicks, and impression truth remain in the staged raw ingest and source health path, but are not shown in the Executive Report yet by design.
- The current cohort view now shows usable source-field coverage, bridge-match coverage, and lead-to-sale match coverage separately so attribution quality can be diagnosed without inflating funnel metrics.
- `LT - Report Attribution Bridge` now rebuilds a rolling 90-day window using normalized raw contact ids and stored GHL attribution fields, which materially improved cohort bridge coverage in the live report.
- The embedded report now includes a metric glossary so the visible cards are defined where they appear.
- The primary funnel cards now use Users as the denominator for conversion rates, while Recorded Visits remains traffic volume context.
- `7d`, `30d`, and `90d` are trailing complete-day presets ending yesterday, not click-day-dependent calendar blocks.
- The Executive Report also accepts explicit `from=YYYY-MM-DD` and `to=YYYY-MM-DD` windows. The UI exposes those controls and automatically loads the immediately preceding equal-length period for week-on-week comparison.
- Top Pages now normalizes landing-page URLs to host-relative paths and removes query strings, fragments, session IDs, and trigger-link parameters before rendering.
- Week-on-week cards show the selected-period value, prior-period value, absolute change, and percentage change for contacts, opportunities, meetings, closed won, email opens, email clicks, and Vapi calls.
- The `Acquisition Sources` sidebar entry opens the contact-level attribution view.
- The `UTM / Campaign Breakdown` section shows observed traffic rows, not every UTM ever created in GHL.
- `Active Opportunities Summary` and `John's Active Deals` are two presentations of the same opportunity payload, with the latter framed as a deal-centred view.
- In the active-opportunity view, `active` means the latest open snapshot, `worked` means the opportunity was updated or moved stage in the selected window, and `stage movers` means the opportunity changed stage at least once in that window.
- Contacts are not guaranteed to be created by forms; they can also arrive through routing, manual CRM entry, imports, and follow-up.
- The GHL sidebar menu record is already live in GHL.

## Expected Runtime Flow

1. GHL sidebar item opens the embedded report URL.
2. The host page reads `view`, `range`, `from`, `to`, `embed`, and `locationId` query params.
3. The host fetches executive report data from a Postgres-backed API.
4. The page renders GHL KPI cards, pipeline panels, and drilldowns in read-only mode.

## GHL Fit

- This host is designed to stay external while being embedded inside GHL.
- That keeps the dashboard flexible while leaving CRM, navigation, and user access inside HighLevel.
- If the team later wants a dashboard-page view instead, the same host can also be embedded through a GHL dashboard widget.
- GA4 traffic data is live in the report. GSC search data is staged in raw tables and will populate the search section once the summary rollup wiring is in place. The same report URL and GHL menu entry continue to work.

## Planned API Contract

- `GET /api/report/executive/summary`
- `GET /api/report/executive/channel-breakdown`
- `GET /api/report/executive/pipeline-dropoff`
- `GET /api/report/executive/health`

The summary endpoint is implemented through n8n and proxied by nginx. The other endpoints remain reserved for future expansion, but the HTML shell is already written to consume the summary payload without changing the GHL embed URL.

## Files

- `Dockerfile`: container build for Coolify or other static hosting.
- `docker-compose.yml`: Coolify-ready service definition for the report host.
- `nginx.conf`: static web server config.
- `index.html`: root redirect into the executive report.
- `embed/executive/index.html`: interactive embedded dashboard shell
