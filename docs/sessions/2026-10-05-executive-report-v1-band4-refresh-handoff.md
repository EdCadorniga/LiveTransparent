# Executive Report V1 — weekly accuracy closeout

Date: 2026-10-05  
Period completed: 2026-09-27 through 2026-10-03 (`America/Los_Angeles`)

## Completed

- Ed directed that GHL native values are authoritative. Report display uses `America/Los_Angeles` regardless of browser locale.
- Updated and deployed V1 only. Legacy `/embed/executive/` source was left unchanged and its prior build marker still verifies live.
- Removed methodology subtitles beneath KPI values.
- Repaired lead-source coverage: SQL denominator is the funnel's 4 SQLs; 2 are attributed and the residual 2 are shown as `Unknown / Unattributed`. Combined coverage is 89% (14/14 MQLs and 2/4 SQLs).
- Rebuilt Band 4 from native GHL counts, added Ringing as its own status, fixed prior-week Busy (124, not the previous double-counted 175), and added week-over-week percentages.
- Changed pipeline timing text to identify 913 as a current snapshot.

## Accepted GHL values and Band 4 reconciliation

| Owner | Week | Attempted | Answered | Busy | No answer | Failed | Ringing |
|---|---|---:|---:|---:|---:|---:|---:|
| Marc | Sep 20–26 | 1,006 | 802 | 105 | 59 | 40 | 0 |
| Jason Bornillo | Sep 20–26 | 350 | 285 | 19 | 35 | 11 | 0 |
| Team | Sep 20–26 | 1,356 | 1,087 | 124 | 94 | 51 | 0 |
| Marc | Sep 27–Oct 3 | 807 | 568 | 115 | 61 | 62 | 1 |
| Jason Bornillo | Sep 27–Oct 3 | 566 | 435 | 32 | 76 | 21 | 2 |
| Team | Sep 27–Oct 3 | 1,373 | 1,003 | 147 | 137 | 83 | 3 |

Statuses reconcile to each attempted total and team totals equal Marc + Jason. When the previous period is zero, the UI shows `— WoW`.

| Owner | Booked | SQLs | MQL→SQL |
|---|---:|---:|---:|
| Cameron Karkut | 2 | 1 | 0 |
| Marc | 0 | 1 | 0 |
| Jason Bornillo | 0 | 0 | 0 |

## Other selected-week headline checks

- Opportunities created 16; MQLs entered 14; SQLs entered 4; MQL→SQL 29%; meetings booked 2; closed SQLs 0; revenue unavailable; new contacts 25.
- SMS summary is displayed from Campaign Channel Summary: sent 94, delivered 95, replies 1, failed 0.
- The facts API marks the broad historical call feed incomplete; the exact selected-week Band 4 snapshot is from GHL native totals. For this exact range the health badge identifies `GHL native call snapshot: ready`; other ranges retain the general feed completeness status.

## Verification and deployment

- Inline JavaScript passed `node --check`; deployment script passed `python -m py_compile`; `git diff --check` passed.
- Live browser showed the selected period, LA timezone, expected funnel/coverage/Band 4 values, zero visible KPI methodology subtitles, and no JavaScript errors.
- All three report API requests returned HTTP 200. V1 build marker `2026-10-05-v1-band4` and unchanged legacy marker `2026-08-17-v27-social-mql` were verified after deployment.
- Deployment image: `v3ud1lum1svamymuor21upog:executive-v1-20261005`.

Detailed implementation is in `reports/embed/executive-v1/index.html`; deployment verification uses `scripts/deploy/deploy_report_vps_local.py`. This closeout changed no CRM records and sent no messages.

## 2026-10-06 rolling default

When no explicit `from`/`to` dates are in the URL, V1 now computes the last completed Sunday–Saturday window from the current `America/Los_Angeles` date. It selected `2026-09-27`–`2026-10-03` on Oct 6 Manila; next week it will select `2026-10-04`–`2026-10-10`. Explicit URL date ranges remain pinned. Live build: `v3ud1lum1svamymuor21upog:executive-v1-20261006`, marker `2026-10-06-v1-rolling-week`; verified at `/embed/executive-v1/`. Legacy report remains unchanged.

## 2026-10-06 weekly Band 4 procedure and scheduler

- Saved the exact weekly GHL/OpenCLI procedure, LA Sunday–Saturday date rules, status/Team reconciliation, V1-only update/deploy/readback, and fail-closed behavior in `docs/runbooks/executive-report-v1-weekly-hermes-refresh.md`.
- The runbook's former Hermes ID `b231ec42ee37` was not present in the active `default` profile. Recreated as `cd6d1b15f148`; schedule was then advanced by 90 minutes to Monday 07:30 machine local (Singapore Standard Time, UTC+08:00), next run 2026-10-12 07:30 +08:00. `hermes cron status` confirms the job active and gateway heartbeat live.
- Windows Scheduled Task install would require admin approval; it was not approved. Hermes used a Startup-folder login item and started gateway PID 22904. The gateway needs the user login session to run. Delivery is local (Telegram is not configured).
- First scheduled run remains the unattended Chrome/GHL browser-access validation. If login, exact tooltips, correct LA dates, or reconciliations fail, the task must preserve the accepted snapshot and record a blocker; it must not deploy guessed values.

## EOS closeout — 2026-10-06

- Project/worktree: `C:\1_Ed's Active Work\Projects\LiveTransparent`, branch `codex/social-outreach-sync`. Worktree has seven modified tracked files; this is a shared worktree with ongoing Cannabis campaign and Executive Report V1 changes. Nothing was committed in this session; preserve those edits.
- Read-only Hermes verification: job `cd6d1b15f148` is active at `30 7 * * 1`; gateway PID 22904 is running with a fresh heartbeat. Next run is `2026-10-12T07:30:00+08:00`. Delivery is local. Gateway login startup depends on the Windows user session; the first scheduled OpenCLI/GHL run is not yet proven.
- Live V1 marker remains `2026-10-06-v1-rolling-week` (image `v3ud1lum1svamymuor21upog:executive-v1-20261006`) from the earlier verified deployment. No report redeploy or CRM action occurred during this closeout.
- Next steps: (1) on/after Oct 12, inspect `hermes cron runs` and the task output; confirm it opened the authenticated GHL native report, used the exact LA Sunday–Saturday window, reconciled both SDR rows and their prior week, then verified the live V1 build and percentages; (2) if browser access or data checks fail, reauthenticate/retry and keep the last accepted snapshot live until a complete validated refresh succeeds; (3) confirm V1's no-date URL advances to `2026-10-04`–`2026-10-10`. Do not assume rolling dates also refresh call counts.
- Documentation diff check: `git diff --check` passed before this closeout section; rerun after edits. No implementation tests were added or run in this EOS.
