# Executive Report Cleanup Closeout

Date: 2026-09-19

## Outcome

The Executive Report presentation was cleaned up without deleting source data, reporting tables, or API fields. The live frontend now serves build `2026-09-19-v30-executive-report-cleanup`.

## Report changes

- Removed the duplicate Team Active Deals panel; Active Opportunities Summary remains canonical.
- Removed the duplicate Current Open Deals by Stage panel; Active Deals by Current Stage remains canonical.
- Removed Pipeline Velocity from the visible report, including misleading cumulative transition counts.
- Hid Vapi Calls from the week comparison and hid the Vapi queue and weekly panels; underlying Vapi data remains available.
- Hid Campaign Channels and Campaign Breakdown from the Executive Report; underlying campaign data remains available.
- Removed Observed UTM & Ad Traffic from the visible report.
- Removed Forms metrics from funnel, capture-gap, and site-traffic cards; form data remains stored.
- Collapsed the Metric Glossary so it no longer occupies the main report flow.
- Hid Search Console from the Executive Report; GSC source health and the dedicated Website report remain available.
- Merged LinkedIn via Unipile and historical-backfill display rows into one displayed lead-source row, summing MQL and SQL counts without deleting attribution rows.

## Verification

- `git diff --check` passed.
- Embedded JavaScript syntax check passed.
- Public frontend returned HTTP 200 and included the new build stamp.
- Executive Summary API returned HTTP 200 with a non-empty 35,976-byte response.
- Container backup created at `/usr/share/nginx/html/embed/executive/index.html.bak-20260919-v30`.
- No CRM, source database, n8n workflow, sender, or tracking data was deleted or changed.

## Limitation

Interactive browser QA could not run because no browser surface was available in the session. Structural HTML parsing, JavaScript syntax validation, live frontend checks, and live API checks passed.
