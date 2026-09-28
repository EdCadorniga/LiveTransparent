# Executive Report V1 workspace

This folder is an isolated working copy for the Executive Report V1 mockup.

## Operating boundary

- The current report remains at `reports/embed/executive/index.html` and must not be overwritten or removed.
- V1 will use the same report hostname through a separate URL path when it is ready for deployment.
- The mockup values are examples only. Every displayed value must come from a verified source or be labelled unavailable/not captured.
- This workspace is for preparation and review until a deployment is explicitly requested.

## Files

- `index.html` — V1 implementation using the existing Executive Summary and Campaign Channel APIs.
- `index.baseline.html` — preserved baseline copy used to compare future V1 changes.
- `mockup-v3.png` — supplied visual reference.
- `DATA-REQUIREMENTS.md` — metric definitions, source mapping, validation rules, and known gaps.
- `REPORTING-GAPS.reference.md` — copied reporting requirements and historical gap register.
- `REPORTS-README.reference.md` — copied report-host/API reference.

## Current implementation boundary

The page is intentionally conservative: it renders real values returned by the current APIs and shows `Unavailable`/`—` when the source does not provide a trustworthy value. Selecting the voicemail custom disposition is treated as a voicemail left; drops sent and delivered therefore use the same unique-contact count. Callback-requested counts come from the latest Vapi custom disposition per unique contact. Cameron's headline meetings KPI counts distinct contact IDs, so cancellation/reschedule rows do not double-count. Same-channel response speed is collected for inbound LinkedIn replies, inbound calls, and marketing-email replies; the report also shows unmatched inbound events. No overdue label is inferred because no business response-time target has been approved.

## Live n8n data layer

- `LT - Executive Report V1 Data Materializer` — workflow `knc2wxe4pyYIJ5tw`, active and published. Runs every 30 minutes and is also callable through `/webhook/lt-executive-report-v1-materializer`.
- `LT - Executive Report V1 Facts API` — workflow `oxYDg6XnRBKhl1Xd`, active and published. Read-only facts endpoint: `/webhook/lt-report-executive-v1-facts?from=YYYY-MM-DD&to=YYYY-MM-DD`.
- `LT - Executive Report V1 Response SLA Materializer` — workflow `KlBw3ThLbNlMfE2J`, active and published. Runs every 15 minutes and is also callable through `/webhook/lt-executive-report-v1-response-sla-materializer`.
- `/api/report/executive-v1/facts` is deployed through the report host's nginx proxy.

The latest controlled data-materializer run succeeded with 2,968 contact facts, 38 appointment facts, and 5,638 call facts (3,818 GHL + 1,820 Vapi). The latest response-SLA run succeeded with 236 durable inbound-response facts, including 107 matched responses and 129 unmatched inbound events; ambiguous candidates are tracked separately. These facts are additive; the existing raw reporting tables and current Executive Report were not changed.

## Count authority

V1 headline counts for new contacts, opportunities, MQLs, and SQLs now use distinct IDs and first-observed dates from raw GHL snapshot tables. They do not read `report_daily_summary` or depend on the daily rollup workflow. The raw GHL ingest and its freshness/row-count health remain prerequisites; a failed or stale ingest must be treated as unavailable rather than as zero.

Appointments and calls use the V1 raw-fact materialization, which is refreshed every 30 minutes. Channel tables and derived campaign metrics still use their channel ledgers/Campaign Channel Summary and are not represented as direct GHL headline counts.

The V1 page has passed an inline JavaScript syntax check and is deployed as a separate path on the report host. The current report path remains separate and unchanged.

## Deployed review URL

Use a separate path on the existing host, such as:

`https://reports.livetransparent.com/embed/executive-v1/`

The deployed review URL is `https://reports.livetransparent.com/embed/executive-v1/`. The current report remains at `https://reports.livetransparent.com/embed/executive/`.
