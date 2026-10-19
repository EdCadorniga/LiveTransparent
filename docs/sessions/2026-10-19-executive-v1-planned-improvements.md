# Executive Report V1 planned improvements — 2026-10-19

## Live result

- Deployed build `2026-10-19-v1-opportunity-actions`; image `v3ud1lum1svamymuor21upog:executive-v1-20261019-opportunity-actions`; container `395ebbd4c2e5`. Earlier same-day builds `2026-10-19-v1-improvements` and `2026-10-19-v1-booking-sources` were superseded.
- Facts payload unchanged: `accuracy-20261015-v1`, metric version `verified-booking-v2`.
- Legacy `/embed/executive/` unchanged; SHA256 `e675c97cd78f86699254a9e384692d1dd65dd1b9be82fe42d1c8c8274d967e6a`.
- Desktop (1440px) and emulated 390px: all sources loaded, no horizontal overflow, zero console errors on tested windows.

## Implemented

1. **Native SDR call inputs.** Band 4 now uses captured native GHL “Outgoing Calls by Status” weekly snapshots for Sep 27–Oct 3, Oct 4–10, and Oct 11–17 (`native-call-evidence.json`). Oct 11–17 matches the user-provided totals exactly: Marc 788/603 answered/95 no answer/60 busy/30 failed; Jason 427/325/69/26/7; team 1,215/928/164/86/37. WoW compares the matching prior weekly snapshot. Windows without a native snapshot show calls as `Unavailable`; partial Conversations call facts are not presented as native totals. Outputs (new booked contacts, verified SQLs, MQLs added) continue to come from `sdrOutputs`.
2. **Meetings detail table and honest outcomes.** The meetings card now renders contact, scheduled Pacific time, owner, approved calendar, recorded status, and booking creation time for every appointment row. Confirmed/cancelled use recorded status; `rescheduled` counts the reschedule flag (can overlap). Showed/no-show remain `Unavailable`; empty windows show `Unavailable`, not zero.
3. **Vertical sends for captured windows.** When a date-matched native GHL email cohort exists, the vertical table now fills Sends from `weekly-email-evidence.json` (Oct 4–10 = 1,501; Oct 11–13 in-progress snapshot). The note states the capture timestamp, email-only basis, and that delivery/engagement remain in Band 3. Other windows remain unavailable.
4. **Partial retargeting visibility.** Newsletter clickers are shown from the event ledger even when audience/suppression coverage is unavailable; unavailable fields are not replaced with zero, and no send authorization is implied.
5. **Action queue expansion.** Added unmatched/ambiguous inbound events and newsletter clickers, alongside MQL-stage contacts awaiting Sales; contract and follow-up sources remain explicitly unavailable.
6. **Label and description consistency.** Band 1/funnel use `MQLs added` and `Verified SQLs`; weekly table keeps `MQL stage entries` and `Sales Outreach entries`; vertical, email, and SMS static notes match current evidence behavior. The legacy unmatched email-engagement row is sorted last.
7. **Late-render race fixed.** The Band 1 comparison script (`renderVertical`) no longer leaves stale `Unavailable` send cells or a stale vertical note after its async summary load; `ltRenderVerticalAccuracy` is reapplied after that render.

## Verification

- `node --check reports/embed/executive-v1/band-improvements.js`; inline scripts parsed by `scripts/verify_deploy_v1.py`.
- nginx config validated in the built image; deployment stamp read back from production.
- Oct 4–10: vertical sends reconcile to 1,501 (169+39+116+0+244+117+688+128); headline 98 opportunities / 36 MQLs / 1 verified SQL / 3 scheduled meeting contacts; SDR retains native call totals.
- Oct 11–13: SDR uses call facts (276 attempted; busy+failed combined), vertical sends use the in-progress native snapshot (Oct 11–13), meetings/outcomes show Unavailable rather than zero.
- Default rolling week (Oct 11–17) loads with call-fact SDR inputs and no console errors.

## Still blocked / not implemented

