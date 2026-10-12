# Executive Report V1 — EOS and next-session handoff (2026-10-13)

> **Continuation supersedes the next-action order below:** Ed asked to verify existing vertical enrollments, sender fields, email/SMS scheduling, and past-week sends. That audit is complete in [`2026-10-13-vertical-enrollment-send-reconciliation.md`](2026-10-13-vertical-enrollment-send-reconciliation.md). No re-enrollment is needed for the audited cohort. The new first priority is **477 unauthorized SMS responses +434 timeouts and the future09:00 queue vs10:00 sender guard**, followed by native email/reporting reconciliation. Use that document's latest copy-ready prompt. The booking-click parser defect and clicker GHL query/filter TODO below remain open.

## Objective and result

Restore the empty Facts API, reconcile the weekly contact cohort, separate SQL entries from verified bookings, implement supported vertical metrics, and deploy/verify V1. Completed reporting work is summarized in the opening section of `executive_report_v1_plan.md`.

**New EOS blocker:** booking-click intake is active but its `Process Click` Code node has two `const cfgValues` declarations (lines 14/15 of live jsCode). Executions **1132673 / 1132676** failed with `Identifier 'cfgValues' has already been declared`. Their executed-node lists contain only `Webhook`, `Config`, `Process Click`; neither reached the downstream contact-update node. These executions were discovered read-only during EOS, not initiated by this session. Their originating callers/events have not been reconciled. No intake repair, publication, or replay was performed during EOS.

**New Ed TODO:** add a report link to a supported **GHL query/filter showing the contacts who clicked booking links**. Recorded for implementation, not built in EOS. Clicks must remain separate from appointments/SQLs.

## Fresh live readback

All three workflows are active, not archived, and have matching draft/active versions:

| Workflow | ID | Active version | Nodes | Latest checked executions |
|---|---|---|---:|---|
| V1 Facts API | `oxYDg6XnRBKhl1Xd` | `e8c3dd1a-1000-4162-b784-93ad161d0e06` | 5 | `1132767`, `1132764` success |
| V1 Data Materializer | `knc2wxe4pyYIJ5tw` | `fdae462c-55b6-4616-b322-e0ca49478c3e` | 4 | `1132746`, **1131832** success |
| Booking Link Click Intake | `1diZyFmTqWQUEny3` | `548c2d96-aec1-4dcd-8e22-cbb055ba5c99` | 6 | `1132676`, `1132673` error at `Process Click` |

- No `new`, `running`, or `waiting` rows appeared in each workflow's latest 20 executions. This is a bounded inspection, not an all-history guarantee.
- The manually acknowledged materializer execution **1131832**, initially unaccepted/queued, is now independently verified successful: Oct 12 16:03:51–16:11:01 UTC. Latest materializer 1132746 also succeeded. Stable materialized current-week cohort was measured at 1,744.
- Public V1 page HTTP 200, marker **`2026-10-13-v1-vertical-facts`**, streaming evidence-renderer hook present. Deployed image: `v3ud1lum1svamymuor21upog:executive-v1-20261013-vertical-facts`.
- Legacy report local/production bytes still match; accepted SHA256 `e675c97cd78f86699254a9e384692d1dd65dd1b9be82fe42d1c8c8274d967e6a`.

## Accepted facts and definitions

For Oct 4–10 / Sep 27–Oct 3, America/Los_Angeles:

- Opportunities 98/16; MQLs 22/14; SQLs 27/4; MQL→SQL 13.64%/28.57%; meeting contacts 3/2.
- Ordinary new contacts **1,744/22**; LinkedIn backfills **0/5**; date-unavailable 0/0. The old 1,760/25 comparison is superseded.
- Contact `hWikhd4bEQNJLcQWmXkh` was created Oct 11 00:42 UTC = Oct 10 Pacific. V1 includes it; legacy Summary's timezone-unqualified DATE excludes it. The Summary was not modified.
- Historical raw opportunity counts include two deleted records per week (live GHL 96/14). Keep this source boundary.
- Current SQLs: **27 without booking evidence / 0 verified**. Prior: 3 without evidence + 1 calendar appointment missing UTM. Meeting and SQL cohorts are independent.
- Nine vertical rows use latest raw contact Vertical, field `ODs8fBt5te5HEfSJ91pY`; preserve Unclassified. Both weeks' supported leads/backfills/MQLs/SQLs/meeting contacts/closed outcomes/captured inbound events reconcile.
- Responses are captured inbound event counts, not distinct clickers or campaign-attributed replies. Sends/revenue remain NULL/unavailable. Won/lost use the existing latest-snapshot rule, not reconstructed closing-event timestamps.

