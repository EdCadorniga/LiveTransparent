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
- GA4 and Search Console references remain available; GA4 is live and Search Console raw ingest is live, but the Executive Report search panel still needs summary-rollup wiring
- Live Postgres bootstrap apply workflow used to initialize the reporting schema in the database
- Current live state: the patched GHL ingest workflows have been rerun, GA4 is live, Search Console raw ingest is live, and the executive report is reading combined GHL + GA4 data while the GSC search section still waits on summary-rollup wiring.
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
2. Finalize the embedded report host deployment from the `reports/` scaffold.
3. Create the GHL sidebar entry.
4. The live n8n workflow shells already exist; keep consolidating corrective logic back into the primary rollup flow.
5. Add GSC summary-rollup wiring if the business wants the search section to populate in the same embed.
6. Recheck the live summary endpoint after the full chain rerun and confirm the integrated Rollups metrics hold without the separate correction handoff.

## Remaining External Dependency

- GA4 property ID, only if traffic reporting is reintroduced in this phase
