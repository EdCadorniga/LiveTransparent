# GHL Reports Configuration Plan

## Purpose
Create the GHL-side reporting shell now, while GA4 stays deferred.

This plan covers the GHL configuration that can be completed immediately and the boundaries between GHL, Postgres, and n8n.

## What Lives Where

### GHL
Use GHL for the operational surface and the CRM facts that already live there:

- Contacts
- Opportunities
- Pipeline stage movement
- Lead source and UTM fields
- Routing and intake metadata
- Saved views for daily operations
- Custom menu entry point for the report surface

### Postgres
Use Postgres for reporting storage and joins:

- Raw source pulls
- Report bridge tables
- Daily rollups
- Sync logs and error tracking

### n8n
Use n8n for orchestration:

- Scheduled source pulls
- Normalization and transform logic
- Daily rollups
- Retry and alert handling
- Publish refresh after successful runs

## Report Entry Point in GHL

Use one of these, in order of preference:

1. Custom menu item in GHL that opens the report surface
2. Embedded dashboard page if the hosting surface is ready
3. External dashboard link if embedding is not ready yet

Recommended default for v1:

- Add a `Reports` or `Executive Report` menu item in GHL.
- Point it to the dashboard page that reads from Postgres.
- Keep GHL as the launch point, not the warehouse.

### Final Recommendation

- Use a **Custom Menu Link** as the primary GHL entry point.
- Configure it to open the report as an **embedded iFrame**.
- Use the external report host as the actual render surface.
- Keep the report read-only and backed by Postgres.
- Use dashboard embed widgets only as a secondary presentation option if a dashboard-page view is later needed.
- Use Marketplace Custom Pages only if the project later needs app-style signed context and a more formal app-install flow.

### Recommended Sidebar Placement

- Put the report under the left sidebar as a top-level custom menu group named `Reporting`.
- Put the primary entry as `Executive Report` under that group.
- If the menu system only allows one item, use `Executive Report` as the sole custom menu label.
- Keep the report read-only from the GHL side so it behaves like a surface, not an editor.

### Suggested Iframe URL Pattern

Use one canonical dashboard host and keep the report path stable:

- `https://reports.livetransparent.com/embed/executive?view=overview&range=30d&embed=1`

Optional query values when needed:

- `view=overview|leads|sales|pipeline`
- `range=7d|30d|90d|custom`
- `from=YYYY-MM-DD`
- `to=YYYY-MM-DD`
- `locationId=Zwz4relUXVPxx8uohnjV`

Notes:

- The iframe should load a read-only page that is rendered from Postgres-backed data.
- The dashboard host should handle its own session or embed token logic.
- Do not expose write actions inside the embedded surface.

### Access Model

- Default access should follow the same operational users who already need CRM visibility.
- Report access should be read-only unless a user explicitly needs configuration rights outside the report page.
- If report-only users are created later, give them the minimum GHL permissions needed to see the custom menu and no extra write access.
- Use the external dashboard host to enforce the actual data access boundary.
- GHL should only be the launch point and navigation wrapper.

## Current Live Inputs

The live GHL build already has the key structures needed for reporting:

- Pipelines: `Warm`, `Sales Outreach`, `Sales`
- Reporting-critical field families:
  - UTM source, medium, campaign, content, term
  - landing page first/last
  - warm source and warm trigger type
  - lead temperature
  - last routing channel and last routing reason
  - last routed at
  - route lock until
  - routing priority
  - last event fingerprint and last event at

### What Can Live Inside GHL Today

- Left sidebar entry for `Executive Report`
- Embedded iframe launch surface
- Saved views for daily operational work
- Contact drill-down fields already present in the CRM
- Opportunity/pipeline data for sales and conversion reporting
- The live custom menu record exists in GHL and points to the embedded report host. The remaining deployment step is to publish the latest committed host build through Coolify and verify the iframe in GHL.
- A native GHL custom report was created for the operational CRM view: report ID `6a67dce4a51a4360c60963a3`. It is intended to include opportunity, email, SMS, and outbound-call widgets and is shared with the location team. Its current widget configuration is not verified: the latest authenticated browser check returned 404 plus Firebase token/permission errors. Cross-channel campaign joins remain in the external Executive Report because native GHL widgets do not join the campaign source tables.
- The external campaign summary endpoint is live at `/webhook/lt-report-campaign-channel-summary`, published as n8n version `64641979-71f3-466c-8a09-36013be6bc0e`. It returns named DAN, Emerald, SMS, LinkedIn, and Vapi campaign rows for the selected date window. This backend result must not be confused with the native GHL widget state or the older public report-host build.

