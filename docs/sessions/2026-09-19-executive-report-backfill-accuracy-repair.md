# Executive Report Backfill Accuracy Repair

Date: 2026-09-19

## Problem confirmed

For the September 6–12 window, the Executive Report showed 260 top-line contacts while Attribution Coverage showed 259. The raw cohort included 223 contacts labelled `LinkedIn via Unipile historical backfill` and 10 labelled `unipile-backfill`. Lead Source included 57 historical-backfill SQLs, and contact-source attribution included 63 related opportunities.

The mismatch came from separate metric paths: the top card used `report_daily_summary`, while coverage/source/SQL panels used raw-record CTEs with different distinctness and no backfill exclusion.

## Repair applied

- Added a shared backfill-contact classifier for Unipile/historical backfill markers.
- Contacts now use one distinct, non-backfill period cohort for the top metric, coverage, source attribution, and funnel denominators.
- Period opportunities, MQL keys, SQL facts, and SQL-tag counts exclude opportunities tied to the classified backfill contacts.
- Underlying raw contacts, opportunities, and attribution rows were preserved.
- Campaign Channels and Campaign Breakdown were restored in the frontend after the newer feedback superseded their earlier temporary hiding.
- Campaign Channels and Campaign Breakdown now hide only rows whose displayed activity metrics are all zero; any non-zero metric keeps the row visible. The API and source rows remain unchanged.

## Live verification

For `from=2026-09-06&to=2026-09-12`:

- Executive Summary API: HTTP 200, non-empty 30,995-byte response.
- Contacts: `25`; Attribution Coverage cohort: `25`.
- Period opportunities: `708`.
- Lead Source SQL total: `52`; SDR SQL total: `52`.
- Campaign Channels API: 13 rows; Campaign Breakdown API: 7 rows.
- Frontend build: `2026-09-19-v32-campaign-zero-row-filter`, HTTP 200; the campaign API remains HTTP 200 with the same source rows.
- Executive Summary workflow active/published version: `13ecaf43-3219-448a-bb55-300638bff697`.
- Frontend backup: `/usr/share/nginx/html/embed/executive/index.html.bak-20260919-v32`.

## Interpretation

The remaining 25 contacts are the distinct non-backfill records in the selected window. The result is intentionally lower than the original 260 because imported historical records are not current-period acquisition. The source data remains available for historical/audit reporting.