- **Booking-link clicker GHL drill-down:** a supported GHL query/filter or deep link showing deduplicated clicker contacts by selected Pacific window is still unverified; no URL parameters were invented. Click intake `1diZyFmTqWQUEny3` remains the prerequisite and still needs a scoped parser repair + publication approval.
- **SMS delivery/auth:** 477 application auth rejections + 434 timeouts remain historical diagnostics, not sends. No replay or sender change; requires approval and provider reconciliation.
- **Closed SQL outcomes / recognized revenue:** no supported source; remains unavailable.
- **Complete per-vertical delivery/engagement feed:** native GHL delivery events are not wired; weekly email evidence is a captured cohort snapshot, not a live event stream.
- **Meeting showed/no-show:** requires GHL appointment status updates after meetings; not inferred.
- **Cold Facts latency:** unchanged (~2 minutes on uncached windows); this change does not claim performance resolution.

## Files changed

- `reports/embed/executive-v1/band-improvements.js`
- `reports/embed/executive-v1/index.html`
- `reports/embed/executive-v1/native-call-evidence.json`
- `scripts/deploy/deploy_report_vps_local.py`

No CRM writes, sends, workflow changes, or commits.

## Follow-up — booking-source detail and Lakeisha Williams (2026-10-19)

- Facts API `oxYDg6XnRBKhl1Xd` published `c540335c-0fb0-4c80-a897-904961ff8a2b`; reporting cache refresh `kBuW8Uq3EOJFQKNF` published `11e51495-aefc-43cd-9beb-e2adf9036ae0`; payload revision `accuracy-20261019-v2`. UI build `2026-10-19-v1-opportunity-actions`.
- **Lakeisha Williams:** booked 2026-10-08 12:41 PT for a meeting 2026-10-19 10:00 PT. She therefore belongs to the Oct 4–10 **new bookings created** cohort, not the Oct 11–17 **scheduled meetings** cohort. The meetings card now shows a separate “New bookings created in this window (meeting may be later)” table, so Lakeisha is visible in Oct 4–10 and Aviv Ben Menachem in Oct 11–17.
- **SQL count:** Oct 11–17 = 1 verified SQL (Aviv, booked Oct 13); Oct 4–10 = 1 verified SQL (Lakeisha, booked Oct 8). The count is by booking creation date, not meeting date; it is not 2 in the same week.
- **MQL detail:** `mqlSourcesDetailed` matches each booking-link MQL to the click ledger by contact and tag time. Oct 11–17: Nicotine 71 (`nicotinesequence` / `email` / `nicotine_brands_oct_2026`), Alcohol 1 (`alcoholsequence` / `email` / `alcohol_brands_oct_2026`), Cannabis Brands 1 (`cannabisbrandemail` / `email` / `cannabis_brands_oct_2026`), plus 14 GHL automation events with UTM not captured.
- **Opportunity source:** `opportunityActionSources` now infers the contact action medium (Email / LinkedIn / Calendar / SMS) and the specific current campaign from campaign/action tags; import source and `csv_import` medium are not used. Oct 11–17 totals 588: Nicotine Email 357, Gambling Email 124, Mushroom Email 28, Peptides Email 27, Dispensaries Email 19 + LinkedIn 5, Alcohol Email 18, Cannabis Email 4 + LinkedIn 2, Crypto Email 1, Calendar 2, and 1 LinkedIn/1 Calendar with campaign not captured. Named-campaign coverage 586/588.
- **SQL source:** the verified SQL row shows UTM fields when present; Aviv’s and Lakeisha’s bookings have no captured UTM and render `source / medium / campaign not captured`.
- **Verification:** `scripts/audit_v1_accuracy.py` passed all four windows with zero mismatches; desktop and 390px checks passed, no console errors or overflow. No CRM writes or sends.

## EOS handoff

Next-session state, Monday auto-production plan, and ordered backlog: [`2026-10-19-executive-v1-eos-handoff.md`](2026-10-19-executive-v1-eos-handoff.md).
