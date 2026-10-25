# Executive Report V1 source-coverage audit — 2026-10-26

## Objective and result

Ed asked to resolve the remaining Executive Report V1 source gaps after supplying the Oct 18–24 SDR call totals. The V1 report is deployed for `2026-10-18`–`2026-10-24` (`America/Los_Angeles`) and the supplied call snapshot is present. The other unavailable metrics could not all be filled from accepted, stable source evidence; the report now makes transport success distinct from metric completeness and states why vertical email/social metrics remain unavailable.

## Call snapshot and report changes

- Ed supplied the GHL call-report values for Oct 18–24: Marc 502 (384 answered, 64 busy, 18 no answer, 36 failed); Jason Bornillo 416 (278 answered, 37 busy, 81 no answer, 20 failed). Team reconciles to 918 (662 answered, 101 busy, 99 no answer, 56 failed, 0 ringing).
- Snapshot data is in `reports/embed/executive-v1/native-call-evidence.json`, captured `2026-10-26`; the call note correctly identifies it as Ed-supplied from the GHL call report. Commit `3ac8754` contains this data.
- Updated `reports/embed/executive-v1/band-improvements.js` to show a selected-window native-call-snapshot availability badge independently from `exec_v1_call_facts` health. The raw V1 call-facts feed remains `incomplete`; the snapshot is a separate accepted source.
- Changed the load message to “All report API requests loaded; metric-level coverage varies by section.” Vertical email and social notes now describe the missing selected-window evidence instead of implying that API success means full data coverage.

## Source reconciliation findings

- **Vertical email export:** the supported GHL `/conversations/messages/export` query must use Pacific offset bounds. A UTC `Z` range incorrectly returned zero. With Pacific offsets, repeated identical Oct 18–24 reads returned totals `0`, `37`, and `0`; on the 37-row response, all outbound rows lacked workflow IDs both at top-level and in email metadata, so they could not be assigned to one of the eight vertical workflows. The Oct 4–10 control returned 1,560 export rows (1,552 outbound), but those rows likewise lack the exact workflow mapping in the supported export. No per-vertical count was accepted from these inconsistent/unattributed results. No private GHL reporting endpoint was used.
- **Delivery/open/click/reply/bounce:** no accepted event-level feed with selected-window timestamps and campaign identity was found. Lifetime campaign statistics are not substituted for weekly facts.
- **SMS:** existing accepted attempt diagnostics are only for Oct 4–10 (477 application auth rejections and 434 timeouts). They do not establish current-week sends or deliveries. No replay or send was made.
- **LinkedIn:** the current V1 data has no reconciled vertical-attributed feed; the vertical invite/DM workflows remain paused. The known out-of-band invite issue is not a reportable campaign outcome.
- **Voicemail:** no Vapi custom-disposition facts were captured for the selected week.
- **Showed/no-show:** appointment status data does not support these outcomes. The new Opportunity custom fields visible in GHL were created Oct 25, but are not yet a verified, populated historical appointment-outcome source and are not wired into V1.
- **Closed SQL outcomes/revenue:** there is no accepted close-event date/source feed for this selected period. Current opportunity stage/status snapshots are not substituted for verified close events.
- **Social account statistics:** the selected-window V1 facts contain no accepted statistics rows covering all displayed platforms. A relative “last 7 days” response would not match this Oct 18–24 window and is not substituted. Post-placement counts remain a separate source.
- **Retargeting/action queue:** one newsletter clicker is visible, but the newsletter audience, suppression/replied state, next-action queue, stale proposal source, and follow-up SLA source are not complete in the selected-window facts.
- **Booking attribution:** no verified booking-source rows exist for this period; clicks are not treated as bookings.
- **Cache write acceptance:** the Oct 26 network repair verified the report cache-read path, but the cache-store path still needs the next natural refresh plus a same-key cache-hit verification. See `docs/sessions/2026-10-26-report-executive-cache-runner-network-fix.md`.

These are source/instrumentation gaps, not front-end display defects. No CRM writes, workflow edits, sends, retries, contact tags, or campaign changes were made in this audit.

## Validation and deployment

- `node --check reports/embed/executive-v1/band-improvements.js` passed.
- `python scripts/verify_deploy_v1.py` passed inline JavaScript validation and confirmed the local legacy report bytes match production.
- V1-only deploy completed. Live container: `42c035c562b2`; V1 build marker remains `2026-10-19-v1-opportunity-actions` (deployment uses the existing image tag). Legacy report remains unchanged at SHA256 `e675c97cd78f86699254a9e384692d1dd65dd1b9be82fe42d1c8c8274d967e6a`.
- Live browser readback confirmed the Oct 18–24 window, the 918-call team total and SDR rows, `GHL call snapshot …: available`, the coverage-qualified API-load message, and explicit vertical email/social coverage notes. One browser console 404 was the report favicon; no JavaScript error was observed.
- The API-source label `exec_v1_call_facts: incomplete` remains accurate for the automated raw facts feed; it is not the source used for the manual native weekly call snapshot.

## Ordered next steps

1. Obtain a stable supported GHL email export with exact message/workflow (or native captured queue-message) identity for each selected week; do not publish counts from the currently inconsistent export.
2. Reconcile SMS attempt IDs against sender idempotency/provider outcomes before any recovery; no timeout is assumed unsent and no replay is authorized by this reporting request.
3. Wire a date-scoped, campaign-attributed Email/SMS/LinkedIn/Vapi facts feed only after each event identity, timestamp, and status basis is verified.
4. Populate and verify appointment outcome/closed-event facts at their source, then wire those event dates and values into V1. Until then, keep showed/no-show, closed SQL outcomes, and revenue unavailable.
5. Add selected-window social-account statistics coverage (all displayed platforms) and retargeting audience/suppression/next-action facts; do not substitute relative windows or partial-platform sums.
6. Verify the natural cache-store execution and same-window hit after the runner network repair.

## Repository state

At close, only `reports/embed/executive-v1/band-improvements.js` is modified by this audit. Preserve the already-committed call snapshot change (`3ac8754`). No commit or legacy-report deployment was performed in this audit.