## Verification and review findings

- Full live-source SQL EXPLAIN passed read-only before saving. The original Facts defect was missing END in SQL→Closed CASE, not the contact CTE.
- Full read-only query execution for both weeks asserted vertical totals against report-wide facts before deployment; both public weekly endpoints returned populated JSON after publication.
- Inline JavaScript syntax, Python helper compilation, nginx configuration, local/live desktop and 390px overflow checks passed.
- A delayed-Summary local regression check and final live all-sources-loaded readback verified the streaming race fix: the SQL evidence card retains 0 verified / 27 without evidence rather than reverting to 100% classification coverage.
- Initial browser/harness timeouts were not accepted on their own; later rendered data and successful readbacks established acceptance. An earlier Summary 504 recovered. Cold source requests remain slow (roughly 80–215 seconds plus queue/cache-lock delays observed); performance is not resolved.
- Band 3 audit: current `Email_Events` contains legacy Emerald opens/clicks/bounces/unsubscribes, not a reconciled eight-vertical October email-send/event feed. SMS has 18 provider-response send rows (15 legacy `john_sms2`, two Emerald intros, one missing template) and generic delivery/unsubscribe callbacks. These do not establish complete per-vertical campaign delivery.
- Additional label-review TODO: the base funnel renderer still pairs period SQL/MQL counts with the cohort-based conversion percentage. Preserve the authoritative cohort percentage; review/clarify the displayed numerator/denominator before changing that presentation. No EOS code fix was made for this finding.

## Ordered next steps and acceptance

