# Executive Report V1 — GHL call source exploration and EOS closeout

**Date:** 2026-09-29  
**Scope:** Establish a trustworthy GHL call basis for Executive Report V1, test supported source options, document the event receiver and its verification boundary, and leave an executable continuation plan.  
**State:** Partially complete. Exact native-report counts are deployed as a one-period snapshot. A signed webhook receiver is published but not subscribed or positively tested.

## Current objective and reporting contract

The V1 SDR performance section needs GHL outbound calls grouped by the assigned user/SDR, with statuses that reconcile to GHL's native per-SDR call widgets. The checked native report is:

- Report ID: `69bbeb2d088aabd9058eaf44`.
- Selected dates: `2026-09-20` through `2026-09-26`.
- Native widget filters: `dateAdded`, `direction=outbound`, and user ID; report timezone `Asia/Manila`.
- Marc (`sqGx5rp3oAUG610NXyjU`): **1,006** = 802 answered, 105 busy, 59 no-answer, 40 failed.
- Jason Bornillo (`yU85G6kfhtW4vUtx3QE6`): **350** = 285 answered, 19 busy, 35 no-answer, 11 failed.
- The native display rounds Marc to 1.01K. The earlier 982 reference does not match the current exact widget response and is superseded.

The captured widget values are exact for that window only. They are not evidence of a refreshed report feed or complete history. V1 must continue to distinguish the dated snapshot from ordinary supported-API facts.

## What was attempted and learned

1. **Read the authenticated GHL report widgets.** The live report showed the exact per-SDR counts above. `dateAdded`, outbound direction, and `userId` are the relevant filters; the browser's report timezone was `Asia/Manila`. A rounded card value should not replace the exact widget total.
2. **Try the GHL PIT against supported APIs.** Supported location/Conversations calls were authorized. The private report widget route `/reporting/dashboards/revex/calls` returned HTTP 401, `The token is not authorized for this scope`. Do not build ongoing ingestion against that private widget route or guess undocumented report endpoints.
3. **Consider GHL's Voice AI call-log API.** Its documented logs concern the Voice AI product and do not reproduce the human SDR widgets. It is not an acceptable source for this requirement.
4. **Initial export search (superseded by the addendum below).** The initial documentation pass missed the official `GET /conversations/messages/export` endpoint. It was later found and tested; its records did not reconcile to the native widgets.
5. **Try a supported paginated Conversations scan.** `LT - GHL Daily Calls Ingest` (`SqNQ0BYaTdcqyt1l`, published version `98a4f785-19bf-4f17-a95e-1222141923bf`) uses bounded retries and a 95-day conversation scan that includes conversations whose latest activity is not a call. Scan progress reached cursor offset 2,600; a larger batch disconnected the runner. The scan is incomplete, and raw totals (including Marc 185 / Jason 26 in the earlier partial raw window) did not reconcile to the native widgets. Do not label these partial counts authoritative or imply that a historical API parity test passed.
6. **Review official `OutboundMessage` webhook support.** GHL's event schema supports `CALL` messages and supplies identifiers/date/direction/user/status/duration fields. The installed app `Transparent eCom Social Inbox` has `conversations/message.readonly`. Marketplace subscriptions are configured in app settings, not by the API.
7. **Build the signed event receiver.** Active/published n8n workflow `LT - GHL Outbound Call Event Ledger (Webhook)` (`SA5SF1cZQcVf3IyB`, version `15b2944f-5b71-40fe-b97a-d87718cd6cdb`, 5 nodes) accepts POST `/webhook/lt-ghl-outbound-message-call`, validates GHL's raw-body signature, normalizes outbound CALL events, and idempotently upserts by `messageId`. Non-call events and invalid requests use a response path that bypasses the database node.
8. **Run negative-signature checks only.** Two requests omitted a valid signature. Endpoint returned HTTP 401 `{"ok":false,"outcome":"invalid_signature"}`. n8n executions `1062819` and `1062820` ended `success`; node-level data showed `verified=false`, `shouldStore=false`, branch `Respond without writing`, and no `Persist GHL Call Event` execution. This demonstrates rejection-path/raw-body normalization behavior only. It does not verify GHL's valid signature or a database insert.
9. **Deploy the V1-only snapshot and source note.** V1 Facts API (`oxYDg6XnRBKhl1Xd`) active version `9a17c3c2-45d2-477e-9c01-3bea0a537ae3` returns the native numbers only for the exact captured period, with a dated snapshot basis. `reports/embed/executive-v1/index.html` now uses the facts API basis for the SDR metrics/source note. `reports/embed/executive-v1/DATA-REQUIREMENTS.md` and `executive_report_v1_plan.md` record the limitation. Deployment used `scripts/deploy/deploy_report_vps_local.py`; the V1 path returned HTTP 200 and contained the `calls-source-note` element. The original `/embed/executive/` report was not altered.

