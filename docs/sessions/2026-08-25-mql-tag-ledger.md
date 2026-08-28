# MQL Tag Ledger (2026-08-25)

## Purpose

The Executive Report's MQL metric was stage-based (opportunities that reached the Warm
"Qualified (MQL)" stage). The business actually wants to count **contacts that had the `mql`
tag added within the selected window (e.g. past week)**.

GHL's public API does **not** expose *when* a tag was added, and the existing hourly contact
snapshot cannot reconstruct it (every captured `mql` contact already had the tag at first
capture). So we built a **forward-looking tag-add ledger**: a GHL automation fires on
"Tag Added → mql" and POSTs the event to n8n, which records it with a timestamp.

## Components

| Item | Detail |
|---|---|
| Table | `mql_tag_events(contact_id, tag, added_at, source, payload_json, created_at)` — UNIQUE `(contact_id, tag)`; `ON CONFLICT DO NOTHING` keeps the first add date |
| n8n workflow | `LT - MQL Tag Event Ingest` (`U9oc2tZRsr4zq6IM`), POST `/webhook/lt-mql-tag-event`, **active** |
| Auth | Requires header `X-LT-MQL-Tag-Secret` (value in the workflow `Config` node). Unauthorized / missing contact_id → HTTP 403; duplicate → 200 `duplicate` |
| Report | Exec Summary `mqlSummary` now includes `taggedMqlsTotal`, `taggedMqlsThisPeriod` (window), `taggedAsOfDate`, `tagBasis: mql_tag_events_ledger` |

## GHL Automation Setup

Created and published in the GHL UI on 2026-08-25 as `WL - MQL Tag Ledger`.
Workflow ID: `203163a4-262a-4195-9a15-b4aa0b712c5a`.

Configuration:

| Setting | Value |
|---|---|
| Name | `WL - MQL Tag Ledger` |
| Trigger | Contact → **Tag Added** → tag `mql` |
| Action | Webhook POST to `https://automations.livetransparent.com/webhook/lt-mql-tag-event` |
| Header | `X-LT-MQL-Tag-Secret` = value in the n8n Config node of `U9oc2tZRsr4zq6IM` |
| Custom Body | `{"contact_id":"{{contact.id}}","first_name":"{{contact.firstName}}","last_name":"{{contact.lastName}}","email":"{{contact.email}}"}` |

The automation is published. Every new `mql` tag add should now be recorded with a
timestamp and the report's `taggedMqlsThisPeriod` will populate for the selected window.

## Notes / Caveats

- **Forward-looking only**: events captured from activation onward. The ledger is empty at
  activation, so `taggedMqlsTotal`/`taggedMqlsThisPeriod` are 0 until events flow. We cannot
  backfill the "added in past week" number for prior weeks.
- **Tag is noisy**: the 443 contacts currently holding `mql` in GHL include mailer-daemon
  bounce records and contacts also tagged `not qualified`. The ledger records whatever GHL
  fires; if you want to exclude junk, add a filter in the workflow or the automation.
- **Idempotent**: a contact is counted once (first add). Re-adds of `mql` are ignored.
- The existing stage-based MQL fields (`totalMqls`, `convertedToSql`, `currentMqls`,
  `enteredMqls`, `convertedThisPeriod`) remain in `mqlSummary` unchanged; the tag fields are
  additive.
