# GHL Reports Configuration Plan

## Purpose
Create the GHL-side reporting shell now, while GA4 stays deferred.

This plan covers the GHL configuration that can be completed immediately and the boundaries between GHL, Postgres, and n8n.

For the complete gap inventory, field-level requirements, and acceptance criteria, see [Reporting Gaps and Requirements](../docs/reports/Reporting%20Gaps%20and%20Requirements.md).

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
- A native GHL custom report was created for the operational CRM view: report ID `6a67dce4a51a4360c60963a3`. It is intended to include opportunity, email, SMS, and outbound-call widgets and is shared with the location team. Its current widget configuration is not verified: the latest authenticated browser check returned 404 plus Firebase token/permission errors. The root `GHL_PIT` was separately verified against the official location and contacts REST endpoints with HTTP 200, so this is a report-builder browser/Firebase session issue rather than a general GHL API-access issue. Cross-channel campaign joins remain in the external Executive Report because native GHL widgets do not join the campaign source tables.
- The external campaign summary endpoint is live at `/webhook/lt-report-campaign-channel-summary`, published as n8n version `64641979-71f3-466c-8a09-36013be6bc0e`. It returns named DAN, Emerald, SMS, LinkedIn, and Vapi campaign rows for the selected date window. This backend result must not be confused with the native GHL widget state or the older public report-host build.
- The external outgoing-call detail endpoint is live at `/webhook/lt-report-outgoing-calls` through n8n workflow `VXFHc8IrF9DDEEdj` (published version `d004556d-0b11-4a86-8827-f8f58a1eeee3`). The report host proxies it as `/api/report/executive/outgoing-calls` and renders the result at the bottom of the Executive Report. It is a read-only Vapi detail surface, not a native GHL widget.

### Partnership Reporting Status

- The Executive Report currently shows the 10 live Partnership LinkedIn invites in the overall LinkedIn activity KPI.
- The campaign table currently shows 10 `Partnership emails`, but the 10 LinkedIn invites are not yet attributed to a `Partnership LinkedIn` row.
- The native GHL report has no verified Partnership Pipeline filter, partnership tag filters, or native Unipile activity widget.
- Unipile connection requests, acceptance events, LinkedIn DMs, replies, and suppression state remain Executive Report/Postgres concerns unless explicitly synchronized into supported GHL objects.

### What Should Stay Outside GHL

- Postgres reporting tables
- n8n ingest and rollup workflows
- GA4 and GSC raw pulls, deferred for later
- The actual executive dashboard rendering logic
- Signed-user auth and report session control, if needed
- Row-level Vapi outgoing-call detail, recordings, and the report-host pagination API

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

Current report-builder blocker:

- A valid location PIT can read CRM data but cannot authenticate the Firebase/browser session used by the native Custom Report builder. The supported API/SDK does not expose widget-layout mutation. Finish this through an authenticated GHL UI session or an explicitly approved internal API path; do not guess undocumented report endpoints.

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
- The report embed target is present in GHL and the host is reachable. The public host serves the Executive Report build `2026-08-01-v12-campaign-breakdown`; live iframe behavior, campaign rows, and the bottom outgoing-call detail section have been verified. Native report configuration remains blocked by the authenticated GHL report page returning 404.
- The executive summary webhook is live and serves the dashboard JSON from Postgres.
- The report host scaffold now exists in `reports/` with a Dockerfile and nginx config.

## Native GHL Report Improvement Plan — `6a67dce4a51a4360c60963a3` (2026-08-01)

Operational CRM view for report ID `6a67dce4a51a4360c60963a3` at `https://app.gohighlevel.com/v2/location/Zwz4relUXVPxx8uohnjV/reporting/reports/view/6a67dce4a51a4360c60963a3`.

### Ground Truth (verified 2026-07-31)

- Report loads in the authenticated GHL UI with **11 editable widgets**; report date window is shared (`Last week`, no per-widget overrides).
- **Already done**: `Campaign Opportunities` filtered to **Partnership Pipeline** (`tQkFYrHjALgoLz6oq0uz`); `Contacts by tag` uses **Tags → Is one of** with `partner_candidate_email` + `partner_candidate_linkedin`.
- Email widgets filter Accepted/Opened/Clicked/Hard bounced; SMS filters Direction=Outbound; calls filter Direction=Outgoing.
- Live pipeline IDs: Sales `MThKauqlvnEFuFmAkyWX`, Sales Outreach `dhdlf3O4tymxFtHk4aqq`, Warm `FRjpDZ1HWj3UPgczsu3t`, Partnership Pipeline `tQkFYrHjALgoLz6oq0uz`. Opportunity custom field **Owner** `Wpg7FGrQTgAY1GoKcdEJ`.
- Constraint: widget layout is **browser-only** (no public API mutation). All edits happen in the authenticated GHL report builder, then save + re-verify.

### Priority 1 — Close the partnership gap (finish what's started)

| Widget | Change | Filter/spec |
|---|---|---|
| `Campaign Opportunities` | Keep Partnership Pipeline filter; add **stage split** | Pipeline `tQkFYrHjALgoLz6oq0uz`, group by stage (New Partner Lead `ccc3d423`, Contacted `7c666a65`, Proposal Sent `2b378529`, Closed `91ab7c92`) |
| `Contacts by tag` | Expand tag set to the full partner tag family | `partner_candidate_email`, `partner_candidate_linkedin`, `partner_email_queued`, `partner_linkedin_requested`, `partner_replied`, `partner_not_interested`, `partner_do_not_contact` (add any that exist; omit unsupported ones) |
| New: `Partnership by stage` | Pipeline stage-count widget | Same pipeline, all 4 stages, labeled with the pipeline context so it is not confused with general opportunities |