1. **Repair booking-click intake before testing.** Fetch live graph, confirm duplicate declaration, back up, compare `scripts/patch_booking_link_click_intake.py` with live source to identify how duplication occurred. Validate the actual Code node offline with a meaningful parse check. Obtain scoped authorization before saving/publishing the intake repair; EOS is not that authorization. Preserve link maps, idempotency, Config, and last-touch-only writes. Re-read version/graph after any authorized mutation. Review the two failed events; do not replay automatically.
2. **Approved controlled booking-click verification.** Ed has not approved the internal contact/event. Choose the internal contact with Ed, inspect all relevant link-trigger automations, then perform only the approved event. Verify one idempotent ledger row, UTM map, preserved first-touch fields, last-touch readback, and absence of a fabricated appointment. No campaign email/SMS send is needed or authorized by this TODO.
3. **Booking-link clicker → GHL filter drill-down (Ed's request).** Define the deduplicated contact cohort from verified `lt_booking_link_clicks` within the report-selected Pacific window, optionally by booking link/campaign. Inspect authenticated GHL Contacts/Smart Lists/Trigger Link filtering and verify a supported saved-filter/deep-link mechanism rather than inventing query parameters. Add a clearly labeled link in V1 that opens the matching GHL contacts; reconcile exact contact IDs/counts against the ledger. Keep clickers separate from booked contacts. If native GHL cannot reproduce the ledger/date filter, document that limitation and ask Ed to choose a supported alternative. Do not add tags or alter CRM records merely to build the filter without approval. Test deduplication, empty cohort, date changes, cross-period stale links, and authenticated destination behavior.
4. **Reconcile Band 3 vertical Email/SMS feeds.** SMS: join canonical provider-message IDs to outcomes, contact IDs, current Vertical, and campaign/step; separate attempts, provider-accepted sends, deliveries, failures and replies. Email: obtain supported native October workflow evidence, confirm message/event identity and campaign mapping. Retain Unclassified and unavailable values; reconcile denominators before exposing campaign rows. Any new production capture workflow/caller/CRM write requires the relevant authorization.
5. **Reporting polish/performance after source integrity.** Review cohort labels and repeated current-period requests, run read-only query plans, and distinguish query cost from queue/cache latency. Scope any implementation separately. Preserve accepted counts and legacy page. For future approved V1 changes, rerun syntax, exact-count, delayed-source, desktop/mobile and legacy-SHA checks.

## Repository and rollback

- Branch `codex/social-outreach-sync`; HEAD `5613544`. No commit made. Worktree remains modified/untracked, with pre-existing LinkedIn cleanup and contact-import CSV changes; preserve them.
- Session implementation: `reports/embed/executive-v1/index.html`, `DATA-REQUIREMENTS.md`, new `lt-exec-v1-vertical-performance.sql`; `scripts/repair_v1_facts_sql.py`, `continue_v1_reporting.py`, `verify_deploy_v1.py`; updated deploy helper and missing-END correction in `patch_v1_band1_facts.py`. SQL/contact-materializer files and opportunity-reconciliation helper include earlier work and should not be overwritten wholesale.
- Workflow backups (sensitive, local-only): `%LOCALAPPDATA%\Temp\opencode\v1-facts-before-repair-20261012T235556.json` (broken pre-repair state) and `v1-facts-before-repair-20261013T001009.json` (repair-only state before vertical addition). Inspect versions before restoring; do not restore the broken source indiscriminately.
- Reports compose backup: `/data/coolify/applications/v3ud1lum1svamymuor21upog/docker-compose.yaml.pre-campaign-accuracy`; overwritten on successive deploys, so verify the referenced image before rollback.
- The session-owned local preview server PID 36940 was stopped. No production operations occurred during EOS; only read-only inspection and documentation changes.

## Copy-ready next-session prompt

> Continue LiveTransparent Executive Report V1 from `executive_report_v1_plan.md` (opening CURRENT section) and `docs/sessions/2026-10-13-executive-v1-facts-vertical-eos.md`. Use only n8n-lt REST via `.env` N8N_LT_API_KEY; all available n8n-katwill connectors are the wrong tenant. Fetch live state before edits. Preserve the dirty worktree, legacy `/embed/executive/`, and existing accepted V1 build `2026-10-13-v1-vertical-facts`.
>
> Facts `oxYDg6XnRBKhl1Xd` is healthy, active/published `e8c3dd1a-1000-4162-b784-93ad161d0e06`. Oct 4–10 / Sep 27–Oct 3 contacts are 1,744/22, backfills 0/5; opportunities 98/16, MQL 22/14, SQL 27/4, meetings 3/2. The one-contact Summary difference is timezone-based and resolved. Nine vertical rows reconcile; sends/revenue remain unavailable and responses mean captured inbound events. Current 27 SQLs lack booking evidence. Do not reclassify them as bookings.
>
> First investigate/prepare repair of booking-click intake `1diZyFmTqWQUEny3`, active version `548c2d96-aec1-4dcd-8e22-cbb055ba5c99`: Process Click declares const cfgValues twice at live lines 14/15; errors 1132673/1132676 confirm the parser failure. Back up, validate actual node syntax, compare the patch helper, obtain scoped repair publication approval, then verify saved/active versions. Do not blindly rerun helpers or replay failed events. Controlled click testing still needs Ed's approval and internal contact selection.
>
> Next implement Ed's new TODO: a link from the report to a supported GHL query/filter showing who clicked booking links. Use verified click-ledger contact IDs and the selected Pacific window; deduplicate; keep clickers separate from appointments/SQLs; verify actual GHL filter/deep-link support instead of guessing URL parameters. If tagging/contact writes are needed, ask before doing them. Reconcile the destination contact IDs/counts to the ledger and handle no-data/date changes.
>
> Then reconcile complete October vertical Email/SMS provider feeds before showing per-vertical campaign sends/delivery/replies. Current legacy Email_Events and generic SMS events are incomplete; leave unsupported values unavailable. Investigate slow query/queue/cache behavior and clarify cohort conversion labels after source integrity. No sends, contact/tag writes, event replay, campaign activation, uncontrolled test, or credential exposure; no commit unless requested. Update the step-status table and handoff as each step is verified. Repomix/packlive remains paused.
