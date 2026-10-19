# V1 Bands 2–4 improvements — 2026-10-13

## Scope and step status

Ed requested simpler source summaries in Band 2, actual campaign names including October vertical outreach in Band 3, and Booked/SQLs/MQLs in Band 4. Reporting-only changes and V1 deployment are authorized by this request. Preserve the legacy report and dirty worktree; no commit or pack operation.

| Step | Status | Verified result |
|---|---|---|
| Inspect sources/live state | Complete | Facts `4172da81-bda2-4267-9316-25d5ad27a2c6`; Summary `4c5b5611-841b-48a4-9d78-c0700e599e6a`; Campaign Channels `24492be1-3b62-436a-8dbe-7f46c64c314e` active with matching published versions. |
| Band 2 source summary | Live | `opportunityOrigin` and `mqlSqlOrigin` exposed. Oct 4–10: 25/27 SQLs in "CRM UI (workflow from CSV import tag)", 2 in "Trigger link click after CSV import", 0 unattributed. MQLs 18 CRM UI + 3 Other CRM action + 1 Booking widget. Opportunities 85 CRM UI + 6 Trigger link + 3 Other CRM action + 2 Booking widget + 1 Other inbound + 1 No attribution recorded. |
| Band 3 campaign evidence | Exact-ID join complete; rendering pending | All 1,501 native queued messages match supported export by message ID, contact ID, outbound sent status and timestamp within 120s. Unique IDs across campaigns; no delivery inference. |
| Band 4 outputs | Live | `sdrOutputs` and `meetingCalendars` exposed. Booked KPI is 0 because the 3 Reg Ads appointment contacts in the window do not overlap any of the 27 SQLs. SQL attribution runs pre-meeting assignees for Marc/Jason/Cameron; the "Unassigned / unattributed" row reconciles totals. |
| Vertical email event feed | Blocked on browser access | The 8 vertical Send Email nodes live in the GHL workflow builder, not n8n-lt. n8n-lt returns 404. Ed chose the GHL Marketplace `OutboundMessage` subscription path; that requires a browser session. |
| Deploy/readback | Complete | Build `2026-10-13-v1-vertical-facts`; legacy report preserved; new keys live in public API. |

## Opportunity origin classification (current week)

The 27 SQLs in the period break down by how their opportunity was created (GHL `attributions` array):

| Origin | MQLs | SQLs | What it really means |
|---|---:|---:|---|
| **CRM UI (workflow from CSV import tag)** | **18** | **25** | A GHL workflow fires when a CSV-imported contact is tagged, creating the SQL opportunity with `medium=csv_import, utmSessionSource="CRM UI"`. |
| Trigger link click after CSV import | 0 | 2 | Same path plus a `msgsndr.com/links/r/2/...` URL — the contact clicked an email link after the tag fired. |
| Booking widget (calendar) | 1 | 0 | The opportunity has a `medium=calendar` attribution. |
| Other CRM action (`medium=other`) | 3 | 0 |  |
| Other inbound | 0 | 0 |  |
| No attribution recorded | 0 | 0 |  |
| **TOTAL** | **22** | **27** ✓ |  |

No SQL is unattributed. The "Unknown / Unattributed" row that previously appeared in the lead-source coverage card is gone for this period.

## SQL booking policy (current policy, effective immediately)

- A SQL is counted as a verified booking only when the contact had a verified Regulated Ads appointment within ±30 days of the SQL stage entry, **OR** the opportunity itself has a `medium=calendar` attribution.
- Trigger-link clicks are **not** counted as bookings. A click is an attribution event; a booking is a calendar event.
- For the Oct 4–10 window: 3 Reg Ads appointments, 0 SQL-coincident bookings. The booking card will show "0" for this period until a real calendar-coincident SQL arrives.

## Vertical email event feed — pending

The 8 vertical Send Email nodes live in the GHL workflow builder, not n8n-lt. n8n-lt returns 404 for those workflow IDs. Per Ed's selection, the recommended path is a GHL Marketplace `OutboundMessage` subscription pointing at `https://automations.livetransparent.com/webhook/lt-email-event-ingest` (live endpoint of `LT - Email Event Ingest` `ZrqFN8qLKO8eVHDc`, active v `e57c2664-f0f1-484f-b3a6-32bba41ff125`). That Marketplace config requires a browser session and is queued for the next session with browser access.

When wired, per-vertical `delivered`/`opened`/`clicked` will populate `Email_Events` and V1 Band 3 will replace the `—` placeholders for the 7 active vertical email senders (Alcohol, Cannabis Brands, Mushroom, Cannabis Dispensaries, Gambling, Peptides, Nicotine). The current 1,501-sent snapshot in `vertical-campaign-evidence.json` is a completed historical-window artifact, not an automatically refreshed feed; it will not double-count when the live event feed arrives.

## Operational follow-up

- SMS boundary repair (477 unauthorized + 434 timeouts)
- Booking-click intake `1diZyFmTqWQUEny3` parser repair
- GHL clicker drill-down to a supported query/filter
- GHL Marketplace `OutboundMessage` subscription (browser session)
