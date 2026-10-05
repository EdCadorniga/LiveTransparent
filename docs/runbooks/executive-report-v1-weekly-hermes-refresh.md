# Executive Report V1 — Weekly Hermes Browser Refresh

**Status:** Hermes recurring job configured and active; job ID `b231ec42ee37`.
**Schedule:** Every Monday at 9:00 AM, timezone `Asia/Manila` (Telegram delivery).
**Reporting window:** The immediately preceding Sunday through Saturday, using `America/Los_Angeles` dates regardless of the operator's browser or local timezone.

## Objective

Use Hermes browser automation to gather fresh values from the authenticated GHL report and refresh the isolated Executive Report V1 call snapshot. All report dates must use `America/Los_Angeles`, even if the operator's browser or GHL UI displays `Asia/Manila`. Hermes must perform the data gathering on every run; it is not enough to tell Hermes that values exist or to reuse the documented baseline. The refresh must include Marc, Jason Bornillo, Team totals, native call statuses, Booked/SQL/MQL→SQL outputs, and week-over-week percentages versus the prior Sunday–Saturday week.

## Hermes task instruction

> Every Monday at 3:00 AM America/Los_Angeles, open the authenticated GHL report at `https://app.gohighlevel.com/v2/location/Zwz4relUXVPxx8uohnjV/reporting/reports/view/69bbeb2d088aabd9058eaf44` for location `Zwz4relUXVPxx8uohnjV`. Use Sunday–Saturday date fields and show `America/Los_Angeles` as the V1 reporting timezone regardless of browser locale. Ed has directed that GHL native report values are authoritative; do not reject or reinterpret native counts solely because the browser UI displays `Asia/Manila`. Read exact outbound call totals and Answered, Busy, Missed/No answer, Failed, and Ringing statuses for Marc Coetzee and Jason Bornillo, and the prior Sunday–Saturday comparison values. Also gather matching Booked, SQLs, and MQL→SQL values from the authenticated Executive Summary SDR output. Validate that each SDR's statuses sum to their total and Team equals Marc plus Jason. Calculate percentage change as `(current - previous) / previous * 100`; use an em dash when the previous value is zero. Update the V1 dated call snapshot and week-over-week values only after validation. Do not use the documented Conversations export as a substitute unless it has passed native parity validation. If login, MFA, CAPTCHA, report loading, date range, user filter, status totals, or output values fail validation, preserve the prior accepted snapshot and report the failure.

## Browser source details

The authenticated report page currently uses the private browser request:

`POST https://backend.leadconnectorhq.com/reporting/dashboards/revex/calls?locationId=Zwz4relUXVPxx8uohnjV`

The native widget request filters by `dateAdded`, `direction=outbound`, SDR `userId`, and a timezone. Ed has directed that the GHL native report values are authoritative for the requested date fields, even when the browser UI displays its local timezone as `Asia/Manila`; the V1 period label remains `America/Los_Angeles`. Do not copy or store bearer tokens, cookies, or browser-session secrets. Do not treat this private route as a supported GHL API contract; the GHL PIT returned HTTP 401 for it.

## Required output

Store a dated V1 snapshot containing:

- Reporting window start/end and timezone.
- Marc and Jason attempted, answered, busy, no-answer, and failed counts.
- Team totals calculated from the two SDR rows.
- Previous-week values and percentage changes for Team and each SDR.
- Source state: `GHL native browser report`, validation timestamp, and whether the refresh passed.

## Validation and safety gates

- The report week must be Sunday–Saturday; do not silently convert it to Monday–Sunday.
- Exact status totals must sum to each SDR's attempted total.
- Team totals must equal the sum of the Marc and Jason rows.
- A zero previous-week value produces `—`, not an invented percentage.
- Rounded card text such as `1.01K` is not accepted when an exact widget total is available.
- A browser login/MFA interruption, private-route error, mismatched export, or incomplete widget response is a failed run. Preserve the prior accepted snapshot and notify the owner.
- No CRM mutation, outbound call, message send, Marketplace subscription, or report-path change is part of this task.

## Current accepted baseline

Prior-week GHL comparison snapshot for `2026-09-20`–`2026-09-26`:

- Marc: `1,006` attempted — `802` answered, `105` busy, `59` no-answer, `40` failed.
- Jason Bornillo: `350` attempted — `285` answered, `19` busy, `35` no-answer, `11` failed.
- Team: `1,356` attempted — `1,087` answered, `124` busy, `94` no-answer, `51` failed.
- Executive Summary outputs: Marc `0` booked, `3` SQLs, `0` MQL→SQL; Jason `0` booked, `1` SQL, `1` MQL→SQL.

The current V1 implementation displays this baseline and status-specific prior-week percentages. Current completed snapshot and verification: `docs/sessions/2026-10-05-executive-report-v1-band4-refresh-handoff.md`.

## Known limitation

Scheduled browser tasks may pause if GHL requires login, MFA, CAPTCHA, or browser takeover. This is not a reason to substitute incomplete API-export numbers. Re-authenticate the browser session, rerun the failed window, and verify the output before publishing.
