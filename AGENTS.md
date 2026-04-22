# LiveTransparent Agent Notes

## Project Context
- This project is deployed on a VPS using Coolify.
- There are currently two separate containers managed in Coolify.
- Those containers can reach each other over Coolify's internal/local network.
- `n8n` is publicly routed at `https://automations.livetransparent.com`.
- `bookstack/` assets are prepared in-repo but BookStack is not deployed yet.

## Working Assumptions
- Prefer internal service-to-service communication over the Coolify network where possible.
- Use `automations.livetransparent.com` as the canonical n8n public host for webhook/editor URLs.
- Keep config values centralized in service `.env` files so future domain cutovers are small changes.

## Current Progress Snapshot
- The Codex config has been set for this session to full access / no approval prompts via `sandbox_mode = "danger-full-access"` and `approval_policy = "never"`.
- The report host is live at `https://reports.livetransparent.com` and the embedded executive report route is live.
- The GHL `Executive Report` menu entry exists and points at the embedded host.
- The live report stack is GHL-first for now; GA4 and GSC remain deferred until the later phase.
- The report summary API is live and now shows different lead totals by window after the manual reruns:
  - `7d` leads: `21`
  - `30d` leads: `50`
  - `90d` leads: `50`
- The lead and sales ingest workflows were patched to derive `report_date` from source timestamps; the leads/sales ingest, attribution bridge, and daily rollups were manually rerun after that patch.
- Direct n8n REST API access with the configured API key is currently working for read/write workflow operations.
- Live channel attribution patch applied on `LT - Report Daily Rollups` (`EUeOiRttoVLQ9zF9`):
  - Added `tmp_bridge_traffic` from `report_bridge_traffic_to_lead` for attribution-first channel/source/medium resolution.
  - `report_channel_daily_summary` now prefers bridge attribution via contact-linked lateral joins and falls back to contact-derived values only when bridge rows are missing.
  - Opportunity attribution in channel rollups now uses bridge-backed contact attribution instead of raw same-day contact channel only.
- Direct n8n workflow execution is not currently exposed via the same public API surface used for read/write in this environment, so manual UI run (or scheduled run) is required to materialize rollup SQL changes.
- Live fix applied on `LT - GHL Daily Sales Ingest` (`aYT5oHcgmBALzHy5`):
  - `sales_config` was converted from a Set node to a Code node so auth/location config is always emitted at runtime.
  - `sales_fetch` now hard-fails with an explicit error when config is missing `authToken` or `locationId`.
  - Active workflow version after cleanup is `57723bc3-4289-4f69-8cb6-820ec1be69dc`.
- Execution `8821` for `aYT5oHcgmBALzHy5` completed successfully (`52s`, `status=completed`, `errorCount=0`, `rawOpportunityRows=2726`, `rawPipelineHistoryRows=2726`).
- Reports embed frontend patch prepared in `reports/embed/executive/index.html`:
  - Sidebar and range controls now use stable anchor-based navigation (no global click interception).
  - Stage movement/drop-off now renders from `stageDropoff` API data in a dedicated movement list.
  - Pipeline cards now display opportunity-driven counts from `pipelineDropoff`.
- Live API patch applied on `LT - Report Executive Summary API` (`Bukc0mgOD2r7V6ED`):
  - `Build Query` now derives stage movement using day-over-day `LAG(stage_count)` from `report_stage_daily_summary` into `moved_in_count` and `moved_out_count` at query time.
  - `pipelineDropoff` now aggregates stage rollup movement (`stage_count`, `moved_in_count`, `moved_out_count`, `won_count`, `lost_count`) instead of cumulative lead/opportunity snapshots.
  - The live summary payload now returns non-zero movement metrics for `range=30d` and `range=90d`.
- Report host deployment/routing issue was resolved:
  - Two report containers were serving different builds behind Traefik; old stale container was removed.
  - Live container now serves `build-stamp: 2026-04-21-nav-no-intercept-v2`.
  - Chrome stale-cache behavior was observed; Firefox validated current behavior correctly.
- UI visibility improvement added:
  - Pipeline panel now includes an explicit top-stage row (`stage-top-grid`) so stage names/counts are visible even when movement bars are easy to miss.
- Commit status for report host changes:
  - `454b6ba` pushed: nav stability + build stamp visibility.
  - `3c8a5d8` pushed: explicit top pipeline stages display.
