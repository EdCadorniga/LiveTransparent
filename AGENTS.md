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

## Agent Tooling
- Use `n8n-lt` as the canonical n8n MCP for this project.
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

## Paths and Layout
- Keep Docker and service-specific assets under their service folders, for example `n8n/` and `postgres/`.
- Place service docs close to the service they describe.
- Keep knowledgebase deployment assets under `bookstack/`.
- Keep marketing assets under `marketing/`.
- Do not recreate the old root-level marketing workspaces; use the consolidated `marketing/` hierarchy instead.

## File Map
- `LiveTransparent Report Plan.md`: Step-by-step plan for the GA4/GSC/GHL executive report build.
- `GHL Live Transparent CRM/Operating Snapshot.md`: Current live GHL/n8n operating summary and active rules.
- `GHL Live Transparent CRM/Legacy Archive.md`: Deprecated and historical notes that should not be treated as the source of truth.
- `GHL Live Transparent CRM/Report Data Contract.md`: Shared data contract for the GA4/GSC/GHL report pipeline.
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
- `n8n/nodes/google-analytics/REFERENCE.md`: GA4 reference for the reporting pipeline.
- `n8n/nodes/search-console/REFERENCE.md`: Search Console reference for the reporting pipeline.
- `n8n/reporting/README.md`: Reporting pack index and build order.
- `n8n/reporting/Embedded_Report_Host_Spec.md`: Iframe host and access contract for the embedded dashboard.
- `n8n/reporting/Workflow_Shell_Index.md`: Short list of reporting workflow shells to create in n8n.
- `n8n/reporting/GHL_Menu_Sync_Workflow.md`: Runbook for the GHL executive report menu provisioner and current payload contract.
- `n8n/reporting/LiveTransparent_Report_Workflow_Spec.md`: Report workflow spec for the GA4/GSC/GHL pipeline.
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