### What Should Stay Outside GHL

- Postgres reporting tables
- n8n ingest and rollup workflows
- GA4 and GSC raw pulls, deferred for later
- The actual executive dashboard rendering logic
- Signed-user auth and report session control, if needed

Do not duplicate the full operating snapshot here. Use this doc as the report configuration layer only.

## Immediate GHL Configuration Work

These items can be done now without the GA4 property ID:

- Decide whether the dashboard opens in an embedded frame or a new tab
- Create or confirm report-friendly labels for:
  - lead source families
  - reporting buckets
  - pipeline states
  - stale or missing attribution
- Confirm saved views for:
  - new leads today
  - routed leads
  - warm leads needing outreach
  - booked opportunities
  - closed won opportunities
- Verify pipeline hygiene:
  - stage names are stable
  - stage order matches the dashboard funnel
  - no duplicate or dead-end stages
- Confirm permissions for users who should see reports
- Confirm which contact fields should be shown in the report drill-down
- Decide which GHL screens should link out to the report
- Set reporting assumptions for:
  - timezone
  - daily cutoff time
  - lead definition
  - sale definition
  - attribution fallback behavior

Previously blocked GHL action:

- Create the report entry menu item once agency-scope custom menu credentials are available.
- The custom menu API is agency-scoped, so the current location-level PIT is not enough to finish this step. This is no longer an active blocker because the menu record was created through authenticated GHL access.

## GHL-Only Phased Checklist

### Phase 1: Report Shell

- Create the GHL custom menu item once the agency-scope token or equivalent management access is available.
- Decide embed versus link-out.
- Confirm the report title and short description.
- Confirm the user groups that can access it.

### Phase 2: Reporting Hygiene

- Validate the live pipelines and stage order.
- Standardize report labels for lead and sales categories.
- Confirm the final field list shown in record drill-down views.
- Identify any obsolete views or labels that should not be used in the report.

### Phase 3: Operational Views

- Create saved views for the team.
- Make sure each view answers a specific question:
  - what came in today
  - what was routed
  - what converted
  - what needs follow-up
- Keep the views small and actionable.

### Phase 4: Reporting Assumptions

- Fix the reporting timezone.
- Fix the daily reporting window.
- Define the lead and sale rules in plain language.
- Decide what counts as unmatched or missing attribution.

### Phase 5: Publish Prep

- Confirm the dashboard path or external URL.
- Confirm the source labels that will be shown on each card.
- Confirm where the report data will be stored and refreshed.

## What Not To Do Yet

- Do not block GHL configuration on the GA4 property ID.
- Do not force traffic data into CRM fields as a substitute for a reporting store.
- Do not create duplicate metrics in GHL that will later be replaced by the Postgres rollup layer.
- Do not treat the sidebar menu as complete until the custom menu API has been exercised with agency-scope credentials.

## When The GA4 Property ID Arrives

Once the GA4 property ID is available:

- Wire the GA4 daily ingest in n8n.
- Store raw GA4 pulls in Postgres.
- Map GA4 traffic to the bridge and rollup tables.
- Add GA4 source labels to the report surface.
- Backfill the date range needed for the executive view.
- Compare GA4 totals against the GHL lead and sales numbers.

## Prepared Artifacts

- `postgres/reporting-bootstrap.sql`
- `n8n/reporting/README.md`
- `n8n/reporting/Embedded_Report_Host_Spec.md`
- `n8n/reporting/Workflow_Shell_Index.md`
- `reports/README.md`
- `reports/embed/executive/index.html`
- `LT - Report Config Sync` is live in n8n as the first real reporting workflow.
- `LT - Report QA and Alerts` is live in n8n as a real starter chain.
- `LT - Report Publish Refresh` is live in n8n as a real starter chain.
- The report embed target is present in GHL and the host is reachable, but the public host currently serves the older `2026-05-11-v9-active-opps` build. The current local campaign/channel UI still requires Coolify deployment and live iframe verification.
- The executive summary webhook is live and serves the dashboard JSON from Postgres.
- The report host scaffold now exists in `reports/` with a Dockerfile and nginx config.

## Execution Rule

Build the GHL shell now. Add the GA4 traffic layer later without changing the report entry point or the GHL operational views.