- Ingestion freshness check (latest verified):
  - Sales ingest (`aYT5oHcgmBALzHy5`): success at `2026-04-20T18:00:46Z` (exec `9031`).
  - Attribution bridge (`Y0TU7Il71JswxOBp`): success at `2026-04-20T18:00:47Z` (exec `9032`).
  - Rollups (`EUeOiRttoVLQ9zF9`): success at `2026-04-20T18:00:57Z` (exec `9033`).
  - Leads ingest (`OtqWjqGXZC3OcrXP`): last success is older at `2026-04-18T18:44:27Z` (exec `7818`), so leads are currently behind the other chains.
- GA4/Search Console status:
  - GA4 is still not added due to access/login blockage at `analytics.google.com`.
  - GA4 and GSC remain deferred and should be retried once access is unblocked.
- LinkedIn outreach scaffolding is now live in n8n:
  - Workflow `LT - UNIPILE LinkedIn Connection Request (Internal Test)` is active in n8n (`Zt8p2aYtIuY0HK18`).
  - Webhook endpoint is `POST https://automations.livetransparent.com/webhook/unipile-linkedin-connect-test`.
  - The workflow uses the current Unipile LinkedIn account and resolves a LinkedIn profile URL to a `provider_id` before any invite send.
  - Webhook auth is enforced via header `x-lt-unipile-key`; the secret value is stored in the live workflow, not in docs.
  - Default behavior is dry-run only. A live invite is sent only when the payload includes `send: true`.
  - Default note is now personalized with `{first_name}` using the resolved Unipile profile first name, with webhook payload first-name fields as fallback.
  - Current default note: `Hi {first_name}, I'm reaching out from LiveTransparent. We help companies market regulated products with compliant advertising systems and clearer attribution. I'd be glad to connect.`
  - Last verified dry-run against `https://www.linkedin.com/in/edmundo-c-a06372166/` resolved successfully and returned a rendered `messagePreview` with `resolvedFirstName = Edmundo`.
- GHL automation for LinkedIn outreach is not built yet:
  - The next implementation step is a GHL automation/webhook action that posts contact LinkedIn URLs into the Unipile n8n webhook.
  - Recommended payload shape for the GHL webhook step is:
    - `linkedin_url`: required LinkedIn profile URL
    - `first_name`: optional fallback first name from GHL contact
    - `message`: optional override note; omit to use the default personalized message
    - `send`: boolean; omit or `false` for dry-run, set `true` only for live invite sends
- Remaining data issue to inspect: `opportunitiesCreated` still reads `193` across the windows while closed-won sales remain `0`; confirm whether that is intended pipeline behavior or if the opportunity date filter still needs tightening.

## Agent Tooling
- Use `n8n-lt` as the canonical n8n MCP for this project.
- Prefer `n8n-lt` MCP or direct API calls before using any browser-based workflow.
- Avoid `agent-browser` or other browser automation unless MCP/API/CLI options are not sufficient.
- If the task can be completed purely from the CLI, use `playwright-cli` or direct shell tooling instead of a browser.
- When workflow state or runtime behavior matters, verify actual instance state with `n8n-lt` instead of guessing from local files.
- Use `ghl_official` as the primary GHL MCP for the Live Transparent location.
- Use `ghl_workflows` as a secondary option when it exposes the needed action.
- If a GHL MCP call returns scope/auth errors for an endpoint that should be available, verify the same action through direct GHL API before assuming the PIT is bad.
- Treat live operational status in docs as last known state and re-verify in-system before making runtime decisions.

## GHL and n8n Rules
- Prefer documented runbooks in `GHL Live Transparent CRM/` before making workflow changes.
- For n8n workflow edits, verify live state after every mutation.
- When n8n MCP mutation helpers are unreliable, use the direct n8n REST API path documented in `n8n/`.
- For direct GHL API testing, use `https://services.leadconnectorhq.com` with the PIT-backed headers already documented in the repo.
- When the report data needs to be validated end to end, rerun the patched GHL ingest workflows first, then the attribution bridge, then the daily rollups, then the executive summary workflow.

## Paths and Layout
- Keep Docker and service-specific assets under their service folders, for example `n8n/` and `postgres/`.
- Place service docs close to the service they describe.
- Keep knowledgebase deployment assets under `bookstack/`.
- Keep marketing assets under `marketing/`.
- Do not recreate the old root-level marketing workspaces; use the consolidated `marketing/` hierarchy instead.

