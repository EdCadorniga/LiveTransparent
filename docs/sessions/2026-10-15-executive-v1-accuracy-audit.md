# Executive Report V1 accuracy audit — 2026-10-15

## Live result

Deployed `2026-10-15-v1-accuracy` at `/embed/executive-v1/`.

- Facts `oxYDg6XnRBKhl1Xd`: active/published `85e82820-b775-4c3f-aea8-dc2456c4b6b6`.
- Reporting cache refresh `kBuW8Uq3EOJFQKNF`: active/published `b594cd8f-e204-40cb-9acd-a4de13b38f73`.
- Payload revision: `accuracy-20261015-v1`.
- Natural refresh execution `1145256` succeeded, 00:15:00–00:19:16 UTC Oct 15.
- Legacy report SHA256 preserved: `e675c97cd78f86699254a9e384692d1dd65dd1b9be82fe42d1c8c8274d967e6a`.

This supersedes earlier reporting-count/cache status in the October 13 handoffs. Live state at entry already contained canonical MQL/booking logic and an hourly cache; those were not newly created in this session.

## Defects corrected

1. **Owner/UTM coverage incorrectly determined SQL eligibility.** The previous canonical query excluded a real approved-calendar booking without a recognized pre-booking owner or click attribution. SQL now counts the contact's first non-canceled approved-calendar appointment by its recorded creation date, independently of owner/UTM capture. Canceled/invalid/deleted appointments do not qualify. Missing creation timestamps are not replaced with scheduled time for SQL. Scheduled meeting history remains a separate cohort and explicitly retains canceled records.
2. **False conversion chronology.** A contact appearing in both window cohorts could count as converted even when the MQL tag came after the booking. Require `mql.added_at <= booking.booked_at`. For Oct 4–10 and Sep 27–Oct 3 the one booking in each week preceded its MQL tag; conversion is therefore 0, despite one verified SQL in each window. The funnel raw conversion now uses `mql_to_sql_converted`, not all SQLs divided by MQLs.
3. **Monthly requests failed.** A cold Sep 1–30 request failed after approximately 240 seconds, returning an empty HTTP 200. Execution `1145194` reported runner disconnection; this does not prove the initial disconnect cause. The query unnecessarily computed obsolete payload fields subsequently overwritten by canonical metrics, including expensive legacy correlated subqueries. Removed unused projections; materialized narrow ownership evidence rather than repeatedly scanning large JSON snapshots. Revised direct SQL completed all four validation windows in 107–128 seconds during the apply pass.
4. **Monthly opportunity sources disagreed.** Sep 1–30 source rows totaled 1,535 against 1,533 created opportunities. Source membership now uses the exact Pacific creation-date opportunity cohort used by the headline. Both total 1,533.
5. **Vertical parity gaps.** Canonical MQL/SQL grouping now retains contacts missing from the latest contact snapshot as Unclassified. Meetings use both approved calendars in vertical rows, matching the headline. Unverified closure counts are unavailable, consistent with the funnel, rather than unrelated snapshot zeroes.
6. **False email zero.** Band 3 previously showed 0 emails while the reconciled vertical rows totaled 1,501. The headline now says **Vertical emails sent**, uses matching date-scoped evidence, and is unavailable when no matching evidence exists. Legacy engagement events are not combined into a false send-cohort funnel.
7. **Misleading social totals.** Previously a partial account-statistics aggregate (one LinkedIn post) was presented as the total while the source post ledger contained eight placement records. Header and channel post counts now use the same ledger: 6 LinkedIn + 2 Instagram + 0 Facebook = 8 records, with 6 published and 2 failed explicitly stated. Cross-platform account totals are N/A without every displayed platform's exact-window coverage; missing comments are not silently zero. Account-statistics posts remain a distinct basis.
8. **Stale descriptions.** Corrected SQL/source labels, scheduled-vs-created booking language, owner-context wording, MQL-stage action-queue wording, and New+Qualified pipeline stock labels. Canonical SQL evidence no longer says evidence is missing merely because the obsolete breakdown is empty. Weekly movement remains explicitly full Monday-start calendar buckets that can extend beyond the chosen range; its MQL-stage/Sales-Outreach-entry labels remain separate from headline qualification events.