## Live state and worktree

- V1 Facts API: `oxYDg6XnRBKhl1Xd`, active and published version `9a17c3c2-45d2-477e-9c01-3bea0a537ae3` (date-specific snapshot override).
- GHL outbound call receiver: `SA5SF1cZQcVf3IyB`, active and published version `15b2944f-5b71-40fe-b97a-d87718cd6cdb`, 5 nodes. Read-only workflow inspection confirmed `active=true`, `versionId == activeVersionId`, and one webhook trigger. No `new`, `running`, or `waiting` executions were found for it at closeout.
- GHL call poller: `SqNQ0BYaTdcqyt1l`, published version `98a4f785-19bf-4f17-a95e-1222141923bf`; historical backfill is incomplete.
- Marketplace event subscription: **not configured**. Marketplace developer login was unavailable in the browser session; no subscription or app setting was changed.
- No real call was placed, no valid signed event sent, no CRM record altered, no mass export imported, and no data table row written by the two negative tests.
- Before this EOS documentation pass, `git status --short` showed three modified tracked files: `executive_report_v1_plan.md`, `reports/embed/executive-v1/DATA-REQUIREMENTS.md`, `reports/embed/executive-v1/index.html`. These are the V1 implementation/source-basis changes. No commit was made. The EOS documentation adds this handoff, the `AGENTS.md` summary and repomix-path correction, and the `Project Status and Next Steps.md` status item.
- The prescribed `. $PROFILE; packlive` command was inspected after execution; the profile function hardcodes a different OneDrive checkout rather than this active `C:\1_Ed's Active Work\Projects\LiveTransparent` workspace. Treat that invocation as not refreshing this workspace's repomix; the current repo's repomix was refreshed directly with an explicit include set after updating documentation. `AGENTS.md` now records this path mismatch so future sessions verify the target before packing.
- Recent commit at review: `2c7cb37 Reconcile September workflow and report updates`. No secrets or API key values are included in this handoff.

## Known gaps and risk checks

- Marketplace must subscribe to `OutboundMessage` and use the production receiver URL. Until then, no events can reach this receiver.
- Authentic signature header/encoding and the exact event payload must be checked against a genuine Marketplace delivery before claiming acceptance. Negative signature testing is not an integration test.
- The receiver's SQL upsert and the existing poller's `report_raw_ghl_calls` upsert need a source-precedence audit. Ensure a weaker/partial poll result cannot overwrite a verified webhook's owner, timestamp, status, or duration. Prefer retaining source-specific fields/provenance and an explicit winner rule.
- A webhook is forward-looking; it cannot establish historical counts by itself. Find and validate a supported GHL export/report source for backfill, or keep historical ranges visibly snapshot-only/unavailable.
- Reconcile statuses carefully. Native widget labels (answered, busy, no-answer, failed) must map to the same categories used in V1, and all counts must reconcile by date, outbound direction, user ID, and unique GHL call/message ID.
- Confirm whether event `dateAdded` is the same date basis used by the widgets in the account timezone. Preserve UTC source timestamp and derive report-local date explicitly; do not silently shift the one-week snapshot.
- The app has `conversations/message.readonly`, but scope presence does not prove that the event subscription is enabled or installed for the relevant location.
- No use of the private widget route, fabricated event payload, report mutation, or live call is permitted as a substitute for a documented supported integration.

## Ordered plan for the next session