## File Map
- `LiveTransparent Report Plan.md`: Step-by-step plan for the GHL executive report build, with GA4/GSC deferred.
- `GHL Live Transparent CRM/Operating Snapshot.md`: Current live GHL/n8n operating summary and active rules.
- `GHL Live Transparent CRM/Legacy Archive.md`: Deprecated and historical notes that should not be treated as the source of truth.
- `GHL Live Transparent CRM/Report Data Contract.md`: Shared data contract for the GHL-first report pipeline, with GA4/GSC deferred.
- `GHL Live Transparent CRM/GHL Reports Configuration Plan.md`: GHL-side report shell, entry point, and operational configuration plan.
- `GHL Live Transparent CRM/GHL Reports Custom Menu Payload.md`: Exact custom menu payload for the embedded report sidebar entry.
- `GHL Live Transparent CRM/Warm_Lead_Conflict_Safe_Implementation_Spec.md`: Canonical warm lead routing and idempotency spec.
- `GHL Live Transparent CRM/Pipeline_Process_Training_Guide.md`: Canonical pipeline usage and reporting guidance.
- `GHL Live Transparent CRM/Pipeline_Quick_Reference.md`: Short pipeline reference for day-to-day use.
- `GHL Live Transparent CRM/RB2B_Website_Visitor_Intake_Workflow.md`: Website visitor intake and reconciliation runbook.
- `postgres/README.md`: Postgres reporting bootstrap and deployment notes.
- `postgres/reporting-bootstrap.sql`: Postgres bootstrap schema for report raw, bridge, rollup, and ops tables.
- `n8n/docker-compose.yml`: n8n service definition, environment wiring, and Traefik labels.
- `n8n/.env`: n8n runtime secrets and host/webhook/editor URL values.
- `n8n/nodes/ghl/REFERENCE.md`: GHL node/API reference map used in this repo.
- `n8n/nodes/apollo/REFERENCE.md`: Apollo node/API reference map used in this repo.
- `n8n/nodes/twilio/REFERENCE.md`: Twilio node/API reference map used in this repo.
- `n8n/nodes/google-analytics/REFERENCE.md`: GA4 reference for the later-phase reporting pipeline.
- `n8n/nodes/search-console/REFERENCE.md`: Search Console reference for the reporting pipeline.
- `n8n/reporting/README.md`: Reporting pack index and build order.
- `n8n/reporting/Embedded_Report_Host_Spec.md`: Iframe host and access contract for the embedded dashboard.
- `n8n/reporting/Workflow_Shell_Index.md`: Short list of reporting workflow shells to create in n8n.
- `n8n/reporting/GHL_Menu_Sync_Workflow.md`: Runbook for the GHL executive report menu provisioner and current payload contract.
- `n8n/reporting/LiveTransparent_Report_Workflow_Spec.md`: Report workflow spec for the GHL-first pipeline, with GA4/GSC deferred.
- `n8n/REPORTING_IMPLEMENTATION.md`: n8n build shape and workflow chain for the report pipeline.
- `reports/README.md`: External embedded dashboard host overview and runtime contract.
- `reports/docker-compose.yml`: Coolify-ready static host service definition for `reports.livetransparent.com`.
- `Dockerfile`: Root-level Coolify fallback build for the report host using `reports/` as the content source.
- `reports/Dockerfile`: Static report host container build for Coolify deployment.
- `reports/nginx.conf`: Nginx config for serving the embedded report host.
- `reports/index.html`: Root landing page and redirect into the executive embed.
- `reports/embed/executive/index.html`: Embedded executive report shell.
- `bookstack/README.md`: BookStack deployment and hardening notes.
- `bookstack/docker-compose.yml`: BookStack + MariaDB service definition and Traefik labels.

## Immediate Next Steps
1. Create the GHL automation that sends LinkedIn contact data to `LT - UNIPILE LinkedIn Connection Request (Internal Test)` through the n8n webhook.
2. Start the GHL automation in dry-run mode only (`send: false` or omitted) and validate payload mapping from real GHL contact data, especially `linkedin_url` and fallback `first_name`.
3. Decide when to allow live sends (`send: true`) and whether that should be a separate GHL automation branch, a guarded condition, or a manual approval step.
4. Run `LT - Report Daily Rollups` once from n8n UI (or wait for next schedule) so the live channel attribution patch is written into `report_channel_daily_summary`.
5. Validate `channelBreakdown` in the executive summary API after the run, specifically reduction in `unattributed` share and expected spread across known channels.
6. Fix and validate `LT - GHL Daily Leads Ingest` schedule/health so leads freshness matches sales/bridge/rollups (daily expected at `0 6 * * *` America/Los_Angeles).
7. Re-verify `opportunitiesCreated` behavior by range after leads freshness is restored, then confirm if it reflects intended counting semantics.
8. Confirm whether `closed_won` should remain `0` for current dataset or whether additional sales ingest mapping is needed.
9. Retry GA4 onboarding once Google access is unblocked, then proceed with deferred GA4/GSC phase.
