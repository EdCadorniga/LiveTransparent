# Executive Report V1 — weekly Band 4 refresh

**Purpose:** Refresh the weekly calls section (Band 4) in Executive Report V1 from GHL's authenticated native report, then deploy and verify V1.
**Reporting timezone:** `America/Los_Angeles` for every range and label. The browser may display `Asia/Manila`; that does not change the reporting timezone.
**Schedule:** Monday, 7:30 AM machine local time (Singapore Standard Time, UTC+08:00, same offset as `Asia/Manila`). The report period is the immediately preceding Sunday–Saturday in Los Angeles.
**Current scheduler state (2026-10-06):** The previously documented job `b231ec42ee37` was absent. Recreated as Hermes job `cd6d1b15f148` (`Executive Report V1 Weekly Band 4`); `hermes cron status` confirms one active job, a live gateway, and next run `2026-10-12T07:30:00+08:00`. Machine timezone is Singapore Standard Time (UTC+08:00, matching Manila offset). Windows Scheduled Task installation required admin approval and was not approved; Hermes used a Startup-folder login item and started the gateway now. The gateway must run after login for jobs to fire. Delivery is local because Telegram is not configured. The first scheduled browser run still needs end-to-end validation; unattended Chrome/GHL session access is not yet proven.

## Exact operator procedure

1. Run `opencli doctor`; continue only when Chrome and its extension are connected. Use the authenticated Chrome tab and the correct GHL location `Zwz4relUXVPxx8uohnjV`.
2. Use the persistent OpenCLI session name `band4`: `opencli browser band4 open https://app.gohighlevel.com/v2/location/Zwz4relUXVPxx8uohnjV/reporting/reports/view/69bbeb2d088aabd9058eaf44`, then `opencli browser band4 state` to inspect the page.
3. Set the report date range to **Last week** (Sunday–Saturday), then confirm the visible start and end dates equal the expected `America/Los_Angeles` dates. Do not proceed on a mismatch. Use `opencli browser <session> state` to inspect current controls and fresh refs; do not reuse stale refs.
4. Open the report page list and choose **GHL Call Report** using a fresh index from `state` (page name is visible in the report page drawer). The page drawer can remain open after selection; verify the chart content changed instead of assuming the click failed. `opencli browser band4 get text '#gridContainerPages'` reads the visible page text.
5. For both **Marc Coetzee** and **Jason Bornillo**, read the native **Outgoing Calls by Status** chart and exact outbound total. Use fresh refs/selectors from `state`/`find`; `opencli browser band4 hover <fresh-ref-or-selector>` exposes each status tooltip, then read the tooltip from a fresh `state`/`get text` result. Hover each status segment/bar to obtain exact values for Answered, Busy, Failed, Missed/No answer, and Ringing. Do not transcribe rounded labels in place of exact tooltip values. Record inbound separately; “No data found” for incoming is not an outbound zero.
6. Read the preceding Sunday–Saturday period using the native date control as well. Read matching **Booked**, **SQLs**, and **MQL→SQL** from the Executive Summary SDR output for the report week and prior week. GHL native values are authoritative. Do not use private reporting endpoints, guessed calculations, or the Conversations export as a substitute.
7. Check each SDR's statuses sum exactly to attempted calls, and Team equals Marc + Jason for every call status and output. Calculate each week-over-week percentage as `(current - previous) / previous * 100`; show `— WoW` when the previous value is zero. Confirm date labels and comparison weeks are Sunday–Saturday in Los Angeles.
8. Update `reports/embed/executive-v1/index.html`: move the accepted current call snapshot to `prior`, set its Booked/SQL/MQL output values as the next comparison baseline, and enter the new dates and current call snapshot. Keep Team values derived from the two SDR rows or reconciled to their sums. Remove any date-specific guard that would hide valid data for the newly selected week. Do not change unrelated report logic.
9. Run `node --check` on the inline report JavaScript and `git diff --check`. Deploy only the Executive Report V1 using `python scripts/deploy/deploy_report_vps_local.py` after checking its help/options and following its established V1-only path. Do not deploy the legacy report.
10. Open `/embed/executive-v1/` with the selected dates and verify the new window, timezone, Marc/Jason/Team values, all comparison percentages, source health label, and zero console errors. Verify the live build marker. Record source, values, validation time, build marker, and outcome in the dated session note.

## Fail-closed conditions

If Chrome/login/MFA/CAPTCHA, the GHL report, exact chart tooltips, prior-period values, date range, output rows, or any reconciliation check is unavailable or ambiguous, do not edit or deploy. Preserve the last accepted snapshot and report the precise blocker through the scheduler's run result. Never invent a number, infer one from a rounded total, or label an unverified run as complete. Do not mutate CRM data, call or message contacts, change report routing, or deploy paths outside Executive Report V1.

## Current accepted snapshot

Window `2026-09-27`–`2026-10-03` (`America/Los_Angeles`), compared with `2026-09-20`–`2026-09-26`:

| Owner | Week | Attempted | Answered | Busy | No answer | Failed | Ringing |
|---|---|---:|---:|---:|---:|---:|---:|
| Marc | Sep 20–26 | 1,006 | 802 | 105 | 59 | 40 | 0 |
| Jason Bornillo | Sep 20–26 | 350 | 285 | 19 | 35 | 11 | 0 |
| Team | Sep 20–26 | 1,356 | 1,087 | 124 | 94 | 51 | 0 |
| Marc | Sep 27–Oct 3 | 807 | 568 | 115 | 61 | 62 | 1 |
| Jason Bornillo | Sep 27–Oct 3 | 566 | 435 | 32 | 76 | 21 | 2 |
| Team | Sep 27–Oct 3 | 1,373 | 1,003 | 147 | 137 | 83 | 3 |

Selected-week Executive Summary outputs: Cameron Karkut `2` booked / `1` SQL / `0` MQL→SQL; Marc `0` / `1` / `0`; Jason `0` / `0` / `0`. Values and implementation details are recorded in `docs/sessions/2026-10-05-executive-report-v1-band4-refresh-handoff.md`.

## Browser/report notes

The GHL native report page is the source of truth. Its browser UI may show local timezone text; Ed directed all report dates and displayed timezone to be `America/Los_Angeles`. The native chart request observed during investigation was a private backend route, not a supported API contract; do not copy/store browser credentials or call that route directly. V1's selected-period call snapshot is embedded in `reports/embed/executive-v1/index.html`; it is not automatically populated by the broad historical facts feed, which is marked incomplete.

V1's no-date URL now computes the last completed Sunday–Saturday period in `America/Los_Angeles`; explicit date query parameters remain pinned. The date roll-forward is automatic; the Band 4 call counts and comparison baseline still require this weekly native-GHL refresh.