1. **Reopen this handoff and refresh live facts.** Read the current V1 Facts API and call receiver details from n8n. Confirm `active`, `activeVersionId`, `versionId`, node count, and receiver executions; do not assume repository workflow exports are authoritative.
2. **Request supported access from GHL.** Ask whether the Call Reporting dataset behind `get-all-phone-calls-new` can be exposed through a documented API/scope, or request report CSV exports for both the selected and immediately preceding seven-day windows. The private UI route returned 401 with the GHL PIT, so do not integrate it directly.
3. **Reconcile the documented message export.** For the exact `2026-09-20..2026-09-26` native-widget week, compare each export message/call ID to a supported report export, including `dateAdded`, direction, `userId`, status/disposition, and timezone. Resolve why `completed` counts exceed native `answered` counts and why exported outbound totals are higher.
4. **Evaluate two-window API access.** If GHL grants supported access or a supported export format is available, run selected `7d` and immediately prior `7d` windows, confirm cursor/date semantics, status mapping, deduplication, and parity. Do not update V1 call values until this passes.
5. **Keep webhook work optional and forward-only.** Do not enable Marketplace subscription as a historical-data fix. If later enabled for a separate realtime ledger, require genuine signature-positive validation, idempotent persistence, and source precedence before using its facts.
6. **Maintain V1 display boundary.** Keep the exact-week snapshot as-is; show other ranges as incomplete/unavailable until a supported source has passed reconciliation. Do not substitute private browser routes or fabricated event payloads.
7. **Close out with documentation.** Record versions, exact execution IDs and node-level evidence, reconciliation totals, unresolved source gaps, final worktree, and next actions in this handoff and project status. Refresh `repomix-output.md` with `packlive` only after documentation is final.

## Safety boundaries

- Keep the original report isolated; V1 changes stay in `reports/embed/executive-v1/` and the V1 Facts API.
- No live outbound call or send for testing. No report-widget private endpoint integration. No edits to production call data to force reconciliation.
- Read production workflows before mutation; after any approved change, verify the saved/published version and execution evidence. Do not publish, activate, or mutate CRM/report records as part of an audit-only session.
- Never put credentials, private keys, signature values, PITs, cookies, or sensitive captures in repository files or response summaries.

## Addendum — Call Reporting private-route test and PIT denial — 2026-09-29

At the user's request, the authenticated GHL Call Reporting page was tested read-only. The browser's own `POST backend.leadconnectorhq.com/reporting/calls/get-all-phone-calls-new` request accepts date bounds, direction, `userId`, limit, and offset pagination. For Manila dates `2026-09-20..2026-09-26`, 28 pages returned 1,377 rows (1,356 outbound plus 21 inbound) without duplicate/missing IDs. Outbound by user and `callStatus` exactly matched the native report:

| SDR | Outbound | answered/completed | busy | no-answer | failed |
|---|---:|---:|---:|---:|---:|
| Marc | 1,006 | 802 | 105 | 59 | 40 |
| Jason | 350 | 285 | 19 | 35 | 11 |

The same request made with the current GHL PIT outside the browser returned HTTP 401 `The token is not authorized for this scope`. The route is private/undocumented, so parity is verified for authenticated browser report data but API suitability is not. No route integration, database write, report change, or outbound call was performed. Next: request documented API access or supported report exports for selected and prior windows; retain the official message export only as an unreconciled supported candidate.

### Browser widget endpoint confirmation

The browser also exposed the native widget request used by the report page: `POST backend.leadconnectorhq.com/reporting/dashboards/revex/calls?locationId=...`. Its request body contains `dateAdded` time-series bounds, `direction=outbound`, the SDR `userId`, the widget grouping/aggregation, and `timezone=Asia/Manila`. The status-widget response directly returned Jason `285 answered, 35 no-answer, 19 busy, 11 failed` with total `350`, and Marc `802 answered, 59 no-answer, 105 busy, 40 failed` with total `1,006`.

This confirms a second browser-level way to read the native values without scraping rounded card text. It is still a private authenticated browser route: the PIT is unauthorized, browser bearer material is short-lived and must not be stored, and the route must not be promoted to a supported unattended integration without GHL approval. The widget's weekly chart can label the selected `Sep 20–26` date bounds as the Monday-start bucket `Sep 21–27`; therefore the status-widget totals, not the weekly-series bucket split, are the authoritative values for this snapshot.