## Reconciliation

All four windows passed these checks against newly computed reporting SQL, then public Facts responses: MQL and SQL totals equal their source and owner totals; vertical MQL/SQL/meeting totals equal headline totals; opportunity-origin totals equal created-opportunity totals.

| Pacific window | Opportunities created | MQL ledger contacts | Verified SQL contacts | MQL→SQL converted | Scheduled meeting contacts | New booked contacts |
|---|---:|---:|---:|---:|---:|---:|
| Oct 4–10 | 98 | 36 | 1 | 0 | 3 | 1 |
| Sep 27–Oct 3 | 16 | 24 | 1 | 0 | 2 | 1 |
| Sep 1–30 | 1,533 | 201 | 8 | 3 | 9 | 10 |
| Oct 11–14 | 365 | 83 | 0 | 0 | 1 | 0 |

Default-week new contacts remain 1,744 vs prior 22; LinkedIn backfills 0 vs 5 remain separate. Historical Sales Outreach entries 27 and MQL-stage entries 22 are preserved separately from the current headline 1 SQL / 36 MQL contacts.

## Verification performed

- SQL EXPLAIN and four complete direct SELECTs before saving; no reconciliation mismatches.
- Fresh REST readbacks: updated reporting workflows active with matching version/activeVersion IDs. No campaign workflow changed or executed.
- Public JSON across all four windows reconciled after deployment.
- September monthly Facts: 1.141 seconds, proxy MISS / native reporting cache HIT, correct revision. Cold query latency remains significant; this is not a claim that all uncached requests are fast.
- Default-week desktop and emulated 390px mobile: all sources loaded, no horizontal overflow, no console warnings/errors.
- Default-week call status sums: Jason 778 = sum of all five status buckets; Marc 1,027 = sum of all five status buckets; team 1,805. Response detail and aggregate both contain 27 events.
- JavaScript parses; nginx configuration passes; legacy report bytes unchanged.

## Remaining source limits

- SQL closure cohorts, recognized revenue, and complete contact-attributed vertical send/delivery feeds remain unavailable. No source gap was converted into zero.
- Weekly email evidence is a captured native-GHL cohort snapshot, not a fresh event stream. Delivery/engagement states have a displayed capture timestamp. Failure categories can overlap other states; do not infer an exclusive sent-minus-delivered funnel from those counters.
- SMS attempt diagnostics remain historical Oct 4–10: 477 application auth rejections + 434 timeouts. They are not provider sends/delivery failures. No resend or operational SMS repair was performed.
- Scheduled meeting counts and new-booking-created counts intentionally differ. Current snapshot ownership is not proof of who booked. Pre-booking assignee is ownership context only; missing ownership stays Unassigned.
- Historical deleted opportunities remain in historical created counts; this does not guarantee parity with a present-day GHL search.
- Full cold Facts queries remain around two minutes. More extensive performance work and arbitrary-window source coverage remain open. Four tested windows are not proof of every possible range or every upstream CRM record's completeness.
- Local pre-existing `canonical-metrics.sql` and older patch helpers differ from the live query. Do not blindly reapply them. `scripts/fix_v1_accuracy.py` derives from freshly read live SQL and validates before publication; retain the live revision as authoritative.

## Changed artifacts and continuation

New helpers: `scripts/audit_v1_accuracy.py`, `scripts/inspect_v1_query_plan.py`, `scripts/fix_v1_accuracy.py`. UI changes: `reports/embed/executive-v1/index.html`, `band-improvements.js`; deployment stamp updated in `scripts/deploy/deploy_report_vps_local.py`.

Re-run `python scripts/audit_v1_accuracy.py` for read-only public parity checks. `--direct` is deliberately more expensive. The fix helper fails closed if prior anchors or paired refresh SQL differ; inspect live state before reuse. Preserve existing dirty worktree. No commit, pack operation, CRM writes, or sends in this session.
