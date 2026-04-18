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
- Search Console and GHL references
- GA4 references, with the property ID still pending
- Live Postgres bootstrap apply workflow used to initialize the reporting schema in the database

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
4. The live n8n workflow shells already exist; finish replacing the remaining shells with the real nodes.
5. Enable GA4 ingest once the property ID arrives from Cameron.

## Remaining External Dependency

- GA4 property ID
