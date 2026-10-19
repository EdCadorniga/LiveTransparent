# Executive Report V1 — EOS handoff (2026-10-19)

## Current live state

- UI build `2026-10-19-v1-opportunity-actions`; image `v3ud1lum1svamymuor21upog:executive-v1-20261019-opportunity-actions`; container `395ebbd4c2e5`.
- Facts API `oxYDg6XnRBKhl1Xd`: active/published `c540335c-0fb0-4c80-a897-904961ff8a2b`.
- Reporting cache refresh `kBuW8Uq3EOJFQKNF`: active/published `11e51495-aefc-43cd-9beb-e2adf9036ae0`.
- Payload revision: `accuracy-20261019-v2`.
- Legacy `/embed/executive/` unchanged; SHA256 `e675c97cd78f86699254a9e384692d1dd65dd1b9be82fe42d1c8c8274d967e6a`.
- Final n8n queue check: 0 `new`, 0 `running`, 0 `waiting`. Natural refresh `1165809` succeeded at 16:19:14 UTC.
- Git: branch `codex/social-outreach-sync`; commits `1a30907` (report changes) and `b383ce0` (security follow-up note) pushed to origin.

## What shipped this session

1. **Native SDR call snapshots.** Sep 27–Oct 3, Oct 4–10, and Oct 11–17 are captured in `reports/embed/executive-v1/native-call-evidence.json`. Oct 11–17 matches the user-provided native GHL totals: Marc 788/603/95/60/30; Jason 427/325/69/26/7; team 1,215/928/164/86/37. Uncaptured windows show `Unavailable`, not partial call facts.
2. **Meetings and new bookings.** Meetings table shows contact, PT scheduled time, pre-booking owner, calendar, status, and booking time. A separate new-bookings table shows contacts booked in the window even when the meeting is later.
3. **Lakeisha Williams reconciliation.** She booked 2026-10-08 12:41 PT for 2026-10-19 10:00 PT. She therefore appears in the Oct 4–10 new-bookings table, not the Oct 11–17 scheduled-meetings table. SQL count is by booking creation date: Oct 11–17 = 1 (Aviv), Oct 4–10 = 1 (Lakeisha).
4. **MQL source detail.** `mqlSourcesDetailed` matches booking-link MQLs to `lt_booking_link_clicks` by contact and tag time and exposes link, vertical, UTM source, UTM medium, and UTM campaign. Oct 11–17: Nicotine 71, Alcohol 1, Cannabis Brands 1, plus 14 GHL automation with UTM not captured.
5. **Opportunity action attribution.** `opportunityActionSources` infers medium from contact action tags (Email / LinkedIn / Calendar / SMS) and campaign from the current vertical/campaign tag. Import source and `csv_import` medium are not used. Oct 11–17 totals 588; 586 have a named campaign. Two rows remain `Campaign not captured`.
6. **SQL source UTM.** `sqlBooking` now exposes UTM source/medium/campaign when present; current bookings have no captured UTM and render explicitly as not captured.
7. **Late-render race fixed.** The Band 1 comparison render no longer overwrites vertical send cells or notes.

## Verification

- `python scripts/audit_v1_accuracy.py` passed all four windows with zero mismatches, including `sources_mql_detailed`, `new_bookings`, and `opportunity_actions`.
- Desktop 1440px and 390px: all sources loaded; no horizontal overflow; zero console errors.
- `scripts/verify_deploy_v1.py --deploy` passed inline JS, nginx, build stamp, and legacy-byte preservation.
- Facts and refresh workflows confirmed active with matching `versionId` / `activeVersionId`.

## Monday auto-production requirement

**Goal:** the completed Sunday–Saturday report and its prior comparison week must be computed, cached, validated, and visible in the first two hours of Monday, in `America/Los_Angeles` (PST/PDT handled automatically).

**Current gap:** the refresh workflow runs hourly at `15 * * * *` America/Los_Angeles but only refreshes window keys already present in `v1_facts_cache`. A new week's key may not exist yet, so Monday's default report can still be cold and take roughly 2–4 minutes.

**Recommended implementation (next session):**
1. Add a native Schedule Trigger for Monday `10 0 * * 1` and `10 1 * * 1` (00:10 and 01:10 Pacific), or a separate `LT - Executive V1 Monday Prewarm` workflow.
2. Compute the completed Sunday–Saturday window and the immediately preceding equal-length window in `America/Los_Angeles`; do not rely on a browser/Manila date.
3. Run the canonical Facts SQL for both windows and upsert `v1_facts_cache` with revision `accuracy-20261019-v2`.
4. Validate each payload: non-empty, correct `window.from/to`, `reportRevision`, `funnel.available`, and reconciled `mqlSourcesDetailed`, `newBookingDetails`, and `opportunityActionSources` totals.
5. Warm the public nginx cache by requesting `/api/report/executive-v1/facts?from=...&to=...`, or verify the native cache is hit.
6. Add a failure alert if the 01:10 run fails or no valid cache row exists by 01:30.
7. Test with an explicit historical window first; do not send CRM messages or change campaign workflows.
8. Keep the refresh idempotent and bounded by `statement_timeout`; no OS cron.

## Next-session backlog (ordered)

1. **Monday auto-production prewarm** — implement and validate as above; confirm the default page loads within seconds from cache by 02:00 Pacific.
2. **Booking-link clicker drill-down** — find a supported GHL query/filter or deep link for deduplicated clicker contacts in the selected Pacific window. Do not invent URL parameters or tag contacts.
3. **Booking-click intake repair** — `1diZyFmTqWQUEny3` still needs a scoped parser fix and publication approval before a controlled click/ledger/UTM test.
4. **SMS delivery boundary** — reconcile 477 auth rejections + 434 timeouts against provider outcomes; no replay without approval.
5. **Closed SQL outcomes / revenue** — no supported source yet; do not substitute snapshot zeros.
6. **Complete per-vertical delivery/engagement feed** — native GHL email events are not wired; weekly email evidence remains a captured cohort snapshot.
7. **Meeting outcomes** — showed/no-show requires GHL status updates after meetings; do not infer.
8. **Opportunity attribution reliability** — current `opportunityActionSources` is tag-inferred. Consider event-time workflow/opportunity creation evidence to raise confidence beyond campaign/action tags, while keeping `Campaign not captured` explicit.
9. **Cold-query performance** — four windows validate, but uncached queries remain roughly 2–4 minutes; profile/materialize only with accuracy guards.

## Safety gates

- Use only `n8n-lt`; never another n8n tenant.
- No CRM writes, sends, enrollments, campaign workflow changes, or contact tagging without explicit approval.
- No replay of click/SMS events without reconciliation.
- Never print or commit PITs, API keys, webhook secrets, JWTs, or database passwords.
- Preserve the legacy `/embed/executive/` report.

## Security follow-up (pre-existing, not introduced by this commit)

- Historical tracked files still contain legacy secret values (for example the 2026-10-12 integration health session doc and marketing workflow snapshots). They were already in Git history and were not added by this commit. Rotate the affected SimpleTexting/Unipile credentials and redact those historical files in a dedicated security pass; do not copy their values into new work.
