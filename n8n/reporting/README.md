# LiveTransparent Reporting Pack

This folder is the implementation pack for the executive report stack.
It is intended to be the handoff point between the written plan and the live build.

## What Is Ready Now

- Postgres bootstrap schema for raw, bridge, rollup, and ops tables
- GHL report shell plan and sidebar/embed contract
- n8n workflow architecture and build order
- Live GHL summary/report workflows for leads, sales, bridge, rollups, QA, and the executive summary API
- GHL menu provisioner workflow for the report entry point
- External report host scaffold in `reports/embed/executive/index.html`
- GHL references and the live GHL summary/report workflows
- GA4 is live. Search Console raw ingest exists, but the current GSC OAuth credential is revoked/expired, so the GSC source remains blocked until reauthorization.
- Live Postgres bootstrap apply workflow used to initialize the reporting schema in the database
- Current live state: the patched GHL ingest workflows have been rerun, GA4 is live, the Executive Report backend is reading combined GHL + GA4 data, and the campaign summary endpoint is published with named channel/campaign rows. The local Executive Report UI is ahead of the public host, which still serves build `2026-05-11-v9-active-opps`.
- Ingest hardening (2026-07-31): GA4 version `8f4c63ea-dd33-4c7f-93a5-b3cbb5c8e7fa` finalizes success/empty/partial/failure states and protects the watermark; sales version `4f3e8068-8864-4b4d-9286-ba4d618cc3a8` uses ingest-date snapshots, bounded cursor/retry guards, fail-closed finalization, and `ghl_opportunities` health isolation. Verification executions: GA4 `276731` success, GA4 pinned failure `276747`, sales `276626` success.
- `LT - Report Daily Rollups` was restored, republished, and verified on 2026-05-02 with the daily-summary fix logic integrated directly.
- `LT - Report Rollup Corrections` has been deactivated because the production Rollups workflow now owns those fixes.

## File Index

- `../REPORTING_IMPLEMENTATION.md`: n8n build scaffold and workflow chain
- `../reporting/LiveTransparent_Report_Workflow_Spec.md`: detailed workflow-by-workflow spec
- `../../postgres/README.md`: Postgres bootstrap and deployment notes
- `../../postgres/reporting-bootstrap.sql`: schema bootstrap for the reporting database
- `../../GHL Live Transparent CRM/GHL Reports Configuration Plan.md`: GHL embed and access model
- `../../GHL Live Transparent CRM/Report Data Contract.md`: shared report data contract
- `../../reports/README.md`: external embedded dashboard host overview and runtime contract
- `../../reports/embed/executive/index.html`: embedded executive report shell
- `./Embedded_Report_Host_Spec.md`: external report host and iframe contract
- `./Workflow_Shell_Index.md`: short inventory of the report workflow shells to create
- `./GHL_Menu_Sync_Workflow.md`: menu provisioner notes and invocation contract
- `../nodes/google-analytics/REFERENCE.md`: GA4 upstream reference
- `../nodes/search-console/REFERENCE.md`: Search Console upstream reference
- `../nodes/ghl/REFERENCE.md`: GHL upstream reference
- `../nodes/postgres/REFERENCE.md`: Postgres node and write-pattern reference

## Build Order

1. Apply the Postgres bootstrap.
2. Deploy the current embedded report host build from the `reports/` scaffold through Coolify and verify the public build stamp.
3. Reauthorize GSC, rerun the blocked ingest, and verify the search section.
4. Create or verify the GHL sidebar entry.
5. The live n8n workflow shells already exist; keep consolidating corrective logic back into the primary rollup flow.
6. Recheck the live summary and campaign endpoints after deployment and confirm the integrated Rollups metrics hold without the separate correction handoff.

## Remaining External Dependency

- GSC OAuth reauthorization is required before Search Console metrics can be refreshed.
