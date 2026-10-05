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