### Priority 2 — MQL + Sales Outreach (the operational funnel)

| Widget | Spec |
|---|---|
| MQL detail | Warm → **Qualified (MQL)** stage `3b3bd98d-cbb9-4c50-8cf3-b4eba29061c2`; show active count + entered/exited this period |
| MQL→SQL movement | Optionally add movement conditions on stage entry into Sales Outreach → **Qualified** `91517911-3eee-45a0-b432-e36209495c16` |
| Sales Outreach funnel | New/Attempting 1st/2nd/3rd/Engaged/Meeting Requested/Booked (`3529dd3d`, `b97e42b1`, `c46c3be3`, `c8b7a450`, `9ced8010`, `1ab47457`, `1f95dd0a`) with shared date range |

### Priority 3 — Revenue + ownership (what closes)

- **Closed Won count + revenue**: Sales → Closed Won `f6b65baa-eac8-4f02-b91e-2ab0c8841b2d`, sum monetary value for the selected window.
- **Owner / assignment breakdown**: group opportunities by the `Owner` custom field (`Wpg7FGrQTgAY1GoKcdEJ`) so Jason/Marc/Janvi volumes are visible; flag unassigned Sales Outreach rows.

### Priority 4 — Channel widgets (verify, don't rebuild)

- **Email**: already has Accepted/Opened/Clicked/Hard bounced. Add **replied** condition if the source supports it; label each widget clearly so the source is obvious.
- **SMS**: confirm **replies** are captured (outbound is filtered; replies come from inbound events) and add a replied metric if supported.
- **Calls**: confirm **answered vs missed** split on top of Direction=Outgoing; add voicemail if stored.
- **Appointments**: keep the Regulated Ads calendar (`SrtXcFVyea7pFl3nTiIK`) as the meeting source; verify status breakdown (booked/showed/no-show/cancelled).

### Priority 5 — Hygiene (applies to all widgets)

- **Shared date range**: one report-level window, no per-widget overrides; confirm sub-account timezone (America/Los_Angeles) is the report default.
- **Documented filters**: every widget should name its data source (contacts / opportunities / conversations / appointments / tags) and its exact filter — put this in the widget title or a pinned note.
- **Access**: confirm location-team sharing and read-only operator access after saving.

### Explicitly OUT of scope for GHL (stays in the Executive Report)

- Unipile LinkedIn invites/accepted/DMs/replies and suppression state (native GHL has no source for it unless synced into GHL objects).
- Cross-channel campaign table (DAN/Emerald/SMS/LinkedIn/Vapi joins).
- Provider activity, Vapi outcomes, trigger-link detail.

### Execution Result (2026-08-01, authenticated GHL UI)

Applied and saved in the authenticated report builder. The report now has **15 widgets** (verified persisted after reload):

- Added **Partnership Pipeline Opportunities** — `Opportunity count` filtered to `Pipeline Is Partnership Pipeline`.
- Added **Partnership Pipeline by Status** — `Opportunity counts by status` grouped by Status, filtered to `Pipeline Is Partnership Pipeline`. GHL offers no native stage-group for opportunities, so status is the available breakdown.
- Added **Closed Won Revenue** — `Won Opportunity value` metric (monetary value of won opportunities for the period).
- Verified existing partnership widgets are correct: `Campaign Opportunities` (Pipeline Is Partnership Pipeline), `Contacts by tag` and `Contacts counts by tags (Partnership Campaign)` (Tags Is one of with `partner_candidate_email` + `partner_candidate_linkedin`, group-by Tags surfaces the full partner tag distribution). Email Accepted/Opened/Clicked/Hard-bounced, SMS by status (Direction=Outbound), Outgoing calls by status, Appointment count by status, Opportunity counts by status, and Posts by social all verified with live data for the shared `This week` window.

Not applied this session:

- **MQL / Sales Outreach funnel widget**: the Stage condition requires its own per-row Pipeline context in the builder's OR-grouped filter UI and was too fragile to complete reliably; the MQL attempt was cancelled cleanly (no invalid widget left behind). MQL detail remains in the Executive Report (`mqlSummary`) and Warm → Qualified (MQL) is stage `3b3bd98d-cbb9-4c50-8cf3-b4eba29061c2` when revisited.
- **Owner breakdown widget**: not added; GHL opportunity widgets group by Status/date, not the `Owner` custom field (`Wpg7FGrQTgAY1GoKcdEJ`). Owner detail stays in GHL opportunity views and the Executive Report.

### Acceptance checklist

1. All Partnership Pipeline stages appear in the partnership widget(s) with correct counts for the shared window.
2. `Contacts by tag` shows the full partner tag set (unsupported tags cleanly omitted).
3. MQL and Closed-Won widgets return correct numbers vs the Executive Report for the same window.
4. Owner breakdown matches GHL opportunity owners.
5. Zero-data windows (e.g. 2026-07-19→25 after filtering) are expected/acknowledged, not treated as breakage.
6. Every widget has a named source + documented filter; no widget implies Unipile data.

## Execution Rule

Build the GHL shell now. Add the GA4 traffic layer later without changing the report entry point or the GHL operational views.
