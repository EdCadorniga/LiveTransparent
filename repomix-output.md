This file is a merged representation of a subset of the codebase, containing specifically included files and files not matching ignore patterns, combined into a single document by Repomix.
The content has been processed where comments have been removed, empty lines have been removed, content has been compressed (code blocks are separated by ⋮---- delimiter).

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: AGENTS.md, Project Status and Next Steps.md, executive_report_v1_plan.md, Project Specifications.md, plan.md, docs/sessions/2026-09-29-executive-report-v1-ghl-call-source-closeout.md, reports/embed/executive-v1/**/*, reports/nginx.conf, postgres/reporting-bootstrap.sql, scripts/n8n/**/*.py, scripts/social-reporting/**/*.py
- Files matching these patterns are excluded: repomix-output.md, node_modules/**/*, *.csv, *.docx, *.png
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Code comments have been removed from supported file types
- Empty lines have been removed from all files
- Content has been compressed - code blocks are separated by ⋮---- delimiter
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
AGENTS.md
docs/sessions/2026-09-29-executive-report-v1-ghl-call-source-closeout.md
executive_report_v1_plan.md
plan.md
postgres/reporting-bootstrap.sql
Project Specifications.md
Project Status and Next Steps.md
reports/embed/executive-v1/DATA-COLLECTION-PLAN.md
reports/embed/executive-v1/DATA-REQUIREMENTS.md
reports/embed/executive-v1/EXECUTIVE-REPORT-V1-FEEDBACK-CONTRACT.md
reports/embed/executive-v1/index.baseline.html
reports/embed/executive-v1/index.html
reports/embed/executive-v1/lt-exec-v1-authoritative-ghl-counts.sql
reports/embed/executive-v1/lt-exec-v1-data-materializer.sql
reports/embed/executive-v1/lt-exec-v1-feedback-contract.sql
reports/embed/executive-v1/lt-exec-v1-response-sla.sql
reports/embed/executive-v1/MOCKUP-COMPARISON.md
reports/embed/executive-v1/mockup-v3.png
reports/embed/executive-v1/nginx-v1-location.conf
reports/embed/executive-v1/PRIORITY-ROUTING-RUNBOOK.md
reports/embed/executive-v1/priority-routing.test.js
reports/embed/executive-v1/README.md
reports/embed/executive-v1/REPORTING-GAPS.reference.md
reports/embed/executive-v1/REPORTS-README.reference.md
reports/embed/executive-v1/RESPONSE-SLA-CONTRACT.md
reports/nginx.conf
scripts/n8n/align_n8n_encryption_key.py
scripts/n8n/check_n8n_db.py
scripts/n8n/check_n8n.py
scripts/n8n/copy_to_n8n_files.py
scripts/n8n/copy_to_n8n.py
scripts/n8n/fix_sheets_node.py
scripts/n8n/fix_workflow.py
scripts/n8n/inventory_n8n_pits.py
scripts/n8n/n8n_api_probe.py
scripts/n8n/n8n_exec_check.py
scripts/n8n/n8n_find_pgerr.py
scripts/n8n/n8n_ga4_err.py
scripts/n8n/n8n_vapi_check.py
scripts/n8n/refresh_ghl_oauth_token.py
scripts/n8n/repair_failed_ghl_pits.py
scripts/social-reporting/audit_social_reporting.py
scripts/social-reporting/fix_brands_code.py
scripts/social-reporting/fix_executive_report_metrics.py
scripts/social-reporting/fix_social_mql_reporting.py
scripts/social-reporting/fix_social_reporting_accuracy.py
scripts/social-reporting/implement_email_attribution.py
scripts/social-reporting/repair_source_health.py
scripts/social-reporting/report_runtime_audit.py
```

# Files

## File: docs/sessions/2026-09-29-executive-report-v1-ghl-call-source-closeout.md
````markdown
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
````

## File: executive_report_v1_plan.md
````markdown
# Executive Report V1 Plan and Session Handoff

Last updated: 2026-09-29 (EOS closeout; GHL outbound call snapshot and signed-event receiver)

This document preserves the working context for the isolated Executive Report V1. Read it before auditing, modifying, or deploying V1.

## 2026-09-26 Campaign Classifier Repair

- `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) was active but its recent scheduled executions were failing at `Upsert Qualified Domain` because `Filter Taggable Rows` dropped paired-item metadata. The published repair is `07e53f3b-c427-4aea-b286-e1071e2b7839`, and `versionId == activeVersionId`.
- The Warm MQL branch now sends contacts with neither `qualified` nor `not qualified` through the DeepSeek classifier instead of marking them qualified by bypass. MQL-derived rows no longer update `vapi_qualified_domains`.
- Sales Outreach promotion now re-checks existing open and closed Sales Outreach opportunities before moving the Warm opportunity to Sales Outreach -> Qualified. Existing later-stage opportunities are preserved; closed-only records are not reopened.
- The first post-repair scheduled execution is verified: execution `1052265` succeeded at `2026-09-25T22:00:20Z` under the published version. It fetched 500 contacts, produced 10 DeepSeek classifications (7 accept, 3 reject), reconciled 10 tag actions plus 3 cleanups, reported 11 writes with 0 failed writes, and completed the qualified-domain upsert. One Warm MQL was skipped as `not qualified`.
- The operator verification was read-only; the scheduled workflow performed its normal production tag/write actions. No manual execution or CRM mutation smoke test was run. The workflow still runs every 15 minutes but does not classify the entire Warm -> New backlog; that remains governed by a separate explicit AI-qualification contract.

## 2026-09-26 Priority Routing Update

- The shared router `URpjcm2k5isHUyls` remains active/published at `3a3a6ab2-79a3-4fcc-822f-52677b6ae38c`, targeting Sales Outreach -> Priority.
- LinkedIn, Instagram, SMS, inbound calls/voicemail, DAN/Emerald email replies, and partnership email replies are now attached after persistence/contact resolution and message-level qualification.
- Published source versions: call `f9388b9a-ab70-45b2-bc77-4f5c2efef829`; campaign email `6e60f832-f175-41a8-a4b7-193f286bef18`; partnership email `42da3b2e-4b6a-4f2f-9341-880b36292eb4`.
- Routing remains non-blocking after persistence. No live CRM mutation smoke test or outbound send has been performed.
- The next hardening item is a durable claimed-event retry/reconciler for router failures that are not replayed.
- Reports proxy caching now covers all three V1 page APIs for 30 minutes with cache locking and cache keys based on range/from/to. Immediate repeated 7-day API requests returned in about 0.5-0.6 seconds with `X-Report-Cache: HIT`; the first Executive Summary cold request remains the expensive path at roughly one minute.

## Objective

Build a six-band executive report based on the supplied mockup:

1. Headline row
2. Story behind the headlines
3. Outbound performance by channel
4. SDR performance: inputs and outputs
5. Social media
6. Action queue

## Required inbound Priority automation

This remains a required implementation item for V1 and must not be lost while the reporting API and frontend are extended. The automation must route four qualifying inbound-intent paths into the `Priority` stage of the `Sales Outreach` pipeline:

- identifiable inbound calls;
- inbound calls with a disposition proving that a voicemail was left;
- inbound LinkedIn DMs or replies received through the existing Unipile inbound workflow;
- qualifying human inbound email replies.

The verified live destination is `Sales Outreach` pipeline `dhdlf3O4tymxFtHk4aqq`, Priority stage `be636da7-3c15-48ab-b589-c75bcd6f9955`, position 1. The workflow must resolve the contact first, then use an atomic idempotency key `(contact_id, source_event_id)` before performing CRM mutations. It must find the existing open Sales Outreach opportunity and move it to Priority while preserving owner and attribution, or create exactly one Priority opportunity when none exists. Closed opportunities must never be reopened or moved.

Each route must record the inbound channel (`call`, `voicemail`, `linkedin`, or `email`), source event ID, event timestamp, routing reason, prior/resulting opportunity and stage IDs, owner, and disposition in the durable Priority audit ledger. Bounces, unsubscribe notices, automated/provider email events, unidentified callers, and unresolved contacts are excluded or fail closed. Priority must be excluded from cold-outbound sequence eligibility; this automation is a hot human-follow-up queue and does not authorize an automatic send.

Required workflow coverage before sign-off:

1. LinkedIn: extend `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`) after contact resolution.
2. Calls and voicemail: use the canonical inbound call/contact resolution path; route both a connected inbound call and a call disposition proving voicemail left, with separate audit channels.
3. Email: attach only after the qualifying human-reply boundary is verified; exclude bounces, unsubscribe notices, and automated provider events.
4. Verify duplicate retries, existing open opportunities, missing opportunities, already-Priority opportunities, closed opportunities, unknown contacts, conflicting owner data, and two distinct events for one contact using exact IDs. Do not use a live outbound send as a test.

The mockup values are examples only. Every displayed number must come from a verified source, or be shown as unavailable/not captured. The report must explain what is happening and why, not merely display aggregate totals.

## Non-negotiable operating rules

- Never overwrite, delete, or alter the current Executive Report. Its source is `reports/embed/executive/index.html` and its live path is `/embed/executive/`.
- V1 source and deployment files live under `reports/embed/executive-v1/`.
- V1 uses the same hostname with a separate URL path: `https://reports.livetransparent.com/embed/executive-v1/`.
- Treat HTTP 200 with an empty body as failure, never as valid zero data.
- Never substitute zero for missing, stale, failed, or unavailable source data.
- Use explicit `Unknown`, `Unattributed`, `Unassigned`, and `Unavailable` buckets.
- Apply one selected reporting window and `America/Los_Angeles` date logic consistently.
- Preserve raw IDs and raw appointment/event rows for auditability.
- For every headline number, record the source table, distinctness rule, date rule, freshness, and reconciliation query.
- Do not claim that a number is “direct from GHL” if it was calculated from a rollup, derived ledger, or incomplete snapshot.
- Production workflow changes, CRM writes, outbound sends, and destructive actions require explicit scope and verification.

## Deployed state

V1 is deployed as a separate static path on the existing report host:

- V1 page: `https://reports.livetransparent.com/embed/executive-v1/`
- V1 facts proxy: `https://reports.livetransparent.com/api/report/executive-v1/facts`
- Current report remains: `https://reports.livetransparent.com/embed/executive/`
- Report container: `reports-livetransparent`
- Deployment image tag used: `v3ud1lum1svamymuor21upog:social-mql-20260817`
- Existing report build still serves `2026-08-17-v27-social-mql`.
- Deployment backup created on the server: `docker-compose.yaml.pre-campaign-accuracy`.

Deployment files:

- `reports/Dockerfile`
- `reports/nginx.conf` — includes the V1 facts proxy location.
- `scripts/deploy/deploy_report_vps_local.py` — deployment helper; its repository-root path was corrected from `scripts/reports` to `reports` during deployment.

No Coolify deployment was made for n8n workflows beyond the already-published n8n API changes described below. The report container deployment does not change GHL records or send messages.

## Live V1 n8n workflows

All three are active and published:

| Workflow | ID | Current published version | Purpose |
|---|---|---|---|
| LT - Executive Report V1 Data Materializer | `knc2wxe4pyYIJ5tw` | `47c5aaf8-047c-4cfe-996f-bdcbb97bb04d` | Refreshes V1 contact, appointment, and call facts every 30 minutes; appointment contact join supports direct, `contact:<id>`, and raw-dimension IDs |
| LT - Executive Report V1 Facts API | `oxYDg6XnRBKhl1Xd` | `677e728d-8f33-4e78-a406-3a0dca56b19e` | Read-only selected-window facts endpoint; meetings restricted to the canonical Regulated Ads calendar; `range=7d|30d|90d` maps to LA date windows |
| LT - Executive Report V1 Response SLA Materializer | `KlBw3ThLbNlMfE2J` | `5d395545-918d-44a5-8a61-e2be77f3d38e` | Refreshes inbound-to-response facts every 15 minutes |

Webhook paths:

- `POST /webhook/lt-executive-report-v1-materializer`
- `GET /webhook/lt-report-executive-v1-facts?from=YYYY-MM-DD&to=YYYY-MM-DD`
- `POST /webhook/lt-executive-report-v1-response-sla-materializer`

The V1 Facts API accepts the frontend’s `range=7d|30d|90d` defaults and explicit `from`/`to` dates. The report host proxies the facts endpoint under `/api/report/executive-v1/facts`.

## Source-of-truth design

### Authoritative raw GHL headline counts

The V1 Facts API now returns `authoritativeGhlCounts`, calculated from raw GHL snapshot tables rather than `report_daily_summary` or the daily rollup table:

- `new_contacts`: distinct non-empty `report_raw_ghl_contacts.source_key`, using the contact `createdAt` or snapshot date in the selected LA date window.
- `opportunities_created`: distinct non-empty `report_raw_ghl_opportunities.source_key`, using the raw source-created/created/date-added timestamp or snapshot date.
- `mqls_entered`: distinct opportunity IDs whose first observed raw GHL MQL-stage date is in the selected window.
- `sqls_entered`: distinct opportunity IDs whose first observed Sales Outreach date is in the selected window.
- Basis returned by the API: `raw GHL snapshot facts; distinct contact/opportunity IDs; America/Los_Angeles dates`.

The SQL contract is versioned in `reports/embed/executive-v1/lt-exec-v1-authoritative-ghl-counts.sql`.

Important: these are raw GHL snapshot facts, not a live GHL API request on every page load. The raw GHL ingest must be fresh and successful. If the ingest is stale or failed, the report must show unavailable/health failure rather than trust the last value silently.

### V1 materialized facts

`lt-exec-v1-data-materializer.sql` and the live materializer populate:

- `lt_exec_v1_contact_provenance` from `report_raw_ghl_contacts`.
- `lt_exec_v1_appointment_facts` from `report_raw_ghl_appointments` plus the latest contact snapshot.
- `lt_exec_v1_call_facts` from `report_raw_ghl_calls` and Vapi `voice_call_attempt` joined to `voice_call_queue`.
- V1 source-health rows in `report_source_health`.

The materializer health-count bug was corrected: `exec_v1_contact_provenance.last_row_count` now reports the full fact count, not the number of acquisition-mechanism groups.

### Existing APIs still used by V1

The V1 frontend currently loads three endpoints in parallel:

- `/api/report/executive/summary`
- `/api/report/executive/campaign-channels`
- `/api/report/executive-v1/facts`

Therefore, not every V1 field is yet rollup-independent:

- Headline contacts, opportunities, MQLs, and SQLs prefer `authoritativeGhlCounts`.
- Cameron meetings, appointment detail, call totals, voicemail, response SLA, and contact mechanisms use V1 facts.
- Email, LinkedIn, and SMS campaign tables still use the Campaign Channel Summary and channel ledgers.
- Some story cards, pipeline/action-queue fields, attribution coverage, and social metrics still use the existing Executive Summary/ledger/statistics sources.
- Action queue contract/proposal and follow-up details remain unavailable rather than fabricated.

This boundary must be kept visible until each remaining field has a raw-source reconciliation contract.

## Business definitions locked for V1

### Cameron meetings

For the selected window, count distinct non-empty contact IDs on Cameron-assigned appointment rows. Cameron is identified by the configured GHL user ID `03p5GatJBH7i9zjMaIzm` or the SDR registry name containing Cameron. A contact who cancels and reschedules counts once. Raw appointment rows remain available for detail and audit.

The response includes:

```json
{
  "basis": "distinct contact_id; canceled and rescheduled appointment rows count once",
  "unique_contacts": 0,
  "appointment_rows": 0
}
```

### Voicemail and callbacks

- Select the latest non-empty Vapi custom disposition per unique contact in the selected window.
- Treat selecting the voicemail disposition as proof that a voicemail was left.
- `voicemail_drops_unique` and `voicemail_delivered_unique` therefore use the same latest-disposition unique-contact count.
- `callbacks_unique` uses the explicit callback-request disposition set.
- Do not count a contact twice.
- If there are no Vapi disposition facts in the selected window, show unavailable/no data, not zero.

### Speed-to-lead and follow-up

Measure the first later same-channel outbound event after:

- inbound LinkedIn DM/reply → later LinkedIn DM;
- inbound call → later outbound GHL/Vapi call;
- marketing-email reply → later qualifying marketing-email send.

Match by contact and strictly later timestamp. Multiple same-timestamp outbound candidates are `ambiguous`. Publish average/median only from unambiguous matched responses, while showing responded, unmatched, and ambiguous denominators. No overdue threshold is assumed because no business target has been approved.

## Verified progress on 2026-09-24

### Deployment and HTTP checks

- V1 page: HTTP 200, non-empty, title `Executive Report V1`.
- V1 facts proxy: HTTP 200, non-empty JSON.
- Current report: HTTP 200 and original build stamp still present.
- V1 desktop and approximately 390px mobile browser screenshots captured.
- Browser automation confirmed the page eventually renders real values after the existing Executive Summary API completes.
- Network checks showed all three report API requests returned HTTP 200.
- The only observed browser 404 was the benign `/favicon.ico` request.

### Latest controlled V1 materializer/facts state

- Contact facts: 2,968.
- Appointment facts: 38.
- Call facts: 5,638 total: 3,818 GHL and 1,820 Vapi.
- Response-SLA facts: 236 total; 107 responded and 129 unmatched in the materialized history.
- V1 source health rows were ready after the controlled materializer run.

### 30-day smoke values from raw GHL counts

For `2026-08-25` through `2026-09-23`, the deployed facts API returned:

- MQLs entered: 7.
- SQLs entered: 1,274.
- New contacts: 1,078.
- Opportunities created: 3,235.

These values are deployment smoke results, not final business sign-off. The next session must reconcile each one directly against GHL and verify that the chosen definitions match leadership expectations.

### Known runtime history

- An earlier V1 Facts API execution (`988041`) returned an error while adding voicemail completeness; the SQL typo was fixed and subsequent endpoint calls returned populated HTTP 200 responses.
- At one point materializer and response-SLA executions appeared as `new`; subsequent checks showed those executions succeeded and no current `new`, `running`, or `waiting` executions remained at the end of the deployment verification.
- The existing Executive Summary API can take roughly 30 seconds for a 30-day request. This is slow but returned HTTP 200 with populated JSON during verification. Do not weaken fail-closed behavior to hide latency.

## Next-session audit plan

### P0 — reconcile raw counts against GHL

For 7d, 30d, 90d, and one custom window:

1. Capture the V1 API payload and source-health rows.
2. Query the corresponding live GHL contact, opportunity, stage, and appointment totals using the approved GHL PIT/API path or authenticated GHL UI.
3. Reconcile by exact IDs, not only aggregate UI totals.
4. Check timezone boundaries and first-observed date rules.
5. Confirm whether leadership wants SQLs to mean first Sales Outreach entry, SQL-tag contacts, or another explicit definition. Do not silently mix definitions.
6. Investigate the large 30-day SQL/opportunity values before calling them correct.
7. Record discrepancies, their cause, and the accepted rule in this document.

### P0 — verify raw-ingest freshness

- Identify the live GHL Leads, Sales, Appointments, and Calls ingest workflow IDs and current schedules.
- Confirm each latest successful execution, row count, watermark, and error state.
- Confirm raw source-health rows are included in the V1 response or add that visibility before sign-off.
- Simulate/read-only check the stale-ingest behavior: stale source must be flagged, never rendered as a trustworthy zero.

### P1 — remove remaining rollup dependence

Create raw-source contracts for:

- MQL/SQL source breakdowns.
- Opportunity source/campaign rows.
- Email, LinkedIn, SMS delivery metrics.
- Pipeline-to-work/action queue.
- Social account statistics.

For each, preserve channel ledgers where they are the authoritative provider event source, but expose freshness, coverage, distinctness, and reconciliation evidence.

### P1 — final report QA

- Verify headline totals reconcile to detail tables.
- Verify Cameron appointment rows reconcile to the distinct-contact headline.
- Verify calls reconcile: attempted = connected + no answer + busy/failed + wrong number + unknown.
- Verify voicemail latest-disposition deduplication.
- Verify response SLA denominators.
- Verify 7d/30d/90d/custom windows.
- Capture desktop and 390px screenshots.
- Check console/network errors; ignore only the known benign favicon 404.
- Confirm current report URL and content remain unchanged.

## Files to inspect first next session

- `executive_report_v1_plan.md` — this handoff.
- `AGENTS.md` — operating rules and precedence.
- `reports/embed/executive-v1/index.html` — V1 frontend.
- `reports/embed/executive-v1/DATA-REQUIREMENTS.md` — metric definitions.
- `reports/embed/executive-v1/DATA-COLLECTION-PLAN.md` — collection contract.
- `reports/embed/executive-v1/lt-exec-v1-authoritative-ghl-counts.sql` — raw GHL headline-count contract.
- `reports/embed/executive-v1/lt-exec-v1-data-materializer.sql` — V1 fact materialization contract.
- `reports/embed/executive-v1/lt-exec-v1-response-sla.sql` — same-channel response contract.
- `reports/nginx.conf` — deployed V1 proxy route.
- `scripts/deploy/deploy_report_vps_local.py` — deployment helper.

## Final safety reminder

Do not deploy a new version, change the current report, alter production workflow definitions, or label the current smoke values “accurate” until the next session completes the direct GHL ID-level reconciliation and source-freshness audit.

## EOS verification — 2026-09-24

Read-only closeout checks completed:

- `LT - Executive Report V1 Data Materializer` is active; `versionId` and `activeVersionId` both equal `935f1d4a-b97b-418c-bb3e-80c9a812eed4`.
- `LT - Executive Report V1 Facts API` is active; `versionId` and `activeVersionId` both equal `9e7182a2-cf99-4236-a453-6b5ed175ab37`.
- `LT - Executive Report V1 Response SLA Materializer` is active; `versionId` and `activeVersionId` both equal `5d395545-918d-44a5-8a61-e2be77f3d38e`.
- Recent executions for all three workflows were `success`; no current `new`, `running`, or `waiting` execution was observed in the checked recent windows.
- `https://reports.livetransparent.com/embed/executive-v1/` returned HTTP 200 with 24,359 bytes.
- `https://reports.livetransparent.com/api/report/executive-v1/facts?from=2026-08-25&to=2026-09-23` returned HTTP 200 with 7,275 bytes.
- `https://reports.livetransparent.com/embed/executive/` returned HTTP 200 with 147,821 bytes.
- The current report source remains unchanged relative to `reports/embed/executive-v1/index.baseline.html`.
- Relevant V1 documentation was rechecked; the stale “Proposed review URL” heading in `reports/embed/executive-v1/README.md` was corrected to “Deployed review URL”.

Next session must begin with the P0 direct GHL ID-level reconciliation and raw-ingest freshness audit. The smoke values remain provisional until that work is complete.

## EOS closeout — 2026-09-26

### Google OAuth replacement and live verification

- Created `Google Analytics account - Ed OAuth` (`rhKm0YiMSBu0Lval`) and `GSC - Ed OAuth` (`awVQ5MnyCYFFCT0v`) using the operator's Google OAuth client values. The GSC credential includes the read-only scope `https://www.googleapis.com/auth/webmasters.readonly`.
- Restored the previous Cameron values in `GSC - Cameron Livetransparent Google account` (`EKnNrSvlEd0A99AX`) from the local `Cameron_CloudConsole_ClientID`/`Cameron_CloudConsole_ClientSecret` environment entries. Do not expose those values.
- Updated the active `LT - GA4 Daily Ingest` (`6pCSGzFmrMDFL5Yq`) `Fetch GA4 Data` node to `rhKm0YiMSBu0Lval`; active/published version `34a63b5f-db3b-43d1-ba12-4961cc15e2c3`.
- Updated the active `LT - GSC Daily Ingest` (`xHqmCC1vOeZ11gCd`) `Fetch GSC Data` node to `awVQ5MnyCYFFCT0v`; active/published version `ed3c59c1-05fc-4c2a-ab88-eef523c13651`.
- The archived inactive `GA4 Credential Test` still contains the old GA4 credential reference because n8n refuses updates to archived workflows. It is not a production path.
- After interactive OAuth connection, GA4 execution `1048537` succeeded with 925 rows and GSC execution `1048538` succeeded with 5 rows. The public Executive Summary returned HTTP 200 with 30,761 bytes; health showed `ga4=success` (925 rows, `2026-09-26T00:43:16+08:00`) and `gsc=success` (5 rows, `2026-09-26T00:43:28+08:00`). The V1 page returned HTTP 200 with 25,060 bytes.

### Remaining health warnings

- `bridge: stale` is the general attribution bridge, not the GA4 or GSC bridge. The public health row reports its last success as `2026-09-12T08:02:54+08:00`, with a 48-hour freshness threshold. `LT - Report Attribution Bridge` (`Y0TU7Il71JswxOBp`) is active at `08d15fa4-e513-4ada-939e-51c3584440a7`, but its latest checked execution `1045692` failed; earlier queued repair executions `989774` and `989781` also ended `error`. No successful bridge repair is accepted yet.
- Read-only inspection of execution `1045692` identified the precise SQL defect: the four `UNION ALL` branches in `Build Bridge SQL` do not alias their first projected expressions, while the enclosing query references `c.identity_type`/`c.identity_value`. PostgreSQL therefore reports `column "identity_type" does not exist` in `Write Bridge Rows`. The minimal repair is to add explicit aliases to the derived-table columns and then run a controlled verification; do not publish or execute this repair without production-change approval.
- `ghl_opp_owner_coverage: attention` is a fresh QA result, not a stale-ingest condition. Its health row was updated at `2026-09-26T00:00:50+08:00` with 11,569 measured rows, but the public payload does not expose the direct-owner/contact-fallback numerator and denominator. The next session must inspect the Report QA execution/node output or the underlying health metadata and reconcile remaining unassigned opportunities by exact opportunity/contact ID.
- The GA4 Traffic Rollup Bridge, GSC Rollup Bridge, and Report Daily Rollups last checked executions were successful, but no manual downstream run was accepted after the new ingest executions; the next session should verify that the post-ingest bridge/rollup cycle completes and that the selected-window metrics update.

### Meeting window and inbound Priority confirmation

- V1 Facts filters meeting detail by appointment `start_at` in `America/Los_Angeles`; these are scheduled meeting times, not booking/creation times.
- The frontend sent `range=7d`, but the API previously defaulted to 30 days when explicit `from`/`to` values were absent. The active API now maps `range=7d|30d|90d` to the corresponding LA date window. Published version: `677e728d-8f33-4e78-a406-3a0dca56b19e`.
- Public verification returned `from=2026-09-18`, `to=2026-09-24`, and 3 appointment rows for `range=7d`.
- A shared inbound-to-`Priority` router is published: `LT - Inbound Intent Priority Router` (`URpjcm2k5isHUyls`), active version `3a3a6ab2-79a3-4fcc-822f-52677b6ae38c`. LinkedIn, Instagram, SMS, inbound calls/voicemail, DAN/Emerald email replies, and partnership email replies are attached after their persistence/contact-resolution and message-qualification boundaries. It has not run against live Postgres/GHL for a CRM mutation smoke test.

### Next session — exact order

1. [ complete ] Verify the first post-repair scheduled execution of `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`); execution `1052265` succeeded with the expected classifier, write, cleanup, domain-upsert, and Warm MQL outcomes.
2. Define and audit the separate Warm -> New qualification path; do not broaden the campaign/Vapi classifier without confirming the explicit AI qualification contract.
3. Reconcile the report's 22 current MQLs against the 15 currently returned by the live GHL Warm -> Qualified (MQL) search, including snapshot lag, moved records, bounces, and `not qualified` conflicts.
4. Obtain explicit production-change approval for the minimal Attribution Bridge SQL alias repair identified from execution `1045692`; then publish, verify a successful execution, and confirm `bridge: ready` in the public payload.
5. Inspect Report QA execution `1048389` or the corresponding `report_source_health.metadata` for the exact owner-coverage split, then reconcile unassigned opportunities by exact ID. Do not lower the 50% threshold or write owners without an approved definition.
6. Verify the next GA4/GSC bridge and Report Daily Rollups executions after ingest executions `1048537`/`1048538`; re-fetch V1 with a cache-busting query.
7. Build the durable retry/reconciler for inbound Priority events whose claimed router executions fail or expire.
8. Keep the active V1 and current report URLs unchanged. Preserve all outbound-send and CRM-mutation smoke-test approval gates.

## P0 audit continuation — 2026-09-24

Read-only reconciliation and freshness checks were completed after the EOS handoff. No report deployment, workflow edit, CRM write, or live send was performed.

### Direct GHL reconciliation

The approved read-only GHL PIT/API path returned 36,604 contacts and 11,197 opportunities for location `Zwz4relUXVPxx8uohnjV` on 2026-09-24. Using `America/Los_Angeles` date boundaries through 2026-09-23:

| Window | Live contacts created | V1 raw contacts | Live opportunities created | V1 raw opportunities | V1 first-observed MQL entry | V1 first-observed SQL entry |
|---|---:|---:|---:|---:|---:|---:|
| 7d | 27 | pending exact raw-ID reconciliation | 88 | pending exact raw-ID reconciliation | pending | pending |
| 30d | 4,803 | 1,078 | 3,199 | 3,235 | 7 | 1,274 |
| 90d | 12,891 | pending exact raw-ID reconciliation | 8,330 | pending exact raw-ID reconciliation | pending | pending |
| custom 2026-09-01..2026-09-15 | 588 | pending exact raw-ID reconciliation | 1,355 | pending exact raw-ID reconciliation | pending | pending |

The live comparison is not yet apples-to-apples for MQL/SQL: the API can show current pipeline/stage and creation dates, while V1 intentionally counts the first observed raw snapshot entry into the configured stage. A current-stage-created-date comparison returned 0 MQL and 604 Sales Outreach opportunities for the 30-day window, so leadership must explicitly confirm that first-observed stage entry is the desired SQL/MQL definition. The 30-day headline values remain provisional.

### Verified contact-ingest gap

The active published workflow `LT - GHL Daily Leads Ingest` (`osIJOgBmWITF5Yuv`, version `c1f85a61-67f5-44ff-b6fd-176f18e91cb9`) is succeeding on its hourly schedule, but its live Config is `pageSize=50` and `maxPages=10`. That imposes a 500-contact page ceiling per run, despite the live GHL contact total of 36,604. This explains the incomplete contact snapshot: `lt_exec_v1_contact_provenance` contains 2,968 contacts, and the 30-day raw headline count is 1,078.

Other checked workflows were active/published and recently successful: GHL Sales Ingest (`aYT5oHcgmBALzHy5`), Appointments Ingest (`yWZVSqEcjTbMT3kG`), Calls Ingest (`SqNQ0BYaTdcqyt1l`), and all three V1 workflows. The Calls Ingest history included one older error among otherwise successful recent executions; this does not validate the contact headline.

### Audit disposition

- Do not label the current V1 headline values accurate or leadership-ready.
- Do not silently convert the first-observed MQL/SQL contract to current-stage counts.
- Repairing the Leads ingest pagination cap and performing a complete non-destructive backfill are the next implementation steps, but require explicit production-change approval and a post-repair ID-level reconciliation.
- Preserve the current report and V1 deployment unchanged until that repair/backfill and the MQL/SQL definition decision are complete.

## Fixes applied — 2026-09-24

The follow-up SMS/voicemail review found and repaired the following V1 issues:

- V1 frontend SMS wiring now reads `smsSummary` from the Campaign Channel Summary response. Previously it incorrectly read that field from the Executive Summary response, leaving the SMS card/table blank.
- The published Campaign Channel Summary workflow (`MvPLbUAN9IIQikxb`, version `24492be1-3b62-436a-8dbe-7f46c64c314e`) now counts SMS sends from `report_sms_sent`, delivery confirmations from SimpleTexting `delivery_event` rows, replies from inbound-reply events, and failures from delivery-failed events. A cache-busted 30-day response now reports 909 sent, 529 delivered, 14 replies, and 0 failed.
- The published GHL Leads Ingest workflow (`osIJOgBmWITF5Yuv`, version `60e78c0e-10bf-49f8-85d1-77f874373626`) now uses `pageSize=100` and `maxPages=1000`, removing the verified 500-contact cap. Its next scheduled run must be checked for complete row count and source-health recovery; no manual run was forced during this session.
- Voicemail rendering was not the defect. The Vapi attempt table contains 1,820 disposition-bearing attempts through 2026-08-11 and no attempts in the 2026-08-25..2026-09-23 30-day window. The V1 Facts API therefore correctly shows unavailable/no disposition facts for 30d, while the 90d response correctly returns 57 unique voicemail dispositions. Do not replace the current 30d unavailable state with zero or inferred voicemail activity.

Deployment verification: V1 and the current report both returned HTTP 200 after the static deployment; the current report build stamp remained `2026-08-17-v27-social-mql`. The original report source was not modified.

## Booking and source-attribution follow-up — 2026-09-24

- The booking rule is already unique-contact based for the selected period. For 2026-08-25..2026-09-23, the Cameron calendar `SrtXcFVyea7pFl3nTiIK` returns 9 appointment rows but 8 unique contact IDs; the cancel/reschedule pair for one contact is counted once. All listed rows are assigned to Cameron Karkut.
- The “Unknown” meeting names are a data-freshness issue, not unknown bookings. Appointment rows contain `contactId`, but the capped contact snapshot did not contain the matching contact names. Direct GHL lookup resolved the IDs; the repaired Leads ingest and the existing V1 materializer should populate names on the next successful cycle. V1 now falls back to displaying `Contact <id>` rather than an anonymous `Unknown` when a name is still unavailable.
- “Opportunities by Source” was incorrectly reusing the contact-cohort source breakdown. The live Executive Summary workflow now exposes `opportunitySourceBreakdown`, based on distinct opportunities created inside the selected period, and V1 reads that field. For 2026-09-17..2026-09-23 the result is 83 Unknown/Unattributed, 2 CRM UI/csv_import, 2 LinkedIn via Unipile, and 1 August 2026 Partnership Contacts (88 total), so the prior all-zero display was not valid.
- The 3/5 SQL source coverage is still an honest raw-attribution boundary. Of the 2 currently unattributed SQL contacts, live GHL currently reports `LinkedIn via Unipile` for both, but the older raw contact snapshot lacks that source because of the 500-contact ingest cap. Keep them unattributed until the repaired ingest captures the source in the report ledger, then reconcile the result by exact contact ID rather than inferring historical attribution.

Deployment verification for this follow-up: Executive Summary active version `d21d7a58-4283-4a78-b1c0-86fe14b7f71b` is published; V1 was redeployed with the contact-ID fallback; the current report source and build remain unchanged.

## Appointment contact-name join fix — 2026-09-24

- Root cause confirmed: V1 materialization joined `report_raw_ghl_contacts.source_key` directly to the appointment `contact_id`, but contact source keys are commonly stored as `contact:<id>`. The join therefore returned null names even after the contact ingest cap was repaired.
- Published `LT - Executive Report V1 Data Materializer` (`knc2wxe4pyYIJ5tw`, version `47c5aaf8-047c-4cfe-996f-bdcbb97bb04d`) now matches direct IDs, `contact:<id>` keys, and the raw contact `dimensions_json.contact_id` fallback.
- A controlled materializer webhook run completed successfully as execution `988447`. The six requested contacts now resolve to Ed Test, Jen Rappaport, Cameron Karkut, Christine Stocco, Cameron Gallacher, and Benjamin Moosher. The duplicate Benjamin rows remain detail rows but are counted once in the unique-contact booking summary.

## Meeting scope and unknown-source attribution follow-up — 2026-09-25

- The V1 Facts API now filters both meeting detail rows and the unique-contact summary to calendar `SrtXcFVyea7pFl3nTiIK` only. The V1 panel title is now `Meetings - Regulated Ads On Social/Search`; the repeated Cameron/calendar identifier line was removed from each row.
- Source attribution now checks the LinkedIn ledgers before returning Unknown: `linkedin_activity_events`, `linkedin_connection_state`, and `partnership_linkedin_connection_state`. Contacts with request evidence are labeled `LinkedIn via Unipile — Connection Request`; contacts with DM/reply evidence are labeled `LinkedIn via Unipile — DM`.
- Source attribution also checks raw contact tag evidence. Contacts carrying Apollo tags are labeled `Apollo import (tag evidence)`; contacts carrying Emerald tags are labeled `Emerald campaign (tag evidence)`. Existing explicit source/UTM and traffic-bridge values remain higher priority.
- The raw latest-contact snapshot currently contains 71 Apollo-tagged contacts and 222 Emerald-tagged contacts overall. These are evidence-based classifications, not assumptions that every tagged contact originated from that campaign. The next successful Executive Summary execution must be checked to confirm how many of the 83 previously unattributed opportunity rows resolve under these fallbacks.

EOS verification: the latest attribution-triggered executions are `989640` (Executive Summary) and `989659` (V1 Facts API), both still `new`/queued with no start time. The last accepted successes were Executive Summary `988482` and V1 Facts `988484`, before the final attribution fallback was verified end-to-end. Treat exact post-fallback source counts as unverified until those queued executions complete successfully.

## Reporting health repairs applied — 2026-09-25

- `LT - Report Attribution Bridge` (`Y0TU7Il71JswxOBp`) was repaired and published; its current active version is `08d15fa4-e513-4ada-939e-51c3584440a7`. Its identity-map upsert now deterministically deduplicates `(identity_type, identity_value)` candidates before `ON CONFLICT`, fixing the recurring `ON CONFLICT DO UPDATE command cannot affect row a second time` failure. The original daily schedule was restored after a controlled trigger attempt.
- `LT - GHL Daily Leads Ingest` (`osIJOgBmWITF5Yuv`) was published as version `7057fd10-a7db-4888-98ad-4adb1af1c2cc` with normalized contact-owner fields preserved for the owner-attribution fallback.
- `LT - Report QA and Alerts` (`M5mXcDTFSko6EdHb`) was repaired and published as version `004f260e-7153-4ab7-9e30-dc066ea2458`. `ghl_opp_owner_coverage` now measures direct opportunity ownership plus contact-owner fallback and records both components in metadata.
- Runtime verification is pending the next successful bridge, leads-ingest, and QA executions. Controlled bridge executions `989774` and `989781` are queued because the n8n worker has not started them yet. Do not call the health indicators green until those executions complete and the live report payload confirms `bridge: ready` and owner coverage is resolved or accurately reflects any remaining unassigned records.

### Next session — first action

1. Recheck executions `989640` and `989659`; accept the attribution result only if both complete `success`.
2. Fetch the selected 7-day summary with a cache-busting query and record the exact Apollo, Emerald, LinkedIn-request, LinkedIn-DM, explicit-source, and residual-unknown counts.
3. If residual Unknown rows remain, reconcile them by exact opportunity/contact ID and document whether they lack a contact link, lack source/tag evidence, or are outside the raw ingest window. Do not relabel them without evidence.

## EOS closeout — 2026-09-26 — V1 feedback round one

### Reviewed

- `Executive Summary Edits .docx` was text-extracted and compared with the V1 implementation.
- `reports/embed/executive-v1/index.html` was syntax-checked and smoke-tested locally with browser automation.
- The live `Sales Outreach` pipeline was re-read. Priority is at position 1 with stage ID `be636da7-3c15-48ab-b589-c75bcd6f9955`.
- The live LinkedIn inbound workflow `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`) was read-only verified active with 19 nodes.

### Completed this session

- Added the V1 feedback contract for funnel, closed-by-source, weekly movement, vertical, retargeting, and Priority reporting.
- Added frontend sections for those metrics with unavailable-state behavior; live API fields are still required before deployment.
- Added the Priority audit-ledger SQL contract and pure routing acceptance fixtures; 5/5 cases passed.
- Documented the required four inbound Priority routes: inbound calls, voicemail-left dispositions, LinkedIn DMs/replies, and qualifying human email replies.
- Preserved the current Executive Report source and URL; no report deployment occurred.

### Not complete / not accepted

- The new facts API fields are not yet implemented or live.
- The inbound Priority automation is not yet created or published.
- No CRM mutation, live inbound smoke, outbound send, workflow publish, or report deployment was performed.
- The DOCX renderer could not run because the environment lacks `pdf2image`; text comparison succeeded, but visual DOCX review remains unaccepted.

### Round-two order of operations

1. Recheck the pending Executive Summary, Facts API, attribution bridge, leads-ingest, and Report QA executions; accept only successful, populated results.
2. Implement and review the facts API contract for funnel percentages, closed-by-source, combined meeting outcomes, weekly lead flow, vertical, retargeting, and Priority counts.
3. Build the shared idempotent Priority router and attach it after contact resolution for LinkedIn, calls/voicemail, and qualifying email replies. Preserve owner/attribution, protect closed opportunities, and exclude Priority from cold outbound.
4. Run mocked exact-ID tests, then obtain approval for any production CRM/workflow smoke test. Re-read workflow versions and pipeline stage after publication.
5. Reconcile the API against raw GHL IDs, stage transitions, appointments, channel ledgers, closed values, and inbound event ledgers for 7d, 30d, 90d, and custom windows.
6. Run populated desktop/mobile QA, deploy only after health and reconciliation gates pass, and verify that `/embed/executive/` remains unchanged.

Safety gates remain in force: do not publish or deploy while new metrics are contract-only, source health is stale/attention, or Priority routing lacks exact-ID end-to-end verification.

## Round-two audit — 2026-09-26

Read-only verification continued from the feedback handoff. No production workflow, CRM record, report deployment, or outbound send was changed.

- The accepted Executive Summary execution `989640` and V1 Facts execution `989659` both completed `success` on the live n8n host. The post-fallback source split is therefore eligible for a fresh payload check, but the public report fetch was not accepted as a new reconciliation result during this check because the report endpoint did not return within the local HTTP probe window.
- Attribution Bridge execution `1045692` failed in `Write Bridge Rows`. The exact PostgreSQL error is `column "identity_type" does not exist`; the node query references `identity_type` without qualifying the source/target scope. The earlier repair executions `989774` and `989781` also ended `error`. Do not call `bridge` healthy or publish a repair without explicit production-change approval and a successful execution.
- Report QA execution `1048389` succeeded but its captured health snapshot was still attention-state: `ghl_opp_owner_coverage` measured 11,569 opportunities with 4,371 direct owners plus 243 contact-owner fallbacks (4,614 / 11,569 = 39.9% assigned). The same snapshot reported `bridge: ready` as a stale health-row status even though the bridge execution had failed; the stale age and execution error remain the authoritative blocker.
- The local V1 frontend had an implementation defect from the first feedback pass: duplicate feedback renderer code existed after the main IIFE, and the active renderer passed the `<div id="closed-sources">` element to a table-only helper. The duplicate block is now disabled and the main renderer writes closed-source rows directly into the div. JavaScript syntax checks pass for both inline script blocks. This is isolated to `reports/embed/executive-v1/index.html`; no deployment occurred.

Next safe step: obtain approval for the narrowly scoped Attribution Bridge SQL qualification repair, then publish and verify one successful bridge execution plus a fresh populated summary/facts payload. Keep V1 deployment and Priority routing unchanged until bridge/owner health and the new facts API fields are reconciled.

## Attribution Bridge repair closeout — 2026-09-26

Production repair was approved and completed without changing the report deployment, CRM records, Priority routing, or outbound senders.

- Workflow `LT - Report Attribution Bridge` (`Y0TU7Il71JswxOBp`) was patched only in `Build Bridge SQL`. The identity-map `UNION ALL` derived table now has an explicit 11-column alias list, and the `SELECT DISTINCT ON` / `ORDER BY` references are qualified against that derived relation. The successive active versions during validation were `31226f6d-5a30-4ccd-b918-b1c95503b26a`, `d17db58f-e436-45fb-a6d6-6fe10ce3594a`, and final `6d56d5c0-cd84-4691-a881-0d215f3f0e31`; final `versionId == activeVersionId` and the workflow remains active. The prior active version `08d15fa4-e513-4ada-939e-51c3584440a7` remains the rollback reference.
- The final controlled execution `1049630` completed `success` after a 90-day rebuild. It reached `Result`; `Summarize Run` reported 3 executed queries for report date `2026-09-25`. Earlier validation executions `1049577`, `1049627`, and `1049629` failed on the intermediate alias fixes; they are retained as evidence of the correction path, not accepted successes. Temporary CLI execution `1049602` was stopped after the external runner handoff stalled before SQL; it performed no accepted bridge writes.
- Report QA execution `1049644` completed `success`. Its fresh health rows show `bridge=ready`, `last_success_at=2026-09-25T17:41:10.397Z`, `last_row_count=3`, `last_error=null`. Owner coverage remains accurately `attention`: 4,371 direct owners + 243 contact fallbacks = 4,614 / 11,569 opportunities (39.9%). Do not label owner attribution complete.
- A cache-busted public Executive Summary request returned HTTP 200 with 32,122 bytes and a populated JSON body. Its public bridge health row was `ready` with `last_success_at=2026-09-26T01:41:10+08:00`. This accepts the bridge health repair; it does not accept the headline reconciliation or owner attribution.

The remaining round-two order is unchanged: reconcile the new feedback facts against raw IDs, keep owner attribution in its attention bucket, repair and attach the call/voicemail and qualifying-email sources, and deploy V1 only after populated desktop/mobile QA and health gates pass.

## Inbound Priority router integration — 2026-09-26

The shared router was created for review, hardened, published, and attached to the persisted LinkedIn, Instagram, and SMS inbound paths. No live CRM mutation smoke test or outbound send was performed.

- Workflow: `LT - Inbound Intent Priority Router` (`URpjcm2k5isHUyls`)
- Active version: `3a3a6ab2-79a3-4fcc-822f-52677b6ae38c`
- Live state: `active=true`, `versionId == activeVersionId == 3a3a6ab2-79a3-4fcc-822f-52677b6ae38c`, `triggerCount=0` by design for an execute-workflow trigger
- Canonical destination: `Sales Outreach` (`dhdlf3O4tymxFtHk4aqq`) → `Priority` (`be636da7-3c15-48ab-b589-c75bcd6f9955`)
- Current normalized channels: `linkedin`, `instagram`, `sms`, `call`, `voicemail`, and `email`. LinkedIn, Instagram, and SMS are attached; calls/voicemail and email are not.
- Input contract: `contact_id`, stable `source_event_id`, `occurred_at`, `channel`, `reason`, optional owner/name fields, and preserved source payload.
- Idempotency boundary: atomically claim `(contact_id, source_event_id)` in `lt_exec_v1_inbound_priority_events` and acquire a short per-contact lock in `lt_exec_v1_priority_contact_locks` before any GHL lookup or mutation.
- Opportunity behavior: update one unambiguous open Sales Outreach opportunity to Priority; create one only when the reviewed contract permits it; preserve owner and attribution fields; return a terminal no-op for duplicate, already-Priority, closed-protected, or ambiguous states.
- Credential references: managed Postgres credential `Postgres account` (`pgAzUqpwOiGkGXzO`) and managed GHL bearer credential `GHL API - Intake Poller` (`LIgX7IrOQoG1BusR`). No secret was copied into documentation.

- LinkedIn caller `7o5EBdvwAuIaWW7k` is published at `dd98c27b-0fca-491c-bac1-3ff38b1b147b`; both main and partnership branches route after state persistence. The router fetches the contact owner before any create and fails closed with `owner_unresolved` when absent.
- Instagram caller `pISlgYUsyJIrLuJd` is published at `e09111d7-2c63-4925-b335-741c57f5ab5d`; it routes after durable reply claim, contact/message handling, and mapping upsert.
- SMS caller `i0pROHpFtN4LYR0Q` is published at `599995a9-72ce-467d-9892-c7ddf496c3fa`; it routes after event claim, contact resolution, and state upsert. STOP/unsubscribe events are excluded.
- Caller Execute Workflow nodes use non-blocking error handling so existing inbound persistence and webhook response paths are not dependent on Priority routing.

Workflow and node validation passed. Six branch tests used n8n pin data, so side-effecting Postgres and GHL nodes were bypassed: create `1050280`, update `1050281`, already Priority `1050282`, closed protected `1050283`, duplicate terminal `1050284`, and ambiguous open `1050285`. After correcting no-op audit projection, closed-protected `1050290` and ambiguous-open `1050291` also passed. These are mocked branch checks, not proof of live API or database behavior.

LinkedIn, Instagram, and SMS caller attachment is complete at the reviewed persistence boundaries. Calls/voicemail and email remain blocked on source-contract repairs. A production smoke test requires separate approval because it can mutate GHL.

### LinkedIn source-contract audit

Read-only inspection of active workflow `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`, attached version `dd98c27b-0fca-491c-bac1-3ff38b1b147b`) and webhook executions `986965`, `986966`, `986969`, and `986971` established the exact caller mapping:

- `contact_id` = resolved `ghl_contact_id` after `Create LinkedIn Contact and Add Inbound Message`
- `source_event_id` = Unipile `message_id`
- `occurred_at` = normalized Unipile `timestamp`
- `channel` = `linkedin`
- `reason` = a fixed audited value such as `linkedin_inbound_reply`
- `contact_name` = `sender_name`
- `payload` = the normalized inbound event, including chat/message/provider identifiers and message text

The same Unipile message IDs appeared in separate webhook executions during OAuth-retry/replay handling, confirming that `message_id` is the correct idempotency key. The caller must require `is_inbound=true`, `account_type=LINKEDIN`, `event_type=message_received`, a non-empty resolved `ghl_contact_id`, `message_id`, and valid `timestamp`. Missing identifiers must fail closed.

The source output does not carry the GHL contact owner. The router now performs a live contact-owner lookup before any create; if no owner is resolved it fails closed with `owner_unresolved` rather than creating an unassigned opportunity. Existing opportunity updates preserve the opportunity's native `assignedTo`.

A read-only official GHL opportunity search for a verified contact returned HTTP 200 with the response shape used by the draft: top-level `opportunities[]` containing `id`, `pipelineId`, `pipelineStageId`, `assignedTo`, `status`, and `contactId`, plus pagination metadata. This accepts the search-response parsing assumptions for a normal open opportunity. Create/update response semantics remain unverified because validating them would mutate CRM data.

The router's five-minute contact lock is recoverable after a pre-mutation HTTP failure: a later replay of the same event can reacquire an expired lock while the audit row is still `claimed`. If a GHL update/create succeeds but final audit persistence fails, a replay should observe the resulting Priority opportunity and converge to `already_priority`. Caller Execute Workflow nodes use non-blocking error handling so failures do not block inbound-message persistence; a durable claimed-event reconciler remains a follow-up requirement.

### Call, voicemail, and email source audit

The remaining live sources were inspected read-only. None is ready to attach without a source-contract repair:

- Protected call workflow `LT - Call Outcome Ingest` (`PUCfTZBANSPcgS0c`, active version `7af98411-009f-4505-9c5c-364a6f8176c3`) derives `source_key` from `startTime + toNumber + fromNumber`, but falls back to `callId` and finally a random key when required fields are absent. It also permits an empty `contact_id`. The router caller must require an identifiable inbound direction, non-empty resolved contact ID, valid call timestamp, and a provider/GHL call ID or a fully populated deterministic composite. Random fallback IDs are not acceptable. Voicemail routing must additionally require the normalized inbound voicemail disposition.
- `LT - GHL Call Outcomes Ingest` (`CFfNeRBRuo7YRBjl`) has a better call-ID-first normalizer but no retained executions and an unauthenticated webhook boundary. It is not accepted as the production caller merely because it is active.
- `GHL Warm Intake - Email Inbound Tag (Webhook)` (`SmMf8QIfysuxQJbG`) provides no durable message/event ID or reply timestamp and defaults to dry-run. It is not an eligible Priority source.
- `LT - Partnership Reply Poller` (`0SQ7tTk03okegp9V`) and `LT - Campaign Email Reply Poller` (`hxiiYCpEfMuoSt5H`) detect only conversation-level `lastMessageDirection=inbound`; their downstream payloads do not preserve a message ID, and they do not fetch the message sender/body needed to exclude bounces, unsubscribe notices, and automated provider events. They cannot yet prove a qualifying human reply.
- `LT - Email Event Ingest` (`ZrqFN8qLKO8eVHDc`) can normalize `message_id`, `provider_message_id`, and `source_event_id`, but sampled live Emerald open/click events had all three fields empty. Existing GHL event wiring therefore cannot be assumed to supply a stable reply identifier.

The email repair boundary is to fetch the actual latest inbound email message, reject automated/bounce/unsubscribe/provider events, and pass its durable GHL/provider message ID plus original timestamp. A deterministic fallback may use conversation ID plus immutable message timestamp only if both are present and verified stable. The call repair boundary is to expose a guaranteed call ID and resolved contact ID from the protected Call Details webhook. No routing caller should use ingestion time or a random value as `source_event_id`.

### GHL contract and failure-path disposition

- Read-only opportunity search behavior is accepted from the official GHL response.
- The official connector schema and existing production workflows use `pipelineId`/`pipelineStageId` for `PUT /opportunities/{id}` and the draft does not depend on the update response body; it relies only on HTTP success and the already selected opportunity ID.
- Historical successful execution `1050287` of `GHL - MQL Tag -> Ensure Warm Qualified Opportunity` confirms that `POST /opportunities/` with location/contact/name/pipeline/stage/status returns a parseable opportunity ID. This is historical evidence, not a Priority mutation test.
- An HTTP failure before finalization leaves the event `claimed` and the contact lock recoverable after five minutes. Recovery still depends on a source replay or explicit reconciler; a scheduled claimed-event reconciler remains a follow-up requirement.
- Caller routing is deliberately a parallel, non-blocking branch after inbound persistence. It does not make the LinkedIn, Instagram, or SMS webhook fail before its existing conversation/map/state handling completes.

## GHL call totals snapshot — 2026-09-28

- The GHL native report `69bbeb2d088aabd9058eaf44` was read through the authenticated browser. Its selected report window was `2026-09-20` through `2026-09-26`; the outgoing-call widgets filter `dateAdded`, `direction=outbound`, and the SDR's native `userId`, with report timezone `Asia/Manila`.
- The live native widget responses returned Marc (`sqGx5rp3oAUG610NXyjU`) = 1,006 calls (802 answered, 105 busy, 59 no-answer, 40 failed), and Jason Bornillo (`yU85G6kfhtW4vUtx3QE6`) = 350 calls (285 answered, 19 busy, 35 no-answer, 11 failed). The screenshot's `1.01K` is the rounded display; a prior text reference of 982 was not the current native widget response.
- The V1 Facts API now serves these values only for that exact date window as a clearly labeled, dated GHL native-report snapshot. For other windows it falls back to GHL outbound call facts from the supported Conversations API and labels that basis as incomplete until reconciliation is complete. This snapshot is not an automatically refreshed feed.
- The published `LT - GHL Daily Calls Ingest` (`SqNQ0BYaTdcqyt1l`, version `98a4f785-19bf-4f17-a95e-1222141923bf`) now retries GHL 429/5xx responses and durably scans paginated conversations across a 95-day lookback, including conversations whose latest activity is no longer a call. Backfill is still in progress; the native-report snapshot remains the accepted source for the captured week.
- The official GHL PIT can read supported location/conversation endpoints but receives HTTP 401 (`The token is not authorized for this scope`) from the private native-report widget endpoint. HighLevel does document `GET /conversations/messages/export`; the current PIT can query this endpoint by `channel=Call`, date bounds, and cursor. Its exact-week counts/statuses did not reconcile to the native widgets, so do not claim parity until a supported source is reconciled by date, direction, user, status, and call ID. The Voice AI call-log API remains Voice-AI-specific and is not a substitute for human SDR widget facts.

## 2026-09-29 EOS — call source exploration and next-session plan

The full attempt log, implementation details, acceptance boundary, and ordered next-session procedure are in [`docs/sessions/2026-09-29-executive-report-v1-ghl-call-source-closeout.md`](docs/sessions/2026-09-29-executive-report-v1-ghl-call-source-closeout.md). Key current facts:

- Active V1 Facts API `oxYDg6XnRBKhl1Xd` is now version `9a17c3c2-45d2-477e-9c01-3bea0a537ae3`, with the exact native GHL snapshot hard-limited to `2026-09-20` through `2026-09-26`. The deployed V1 page displays the source/basis note; the original report path remains untouched.
- Active signed-event receiver `SA5SF1cZQcVf3IyB` is published at `15b2944f-5b71-40fe-b97a-d87718cd6cdb` (5 nodes). Executions `1062819` and `1062820` tested absent signatures and returned HTTP 401 `invalid_signature`; both followed the response branch and skipped `Persist GHL Call Event`. This is a successful negative test only.
- The receiver is not yet subscribed in Marketplace, has not processed an authentic signed event, and cannot backfill history. It is not the historical-data solution. The later supported-export investigation is now the priority; do not enable the subscription solely as a substitute for historical access.
- The documented location-level message export can query selected and prior date windows, but it has not reconciled to the native widget counts/statuses. Keep any poller/API-derived facts labeled incomplete until an exact-ID status reconciliation establishes parity.

## 2026-09-29 — supported call-message export investigation

HighLevel's public API documentation includes `GET /conversations/messages/export`. Query parameters include `locationId`, `channel=Call`, `startDate`, `endDate`, `limit`, `cursor`, `sortBy`, and `sortOrder`. Response messages expose `id`, `messageType`, `dateAdded`, `direction`, `userId`, `status`, and call metadata. The endpoint requires `conversations/message.readonly`; the current GHL PIT returned HTTP 200 for read-only requests.

### Read-only results

- For completed LA report days `2026-09-22` through `2026-09-28`, the export returned `total=1,990` across 20 pages. Outbound counts were Marc 1,305 (1,086 `completed`, 109 `busy`, 56 `no-answer`, 53 `failed`, 1 `unknown`) and Jason 663 (564 `completed`, 23 `busy`, 52 `no-answer`, 24 `failed`).
- For prior LA week `2026-09-15` through `2026-09-21`, it returned `total=1,227` across 13 pages. Outbound counts were Marc 764 (653 `completed`, 46 `busy`, 47 `no-answer`, 18 `failed`) and Jason 450 (366 `completed`, 24 `busy`, 37 `no-answer`, 23 `failed`).
- For exact native-widget dates `2026-09-20` through `2026-09-26` in `Asia/Manila` (UTC bounds `2026-09-19T16:00:00Z` through `2026-09-26T16:00:00Z`), the export returned `total=1,769` across 18 pages and 1,747 outbound rows with no duplicate/missing IDs in the scan. Marc: 1,288 (1,075 `completed`, 105 `busy`, 59 `no-answer`, 48 `failed`, 1 `unknown`). Jason: 460 (393 `completed`, 19 `busy`, 34 `no-answer`, 14 `failed`).
- Native counts for that week remain Marc 1,006 (802 answered, 105 busy, 59 no-answer, 40 failed) and Jason 350 (285 answered, 19 busy, 35 no-answer, 11 failed). The export is not currently an accepted V1 metric source: `completed` is not established as equivalent to native `answered`, and outbound totals differ materially.
- The authenticated Call Reporting UI's private `POST backend.leadconnectorhq.com/reporting/calls/get-all-phone-calls-new` returned 1,377 rows for the exact captured week; paginating all 28 pages and filtering outbound by `userId` and `callStatus` exactly matched the native widget totals/statuses (Marc 1,006; Jason 350). The response included 21 inbound rows in addition to 1,356 outbound. The same POST using the GHL PIT outside the browser returned HTTP 401 `The token is not authorized for this scope`. Exact parity in the authenticated UI does not make this private/undocumented route an approved n8n integration.

### Decision and next validation

- Two date-bounded queries (selected 7d and prior 7d) are technically possible using the documented export. Cursor pagination is required, and cursors are valid for two minutes; collect each window promptly within that cursor lifetime. The private Call Reporting UI route also paginated the exact snapshot week in 28 pages, but it rejected the PIT and remains unsupported for automation.
- Reconcile the supported export against a supported GHL CSV/report detail export for the exact snapshot week by call ID, `dateAdded`, direction, user, status/disposition, and timezone. If no supported detail export can establish parity, retain the exact-week snapshot and label other periods unavailable/incomplete rather than showing unvalidated numbers. Ask GHL whether the privately tested Call Reporting data can be exposed through a documented API/scope.
- The Marketplace webhook remains optional as a forward-looking event ledger; it cannot provide history. No subscription was configured, and no call/report records were changed. Next, ask GHL for documented API access to the proven Call Reporting data or obtain supported report exports; do not automate the private browser route.
````

## File: reports/embed/executive-v1/DATA-COLLECTION-PLAN.md
````markdown
# V1 data collection plan

This is the implementation contract for making every mockup detail real and auditable. It is deliberately separate from the UI so data work can be completed and tested before deployment.

## Required canonical facts

### 1. Contact acquisition provenance

Create or expose one row per contact with:

- `contact_id`, `created_at`, `source`, `medium`, `campaign`
- `acquisition_mechanism`: `linkedin_backfill`, `apollo_upload`, `form`, `manual`, `booking`, `other`, or `unknown`
- `mechanism_evidence`: sanitized import name, workflow/event ID, or form ID
- `is_backfill`, `is_duplicate`, `is_in_period`

Rules: classify once per contact, use deterministic precedence, and reconcile the mechanism total to the New Contacts headline card.

### 2. Appointment detail and outcomes

Expose one row per appointment with:

- appointment/contact IDs, contact name, calendar/link, start time, status
- assigned SDR, originating SDR, attribution path, attribution confidence
- created time, updated time, rescheduled-from ID, cancellation reason

Rules: booked is based on `start_at` in the selected window; showed/no-show/cancelled/rescheduled are recorded statuses only; never infer an outcome from elapsed time.

For the Cameron headline KPI, count `COUNT(DISTINCT contact_id)` over Cameron-assigned appointment rows in the selected window, excluding blank contact IDs. Multiple appointment rows for the same contact—including cancellation followed by reschedule—count once. Preserve the raw appointment rows separately for audit and outcome detail.

### 3. Pipeline-to-work and action queue

Expose one row per actionable opportunity/task with:

- opportunity/contact ID, pipeline, stage, owner, stage-entered time
- next-action type, next-action due time, last activity time
- SLA rule version, overdue flag, suppression/closed flag

Rules: define “qualified remaining” and “overdue” in code and return the rule version with the counts. The action queue total must reconcile to the underlying actionable rows.

### 4. Same-channel response speed and follow-up

Persist each inbound response opportunity and the first later outbound response on the same channel:

- LinkedIn inbound DM/reply → later LinkedIn DM
- inbound call → later outbound call
- marketing-email reply → later marketing email send
- contact ID, inbound/outbound event IDs and timestamps, channel, campaign, actor/workflow
- elapsed seconds, `responded`/`unmatched`/`ambiguous` status, source-health status

Rules: match by contact and channel with a strictly later timestamp; mark multiple same-timestamp candidates as ambiguous; publish average and median only from unambiguous matched responses with explicit denominators; keep unmatched and ambiguous inbound events visible; do not label them overdue until an approved response-time target exists.

### 5. Voicemail disposition and callback facts

For the selected period, select the latest non-empty `voice_call_attempt.disposition` per unique contact and expose:

- unique contacts with a latest disposition
- unique contacts whose latest disposition is `voicemail`/`voicemail_left`
- unique contacts whose latest disposition is an explicit callback request
- disposition breakdown and source freshness

Rules: selecting the voicemail custom disposition is the approved indicator that a voicemail was left. Use the latest disposition per unique contact and do not count a contact more than once in the drops, delivered, or callback totals.

### 6. Channel delivery facts

For each email, LinkedIn, SMS, and voicemail event, expose:

- stable event ID, campaign key, contact ID, event timestamp
- sent/delivered/opened/clicked/replied/bounced/failed/callback status as applicable
- provider ID, source workflow, deduplication key, attribution confidence

Rules: aggregate distinct recipients where the mockup implies people; keep raw event counts separate; do not turn missing provider events into zero.

### 7. SDR inputs

Expose one canonical call-attempt fact with:

- call ID, contact ID, SDR, campaign, attempt time
- connected/no-answer/busy/failed/wrong-number disposition
- provider and workflow IDs, duplicate key

Rules: use `report_raw_ghl_calls` as the current GHL source of truth and include Vapi attempts as a separate source in the canonical fact table. Calls-attempted must equal connected + no-answer + busy/failed + wrong-number + explicit unknown/other; per-SDR totals must reconcile to the team strip without treating missing owner attribution as zero.

### 8. Social account statistics

Ingest platform/account/day facts for posts, impressions, reach, engagement, and followers, with:

- platform, account ID, date, metric name/value, provider response timestamp
- source-health status and timezone

Rules: do not mix post-placement counts with account statistics; label metrics unavailable when OAuth/statistics data is absent.

## QA gates

1. Each selected period returns non-empty JSON and source-health rows.
2. Every headline metric has a denominator/basis and a reconciliation query.
3. Source breakdowns sum to the headline or expose an explicit Unknown/Unattributed remainder.
4. SDR rows sum to team totals; owner conflicts and Unassigned are visible.
5. Channel tables reconcile to channel totals and preserve campaign keys.
6. Appointment detail reconciles to booked and outcome totals.
7. No metric is silently defaulted to zero when its source field is missing.
8. Run the same checks for 7d, 30d, 90d, and a custom period.
9. Capture a desktop and approximately 390px mobile screenshot; confirm no horizontal overflow.
10. Validate the original Executive Report URL remains unchanged before any V1 deployment.
````

## File: reports/embed/executive-v1/DATA-REQUIREMENTS.md
````markdown
# Executive Report V1 data requirements

The supplied mockup defines the presentation flow. Its numbers are illustrative; the V1 report must calculate real values for one shared reporting window and must not silently convert missing data into zero.

## Shared rules

- Use one selected date window across all sections, with the reporting timezone applied consistently.
- Preserve the existing `7d`, `30d`, `90d`, and custom-period controls where practical.
- Show the selected period and freshness/source-health context.
- Use explicit `Unknown`, `Unattributed`, `Unassigned`, and `Unavailable` buckets.
- Treat HTTP 200 with an empty report body as a failure.
- Every metric needs a short definition and a source note in the UI or glossary.
- Validate that totals reconcile across headline cards, breakdowns, and tables before review.

## P0 — trustworthy numbers

| Mockup area | Required real values | Current source / status | Validation needed |
|---|---|---|---|
| Headline row | New MQLs, new SQLs, MQL→SQL, unique Cameron booking contacts, new contacts, opportunities created | Executive Summary API plus V1 appointment facts | Count distinct non-empty contact IDs for Cameron-assigned bookings in the selected window; cancellation/reschedule appointment rows for the same contact count once |
| Opportunities by source | Opportunities grouped by source/campaign | Executive Summary attribution and campaign/source payloads | Distinct opportunity IDs; exclude classified historical backfill contacts where required |
| MQL sources | MQLs by originating source | `leadSourceBreakdown` / `leadSourceCoverage` | Display coverage and Unknown / Unattributed rather than implying full attribution |
| SQL sources | SQLs by originating source | `leadSourceBreakdown` / `leadSourceCoverage` | Reconcile sum of rows to SQL denominator |
| New contacts — how added | Contacts by acquisition/addition mechanism | GHL contacts, source fields, backfill classifier, campaign/import markers | Define LinkedIn backfill, Apollo upload, form, manual/other buckets without double counting |
| Meetings — who & where | Contact, SDR/owner, booking link/calendar | Appointments snapshot plus contact/opportunity owner mapping | Verify appointment-to-contact and originating-SDR attribution; expose Unassigned; keep the headline KPI distinct-contact based for Cameron |
| Meeting outcomes | Showed, no-show, cancelled, rescheduled | GHL appointment statuses | Do not infer Showed; current status-update gap may require Unavailable or clearly labelled 0 |
| Pipeline to work | Qualified/open work remaining this period | Opportunity snapshot/stage data | Define “qualified” and “remaining”; avoid mixing active snapshot with created-in-period |
| Lead-source coverage | Attributed / total and percentage | `leadSourceCoverage` | Coverage denominator must match MQL/SQL cards |
| Speed-to-lead / follow-up | Response time from inbound LinkedIn DM, inbound call, or marketing-email reply to the next outbound event on the same channel; unmatched inbound count | `lt_exec_v1_response_sla`, materialized from LinkedIn activity, `Email_Events` + marketing send ledgers, and GHL call outcomes | Match by contact/channel and later timestamp; publish average/median only with response denominator; do not call unmatched records “overdue” until a business target is configured |

## P1 — layout and channel story

## Feedback extension — funnel, movement, retargeting, and Priority

- Funnel order is opportunities, MQLs, SQLs, meetings, closed won/lost, and revenue. Closed-by-source keeps referral and other valid sources in the denominator; residuals are `Unknown / Unattributed`.
- Weekly flow uses distinct contact IDs for new leads and distinct opportunity IDs for stage movement. Current stage distribution is a snapshot, not a period-entry count.
- Vertical reporting uses the canonical vertical/source field and retains `Unclassified`; unsupported metrics are unavailable.
- Retargeting is queue visibility only: eligible contacts, latest click/audience touch, suppression/reply state, and next action. It does not authorize a send.
- Inbound response speed retains the same-channel SLA contract. It is not MQL-to-first-call.
- Priority is `Sales Outreach` stage `be636da7-3c15-48ab-b589-c75bcd6f9955`; closed opportunities are protected and retries are keyed by contact plus source event.

| Mockup area | Required values | Likely source |
|---|---|---|
| Outbound total strip | Emails, LinkedIn messages, SMS, voicemails, newsletters | Campaign Channel Summary plus channel ledgers |
| Email campaign table | Sent, delivered, opened, clicked, replied, bounced | Email send/event ledgers and Campaign Channel Summary |
| LinkedIn campaign table | Invites, accepted, messages delivered, opened if available, replied | `linkedin_activity_events` and campaign attribution |
| SMS table | Sent, delivered, replies, failed | SimpleTexting event ledger / campaign summary |
| Voicemail table | Latest custom disposition per unique contact; voicemail drops/left and callback-requested counts | `voice_call_attempt.disposition`, materialized into `lt_exec_v1_call_facts` |
| SDR performance strip/table | Calls attempted, connected, no answer, busy/failed, wrong number; per SDR effort and outputs | GHL native call-report snapshot when captured; otherwise `report_raw_ghl_calls` / V1 call facts |
| Social media strip/table | Posts, impressions, reach, engagement, followers by channel | GHL Social Planner post ledger and account statistics |
| Action queue | MQL response SLA, stale contracts/proposals, overdue follow-ups | GHL opportunity/task/activity timestamps plus agreed SLA rules |

## Known data gaps to surface early

1. Appointment outcomes are not reliable until GHL status is updated after meetings; do not manufacture showed/no-show values.
2. Social reach, impressions, saves, and follower statistics may be unavailable when the GHL OAuth/statistics source is not authenticated.
3. Selecting the voicemail custom disposition is the business rule for “voicemail left”; drops sent and delivered therefore use the same latest-disposition unique-contact count. Callback-requested counts use explicit callback dispositions.
4. Response speed is now collected from durable same-channel event timestamps. A response-time target is still not configured, so the report shows unmatched inbound events rather than inventing an overdue threshold.
5. Email engagement must show coverage and use unique-recipient rates where possible; missing provider events must not be presented as zero engagement.
6. GHL's native per-SDR call widgets use `dateAdded`, `direction=outbound`, and `userId`, with the checked native report in `Asia/Manila`. The captured 2026-09-20..2026-09-26 snapshot is exact for that period only. HighLevel publicly documents `GET /conversations/messages/export` with `channel=Call`, date bounds, and cursor pagination; the current PIT can read it, but its exact-week outbound rows/statuses did not reconcile to native widget totals. The authenticated Call Reporting UI's private calls endpoint did match the exact-week widget counts, but that endpoint returned HTTP 401 with the GHL PIT and is undocumented. Do not build an automated dependency on the private UI endpoint; request supported access or use a supported export. Keep documented-export values incomplete until reconciled.

## Acceptance checks before V1 review

- API response is non-empty JSON and all required source-health rows are ready or visibly flagged.
- Headline numbers reconcile to the corresponding breakdowns.
- MQL/SQL/contacts/opportunities use documented distinctness and period rules.
- Meeting totals reconcile to the appointment table and SDR rows.
- Channel totals reconcile to the campaign tables, with unattributed activity shown separately.
- No unavailable source is rendered as a trustworthy zero.
- Desktop and approximately 390px mobile layouts have no horizontal overflow.
- The existing Executive Report remains unchanged and still renders from its original path.
````

## File: reports/embed/executive-v1/EXECUTIVE-REPORT-V1-FEEDBACK-CONTRACT.md
````markdown
# Executive Report V1 feedback contract

This contract extends V1 without changing `/embed/executive/`. It is the interface between the facts API, the report UI, and the eventual Priority routing workflow.

## Shared rules

- Every metric uses the selected `America/Los_Angeles` window and returns `basis`, `distinctness`, `date_rule`, `freshness`, and `source_health` metadata.
- Missing, stale, or incomplete sources render `Unavailable`; they never become zero.
- Contacts are distinct by canonical GHL contact ID. Opportunities and stage movement are distinct by opportunity ID unless a field says `contact_metric: true`.
- Closed opportunities are never reopened or moved by Priority routing.
- `Unknown`, `Unattributed`, `Unassigned`, and `Unclassified` remain real buckets in every breakdown.

## Facts API additions

The V1 facts payload may contain these top-level objects. An object is considered available only when `available: true` and its health is ready.

```json
{
  "funnel": {
    "available": true,
    "opportunities_created": 0,
    "mqls_entered": 0,
    "sqls_entered": 0,
    "mql_to_sql_rate": null,
    "closed_won_sqls": 0,
    "closed_lost_sqls": 0,
    "sql_to_closed_rate": null,
    "revenue": null,
    "basis": "distinct opportunity_id; first observed stage entry; LA dates",
    "source_health": "ready"
  },
  "closedBySource": [{
    "source": "Unknown / Unattributed", "sqls": 0, "won": 0, "lost": 0,
    "revenue": null, "coverage": "partial"
  }],
  "weeklyLeadFlow": [{
    "week_start": "2026-09-21", "new_contacts": 0, "mqls_entered": 0,
    "sqls_entered": 0, "later_stage_entries": 0, "current_stage_distribution": []
  }],
  "verticalPerformance": [{
    "vertical": "Unclassified", "leads": 0, "sends": 0, "responses": 0,
    "meetings": 0, "sqls": 0, "won": 0, "lost": 0, "revenue": null
  }],
  "retargeting": {
    "available": true, "eligible": 0, "latest_touchpoints": [],
    "suppressed_or_replied": 0, "next_action_pending": 0,
    "send_authorized": false
  },
  "priority": {
    "available": true, "stage_id": null, "stage_name": "Priority",
    "open_count": 0, "created_in_window": 0,
    "by_source": [], "routing_health": "not_configured"
  }
}
```

The existing same-channel response-SLA definition remains authoritative. The UI label is **Inbound response speed**, not MQL-to-call speed.

## Priority routing contract

The canonical pipeline is `Sales Outreach` (`dhdlf3O4tymxFtHk4aqq`). The live Priority stage is now verified at position 1 with GHL stage ID `be636da7-3c15-48ab-b589-c75bcd6f9955`. Workflow publication must use this exact ID and re-read the pipeline after publication.

Qualifying events are: identifiable inbound call, inbound voicemail disposition, identifiable Unipile LinkedIn DM/reply, and qualifying human email reply. Bounces, unsubscribe notices, and automated provider events are excluded. Each accepted event writes an immutable audit row keyed by `(contact_id, source_event_id)` with channel (`call`, `voicemail`, `linkedin`, or `email`), event timestamp, routing reason, prior opportunity ID/stage, resulting opportunity ID/stage, owner, and outcome.

Routing is an upsert-and-move operation:

1. Resolve the contact using the existing inbound handler.
2. Search open `Sales Outreach` opportunities for that contact.
3. Move the existing open opportunity to Priority, preserving owner and attribution; otherwise create one Priority opportunity.
4. Never reopen or move a closed opportunity.
5. A retry with the same contact and source event is a no-op.

Priority is excluded from cold-outbound sequence eligibility. This report-only visibility does not authorize sending.

## Acceptance fixtures

The API and routing tests must cover: first event, duplicate event retry, existing open opportunity, no opportunity, closed opportunity, unknown contact, excluded email event, conflicting owner data, and two different events for the same contact. Each fixture must assert exact IDs and no duplicate opportunity creation.
````

## File: reports/embed/executive-v1/index.baseline.html
````html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Live Transparent | Executive Report</title>
    <meta name="color-scheme" content="dark" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
    <style>
      :root {
        --bg: #0b1020;
        --panel: #12192d;
        --panel-2: #161f36;
        --panel-3: #1a2440;
        --line: rgba(255, 255, 255, 0.08);
        --text: #eef2ff;
        --muted: #9aa4bf;
        --faint: #7380a3;
        --green: #37d67a;
        --blue: #4f8cff;
        --amber: #f3b63f;
        --red: #ff6b6b;
        --purple: #8f7cff;
        --teal: #2fc7b5;
        --shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
        --radius: 18px;
      }
      * { box-sizing: border-box; margin: 0; padding: 0; }
      html, body {
        min-height: 100%;
        background: radial-gradient(circle at top left, rgba(79, 140, 255, 0.16), transparent 26%),
          radial-gradient(circle at top right, rgba(143, 124, 255, 0.12), transparent 22%),
          linear-gradient(180deg, #090d19 0%, #0b1020 100%);
        color: var(--text);
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, sans-serif;
      }
      .shell { display: grid; grid-template-columns: 248px 1fr; min-height: 100vh; }
      .sidebar {
        position: relative; z-index: 20; min-width: 0; border-right: 1px solid var(--line);
        background: rgba(7, 11, 24, 0.78); backdrop-filter: blur(18px); padding: 24px 16px;
      }
      .brand { display: flex; align-items: center; gap: 12px; padding: 10px 12px 22px; }
      .brand-mark { width: 36px; height: 36px; border-radius: 12px; background: linear-gradient(135deg, var(--blue), var(--purple)); box-shadow: 0 10px 30px rgba(79, 140, 255, 0.35); }
      .brand-copy { display: grid; gap: 2px; }
      .brand-copy strong { font-size: 0.92rem; letter-spacing: 0.03em; }
      .brand-copy span { font-size: 0.76rem; color: var(--muted); }
      .nav-group { margin-top: 18px; }
      .nav-title { padding: 0 12px 8px; font-size: 0.7rem; letter-spacing: 0.16em; text-transform: uppercase; color: var(--faint); }
      .nav-item {
        display: flex; align-items: center; gap: 10px; width: 100%; border: 0;
        background: transparent; color: var(--muted); padding: 11px 12px;
        border-radius: 12px; text-align: left; font: inherit; cursor: pointer;
      }
      .nav-item.active { background: rgba(79, 140, 255, 0.14); color: var(--text); }
      .nav-dot { width: 8px; height: 8px; border-radius: 50%; background: currentColor; opacity: 0.9; }
      .content { position: relative; z-index: 1; min-width: 0; padding: 28px; }
      .topbar { display: flex; justify-content: space-between; gap: 16px; align-items: center; margin-bottom: 22px; }
      .title-wrap h1 { margin: 0; font-size: clamp(1.5rem, 2.2vw, 2.2rem); line-height: 1.1; }
      .title-wrap p { margin: 8px 0 0; color: var(--muted); font-size: 0.95rem; }
      .controls { display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-end; position: relative; z-index: 20; }
      .build-badge {
        display: inline-flex; align-items: center; padding: 8px 12px; border-radius: 999px;
        border: 1px solid rgba(79, 140, 255, 0.4); background: rgba(79, 140, 255, 0.12);
        color: #c9d8ff; font-size: 0.78rem; letter-spacing: 0.02em; white-space: nowrap;
      }
      .chip, .button {
        border-radius: 999px; border: 1px solid var(--line); background: rgba(255, 255, 255, 0.03);
        color: var(--text); padding: 10px 14px; font: inherit; cursor: pointer;
      }
      .chip.active { background: rgba(79, 140, 255, 0.18); border-color: rgba(79, 140, 255, 0.36); }
      .button { background: linear-gradient(135deg, rgba(79, 140, 255, 0.18), rgba(143, 124, 255, 0.18)); }
      .period-picker { display: flex; flex-wrap: wrap; align-items: end; gap: 10px; margin-bottom: 16px; padding: 14px 16px; border: 1px solid var(--line); border-radius: var(--radius); background: rgba(255, 255, 255, 0.025); }
      .period-picker label { display: grid; gap: 5px; color: var(--muted); font-size: 0.76rem; }
      .period-picker input { min-height: 38px; border: 1px solid var(--line); border-radius: 10px; background: var(--panel-2); color: var(--text); padding: 8px 10px; font: inherit; }
      .period-picker .period-note { margin-left: auto; color: var(--faint); font-size: 0.8rem; align-self: center; }
      .grid { display: grid; gap: 16px; min-width: 0; }
      .grid > *, .panel, .panel-body, .table-scroll { min-width: 0; }
      .kpi-row { grid-template-columns: repeat(6, minmax(0, 1fr)); }
      .three-col { grid-template-columns: repeat(3, minmax(0, 1fr)); }
      .two-col { grid-template-columns: 1.3fr 1fr; }
      .panel {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
        border: 1px solid var(--line); border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden;
      }
      .panel-head { display: flex; justify-content: space-between; align-items: center; gap: 16px; padding: 18px 18px 0; }
      .panel-head h2 { margin: 0; font-size: 0.96rem; letter-spacing: 0.08em; text-transform: uppercase; }
      .panel-head span { color: var(--muted); font-size: 0.86rem; }
      .panel-body { padding: 18px; }
      .kpi-card {
        padding: 20px; border-radius: 18px; border: 1px solid var(--line);
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.035), rgba(255, 255, 255, 0.018));
        text-align: center;
      }
      .kpi-card .label { color: var(--muted); font-size: 0.8rem; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.08em; }
      .kpi-card .value { font-size: 2.2rem; font-weight: 700; line-height: 1; }
      .kpi-card .sub { margin-top: 6px; color: var(--faint); font-size: 0.82rem; }
      .mini-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
      .mini {
        padding: 16px; border-radius: 16px; background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
      }
      .mini strong { display: block; margin-bottom: 8px; color: var(--muted); font-size: 0.8rem; }
      .mini div { font-size: 1.3rem; font-weight: 700; }
      .mini-grid-2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
      .mini-grid-4 { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
      .definition-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
      .definition-card {
        padding: 16px; border-radius: 16px; background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
      }
      .definition-card strong {
        display: block; margin-bottom: 8px; color: var(--text); font-size: 0.9rem; letter-spacing: 0.03em;
      }
      .definition-card p { color: var(--muted); font-size: 0.84rem; line-height: 1.5; }
      .bar-list { display: grid; gap: 12px; }
      .bar-item { display: grid; grid-template-columns: 180px 1fr 68px; gap: 12px; align-items: center; }
      .bar-label { color: var(--text); font-size: 0.92rem; }
      .bar-track { height: 10px; border-radius: 999px; background: rgba(255, 255, 255, 0.08); overflow: hidden; }
      .bar-fill { height: 100%; border-radius: inherit; width: var(--w); background: linear-gradient(90deg, var(--c1), var(--c2)); }
      .bar-value { text-align: right; color: var(--muted); font-variant-numeric: tabular-nums; }
      .metric-glossary > summary { list-style: none; cursor: pointer; }
      .metric-glossary > summary::-webkit-details-marker { display: none; }
      .campaign-filters { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }
      .campaign-filters .chip { padding: 7px 11px; font-size: 0.78rem; }
      .campaign-table { width: 100%; border-collapse: collapse; min-width: 760px; }
      .campaign-table th, .campaign-table td { padding: 12px 10px; border-bottom: 1px solid var(--line); text-align: right; font-variant-numeric: tabular-nums; }
      .campaign-table th:first-child, .campaign-table td:first-child { text-align: left; }
      .campaign-table th { color: var(--muted); font-size: 0.75rem; letter-spacing: 0.06em; text-transform: uppercase; }
       .campaign-table td { color: var(--text); font-size: 0.9rem; }
       .table-scroll { overflow-x: auto; }
       .call-table { width: 100%; border-collapse: collapse; min-width: 1180px; }
       .call-table th, .call-table td { padding: 11px 10px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: middle; }
       .call-table th { color: var(--muted); font-size: 0.72rem; letter-spacing: 0.06em; text-transform: uppercase; white-space: nowrap; }
       .call-table td { color: var(--text); font-size: 0.84rem; }
       .call-table .numeric { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
       .call-table .muted { color: var(--muted); }
       .call-table .contact { display: grid; gap: 3px; }
       .call-table .contact small { color: var(--muted); }
       .call-controls { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 12px; }
       .call-pagination { display: flex; align-items: center; gap: 8px; color: var(--muted); font-size: 0.82rem; }
       .call-pagination button { border: 1px solid var(--line); border-radius: 9px; background: rgba(255,255,255,0.04); color: var(--text); padding: 7px 10px; cursor: pointer; }
       .call-pagination button:disabled { opacity: 0.45; cursor: not-allowed; }
       .call-page-size { color: var(--muted); font-size: 0.82rem; }
       .call-audio { width: 170px; height: 30px; }
       .footer-note { margin-top: 14px; color: var(--faint); font-size: 0.82rem; }
       .campaign-row-clickable { cursor: pointer; transition: background 0.15s; }
       .campaign-row-clickable:hover { background: rgba(79, 140, 255, 0.08); }
       .campaign-row-clickable.expanded { background: rgba(79, 140, 255, 0.1); }
       .campaign-detail-panel {
         margin-top: 14px; padding: 18px; border-radius: 14px;
         border: 1px solid rgba(79, 140, 255, 0.2);
         background: rgba(79, 140, 255, 0.05);
       }
       .campaign-detail-panel h3 { margin: 0 0 12px; font-size: 0.95rem; color: var(--blue); }
       .campaign-detail-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }
       .campaign-detail-card {
         padding: 14px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.06);
         background: rgba(255, 255, 255, 0.025);
       }
       .campaign-detail-card .detail-label { display: block; color: var(--muted); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 5px; }
       .campaign-detail-card .detail-value { font-size: 1.15rem; font-weight: 700; }
       .campaign-detail-card .detail-rate { margin-top: 3px; color: var(--faint); font-size: 0.78rem; }
       .campaign-actions { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }
       .campaign-actions button { padding: 5px 10px; font-size: 0.75rem; }
      .divider { border-top: 1px solid var(--line); margin: 16px 0; }
      .sub-head { color: var(--muted); font-size: 0.84rem; font-weight: 600; letter-spacing: 0.05em; margin: 14px 0 8px; }
      .section-label { font-size: 0.75rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--faint); margin-bottom: 10px; padding-left: 4px; }
      .loading { color: var(--muted); font-style: italic; }
      .good { color: var(--green); }
      .warn { color: var(--amber); }
      .bad { color: var(--red); }
      .pending { color: var(--faint); }
      .comparison-grid { grid-template-columns: repeat(7, minmax(0, 1fr)); }
      .comparison-grid .mini div { font-size: 1.05rem; }
      .comparison-grid .delta { display: block; margin-top: 5px; color: var(--muted); font-size: 0.76rem; font-weight: 500; }
      @media (max-width: 1100px) {
        .shell { grid-template-columns: 1fr; }
        .sidebar { border-right: 0; border-bottom: 1px solid var(--line); }
        .topbar { align-items: flex-start; flex-direction: column; }
        .controls { justify-content: flex-start; max-width: 100%; }
        .kpi-row { grid-template-columns: repeat(3, 1fr); }
        .three-col, .two-col { grid-template-columns: 1fr; }
        .mini-grid, .mini-grid-2, .mini-grid-4 { grid-template-columns: repeat(2, 1fr); }
        .comparison-grid { grid-template-columns: repeat(3, 1fr); }
        .definition-grid { grid-template-columns: 1fr; }
        .bar-item { grid-template-columns: minmax(0, 1fr); width: 100%; }
        .bar-label { overflow-wrap: anywhere; }
        .bar-value { text-align: left; }
      }
      @media (max-width: 600px) {
        .content { padding: 20px 14px; }
        .build-badge { max-width: 100%; white-space: normal; overflow-wrap: anywhere; }
        html, body { overflow-x: clip; }
      }
    </style>
  </head>
  <body>
    <div class="shell">
      <aside class="sidebar">
        <div class="brand">
          <div class="brand-mark" aria-hidden="true"></div>
          <div class="brand-copy">
            <strong>Live Transparent</strong>
            <span>Executive Report</span>
          </div>
        </div>
        <div class="nav-group">
          <div class="nav-title">Overview</div>
          <a class="nav-item active" href="?view=overview&range=30d&embed=1&section=section-kpis" data-view="overview" data-scroll="section-kpis"><span class="nav-dot"></span> Executive Summary</a>
          <a class="nav-item" href="?view=overview&range=30d&embed=1&section=section-traffic" data-view="overview" data-scroll="section-traffic"><span class="nav-dot"></span> Traffic &amp; Channels</a>
          <a class="nav-item" href="?view=overview&range=30d&embed=1&section=section-funnel" data-view="overview" data-scroll="section-funnel"><span class="nav-dot"></span> Funnel &amp; Attribution</a>
          <a class="nav-item" href="?view=overview&range=30d&embed=1&section=section-acquisition" data-view="overview" data-scroll="section-acquisition"><span class="nav-dot"></span> Acquisition Sources</a>
          <a class="nav-item" href="?view=overview&range=30d&embed=1&section=section-pages" data-view="overview" data-scroll="section-pages"><span class="nav-dot"></span> Top Pages</a>
          <a class="nav-item" href="?view=overview&range=30d&embed=1&section=section-sales" data-view="overview" data-scroll="section-sales"><span class="nav-dot"></span> Sales &amp; Pipeline</a>
            <a class="nav-item" href="?view=overview&range=30d&embed=1&section=section-sdr" data-view="overview" data-scroll="section-sdr"><span class="nav-dot"></span> SDR Performance</a>
            <a class="nav-item" href="?view=overview&range=30d&embed=1&section=section-lead-source" data-view="overview" data-scroll="section-lead-source"><span class="nav-dot"></span> Lead Source</a>
           <a class="nav-item" href="?view=overview&range=30d&embed=1&section=section-calls" data-view="overview" data-scroll="section-calls"><span class="nav-dot"></span> Calls &amp; Conversations</a>
           <a class="nav-item" href="?view=overview&range=30d&embed=1&section=section-campaigns" data-view="overview" data-scroll="section-campaigns"><span class="nav-dot"></span> Campaign Channels</a>
        </div>
        <div class="nav-group">
          <div class="nav-title">Channels</div>
          <a class="nav-item" href="?view=overview&range=30d&embed=1&section=section-meta" data-view="overview" data-scroll="section-meta"><span class="nav-dot"></span> Meta Ads</a>
          <a class="nav-item" href="?view=overview&range=30d&embed=1&section=section-traffic&channel=google-ads" data-view="overview" data-scroll="section-traffic" data-channel="google-ads"><span class="nav-dot"></span> Google Ads</a>
          <a class="nav-item" href="?view=overview&range=30d&embed=1&section=section-traffic&channel=organic" data-view="overview" data-scroll="section-traffic" data-channel="organic"><span class="nav-dot"></span> Organic</a>
          <a class="nav-item" href="?view=overview&range=30d&embed=1&section=section-traffic&channel=email-sms" data-view="overview" data-scroll="section-traffic" data-channel="email-sms"><span class="nav-dot"></span> Email / SMS</a>
          <a class="nav-item" href="?view=overview&range=30d&embed=1&section=section-traffic&channel=linkedin" data-view="overview" data-scroll="section-traffic" data-channel="linkedin"><span class="nav-dot"></span> LinkedIn</a>
        </div>
        <div class="nav-group">
          <div class="nav-title">Integrations</div>
          <a class="nav-item" href="?view=overview&range=30d&embed=1&section=section-health" data-view="overview" data-scroll="section-health"><span class="nav-dot"></span> Source Health</a>
        </div>
      </aside>
      <main class="content">
        <div class="topbar" id="section-kpis">
          <div class="title-wrap">
            <h1>Executive Report</h1>
            <p id="subtitle">Loading...</p>
          </div>
          <div class="controls">
            <span class="build-badge" id="build-badge">build: pending</span>
            <a class="chip" href="?view=overview&range=7d&embed=1" data-range="7d">7d</a>
            <a class="chip active" href="?view=overview&range=30d&embed=1" data-range="30d">30d</a>
            <a class="chip" href="?view=overview&range=90d&embed=1" data-range="90d">90d</a>
          </div>
        </div>
        <form class="period-picker" id="period-picker">
          <label>Selected period<input type="date" id="period-from" aria-label="Selected period start date" required></label>
          <span style="color:var(--muted);padding-bottom:10px;">to</span>
          <label><span>&nbsp;</span><input type="date" id="period-to" aria-label="Selected period end date" required></label>
          <button class="button" type="submit">Apply period</button>
          <span class="period-note" id="period-note">Previous equal-length period will be compared automatically.</span>
        </form>
        <section class="panel" id="section-week-comparison" style="margin-bottom:16px;">
          <div class="panel-head">
            <h2>Week-on-Week Comparison</h2>
            <span id="comparison-period-label">Loading periods...</span>
          </div>
          <div class="panel-body">
            <div class="grid comparison-grid" id="comparison-grid">
              <div class="mini"><strong>New Contacts</strong><div id="wow-contacts">—</div><span class="delta" id="wow-contacts-delta">—</span></div>
              <div class="mini"><strong>Opps Created</strong><div id="wow-opportunities">—</div><span class="delta" id="wow-opportunities-delta">—</span></div>
              <div class="mini"><strong>Meetings</strong><div id="wow-meetings">—</div><span class="delta" id="wow-meetings-delta">—</span></div>
              <div class="mini"><strong>Closed Won</strong><div id="wow-closed-won">—</div><span class="delta" id="wow-closed-won-delta">—</span></div>
              <div class="mini"><strong>Email Opens</strong><div id="wow-email-opened">—</div><span class="delta" id="wow-email-opened-delta">—</span></div>
              <div class="mini"><strong>Email Clicks</strong><div id="wow-email-clicked">—</div><span class="delta" id="wow-email-clicked-delta">—</span></div>
              <div class="mini"><strong>LinkedIn DMs</strong><div id="wow-linkedin-dms">—</div><span class="delta" id="wow-linkedin-dms-delta">—</span></div>
              <div class="mini"><strong>LinkedIn Replies</strong><div id="wow-linkedin-replies">—</div><span class="delta" id="wow-linkedin-replies-delta">—</span></div>
            </div>
            <div class="footer-note">The selected period is compared with the immediately preceding period of equal length. Dates follow the reporting API window.</div>
          </div>
        </section>
        <section class="grid kpi-row" style="margin-bottom:16px;">
          <div class="kpi-card">
            <div class="label">Recorded Visits</div>
            <div class="value" id="kpi-sessions">—</div>
            <div class="sub" id="kpi-sessions-sub">GA4 recorded visits</div>
          </div>
          <div class="kpi-card">
            <div class="label">Contacts</div>
            <div class="value" id="kpi-contacts">—</div>
            <div class="sub">GHL</div>
          </div>
          <div class="kpi-card">
            <div class="label">Opps Created</div>
            <div class="value" id="kpi-opportunities">—</div>
            <div class="sub">GHL</div>
          </div>
          <div class="kpi-card">
            <div class="label">Meetings</div>
            <div class="value" id="kpi-meetings">—</div>
            <div class="sub">GHL</div>
          </div>
          <div class="kpi-card">
            <div class="label">Closed Won</div>
            <div class="value" id="kpi-closed-won">—</div>
            <div class="sub">GHL</div>
          </div>
          <div class="kpi-card">
            <div class="label">Revenue</div>
            <div class="value" id="kpi-revenue">—</div>
            <div class="sub">GHL</div>
          </div>
        </section>
         <details class="panel metric-glossary" style="margin-bottom:16px;">
           <summary class="panel-head">
             <h2>Metric Glossary</h2>
             <span>Definitions as shown</span>
           </summary>
          <div class="panel-body">
              <div class="definition-grid">
              <div class="definition-card">
                <strong>Traffic</strong>
                <p><b>Recorded visits</b> are the visits GA4 captured in the selected window. <b>Users</b> are unique visitors and are the primary denominator for the funnel cards below.</p>
              </div>
              <div class="definition-card">
                <strong>Lead Capture</strong>
                <p><b>Contacts</b> are GHL contacts created in the window from any source. Form metrics remain stored but are not shown here until tracking is validated.</p>
              </div>
              <div class="definition-card">
                <strong>Funnel Efficiency</strong>
                <p><b>User → Contact</b> shows how efficiently unique visitors become CRM contacts. Form conversion is not shown until form tracking is validated.</p>
              </div>
              <div class="definition-card">
                <strong>Attribution Coverage</strong>
                <p><b>Contacts Created in Window</b> are new contacts created in the window. <b>Source Coverage</b> means usable source fields exist, <b>Bridge Matched</b> means the contact was linked to a GA4 recorded visit, and <b>Sale Matched</b> means it was linked to an opportunity.</p>
              </div>
              <div class="definition-card">
                <strong>Acquisition Sources</strong>
                <p>This section shows contact-level source / medium / campaign attribution. It is the visible home for the dashboard's acquisition source view.</p>
              </div>
              <div class="definition-card">
                <strong>UTM / Campaign Breakdown</strong>
                <p>This table shows observed UTM traffic rows. A UTM created in GHL will only appear here once it is actually observed in traffic or matched through the bridge.</p>
              </div>
              <div class="definition-card">
                <strong>Sales Panels</strong>
                <p><b>Active Opportunities Summary</b> is the team-wide open-deal view. Duplicate deal panels are omitted so the same opportunity payload is not counted twice visually.</p>
              </div>
              <div class="definition-card">
                <strong>SDR Performance</strong>
                <p>Per-owner breakout for the end-of-month SDR assessment. <b>Booked</b> counts Regulated Ads calendar appointments (start date in the window) attributed to the SDR via appointment → contact → opportunity <b>assigned to</b>. <b>Showed / No-show / Cancelled</b> use the GHL appointment status saved on each record — status is not yet updated after meetings, so Showed stays 0 until the Phase-3 status-update automation. <b>SQLs Created</b> = Sales Outreach opportunities created in the window by owner. <b>MQL→SQL</b> = MQL opportunities that entered Sales Outreach in the window. <b>Won / Lost / Revenue</b> = closed opportunities created in the window by owner. Unassigned opportunities roll into an explicit Unassigned row; owner-coverage % is surfaced in Source Health.</p>
              </div>
              <div class="definition-card">
                <strong>Lead Source — MQL &amp; SQL</strong>
                <p>Breakout of MQLs Entered (Warm Qualified stage entries in the window) and SQLs Created (Sales Outreach opportunities created in the window) by the originating lead source. Each MQL/SQL opportunity is joined to its contact; the lead source is resolved from the contact's first UTM source/medium/campaign, falling back to the traffic-to-lead bridge attribution, then to the GHL contact source field. Coverage is bounded by the leads snapshot — rows without a resolvable source are grouped under <b>Unknown / Unattributed</b>, and the coverage note shows how many MQLs/SQLs were attributed in the window.</p>
              </div>
              <div class="definition-card">
                <strong>Calls &amp; Conversations</strong>
                <p>This panel shows GHL conversation call records. It groups calls by the raw CRM status so the team can see answered, missed, and voicemail activity without guessing from SMS or Twilio data.</p>
              </div>
              <div class="definition-card">
                <strong>Active Opportunities</strong>
                <p><b>Active Open</b> counts the latest opportunity snapshot whose status is still open as of the selected end date. It is not the same thing as opportunities created in the window.</p>
              </div>
              <div class="definition-card">
                <strong>Worked Opportunities</strong>
                <p><b>Worked</b> counts active opportunities that were updated or had a stage change inside the selected window. This is the closest dashboard proxy for deals that were definitely touched.</p>
              </div>
              <div class="definition-card">
                <strong>Stage Movers</strong>
                <p><b>Stage Movers</b> counts active opportunities that changed stage at least once inside the selected window. The stage lists below show where those open deals currently sit.</p>
              </div>
              <div class="definition-card">
                <strong>Social Posts</strong>
                <p><b>Post Placements</b> counts each platform/account destination in GHL Social Planner. One composed post published to Instagram and three LinkedIn accounts therefore counts as four placements. Likes, comments, and shares are the latest post-ledger values. Reach, impressions, and saves show N/A until authenticated account statistics are available.</p>
              </div>
              <div class="definition-card">
                <strong>Date Ranges</strong>
                <p><b>7d</b>, <b>30d</b>, and <b>90d</b> are trailing complete days ending yesterday. Example: clicking 7d on a Tuesday shows the previous Tuesday through Monday.</p>
              </div>
              <div class="definition-card">
                <strong>Channel Breakdown</strong>
                <p>This is the GA4 channel summary for the selected window. It is traffic volume, not contact volume.</p>
              </div>
            </div>
             <div class="footer-note">The glossary is the source of truth for how each visible card should be read. If a metric is not defined here, it should be treated as incomplete until the definition is added.</div>
           </div>
         </details>
        <div class="section-label" id="section-traffic">Traffic &amp; Channels</div>
        <section class="grid two-col" style="margin-bottom:16px;">
          <div class="panel">
            <div class="panel-head">
              <h2>Channel Breakdown</h2>
              <span>GA4</span>
            </div>
            <div class="panel-body">
              <div class="bar-list" id="channels-list"><div class="loading">Waiting for data...</div></div>
            </div>
          </div>
          <div class="panel">
            <div class="panel-head">
              <h2>Channel Detail</h2>
              <span>GA4 + GHL</span>
            </div>
            <div class="panel-body">
              <div class="mini-grid" id="channel-detail-grid"><div class="loading">Loading...</div></div>
            </div>
          </div>
        </section>
        <div class="section-label" id="section-meta">Meta Ads</div>
        <section class="grid two-col" style="margin-bottom:16px;">
          <div class="panel">
            <div class="panel-head">
              <h2>Meta Ads Overview</h2>
              <span>Meta Ads source data</span>
            </div>
            <div class="panel-body">
              <div class="mini-grid-4" id="meta-summary-grid">
                <div class="mini"><strong>Spend</strong><div id="meta-visits">—</div></div>
                <div class="mini"><strong>Clicks</strong><div id="meta-contacts">—</div></div>
                <div class="mini"><strong>Impressions</strong><div id="meta-opps">—</div></div>
                <div class="mini"><strong>Leads</strong><div id="meta-booked">—</div></div>
              </div>
              <div class="footer-note">Direct Meta Ads delivery metrics. GA4/GHL attribution remains available in the campaign and acquisition sections when UTM data is present.</div>
            </div>
          </div>
          <div class="panel">
            <div class="panel-head">
              <h2>Meta Campaign Performance</h2>
              <span>Meta Ads source data</span>
            </div>
            <div class="panel-body">
              <div class="bar-list" id="meta-campaign-list"><div class="loading">No Meta data yet...</div></div>
              <div class="footer-note">Ranked by Meta Ads spend for the selected window. Attribution from GA4/GHL is shown separately when available.</div>
            </div>
          </div>
        </section>
        <div class="section-label" id="section-acquisition">Acquisition Sources</div>
        <section class="grid two-col" style="margin-bottom:16px;">
          <div class="panel">
            <div class="panel-head">
              <h2>Contact Acquisition Sources</h2>
              <span>Attribution</span>
            </div>
            <div class="panel-body">
              <div class="bar-list" id="contact-sources-list"><div class="loading">Loading...</div></div>
              <div class="footer-note">Shows which sources brought in contacts. Campaign details enriched from GA4 bridge when contact-level UTM data is available.</div>
            </div>
          </div>
        </section>
        <div class="section-label" id="section-pages">Top Pages</div>
        <section class="grid" style="margin-bottom:16px;">
          <div class="panel">
            <div class="panel-head">
              <h2>Most Visited Pages</h2>
              <span>GA4 landing pages</span>
            </div>
            <div class="panel-body">
              <div class="bar-list" id="top-pages-list"><div class="loading">Loading page summary...</div></div>
              <div class="footer-note">This is a short page summary based on the landing-page rollup we already capture. It shows the pages that received the most recorded visits, plus form and opportunity activity when available.</div>
            </div>
          </div>
        </section>
        <div class="section-label" id="section-funnel">Funnel &amp; Attribution</div>
        <section class="grid two-col" style="margin-bottom:16px;">
          <div class="panel">
            <div class="panel-head">
              <h2>Funnel Efficiency</h2>
              <span>GHL + GA4</span>
            </div>
            <div class="panel-body">
              <div class="mini-grid" id="funnel-grid">
                <div class="mini"><strong>User → Contact</strong><div id="fn-session-to-contact">—</div></div>
                <div class="mini"><strong>Contact → Opp</strong><div id="fn-contact-to-opp">—</div></div>
                <div class="mini"><strong>Opp → Meeting</strong><div id="fn-opp-to-meeting">—</div></div>
                <div class="mini"><strong>Meeting → Won</strong><div id="fn-meeting-to-won">—</div></div>
                <div class="mini"><strong>Best Channel</strong><div id="fn-best-channel">—</div></div>
              </div>
              <div class="footer-note">Primary funnel cards use <b>Users</b> as the denominator. Session-based rates remain in the glossary for cross-checking.</div>
            </div>
          </div>
          <div class="panel">
            <div class="panel-head">
              <h2>Attribution Coverage</h2>
              <span>GHL Bridge</span>
            </div>
            <div class="panel-body">
              <div class="mini-grid" id="attribution-grid">
                <div class="mini"><strong>Contacts Created in Window</strong><div id="attr-cohort">—</div></div>
                <div class="mini"><strong>With Source Fields</strong><div id="attr-source">—</div></div>
                <div class="mini"><strong>Bridge Matched</strong><div id="attr-bridge">—</div></div>
                <div class="mini"><strong>Sale Matched</strong><div id="attr-sale">—</div></div>
                <div class="mini"><strong>Source Coverage</strong><div id="attr-source-rate">—</div></div>
                <div class="mini"><strong>Bridge Match Rate</strong><div id="attr-bridge-rate">—</div></div>
              </div>
              <div class="footer-note">Contacts created in window are the new contacts created in the selected window. Source coverage means the contact has usable source fields. Bridge matched means the contact was linked to a GA4 session. Sale matched means the contact was linked to an opportunity.</div>
            </div>
          </div>
        </section>
        <section class="grid" style="margin-bottom:16px;">
          <div class="panel">
            <div class="panel-head">
              <h2>Capture Gaps — Absolute Volume</h2>
              <span>GHL</span>
            </div>
            <div class="panel-body">
              <div class="mini-grid" id="capture-gaps-grid">
                <div class="mini"><strong>Recorded Visits</strong><div id="cg-sessions">—</div></div>
                <div class="mini"><strong>Contacts</strong><div id="cg-contacts">—</div></div>
                <div class="mini"><strong>Opportunities</strong><div id="cg-opportunities">—</div></div>
                <div class="mini"><strong>Meetings</strong><div id="cg-meetings">—</div></div>
                <div class="mini"><strong>Closed Won</strong><div id="cg-closed-won">—</div></div>
              </div>
              <div class="footer-note">Contacts are not strictly downstream of forms. They can also come from routed leads, manual CRM entry, imports, and follow-up conversions, so this block is absolute volume rather than a step-by-step funnel.</div>
            </div>
          </div>
        </section>
        <div class="section-label" id="section-sales">Sales &amp; Pipeline</div>
        <section class="grid two-col" style="margin-bottom:16px;">
          <div class="panel">
            <div class="panel-head">
              <h2>Pipeline Overview</h2>
              <span>GHL</span>
            </div>
            <div class="panel-body">
              <div class="mini-grid" id="pipeline-grid">
                <div class="mini"><strong>Warm</strong><div id="pipe-warm">—</div></div>
                <div class="mini"><strong>Sales Outreach</strong><div id="pipe-outreach">—</div></div>
                <div class="mini"><strong>Sales</strong><div id="pipe-sales">—</div></div>
              </div>
              <div class="divider"></div>
              <div class="bar-list" id="stage-movement-list"><div class="loading">Loading stage data...</div></div>
            </div>
          </div>
          <div class="panel">
            <div class="panel-head">
              <h2>Sales Quality</h2>
              <span>GHL</span>
            </div>
            <div class="panel-body">
              <div class="mini-grid" id="sales-quality-grid">
                <div class="mini"><strong>Avg. Cycle</strong><div id="sq-cycle">—</div></div>
                <div class="mini"><strong>Won Revenue</strong><div id="sq-revenue">—</div></div>
                <div class="mini"><strong>Won Deals</strong><div id="sq-won">—</div></div>
                <div class="mini"><strong>Lost Deals</strong><div id="sq-lost">—</div></div>
                <div class="mini"><strong>Win Rate</strong><div id="sq-win-rate">—</div></div>
                <div class="mini"><strong>Best Channel</strong><div id="sq-best-channel">—</div></div>
              </div>
              <div class="divider"></div>
              <div class="sub-head">Active Deals by Current Stage</div>
              <div class="bar-list" id="deal-stage-list"><div class="loading">Loading deal data...</div></div>
            </div>
          </div>
        </section>
        <section class="grid" style="margin-bottom:16px;">
          <div class="panel">
            <div class="panel-head">
              <h2>UTM / Campaign Breakdown</h2>
              <span>GA4 + GHL</span>
            </div>
            <div class="panel-body">
              <div class="bar-list" id="utm-list"><div class="loading">Waiting for UTM data...</div></div>
              <div class="footer-note">This is an observed traffic table, not a master list of every UTM created in GHL. Only rows that appear in traffic or bridge data can surface here.</div>
            </div>
          </div>
        </section>
        <div class="section-label" id="section-contracts">Contracts &amp; Deals</div>
        <section class="grid two-col" style="margin-bottom:16px;">
          <div class="panel">
            <div class="panel-head">
              <h2>Active Opportunities Summary</h2>
              <span>GHL</span>
            </div>
            <div class="panel-body" id="sales-team-panel">
              <div class="mini-grid" id="sales-team-grid">
                <div class="mini"><strong>Active Open</strong><div id="st-total-opps">—</div></div>
                <div class="mini"><strong>Worked</strong><div id="st-worked-opps">—</div></div>
                <div class="mini"><strong>Stage Movers</strong><div id="st-stage-movers">—</div></div>
                <div class="mini"><strong>Pipeline Value</strong><div id="st-pipeline-value">—</div></div>
              </div>
              <div class="footer-note">Team totals use the latest open opportunity snapshot as of the selected end date. Worked means the opportunity updated or moved stage inside the selected window.</div>
            </div>
          </div>
        </section>
        <div class="section-label" id="section-john">Sales Detail</div>
        <section class="grid two-col" style="margin-bottom:16px;">
          <div class="panel">
            <div class="panel-head">
              <h2>Meetings (Cameron's Calendar)</h2>
              <span>GHL Appointments</span>
            </div>
            <div class="panel-body">
              <div class="mini-grid" id="appointments-grid" style="margin-bottom:12px;">
                <div class="mini"><strong>Total</strong><div id="appointments-total">—</div></div>
                <div class="mini"><strong>Showed</strong><div id="appointments-showed">—</div></div>
                <div class="mini"><strong>No-show</strong><div id="appointments-noshow">—</div></div>
                <div class="mini"><strong>Cancelled</strong><div id="appointments-cancelled">—</div></div>
              </div>
              <div class="bar-list" id="appointments-list"><div class="loading">Loading appointment data...</div></div>
              <div class="footer-note">Appointments from calendar SrtXcFVyea7pFl3nTiIK — Regulated Ads On Social/Search. The status counts below come from the current GHL appointment status saved on each record. Call activity is shown separately in the Calls &amp; Conversations section.</div>
            </div>
          </div>
        </section>
        <div class="section-label" id="section-sdr">SDR Performance</div>
        <section class="grid" style="margin-bottom:16px;">
          <div class="panel">
            <div class="panel-head">
              <h2>SDR Performance</h2>
              <span>GHL owner attribution</span>
            </div>
            <div class="panel-body">
              <div class="table-scroll">
                <table class="campaign-table">
                  <thead><tr><th>SDR</th><th>Booked</th><th>Showed</th><th>No-show</th><th>Cancelled</th><th>SQLs Created</th><th>MQL→SQL</th><th>Won</th><th>Lost</th><th>Revenue</th></tr></thead>
                  <tbody id="sdr-performance-table"><tr><td colspan="10" class="loading">Loading SDR performance data...</td></tr></tbody>
                </table>
              </div>
              <div class="footer-note">Owner = native opportunity "assigned to" (contact-owner fallback). Booked meetings are Regulated Ads calendar appointments windowed by start date, attributed to the SDR via appointment → contact → opportunity owner. Unassigned opportunities roll into an explicit Unassigned row; owner-coverage % is shown in Source Health.</div>
            </div>
          </div>
        </section>
        <div class="section-label" id="section-lead-source">Lead Source</div>
        <section class="grid" style="margin-bottom:16px;">
          <div class="panel">
            <div class="panel-head">
              <h2>Lead Source — MQL &amp; SQL</h2>
              <span>What is working</span>
            </div>
            <div class="panel-body">
              <div class="table-scroll">
                <table class="campaign-table">
                  <thead><tr><th>Lead Source</th><th>Medium</th><th>MQLs Entered</th><th>SQLs Created</th></tr></thead>
                  <tbody id="lead-source-table"><tr><td colspan="4" class="loading">Loading lead source data...</td></tr></tbody>
                </table>
              </div>
              <div class="footer-note" id="lead-source-note">MQLs Entered = Warm Qualified (MQL) opportunities that entered the stage in the window. SQLs Created = Sales Outreach opportunities created in the window. Lead source resolved from the contact's first UTM source (medium/campaign), falling back to the traffic-to-lead bridge, then to the GHL contact source field. Coverage is limited by the leads snapshot — unattributed rows are labelled "Unknown / Unattributed".</div>
            </div>
          </div>
        </section>
        <div class="section-label" id="section-calls">Calls &amp; Conversations</div>
        <section class="grid" style="margin-bottom:16px;">
          <div class="panel">
            <div class="panel-head">
              <h2>GHL Calls</h2>
              <span>Conversations</span>
            </div>
            <div class="panel-body">
              <div class="mini-grid" id="calls-grid">
                <div class="mini"><strong>Total Calls</strong><div id="calls-total">—</div></div>
                <div class="mini"><strong>Answered</strong><div id="calls-answered">—</div></div>
                <div class="mini"><strong>Missed</strong><div id="calls-missed">—</div></div>
                <div class="mini"><strong>Voicemail</strong><div id="calls-voicemail">—</div></div>
                <div class="mini"><strong>Inbound</strong><div id="calls-inbound">—</div></div>
                <div class="mini"><strong>Outbound</strong><div id="calls-outbound">—</div></div>
              </div>
              <div class="divider"></div>
              <div class="bar-list" id="call-status-list"><div class="loading">Loading call data...</div></div>
              <div class="divider"></div>
              <div class="sub-head">Outbound Call Outcomes</div>
              <div class="bar-list" id="call-outcome-list"><div class="loading">Loading call outcome data...</div></div>
               <div hidden>
               <div class="divider"></div>
               <div class="sub-head">Vapi Queue Timezones</div>
               <div class="mini-grid" id="vapi-timezone-grid" style="margin-bottom:12px;">
                <div class="mini"><strong>Total Queued</strong><div id="vapi-tz-total">—</div></div>
                <div class="mini"><strong>Explicit</strong><div id="vapi-tz-explicit">—</div></div>
                <div class="mini"><strong>Inferred</strong><div id="vapi-tz-inferred">—</div></div>
                <div class="mini"><strong>None</strong><div id="vapi-tz-none">—</div></div>
              </div>
              <div class="footer-note">These buckets are derived from the queue table plus the cached contact snapshot. Explicit means the contact already carried a timezone; inferred means the workflow resolved one from location data; none means the queue row still lacks a usable timezone.</div>
              <div class="divider"></div>
              <div class="sub-head">Vapi Last 7 Days</div>
              <div class="mini-grid" id="vapi-weekly-grid" style="margin-bottom:12px;">
                <div class="mini"><strong>Attempts</strong><div id="vapi-weekly-total">—</div></div>
                <div class="mini"><strong>Answered</strong><div id="vapi-weekly-answered">—</div></div>
                <div class="mini"><strong>Missed</strong><div id="vapi-weekly-missed">—</div></div>
                <div class="mini"><strong>Qualified</strong><div id="vapi-weekly-qualified">—</div></div>
                <div class="mini"><strong>Voicemail</strong><div id="vapi-weekly-voicemail">—</div></div>
                <div class="mini"><strong>Handoff</strong><div id="vapi-weekly-handoff">—</div></div>
              </div>
              <div class="bar-list" id="vapi-weekly-breakdown-list"><div class="loading">Loading Vapi weekly data...</div></div>
              <div class="footer-note">This is a trailing selected-range rollup from <code>voice_call_attempt</code>. Attempts may include repeat calls to the same contact; answered counts live contacts; qualified is the strongest intent signal we currently store; handoff counts calls that requested a sales follow-up.</div>
               <div class="footer-note">Calls are read from GHL Conversations. Status groups use the raw CRM status plus answered timestamp so the report reflects what the CRM actually stores.</div>
               </div>
            </div>
          </div>
         </section>
         <div class="section-label" id="section-campaigns">Campaign Channels</div>
         <section class="grid" style="margin-bottom:16px;">
           <div class="panel">
              <div class="panel-head">
                 <h2>Campaign Channels</h2>
                  <span>Email + LinkedIn + Instagram + SMS + VAPI</span>
              </div>
              <div class="panel-body">
                 <div class="campaign-filters" aria-label="Campaign channel filters">
                   <button class="chip active" type="button" data-campaign-channel="all">All campaigns</button>
                   <button class="chip" type="button" data-campaign-channel="email">Email</button>
                    <button class="chip" type="button" data-campaign-channel="linkedin">LinkedIn</button>
                    <button class="chip" type="button" data-campaign-channel="instagram">Instagram</button>
                   <button class="chip" type="button" data-campaign-channel="sms">SMS</button>
                   <button class="chip" type="button" data-campaign-channel="vapi">VAPI</button>
                 </div>
                 <div class="campaign-filters" aria-label="Campaign name filters" style="margin-bottom:14px;">
                   <button class="chip active" type="button" data-campaign-name="all">All</button>
                   <button class="chip" type="button" data-campaign-name="DAN">DAN</button>
                   <button class="chip" type="button" data-campaign-name="Emerald">Emerald</button>
                    <button class="chip" type="button" data-campaign-name="Partnership">Partnership</button>
                    <button class="chip" type="button" data-campaign-name="Instagram">Instagram</button>
                   <button class="chip" type="button" data-campaign-name="Vapi Brand">Vapi Brand</button>
                    <button class="chip" type="button" data-campaign-name="Vapi Dispensary">Vapi Dispensary</button>
                  </div>
                  <div id="sms-summary" class="footer-note" style="margin:0 0 6px;">SMS delivery summary: loading...</div>
                  <div id="instagram-summary" class="footer-note" style="margin:0 0 12px;">Instagram activity: loading...</div>
                 <div class="table-scroll">
                 <table class="campaign-table">
                       <thead><tr><th>Channel</th><th>Campaign</th><th>SMS Sent</th><th>SMS Replies</th><th>Tracked Delivered</th><th>Unique Opens</th><th>Unique Open Rate</th><th>Unique Clickers</th><th>Unique Click Rate</th><th>Unique Replies</th><th>Unique Response Rate</th><th>Bounced</th><th>LI Invites</th><th>LI Accepted</th><th>LI DMs</th><th>LI Replies</th><th>IG DMs</th><th>IG Replies</th><th>VAPI Calls</th><th>Answered</th><th>Qualified</th><th>Booked</th></tr></thead>
                      <tbody id="campaign-channel-table"><tr><td colspan="22" class="loading">Loading campaign channel data...</td></tr></tbody>
                 </table>
               </div>
                 <div class="footer-note">Date range follows the report selector. This is the tracked campaign view, not all GHL Workflow Campaign activity. Tracked Delivered is an interim recipient-level approximation: tracked recipients minus tracked bounces. Opens, clicks, bounces, and replies are distinct contacts in the selected window. Exact GHL delivered-email rates require the GHL Email Statistics source. DAN, Emerald, and Partnership rows use enrollment/release attribution; SMS uses campaign keys; LinkedIn and Instagram use durable activity ledgers. Older events without campaign metadata remain unattributed.</div>
              </div>
            </div>
            <div class="panel">
                    <div class="panel-head">
                    <h2>Campaign Breakdown</h2>
                    <div style="display:flex;align-items:center;gap:8px;">
                      <span>Email + LinkedIn + Instagram + SMS + VAPI by campaign</span>
                     <button class="chip active" type="button" id="cmp-view-list" data-campaign-view="list" style="padding:4px 8px;font-size:0.7rem;">List</button>
                     <button class="chip" type="button" id="cmp-view-compare" data-campaign-view="compare" style="padding:4px 8px;font-size:0.7rem;">Compare</button>
                   </div>
                </div>
               <div class="panel-body">
                <div class="table-scroll">
                 <table class="campaign-table">
                       <thead><tr><th>Campaign</th><th>Opportunities</th><th>Tracked Delivered</th><th>Unique Opens</th><th>Unique Open Rate</th><th>Unique Clickers</th><th>Unique Click Rate</th><th>Unique Replies</th><th>Bounced</th><th>LI Invites</th><th>LI Accepted</th><th>LI DMs</th><th>LI Replies</th><th>IG DMs</th><th>IG Replies</th><th>SMS Sent</th><th>SMS Replies</th><th>VAPI Calls</th><th>Answered</th><th>Qualified</th><th>Booked</th></tr></thead>
                       <tbody id="campaign-breakdown-table"><tr><td colspan="21" class="loading">Loading campaign breakdown...</td></tr></tbody>
                 </table>
                </div>
                    <div class="footer-note">Rolls DAN, Partnership, Emerald, and Vapi activity into one row per campaign. Email rates use tracked delivered recipients, approximated as tracked recipients minus tracked bounces; they are not the exact GHL Email Statistics rates. Opportunities use distinct selected-window opportunity IDs matched to current campaign tags; Vapi Brand and Vapi Dispensary remain separate from DAN.</div>
                 </div>
                 <div id="campaign-compare-view" style="display:none;">
                   <div class="table-scroll">
                    <table class="campaign-table" id="campaign-compare-table">
                      <thead id="campaign-compare-head"></thead>
                      <tbody id="campaign-compare-body"><tr><td colspan="20" class="loading">No comparison data yet.</td></tr></tbody>
                    </table>
                   </div>
                   <div class="footer-note">Side-by-side comparison of all active campaigns. Each campaign is a column; metrics are rows.</div>
                 </div>
                 <div id="campaign-detail-container" class="campaign-detail-panel" style="display:none;"></div>
            </div>
            <div class="panel">
              <div class="panel-head">
                <h2>MQL &amp; LinkedIn State Snapshot</h2>
               <span>Current CRM state</span>
             </div>
<div class="panel-body">
                <div class="sub-head" style="margin-bottom:8px;">MQL</div>
                <div class="mini-grid-4">
                  <div class="mini"><strong>Total MQLs</strong><div id="snapshot-mql-total">—</div></div>
                  <div class="mini"><strong>MQLs Converted to SQL</strong><div id="snapshot-mql-converted">—</div></div>
                  <div class="mini"><strong>Current MQLs (awaiting Sales)</strong><div id="snapshot-mql-current">—</div></div>
                  <div class="mini"><strong>SQL Contacts</strong><div id="snapshot-sql">—</div></div>
                </div>
                <div class="mini-grid-4" style="margin-top:12px;">
                  <div class="mini"><strong>Entered MQLs This Period</strong><div id="snapshot-mql-entered">—</div></div>
                  <div class="mini"><strong>Converted This Period</strong><div id="snapshot-mql-conv-period">—</div></div>
                </div>
                <div class="sub-head" style="margin:16px 0 8px;">LinkedIn State</div>
                <div class="mini-grid-4">
                  <div class="mini"><strong>LinkedIn Ready</strong><div id="snapshot-li-ready">—</div></div>
                  <div class="mini"><strong>LinkedIn Requested</strong><div id="snapshot-li-requested">—</div></div>
                  <div class="mini"><strong>LinkedIn Connected</strong><div id="snapshot-li-connected">—</div></div>
                  <div class="mini"><strong>Follower Messaged</strong><div id="snapshot-li-follower-messaged">—</div></div>
                  <div class="mini"><strong>LinkedIn DM Active</strong><div id="snapshot-li-active">—</div></div>
                  <div class="mini"><strong>LinkedIn DM Completed</strong><div id="snapshot-li-completed">—</div></div>
                  <div class="mini"><strong>Total State Rows</strong><div id="snapshot-li-total">—</div></div>
                </div>
                <div class="mini-grid-4" style="margin-top:12px;">
                  <div class="mini"><strong>Weekly Requests</strong><div id="linkedin-weekly-requests">—</div></div>
                  <div class="mini"><strong>Weekly Accepts</strong><div id="linkedin-weekly-accepts">—</div></div>
                  <div class="mini"><strong>Weekly DMs Sent</strong><div id="linkedin-weekly-dms">—</div></div>
                  <div class="mini"><strong>Weekly Replies</strong><div id="linkedin-weekly-replies">—</div></div>
                </div>
                 <div class="footer-note">Total MQLs are opportunities that ever reached the Warm pipeline Qualified (MQL) stage. Converted to SQL means the opportunity also entered the Sales Outreach pipeline; Current MQLs are still sitting in Warm without a Sales Outreach record. A Converted MQL is no longer counted as Current. The snapshot values are cumulative; Entered/Converted This Period follow the selected reporting range. LinkedIn state values are current snapshots; activity follows the selected period from the LinkedIn activity ledger.</div>
             </div>
           </div>
         </section>
        <div class="section-label" id="section-chella">Social &amp; Site</div>
        <section class="grid two-col" style="margin-bottom:16px;">
          <div class="panel">
            <div class="panel-head">
              <h2>Social Posts</h2>
              <span>GHL Social Planner</span>
            </div>
            <div class="panel-body">
              <div class="mini-grid" id="social-posts-grid">
                <div class="mini"><strong>Post Placements</strong><div id="sp-total">—</div></div>
                <div class="mini"><strong>Published Placements</strong><div id="sp-published">—</div></div>
                <div class="mini"><strong>Failed</strong><div id="sp-failed">—</div></div>
                 <div class="mini"><strong>Facebook</strong><div id="sp-fb">—</div></div>
                 <div class="mini"><strong>Instagram</strong><div id="sp-ig">—</div></div>
                 <div class="mini"><strong>LinkedIn</strong><div id="sp-li">—</div></div>
                  <div class="mini"><strong>Ledger Likes</strong><div id="sp-likes">—</div></div>
                  <div class="mini"><strong>Ledger Comments</strong><div id="sp-comments">—</div></div>
                  <div class="mini"><strong>Ledger Shares</strong><div id="sp-shares">—</div></div>
<div class="mini"><strong>Account Reach</strong><div id="sp-reach">—</div></div>
                  <div class="mini"><strong>Account Impressions</strong><div id="sp-impressions">—</div></div>
                  <div class="mini"><strong>Account Posts</strong><div id="sp-account-posts">—</div></div>
                  <div class="mini"><strong>Account Likes</strong><div id="sp-account-likes">—</div></div>
                  <div class="mini"><strong>Account Followers</strong><div id="sp-account-followers">—</div></div>
               </div>
                 <div class="footer-note">Counts are platform/account placements from the selected period, not unique composer posts. Failed means the latest placement status is failed or error. Likes, comments, and shares come from the post ledger. Reach, impressions, posts, likes, and followers are GHL Social Planner account statistics for the selected window; Saves stays N/A because the statistics source does not return saves.</div>
            </div>
          </div>
          <div class="panel">
            <div class="panel-head">
              <h2>Site Traffic</h2>
              <span>GA4</span>
            </div>
            <div class="panel-body">
              <div class="mini-grid" id="site-traffic-grid">
                <div class="mini"><strong>Recorded Visits</strong><div id="st-sessions">—</div></div>
                <div class="mini"><strong>Users</strong><div id="st-users">—</div></div>
                <div class="mini"><strong>Engaged</strong><div id="st-engaged">—</div></div>
                <div class="mini"><strong>Top Page</strong><div id="st-top-page">—</div></div>
                <div class="mini"><strong>Eng. Rate</strong><div id="st-eng-rate">—</div></div>
              </div>
              <div class="footer-note">GA4 website traffic and engagement. Social engagement (reactions/comments/shares) tracked via GHL Social Planner posts.</div>
            </div>
          </div>
        </section>
        <div class="section-label" id="section-health">Integrations</div>
        <section class="grid" style="margin-bottom:16px;">
          <div class="panel">
            <div class="panel-head">
              <h2>Source Health</h2>
                <span>Runtime, pipeline, and snapshot freshness</span>
            </div>
            <div class="panel-body">
              <div class="mini-grid" id="health-grid">
                <div class="mini"><strong>GHL</strong><div id="hl-ghl">—</div></div>
                <div class="mini"><strong>GA4</strong><div id="hl-ga4">—</div></div>
                <div class="mini"><strong>n8n</strong><div id="hl-n8n">—</div></div>
                <div class="mini"><strong>Postgres</strong><div id="hl-postgres">—</div></div>
                <div class="mini"><strong>GSC</strong><div id="hl-gsc">Pending</div></div>
                <div class="mini"><strong>Appointments</strong><div id="hl-calls">Pending</div></div>
                <div class="mini"><strong>Meta Ads</strong><div id="hl-meta">Pending</div></div>
              </div>
              <div class="footer-note">Green = last sync within 48h. Amber = 48-96h. Red = &gt;96h or failed.</div>
            </div>
          </div>
        </section>
         <div class="section-label" id="section-gsc" hidden>Search Console</div>
         <section class="grid" style="margin-bottom:16px; display:none;">
          <div class="panel">
            <div class="panel-head">
              <h2>GSC Search</h2>
              <span>Google Search Console</span>
            </div>
            <div class="panel-body">
              <div class="mini-grid" id="gsc-grid">
                <div class="mini"><strong>Clicks</strong><div id="gsc-clicks">—</div></div>
                <div class="mini"><strong>Impressions</strong><div id="gsc-impressions">—</div></div>
                <div class="mini"><strong>Est. Unique Visitors</strong><div id="gsc-unique-visitors">—</div></div>
                <div class="mini"><strong>CTR</strong><div id="gsc-ctr">—</div></div>
                <div class="mini"><strong>Avg Position</strong><div id="gsc-position">—</div></div>
              </div>
              <div class="footer-note">Estimated unique visitors uses GA4 Organic Search users as a proxy. Google Search Console metrics are still rolled up from the raw GSC query table into the summary payload. Query and page detail stays in the dedicated GSC workflow.</div>
            </div>
          </div>
         </section>
       </main>
    </div>
    <script>
      (function () {
           var BUILD_STAMP = "2026-09-19-v34-hide-outgoing-calls";
        // Pipeline and stage name map (GHL LiveTransparent location Zwz4relUXVPxx8uohnjV)
        var PIPELINE_NAMES = {
          "FRjpDZ1HWj3UPgczsu3t": "Warm",
          "dhdlf3O4tymxFtHk4aqq": "Sales Outreach",
          "MThKauqlvnEFuFmAkyWX": "Sales",
          "tQkFYrHjALgoLz6oq0uz": "Partnership"
        };
        var STAGE_NAMES = {
          "b961de1f-34fd-4b66-b032-f21225654868": "New",
          "67d47ef7-73af-44db-9061-a1acfe65d142": "New_Not Qualified",
          "3b3bd98d-cbb9-4c50-8cf3-b4eba29061c2": "Qualified (MQL)",
          "477c0b59-4a64-4566-81d6-63e233362520": "Routed to Outreach",
          "98775f02-0018-4629-9e69-0b1fcab293eb": "Nurture Active",
          "dae2ddc5-a031-4ffa-bcdb-79d5c9afe91b": "Disqualified",
          "0741e8b5-bab0-4500-a8f6-34fbfec6cf7e": "Vapi Voicemail",
          "967292f9-aba0-416e-9723-5d2aa9719eaa": "Vapi Nurture",
          "16fb26a2-736c-498d-be91-6a94633146f9": "Vapi Qualified",
          "3529dd3d-cab0-4279-967c-1aea203de4fb": "New",
          "b97e42b1-b4c2-4759-8212-33596a085cf2": "Attempting Contact 1st Attempt",
          "c46c3be3-a216-4489-8ae3-c4284cfc747f": "2nd attempt",
          "c8b7a450-462a-497d-ab86-65f9a8e9b082": "3rd attempt",
          "9ced8010-dfd7-4d5b-aa9c-c2eb58fca94d": "Engaged",
          "1ab47457-c945-4d16-9dd7-305583823114": "Meeting Requested",
          "1f95dd0a-1cf2-4d31-abad-825d97d3ef69": "Booked",
          "23276991-fbb3-4b0f-8d65-35c737b62bdd": "Unresponsive",
          "5112b5c8-efe5-48f5-b90b-29b3e28a7a3e": "Discovery No Shows for Rescheduling",
          "6f5aa304-a190-40da-8556-7c65bbc52733": "Discovery Scheduled",
          "facd3d31-c634-40c5-9271-17d608b4379c": "Discovery Completed",
          "42b12e59-9b51-4c82-b597-4a9c972322c9": "Proposal Sent",
          "f9022c83-7791-45c9-903d-381668454b2f": "Negotiation",
          "f6b65baa-eac8-4f02-b91e-2ab0c8841b2d": "Closed Won",
          "d7784617-96f4-4ae4-8b3e-e2088b62627d": "Closed Lost",
          "268ed432-ce29-42a6-81a1-bb85617db575": "Discovery No Shows",
          "91517911-3eee-45a0-b432-e36209495c16": "Qualified",
          "ccc3d423-ff86-46b4-bd53-064458910eba": "New Partner Lead",
          "7c666a65-7497-4b20-a5a1-ab3c64934b1a": "Contacted",
          "2b378529-219e-4185-8871-a1d0b09459bb": "Proposal Sent",
          "91ab7c92-7705-41f0-a192-d94626269329": "Closed"
        };
        function resolvePipeline(id) { return PIPELINE_NAMES[id] || id; }
        function resolveStage(id) { return STAGE_NAMES[id] || id; }
        var params = new URLSearchParams(window.location.search);
        var view = params.get("view") || "overview";
         var validRanges = ["7d", "30d", "90d", "custom"];
         var range = validRanges.indexOf(params.get("range")) >= 0 ? params.get("range") : "30d";
         var from = params.get("from");
         var to = params.get("to");
         if (from && to) range = "custom";
        var section = params.get("section") || "";
        var channel = params.get("channel") || "";
        var subtitle = document.getElementById("subtitle");
        var buildBadge = document.getElementById("build-badge");
        var rangeButtons = Array.from(document.querySelectorAll("[data-range]"));
        var sidebarButtons = Array.from(document.querySelectorAll(".nav-item[data-view]"));
        var parts = [];
        if (view) parts.push(view.charAt(0).toUpperCase() + view.slice(1));
         if (range) parts.push(range === "custom" ? "custom period" : range);
         if (from && to) parts.push(from + " to " + to);
         parts.push("Sources: GHL, GA4, Meta attribution");
         if (!from || !to) parts.push("Preset windows: trailing complete days ending yesterday");
        subtitle.textContent = parts.join(" \u00b7 ") || "Loading...";
        if (buildBadge) buildBadge.textContent = "build: " + BUILD_STAMP;
        function formatNumber(value, digits) {
          if (digits === undefined) digits = 0;
          var num = Number(value);
          if (!Number.isFinite(num)) return "0";
          return new Intl.NumberFormat("en-US", { maximumFractionDigits: digits, minimumFractionDigits: digits > 0 ? digits : 0 }).format(num);
        }
         function formatPercent(value) {
           var num = Number(value);
           if (!Number.isFinite(num)) return "0%";
           var pct = num <= 1 ? num * 100 : num;
           return pct.toFixed(pct >= 10 ? 0 : 1) + "%";
         }
         function formatCampaignPercent(value) {
           var num = Number(value);
           if (!Number.isFinite(num)) return "0%";
           var pct = num <= 1 ? num * 100 : num;
           return pct.toFixed(pct >= 10 ? 0 : 2) + "%";
         }
         function formatCurrency(value) {
           var num = Number(value);
           if (!Number.isFinite(num)) return "$0";
           return "$" + new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(num);
         }
         function normalizeLandingPage(value) {
           var page = String(value || "").trim();
           if (!page) return "/";
           page = page.replace(/^https?:\/\/[^\/]+/i, "");
           page = page.split(/[?#]/)[0] || "/";
           try { page = decodeURIComponent(page); } catch (_) {}
           return page || "/";
         }
        function setActiveRange(nextRange) {
          rangeButtons.forEach(function (btn) { btn.classList.toggle("active", btn.dataset.range === nextRange); });
        }
        function buildUrl(opts) {
          var o = opts || {};
          var nv = o.nextView !== undefined ? o.nextView : view || "overview";
          var nr = o.nextRange !== undefined ? o.nextRange : range || "30d";
          var ns = o.nextSection !== undefined ? o.nextSection : section || "";
          var nc = o.nextChannel !== undefined ? o.nextChannel : channel || "";
          var next = new URL(window.location.href);
           next.searchParams.set("view", nv);
           next.searchParams.set("range", nr);
           next.searchParams.set("embed", "1");
           if (nr === "custom" && from && to) {
             next.searchParams.set("from", from);
             next.searchParams.set("to", to);
           } else {
             next.searchParams.delete("from");
             next.searchParams.delete("to");
           }
          if (ns) next.searchParams.set("section", ns); else next.searchParams.delete("section");
          if (nc) next.searchParams.set("channel", nc); else next.searchParams.delete("channel");
          return next.toString();
        }
        function scrollToSection(s) {
          if (!s) return;
          var t = document.querySelector(s.startsWith("#") ? s : "#" + s);
          if (t) t.scrollIntoView({ behavior: "smooth", block: "start" });
        }
        function syncNavLinks() {
          rangeButtons.forEach(function (btn) {
            btn.setAttribute("href", buildUrl({ nextRange: btn.dataset.range || "30d", nextSection: "", nextChannel: "" }));
          });
          sidebarButtons.forEach(function (btn) {
            btn.setAttribute("href", buildUrl({
              nextView: btn.dataset.view || "overview",
              nextRange: range || "30d",
              nextSection: String(btn.dataset.scroll || "").replace(/^#/, ""),
              nextChannel: btn.dataset.channel || ""
            }));
          });
        }
        function setActiveSidebar(s) {
          var ns = String(s || "").trim().toLowerCase();
          var nv = String(view || "overview").trim().toLowerCase();
          sidebarButtons.forEach(function (btn) {
            var bv = String(btn.dataset.view || "").trim().toLowerCase();
            var bs = String((btn.dataset.scroll || "").replace(/^#/, "") || "").trim().toLowerCase();
            var isRoot = !ns || ns === "section-kpis" || ns === "overview";
            var isActive = bv === nv && ((isRoot && (bs === "section-kpis" || bs === "overview" || bs === "")));
            btn.classList.toggle("active", isActive);
          });
        }
        function renderBars(container, items, emptyLabel) {
          if (!container) return;
          if (!Array.isArray(items) || items.length === 0) {
            container.innerHTML = "<div class=\"loading\">" + (emptyLabel || "No data") + "</div>"; return;
          }
          var max = Math.max(1, ...items.map(function (i) { return Number(i.sessions || i.value || 0); }));
          container.innerHTML = items.map(function (i) {
            var label = i.label || i.channel || i.pipeline || i.stage || "?";
            var value = Number(i.sessions || i.value || i.leads || 0);
            var width = Math.max(3, Math.round((value / max) * 100));
            var sub = i.sub ? "<span style=\"color:var(--faint);font-size:0.75rem;margin-left:6px;\">" + i.sub + "</span>" : "";
            return "<div class=\"bar-item\"><div class=\"bar-label\">" + label + sub + "</div><div class=\"bar-track\"><div class=\"bar-fill\" style=\"--w:" + width + "%;--c1:var(--blue);--c2:var(--purple);\"></div></div><div class=\"bar-value\">" + formatNumber(value) + "</div></div>";
          }).join("");
        }
         function renderMiniGrid(container, items, fallbackItems) {
          if (!container) return;
          if (!Array.isArray(items) || items.length === 0) {
            if (fallbackItems) container.innerHTML = fallbackItems.map(function (i) {
              return "<div class=\"mini\"><strong>" + i.label + "</strong><div>" + i.value + "</div></div>";
            }).join("");
            return;
          }
          container.innerHTML = items.map(function (i) {
            return "<div class=\"mini\"><strong>" + i.label + "</strong><div>" + i.value + "</div></div>";
          }).join("");
        }
        function isMetaAttributedRow(item) {
          var haystack = [item && (item.source || item.medium || item.campaign || item.content || item.term || item.landingPage || item.landing_page || "")].join(" ").toLowerCase();
          if (!haystack) return false;
          return ["facebook", "instagram", "meta", "fb", "ig", "an", "adsmanager", "utm_id=", "utm_source=an"].some(function (n) { return haystack.includes(n); });
        }
        function renderMetaAttribution(data) {
          var rows = Array.isArray(data.utmBreakdown) ? data.utmBreakdown.filter(isMetaAttributedRow) : [];
          var contacts = Array.isArray(data.metaAttribution) ? data.metaAttribution : [];
          var raw = data.metaAdsOverview || {};
          var rawCampaigns = Array.isArray(raw.campaigns) ? raw.campaigns : [];
          var hasRaw = Number(raw.impressions || 0) > 0 || Number(raw.clicks || 0) > 0 || Number(raw.spend || 0) > 0 || Number(raw.leads || 0) > 0;
          var totalVisits = rows.reduce(function (acc, i) { return acc + Number(i.sessions || 0); }, 0);
          var totalContacts = contacts.reduce(function (acc, i) { return acc + Number(i.contacts || 0); }, 0);
          var totalOpps = contacts.reduce(function (acc, i) { return acc + Number(i.opportunities || 0); }, 0);
          var totalBooked = contacts.reduce(function (acc, i) { return acc + Number(i.bookedContacts || 0); }, 0);
          var el;
          el = document.getElementById("meta-visits"); if (el) el.textContent = hasRaw ? formatCurrency(raw.spend || 0) : formatNumber(totalVisits);
          el = document.getElementById("meta-contacts"); if (el) el.textContent = hasRaw ? formatNumber(raw.clicks || 0) : formatNumber(totalContacts);
          el = document.getElementById("meta-opps"); if (el) el.textContent = hasRaw ? formatNumber(raw.impressions || 0) : formatNumber(totalOpps);
          el = document.getElementById("meta-booked"); if (el) el.textContent = hasRaw ? formatNumber(raw.leads || 0) : formatNumber(totalBooked);
          renderBars(document.getElementById("meta-campaign-list"), hasRaw ? rawCampaigns.map(function (i) {
            return { label: i.campaign || "Unknown", sessions: Number(i.spend || 0), sub: "spend:" + formatCurrency(i.spend || 0) + " clicks:" + formatNumber(i.clicks || 0) + " impressions:" + formatNumber(i.impressions || 0) + " leads:" + formatNumber(i.leads || 0) };
          }) : contacts.slice(0, 12).map(function (i) {
            var label = (i.campaign && i.campaign !== "unknown") ? i.campaign : (i.source || "Meta");
            if (i.medium && i.medium !== "unknown") label += " (" + i.medium + ")";
            return { label: label, sessions: i.contacts || 0, sub: "contacts:" + formatNumber(i.contacts || 0) + " opps:" + formatNumber(i.opportunities || 0) + " booked:" + formatNumber(i.bookedContacts || 0) };
          }), hasRaw ? "No Meta Ads delivery data in this window." : "No Meta-attributed contacts in this window.");
        }
        function renderContactSources(data) {
          var sources = Array.isArray(data.contactSources) ? data.contactSources : [];
          var metaSources = Array.isArray(data.metaAttribution) ? data.metaAttribution : [];
          if (sources.length === 0 && metaSources.length > 0) {
            sources = metaSources.map(function (i) {
              return { source: i.source || "Meta", medium: i.medium || "", campaign: (i.campaign !== "unknown" ? i.campaign : "") || "", contacts: i.contacts || 0, opportunities: i.opportunities || 0 };
            });
          }
          if (sources.length === 0) {
            var el = document.getElementById("contact-sources-list");
            if (el) el.innerHTML = "<div class=\"loading\">Contact-level attribution data pending bridge enrichment.</div>";
            return;
          }
          renderBars(document.getElementById("contact-sources-list"), sources.map(function (s) {
            var label = s.source || "Unknown";
            if (s.medium && s.medium !== "Unknown" && s.medium !== "") label += " / " + s.medium;
            var sub = "contacts:" + formatNumber(s.contacts||0) + " opps:" + formatNumber(s.opportunities||0);
            if (s.campaign && s.campaign !== "") sub += " cmp:" + s.campaign;
            return { label: label, sessions: s.contacts || 0, sub: sub };
          }), "No acquisition source data.");
        }
        function renderAdUtmTraffic(data) {
          var utms = Array.isArray(data.utmBreakdown) ? data.utmBreakdown : [];
          var adRows = utms.filter(function (u) {
            var src = (u.source || "").toLowerCase();
            var med = (u.medium || "").toLowerCase();
            var camp = (u.campaign || "").toLowerCase();
            return ["an", "facebook", "instagram", "fb", "ig", "meta"].indexOf(src) >= 0 ||
              med.indexOf("facebook") >= 0 || med.indexOf("instagram") >= 0 || med.indexOf("leadform") >= 0 ||
              camp.indexOf("meta") >= 0 || camp.indexOf("leadform") >= 0 ||
              (u.landingPage || "").indexOf("utm_id=") >= 0 || (u.landingPage || "").indexOf("utm_source=an") >= 0;
          });
          if (adRows.length === 0) {
            var el = document.getElementById("ad-utm-list");
            if (el) el.innerHTML = "<div class=\"loading\">No ad-tagged recorded visits in this window.</div>";
            return;
          }
          var maxAd = Math.max(1, ...adRows.map(function (i) { return i.sessions || 0; }));
          renderBars(document.getElementById("ad-utm-list"), adRows.slice(0, 8).map(function (u) {
            var label = (u.source || "?") + " / " + (u.medium || "?");
            if (u.campaign) label += " [" + u.campaign + "]";
            var value = u.sessions || 0;
            return { label: label, sessions: value, sub: "recorded visits:" + formatNumber(value) + (u.leads > 0 ? " contacts:" + formatNumber(u.leads) : "") };
          }), "No ad traffic data.");
        }
        function getHealthStatus(lastSuccessAt) {
          if (!lastSuccessAt) return { label: "Unknown", cls: "pending" };
          var hours = (Date.now() - new Date(lastSuccessAt).getTime()) / 3600000;
          if (hours <= 48) return { label: "Healthy", cls: "good" };
          if (hours <= 96) return { label: "Stale", cls: "warn" };
           return { label: "Failed", cls: "bad" };
         }
           var campaignChannelRows = [];
           var campaignChannelFilter = "all";
           var campaignNameFilter = "all";
           var campaignBreakdownRows = [];
           var expandedCampaign = null;
          function escapeHtml(value) {
            return String(value == null ? "" : value)
              .replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;")
              .replace(/\"/g, "&quot;")
              .replace(/'/g, "&#39;");
          }
            function campaignMatchesGroup(row, group) {
              var channel = String(row.channel || "").toLowerCase();
               var campaign = String(row.campaign || "").toLowerCase();
               var target = String(group || "").toLowerCase();
               if (campaign === target) return true;
              if (target === "dan") return campaign.indexOf("new attribution model") !== -1 || (channel === "sms" && campaign === "simpletexting_campaign_v1") || campaign === "general outbound";
              if (target === "emerald") return campaign.indexOf("emerald -") === 0;
              if (target === "partnership") return campaign.indexOf("partnership") !== -1;
              if (target === "vapi brand") return channel === "vapi" && campaign.indexOf("brand") !== -1;
              if (target === "vapi dispensary") return channel === "vapi" && campaign.indexOf("dispens") !== -1;
              if (target === "vapi") return channel === "vapi";
              return campaign.indexOf(target) !== -1;
            }
            var CAMPAIGN_CHANNEL_ACTIVITY_FIELDS = ["sms_sent", "sms_replies", "email_sent", "email_recipients", "email_delivered", "email_opened", "email_clicked", "email_replies", "email_bounced", "linkedin_invites", "linkedin_accepted", "linkedin_dms", "linkedin_replies", "instagram_dms", "instagram_replies", "vapi_calls", "vapi_answered", "vapi_qualified", "vapi_booked"];
            var CAMPAIGN_BREAKDOWN_ACTIVITY_FIELDS = ["opportunities", "email_sent", "email_recipients", "email_delivered", "email_opened", "email_clicked", "email_replies", "email_bounced", "linkedin_invites", "linkedin_accepted", "linkedin_dms", "linkedin_replies", "instagram_dms", "instagram_replies", "sms_sent", "sms_replies", "vapi_calls", "vapi_answered", "vapi_qualified", "vapi_booked"];
            function campaignRowHasActivity(row, fields) {
              return fields.some(function (field) { return Number(row && row[field] || 0) !== 0; });
            }
            function renderCampaignChannels(rows) {
             var body = document.getElementById("campaign-channel-table");
             if (!body) return;
             campaignChannelRows = Array.isArray(rows) ? rows : [];
             var visibleRows = campaignChannelRows.filter(function (row) {
               return campaignRowHasActivity(row, CAMPAIGN_CHANNEL_ACTIVITY_FIELDS);
             });
             if (campaignChannelFilter !== "all") {
               visibleRows = visibleRows.filter(function (row) {
                 return String(row.channel || "").toLowerCase() === campaignChannelFilter;
               });
             }
             if (campaignNameFilter !== "all") {
               visibleRows = visibleRows.filter(function (row) {
                  return campaignMatchesGroup(row, campaignNameFilter);
               });
             }
            if (visibleRows.length === 0) {
                  body.innerHTML = '<tr><td colspan="22" class="loading">No non-zero campaign channel data yet.</td></tr>';
              return;
            }
             body.innerHTML = visibleRows.map(function (r) {
              return "<tr>" +
                 "<td>" + escapeHtml(r.channel || "Unknown") + "</td>" +
                 "<td>" + escapeHtml(r.campaign || "Unknown") + "</td>" +
               "<td>" + formatNumber(r.sms_sent || 0) + "</td>" +
                "<td>" + formatNumber(r.sms_replies || 0) + "</td>" +
                  "<td>" + formatNumber(r.email_delivered || 0) + "</td>" +
                "<td>" + formatNumber(r.email_opened || 0) + "</td>" +
                "<td>" + (r.email_open_rate === null || r.email_open_rate === undefined ? "—" : formatCampaignPercent(r.email_open_rate)) + "</td>" +
                "<td>" + formatNumber(r.email_clicked || 0) + "</td>" +
                "<td>" + (r.email_click_rate === null || r.email_click_rate === undefined ? "—" : formatCampaignPercent(r.email_click_rate)) + "</td>" +
                "<td>" + formatNumber(r.email_replies || 0) + "</td>" +
                "<td>" + (r.email_response_rate === null || r.email_response_rate === undefined ? "—" : formatCampaignPercent(r.email_response_rate)) + "</td>" +
                "<td>" + formatNumber(r.email_bounced || 0) + "</td>" +
                "<td>" + formatNumber(r.linkedin_invites || 0) + "</td>" +
                "<td>" + formatNumber(r.linkedin_accepted || 0) + "</td>" +
                 "<td>" + formatNumber(r.linkedin_dms || 0) + "</td>" +
                 "<td>" + formatNumber(r.linkedin_replies || 0) + "</td>" +
                 "<td>" + formatNumber(r.instagram_dms || 0) + "</td>" +
                 "<td>" + formatNumber(r.instagram_replies || 0) + "</td>" +
                "<td>" + formatNumber(r.vapi_calls || 0) + "</td>" +
               "<td>" + formatNumber(r.vapi_answered || 0) + "</td>" +
               "<td>" + formatNumber(r.vapi_qualified || 0) + "</td>" +
               "<td>" + formatNumber(r.vapi_booked || 0) + "</td>" +
               "</tr>";
           }).join("");
          }
            function renderSmsSummary(summary) {
              var node = document.getElementById("sms-summary");
              if (!node) return;
              var data = summary || {};
              var failures = Array.isArray(data.failureBreakdown) ? data.failureBreakdown.slice(0, 4).map(function (item) {
                return String(item.reason || "unknown") + " (" + formatNumber(item.failures || 0) + ")";
              }).join(", ") : "";
              node.textContent = "SMS delivery summary: " + formatNumber(data.sent || 0) + " sent, " + formatNumber(data.failed || 0) + " failed, " + formatNumber(data.replies || 0) + " replies." + (failures ? " Failure reasons: " + failures + "." : "");
            }
             function renderInstagramSummary(summary) {
               var node = document.getElementById("instagram-summary");
               if (!node) return;
               var data = summary || {};
               node.textContent = "Instagram activity: " + formatNumber(data.dmsSent || 0) + " DMs sent, " + formatNumber(data.inboundReplies || 0) + " replies. Coverage: " + String(data.coverage || "unavailable") + ".";
             }
            function renderCampaignBreakdown(rows) {
             var body = document.getElementById("campaign-breakdown-table");
             if (!body) return;
             campaignBreakdownRows = Array.isArray(rows) ? rows : [];
              if (campaignBreakdownRows.length === 0) {
                    body.innerHTML = '<tr><td colspan="21" class="loading">No non-zero campaign breakdown data yet.</td></tr>';
               renderCampaignDetail(null, null);
               return;
             }
               var visibleBreakdownRows = campaignBreakdownRows.filter(function (r) {
                 return campaignRowHasActivity(r, CAMPAIGN_BREAKDOWN_ACTIVITY_FIELDS);
               });
               if (campaignNameFilter !== "all") {
                 visibleBreakdownRows = visibleBreakdownRows.filter(function (r) { return campaignMatchesGroup(r, campaignNameFilter); });
               }
              if (visibleBreakdownRows.length === 0) {
                  body.innerHTML = '<tr><td colspan="21" class="loading">No non-zero campaign breakdown data for this filter.</td></tr>';
                renderCampaignDetail(null, null);
                return;
              }
              body.innerHTML = visibleBreakdownRows.map(function (r) {
                var isExpanded = expandedCampaign === r.campaign;
                return "<tr class=\"campaign-row-clickable" + (isExpanded ? " expanded" : "") + "\" tabindex=\"0\" role=\"button\" aria-expanded=\"" + (isExpanded ? "true" : "false") + "\" data-campaign-name=\"" + escapeHtml(r.campaign || "") + "\">" +
                  "<td><strong>" + escapeHtml(r.campaign || "Unknown") + (isExpanded ? " ▾" : " ▸") + "</strong></td>" +
                  "<td>" + formatNumber(r.opportunities || 0) + "</td>" +
                 "<td>" + formatNumber(r.email_delivered || 0) + "</td>" +
                 "<td>" + formatNumber(r.email_opened || 0) + "</td>" +
                 "<td>" + (r.email_open_rate === null || r.email_open_rate === undefined ? "—" : formatCampaignPercent(r.email_open_rate)) + "</td>" +
                 "<td>" + formatNumber(r.email_clicked || 0) + "</td>" +
                 "<td>" + (r.email_click_rate === null || r.email_click_rate === undefined ? "—" : formatCampaignPercent(r.email_click_rate)) + "</td>" +
                  "<td>" + formatNumber(r.email_replies || 0) + "</td>" +
                  "<td>" + formatNumber(r.email_bounced || 0) + "</td>" +
                  "<td>" + formatNumber(r.linkedin_invites || 0) + "</td>" +
                  "<td>" + formatNumber(r.linkedin_accepted || 0) + "</td>" +
                   "<td>" + formatNumber(r.linkedin_dms || 0) + "</td>" +
                   "<td>" + formatNumber(r.linkedin_replies || 0) + "</td>" +
                   "<td>" + formatNumber(r.instagram_dms || 0) + "</td>" +
                   "<td>" + formatNumber(r.instagram_replies || 0) + "</td>" +
                  "<td>" + formatNumber(r.sms_sent || 0) + "</td>" +
                 "<td>" + formatNumber(r.sms_replies || 0) + "</td>" +
                 "<td>" + formatNumber(r.vapi_calls || 0) + "</td>" +
                 "<td>" + formatNumber(r.vapi_answered || 0) + "</td>" +
                 "<td>" + formatNumber(r.vapi_qualified || 0) + "</td>" +
                 "<td>" + formatNumber(r.vapi_booked || 0) + "</td>" +
                 "</tr>";
             }).join("");
             body.querySelectorAll(".campaign-row-clickable").forEach(function (tr) {
               tr.addEventListener("click", function () {
                  var row = campaignBreakdownRows.find(function (candidate) { return candidate.campaign === tr.getAttribute("data-campaign-name"); });
                 if (!row) return;
                 if (expandedCampaign === row.campaign) {
                   expandedCampaign = null;
                 } else {
                   expandedCampaign = row.campaign;
                 }
                  renderCampaignDetail(row, campaignChannelRows);
                  renderCampaignBreakdown(campaignBreakdownRows);
                });
                tr.addEventListener("keydown", function (event) {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    tr.click();
                  }
                });
             });
             renderCampaignDetail(
               expandedCampaign ? campaignBreakdownRows.find(function(r) { return r.campaign === expandedCampaign; }) : null,
                campaignChannelRows
              );
            }
           function renderCampaignDetail(campaignRow, channelRows) {
             var container = document.getElementById("campaign-detail-container");
             if (!container) return;
             if (!campaignRow) { container.style.display = "none"; container.innerHTML = ""; return; }
             container.style.display = "block";
             var campaignName = escapeHtml(campaignRow.campaign || "Unknown");
              var channelRowsFor = Array.isArray(channelRows)
                ? channelRows.filter(function(r) { return campaignMatchesGroup(r, campaignRow.campaign); })
               : [];
              var emailRows = channelRowsFor.filter(function(r) { return String(r.channel || "").toLowerCase() === "email"; });
              var liRows = channelRowsFor.filter(function(r) { return String(r.channel || "").toLowerCase() === "linkedin"; });
              var instagramRows = channelRowsFor.filter(function(r) { return String(r.channel || "").toLowerCase() === "instagram"; });
              var vapiRows = channelRowsFor.filter(function(r) { return String(r.channel || "").toLowerCase() === "vapi"; });
             var smsRows = channelRowsFor.filter(function(r) { return String(r.channel || "").toLowerCase() === "sms"; });
             function renderSubRows(rows, title, cols) {
               if (!rows.length) return "";
                 var colLabels = { sub_campaign: "Campaign", campaign: "Campaign", email_delivered: "Tracked Delivered", email_sent: "Tracked Recipients", email_opened: "Unique Opens", email_clicked: "Unique Clickers", email_replies: "Unique Replies", email_bounced: "Bounced", linkedin_invites: "Invites", linkedin_accepted: "Accepted", linkedin_dms: "DMs", linkedin_replies: "Replies", instagram_dms: "DMs", instagram_replies: "Replies", vapi_calls: "Calls", vapi_answered: "Answered", vapi_qualified: "Qualified", vapi_booked: "Booked", sms_sent: "Sent", sms_replies: "Replies" };
               return "<div style=\"margin-top:8px;\"><strong style=\"color:var(--muted);font-size:0.8rem;\">" + title + "</strong>" +
                 "<table class=\"campaign-table\" style=\"margin-top:4px;\"><thead><tr>" +
                 cols.map(function(c) { return "<th>" + (colLabels[c] || c) + "</th>"; }).join("") +
                 "</tr></thead><tbody>" +
                 rows.map(function(r) {
                   return "<tr>" + cols.map(function(c) {
                     if (c === "sub_campaign") return "<td style=\"text-align:left;\">" + escapeHtml(r.campaign || r.sub_campaign || "") + "</td>";
                     return "<td>" + formatNumber(r[c] || 0) + "</td>";
                   }).join("") + "</tr>";
                 }).join("") +
                 "</tbody></table></div>";
             }
             var detailHtml = "<h3>" + campaignName + " Campaign Detail</h3>" +
               "<div class=\"campaign-detail-grid\">" +
                buildDetailCard("Opportunities", campaignRow.opportunities, "") +
                 buildDetailCard("Tracked Delivered", campaignRow.email_delivered, "") +
                buildDetailCard("Unique Opens", campaignRow.email_opened, "Unique Open Rate: " + (campaignRow.email_open_rate !== null && campaignRow.email_open_rate !== undefined ? formatCampaignPercent(campaignRow.email_open_rate) : "—")) +
                buildDetailCard("Unique Clickers", campaignRow.email_clicked, "Unique Click Rate: " + (campaignRow.email_click_rate !== null && campaignRow.email_click_rate !== undefined ? formatCampaignPercent(campaignRow.email_click_rate) : "—")) +
                 buildDetailCard("Unique Replies", campaignRow.email_replies, "Unique Response Rate: " + (campaignRow.email_response_rate !== null && campaignRow.email_response_rate !== undefined ? formatCampaignPercent(campaignRow.email_response_rate) : "—")) +
                buildDetailCard("Bounced", campaignRow.email_bounced, "") +
                buildDetailCard("LinkedIn Invites", campaignRow.linkedin_invites, "") +
                buildDetailCard("LinkedIn Accepted", campaignRow.linkedin_accepted, "") +
                 buildDetailCard("LinkedIn DMs", campaignRow.linkedin_dms, "") +
                 buildDetailCard("LinkedIn Replies", campaignRow.linkedin_replies, "") +
                 buildDetailCard("Instagram DMs", campaignRow.instagram_dms, "") +
                 buildDetailCard("Instagram Replies", campaignRow.instagram_replies, "") +
                buildDetailCard("SMS Sent", campaignRow.sms_sent, "") +
               buildDetailCard("SMS Replies", campaignRow.sms_replies, "") +
               buildDetailCard("Vapi Calls", campaignRow.vapi_calls, "") +
               buildDetailCard("Vapi Answered", campaignRow.vapi_answered, "") +
               buildDetailCard("Vapi Qualified", campaignRow.vapi_qualified, "") +
               buildDetailCard("Vapi Booked", campaignRow.vapi_booked, "") +
                buildDetailCard("Total Actions", (campaignRow.email_sent || 0) + (campaignRow.linkedin_dms || 0) + (campaignRow.instagram_dms || 0) + (campaignRow.sms_sent || 0) + (campaignRow.vapi_calls || 0), "") +
               "</div>";
              detailHtml += renderSubRows(emailRows, "Email Sub-Campaigns", ["sub_campaign", "email_delivered", "email_opened", "email_clicked", "email_replies", "email_bounced"]);
              detailHtml += renderSubRows(liRows, "LinkedIn Sub-Campaigns", ["sub_campaign", "linkedin_invites", "linkedin_accepted", "linkedin_dms", "linkedin_replies"]);
              detailHtml += renderSubRows(instagramRows, "Instagram Sub-Campaigns", ["sub_campaign", "instagram_dms", "instagram_replies"]);
             detailHtml += renderSubRows(vapiRows, "Vapi Sub-Campaigns", ["sub_campaign", "vapi_calls", "vapi_answered", "vapi_qualified", "vapi_booked"]);
             detailHtml += renderSubRows(smsRows, "SMS Sub-Campaigns", ["sub_campaign", "sms_sent", "sms_replies"]);
             container.innerHTML = detailHtml;
           }
           function buildDetailCard(label, value, rate) {
             var val = Number(value || 0);
             return "<div class=\"campaign-detail-card\">" +
               "<span class=\"detail-label\">" + escapeHtml(label) + "</span>" +
               "<span class=\"detail-value\">" + formatNumber(val) + "</span>" +
               (rate ? "<span class=\"detail-rate\">" + escapeHtml(rate) + "</span>" : "") +
               "</div>";
           }
           var campaignViewMode = "list";
           function renderCampaignComparison(rows) {
             var container = document.getElementById("campaign-compare-view");
             var head = document.getElementById("campaign-compare-head");
             var body = document.getElementById("campaign-compare-body");
             if (!container || !head || !body) return;
             var campaigns = Array.isArray(rows) ? rows : [];
             if (!campaigns.length) { return; }
             var metrics = [
                { key: "opportunities", label: "Opportunities" },
                 { key: "email_delivered", label: "Tracked Delivered" },
                { key: "email_opened", label: "Unique Opens" },
                { key: "email_open_rate", label: "Unique Open Rate", isPct: true },
                { key: "email_clicked", label: "Unique Clickers" },
                { key: "email_click_rate", label: "Unique Click Rate", isPct: true },
                { key: "email_replies", label: "Unique Replies" },
                { key: "email_response_rate", label: "Unique Response Rate", isPct: true },
                { key: "email_bounced", label: "Bounced" },
                { key: "linkedin_invites", label: "LinkedIn Invites" },
                { key: "linkedin_accepted", label: "LinkedIn Accepted" },
                 { key: "linkedin_dms", label: "LinkedIn DMs" },
                 { key: "linkedin_replies", label: "LinkedIn Replies" },
                 { key: "instagram_dms", label: "Instagram DMs" },
                 { key: "instagram_replies", label: "Instagram Replies" },
               { key: "sms_sent", label: "SMS Sent" },
               { key: "sms_replies", label: "SMS Replies" },
               { key: "vapi_calls", label: "Vapi Calls" },
               { key: "vapi_answered", label: "Vapi Answered" },
               { key: "vapi_qualified", label: "Vapi Qualified" },
               { key: "vapi_booked", label: "Vapi Booked" }
             ];
             head.innerHTML = "<tr><th>Metric</th>" + campaigns.map(function(c) {
               return "<th>" + escapeHtml(c.campaign || "?") + "</th>";
             }).join("") + "</tr>";
             body.innerHTML = metrics.map(function(m) {
               return "<tr><td><strong>" + m.label + "</strong></td>" + campaigns.map(function(c) {
                 var val = c[m.key];
                 if (m.isPct) {
                   return "<td>" + (val === null || val === undefined ? "—" : formatCampaignPercent(val)) + "</td>";
                 }
                 return "<td>" + formatNumber(val || 0) + "</td>";
               }).join("") + "</tr>";
             }).join("");
           }
           function setCampaignView(mode) {
             campaignViewMode = mode;
             var listView = document.getElementById("campaign-breakdown-table")?.parentElement?.parentElement;
             var compareView = document.getElementById("campaign-compare-view");
             var listBtn = document.getElementById("cmp-view-list");
             var compareBtn = document.getElementById("cmp-view-compare");
             if (mode === "compare") {
               if (listView) listView.style.display = "none";
               if (compareView) compareView.style.display = "block";
               if (listBtn) listBtn.classList.remove("active");
               if (compareBtn) compareBtn.classList.add("active");
               renderCampaignComparison(campaignBreakdownRows);
             } else {
               if (listView) listView.style.display = "";
               if (compareView) compareView.style.display = "none";
               if (listBtn) listBtn.classList.add("active");
               if (compareBtn) compareBtn.classList.remove("active");
             }
           }
           function addDays(value, days) {
           var d = new Date(String(value) + "T00:00:00Z");
           d.setUTCDate(d.getUTCDate() + days);
           return d.toISOString().slice(0, 10);
         }
         function getPreviousWindow(window) {
           if (!window || !window.from || !window.to) return null;
           var start = new Date(window.from + "T00:00:00Z");
           var end = new Date(window.to + "T00:00:00Z");
           if (!Number.isFinite(start.getTime()) || !Number.isFinite(end.getTime()) || end < start) return null;
           var days = Math.round((end - start) / 86400000) + 1;
           return { from: addDays(window.from, -days), to: addDays(window.from, -1) };
         }
         function windowLabel(window) {
           return window && window.from && window.to ? window.from + " to " + window.to : "period unavailable";
         }
          function metricValue(data, key) {
            var summary = data && data.summary ? data.summary : {};
            var values = {
              contacts: Number(summary.contactsCreated || data.leadsNumeric || data.leads || 0),
              opportunities: Number(summary.opportunitiesCreated || data.opportunitiesCreated || 0),
              meetings: Number(summary.meetingsBooked || data.meetingsBooked || 0),
              closedWon: Number(summary.closedWonCount || data.closedWonCount || 0),
              emailOpened: Number(data.emailsOpened || 0),
              emailClicked: Number(data.emailsClicked || 0),
               vapiCalls: Number((data.vapiWeeklyPerformance || {}).totalCalls || 0),
              linkedinDms: Number((data.linkedinWeeklyActivity || {}).dmsSent || 0),
              linkedinReplies: Number((data.linkedinWeeklyActivity || {}).inboundReplies || 0)
            };
           return values[key] || 0;
         }
         function renderWeekComparison(current, previous) {
           var labels = [
             ["contacts", "wow-contacts"], ["opportunities", "wow-opportunities"], ["meetings", "wow-meetings"],
              ["closedWon", "wow-closed-won"], ["emailOpened", "wow-email-opened"], ["emailClicked", "wow-email-clicked"], ["vapiCalls", "wow-vapi-calls"],
              ["linkedinDms", "wow-linkedin-dms"], ["linkedinReplies", "wow-linkedin-replies"]
           ];
           labels.forEach(function (entry) {
             var currentValue = metricValue(current, entry[0]);
             var previousValue = metricValue(previous, entry[0]);
             var delta = currentValue - previousValue;
             var pct = previousValue === 0 ? (currentValue === 0 ? 0 : null) : (delta / previousValue) * 100;
             var valueEl = document.getElementById(entry[1]);
             var deltaEl = document.getElementById(entry[1] + "-delta");
             if (valueEl) valueEl.textContent = formatNumber(currentValue);
             if (deltaEl) deltaEl.textContent = "prior " + formatNumber(previousValue) + " · " + (pct === null ? "new" : (delta >= 0 ? "+" : "") + formatNumber(delta) + " (" + (pct >= 0 ? "+" : "") + pct.toFixed(1) + "%)");
           });
         }
         function setPeriodInputs(window) {
           var fromEl = document.getElementById("period-from");
           var toEl = document.getElementById("period-to");
           if (fromEl && window && window.from) fromEl.value = window.from;
           if (toEl && window && window.to) toEl.value = window.to;
         }
          async function loadJson(url) {
            var res = await fetch(url, { headers: { Accept: "application/json" } });
            if (!res.ok) throw new Error("HTTP " + res.status);
            return res.json();
          }
         function appendWindow(url, window) {
           if (window && window.from && window.to) {
              url = url.replace(/([?&])range=[^&]*/, "$1range=custom");
              url += "&from=" + encodeURIComponent(window.from) + "&to=" + encodeURIComponent(window.to);
            }
            return url;
         }
          function estimateWindow(r) {
            var end = new Date();
            end.setDate(end.getDate() - 1);
            end.setHours(0, 0, 0, 0);
            var days = r === "7d" ? 7 : r === "90d" ? 90 : 30;
            var start = new Date(end);
            start.setDate(start.getDate() - days + 1);
            return { from: start.toISOString().slice(0, 10), to: end.toISOString().slice(0, 10) };
          }
           async function loadReport() {
             var base = "/api/report/executive";
             var currentUrl = base + "/summary?view=" + encodeURIComponent(view) + "&range=" + encodeURIComponent(range);
             if (from) currentUrl += "&from=" + encodeURIComponent(from);
             if (to) currentUrl += "&to=" + encodeURIComponent(to);
             var estimatedWindow = from && to ? { from: from, to: to } : estimateWindow(range);
             var priorEstimate = getPreviousWindow(estimatedWindow);
             var previousUrl = priorEstimate ? appendWindow(base + "/summary?view=" + encodeURIComponent(view), priorEstimate) : null;
             var campaignUrl = base + "/campaign-channels?range=" + encodeURIComponent(range);
             if (from) campaignUrl += "&from=" + encodeURIComponent(from);
             if (to) campaignUrl += "&to=" + encodeURIComponent(to);
             try {
               // Render the selected window as soon as the primary summary is ready.
               // Campaign channels and prior-period comparison enrich the page afterward.
               var data = await loadJson(currentUrl);
               if (!data || !data.summary) throw new Error("Summary response was empty or malformed");
               var currentWindow = data.window || estimatedWindow || { from: from, to: to };
               var previousWindow = getPreviousWindow(currentWindow);
               setPeriodInputs(currentWindow);
               data.campaignChannelBreakdown = [];
               data.campaignBreakdown = [];
               data.smsSummary = { sent: 0, failed: 0, replies: 0 };
               data.instagramActivity = { dmsSent: 0, inboundReplies: 0, coverage: "loading" };
               render(data);
               renderWeekComparison(data, {});
               var comparisonLabel = document.getElementById("comparison-period-label");
               if (comparisonLabel) comparisonLabel.textContent = windowLabel(currentWindow) + " vs prior period loading…";
               var periodNote = document.getElementById("period-note");
               if (periodNote) periodNote.textContent = "Current period loaded. Loading prior-period comparison…";
               loadJson(campaignUrl).then(function (campaignData) {
                 data.campaignChannelBreakdown = campaignData.campaignChannelBreakdown || [];
                 data.campaignBreakdown = campaignData.campaignBreakdown || [];
                 data.smsSummary = campaignData.smsSummary || { sent: 0, failed: 0, replies: 0 };
                 data.instagramActivity = campaignData.instagramActivity || { dmsSent: 0, inboundReplies: 0, coverage: "unavailable" };
                 render(data);
               }).catch(function (err) {
                 console.warn("Campaign channel load failed:", err);
               });
               if (previousUrl) {
                 loadJson(previousUrl).then(function (previousData) {
                   renderWeekComparison(data, previousData || {});
                   if (comparisonLabel) comparisonLabel.textContent = windowLabel(currentWindow) + " vs " + windowLabel(previousWindow);
                   if (periodNote) periodNote.textContent = "Comparing against " + windowLabel(previousWindow) + ".";
                 }).catch(function (err) {
                   console.warn("Prior-period report load failed:", err);
                   if (comparisonLabel) comparisonLabel.textContent = windowLabel(currentWindow) + " vs prior period unavailable";
                   if (periodNote) periodNote.textContent = "Current period loaded; prior-period comparison is temporarily unavailable.";
                 });
               } else if (periodNote) {
                 periodNote.textContent = "Current period loaded.";
               }
             } catch (err) {
               console.warn("Report load failed:", err);
               var errorNote = document.getElementById("period-note");
               if (errorNote) errorNote.textContent = "Report data is temporarily unavailable. Please retry in a moment.";
             }
           }
function renderSdrPerformance(rows) {
            var list = Array.isArray(rows) ? rows : [];
            var body = document.getElementById("sdr-performance-table");
            if (!body) return;
            if (list.length === 0) {
              body.innerHTML = '<tr><td colspan="10" class="loading">No SDR performance data in this window.</td></tr>';
              return;
            }
            var html = list.map(function (row) {
              var role = row.owner_role === "sdr" ? "SDR" : (row.owner_role === "leadership" ? "Sales lead" : (row.owner_role === "exec" ? "Exec" : "—"));
              var name = String(row.owner_name || "Unknown SDR");
              return "<tr>" +
                "<td><strong>" + escapeHtml(name) + "</strong><div class=\"sub\">" + escapeHtml(role) + "</div></td>" +
                "<td>" + formatNumber(row.booked || 0) + "</td>" +
                "<td>" + formatNumber(row.showed || 0) + "</td>" +
                "<td>" + formatNumber(row.no_show || 0) + "</td>" +
                "<td>" + formatNumber(row.cancelled || 0) + "</td>" +
                "<td>" + formatNumber(row.sqls_created || 0) + "</td>" +
                "<td>" + formatNumber(row.mqls_converted || 0) + "</td>" +
                "<td>" + formatNumber(row.won || 0) + "</td>" +
                "<td>" + formatNumber(row.lost || 0) + "</td>" +
                "<td>" + formatCurrency(row.revenue || 0) + "</td>" +
                "</tr>";
            }).join("");
            body.innerHTML = html;
          }
          function renderLeadSource(rows, coverage) {
             var raw = Array.isArray(rows) ? rows : [];
             var merged = {};
             raw.forEach(function (row) {
               var source = String(row.source || "Unknown / Unattributed").trim();
               var sourceKey = source.toLowerCase();
               var isLinkedInUnipile = sourceKey.indexOf("linkedin via unipile") === 0;
               var displaySource = isLinkedInUnipile ? "LinkedIn via Unipile" : source;
               var medium = isLinkedInUnipile ? "" : String(row.medium || "").trim();
               var key = displaySource.toLowerCase() + "\u0000" + medium.toLowerCase();
               if (!merged[key]) merged[key] = { source: displaySource, medium: medium, mqls: 0, sqls: 0 };
               merged[key].mqls += Number(row.mqls || 0);
               merged[key].sqls += Number(row.sqls || 0);
             });
             var list = Object.keys(merged).map(function (key) { return merged[key]; });
            var body = document.getElementById("lead-source-table");
            if (!body) return;
            if (list.length === 0) {
              body.innerHTML = '<tr><td colspan="4" class="loading">No lead source data in this window.</td></tr>';
              return;
            }
            var html = list.map(function (row) {
              var mqls = formatNumber(row.mqls || 0);
              var sqls = formatNumber(row.sqls || 0);
              var source = String(row.source || "Unknown / Unattributed");
              var medium = String(row.medium || "—");
              var unattributed = source === "Unknown / Unattributed";
              var sourceCell = unattributed
                ? "<strong><span style=\"color:var(--faint);\">" + escapeHtml(source) + "</span></strong>"
                : "<strong>" + escapeHtml(source) + "</strong>";
              var mediumCell = unattributed
                ? "<span style=\"color:var(--faint);\">—</span>"
                : escapeHtml(medium);
              return "<tr>" +
                "<td>" + sourceCell + "</td>" +
                "<td>" + mediumCell + "</td>" +
                "<td>" + mqls + "</td>" +
                "<td>" + sqls + "</td>" +
                "</tr>";
            }).join("");
            body.innerHTML = html;
            var note = document.getElementById("lead-source-note");
            if (note && coverage && typeof coverage === "object") {
              var cov = "Attribution basis: contact first UTM source (medium/campaign) with traffic-to-lead bridge fallback, then GHL contact source. Coverage is limited by the leads snapshot. Attributed in this window: " +
                formatNumber(coverage.sqlsAttributed || 0) + " of " + formatNumber(coverage.sqlsTotal || 0) + " SQLs, " +
                formatNumber(coverage.mqlsAttributed || 0) + " of " + formatNumber(coverage.mqlsTotal || 0) + " MQLs. Unattributed rows are labelled \"Unknown / Unattributed\".";
              note.textContent = cov;
            }
          }
          function render(data) {
            if (!data || typeof data !== "object") return;
             renderCampaignChannels(data.campaignChannelBreakdown || []);
              renderCampaignBreakdown(data.campaignBreakdown || []);
              renderSmsSummary(data.smsSummary || {});
              renderInstagramSummary(data.instagramActivity || {});
               renderSdrPerformance(data.sdrPerformance || []);
                renderLeadSource(data.leadSourceBreakdown || [], data.leadSourceCoverage || {});
          var summary = data.summary || {};
          var captureGaps = data.captureGaps || {};
          var salesQuality = data.salesQuality || {};
          var channelBreakdown = Array.isArray(data.channelBreakdown) ? data.channelBreakdown : [];
          var pipelineDropoff = Array.isArray(data.pipelineDropoff) ? data.pipelineDropoff : [];
          var stageDropoff = Array.isArray(data.stageDropoff) ? data.stageDropoff : [];
          var stageVelocity = Array.isArray(data.stageVelocity) ? data.stageVelocity : [];
          var opportunityStageBreakdown = Array.isArray(data.opportunityStageBreakdown) ? data.opportunityStageBreakdown : [];
          var appointments = Array.isArray(data.appointments) ? data.appointments : [];
          var callStatusBreakdown = Array.isArray(data.callStatusBreakdown) ? data.callStatusBreakdown : [];
          var callOutcomeBreakdown = Array.isArray(data.callOutcomeBreakdown) ? data.callOutcomeBreakdown : [];
          var vapiTimezoneBuckets = (data.vapiTimezoneBuckets && Object.keys(data.vapiTimezoneBuckets).length > 0) ? data.vapiTimezoneBuckets : (summary.vapiTimezoneBuckets || {});
          var vapiWeeklyPerformance = (data.vapiWeeklyPerformance && Object.keys(data.vapiWeeklyPerformance).length > 0) ? data.vapiWeeklyPerformance : (summary.vapiWeeklyPerformance || {});
          var vapiWeeklyBreakdown = Array.isArray(data.vapiWeeklyBreakdown) ? data.vapiWeeklyBreakdown : (Array.isArray(summary.vapiWeeklyBreakdown) ? summary.vapiWeeklyBreakdown : []);
          var utmBreakdown = Array.isArray(data.utmBreakdown) ? data.utmBreakdown : [];
          var health = Array.isArray(data.health) ? data.health : [];
          function normalizeDisposition(value) {
            return String(value || "").trim().toLowerCase().replace(/_/g, "-");
          }
          function isAnsweredDisposition(value) {
            var normalized = normalizeDisposition(value);
            return normalized === "answered" || normalized === "connected" || normalized === "completed";
          }
          function isMissedDisposition(value) {
            var normalized = normalizeDisposition(value);
            return normalized === "no-answer" || normalized === "no answer" || normalized === "busy" || normalized === "failed" || normalized === "unanswered" || normalized === "missed";
          }
          function isVoicemailDisposition(value) {
            return normalizeDisposition(value).indexOf("voicemail") !== -1;
          }
          function sumOutcomeCounts(filterFn) {
            return callOutcomeBreakdown.reduce(function (total, item) {
              var disposition = item && item.disposition ? item.disposition : "unknown";
              var count = Number(item && (item.outcome_count || 0) || 0);
              return filterFn(disposition) ? total + count : total;
            }, 0);
          }
          var gscClicks = Number(summary.gscClicks || 0);
          var gscImpressions = Number(summary.gscImpressions || 0);
          var organicSearchUsers = Number(summary.organicSearchUsers || 0);
          var gscCtr = Number(summary.gscCtr || 0);
          var gscPosition = Number(summary.gscPosition || 0);
          var appointmentCounts = appointments.reduce(function (acc, item) {
            var status = String(item && item.status ? item.status : 'unknown').toLowerCase();
            var count = Number(item && (item.count || item.appointment_count || 0) || 0);
            acc.total += count;
            if (status === 'showed') acc.showed += count;
            else if (status === 'no-show') acc.noShow += count;
            else if (status === 'cancelled') acc.cancelled += count;
            return acc;
          }, { total: 0, showed: 0, noShow: 0, cancelled: 0 });
          var sessions = Number(summary.trafficNumeric || summary.sessions || 0);
          var contacts = Number(summary.leadsNumeric || summary.contactsCreated || 0);
          var opps = Number(summary.opportunitiesCreated || 0);
          var meetings = Number(summary.meetingsBooked || 0);
          var users = Number(summary.users || 0);
          var forms = Number(summary.formSubmissions || 0);
          var closedWon = Number(summary.closedWonCount || 0);
          var closedLost = Number(summary.closedLostCount || 0);
          var revenue = Number(summary.closedWonRevenue || 0);
          var activeOpps = Number(summary.activeOpportunityCount || 0);
          var workedOpps = Number(summary.workedOpportunityCount || 0);
          var stageMovers = Number(summary.stageMoverCount || 0);
          var callTotal = Number(summary.callTotal || summary.callOutcomeTotal || 0);
          var callAnswered = Number(summary.callAnsweredCount || sumOutcomeCounts(isAnsweredDisposition) || 0);
          var callMissed = Number(summary.callMissedCount || sumOutcomeCounts(isMissedDisposition) || 0);
          var callVoicemail = Number(summary.callVoicemailCount || sumOutcomeCounts(isVoicemailDisposition) || 0);
          var callInbound = Number(summary.callInboundCount || callOutcomeBreakdown.reduce(function (total, item) {
            return total + Number(item && (item.inbound_count || 0) || 0);
          }, 0));
          var callOutbound = Number(summary.callOutboundCount || callOutcomeBreakdown.reduce(function (total, item) {
            return total + Number(item && (item.outbound_count || 0) || 0);
          }, 0));
          var callStatusBreakdownEffective = callStatusBreakdown.length > 0 ? callStatusBreakdown : callOutcomeBreakdown.map(function (item) {
            var disposition = item && item.disposition ? item.disposition : "unknown";
            var outcomeCount = Number(item && (item.outcome_count || 0) || 0);
            return {
              status: disposition,
              call_count: outcomeCount,
              inbound_count: Number(item && (item.inbound_count || 0) || 0),
              outbound_count: Number(item && (item.outbound_count || 0) || 0),
              answered_count: isAnsweredDisposition(disposition) ? outcomeCount : 0
            };
          });
          var topPages = Array.isArray(data.topPages) ? data.topPages : [];
          var appointmentTotal = Number(summary.appointmentTotal || appointmentCounts.total || 0);
          var appointmentShowed = Number(summary.appointmentShowedCount || appointmentCounts.showed || 0);
          var appointmentNoShow = Number(summary.appointmentNoShowCount || appointmentCounts.noShow || 0);
          var appointmentCancelled = Number(summary.appointmentCancelledCount || appointmentCounts.cancelled || 0);
          var winRate = closedWon + closedLost > 0 ? (closedWon / (closedWon + closedLost)) * 100 : 0;
          var userToContactRate = users > 0 ? (contacts / users) : 0;
          var userToFormRate = users > 0 ? (forms / users) : 0;
          var el;
          el = document.getElementById("kpi-sessions");
          if (el) { el.textContent = sessions > 0 ? formatNumber(sessions) : "GA4 pending"; el.className = "value"; }
          el = document.getElementById("kpi-contacts"); if (el) el.textContent = formatNumber(contacts);
          el = document.getElementById("kpi-opportunities"); if (el) el.textContent = formatNumber(opps);
          el = document.getElementById("kpi-meetings"); if (el) el.textContent = formatNumber(meetings);
          el = document.getElementById("kpi-closed-won"); if (el) { el.textContent = formatNumber(closedWon); el.className = "value" + (closedWon > 0 ? " good" : ""); }
          el = document.getElementById("kpi-revenue"); if (el) { el.textContent = formatCurrency(revenue); el.className = "value" + (revenue > 0 ? " good" : ""); }
          var filteredChannels = channelBreakdown.filter(function(c) {
            var lbl = (c.label || c.channel || "").toLowerCase();
            return lbl !== "unattributed" && lbl !== "unknown" || (c.sessions || 0) > 0;
          });
          renderBars(document.getElementById("channels-list"), filteredChannels.map(function (c) {
            return { label: c.label || c.channel || "Other", sessions: c.sessions || 0, value: c.sessions || 0 };
          }), "No channel data yet.");
          renderMiniGrid(document.getElementById("channel-detail-grid"), filteredChannels.slice(0, 6).map(function (c) {
            return { label: c.label || c.channel || "?", value: formatNumber(c.sessions || 0) + " recorded visits / " + formatNumber(c.leads || 0) + " contacts" };
          }), null);
          renderMetaAttribution(data);
          renderContactSources(data);
          renderAdUtmTraffic(data);
           renderBars(document.getElementById("top-pages-list"), topPages.slice(0, 8).map(function (p) {
             var page = normalizeLandingPage(p.landing_page || p.landingPage || "Unknown");
             return {
               label: page,
              sessions: Number(p.sessions || 0),
              sub: "forms:" + formatNumber(Number(p.form_submissions || 0)) + " opps:" + formatNumber(Number(p.opportunities || 0)) + " revenue:" + formatCurrency(Number(p.closed_won_revenue || 0))
            };
          }), "No page summary yet.");
          var bestChannel = filteredChannels.length > 0 ? (filteredChannels[0].label || "GHL ready") : "GHL ready";
          el = document.getElementById("fn-session-to-form"); if (el) el.textContent = formatPercent(userToFormRate);
          el = document.getElementById("fn-session-to-contact"); if (el) el.textContent = formatPercent(userToContactRate);
          el = document.getElementById("fn-contact-to-opp"); if (el) el.textContent = formatPercent(Number(summary.contactToOpportunityRate || 0));
          el = document.getElementById("fn-opp-to-meeting"); if (el) el.textContent = formatPercent(Number(summary.opportunityToMeetingRate || 0));
          el = document.getElementById("fn-meeting-to-won"); if (el) el.textContent = formatPercent(Number(summary.meetingToClosedWonRate || 0));
          el = document.getElementById("fn-best-channel"); if (el) el.textContent = bestChannel;
          el = document.getElementById("attr-cohort"); if (el) el.textContent = formatNumber(Number(summary.cohortContacts || 0));
          el = document.getElementById("attr-source"); if (el) el.textContent = formatNumber(Number(summary.contactsWithSourceFields || 0));
          el = document.getElementById("attr-bridge"); if (el) el.textContent = formatNumber(Number(summary.contactsWithBridgeMatch || 0));
          el = document.getElementById("attr-sale"); if (el) el.textContent = formatNumber(Number(summary.contactsWithSaleMatch || 0));
          el = document.getElementById("attr-source-rate"); if (el) el.textContent = formatPercent(Number(summary.contactSourceCoverageRate || 0));
          el = document.getElementById("attr-bridge-rate"); if (el) el.textContent = formatPercent(Number(summary.contactBridgeMatchRate || 0));
          el = document.getElementById("cg-sessions"); if (el) el.textContent = formatNumber(sessions);
          el = document.getElementById("cg-forms"); if (el) el.textContent = formatNumber(Number(summary.formSubmissions || 0));
          el = document.getElementById("cg-contacts"); if (el) el.textContent = formatNumber(contacts);
          el = document.getElementById("cg-opportunities"); if (el) el.textContent = formatNumber(opps);
          el = document.getElementById("cg-meetings"); if (el) el.textContent = formatNumber(meetings);
          el = document.getElementById("cg-closed-won"); if (el) el.textContent = formatNumber(closedWon);
          el = document.getElementById("gsc-clicks"); if (el) el.textContent = formatNumber(gscClicks);
          el = document.getElementById("gsc-impressions"); if (el) el.textContent = formatNumber(gscImpressions);
          el = document.getElementById("gsc-unique-visitors"); if (el) el.textContent = formatNumber(organicSearchUsers);
          el = document.getElementById("gsc-ctr"); if (el) el.textContent = formatPercent(gscCtr);
          el = document.getElementById("gsc-position"); if (el) el.textContent = formatNumber(gscPosition, 1);
          renderMiniGrid(document.getElementById("pipeline-grid"), pipelineDropoff.map(function (p) {
            return { label: resolvePipeline(p.label || p.pipeline || "Pipeline"), value: formatNumber(p.value || p.stageCount || 0) };
          }), [{ label: "Warm", value: "—" }, { label: "Sales Outreach", value: "—" }, { label: "Sales", value: "—" }]);
          renderBars(document.getElementById("stage-movement-list"), stageDropoff.slice(0, 8).map(function (s) {
            return { label: resolvePipeline(s.pipeline || "?") + " \u2192 " + resolveStage(s.stage || "?"), sessions: s.moved_out_count || 0, sub: "in:" + formatNumber(s.moved_in_count || 0) + " out:" + formatNumber(s.moved_out_count || 0) };
          }), "No stage data yet.");
          renderBars(document.getElementById("velocity-list"), stageVelocity.map(function (v) {
            var pipeName = resolvePipeline(v.pipeline);
            var stageName = resolveStage(v.stage);
            return { label: pipeName + " \u2192 " + stageName, sessions: v.avg_days_in_stage || 0, sub: "avg:" + formatNumber(v.avg_days_in_stage, 1) + "d | " + formatNumber(v.opp_count) + " opps | " + formatNumber(v.total_transitions) + " transitions" };
          }), "No velocity data yet.");
          el = document.getElementById("sq-cycle"); if (el) el.textContent = salesQuality.avgCycleLengthDays ? salesQuality.avgCycleLengthDays + "d" : "—";
          el = document.getElementById("sq-best-channel"); if (el) el.textContent = salesQuality.bestChannel || bestChannel || "—";
          el = document.getElementById("sq-revenue"); if (el) el.textContent = formatCurrency(revenue);
          el = document.getElementById("sq-won"); if (el) { el.textContent = formatNumber(closedWon); el.className = closedWon > 0 ? "value good" : ""; }
          el = document.getElementById("sq-lost"); if (el) el.textContent = formatNumber(closedLost);
          el = document.getElementById("sq-win-rate"); if (el) el.textContent = formatNumber(winRate, 1) + "%";
          renderBars(document.getElementById("deal-stage-list"), opportunityStageBreakdown.slice(0, 10).map(function (s) {
            return { label: resolvePipeline(s.pipeline || "?") + " → " + resolveStage(s.stage || "?"), sessions: s.active_opportunities || 0, sub: "worked:" + formatNumber(s.worked_opportunities || 0) + " movers:" + formatNumber(s.stage_movers || 0) };
          }), "No active opportunity data yet.");
          // John's view — appointments + deals
          el = document.getElementById("appointments-total"); if (el) el.textContent = formatNumber(appointmentTotal);
          el = document.getElementById("appointments-showed"); if (el) el.textContent = formatNumber(appointmentShowed);
          el = document.getElementById("appointments-noshow"); if (el) el.textContent = formatNumber(appointmentNoShow);
          el = document.getElementById("appointments-cancelled"); if (el) el.textContent = formatNumber(appointmentCancelled);
          renderBars(document.getElementById("appointments-list"), appointments.map(function(a) {
            return { label: a.status || "?", sessions: a.count || 0, sub: formatNumber(a.count || 0) + " total" };
          }), "No appointment data yet.");
          el = document.getElementById("calls-total"); if (el) el.textContent = formatNumber(callTotal);
          el = document.getElementById("calls-answered"); if (el) el.textContent = formatNumber(callAnswered);
          el = document.getElementById("calls-missed"); if (el) el.textContent = formatNumber(callMissed);
          el = document.getElementById("calls-voicemail"); if (el) el.textContent = formatNumber(callVoicemail);
          el = document.getElementById("calls-inbound"); if (el) el.textContent = formatNumber(callInbound);
          el = document.getElementById("calls-outbound"); if (el) el.textContent = formatNumber(callOutbound);
          renderBars(document.getElementById("call-status-list"), callStatusBreakdownEffective.map(function (s) {
            return { label: s.status || "unknown", sessions: s.call_count || 0, sub: "answered:" + formatNumber(s.answered_count || 0) + " in:" + formatNumber(s.inbound_count || 0) + " out:" + formatNumber(s.outbound_count || 0) };
          }), "No call data yet.");
          renderBars(document.getElementById("call-outcome-list"), callOutcomeBreakdown.map(function (s) {
            return { label: s.disposition || "unknown", sessions: s.outcome_count || 0, sub: "out:" + formatNumber(s.outbound_count || 0) + " in:" + formatNumber(s.inbound_count || 0) + " linked:" + formatNumber(s.linked_contact_count || 0) };
          }), "No call outcome data yet.");
          var vapiTimezoneTotal = Number(vapiTimezoneBuckets.total_queued || vapiTimezoneBuckets.totalQueued || 0);
          var vapiTimezoneExplicit = Number(vapiTimezoneBuckets.explicit_count || vapiTimezoneBuckets.explicit || 0);
          var vapiTimezoneInferred = Number(vapiTimezoneBuckets.inferred_count || vapiTimezoneBuckets.inferred || 0);
          var vapiTimezoneNone = Number(vapiTimezoneBuckets.none_count || vapiTimezoneBuckets.none || 0);
          el = document.getElementById("vapi-tz-total"); if (el) el.textContent = formatNumber(vapiTimezoneTotal);
          el = document.getElementById("vapi-tz-explicit"); if (el) el.textContent = formatNumber(vapiTimezoneExplicit);
          el = document.getElementById("vapi-tz-inferred"); if (el) el.textContent = formatNumber(vapiTimezoneInferred);
          el = document.getElementById("vapi-tz-none"); if (el) el.textContent = formatNumber(vapiTimezoneNone);
          var vapiWeeklyTotal = Number(vapiWeeklyPerformance.total_calls || vapiWeeklyPerformance.totalCalls || 0);
          var vapiWeeklyAnswered = Number(vapiWeeklyPerformance.answered_calls || vapiWeeklyPerformance.answeredCalls || 0);
          var vapiWeeklyMissed = Number(vapiWeeklyPerformance.missed_calls || vapiWeeklyPerformance.missedCalls || 0);
          var vapiWeeklyQualified = Number(vapiWeeklyPerformance.qualified_calls || vapiWeeklyPerformance.qualifiedCalls || 0);
          var vapiWeeklyVoicemail = Number(vapiWeeklyPerformance.voicemail_calls || vapiWeeklyPerformance.voicemailCalls || 0);
          var vapiWeeklyHandoff = Number(vapiWeeklyPerformance.handoff_required_calls || vapiWeeklyPerformance.handoffRequiredCalls || 0);
          el = document.getElementById("vapi-weekly-total"); if (el) el.textContent = formatNumber(vapiWeeklyTotal);
          el = document.getElementById("vapi-weekly-answered"); if (el) el.textContent = formatNumber(vapiWeeklyAnswered);
          el = document.getElementById("vapi-weekly-missed"); if (el) el.textContent = formatNumber(vapiWeeklyMissed);
          el = document.getElementById("vapi-weekly-qualified"); if (el) el.textContent = formatNumber(vapiWeeklyQualified);
          el = document.getElementById("vapi-weekly-voicemail"); if (el) el.textContent = formatNumber(vapiWeeklyVoicemail);
          el = document.getElementById("vapi-weekly-handoff"); if (el) el.textContent = formatNumber(vapiWeeklyHandoff);
          renderBars(document.getElementById("vapi-weekly-breakdown-list"), vapiWeeklyBreakdown.map(function (item) {
            return {
              label: String(item.disposition || item.status || 'unknown'),
              sessions: Number(item.call_count || item.count || 0),
              sub: "qualified:" + formatNumber(Number(item.qualified_count || 0)) + " handoff:" + formatNumber(Number(item.handoff_required_count || 0))
            };
          }), "No Vapi weekly data yet.");
          el = document.getElementById("jd-opps"); if (el) el.textContent = formatNumber(activeOpps);
          el = document.getElementById("jd-worked"); if (el) el.textContent = formatNumber(workedOpps);
          el = document.getElementById("jd-stage-movers"); if (el) el.textContent = formatNumber(stageMovers);
          el = document.getElementById("jd-won"); if (el) el.textContent = formatNumber(closedWon);
          el = document.getElementById("jd-lost"); if (el) el.textContent = formatNumber(closedLost);
          el = document.getElementById("jd-win-rate"); if (el) el.textContent = formatNumber(winRate, 1) + "%";
          // Chella's social — data from GHL Social Planner API via Postgres
          var sp = data.socialPosts || {};
          el = document.getElementById("sp-total"); if (el) el.textContent = formatNumber(sp.totalPosts || 0);
           el = document.getElementById("sp-fb"); if (el) el.textContent = formatNumber(sp.facebookCount || 0);
           el = document.getElementById("sp-ig"); if (el) el.textContent = formatNumber(sp.instagramCount || 0);
           el = document.getElementById("sp-li"); if (el) el.textContent = formatNumber(sp.linkedinCount || 0);
           el = document.getElementById("sp-published"); if (el) el.textContent = formatNumber(sp.publishedCount || 0);
           el = document.getElementById("sp-failed"); if (el) el.textContent = formatNumber(sp.failedCount || 0);
           el = document.getElementById("sp-likes"); if (el) el.textContent = formatNumber(sp.totalLikes || 0);
           el = document.getElementById("sp-comments"); if (el) el.textContent = formatNumber(sp.totalComments || 0);
           el = document.getElementById("sp-shares"); if (el) el.textContent = formatNumber(sp.totalShares || 0);
function formatOptionalSocialMetric(value) {
               return value !== null && value !== undefined ? formatNumber(value) : "N/A";
             }
             el = document.getElementById("sp-reach"); if (el) el.textContent = formatOptionalSocialMetric(sp.totalReach);
             el = document.getElementById("sp-impressions"); if (el) el.textContent = formatOptionalSocialMetric(sp.totalImpressions);
             el = document.getElementById("sp-account-posts"); if (el) el.textContent = formatOptionalSocialMetric(sp.accountPosts);
             el = document.getElementById("sp-account-likes"); if (el) el.textContent = formatOptionalSocialMetric(sp.accountLikes);
             el = document.getElementById("sp-account-followers"); if (el) el.textContent = formatOptionalSocialMetric(sp.accountFollowers);
           // Site traffic from summary
           var mqlSummary = data.mqlSummary || {};
           var sqlContacts = data.sqlContacts || {};
           var linkedinFunnel = data.linkedinFunnel || {};
           var linkedinWeeklyActivity = data.linkedinWeeklyActivity || {};
el = document.getElementById("snapshot-mql-total"); if (el) el.textContent = formatNumber(mqlSummary.totalMqls ?? mqlSummary.totalEver ?? 0);
           el = document.getElementById("snapshot-mql-converted"); if (el) el.textContent = formatNumber(mqlSummary.convertedToSql ?? 0);
           el = document.getElementById("snapshot-mql-current"); if (el) el.textContent = formatNumber(mqlSummary.currentMqls ?? mqlSummary.active ?? 0);
           el = document.getElementById("snapshot-mql-entered"); if (el) el.textContent = formatNumber(mqlSummary.enteredMqls ?? 0);
           el = document.getElementById("snapshot-mql-conv-period"); if (el) el.textContent = formatNumber(mqlSummary.convertedThisPeriod ?? 0);
            el = document.getElementById("snapshot-sql"); if (el) el.textContent = formatNumber(sqlContacts.totalCount || 0);
            el = document.getElementById("snapshot-li-ready"); if (el) el.textContent = formatNumber(linkedinFunnel.readyCount || 0);
            el = document.getElementById("snapshot-li-requested"); if (el) el.textContent = formatNumber(linkedinFunnel.requestedCount || 0);
            el = document.getElementById("snapshot-li-connected"); if (el) el.textContent = formatNumber(linkedinFunnel.connectedCount || 0);
             el = document.getElementById("snapshot-li-follower-messaged"); if (el) el.textContent = formatNumber(linkedinFunnel.followerMessagedCount || 0);
             el = document.getElementById("snapshot-li-active"); if (el) el.textContent = formatNumber(linkedinFunnel.dmActiveCount || 0);
             el = document.getElementById("snapshot-li-completed"); if (el) el.textContent = formatNumber(linkedinFunnel.dmCompletedCount || 0);
             el = document.getElementById("snapshot-li-total"); if (el) el.textContent = formatNumber(linkedinFunnel.totalInState || 0);
            el = document.getElementById("linkedin-weekly-requests"); if (el) el.textContent = formatNumber(linkedinWeeklyActivity.connectionRequestsSent || 0);
            el = document.getElementById("linkedin-weekly-accepts"); if (el) el.textContent = formatNumber(linkedinWeeklyActivity.connectionsAccepted || 0);
            el = document.getElementById("linkedin-weekly-dms"); if (el) el.textContent = formatNumber(linkedinWeeklyActivity.dmsSent || 0);
            el = document.getElementById("linkedin-weekly-replies"); if (el) el.textContent = formatNumber(linkedinWeeklyActivity.inboundReplies || 0);
           el = document.getElementById("st-sessions"); if (el) el.textContent = formatNumber(sessions);
          el = document.getElementById("st-users"); if (el) el.textContent = formatNumber(Number(summary.users || 0));
          el = document.getElementById("st-engaged"); if (el) el.textContent = formatNumber(Number(summary.engagedSessions || 0));
          el = document.getElementById("st-forms"); if (el) el.textContent = formatNumber(Number(summary.formSubmissions || 0));
           el = document.getElementById("st-top-page");
           if (el) {
             var topPageLabel = topPages.length > 0 ? normalizeLandingPage(topPages[0].landing_page || topPages[0].landingPage || "Unknown") : "No page data yet";
             el.textContent = topPageLabel;
           }
          el = document.getElementById("st-eng-rate"); if (el) el.textContent = formatPercent(Number(summary.engagementRate || 0));
          renderBars(document.getElementById("deals-pipeline-list"), opportunityStageBreakdown.slice(0, 10).map(function(s) {
            return { label: resolvePipeline(s.pipeline || "?") + " → " + resolveStage(s.stage || "?"), sessions: s.active_opportunities || 0, sub: "worked:" + formatNumber(s.worked_opportunities || 0) + " movers:" + formatNumber(s.stage_movers || 0) };
          }), "No active opportunity data.");
          // Sales team panel
          el = document.getElementById("st-total-opps"); if (el) el.textContent = formatNumber(activeOpps);
          el = document.getElementById("st-worked-opps"); if (el) el.textContent = formatNumber(workedOpps);
          el = document.getElementById("st-stage-movers"); if (el) el.textContent = formatNumber(stageMovers);
          el = document.getElementById("st-pipeline-value"); if (el) el.textContent = formatCurrency(revenue);
          var utmRows = [];
          var unknownPaths = {};
          utmBreakdown.forEach(function (u) {
            var src = (u.source || "").toLowerCase();
            var med = (u.medium || "").toLowerCase();
            var camp = (u.campaign || "").toLowerCase();
            if (src === "unknown" && med === "unknown" && camp === "unknown") {
              var page = u.landingPage || "";
              var path = page.replace(/^https?:\/\/[^\/]+/i, "") || "/";
              if (!unknownPaths[path]) unknownPaths[path] = 0;
              unknownPaths[path] += Number(u.sessions || 0);
            } else if (src === "unknown" || med === "unknown" || src === "(not set)") {
              utmRows.push({ source: u.source || "?", medium: u.medium || "?", campaign: u.campaign || "", sessions: u.sessions || 0 });
            } else {
              utmRows.push(u);
            }
          });
          Object.keys(unknownPaths).sort(function(a,b){return (unknownPaths[b]||0)-(unknownPaths[a]||0);}).forEach(function(path) {
            utmRows.push({ source: "direct", medium: path, campaign: "", sessions: unknownPaths[path] });
          });
          renderBars(document.getElementById("utm-list"), utmRows.slice(0, 12).map(function (u) {
            var label = (u.source === "direct") ? u.medium : (u.source || "?") + " / " + (u.medium || "?");
            return { label: label, sessions: u.sessions || 0, sub: "contacts:" + formatNumber(u.leads || 0) + " opps:" + formatNumber(u.opportunities || 0) };
          }), "No UTM data yet.");
           var healthByKey = {};
           health.forEach(function (h) {
             var key = String(h.source_system || h.source || "").replace(/^"+|"+$/g, "").trim();
             if (!key) return;
             var existing = healthByKey[key];
             if (!existing || (h.last_success_at && !existing.last_success_at) || (h.last_attempt_at && !existing.last_attempt_at)) healthByKey[key] = h;
           });
           Object.keys(healthByKey).forEach(function (key) {
             var h = healthByKey[key];
             var idMap = {
              "ghl": "hl-ghl",
              "ga4": "hl-ga4",
              "gsc": "hl-gsc",
              "meta_ads": "hl-meta",
              "n8n": "hl-n8n",
              "postgres": "hl-postgres",
              "rollups": "hl-rollups",
              "bridge": "hl-bridge",
              "velocity": "hl-velocity",
              "appointments": "hl-calls"
            };
            var id = idMap[key] || null;
            if (!id) return;
            el = document.getElementById(id);
            if (!el) return;
            if (h.status === "success" || h.status === "ready") {
              var hours = h.last_success_at ? (Date.now() - new Date(h.last_success_at).getTime()) / 3600000 : null;
              if (hours === null || hours === undefined) {
                el.textContent = "Unknown"; el.className = "pending";
              } else if (hours <= 48) {
                el.textContent = "Healthy"; el.className = "good";
              } else if (hours <= 96) {
                el.textContent = "Stale"; el.className = "warn";
              } else {
                el.textContent = "Failed"; el.className = "bad";
              }
            } else if (h.status === "blocked") {
              el.textContent = "Blocked"; el.className = "bad";
            } else if (h.status === "pending") {
              el.textContent = "Pending"; el.className = "pending";
            } else {
              el.textContent = h.status || "—"; el.className = "";
            }
          });
        }
         syncNavLinks();
         setActiveRange(range);
         setActiveSidebar(section || "section-kpis");
         var periodForm = document.getElementById("period-picker");
          if (periodForm) {
           periodForm.addEventListener("submit", function (event) {
             event.preventDefault();
             var nextFrom = document.getElementById("period-from").value;
             var nextTo = document.getElementById("period-to").value;
             if (!nextFrom || !nextTo || nextFrom > nextTo) return;
             var next = new URL(window.location.href);
             next.searchParams.set("range", "custom");
             next.searchParams.set("from", nextFrom);
             next.searchParams.set("to", nextTo);
             next.searchParams.set("embed", "1");
             window.location.href = next.toString();
           });
          }
           document.querySelectorAll("[data-campaign-channel]").forEach(function (button) {
             button.addEventListener("click", function () {
               campaignChannelFilter = button.getAttribute("data-campaign-channel") || "all";
               document.querySelectorAll("[data-campaign-channel]").forEach(function (item) {
                 item.classList.toggle("active", item === button);
               });
               renderCampaignChannels(campaignChannelRows);
             });
           });
           document.querySelectorAll("[data-campaign-name]").forEach(function (button) {
             button.addEventListener("click", function () {
               campaignNameFilter = button.getAttribute("data-campaign-name") || "all";
               document.querySelectorAll("[data-campaign-name]").forEach(function (item) {
                 item.classList.toggle("active", item === button);
               });
               renderCampaignChannels(campaignChannelRows);
             });
            });
            document.querySelectorAll("[data-campaign-view]").forEach(function (button) {
              button.addEventListener("click", function () {
                setCampaignView(button.getAttribute("data-campaign-view") || "list");
              });
            });
            loadReport();
        if (section) window.setTimeout(function () { scrollToSection(section); }, 150);
      })();
    </script>
  </body>
</html>
````

## File: reports/embed/executive-v1/index.html
````html
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Executive Report V1</title>
<style>
:root{--ink:#303030;--muted:#707070;--line:#d5d2ca;--soft:#f5f5f2;--blue:#2164a6;--gold:#c59200;--green:#2c7737;--red:#c32222}*{box-sizing:border-box}body{margin:0;color:var(--ink);font:13px/1.35 Arial,sans-serif}main{max-width:1220px;margin:auto;padding:26px 30px 50px}h1,h2,h3,p{margin:0}h1{font-size:25px}h3{font-size:14px}.sub,.desc,.small-note,.foot{color:var(--muted);font-size:11px}.top{display:flex;justify-content:space-between;align-items:flex-end;gap:18px;margin-bottom:18px}.controls{display:flex;gap:8px;flex-wrap:wrap}.controls input,.controls select,.controls button{font:inherit;border:1px solid var(--line);background:#fff;padding:7px 9px;border-radius:5px}.controls button{background:var(--blue);color:#fff;border-color:var(--blue);cursor:pointer}.health{display:flex;gap:9px;flex-wrap:wrap;font-size:11px}.health span{padding:4px 7px;border-radius:10px;background:#e8f3e9;color:var(--green)}.health .bad{background:#fae4e4;color:var(--red)}.error{display:none;color:var(--red);background:#fff1f1;border:1px solid #e8baba;padding:10px;border-radius:7px;margin-top:10px}.band-title{font-size:15px;color:#707070;letter-spacing:.04em;margin:18px 0 8px;font-weight:700}.grid{display:grid;gap:10px}.six{grid-template-columns:repeat(6,minmax(0,1fr))}.five{grid-template-columns:repeat(5,minmax(0,1fr))}.three{grid-template-columns:repeat(3,minmax(0,1fr))}.two{grid-template-columns:repeat(2,minmax(0,1fr))}.kpi{background:var(--soft);border-radius:10px;padding:11px 12px;min-height:73px}.kpi .label{color:#696969;font-size:11px}.kpi .value{font-size:25px;font-weight:700;line-height:1.1;margin:3px 0}.kpi .note{font-size:10px;color:var(--muted)}.card{border:1px solid var(--line);border-radius:11px;padding:12px;background:#fff;min-width:0}.card .desc{margin:2px 0 10px}.bar{margin:8px 0}.barline{display:flex;align-items:center;gap:8px;font-size:11px}.barline .name{min-width:110px;max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.track{height:8px;background:#f0f0ee;border-radius:5px;flex:1;overflow:hidden}.fill{height:100%;background:var(--blue);border-radius:5px}.barline .num{width:40px;text-align:right;font-variant-numeric:tabular-nums}.empty,.unavailable{color:var(--muted);font-size:11px;font-style:italic}.metric{display:flex;justify-content:space-between;gap:10px;margin:7px 0}.metric strong{font-size:24px}.metric span{color:var(--muted);font-size:10px}.table-wrap{overflow-x:auto}.table{width:100%;border-collapse:collapse;min-width:680px}.table th,.table td{border:1px solid var(--line);padding:8px 9px;text-align:right;white-space:nowrap;font-size:11px}.table th:first-child,.table td:first-child{text-align:left}.table th{background:#f6f6f3;color:#666;font-weight:400}.table td{font-variant-numeric:tabular-nums}.table caption{text-align:left;color:var(--blue);font-weight:700;font-size:14px;padding:0 0 7px}.section-gap{margin-top:12px}.right{text-align:right}.pill{display:inline-block;border-radius:12px;padding:3px 9px;font-size:10px;background:#fae4e4;color:var(--red);margin-right:6px}.pill.yellow{background:#fff4d5;color:#8a6800}.action{display:flex;align-items:flex-start;gap:8px;border-bottom:1px solid #eee;padding:8px 0}.action:last-child{border-bottom:0}.foot{margin-top:18px}@media(max-width:900px){main{padding:18px 14px}.six{grid-template-columns:repeat(3,minmax(0,1fr))}.three{grid-template-columns:1fr 1fr}.top{align-items:flex-start;flex-direction:column}}@media(max-width:580px){.six,.five,.three,.two{grid-template-columns:1fr}.kpi{min-height:65px}.barline .name{min-width:92px;max-width:110px}}
</style><style>.eight{grid-template-columns:repeat(8,minmax(0,1fr))}@media(max-width:900px){.eight{grid-template-columns:repeat(4,minmax(0,1fr))}}@media(max-width:580px){.eight{grid-template-columns:1fr}}</style></head><body><main>
<header class="top"><div><h1>Executive Report <span class="sub">V1</span></h1><p id="period-label" class="sub">Loading reporting period…</p></div><form id="period-form" class="controls"><select id="range"><option value="7d">7d</option><option value="30d" selected>30d</option><option value="90d">90d</option></select><input id="from" type="date" aria-label="From date"><input id="to" type="date" aria-label="To date"><button>Apply</button></form></header>
<div id="health" class="health"></div><div id="error" class="error"></div>
<div class="band-title">BAND 1 · Funnel — read first</div><section class="grid eight" id="headline"></section><section class="section-gap card"><h3>Funnel outcomes</h3><p class="desc">Opportunities → MQLs → SQLs → meetings → closed outcomes → revenue</p><div class="grid five" id="funnel-metrics"></div><p id="funnel-note" class="small-note"></p></section>
<div class="band-title">BAND 2 · The story behind each headline</div><section class="grid three">
<article class="card"><h3>Opportunities by source</h3><p class="desc">drills from opportunities in the selected period</p><div id="opp-sources"></div></article>
<article class="card"><h3>MQL sources</h3><p class="desc">where MQLs came from</p><div id="mql-sources"></div><p id="mql-coverage" class="small-note"></p></article>
<article class="card"><h3>SQL sources</h3><p class="desc">where SQLs came from</p><div id="sql-sources"></div><p id="sql-coverage" class="small-note"></p></article>
<article class="card"><h3>New contacts — how added</h3><p class="desc">source labels from contact attribution</p><div id="contact-sources"></div><p class="small-note">Mechanism-level splits appear only when the source records them.</p></article>
<article class="card"><h3>Meetings - Regulated Ads On Social/Search</h3><p class="desc">unique contacts booked on this calendar</p><div id="meetings-detail"></div></article>
<article class="card"><h3>Meeting outcomes</h3><p class="desc">showed · no-show · cancelled · rescheduled</p><div id="meeting-outcomes" class="grid two"></div><p id="meeting-note" class="small-note"></p></article>
<article class="card"><h3>Pipeline to work</h3><p class="desc">qualified leads left to call</p><div class="metric"><strong id="pipeline-work">—</strong><span>qualified remaining<br>this period</span></div><p class="small-note">Uses opportunity-stage data when available.</p></article>
<article class="card"><h3>Lead-source coverage</h3><p class="desc">how much is attributed</p><div class="metric"><strong id="coverage-rate">—</strong><span id="coverage-detail">coverage unavailable</span></div></article>
<article class="card"><h3>Speed-to-lead &amp; follow-up</h3><p class="desc">same-channel inbound reply response</p><div class="grid two"><div><strong id="speed">—</strong><div class="sub">avg response time</div></div><div><strong id="overdue">—</strong><div class="sub">inbound events unresolved</div></div></div><p id="response-sla-note" class="small-note">Measured from inbound LinkedIn DM, inbound call, or marketing-email reply to the next outbound event on that same channel.</p></article>
  <article class="card"><h3>Closed outcomes by source</h3><p class="desc">won/lost SQL outcomes and recognized revenue</p><div id="closed-sources"></div></article>
<article class="card"><h3>Weekly lead movement</h3><p class="desc">distinct contacts at intake; distinct opportunities for stage movement</p><div class="table-wrap"><table class="table" id="weekly-table"><thead><tr><th>Week</th><th>New leads</th><th>MQLs</th><th>SQLs</th><th>Later stages</th><th>Current distribution</th></tr></thead><tbody></tbody></table></div></article>
<article class="card"><h3>Retargeting signals</h3><p class="desc">newsletter click/audience visibility only; no automatic send permission</p><div id="retargeting"></div></article>
<article class="card"><h3>Vertical performance</h3><p class="desc">canonical vertical/source; Unclassified retained</p><div class="table-wrap"><table class="table" id="vertical-table"><thead><tr><th>Vertical</th><th>Leads</th><th>Sends</th><th>Responses</th><th>Meetings</th><th>SQLs</th><th>Won</th><th>Lost</th><th>Revenue</th></tr></thead><tbody></tbody></table></div></article></section>
<div class="band-title">BAND 3 · Outbound performance (across channels)</div><section class="grid five" id="outbound-totals"></section>
<section class="section-gap card"><div class="table-wrap"><table class="table" id="email-table"><caption>1 · Email campaigns</caption><thead><tr><th>Campaign</th><th>Sent</th><th>Delivered</th><th>Opened</th><th>Clicked</th><th>Replied</th><th>Bounced</th></tr></thead><tbody></tbody></table></div><p class="small-note">Missing provider events are not treated as zero.</p></section>
<section class="section-gap card"><div class="table-wrap"><table class="table" id="linkedin-table"><caption>2 · LinkedIn campaigns</caption><thead><tr><th>Campaign</th><th>Invites sent</th><th>Accepted</th><th>Msgs delivered</th><th>Opened</th><th>Replied</th></tr></thead><tbody></tbody></table></div></section>
<section class="section-gap card"><div class="table-wrap"><table class="table" id="sms-table"><caption>3 · SMS</caption><thead><tr><th>SMS campaign</th><th>Sent</th><th>Delivered</th><th>Replies</th><th>Failed</th></tr></thead><tbody></tbody></table></div></section>
<section class="section-gap card"><div class="table-wrap"><table class="table" id="voicemail-table"><caption>4 · Voicemail</caption><thead><tr><th>Voicemail</th><th>Drops sent</th><th>Delivered</th><th>Callbacks</th><th>Notes</th></tr></thead><tbody></tbody></table></div></section>
<div class="band-title">BAND 4 · SDR performance — inputs &amp; outputs</div><section class="grid five" id="sdr-totals"></section>
<section class="section-gap card"><div class="table-wrap"><table class="table" id="sdr-table"><caption>Team call summary and per-SDR outputs</caption><thead><tr><th>SDR</th><th>Calls attempted</th><th>Connected</th><th>No pick</th><th>Booked</th><th>SQLs</th><th>MQL→SQL</th></tr></thead><tbody></tbody></table></div><p id="calls-source-note" class="small-note">Call totals source and owner attribution are reported by the facts API.</p></section>
<div class="band-title">BAND 5 · Social media</div><section class="grid five" id="social-totals"></section>
<section class="section-gap card"><div class="table-wrap"><table class="table" id="social-table"><caption>Summary by channel</caption><thead><tr><th>Channel</th><th>Posts</th><th>Impressions</th><th>Reach</th><th>Engagement</th><th>Followers</th></tr></thead><tbody></tbody></table></div><p class="small-note">N/A means the account-statistics source did not provide the metric.</p></section>
<div class="band-title">BAND 6 · Action queue</div><section class="card" id="actions"></section><p class="foot">V1 build · real values from the Executive Summary API, Campaign Channel Summary, GHL snapshots, appointment records, channel ledgers, and Social Planner data. The original report is not modified.</p>
</main><script>
(function(){"use strict";var $=function(s){return document.querySelector(s)};var p=new URLSearchParams(location.search);var state={range:p.get("range")||"30d",from:p.get("from")||"",to:p.get("to")||"",loadId:0};
function n(v){return v===null||v===undefined||v===""?"—":Number(v).toLocaleString("en-US")}function safe(v){var d=document.createElement("div");d.textContent=String(v==null?"":v);return d.innerHTML}function val(o){for(var i=1;i<arguments.length;i++)if(o&&o[arguments[i]]!=null)return o[arguments[i]];return null}function pct(v){return v==null||isNaN(Number(v))?"—":(Number(v)*100).toFixed(0)+"%"}function metric(a,b,c){return '<div class="kpi"><div class="label">'+safe(a)+'</div><div class="value">'+safe(b)+'</div><div class="note">'+safe(c||"")+'</div></div>'}
function field(r,ks){for(var i=0;i<ks.length;i++)if(r&&r[ks[i]]!=null)return r[ks[i]];return null}function bar(el,a,empty){var node=$(el);if(!a||!a.length){node.innerHTML='<div class="empty">'+safe(empty||"No data captured")+'</div>';return}var max=Math.max.apply(null,a.map(function(x){return Number(x.value||0)}).concat([1]));node.innerHTML=a.slice(0,8).map(function(x){return '<div class="bar"><div class="barline"><span class="name" title="'+safe(x.label)+'">'+safe(x.label)+'</span><span class="track"><span class="fill" style="width:'+Math.min(100,Number(x.value||0)/max*100)+'%"></span></span><span class="num">'+n(x.value)+'</span></div></div>'}).join("")}
 function qs(path){var u=path+"?range="+encodeURIComponent(state.range);if(state.from&&state.to)u+="&from="+encodeURIComponent(state.from)+"&to="+encodeURIComponent(state.to);return u}function wait(ms){return new Promise(function(resolve){setTimeout(resolve,ms)})}function get(label,u,attempt){attempt=attempt||0;var retry=attempt?u+"&lt_retry="+Date.now():u;return fetch(retry,{headers:{Accept:"application/json"}}).then(function(r){return r.text().then(function(body){if(!r.ok)throw Error(label+" HTTP "+r.status);if(!body||!body.trim())throw Error(label+" returned an empty response");var x;try{x=JSON.parse(body)}catch(e){throw Error(label+" returned invalid JSON")};if(!x||typeof x!=="object"||Array.isArray(x)||!Object.keys(x).length)throw Error(label+" returned an empty data object");return x})}).catch(function(e){if(attempt<2)return wait(attempt?3000:1200).then(function(){return get(label,u,attempt+1)});throw e})}
function health(d,f){var hs=(Array.isArray(d.health)?d.health:[]).concat(Array.isArray(f&&f.v1Health)?f.v1Health:[]),seen={};hs=hs.filter(function(x){var k=String(x.source_system||x.source||"source");if(seen[k])return false;seen[k]=true;return true});$("#health").innerHTML=hs.slice(0,16).map(function(x){var ok=/ready|success/i.test(String(x.status||x.state||""));return '<span class="'+(ok?"":"bad")+'">'+safe(x.source_system||x.source||"source")+': '+safe(x.status||x.state||"unknown")+'</span>'}).join("")||'<span class="bad">Source health unavailable</span>'}
function headline(d,f){var s=d.summary||{},m=d.mqlSummary||{},c=d.leadSourceCoverage||{},ms=f&&f.meetingSummary||{},g=f&&f.authoritativeGhlCounts||{},fu=f&&f.funnel||d.funnel||{};var sql=val(fu,"sqls_entered");if(sql==null)sql=val(g,"sqls_entered");if(sql==null)sql=val(s,"sqlsCreated","sqlContactsCreated");var mql=val(fu,"mqls_entered");if(mql==null)mql=val(g,"mqls_entered");if(mql==null)mql=val(m,"enteredMqls","mqlsEntered","totalMqls");var contacts=val(g,"new_contacts");if(contacts==null)contacts=val(s,"contactsCreated","leadsNumeric");var opps=val(fu,"opportunities_created");if(opps==null)opps=val(g,"opportunities_created");if(opps==null)opps=val(s,"opportunitiesCreated");var meetings=val(ms,"unique_contacts");if(meetings==null)meetings=val(s,"meetingsBooked","appointmentTotal");var basis=fu.basis||g.basis||"selected period";$("#headline").innerHTML=[metric("Opportunities created",n(opps),basis),metric("MQLs entered",n(mql),basis),metric("SQLs entered",n(sql),basis),metric("MQL→SQL",fu.mql_to_sql_rate==null?n(val(m,"convertedThisPeriod","convertedToSql","mqlToSql")):pct(fu.mql_to_sql_rate),"distinct opportunity basis"),metric("Meetings booked",n(meetings),ms.unique_contacts!=null?"unique Cameron contacts":"appointments basis"),metric("Closed SQLs",fu.closed_won_sqls==null&&fu.closed_lost_sqls==null?"—":n(Number(fu.closed_won_sqls||0)+Number(fu.closed_lost_sqls||0)),"won + lost"),metric("Revenue",fu.revenue==null?"—":n(fu.revenue),"closed-won value"),metric("New contacts",n(contacts),basis)].join("")}
function feedback(d,f){var x=f&&f.funnel||d.funnel||{};$("#funnel-metrics").innerHTML=[metric("Opportunities",n(x.opportunities_created),x.available===false?"Unavailable":"distinct opportunity IDs"),metric("MQLs",n(x.mqls_entered),"first observed MQL entry"),metric("SQLs",n(x.sqls_entered),"first Sales Outreach entry"),metric("SQL→Closed",x.sql_to_closed_rate==null?"—":pct(x.sql_to_closed_rate),"closed won + lost / SQLs"),metric("Revenue",x.revenue==null?"—":n(x.revenue),"closed-won value")].join("");$("#funnel-note").textContent=x.available===false?"Funnel facts unavailable: "+(x.reason||"source health is not ready")+". No zero substituted.":"Basis: "+(x.basis||"distinct opportunity IDs; America/Los_Angeles window")+" · health: "+(x.source_health||"not reported");var closed=Array.isArray(f&&f.closedBySource)?f.closedBySource:(Array.isArray(d.closedBySource)?d.closedBySource:[]);table("#closed-sources",closed,[["source"],["won"],["lost"],["revenue"]],"No closed-outcome source rows returned");var weeks=Array.isArray(f&&f.weeklyLeadFlow)?f.weeklyLeadFlow:[];$("#weekly-table tbody").innerHTML=weeks.length?weeks.map(function(w){return '<tr><td>'+safe(w.week_start||"Unknown")+'</td><td>'+n(w.new_contacts)+'</td><td>'+n(w.mqls_entered)+'</td><td>'+n(w.sqls_entered)+'</td><td>'+n(w.later_stage_entries)+'</td><td>'+safe((w.current_stage_distribution||[]).map(function(s){return (s.stage||"Unknown")+": "+n(s.count)}).join(", ")||"—")+'</td></tr>'}).join(""): '<tr><td colspan="6" class="unavailable">Weekly lead movement is unavailable; no zero substituted.</td></tr>';var v=Array.isArray(f&&f.verticalPerformance)?f.verticalPerformance:[];$("#vertical-table tbody").innerHTML=v.length?v.map(function(x){return '<tr><td>'+safe(x.vertical||"Unclassified")+'</td><td>'+n(x.leads)+'</td><td>'+n(x.sends)+'</td><td>'+n(x.responses)+'</td><td>'+n(x.meetings)+'</td><td>'+n(x.sqls)+'</td><td>'+n(x.won)+'</td><td>'+n(x.lost)+'</td><td>'+n(x.revenue)+'</td></tr>'}).join(""): '<tr><td colspan="9" class="unavailable">Vertical facts are unavailable; no zero substituted.</td></tr>';var r=f&&f.retargeting||d.retargeting||{};$("#retargeting").innerHTML=r.available===false?'<div class="unavailable">Retargeting facts unavailable; no send authorization inferred.</div>':'<div class="metric"><span>Eligible contacts</span><strong>'+n(r.eligible)+'</strong></div><div class="metric"><span>Suppressed or replied</span><strong>'+n(r.suppressed_or_replied)+'</strong></div><div class="metric"><span>Next action pending</span><strong>'+n(r.next_action_pending)+'</strong></div><p class="small-note">Latest touchpoints: '+n((r.latest_touchpoints||[]).length)+' · automatic sends authorized: '+(r.send_authorized===true?"yes":"no")+'</p>'}
function story(d,f){var src=Array.isArray(d.opportunitySourceBreakdown)?d.opportunitySourceBreakdown:(Array.isArray(d.contactSources)?d.contactSources:[]),mech=Array.isArray(f&&f.contactMechanisms)?f.contactMechanisms:[],ls=Array.isArray(d.leadSourceBreakdown)?d.leadSourceBreakdown:[],c=d.leadSourceCoverage||{};bar("#opp-sources",src.map(function(x){return{label:x.source||x.medium||"Unknown",value:field(x,["opportunities","opps","count"])}}).filter(function(x){return x.value!=null}),"No source-attributed opportunities");bar("#contact-sources",(mech.length?mech:src).map(function(x){return{label:x.mechanism||x.source||x.medium||"Unknown",value:field(x,["count","contacts"])}}),"No contact-source data");bar("#mql-sources",ls.map(function(x){return{label:x.source||x.medium||"Unknown / Unattributed",value:field(x,["mqls_entered","mqlsEntered","mqls"])}}).filter(function(x){return x.value!=null}),"No MQL source data");bar("#sql-sources",ls.map(function(x){return{label:x.source||x.medium||"Unknown / Unattributed",value:field(x,["sqls_created","sqlsCreated","sqls"])}}).filter(function(x){return x.value!=null}),"No SQL source data");$("#mql-coverage").textContent="Coverage: "+n(c.mqlsAttributed)+" / "+n(c.mqlsTotal);$("#sql-coverage").textContent="Coverage: "+n(c.sqlsAttributed)+" / "+n(c.sqlsTotal);var r=Number(c.sqlsTotal)?Number(c.sqlsAttributed||0)/Number(c.sqlsTotal):null;$("#coverage-rate").textContent=r==null?"—":pct(r);$("#coverage-detail").textContent=r==null?"SQL coverage unavailable":n(c.sqlsAttributed)+" / "+n(c.sqlsTotal)+" SQLs attributed";var qRows=(d.pipelineDropoff||[]).filter(function(x){return /qualif|mql/i.test(String(x.stage||x.label||""))}),q=qRows.length?qRows.reduce(function(a,x){var v=field(x,["value","stageCount","active_opportunities"]);return v==null?a:Number(a)+Number(v)},0):null;$("#pipeline-work").textContent=n(q)}
function meetings(d,f){var details=Array.isArray(f&&f.appointmentDetails)?f.appointmentDetails:[],ms=f&&f.meetingSummary||{};$("#meetings-detail").innerHTML=details.length?details.slice(0,6).map(function(x){return '<div class="metric"><span>'+safe(x.contact_name||x.contact||x.name||(x.contact_id?"Contact "+x.contact_id:"Unknown"))+'</span><span>'+safe(x.start_at||x.start||"")+'</span></div>'}).join(""):'<div class="empty">Meeting detail is not currently returned by the V1 facts API.</div>';var a=details.length?details.reduce(function(m,x){var k=String(x.status||"").toLowerCase();m[k]=(m[k]||0)+1;return m},{}):(Array.isArray(d.appointments)?d.appointments.reduce(function(m,x){m[String(x.status||"").toLowerCase()]=Number(x.count||0);return m},{}):{});["showed","no-show","cancelled","rescheduled"].forEach(function(k){$("#meeting-outcomes").innerHTML+='<div class="right"><strong>'+n(Object.prototype.hasOwnProperty.call(a,k)?a[k]:null)+'</strong><div class="sub">'+k+'</div></div>'});$("#meeting-note").textContent=details.length?(ms.unique_contacts!=null?"Regulated Ads On Social/Search: "+n(ms.unique_contacts)+" unique contacts across "+n(ms.appointment_rows)+" appointment rows; canceled/rescheduled contacts counted once.":"Recorded GHL appointment statuses; not inferred."):"Appointment outcome data unavailable; no zero substituted."}
function table(id,arr,keys,empty){var b=$(id+" tbody");b.innerHTML=arr.length?arr.map(function(x){return '<tr>'+keys.map(function(k,i){return '<td>'+safe(i===0?(x.campaign||x.name||"Unknown"):n(field(x,k)))+'</td>'}).join("")+'</tr>'}).join(""):'<tr><td colspan="'+keys.length+'" class="unavailable">'+safe(empty||"No data captured")+'</td></tr>'}
function outbound(d,c,f){var r=Array.isArray(c&&c.campaignChannelBreakdown)?c.campaignChannelBreakdown:[],em=r.filter(function(x){return /email/i.test(x.channel||"")}),li=r.filter(function(x){return /linkedin/i.test(x.channel||"")}),sum=function(ch,k,filter){var rows=r.filter(function(x){return String(x.channel||"").toLowerCase()===ch&&(!filter||filter(x))});if(!rows.length)return null;var vals=rows.map(function(x){return field(x,[k])});if(vals.some(function(v){return v==null||v===""||isNaN(Number(v))}))return null;return vals.reduce(function(a,v){return a+Number(v)},0)},isNewsletter=function(x){return /newsletter/i.test(String(x.campaign||x.name||""))};table("#email-table",em,[["campaign","name"],["email_sent","sent"],["email_delivered","delivered"],["email_opened","opened"],["email_clicked","clicked"],["email_replies","replied"],["email_bounced","bounced"]],"No email campaign rows returned");table("#linkedin-table",li,[["campaign","name"],["linkedin_invites","invites_sent"],["linkedin_accepted","accepted"],["linkedin_dms","msg_delivered"],["linkedin_opened","opened"],["linkedin_replies","replied"]],"No LinkedIn campaign rows returned");var sms=(c&&c.smsSummary)||d.smsSummary||{};table("#sms-table",[{campaign:"All SMS",sent:field(sms,["sent"]),delivered:field(sms,["delivered"]),replies:field(sms,["replies"]),failed:field(sms,["failed"])}],[["campaign"],["sent"],["delivered"],["replies"],["failed"]],"SMS unavailable");var v=f&&f.voicemailSummary||null,hasV=v&&Number(v.unique_contacts_with_latest_disposition)>0;$("#voicemail-table tbody").innerHTML=hasV?'<tr><td>Latest Vapi custom disposition</td><td>'+n(v.voicemail_drops_unique)+' unique contacts</td><td>'+n(v.voicemail_delivered_unique)+' unique contacts</td><td>'+n(v.callbacks_unique)+' unique contacts</td><td>Latest disposition per unique contact; voicemail selected means left; drops and delivered are unique-contact counts.</td></tr>':'<tr><td colspan="5" class="unavailable">No Vapi custom disposition facts captured for this period.</td></tr>';$("#outbound-totals").innerHTML=[metric("Emails sent",n(sum("email","email_sent")),"campaign ledger"),metric("LinkedIn msgs",n(sum("linkedin","linkedin_dms")),"activity ledger"),metric("SMS",n(field(sms,["sent"])),"provider ledger"),metric("Voicemails",hasV?n(v.voicemail_delivered_unique):"—",hasV?"unique latest dispositions":"no disposition facts"),metric("Newsletters",n(sum("email","email_sent",isNewsletter)),"newsletter campaign rows")].join("")}
function sdr(d,f){var s=Array.isArray(d.sdrPerformance)?d.sdrPerformance:[],x=f&&f.callTotals||d.summary||{},by=Array.isArray(f&&f.callsBySdr)?f.callsBySdr:[],basis=String(x.basis||"GHL call facts; source coverage not confirmed");$("#sdr-totals").innerHTML=[metric("Calls attempted",n(val(x,"attempted","callTotal","callOutcomeTotal")),basis),metric("Connected",n(val(x,"connected","callAnsweredCount")),basis),metric("No answer",n(val(x,"no_answer","callMissedCount")),basis),metric("Busy/failed",n(val(x,"busy_failed")),basis),metric("Wrong number",n(val(x,"wrong_number")),basis),metric("Unknown/other",n(val(x,"unknown")),basis)].join("");$("#calls-source-note").textContent=basis;var byName={};by.forEach(function(a){byName[String(a.sdr||"")]=a});$("#sdr-table tbody").innerHTML=s.length?s.map(function(a){var name=a.owner_name||a.owner||a.name||"Unassigned",call=byName[name]||{};return '<tr><td>'+safe(name)+'</td><td>'+n(call.attempted)+'</td><td>'+n(call.connected)+'</td><td>'+n(call.no_answer)+'</td><td>'+n(field(a,["booked","meetings_booked"]))+'</td><td>'+n(field(a,["sqls_created","sqls"]))+'</td><td>'+n(field(a,["mqls_converted","mql_to_sql"]))+'</td></tr>'}).join(""):'<tr><td colspan="7" class="unavailable">No SDR performance rows returned</td></tr>'}
function social(d,f){var s=d.socialPosts||{},stats=Array.isArray(f&&f.socialStatistics)?f.socialStatistics:[],all=stats.find(function(x){return String(x.scope||"").toLowerCase()==="all"})||{};var posts=all.posts!=null?all.posts:s.totalPosts,impressions=all.impressions!=null?all.impressions:s.totalImpressions,reach=all.reach!=null?all.reach:s.totalReach,followers=all.followers!=null?all.followers:s.accountFollowers,engagement=all.likes!=null?Number(all.likes||0)+Number(all.comments||0):Number(s.totalLikes||0)+Number(s.totalComments||0)+Number(s.totalShares||0);$("#social-totals").innerHTML=[metric("Posts",n(posts),"post placements"),metric("Impressions",impressions==null?"N/A":n(impressions),"account statistics"),metric("Reach",reach==null?"N/A":n(reach),"account statistics"),metric("Engagement",n(engagement),"likes + comments"),metric("Followers",followers==null?"N/A":n(followers),"account statistics")].join("");$("#social-table tbody").innerHTML="";var platforms={};stats.forEach(function(x){if(x.platform)platforms[String(x.platform).toLowerCase()]=x});[{name:"LinkedIn",key:"linkedin",p:s.linkedinCount},{name:"Instagram",key:"instagram",p:s.instagramCount},{name:"Facebook",key:"facebook",p:s.facebookCount}].forEach(function(x){var a=platforms[x.key]||{};$("#social-table tbody").innerHTML+='<tr><td>'+x.name+'</td><td>'+n(a.posts!=null?a.posts:x.p)+'</td><td>'+(a.impressions==null?"N/A":n(a.impressions))+'</td><td>'+(a.reach==null?"N/A":n(a.reach))+'</td><td>'+(a.likes==null?"N/A":n(Number(a.likes||0)+Number(a.comments||0)))+'</td><td>'+(a.followers==null?"N/A":n(a.followers))+'</td></tr>'})}
function responseSla(f){var rows=Array.isArray(f&&f.responseSla)?f.responseSla:[],inbound=rows.reduce(function(a,x){return a+Number(x.inbound_events||0)},0),responded=rows.reduce(function(a,x){return a+Number(x.responded||0)},0),unmatched=rows.reduce(function(a,x){return a+Number(x.unmatched||0)},0),ambiguous=rows.reduce(function(a,x){return a+Number(x.ambiguous||0)},0),weighted=rows.reduce(function(a,x){return a+Number(x.avg_response_seconds||0)*Number(x.responded||0)},0),avg=responded?weighted/responded:null;$("#speed").textContent=avg==null?"—":(avg/3600).toFixed(1)+"h";$("#overdue").textContent=inbound? n(unmatched+ambiguous):"—";$("#response-sla-note").textContent=rows.length?"Across "+n(inbound)+" inbound events: "+n(responded)+" responded, "+n(unmatched)+" unmatched, and "+n(ambiguous)+" ambiguous. No response-time target is assumed.":"No inbound LinkedIn, call, or marketing-email reply facts were captured for this period."}
function actions(d){var m=d.mqlSummary||{};$("#actions").innerHTML='<div class="action"><span class="pill">MQL</span><span>'+n(val(m,"currentMqls","active"))+' MQLs awaiting Sales</span></div><div class="action"><span class="pill yellow">Contract</span><span>Unavailable — stale proposal source not captured</span></div><div class="action"><span class="pill yellow">Follow-up</span><span>Unavailable — follow-up SLA source not captured</span></div>'}
function render(d,c,f){$("#period-label").textContent=((d.window||{}).from||state.from||"")+" → "+((d.window||{}).to||state.to||"")+" · executive-v1";health(d,f);headline(d,f);story(d,f);$("#meeting-outcomes").innerHTML="";meetings(d,f);outbound(d,c,f);sdr(d,f);social(d,f);responseSla(f);actions(d)}function load(){var loadId=++state.loadId;$("#error").style.display="none";Promise.all([get("Executive Summary",qs("/api/report/executive/summary")),get("Campaign Channels",qs("/api/report/executive/campaign-channels")),get("V1 Facts",qs("/api/report/executive-v1/facts"))]).then(function(x){if(loadId===state.loadId)render(x[0],x[1],x[2])}).catch(function(e){if(loadId!==state.loadId)return;$("#error").textContent="Report data could not be loaded after 3 attempts: "+e.message+". No placeholder zeros were substituted.";$("#error").style.display="block"})}
$("#range").value=state.range;$("#from").value=state.from;$("#to").value=state.to;$("#period-form").addEventListener("submit",function(e){e.preventDefault();state.range=$("#range").value;state.from=$("#from").value;state.to=$("#to").value;history.replaceState(null,"","?range="+state.range+(state.from&&state.to?"&from="+state.from+"&to="+state.to:""));load()});load();})();
function feedback(d,f){var x=f&&f.funnel||d.funnel||{};$("#funnel-metrics").innerHTML=[metric("Opportunities",n(x.opportunities_created),x.available===false?"Unavailable":"distinct opportunity IDs"),metric("MQLs",n(x.mqls_entered),"first observed MQL entry"),metric("SQLs",n(x.sqls_entered),"first Sales Outreach entry"),metric("SQL→Closed",x.sql_to_closed_rate==null?"—":pct(x.sql_to_closed_rate),"closed won + lost / SQLs"),metric("Revenue",x.revenue==null?"—":n(x.revenue),"closed-won value")].join("");$("#funnel-note").textContent=x.available===false?"Funnel facts unavailable: "+(x.reason||"source health is not ready")+". No zero substituted.":"Basis: "+(x.basis||"distinct opportunity IDs; America/Los_Angeles window")+" · health: "+(x.source_health||"not reported");var closed=Array.isArray(f&&f.closedBySource)?f.closedBySource:(Array.isArray(d.closedBySource)?d.closedBySource:[]);$("#closed-sources").innerHTML=closed.length?closed.slice(0,8).map(function(a){return '<div class="metric"><span>'+safe(a.source||"Unknown / Unattributed")+'</span><span>won '+n(a.won)+' · lost '+n(a.lost)+' · revenue '+n(a.revenue)+'</span></div>'}).join(""): '<div class="unavailable">No closed-outcome source rows returned.</div>';var weeks=Array.isArray(f&&f.weeklyLeadFlow)?f.weeklyLeadFlow:[];$("#weekly-table tbody").innerHTML=weeks.length?weeks.map(function(w){return '<tr><td>'+safe(w.week_start||"Unknown")+'</td><td>'+n(w.new_contacts)+'</td><td>'+n(w.mqls_entered)+'</td><td>'+n(w.sqls_entered)+'</td><td>'+n(w.later_stage_entries)+'</td><td>'+safe((w.current_stage_distribution||[]).map(function(a){return (a.stage||"Unknown")+": "+n(a.count)}).join(", ")||"—")+'</td></tr>'}).join(""): '<tr><td colspan="6" class="unavailable">Weekly lead movement is unavailable; no zero substituted.</td></tr>';var v=Array.isArray(f&&f.verticalPerformance)?f.verticalPerformance:[];$("#vertical-table tbody").innerHTML=v.length?v.map(function(a){return '<tr><td>'+safe(a.vertical||"Unclassified")+'</td><td>'+n(a.leads)+'</td><td>'+n(a.sends)+'</td><td>'+n(a.responses)+'</td><td>'+n(a.meetings)+'</td><td>'+n(a.sqls)+'</td><td>'+n(a.won)+'</td><td>'+n(a.lost)+'</td><td>'+n(a.revenue)+'</td></tr>'}).join(""): '<tr><td colspan="9" class="unavailable">Vertical facts are unavailable; no zero substituted.</td></tr>';var r=f&&f.retargeting||d.retargeting||{};$("#retargeting").innerHTML=r.available===false?'<div class="unavailable">Retargeting facts unavailable; no send authorization inferred.</div>':'<div class="metric"><span>Eligible contacts</span><strong>'+n(r.eligible)+'</strong></div><div class="metric"><span>Suppressed or replied</span><strong>'+n(r.suppressed_or_replied)+'</strong></div><div class="metric"><span>Next action pending</span><strong>'+n(r.next_action_pending)+'</strong></div><p class="small-note">Latest touchpoints: '+n((r.latest_touchpoints||[]).length)+' · automatic sends authorized: '+(r.send_authorized===true?"yes":"no")+'</p>'}
function render(d,c,f){$("#period-label").textContent=((d.window||{}).from||state.from||"")+" → "+((d.window||{}).to||state.to||"")+" · executive-v1";health(d,f);headline(d,f);feedback(d,f);story(d,f);$("#meeting-outcomes").innerHTML="";meetings(d,f);outbound(d,c,f);sdr(d,f);social(d,f);responseSla(f);actions(d)}
 </script><!--<script>
/* Feedback metrics are intentionally isolated from the legacy V1 renderer. */
(function(){var q=new URLSearchParams(location.search),u="/api/report/executive-v1/facts?range="+(q.get("range")||"30d");if(q.get("from")&&q.get("to"))u+="&from="+q.get("from")+"&to="+q.get("to");function e(s){var x=document.createElement("div");x.textContent=s==null?"":String(s);return x.innerHTML}function n(v){return v==null||v===""?"—":Number(v).toLocaleString("en-US")}function k(t,v,z){return '<div class="kpi"><div class="label">'+e(t)+'</div><div class="value">'+e(v)+'</div><div class="note">'+e(z||"")+'</div></div>'}function set(id,v){var x=document.getElementById(id);if(x)x.innerHTML=v}fetch(u,{headers:{Accept:"application/json", "Cache-Control":"no-cache"}}).then(function(r){return r.json()}).then(function(f){var x=f.funnel||{};set("funnel-metrics",[k("Opportunities",n(x.opportunities_created),"distinct opportunity IDs"),k("MQLs",n(x.mqls_entered),"first observed stage entry"),k("SQLs",n(x.sqls_entered),"first Sales Outreach entry"),k("SQL→Closed",x.sql_to_closed_rate==null?"—":(Number(x.sql_to_closed_rate)*100).toFixed(0)+"%","closed outcomes / SQLs"),k("Revenue",x.revenue==null?"—":n(x.revenue),"closed-won value")].join(""));set("funnel-note",x.available===false?"Funnel facts unavailable; no zero substituted.":"Basis: "+(x.basis||"distinct opportunity IDs; America/Los_Angeles dates")+" · health: "+(x.source_health||"not reported"));var c=f.closedBySource||[];set("closed-sources",c.length?c.slice(0,8).map(function(a){return '<div class="metric"><span>'+e(a.source||"Unknown / Unattributed")+'</span><span>won '+n(a.won)+' · lost '+n(a.lost)+' · revenue '+n(a.revenue)+'</span></div>'}).join(""): '<div class="unavailable">No closed-outcome source rows returned.</div>');var w=f.weeklyLeadFlow||[];set("weekly-table",w.length?w.map(function(a){return '<tr><td>'+e(a.week_start||"Unknown")+'</td><td>'+n(a.new_contacts)+'</td><td>'+n(a.mqls_entered)+'</td><td>'+n(a.sqls_entered)+'</td><td>'+n(a.later_stage_entries)+'</td><td>'+e((a.current_stage_distribution||[]).map(function(b){return (b.stage||"Unknown")+": "+n(b.count)}).join(", ")||"—")+'</td></tr>'}).join(""): '<tr><td colspan="6" class="unavailable">Weekly lead movement unavailable; no zero substituted.</td></tr>');var v=f.verticalPerformance||[];set("vertical-table",v.length?v.map(function(a){return '<tr><td>'+e(a.vertical||"Unclassified")+'</td><td>'+n(a.leads)+'</td><td>'+n(a.sends)+'</td><td>'+n(a.responses)+'</td><td>'+n(a.meetings)+'</td><td>'+n(a.sqls)+'</td><td>'+n(a.won)+'</td><td>'+n(a.lost)+'</td><td>'+n(a.revenue)+'</td></tr>'}).join(""): '<tr><td colspan="9" class="unavailable">Vertical facts unavailable; no zero substituted.</td></tr>');var r=f.retargeting||{};set("retargeting",r.available===false?'<div class="unavailable">Retargeting facts unavailable; no send authorization inferred.</div>':'<div class="metric"><span>Eligible contacts</span><strong>'+n(r.eligible)+'</strong></div><div class="metric"><span>Suppressed or replied</span><strong>'+n(r.suppressed_or_replied)+'</strong></div><div class="metric"><span>Next action pending</span><strong>'+n(r.next_action_pending)+'</strong></div><p class="small-note">Automatic sends authorized: '+(r.send_authorized===true?"yes":"no")+'</p>')}).catch(function(){set("funnel-note","Feedback metrics unavailable; no zero substituted.")})})();
 </script>--></body></html>
````

## File: reports/embed/executive-v1/lt-exec-v1-authoritative-ghl-counts.sql
````sql
authoritative_ghl_counts AS (
  SELECT jsonb_build_object(
    'new_contacts', (
      SELECT COUNT(DISTINCT NULLIF(source_key,''))::int
      FROM report_raw_ghl_contacts
      WHERE (COALESCE(NULLIF(payload_json->>'createdAt','')::timestamptz, report_date::timestamptz)
             AT TIME ZONE 'America/Los_Angeles')::date BETWEEN $1::date AND $2::date
    ),
    'opportunities_created', (
      SELECT COUNT(DISTINCT NULLIF(source_key,''))::int
      FROM report_raw_ghl_opportunities
      WHERE (COALESCE(NULLIF(dimensions_json->>'source_created_at','')::timestamptz,
                      NULLIF(payload_json->>'createdAt','')::timestamptz,
                      NULLIF(payload_json->>'dateAdded','')::timestamptz,
                      report_date::timestamptz)
             AT TIME ZONE 'America/Los_Angeles')::date BETWEEN $1::date AND $2::date
    ),
    'mqls_entered', (
      SELECT COUNT(*)::int FROM (
        SELECT source_key, MIN(report_date)::date AS first_mql_date
        FROM report_raw_ghl_opportunities
        WHERE COALESCE(NULLIF(dimensions_json->>'pipeline_id',''), NULLIF(payload_json->>'pipelineId','')) = 'FRjpDZ1HWj3UPgczsu3t'
          AND COALESCE(NULLIF(dimensions_json->>'pipeline_stage_id',''), NULLIF(payload_json->>'pipelineStageId','')) = '3b3bd98d-cbb9-4c50-8cf3-b4eba29061c2'
        GROUP BY source_key
      ) x WHERE first_mql_date BETWEEN $1::date AND $2::date
    ),
    'sqls_entered', (
      SELECT COUNT(*)::int FROM (
        SELECT source_key, MIN(report_date)::date AS first_sql_date
        FROM report_raw_ghl_opportunities
        WHERE COALESCE(NULLIF(dimensions_json->>'pipeline_id',''), NULLIF(payload_json->>'pipelineId','')) = 'dhdlf3O4tymxFtHk4aqq'
        GROUP BY source_key
      ) x WHERE first_sql_date BETWEEN $1::date AND $2::date
    ),
    'basis', 'raw GHL snapshot facts; distinct contact/opportunity IDs; America/Los_Angeles dates'
  ) AS payload
)
````

## File: reports/embed/executive-v1/lt-exec-v1-data-materializer.sql
````sql
CREATE TABLE IF NOT EXISTS lt_exec_v1_contact_provenance (
  contact_id TEXT PRIMARY KEY,
  first_seen_at TIMESTAMPTZ,
  source TEXT,
  medium TEXT,
  campaign TEXT,
  acquisition_mechanism TEXT NOT NULL DEFAULT 'unknown',
  mechanism_evidence TEXT,
  is_backfill BOOLEAN NOT NULL DEFAULT FALSE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS lt_exec_v1_contact_provenance_mechanism_idx ON lt_exec_v1_contact_provenance (acquisition_mechanism);
CREATE INDEX IF NOT EXISTS lt_exec_v1_contact_provenance_first_seen_idx ON lt_exec_v1_contact_provenance (first_seen_at);
WITH latest AS (
  SELECT DISTINCT ON (source_key) NULLIF(source_key, '') AS contact_id, payload_json, dimensions_json, report_date, loaded_at
  FROM report_raw_ghl_contacts
  WHERE NULLIF(source_key, '') IS NOT NULL
  ORDER BY source_key, report_date DESC, loaded_at DESC
), normalized AS (
  SELECT contact_id,
    COALESCE(NULLIF(payload_json->>'createdAt','')::timestamptz, report_date::timestamptz) AS first_seen_at,
    COALESCE(NULLIF(payload_json->>'source',''), NULLIF(dimensions_json->>'source',''), NULLIF(payload_json->>'leadSource','')) AS source,
    COALESCE(NULLIF(payload_json->>'medium',''), NULLIF(dimensions_json->>'medium','')) AS medium,
    COALESCE(NULLIF(payload_json->>'campaign',''), NULLIF(dimensions_json->>'campaign','')) AS campaign,
    payload_json, lower(payload_json::text || ' ' || dimensions_json::text) AS haystack
  FROM latest
), classified AS (
  SELECT *,
    CASE
      WHEN haystack LIKE '%historical backfill%' OR haystack LIKE '%unipile-backfill%' OR haystack LIKE '%linkedin via unipile%' THEN 'linkedin_backfill'
      WHEN haystack LIKE '%apollo%' THEN 'apollo_upload'
      WHEN haystack LIKE '%form%' OR haystack LIKE '%website lead intake%' THEN 'form'
      WHEN haystack LIKE '%booking_widget%' OR haystack LIKE '%appointment%' THEN 'booking'
      WHEN COALESCE(source,'') <> '' OR COALESCE(medium,'') <> '' OR COALESCE(campaign,'') <> '' THEN 'attributed_source'
      ELSE 'unknown'
    END AS acquisition_mechanism,
    (haystack LIKE '%historical backfill%' OR haystack LIKE '%unipile-backfill%' OR haystack LIKE '%linkedin via unipile%') AS is_backfill
  FROM normalized
)
INSERT INTO lt_exec_v1_contact_provenance
  (contact_id, first_seen_at, source, medium, campaign, acquisition_mechanism, mechanism_evidence, is_backfill, payload_json, loaded_at)
SELECT contact_id, first_seen_at, source, medium, campaign, acquisition_mechanism,
  left(regexp_replace(haystack, '[\r\n]+', ' ', 'g'), 500), is_backfill, payload_json, NOW()
FROM classified
ON CONFLICT (contact_id) DO UPDATE SET
  first_seen_at=EXCLUDED.first_seen_at, source=EXCLUDED.source, medium=EXCLUDED.medium,
  campaign=EXCLUDED.campaign, acquisition_mechanism=EXCLUDED.acquisition_mechanism,
  mechanism_evidence=EXCLUDED.mechanism_evidence, is_backfill=EXCLUDED.is_backfill,
  payload_json=EXCLUDED.payload_json, loaded_at=NOW();
CREATE TABLE IF NOT EXISTS lt_exec_v1_appointment_facts (
  appointment_id TEXT PRIMARY KEY,
  contact_id TEXT,
  contact_name TEXT,
  calendar_id TEXT,
  assigned_user_id TEXT,
  status TEXT,
  start_at TIMESTAMPTZ,
  end_at TIMESTAMPTZ,
  attribution_confidence TEXT NOT NULL DEFAULT 'unresolved',
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO lt_exec_v1_appointment_facts
  (appointment_id, contact_id, contact_name, calendar_id, assigned_user_id, status, start_at, end_at, attribution_confidence, payload_json, loaded_at)
SELECT a.appointment_id, a.contact_id,
  COALESCE(NULLIF(c.payload_json->>'name',''), NULLIF(trim(concat_ws(' ', c.payload_json->>'firstName', c.payload_json->>'lastName')), '')),
  a.calendar_id, a.assigned_user_id, a.status, a.start_at, a.end_at,
  CASE WHEN NULLIF(a.contact_id,'') IS NULL THEN 'unresolved' WHEN NULLIF(a.assigned_user_id,'') IS NOT NULL THEN 'appointment_assigned' ELSE 'contact_only' END,
  a.payload_json, NOW()
FROM report_raw_ghl_appointments a
LEFT JOIN LATERAL (
  SELECT payload_json FROM report_raw_ghl_contacts c
  WHERE c.source_key=a.contact_id ORDER BY c.report_date DESC, c.loaded_at DESC LIMIT 1
) c ON TRUE
ON CONFLICT (appointment_id) DO UPDATE SET
  contact_id=EXCLUDED.contact_id, contact_name=EXCLUDED.contact_name, calendar_id=EXCLUDED.calendar_id,
  assigned_user_id=EXCLUDED.assigned_user_id, status=EXCLUDED.status, start_at=EXCLUDED.start_at,
  end_at=EXCLUDED.end_at, attribution_confidence=EXCLUDED.attribution_confidence,
  payload_json=EXCLUDED.payload_json, loaded_at=NOW();
CREATE TABLE IF NOT EXISTS lt_exec_v1_call_facts (
  call_key TEXT PRIMARY KEY,
  source_system TEXT NOT NULL,
  contact_id TEXT,
  sdr_user_id TEXT,
  direction TEXT,
  disposition TEXT,
  started_at TIMESTAMPTZ,
  ended_at TIMESTAMPTZ,
  campaign_id TEXT,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO lt_exec_v1_call_facts
  (call_key, source_system, contact_id, sdr_user_id, direction, disposition, started_at, ended_at, campaign_id, payload_json, loaded_at)
SELECT 'ghl:' || call_id, 'ghl', contact_id, assigned_user_id, direction, status, started_at,
  COALESCE(ended_at, started_at + make_interval(secs => GREATEST(COALESCE(duration_ms,0),0)::double precision / 1000.0)), NULL, payload_json, NOW()
FROM report_raw_ghl_calls WHERE NULLIF(call_id,'') IS NOT NULL
ON CONFLICT (call_key) DO UPDATE SET
  contact_id=EXCLUDED.contact_id, sdr_user_id=EXCLUDED.sdr_user_id, direction=EXCLUDED.direction,
  disposition=EXCLUDED.disposition, started_at=EXCLUDED.started_at, ended_at=EXCLUDED.ended_at,
  payload_json=EXCLUDED.payload_json, loaded_at=NOW();
INSERT INTO lt_exec_v1_call_facts
  (call_key, source_system, contact_id, sdr_user_id, direction, disposition, started_at, ended_at, campaign_id, payload_json, loaded_at)
SELECT 'vapi:' || a.call_id::text, 'vapi', a.contact_id, NULL, 'outbound', a.disposition, a.started_at, a.ended_at,
  q.campaign_id, to_jsonb(a), NOW()
FROM voice_call_attempt a JOIN voice_call_queue q ON q.queue_id=a.queue_id
ON CONFLICT (call_key) DO UPDATE SET
  contact_id=EXCLUDED.contact_id, disposition=EXCLUDED.disposition, started_at=EXCLUDED.started_at,
  ended_at=EXCLUDED.ended_at, campaign_id=EXCLUDED.campaign_id, payload_json=EXCLUDED.payload_json, loaded_at=NOW();
INSERT INTO report_source_health
  (source_system, status, last_success_at, last_attempt_at, last_row_count, stale_after_hours, last_error, metadata, updated_at)
SELECT 'exec_v1_contact_provenance', CASE WHEN (SELECT COUNT(*) FROM lt_exec_v1_contact_provenance)=0 THEN 'no_data' ELSE 'ready' END, NOW(), NOW(), (SELECT COUNT(*)::int FROM lt_exec_v1_contact_provenance), 48, NULL,
  jsonb_build_object('workflow_name','LT - Executive Report V1 Data Materializer', 'mechanism_counts',
    jsonb_object_agg(COALESCE(acquisition_mechanism,'unknown'), cnt)), NOW()
FROM (SELECT acquisition_mechanism, COUNT(*) cnt FROM lt_exec_v1_contact_provenance GROUP BY acquisition_mechanism) x
ON CONFLICT (source_system) DO UPDATE SET status=EXCLUDED.status,last_success_at=NOW(),last_attempt_at=NOW(),last_row_count=EXCLUDED.last_row_count,last_error=NULL,metadata=EXCLUDED.metadata,updated_at=NOW();
INSERT INTO report_source_health
  (source_system, status, last_success_at, last_attempt_at, last_row_count, stale_after_hours, last_error, metadata, updated_at)
SELECT 'exec_v1_appointment_facts', CASE WHEN COUNT(*)=0 THEN 'no_data' ELSE 'ready' END, NOW(), NOW(), COUNT(*)::int, 48, NULL,
  jsonb_build_object('workflow_name','LT - Executive Report V1 Data Materializer', 'unresolved', COUNT(*) FILTER (WHERE attribution_confidence='unresolved')), NOW()
FROM lt_exec_v1_appointment_facts
ON CONFLICT (source_system) DO UPDATE SET status=EXCLUDED.status,last_success_at=NOW(),last_attempt_at=NOW(),last_row_count=EXCLUDED.last_row_count,last_error=NULL,metadata=EXCLUDED.metadata,updated_at=NOW();
INSERT INTO report_source_health
  (source_system, status, last_success_at, last_attempt_at, last_row_count, stale_after_hours, last_error, metadata, updated_at)
SELECT 'exec_v1_call_facts', CASE WHEN COUNT(*)=0 THEN 'no_data' ELSE 'ready' END, NOW(), NOW(), COUNT(*)::int, 48, NULL,
  jsonb_build_object('workflow_name','LT - Executive Report V1 Data Materializer', 'source_counts',
    COALESCE((SELECT jsonb_object_agg(source_system,cnt) FROM (SELECT source_system, COUNT(*) cnt FROM lt_exec_v1_call_facts GROUP BY source_system) q), '{}'::jsonb)), NOW()
FROM lt_exec_v1_call_facts
ON CONFLICT (source_system) DO UPDATE SET status=EXCLUDED.status,last_success_at=NOW(),last_attempt_at=NOW(),last_row_count=EXCLUDED.last_row_count,last_error=NULL,metadata=EXCLUDED.metadata,updated_at=NOW();
SELECT json_build_object('status','completed','contacts',(SELECT COUNT(*) FROM lt_exec_v1_contact_provenance),'appointments',(SELECT COUNT(*) FROM lt_exec_v1_appointment_facts),'calls',(SELECT COUNT(*) FROM lt_exec_v1_call_facts)) AS result;
````

## File: reports/embed/executive-v1/lt-exec-v1-feedback-contract.sql
````sql
CREATE TABLE IF NOT EXISTS lt_exec_v1_inbound_priority_events (
  contact_id TEXT NOT NULL,
  source_event_id TEXT NOT NULL,
  channel TEXT NOT NULL CHECK (channel IN ('linkedin','call','voicemail','email')),
  event_at TIMESTAMPTZ NOT NULL,
  routing_reason TEXT NOT NULL,
  prior_opportunity_id TEXT,
  prior_stage_id TEXT,
  resulting_opportunity_id TEXT,
  resulting_stage_id TEXT,
  owner_id TEXT,
  disposition TEXT NOT NULL DEFAULT 'pending',
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (contact_id, source_event_id)
);
CREATE INDEX IF NOT EXISTS lt_exec_v1_priority_events_at_idx
  ON lt_exec_v1_inbound_priority_events (event_at);
CREATE INDEX IF NOT EXISTS lt_exec_v1_priority_events_channel_idx
  ON lt_exec_v1_inbound_priority_events (channel, disposition);
WITH windowed AS (
  SELECT * FROM lt_exec_v1_inbound_priority_events
  WHERE event_at >= $1::date AT TIME ZONE 'America/Los_Angeles'
    AND event_at < (($2::date + 1) AT TIME ZONE 'America/Los_Angeles')
), distinct_events AS (
  SELECT DISTINCT ON (contact_id, source_event_id) *
  FROM windowed ORDER BY contact_id, source_event_id, updated_at DESC
)
SELECT jsonb_build_object(
  'open_count', COUNT(*) FILTER (WHERE disposition IN ('routed','already_priority')),
  'created_in_window', COUNT(*) FILTER (WHERE disposition = 'created'),
  'by_source', COALESCE(jsonb_agg(jsonb_build_object('channel', channel, 'count', channel_count)), '[]'::jsonb),
  'basis', 'distinct contact_id + source_event_id; immutable inbound event key'
)
FROM distinct_events
JOIN (
  SELECT channel, COUNT(*)::int AS channel_count FROM distinct_events GROUP BY channel
) counts USING (channel);
````

## File: reports/embed/executive-v1/lt-exec-v1-response-sla.sql
````sql
CREATE TABLE IF NOT EXISTS lt_exec_v1_response_sla (
  inbound_event_key TEXT PRIMARY KEY,
  contact_id TEXT,
  channel TEXT NOT NULL,
  inbound_event_type TEXT NOT NULL,
  inbound_at TIMESTAMPTZ NOT NULL,
  response_event_key TEXT,
  response_at TIMESTAMPTZ,
  response_seconds BIGINT,
  response_status TEXT NOT NULL,
  campaign_key TEXT,
  source_workflow TEXT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS lt_exec_v1_response_sla_window_idx ON lt_exec_v1_response_sla (channel, inbound_at);
CREATE INDEX IF NOT EXISTS lt_exec_v1_response_sla_status_idx ON lt_exec_v1_response_sla (response_status, channel);
WITH marketing_email_sends AS (
  SELECT contact_id, release_ts AS sent_at
  FROM "DAN_Release_Log"
  WHERE COALESCE(status,'sent') NOT IN ('failed','error','cancelled') AND NULLIF(contact_id,'') IS NOT NULL AND release_ts IS NOT NULL
  UNION ALL
  SELECT ghl_contact_id, release_ts
  FROM "Emerald_Release_Log"
  WHERE COALESCE(status,'sent') NOT IN ('failed','error','cancelled') AND NULLIF(ghl_contact_id,'') IS NOT NULL AND release_ts IS NOT NULL
  UNION ALL
  SELECT ghl_contact_id, release_ts
  FROM partnership_release_log
  WHERE COALESCE(status,'sent') NOT IN ('failed','error','cancelled') AND NULLIF(ghl_contact_id,'') IS NOT NULL AND release_ts IS NOT NULL
  UNION ALL
  SELECT ghl_contact_id, sent_at
  FROM newsletter_send_log
  WHERE status IN ('sent','delivered','opened','clicked') AND sent_at IS NOT NULL AND NULLIF(ghl_contact_id,'') IS NOT NULL
), inbound AS (
  SELECT 'linkedin:' || event_key AS inbound_event_key, ghl_contact_id AS contact_id, 'linkedin' AS channel,
    event_type AS inbound_event_type, event_at AS inbound_at, campaign_key, workflow_name AS source_workflow
  FROM linkedin_activity_events
  WHERE event_type IN ('reply_received','inbound_reply') AND NULLIF(ghl_contact_id,'') IS NOT NULL
  UNION ALL
  SELECT 'email:' || COALESCE(NULLIF(e.source_event_id,''), e.id::text), e.contact_id, 'email', lower(e.event_type), e.event_ts,
    e.campaign_key, e.workflow_id
  FROM "Email_Events" e
  WHERE lower(e.event_type) IN ('replied','reply','inbound_reply','reply_received') AND NULLIF(e.contact_id,'') IS NOT NULL
    AND EXISTS (SELECT 1 FROM marketing_email_sends m WHERE m.contact_id=e.contact_id AND m.sent_at < e.event_ts)
  UNION ALL
  SELECT 'call:ghl:' || call_id, contact_id, 'phone', 'inbound_call', started_at, NULL, 'report_raw_ghl_calls'
  FROM report_raw_ghl_calls
  WHERE lower(COALESCE(direction,'')) = 'inbound' AND NULLIF(contact_id,'') IS NOT NULL AND started_at IS NOT NULL
), outbound AS (
  SELECT 'linkedin:' || event_key AS response_event_key, ghl_contact_id AS contact_id, 'linkedin' AS channel, event_at AS response_at, campaign_key
  FROM linkedin_activity_events WHERE event_type = 'dm_sent' AND NULLIF(ghl_contact_id,'') IS NOT NULL
  UNION ALL
  SELECT 'email:dan:' || id::text, contact_id, 'email', release_ts, campaign_key
  FROM "DAN_Release_Log" WHERE COALESCE(status,'sent') NOT IN ('failed','error','cancelled') AND NULLIF(contact_id,'') IS NOT NULL
  UNION ALL
  SELECT 'email:emerald:' || id::text, ghl_contact_id, 'email', release_ts, campaign_key
  FROM "Emerald_Release_Log" WHERE COALESCE(status,'sent') NOT IN ('failed','error','cancelled') AND NULLIF(ghl_contact_id,'') IS NOT NULL
  UNION ALL
  SELECT 'email:partnership:' || id::text, ghl_contact_id, 'email', release_ts, campaign_key
  FROM partnership_release_log WHERE COALESCE(status,'sent') NOT IN ('failed','error','cancelled') AND NULLIF(ghl_contact_id,'') IS NOT NULL
  UNION ALL
  SELECT 'email:newsletter:' || id::text, ghl_contact_id, 'email', sent_at, campaign_key
  FROM newsletter_send_log WHERE status IN ('sent','delivered','opened','clicked') AND sent_at IS NOT NULL AND NULLIF(ghl_contact_id,'') IS NOT NULL
  UNION ALL
  SELECT 'call:ghl:' || call_id, contact_id, 'phone', started_at, NULL
  FROM report_raw_ghl_calls
  WHERE lower(COALESCE(direction,'')) = 'outbound' AND NULLIF(contact_id,'') IS NOT NULL AND started_at IS NOT NULL
  UNION ALL
  SELECT 'call:vapi:' || a.call_id::text, a.contact_id, 'phone', a.started_at, NULL
  FROM voice_call_attempt a
  WHERE NULLIF(a.contact_id,'') IS NOT NULL AND a.started_at IS NOT NULL
), matched AS (
  SELECT i.*, o.response_event_key, o.response_at,
    EXTRACT(EPOCH FROM (o.response_at - i.inbound_at))::bigint AS response_seconds,
    CASE WHEN o.response_event_key IS NULL THEN 'unmatched'
         WHEN o.same_timestamp_count > 1 THEN 'ambiguous'
         ELSE 'responded' END AS response_status,
    COALESCE(o.campaign_key, i.campaign_key) AS final_campaign_key
  FROM inbound i
  LEFT JOIN LATERAL (
    SELECT o.response_event_key, o.response_at, o.campaign_key,
      COUNT(*) OVER (PARTITION BY o.response_at) AS same_timestamp_count
    FROM outbound o
    WHERE o.contact_id=i.contact_id AND o.channel=i.channel AND o.response_at > i.inbound_at
    ORDER BY o.response_at, o.response_event_key
    LIMIT 1
  ) o ON TRUE
)
INSERT INTO lt_exec_v1_response_sla
  (inbound_event_key, contact_id, channel, inbound_event_type, inbound_at, response_event_key, response_at, response_seconds, response_status, campaign_key, source_workflow, loaded_at)
SELECT inbound_event_key, contact_id, channel, inbound_event_type, inbound_at, response_event_key, response_at, response_seconds, response_status, final_campaign_key, source_workflow, NOW()
FROM matched
ON CONFLICT (inbound_event_key) DO UPDATE SET
  contact_id=EXCLUDED.contact_id, channel=EXCLUDED.channel, inbound_event_type=EXCLUDED.inbound_event_type,
  inbound_at=EXCLUDED.inbound_at, response_event_key=EXCLUDED.response_event_key, response_at=EXCLUDED.response_at,
  response_seconds=EXCLUDED.response_seconds, response_status=EXCLUDED.response_status,
  campaign_key=EXCLUDED.campaign_key, source_workflow=EXCLUDED.source_workflow, loaded_at=NOW();
INSERT INTO report_source_health
  (source_system,status,last_success_at,last_attempt_at,last_row_count,stale_after_hours,last_error,metadata,updated_at)
SELECT 'exec_v1_response_sla', CASE WHEN COUNT(*)=0 THEN 'no_data' ELSE 'ready' END, NOW(), NOW(), COUNT(*)::int, 48, NULL,
  jsonb_build_object('workflow_name','LT - Executive Report V1 Response SLA Materializer',
    'responded',COUNT(*) FILTER (WHERE response_status='responded'),
    'unmatched',COUNT(*) FILTER (WHERE response_status='unmatched'),
    'channels',jsonb_object_agg(channel,channel_count)), NOW()
FROM lt_exec_v1_response_sla s
JOIN (SELECT channel,COUNT(*) channel_count FROM lt_exec_v1_response_sla GROUP BY channel) c USING(channel)
ON CONFLICT (source_system) DO UPDATE SET status=EXCLUDED.status,last_success_at=NOW(),last_attempt_at=NOW(),last_row_count=EXCLUDED.last_row_count,last_error=NULL,metadata=EXCLUDED.metadata,updated_at=NOW();
SELECT json_build_object('status','completed','facts',(SELECT COUNT(*) FROM lt_exec_v1_response_sla),'responded',(SELECT COUNT(*) FROM lt_exec_v1_response_sla WHERE response_status='responded'),'unmatched',(SELECT COUNT(*) FROM lt_exec_v1_response_sla WHERE response_status='unmatched')) AS result;
````

## File: reports/embed/executive-v1/MOCKUP-COMPARISON.md
````markdown
# V1 mockup comparison and data-completeness audit

Updated: 2026-09-24

## Result

The V1 page now follows the mockup's six-band flow. It is not yet complete-data ready: voicemail facts, the formal action queue, and some attribution/statistics coverage still do not exist in the current source layer. The page marks those details unavailable instead of displaying guessed or implicit zero values.

## Field-by-field status

| Mockup detail | V1 presentation | Data status | Required before calling complete |
|---|---|---|---|
| New MQLs | Headline card | Available through `mqlSummary` | Reconcile period definition with MQL source totals |
| New SQLs | Headline card | Available through SQL/coverage payload | Reconcile to SQL source rows |
| MQL→SQL | Headline card | Available when `mqlSummary` returns conversion | Confirm period basis and denominator |
| Meetings booked | Headline card | V1 now counts unique Cameron contact IDs | Cancellation/reschedule rows for the same contact count once; raw appointment rows remain available for audit |
| New contacts | Headline card | Available from summary | Add mechanism classification for the source-story card |
| Opportunities created | Headline card | Available from summary | Reconcile to source breakdown |
| Opportunities by source | Story card | Partially available via contact-source opportunity counts | Add a canonical source/opportunity fact table and Unknown bucket |
| MQL sources | Story card | Partially available via `leadSourceBreakdown` | Coverage must equal headline denominator |
| SQL sources | Story card | Partially available via `leadSourceBreakdown` | Coverage must equal headline denominator |
| New contacts — LinkedIn backfill / Apollo / form | Story card | Available through V1 contact provenance facts | Reconcile mechanism rows to the headline contact denominator and retain Unknown |
| Meetings — contact, SDR, link | Story card | Available through V1 appointment-detail facts | Contact names remain unavailable when the source snapshot has no name; preserve the contact ID and attribution confidence; headline uses distinct Cameron contacts |
| Showed / no-show / cancelled / rescheduled | Story card | Aggregate statuses may be available; missing statuses are now not shown as zero | Update appointment status after the meeting and expose all four status buckets |
| Pipeline to work | Story card | Current stage payload is not sufficient to guarantee the mockup definition | Define “qualified remaining” and return a dedicated count |
| Lead-source coverage | Story card | Available through `leadSourceCoverage` | Reconcile all denominators and show Unknown/Unattributed explicitly |
| Speed-to-lead | Story card | Collected in V1 response facts | Match inbound LinkedIn DM, inbound call, or marketing-email reply to the first later outbound event on the same channel; show average/median with denominator |
| Follow-up status | Story card | Unmatched inbound count collected; target not configured | Show inbound events without a matched same-channel reply; do not label them overdue until an approved response-time target exists |
| Email campaigns | Table | Available through Campaign Channel Summary | Verify delivered/open/click/reply/bounce event coverage and unique-recipient rate semantics |
| LinkedIn campaigns | Table | Available for ledger-backed activity | Add accepted/opened/delivered definitions where provider data exists; otherwise show unavailable |
| SMS | Table | Sent/failed/replies available; delivered may be source-dependent | Verify provider delivery event contract and campaign-level rows |
| Voicemail | Table | Drops/left and callback counts now available from latest custom disposition per unique contact | The approved rule treats selecting the voicemail disposition as voicemail left; drops and delivered intentionally use the same unique-contact count |
| Calls attempted / connected / no answer | SDR strip | Available through V1 canonical call facts | Uses `report_raw_ghl_calls` plus Vapi attempts and includes an explicit Unknown/Other bucket so totals reconcile |
| Calls by SDR | SDR table | Available through V1 call facts | Preserve Unassigned when the source has no owner; reconcile team and owner totals |
| Booked / SQLs / MQL→SQL by SDR | SDR table | Available through `sdrPerformance` | Reconcile owner coverage and Unassigned totals |
| Social posts | Social strip/table | Post placements available | Reconcile channel rows to total placements |
| Impressions / reach / followers | Social strip/table | May be unavailable without authenticated statistics | Ingest account statistics by platform/day or explicitly label unavailable |
| Action queue | Final band | MQL awaiting Sales is available; contract/follow-up are not | Define queue rules and return durable actionable records/counts |

## Accuracy rules now enforced in V1

- Missing values do not silently become zero in tables, cards, or outcome buckets.
- Source-health state is visible at the top of the page.
- An empty API response is treated as an error.
- Campaign tables preserve the API's campaign rows; the page does not invent attribution.
- Unavailable provider metrics are labelled `N/A` or `Unavailable`.

## Completion gate

The report should not be described as complete until every row marked “Required before calling complete” has a populated source, a documented definition, and a reconciliation test against the headline totals. The next implementation step is the reporting API/data-model work for those missing facts, followed by live-period QA and desktop/mobile visual QA.
````

## File: reports/embed/executive-v1/nginx-v1-location.conf
````ini
# Deployed in the report host configuration for the isolated V1 path.
location /api/report/executive-v1/facts {
    proxy_pass http://n8n:5678/webhook/lt-report-executive-v1-facts;
    proxy_set_header Host n8n;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto https;
    proxy_read_timeout 120s;
}
````

## File: reports/embed/executive-v1/PRIORITY-ROUTING-RUNBOOK.md
````markdown
# Priority routing implementation boundary

Live verification on 2026-09-26 confirms:

- Pipeline: `Sales Outreach` / `dhdlf3O4tymxFtHk4aqq`
- Stage: `Priority` / `be636da7-3c15-48ab-b589-c75bcd6f9955`
- Position: `1`, immediately before `New`
- Cold-outbound eligibility: explicitly excluded

The existing LinkedIn inbound workflow is `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`). The automation must cover four inbound-intent sources: inbound calls, voicemail-left call dispositions, LinkedIn DMs/replies, and qualifying human email replies. Existing partnership email handlers are separate and must be adapted only after their qualifying-event filter is confirmed. The routing implementation must be attached after contact resolution and before any non-idempotent opportunity mutation.

## Current draft

- Workflow: `LT - Inbound Intent Priority Router` (`URpjcm2k5isHUyls`)
- Active version: `3a3a6ab2-79a3-4fcc-822f-52677b6ae38c`
- State: active/published, `versionId == activeVersionId`; LinkedIn, Instagram, and SMS callers are attached after persistence/contact resolution. The execute-workflow trigger itself reports `triggerCount=0` because it is not a schedule/webhook trigger.
- Managed credentials: Postgres `pgAzUqpwOiGkGXzO`; GHL bearer `LIgX7IrOQoG1BusR`
- Supported normalized channels: `linkedin`, `instagram`, `sms`, `call`, `voicemail`, `email`

The draft was validated and branch-tested with pin data only. Create `1050280`, update `1050281`, already Priority `1050282`, closed protected `1050283`, duplicate terminal `1050284`, and ambiguous open `1050285` succeeded. Corrected no-op audit projection was retested in `1050290` and `1050291`. These executions bypassed Postgres and GHL side effects and are not production smoke tests.

## Required transaction boundary

The handler must first insert the `(contact_id, source_event_id)` key into `lt_exec_v1_inbound_priority_events` with `ON CONFLICT DO NOTHING` and acquire the contact lock in `lt_exec_v1_priority_contact_locks`. A conflict returns a duplicate result and stops. Only the row that won the claim may search or mutate GHL. A closed opportunity is an explicit no-op with `disposition=closed_protected`; one unambiguous open Sales Outreach opportunity is moved to Priority; a new Priority opportunity is created only when the reviewed contract permits it. Every result is written back to the same audit row and the contact lock is released.

No live inbound execution or outbound send is used as a test fixture. Verification uses a mocked GHL adapter and exact IDs; a production smoke test requires a real qualifying event and operator approval because it writes CRM data.

Before attachment, audit the exact source contract for each caller and confirm the real GHL opportunity search response shape. Required source fields are a resolved `contact_id`, stable `source_event_id`, `occurred_at`, normalized `channel`, qualifying `reason`, optional owner/name fields, and preserved source payload. LinkedIn, Instagram, SMS, calls/voicemail, and qualifying email replies now meet this boundary. No live CRM mutation smoke test has been run.

## LinkedIn caller contract

Read-only workflow and execution inspection accepted this mapping for `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`, active version `1208f803-7fb9-4bf5-a25a-e09181874ed2`):

| Router input | LinkedIn source field |
|---|---|
| `contact_id` | `ghl_contact_id` after contact resolution |
| `source_event_id` | Unipile `message_id` |
| `occurred_at` | normalized `timestamp` |
| `channel` | literal `linkedin` |
| `reason` | literal `linkedin_inbound_reply` |
| `contact_name` | `sender_name` |
| `payload` | normalized inbound event |

Executions `986965`/`986969` and `986966`/`986971` replayed the same two message IDs, validating `message_id` as the idempotency key. The caller gate must require `is_inbound=true`, `account_type=LINKEDIN`, `event_type=message_received`, and non-empty `ghl_contact_id`, `message_id`, and valid `timestamp`.

The caller is attached in published version `dd98c27b-0fca-491c-bac1-3ff38b1b147b` after main/partnership conversation-state persistence. The router performs a live contact-owner lookup before a create and returns `owner_unresolved` rather than creating an unassigned opportunity. No live CRM mutation smoke test has been run.

## Instagram and SMS caller contracts

- Instagram `pISlgYUsyJIrLuJd` is attached in published version `e09111d7-2c63-4925-b335-741c57f5ab5d` after the durable message claim, GHL contact/message handling, and mapping upsert. It uses the provider `message_id`, original message timestamp, resolved GHL contact ID, and `channel=instagram`.
- SMS `i0pROHpFtN4LYR0Q` is attached in published version `599995a9-72ce-467d-9892-c7ddf496c3fa` after event claim, contact resolution, and SMS state upsert. It uses the provider message ID and received timestamp. STOP/unsubscribe messages are intentionally excluded from Priority routing.
- Both caller branches invoke the router with non-blocking error handling, preserving the existing inbound persistence and response path if Priority routing fails.

## Call and voicemail caller contract

The protected production candidate is `LT - Call Outcome Ingest` (`PUCfTZBANSPcgS0c`). Do not attach its output as currently normalized. It allows an empty `contact_id` and can generate a random fallback source key. An accepted caller must require:

- `direction=inbound`
- resolved non-empty GHL `contact_id`
- valid original call timestamp
- stable GHL/provider `call_id`, or a verified deterministic composite of immutable call fields
- `channel=voicemail` only when the normalized disposition is voicemail; otherwise `channel=call`
- a fixed audited reason that distinguishes inbound call from voicemail-left disposition

`LT - GHL Call Outcomes Ingest` (`CFfNeRBRuo7YRBjl`) has a call-ID-first normalizer but lacks retained live executions and has an unauthenticated webhook boundary. It is not an accepted replacement without identifying the real GHL caller and verifying payload/authentication.

## Email caller contract

Current email workflows are insufficient for Priority routing:

- `SmMf8QIfysuxQJbG` has no durable event ID/timestamp and defaults to dry-run.
- `0SQ7tTk03okegp9V` and `hxiiYCpEfMuoSt5H` detect conversation-level inbound email but do not preserve message ID or inspect the actual sender/body.
- `ZrqFN8qLKO8eVHDc` supports message/provider/event IDs, but sampled live event payloads left them empty and were opens/clicks rather than replies.

Before attachment, fetch the actual inbound email message, require a stable message ID and original timestamp, and explicitly exclude bounce, unsubscribe, out-of-office/provider, and other automated events. Use `channel=email` and a fixed qualifying reason only after that filter passes.

## Retry boundary

Call/voicemail is published in `PUCfTZBANSPcgS0c` version `f9388b9a-ab70-45b2-bc77-4f5c2efef829`. DAN/Emerald email is published in `hxiiYCpEfMuoSt5H` version `6e60f832-f175-41a8-a4b7-193f286bef18`; partnership email is published in `mRDw57IHtnQe4wOo` version `42da3b2e-4b6a-4f2f-9341-880b36292eb4`. These branches qualify stable message/call events and invoke the router non-blockingly after persistence.

The five-minute lock self-recovers only when the same event is replayed. Caller branches are non-blocking after persistence so inbound handling is preserved, but a durable claimed-event reconciler remains the next hardening item for failures that are not replayed.
````

## File: reports/embed/executive-v1/priority-routing.test.js
````javascript
const decide = (
````

## File: reports/embed/executive-v1/README.md
````markdown
# Executive Report V1 workspace

This folder is an isolated working copy for the Executive Report V1 mockup.

## Operating boundary

- The current report remains at `reports/embed/executive/index.html` and must not be overwritten or removed.
- V1 will use the same report hostname through a separate URL path when it is ready for deployment.
- The mockup values are examples only. Every displayed value must come from a verified source or be labelled unavailable/not captured.
- This workspace is for preparation and review until a deployment is explicitly requested.

## Files

- `index.html` — V1 implementation using the existing Executive Summary and Campaign Channel APIs.
- `index.baseline.html` — preserved baseline copy used to compare future V1 changes.
- `mockup-v3.png` — supplied visual reference.
- `DATA-REQUIREMENTS.md` — metric definitions, source mapping, validation rules, and known gaps.
- `REPORTING-GAPS.reference.md` — copied reporting requirements and historical gap register.
- `REPORTS-README.reference.md` — copied report-host/API reference.

## Current implementation boundary

The page is intentionally conservative: it renders real values returned by the current APIs and shows `Unavailable`/`—` when the source does not provide a trustworthy value. Selecting the voicemail custom disposition is treated as a voicemail left; drops sent and delivered therefore use the same unique-contact count. Callback-requested counts come from the latest Vapi custom disposition per unique contact. Cameron's headline meetings KPI counts distinct contact IDs, so cancellation/reschedule rows do not double-count. Same-channel response speed is collected for inbound LinkedIn replies, inbound calls, and marketing-email replies; the report also shows unmatched inbound events. No overdue label is inferred because no business response-time target has been approved.

## Live n8n data layer

- `LT - Executive Report V1 Data Materializer` — workflow `knc2wxe4pyYIJ5tw`, active and published. Runs every 30 minutes and is also callable through `/webhook/lt-executive-report-v1-materializer`.
- `LT - Executive Report V1 Facts API` — workflow `oxYDg6XnRBKhl1Xd`, active and published. Read-only facts endpoint: `/webhook/lt-report-executive-v1-facts?from=YYYY-MM-DD&to=YYYY-MM-DD`.
- `LT - Executive Report V1 Response SLA Materializer` — workflow `KlBw3ThLbNlMfE2J`, active and published. Runs every 15 minutes and is also callable through `/webhook/lt-executive-report-v1-response-sla-materializer`.
- `/api/report/executive-v1/facts` is deployed through the report host's nginx proxy.

The latest controlled data-materializer run succeeded with 2,968 contact facts, 38 appointment facts, and 5,638 call facts (3,818 GHL + 1,820 Vapi). The latest response-SLA run succeeded with 236 durable inbound-response facts, including 107 matched responses and 129 unmatched inbound events; ambiguous candidates are tracked separately. These facts are additive; the existing raw reporting tables and current Executive Report were not changed.

## Count authority

V1 headline counts for new contacts, opportunities, MQLs, and SQLs now use distinct IDs and first-observed dates from raw GHL snapshot tables. They do not read `report_daily_summary` or depend on the daily rollup workflow. The raw GHL ingest and its freshness/row-count health remain prerequisites; a failed or stale ingest must be treated as unavailable rather than as zero.

Appointments and calls use the V1 raw-fact materialization, which is refreshed every 30 minutes. Channel tables and derived campaign metrics still use their channel ledgers/Campaign Channel Summary and are not represented as direct GHL headline counts.

The V1 page has passed an inline JavaScript syntax check and is deployed as a separate path on the report host. The current report path remains separate and unchanged.

## Deployed review URL

Use a separate path on the existing host, such as:

`https://reports.livetransparent.com/embed/executive-v1/`

The deployed review URL is `https://reports.livetransparent.com/embed/executive-v1/`. The current report remains at `https://reports.livetransparent.com/embed/executive/`.
````

## File: reports/embed/executive-v1/REPORTING-GAPS.reference.md
````markdown
# Reporting Gaps and Requirements

**Updated:** 2026-09-09
**Status:** Campaign attribution, SMS delivery diagnostics, opportunity counts, LinkedIn activity, partnership reply attribution, account-level social statistics, MQL-to-SQL movement, **SDR Performance / owner attribution (Phases 1–2)**, and the **MQL/SQL lead-source breakdown (Phase 4)** are live. Remaining: native GHL stage/tag/email/custom-metric widgets, GHL appointment-status update post-meeting (SDR Phase 3), and Team Active Deals glossary polish. See `docs/sessions/2026-09-09-executive-report-sdr-attribution-plan.md` (plan), `docs/sessions/2026-09-09-executive-report-sdr-attribution-phase1-2.md` (Phases 1–2 implementation), and `docs/sessions/2026-09-09-executive-report-sdr-attribution-phase4-lead-source.md` (Phase 4 implementation).

## Purpose

This document records what is missing from the native GHL report and the external Executive Report, and defines exactly what each report must show. It is the reporting acceptance checklist for the active DAN, Emerald, SMS, Vapi, LinkedIn, and Partnership systems.

## Verified Current State

### Executive Report

- Host: `https://reports.livetransparent.com`
- Current build: `2026-08-12-v23-mobile-overflow`
- Selected-period controls and prior equal-length comparison are live.
- Campaign Channel Summary is live and returns named campaign rows.
- Campaign rows remain separate for `DAN`, `Emerald`, `Partnership`, `Vapi Brand`, and `Vapi Dispensary`; Vapi activity is no longer rolled into DAN.
- Campaign rows include selected-window distinct opportunity counts matched from current campaign tags in `report_raw_ghl_opportunities`.
- SMS summary includes sent, failed, replies, and normalized failure reasons. The verified 2026-07-09 through 2026-08-07 window returned 294 sent, 1,095 failed, 0 replies; failure reasons were provider failure 1,010, duplicate send 63, unknown 16, invalid phone 5, and idempotent webhook error 1.
- In the current 30-day window, `Partnership emails` shows 59 sends, 1 reply, and a 1.69% response rate.
- In the current 30-day window, `Partnership LinkedIn` shows 17 invites and 3 replies.
- Verified historical replies are stored with provider timestamps: Strider Peterson email at `2026-08-03T15:41:03Z`; Jaret Christopher LinkedIn at `2026-08-01T03:05:55Z`; David Schachter LinkedIn (`rvWEW2K2WYeQ7v6zypDdZQ`) at `2026-08-10T15:09:07.711Z`; and Gretchen Gailey LinkedIn (`8UF3lxibUmKYaG87h1F5Pg`) at `2026-08-06T16:20:35.281Z`.
- Social post totals currently show 24 likes, 3 comments, and 4 shares. The UI also exposes saves, reach, and impressions, but the PIT-based post ingest currently supplies none of those fields.
- The Executive Report is the only current surface that can combine Postgres state, Unipile activity, GHL CRM data, and campaign joins.
- Outgoing Call Detail is live at the bottom of the report. It loads the seven most recent completed days, paginates at 100 rows, and displays contact ID/name fallback, phone, disposition, duration, first-attempt flag, campaign, and lazy signed recording playback.
- Outgoing Call Detail API: `GET /api/report/executive/outgoing-calls?range=7d&limit=100&offset=0`; nginx proxies to `GET /webhook/lt-report-outgoing-calls`.
- The detail endpoint is backed by n8n workflow `LT - Report Outgoing Calls Detail` (`VXFHc8IrF9DDEEdj`), published version `d004556d-0b11-4a86-8827-f8f58a1eeee3`.
- The aggregate `GHL Calls` panel and the outgoing Vapi detail table are separate surfaces: aggregate GHL call status facts remain sourced from `report_raw_ghl_call_outcomes`, while the detail table is sourced from `voice_call_attempt` plus `voice_call_queue`.

### Native GHL Report

- Report ID: `6a67dce4a51a4360c60963a3`
- The report is intended for operational CRM facts. Its saved date range is `Last 30 days`; the duplicate page-3 `Outgoing calls by status` widget was removed on 2026-08-08 and the report still has three content pages.
- The report-builder UI requires an authenticated GHL browser/Firebase session.
- A location PIT can read CRM data but cannot mutate native report widget layouts.
- `Campaign Opportunities` is filtered to `Pipeline Is Partnership Pipeline`.
- `Contacts by tag` uses `Tags Is one of` with `partner_candidate_email` + `partner_candidate_linkedin`, group-by Tags surfaces the full partner tag distribution (email 122, LinkedIn 93, email queued 59, LinkedIn requested 10 for the verified window).
- Added **Partnership Pipeline Opportunities** (count, `Pipeline Is Partnership Pipeline`), **Partnership Pipeline by Status** (grouped by Status, same pipeline), and **Closed Won Revenue** (`Won Opportunity value`).
- GHL offers **no native stage-group dimension** for opportunity widgets and **no group-by on the `Owner` custom field**; a per-row Pipeline dependency blocks a reliable Stage filter in the builder. MQL, Sales Outreach funnel, and owner breakdown therefore remain Executive Report / GHL opportunity-view concerns.
- No native widget currently represents Unipile LinkedIn invitations, LinkedIn acceptance, or LinkedIn DM activity.
- The native report must not be treated as a cross-channel campaign warehouse.

## Missing Items

### P0: LinkedIn Activity Ledger

**Implemented:** Partnership LinkedIn actions are attributed through durable, idempotent `linkedin_activity_events` rows. The requirements below remain the event contract for every LinkedIn action.

Use the existing `linkedin_activity_events` pattern or create a partnership-specific table that is UNIONed into it. Each event must contain:

- `event_id`: stable idempotency key
- `event_at`: provider/action timestamp
- `ghl_contact_id` and `location_id`
- `source_key`: `partnership`, `dan`, or another canonical campaign source
- `campaign_key`: `partnership_linkedin`
- `channel`: `linkedin`
- `event_type`: `connection_request_sent`, `connection_accepted`, `dm_sent`, `reply_received`, `sequence_completed`, `suppressed`, or `send_failed`
- `linkedin_profile_url`, `linkedin_public_identifier`, and `linkedin_provider_id`
- `unipile_account_id`
- `provider_message_id` or invitation id when available
- `workflow_id` and workflow name
- `status`: `sent`, `accepted`, `replied`, `failed`, `skipped`, or `suppressed`
- `error_code` and sanitized `error_detail` for failures
- `metadata_json` and `created_at`

The dispatcher must write `connection_request_sent` only after the Unipile request succeeds. The state-upsert response must be checked and failures must be recorded separately rather than silently ignored.

### P0: Partnership LinkedIn Campaign Attribution

Add a durable `Partnership LinkedIn` catalog row to the campaign summary and populate it from the activity ledger. The row must show invitations sent, invitations failed, connections accepted, DMs by step, replies, sequence completions, suppressions, response rate, acceptance rate, and current ready/requested/connected/completed state counts.

**Implemented 2026-07-31 through 2026-08-01**: the full LinkedIn activity ledger is now instrumented across all send/reply/suppression paths, all writing idempotently to `linkedin_activity_events`:

- `connection_request_sent` — Partnership LinkedIn Dispatcher (`crKIsaL5k3YBfqDZ`, after Unipile success) + reconciliation backfill from requested/connected state rows. The verified 2026-07-31 run shows 10 invites.
- `connection_accepted` — LinkedIn Connection Acceptance Checker (`3ttEvr5NMcQCS4Hp`), keyed per contact+provider, with partnership campaign routing via `source_table`.
- `dm_sent` — Canonical LinkedIn DM Sequence (`d0tEtijajisIsYcs`, parallel flatten→record path) and Partnership LinkedIn DM Sequence (`nspggypNF245xzeL`, `campaign_type='partnership'`).
- `reply_received` — LinkedIn Reply Backfill (`QfJ2EZcc7lZwNgxj`, per contact) and LinkedIn Unipile New Messages (`7o5EBdvwAuIaWW7k`, per inbound message). Reply Backfill now also carries `source_table` so partnership rows route correctly.
- `suppressed` + `sequence_completed` — LinkedIn DM Suppression from GHL Tag (`IPN8jnR3XSurX0o1`), written when a contact is suppressed.

All six workflows are active and published (versionId == activeVersionId). The Campaign Channel Summary routes partnership events to `Partnership LinkedIn` via `campaign_type`/`source_key = 'partnership'` and exposes `linkedin_invites`/`linkedin_accepted`/`linkedin_replies` columns. The selected-window row now shows 17 invites and 3 verified historical replies. `LT - LinkedIn Unipile New Messages` is published on `f96dafba-9818-4aab-8656-c2e4e2ab8480` with malformed form-payload field recovery. Still open: acceptance/completion rates and natural (non-suppression) `sequence_completed` events from the DM sequence completion branch.

### P0: Partnership Email Event Coverage

Partnership emails are sent inline through `POST /conversations/messages`, not through GHL template actions. Confirm that GHL open, click, bounce, complaint, unsubscribe, and reply events are emitted for these messages.

If GHL does not emit events consistently, correlate events using GHL message ID, conversation ID, contact ID, sender email, campaign key, and event timestamp. Do not fabricate engagement rates. Show `unavailable` or a source-coverage warning when event data is missing.

### P1: Native GHL Partnership Configuration

**Implemented 2026-08-01** through the authenticated GHL UI (15 widgets saved and verified):

- `Campaign Opportunities`: filtered to `Pipeline Is Partnership Pipeline`.
- `Contacts by tag` and `Contacts counts by tags (Partnership Campaign)`: `Tags Is one of` with `partner_candidate_email` + `partner_candidate_linkedin`; group-by Tags surfaces the full partner tag family distribution.
- Added `Partnership Pipeline Opportunities` (count), `Partnership Pipeline by Status` (grouped by Status), and `Closed Won Revenue` (`Won Opportunity value`).
- Shared report date range confirmed as `Last 30 days` (saved 2026-08-08) with no per-widget overrides.

Still open (builder limitations, not yet reliable via the report-builder UI):

- A Partnership Pipeline **stage** split (GHL opportunity widgets group by Status, not stage).
- The full `partner_*` tag set as explicit `Is one of` values where the tag list is virtualized; add `partner_email_queued`, `partner_linkedin_requested`, `partner_replied`, `partner_not_interested`, `partner_do_not_contact` when editing through a stable UI path.
- MQL / Sales Outreach funnel widget (per-row Pipeline dependency on the Stage filter).
- Owner and assignment breakdown widget (no group-by on the `Owner` custom field `Wpg7FGrQTgAY1GoKcdEJ`).
- Location-team sharing and read-only operator access confirmation.

Native GHL still will not show Unipile activity unless it is synchronized into GHL objects supported by the widget. The Executive Report remains authoritative for provider activity.

### P1: Reporting Owner Dimensions

Normalize contact owner, native opportunity owner, custom opportunity `Owner`, canonical SDR identity, owner conflict flag, assignment source, assignment timestamp, and unassigned Sales Outreach count in the reporting read model.

**Implemented 2026-09-09 (Phases 1–2)**:
- `report_sdr_registry` table (user-id → name → role → `is_sdr`) created in `postgres/reporting-bootstrap.sql` and applied on the live `postgres` DB. Seeded: Jason Bornillo (`yU85G6kfhtW4vUtx3QE6`, sdr), Marc (`sqGx5rp3oAUG610NXyjU`, sdr), Cameron Karkut (`03p5GatJBH7i9zjMaIzm`, leadership), Ed Cadorniga (`gePIeuHOEsAiPVA1mfOR`, exec). Pending IDs to identify before ranking: `ck6TRlU3wnTmMxuVpn5F` and Janvi.
- Daily Rollups (`EUeOiRttoVLQ9zF9`, active `1af59845…`) now carries `assigned_to` through `tmp_report_opps` and `tmp_daily_opps_fixed`.
- `LT - Report QA and Alerts` (`M5mXcDTFSko6EdHb`, active `a21c0f4a…`) adds two owner-coverage probes to `report_source_health`: `ghl_opp_owner_coverage` (34.6% assigned on latest snapshot, 3,618/10,466) and `ghl_appt_owner_coverage` (11/31 appointments attributable to an SDR via contact→opp owner).
- Exec Summary (`Bukc0mgOD2r7V6ED`, active `162bbba8…`) projects owner via native `assigned_to` (primary) with contact-owner fallback and an explicit `Unassigned` bucket, resolves names via `report_sdr_registry`, and returns `sdrPerformance` rows plus `leadSourceBreakdown`/`leadSourceCoverage`. The query now runs with `SET jit=off` (16–19s vs ~71s before).
- Opportunities: `report_raw_ghl_opportunities.dimensions_json->>'assigned_to'`; Appointments: `report_raw_ghl_appointments.assigned_user_id` + `contact_id`; Contacts: full object in `report_raw_ghl_contacts.payload_json`.

Remaining owner work: GHL appointment-status update so showed/no-show flows (Phase 3), and identifying the two unknown owner IDs.

### P1: Source Health and Coverage

Expose last successful sync, latest attempt, row count, selected-window coverage, and failure message for GHL contacts, opportunities, pipeline history, calls, appointments, email events, SimpleTexting events, Unipile LinkedIn activity, Vapi queue/outcomes, GA4, and GSC. GSC is currently live after OAuth renewal and must retain its health/coverage status. Historical SimpleTexting HTTP 409 failures are terminalized and reported; current provider acceptance remains unverified until approved live or natural traffic supplies a new result.

**Coverage probe added (2026-08-01)**: `LT - Report QA and Alerts` (`M5mXcDTFSko6EdHb`) now upserts `report_source_health` rows for `email_events` and `linkedin_activity_events` (max event freshness, row count, 24h staleness) on every hourly run before evaluating QA. Verified live: `email_events` ready/22,613 rows; `linkedin_activity_events` ready/10 rows (the verified partnership invites). Because the Executive Summary API reads all `report_source_health` rows dynamically, these now appear in the report `health` section without query changes.

**Social statistics blocker confirmed (updated 2026-08-17)**: the official GHL Social Planner statistics endpoint proves reach/impression data exists, but PIT access returns 401 and the active `ghl_oauth_tokens` row has an empty access token. The report therefore returns null and renders N/A for reach, impressions, and saves. Scheduled exact-range account analytics remain blocked until GHL OAuth is reconnected.

**Social accuracy audit completed (2026-08-17)**: Executive Summary counts both `inbound_reply` and `reply_received`. The completed 7-day window reports 8 verified GHL platform/account placements, 3 ledger likes, 2 LinkedIn requests, and 2 LinkedIn replies from 2 responders. LinkedIn Requested now includes both `requested` and `requested_pending`; separate subcounts preserve the state detail. Account statistics and post-ledger engagement remain separate metric families.

## Executive Report Requirements

### Shared Controls

- Range presets: `7d`, `30d`, `90d`, and `custom`.
- Custom dates: `from=YYYY-MM-DD` and `to=YYYY-MM-DD`.
- Shared sub-account reporting timezone.
- Selected period plus immediately preceding equal-length period.
- Current value, prior value, absolute change, and percentage change for every comparable metric.
- One selected window across all widgets.
- Explicit `unmatched`, `unknown`, and `source unavailable` buckets.

### Executive KPI Cards

Show current, prior, change, and definition for recorded visits/users, GHL contacts, MQLs, SQL contacts, opportunities, meetings, closed-won opportunities, closed-won revenue, email sent/opened/clicked/bounced/complained/unsubscribed, email rates, SMS sent/delivered/replied/failed/opted out, LinkedIn invites/accepted/DMs/replies, and Vapi calls/answered/qualified/booked.

### SDR Performance (IMPLEMENTED 2026-09-09 — Phases 1–2) and Lead Source (IMPLEMENTED 2026-09-09 — Phase 4)

Per-SDR breakouts for the end-of-month SDR assessment are live via the `sdrPerformance` payload + frontend panel. Definitions agreed with the operator (Cameron/Janvi sign-off still recommended on ranking scope):

- **Owner attribution field** — canonical SDR identity on every surfaced opportunity/appointment: native opportunity `assigned_to` primary, contact-owner fallback, custom opportunity `Owner` cross-check; names resolved via `report_sdr_registry`. Unassigned rolls into an explicit `Unassigned` row.
- **Booked Meetings by SDR** — Regulated Ads calendar (`SrtXcFVyea7pFl3nTiIK`) appointments windowed by `start_at`, attributed via appointment → contact → opportunity `assigned_to`. The top KPI `meetingsBooked` now uses this definition (`basis: appointments_start_at`; `meetingsBookedStageBasis` keeps the old opportunity-stage figure). Current 30d: 5 booked.
- **Meetings Showed / No-show / Cancelled by SDR** — status bucket per SDR. **"Showed" is still 0 because GHL `appointmentStatus` is never updated post-meeting — Phase 3 (GHL-side status-update automation) is required; the report query logic is correct.**
- **SQLs Created by SDR** — Sales Outreach opportunities created in the window grouped by owner (primary); the cumulative `sql`-tag contact count stays a secondary figure. Current 30d: Marc 156, Jason 8.
- **MQL → SQL conversion by SDR** — MQL opportunities that entered Sales Outreach in the window, grouped by owner. Current 30d: Marc 49, Jason 7.
- **Won / Lost / Revenue by SDR** — closed opportunities created in the window by owner (latest-snapshot status).
- **Lead source for MQL/SQL** — Phase 4 (implemented 2026-09-09): Exec Summary returns `leadSourceBreakdown` (per source+medium: MQLs Entered / SQLs Created in the window) and `leadSourceCoverage` (attributed/total). Resolution: contact first UTM source/medium/campaign → `report_bridge_traffic_to_lead` fallback → GHL contact `source`; rows without a resolvable source are grouped under "Unknown / Unattributed" (current 30d coverage bounded by the ~500-row Leads snapshot: 32/164 SQLs, 0/3 MQLs attributed).
- **"Team Active Deals"** — the team-wide opportunity payload relabeled as a deal-centred view; no owner filter is applied.

### Campaign Channel Table

Columns must include channel, campaign, SMS sent/failed/replies, email sent/opened/open rate/clicked/click rate/replies/response rate/bounced, LinkedIn invites or DMs/replies, Vapi calls/answered/qualified/booked, and selected-window distinct opportunities.

Required partnership rows:

- `Partnership emails`
- `Partnership LinkedIn`

### Outgoing Call Detail

The Executive Report must keep the following call-detail contract:

- Use only the seven most recent completed calendar days in `America/Los_Angeles`.
- Return a stable JSON payload with `calls`, `total`, `limit`, `offset`, and `range`.
- Cap one page at 100 rows and support non-negative offsets.
- Include call ID, contact ID/name fallback, phone, started/ended timestamps, status/disposition, duration seconds, first-attempt flag, campaign, and recording URL.
- Calculate duration from `ended_at - started_at`; null or missing end time falls back to zero-duration behavior rather than failing the whole report.
- Load recordings lazily and preserve provider-signed URL handling; do not put signed URLs in documentation or source control.
- Preserve an explicit contact-ID fallback when raw contact snapshots do not include a name.
- Keep this read-only endpoint separate from aggregate GHL call reporting and Vapi queue mutation workflows.

The 10 live test invites must appear in `Partnership LinkedIn`, not only in the overall LinkedIn KPI.

### LinkedIn Funnel

Show current state and selected-period activity for Ready, Requested, Connected, DM Active, DM Completed, Suppressed, requests sent, requests accepted, DMs by step, replies, acceptance rate, reply rate, completion rate, and provider/API failures.

Filters must include campaign key, source list, Brand versus Dispensary versus Partnership, owner, date window, and LinkedIn account.

### Partnership Detail

Show candidate counts by email and LinkedIn eligibility, email step distribution, email release status, LinkedIn request status, accepted connections, DM step and next eligible date, reply/suppression status, Partnership Pipeline stage, owner, contact/company/email/LinkedIn URL, and last activity timestamp.

## Native GHL Report Requirements

The native report should remain an operational CRM report, not a replacement for the Executive Report.

Required widgets:

1. Contacts created by reporting period. — **present** (via tag/contact widgets).
2. Contacts by source or campaign tag. — **present** (`Contacts by tag`, `Contacts counts by tags (Partnership Campaign)`).
3. Opportunities by pipeline and stage. — **partial**: `Opportunity counts by status` groups by Status; no native stage-group.
4. Partnership Pipeline opportunities by stage. — **partial**: `Partnership Pipeline Opportunities` (count) and `Partnership Pipeline by Status` (Status split) present; stage split not natively available.
5. MQL opportunities and MQL-to-SQL movement. — **live in the Executive Report** `mqlSummary` (total MQLs, converted to SQL via Sales Outreach pipeline, current MQLs awaiting sales, plus entered/converted in the selected window).
6. Meetings and appointments by calendar/status. — **present** (`Appointment count by status`).
7. Outbound email counts and engagement where GHL supports the event. — **present** (Accepted/Opened/Clicked/Hard bounced).
8. Outbound SMS counts and replies where GHL supports the event. — **present** (`SMS by status`).
9. Outbound call counts and answered status. — **present** (`Outgoing calls by status`).
10. Closed-won count and revenue. — **revenue present** (`Closed Won Revenue`); won-count is in `Opportunity counts by status`.
11. Owner and assignment breakdown. — **open** (no group-by on the `Owner` custom field; stays in GHL opportunity views / Executive Report).
12. Partnership contact and suppression tags. — **present** (partner tag widgets).

Every widget must use the shared report date range, have a documented filter, and identify whether it reads contacts, opportunities, conversations, appointments, or tags. No widget may imply it includes Unipile activity unless that activity has been synchronized into a supported GHL object.

## Data and API Work Required

1. Instrument the Partnership LinkedIn Dispatcher to write activity events after successful invite requests. — **done** (`crKIsaL5k3YBfqDZ`).
2. Instrument the Partnership LinkedIn DM Sequence to write DM, reply, suppression, and completion events. — **done** (DM in `nspggypNF245xzeL`; reply in `QfJ2EZcc7lZwNgxj`/`7o5EBdvwAuIaWW7k`; suppression/completion in `IPN8jnR3XSurX0o1`).
3. Instrument acceptance and inbound-message workflows to write partnership-scoped LinkedIn events. — **done** (`3ttEvr5NMcQCS4Hp`, `7o5EBdvwAuIaWW7k`).
4. Add `campaign_key` and `source_key` to every new LinkedIn event. — **done** for partnership events; non-partnership events route via `emerging_pool_contacts.ghl_contact_id` join.
5. Update Campaign Channel Summary to aggregate `Partnership LinkedIn` from the ledger. — **done** (linkedin_invites/linkedin_accepted/linkedin_replies columns).
6. Add event coverage and error counts to the Executive Report API payload.
7. Verify partnership email event delivery and correlate message IDs. — **partially done**: the Partnership Email Dispatcher (`Xshck23cKo1yXL9D`) stores `ghl_message_id`/`ghl_conversation_id` per send in `partnership_release_log`, and the Campaign Channel Summary attributes partnership email opens/clicks via a release-log fallback keyed on `contact_id`. The known historical reply is backfilled and the selected-window row shows 59 sent / 1 reply / 1.69%. Still open: confirming GHL emits all per-message open/click webhooks for inline `POST /conversations/messages` sends and correlating those events consistently.
8. Add owner dimensions and conflict state to the reporting read model. — **implemented 2026-09-09 (Phases 1–2)** via `report_sdr_registry` + `assigned_to` through the rollups + Exec Summary `sdrPerformance` and owner-coverage health probes; see `docs/sessions/2026-09-09-executive-report-sdr-attribution-phase1-2.md`.
9. Reconnect GSC OAuth and resume GSC ingestion.
10. Keep historical SimpleTexting HTTP 409 failures distinct from current provider health. Count only rows with confirmed provider IDs as sent/delivered; retain `send_unknown` rows in quarantine until provider evidence resolves them.
11. Configure native GHL widgets through authenticated UI access; do not guess undocumented report-builder APIs. **Partially done**: saved `Last 30 days` and removed the duplicate page-3 outgoing-call widget on 2026-08-08. MQL, owner, stage-split, campaign-tag, email-detail, page-name, and custom-metric widgets remain open because the builder has no stage-group dimension, no Owner-custom-field group-by, and some tag selections are virtualized.
12. Add QA assertions for the 10-contact test: 10 invite events, 10 campaign-attributed LinkedIn requests, 10 state transitions or explicit state-upsert failures, and no duplicate event IDs.
13. Add a GHL OAuth credential to n8n and ingest Social Planner statistics by platform/day, including saves, reach, and impressions.

## Acceptance Criteria

- Native GHL report loads in an authenticated session and has documented widget filters.
- Partnership Pipeline opportunities appear in native GHL widgets.
- Partnership tags appear in native GHL contact widgets.
- Executive Report shows `Partnership emails` and `Partnership LinkedIn` rows.
- The 10 live LinkedIn requests appear as 10 in both the overall LinkedIn KPI and the Partnership LinkedIn campaign row.
- LinkedIn activity can be filtered by Partnership, Brand, and Dispensary.
- Email engagement rates show event coverage and do not silently treat missing events as zero.
- Selected-period and previous-period values agree across KPI cards and campaign rows.
- Email open/click rates use unique contacts rather than raw open events, or the report documents that rates are event-based (current Campaign Channel Summary `email_open_rate` counts raw events, so multi-open contacts can exceed 100%).
- Source health identifies GSC OAuth and SimpleTexting provider blockers.
- No report contains credentials, PITs, OAuth tokens, or signed URLs.
- Outgoing Call Detail returns HTTP 200 with a valid empty payload when the selected seven-day window has no rows.
- Outgoing Call Detail production and manual smoke executions complete without Postgres, Code-node, or webhook-response errors.
- SDR Performance (2026-09-09): Exec Summary returns `sdrPerformance` with per-owner `booked / showed / no_show / cancelled / sqls_created / mqls_converted / won / lost / revenue`; `summary.meetingsBooked` equals the sum of per-owner `booked` (basis `appointments_start_at`); `report_source_health` contains `ghl_opp_owner_coverage` and `ghl_appt_owner_coverage`; the SDR panel renders on desktop and 390px with no horizontal overflow and no console errors.

## References

- `Project Status and Next Steps.md`
- `GHL Live Transparent CRM/GHL Reports Configuration Plan.md`
- `GHL Live Transparent CRM/Report Data Contract.md`
- `docs/audits/partnership-campaign-audit-plan.md`
- `n8n/reporting/LiveTransparent_Report_Workflow_Spec.md`
- `n8n/reporting/Embedded_Report_Host_Spec.md`
````

## File: reports/embed/executive-v1/REPORTS-README.reference.md
````markdown
# LiveTransparent Report Host

This folder holds the external dashboard surface that GHL will load inside an iframe.

## Canonical Route

- `https://reports.livetransparent.com/embed/executive`

## Current Status

- The host shell is prepared in repo.
- The public host serves build stamp `2026-08-12-v23-mobile-overflow`; campaign/channel filters, separate Vapi campaign rows, campaign drill-downs, comparison view, selected-period controls, prior-period comparison, campaign opportunity counts, SMS delivery diagnostics, partnership attribution, resolved GHL stage labels, responsive wide-table containment, and social engagement fields are live.
- The report host is now deployment-ready with `docker-compose.yml`, `Dockerfile`, `nginx.conf`, and `index.html`.
- The preferred GHL entry point is a Custom Menu Link that opens this page in an embedded iframe.
- The report data store remains Postgres.
- n8n writes the raw data, bridge rows, rollups, QA rows, and publish markers.
- The live executive summary webhook is wired to the report host and serves JSON from the Postgres reporting tables. GA4 traffic is ingested daily and bridged into the rollup tables (recorded visits, users, engaged_sessions, engagement_rate) alongside GHL CRM data.
- The live outgoing-call detail endpoint is `GET /webhook/lt-report-outgoing-calls`, backed by n8n workflow `VXFHc8IrF9DDEEdj`. It returns up to 100 Vapi calls from the last 7 completed days with pagination, disposition, duration, campaign, and signed recording URL fields.
- The outgoing-call detail endpoint remains available for diagnostics, but the Executive Report currently hides its bottom `Outgoing Call Detail` section because the report is not receiving usable data there. The sidebar bookmark and browser request have been removed; nginx still proxies the endpoint to the n8n webhook.
- The outgoing detail window is intentionally fixed to the seven most recent completed calendar days in `America/Los_Angeles`; the endpoint ignores broader report-range controls. `limit` is clamped to 1-100 and `offset` is non-negative.
- The detail query reads `voice_call_attempt` joined to `voice_call_queue`, calculates duration from `started_at`/`ended_at`, derives the first-attempt flag from prior attempts, and uses the latest `report_raw_ghl_contacts` snapshot for contact identity when available. Current snapshots may lack names, so the API falls back to the GHL contact ID.
- Recording playback is lazy (`preload="none"`) and uses the provider-signed `recording_url` already stored on the call attempt. Do not persist or document signed recording URLs in source files.
- The Executive Report now surfaces a Meta attribution panel using the live summary payload. It is intentionally focused on which Meta-tagged ads/campaigns are driving recorded visits and downstream opportunities, not spend.
- The Postgres reporting bootstrap has been applied to the live database.
- GHL leads/sales/report workflows are live and active.
- GA4 is now live and flowing to the executive report (recorded visits, users, engagement by channel). GSC raw ingest is also live, and the search section now shows native GSC performance plus an estimated unique visitors proxy from GA4 Organic Search users.
- `LT - Report Daily Rollups` was restored, republished, and verified on 2026-05-02 with the daily-summary dedupe and stage-aware win logic integrated into production.
- `LT - Report Daily Rollups` now preserves GA-backed channel, UTM, landing-page, and daily traffic rows so the report host keeps live Channel Breakdown after rollups run.
- `LT - Report Rollup Corrections` has been deactivated because the production Rollups workflow now owns those fixes.
- The Executive Report now surfaces email campaign metrics (sent, opened, clicked, bounced, unsubscribed, complained) with computed engagement rates. Data sourced from `report_daily_summary` (emails_* columns), populated from `DAN_Release_Log`, `Emerald_Release_Log`, and `Email_Events`.
- The Campaign Channel Summary now exposes `smsSummary` with sent, failed, replies, and normalized failure reasons. The current verified 30-day window returned 294 sent, 1,095 failed, and 0 replies; failure reasons were provider failure, duplicate send, unknown, invalid phone, and idempotent webhook error.
- The Campaign Channel Summary now exposes distinct selected-window campaign opportunity counts from `report_raw_ghl_opportunities`, matched to current campaign tags. The Executive Report renders these counts in campaign rows, details, and comparison view.
- LinkedIn outreach funnel metrics (`linkedinFunnel`) are now available, aggregated from `linkedin_connection_state` showing the full funnel: ready → requested → connected → DM active → completed.
- Vapi voice campaign breakdown (`vapiCampaignBreakdown`) and queue distribution (`vapiQueueDistribution`) are now surfaced from `voice_call_attempt` and `voice_call_queue`.
- A separate live campaign-channel endpoint (`/webhook/lt-report-campaign-channel-summary`) returns date-filtered named rows for DAN, Emerald, SMS, LinkedIn, and Vapi. DAN uses release-log campaign fields, Emerald uses bucket/enrollment data, SMS uses `campaign_key`, LinkedIn uses append-only activity events joined to Brand/Dispensary source pools (plus `linkedin_invites`/`linkedin_accepted` columns routed by `campaign_type`/`source_key = 'partnership'`), and Vapi uses queue campaign IDs.
- The campaign-channel endpoint returns its selected `window`, channel, campaign, SMS metrics/diagnostics, email metrics/rates, LinkedIn DM/reply metrics, Vapi metrics, and campaign opportunity counts. Rates are deliberately `null` when the campaign sent denominator is unavailable; the report renders those as `—` rather than inventing a percentage.
- The selected-window campaign endpoint reflects verified historical partnership replies: `Partnership emails` shows 59 sent / 1 reply / 1.69% response rate, and `Partnership LinkedIn` shows 17 invites / 3 replies after the 2026-08-12 recovery of David Schachter and Gretchen Gailey from Unipile provider records.
- Catalog rows for `General outbound`, `Partnership emails`, `xyz`, and `abc` are intentionally present but remain zero until matching source events exist. Historical email events can also have opens/clicks without a matching send row; those are retained as source-coverage limitations.
- Historical campaign engagement is limited by `Email_Events` coverage. The event-ingest path had no executions for the tested 2026-07-20 through 2026-07-26 window, while later windows contain live opened/bounced events. The report therefore preserves zero counts for periods with no stored events instead of fabricating rates.
- A parallel native GHL custom report was created at report ID `6a67dce4a51a4360c60963a3`. The authenticated GHL UI session now has the saved `Last 30 days` date range and the duplicate page-3 `Outgoing calls by status` widget removed. The external Executive Report remains the campaign-level view: its campaign table has All, Email, LinkedIn, SMS, and VAPI filters, separate Vapi campaign rows, drill-downs, comparison view, opportunity counts, SMS diagnostics, dynamic campaign rows, and LinkedIn Invites/Accepted columns.
- MQL summary (`mqlSummary`) reports total MQLs, MQLs converted to SQL (Sales Outreach pipeline), current MQLs awaiting sales, and entered/converted in the selected window. SQL contacts (`sqlContacts`) counts contacts with the SQL tag. Social reach/impressions/likes/followers/posts come from `report_ghl_social_statistics` (PIT-backed daily ingest), distinct from the post-placement ledger.
- AI qualification reporting must distinguish Janvi-qualified cannabis contacts promoted to Sales Outreach from AI-pending/unverified contacts remaining in Warm and Vapi.
- SDR reporting must capture assignment source, owner-alignment result, conflicts, and unassigned Sales Outreach records.
- Pool distribution (`poolDistribution`) shows brand, dispensary, and Vapi campaign pool tag counts.
- Stage mover count was fixed (was 0) by resolving pipeline/stage names from GHL stage IDs when name fields are NULL and by removing the date filter from `opportunity_traces` to detect transitions across all history.
- `LT - Report Executive Summary API` now uses a contact-safe cohort definition for `contactToOpportunityRate` so the embedded funnel is not inflated by multi-opportunity rollup semantics.
- `LT - Report Executive Summary API` now also exposes attribution-coverage metrics for the new-contact cohort so the report can separate funnel weakness from matching weakness.
- Meta reporting in the Executive Report is currently attribution-first:
  - Traffic and campaign rows come from GA4 UTM/session reporting.
  - Downstream lead/opportunity counts come from the GHL bridge and rollup tables.
  - Meta spend, clicks, and impression truth remain in the staged raw ingest and source health path, but are not shown in the Executive Report yet by design.
- The current cohort view now shows usable source-field coverage, bridge-match coverage, and lead-to-sale match coverage separately so attribution quality can be diagnosed without inflating funnel metrics.
- The Executive Summary API and embedded report expose social likes, comments, shares, saves, reach, and impressions when supplied by the raw post payload. Current PIT-based post ingestion provides likes/comments/shares only; OAuth-backed GHL statistics ingestion is still required for saves/reach/impressions.
- `LT - Report Attribution Bridge` now rebuilds a rolling 90-day window using normalized raw contact ids and stored GHL attribution fields, which materially improved cohort bridge coverage in the live report.
- The embedded report now includes a metric glossary so the visible cards are defined where they appear.
- The primary funnel cards now use Users as the denominator for conversion rates, while Recorded Visits remains traffic volume context.
- `7d`, `30d`, and `90d` are trailing complete-day presets ending yesterday, not click-day-dependent calendar blocks.
- The Executive Report also accepts explicit `from=YYYY-MM-DD` and `to=YYYY-MM-DD` windows. The UI exposes those controls and automatically loads the immediately preceding equal-length period for week-on-week comparison.
- Top Pages now normalizes landing-page URLs to host-relative paths and removes query strings, fragments, session IDs, and trigger-link parameters before rendering.
- Week-on-week cards show the selected-period value, prior-period value, absolute change, and percentage change for contacts, opportunities, meetings, closed won, email opens, email clicks, and Vapi calls.
- The `Acquisition Sources` sidebar entry opens the contact-level attribution view.
- The `UTM / Campaign Breakdown` section shows observed traffic rows, not every UTM ever created in GHL.
- `Active Opportunities Summary` and `Team Active Deals` are two presentations of the same opportunity payload, with the latter framed as a deal-centred view.
- In the active-opportunity view, `active` means the latest open snapshot, `worked` means the opportunity was updated or moved stage in the selected window, and `stage movers` means the opportunity changed stage at least once in that window.
- Contacts are not guaranteed to be created by forms; they can also arrive through routing, manual CRM entry, imports, and follow-up.
- The GHL sidebar menu record is already live in GHL.

## Expected Runtime Flow

1. GHL sidebar item opens the embedded report URL.
2. The host page reads `view`, `range`, `from`, `to`, `embed`, and `locationId` query params.
3. The host fetches executive report data from a Postgres-backed API.
4. The page renders GHL KPI cards, pipeline panels, and drilldowns in read-only mode.

## GHL Fit

- This host is designed to stay external while being embedded inside GHL.
- That keeps the dashboard flexible while leaving CRM, navigation, and user access inside HighLevel.
- If the team later wants a dashboard-page view instead, the same host can also be embedded through a GHL dashboard widget.
- GA4 traffic data is live in the report. GSC search data is staged in raw tables and will populate the search section once the summary rollup wiring is in place. The same report URL and GHL menu entry continue to work.

## Planned API Contract

- `GET /api/report/executive/summary`
- `GET /api/report/executive/outgoing-calls`
- `GET /api/report/executive/channel-breakdown`
- `GET /api/report/executive/pipeline-dropoff`
- `GET /api/report/executive/health`

The summary endpoint is implemented through n8n and proxied by nginx. The other endpoints remain reserved for future expansion, but the HTML shell is already written to consume the summary payload without changing the GHL embed URL.

The outgoing-call detail endpoint is also implemented through n8n and proxied by nginx. It is a read-only endpoint and does not mutate GHL, Vapi, queue, or reporting data.

## Files

- `Dockerfile`: container build for Coolify or other static hosting.
- `docker-compose.yml`: Coolify-ready service definition for the report host.
- `nginx.conf`: static web server config.
- `index.html`: root redirect into the executive report.
- `embed/executive/index.html`: interactive embedded dashboard shell
````

## File: reports/embed/executive-v1/RESPONSE-SLA-CONTRACT.md
````markdown
# Same-channel response SLA contract

## Definition

For each inbound prospect interaction in the selected period, measure the elapsed time from the inbound event to the first qualifying outbound response from the business on the same channel.

| Channel | Inbound event | Qualifying response |
|---|---|---|
| LinkedIn | Durable `linkedin_activity_events` row with `event_type` `reply_received` or `inbound_reply` | Later `linkedin_activity_events` row for the same contact/channel with `event_type` `dm_sent` |
| Email | Durable email reply event stored in `Email_Events` with reply/replied classification | Later marketing-email send event for the same contact from the campaign/release ledger |
| Phone | Inbound `report_raw_ghl_calls` row with inbound direction | Later outbound `report_raw_ghl_calls` or Vapi call attempt for the same contact |

## Required output per inbound event

- `inbound_event_id`, `contact_id`, `channel`, `inbound_at`
- `response_event_id`, `response_at`, `response_seconds`
- `response_status`: `responded`, `unmatched`, `ambiguous`, or `source_gap`
- `campaign_key`, `sender/owner`, and source workflow
- `target_minutes` only when a business SLA is explicitly configured

## Accuracy rules

- Use the first later same-channel outbound event only.
- Never match an outbound event that occurred before the inbound event.
- Do not match across channels.
- Do not count automated bounce, out-of-office, unsubscribe, or system messages as human replies.
- Preserve unmatched inbound events; they are required for the follow-up queue.
- Preserve ambiguous events when multiple same-timestamp candidates exist.
- Report median, average, and percentile response time only with the event count and matched/unmatched coverage.
- “Overdue follow-up” means an unmatched inbound event older than the configured channel target; it must not be shown until targets are configured.

## Initial implementation boundary

LinkedIn, phone, and email are derived from the durable activity/call/release ledgers. Email reply events and every marketing send ledger must expose a common contact ID and timestamp. If a channel has inbound events but no later qualifying response, the facts remain `unmatched`; they are not converted to zero response time.
````

## File: scripts/n8n/align_n8n_encryption_key.py
````python
HOST = "89.117.21.29"
KEY = r"C:\Users\edmon\.ssh\local-upload"
SERVICE_DIR = "/data/coolify/services/n44wksswcocwk88ogcog8c48"
⋮----
key = paramiko.Ed25519Key.from_private_key_file(KEY)
client = paramiko.SSHClient()
⋮----
command = (
````

## File: scripts/n8n/fix_sheets_node.py
````python
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4NjFmYjY1NS1iMTc2LTRkNjMtYTRlZC0zY2M2NmUyNzk2NDIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiOTEwOThlZTEtZWI4NS00NjAwLTg5NmYtMGM3ZDMwOTg4YTg1IiwiaWF0IjoxNzc3NDIwMDk5fQ.6ZVb5kKoNltBUFYHoS2x4PQABycoJDvdmN9Nrfx-Z7U"
BASE = "https://automations.livetransparent.com/api/v1"
WF_ID = "q7qbjjm6185WeukV"
⋮----
req = urllib.request.Request(f"{BASE}/workflows/{WF_ID}", headers={"X-N8N-API-KEY": API_KEY})
wf = json.loads(urllib.request.urlopen(req).read())
⋮----
body = {
⋮----
data = json.dumps(body).encode("utf-8")
req = urllib.request.Request(f"{BASE}/workflows/{WF_ID}", data=data, method="PUT", headers={
resp = json.loads(urllib.request.urlopen(req).read())
⋮----
# Verify
⋮----
wf2 = json.loads(urllib.request.urlopen(req).read())
⋮----
code = n["parameters"].get("jsCode", "")
has_auth = "httpRequestWithAuthentication" in code
has_data_ref = "$('Parse CSV').all()" in code
````

## File: scripts/n8n/fix_workflow.py
````python
k = paramiko.Ed25519Key.from_private_key_file(r'C:\Users\edmon\.ssh\local-upload')
c = paramiko.SSHClient()
⋮----
nodes_json = stdout.read().decode().strip()
nodes = json.loads(nodes_json)
⋮----
old_js = node['parameters']['jsCode']
⋮----
new_js = old_js.replace(
new_js = new_js.replace(
⋮----
# Write the updated nodes back
nodes_json = json.dumps(nodes)
⋮----
# Update via n8n REST API
cmd = f"""docker exec postgres-uokgs4c04ko0s4scccg40cgg psql -U postgres -d n8n -c "UPDATE workflow_entity SET nodes = '{nodes_json.replace(chr(39), chr(39)+chr(39))}' WHERE id = 'osIJOgBmWITF5Yuv';\""""
⋮----
out = stdout.read().decode().strip()
err = stderr.read().decode().strip()
⋮----
# Also need to update the active version
cmd2 = f"""docker exec postgres-uokgs4c04ko0s4scccg40cgg psql -U postgres -d n8n -c "UPDATE workflow_published_version SET nodes = '{nodes_json.replace(chr(39), chr(39)+chr(39))}' WHERE id = '64139619-eff5-4354-89cf-d5ce63e1a1a5';\""""
````

## File: scripts/n8n/inventory_n8n_pits.py
````python
def main() -> None
⋮----
env = load_env_file()
api_key = os.environ.get("N8N_API_KEY_LT") or env.get("N8N_API_KEY_LT", "")
result = subprocess.run(
payload = json.loads(result.stdout.decode("utf-8", errors="replace"))
matches = []
token_workflows = {}
⋮----
nodes = workflow.get("nodes", [])
matching_nodes = []
⋮----
serialized = json.dumps(node.get("parameters", {}))
⋮----
text = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
⋮----
status = subprocess.run(
````

## File: scripts/n8n/n8n_api_probe.py
````python
PROJ = r"C:\1_Ed's Active Work\Projects\LiveTransparent"
def load_env(path, keys)
⋮----
vals = {}
⋮----
line=line.strip()
⋮----
env = load_env(os.path.join(PROJ,".env"),["N8N_API_KEY_LT","n8n_API_Key","N8N_HOST"])
key = env.get("N8N_API_KEY_LT") or env.get("n8n_API_Key")
host = env.get("N8N_HOST") or "https://automations.livetransparent.com"
⋮----
host = "https://" + host
⋮----
def api(path, method="GET")
⋮----
url = host.rstrip("/") + path
req = urllib.request.Request(url, method=method, headers={"X-N8N-API-KEY": key, "Accept":"application/json"})
ctx = ssl.create_default_context()
⋮----
wfs = body.get("data", [])
⋮----
name = (w.get("name") or "")
````

## File: scripts/n8n/n8n_exec_check.py
````python
PROJ = r"C:\1_Ed's Active Work\Projects\LiveTransparent"
def load_env(path, keys)
⋮----
vals = {}
⋮----
line=line.strip()
⋮----
env = load_env(os.path.join(PROJ,".env"),["N8N_API_KEY_LT","n8n_API_Key","N8N_HOST"])
key = env.get("N8N_API_KEY_LT") or env.get("n8n_API_Key")
host = env.get("N8N_HOST") or "https://automations.livetransparent.com"
if not host.startswith("http"): host = "https://"+host
def api(path)
⋮----
req = urllib.request.Request(host.rstrip("/")+path, method="GET", headers={"X-N8N-API-KEY":key,"Accept":"application/json"})
⋮----
wf_ids = {
fix_ts = datetime(2026,9,7,14,53,0,tzinfo=timezone.utc)
⋮----
ts_s = ex.get("startedAt") or ex.get("stoppedAt") or ""
status = ex.get("status")
⋮----
ts = datetime.fromisoformat(ts_s.replace("Z","+00:00"))
after = ts >= fix_ts
mark = "AFTER-FIX" if after else "before-fix"
⋮----
mark = "?"
````

## File: scripts/n8n/n8n_find_pgerr.py
````python
PROJ = r"C:\1_Ed's Active Work\Projects\LiveTransparent"
def load_env(path, keys)
⋮----
vals = {}
⋮----
line=line.strip()
⋮----
env = load_env(os.path.join(PROJ,".env"),["N8N_API_KEY_LT","n8n_API_Key","N8N_HOST"])
key = env.get("N8N_API_KEY_LT") or env.get("n8n_API_Key")
host = env.get("N8N_HOST") or "https://automations.livetransparent.com"
if not host.startswith("http"): host = "https://"+host
def api(path)
⋮----
req = urllib.request.Request(host.rstrip("/")+path, method="GET", headers={"X-N8N-API-KEY":key,"Accept":"application/json"})
⋮----
blob = json.dumps(ex)
⋮----
# error message
err = ex.get("data",{}).get("resultData",{}).get("error",{}) if isinstance(ex.get("data"),dict) else {}
````

## File: scripts/n8n/n8n_ga4_err.py
````python
PROJ = r"C:\1_Ed's Active Work\Projects\LiveTransparent"
def load_env(path, keys)
⋮----
vals = {}
⋮----
line=line.strip()
⋮----
env = load_env(os.path.join(PROJ,".env"),["N8N_API_KEY_LT","n8n_API_Key","N8N_HOST"])
key = env.get("N8N_API_KEY_LT") or env.get("n8n_API_Key")
host = env.get("N8N_HOST") or "https://automations.livetransparent.com"
if not host.startswith("http"): host = "https://"+host
def api(path)
⋮----
req = urllib.request.Request(host.rstrip("/")+path, method="GET", headers={"X-N8N-API-KEY":key,"Accept":"application/json"})
⋮----
data = ex.get("data") or {}
result = data.get("resultData", {}).get("error", {})
⋮----
blob = J.dumps(data)
⋮----
idx = blob.find(pat)
````

## File: scripts/n8n/n8n_vapi_check.py
````python
PROJ = r"C:\1_Ed's Active Work\Projects\LiveTransparent"
def load_env(path, keys)
⋮----
vals = {}
⋮----
line=line.strip()
⋮----
env = load_env(os.path.join(PROJ,".env"),["N8N_API_KEY_LT","n8n_API_Key","N8N_HOST"])
key = env.get("N8N_API_KEY_LT") or env.get("n8n_API_Key")
host = env.get("N8N_HOST") or "https://automations.livetransparent.com"
if not host.startswith("http"): host = "https://"+host
def api(path)
⋮----
req = urllib.request.Request(host.rstrip("/")+path, method="GET", headers={"X-N8N-API-KEY":key,"Accept":"application/json"})
⋮----
WID = "r7UjWLndmc6EqEUW"
⋮----
fix_ts = datetime(2026,9,7,14,53,0,tzinfo=timezone.utc)
⋮----
ts_s = ex.get("startedAt") or ""
status = ex.get("status")
⋮----
ts = datetime.fromisoformat(ts_s.replace("Z","+00:00"))
after = "POST-FIX" if ts >= fix_ts else "pre-fix"
⋮----
after="?"
⋮----
err = ""
⋮----
d = ex.get("data") or {}
e = (d.get("resultData") or {}).get("error") or {}
err = str(e.get("message"))[:60]
````

## File: scripts/n8n/refresh_ghl_oauth_token.py
````python
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORKFLOW_ID = "kqIi8i1RjFAZKrK3"
N8N_BASE = "https://automations.livetransparent.com/api/v1"
GHL_TOKEN_URL = "https://services.leadconnectorhq.com/oauth/token"
⋮----
def load_env()
⋮----
values = {}
⋮----
line = line.strip()
⋮----
ENV = load_env()
⋮----
def ssh_client()
⋮----
key_path = os.path.expandvars(os.path.expanduser(ENV.get("VPS_SSH_KEY_PATH", "")))
key = None
⋮----
key = key_type.from_private_key_file(key_path)
⋮----
client = paramiko.SSHClient()
⋮----
def psql(sql)
⋮----
client = ssh_client()
⋮----
command = "docker exec -i postgres-uokgs4c04ko0s4scccg40cgg psql -U postgres -d postgres -v ON_ERROR_STOP=1 -X -q -t -A"
⋮----
output = stdout.read().decode(errors="replace").strip()
error = stderr.read().decode(errors="replace").strip()
⋮----
def sql_literal(value)
⋮----
api_key = ENV.get("N8N_API_KEY_LT") or ENV.get("n8n_API_KEY")
request = urllib.request.Request(f"{N8N_BASE}/workflows/{WORKFLOW_ID}", headers={"X-N8N-API-KEY": api_key, "Accept": "application/json"})
⋮----
workflow = json.loads(response.read().decode())
exchange = next(node for node in workflow["nodes"] if node["name"] == "Exchange OAuth Token")
params = exchange["parameters"]["bodyParameters"]["parameters"]
oauth_values = {item["name"]: item["value"] for item in params}
client_id = oauth_values["client_id"]
client_secret = oauth_values["client_secret"]
⋮----
row = json.loads(psql("SELECT row_to_json(x)::text FROM (SELECT refresh_token, company_id, location_id, user_type FROM ghl_oauth_tokens WHERE active IS TRUE AND refresh_token <> '' ORDER BY received_at DESC NULLS LAST LIMIT 1) x;"))
⋮----
response = requests.post(GHL_TOKEN_URL, data={
⋮----
token = response.json()
⋮----
company_id = token.get("companyId") or row.get("company_id") or "7vMmm4at5OrjQplRN3EO"
location_id = token.get("locationId") or row.get("location_id") or "Zwz4relUXVPxx8uohnjV"
user_type = token.get("userType") or row.get("user_type") or "Company"
scope = token.get("scope") or token.get("scopes") or ""
⋮----
scope = " ".join(scope)
raw = json.dumps(token, separators=(",", ":"))
⋮----
sql = f"""
````

## File: scripts/n8n/repair_failed_ghl_pits.py
````python
N8N_BASE = "https://automations.livetransparent.com/api/v1/workflows/"
WORKFLOW_IDS = ["NTpQnMrpjzusPXHX", "dZQLlbTLkpE1843X"]
⋮----
def api_key() -> str
⋮----
def pit_values() -> tuple[str, str]
⋮----
env = load_env_file()
old = os.environ.get("GHL_OLD_PIT") or env.get("GHL_OLD_PIT", "")
new = os.environ.get("GHL_PIT") or env.get("GHL_PIT", "")
⋮----
def curl(args: list[str], body: bytes | None = None) -> dict
⋮----
result = subprocess.run(
⋮----
def replace_value(value)
⋮----
def main() -> None
⋮----
key = api_key()
⋮----
headers = ["-H", f"X-N8N-API-KEY: {key}", "-H", "Accept: application/json"]
allowed_settings = {
⋮----
current = curl([*headers, N8N_BASE + workflow_id])
settings = {k: v for k, v in (current.get("settings") or {}).items() if k in allowed_settings}
nodes = current.get("nodes") or []
changed = False
⋮----
params = node.get("parameters") or {}
⋮----
changed = True
replaced = replace_value(params)
⋮----
body = json.dumps({
updated = curl([
````

## File: scripts/social-reporting/audit_social_reporting.py
````python
QUERY = """
⋮----
key = paramiko.Ed25519Key.from_private_key_file(r"C:\Users\edmon\.ssh\local-upload")
client = paramiko.SSHClient()
⋮----
postgres = stdout.read().decode().strip().splitlines()[0]
⋮----
environment = dict(line.split("=", 1) for line in stdout.read().decode().splitlines() if "=" in line)
encoded = base64.b64encode(QUERY.encode()).decode()
command = (
````

## File: scripts/social-reporting/fix_brands_code.py
````python
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4NjFmYjY1NS1iMTc2LTRkNjMtYTRlZC0zY2M2NmUyNzk2NDIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiOTEwOThlZTEtZWI4NS00NjAwLTg5NmYtMGM3ZDMwOTg4YTg1IiwiaWF0IjoxNzc3NDIwMDk5fQ.6ZVb5kKoNltBUFYHoS2x4PQABycoJDvdmN9Nrfx-Z7U"
BASE = "https://automations.livetransparent.com/api/v1"
WF_BRANDS = "fg06Ip8wT3EapfdD"
⋮----
req = urllib.request.Request(f"{BASE}/workflows/{WF_BRANDS}", headers={"X-N8N-API-KEY": API_KEY})
wf = json.loads(urllib.request.urlopen(req).read())
⋮----
body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"], "settings": wf["settings"], "description": wf.get("description", "")}
data = json.dumps(body).encode("utf-8")
req = urllib.request.Request(f"{BASE}/workflows/{WF_BRANDS}", data=data, method="PUT", headers={"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"})
resp = json.loads(urllib.request.urlopen(req).read())
⋮----
# Verify
req2 = urllib.request.Request(f"{BASE}/workflows/{WF_BRANDS}", headers={"X-N8N-API-KEY": API_KEY})
wf2 = json.loads(urllib.request.urlopen(req2).read())
⋮----
code = n["parameters"].get("jsCode", "")
````

## File: scripts/social-reporting/fix_executive_report_metrics.py
````python
BASE_URL = "https://automations.livetransparent.com/api/v1/workflows/"
WORKFLOW_IDS = {
ALLOWED_SETTINGS = {
⋮----
def load_env() -> dict[str, str]
⋮----
values: dict[str, str] = {}
env_path = Path(__file__).resolve().parents[1] / ".env"
⋮----
line = raw_line.strip()
⋮----
def api_key() -> str
⋮----
key = os.environ.get("N8N_API_KEY_LT") or load_env().get("N8N_API_KEY_LT", "")
⋮----
def request(workflow_id: str, method: str = "GET", payload: dict | None = None) -> dict
⋮----
body = None if payload is None else json.dumps(payload, ensure_ascii=True).encode("utf-8")
req = urllib.request.Request(
⋮----
def node_map(workflow: dict) -> dict[str, dict]
⋮----
def code_summary(node: dict) -> dict
⋮----
code = str((node.get("parameters") or {}).get("jsCode") or "")
⋮----
def inspect() -> None
⋮----
workflow = request(workflow_id)
summaries = [code_summary(node) for node in workflow.get("nodes", []) if node.get("type") == "n8n-nodes-base.code"]
⋮----
def snippets() -> None
⋮----
requests = {
⋮----
workflow = request(WORKFLOW_IDS[label])
nodes = node_map(workflow)
⋮----
code = str((nodes[node_name].get("parameters") or {}).get("jsCode") or "")
⋮----
lines = code.splitlines()
selected: set[int] = set()
⋮----
campaign = request(WORKFLOW_IDS["campaign"])
query = str((node_map(campaign)["Campaign Channel Query"].get("parameters") or {}).get("query") or "")
⋮----
index = query.find(needle)
⋮----
def replace_once(text: str, old: str, new: str, label: str) -> str
⋮----
count = text.count(old)
⋮----
def replace_count(text: str, old: str, new: str, expected: int, label: str) -> str
⋮----
def update_workflow(workflow: dict) -> dict
⋮----
settings = {key: value for key, value in (workflow.get("settings") or {}).items() if key in ALLOWED_SETTINGS}
payload = {
⋮----
CAMPAIGN_NORMALIZE = r"""const query = $json.query || {};
⋮----
EXECUTIVE_NORMALIZE = r"""const req = $node['Webhook Intake'].json || {};
⋮----
INSTAGRAM_TABLE_DDL = """CREATE TABLE IF NOT EXISTS instagram_activity_events (
⋮----
LINKEDIN_REPLY_EVENT_CODE = r"""function esc(v) {
⋮----
def patch_campaign(workflow: dict) -> None
⋮----
query = str(nodes["Campaign Channel Query"]["parameters"]["query"]).replace("\r\n", "\n").replace("\r", "\n")
⋮----
query = INSTAGRAM_TABLE_DDL + "\n" + query
query = query.replace(
⋮----
marker = "  'campaignOpportunities',"
insert = """  'instagramActivity', (SELECT json_build_object(
query = replace_once(query, marker, insert + marker, "campaign instagram aggregate")
⋮----
code = nodes["Shape Campaign Response"]["parameters"]["jsCode"]
code = replace_once(
⋮----
def patch_executive(workflow: dict) -> None
⋮----
code = nodes["Build Query"]["parameters"]["jsCode"]
⋮----
code = replace_once(code, " WITH meta_ads_raw AS", " " + INSTAGRAM_TABLE_DDL + " WITH meta_ads_raw AS", "executive instagram ddl")
code = replace_count(
⋮----
marker = "vapi_campaign_breakdown AS ("
insert = """instagram_weekly_activity AS (  SELECT jsonb_build_object(    'dmsSent', COUNT(*) FILTER (WHERE event_type = 'dm_sent')::int,    'inboundReplies', COUNT(*) FILTER (WHERE event_type IN ('reply_received', 'inbound_reply'))::int,    'eventCount', COUNT(*)::int,    'coverage', 'ledger'  ) AS payload  FROM instagram_activity_events  WHERE event_at >= $1::date::timestamptz AND event_at < ($2::date + INTERVAL '1 day')),"""
code = replace_once(code, marker, insert + marker, "executive instagram cte")
⋮----
rate_patterns = [
⋮----
shape = nodes["Shape Response"]["parameters"]["jsCode"]
shape = replace_once(
⋮----
def patch_linkedin_inbound(workflow: dict) -> None
⋮----
code = nodes["Normalize Unipile Message Event"]["parameters"]["jsCode"]
old = r"""function formPayloadText(value) {
new = r"""function formPayloadText(value) {
⋮----
def pg_client_config(code: str) -> str
⋮----
match = re.search(r"const client = new Client\((\{[\s\S]*?\})\);", code)
⋮----
def patch_instagram_inbound(workflow: dict) -> str
⋮----
code = nodes["Persist and Claim Instagram Reply"]["parameters"]["jsCode"]
config = pg_client_config(code)
⋮----
def patch_social_outbound(workflow: dict, config: str) -> None
⋮----
node_name = "Log Instagram Outbound Activity"
⋮----
code = f"""const {{ Client }} = require('pg');
new_node = {
⋮----
def apply_repairs(dry_run: bool = False) -> None
⋮----
workflows = {label: request(workflow_id) for label, workflow_id in WORKFLOW_IDS.items()}
⋮----
pg_config = patch_instagram_inbound(workflows["instagram_inbound"])
⋮----
updated = update_workflow(workflows[label])
⋮----
def patch_linkedin_schema_only() -> None
⋮----
workflow = request(WORKFLOW_IDS["linkedin_inbound"])
⋮----
updated = update_workflow(workflow)
⋮----
def main() -> None
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args()
````

## File: scripts/social-reporting/fix_social_mql_reporting.py
````python
BASE_URL = "https://automations.livetransparent.com/api/v1/workflows/"
EXECUTIVE_ID = "Bukc0mgOD2r7V6ED"
ALLOWED_SETTINGS = {
⋮----
WARM_PIPELINE = "FRjpDZ1HWj3UPgczsu3t"
MQL_STAGE = "3b3bd98d-cbb9-4c50-8cf3-b4eba29061c2"
SALES_OUTREACH_PIPELINE = "dhdlf3O4tymxFtHk4aqq"
⋮----
def load_env() -> dict[str, str]
⋮----
values: dict[str, str] = {}
env_path = Path(__file__).resolve().parents[1] / ".env"
⋮----
line = raw_line.strip()
⋮----
def api_key() -> str
⋮----
key = os.environ.get("N8N_API_KEY_LT") or load_env().get("N8N_API_KEY_LT", "")
⋮----
def request(workflow_id: str, method: str = "GET", payload: dict | None = None) -> dict
⋮----
body = None if payload is None else json.dumps(payload, ensure_ascii=True).encode("utf-8")
req = urllib.request.Request(
⋮----
def replace_between(code: str, start_marker: str, end_marker: str, replacement: str, label: str) -> str
⋮----
start = code.find(start_marker)
⋮----
end = code.find(end_marker, start + 1)
⋮----
SOCIAL_POSTS_CTE = """social_posts AS (
⋮----
MQL_CTES = f"""mql_keys AS (
⋮----
def node_map(workflow: dict) -> dict[str, dict]
⋮----
def update_workflow(workflow: dict) -> dict
⋮----
settings = {key: value for key, value in (workflow.get("settings") or {}).items() if key in ALLOWED_SETTINGS}
payload = {
⋮----
def main() -> None
⋮----
workflow = request(EXECUTIVE_ID)
⋮----
build_query = node_map(workflow)["Build Query"]
code = str(build_query["parameters"]["jsCode"])
code = replace_between(code, "social_posts AS (", "calls AS (", SOCIAL_POSTS_CTE, "socialPosts")
code = replace_between(code, "mql_history AS (", "sql_contacts AS (", MQL_CTES, "mqlSummary")
⋮----
updated = update_workflow(workflow)
````

## File: scripts/social-reporting/fix_social_reporting_accuracy.py
````python
SOCIAL_POSTS_CTE = r"""social_posts AS (
⋮----
LINKEDIN_FUNNEL_CTE = r"""linkedin_funnel AS (
⋮----
def replace_cte(code: str, start_marker: str, end_marker: str, replacement: str) -> str
⋮----
start = code.index(start_marker)
end = code.index(end_marker, start)
⋮----
def main() -> None
⋮----
workflow = request(WORKFLOW_IDS["executive"])
⋮----
build_query = node_map(workflow)["Build Query"]
code = str(build_query["parameters"]["jsCode"])
code = replace_cte(code, "social_posts AS (", "calls AS (", SOCIAL_POSTS_CTE)
code = replace_cte(code, "linkedin_funnel AS (", "linkedin_weekly_activity AS (", LINKEDIN_FUNNEL_CTE)
⋮----
updated = update_workflow(workflow)
````

## File: scripts/social-reporting/implement_email_attribution.py
````python
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WORKFLOW_ID = "Bukc0mgOD2r7V6ED"
⋮----
def load_env()
⋮----
values = {}
⋮----
line = line.strip()
⋮----
env = load_env()
api_key = env.get("N8N_API_KEY_LT") or env.get("n8n_API_Key")
host = (env.get("N8N_HOST") or "https://automations.livetransparent.com").rstrip("/")
⋮----
host = "https://" + host
⋮----
def request(path, method="GET", body=None)
⋮----
payload = None if body is None else json.dumps(body).encode("utf-8")
req = urllib.request.Request(
context = ssl.create_default_context()
⋮----
workflow = request(f"/api/v1/workflows/{WORKFLOW_ID}")
nodes = workflow["nodes"]
build_query = next(node for node in nodes if node.get("name") == "Build Query")
js_code = build_query["parameters"]["jsCode"]
⋮----
schema_sql = """
⋮----
js_code = js_code.replace("SET jit=off;", "SET jit=off;\n" + schema_sql, 1)
⋮----
attribution_cte = r"""
marker = "),summary AS ("
⋮----
js_code = js_code.replace(marker, ")," + attribution_cte + "summary AS (", 1)
⋮----
final_marker = "'opportunityStageBreakdown', COALESCE((SELECT items FROM opportunity_stage_breakdown), '[]'::json)) AS payload;"
final_replacement = "'opportunityStageBreakdown', COALESCE((SELECT items FROM opportunity_stage_breakdown), '[]'::json), 'emailCampaignAttribution', COALESCE((SELECT items FROM email_campaign_attribution), '[]'::jsonb), 'emailAttributionCoverage', COALESCE((SELECT to_jsonb(payload) FROM email_attribution_coverage), '{}'::jsonb)) AS payload;"
⋮----
js_code = js_code.replace(final_marker, final_replacement, 1)
⋮----
js_code = js_code.replace(
⋮----
settings = dict(workflow.get("settings") or {})
⋮----
payload = {
updated = request(f"/api/v1/workflows/{WORKFLOW_ID}", method="PUT", body=payload)
````

## File: scripts/social-reporting/repair_source_health.py
````python
WORKFLOW_ID = "Bukc0mgOD2r7V6ED"
HOST = "https://automations.livetransparent.com"
⋮----
def load_env() -> dict[str, str]
⋮----
values: dict[str, str] = {}
⋮----
line = raw.strip()
⋮----
def request(method: str = "GET", payload: dict | None = None) -> dict
⋮----
env = load_env()
body = None if payload is None else json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
⋮----
def main() -> None
⋮----
workflow = request()
⋮----
build = next(node for node in workflow["nodes"] if node.get("name") == "Build Query")
code = build["parameters"]["jsCode"]
old = """health AS (  SELECT COALESCE(json_agg(row_to_json(t) ORDER BY t.source_system), '[]'::json) AS items FROM (    SELECT btrim(source_system, '\"') AS source_system, CASE WHEN source_system IN ('email_events','linkedin_activity_events') THEN status WHEN last_success_at IS NULL OR (stale_after_hours > 0 AND last_success_at < NOW() - (stale_after_hours || ' hours')::interval) THEN 'stale' ELSE status END AS status, last_success_at, last_attempt_at, last_row_count, stale_after_hours, last_error FROM report_source_health WHERE source_system <> 'undefined' ORDER BY btrim(source_system, '\"')  ) t),"""
new = """health AS (  SELECT COALESCE(json_agg(row_to_json(t) ORDER BY t.source_system), '[]'::json) AS items FROM (    SELECT btrim(source_system, '\"') AS source_system, CASE WHEN source_system IN ('email_events','linkedin_activity_events') THEN status WHEN last_success_at IS NULL OR (stale_after_hours > 0 AND last_success_at < NOW() - (stale_after_hours || ' hours')::interval) THEN 'stale' ELSE status END AS status, last_success_at, last_attempt_at, last_row_count, stale_after_hours, last_error FROM report_source_health WHERE source_system NOT IN ('undefined', 'n8n', 'postgres', 'appointments')    UNION ALL    SELECT 'appointments', CASE WHEN MAX(loaded_at) IS NULL THEN 'pending' WHEN MAX(loaded_at) < NOW() - INTERVAL '48 hours' THEN 'stale' ELSE 'ready' END, MAX(loaded_at), MAX(loaded_at), COUNT(*)::int, 48, NULL::text FROM report_raw_ghl_appointments    UNION ALL    SELECT 'n8n', 'ready', NOW(), NOW(), 1, 1, NULL::text    UNION ALL    SELECT 'postgres', 'ready', NOW(), NOW(), 1, 1, NULL::text    ORDER BY source_system  ) t),"""
⋮----
code = code.replace(old, new, 1)
⋮----
code = code.replace("ORDER BY btrim(source_system, '\"')  ) t),", "ORDER BY source_system  ) t),", 1)
⋮----
settings = {k: v for k, v in (workflow.get("settings") or {}).items() if k != "availableInMCP"}
updated = request("PUT", {
````

## File: scripts/social-reporting/report_runtime_audit.py
````python
key = paramiko.Ed25519Key.from_private_key_file(r"C:\Users\edmon\.ssh\local-upload")
client = paramiko.SSHClient()
⋮----
commands = [
⋮----
error = stderr.read().decode().strip()
````

## File: postgres/reporting-bootstrap.sql
````sql
CREATE TABLE IF NOT EXISTS report_config (
  config_key TEXT PRIMARY KEY,
  config_value JSONB NOT NULL DEFAULT '{}'::jsonb,
  notes TEXT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS report_source_registry (
  source_system TEXT PRIMARY KEY,
  source_name TEXT NOT NULL,
  is_required BOOLEAN NOT NULL DEFAULT TRUE,
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  notes TEXT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS report_sync_watermarks (
  workflow_name TEXT NOT NULL,
  source_system TEXT NOT NULL,
  watermark_key TEXT NOT NULL,
  watermark_value TEXT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (workflow_name, source_system, watermark_key)
);
CREATE TABLE IF NOT EXISTS report_sync_runs (
  run_id BIGSERIAL PRIMARY KEY,
  workflow_name TEXT NOT NULL,
  source_system TEXT,
  report_date DATE,
  batch_id TEXT,
  status TEXT NOT NULL,
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  finished_at TIMESTAMPTZ,
  row_count INTEGER NOT NULL DEFAULT 0,
  error_count INTEGER NOT NULL DEFAULT 0,
  retry_count INTEGER NOT NULL DEFAULT 0,
  cursor_value TEXT,
  error_message TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS report_sync_runs_workflow_name_idx
  ON report_sync_runs (workflow_name, started_at DESC);
CREATE INDEX IF NOT EXISTS report_sync_runs_status_idx
  ON report_sync_runs (status, started_at DESC);
CREATE TABLE IF NOT EXISTS report_sync_errors (
  error_id BIGSERIAL PRIMARY KEY,
  run_id BIGINT,
  workflow_name TEXT NOT NULL,
  source_system TEXT,
  source_key TEXT,
  report_date DATE,
  error_category TEXT NOT NULL,
  error_message TEXT NOT NULL,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS report_sync_errors_run_id_idx
  ON report_sync_errors (run_id, created_at DESC);
CREATE INDEX IF NOT EXISTS report_sync_errors_workflow_name_idx
  ON report_sync_errors (workflow_name, created_at DESC);
CREATE TABLE IF NOT EXISTS report_source_health (
  source_system TEXT PRIMARY KEY,
  status TEXT NOT NULL,
  last_success_at TIMESTAMPTZ,
  last_attempt_at TIMESTAMPTZ,
  last_row_count INTEGER NOT NULL DEFAULT 0,
  stale_after_hours INTEGER NOT NULL DEFAULT 48,
  last_error TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS report_raw_ga4_sessions (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'ga4',
  source_key TEXT NOT NULL,
  source_window_start DATE,
  source_window_end DATE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  dimensions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  run_id BIGINT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS report_raw_ga4_sessions_uq
  ON report_raw_ga4_sessions (source_system, report_date, source_key);
CREATE INDEX IF NOT EXISTS report_raw_ga4_sessions_report_date_idx
  ON report_raw_ga4_sessions (report_date);
CREATE TABLE IF NOT EXISTS report_raw_ga4_pages (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'ga4',
  source_key TEXT NOT NULL,
  source_window_start DATE,
  source_window_end DATE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  dimensions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  run_id BIGINT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS report_raw_ga4_pages_uq
  ON report_raw_ga4_pages (source_system, report_date, source_key);
CREATE INDEX IF NOT EXISTS report_raw_ga4_pages_report_date_idx
  ON report_raw_ga4_pages (report_date);
CREATE TABLE IF NOT EXISTS report_raw_ga4_events (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'ga4',
  source_key TEXT NOT NULL,
  source_window_start DATE,
  source_window_end DATE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  dimensions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  run_id BIGINT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS report_raw_ga4_events_uq
  ON report_raw_ga4_events (source_system, report_date, source_key);
CREATE INDEX IF NOT EXISTS report_raw_ga4_events_report_date_idx
  ON report_raw_ga4_events (report_date);
CREATE TABLE IF NOT EXISTS report_raw_gsc_queries (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'gsc',
  source_key TEXT NOT NULL,
  source_window_start DATE,
  source_window_end DATE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  dimensions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  run_id BIGINT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS report_raw_gsc_queries_uq
  ON report_raw_gsc_queries (source_system, report_date, source_key);
CREATE INDEX IF NOT EXISTS report_raw_gsc_queries_report_date_idx
  ON report_raw_gsc_queries (report_date);
CREATE TABLE IF NOT EXISTS report_raw_gsc_pages (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'gsc',
  source_key TEXT NOT NULL,
  source_window_start DATE,
  source_window_end DATE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  dimensions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  run_id BIGINT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS report_raw_gsc_pages_uq
  ON report_raw_gsc_pages (source_system, report_date, source_key);
CREATE INDEX IF NOT EXISTS report_raw_gsc_pages_report_date_idx
  ON report_raw_gsc_pages (report_date);
CREATE TABLE IF NOT EXISTS report_raw_gsc_site (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'gsc',
  source_key TEXT NOT NULL,
  source_window_start DATE,
  source_window_end DATE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  dimensions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  run_id BIGINT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS report_raw_gsc_site_uq
  ON report_raw_gsc_site (source_system, report_date, source_key);
CREATE INDEX IF NOT EXISTS report_raw_gsc_site_report_date_idx
  ON report_raw_gsc_site (report_date);
CREATE TABLE IF NOT EXISTS report_raw_ghl_contacts (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'ghl',
  source_key TEXT NOT NULL,
  source_window_start DATE,
  source_window_end DATE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  dimensions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  run_id BIGINT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS report_raw_ghl_contacts_uq
  ON report_raw_ghl_contacts (source_system, report_date, source_key);
CREATE INDEX IF NOT EXISTS report_raw_ghl_contacts_report_date_idx
  ON report_raw_ghl_contacts (report_date);
CREATE TABLE IF NOT EXISTS report_raw_ghl_forms (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'ghl',
  source_key TEXT NOT NULL,
  source_window_start DATE,
  source_window_end DATE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  dimensions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  run_id BIGINT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS report_raw_ghl_forms_uq
  ON report_raw_ghl_forms (source_system, report_date, source_key);
CREATE INDEX IF NOT EXISTS report_raw_ghl_forms_report_date_idx
  ON report_raw_ghl_forms (report_date);
CREATE TABLE IF NOT EXISTS report_raw_ghl_opportunities (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'ghl',
  source_key TEXT NOT NULL,
  source_window_start DATE,
  source_window_end DATE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  dimensions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  run_id BIGINT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS report_raw_ghl_opportunities_uq
  ON report_raw_ghl_opportunities (source_system, report_date, source_key);
CREATE INDEX IF NOT EXISTS report_raw_ghl_opportunities_report_date_idx
  ON report_raw_ghl_opportunities (report_date);
CREATE TABLE IF NOT EXISTS report_raw_ghl_pipeline_history (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'ghl',
  source_key TEXT NOT NULL,
  source_window_start DATE,
  source_window_end DATE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  dimensions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  run_id BIGINT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS report_raw_ghl_pipeline_history_uq
  ON report_raw_ghl_pipeline_history (source_system, report_date, source_key);
CREATE INDEX IF NOT EXISTS report_raw_ghl_pipeline_history_report_date_idx
  ON report_raw_ghl_pipeline_history (report_date);
CREATE TABLE IF NOT EXISTS report_raw_ghl_call_outcomes (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'ghl',
  source_key TEXT NOT NULL,
  call_date TIMESTAMPTZ,
  direction TEXT,
  duration_seconds INTEGER,
  disposition TEXT,
  disposition_label TEXT,
  from_number TEXT,
  to_number TEXT,
  contact_id TEXT,
  contact_name TEXT,
  user_id TEXT,
  user_name TEXT,
  ghL_message_id TEXT,
  ghL_conversation_id TEXT,
  ghL_alt_id TEXT,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS report_raw_ghl_call_outcomes_uq
  ON report_raw_ghl_call_outcomes (source_system, report_date, source_key);
CREATE INDEX IF NOT EXISTS report_raw_ghl_call_outcomes_report_date_idx
  ON report_raw_ghl_call_outcomes (report_date);
CREATE INDEX IF NOT EXISTS report_raw_ghl_call_outcomes_disposition_idx
  ON report_raw_ghl_call_outcomes (disposition);
CREATE TABLE IF NOT EXISTS report_bridge_identity_map (
  identity_type TEXT NOT NULL,
  identity_value TEXT NOT NULL,
  normalized_value TEXT NOT NULL,
  ghl_contact_id TEXT,
  ghl_opportunity_id TEXT,
  match_confidence NUMERIC(5,2) NOT NULL DEFAULT 0,
  match_rule TEXT,
  first_seen_at TIMESTAMPTZ,
  last_seen_at TIMESTAMPTZ,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (identity_type, identity_value)
);
CREATE INDEX IF NOT EXISTS report_bridge_identity_map_normalized_idx
  ON report_bridge_identity_map (normalized_value);
CREATE TABLE IF NOT EXISTS report_bridge_traffic_to_lead (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  ga_session_id TEXT NOT NULL DEFAULT '',
  traffic_source TEXT,
  medium TEXT,
  campaign TEXT,
  landing_page TEXT,
  ghl_contact_id TEXT NOT NULL DEFAULT '',
  match_confidence NUMERIC(5,2) NOT NULL DEFAULT 0,
  match_rule TEXT,
  match_reason TEXT,
  source_trace JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS report_bridge_traffic_to_lead_uq
  ON report_bridge_traffic_to_lead (report_date, ga_session_id, COALESCE(ghl_contact_id, ''));
CREATE INDEX IF NOT EXISTS report_bridge_traffic_to_lead_contact_idx
  ON report_bridge_traffic_to_lead (ghl_contact_id, report_date);
CREATE TABLE IF NOT EXISTS report_bridge_lead_to_sale (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  ghl_contact_id TEXT NOT NULL DEFAULT '',
  ghl_opportunity_id TEXT NOT NULL DEFAULT '',
  pipeline TEXT,
  stage TEXT,
  match_confidence NUMERIC(5,2) NOT NULL DEFAULT 0,
  match_rule TEXT,
  match_reason TEXT,
  source_trace JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS report_bridge_lead_to_sale_uq
  ON report_bridge_lead_to_sale (report_date, COALESCE(ghl_contact_id, ''), COALESCE(ghl_opportunity_id, ''));
CREATE INDEX IF NOT EXISTS report_bridge_lead_to_sale_contact_idx
  ON report_bridge_lead_to_sale (ghl_contact_id, report_date);
-- Rollup layer
CREATE TABLE IF NOT EXISTS report_daily_summary (
  report_date DATE PRIMARY KEY,
  sessions INTEGER NOT NULL DEFAULT 0,
  users INTEGER NOT NULL DEFAULT 0,
  new_users INTEGER NOT NULL DEFAULT 0,
  engaged_sessions INTEGER NOT NULL DEFAULT 0,
  engagement_rate NUMERIC(10,4) NOT NULL DEFAULT 0,
  gsc_clicks INTEGER NOT NULL DEFAULT 0,
  gsc_impressions INTEGER NOT NULL DEFAULT 0,
  gsc_ctr NUMERIC(10,4) NOT NULL DEFAULT 0,
  gsc_position NUMERIC(10,4) NOT NULL DEFAULT 0,
  contacts_created INTEGER NOT NULL DEFAULT 0,
  form_submissions INTEGER NOT NULL DEFAULT 0,
  opportunities_created INTEGER NOT NULL DEFAULT 0,
  meetings_booked INTEGER NOT NULL DEFAULT 0,
  closed_won_count INTEGER NOT NULL DEFAULT 0,
  closed_won_revenue NUMERIC(18,2) NOT NULL DEFAULT 0,
  closed_lost_count INTEGER NOT NULL DEFAULT 0,
  emails_sent INTEGER NOT NULL DEFAULT 0,
  emails_opened INTEGER NOT NULL DEFAULT 0,
  emails_clicked INTEGER NOT NULL DEFAULT 0,
  emails_bounced INTEGER NOT NULL DEFAULT 0,
  emails_unsubscribed INTEGER NOT NULL DEFAULT 0,
  emails_complained INTEGER NOT NULL DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS report_channel_daily_summary (
  report_date DATE NOT NULL,
  channel TEXT NOT NULL,
  traffic_source TEXT NOT NULL DEFAULT '',
  source TEXT NOT NULL DEFAULT '',
  medium TEXT NOT NULL DEFAULT '',
  sessions INTEGER NOT NULL DEFAULT 0,
  users INTEGER NOT NULL DEFAULT 0,
  new_users INTEGER NOT NULL DEFAULT 0,
  leads INTEGER NOT NULL DEFAULT 0,
  opportunities INTEGER NOT NULL DEFAULT 0,
  closed_won_revenue NUMERIC(18,2) NOT NULL DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (report_date, channel, traffic_source, source, medium)
);
CREATE TABLE IF NOT EXISTS report_funnel_daily_summary (
  report_date DATE PRIMARY KEY,
  traffic INTEGER NOT NULL DEFAULT 0,
  leads INTEGER NOT NULL DEFAULT 0,
  sales INTEGER NOT NULL DEFAULT 0,
  contact_to_opportunity_rate NUMERIC(10,4) NOT NULL DEFAULT 0,
  opportunity_to_win_rate NUMERIC(10,4) NOT NULL DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS report_pipeline_daily_summary (
  report_date DATE NOT NULL,
  pipeline TEXT NOT NULL,
  leads INTEGER NOT NULL DEFAULT 0,
  opportunities INTEGER NOT NULL DEFAULT 0,
  booked INTEGER NOT NULL DEFAULT 0,
  closed_won_count INTEGER NOT NULL DEFAULT 0,
  closed_won_revenue NUMERIC(18,2) NOT NULL DEFAULT 0,
  closed_lost_count INTEGER NOT NULL DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (report_date, pipeline)
);
CREATE TABLE IF NOT EXISTS report_stage_daily_summary (
  report_date DATE NOT NULL,
  pipeline TEXT NOT NULL,
  stage TEXT NOT NULL,
  stage_count INTEGER NOT NULL DEFAULT 0,
  moved_in_count INTEGER NOT NULL DEFAULT 0,
  moved_out_count INTEGER NOT NULL DEFAULT 0,
  won_count INTEGER NOT NULL DEFAULT 0,
  lost_count INTEGER NOT NULL DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (report_date, pipeline, stage)
);
CREATE TABLE IF NOT EXISTS report_utm_daily_summary (
  report_date DATE NOT NULL,
  source TEXT NOT NULL DEFAULT '',
  medium TEXT NOT NULL DEFAULT '',
  campaign TEXT NOT NULL DEFAULT '',
  content TEXT NOT NULL DEFAULT '',
  term TEXT NOT NULL DEFAULT '',
  landing_page TEXT NOT NULL DEFAULT '',
  sessions INTEGER NOT NULL DEFAULT 0,
  leads INTEGER NOT NULL DEFAULT 0,
  opportunities INTEGER NOT NULL DEFAULT 0,
  closed_won_revenue NUMERIC(18,2) NOT NULL DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (report_date, source, medium, campaign, content, term, landing_page)
);
CREATE TABLE IF NOT EXISTS report_landing_page_daily_summary (
  report_date DATE NOT NULL,
  landing_page TEXT NOT NULL,
  sessions INTEGER NOT NULL DEFAULT 0,
  engaged_sessions INTEGER NOT NULL DEFAULT 0,
  leads INTEGER NOT NULL DEFAULT 0,
  opportunities INTEGER NOT NULL DEFAULT 0,
  form_submissions INTEGER NOT NULL DEFAULT 0,
  closed_won_revenue NUMERIC(18,2) NOT NULL DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (report_date, landing_page)
);
-- Pipeline velocity: per-stage avg days computed from actual pipeline history event timestamps
CREATE TABLE IF NOT EXISTS report_stage_velocity_summary (
  id SERIAL PRIMARY KEY,
  pipeline TEXT NOT NULL,
  stage TEXT NOT NULL,
  opp_count INTEGER NOT NULL DEFAULT 0,
  avg_days_in_stage NUMERIC(10,2) NOT NULL DEFAULT 0,
  min_days INTEGER NOT NULL DEFAULT 0,
  max_days INTEGER NOT NULL DEFAULT 0,
  median_days NUMERIC(10,2) NOT NULL DEFAULT 0,
  total_transitions INTEGER NOT NULL DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (pipeline, stage)
);
-- Pipeline cycle: per-opportunity stage progression with timestamps
CREATE TABLE IF NOT EXISTS report_opp_stage_timeline (
  id SERIAL PRIMARY KEY,
  opportunity_id TEXT NOT NULL,
  pipeline TEXT NOT NULL,
  stage TEXT NOT NULL,
  entered_at TIMESTAMPTZ,
  exited_at TIMESTAMPTZ,
  days_in_stage NUMERIC(10,2) NOT NULL DEFAULT 0,
  is_final BOOLEAN NOT NULL DEFAULT FALSE,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_report_opp_stage_timeline_opp ON report_opp_stage_timeline (opportunity_id);
CREATE INDEX IF NOT EXISTS idx_report_opp_stage_timeline_pipeline_stage ON report_opp_stage_timeline (pipeline, stage);
-- Light-touch bootstrap values so the workflows have a predictable baseline.
INSERT INTO report_source_registry (source_system, source_name, is_required, enabled, notes)
VALUES
  ('ga4', 'Google Analytics 4', TRUE, TRUE, 'Traffic source; active in production.'),
  ('gsc', 'Google Search Console', TRUE, TRUE, 'Organic search source.'),
  ('ghl', 'GoHighLevel', TRUE, TRUE, 'CRM source of truth for leads and sales.'),
  ('velocity', 'Pipeline Velocity', FALSE, TRUE, 'Per-stage avg days from pipeline history timestamps.')
ON CONFLICT (source_system) DO UPDATE
SET source_name = EXCLUDED.source_name,
    is_required = EXCLUDED.is_required,
    enabled = EXCLUDED.enabled,
    notes = EXCLUDED.notes,
  updated_at = NOW();
CREATE TABLE IF NOT EXISTS report_sdr_registry (
  user_id TEXT PRIMARY KEY,
  user_name TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'unknown',
  is_sdr BOOLEAN NOT NULL DEFAULT FALSE,
  email TEXT,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  notes TEXT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO report_sdr_registry (user_id, user_name, role, is_sdr, email, notes)
VALUES
  ('yU85G6kfhtW4vUtx3QE6', 'Jason Bornillo', 'sdr', TRUE, 'jason@livetransparent.com', 'SDR. Also the fallback owner for unassigned follow-up routing.'),
  ('sqGx5rp3oAUG610NXyjU', 'Marc', 'sdr', TRUE, 'marc@livetransparent.com', 'SDR. Marc-routing path; no Marc-owned opps in trigger stages as of 2026-07-30.'),
  ('03p5GatJBH7i9zjMaIzm', 'Cameron Karkut', 'leadership', FALSE, 'cameron@livetransparent.com', 'Co-founder / Head of Sales and Strategy. Owns Regulated Ads calendar SrtXcFVyea7pFl3nTiIK.'),
  ('gePIeuHOEsAiPVA1mfOR', 'Ed Cadorniga', 'exec', FALSE, 'ed@livetransparent.com', 'Co-founder / operations and automation.'),
  ('ck6TRlU3wnTmMxuVpn5F', 'Janvi Mahajan', 'marketing', FALSE, 'janvi@livetransparent.com', 'Partnership + qualification gate owner. Resolved from live GHL users list 2026-09-09; formerly rendered as "Unknown SDR" (ck6TRlU3…). Non-SDR.'),
  ('7s3brzxGF4WSiz95DPkF', 'Kevin Lagudgud', 'staff', FALSE, 'kevin@livetransparent.com', 'GHL user (account admin). No opp ownership in current data; informational.'),
  ('D8NgkeZYX481rR4J2gOc', 'Mike deVries', 'staff', FALSE, 'mike@livetransparent.com', 'GHL user (account admin). No opp ownership in current data; informational.'),
  ('R5VljBpXah3LaVXFNfCV', 'Remus Borela', 'staff', FALSE, 'remus@livetransparent.com', 'GHL user (account admin). No opp ownership in current data; informational.')
ON CONFLICT (user_id) DO UPDATE
SET user_name = EXCLUDED.user_name,
    role = EXCLUDED.role,
    is_sdr = EXCLUDED.is_sdr,
    email = EXCLUDED.email,
    notes = EXCLUDED.notes,
    is_active = TRUE,
    updated_at = NOW();
CREATE TABLE IF NOT EXISTS report_raw_ghl_social_posts (
  post_id TEXT PRIMARY KEY,
  account_id TEXT,
  platform TEXT,
  type TEXT,
  status TEXT,
  summary TEXT,
  error_message TEXT,
  published_at TIMESTAMPTZ,
  scheduled_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ,
  insights JSONB NOT NULL DEFAULT '{}'::jsonb,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_raw_social_posts_platform ON report_raw_ghl_social_posts (platform, status);
CREATE INDEX IF NOT EXISTS idx_raw_social_posts_published ON report_raw_ghl_social_posts (published_at DESC);
CREATE INDEX IF NOT EXISTS idx_raw_social_posts_account ON report_raw_ghl_social_posts (account_id);
CREATE TABLE IF NOT EXISTS report_ghl_social_statistics (
  id BIGSERIAL PRIMARY KEY,
  window_start DATE NOT NULL,
  window_end DATE NOT NULL,
  scope TEXT NOT NULL,
  platform TEXT,
  posts INT,
  likes INT,
  followers INT,
  impressions INT,
  reach INT,
  comments INT,
  saves INT,
  source TEXT NOT NULL DEFAULT 'ghl_statistics',
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT report_ghl_social_statistics_uq UNIQUE (window_start, window_end, scope)
);
CREATE INDEX IF NOT EXISTS idx_ghl_social_statistics_window
  ON report_ghl_social_statistics (window_start, window_end);
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE TABLE IF NOT EXISTS report_sms_sent (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  contact_id text NOT NULL,
  phone text NOT NULL,
  workflow_id text NOT NULL,
  template_id text,
  message_hash text NOT NULL,
  sent_at timestamptz NOT NULL DEFAULT now(),
  provider_response jsonb,
  CONSTRAINT ux_report_sms_unique UNIQUE (contact_id, workflow_id, message_hash)
);
CREATE INDEX IF NOT EXISTS idx_report_sms_sent_sent_at ON report_sms_sent (sent_at);
CREATE TABLE IF NOT EXISTS report_raw_ghl_calls (
  call_id TEXT PRIMARY KEY,
  contact_id TEXT,
  assigned_user_id TEXT,
  location_id TEXT,
  direction TEXT,
  status TEXT,
  duration_ms INTEGER NOT NULL DEFAULT 0,
  started_at TIMESTAMPTZ,
  ended_at TIMESTAMPTZ,
  answered_at TIMESTAMPTZ,
  recording_url TEXT,
  notes TEXT,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_raw_ghl_calls_contact ON report_raw_ghl_calls (contact_id);
CREATE INDEX IF NOT EXISTS idx_raw_ghl_calls_status ON report_raw_ghl_calls (status, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_raw_ghl_calls_started_at ON report_raw_ghl_calls (started_at DESC);
CREATE TABLE IF NOT EXISTS report_raw_ghl_appointments (
  appointment_id TEXT PRIMARY KEY,
  contact_id TEXT,
  calendar_id TEXT,
  assigned_user_id TEXT,
  location_id TEXT,
  title TEXT,
  status TEXT,
  start_at TIMESTAMPTZ,
  end_at TIMESTAMPTZ,
  notes TEXT,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_raw_ghl_appts_contact ON report_raw_ghl_appointments (contact_id);
CREATE INDEX IF NOT EXISTS idx_raw_ghl_appts_status ON report_raw_ghl_appointments (status, start_at DESC);
CREATE INDEX IF NOT EXISTS idx_raw_ghl_appts_start_at ON report_raw_ghl_appointments (start_at DESC);
CREATE TABLE IF NOT EXISTS voice_call_queue (
  queue_id uuid PRIMARY KEY,
  contact_id text NOT NULL,
  first_name text,
  phone_e164 text NOT NULL,
  campaign_id text NOT NULL,
  lead_timezone text,
  status text NOT NULL default 'pending',
  dnc boolean NOT NULL default false,
  max_attempts integer NOT NULL default 3,
  attempt_count integer NOT NULL default 0,
  phone_candidates jsonb,
  phone_index integer NOT NULL default 0,
  last_attempt_at timestamptz,
  next_attempt_at timestamptz,
  locked_at timestamptz,
  lock_owner text,
  created_at timestamptz NOT NULL default now(),
  updated_at timestamptz NOT NULL default now()
);
CREATE INDEX IF NOT EXISTS idx_voice_call_queue_status_next_attempt
  ON voice_call_queue(status, next_attempt_at);
CREATE TABLE IF NOT EXISTS voice_call_attempt (
  call_id uuid PRIMARY KEY,
  queue_id uuid NOT NULL REFERENCES voice_call_queue(queue_id),
  contact_id text NOT NULL,
  provider_call_id text,
  idempotency_key text NOT NULL UNIQUE,
  started_at timestamptz NOT NULL default now(),
  ended_at timestamptz,
  disposition text NOT NULL,
  qualified_intent_fit boolean NOT NULL default false,
  booking_attempted boolean NOT NULL default false,
  booking_result text NOT NULL default 'not_attempted',
  handoff_required boolean NOT NULL default false,
  handoff_reason text,
  summary text,
  transcript_url text,
  recording_url text,
  created_at timestamptz NOT NULL default now()
);
CREATE INDEX IF NOT EXISTS idx_voice_call_attempt_queue_id
  ON voice_call_attempt(queue_id);
CREATE TABLE IF NOT EXISTS voice_call_transcript_turn (
  turn_id bigserial PRIMARY KEY,
  call_id uuid NOT NULL REFERENCES voice_call_attempt(call_id) ON DELETE CASCADE,
  turn_index integer NOT NULL,
  speaker text NOT NULL,
  utterance text NOT NULL,
  timestamp_utc timestamptz NOT NULL,
  created_at timestamptz NOT NULL default now()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_voice_call_transcript_turn_unique
  ON voice_call_transcript_turn(call_id, turn_index);
CREATE TABLE IF NOT EXISTS report_meta_campaign_map (
  id SERIAL PRIMARY KEY,
  ad_account_id TEXT NOT NULL,
  ad_account_name TEXT,
  campaign_id TEXT,
  campaign_name TEXT,
  campaign_status TEXT,
  adset_id TEXT,
  adset_name TEXT,
  adset_status TEXT,
  ad_id TEXT,
  ad_name TEXT,
  ad_status TEXT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (ad_account_id, COALESCE(campaign_id, ''), COALESCE(adset_id, ''), COALESCE(ad_id, ''))
);
CREATE INDEX IF NOT EXISTS idx_meta_campaign_map_campaign_name
  ON report_meta_campaign_map (campaign_name);
CREATE INDEX IF NOT EXISTS idx_meta_campaign_map_adset_name
  ON report_meta_campaign_map (adset_name);
-- Meta Ads daily performance — time-series data from Insights API
CREATE TABLE IF NOT EXISTS report_meta_ads_daily_summary (
  report_date DATE NOT NULL,
  ad_account_id TEXT NOT NULL,
  ad_account_name TEXT,
  campaign_id TEXT NOT NULL,
  campaign_name TEXT NOT NULL,
  adset_id TEXT,
  adset_name TEXT,
  ad_id TEXT NOT NULL,
  ad_name TEXT NOT NULL,
  impressions INTEGER DEFAULT 0,
  clicks INTEGER DEFAULT 0,
  spend NUMERIC(12,2) DEFAULT 0,
  leads INTEGER DEFAULT 0,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (report_date, ad_id)
);
CREATE INDEX IF NOT EXISTS idx_meta_ads_daily_date
  ON report_meta_ads_daily_summary (report_date DESC);
CREATE INDEX IF NOT EXISTS idx_meta_ads_daily_campaign
  ON report_meta_ads_daily_summary (campaign_name);
-- Seed campaign map from live Meta API query (2026-05-07)
-- act_975543647768982 — Livetransparent
INSERT INTO report_meta_campaign_map (ad_account_id, ad_account_name, campaign_id, campaign_name, campaign_status, adset_id, adset_name, adset_status, ad_id, ad_name, ad_status) VALUES
('act_975543647768982','Livetransparent','120247206237760159','Transparent-LeadForm-List','ACTIVE','120247206237750159','List-11.20.25','ACTIVE',null,null,null),
('act_975543647768982','Livetransparent','120246336171860159','LV-Template','PAUSED','120246336171870159','New Traffic Ad Set','ACTIVE',null,null,null),
('act_975543647768982','Livetransparent','120246017455700159','Transparent-Posts','PAUSED','120246017455690159','List-11.20.25','ACTIVE',null,null,null),
('act_975543647768982','Livetransparent','120241213439880159','Transparent-LeadForm-MJBizCon','ACTIVE','120241213439870159','Convention-11.20.25','ACTIVE',null,null,null),
('act_975543647768982','Livetransparent','120241212056450159','Transparent-Traffic-MJBiz','ACTIVE','120241300131650159','ConventionLAL-11.20.25','ACTIVE',null,null,null),
('act_975543647768982','Livetransparent','120241212056450159','Transparent-Traffic-MJBiz','ACTIVE','120241212056430159','Convention-11.20.25','ACTIVE',null,null,null),
('act_975543647768982','Livetransparent','120241058805550159','Transparent-Traffic','ACTIVE','120248139310460159','List-11.20.25 - Copy','ACTIVE',null,null,null),
('act_975543647768982','Livetransparent','120241058805550159','Transparent-Traffic','ACTIVE','120241058805570159','List-11.20.25','PAUSED',null,null,null),
('act_975543647768982','Livetransparent','120240619542520159','Transparent-LeadForm-Rem','ACTIVE','120240619542530159','List-11.20.25','ACTIVE',null,null,null),
('act_24843211111954088','Livetransparent-2','120244608199430363','HYPE-Stilo Supply - Shop Now V1 - April (Evergreen) - DTS','ACTIVE','120244608199420363','Stilo Supply - Shop Now V1 Ad 1 - April 22 to Evergreen - DTS','ACTIVE',null,null,null),
('act_24843211111954088','Livetransparent-2','120244608146670363','HYPE-Chkn''n Wafflez - Shop Now V1 - April (Evergreen) - DTS','ACTIVE','120244608182680363','Chkn''n Wafflez - Shop Now V1 Ad 1 - April 22 to Evergreen - DTS','ACTIVE',null,null,null),
('act_24843211111954088','Livetransparent-2','120244518262720363','Hyperwolf - Template','PAUSED','120244518262730363','Hyperwolf - Shop Now V1 Ad 1 - April 22 to Evergreen - DTS','ACTIVE',null,null,null),
('act_24843211111954088','Livetransparent-2','120244443459370363','HYPE-Hyperwolf - Shop Now V1 - April (Evergreen) - DTS','ACTIVE','120244443459380363','Hyperwolf - Shop Now V1 Ad 1 - April 22 to Evergreen - DTS','ACTIVE',null,null,null)
ON CONFLICT (ad_account_id, COALESCE(campaign_id, ''), COALESCE(adset_id, ''), COALESCE(ad_id, '')) DO UPDATE SET
  campaign_name = EXCLUDED.campaign_name, campaign_status = EXCLUDED.campaign_status,
  adset_name = EXCLUDED.adset_name, adset_status = EXCLUDED.adset_status,
  updated_at = NOW();
-- LinkedIn connection state store
CREATE TABLE IF NOT EXISTS linkedin_connection_state (
  ghl_contact_id TEXT PRIMARY KEY,
  location_id TEXT NOT NULL,
  unipile_account_id TEXT NOT NULL DEFAULT '',
  linkedin_profile_url TEXT NOT NULL DEFAULT '',
  linkedin_public_identifier TEXT NOT NULL DEFAULT '',
  linkedin_provider_id TEXT NOT NULL DEFAULT '',
  connection_request_tag TEXT NOT NULL DEFAULT 'linkedin_connection_requested',
  connection_status TEXT NOT NULL DEFAULT 'requested',
  request_sent_at TIMESTAMPTZ,
  connected_at TIMESTAMPTZ,
  dm_sequence_started_at TIMESTAMPTZ,
  last_checked_at TIMESTAMPTZ,
  request_message TEXT,
  request_message_hash TEXT,
  sequence_step INTEGER NOT NULL DEFAULT 0,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS linkedin_connection_state_provider_uq
  ON linkedin_connection_state (unipile_account_id, linkedin_provider_id)
  WHERE linkedin_provider_id <> '';
CREATE UNIQUE INDEX IF NOT EXISTS linkedin_connection_state_identifier_uq
  ON linkedin_connection_state (unipile_account_id, linkedin_public_identifier)
  WHERE linkedin_public_identifier <> '';
CREATE INDEX IF NOT EXISTS linkedin_connection_state_status_idx
  ON linkedin_connection_state (connection_status, updated_at DESC);
````

## File: reports/nginx.conf
````ini
# Report queries are expensive but safe to cache briefly. The lock prevents
# simultaneous cold requests from stampeding the n8n/Postgres backend.
proxy_cache_path /var/cache/nginx/report-api levels=1:2 keys_zone=report_api_cache:10m max_size=100m inactive=10m use_temp_path=off;

server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    proxy_read_timeout 300s;
    proxy_send_timeout 300s;
    proxy_connect_timeout 10s;

    location /api/report/executive/summary {
        proxy_pass http://n8n:5678/webhook/lt-report-executive-summary;
        proxy_cache report_api_cache;
        proxy_cache_methods GET;
        proxy_cache_key "$scheme$request_method$host$uri|range=$arg_range|from=$arg_from|to=$arg_to";
        proxy_cache_valid 200 30m;
        proxy_cache_lock on;
        proxy_cache_lock_timeout 300s;
        proxy_cache_lock_age 300s;
        proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
        add_header X-Report-Cache $upstream_cache_status always;
        proxy_set_header Host n8n;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }

    location /api/report/executive/outgoing-calls {
        proxy_pass http://n8n:5678/webhook/lt-report-outgoing-calls;
        proxy_set_header Host n8n;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }

    location /api/report/executive/campaign-channels {
        proxy_pass http://n8n:5678/webhook/lt-report-campaign-channel-summary;
        proxy_cache report_api_cache;
        proxy_cache_methods GET;
        proxy_cache_key "$scheme$request_method$host$uri|range=$arg_range|from=$arg_from|to=$arg_to";
        proxy_cache_valid 200 30m;
        proxy_cache_lock on;
        proxy_cache_lock_timeout 300s;
        proxy_cache_lock_age 300s;
        proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
        add_header X-Report-Cache $upstream_cache_status always;
        proxy_set_header Host n8n;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }

    location /api/report/executive-v1/facts {
        proxy_pass http://n8n:5678/webhook/lt-report-executive-v1-facts;
        proxy_cache report_api_cache;
        proxy_cache_methods GET;
        proxy_cache_key "$scheme$request_method$host$uri|range=$arg_range|from=$arg_from|to=$arg_to";
        proxy_cache_valid 200 30m;
        proxy_cache_lock on;
        proxy_cache_lock_timeout 300s;
        proxy_cache_lock_age 300s;
        proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
        add_header X-Report-Cache $upstream_cache_status always;
        proxy_set_header Host n8n;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_read_timeout 120s;
    }

    location / {
        add_header Cache-Control "no-store, no-cache, must-revalidate, max-age=0" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
        try_files $uri $uri/ =404;
    }
}
````

## File: Project Specifications.md
````markdown
# Project Specifications: Outbound Voice Agent and Social Outreach

> **Before reading this file, first review `repomix-output.md` for full system architecture, blueprints, and roadmaps.** This file defines boundaries, guardrails, and contracts; it does not repeat the architecture.

## Purpose

Production outbound calling flow for Vapi + n8n + GHL. The agent introduces LiveTransparent, qualifies intent and fit, records call context, and routes outcomes through tool calls.

## Canonical Status

- Current live state and priority order: [Project Status and Next Steps.md](./Project%20Status%20and%20Next%20Steps.md)

## System Boundaries

- Vapi: realtime voice runtime.
- n8n: queueing, dispatch, callback routing, persistence, CRM sync.
- GHL: contact, opportunity, note, and tag system of record.
- Postgres: call-attempt and transcript metadata store.

### Qualification and SDR Boundary

- Warm is the unassigned intake and verification layer.
- The canonical classification tags are `qualified` for a regulated business, including nicotine, cannabis, CBD, vape, hemp, and related verticals, and `not qualified` for a non-regulated business.
- `qualified` is the regulated-business classification gate and routes qualified opportunities to `Sales Outreach -> Qualified`.
- SDR assignment happens only at Sales Outreach entry: align a single existing owner, preserve matching owners, flag conflicting owners, or assign Jason/Marc 50/50 when neither record has an owner.
- Contact native `assignedTo`, opportunity native `assignedTo`, and custom opportunity `Owner` must remain aligned.
- Vapi handles classified regulated-business contacts in Warm and excludes `not qualified` contacts. Raw pool tags must not bypass the canonical classification result.
- A successful Vapi warm transfer is manually claimed by the answering SDR and promoted to Sales Outreach. Vapi booking remains on Cameron's Regulated Ads calendar.

### Scheduling Contract

- Recurring n8n workflows must use n8n's native `Schedule Trigger` node.
- Do not create OS, Coolify, or external cron jobs for workflow scheduling.
- The Vapi dialer runs from a two-minute Schedule Trigger and applies its timezone-aware business-hours guard before dispatching a call.
- `LT - Voice Dequeue Next` is an unpublished helper and must not be used as an automatic call-start path. Callback completion must not trigger another dequeue request.
- `LT - Voice Queue Enqueue` is authenticated with `X-LT-Voice-Queue-Secret` using the `VOICE_QUEUE_ENQUEUE_SECRET` deployment/reference value.
- Callback timer state is deduplicated within 60 seconds and pruned after 30 minutes.

## Live Workflows

| Workflow | ID | Role |
|----------|----|------|
| LT - Voice Agent V1 Outbound Dialer (Vapi) | `r7UjWLndmc6EqEUW` | Queue poller, timezone guard, call dispatch |
| LT - Voice Agent V1 Vapi Callback + Tools | `fx4UvKUWbqJEY3LK` | End-of-call webhook plus 4 tool endpoints |

## Social Outreach Scope

### Current Live LinkedIn State

- `LT - GHL LinkedIn Connect Dispatcher (Unipile)` is active and uses the invite copy from `outreach_messages.v2.docx`.
- `LT - LinkedIn DM Sequence (Unipile)` is active and uses the LinkedIn DM copy from `outreach_messages.v2.docx`.
- `LT - LinkedIn Unipile New Messages` is active and marks active conversations when inbound replies arrive. Its inbound normalizer must preserve the malformed form-payload fallback because Unipile can send unescaped JSON as the sole form body key; removing that fallback can lose reply sender/message fields.
- LinkedIn DM sends are blocked when `payload_json.dm_conversation_status = 'active'`.

### LinkedIn Timing

- The current LinkedIn DM cadence is approximately day 0, day 3, day 7, and day 10, with terminal completion at day 14.
- The first message starts the clock by setting `dm_sequence_started_at`.
- Sequence state is stored in `linkedin_connection_state`.

### LinkedIn State Requirements

- Use one canonical state row per contact.
- Persist `sequence_step`, `dm_sequence_started_at`, and `payload_json`.
- Preserve reply state when a contact enters active conversation.
- Never send duplicate LinkedIn DMs once a reply is detected.
- If someone responds on LinkedIn, immediately suppress them from all remaining automated LinkedIn DMs and persist that suppression in the shared state.
- State sync must use bounded direct HTTP calls with explicit retry/error reporting; API failures must not be reported as an empty healthy scan.
- Connection dispatch must atomically claim a `ready` row before an invite and perform a live GHL suppression/reply check immediately before sending.
- The state-upsert boundary uses the protected n8n `httpHeaderAuth` credential `LT LinkedIn State Upsert Webhook` and requires `X-LT-LinkedIn-State-Secret`. Callers must send the shared header; do not reuse an unrelated webhook secret. In Community Edition, each relevant workflow stores `stateUpsertSecret` in its single `Config` node and Code nodes read that value instead of embedding the literal. The secret is not stored in the repository.

### Partnership LinkedIn State

- Partnership LinkedIn state is isolated in `partnership_linkedin_connection_state` with `source_key = 'partnership'`; it must not be conflated with the main `linkedin_connection_state` table.
- The partnership dispatcher seeds `ready` rows from GHL contacts tagged `partner_candidate_linkedin` before reading its ready queue. The 2026-07-31 seed produced 127 rows.
- Partnership Email Dispatcher, LinkedIn Dispatcher, and LinkedIn DM Sequence have been live with `defaultDryRun=false` since explicit approval on 2026-07-31. Do not manually execute them unless an additional live batch is intentional.
- Before changing or republishing a send-capable path, verify GHL suppression/reply checks, state-upsert authentication, idempotent claims, release-log writes, and the exact active version. A successful dry run or readable PIT is not sufficient evidence for safe production sending.

### SMS Campaign Scope

- `outreach_messages.docx` is the source of truth for SMS copy.
- SMS is implemented as a SimpleTexting campaign stack, not as one-off ad hoc messages.
- The campaign uses a controlled pool dispatcher, a sequencer, and a shared send endpoint.
- The SMS workflow needs per-contact send tracking so each message can be marked as sent once and never repeated.
- The SMS workflow also needs response ingestion so replies update the same canonical state used by the send workflow.
- The SMS workflow should preserve unsubscribe handling and should not send to opted-out contacts.
- Replies should trigger a Slack notification in `#lead` so the team can respond without checking n8n first.
- The preferred model is a shared Postgres state table or a tightly controlled send-state plus response-state pair, but the same contact record must be authoritative for both send and reply logic.

### SMS Missing Steps

1. Normalize SMS copy from `outreach_messages.docx` into a template registry.
2. Define the SMS state schema and idempotency keys.
3. Build the SimpleTexting send workflow with batching controls.
4. Wire inbound reply and delivery webhooks into the same state model.
5. Confirm opt-out / unsubscribe propagation.
6. Run a low-volume smoke test before batch sends.
7. Deploy the staged SMS workflows into live n8n and verify the live webhook routes.

## Queue Contract

Minimum live `voice_call_queue` fields:

`queue_id`, `contact_id`, `phone_e164`, `campaign_id`, `status`, `attempt_count`, `max_attempts`, `next_attempt_at`, `dnc`, `first_name`, `lead_timezone`

Injected Vapi variables:

`contact_id`, `queue_id`, `campaign_id`, `lead_timezone`, `first_name`

Planned qualification extension: add `ai_qualification_state` only after the authoritative qualification workflow and field/tag contract has been identified and migrated through the live queue, dialer, and callback paths.

Normalized callback output:

`call_id`, `contact_id`, `queue_id`, `disposition`, `summary`, `transcript_text`, `recording_url`

## GHL Configuration

- Secrets: `GHL_PIT` aliased as `GHL_API_KEY`, `GHL_LOCATION_ID=Zwz4relUXVPxx8uohnjV`
- The root `GHL_PIT` was directly verified on 2026-07-31 against the official REST location and contacts endpoints with HTTP 200. PIT access confirms CRM/API access only; it does not authenticate the Firebase/browser session used by the native Custom Report builder.
- Native GHL Custom Report widget layout has no supported public API/SDK mutation surface. Use the authenticated GHL UI or an explicitly approved internal API path; do not infer report-builder access from successful PIT REST calls.
- Voice write actions: add `vapi_*` tags per outcome, create contact notes for completed calls

## Guardrails

- Do not call `dnc=true` contacts.
- Respect `attempt_count < max_attempts`.
- Enforce 72h cooldown between attempts.
- Call only Mon-Fri 9am-5pm CT.
- The native Schedule Trigger controls polling frequency; the workflow guard controls call eligibility.
- Fall back to GHL contact timezone when queue timezone is missing; use CT 12-2pm safe window if neither is available.
- Keep secrets in env/credentials; do not hardcode them in workflow JSON.
- Do not enqueue AI-qualified or explicitly rejected/non-cannabis contacts for Vapi. Vapi queue eligibility is limited to AI-pending/unverified Warm contacts.
- Keep Vapi warm transfer separate from Cameron calendar booking. Transfer uses the shared SDR number; booking uses Cameron's Regulated Ads calendar.
- Preserve n8n graph integrity when editing workflows.
- For social outreach, never send duplicate messages. Every send workflow must check and update shared state before and after send.
- For social outreach, reply-handling workflows must mark the contact as in conversation so follow-up sequences stop.
- For SMS, keep the batch size controlled until reply capture, opt-out propagation, and Slack alerts have all been verified live.

## Callback Tools

- `update_lead_status`: GHL tag plus Postgres disposition update.
- `add_to_dnc`: set `voice_call_queue.dnc=true` and add the GHL DNC tag.
- `log_call_outcome`: upsert `voice_call_attempt` with disposition, notes, and follow-up time.
- `notify_sales`: post lead name and summary into `#leads`.
- Vapi API-managed `transferCall`: warm-transfer to the shared SDR number using neutral Sales Lead language.

## Voice Tags

- `vapi_call_attempted`
- `vapi_dnc`
- `vapi_human_answered`
- `vapi_interested`
- `vapi_not_interested`
- `vapi_interest_unknown`
- `vapi_voicemail`
- `vapi_voicemail_left`
- `vapi_no_answer`
- `vapi_busy`
- `vapi_wrong_number`
- `vapi_contact_disconnected`

## Smoke Test

1. Seed one queue row with a controlled test number.
2. Run the outbound workflow manually.
3. Confirm the Vapi request includes expected metadata.
4. Send a simulated callback payload.
5. Confirm Postgres insert plus GHL note creation.
6. Replay the callback and confirm no duplicate record.
7. Confirm AI-qualified contacts are excluded from the Vapi queue and a successful warm transfer remains manually claimable by the answering SDR.

## Social Outreach Smoke Test

1. Verify LinkedIn invite and DM copy are still sourced from `outreach_messages.v2.docx`.
2. Send one LinkedIn test DM and confirm `linkedin_connection_state` advances exactly one step.
3. Simulate an inbound LinkedIn reply and confirm `dm_conversation_status` becomes `active`.
4. Confirm the active conversation is excluded from both LinkedIn DM send paths.
5. Confirm a replied LinkedIn contact stays excluded from all later automated DM steps, not just the next scheduled run.
6. Prepare a single SMS test contact and confirm one SMS send is tagged in state.
7. Simulate an inbound SMS reply and confirm the response workflow updates the same canonical state.
8. Confirm unsubscribe handling blocks any future SMS sends for opted-out contacts.
````

## File: plan.md
````markdown
# Plan Pointer

> **ARCHIVE / HISTORICAL.** This file is a chronological log of completed work and older baselines. It is NOT the operational source of truth. For current status, open issues, and next steps use **`Project Status and Next Steps.md`** (canonical) and the latest dated handoff under `docs/sessions/`. Per AGENTS.md document precedence, this file ranks last.
>
> **Before reading this file, first review `repomix-output.md` for full system architecture, blueprints, and roadmaps.** This plan tracks active work items; it does not repeat the architecture.

## ✅ 2026-09-17: Apollo C-Suite and Marketing September 2026 GHL batch closeout

- Prepared 485 source rows for GHL; 477 apparent new-contact rows remained after 8 exact-email matches. The operator completed the import and the 32 phone-collision retry rows with values moved to `Em_All_Known_Phones`.
- Directly reconciled 114 missing source-email tags by email-based GHL upsert; all returned contact IDs and verified tags. GHL’s aggregate tag search remained incomplete and reported 395 contacts.
- Reconciled opportunities for the 395 searchable tagged contacts into `Sales Outreach -> New`: 361 ended in the requested stage, 25 already had opportunities elsewhere and were left unchanged, and 9 transient create errors were confirmed afterward to already have the requested opportunity. No duplicate opportunities were created by the final state.
- Detailed handoff: `docs/sessions/2026-09-17-apollo-csuite-sep2026-ghl-import-closeout.md`.

## ✅ 2026-09-09: Executive Report — SDR Performance & Owner Attribution (Phases 1–5 IMPLEMENTED; monitoring/sign-off remains)

- Request: track booked meetings by SDR for Cameron's end-of-month SDR assessment (focus SQL/booked meetings), plus marketing's requirements for owner/SDR attribution everywhere, booked meetings by SDR, showed/no-show by SDR, SQLs created by SDR, MQL→SQL conversion by SDR, clarification of the former owner-labelled active deals view, and lead-source breakdown for MQL/SQL.
- **Verified:** owner data is already captured by the ingests (opportunities `dimensions_json->>'assigned_to'`, appointments `assigned_user_id`+`contact_id`, contacts `payload_json`). The Exec Summary SQL never projected any owner field. Root causes: `meetingsBooked` KPI (opportunity-stage-based via Daily Rollups) vs Meetings panel (appointments by `start_at`) were two different sources → 3 vs 7; "Team Active Deals" is the team-wide payload relabeled.
- **Phases 1–2 IMPLEMENTED + verified:** `report_sdr_registry` (user map) + owner-coverage health probes; Daily Rollups carries `assigned_to`; Exec Summary returns `sdrPerformance` per-owner rows + `meetingsBooked` aligned to appointments (`basis appointments_start_at`); `SET jit=off` (16–19s). Frontend build `2026-09-09-v28-sdr-performance`.
- **Phase 4 IMPLEMENTED + verified:** Exec Summary adds `leadSourceBreakdown`/`leadSourceCoverage` (MQL/SQL by originating source: contact first UTM → bridge fallback → GHL `source`; "Unknown / Unattributed" for unresolvable rows). Active version `162bbba8…`. Frontend build `2026-09-09-v29-lead-source` with Lead Source panel + glossary.
- **Post-implementation follow-up:** monitor the 08:00 LA meeting-outcome reminder and Showed/No-show updates, obtain Cameron/Janvi sign-off on the ranking wording (Booked + SQLs + MQL→SQL), reconcile MQL definitions if needed, and verify future booking SDR capture at runtime. Janvi and the previously unknown owner IDs are resolved and seeded.
- Full plan: `docs/sessions/2026-09-09-executive-report-sdr-attribution-plan.md`. Implementation + verification: `docs/sessions/2026-09-09-executive-report-sdr-attribution-phase1-2.md` and `docs/sessions/2026-09-09-executive-report-sdr-attribution-phase4-lead-source.md`.

## ✅ 2026-08-20: Emerald/DAN/Partnership release-log fix + Apollo August enrollment

- Fixed the same release-log single-row write bug (`runOnceForAllItems` + `$json` read only the first item) in all three campaign dispatchers:
  - Emerald `8UXlpoMJnQ229AuG` → published `d6737e68`
  - DAN `toUG1yPDmFG48KEP` → published `f8f29288`
  - Partnership `Xshck23cKo1yXL9D` → published `2663f32b`
- Enrolled 73 clean `apollo_august2026` contacts (from `Sales - New Leads - Cannabis _ Hemp _ CBD.csv`) into Emerald **Executives MSO** via dispatcher run `769889`; all confirmed enrolled in GHL and marked released + release-logged. 12 pre-existing Emerald contacts + 1 DAN-only were skipped.
- Backfilled release-log + released status for 58 prior-run contacts the bug left unlogged → **0 pending+unlogged candidates**, no re-dispatch risk.
- Postgres campaign tables live in the `postgres` default DB (container `postgres-uokgs4c04ko0s4scccg40cgg`), not `n8n`.

## ✅ RESOLVED: 2026-08-12 Postgres Write Blocker & Executive Report Runtime Recovery

### Documentation Review (2026-08-12)

Full cross-file documentation review completed. Fixed 18 issues across 4 files (AGENTS.md, plan.md, Project Status.md, docs/handoff/2026-08-12-report-recovery.md). Key fixes: redacted 3 exposed secrets, updated stale `ghl_contact_id` from `0/13,868` to `13,755/13,868`, marked Sales Ingest repair and Call Outcome auth as DONE, resolved 6 cross-file contradictions (SimpleTexting status, DAN candidateLimit, Partnership dry-run→live, Reply Backfill version ID, Emerald HTTP wrapper severity, implementation order indentation). `repomix-output.md` was regenerated at end of session.

### Summary

The n8n Postgres node v2.5/2.6 has a known bug where parameterized queries (`$1, $2, ...` with `queryReplacement`) silently fail to persist data. The node reports execution success but data never reaches the database. This affects ~25 Postgres nodes across ~12 workflows.

### Current State (2026-08-12)

| Component | Status |
|-----------|--------|
| **n8n container** (DB_TYPE=postgresdb, persisted encryption key) | ✅ Running; recreated after credential decryption mismatch |
| **External task runner** (n8nio/runners-custom) | ✅ Running; direct `pg` and real Code-node transaction verified in execution `742843` |
| **Workflow publication recovery** | ✅ 85 published versions recreated after DB switch; individual active states still require live checks |
| **emerging_pool_contacts** (13,868 rows) | ✅ Created from CSVs |
| **DAN_Release_Log, Emerald_Release_Log** | ✅ Tables created |
| **Email_Events** | ✅ Table created (empty) |
| **LinkedIn workflows** (6 workflows, 16 nodes) | ✅ Build SQL → Postgres pattern applied |
| **Campaign/Email workflows** (4 workflows, 4 nodes) | ✅ Build SQL → Postgres pattern applied |
| **GHL Leads Ingest** (4 Postgres nodes) | ✅ Build SQL → Postgres pattern applied |
| **Frontend fixes** (CSS, mappings, CORS proxies) | ✅ Deployed to reports.livetransparent.com |
| **nginx config** (campaign channel + outgoing calls proxies) | ✅ Deployed |
| **Executive Summary endpoint** | ✅ Public HTTP 200 with real JSON payload; verified 2026-08-12 |

### Resolution

The custom runner now installs `pg@8.21.0` in a clean npm build stage, copies the isolated dependency tree to `/opt/pg-node_modules`, and sets `NODE_PATH` both in the runner container and task-runner configuration. This avoids copying n8n's pnpm symlinks and preserves the runner's own dependency metadata.

**Verification:**
1. `docker build --pull -t n8nio/runners-custom:latest n8n/runners` succeeds on the VPS.
2. `require('pg').Client` resolves as `function` inside the deployed runner with `NODE_PATH=/opt/pg-node_modules`.
3. Real GHL Leads Ingest execution `742843` loaded `pg` and committed the atomic transaction successfully.

The repository deployment helper is `scripts/deploy/deploy_runner.py`; the reference compose file mounts the checked-in runner configuration.

### Completed Fixes (2026-08-11 session)

| Fix | Details |
|-----|---------|
| **Frontend CSS** | Added `.divider` and `.sub-head` rules |
| **Frontend stage names** | Added 8 missing stage ID mappings + Partnership Pipeline |
| **Frontend CORS proxy** | Campaign channel summary now uses `/api/report/executive/campaign-channels` |
| **Frontend outgoing calls** | Fixed hardcoded `range=7d`, added page reset, proxy route works |
| **nginx proxies** | Both campaign-channels and outgoing-calls return HTTP 200 |
| **Email_Events table** | Created with indexes, waiting for data flow |
| **emerging_pool_contacts** | Recreated from CSVs: 13,868 rows (3,668 brands, 10,200 dispensaries) |
| **DAN/Emerald Release Logs** | Tables created |
| **GHL Leads Ingest** | Active hourly; atomic writes and cursor-pair pagination verified |
| **n8n DB migration** | Switched from SQLite to PostgreSQL (DB_TYPE=postgresdb) |
| **n8n encryption** | Configured N8N_ENCRYPTION_KEY for credential decryption |
| **n8n published versions** | 85 published versions created (were missing after DB switch) |

### Data Pipeline Status

```
✅ report_raw_ghl_contacts (controlled batch: 500/500 distinct contacts)
✅ report_raw_ghl_opportunities (7,984 rows via execution 743094)
✅ report_raw_ghl_pipeline_history (7,984 rows via execution 743094)
✅ emerging_pool_contacts (13,868 rows; 12,639 with ghl_contact_id, 1,229 null — not in exports)
⚠️ voice_call_queue (3 pending rows)
❌ voice_call_attempt (empty — post-recovery baseline; dialer Postgres nodes migrated to direct pg)
❌ Email_Events (empty — post-recovery baseline)
✅ linkedin_activity_events (28 rows; Reply Backfill execution 743291 succeeded)
✅ DAN_Release_Log (table exists, 0 rows — post-recovery baseline)
✅ Emerald_Release_Log (table exists, 0 rows — post-recovery baseline)
```

### Follow-up Verification Required

1. ~~**CRITICAL: GHL Sales Ingest** — workflow `aYT5oHcgmBALzHy5` active version `4f3e8068-8864-4b4d-9286-ba4d618cc3a8`; execution `742754` fails at `Fetch Opportunities` with HTTP `401`. Fix auth, migrate both Postgres writes to one atomic direct-`pg` transaction, publish, run, and verify database metadata.~~ **DONE.** Published version `91603d56`; execution `743094` wrote 7,984 opportunities + 7,984 pipeline history rows.
2. **CRITICAL: source recovery** — opportunities now restored. Recover voice attempts/outcomes, email events, release logs, main LinkedIn state, and SimpleTexting state one source at a time through controlled ingest/replay; do not fabricate history. LinkedIn Reply Backfill succeeded (execution `743291`).
3. ~~**CRITICAL: webhook auth/outbound gates**~~ **DONE for Call Outcome Ingest and SimpleTexting send/callback boundaries**. Review the remaining Warm intake authentication; do not manually run live senders/dialer without approval.
4. **HIGH: ghl_contact_id backfill** — raw contact ingest is confirmed; audit candidate matches before changing the current `12,639/13,868` linkage (1,229 null — not in GHL exports).
5. ~~**HIGH: voice persistence** — verify the published dialer release-lock fix and callback/attempt writes safely.~~ **DONE.** Dialer (4 nodes) and callback (8 nodes) migrated from Postgres v2.6 to direct `require('pg')`. Published versions `b8e9c57a` and `c97480db`.
6. **HIGH: migrate embedded secrets** to Config nodes (Community Edition cannot use env vars in Code nodes), then rotate exposed values.
7. ~~**MEDIUM: Executive Summary SQL** — remove duplicate response keys and verify JSON shape.~~ **DONE.** Published version `d458117c`.
8. ~~**MEDIUM: Executive Report** — fix timezone normalization and selected-period date filters.~~ **DONE.** Both report workflows fixed and published.
9. **LOW: cleanup** — remove disconnected legacy nodes/scripts only after live paths are stable.
9. **Guardrail: encryption-key continuity** — keep the Coolify persisted key; replacing it makes existing credentials unreadable.

### Next Agent Immediate Start

Do not infer the next task from the historical plan below. Open `docs/handoff/2026-08-12-report-recovery.md` and follow `Next Agent: Start Here` exactly. The GHL Sales Ingest (`aYT5oHcgmBALzHy5`) repair is DONE — published version `91603d56`, execution `743094` wrote 7,984 opportunities + 7,984 pipeline history rows. The next implementation task is source coverage restoration: recover voice attempts/outcomes, email/release logs, main LinkedIn state, and SimpleTexting state one source at a time through controlled ingest/replay. Do not fabricate historical data.

### Key Files

- `n8n/runners/Dockerfile` — Custom runner image definition
- `n8n/runners/n8n-task-runners.json` — Runner config with pg allowlist
- `n8n/docker-compose.yml` — Reference docker-compose (contains NODE_FUNCTION_ALLOW_EXTERNAL)
- `scripts/utilities/vapi_audit.py` — VPS SSH utility for DB queries
- `scripts/social-reporting/report_runtime_audit.py` — VPS/container/network/report endpoint diagnostics
- `scripts/n8n/align_n8n_encryption_key.py` — recreates n8n with the persisted Coolify encryption key; review before reuse
- `scripts/deploy/deploy_runner.py` — rebuilds and deploys the custom external runner

- Canonical status: [Project Status and Next Steps.md](./Project%20Status%20and%20Next%20Steps.md)
- Session handoff: [docs/handoff/2026-08-12-report-recovery.md](./docs/handoff/2026-08-12-report-recovery.md)
- Company Instagram-page DM handoff: [docs/sessions/2026-08-14-company-instagram-page-dm-handoff.md](./docs/sessions/2026-08-14-company-instagram-page-dm-handoff.md)
- Active work now spans the **Emerald email campaign** (activated 2026-07-07), **DAN email campaign** (backfilled ghl_contact_id 2026-07-13, 5,373 eligible for dispatch), **Partnership Marketing pipeline** (activated 2026-07-31, 131 contacts, dual email+LinkedIn sequences, fully audited and deployed), **Apollo phone enrichment** (repaired 2026-07-14, new polling workflow), voice, reporting, LinkedIn outreach (canonical sender path and suppression guardrails hardened), the **LinkedIn/Instagram via Unipile -> GHL bidirectional conversation provider integration**, and the SimpleTexting SMS campaign stack, currently paused for one-by-one reactivation after n8n dispatcher recovery.

### Company Instagram Page Enrichment and DM Delivery (2026-08-14)

The approved three-message sequences in the three Instagram/FB DM DOCX files remain unchanged. Phase one delivers to verified company Instagram pages through Unipile account `F2UprZ8aQc6Qm9CYYWU6cg`, not employee profiles. The old `LT - Instagram DM Sequence (Unipile)` (`iCnY6ccdHhfJg3sf`) remains unpublished because it used the LinkedIn account and old state model. Facebook Messenger is deferred to native GHL Messenger; public Facebook URLs/Page IDs are reference data, not recipient IDs.

Audience selectors: Brands=`brands_pool`; Dispensaries=`dispensaries_pool`; Partnerships=`partner_candidate_email` OR `partner_candidate_linkedin`. `data/Brands.csv` contains 3,668 rows, with 3,224 rows containing Instagram URL occurrences and 2,799 containing Facebook URL occurrences. `data/Dispensaries.csv` contains 10,200 rows, with 6,875 Instagram and 6,431 Facebook URL occurrences. Relevant columns are `Company non-LinkedIn URL(s)`, `Location non-LinkedIn URL(s)`, and `Contact non-LinkedIn URL(s)`. Partnership source files currently lack reliable Instagram/Facebook URL fields and require separate enrichment.

Existing contact-level Instagram fields remain protected: `Instagram Username` (`8k6vF61VBIysdIXXFQD5`), `Instagram Profile URL` (`beGMXoidqHdYqAQDORWX`), `Instagram Profile Provider ID` (`fYYUrFLABP5l0w7RdK7Y`), `Instagram Chat Attendee ID` (`SQdQw0MNvk8uQbr4yDZU`), and `Instagram Chat ID` (`ab6euY7qo5klhUSe7VWu`). Add separate company-level fields with exact names: `Company Instagram Username`, `Company Instagram Profile URL`, `Company Instagram Profile Provider ID`, `Company Instagram Chat Attendee ID`, `Company Instagram Chat ID`, `Company Facebook Page URL`, `Company Facebook Page ID`, and `Company Facebook Messenger PSID`. Do not repurpose `Apollo Facebook URL`; populate a Facebook PSID only from an eligible GHL Messenger event.

The enrichment workflow matches by Emerald Contact ID, source metadata, exact normalized email, exact normalized phone, then company-plus-contact-name as a review fallback. It extracts/normalizes company and location URLs, resolves Instagram pages through Unipile, rejects personal/ambiguous profiles, updates only new company-level fields, and creates an unresolved/conflict review report. Multiple GHL contacts can map to one company page; Postgres stores all associated IDs and one primary attribution contact. Create a dedicated Postgres company-page identity/state model tracking campaign, page/profile/chat IDs, GHL associations, source tag, message step/status, next due time, message ID/hash, reply/suppression state, failures, and timestamps. Enforce identity uniqueness by campaign/account/profile provider ID and send idempotency by campaign/profile/step; use direct `require('pg')` transactions for writes. All eight new GHL fields are `TEXT`; provider/profile fields are populated only after Unipile validation, and chat attendee/chat ID fields only after a usable Unipile messaging identity is confirmed. The existing `instagram_conversation_map` remains the contact-level inbound bridge and is not the company-page campaign state table.

Any prior reply or suppression from any associated contact stops the company-page sequence. This includes prior social replies and relevant GHL/email/LinkedIn reply evidence; email and LinkedIn campaigns may continue independently when there is no reply, but a social-page reply suppresses the social sequence. Identity/reply-check errors skip the send. Cadence is Message 1 on the first eligible weekday, Messages 2 and 3 two business days apart, with no weekend sends. Lifecycle remains in Postgres and requires no lifecycle tags. Gates: source extraction report; GHL matching and review; create eight company fields; resolve/write validated Instagram identities; create/import state; five-page dry-run samples for Brands and Dispensaries; one controlled live Instagram test per campaign; verify Unipile IDs, GHL mapping, state persistence, and reply suppression; then publish/activate the weekday dispatcher. No live production execution is permitted during validation without explicit approval.
## Original Plan Content (pre-2026-08-11)

> The historical sections below contain old snapshots and completed work narratives. For current blockers, use the resolved runtime update above and `Project Status and Next Steps.md`.

- Social provider integration handoff: [docs/strategy/unipile-ghl-bidirectional-integration.md](./docs/strategy/unipile-ghl-bidirectional-integration.md)
- Reporting implementation handoff: native GHL report `6a67dce4a51a4360c60963a3` plus the read-only Executive Report at `reports/embed/executive/index.html`. The public report host now serves build `2026-08-17-v26-social-reporting-accuracy`.
- Reporting contract: use native GHL for CRM/email/SMS/call facts and custom metrics; use Social Planner for native social analytics; use the Executive Report for Brands-versus-Dispensaries joins, Unipile, Vapi, trigger-link detail, and cross-channel reporting.
- **Outgoing call detail (2026-08-06)**: the Executive Report now has a bottom row-level Vapi table backed by `LT - Report Outgoing Calls Detail` (`VXFHc8IrF9DDEEdj`). The report-host route `/api/report/executive/outgoing-calls` proxies to `/webhook/lt-report-outgoing-calls`; it is fixed to the seven most recent completed `America/Los_Angeles` days, capped at 100 rows per page, and reads `voice_call_attempt` + `voice_call_queue` with latest contact-snapshot enrichment. Aggregate GHL calls remain a separate status/outcome surface.
- Date contract: selected `from`/`to` windows are supported by the Executive Report and campaign summary endpoint. Every selected period must compare with the immediately preceding equal-length period, including absolute and percentage changes. Default weekly interpretation is Monday-Sunday in the reporting timezone.
- Native GHL limitation: the verified `GHL_PIT` provides valid REST access to the location and contacts endpoints, but the official API/SDK exposes no supported Custom Report widget-layout mutation. Authenticated browser access is now available and has been used to save `Last 30 days` and remove the duplicate page-3 outgoing-call widget. Do not use undocumented endpoints.
- **Execution order (2026-07-30)**: deploy and verify the Executive Report; complete native GHL report configuration through an approved authenticated path; verify SimpleTexting live delivery; run controlled Brand/Dispensary Vapi checks; implement the deterministic Jason/Marc no-owner allocator; harden public webhook/secret boundaries; then finish the remaining reporting backlog.
- **Current blockers**: Post-recovery reporting/source tables require controlled restoration. Remaining native GHL widget configuration requires authenticated UI edits because the supported API cannot mutate layouts. Credential-bearing response captures must remain untracked.
- **n8n stale execution recovery (2026-08-05)**: the regular-mode n8n instance accumulated 6,946 `new` executions after the PostgreSQL outage/redeploy, including 1,915 SimpleTexting Step Runner, 1,905 SimpleTexting Phone Backfill, 788 Partnership Reply Poller, 396 Vapi Intake Poller, 386 LinkedIn Reply Backfill, 313 Vapi Dialer, and 261 Campaign Contact Classifier records. Follow `docs/n8n-stale-execution-recovery.md`; pause high-volume schedules, preserve recent webhook executions, remove stale scheduled records through n8n UI/API in batches, then add `N8N_CONCURRENCY=10` and re-enable workflows gradually. Do not delete execution rows directly in PostgreSQL.
- **n8n stale execution recovery completed 2026-08-05**: rebuilt the n8n PostgreSQL pool by restarting n8n, unpublished nine high-volume scheduled workflows, and deleted 6,964 stale `new` trigger executions through the supported execution API. No webhook executions were deleted and the current `new` count is zero. `N8N_CONCURRENCY=10` is staged in `n8n/docker-compose.yml` for the next Coolify redeploy. Re-enable schedules gradually; do not reactivate outbound workflows until controlled verification passes.
- **n8n gradual reactivation and optimization**: SimpleTexting sender schedules remain unpublished. Phone Backfill is active and non-sending; sender reactivation still requires one explicitly approved live provider test or natural traffic verification. Optimize with bounded batches, no-work exits, atomic claims, watermarks, idempotency, and overlap guards. See `docs/n8n-stale-execution-recovery.md` for the exact sequence and stop conditions.
- **Resolved 2026-08-14 — scheduled dialer release-lock error**: The `there is no parameter $1` failure was in the shared scheduled Vapi outbound dialer's n8n/Postgres queue-release path, not a manual dialer and not Twilio. The direct-`pg` migration is published in `b8e9c57a-f81f-49fd-b469-1388320568c5`; thirteen consecutive scheduled executions, including `746845`, completed successfully.
- **Resolved 2026-08-14 — residual voice enqueue path**: A separate active `LT - Voice Queue Enqueue` webhook (`XzcpOBi9YcIhJPck`) still used Postgres v2.6 `queryReplacement` and could emit the same `$1` error. Its insert node was migrated to direct `require('pg')` and published as `42aba803-09b0-4118-a105-9161bebe66e9`; live details confirm the active version matches the draft. The issue was n8n/Postgres persistence, not Twilio.
- **OpenCode optimization (in progress)**: purpose-built agents, stable LiteLLM capability aliases, reusable commands, and LiteLLM-backed default/small models are now configured. LiteLLM health and all eight capability aliases passed harmless request tests. Remaining validation is controlled failure testing for fallback behavior; current permissions and MCP servers remain unchanged except Whitefriar, which is disabled by default.
- **n8n reactivation result**: republished the seven non-SimpleTexting workflows after redeploy and verified matching active versions, HTTP 200 readiness, and zero `new` executions. SimpleTexting Step Runner, Warmup, Pool, and Campaign Sequencer are unpublished; Phone Backfill is active and non-sending. No manual production send was started.
- **Resolved 2026-07-30**: outbound dialer and Call Outcome Ingest crash fixes. Root causes: (1) GHL `Version` header `2023-02-21` rejected by the API (mandate is `2021-07-28`); (2) dialer loop guard read Postgres `RETURNING` columns that n8n's Postgres v2 node never delivers (only `{"success":true}` is visible); (3) empty-queue fetches produced phantom `GET /contacts/`→403 requests; (4) Call Outcome Ingest used invalid `new Date()` in `queryReplacement`. Fixes applied: Version header corrected on both dialer HTTP nodes, loop guard rewritten to read from Code-node item data, empty-queue guard added before GHL lookup, ingest expression fixed. All three workflows published and verified. Queue reset: 1,051 contacts (1,047 failed + 4 cooling_down) → `status='pending'`. End-to-end verification passed for a real GHL contact lookup.
- SimpleTexting provider handoff is live (2026-07-20). The 2026-08-17 safety pass hardened the send webhook, provider router, idempotent boundary, and all three provider callbacks; registered protected callback URLs; and reconciled 41 confirmed sends, 202 terminal provider failures, and 55 quarantined unknown sends without replay. Provider acceptance is not assumed from historical HTTP 409s; it remains unverified until approved live or natural traffic supplies a current provider result.
- Vapi Brand prompt/variable hardening completed 2026-07-25: removed the unresolved `{{company_name}}` opener dependency, added GHL `company_name` propagation through the outbound dialer, and tightened live prompt handling for missing variables, IVR/voicemail detection, one-question turn-taking, and stage directions. Brand assistant and dialer are live/published; callback execution `241581` confirmed successful voicemail outcome processing.
- Reporting and LinkedIn hardening completed 2026-07-31: GA4 `6pCSGzFmrMDFL5Yq` is published on `8f4c63ea-dd33-4c7f-93a5-b3cbb5c8e7fa` with explicit success/empty/partial/failed finalization, transactional health/run writes, stable named-dimension keys, and no watermark advancement on fetch failure. GA4 success execution `276731` and pinned failure execution `276747` passed. Sales `aYT5oHcgmBALzHy5` is published on `4f3e8068-8864-4b4d-9286-ba4d618cc3a8` with ingest-date snapshots, cursor/retry guards, fail-closed writes, and `ghl_opportunities` source health; execution `276626` passed with 7,683 opportunities and 7,683 history rows. LinkedIn sync `ceaKnz6E3onQrZpt` and dispatcher `fXxw5lanZcDmUrst` remain published with bounded/atomic behavior and protected state-upsert headers. State upsert `Old7ZvyVYgFaJgDr` is published with terminal promotion, active-reply preservation, protected `httpHeaderAuth`, and a Community Edition `Config` node. All eight relevant workflows now have exactly one `Config` node and callers read `Config.stateUpsertSecret` instead of embedding the literal in request code. Unauthorized verification returned `403`; malformed authorized verification reached validation without writing state. Remaining security work is migrating other embedded GHL/Unipile API secrets to credentialed HTTP Request nodes or approved runtime configuration.

## Vapi Campaign Rollout

### GHL Tag IDs

| Tag | ID |
|-----|----|
| vapi_campaign_brand | exfU7DXbFF1c314Z1QXQ |
| vapi_campaign_dispensary | FiYEwJdMSIyKZa059wRY |
| vapi_already_called | HhkfhzocuEdOFOxeeHu2 |

### Active 2026-07-14

Both workflows published and running:
- **Intake Poller** (bYk1Ai6MJLyhTsDZ): Active, every 10 min, 30 contacts/cycle, tag rotation across all 4 pools (vapi_campaign_brand, vapi_campaign_dispensary, brands_pool, dispensaries_pool).
- **Outbound Dialer** (r7UjWLndmc6EqEUW): Active, native n8n Schedule Trigger every 2 minutes. Places calls via Vapi using campaign-specific assistants (Alex for brand, Jordan for dispensary). The timezone-aware business-hours guard is authoritative; no external cron is used.
- **Outbound Dialer queue loop**: After releasing a blocked, invalid, or outside-hours contact, the dialer immediately checks the next queue row in the same execution, capped at 25 queue checks. The live workflow is published and verified.

### Remaining Operational Items

- App reinstalled in Live Transparent with canonical SMS-type additional custom providers: LinkedIn `6a58a14ff3023bea3783c152`, Instagram `6a58a1193cdfc36997580a68`.
- Instagram GHL UI outbound reply and direct router smoke test both route to Unipile. Post-merge map repair points Instagram and LinkedIn social chats to canonical contact `XZ4yChllGBdcsVxhFRDe`.
- LinkedIn inbound under provider `6a58a14ff3023bea3783c152` is verified end-to-end; optional next check is a controlled LinkedIn GHL UI outbound reply from conversation `Ze8o3KbsrwuAXQ3KK5ge`.
- Register/confirm Unipile Instagram inbound webhook points to `https://automations.livetransparent.com/webhook/lt-unipile-instagram-new-messages`.
- Move remaining secrets out of workflow Config nodes into credentials or env-backed config.
- Monitor the next real Instagram inbound after GHL duplicate cleanup; map rows are repaired, but avoid further artificial inbound replays unless needed because they create visible conversation messages.
- ~~Update `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) to apply canonical classification tags: `qualified` on regulated-business acceptance and `not qualified` on rejection, removing the opposite tag when reclassifying.~~ **Done 2026-07-30 — published active version `9eae8a33-319a-4c8a-9ee7-2b3b3d5fb45f`.**
- ~~Update Vapi intake so raw pool tags cannot bypass classification; only `qualified` contacts with the required Warm opportunity may enter the Vapi path.~~ **Done 2026-07-30 — published active version `99244f60-3c68-4c08-9bcb-1cf5d8bf20d1`.**
- ~~Update GHL promotion workflow `Move Contact's Opportunity to Sales Outreach New` (`cd29d8e6-5e0f-45f8-ba4f-c30804ad9b49`) so the destination is `Sales Outreach -> Qualified`.~~ **Done 2026-07-30 — GHL version 10 published; both opportunity actions target `Sales Outreach -> Qualified`.**
- ~~Implement the Jason/Marc no-owner allocator at Sales Outreach entry.~~ **Live 2026-07-30 — n8n workflow `LT - Sales Outreach Jason Marc No-Owner Allocator` (`eeksgD0fbGHUqh4r`) runs every 30 minutes, selects open `Sales Outreach -> Qualified` opportunities, filters blank native owners in code, and assigns Jason/Marc by deterministic opportunity-ID hash. It writes only native opportunity ownership; the published GHL alignment workflow handles the contact and custom opportunity owner cascade.**
- Ownership audit result: the allocator assigns only the native opportunity owner, then lets the published GHL `LT - Opportunity Owner Alignment` workflow assign the contact and mirror the custom opportunity `Owner`. The staged n8n owner-sync workflow remains inactive.
- ~~Complete legacy-owner migration for open Sales Outreach opportunities whose custom `Owner` was a former owner or Kevin.~~ **Done 2026-07-30 — authoritative opportunity search returned zero remaining former-owner/Kevin custom-owner records; native ownership cascaded through the published GHL alignment workflow.**
- Verify Vapi dashboard still points all tools and end-of-call webhook to canonical callback URL. This remains a manual dashboard check because it cannot be safely simulated through n8n.
- Run a controlled live Brand and Dispensary call after the 2026-07-25 prompt/variable patch and verify no unresolved placeholders, no disclosure in voicemail, and one-question turn-taking.
- **SimpleTexting next step**: keep Step Runner, Warmup, Pool, and Campaign Sequencer unpublished. Allow active Phone Backfill to maintain phone state. Use one explicitly approved live SMS or natural provider traffic to verify current provider acceptance and callback persistence before publishing any sender schedule.
- SimpleTexting GHL Conversations provider is LIVE: `SimpleTexting SMS` (`6a5b91913953360948dd59f1`) routes GHL outbound replies through the hardened outbound router (`f4VoO1lBWkYRcQai`) → idempotent send → SimpleTexting. Inbound posts to both Slack and GHL Conversations. Provider callbacks are registered with protected secret URLs, and outbound campaign sends mirror into GHL Conversations only after confirmed delivery acceptance.
- Retry blocked GSC ingest workflow.
- Build Meta Ads ingest for spend, clicks, impressions, and cost metrics.
- ~~Investigate Executive Report → Site Traffic → Top Page formatting/aggregation: the displayed page is showing the full email UTM URL instead of the expected normalized top-page label/path.~~ **Fixed locally 2026-07-30 — the Executive Report now strips host, query, fragment, session, and trigger-link parameters; deploy and verify through Coolify remains.**
- Complete the native GHL report configuration through the authenticated GHL UI: add Sales Outreach/Warm stage widgets, DAN/Emerald/Vapi tag widgets, Replied/Soft bounced/Emails by domain widgets, page names, and open/click/response custom metrics.
- ~~**Add campaign-level reporting to the native GHL report and Executive Report.**~~ **Executive Report campaign reporting is live 2026-08-08**: build `2026-08-08-v18-opportunity-attribution` renders All, Email, LinkedIn, SMS, and VAPI filters, separate Vapi campaign rows, drill-downs, comparison view, SMS failure diagnostics, and selected-window campaign opportunity counts. Native GHL campaign widgets remain a separate operational backlog.
  - Email campaigns: `New attribution model - brands`, `New attribution model - dispensaries`, `General outbound`, `Partnership emails`, and any additional active email campaign discovered from release logs, GHL workflow/sequence metadata, or event attribution.
  - LinkedIn campaigns: `New attribution model - brands`, `New attribution model - dispensaries`, and other named LinkedIn outreach campaigns, using Unipile/state activity where GHL-native data is unavailable.
  - SMS campaigns: each named campaign, including `xyz`, `abc`, and any current SimpleTexting campaign identifiers or template registries.
  - Required campaign metrics: sends, delivered/provider success, opens, clicks, replies, bounces, unsubscribes/complaints, calls or DMs where applicable, booked meetings, qualified outcomes, opportunities, and closed-won revenue.
  - Required dimensions: campaign, channel, audience (`Brands`/`Dispensaries` where applicable), source/medium, workflow or sequence, template/message key, sender/owner, and date window. Preserve unknown/unattributed values instead of silently dropping them.
  - Reconcile campaign totals to the corresponding overall channel totals and surface source-coverage gaps, especially historical email events and LinkedIn activity events.
  - **Tag attribution rules:** use queue/enrollment tags as campaign evidence, source-pool tags as audience evidence, and lifecycle/outcome tags only for status or conversion metrics. Do not treat `seq enrolled - dan`, `seq enrolled - emerald`, `simpletext_ongoing`, `simpletext_finished`, `simpletext_stop`, `linkedin_connected`, or `linkedin_dm_sequence_completed` as campaign names by themselves.
    - DAN: `Enrollment Queue - DAN - Brands` and `Enrollment Queue - DAN - Dispensaries` are definitive campaign triggers; `brands_pool` and `dispensaries_pool` are supporting audience/source tags. The `DAN_Release_Log.campaign` and `enrollment_tag` fields are preferred because queue tags may be removed after enrollment.
    - Emerald: the eight `Enrollment Queue - Emerald - {Executives,Marketing,Finance,Retail and Sales} {MSO,SSO}` tags and matching `Seq Emerald - ...` tags identify the campaign bucket. The source tags `cannabis-retail-{mso,sso}-{executive,marketing,finance}-1/2` are fallback routing evidence; generic `emerald` is insufficient. Prefer `Emerald_Campaign_Contacts.bucket`, `email_campaign`, and `Emerald_Release_Log.bucket` when available.
    - SMS: `sms_drip` identifies the eligibility pool, while `simpletext_start`, `simpletext_ongoing`, `simpletext_finished`, `simpletext_stop`, and `simpletext_sms_1` through `simpletext_sms_6` are lifecycle/template tags. Prefer `SimpleTexting_Campaign_State.campaign_key` and `SimpleTexting_Campaign_Event_Log.campaign_key`; `xyz`/`abc` must be registered campaign keys or explicit campaign tags before they are reported as named campaigns.
    - LinkedIn: current tags (`linkedin_connection_requested`, `linkedin_connected`, `linkedin_state_queued`, `linkedin_dm_sequence_completed`, and `stop_linkedin_dms`) are lifecycle/suppression tags, not campaign identifiers. Use `emerging_pool_contacts.source_list` or historical `brands_pool`/`dispensaries_pool` observations as an audience fallback, then add a durable LinkedIn campaign key/tag at state enqueue for future exact attribution.
    - General outbound and Partnership emails: no reliable campaign-specific tag was found in the current runbooks/live workflow definitions. Report them as `unattributed` until a sequence/workflow/tag mapping is registered; do not infer them from generic engagement or completion tags.
- Add remaining spreadsheet-only metrics to the Executive Report: per-campaign rates, trigger-link views/clicks, Unipile LinkedIn campaign metrics, and social impressions/reach/clicks/top-post detail where the source API supports the selected period.
- ~~Publish selected-window metadata and derived email rates from `LT - Report Campaign Channel Summary` (`MvPLbUAN9IIQikxb`).~~ **Done 2026-08-08 — current published version `1cea3b9c-d587-4135-806d-46d301e2c7f4` includes separate campaign rows, selected/prior comparison data, campaign opportunity counts, and SMS delivery diagnostics.**
- ~~Validate campaign email sent counts against DAN/Emerald release logs and `Email_Events`; zero sent with nonzero opened/clicked is a reporting defect, not a valid result.~~ **Checked 2026-07-30 — the selected 2026-07-20 to 2026-07-26 window has no `LT - Email Event Ingest` executions, so its zero engagement counts reflect missing historical event coverage. Later events are ingesting and aggregate correctly; retain this as a source-coverage limitation rather than altering the query.**
- ~~Deploy the selected-period and campaign-channel Executive Report host change through the normal Coolify path, then verify the live build stamp, campaign table, selected-period controls, prior-period comparison, and both historical/current API windows.~~ **Done 2026-08-08**: build `2026-08-08-v18-opportunity-attribution` and live campaign endpoint verified.
- Monitor LinkedIn outbound guardrails, completion tagging, and reply-state sync after the fail-closed patch.
- Monitor the dialer's same-run queue loop and confirm eligible contacts are reached without exceeding the 25-contact safety cap.
~~- Verify one controlled production call using the rotated GHL PIT; manual dialer smoke execution `242609` already succeeded.~~ **Done 2026-07-30 — full audit of all 67 active workflows confirmed old PIT purged. Intake Poller and Dialer Config nodes updated and published.**
- Configure and enforce Vapi callback/server authentication before accepting forged tool or outcome requests.
- Audit and authenticate public Warm intake and SimpleTexting send webhooks whose shared-secret configuration is empty.
- Migrate active n8n Config-node secrets into credentials/protected runtime configuration and rotate exposed values.
- Add provider call ID/idempotency persistence and stale-lock reconciliation to the voice queue.
- Normalize contact owner, opportunity native owner, custom opportunity `Owner`, owner conflict, and canonical SDR identity for reporting.

### Marc Coetzee Sales Rep Onboarding Plan (Planning Only)

The reusable multi-SDR design contract is documented in [docs/strategy/sdr-registry-and-routing-contract.md](./docs/strategy/sdr-registry-and-routing-contract.md). Do not activate a new allocator until the live qualification and Sales Outreach promotion contract is confirmed.

New sales rep:
- Name: Marc Coetzee
- Email: marc@livetransparent.com
- GHL user ID: `sqGx5rp3oAUG610NXyjU`

Required pre-cutover cleanup for any future legacy-owner migration:

- Before enabling any Jason/Marc round-robin, identify any contacts currently owned by former staff using their live GHL user IDs. Do not infer user IDs from display names or historical records.
- Reassign those contacts to Jason Bornillo (`yU85G6kfhtW4vUtx3QE6`) first, with a record-level audit of previous owner, new owner, timestamp, source, and reason.
- Preserve contact tags, custom fields, conversations, notes, tasks, DND/opt-out status, and existing attribution during the owner transfer.
- Inventory opportunities associated with those contacts separately. Do not silently change existing opportunity owners as part of the contact cleanup; apply the documented opportunity ownership and Sales-pipeline handoff rules deliberately.
- Verify the cleanup count before proceeding. No former-staff-owned contact should remain unless it is explicitly excluded and documented.
- This cleanup is separate from the qualification gate. Do not enable a new allocator or make Warm assignments until the Janvi gate and Sales Outreach boundary are implemented.

The 2026-07-30 migration is complete. The initial audit identified 307 open Sales Outreach opportunities with a former owner or Kevin as custom owner; the final authoritative search found zero remaining records. The migration changed native opportunity ownership and allowed the published GHL alignment workflow to cascade contact ownership and the custom opportunity `Owner`; no direct duplicate writer was activated.

Allocator rollout note (2026-07-30): the first controlled run assigned 73 previously unowned Qualified opportunities successfully. A live verification confirmed native opportunity owner, contact owner, and custom opportunity `Owner` agree for Jason and Marc. The remaining unowned Qualified backlog is processed in bounded batches by the active allocator; do not manually assign records while the backlog drains.

Before executing any live changes, audit and map every Jason-specific reference across GHL and n8n:

- Workflow names and descriptions that identify Jason, including `WL - Micro - Email Open Counter + Assignment to Jason` (`42aa5940`).
- Contact owner assignment paths and opportunity owner assignment paths; confirm whether each path uses a GHL user ID, a custom field, a round-robin rule, or a hardcoded name.
- GHL email templates, HTML signatures, sender addresses, reply-from values, and any sequence/template folder naming that is Jason-specific.
- Current live Jason-specific GHL templates identified: `Jason - 01` (`69e0d86b9af59801b580f4b5`), `Jason - 02` (`69e0db27d6a707bbf190d022`), `Jason - 03` (`69e0db9ab02114c1ba3c29d3`), `Jason - 04` (`69e0dc56d6a707c0ac90e074`), `Jason - 05` (`69e0dcad8ffabf47b4d987c5`), and `Jason - 06` (`69e0ddd0b021145bab3c4569`). All require backup and a decision between Marc-specific copies versus shared rep-merge templates.
- The former-owner follow-up template currently contains a stale former-owner signature and must be corrected during the template audit, regardless of whether it becomes an SDR-specific copy.
- SMS template registries and GHL SMS workflow payloads, including preserved legacy keys such as `john_sms1` through `john_sms5`; do not rename keys without mapping review.
- Vapi assistant `firstMessage`, prompt identity, transfer language, metadata, notes, and any campaign-specific sales-rep references.
- GHL automations and micro-workflows that assign contacts or opportunities after opens, clicks, replies, deck downloads, bookings, or other engagement events.
- Previously documented Jason-specific GHL workflow references: `Jason Followup Emails and SMS` (`f6b44e34`, verified v39, 2026-07-30) and `WL - Micro - Email Open Counter + Assignment to Jason` (`42aa5940`, pending re-fetch and verification).

Required routing change:

- Update `WL - Micro - Email Open Counter + Assignment to Jason` so email opens remain an engagement signal only and do not independently assign an SDR or promote a Warm record.
- Apply Jason/Marc ownership resolution only when Janvi-qualified promotion enters `Sales Outreach -> New`.
- Define the exact balancing rule before implementation, preferably deterministic round-robin or an equivalent 50/50 rule that remains stable across retries and does not repeatedly reassign the same contact.
- Verify the promotion automation's contact-owner and opportunity-owner effects separately; changing one must not be assumed to change the other.
- Preserve existing open-count, tagging, notification, and deduplication behavior.
- For `WL - Micro - Email Open Counter + Assignment to Jason`, preserve the open counter, tagging, notification, and engagement thresholds while removing direct owner/opportunity assignment from the open-event path.

Canonical SDR Routing Contract:

- Create or confirm one authoritative assignment decision for every new qualifying contact. Do not let email opens, SMS sends, Vapi calls, LinkedIn replies, bookings, and opportunity creation independently choose an SDR.
- Use a deterministic 50/50 allocator, preferably a transactional round-robin counter or a contact-ID hash with an explicit tie-break rule. Random assignment is not acceptable because retries can change owners and make the split unverifiable.
- Persist the decision on the contact before any outbound message is sent, and treat the assignment as sticky. Retries, webhook replays, sequence steps, and later engagement events must reuse the existing SDR.
- Store both the GHL user ID and the rep identity needed by outbound channels. At minimum verify fields for `sdr_user_id`, `sdr_name`, `sdr_email`, `sdr_phone`, `sdr_signature`, `sdr_vapi_assistant_id`, and `sdr_calendar_id` or an equivalent canonical mapping.
- Define behavior for contacts that already have an owner, are already assigned to Jason, are assigned to another team member, or have conflicting owner/custom-field values. Do not silently overwrite existing non-SDR ownership.
- Precedence rule: former-owner/Kevin contacts are migrated to the approved active owner before round-robin assignment. Existing contacts owned by active staff remain unchanged unless separately approved.
- Define the cutover scope: new contacts only, or a controlled rebalance/backfill of existing Jason-owned contacts. If rebalancing existing contacts is requested, preserve active conversations, booked meetings, opt-outs, and opportunity history.
- Make the assignment idempotent using contact ID plus a routing version/cutover marker. A duplicate event must return the prior assignment rather than consume the next round-robin slot.
- Add a routing audit trail containing contact ID, previous owner, assigned SDR, assignment timestamp, trigger/source, routing version, and idempotency key.
- Ownership rule: the canonical assigned SDR must own the contact and every newly created opportunity for that contact while the opportunity is in pre-sales/outreach stages.
- Sales handoff rule: when the opportunity moves into the `Sales` pipeline (`MThKauqlvnEFuFmAkyWX`), transfer the opportunity owner to Cameron. Do not transfer the contact owner unless separately approved; the contact should remain owned by its assigned SDR for relationship continuity.
- Define the exact Sales-pipeline handoff trigger, including whether it fires on pipeline ID change, opportunity creation directly in Sales, or both. The handoff must be idempotent and must not revert the opportunity to the SDR on later contact updates.
- Cameron's live GHL user ID is confirmed as `03p5GatJBH7i9zjMaIzm`; use the user ID rather than a display name in the Sales-pipeline opportunity handoff.

Assignment Surfaces To Audit And Update:

- `WL - Micro - Email Open Counter + Assignment to Jason` (`42aa5940`): email-open threshold, contact owner action, opportunity owner action, assignment state, retry/replay behavior, and notification recipient.
- `Sales Followup Emails and SMS` (`f6b44e34`): all email/SMS actions, owner fields, sender fields, transfer/notification recipients, and legacy sender identities. **Completed (2026-07-29), re-audited (2026-07-30)** — all 7 Send Email actions confirmed with owner-driven sender fields; the workflow defaults and active-owner fallback were verified; published v39. The 14 SMS follow-ups are not owner-routed. The active SDR routing path remains subject to controlled verification.
- Warm intake workflows for email inbound, email outbound, and SMS: `SmMf8QIfysuxQJbG`, `J4B0n0QeSeOeqAci`, and `5nYzp9DgQUopzWhR`. Confirm they only tag/intake contacts or whether they also assign owners.
- Email enrollment and stop workflows for DAN and Emerald: sender selection, owner persistence, reply/booked stop logic, and any GHL sequence action that assigns or notifies Jason.
- Vapi intake, queue, dialer, callback, and tool paths: `bYk1Ai6MJLyhTsDZ`, `XzcpOBi9YcIhJPck`, `r7UjWLndmc6EqEUW`, and `fx4UvKUWbqJEY3LK`. Carry the canonical SDR identity through queue metadata, Vapi variables, notes, callbacks, Slack alerts, transfers, and bookings.
- SimpleTexting campaign and provider paths: `usxYXSuc4ahw40V3`, `7mSiivR3NhtLIcNz`, `Q3Ivnwe4z2Y3cD7A`, `gwaEpWDpTIwsafi8`, and `f4VoO1lBWkYRcQai`. Confirm campaign template selection, sender identity, conversation mirroring, inbound reply routing, and `externalId`/idempotency keys include the assigned SDR where required.
- LinkedIn/Instagram inbound and outbound provider paths: preserve the assigned SDR on the contact and route replies/notifications to that SDR without changing the shared Unipile transport or conversation-provider IDs.
- Appointment, booking, opportunity, and post-booking workflows: assign the opportunity and appointment owner consistently with the sticky contact SDR, while preserving any separate fulfillment/calendar owner rules.
- Opportunity lifecycle: verify SDR ownership at opportunity creation, retain SDR ownership through pre-sales stages, transfer only the opportunity to Cameron on entry to the Sales pipeline, and preserve the assigned SDR in contact/custom-field/audit metadata.
- Reporting and attribution: include SDR/owner identity in release logs, email events, SMS events, Vapi attempts, opportunities, appointments, and dashboards so the 50/50 result can be measured independently of sender address.

### Revised Qualification and SDR Work Queue Model

- Warm is the unassigned intake and regulated-business classification layer. Contacts receive `qualified` when their business is related to a regulated vertical, or `not qualified` when it is not.
- `qualified` is the regulated-business classification gate and routes the opportunity into `Sales Outreach -> Qualified`.
- SDR allocation occurs at the Sales Outreach promotion boundary, not during Warm intake, email opens, SMS sends, Vapi queueing, or other channel micro-automations.
- When a contact enters Sales Outreach, resolve ownership in this order:
  1. If exactly one of the contact or opportunity has an owner, align the other record to that owner.
  2. If both have the same owner, preserve the assignment.
  3. If both have different owners, flag an ownership conflict for review and do not overwrite automatically.
  4. If neither has an owner, assign Jason or Marc with the deterministic 50/50 allocator.
- Every Sales Outreach assignment must keep contact `assignedTo`, opportunity native `assignedTo`, and custom opportunity `Owner` aligned through the canonical SDR mapping.
- SDRs work from Sales Outreach. Warm contacts are not part of the normal SDR work queue.
- Vapi remains in Warm and must not call contacts tagged `not qualified` or contacts that have bypassed the canonical classification result.
- The existing GHL promotion workflow should use the canonical `qualified` result to route the opportunity to `Sales Outreach -> Qualified`, while `not qualified` blocks promotion.
- A Vapi warm transfer is an exception path: if an SDR answers the shared transfer number, the SDR manually claims the contact and opportunity and promotes the record into `Sales Outreach -> New`.
- Vapi warm transfer uses the shared SDR number through the Vapi `transferCall` tool; it does not select Jason or Marc by phone number.
- Vapi booking remains separate from transfer and uses Cameron's `Regulated Ads On Social/Search` calendar (`SrtXcFVyea7pFl3nTiIK`).
- The authoritative classification contract is now the `qualified` / `not qualified` tag pair. The live classifier currently needs a write-path patch to apply both outcomes; its campaign tags remain downstream campaign labels.

Rep-Specific Message And Channel Configuration:

- Email: decide whether to create SDR-specific copies of the six follow-up templates or convert them to shared templates driven by SDR merge fields. Update subject/preheader/body signatures, sender/from/reply-to, meeting links, phone numbers, template names/folders, and any GHL sequence references. Correct the stale former-owner signature in Template 04 before reuse.
- Email: ensure a sequence step cannot send Jason copy from a Marc-owned contact or vice versa. Add a pre-send identity check and fail closed when the SDR mapping is missing or invalid.
- SMS: add SDR-specific message variants or a rep-aware template registry. Preserve existing legacy compatibility keys only where live GHL automations require them, and define new keys/mappings rather than changing keys without a migration map.
- SMS: make the selected message, sender label, conversation mirror, reply notification, and idempotency/external ID use the assigned SDR. Confirm STOP, DND, and reply suppression remain global and are not weakened by routing branches.
- Vapi: document the mapping from SDR to assistant identity, first message, system-prompt name, transfer target, calendar, meeting link, phone number, callback metadata, GHL note signature, and Slack notification destination. Do not rely on a generic campaign assistant ID if the spoken rep identity must vary.
- Vapi: pass the SDR identity in `assistantOverrides.variableValues` and metadata, guard against missing/unresolved placeholders, and ensure the callback uses the same owner for notes, outcomes, booking, and follow-up.
- Vapi: keep warm transfer and booking separate. The Vapi `transferCall` tool uses the shared SDR number; the booking tools use Cameron's Regulated Ads calendar. Vapi should refer to the receiving SDR team/Sales Lead without naming Cameron for transfers.
- Vapi: completed 2026-07-25. Updated live transfer tool `86d380a3-34d2-41f8-96a0-acf5f0124ccb` and all four assistants to neutral Sales Lead wording. Preserved compatibility function name `ok_transfer_to_jason` and shared destination `+15622474600`.
- Manual operator sends: update the SimpleTexting/GHL manual-send contract so an operator can send as the assigned SDR without allowing an arbitrary sender override that breaks ownership or auditability.

Equal-Split Validation And Monitoring:

- Build a controlled test matrix covering new contact, email open threshold, SMS send, SMS reply, Vapi call, Vapi callback, inbound email reply, LinkedIn/Instagram reply, deck download, booked appointment, opportunity creation, duplicate webhook, and replayed webhook.
- For every test, verify the same SDR remains on the contact, opportunity, appointment/follow-up task, outbound sender, signature, Vapi variables, CRM note, notification, and report record.
- Add qualification-gate tests for AI-qualified cannabis, AI-rejected/non-cannabis, AI-pending/unverified, duplicate assessment, and Vapi warm-transfer claim.
- Add Sales Outreach ownership tests for contact-only owner, opportunity-only owner, matching owners, conflicting owners, and both records unassigned.
- Include an opportunity lifecycle test: create an opportunity from a Jason-owned contact and a Marc-owned contact, verify the opportunity initially matches the contact owner, move each into the Sales pipeline, verify only the opportunity owner changes to Cameron, and confirm subsequent contact updates do not undo the handoff.
- Verify at least 20 fresh test contacts produce a 10/10 Jason/Marc distribution, or the documented deterministic equivalent, without duplicate assignment on retries.
- Add monitoring for assignment counts, unassigned contacts, invalid SDR mappings, reassignment events, sender/owner mismatches, and failed Vapi/email/SMS identity resolution.
- Add a rollback plan for routing rules, templates, sender mappings, and ownership fields. Backups must be taken before changing GHL workflows or email template HTML.

Implementation order after plan approval:

1. Resolve former-owner and Kevin live GHL user IDs and inventory all contacts and associated opportunities they currently own.
2. Back up the affected contact ownership records and transfer former-owner/Kevin contacts to the approved active owner; verify the complete migration before continuing.
3. Confirm Marc's GHL user record, permissions, email identity, calendar/meeting routing, and any required Vapi or sending-account access.
4. Fetch current live GHL workflow definitions and all referenced n8n workflow versions before editing.
5. Back up every affected GHL email template and record current sender/signature values.
6. Identify Janvi's authoritative AI assessment field/tag and implement the AI-qualified-cannabis -> Sales Outreach New gate. Apply the canonical ownership alignment/50/50 fallback at that boundary, then update Marc-specific copies/templates and sender identity.
7. Run the controlled routing and channel test matrix before enabling production traffic.
8. Publish changed workflows and verify contact owner, opportunity owner, Sales-pipeline Cameron handoff, sender, signature, SMS, and Vapi behavior with controlled test records.
9. Verify no stale former-owner-branded references remain in active production paths, while preserving intentional legacy compatibility keys and historical reporting identifiers.
10. Monitor the first production assignment batch and confirm the measured Jason/Marc distribution, sticky ownership, and zero sender/owner mismatches.

### Completed

- **2026-07-30**: Repaired outbound dialer and Call Outcome Ingest after prolonged outage. Fixed GHL `Version` header (`2023-02-21`→`2021-07-28`), rewrote loop guard to read from Code-node items (Postgres `RETURNING` invisible to n8n Postgres v2), added empty-queue guard before GHL lookup, and removed invalid `new Date()` from ingest `queryReplacement`. Reset 1,051 contacts to pending. Verified end-to-end GHL lookup succeeds. All three workflows published.

- **2026-07-25**: Gap audit hardened the live voice path: silent human answers no longer receive `qualified_booked`/`vapi_qualified`; the dialer fails closed on GHL `401/403`, uses 9am-5pm CT global hours, and the intake poller rejects unknown campaign tags while cleaning the actual source tag.
- **2026-07-25**: Reconnected the six-hour Schedule Trigger paths for `LT - Report Config Sync` (`aomO3Z4AXJIgEvvN`) and `LT - Report Publish Refresh` (`3gXztCnBEN6sGINb`). Both were published and manual executions `242576` and `242577` succeeded.
- **2026-07-25**: Unpublished superseded Apollo Sheet First webhook `WmKAhG7mIaXonNsh` after confirming zero executions; canonical polling `JH8ShfpglWmLMZ3l` remains active.

- **2026-07-25**: Neutralized live Vapi transfer and voicemail language across the transfer tool and assistants. Human-facing copy no longer names individual owners; the compatibility function name and shared destination remain unchanged.
- **2026-07-25**: Disabled the hardcoded Kevin follow-up task in live RB2B workflow `3kjsIUeoEQFx26cC`. Warm intake now persists the contact/lead and returns without creating an SDR task; the legacy task node remains disconnected for future owner-resolved Sales Outreach use.

- **2026-07-24**: Fixed SimpleTexting campaign delivery. `LT - SMS Idempotent Send` now sends multi-segment messages with `AUTO`, records provider errors without crashing, and reclaims failed claims. `LT - SimpleTexting SMS Send (Webhook, Staged)` now gates GHL mirroring on a real provider message ID. Published both workflows and passed safe simulation executions `241272` and `241275`. Live provider confirmation is explicitly queued for the next dispatcher run.
- **2026-07-26**: Refreshed the live SimpleTexting template registry in `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`). Updated `sms_1`, `sms_3`, and `sms_5` with clearer copy and selective `https://livetransparent.com/` references; preserved the other templates and required legacy payload aliases. Republished and verified the workflow's draft and active versions match.

- **2026-07-25**: Audited Vapi callback execution `241579` and its successful end-of-call follow-up `241581`. Fixed the Brand assistant opener and system prompt, added `company_name` extraction/propagation in the outbound dialer, and published/verified dialer version `b3c80814-d7f0-442b-b5d2-f350377a0f2c` as active.
- **2026-07-25**: Recovered n8n from 745 orphaned queued `new` executions that were producing “Starting soon” records and competing recovery messages. Preserved legitimate `waiting` executions, republished the Vapi dialer, and verified the native trigger and manual execution path.
- **2026-07-25**: Updated `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`r7UjWLndmc6EqEUW`) to continue within the same execution after blocked/invalid/outside-hours contacts are released. Added a 25-contact loop cap, published the workflow, and verified it reaches different queue contacts.

- **2026-07-20**: SimpleTexting GHL Conversations bidirectional provider is LIVE. Separate `LiveTransparent SimpleTexting SMS` GHL app with provider `SimpleTexting SMS` (`6a5b91913953360948dd59f1`). Built `LT - SimpleTexting Provider Outbound Router` (`f4VoO1lBWkYRcQai`) at `/webhook/lt-simpletexting-provider-outbound` — validates provider, E.164-normalizes phone, routes through idempotent send to SimpleTexting. Patched `LT - SimpleTexting Inbound Reply (Webhook)` (`i0pROHpFtN4LYR0Q`) to post inbound messages to GHL Conversations under `SimpleTexting SMS` with `type: "Custom"` + `conversationProviderId` (Slack alert preserved). Patched `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`) to mirror outbound campaign sends into GHL Conversations. Created `simpletexting_conversation_map` table in Postgres. First end-to-end test passed: GHL → outbound router → idempotent send → SimpleTexting (201, message `6a5e46218ebb0860da623b0f`). Remaining: full E.164 normalization across delivery/unsubscribe workflows.
- **2026-07-16**: Verified the GHL Custom Conversation Provider bridge for Instagram and LinkedIn via Unipile using canonical SMS-type custom providers. Inbound uses `type: "Custom"` + `conversationProviderId` + `altId` with no dummy phone/email fields. `LT - Instagram Unipile New Messages` and `LT - LinkedIn Unipile New Messages` are active and published; LinkedIn replay verified `TYPE_CUSTOM_PROVIDER_SMS` on contact `XZ4yChllGBdcsVxhFRDe`, conversation `Ze8o3KbsrwuAXQ3KK5ge`. GHL duplicate cleanup consolidated Edmundo Cadorniga to `XZ4yChllGBdcsVxhFRDe`; Instagram map row `1` and LinkedIn map row `2` were repointed there. Direct outbound router checks passed for Instagram and LinkedIn. Full handoff in `docs/strategy/unipile-ghl-bidirectional-integration.md`.
- **2026-07-16**: Cleaned up duplicate LinkedIn sender paths. Traced malformed LinkedIn screenshot DMs to misconfigured `LT - Instagram DM Sequence (Unipile)` (`iCnY6ccdHhfJg3sf`), which used the LinkedIn Unipile account ID and `instagram_dm_state`; unpublished it. Also unpublished redundant `LT - LinkedIn Follower DM Sequence (Unipile)` (`pq7XVajNFnnwMUTr`). Production LinkedIn outreach is now dispatcher → acceptance/state sync → canonical 4-message DM sequence only.
- **2026-07-15**: Built and published automated LinkedIn DM suppression workflow (`LT - LinkedIn DM Suppression from GHL Tag`, IPN8jnR3XSurX0o1). GHL tag `stop_linkedin_dms` triggers a GHL automation → POSTs to `/webhook/lt-linkedin-suppress-dms` → resolves LinkedIn profile via Unipile, tags `linkedin_dm_sequence_completed`, upserts `linkedin_connection_state` to terminal for both real contact and synthetic `linkedin:follower:{providerId}`. Full audit confirmed all 3 send paths (DM Sequence, Follower DM, Dispatcher) correctly block suppressed contacts. Fixed dispatcher Feeder gap: added `linkedin_dm_sequence_completed` to blocking tag list.
- **2026-07-15**: Unicode/mojibake encoding fix expanded across all audited Unipile message sender nodes: LinkedIn DM Sequence (`Sync Connected from Unipile`, `Send DM Sequence Messages`), LinkedIn Follower DM, LinkedIn Dispatcher invites, and Instagram DM Sequence. Templates are pre-sanitized at runtime and final outbound text is sanitized immediately before Unipile API calls. Handles smart punctuation plus already-garbled forms like `canâ€™t` / `canΓÇÖt`. Created the local operator helper `local-scripts/suppress_linkedin_dms.py` for one-command DM suppression.
- **2026-07-14**: Vapi voice system activated. Published Intake Poller + Outbound Dialer. Fixed Trigger Apollo Enrichment auth and Remove Tag - Enriching URL. Added pagination, 30-contact cap, brands_pool/dispensaries_pool tag search, and tag rotation. Added state-to-timezone inference for both poller and dialer. Historical dialer cron was shifted to `*/2 13-22` UTC for 9am ET start; the current implementation uses a native two-minute Schedule Trigger and the timezone-aware business-hours guard remains authoritative.
- **2026-07-14**: Apollo phone enrichment repaired. Created and published LT - Apollo Phone Enrichment Polling (JH8ShfpglWmLMZ3l, every 30 min). Replaces dead webhook-based pipeline. Syncs profile data immediately, requests phone numbers via async callback to V4 handler.
- **2026-07-13**: Backfilled 13,705 ghl_contact_id values into emerging_pool_contacts from GHL export CSVs (email + phone + name/company match). DAN dispatcher now has 5,373 eligible contacts.

- **2026-07-20 - Voice Assistant Optimization (all 3 outbound assistants + dialer)**:
  - **Jordan (Dispensary, 056f2e50)**: 8 system prompt fixes + 2 config fixes from live call audit. Removed compliance disclosure from firstMessage (voicemail fix). Fixed {{contact_name}}->{{first_name}} (n8n passes first_name not contact_name). Removed unmet {{market}} variable. Changed "with"->"from" Transparent eCom (Nico TTS inserted "a"). Discovery questions restructured to one-at-a-time with numbered Q1-Q4 + WAIT instructions. Added [IVR vs Voicemail Detection] disambiguation section. Tightened "um/uh" to once per call max. Added [Pronunciation] rules: "Point of Sale" not "POS", "from" not "with". Expanded [No Stage Directions] to ban throat-clearing/coughing/sighing. [Turn-Taking] strengthened to CRITICAL with self-check. Transcriber smartFormat enabled. Model tested Llama 3.3 70B then reverted to Claude 3 Haiku (system prompt preserved through model swap).
  - **Alex (Brand, 1d7c5d42)**: Same discovery questions, IVR/voicemail disambiguation, turn-taking, stage directions, and {{contact_name}}->{{first_name}} fixes. Brand-specific questions preserved.
  - **Savannah (V1 Outbound, 3f9bbfd2)**: Same IVR/voicemail disambiguation, stage directions, and {{contact_name}}->{{first_name}} fixes. First message already clean.
   - **Outbound Dialer (r7UjWLndmc6EqEUW)**: Stuck contact AX3wfQNpRwm6DG0HgUE2 (deleted from GHL, 2 entries in voice_call_queue) blocked every run since 18:38 UTC. HTTP - Get GHL Contact had neverError: false - 400 crashed run before lock release. Same contact re-picked every 2 min. Fix: neverError: true on lookup node; onError: continueRegularOutput on GHL - Create Call Note. Calls resumed by 18:50 UTC. Intake poller unaffected throughout.

- **2026-07-23 - Vapi and n8n production hardening**:
  - Standardized documentation on n8n `2.33.3` and native Schedule Triggers.
  - Kept the callback-to-dequeue path removed and `LT - Voice Dequeue Next` unpublished.
  - Added callback timer deduplication plus 30-minute static-state pruning.
  - Added queue enqueue authentication with `X-LT-Voice-Queue-Secret` and `VOICE_QUEUE_ENQUEUE_SECRET`.
  - Added Apollo asynchronous phone-request failure telemetry.
  - Reconnected timeout-reaper Slack summaries and removed the stale outcome-webhook response option.
  - Verified changed workflows are published and smoke-tested authenticated and unauthenticated enqueue behavior.

- **2026-07-31 — Partnership Marketing pipeline activated and fully audited**: 131 content partnership contacts imported into GHL (98 email + 33 LinkedIn-only) from two CSV lists, deduplicated/cleaned by `scripts/partnerships/clean_partnership_data.py`. Built 7 n8n workflows: Email Dispatcher (`Xshck23cKo1yXL9D`, 60/day 11am ET), LinkedIn Dispatcher (`crKIsaL5k3YBfqDZ`, 30/day 3pm CT), LinkedIn DM Sequence (`nspggypNF245xzeL`), Reply Handler (`mRDw57IHtnQe4wOo`, webhook), Reply Poller (`0SQ7tTk03okegp9V`, every 5 min), Bulk Import (`zmrYrUjVcyXaS7PJ`), and LinkedIn URL Update (`ew6uQQnAjgCbjeGn`). Created GHL Partnership Pipeline (`tQkFYrHjALgoLz6oq0uz`) with 4 stages. Created 4 GHL email templates in folder `6a6b768aa43d24a7ce1514f1` with HTML content via PATCH API. Patched 3 existing LinkedIn workflows (Acceptance Checker `3ttEvr5NMcQCS4Hp`, Reply Backfill `QfJ2EZcc7lZwNgxj`, Unipile New Messages `7o5EBdvwAuIaWW7k`) to also query `partnership_linkedin_connection_state`. All infrastructure isolated from DAN/Emerald pipelines (separate Postgres tables, separate state tracking).

- **2026-08-27 — August partnership cohort enrolled**: Reconciled 431 source rows / 429 unique emails against live GHL. Created 404 new contacts and enrolled 427 actionable contacts with both `partner_candidate_email` and `partner_candidate_linkedin`; added `august_26_partnership_contact` to all 404 new contacts. Added three missing LinkedIn URLs to existing contacts. Skipped four rows across two shared-email groups for manual resolution. Applied no Vapi selector tags. No manual outbound execution was performed; active scheduled dispatchers will process the cohort. Details: `docs/sessions/2026-08-27-august-partnership-contact-enrollment.md`.
- **2026-07-31 — Partnership reporting integration**: Campaign Channel Summary (`MvPLbUAN9IIQikxb`) SQL updated with `partnership_release_log` UNION ALL in `email_sent` CTE (published version `6641aa9a`). Postgres tables `partnership_release_log` and `partnership_linkedin_connection_state` bootstrapped via `postgres/partnership-bootstrap.sql`. Executive Report frontend deployed as build `2026-07-31-v10-partnership` to reports.livetransparent.com with updated footer note. Full audit completed: 7 partnership workflows confirmed published/active, 3 patched LinkedIn workflows verified with correct queries/routing, all 131 GHL contacts assigned to Janvi, email templates confirmed, pipeline confirmed, Campaign Channel Summary confirmed returning "Partnership emails" row, and the Executive Summary API includes partnership release/state data. Reply Poller version `04cf007e-0ed1-41c7-abf5-4d1174b4bc9f` now uses POST conversation lookup and fails closed; manual execution `277923` passed. Remaining: GHL Custom Report integration (browser-only), provider-side SimpleTexting HTTP 409, and 14 excluded contacts awaiting corrected company names.
- **2026-07-31 — Partnership state and dry-run remediation**: Replaced partnership candidate reads with supported paginated `GET /contacts/` and explicit failure handling. Added LinkedIn `Seed Partnership State`, which populated 127 `ready` rows from GHL LinkedIn-tagged contacts. Current live versions are Email Dispatcher `1b41ce9c-8a89-4e2f-b45c-81bce8bc3484`, LinkedIn Dispatcher `ef3f9aee-88c1-4d02-a40e-b74e8694b6b9`, LinkedIn DM Sequence `798b1c75-cf15-4e4e-9cf4-e3c9fd7b9d7c`, and Reply Poller `42fbe7fc-fffe-4784-a4a4-4187a385bd5b`; relevant outbound configs remain `defaultDryRun=true`. Dispatcher dry run `278203` planned 30 requests with 0 sent; DM dry run `278342` completed with no sends. Direct GHL PIT verification returned HTTP 200 for location and contacts endpoints. Remaining: explicit live launch approval, native GHL report-builder access/configuration, provider-side SimpleTexting HTTP 409, credential migration, and 14 excluded partnership contacts awaiting corrected company names.
- **2026-07-31 — Partnership live-state hardening**: Audited all 7 live workflows and corrected the three outbound schedules from hourly interval definitions to explicit weekday cron schedules: email `0 11 * * 1-5` America/New_York, LinkedIn `0 15 * * 1-5` America/Chicago, and LinkedIn DM `0 12 * * 1-5` America/Chicago. Fixed the DM sequence terminal completion query and the shared LinkedIn Acceptance Checker state-upsert header. Published versions are Email `ca59164e-b3d8-4e84-b8af-c843832d043a`, LinkedIn `31a83f80-6256-4a50-a690-aa666102c1d4`, DM `f37a01e2-5ce6-4ce7-9327-21f3510d99bc`, and Acceptance Checker `0d85599c-fc9a-4391-83b5-725da2d7f451`; smoke executions `281269`, `281268`, and `281270` succeeded. Outbound remains dry-run pending explicit authorization.
- **2026-07-31 — Partnership outbound activated**: After explicit user approval, set Email Dispatcher, LinkedIn Dispatcher, and LinkedIn DM Sequence `defaultDryRun=false`. Published and verified active versions: Email `6b7490a9-05d8-44e1-8f94-3c4427a7f969`, LinkedIn `29089175-1b37-4271-8b03-d4722b809692`, and DM `3bd0b759-4740-4e67-85ef-9540bf31c08e`. Scheduled production sending is now enabled; no unscheduled manual live execution was run.
- **2026-08-12 — Partnership LinkedIn reply recovery**: Campaign Channels undercounted replies because malformed form-encoded Unipile payloads could lose critical sender/message fields. Recovered verified David Schachter and Gretchen Gailey replies with original provider message IDs/timestamps, inserted them idempotently into `linkedin_activity_events`, and raised Partnership LinkedIn replies from 1 to 3. Published `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`) version `f96dafba-9818-4aab-8656-c2e4e2ab8480` with malformed form-payload field recovery.
- **2026-08-19 — LinkedIn send-path double-escape corruption fixed**: An 08-11 MCP mutation (`3b70854e`) double-escaped regex literals in Code-node `jsCode`. Two distinct failures resulted: (1) the Dispatcher crashed at parse time (`SyntaxError` on `identifier()` `\\/`) so sent no invites 08-11→08-18; (2) after the 08-18 REST PUT fixed that crash, `sanitize()` matched literal `u`/`C`/`D`+digits and `{first_name}` was left unreplaced, so garbled invites went out only 08-18 00:15→08-19 04:45 (60/day cap). Fixed with `scripts/linkedin/fix_linkedin_sanitize_double_escape.py`; republished Dispatcher (`0a349cdb`) and DM Sequence (`db7dde63`); full 164-workflow scan clean. Full narrative: `docs/sessions/2026-08-19-linkedin-double-escape-fix.md`.
````

## File: AGENTS.md
````markdown
# LiveTransparent Agent Notes

## ⚠️ CURRENT 2026-09-29 Executive Report V1 GHL Call Source Handoff

- The V1 SDR call section now displays an exact GHL native-report snapshot for `2026-09-20`–`2026-09-26` only: Marc 1,006 (802 answered, 105 busy, 59 no-answer, 40 failed); Jason 350 (285 answered, 19 busy, 35 no-answer, 11 failed). The native widgets use `dateAdded`, `direction=outbound`, `userId`, and report timezone `Asia/Manila`; the API snapshot is clearly labeled and must not be treated as a refreshed or historical series.
- The V1-only frontend change is deployed at `/embed/executive-v1/`; the legacy `/embed/executive/` report was not changed. V1 Facts API `oxYDg6XnRBKhl1Xd` serves the dated snapshot for that exact window (version `9a17c3c2-45d2-477e-9c01-3bea0a537ae3`).
- **2026-09-29 source investigation update:** the official `/conversations/messages/export` API is documented and PIT-readable for historical date windows, but its exact-week rows/statuses do not match native widget totals. The authenticated GHL Call Reporting UI's private `POST backend.leadconnectorhq.com/reporting/calls/get-all-phone-calls-new` did match all outbound per-user/status counts for that week (1,377 total rows including 21 inbound; 1,356 outbound). Calling the same private route with the PIT returned HTTP 401. Do not automate this private route; seek documented GHL API access or supported exports. Keep the V1 exact-week snapshot and do not publish unverified export metrics.
- Published active workflow `LT - GHL Outbound Call Event Ledger (Webhook)` (`SA5SF1cZQcVf3IyB`, version `15b2944f-5b71-40fe-b97a-d87718cd6cdb`, 5 nodes) verifies the official GHL `OutboundMessage` signature and idempotently stores outbound CALL events at `/webhook/lt-ghl-outbound-message-call`. Negative-signature tests returned HTTP 401 `invalid_signature`; executions `1062819` and `1062820` did not run the database write node. This proves rejection-path behavior only, not valid-signature acceptance or event delivery.
- **Not wired yet:** GHL Marketplace app `Transparent eCom Social Inbox` must subscribe to `OutboundMessage` and point to `https://automations.livetransparent.com/webhook/lt-ghl-outbound-message-call`. Subscription settings are in Marketplace app configuration, not available through the API; Marketplace developer login was unavailable in the session. App already has `conversations/message.readonly` scope. No live call was placed and no subscription or CRM/report data was mutated for testing.
- GHL PIT can read supported Conversations APIs but receives HTTP 401 from the private report-widget route. The paginated Conversations backfill is still incomplete and must be reconciled before use for arbitrary ranges. Audit source precedence so polling cannot downgrade webhook event facts.
- **Next session:** follow the latest export investigation addendum in `docs/sessions/2026-09-29-executive-report-v1-ghl-call-source-closeout.md`: ask GHL for supported API access to Call Reporting or obtain report exports spanning selected/prior windows, then validate parity and status semantics. Marketplace subscription is optional and forward-only; do not enable it as a historical-data solution. No outbound call test or production data correction without explicit approval.

## ✅ CURRENT 2026-09-29 LinkedIn Identity and Sales Navigator Handoff

- Alexis Mora's authoritative GHL contact is `RGjMxzMqOR2L14ao8qmg` (`firstName=Alexis`, A.MORA Marketing, LinkedIn `alexistaylormora`). No authoritative source for the historical `Angel` greeting was found.
- Personal LinkedIn dispatcher `fXxw5lanZcDmUrst` and DM sequence `d0tEtijajisIsYcs` now require a non-empty provider first name and use it for outbound copy. Partnership/company paths remain GHL-based.
- Outbound GHL mirrors use `/conversations/messages`; inbound LinkedIn bridge posts use `/conversations/messages/inbound`. Published versions are dispatcher `ca663633-143f-4312-9cc3-d0a4ac262661`, personal DM `96f7cf60-97c2-4f54-ba13-20ebf9d49ef1`, partnership dispatcher `44c4ed5f-d5e3-4c75-94f0-1ac21cd7355e`, and partnership DM `9c04b07a-812d-4755-850d-125cadec8c7a`; all were REST-verified with matching draft/active versions.
- Official Unipile docs state that Sales Navigator is enabled in Hosted Auth with `products: ["classic", "sales_navigator"]`; `ACw...` identifies Sales Navigator provider users, `acc_...` identifies v2 Unipile accounts, and `SALES_NAVIGATOR_PRIMARY` starts new Sales Navigator chats. The current legacy `/api/v1` account has not been migrated or verified for that inbox.
- No live LinkedIn sends, account registration, or historical backfill occurred. Preserve the existing Classic connection until a new Sales Navigator-capable account is read-only verified. Cameron must authenticate directly in Unipile; never request/store `li_at`, `li_a`, cookies, API keys, or session secrets in repository artifacts.
- Next: provision/verify v2 Sales Navigator access, add durable personal/hiring exclusions, then generate a deduplicated historical candidate report limited to canonical DM-sequence messages, connection requests, and connection approvals. Detailed handoff: `docs/sessions/2026-09-29-linkedin-sales-navigator-and-identity-eos-closeout.md`.

## ✅ CURRENT 2026-09-29 SimpleTexting Follow-up SMS Sender Personalization

- `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`) is active/published at `b69a183e-273a-43f9-b06d-b2bd1575543b` (`versionId == activeVersionId`; 7 nodes).
- New `Resolve Sender + SMS Templates` node reads GHL webhook `owner` first, then assignee name, then workflow `user`; recognized owner names Marc/Jason are used, otherwise Jason is the fallback. Owner wins if the owner and workflow user differ.
- Legacy `john_sms1`–`john_sms5` templates are dynamically rendered with that resolved sender name; these remain text-only (`AUTO`), without MMS attachments.
- The effective live business-hours gate is weekdays 10:00–17:00 `America/Los_Angeles`. This overrides the stale Eastern-time Config value for this sender.
- Dry-run manual executions `1062414` and `1062422` passed; one rendered Marc for a Marc owner despite a Jason workflow user, and one rendered Jason for a Jason owner despite a Marc user. No provider send was performed. Prior real invocation `1062395` returned `outside_business_hours` under the old Eastern gate and did not reach SimpleTexting.
- No test executions remain `new`, `running`, or `waiting`. The workflow has no automatic replay guarantee for past business-hours rejections.
- **Next:** observe a natural GHL follow-up invocation during Pacific business hours; confirm SimpleTexting provider message ID and delivery callback before claiming delivery. A controlled send still requires explicit approval.

## ✅ CURRENT 2026-09-26 Executive Report QA and V1 Meeting Window Repair

- `ghl_opp_owner_coverage` remains `attention` because the latest QA probe found 4,614 assigned/fallback owners out of 11,569 opportunities (39.9%), below the intentional 50% threshold. The probe succeeded; the data coverage is below threshold.
- V1 meeting details use appointment `start_at` in `America/Los_Angeles`, meaning scheduled meeting time, not booking/creation time. The frontend sent `range=7d`, but the API previously ignored it and defaulted to 30 days.
- `LT - Executive Report V1 Facts API` (`oxYDg6XnRBKhl1Xd`) now handles `range=7d|30d|90d`; active/published version `677e728d-8f33-4e78-a406-3a0dca56b19e`. A 7-day endpoint check returned `2026-09-18` through `2026-09-24` with 3 rows.
- Executive report API proxy caching is now 30 minutes for Summary, Campaign Channels, and V1 Facts. Cache keys include only the selected range/from/to values, so retry parameters do not create duplicate cold queries. The V1 Facts endpoint is now cached and uses nginx cache locking/stale-on-upstream-error behavior.
- **Inbound Priority router:** `LT - Inbound Intent Priority Router` (`URpjcm2k5isHUyls`) is active/published at `3a3a6ab2-79a3-4fcc-822f-52677b6ae38c` with `versionId == activeVersionId`. It targets `Sales Outreach` (`dhdlf3O4tymxFtHk4aqq`) → `Priority` (`be636da7-3c15-48ab-b589-c75bcd6f9955`) and passed mocked pin-data branch tests only. Its execute-workflow trigger remains `triggerCount=0` by design; it is now called by the persisted LinkedIn, Instagram, and SMS inbound branches below. No live CRM mutation smoke test has been run.
- **LinkedIn Priority source integration:** workflow `7o5EBdvwAuIaWW7k` is active/published at `dd98c27b-0fca-491c-bac1-3ff38b1b147b`. Main and partnership inbound branches route only after conversation-state persistence, using resolved `ghl_contact_id`, stable Unipile `message_id`, normalized `timestamp`, and inbound sender/event payload. The router now fetches the live GHL contact owner before any create, so owner resolution is fail-closed.
- **Instagram/SMS Priority source integration:** Instagram `pISlgYUsyJIrLuJd` is active/published at `e09111d7-2c63-4925-b335-741c57f5ab5d`; SMS `i0pROHpFtN4LYR0Q` is active/published at `599995a9-72ce-467d-9892-c7ddf496c3fa`. Both route only after their existing durable claim/contact-resolution/state paths. SMS STOP/unsubscribe events are explicitly excluded from Priority routing.
- **Call/email Priority source integration:** call workflow `PUCfTZBANSPcgS0c` is active/published at `f9388b9a-ab70-45b2-bc77-4f5c2efef829`; its parallel Priority branch requires inbound direction, resolved contact, original timestamp, and stable call ID/composite, and distinguishes voicemail. DAN/Emerald email poller `hxiiYCpEfMuoSt5H` is active/published at `6e60f832-f175-41a8-a4b7-193f286bef18`; it re-fetches actual messages and rejects automated mail before routing. Partnership handler `mRDw57IHtnQe4wOo` is active/published at `42da3b2e-4b6a-4f2f-9341-880b36292eb4` with the same message-level qualifier. No live CRM mutation smoke test has been run. Router lock expiry still requires a durable retry/reconciler for failures that are not replayed.

## ✅ CURRENT 2026-09-26 Newsletter Fail-Closed Repair

- Live inspection confirmed `LT - Newsletter Dispatcher` (`vru7OtCkDnPJkWt2`) already selected the newest pending week dynamically and had no hardcoded historical week keys.
- Its scheduled runs were failing when no GHL template matched active pending week `2026-09-21`. The missing-template path now fails closed with a no-op result instead of an execution error.
- Published active version: `dacd2df9-4647-4910-8ea3-857cf889f9b5`; `versionId == activeVersionId`. No manual execution or email send was performed. A matching current-week GHL template is still required before delivery can resume.

## ✅ CURRENT 2026-09-26 Campaign Classifier Repair

- `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) remains active on its native 15-minute schedule. The current published version is `07e53f3b-c427-4aea-b286-e1071e2b7839`; `versionId == activeVersionId`.
- The paired-item failure at `Upsert Qualified Domain` was repaired. Unknown Warm MQL contacts now pass through DeepSeek instead of being marked `qualified` by bypass, and MQL-derived rows cannot update `vapi_qualified_domains`.
- Sales Outreach promotion now re-checks open and closed Sales Outreach opportunities before moving a qualified Warm opportunity to Sales Outreach -> Qualified. Existing later-stage opportunities are preserved and closed-only records are not reopened.
- Recent pre-repair executions failed at the paired-item boundary; the first post-repair scheduled success remains unverified. Do not claim the repair is runtime-accepted until a new scheduled execution succeeds.
- This workflow does not classify the entire Warm -> New backlog. Warm -> New promotion remains the separate explicit AI-qualification path and is a TODO below, not a completed classifier capability.

## EOS TODOs — 2026-09-26

1. Verify the first post-repair scheduled execution of `IduCoT5YOs0g2faT`; inspect node-level output for DeepSeek decisions, tag writes, domain-cache writes, and MQL promotions.
2. Define and audit the separate Warm -> New qualification path; do not route Warm -> New records through the campaign/Vapi classifier without confirming the explicit AI qualification contract.
3. Reconcile the report's 22 current MQLs against the 15 currently returned by the live GHL Warm -> Qualified (MQL) search; identify snapshot lag, moved records, bounce records, and `not qualified` conflicts.
4. Diagnose `ghl_opp_owner_coverage` at exact opportunity/contact ID level; 4,614/11,569 = 39.9% remains below the 50% threshold. Do not lower the threshold or assign owners without an approved definition.
5. Repair and verify Attribution Bridge execution `1045692`; accept `bridge: ready` only after a successful execution and public health check.
6. Verify the next GA4/GSC bridge and Report Daily Rollups cycle after ingest executions `1048537` and `1048538`.
7. Build the durable retry/reconciler for inbound Priority events whose claimed router executions fail or expire.
8. Keep all outbound send, CRM mutation smoke-test, campaign activation, and sender changes approval-gated unless separately authorized.

## Executive Report V1 session handoff

- Read [`executive_report_v1_plan.md`](executive_report_v1_plan.md) before continuing Executive Report V1 work. It is the authoritative session handoff for the V1 plan, source rules, deployment state, verified progress, known gaps, and next audit steps.
- Preserve the current report at `reports/embed/executive/index.html`; V1 is isolated at `reports/embed/executive-v1/` and is deployed only at `/embed/executive-v1/`.

## ✅ CURRENT 2026-09-25 Executive Report V1 Closeout State

- The authoritative handoff is [`executive_report_v1_plan.md`](executive_report_v1_plan.md), updated for this closeout. Its dated 2026-09-25 section supersedes older V1 version/count references below.
- V1 is active at `https://reports.livetransparent.com/embed/executive-v1/`; the current report at `/embed/executive/` remains preserved and unchanged. The deployed static image remains `v3ud1lum1svamymuor21upog:social-mql-20260817`; current-report build remains `2026-08-17-v27-social-mql`.
- `LT - Executive Report V1 Data Materializer` (`knc2wxe4pyYIJ5tw`) is active/published at `47c5aaf8-047c-4cfe-996f-bdcbb97bb04d`; its appointment/contact join now handles direct IDs, `contact:<id>` keys, and raw contact dimension IDs.
- `LT - Executive Report V1 Facts API` (`oxYDg6XnRBKhl1Xd`) is active/published at `677e728d-8f33-4e78-a406-3a0dca56b19e`; meeting details and unique booking counts are restricted to calendar `SrtXcFVyea7pFl3nTiIK` (Regulated Ads On Social/Search) and count distinct contact IDs.
- The V1 meeting panel is titled `Meetings - Regulated Ads On Social/Search`; redundant Cameron/calendar text was removed. The previously missing six names were verified after materializer execution `988447`.
- Executive Summary (`Bukc0mgOD2r7V6ED`) is active/published at `4c5b5611-841b-48a4-9d78-c0700e599e6a`. Its attribution fallback now checks LinkedIn request/DM/reply ledgers and Apollo/Emerald tag evidence before using Unknown. The next successful execution must verify the exact split of the previously 83 unattributed opportunity rows; do not claim those exact rows are fully classified until that read-only check succeeds.
- Campaign Channel Summary (`MvPLbUAN9IIQikxb`) is active/published at `24492be1-3b62-436a-8dbe-7f46c64c314e`; SMS counts use the send ledger plus provider delivery events. Leads Ingest (`osIJOgBmWITF5Yuv`) is active/published at `7057fd10-a7db-4888-98ad-4adb1af1c2cc` with `pageSize=100`, `maxPages=1000`, and normalized contact-owner preservation.
- Reporting health repairs are active/published: Attribution Bridge (`Y0TU7Il71JswxOBp`) at `08d15fa4-e513-4ada-939e-51c3584440a7` deduplicates identity-map keys before upsert; Report QA (`M5mXcDTFSko6EdHb`) at `004f260e-7153-4ab7-9e30-dc066ea2458` measures opportunity owner coverage with contact-owner fallback. Queued bridge executions `989774` and `989781` remain unaccepted until they complete successfully.
- Do not treat HTTP 200 with an empty body, queued `new` execution, stale cache, or unverified attribution fallback as a successful closeout. No live outbound sends were performed for this reporting work.
- EOS boundary 2026-09-25: Executive Summary execution `989640` and V1 Facts execution `989659` were still `new`/queued; last accepted successes were `988482` and `988484`, before the final attribution fallback was verified end-to-end. Recheck these executions before relying on the new Apollo/Emerald/LinkedIn source breakdown.

## ✅ CURRENT 2026-09-19 Executive Report Source Health and Cache State

- The Executive Summary API (`Bukc0mgOD2r7V6ED`) is active/published at `00285be3-e4b5-4741-95a9-474b2c74ce00`. It emits `n8n`, `postgres`, and appointment snapshot health rows; the 7-day endpoint returned HTTP 200 with populated data and all three rows `ready`.
- The Executive Report frontend renders the primary summary before campaign-channel and prior-period requests finish. All three report API caches use a 30-minute successful-response TTL with cache locking and stale-if-error fallback.
- This current state supersedes the older Executive Summary version references below. Treat HTTP 200 with an empty report body as a failure, not valid zero data.

## ⚠️ IN PROGRESS: 2026-09-17 Executive Report Email Attribution Audit

- Read-only audit handoff: [`docs/sessions/2026-09-17-executive-report-api-regression-and-email-attribution-audit.md`](docs/sessions/2026-09-17-executive-report-api-regression-and-email-attribution-audit.md).
- `LT - Report Executive Summary API` (`Bukc0mgOD2r7V6ED`) is active/published at `da17ea49-6473-4e33-9df5-9d93bf6cf273`. It includes the `s.contact_id` fix, attribution response projection, and the later `s.campaign_key`/`s.campaign_group` qualification required after adding `Email_Events.campaign_key`. The embed-query endpoint returned HTTP 200 with 36,184 bytes and populated metrics. Do not revert this version.
- Newsletter dispatcher `vru7OtCkDnPJkWt2` now derives the newest pending week and matching template dynamically; active version `88c53670-6e0a-4f2d-a4c4-3f27ca3ffdff`. It currently fails closed when no builder matches the active pending week; no manual sender execution was run.
- Campaign Channel Summary `MvPLbUAN9IIQikxb` now honors explicit `Email_Events.campaign_key` and maps live Emerald event labels; active version `9bcb5e46-f2a4-484a-ad6e-7761c6538cef`.
- Email Event Ingest `ZrqFN8qLKO8eVHDc` now persists message ID, provider message ID, source event ID, campaign key, and sender email; active version `e57c2664-f0f1-484f-b3a6-32bba41ff125`. DAN event automations remain unwired.
- Do not infer historical campaign attribution where the recipient maps to multiple campaigns. Treat HTTP 200 with an empty report body as a failure, not valid zero data.
- **2026-09-17 follow-up regression and repair:** Adding `Email_Events.campaign_key` exposed a second ambiguity in the Executive Summary attribution CTE (`campaign_key` was unqualified after the new column existed). The report endpoint briefly returned HTTP 200 with an empty body, and the embed's fail-soft loader consequently displayed placeholders/zeros. The attribution CTE now qualifies `s.campaign_key` and `s.campaign_group`; Executive Summary version `da17ea49-6473-4e33-9df5-9d93bf6cf273` is active and published. A fresh endpoint call with the embed query returned HTTP 200 and 36,184 bytes; the latest execution succeeded. Do not treat an HTTP 200 with zero bytes as a valid report response.

## ✅ CLOSED OUT: 2026-09-17 Apollo C-Suite and Marketing September 2026 GHL Batch

- Source `Apollo_VP_Contacts.csv` contained 485 rows; 477 apparent new-contact rows were prepared after 8 exact-email matches. The operator completed the prepared CSV imports, including the 32-row phone-collision retry with original phone values moved to `Em_All_Known_Phones`.
- The expected tag count did not appear after the operator’s email/tag-only update import. The assistant directly reconciled 114 source emails with email-based GHL upserts, omitting phone values to avoid phone collisions; all 114 returned contact IDs and verified the required tag `Apollo_CSuite_and_Marketing_Sep2026`.
- GHL’s aggregate tag search remained incomplete/lagging and returned 395 contacts on the final check. Treat that as a searchable cohort boundary, not proof that the entire source cohort is absent from GHL.
- Opportunities were reconciled for those 395 searchable tagged contacts. The destination is `Sales Outreach` (`dhdlf3O4tymxFtHk4aqq`) → `New` (`3529dd3d-cab0-4279-967c-1aea203de4fb`). Final state: 361 in the requested stage; 25 already had opportunities elsewhere and were left unchanged; 9 transient create errors were confirmed afterward to already have the requested opportunity. No duplicate opportunities were created by the final reconciled state.
- Detailed handoff: [`docs/sessions/2026-09-17-apollo-csuite-sep2026-ghl-import-closeout.md`](docs/sessions/2026-09-17-apollo-csuite-sep2026-ghl-import-closeout.md). Do not create additional opportunities solely from the visible tag count; use exact-email/contact-ID reconciliation for any remaining source-cohort recovery.

## ⚠️ IN PROGRESS: 2026-09-16 GHL-Triggered Mass Email Delivery (active, dry-run protection still enabled)

- The generic email-template mass-delivery pipeline is built end-to-end. The authenticated intake, queue, and dispatcher are now **active/published**; queue and dispatcher `defaultDryRun=true`, so scheduled runs remain non-sending until that guard is deliberately changed. One controlled live send to the owner's address was made earlier (see below); all temporary probe contacts were deleted.
- **Schema APPLIED (non-sending):** `postgres/mass-email-bootstrap.sql` was executed against the `postgres` DB. Live tables `lt_mass_email_campaigns`, `lt_mass_email_deliveries`, `lt_mass_email_events`, 4 indexes, and the `lt_mass_email_campaign_metrics` view exist (all empty). Additive columns for the claim model: `campaigns.subject/queued_at/planned_count`, `deliveries.claimed_at/run_id`. The live intake schema node matches the versioned file byte-for-byte.
- **Intake:** `LT - GHL Email Template Trigger Intake (STAGED)` (`t5frjtbuKzVZI294`, version `9523da34-9306-462b-b24f-72594a62a023`, active/published). Webhook `/webhook/lt-email-template-trigger-stage`. Validates the dedicated `X-LT-Mass-Email-Secret`, ensures schema, idempotently upserts one campaign row (`ON CONFLICT (idempotency_key)`), returns `202` with `campaignId`/`created`; unauthorized → `401`, invalid → `400`, no row.
- **Queue:** `LT - GHL Email Template Campaign Queue (STAGED)` (`vRXRFC6IwIxUME2k`, inactive). Claims `accepted` campaigns, paginates GHL contacts, excludes no-email/duplicate/blocked-tag/`validEmail=false`, assigns senders round-robin, writes idempotent delivery rows. `maxRecipientsPerCampaign` bounds a cohort (0 = unlimited).
- **Dispatcher:** `LT - GHL Email Template Campaign Dispatcher (STAGED)` (`b41Sas8FVVrytZrl`, inactive). Resolves GHL template HTML, atomically claims deliveries, re-fetches each contact and fails closed on suppression/lookup errors, enforces per-sender daily caps (2333), sends via GHL Conversations Email, injects signed open/click tracking, captures provider message IDs, retries 429/5xx, finalizes campaign status.
- **Tracking:** open `J7xZH6BBnoXEQsoB`, click `TbYFpB80xSlRZ6gy`, provider events `f87KRQ1Slhs9VUxJ` — all inactive; `Config` now wired between webhook and record node; open/click stamp delivery timestamps; provider responder returns JSON.
- **Acceptance tests PASSED (non-sending):** duplicate retry returns existing campaign; invalid → 400 no row; queue dry-run = planned counts + zero writes; queue live-planning = 5 deliveries round-robin; dispatcher dry-run = 5 planned / 0 sent; dispatch-time suppression blocked a tagged contact (`suppressed:1`, `sent:0`); signed tokens resolve only to the intended delivery (bad token rejected); provider `delivered` updated the delivery; metrics view reported 2 opens as `total_opens=2`/`unique_opens=1` without inflating planned/sent/delivered. All test rows deleted (0 campaigns/deliveries/events).
- **Recipient allowlist:** queue + dispatcher Config carry `recipientAllowlist` (emails; empty = all) and the queue carries `contactIdAllowlist` (GHL contact IDs; skips pagination). Both are currently set to `edmundocadorniga@gmail.com`, so the pipeline can only plan/send to that address.
- **First controlled live send (2026-09-16):** one campaign (`allowlist-test-2026-09-16`, template `6a87716221922afe5eda9e6f`) sent to exactly one recipient from `cameron@livetransparent.co`; delivery `id=8` = `sent`, provider message `lbOQGrp4bxMvxIBNNFlq`; campaign `completed`. Dispatcher returned to `defaultDryRun=true` immediately after.
- **DELIVERABILITY ROOT CAUSE (2026-09-16, proven with mail-tester):** GHL LC Email for this location sends **all** mail through the `.com` sending subdomain `mg.livetransparent.com` (Mailgun `use4.send.mailgun.net`) regardless of the `emailFrom` domain. A `From:` on `.co`/`.agency`/`.org` therefore does not match the SPF/DKIM domain → **SPF and DKIM do not align → DMARC fails** for the From domain, so Gmail filters/spams it (also a look-alike-domain signal). Gmail later located the original `.co` test in spam; its headers showed `From: cameron@livetransparent.co`, `Reply-To: cameron@mg.livetransparent.com`, `mailed-by: mg.livetransparent.com`, and `signed-by: mg.livetransparent.com`, confirming delivery through the `.com` transport with a different `.co` From identity. Evidence: From `cameron@livetransparent.co` = **5.6/10, "You're not fully authenticated", DMARC fail**; From `cameron@livetransparent.com` = **8.8/10, "You're properly authenticated"**. **Fix applied to the mass-email pipeline:** sender pool is now `cameron@livetransparent.com`. **Confirmed 2026-09-16:** a fresh-subject send from `cameron@livetransparent.com` arrived in the inbox (not spam); Gmail showed `mailed-by: mg.livetransparent.com` and `signed-by: mg.livetransparent.com`, which match the `@livetransparent.com` From. **Still outstanding:** the live newsletter dispatcher (`vru7OtCkDnPJkWt2`) still uses `.co`/`.agency`/`.org` senders and has the same DMARC failure. GHL UI now shows all four dedicated domains present with `SSL Issued`; only `mg.livetransparent.com` is selected, while `.agency`, `.co`, and `.org` are unselected at warmup Stage 1 (0/1000). Select/enable a domain before testing its sender; if only one domain may be selected, keep `.com` selected and use only its sender.
- **Known limitation:** the GHL email-builder API does not expose a template subject; the dispatcher resolves subject as operator `subject` → parenthesized template name → template name. No mass-email unsubscribe webhook (provider-event only). Open/click/provider tracking workflows remain **inactive**, so open/click events are not recorded until activated.
- **Pre-activation hardening applied:** the intake validates `X-LT-Mass-Email-Secret`; the provider-event webhook validates a separate `X-LT-Mass-Email-Provider-Secret`, uses `POST` for body-bearing callbacks, and maps handler status codes to the actual response. Open/click tracking remains `GET`. The intake is active/published; provider events and open/click tracking remain inactive pending caller configuration and approval.
- **Next:** obtain approval for a broader live send naming template, cohort, max recipients, sender boundary, and window; verify SPF/DKIM/DMARC; optionally activate the tracking workflows; then flip the dispatcher `defaultDryRun=false` for that campaign only. Separate approval is required before activation or live sending.
- Detailed handoff: [`docs/sessions/2026-09-16-ghl-triggered-newsletter-design.md`](docs/sessions/2026-09-16-ghl-triggered-newsletter-design.md). Project status: [`Project Status and Next Steps.md`](Project%20Status%20and%20Next%20Steps.md).

**2026-09-17 live-state supersession:** Queue `vRXRFC6IwIxUME2k` and dispatcher `b41Sas8FVVrytZrl` are now active/published at versions `714b2d22-777c-4006-a233-d7e0fa6eb930` and `bf892c33-edca-416d-9b74-cff2ccea9fdf`. Both Config nodes use the sender pool `cameron@livetransparent.co,cameron@livetransparent.org,cameron@livetransparent.agency`; temporary recipient/contact allowlists are empty; the suppression blocklist is preserved. Both still have `defaultDryRun=true`, so scheduled activation has not enabled provider sends. Queue execution `956286` and dispatcher execution `956284` succeeded with zero live sends; execution `956269` also completed. No `new`, `running`, or `waiting` executions remained at final verification. Treat older inactive/.com-only statements in this historical section as superseded. Next step is transport-level SPF/DKIM/DMARC verification per sender, followed by an approved change to `defaultDryRun=false` for the intended campaign.

## ✅ CLOSED OUT: 2026-09-16 LinkedIn Outbound Safety Bug Fixes

- Active LinkedIn dispatcher, DM, Partnership dispatcher/DM, and suppression workflows were updated and published after the confirmed daily-limit, duplicate-send, literal-secret, and outbound-message-validation audit. Fresh GETs verified all five are active with `versionId == activeVersionId`; exact versions and evidence are recorded in [`docs/sessions/2026-09-16-linkedin-outbound-safety-bugfix-closeout.md`](docs/sessions/2026-09-16-linkedin-outbound-safety-bugfix-closeout.md) and `Project Status and Next Steps.md`.
- Actual template literals were parsed from the live registries: zero apostrophes and zero non-ASCII characters. Do not use whole-node character counts as copy proof because sanitizer tables and JavaScript syntax create false positives; use literal-level extraction.
- Remaining approval-gated work: validate `X-LT-LinkedIn-State-Secret` on the receiver, migrate hardcoded credential fallbacks, and implement the durable inbound-reply suppression design. Do not manually execute sender workflows or send tests without explicit approval.

## ⚠️ IN PROGRESS: 2026-09-14 LinkedIn Reply Suppression Review and Handoff

- Read [`docs/sessions/2026-09-14-linkedin-reply-suppression-audit-and-plan.md`](docs/sessions/2026-09-14-linkedin-reply-suppression-audit-and-plan.md) before changing LinkedIn senders. It records the live workflow IDs/versions, verified gaps, the refined design, test boundaries, and next steps.
- Current decision: do not treat a per-send GHL `lastMessageDirection=inbound` lookup as the primary guarantee. Build a durable LinkedIn-specific reply suppression record from inbound Unipile events before slower CRM writes; gate every automated LinkedIn invite/DM sender on it, with GHL checks as a fail-closed reconciliation fallback.
- Confirm the exact prospect/conversation and originating sender execution before attributing the supplied repeated-message screenshot to a workflow. Its repeated copy matches the connect-invite template; the partnership DM sender has a separate, confirmed cached-state-only gap.
- Preserve normal human replies through the GHL custom-provider outbound router. Scope suppression to automated outreach; do not block all GHL-originated LinkedIn messages.
- No production workflow, CRM record, campaign, sender, or live test was changed during this read-only review. Production workflow changes and live sends require explicit approval. The supplied screenshot is identifying prospect data and remains untracked/local; do not stage it.

## ✅ CLOSED OUT: 2026-09-11 Documentation Staleness Audit

- `AGENTS.md`, `plan.md`, and `Project Status and Next Steps.md` were reconciled against the September 2026 LinkedIn, runner, reporting, and SDR closeouts.
- The detailed handoff is [`docs/sessions/2026-09-11-documentation-staleness-audit-closeout.md`](docs/sessions/2026-09-11-documentation-staleness-audit-closeout.md).
- No production workflow, CRM record, campaign, sender, deployment, or live test was changed during this audit. The worktree remains intentionally dirty; stage reviewed files individually.

## ✅ CLOSED OUT: 2026-09-10 Business Improvement Plan and Shareable Guides

- `improvementPlan.md` is a review-only strategic plan for Transparent eCom. Its opening now contains a plain-language summary, document map, jump links, role-specific reading paths, video-informed positioning, customer FAQ, reusable messaging, a Cameron booking bridge, and Executive Report simplification recommendations.
- The full plan was converted to `Transparent eCom Business Improvement Plan - Full.docx`; it remains untracked and uncommitted. The condensed Google Doc and full converted Google Doc are documented in `Project Status and Next Steps.md` and the detailed closeout under `docs/sessions/`.
- The condensed guide's full-plan link was reinserted after an initial insertion did not persist and was verified in the document contents. Both Google Docs were verified under `ed@livetransparent.com`.
- This strategy/documentation session did not mutate or execute production workflows, GHL records, campaigns, senders, or website deployments. FAQ and claim language requires owner approval and proof references before publication or outbound use.
- The isolated sample landing page was built and deployed for review on 2026-09-10. Deployment details and limitations are documented in `docs/sessions/2026-09-10-sample-landing-page-preview-deployment.md`. The preview remains non-production and requires Cameron approval before any production implementation.

## Sample Landing Page Operating Boundary

- The sample landing page is a review-only prototype in `Sample Landing Page/`; its implementation plan is `Sample Landing Page/PLAN.md`.
- Build it as plain static HTML, CSS, and JavaScript. Keep it isolated from the production website, CRM, GHL workflows, campaigns, senders, and live tracking.
- Use a non-submitting CTA placeholder during early review. The approved GHL booking widget may be added only after page structure and copy are accepted.
- The sample preview may remain deployed as an isolated review service when explicitly requested. Do not add production tracking, connect CRM/GHL/booking functionality, or change the live website without explicit approval.
- Before any preview deployment, test desktop and approximately 390px mobile layout, accessibility basics, horizontal overflow, and unexpected network requests.
- The current preview uses HTTP at the generated `sslip.io` hostname; HTTPS is not yet working. Do not represent it as a production-ready deployment.

## ✅ RESOLVED: 2026-09-10 GHL PIT Rotation (all workflows + .env)

- Full closeout: [`docs/sessions/2026-09-10-ghl-pit-rotation-closeout.md`](docs/sessions/2026-09-10-ghl-pit-rotation-closeout.md).
- `.env` `GHL_PIT`, `GHL_API_KEY`, `GHL_PIT_LT_HERMES` all = the new full-access PIT (`pit-d25ac994-...`, Ed-supplied; verified GET /locations + POST /contacts/search HTTP 200). Both old tokens (`pit-3f4dc6...`, `pit-48a3...`) were also `pit-`-format and functionally identical — one token now covers all GHL slots including embedded workflow tokens.
- Live n8n: 70/75 workflows rotated via API (backs up pre-change JSON per workflow in `%LOCALAPPDATA%\Temp\lt_pit_rotation\`); re-verified by `scripts/n8n/inventory_n8n_pits.py` — only the new PIT remains in active workflows, all HTTP 200. Dead 401 token `13c5a02e54a2` gone from active workflows.
- Repo exports: 17 JSON files refreshed (0 old tokens confirmed remaining in repo `*.json`). Nothing committed/pushed; `.env` local-only.
- Untouched: `AGENCY_TOKEN_PIT` (agency-scope, unreferenced). Residual old tokens: 5 archived workflows (API cannot update archived; need UI unarchive or delete) + ~19 non-JSON helper scripts (offered to Ed, no permission yet).

## ✅ RESOLVED + MONITORED: 2026-09-07 External Runner PostgreSQL Network Path

- Detailed records: [`docs/sessions/2026-09-07-runner-network-path-fix-applied.md`](docs/sessions/2026-09-07-runner-network-path-fix-applied.md), [`docs/sessions/2026-09-07-runner-network-path-verification.md`](docs/sessions/2026-09-07-runner-network-path-verification.md).
- The live Coolify runner had `extra_hosts: postgres:host-gateway` and was NOT on `coolify-shared`, so `postgres` resolved to stale `10.0.0.1` → `ECONNREFUSED 10.0.0.1:5432` every 2 min on pg-using runner workflows.
- **FIX APPLIED and VERIFIED 2026-09-07 UTC**: removed the runner `extra_hosts`, added `coolify-shared` to the runner's networks, recreated the runner (backup + compose validation first). Runner now dual-homed (`10.0.2.5` shared + `10.0.4.4` private); `postgres` → `10.0.2.3`; TCP `postgres:5432` OK; n8n `/healthz` ok; workflow `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`r7UjWLndmc6EqEUW`) went from `ECONNREFUSED` errors to continuous `success`.
- **Monitoring live (replaced 2026-09-09)**: Hermes cron job `LT hourly infra+email monitor (Telegram)` (`9622fde81b78`) every 60 min — deterministic gate `C:\1_Ed's Active Work\AI\Hermes\scripts\lt_alert_gate.py` probes n8n `/healthz`, PostgreSQL container health, runner DNS/state, restart counts, and Gmail alert-subject emails (`[LiveTransparent]` `UNHEALTHY|RECOVERED|ALERT`); the agent runs ONLY when the gate line changes, then classifies from full email bodies, applies read-only + safe auto-fix, and escalates to Ed via Telegram (deliver=telegram, ONE message per issue; ids marked processed only on resolution). Old 30-min jobs `33eea46dd9b3` and `b3f164cd1746` PAUSED (folded into the hourly monitor). Full record: [`docs/sessions/2026-09-09-workflow-incident-alerts-skill-review-and-hourly-telegram-monitor.md`](docs/sessions/2026-09-09-workflow-incident-alerts-skill-review-and-hourly-telegram-monitor.md). Email transport: Hermes Google OAuth Gmail (`edmundocadorniga@gmail.com`), tested in prior sessions.
- The n8n internal pool-closure incident remains OPEN and separate (see below). Do not treat the network fix as proof the pool issue is fixed.

## ✅ IN PROGRESS: 2026-09-09 Executive Report — SDR Performance & Owner Attribution (Phases 1–5 LIVE; monitoring/sign-off remains)

- Request (sales leadership/marketing): track booked meetings by SDR for the end-of-month SDR assessment (focus SQL/booked meetings), plus per-SDR owner attribution, showed/no-show, SQLs created, MQL→SQL conversion, lead source for MQL/SQL, and clarification of the former owner-labelled active-deals view.
- **Phases 1–2 IMPLEMENTED and verified 2026-09-09** (operator sign-off on Phase-0 decisions: canonical booked meeting = appointments by `start_at`; owner authority = native opportunity `assigned_to` primary + contact fallback + explicit Unassigned bucket; SDRs = Jason + Marc). Details + verification: `docs/sessions/2026-09-09-executive-report-sdr-attribution-phase1-2.md`.
  - `report_sdr_registry` DDL + seed in `postgres/reporting-bootstrap.sql`, applied live (Jason/Marc SDR; Cameron leadership; Ed exec; Janvi resolved as non-SDR; Kevin/Mike/Remus informational).
  - Daily Rollups `EUeOiRttoVLQ9zF9` active `1af59845…` carries `assigned_to` through `tmp_report_opps`/`tmp_daily_opps_fixed`.
  - Report QA `M5mXcDTFSko6EdHb` active `a21c0f4a…` probes `ghl_opp_owner_coverage` (34.6%) + `ghl_appt_owner_coverage` (11/31) into `report_source_health`.
  - Exec Summary `Bukc0mgOD2r7V6ED` active `90bcc99f…` returns `sdrPerformance` per-owner rows; `meetingsBooked` aligned to appointments (`basis appointments_start_at`, `meetingsBookedStageBasis` kept); query now runs `SET jit=off` (16–19s vs ~71s before). Postgres credential `pgAzUqpwOiGkGXzO` retained on all nodes.
  - Frontend `reports/embed/executive/index.html` deployed as build `2026-09-09-v28-sdr-performance` (backup `index.html.bak-20260909-022102` in the reports container): SDR Performance table + nav item + glossary, former owner-labelled active deals view → "Team Active Deals". Desktop + 390px verified, no overflow, only benign favicon 404.
  - **Phase 4 IMPLEMENTED 2026-09-09**: Lead Source panel (MQLs Entered / SQLs Created by originating source) in Exec Summary `Bukc0mgOD2r7V6ED` (new active version `162bbba8-0b28-425d-891c-488bd00bc781`, `versionId == activeVersionId`, postgres cred `pgAzUqpwOiGkGXzO` retained). New CTEs `lead_source_contacts` / `lead_source_bridge` / `lead_source_mql` / `lead_source_sql` / `lead_source_breakdown` / `lead_source_coverage` resolve each MQL/SQL opportunity's contact → first UTM source (medium/campaign) with `report_bridge_traffic_to_lead` fallback, then GHL contact `source`; breakdown caps at 20 rows, coverage reports attributed/total (30d: 32/164 SQLs, 0/3 MQLs — bounded by the ~500-row Leads snapshot). Query timing unchanged (~17s JIT-off). Frontend build `2026-09-09-v29-lead-source` deployed (backup `index.html.bak-20260908-185312`), Lead Source nav item + panel + glossary card, desktop + 390px verified no overflow, zero console errors. Details: `docs/sessions/2026-09-09-executive-report-sdr-attribution-phase4-lead-source.md`.
- **Phase 3–5 status (2026-09-09 session)**: Unknown owners resolved + seeded — `ck6TRlU3wnTmMxuVpn5F` = **Janvi Mahajan** (`janvi@livetransparent.com`, non-SDR; resolved via live GHL `GET /users/`), Kevin `7s3brzxGF4WSiz95DPkF` / Mike `D8NgkeZYX481rR4J2gOc` / Remus `R5VljBpXah3LaVXFNfCV` added informational; `report_sdr_registry` = 8 rows applied live (bootstrap staged/uncommitted). **GA4+GSC stale was diagnosed + RESOLVED 2026-09-09** — both n8n Google OAuth credentials had re-expired (~09-03/09-04); the operator reconnected them 09-09 and I verified (manual runs GA4 `916807`, GSC `916808`, bridges+rollups `916815-916817`; data current through 09-07; `report_source_health` ga4/gsc `success`). **Phase 3 (Showed/No-show) IMPLEMENTED + LIVE 2026-09-09**: `LT - Meeting Outcome Reminder` (`x5vUQ34IcyKggdqP`, active `cf3c0d72…`, `versionId==activeVersionId`) posts a per-SDR pending-outcome digest to Slack `#sales` Mon–Fri 08:00 LA (smoke `916780`); SDRs mark Showed/No-Show in GHL and the 6-hourly Appointments Ingest (30d look-back) re-syncs status — no report/ingest change. Phase 5 scope confirmed: rank SDRs on **Booked + SQLs + MQL→SQL** (non-SDR/Unassigned rows shown but excluded). Stage-based MQL authoritative (140 total / 3 entered 30d) vs tag ledger 31 (27 in 30d). Details: `docs/sessions/2026-09-09-sdr-attribution-phase3-5-owners-and-ga4-gsc-diagnosis.md`.
- **Post-implementation follow-up**: monitor the daily 08:00 LA meeting-outcome digest runs (Slack `#sales`) and confirm SDRs start marking Showed/No-Show in GHL; get Cameron/Janvi sign-off on the confirmed per-SDR ranking scope wording (Booked + SQLs + MQL→SQL); confirm nightly Rollups/QA health after GA4/GSC reconnection. Janvi and the previously unknown owner IDs are resolved and seeded. Full plan: `docs/sessions/2026-09-09-executive-report-sdr-attribution-plan.md`.

## ⚠️ IN PROGRESS: 2026-09-10 SDR attribution for regulated-ads bookings (booking webhook capture deployed)

- **Problem:** An SDR who books a regulated-ads meeting on Cameron's calendar (`SrtXcFVyea7pFl3nTiIK`) gets no credit in `sdr_booked`: at booking, opportunity ownership flips to Cameron and the SDR is recorded NOWHERE that survives (appointments `createdBy.source=booking_widget` userId null; opp created unassigned/Cameron; contact `assignedTo` never an SDR). Confirmed to GHL source of truth; **historical bookings unrecoverable — future-only fix**.
- **Root-cause anchors:** routing stamps `opportunity_owner_sync` → contact field `FQv9wyl2JrMkpf1GPprP`, `opportunity_owner_change` → `IPzJpFLekz9TDi4nWBaV`, written by GHL workflow **`LT - Opportunity Owner Alignment`** (`b26326a5-77af-4df8-8d86-3f636e73afe0`, v7, branches Jason/Marc by `assignedTo`).
- **GHL field DONE:** Contact custom field `Originating SDR` exists as `TEXT`, field id `wBGXjev0rKowcfxTSWNa`. Its value is the assigned user's email in the booking webhook; n8n maps Jason/Marc/Cameron emails to their GHL user IDs.
- **Correct booking boundary identified:** GHL workflow `Appointment with Cameron for Regulated Ads` (`971c3016-946a-4612-ad0a-2afc9a0ee6f0`) is confirmed `published`, version 14, updated 2026-09-09 17:09:26 UTC, and posts to `https://automations.livetransparent.com/webhook/wl-slack-channel-update-v2`. This is separate from `LT - Opportunity Owner Alignment`, which remains owner synchronization only. The public GHL workflow-list API does not expose action bodies, so the `assignedSDR` payload still requires runtime webhook confirmation.
- **n8n implementation LIVE:** `WL - Webhook to Slack Channel Update` (`lQTW0QPwBcf3o7j8`) active/published at version `1cb05fcd-e0c0-4ae1-9413-637878325e8e`. Its `Build Slack Payload` node reads `assignedSDR`, writes field `wBGXjev0rKowcfxTSWNa` before SQL-tag/opportunity mutation, and skips stamping when the value is missing or unrecognized. The Exec Summary `Bukc0mgOD2r7V6ED` was also activated with field id `wBGXjev0rKowcfxTSWNa` in version `08abd9cb-7100-4e31-88d1-4413aadee625`; both workflows have matching draft/active versions.
- **Verification boundary:** Live workflow reads after deployment passed; no production test execution was run because the webhook performs CRM writes and sends Slack. No executions are currently `new`, `running`, or `waiting`.
- **Next:** observe the next real booking webhook and verify the already-published GHL workflow supplies custom-data key `assignedSDR`, then confirm `sync.originatingSdr = stamped`, the contact field value, and the resulting SDR row in Exec Summary. Historical bookings remain unrecoverable.

## Document precedence (applies to all future work)

1. Live Coolify/n8n state (authoritative: generated `/data/coolify/services/n44wksswcocwk88ogcog8c48/docker-compose.yml`, container state, health endpoints)
2. `Project Status and Next Steps.md`
3. Latest dated session handoff under `docs/sessions/`
4. This file's operating rules / safety gates
5. `plan.md` and `repomix-output.md` — historical/archive material; not operational source of truth

## ✅ RESOLVED: 2026-09-02 n8n Compose Database/Runner Hardening

Updated `n8n/docker-compose.yml` after diagnosing transient n8n readiness failures and runner `pg` resolution issues. The changes are committed and pushed in commit `27dea1e`.

### Persistent Compose Changes

- n8n and the inline runner base image were pinned to `2.36.9` at that time; the deployed version is now `2.37.10` (2026-09-07 force redeploy). Concurrency/health settings below remain in effect.
- Production execution concurrency is capped at 5 with `N8N_CONCURRENCY_PRODUCTION_LIMIT=5`; the runner task concurrency remains 10.
- PostgreSQL idle connections are recycled after 30 seconds and pooled connections after 30 minutes.
- n8n database health monitoring pings every 5 seconds and begins recovery after 3 failures, with 1-30 second exponential backoff.
- Runner idle shutdown is set to 300 seconds and runner concurrency is set to 10 in the Compose service environment.
- The Coolify/Compose runner uses the pnpm module path `/opt/pg-node_modules/node_modules` for `pg`. Do not use the standalone runner path `/opt/pg-node_modules` here; that npm-layout path applies only to `scripts/deploy/deploy_runner.py` and `n8n/runners/Dockerfile`.
- Both services use the external `coolify-shared` network, and the n8n service retains the `n8n` network alias required by the runner broker URI `http://n8n:5679`.

### Verification

- `docker compose -f n8n/docker-compose.yml config --quiet` passes with `N8N_RUNNERS_AUTH_TOKEN` supplied by the deployment environment.
- `git diff --check` passes.
- After the deployment restart, `https://automations.livetransparent.com/healthz/readiness`, `/healthz`, and `/` returned HTTP 200. A temporary 404/bad-gateway symptom occurred during container recreation and cleared without a configuration rollback.
- Do not commit the untracked PowerShell investigation scripts from the September 2026 session; several contain embedded GHL bearer tokens. Use environment-based `GHL_PIT` access instead.

## ⚠️ OPEN: 2026-09-07 n8n PostgreSQL Pool Closure Investigation

The later n8n incident is documented in [`docs/sessions/2026-09-07-n8n-pool-closure-investigation.md`](docs/sessions/2026-09-07-n8n-pool-closure-investigation.md). The immediate mechanism is confirmed: n8n remained alive while its internal PostgreSQL pool was already ended, producing `Cannot use a pool after calling end on the pool`, readiness failure, and authenticated API HTTP 503 (`Database is not ready!`). PostgreSQL connectivity, credentials, runner networking, and substantive Compose alignment were not shown to be the primary cause.

The original event that called `pool.end()` remains unresolved. No restart, deployment, workflow operation, configuration write, or database change was performed during the initial investigation. A September 4 kernel soft-lockup involving `postgres` and `soketi-server` is a clue but not proven causal because the first retained pool error was September 7. The live stack was subsequently force-redeployed on n8n `2.37.10` and is monitored, but that does not identify the original caller. If the pool-closure symptom recurs, correlate Docker/Coolify, PostgreSQL, n8n, runner, host, and network events before an approved n8n-only restart. Do not restart PostgreSQL/Redis or rotate `N8N_ENCRYPTION_KEY` casually.

## ✅ RESOLVED: 2026-08-30 Executive Report Audit & Fixes

Full 7d/30d cross-check of the Executive Report (`https://reports.livetransparent.com/embed/executive/`) against source Postgres tables. The report page was **completely down** — nginx returned 504 because the Executive Summary query took 76.5s (nginx default proxy_read_timeout is 60s). Fixed everything and cut query time to ~15s.

### Changes made (all in `LT - Report Executive Summary API`, active version `11ca17d6-fba7-4fe3-b45c-4c8522ca9e49`)

| Fix | Detail |
|-----|--------|
| **nginx 504** | `reports/nginx.conf` now sets `proxy_read_timeout 300s; proxy_send_timeout 300s; proxy_connect_timeout 10s`. Applied to the running `reports-livetransparent` container + `nginx -s reload`, and committed to the repo. **Permanent via rebuild** — `reports/Dockerfile` copies `reports/nginx.conf`, so the next image build bakes it in; the currently-running container still has the old image until rebuilt. |
| **GHL Calls read wrong table** | The `calls` / `call_status_breakdown` / `call_outcome_breakdown` / `call_outcomes` CTEs read `report_raw_ghl_call_outcomes` (Vapi/GHL outcome table, stale since 08-10) → reported **0 calls**. They now read `report_raw_ghl_calls` (the working GHL Conversations ingest, every 4h). 7d window: 201 calls (115 completed, 51 no-answer, 19 busy, 12 failed, 4 ringing; 4 inbound / 197 outbound; answered 115, missed 82). |
| **Duplicate "Unassigned" channels** | `channels` CTE outer SELECT used `COALESCE(NULLIF(g.channel,''),'Unassigned')` so any row coming only from the rollup side (`r`) was labeled "Unassigned", producing two identical rows. Fixed to `COALESCE(NULLIF(COALESCE(g.channel, r.channel),''),'Unassigned')`. |
| **Vapi timezone buckets** | `vapi_timezone_buckets` counted ALL queue rows ever (2708) and emitted camelCase keys the frontend can't read. Now `WHERE status='pending'` (39) and emits both camelCase AND snake_case keys (`total_queued`/`explicit_count`/`inferred_count`/`none_count`) the deployed frontend expects. |
| **Stage movedIn boundary bug** | `stage_daily` CTE fetched from `$1 - 1 day` for the LAG baseline but did NOT filter the output to the window, so the entire previous day's `stage_count` was counted as "moved in" (Warm New movedIn 5476 vs true 1679). Added `WHERE x.report_date >= $1::date`. |
| **Perf: vapi timezone cross join** | `vapi_timezone_buckets` joined `voice_call_queue` to `vapi_contact_timezone_snapshots` with an `OR` on two normalized IDs → forced a 6.28M-row nested loop (~12s). Replaced with a single equality join on `LOWER(TRIM(REPLACE(q.contact_id,'contact:','')))`. |

Overall Exec Summary query went from **73–77s → ~15–21s** (both 7d and 30d verified through the proxy).

### Pipeline fixes
- **Pipeline Velocity** (`iFfwh0jpYUZoDhDR`): schedule was `hoursInterval:24` and had **0 executions ever** (stale data since 08-24). Changed to daily cron `0 9 * * *` (UTC), published (`09e0f2e7-193b-4102-9008-4ec33bda02d2`), and manually re-ran (execution `832368`) so `report_stage_velocity_summary` is fresh. Health now `ready`.
- **Sender schedules are NOT broken** — the Vapi dialer (`*/2 9-16 * * 1-5`), LinkedIn DM Sequence (`0 12-22 * * 1-5`), IG Company Sender (`0 10-15 * * 1-5`), and LinkedIn Dispatcher (`*/15 15-21 * * 1-5`) are all **weekday-only cron schedules** in America/Chicago or America/Los_Angeles; the apparent "outage" was just the weekend. They will resume Monday. (A harmless deactivate/reactivate cycle was done during diagnosis.)

### Findings needing operator action
- **GA4 resolved 2026-08-31** — the Google OAuth credential was reconnected by the user. `LT - GA4 Daily Ingest` was manually re-run (execution `832654`) and backfilled the entire 08-14…08-29 gap; the GA4 Traffic Rollup Bridge + Daily Rollups were re-run so `report_daily_summary.sessions` is current. The 7d report now shows traffic=174, users=166, real channel breakdown (Direct 43, Email 102, Organic Search 15…), and ga4 health `ready`. **⚠️ Re-broken 2026-09-09 → RESOLVED**: both GA4 (`Google Analytics account`) and GSC (`GSC - Cameron Livetransparent Google account`, id `EKnNrSvlEd0A99AX`) n8n OAuth credentials expired again ~09-03/09-04 (GA4 frozen at 09-02, GSC at 09-03; Exec Report health showed `stale`). **Reconnected by the operator 2026-09-09 and verified**: manual GA4 ingest run `916807` (853 rows, self-backfilled 90d through 09-07), GSC `916808` (13 rows through 09-07), GA4 Bridge `916815` + GSC Bridge `916816` + Daily Rollups `916817` all success; `report_daily_summary.sessions` restored 09-03…09-07 (25/10/5/11/13) and `report_source_health` ga4/gsc = `success`. GA4 data for 09-08 flows on the next scheduled GA4 run (~13:31 UTC) + Rollups.
- **LinkedIn senders: root cause = temporary LinkedIn restriction, now cleared + fixed.** Around 08-28 17:00 UTC the Unipile LinkedIn account hit a temporary LinkedIn sending restriction — every `/users/invite` and `/chats` returned 422. **Verified cleared 2026-08-31**: a live `/users/invite` to a previously-failed ready-pool target returned HTTP 201 (invitation_id `7499980380033150976`). The restriction was likely the weekly invitation limit. Fixes applied:
  - **Dispatcher stuck-claim bug (the real accumulation)**: `Fetch Ready Queue` claimed `ready`→`requested_pending` and when the daily invite limit was reached it returned early WITHOUT releasing the claim — so claimed rows accumulated forever (5,046 stuck rows, all `request_sent_at IS NULL`). Released all 5,046 back to `ready` and added a self-healing `released` CTE to the claim SQL (releases `requested_pending` rows older than 30 min with no confirmed send). Dispatcher published `7b002976-9e3e-450e-9c36-073e13c4e342`.
  - **DM Sequence unreachable recipients**: 5 connected contacts (perrychase, darrylbryanallen, adolfo-araiza, cceciliaw, alison-li-lin) have genuinely unreachable LinkedIn profiles (Unipile `errors/invalid_recipient` on both provider-id and public-identifier lookups) and were clogging the hourly batch. The selection query now excludes `payload_json.dm_unreachable='true'`, the send code marks contacts `dm_unreachable` on invalid_recipient detection, and the 5 current ones are flagged. DM Sequence published `e99b0d0d-b90f-4e41-89bd-164c98e48c7e`.
  - The dispatcher's 08-28 invite failures were the temporary restriction (not a code bug); the DM sequence's 08-28 failures were the 5 unreachable profiles + the restriction. Sender schedules resume Monday.
- **GSC reconnected 2026-08-31** — the user reconnected the Search Console credential; `LT - GSC Daily Ingest` re-ran successfully (execution `832997`) and health is now `success`. It uses a 3-day rolling window (Config computes `end=yesterday, start=end-2`), so the 08-08…08-29 outage gap was NOT backfilled — but GSC volume is negligible (0 clicks, ~30 impressions/month), so the impact is immaterial.
- **Contact acquisition UI cleanup (2026-08-31)** — `contact_sources` CTE now relabels GHL/msgsndr tracking-link landings (`/links/`, `msgsndr.com`) as a single `Email/SMS link` source with a blanked landing page instead of ~17 one-contact rows carrying unreadable `services.leadconnectorhq.com/links/r/2/{JWT}` URLs. 18 link-click contacts now aggregate into one row. Exec Summary version `a66e1914-7ff0-4414-b218-9f688b52803a`.
- **OpenRouter credits restored 2026-08-31** — user added credits; no further `402 Insufficient credits` errors in n8n logs (affects IG/Dispensary/Partnership enrichment + DeepSeek classifier).
- **`sqlContacts`/`poolDistribution` fixed (2026-08-31)** — these read `report_raw_ghl_contacts`, but the pool tags are NOT real GHL tags (`brands_pool`/`dispensaries_pool`/`vapi_campaign_*` return 0 via GHL `/contacts/search`; they are source-list designations in `emerging_pool_contacts`). Exec Summary `pool_distribution` now reads `emerging_pool_contacts` for `brandsPool` (3,668) / `dispensariesPool` (10,200) and `voice_call_queue` for `vapiBrand` (106) / `vapiDispensary` (66 distinct contacts). `sqlContacts` reads the `sql` GHL tag (36 contacts): backfilled once into `report_raw_ghl_contacts` and now re-snapshotted daily by a `sql`-tag fetch added to `LT - GHL Daily Leads Ingest` (idempotent, `report_date` = LA-yesterday so it lands in the current window). Exec Summary version `9c43be7d-7160-448f-82be-00e5f8303b88`.
- **n8n runner `pg` + network fix (2026-08-31 diagnosis, superseded 2026-09-07)** — the Coolify-managed runner initially had an incompatible `NODE_PATH` and stale PostgreSQL host mapping. The repository and live Coolify stack were corrected, the runner was recreated on `coolify-shared`, DNS/TCP resolution was verified, and a pg-using dialer workflow returned continuous success. Treat the network path as resolved and monitored; do not re-apply the old drift diagnosis unless the monitor alerts. See `docs/sessions/2026-09-07-runner-network-path-verification.md`.
- **`report_raw_ghl_call_outcomes`** is now effectively deprecated for the report (reads `report_raw_ghl_calls`). Note: `LT - Call Outcome Ingest` (`PUCfTZBANSPcgS0c`) writes to database **`n8n`** (not `postgres`), so its rows never reach the report DB — a pre-existing misconfiguration worth fixing.
- **Newsletter is live** — `newsletter_send_log` shows 19,739 sent + 101 failed in the 08-23…08-29 window. The DNS-gate note is stale; go-live happened 2026-08-21. The current dispatcher uses 250-row batches every 15 minutes Monday-Friday, with a database-backed cap of 2,333 per sender (6,999/day). Report folds newsletter metrics into email metrics with these definitions:
  - `emailsSent` = **unique sends** (one row per `ghl_contact_id + week_key` in `newsletter_send_log`; UNIQUE constraint ensures no duplicates)
  - `emailsOpened` = **total open events** (counted from `newsletter_events`; a single contact can have multiple open events tracked via HMAC pixel)
  - `emailsClicked` = **total click events** (counted from `newsletter_events`; a single contact can have multiple clicks tracked via HMAC link rewriting)
  - `emailsUnsubscribed` = **unique unsubscribes** (one row per contact who clicked unsubscribe link; logged in `newsletter_events` and `newsletter_send_log`)
  - `newsletterFailed` = **failed send attempts** (rows marked `status='failed'` in `newsletter_send_log`; 101 in last window)
  - Rates (`emailOpenRate`/`emailClickRate`/`emailBounceRate`) are computed from **unique recipients** in the window send cohort
- `sqlContacts`/`poolDistribution` were historically limited by the 500-contact GHL snapshot; the current Executive Summary uses the SQL tag ledger and source tables where available. Treat remaining coverage gaps as data-source limitations, not as evidence that the report logic is still returning zeroes.

## ✅ RESOLVED: 2026-08-12 Postgres Write Blocker

**The n8n Postgres node v2.5+ has a known bug where `queryReplacement` silently fails to persist data.** This affects ~25 Postgres nodes across ~12 workflows. The root cause is that parameterized queries (`$1, $2, ...`) fail to commit in n8n's embedded task runner.

### Current Strategy: External Task Runner

The fix is to switch n8n from embedded task runner mode to **external task runner mode** (`N8N_RUNNERS_MODE=external`). This requires:
1. A custom `n8nio/runners` Docker image with the `pg` module installed
2. The `NODE_FUNCTION_ALLOW_EXTERNAL=*` override in the runner config and runner container
3. Code nodes using `require('pg')` for direct Postgres connections (bypassing the broken Postgres node)

### What's Already Done

| Area | Status |
|------|--------|
| **Frontend fixes** (CSS, mappings, CORS proxy, outgoing calls) | Deployed to live |
| **Database tables** (emerging_pool_contacts, DAN/Emerald release logs, Email_Events) | Created |
| **LinkedIn workflows** (6 workflows, 16 nodes) | Published with fix |
| **Campaign/Email workflows** (4 workflows, 4 nodes) | Published with fix |
| **GHL Leads Ingest** (4 Postgres nodes) | Published with fix |
| **GHL Sales Ingest** (`aYT5oHcgmBALzHy5`) | Published with fix (version `91603d56`, execution `743094`, 7,984 opps) |
| **Call Outcome Ingest auth** (`PUCfTZBANSPcgS0c`) | Published with secret header (version `7af98411`) |
| **Executive Summary query/runtime recovery** (`Bukc0mgOD2r7V6ED`) | Fixed (version `d177a923`, corrected stage-velocity date column and removed redundant campaign lookup) |
| **Report timezone drift** (both report workflows) | Fixed (timezone-aware `isoDateInTimezone()` in both Normalize nodes) |
| **Voice dialer Postgres migration** (`r7UjWLndmc6EqEUW`) | Fixed (version `b8e9c57a`, 4 nodes migrated from broken Postgres v2.6 to direct pg) |
| **Voice callback Postgres migration** (`fx4UvKUWbqJEY3LK`) | Fixed (version `c97480db`, 8 nodes migrated from broken Postgres v2.6 to direct pg) |
| **Voice dialer release-lock verification** (2026-08-14) | Shared scheduled Vapi path verified across 13 consecutive successful executions, including `746845`; no recurrence of `there is no parameter $1`. Not a manual-dialer or Twilio issue. |
| **Voice queue enqueue persistence verification** (2026-08-14) | Found a second active voice path still using Postgres v2.6 `queryReplacement` in `LT - Voice Queue Enqueue` (`XzcpOBi9YcIhJPck`). Replaced `Postgres - Insert or Noop` with direct `require('pg')`, published version `42aba803-09b0-4118-a105-9161bebe66e9`, and verified `versionId == activeVersionId`. |
| **Voice intake poller hardening** (2026-08-14) | Published `LT - Voice Queue Vapi Intake Poller` (`bYk1Ai6MJLyhTsDZ`) on `5c464233-c79a-4f49-a809-de303f3b6136`. Aligned terminal blocklist tags with enqueue, routed suppressed contacts through the skip branch, surfaced tag add/remove failures, and made queue insert/no-op outcomes explicit. Smoke execution `747051` succeeded. |
| **Voice intake Apollo tag-context fix** (2026-08-14) | Published `LT - Voice Queue Vapi Intake Poller` on `d852a93d-b468-4b9b-8cc9-d4995131f926`. Preserved the classified campaign tag across the Apollo HTTP response boundary so `Remove Tag - Enriching` removes the actual campaign tag instead of falling back to `vapi_queue`. Verification execution `747053` showed `tagsRemoved: ["vapi_campaign_brand"]` and succeeded. |
| **ghl_contact_id re-backfill** | 12,639/13,868 matched from GHL export CSVs (1,229 not in exports) |
| **Embedded secrets audit** | 12 critical, 5 high, 2 medium findings across 83 active workflows |
| **n8n container** (DB_TYPE=postgresdb, persisted encryption key) | Running |
| **External runner container** (custom image with pg) | Running; `pg.Client` resolves successfully |
| **External runner task timeout propagation** (2026-08-14) | Fixed. `N8N_RUNNERS_TASK_TIMEOUT=300` is now set on the runner container itself, not only the n8n broker. Sales Ingest verification execution `749605` completed in 104.7s and persisted 8,007 opportunities plus 8,007 history rows. |
| **GHL Sales Ingest daily schedule** (2026-08-14) | Fixed. Invalid `minutesInterval: 1440` was firing hourly because minute intervals only support 1-59. Published version `c1b5020c` now runs daily at 1:15 AM `America/Los_Angeles`, after the hourly Leads Ingest. |
| **Social reporting accuracy** (2026-08-17) | Executive Summary version `e4fa3d18` adds account-level reach/impressions/followers from the new daily statistics ingest (`veg9jbN1P67Xmqy8`, PIT-backed) and reworks `mqlSummary` into total MQLs / converted-to-SQL / current MQLs plus windowed movement. Social ingest version `2ed24c59` paginates the 366-day horizon and passed execution `759065`; report build `2026-08-17-v27-social-mql` passed desktop and 390px checks. |
| **Social statistics ingest live** (2026-08-17) | `LT - GHL Social Statistics Ingest` (`veg9jbN1P67Xmqy8`, version `bee234fb`) runs daily 06:00 LA, calls `/social-media-posting/statistics` with the GHL PIT, and stores 7/30/90-day window totals in `report_ghl_social_statistics` in the report database. Execution `760249` stored 12 rows. |
| **LinkedIn DM pipeline repair** (2026-08-18) | Dispatcher `f2f52041`, DM Sequence `bc79f0d1`, Reply Backfill `9e0131f4`, State Upsert `4045c96c`. Fixed dispatcher `\\/` regex + 60/day limit, DM send 422 (existing-chat routing), reply-backfill over-suppression, and the state-updater blocking `requested_pending -> requested`. DM sends now write a durable `dm_sent` event (dedup + reporting metric). 60 distinct invites verified today, zero duplicates; DM queue 66. |
| **LinkedIn send-path double-escape corruption** (2026-08-19) | A 2026-08-11 MCP mutation (version `3b70854e`) double-escaped regex literals in the Code nodes. Two distinct failures resulted. (1) The Dispatcher **crashed at parse time** (`SyntaxError: Invalid regular expression flags` on the `identifier()` `\\/` regex), so it sent **no invites at all** from 08-11 to 08-18. (2) After the 08-18 REST PUT fixed that crash, `sanitize()` char classes matched literal letters `u`/`C`/`D` + digits instead of smart quotes (`u`→`'`, `C`→`"`, producing `"ameron co-fo'nder of Transparent e"om`) and `/\\{first_name\\}/gi` matched only literal `\{first_name\}`, leaving `{first_name}` unreplaced — so **garbled invites were sent only from 08-18 00:15 through 08-19 04:45**, bounded by the 60/day cap, not since 08-11. The 08-18 REST PUT inherited but did not touch these regexes. Fixed via `scripts/linkedin/fix_linkedin_sanitize_double_escape.py`: Dispatcher `fXxw5lanZcDmUrst` (sanitize 8 escapes + `{first_name}` + `[^\\s,]` URL class) → `0a349cdb-295f-45a5-978a-2f3e46022ace`; LinkedIn DM Sequence `d0tEtijajisIsYcs` (`{first_name}` in Sync Connected from Unipile + Send DM Sequence Messages) → `db7dde63-2f6e-42e8-92f0-7f68c66e7445`; both published + active. Full-instance scan of all 164 workflows confirmed no other Code nodes affected. Same failure class as the 2026-07-15 mojibake fix. Full narrative: `docs/sessions/2026-08-19-linkedin-double-escape-fix.md`. |
| **Emerald release-log single-row bug + Apollo August batch enrollment** (2026-08-20) | `LT - Emerald Campaign Sender Release Dispatcher` (`8UXlpoMJnQ229AuG`) `Write Release Log` node used `mode: runOnceForAllItems` with `$json`, so only **1 release-log row persisted per run** even when 60–132 were queued — the other queued contacts stayed pending+unlogged and were re-selected on the next hour (re-tagging risk). Fixed by iterating `$input.all()` in `Build SQL - Write Release Log` and setting `queryBatching: "independently"` on the Postgres node; published version `d6737e68-b2b1-4163-bd99-19d0176640c2`. Separately enrolled 73 clean `apollo_august2026` imports (of 86) into `Emerald_Campaign_Contacts` with `bucket=executives_mso` (dispatcher run `769889`, all queued + GHL enrollment confirmed via `seq emerald - executives mso`/`seq enrolled - emerald`); 12 were already Emerald-enrolled and 1 DAN-only (skipped). Marked the 73 released + release-logged, then backfilled release-log + released status for the 58 prior-run contacts the bug had left unlogged so no re-dispatch occurs. Postgres campaign tables live in the `postgres` default DB (container `postgres-uokgs4c04ko0s4scccg40cgg`), not `n8n`. |
| **Same release-log single-row bug fixed in DAN + Partnership dispatchers** (2026-08-20) | Audit found `LT - DAN Campaign Sender Release Dispatcher` (`toUG1yPDmFG48KEP`) and `LT - Partnership Email Dispatcher` (`Xshck23cKo1yXL9D`) had the identical `mode: runOnceForAllItems` + `$json` bug in their `Build SQL - Write Release Log` nodes. **Partnership was actively manifesting**: run `766371` (2026-08-19) sent 3 step-4 emails but logged only 1 (robert@herb.co), leaving the other 2 contacts unlogged for their step → duplicate re-send risk. DAN was dormant (pool exhausted, no log entries since 07-22). Fixed both with the same `$input.all()` iteration + `queryBatching: "independently"` on the Postgres node. Published: Partnership `2663f32b-4e45-4a5c-9b7f-e9db58ff9bc4`, DAN `f8f29288-45d9-4f35-81a6-a60d2b54ad11` (both `versionId == activeVersionId`). Functional test (`test_workflow` execution `769961`) confirmed 3 sent items → 3 release-log writes; the 3 test rows written to the live `partnership_release_log` were deleted afterward (total restored to 188). |
| **August 2026 Emerald contact enrollment reconciled** (2026-08-26) | Reconciled 2,620 cleaned Brand/Agency/Dispensary rows against live GHL. The bounded reconciliation created 36 genuinely new email-only contacts and completed 319 contact-level repair groups representing 325 tag assignments: 313 Emerald MSO queue enrollments plus six Dispensary pool and six DAN queue assignments. Final dry run returned 0 unmatched rows and 0 pending tag actions. Five AURI emails were identified as additional emails on existing contact `Amy Lund` and intentionally skipped; `scripts/emerald/reconcile_august_2026_emerald_live.ps1` now prevents retrying them. Details: `docs/sessions/2026-08-26-august-emerald-contact-enrollment.md`. |
| **August 2026 partnership contact enrollment** (2026-08-27) | Reconciled the August 26 partnership CSVs as 431 people / 429 unique emails. Created 404 new GHL contacts and enrolled 427 actionable contacts with both `partner_candidate_email` and `partner_candidate_linkedin`; added `august_26_partnership_contact` to the 404 new contacts. Three existing contacts received missing LinkedIn URLs. Four rows across two shared-email groups were skipped for manual resolution. No Vapi selector tags were applied. Details: `docs/sessions/2026-08-27-august-partnership-contact-enrollment.md`. |

### Resolution

The runner now uses an isolated npm-installed `pg@8.21.0` tree at `/opt/pg-node_modules`. `NODE_PATH` is configured in both the container environment and `n8n-task-runners.json`; the runner is rebuilt by `scripts/deploy/deploy_runner.py`. Direct runner verification returns `typeof require('pg').Client === 'function'`. The n8n container must use the persisted Coolify encryption key, not the earlier local/reference key. The live container was recreated with the persisted key and credential decryption errors stopped.

### Executive Report Recovery: 2026-08-12

- The report host and n8n are attached to `coolify-shared`; n8n has the network alias `n8n`.
- `reports/nginx.conf` proxies the Executive Summary, campaign-channel summary, and outgoing-call endpoints directly to `http://n8n:5678`.
- `https://reports.livetransparent.com/api/report/executive/summary?range=30d` now returns HTTP 200 with a real approximately 33 KB JSON payload.
- Executive Report build `2026-08-17-v26-social-reporting-accuracy` resolves raw pipeline/stage IDs, uses exact completed-day ranges, exposes LinkedIn and Instagram ledger metrics, labels Social Planner rows as platform placements, and renders unavailable account statistics as N/A. Desktop and 390px mobile verification found no raw IDs or page-level horizontal overflow.
- The empty-body/zero-metric symptom was caused by the reports proxy reaching n8n while report workflow Postgres credentials failed to decrypt. The running container used `WJR...`; Coolify's persisted service `.env` used `ffff...`. The container was recreated from the persisted value.
- Do not rotate or replace `N8N_ENCRYPTION_KEY` casually. A mismatch makes existing n8n credentials unreadable. Back up the service `.env` before changing it.

### Current Runner Caveat

- Some older n8n logs contain `Module .../pg@8.21.0... is disallowed`. The effective config uses `NODE_FUNCTION_ALLOW_EXTERNAL=*`, and the real affected Code-node path succeeded in GHL Leads Ingest execution `742843`. Treat new warnings as actionable only when tied to a reproducible failing workflow.

### Remaining Follow-up

1. **High**: 1,229 unmatched `ghl_contact_id` rows in `emerging_pool_contacts` — contacts not in GHL export CSVs. Decide: skip, manual GHL lookup, or re-export with broader filter.
2. **High**: migrate embedded secrets to Config nodes (Community Edition cannot use env vars in Code nodes). Priority: GHL PIT (8+ workflows) → Unipile (5+ workflows) → Vapi (2 workflows) → Postgres credentials → webhook secrets. Then rotate exposed values.
3. **High**: recover campaign/reporting state deliberately — `Email_Events`, release logs, LinkedIn state, and SimpleTexting state will populate through live workflow activity. Do NOT fabricate historical data. **Progress 2026-08-20**: Emerald/DAN/Partnership release logs are flowing again after the release-log write fix; 73 `apollo_august2026` contacts were enrolled into Emerald Executives MSO.
4. **Medium**: Warm intake authentication review — `5nYzp9DgQUopzWhR`, `OowP3sAd8c9paSKf`, and `SmMf8QIfysuxQJbG` have empty shared-secret configuration. SimpleTexting send/callback boundaries were hardened on 2026-08-17.
5. **Medium**: add OAuth-backed social statistics for reach/impressions/saves; complete native GHL report UI widgets.
6. **Low**: monitor migrated voice dialer next scheduled execution; clean legacy artifacts after live paths are stable.

### Known Issues Still Unresolved

- **`report_raw_ghl_contacts`** verified (500 rows); **`report_raw_ghl_opportunities`** verified (7,984 rows via execution `743094`)
- **Live post-recovery baseline**: `report_raw_ghl_contacts=500`, `report_raw_ghl_opportunities=7984`, `voice_call_queue=3` pending, `voice_call_attempt=0`, `report_raw_ghl_call_outcomes=0`, `Email_Events=0`, DAN/Emerald/partnership release logs `=0`, main LinkedIn state `=0`, partnership LinkedIn state `=18`, SimpleTexting campaign state/events `=0`. **Updated 2026-08-20**: `Emerald_Release_Log=16,154` (incl. 73 `apollo_august2026` executives_mso + 58 backfilled), `partnership_release_log=188`, `DAN_Release_Log=4,664` (dormant since 07-22)
- **`emerging_pool_contacts.ghl_contact_id`** needs audited backfill (`12,639/13,868` currently populated; 1,229 null — not in GHL exports)
- **Call Outcome Ingest** now requires `X-LT-Call-Outcome-Secret` header (secret in Config node of `PUCfTZBANSPcgS0c`)
- **Call Outcome caller auth fix (2026-08-13)**: GHL automation `LT - Call Outcome to Report` (`2152ba2b-0b9d-4645-aba4-44cc818a1789`) was sending Call Details webhooks to `https://automations.livetransparent.com/webhook/lt-call-outcome-ingest` without the required header. Its Webhook action now includes `X-LT-Call-Outcome-Secret` with the value stored in the n8n Config node, was saved, and was confirmed published in the GHL advanced canvas. Do not weaken the n8n validation or expose the secret in documentation. No live Vapi call was placed during verification.
- **Warm intake boundaries** still need authentication review; SimpleTexting send and provider callback boundaries are protected

### Key Files

- Runner Dockerfile: `n8n/runners/Dockerfile`
- Runner config: `n8n/runners/n8n-task-runners.json`
- n8n docker-compose: `n8n/docker-compose.yml`
- VPS scripts: `scripts/utilities/vapi_audit.py`

## IMPORTANT — Read This First

Analyze the attached `repomix-output.md` file. It contains the core system architecture, code blueprints, and operational roadmaps for my LiveTransparent automation environment. Review custom script setups (like `fix_intake_poller.js`) to understand how my infrastructure is organized.

**LLM context-loading order:**
1. `repomix-output.md` — start here for architecture, blueprints, and roadmaps
2. `AGENTS.md` (this file) — short operating guide
3. `Project Status and Next Steps.md` — current priorities and live-state
4. `Project Specifications.md` — system boundaries, guardrails, contracts
5. `plan.md` + sub-plans — active work plan
6. Custom scripts — infrastructure specifics
7. All other repo files — only when a task requires fine detail

> **Source of Truth**: Live n8n (via `n8n-lt` MCP) is the single source of truth for all workflow state. Repo files (`.ts`, `.json`, `Backup of all n8n workflows/`) may be outdated snapshots. Always `get_workflow_details` or `search_workflows` to read current state before editing.

> **Historical traceability**: Detailed fix narratives, root-cause analyses, and execution histories from 2026-06 onward are preserved in git history. This file contains only the current operating guide and critical patterns.

## Canonical Status

- Use [Project Status and Next Steps.md](./Project%20Status%20and%20Next%20Steps.md) for current priorities and live-state details.
- For the 2026-08-12 report recovery and session continuation order, read [docs/handoff/2026-08-12-report-recovery.md](./docs/handoff/2026-08-12-report-recovery.md).
- For the 2026-08-14 company Instagram-page DM implementation, read [docs/sessions/2026-08-14-company-instagram-page-dm-handoff.md](./docs/sessions/2026-08-14-company-instagram-page-dm-handoff.md).
- For the 2026-08-19 LinkedIn double-escape corruption fix (timeline, root cause, published versions), read [docs/sessions/2026-08-19-linkedin-double-escape-fix.md](./docs/sessions/2026-08-19-linkedin-double-escape-fix.md).
- This file is the short operating guide: keep it current, but avoid duplicating long planning material here.

### Documentation Review Session (2026-08-12)

Full cross-file review of AGENTS.md, plan.md, Project Status and Next Steps.md, and docs/handoff/2026-08-12-report-recovery.md. Fixed 18 issues across 4 files:

**Security (CRITICAL)**: Redacted 3 exposed secrets — Apollo webhook key, Apollo API key, and Call Outcome secret — from AGENTS.md, Project Status.md, and handoff document. All replaced with `<see .env>` or `stored in Config node` placeholders.

**Stale data (HIGH)**: Updated `ghl_contact_id` from `0/13,868` to `13,755/13,868` across 4 files (AGENTS.md, plan.md, Project Status.md, handoff). Updated plan.md Data Pipeline Status to reflect post-recovery baseline (opportunities=7,984, pipeline_history=7,984, voice_call_queue=3). Marked Sales Ingest repair and Call Outcome auth as DONE in plan.md Follow-up and Next Agent sections. Fixed plan.md Current blockers to remove stale Sales Ingest HTTP 401 reference.

**Contradictions (HIGH)**: Fixed SimpleTexting Step Runner/Phone Backfill/Warmup/Pool Dispatcher status in AGENTS.md from "active and published" to "passed smoke executions but remain unpublished" (matches Project Status.md). Fixed DAN dispatcher candidateLimit from 65 to 85 in Project Status.md (matches AGENTS.md 2026-07-21 change). Fixed Partnership dispatchers from "dry-run" to "Active" in AGENTS.md (outbound activated 2026-07-31). Fixed Partnership header from "Outbound Dry-Run" to "Outbound Live".

**Consistency (MEDIUM)**: Fixed Reply Backfill version ID `462e`→`4620` in AGENTS.md (matching canonical Project Status.md). Fixed plan.md implementation order indentation. Strengthened Emerald HTTP wrapper warning from "should" to "must" migrate.

**Next session**: `repomix-output.md` was regenerated via `packlive` at end of this session. It now reflects all fixes above.

## Environment

- Deployed via Coolify on a VPS.
- Public hosts: `automations.livetransparent.com` for n8n and `reports.livetransparent.com` for the report host.
- Prefer Coolify internal service-to-service calls when possible.
- n8n target version: `2.33.3` (native Schedule Trigger is the scheduling standard; do not add OS/Coolify cron jobs for workflows).
- Canonical MCP: `n8n-lt`.
- Root `.env` is the reference copy; Coolify env vars are the deployed source of truth.

### Business Timezone vs Operator Timezone

- The operator may access GHL from Manila (`Asia/Manila`), but LiveTransparent business operations are pinned to `America/Los_Angeles`.
- Interpret Cameron's calendar availability, GHL appointment dates/times, reminders, campaign schedules, report windows, and business-hours guards in `America/Los_Angeles` unless a task explicitly requests another timezone.
- Never treat a Manila-rendered GHL UI timestamp as the business-local timestamp without converting it to `America/Los_Angeles` and checking the underlying timezone metadata.
- Booking pages and confirmation copy must display or clearly state Pacific Time; a widget defaulting to Manila is a configuration/UX issue, not evidence that the business operates on Manila time.

### n8n Community Edition Constraint

**n8n Community Edition does NOT support environment variables inside Code nodes or workflow expressions.** The `N8N_BLOCK_ENV_ACCESS_IN_NODE` setting blocks `$env.*` access in Code nodes. This is a hard platform limitation, not a configuration choice.

**Canonical pattern for workflow-scoped configuration:**
- Each workflow that needs API keys, secrets, or configuration values uses exactly one **Set node named `Config`** (type `n8n-nodes-base.set`, version 3.4).
- The Config node stores all workflow-scoped values as named assignments (e.g., `ghlApiKey`, `unipileApiKey`, `stateUpsertSecret`, `vapiApiKey`, `pgPassword`).
- Code nodes read these values via `$node['Config'].json.ghlApiKey` (or `$('Config').item.json.ghlApiKey`).
- HTTP Request nodes reference them via `={{ $node['Config'].json.ghlApiKey }}` in header/body expressions.
- Config nodes are **operational storage**, not equivalent to managed n8n credentials. They store secrets in plaintext in the workflow definition. Keep access restricted.

**What Config nodes replace:**
- `$env.GHL_API_KEY` → `Config.ghlApiKey`
- `$env.VAPI_API_KEY` → `Config.vapiApiKey`
- `$env.UNIPILE_API_KEY` → `Config.unipileApiKey`
- `$env.POSTGRES_PASSWORD` → `Config.pgPassword`
- Hardcoded API key literals in Code node jsCode → Config assignment

**What remains as managed credentials (preferred when available):**
- n8n `httpHeaderAuth` credentials for webhook authentication
- n8n `postgres` credentials (when the Postgres v2 node bug is resolved)
- n8n OAuth2 credentials (when implemented)

**Migration priority for embedded secrets:**
1. GHL PIT token → Config node in each of 8+ workflows (already done in some; complete the rest)
2. Vapi API key → Config node in dialer and callback workflows
3. Unipile API key → Config node in all LinkedIn/Instagram workflows
4. Postgres credentials → Config node in direct-`pg` Code nodes (already done in some)
5. Webhook secrets → Config node (already done for state-upsert, call-outcome, voice-queue)
6. GHL OAuth client credentials → migrate to n8n OAuth2 credential when available

### Reporting Execution Contract (2026-07-31)

- The spreadsheet at `1AbLdIhQiEoJhdx3l6yeAppNxbYbAIYhcZfoKhy68VZw` is the requirements reference for the MQL, email, LinkedIn, and social report layout.
- Native GHL Custom Report: `6a67dce4a51a4360c60963a3`. Use it for CRM contacts/opportunities, MQL detail, pipeline, email, SMS, calls, appointments, and custom-metric rates.
- Native GHL Social Planner is the source for Facebook, Instagram, and LinkedIn Page post analytics. LinkedIn personal-profile analytics are not supported by the platform API.
- Keep Brands-versus-Dispensaries joins, Unipile LinkedIn DM state, Vapi campaign state, trigger-link detail, and cross-channel comparison in the Executive Report unless the underlying data is intentionally synchronized into GHL objects.
- The Executive Report accepts `range=7d|30d|90d|custom` plus `from=YYYY-MM-DD` and `to=YYYY-MM-DD`. For every selected period it loads the immediately preceding equal-length period and shows current value, prior value, absolute change, and percentage change.
- Reporting weeks use the report API's returned date window and the sub-account reporting timezone. Do not mix widget-level date overrides with the shared selected-period comparison unless the metric definition explicitly requires it.
- Campaign summary workflow: `LT - Report Campaign Channel Summary` (`MvPLbUAN9IIQikxb`) is active and published. Its selected-window endpoint is `/webhook/lt-report-campaign-channel-summary`.
- Campaign summary active version `d65e2845-660a-40ca-88f4-d39445b87403` returns named channel/campaign rows plus `linkedin_invites`/`linkedin_accepted` columns. DAN uses release-log campaign fields, Emerald uses bucket/enrollment data, SMS uses `SimpleTexting_Campaign_Event_Log.campaign_key`, LinkedIn uses `linkedin_activity_events` joined to `emerging_pool_contacts.source_list` with `campaign_type`/`source_key = 'partnership'` routing, and Vapi uses queue campaign IDs. The response-shaping node now derives separate `DAN`, `Emerald`, `Partnership`, `Vapi Brand`, and `Vapi Dispensary` aggregates from channel rows, so Vapi is no longer incorrectly rolled into DAN.
- The Executive Report is live at `https://reports.livetransparent.com` as build `2026-08-17-v26-social-reporting-accuracy`; it includes campaign/channel filters, separate Vapi filters, campaign drill-downs, comparison view, campaign opportunity counts, LinkedIn and Instagram activity columns, selected-period controls, prior-period comparison, resolved GHL stage names, responsive table containment, and explicit post-ledger versus account-statistics coverage.
- The Executive Report also includes a bottom `Outgoing Call Detail` table. It calls `/api/report/executive/outgoing-calls`, which nginx proxies to `GET /webhook/lt-report-outgoing-calls` from active workflow `LT - Report Outgoing Calls Detail` (`VXFHc8IrF9DDEEdj`). The endpoint is fixed to the seven most recent completed `America/Los_Angeles` days, paginates at 100 rows, and reads `voice_call_attempt` joined to `voice_call_queue`.
- Partnership LinkedIn reply recovery (2026-08-12): Campaign Channels now reports 3 verified Partnership replies. Jaret Christopher was already present; David Schachter (`rvWEW2K2WYeQ7v6zypDdZQ`, 2026-08-10) and Gretchen Gailey (`8UF3lxibUmKYaG87h1F5Pg`, 2026-08-06) were recovered from the Unipile API with their original timestamps and inserted idempotently into `linkedin_activity_events`. `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`) is published on `f96dafba-9818-4aab-8656-c2e4e2ab8480` with a malformed form-payload fallback so unescaped Unipile JSON no longer loses critical inbound fields. **2026-09-10/11 fixes (E2E verified)**: (1) Endpoint corrected from `/conversations/messages` to `/conversations/messages/inbound` (the `/inbound` suffix is required for posting inbound messages). (2) `resolveWithFullResponse` is silently ignored by `this.helpers.httpRequest` — use `returnFullResponse: true` (returns `{body, headers, statusCode, statusMessage}`); the old option made every successful post read as `inbound_failed: status=undefined body={}`. (3) All `Build * SQL` Code nodes in that workflow must NOT double backslashes inside `'...'::jsonb` literals (`esc()` keeps only `'` → `''`; backslash doubling made any payload containing an embedded quote crash `Upsert LinkedIn Map` with "invalid input syntax for type json" and blocked `linkedin_conversation_map` persistence). **2026-09-25 revert:** The Sales Navigator exclusion (`if (payload.linkedin_feature === 'sales_navigator') return ...sales_navigator_recruiting_exclusion`) was added 2026-09-24 17:01 UTC and reverted 2026-09-25 18:30 UTC. The `normalizedFeature` classification was also removed from `Normalize Unipile Message Event`. All LinkedIn DMs including Sales Navigator are now accepted and contacts are created. Current published version `ec870256-8946-4ff6-be46-e55eab4710b7` (`versionId == activeVersionId`). Correct GHL API flow: POST `/oauth/locationToken` with `{companyId, locationId}` using `Authorization: Bearer <oauth access_token from Postgres ghl_oauth_tokens>` (the PIT returns 401/403 there) to get `access_token`, then use that as Bearer for `POST /conversations/messages/inbound` (inbound) or `POST /conversations/messages` (outbound mirroring) with body `{"type":"Custom","contactId":"<ghl_contact_id>","message":"<text>","conversationProviderId":"6a58a14ff3023bea3783c152","altId":"<chat_id>","date":"<ISO ts>"}`. Gretchen Gailey's two historical outbound messages were backfilled successfully via `/conversations/messages` (the nonexistent `/conversations/messages/outbound` direction path caused the original 422s); the inactive `LT - LinkedIn Conversation Backfill` (`JUvrA7qMa24SwAZG`) now has conversation-message dedup and a Config `only_chat_id` (currently Gretchen's chat `8NOmhtWSUpKbsec3YdsxlA` — clear before broader backfill). Local python scripts calling GHL need a browser `User-Agent` (Cloudflare 1010 blocks python-urllib).
- On 2026-08-08 the live reports container was missing the repository nginx proxy route for `/api/report/executive/outgoing-calls`; the route was copied into `reports-livetransparent`, `nginx -t` passed, nginx was reloaded, and the proxy now returns the healthy n8n endpoint response.
- Campaign summary active version `1cea3b9c-d587-4135-806d-46d301e2c7f4` now counts SimpleTexting `sent_step_1` through `sent_step_4` events and exposes a selected-window `smsSummary` with sent, `delivery_failed`, reply, and normalized failure-reason counts. The Executive Report displays this as the SMS delivery summary; the verified 2026-07-09 through 2026-08-07 window returned 294 sent, 1,095 failed, and 0 replies. Failure reasons were `simpletext_provider_failed` (1,010), `duplicate_send` (63), `unknown` (16), `invalid_phone` (5), and `idempotent_webhook_error` (1).
- **Newsletter reporting (2026-08-24)**: the Campaign Channel Summary (`MvPLbUAN9IIQikxb`, active `2b8608aa-86e3-466f-9347-2ceb6f0b6818`) returns a `Newsletter` campaign channel row (sent/opened/clicked from `newsletter_send_log` + `newsletter_events` mapped into the existing `email_*` columns, grouped as `Newsletter`). The Executive Summary (`Bukc0mgOD2r7V6ED`) folds newsletter sends into `emailsSent` and newsletter opened/clicked/unsubscribed into `emailsOpened`/`emailsClicked`/`emailsUnsubscribed`, and newsletter `failed` rows into a new top-level `newsletterFailed` metric. Because the reports window defaults to ending yesterday, newsletter data only appears when the window includes the send day. The dispatcher sets `sent_at` on `failed` rows too so the failure metric is window-able.
- The same campaign summary response now includes distinct selected-window opportunity counts matched from current contact campaign tags in `report_raw_ghl_opportunities`. The Executive Report displays these in campaign rows, detail cards, and comparison view. The verified window returned Emerald 3,909, Partnership 8, and Vapi Brand 13; DAN and Vapi Dispensary had zero matched opportunities.
- The root `GHL_PIT` was directly verified against the official REST location and contacts endpoints on 2026-07-31; both returned HTTP 200 with the required Bearer/Version headers. The native GHL report `6a67dce4a51a4360c60963a3` was also verified in an authenticated GHL UI session: it supports editing. Its `Campaign Opportunities` widget is filtered to `Partnership Pipeline`, its `Contacts by tag` widget uses `Tags -> Is one of` with `partner_candidate_email` and `partner_candidate_linkedin`, its saved date range is now `Last 30 days`, and the duplicate page-3 outgoing-call widget was removed.
- The official GHL API/SDK does not expose Custom Report widget-layout mutation. Do not guess undocumented report-builder endpoints; native widget changes require authenticated GHL UI access or an explicitly approved internal API path.
- **GHL Native Report Audit (2026-08-08)**: Report `6a67dce4a51a4360c60963a3` ("New LiveTransparent Reporting") was reviewed against live data. The authenticated report editor is now reachable at the documented URL; its saved date range was changed from `Last week` to `Last 30 days` on 2026-08-08. Findings:
  - **1 Partnership Pipeline opportunity exists** (Strider Peterson, created Aug 4, assigned to Janvi, stage "New Partner Lead"). It falls outside the "Last week" window — change to "Last 30 days" to include it.
  - **Duplicate widget**: "Outgoing calls by status" appeared identically on pages 2 and 3 (319 calls, same data). It was deleted from page 3 and saved on 2026-08-08.
  - **Missing pipeline widgets**: Stage Distribution on page 3 only shows Sales pipeline. Add separate Stage Distribution widgets for Sales Outreach (`dhdlf3O4tymxFtHk4aqq`) and Warm (`FRjpDZ1HWj3UPgczsu3t`) pipelines. The Partnership Pipeline widget already exists on page 1.
  - **Missing campaign tag widgets**: Only Partnership tags are widget-tracked. Add "Contacts counts by tags" widgets for DAN (`seq enrolled - dan`, `dan_seq_replied_or_booked`, `dan_seq_completed`), Emerald (`seq emerald`, `seq enrolled - emerald`), and Vapi (`vapi_campaign_brand`, `vapi_campaign_dispensary`) tags.
  - **Missing email widgets**: "Replied emails", "Soft bounced emails", and "Emails by domain" are available in GHL but not used. Add them to page 2.
  - **Pages untitled**: All 3 content pages are "Untitled page". Rename to: Page 1 "Pipeline Overview", Page 2 "Campaigns & Outreach", Page 3 "Communications Detail".
  - **Custom metrics unused**: GHL supports custom metrics (e.g., email open rate, campaign conversion rate). Create at least the open-rate and click-rate custom metrics for cross-filtering.
  - **GHL CANNOT do**: LinkedIn metrics, Vapi campaign outcomes, email attribution by source tag, cross-channel comparison, release-log data. These remain in the Executive Report only.
  - **Available widget counts per category**: Opportunities (17), Emails (11), SMS (5), Calls (13), Contacts (17), Social Planner (18), Appointments (15), Conversations (16), Payments (17), General (15).
- Never commit GHL PITs, Firebase signed URLs, OAuth tokens, or captured response artifacts containing credentials. Use environment placeholders in documentation and leave sensitive captures untracked.

### Ingest and LinkedIn Hardening (2026-07-31)

- `LT - GA4 Daily Ingest` (`6pCSGzFmrMDFL5Yq`) is published on `8f4c63ea-dd33-4c7f-93a5-b3cbb5c8e7fa`. Empty responses finalize as `empty`; malformed data is `partial`; fetch failures finalize run/health state, do not advance the watermark, and then fail the execution. Verification: success `276731`, pinned failure `276747`.
- `LT - GHL Daily Sales Ingest` (`aYT5oHcgmBALzHy5`) is published on `4f3e8068-8864-4b4d-9286-ba4d618cc3a8`. Snapshot/history rows use ingest date, raw rows preserve source timestamps, retries/cursor guards are bounded, finalization errors fail closed, and sales health uses `ghl_opportunities` while raw compatibility remains `source_system = 'ghl'`. Verification: execution `276626` processed 7,683 opportunities and 7,683 history rows.
- `LT - LinkedIn Connection State Sync (Unipile)` (`ceaKnz6E3onQrZpt`) is published on `fa1a5dfe-d00c-47b3-98d3-862ea6f912a7`. It uses direct `this.helpers.httpRequest`, bounded contact/API budgets, retry/timeouts, explicit error reporting, and terminal/reply-state preservation.
- `LT - GHL LinkedIn Connect Dispatcher` (`fXxw5lanZcDmUrst`) is published on `bd385c89-0678-4301-84e6-abc63fea3c28`. It reads Config explicitly, atomically claims `ready` rows as `requested_pending`, and performs live suppression/reply checks before invites. Do not manually execute it without explicit approval because it can send LinkedIn invites.
- `LT - LinkedIn Connection State Upsert` (`Old7ZvyVYgFaJgDr`) is published on `d9168bbc-9c96-44fd-a356-12e645a2ec3d`; its webhook requires the protected `X-LT-LinkedIn-State-Secret` header. All discovered callers, including the partnership dispatcher/DM path, were updated and published. Unauthorized requests return `403`; malformed authorized requests reach the workflow and fail validation without a state write.
- Community Edition variable convention: each relevant LinkedIn state-upsert workflow has exactly one `Config` node. Workflow-scoped values such as `stateUpsertSecret` live there and Code nodes read them from Config instead of embedding request literals. Config nodes are operational storage, not equivalent to managed credentials; keep access restricted and migrate to credentialed HTTP Request nodes when possible.

## Working Rules

### Company Instagram Page Outreach (2026-08-18)

The company-page Instagram DM delivery pipeline is LIVE. The sender `LT - Instagram Company Page Partnership Sender` (`IeovbYnhCsetXS89`) is active and published (dryRun=false), Mon-Fri 10:00-15:00 America/Los_Angeles, 45/day cap, 10/hour. It reads `instagram_company_dm_state` and sends via Unipile account `F2UprZ8aQc6Qm9CYYWU6cg`. Do not republish `LT - Instagram DM Sequence (Unipile)` (`iCnY6ccdHhfJg3sf`): it used the LinkedIn account and old `instagram_dm_state` model.

**Send priority (2026-08-18):** `campaign_priority` in `instagram_company_dm_state` is `dan_brands`=1, `dan_dispensaries`=2, `partnerships`=3. Brands go first, then Dispensaries, then Partnerships. The 379 state rows are 245 Brands, 58 Dispensaries, 76 Partnerships.

**Message strategy:** Message 2 is now enabled in the live sender (published version `3d721cec-04e6-45cc-9ebb-fb21589b61a6`). It selects `message_step = 1`, waits two business days after Message 1, sends the approved campaign-specific Message 2 copy, and advances state/log idempotently to step 2. Message 3 remains disabled. Do not manually execute the live sender without explicit approval.

**Current state:** 45 Partnerships received Message 1 on 2026-08-17 (before the priority change). The remaining Partnerships and all Brands/Dispensaries are pending Message 1. Unipile key tested OK on 2026-08-18.

**IG/FB enrichment status:** `brand_pool - IG & FB` enrichment is COMPLETE (workflow `BIVAw1AWTTzC0igW` unpublished; last run found 0 unresolved). Dispensary (`Qd7sn9MPq4W24WKi`) and Partnership (`RlogFNDYjtjkuRFJ`) enrichment remain active on a 5-minute schedule; they were temporarily blocked by an OpenRouter weekly key limit that the user fixed on 2026-08-18.

**Contract (from 2026-08-14):** audience selectors `brands_pool`, `dispensaries_pool`, `partner_candidate_email`/`partner_candidate_linkedin`. Existing contact-level Instagram fields are protected; create separate company-level fields (`Company Instagram Username`, `Company Instagram Profile URL`, `Company Instagram Profile Provider ID`, `Company Instagram Chat Attendee ID`, `Company Instagram Chat ID`, `Company Facebook Page URL`, `Company Facebook Page ID`, `Company Facebook Messenger PSID`). Deduplicate by normalized company Instagram handle; retain associated GHL contact IDs plus a primary attribution contact in Postgres. Use direct `require('pg')` transactions for writes. Any prior reply/suppression from any associated contact stops the sequence; identity/reply-check errors fail closed. Cadence: Message 1 first eligible weekday, Messages 2-3 two business days apart, never weekends. No lifecycle tags. Full history in `docs/sessions/2026-08-14-company-instagram-page-dm-handoff.md` and `docs/sessions/2026-08-18-instagram-company-page-dm-priority.md`. Do not manually execute live validation sends without explicit approval.

- Check the live state before and after every mutation.
- Fetch first, patch second.
- After every mutation via `update_workflow`, verify the workflow is both **updated AND published**: compare `versionId` vs `activeVersionId` from `get_workflow_details`. If they differ, call `publish_workflow` to activate the draft. The `update_workflow` MCP tool does NOT auto-publish.
- Preserve n8n graph integrity: keep node IDs and connection maps aligned.
- Use `Switch` over `IF` for voice automations.
- Prefer raw JSON import for dialer patches.
- Use `={{ ... }}` expressions with `$('Node').item.json.field`.
- Prefer runbooks in `GHL Live Transparent CRM/` before changing GHL/n8n workflows.
- Website demo bookings must use the direct GHL Regulated Ads booking widget. Do not route website visitors through the legacy hero form or Calendly embed first.
- Use `Config` nodes only when env or credential access is blocked.
- LinkedIn outbound senders must fail closed on reply/inbound lookup errors. A failed reply check is a skip, not a send.
- For any "stop LinkedIn DMs" request, suppress the contact in both places: add `linkedin_dm_sequence_completed` in GHL and mark the shared `linkedin_connection_state` row terminal (`connection_status = completed`, `sequence_step >= 4`, `dm_sequence_status = completed`/`dm_conversation_status = active` as applicable). The GHL tag alone is not enough because the live LinkedIn send paths select from shared state.
- LinkedIn DM sequences must mark terminal contacts with `linkedin_dm_sequence_completed` and stop reselecting step-4 rows; the queue source is `LT - LinkedIn Connection State Sync (Unipile)` and the GHL connect dispatcher feeds 20 contacts at a time when healthy.

### Follow-up Sender Routing Handoff (2026-07-29)

- User requirement: follow-up email From Name and From Email must follow the opportunity/contact owner; if neither has an owner, default to Jason.
- Affected GHL workflow: `Jason Followup Emails and SMS` (`f6b44e34-779e-4959-b41d-b05641f134e7`), published version 39. Triggers on opportunity stage entry into Sales Outreach: New (`3529dd3d`), Attempting Contact 1st Attempt (`b97e42b1`), 2nd Attempt (`c46c3be3`), 3rd Attempt (`c8b7a450`), Engaged (`9ced8010`).
- Six affected templates are in folder `Jason Follow Up Emails` (`69e0c9069af5986541802d88`) and currently have literal Jason sender defaults. Do not mistake those defaults for the final owner-routing implementation. One template (`69e0dcad8ffabf47b4d987c5`, "Cannabis Ads: Next Steps") is reused by 2 of the 7 email actions. Template signatures use `{{user.email_signature}}` (dynamic).
- The workflow also sends 14 SMS follow-ups via SimpleTexting webhook using legacy compatibility aliases; these messages are not owner-routed.
- Current live artifact check: published version 39 has Jason workflow defaults (`Jason from Transparent eCom`, `jason@livetransparent.com`) confirmed via `senderAddress` in the API response. All 7 Send Email actions retain owner-driven sender fields: `{{opportunity.owner}} from Transparent eCom` and `{{user.email}}`. The three-layer defense is: (1) action-level merge fields resolve to owner, (2) template-level literal Jason values backstop if merge fields fail, (3) workflow-level `senderAddress` defaults backstop if both above fail.
- Remaining GHL work: none for sender routing. Do not send a live test email unless explicitly requested. **Marc routing path is untested in production** — as of 2026-07-30, zero Marc-owned (`sqGx5rp3oAUG610NXyjU`) opportunities exist in any of the 5 trigger stages; all Marc-owned opportunities are in the Qualified stage and have not yet entered a stage that fires this workflow.
- Public GHL APIs cannot write workflow action definitions. The template PATCH API rejects `{{user.email}}` as `fromEmail`; do not attempt to solve owner routing by putting merge fields into template sender metadata.
- Authenticated browser access was used to set and publish the workflow defaults. The published version 39 response confirms `senderAddress` and `status: published`.

### LinkedIn DM Suppression — Production Automation

**Primary path (GHL UI)**: Adding the tag `stop_linkedin_dms` to any contact in GHL triggers the automated suppression pipeline. No code access needed.

```
GHL tag "stop_linkedin_dms" added
  → GHL automation "WL - Stop LinkedIn DMs" fires
    → POST https://automations.livetransparent.com/webhook/lt-linkedin-suppress-dms
      → n8n workflow: LT - LinkedIn DM Suppression from GHL Tag (IPN8jnR3XSurX0o1)
        1. Scans webhook body for LinkedIn URL (any key containing "linkedin", nested customData, customFields)
        2. Falls back to GET /contacts/{id} if no URL in webhook
        3. Falls back to Unipile name search as last resort
        4. Adds linkedin_dm_sequence_completed tag via GHL API
        5. Upserts linkedin_connection_state (completed, step=4) for real contact
        6. Upserts linkedin_connection_state (completed, step=4) for synthetic linkedin:follower:{providerId}
```

**GHL automation setup:**
| Setting | Value |
|---------|-------|
| Name | WL - Stop LinkedIn DMs |
| Trigger | Tag Added → `stop_linkedin_dms` |
| Action | Webhook POST to `https://automations.livetransparent.com/webhook/lt-linkedin-suppress-dms` |
| Custom Body | `{"contact_id":"{{contact.id}}","first_name":"{{contact.firstName}}","last_name":"{{contact.lastName}}","linkedin_url":"{{contact.customField.apollo_person_linkedin_url}}"}` |

**Suppression verified across all 3 LinkedIn send paths (2026-07-15 audit):**
| Send Path | How it's blocked |
|-----------|-----------------|
| DM Sequence (d0tEtijajisIsYcs) | SQL `WHERE connection_status = 'connected'` + `dm_conversation_status <> 'active'` |
| Follower DM (pq7XVajNFnnwMUTr) | Code `sequence_step >= 1` + `dm_conversation_status === 'active'` |
| Dispatcher (fXxw5lanZcDmUrst) | SQL `WHERE connection_status = 'ready'` + GHL tag block `linkedin_dm_sequence_completed` |

### LinkedIn DM Suppression Runbook (Manual/CLI)

When the user asks to stop DMs for a contact, preferred path is the GHL tag above. If CLI is needed:

```bash
python local-scripts/suppress_linkedin_dms.py "<name or LinkedIn URL>"
```

This single command handles everything:
1. Resolves the LinkedIn profile via Unipile (by URL or name search)
2. Finds the GHL contact if one exists
3. Adds `linkedin_dm_sequence_completed` tag in GHL (when a GHL contact is found)
4. Upserts `linkedin_connection_state` rows (both real GHL contact ID and synthetic `linkedin:follower:{providerId}`) to terminal:
   - `connection_status` = `completed`
   - `sequence_step` = 4
   - `dm_sequence_status` = `completed`, `dm_conversation_status` = `active`

If the script isn't available, POST directly to the suppression webhook or state upsert webhook:

**Path A — Suppression webhook** (does everything — tag + state table):
POST to `https://automations.livetransparent.com/webhook/lt-linkedin-suppress-dms` with `{"contact_id":"...","first_name":"...","last_name":"..."}`

**Path B — State table only** (tag separately via GHL UI):
POST to `https://automations.livetransparent.com/webhook/lt-linkedin-connection-state-upsert`:
```json
{
  "ghl_contact_id": "<contact_id>",
  "location_id": "Zwz4relUXVPxx8uohnjV",
  "unipile_account_id": "V9eiHiDpRmCtan0YNdzsQw",
  "linkedin_profile_url": "https://www.linkedin.com/in/<identifier>/",
  "linkedin_public_identifier": "<identifier>",
  "linkedin_provider_id": "<provider_id>",
  "connection_status": "completed",
  "sequence_step": 4,
  "source_workflow_name": "manual_suppression",
  "source_key": "manual:suppress:<identifier>",
  "payload_json": {
    "dm_sequence_status": "completed",
    "dm_conversation_status": "active"
  },
  "metadata_json": {
    "source": "manual_suppression",
    "reason": "user_requested_stop_DMs"
  }
}
```
4. Also upsert with `ghl_contact_id` = `linkedin:follower:<provider_id>` if the real GHL contact wasn't found (covers the Follower DM path).

## Tooling

- Prefer `n8n-lt` MCP or direct API calls before browser workflows.
- GHL MCP: primary `ghl_official`, secondary `ghl_katwill_*`.
- Codex config: `C:\Users\edmon\.codex\config.toml`.
- **Avoid `n8n-lt` `updateNodeParameters` for Set v3.4 nodes.** It silently corrupts `assignments.assignments` from `[{...}]` to `{item: [{...}]}` and stringifies booleans / `options`. Use `setNodeParameter` for single-path edits on Set v3.4 nodes. If that also fails, use direct n8n REST `PUT /api/v1/workflows/{id}` with `N8N_API_KEY_LT` from `.env` (note: PUT auto-publishes and validates all node credentials). For Code nodes, both `updateNodeParameters` and `setNodeParameter` are safe. Known-good Config shape: `{"mode": "manual", "assignments": {"assignments": [{id, name, value}, ...]}}` — no `includeOtherFields` or `options` keys required.
- **`setNodeParameter` silent failure (observed 2026-07-06):** On Code nodes and HTTP Request nodes, `setNodeParameter` may report success without modifying parameters. **Use `updateNodeParameters` with `replace: true`** as the primary mutation method for both. Always verify with a fresh `GET` after mutation.
- n8n Code nodes cannot access managed credentials by design. Do not attempt `$getCredentials()` or `this.getCredentials()` in Code nodes. Credential migration for direct API calls requires credentialed HTTP Request nodes, or an explicitly approved protected runtime-variable path.
- **Historical n8n 2.28.6 MCP schema bug (upstream #33056):** `search_workflows`, `search_projects`, and `get_workflow_details` returned fields that violated the MCP output schema. The deployment target is now n8n `2.33.3`; retain the REST workaround if the MCP schema issue recurs:
  ```bash
  curl.exe -s -H "X-N8N-API-KEY: $env:N8N_API_KEY_LT" "https://automations.livetransparent.com/api/v1/workflows?active=true&limit=100"
  curl.exe -s -H "X-N8N-API-KEY: $env:N8N_API_KEY_LT" "https://automations.livetransparent.com/api/v1/workflows/{workflowId}"
  ```
  MCP tools for **execution, editing, and node operations** are unaffected.

## Code Node HTTP Requests

- **Use `this.helpers.httpRequest({...})` directly** — do NOT wrap in an async helper function called with `.call(this, ...)`. The wrapper pattern causes HTTP 400 errors in task-runner loops.
- **`$httpRequest`** works for single calls but may fail in pagination loops.
- **`json: true`** works but must be paired with explicit `'Content-Type': 'application/json'` header.
- For paginated GHL search API calls, use `page` (1-indexed) + `pageLimit` (max 100). Do NOT use `startAfter`/`startAfterId`.
- Do NOT include empty `filters: []` in GHL search body — omit entirely.
- Add `await new Promise(r => setTimeout(r, delayMs))` between pages to avoid rate limiting.

## GHL REST API

- **API base URL**: `https://services.leadconnectorhq.com` — NOT `rest.gohighlevel.com`.
- **Auth header**: `Authorization: Bearer <GHL_PIT_FROM_ENV>` (PIT token from root `.env`). The `token:` header style does NOT work.
- **Required header**: `Version: 2021-07-28` on every request.
- **Accept/Content-Type**: Always include `Accept: application/json` and `Content-Type: application/json`.

### Email Template Operations

**Listing templates**: Use `ghl_official_emails_fetch-template` MCP tool (OAuth). Pass `query_parentId` for folder-scoped listing, `query_limit` (max 50), `query_offset`.

**Reading template content**: Each template has a `previewUrl` pointing to Firebase Storage. Use `webfetch` with `format: "html"`. No working GET endpoint exists.

**Updating a template** (PATCH):
```bash
curl.exe -s -X PATCH "https://services.leadconnectorhq.com/emails/builder/{templateId}" \
  -H "Authorization: Bearer $env:GHL_PIT" \
  -H "Version: 2021-07-28" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"locationId":"Zwz4relUXVPxx8uohnjV","editorType":"html","editorContent":"<html>...</html>"}'
```
- Uses `editorType` + `editorContent`, NOT `rawHTML`/`html`/`type` fields.
- `locationId` is required in body.
- On success, verify new `lastUpdated` timestamp and `previewUrl`.
- **Backup before editing**: `webfetch` current HTML first.
- **Watch for `&#8211;` entities**: GHL normalizes en-dashes to `&#8211;`. Preserve exactly.

## n8n REST API Note

When using direct n8n REST `PUT /api/v1/workflows/{id}`:
- Required fields: `name`, `nodes`, `connections`, `settings`
- Settings must NOT include `availableInMCP` (remove before PUT)
- `versionId` and `tags` are read-only — exclude from body
- `Content-Type: application/json` header is required
- If settings get rejected as "additional properties", strip to: `executionOrder`, `timezone`, `saveDataErrorExecution`, `saveDataSuccessExecution`, `saveManualExecutions`, `saveExecutionProgress`, `executionTimeout`, `callerPolicy`
- Use `curl.exe` with JSON file for large payloads (PowerShell `ConvertTo-Json` can corrupt nested objects with `#` chars)

## Live Voice System

| Item | Value |
|------|-------|
| Phone | +1 (562) 534 1977 (bd4ba248-a2b4-4738-b701-7c6a5ebb5bb4) |
| Callback webhook | https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback |
| Key env | VAPI_PHONE_NUMBER_ID, GHL_LOCATION_ID=Zwz4relUXVPxx8uohnjV, GHL_API_KEY / GHL_PIT |

### Voice Workflows

| Workflow | ID | Status |
|----------|----|--------|
| LT - Campaign Contact Classifier | IduCoT5YOs0g2faT | Active (native Schedule Trigger every 15 min; 10 Brand + 10 Dispensary candidates/run) |
| LT - Vapi Campaign Queue Feeder | RFIZ9Bcfl3Yvms2b | Inactive helper |
| LT - Emerging Pool Go Live Helper | OGnADUQKd5z5f905 | Manual helper |
| LT - Voice Agent V1 Vapi Callback + Tools | fx4UvKUWbqJEY3LK | Active |
| LT - Voice Agent V1 Outbound Dialer (Vapi) | r7UjWLndmc6EqEUW | Active (native Schedule Trigger every 2 minutes; business-hours guard) |
| LT - Voice Queue Vapi Intake Poller | bYk1Ai6MJLyhTsDZ | Active (polls every 10 min, 30 contacts/cycle, tag rotation) |
| LT - Voice Queue Enqueue | XzcpOBi9YcIhJPck | Active |
| LT - Voice Dequeue Next | KsBMFcz1YpBGrjDW | **Unpublished** (explicit helper only; not an automatic call-start path) |
| LT - Call Outcome Ingest | PUCfTZBANSPcgS0c | Active |
| LT - Apollo Queued Timeout Reaper | RL5ZyUoshSPbmVA1 | Active (hourly, reports to #reaper) |
| LT - Voice Campaign Brand (Alex) | 1d7c5d42-f0a4-4b58-9494-dbda3be3c657 | Active (optimized 2026-07-20) |
| LT - Voice Campaign Dispensary (Jordan) | 056f2e50-8bdf-4257-ac45-4d575600c39d | Active (optimized 2026-07-20) |

### Campaign Contact Classifier Audit (2026-07-29)

- `LT - Campaign Contact Classifier` is production-active, not manual-only. It runs every 15 minutes and selects up to 10 Brand and 10 Dispensary candidates per execution.
- It reads `emerging_pool_contacts`, performs live GHL contact and suppression checks, and applies campaign tags only after DeepSeek acceptance or a prior qualified-domain match.
- Qualified domains are persisted in `vapi_qualified_domains`. Common free-email domains are excluded, and a domain is written only after a successful GHL tag-add response.
- DeepSeek uses a 600-token output budget with concise English reasoning. The SQL candidate filter accepts a live GHL phone fallback when the imported pool phone is blank.
- Manual execution `268658` and scheduled execution `268659` passed after the audit patch with zero failed writes. The patch fixed model-output truncation, live-phone eligibility exclusion, and unsafe domain persistence on cleanup/failed writes.

### Campaign Contact Classifier — fetch diagnostics + 429 retry (2026-08-07)

- `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) `Process Warm MQL Contacts` Code node the per-contact `GET /contacts/{id}` loop failed opaquely. Two changes were made and each was deployed via direct n8n REST `PUT /api/v1/workflows/{id}` (publishing automatically; `versionId === activeVersionId` after each).
- **Fetch diagnostics**: the `fetch_error` catch now emits `error` (message, truncated to 300 chars) and `status_code` alongside `contact_id`/`status`, so every failure is self-diagnosing in execution output.
- **Bounded 429 retry**: a new `fetchContact(contactId)` helper (with a shared `SLEEP(ms)` helper) wraps the contact fetch and retries on `status_code === 429` up to 3 attempts with linear backoff (1s, 2s). Non-429 errors and a persistent 429 after the 3rd attempt rethrow into the catch as `fetch_error`.
- **Deployment**: first change published as version `85bcae4f-ce87-428c-be45-f82450bee12`; second (479) as version `adcc6622-2e7e-4519-8acf-ba6a628dc8d9`. Both active/published with matching `versionId`/`activeVersionId`; the 15-minute schedout Trigger remains intact.
- **Verification run `723561` (00:45)**: the first run on the diagnostics change classified 79 contacts (0 empty), all 12 failures clearly reported `error: "Request failed with status code 429"` and `status_code: 429` — identifying GHL per-window rate limiting as the cause rather than dead contacts or auth. The scheduler is healthy (confirmed by concurrent runs of other scheduled workflows); no runs are missed (local-clock misreading was ruled out).
- Deployment via PUT is made while the workflow is active; any single missed-tick from a publish repo is self-healed by the next 15-minute run.

**Tag rotation** (one tag per 10-min cycle, cycles every 40 min):
1. `vapi_campaign_brand` (926)
2. `vapi_campaign_dispensary` (19)
3. `brands_pool` (3,024)
4. `dispensaries_pool` (7,953)

**Fixes applied 2026-07-14:**
- `Trigger Apollo Enrichment` auth: changed `predefinedCredentialType` → `none` (was crashing because API key is passed in headers)
- `Remove Tag - Enriching` URL: changed `$json.contact_id` → `$json.contact.id` (Apollo response nests ID)
- Added full pagination loop with 250ms delays and 30-contact cap to avoid GHL rate limiting
- Added `brands_pool`/`dispensaries_pool` to search tags (was only searching campaign tags)
- Dedup: SQL `WHERE NOT EXISTS` prevents re-enqueue + `Set` dedup within each run
- **Timezone inference**: added state-to-timezone mapping in both intake poller (`Classify Contacts`) and outbound dialer (`Code - Check Phone`) since most pool contacts lack timezone data. Maps US state/Canadian province codes to IANA timezone names (e.g. `NY`→`America/New_York`, `CA`→`America/Los_Angeles`).
- **Native scheduling**: the dialer uses n8n's Schedule Trigger at a two-minute interval. The workflow's timezone-aware business-hours guard remains the authority for whether a call may start; no external cron job is required.
- **Release-lock resolution (2026-08-14)**: The shared scheduled dialer had an n8n Postgres v2.6 `queryReplacement` binding failure (`there is no parameter $1`) in the queue-release path. The affected node and three related persistence nodes were migrated to direct `require('pg')` Code nodes in published version `b8e9c57a-f81f-49fd-b469-1388320568c5`. Thirteen consecutive scheduled executions, including `746845`, succeeded afterward. The error occurred before Vapi/Twilio call creation and was not a provider outage.
- **Same-run queue advancement (2026-07-25)**: `LT - Voice Agent V1 Outbound Dialer (Vapi)` releases blocked, invalid, and outside-hours contacts and loops back to `Postgres - Fetch Next Queue Item` in the same execution. `Code - Continue Queue Loop` caps each execution at 25 queue checks. The old `End - No Phone` and `End - Outside Contact Hours` nodes are disconnected legacy nodes and are not required for the live path.
- **Dialer credential guard (2026-07-25)**: live GHL contact lookups began returning `401/403`; the dialer now fails closed after an infrastructure lookup failure instead of looping until its one-hour timeout. The `.env` GHL PIT was subsequently rotated, verified against GHL, propagated to active n8n workflows, and smoke-tested with execution `242609`.
- **Gap hardening (2026-07-25)**: silent human answers now produce `interest_unknown` rather than `vapi_qualified`; global dialer hours are 9am-5pm CT; unknown Vapi campaign tags fail closed; source-tag cleanup is dynamic; superseded Apollo Sheet First intake is unpublished; reporting config/publish schedules are connected and tested.
- **Dialer and ingest crash fixes (2026-07-30)**: Three bugs caused every dialer execution to crash. (1) GHL `Version` header `2023-02-21` rejected — corrected to `2021-07-28` on both `HTTP - Get GHL Contact` and `GHL - Create Call Note`. (2) `Code - Continue Queue Loop` read Postgres `RETURNING` columns (`skip_reason`, `loop_attempts`) that n8n's Postgres v2 node never surfaces — rewritten to read from `$('Code - Check Phone').item.json`. Infrastructure errors (`ghl_lookup_failed`, `eligibility_lookup_failed`) now fail closed with `return []`. (3) Empty queue fetches produced phantom `GET /contacts/` → 403 — added `Code - Queue Found Guard` before lookup. Queue reset: 1,051 contacts (1,047 failed + 4 cooling_down) restored to `status='pending'`. Call Outcome Ingest fix: removed `new Date().toISOString().slice(0,10)` from `queryReplacement` (invalid n8n expression). All three workflows published and verified end-to-end.

**Fixes applied 2026-07-16 (anti-spam):**
- **Campaign tag removal**: After enqueueing, the poller now removes the source campaign tag (e.g. `brands_pool`) instead of the hardcoded `vapi_queue` tag. This prevents contacts from being re-found in subsequent rotation cycles.
- **Blocklist expansion**: `Classify Contacts` now checks all 8 `BLOCKLIST_TAGS` via `hasAnyBlocklistTag()` (was only checking `vapi_voicemail` and `vapi_qualified`). Contacts with any terminal outcome tag have their campaign tag removed inline and are skipped.
- `removeTag()` helper now accepts a `tagsToRemove` array parameter for flexible tag removal.

### Voice Assistant Optimizations (2026-07-20)

Live call audit of 4 Vapi calls uncovered 7 issues across the outbound assistants. All fixes applied and published.

**Jordan (Dispensary, `056f2e50`) — 8 prompt fixes + 2 config fixes:**
- `firstMessage` template variables fixed: `{{contact_name}}` → `{{first_name}}` (n8n passes `first_name`, name was never resolving). Removed `{{market}}` (never passed, rendered as blank).
- "with Transparent eCom" → "from Transparent eCom" (Nico TTS inserted "a" → "with-a-transparent").
- Compliance disclosure removed from `firstMessage` — now system-prompt-only for live calls. Voicemail recipients no longer hear the AI/recording disclosure.
- Discovery questions restructured to ONE AT A TIME: numbered Q1-Q4 each with WAIT instructions. Old bullet list caused all 4 questions fired in one turn.
- New `[IVR vs Voicemail Detection - CRITICAL DISAMBIGUATION]` section with keyword-based classification. Voicemail indicators: "record/rerecord your message", "press pound to send". IVR indicators: "press X for sales/operator". Tiebreaker: assume voicemail.
- `[Speech Naturalness]`: "um"/"uh" minimized to once per call max (was explicitly permitted).
- `[Pronunciation]`: "Point of Sale" never "POS" (Nico says "paws"), "from" never "with".
- `[No Stage Directions]` expanded: banned throat-clearing, coughing, sighing, humming, and text like "*clears throat*" that TTS acts out.
- Transcriber: `smartFormat` false → true (Deepgram suppresses non-speech artifacts).
- Model: Llama 3.3 70B tested (cheaper/faster) but reverted to Claude 3 Haiku (better instruction following). System prompt preserved through swap.
- Voice: Nico kept (Emma + Layla as fallbacks).

**Alex (Brand, `1d7c5d42`) — same discovery questions, IVR/voicemail disambiguation, turn-taking, stage directions, and `{{contact_name}}`→`{{first_name}}` fixes.**

**Savannah (V1 Outbound, `3f9bbfd2`) — same IVR/voicemail disambiguation, stage directions, and `{{contact_name}}`→`{{first_name}}` fixes.**

**Outbound Dialer (`r7UjWLndmc6EqEUW`) — stuck queue fix:**
- Contact `AX3wfQNpRwm6DG0HgUE2` (deleted from GHL, 2 entries in voice_call_queue) blocked every dialer run since ~18:38 UTC.
- `HTTP - Get GHL Contact` had `neverError: false` — GHL's 400 crashed the run before lock release. Same contact re-picked every 2 min.
- Fix: `neverError: true` on lookup node (400 passes through to Code - Check Phone which falls back to queue phone). `onError: continueRegularOutput` on `GHL - Create Call Note` (cosmetic note failure won't error the execution).
- Intake poller (`bYk1Ai6MJLyhTsDZ`) was unaffected — continued enqueueing contacts every 10 min throughout.

### Voice Tags

vapi_call_attempted, vapi_dnc, vapi_human_answered, vapi_interested, vapi_not_interested, vapi_interest_unknown, vapi_voicemail, vapi_voicemail_left, vapi_no_answer, vapi_busy, vapi_wrong_number, vapi_contact_disconnected

### Vapi Campaign Tags

| Tag | ID |
|-----|-----|
| vapi_campaign_brand | exfU7DXbFF1c314Z1QXQ |
| vapi_campaign_dispensary | FiYEwJdMSIyKZa059wRY |
| vapi_already_called | HhkfhzocuEdOFOxeeHu2 |

### Vapi Assistants

| Assistant | ID | LLM | maxTokens | Temp | Speed | Voice |
|-----------|-----|-----|-----------|------|-------|-------|
| V1 Outbound (Savannah) | 3f9bbfd2 | claude-3-haiku | 300 | 0.5 | 0.95 | Savannah |
| Brand (Alex) | 1d7c5d42 | claude-3-haiku | 300 | 0.5 | 1.05 | Elliot |
| Dispensary (Jordan) | 056f2e50 | claude-3-haiku | 300 | 0.5 | 0.88 | Nico |
| V1 Inbound (Savannah) | 43f379ff | claude-3-haiku | 300 | 0.5 | 0.95 | Savannah |

### Regulated-Business Classification and SDR Work Queue Boundary

- Warm is the unassigned intake and verification layer.
- The canonical classifier result is the GHL tag `qualified` for a regulated business (including nicotine, cannabis, CBD, vape, hemp, and related regulated verticals), or `not qualified` for a non-regulated business.
- `qualified` is the regulated-business classification gate; qualified opportunities belong in `Sales Outreach -> Qualified`, not `Sales Outreach -> New`.
- SDR allocation occurs only at Sales Outreach entry:
  - one existing owner: align the other record;
  - matching owners: preserve;
  - conflicting owners: flag for review;
  - neither owner present: deterministic Jason/Marc 50/50 assignment.
- Keep contact `assignedTo`, opportunity native `assignedTo`, and custom opportunity `Owner` aligned.
- Vapi remains in Warm and must exclude contacts tagged `not qualified`; the intake path must not bypass the canonical classification result.
- A successful Vapi warm transfer is manually claimed by the answering SDR, who then promotes the record to Sales Outreach.
- Vapi booking remains on Cameron's Regulated Ads calendar; warm transfer uses the shared SDR number and neutral Sales Lead language.
- Vapi transfer tool: `86d380a3-34d2-41f8-96a0-acf5f0124ccb` (`transferCall`); live human-facing wording is neutral Sales Lead language, while compatibility function name `ok_transfer_to_jason` and shared destination `+15622474600` remain unchanged.

### Website Booking Path

- Canonical calendar: `Regulated Ads On Social/Search`.
- Calendar ID: `SrtXcFVyea7pFl3nTiIK`.
- Direct booking URL: `https://api.leadconnectorhq.com/widget/booking/SrtXcFVyea7pFl3nTiIK`.
- Website `Book a Demo` CTAs should link directly to this widget or embed it in an iframe. Visitors should enter identity/contact fields once on the booking form.
- The legacy GHL hero form `kxrHpS9bX16nzkIbr2py` must not appear before the booking form for the primary demo CTA; it duplicates name, email, and phone collection.
- The `/apply/` page currently has a legacy Calendly embed and should replace it with:

```html
<div style="width:100%; max-width:1100px; margin:0 auto;">
  <iframe
    src="https://api.leadconnectorhq.com/widget/booking/SrtXcFVyea7pFl3nTiIK?utm_source=website&amp;utm_medium=calendar&amp;utm_campaign=regulated_ads_booking&amp;utm_content=apply_page"
    style="width:100%; min-height:900px; border:0;"
    scrolling="no"
    title="Book a Regulated Ads Strategy Call">
  </iframe>
</div>
<script src="https://link.msgsndr.com/js/form_embed.js"></script>
```

- After any website booking change, verify the appointment is created on `SrtXcFVyea7pFl3nTiIK`, not a personal, interview, or Calendly calendar.

### Apollo Phone Enrichment Status (custom field rgYJ7UqoznGoe3WeUAtH)

- enriched -- terminal (good)
- no_match -- terminal (no Apollo hit)
- error -- terminal (API error)
- queued -- transient (awaiting Apollo callback)
- queued_phone -- transient (profile enriched, phone requested via async callback)
- callback_timeout -- terminal (set by reaper when queued > 24h)
- callback_failed -- terminal (Apollo callbacks received but processing failed)

### Apollo Enrichment Pipeline (Fixed 2026-07-14)

The pipeline was completely dead since 2026-05-13. All webhook-based workflows had 0 executions.

**Before fix**: 3 webhook workflows with 0 executions each, 1,279 contacts stuck at callback_timeout.

**After fix**: New polling workflow replaces the webhook-based intake. Works in two steps per contact:
1. Sync profile match: calls Apollo `/v1/people/match` (no phone), writes name/email/company/LinkedIn/title/dept/revenue immediately
2. Async phone request: calls Apollo again with `webhook_url` pointing to V4 callback handler

| Workflow | ID | Status |
|----------|-----|--------|
| **LT - Apollo Phone Enrichment Polling** | **JH8ShfpglWmLMZ3l** | **Active, every 30 min, batch 50** |
| GHL Apollo Phone Enrichment - Callback Handler V4 | U7c6byTLXAMgcS75 | Active (1,058+ callbacks received by 2026-07-16, working) |
| GHL Apollo Enrichment - Webhook Intake (Sheet First) | WmKAhG7mIaXonNsh | Active (0 executions - superseded by polling) |
| GHL Apollo Enrichment - Phone Webhook Intake (Staged) | WuxgTa0EEL1mb2SA | **Unpublished** (legacy; 1,008 orphaned webhook executions canceled 2026-07-16) |
| GHL Apollo Phone Enrichment - Callback Handler V3 | YaWizRnw7XmkcvZH | **Unpublished** (legacy V3, fully superseded by V4) |

**Pipeline flow:**
1. **Polling workflow** searches GHL every 30 minutes for contacts needing enrichment (3 sources: `Enrich Phone via Apollo = Yes`, empty enrichment status + no phone, orphaned `queued` / `queued_phone` status)
2. **Sync step**: Calls Apollo `/v1/people/match` with name/email/LinkedIn → writes profile data (name, email, company, title, dept, LinkedIn, revenue, funding) to GHL immediately
3. **Async step**: Calls Apollo `/v1/people/match` with `reveal_phone_number: true` + `webhook_url` pointing to V4 callback → Apollo processes and calls back
4. **V4 callback handler** receives the phone number and updates GHL with it, setting status to `enriched`
5. **GHL automation** (`WL - Apollo Phone Enrichment Trigger`) watches for `Enrich Phone via Apollo = Yes` and POSTs to the (now unpublished) intake webhook — no longer needed since poller handles it

**Webhook key** for all Apollo callbacks: `<APOLLO_WEBHOOK_KEY — see .env>`

**Apollo API key**: `<APOLLO_API_KEY — see .env>`

### Apollo Pipeline Full Audit + Fixes (2026-07-15)

Full review of 7 Apollo-related workflows found 2 CRITICAL bugs, 2 HIGH issues, and several medium/low cleanups. 10 fixes applied across 6 workflows:

#### 1. `queued_phone` status invisible to Timeout Reaper — CRITICAL (RL5Zy, JH8Sh)

**Bug**: Polling workflow set status to `queued_phone` after async phone request, but Reaper only searched for `queued`. Contacts stuck in async callback phase were never unblocked.

**Fix**: Reaper now searches both `queued` AND `queued_phone`. Polling workflow now writes `Apollo Phone Enrichment Queued At` (NgC3xGTh0laQ9ArTnude) alongside `queued_phone` so aging works.

#### 2. Intake Poller re-triggers enrichment on `queued_phone` — CRITICAL (bYk1)

**Bug**: Classify Contacts code matched `queued` → `waiting` but `queued_phone` fell through to default `enrich` action, triggering duplicate Apollo API calls for already-pending contacts.

**Fix**: Added `queued_phone` to the `waiting` path alongside `queued`.

#### 3. SQL injection in Sheet First intake — CRITICAL (WmKAh)

**Bug**: Build Upsert SQL used template-literal injection with manual `''` escaping — same anti-pattern previously fixed in LinkedIn Reply Backfill.

**Fix**: Switched to parameterized query with `$1..$9` and `queryReplacement` array. Code node now outputs typed JSON fields instead of building SQL strings.

#### 4. `doHttpRequest` wrapper pattern removed from all workflows — HIGH

The wrapper pattern `async function doHttpRequest(options) { ... $httpRequest / this.helpers.httpRequest ... }` called with `.call(this, ...)` causes HTTP 400 errors in task-runner loops. Removed from: V4 callback (U7c6), V3 callback (YaWi), Intake Poller Search GHL Contacts (bYk1), Sheet First main Code node (WmKAh). All replaced with direct `this.helpers.httpRequest(options)` or `this.helpers.httpRequest(opts)`.

#### 5. V3 callback handler had zero error handling — HIGH (YaWi)

**Bug**: No try/catch in main Code node. Any error returned 500 with no status update.

**Fix**: Added try/catch with best-effort `callback_failed` status update on error, matching V4's error handler. Then **unpublished** V3 (fully superseded by V4).

#### 6. GHL error handling in polling workflow — MEDIUM (JH8Sh)

**Bug**: `ghl()` helper swallowed all errors identically (`{ ok: false }`). A 429 rate limit looked the same as a 404.

**Fix**: `ghl()` now returns `{ ok: false, status: ... }`. All 3 search sources retry on 429 with 5s delay before re-scanning the same page.

#### 7. V4 callback `Apollo Contact Id` conditionally set — MEDIUM (U7c6)

**Bug**: `Apollo Contact Id` was only written when `normalizedPhone` was found. If Apollo returned valid profile but phone was blocked (corporate phone match), the contact lost traceability.

**Fix**: `successfulApolloContactId` now always set to `str(person?.contact?.id || person?.id)` regardless of phone status.

#### 8. Reaper Config node corruption — LOW (RL5Zy)

**Bug**: Set v3.4 Config node had nested `parameters.parameters.assignments.assignments` corruption artifact from a prior `setNodeParameter` call.

**Fix**: Removed via REST API PUT. Config node now has clean `{"mode":"manual","assignments":{"assignments":[...]}}` shape.

#### 9. Intake Poller `removeTag` used `$httpRequest` fallback — LOW (bYk1)

**Bug**: Classify Contacts `removeTag()` function checked `typeof $httpRequest === 'function'` as primary with `this.helpers.httpRequest` as fallback.

**Fix**: Replaced with direct `await this.helpers.httpRequest(opts)` call.

#### 10. Status pipeline now consistent end-to-end

| Status | Set by | Read by | Action |
|--------|--------|---------|--------|
| `queued` | Staged Intake (legacy) | Reaper, Intake Poller | Reaper: unblock after 24h; Poller: waiting |
| `queued_phone` | Polling workflow | Reaper, Intake Poller | Reaper: unblock after 24h; Poller: waiting |
| `enriched` | V4 callback | Intake Poller | Enqueue to voice_call_queue |
| `no_match` | Polling/V4/Sheet First | Intake Poller | Terminal skip |
| `error` | Polling | Intake Poller | Terminal skip |
| `callback_failed` | V4 callback catch | Intake Poller | Terminal skip |
| `callback_timeout` | Reaper | Intake Poller | Terminal skip |

### Apollo Production Hardening (2026-07-16)

- Audited the live production path end-to-end: Polling (`JH8ShfpglWmLMZ3l`), V4 callback (`U7c6byTLXAMgcS75`), and Reaper (`RL5ZyUoshSPbmVA1`) were all active and published.
- Canceled **1,008** orphaned `running` executions on legacy staged workflow `WuxgTa0EEL1mb2SA`. Sample stuck runs never progressed beyond the `Webhook` node; this was stale execution state, not the active Apollo production path.
- Polling workflow fix: orphan re-discovery now searches both `queued` and `queued_phone` instead of only `queued`.
- Callback V4 fix: Apollo provider-level callback failures (for example `failure_reason: "you ran out of mobile number credits"`) now write `Apollo Phone Enrichment Status = callback_failed` instead of being silently treated as `no_match`.
- Polling workflow write-path fix: hardened GHL contact update fallback after reproducing live GHL behavior on `PUT /contacts/{id}`.
  Accepted shape for this endpoint is `{"customFields":[...]}` without `locationId`; bodies containing `locationId` or `customField` can return `422`.
- Polling workflow now falls back to a minimal write when the full profile update fails, ensuring at least:
  - `Apollo Phone Enrichment Status = queued_phone`
  - `Apollo Phone Enrichment Queued At = <today>`
  - `Enrich Phone via Apollo = No`
  - Apollo IDs where available
- Backfilled 6 previously blank contacts on 2026-07-16 into `queued_phone` so they are now visible to the callback/reaper path immediately:
  `VXwNjbZyBm1DMNljim6g`, `K9otZl89OAFlWmGk8fY7`, `mUgGwrkOB8CW8reYmpMd`, `e7eu0xGixu3ATmA61OqN`, `KA8xGJbf0QZHxXV6HXWF`, `8uobjmgriFLAdtmHfjk7`.

### Custom Field IDs (GHL)

- Apollo Phone Enrichment Status = rgYJ7UqoznGoe3WeUAtH (SINGLE_OPTIONS)
- Apollo Phone Enrichment Queued At = NgC3xGTh0laQ9ArTnude (DATE)
- Enrich Phone via Apollo = gdJDuZelIxEBE6n9i5Q6 (SINGLE_OPTIONS: Yes/No)
- Em_Emerald_Contact_ID = R0wbDRyzZz34PMlQSRWN
- Em_Source_File = ILurFacMbAaHz2DdGjPa

### Pool Tags

- brands_pool -- contacts from Brands.csv import
- dispensaries_pool -- contacts from Dispensaries.csv import

### Apollo Re-enrichment on Bad Numbers

In callback workflow fx4UvKUWbqJEY3LK, when Vapi returns wrong_number or contact_disconnected, Vapi first tries every available phone number for the contact before requesting Apollo enrichment (2026-08-04).

**Phone candidate sources** (built by the dialer's `Code - Check Phone`, deduped + E.164-normalized): GHL primary `phone`, `Corporate Phone` (`036gD9ds9P5V8VUHnFBP`), `Company Phone` (`YNlWu5FRGk0PhepqD0Zo`), `Em_All_Known_Phones` (`F8iUFGsA8CqdzEzjY3Eh`, may hold multiple), and the queue's `phone_e164` pool fallback.

**How it works:**
- `voice_call_queue` gained `phone_candidates jsonb` and `phone_index integer NOT NULL DEFAULT 0`.
- The dialer (`r7UjWLndmc6EqEUW`) builds the candidate list, picks `phone_candidates[phone_index]`, and passes `phone_candidates` (JSON string) + `phone_index` into the Vapi call metadata/variableValues. `Postgres - Mark Attempted` (updated) also persists `phone_candidates` and `phone_index` to the queue row after the call is submitted.
- The callback's `Code - Normalize End Of Call` extracts `phone_candidates`/`phone_index` from the Vapi metadata (same proven path as `queue_id`).
- `Code - Decide Next Phone` (replaces the old `Should Re-enrich Phone` IF) reads disposition + candidates + index from `Code - Normalize End Of Call`. If `wrong_number`/`contact_disconnected` and `(index + 1) < candidates.length`, it advances: `Postgres - Advance Phone Index` sets `phone_index + 1`, `status='pending'`, `attempt_count=0`, `next_attempt_at=NOW()`, clears the lock, and `HTTP - Remove Bad Call Tag` removes the `vapi_wrong_number`/`vapi_contact_disconnected` tag from GHL so the dialer's blocklist doesn't skip the retry. Only after the last candidate fails does `HTTP - Set Apollo Enrichment` set `Enrich Phone via Apollo = Yes` (custom field gdJDuZelIxEBE6n9i5Q6). The existing LT - Apollo Phone Enrichment Intake V3 then looks up a new number.
- If `queue_id`/`phone_candidates` are absent from the metadata (rare non-dialer call), the decision degrades to the previous behavior (Apollo enrichment immediately).

## Vapi Workflow Fixes (2026-07-14)

Full review conducted of all 12 Vapi-related workflows. Five bugs fixed across 3 workflows:

### 1. Race Condition: Dialer Picked Queue Items Without Lock (r7UjWLndmc6EqEUW)
`Postgres - Fetch Next Queue Item` used `SELECT...LIMIT 1` (read-only). Between the read and the write, `LT - Voice Dequeue Next` could `UPDATE...RETURNING` the same item, causing **duplicate outbound calls** to the same contact.
**Fix**: Changed to `UPDATE...FROM...RETURNING` that atomically locks the row (`locked_at = NOW(), lock_owner = 'outbound-dialer'`) at fetch time.

### 2. `report_referral` Tool Was Dead Code (fx4UvKUWbqJEY3LK)
`Switch - Route Tool` output 4 routed `report_referral` to `Code - Normalize End Of Call`, which checks `endedReason`/`analysis.summary` — none of which exist on tool call payloads. Node returned `[]` silently.
**Fix**: Re-routed to `Respond - 200` so Vapi gets a proper acknowledgment.

### 3. Intake Poller Could Create Duplicate Queue Entries (bYk1Ai6MJLyhTsDZ)
`Postgres - Insert Queue` used plain `INSERT INTO...VALUES(...)` with **no dedup check**. The webhook-based enqueue had `WHERE NOT EXISTS` but the poller didn't.
**Fix**: Wrapped INSERT in `SELECT...WHERE NOT EXISTS (SELECT 1 FROM voice_call_queue WHERE contact_id = $1 AND status IN ('pending', 'in_progress'))`. Also updated `Transform Postgres Output` to return `[]` gracefully when dedup blocks insertion (was throwing an error).

### 4. No Error Handling on Tag Removal HTTP Nodes (bYk1Ai6MJLyhTsDZ)
Three HTTP DELETE nodes (`Remove Tag - Enqueued`, `Remove Tag - Enriching`, `Remove Tag - Skipped`) lacked `continueOnFail`. A flaky GHL tag deletion crashed the workflow after the enqueue/enrich/skip already succeeded.
**Fix**: Enabled `continueOnFail: true` on all three.

### 5. Timer System Static Data Race Condition (fx4UvKUWbqJEY3LK)
`$getWorkflowStaticData('global')` not atomic across concurrent executions. Two rapid status-update webhooks could both start a 465-second timer chain — producing duplicate background warnings and force-end commands.
**Fix**: Replaced `state.timersScheduled` boolean with `state.timersScheduledAt` timestamp. Added 60-second dedup window: if a timer was already started within 60s, a duplicate is skipped. Updated `Code - Prepare Background Warning` and `Code - Prepare Hard Stop` to check `timersScheduledAt`.

## Vapi Anti-Spam Fixes (2026-07-16)

Root-cause audit triggered by a contact complaint about repeated Vapi calls after voicemail had already been left. Identified **4 bugs combining into an infinite call loop** across 3 workflows. All published 2026-07-16.

### The Spam Chain (before fixes)

1. Intake Poller finds contacts by campaign tag (e.g. `brands_pool`) → enqueues → **only removed `vapi_queue` tag** (which contacts never had). Campaign tag stayed.
2. Dialer calls → voicemail → Callback applies tags but **never marks queue `completed`** (only the tool-call `update_lead_status` path did that).
3. 3 days later, dialer retries → `Code - Check Phone` sees `vapi_voicemail` tag → blanks phone → release lock → `status = 'completed'`.
4. Next poller cycle finds same contact (campaign tag still present) → old entry is `completed` → dedup only blocks `pending`/`in_progress` → **creates new queue entry**.
5. Dialer picks new entry → calls again → voicemail again → loop forever.

### Fixes Applied

#### 1. Intake Poller removed wrong tag after enqueue (bYk1Ai6MJLyhTsDZ) — CRITICAL

**Bug**: `Remove Tag - Enqueued` always removed `vapi_queue`, but contacts were found by campaign tags like `brands_pool`, `dispensaries_pool`, `vapi_campaign_brand`, `vapi_campaign_dispensary`. The campaign tag never got removed, so contacts were re-found every 40-minute rotation cycle.

**2026-07-16 Fix (incomplete)**:
- `Classify Contacts` now outputs `source_tag` (the matched campaign tag) with every enqueue result
- `removeTag()` function accepts `tagsToRemove` array argument
- `removeFromQueue` check replaced by `hasAnyBlocklistTag()` checking all 8 outcome tags
- **BUT**: `Transform Postgres Output` couldn't read `source_tag` — Postgres `INSERT...RETURNING` only returns DB columns, not the extra `source_tag` field. `Remove Tag - Enqueued` silently fell back to removing `"vapi_queue"`, which contacts never had. Campaign tag stayed on first enqueue.

**2026-07-22 Fix (this session)**: Rewrote `Transform Postgres Output` to look up `source_tag` from `$("Classify Contacts").all()` by `contact_id` using a pre-built lookup map, instead of expecting Postgres to pass it through. `Remove Tag - Enqueued` now receives the real campaign tag on every run.

**Self-healing behavior**: On the next poller cycle after a contact gets a blocklist outcome tag, `Classify Contacts` matches it in the `skipped` path (not the `enqueue` path). The `skipped` path resolves `matchedCampaignTag` in-scope before any Postgres call and removes the campaign tag inline. So even before this fix, contacts eventually self-cleaned within 1 cycle after getting a terminal tag — but the first enqueue always left the campaign tag intact.

#### 2. EOC callback never marked queue completed (fx4UvKUWbqJEY3LK) — CRITICAL

**Bug**: End-of-call path was `Normalize End Of Call → Respond → Insert Attempt → Apply Tags → Should Re-enrich Phone`. It inserted call attempts, applied GHL tags, and triggered re-enrichment — but **never set `voice_call_queue.status = 'completed'`**. Only the tool-call path (`update_lead_status` → Postgres - Update Status) updated the queue.

**Fix**: Added new Postgres node `Postgres - Mark Queue Completed` wired between `GHL - Apply Tags` and `Should Re-enrich Phone`:
```sql
UPDATE voice_call_queue SET status = 'completed', updated_at = NOW() WHERE queue_id = $1;
```
Now every end-of-call callback immediately terminates the queue entry.

#### 3. Only 2 of 10 outcome tags blocked retries (r7UjWLndmc6EqEUW) — HIGH

**Bug**: `Code - Check Phone` blocklist was only `['vapi_voicemail', 'vapi_qualified']`. Contacts with `vapi_no_answer`, `vapi_busy`, `vapi_wrong_number`, `vapi_contact_disconnected`, `vapi_voicemail_left`, `vapi_dnc` were retried indefinitely (up to `max_attempts`).

**Fix**: Expanded `BLOCKLIST_TAGS` to all 8 terminal tags:
```
vapi_voicemail, vapi_voicemail_left, vapi_qualified, vapi_no_answer, vapi_busy, vapi_wrong_number, vapi_contact_disconnected, vapi_dnc
```

#### 4. Intake Poller blocklist only checked 2 tags (bYk1Ai6MJLyhTsDZ) — HIGH

**Bug**: `Classify Contacts` only skipped contacts with `vapi_voicemail` or `vapi_qualified`. Contacts with other outcome tags could be re-enqueued on discovery.

**Fix**: Added `hasAnyBlocklistTag()` using the same 8-tag `BLOCKLIST_TAGS` constant. Also removes the campaign tag inline before skipping.

### Defense Layers (per-contact, now active)

| Layer | What blocks the call |
|--------|---------------------|
| 1 | **Campaign tag removed** after enqueue — poller never re-finds contact |
| 2 | **Queue marked `completed`** by callback — dialer FETCH ignores it (`WHERE status = 'pending'`) |
| 3 | **Dialer live-checks** all 8 outcome tags on GHL contact before every call via `Code - Check Phone` |
| 4 | **Intake Poller rejects** contacts with any of the 8 blocklist tags via `hasAnyBlocklistTag()` |
| 5 | **Queue dedup** `WHERE NOT EXISTS` blocks duplicate `pending`/`in_progress` entries |

### Key Constants (synced across all 3 workflows)

```
BLOCKLIST_TAGS = ['vapi_voicemail', 'vapi_voicemail_left', 'vapi_qualified', 'vapi_no_answer', 'vapi_busy', 'vapi_wrong_number', 'vapi_contact_disconnected', 'vapi_dnc']
```

### New Callback EOC Path

```
Before: Apply Tags → Should Re-enrich Phone
After:  Apply Tags → Postgres - Mark Queue Completed → Should Re-enrich Phone
```

### Vapi Call-Path Hardening (2026-07-22 — 2026-07-23)

- n8n target upgraded to `2.33.3`; recurring workflows use native Schedule Trigger nodes, not OS/Coolify cron jobs.
- `Code - Detect Tool vs Callback` now reads the original `Webhook - Vapi` input because the Config Set node replaces the current item.
- Callback normalization now reads Vapi IDs from `message.assistant.metadata`, `message.assistant.variableValues`, and `artifact.variables`.
- Callback completion-note JSON is built as an object expression, avoiding invalid JSON when summaries contain quotes or newlines.
- GHL note/tag failures continue without blocking Postgres queue completion; queue completion passes query replacements as an array.
- The callback no longer invokes `LT - Voice Dequeue Next`. That helper is unpublished and must remain an explicit/manual helper, not an automatic call-start path.
- The outbound dialer uses a native two-minute Schedule Trigger plus the existing timezone-aware business-hours guard.
- The outbound dialer atomically changes a selected queue row from `pending` to `in_progress` before calling Vapi. Ambiguous Vapi/API failures cannot be retried after the stale-lock window; no-phone and outside-hours release branches explicitly restore `pending`.

### Vapi/n8n Final Hardening (2026-07-23)

- n8n is now documented and operated at target version `2.33.3`; recurring workflows use native Schedule Trigger nodes rather than OS/Coolify cron.
- Callback timer state keeps the 60-second duplicate-start guard and now prunes ended/inactive entries older than 30 minutes.
- `LT - Voice Queue Enqueue` (`XzcpOBi9YcIhJPck`) requires `X-LT-Voice-Queue-Secret`; the caller reference is `VOICE_QUEUE_ENQUEUE_SECRET`. Missing authentication fails closed before queue insertion.
- `LT - Apollo Phone Enrichment Polling` reports `apollo_phone_request_failed` when the asynchronous Apollo phone request fails after profile processing.
- `LT - Apollo Queued Timeout Reaper` now connects `Build Slack Summary` to `Post to Slack #reaper`.
- Removed the stale response-code option from `LT - Call Outcome Ingest`.
- Final live workflow versions were checked after each mutation; `versionId` matched `activeVersionId` for all changed workflows.
- Safe queue smoke checks passed: unauthenticated requests return `400 unauthorized`; authenticated malformed requests reach validation and do not insert a queue row. Live Vapi control URLs remain untested because exercising them requires an actual call.

## LinkedIn Workflow Fixes (2026-07-14 — 2026-07-15)

### Current Published Workflow Inventory (Updated 2026-07-16)

**Canonical LinkedIn path**: Dispatcher sends connection requests -> Acceptance Checker/State Sync marks contacts `connected` -> DM Sequence sends the 4-message cadence -> Unipile New Messages/Reply Backfill marks conversations active -> DM Suppression or sequence completion prevents future sends.

**Published / active LinkedIn workflows left running:**

| Workflow | ID | Status | Role |
|----------|----|--------|------|
| LT - GHL LinkedIn Connect Dispatcher (Unipile) | fXxw5lanZcDmUrst | Active | Selects `ready` contacts from `linkedin_connection_state`, live-checks GHL tags/conversations, sends LinkedIn connection requests through Unipile, writes `requested` state. |
| LT - LinkedIn Connection Acceptance Checker (Unipile) | 3ttEvr5NMcQCS4Hp | Active webhook | Receives Unipile relation/acceptance events at `/webhook/lt-linkedin-connection-accepted`, finds matching state row, marks contact `connected`, tags GHL with `linkedin_connected`. |
| LT - LinkedIn Connection State Sync (Unipile) | ceaKnz6E3onQrZpt | Active schedule `15 */6 * * *` | Reconciles GHL contacts + LinkedIn profile URLs against Unipile and upserts ready/connection state rows. |
| LT - LinkedIn Connection State Upsert | Old7ZvyVYgFaJgDr | Active webhook | Canonical state-table write endpoint at `/webhook/lt-linkedin-connection-state-upsert`; used by dispatcher, acceptance, sync, suppression, and DM workflows. |
| LT - LinkedIn DM Sequence (Unipile) | d0tEtijajisIsYcs | Active schedule `0 12-22 * * 1-5` | Canonical post-connection DM sequence for contacts with `connection_status = connected`; sends 4 DMs and later marks complete. |
| LT - LinkedIn Unipile New Messages | 7o5EBdvwAuIaWW7k | Active webhook | Receives inbound LinkedIn message events at `/webhook/lt-unipile-linkedin-new-messages`; marks `dm_conversation_status = active` so outbound DM sequences stop. |
| LT - LinkedIn Reply Backfill | QfJ2EZcc7lZwNgxj | Active schedule `*/10 * * * *` | Backfills/updates reply state from Unipile conversations so contacts with inbound replies are not messaged again. |
| LT - LinkedIn Relations Backfill | VPiHfBwzOHaJnHBY | Active daily 3:15am | Backfills LinkedIn relation/provider state, including synthetic rows where needed. |
| LT - LinkedIn DM Suppression from GHL Tag | IPN8jnR3XSurX0o1 | Active webhook | Receives GHL `stop_linkedin_dms` automation payload at `/webhook/lt-linkedin-suppress-dms`; resolves LinkedIn profile, applies `linkedin_dm_sequence_completed`, and terminal-upserts real + synthetic state IDs. |

**Unpublished / intentionally stopped:**

| Workflow | ID | Status | Why |
|----------|----|--------|-----|
| LT - LinkedIn Follower DM Sequence (Unipile) | pq7XVajNFnnwMUTr | Unpublished, `active=false` | Redundant one-touch LinkedIn follower DM path. It used separate follower state semantics and could overlap the canonical dispatcher -> connected -> 4-message DM sequence. |
| LT - Instagram DM Sequence (Unipile) | iCnY6ccdHhfJg3sf | Unpublished, `active=false` | Misconfigured with the LinkedIn Unipile account ID (`V9eiHiDpRmCtan0YNdzsQw`) and no account-type guard. It was sending the short Instagram templates as LinkedIn DMs using `instagram_dm_state`. |
| LT - LinkedIn DM Sequence Test (No Delay) | wnpVYUNFLyNe5cS6 | Manual/test only | Not part of production sending. Use only for controlled testing. |

### Canonical DM Sequence Definition (d0tEtijajisIsYcs)

The production LinkedIn DM sequence sends 4 messages after a contact reaches `connection_status = connected` in `linkedin_connection_state`.

| Step | When Eligible | Behavior |
|------|---------------|----------|
| 1 | `sequence_step = 0` and `dm_sequence_started_at IS NULL` | Sends DM 1 immediately and sets `dm_sequence_started_at`. |
| 2 | Sequence started at least 3 days ago | Sends DM 2. |
| 3 | Sequence started at least 7 days ago | Sends DM 3. |
| 4 | Sequence started at least 10 days ago | Sends DM 4. |
| Complete | Sequence started at least 14 days ago and `sequence_step = 4` | Sends no DM; applies `linkedin_dm_sequence_completed`, sets `connection_status = completed`, and advances terminal state. |

The sequence skips if `payload_json.dm_conversation_status = active`, if GHL conversation lookup finds an inbound message, or if the reply lookup fails. Reply lookup failure is fail-closed.

### Fixes Applied 2026-07-16

- Traced malformed LinkedIn screenshot messages and identified they were sent by `LT - Instagram DM Sequence (Unipile)`, not the canonical LinkedIn DM sequence. The exact templates were `instagram.v1[1]` and `instagram.v1[2]`.
- Unpublished `LT - Instagram DM Sequence (Unipile)` (`iCnY6ccdHhfJg3sf`) after confirming it was using the LinkedIn Unipile account ID and separate `instagram_dm_state`, creating an accidental second LinkedIn DM path.
- Unpublished `LT - LinkedIn Follower DM Sequence (Unipile)` (`pq7XVajNFnnwMUTr`) because the canonical 4-message connected-contact sequence supersedes the one-touch follower DM path.
- Expanded sanitizer coverage across all audited Unipile sender template nodes before unpublishing the redundant paths: template registries are pre-sanitized, and final outbound text is sanitized immediately before `POST /chats` or `POST /users/invite`.
- Cleaned stored mojibake/smart punctuation from audited DM template literals and verified no bad literal message text remained in sender nodes.

### Connection Acceptance Checker (3ttEvr5NMcQCS4Hp)
`access to env vars denied` on Postgres queryReplacement using `$env.UNIPILE_ACCOUNT_ID`. Node `N8N_BLOCK_ENV_ACCESS_IN_NODE` blocks env access. **Fix**: Replaced with hardcoded `V9eiHiDpRmCtan0YNdzsQw`.

### Connection State Sync (ceaKnz6E3onQrZpt)
Task runner timed out after 300s. Code node searches GHL + Unipile with 15 pages/200 contacts. **Fix**: Reduced maxPages 15→5, maxContacts 200→50.

### Follower DM Sequence (pq7XVajNFnnwMUTr)
Code node referenced `CFG.ghlApiBaseUrl`/`CFG.ghlApiKey` but both the Config node's outer `assignments` AND the Code node's CFG object lacked those fields. The Config node had a duplicate inner `parameters.assignments` (11 items with GHL creds) that n8n ignored because only the outer `parameters.assignments` (9 items, no GHL) is the live path. **Fix (2026-07-14)**: Added `ghlApiBaseUrl`/`ghlApiKey` to Config inner assignments — BUT this didn't fix the Code node CFG which still didn't read them. **Fix (2026-07-15)**: Added `ghlApiBaseUrl`/`ghlApiKey` to Config outer assignments AND to the Code node CFG object AND fixed the synthetic ID inbound check (see below).

### DM Sequence (d0tEtijajisIsYcs)
`Code doesn't return items properly` — **leading** backtick (not trailing) at start of `jsCode` field in node "Send DM Sequence Messages" caused unterminated template literal syntax error. **Fix (2026-07-14)**: Removed orphan backtick — BUT it was never published (draft versionId ≠ activeVersionId). **Fix (2026-07-15)**: Published the corrected draft; confirmed jsCode char[0] is 'c' (ASCII 99).

### Dispatcher Feeder Tag Check (fXxw5lanZcDmUrst)
`Feed Ready Queue` Code node checked `fullContact.tags` but GHL `GET /contacts/{id}` returns tags nested under `fullContact.contact.tags`. So blocking tags (`linkedin_connection_requested`, `linkedin_connected`, `linkedin_state_queued`) were never detected — `skipped` was always 0. This caused every run to re-process already-queued contacts, but the UPSERT CASE in `linkedin_connection_state` prevented downgrading `requested`/`connected` back to `ready`, so `Fetch Ready Queue` always returned empty. **Fix**: Added GHL response unwrap: `var contactData = fullContact.contact ? fullContact.contact : fullContact;`. Tag check now correctly skips already-processed contacts.

**GHL API response gotcha**: `GET /contacts/{id}` returns `{ contact: { tags: [...], ... } }`. Code reading `.tags` directly will always get `undefined`. Always unwrap via `.contact` first.

### Bulk Feed (2026-07-13)
Discovered dispatcher had zero `connection_status = 'ready'` rows because all contacts in the state table were `requested` or `connected` from June 2026. User exported 14,987 contacts from GHL with LinkedIn URLs and no blocking tags. Batch-upserted via state upsert webhook into `linkedin_connection_state` with `connection_status = 'ready'`. ~15,202 total executions recorded. Dispatcher's `Fetch Ready Queue` will now find contacts on its next scheduled run.

### Full 9-Workflow LinkedIn Audit + Fixes (2026-07-15)

Full review of all 9 LinkedIn workflows found 2 critical bugs, 3 high-severity issues, and 3 medium issues. Three fixes applied:

#### 1. Reply Backfill SQL Injection (QfJ2EZcc7lZwNgxj) — CRITICAL

**Bug**: `Apply Backfill Update` Postgres node used n8n template literal injection:
```
query: `={{ \`UPDATE ... SET payload_json = '\${$json.payload_json_sql}'::jsonb WHERE ghl_contact_id = '\${$json.ghl_contact_id}'...\` }}`
```
The Code node manually escaped with `.replace(/'/g, "''")`, but this is not safe against all SQL injection vectors (backslash/Unicode).

**Fix**: Changed Code node output to `JSON.stringify(nextPayload)` (no `''` escaping) and Postgres node to parameterized query:
```sql
UPDATE linkedin_connection_state
SET payload_json = $1::jsonb, metadata_json = $2::jsonb, ...
WHERE ghl_contact_id = $3
```
With `queryReplacement: "={{ [ $json.payload_json_sql, $json.metadata_json_sql, $json.ghl_contact_id ] }}"`.

#### 2. Follower DM Synthetic ID Inbound Check (pq7XVajNFnnwMUTr) — HIGH

**Bug**: `Process LinkedIn Followers` Code node passed `existing?.ghl_contact_id || 'linkedin:follower:' + providerId` to `hasInboundConversation`. For new followers (no Postgres row), `existing` was `undefined`, so the fallback synthetic ID hit GHL's conversation search API. GHL returned an error (no contact with that ID) → catch returned `{ blocked: true }` → **all new follower DMs were skipped**.

**Fix**: Only call `hasInboundConversation` when the Contact ID is a real GHL contact:
```js
var checkContactId = existing?.ghl_contact_id || '';
var inbound = checkContactId
  ? await hasInboundConversation.call(this, checkContactId)
  : { blocked: false, reason: '' };
```
New followers (no existing row) now skip the inbound check and allow the DM send (fail-open).

**Also fixed**: Added `ghlApiBaseUrl` and `ghlApiKey` to both Config node outer assignments AND Code node CFG object. Previously they were only present in a duplicate inner `parameters.parameters` object that n8n ignores.

#### 3. DM Sequence Backtick Published (d0tEtijajisIsYcs) — CRITICAL

**Bug**: Leading backtick had been removed from the draft in a prior fix session but the draft was never published — the active version still had the syntax error.

**Fix**: Published the corrected draft. Verified jsCode char[0] = ASCII 99 ('c').

### Unicode Encoding Fix — LinkedIn + Instagram Send Paths (2026-07-15)

**Bug**: Message templates contained Unicode smart punctuation (curly apostrophes `'`/`'` U+2018—U+2019, smart quotes `"`/`"` U+201C—U+201D, em-dashes `—`, ellipsis `…`, non-breaking spaces). Some already-stored templates also contained mojibake like `canΓÇÖt`. These multi-byte characters could get decoded as Latin-1/CP437 instead of UTF-8 when passing through the `JSON.stringify` → Unipile API chain, producing garbled text (e.g., `can't` → `canâ€™t` / `canΓÇÖt`).

**Fix**: Added/expanded `sanitizeMessage()` and `sanitizeTemplateRegistry()` across all Unipile send-capable message-template nodes. Stored templates are pre-sanitized when the Code node starts, and final outbound text is sanitized again immediately before `POST /chats` or `POST /users/invite`.

```js
function sanitizeMessage(text) {
  if (typeof text !== 'string') return text;
  return text
    .replace(/[\u2018\u2019]/g, "'")
    .replace(/[\u201C\u201D]/g, '"')
    .replace(/\u2013|\u2014/g, '-')
    .replace(/\u2026/g, '...')
    .replace(/\u00A0/g, ' ')
    .replace(/\u0393\u00C7[\u00D6\u00FF]/g, "'")
    .replace(/\u0393\u00C7[\u00A3\u00A5]/g, '"')
    .replace(/\u0393\u00C7[\u00F4\u00F6]/g, '-')
    .replace(/\u0393\u00C7\u00AA/g, '...')
    .replace(/\u00E2\u20AC[\u02DC\u2122]/g, "'")
    .replace(/\u00E2\u20AC[\u0153\u009D]/g, '"')
    .replace(/\u00E2\u20AC[\u201C\u009D]/g, '"')
    .replace(/\u00E2\u20AC[\u201C\u0094]/g, '-')
    .replace(/\u00E2\u20AC\u00A6/g, '...');
}
```

Applied in the message assembly line of each workflow before the Unipile `POST /chats` or `POST /users/invite` call:
```js
var message = sanitizeMessage(msgTemplate.replace(/\{first_name\}/gi, firstName));
```

| Workflow | ID | Node fixed |
|----------|-----|------------|
| LT - LinkedIn DM Sequence (Unipile) | d0tEtijajisIsYcs | Sync Connected from Unipile; Send DM Sequence Messages |
| LT - LinkedIn Follower DM Sequence (Unipile) | pq7XVajNFnnwMUTr | Process LinkedIn Followers |
| LT - GHL LinkedIn Connect Dispatcher (Unipile) | fXxw5lanZcDmUrst | Dispatch LinkedIn Requests |
| LT - Instagram DM Sequence (Unipile) | iCnY6ccdHhfJg3sf | Process Instagram Outreach |

**Verification 2026-07-15 follow-up**: live versions were active/published after patching. Final audit passed for smart/mojibake sanitizer coverage, template registry pre-sanitization where present, immediate send-time sanitization, and no remaining bad literal message text in the audited sender template nodes.

The local operator helper `local-scripts/suppress_linkedin_dms.py` provides one-command DM suppression (resolves LinkedIn profile via Unipile, finds GHL contact, tags + state-table-terminates in both ID paths).

### LinkedIn Regex Double-Escaping — Root Cause & Prevention (2026-08-19)

The 07-15 sanitizer/mojibake fix **recurred as a different failure** on 08-19. An MCP mutation on 08-11 (`3b70854e`) double-escaped regex literals in Code-node `jsCode`, producing **syntactically valid JavaScript that silently does the wrong thing**. This is distinct from the 07-15 mojibake (Unicode decode at write time): here the source characters were corrupted at edit time.

**Two distinct failures resulted (not one):**
1. `identifier()` `/^https?:\\\\/\\\\//i` → **crashed the Dispatcher at parse time** (`SyntaxError: Invalid regular expression flags`). No invites were sent at all from 08-11 → 08-18.
2. After the 08-18 REST PUT fixed only that crash regex, `sanitize()` `/[\\\\u2018\\\\u2019]/` matched literal `u`/`C`/`D` + digits instead of smart quotes (`u`→`'`, `C`→`"`, producing `"ameron co-fo'nder of Transparent e"om`), and `/\\\\{first_name\\\\}/gi` matched only a literal `\{first_name\}`, leaving `{first_name}` unreplaced. **Garbled invites were sent only from 08-18 00:15 → 08-19 04:45**, bounded by the 60/day cap — not since 08-11.

**Why the 08-18 REST PUT repair missed it:** it fixed the crash-causing `\\/` regex and the daily-cap logic via direct REST `PUT /workflows/{id}`, but the PUT inherited the two offending Code-node `jsCode` bodies unchanged because the corrupt regexes were still valid JS.

**Fix + prevention:** `scripts/linkedin/fix_linkedin_sanitize_double_escape.py` rewrites `\\uXXXX` → `\uXXXX` and `\\{` → `\{` idempotently (dry-run report by default). Re-publish after every run and verify `versionId == activeVersionId`. When editing any Code node with an MCP/API tool path, avoid `\\\\`-style literal escaping in character classes and `\\{` for placeholders; use character-class form `[/][/]` instead of `\/` where possible. Full narrative: `docs/sessions/2026-08-19-linkedin-double-escape-fix.md`.

### Unfixed Issues (acknowledged, not fixed today)

| Severity | Issue | Workflow(s) |
|----------|-------|-------------|
| Medium | Two different PIT tokens in use (`pit-2d2e...` vs `pit-b278...`) | Dispatcher vs others |
| Medium | `payload_json` grows unbounded per row due to `||` merge on every upsert | Connection State Upsert (Old7Z) |
| Low | Reply Backfill runs every 10 min (`*/10 * * * *`) — 144x/day | Reply Backfill (QfJ2) |
| Low | Relations Backfill can produce thousands of synthetic rows | Relations Backfill (VPiHf) |
| Low | `n8n/lt-linkedin-dispatcher.ts` SDK file is stale vs live workflow | Dispatcher (fXxw) |

## Emerald Email Campaign (Activated 2026-07-07)

Dispatches ~14,702 unenrolled Emerald contacts through GHL email sequences using 4 sender addresses with safe warmup pacing.

### Pipeline

```
Snapshot -> Postgres (Emerald_Campaign_Contacts) -> Dispatcher -> GHL tags + sender field
-> GHL "Enrollment Queue Entry" workflow -> Emerald Sequence -> Email
-> GHL Event webhook -> n8n Event Ingest -> Postgres (Email_Events)
```

### n8n Workflows

| Workflow | ID | Status |
|----------|----|--------|
| LT - Emerald Campaign Sender Release Dispatcher (Staged) | 8UXlpoMJnQ229AuG | Active, hourly |
| LT - Email Event Ingest | ZrqFN8qLKO8eVHDc | Active, webhook |
| LT - Emerald Campaign Snapshot -> Postgres Ingest (Staged) | 0jDKgG8VvmfyORQn | Active, webhook |

### GHL Workflows (all published)

- **5 Event automations**: WL - Event - Emerald Email Event Ingest - {Opened,Clicked,Bounced,Complained,Unsubscribed} -- POST to n8n webhook /lt-email-event-ingest
- **Bridge**: WL - Seq - Enrollment Queue Entry (v13)
- **12 Emerald sequences**: WL - Seq - Cannabis Ads Emerald - {Executives, Marketing, Finance, Retail and Sales} {MSO, SSO}, including the applicable P2 variants
- **Supporting**: WL - Seq - Cannabis Ads - Variant A/B, WL - Seq - Stop on Booked/Reply/Closed (published version 17), WL - Micro - Email Inbound/Outbound/Open Counter

### Current State

- 4 senders: cameron@livetransparent.{com,co,agency,org}, warmup Week 1 cap 300/day each
- Safety buffer: 5% of cap (15/sender), remaining: 285/sender/day
- Backlog: ~16,672 unreleased pending in `Emerald_Campaign_Contacts` (dispatcher candidateLimit=250, runs hourly)
- Email events flowing to Email_Events table within 3 min
- **2026-08-20**: release-log single-row write bug fixed (published `d6737e68`); 73 `apollo_august2026` imports enrolled into Executives MSO (all confirmed in GHL, marked released + release-logged)

### Sender Capacity (Week 1, per-day)

| Sender | Cap | Safety (5%) | Remaining |
|--------|-----|-------------|-----------|
| cameron@livetransparent.com | 300 | 15 | 285 |
| cameron@livetransparent.co | 300 | 15 | 285 |
| cameron@livetransparent.agency | 300 | 15 | 285 |
| cameron@livetransparent.org | 300 | 15 | 285 |

**Total: ~1,140/day** (4 × 285). Warmup stages: Week 2 = 400/day, Week 3+ = 500/day.

### Fixes Applied (2026-07-21)

- **CRITICAL: In-flight capacity double-counting**: `Estimate InFlight Due Today` queried across 3 days (`CURRENT_DATE, -2d, -4d`), inflating `inFlightDueToday` to 285/sender and blocking all dispatches. Changed to `release_date = CURRENT_DATE` — counts only today's releases.
- **Known unfixed**: Dispatch code uses `doHttpRequest` wrapper (HTTP 400 risk in task-runner loops). Write Release Log uses template-literal SQL injection. These are low-risk for Emerald's current low volume but **must** be migrated to match DAN's patterns (`this.helpers.httpRequest` direct calls + parameterized queries) before scaling.

### Reply Suppression Repair (2026-07-26)

- `WL - Seq - Stop on Booked/Reply/Closed` (`3dd33ec4-d8c2-40c6-b72f-d1cba57b8c39`) had the correct Email reply trigger, but its removal action only targeted the legacy Variant A/B workflows. It did not remove contacts from the Emerald sequences.
- Added all 12 Emerald sequence workflows, including P2 variants, to the removal action through the GHL UI and published version 17.
- n8n `LT - Email Event Ingest` is reporting-only and does not suppress sequence enrollment.
- For the affected Christy Essex contact, removed `seq enrolled - emerald` and `seq emerald - executives sso` while preserving Warm/MQL state and the opportunity.

### Postgres Tables

| Table | Rows | Notes |
|-------|------|-------|
| Emerald_Campaign_Contacts | 20,238 | 16,672 pending, 3,566 released (incl. 73 `apollo_august2026` executives_mso released 2026-08-20) |
| Emerald_Release_Log | 16,154 | Dispatched contacts by sender |
| Email_Events | growing | From 5 GHL event automations |

## DAN Email Campaign -- Brands and Dispensaries (LIVE 2026-07-10, Backfilled 2026-07-13)

### Dispatcher

| Workflow | ID | Status |
|----------|----|--------|
| LT - DAN Campaign Sender Release Dispatcher (Staged) | toUG1yPDmFG48KEP | Active (dryRun=false), every 30 min |

**Pipeline**: Schedule Trigger -> Config -> Ensure Release Log Table -> Fetch DAN Candidates -> Dispatch + Queue (DryRun Safe) -> Only Queued (filter) -> Write Release Log (with Summary branch)

**Config**: dryRun=false, candidateLimit=85, senders=cameron@livetransparent.{com,co,agency,org} (round-robin), senderFieldName=marketing_sender_email

**Fixes applied 2026-07-14:**
- Schedule changed from hourly to every 30 min (was only hitting 600/day, needed 1200+)
- Added `await new Promise(r => setTimeout(r, 250))` between each contact's GHL API calls to prevent rate limiting (was seeing 20-40% `error_fetch_contact` on early runs)
- candidateLimit increased from 50 to 65 to compensate for ~10 recurring DNC contacts per run (BRĒZ, Teal Cannabis, AYR Wellness, Nova Farms — have `do not contact` in GHL but stale data in report_raw_ghl_contacts)

**Fixes applied 2026-07-15 (code/logic audit):**
- **Brand starvation**: Changed `ORDER BY epc.source_list, epc.id ASC` → `ORDER BY RANDOM()` so brands and dispensaries interleave proportionally instead of brands always filling the slot limit first
- **HTTP wrapper**: Removed `doHttpRequest` wrapper function and deprecated `$httpRequest` — all HTTP calls use `this.helpers.httpRequest(options)` directly
- **Sender rotation**: Added 4-sender pool (`cameron@livetransparent.{com,co,agency,org}`) with round-robin via `ci % senders.length`, matching Emerald's warmup pattern
- **Jitter**: Delay randomized to `250 + Math.random() * 250`ms to prevent thundering herd on GHL API recovery

**Fixes applied 2026-07-21 (full audit + hardening):**
- **CRITICAL: Release log crash on skipped_dnc**: `Only Queued` filter passed all non-summary items to `Write Release Log`, but `skipped_dnc` items lacked `enrollment_tag` which is `NOT NULL` in the table. Every daytime run errored on the INSERT. Tags WERE being applied to GHL, so emails were sending, but tracking was broken and the report showed `0 emails sent`.
  - Fix #1: Changed `Only Queued` filter from `status !== "summary"` to `status === "queued"` so only valid items reach the INSERT.
  - Fix #2: Expanded filter to `s !== "summary" && s !== "skipped_incomplete"` — passes `queued`, `skipped_dnc`, and all error items now that they carry `enrollment_tag`.
- **CRITICAL: SQL injection in Write Release Log**: Template-literal `.replace(/'/g, "''")` pattern replaced with parameterized `$1..$10` placeholders and `queryReplacement` array. Same anti-pattern previously fixed in LinkedIn Reply Backfill and Apollo Sheet First.
- **Self-healing pipeline**: `Dispatch + Queue` code now outputs `enrollment_tag`, `first_name`, `last_name`, `company_name` in ALL non-summary items (`skipped_dnc`, `error_fetch_contact`, `error_set_sender`, `error_add_tag`). This means every outcome — success or skip — gets tracked in `DAN_Release_Log`, permanently excluding that contact from future SQL candidate fetches. Pool self-cleans within a few dispatch cycles.
- **Candidate limit**: 65 → 85 to compensate for backfilled/skipped contacts, targeting higher throughput.

**Fixes applied 2026-08-20 (release-log single-row bug):**
- **CRITICAL: Only 1 release-log row persisted per run**: `Build SQL - Write Release Log` used `mode: runOnceForAllItems` with `$json` (first item only), so even when multiple contacts were queued/skipped, exactly 1 `DAN_Release_Log` row was inserted. Unlogged contacts were re-selected on the next run. Fixed by iterating `$input.all()` and setting `queryBatching: "independently"` on the Postgres node. Published `f8f29288-45d9-4f35-81a6-a60d2b54ad11` (versionId == activeVersionId). DAN pool is currently exhausted (last log entry 07-22), so the fix is dormant until candidates reappear.

**Candidate freshness (3-layer defense):**
1. **SQL dedup**: `NOT EXISTS (SELECT 1 FROM "DAN_Release_Log" r WHERE r.contact_id = epc.ghl_contact_id AND r.campaign = epc.source_list)` — any contact with a release log entry is excluded
2. **SQL tag filter**: `(lt.tags_raw IS NULL OR NOT (lt.tags_raw ILIKE '%seq enrolled - dan%'))` — stale report data catches already-enrolled contacts
3. **Live GHL check**: Per-contact `GET /contacts/{id}` + `isBlocked()` tag check — blocks contacts with `do not contact`, `do not nurture`, `unsubscribed`, `opted out`, `seq enrolled - dan`

All three layers feed into the release log: any contact that passes the SQL but gets live-skipped is recorded with `status: 'skipped_dnc'` (with enrollment_tag) and won't reappear.

**Dispatch performance (2026-07-21):**
- Max theoretical: 85 contacts × 24 runs/day = 2,040/day (Mon-Sat 8 AM ET to 5 PM PT window)
- After fix, first dispatch window will self-clean: previously-tagged contacts get release-logged as `skipped_dnc`, fresh contacts get `queued`
- Email events flow: GHL → n8n Email Event Ingest (`ZrqFN8qLKO8eVHDc`) → Postgres `Email_Events` table → Daily Rollups → Executive Summary
- Report dashboard (`emailsSent`/`emailsOpened`/`emailsClicked`) will populate as the release log backfills and daily rollups ingest

**Enrollment tags applied**:
- Brands: Enrollment Queue - DAN - Brands
- Dispensaries: Enrollment Queue - DAN - Dispensaries

**Deduplication**: Per-contact + per-campaign via DAN_Release_Log table (UNIQUE on contact_id, campaign). Every outcome (queued, skipped_dnc, errors) writes to the release log, permanently excluding the contact from future candidate fetches.

**DNC/unsubscribe protection** (three layers — see "Candidate freshness" above for full details):
1. SQL-level: filters report_raw_ghl_contacts.tags_raw for do not contact, do not nurture, unsubscribed, opted out, seq enrolled - dan
2. Per-contact live GHL check: GET /contacts/{id} before dispatching
3. Release log dedup: any contact with a DAN_Release_Log entry (any status) is excluded from SQL candidates

### ghl_contact_id Backfill (2026-07-13)

The import workflows (`LT - Brands Pool to Postgres + Sheets`, `LT - Dispensaries Pool to Postgres + Sheets`) set `ghl_contact_id = NULL`. The DAN dispatcher requires a non-null `ghl_contact_id`, so it found zero candidates despite contacts existing in GHL.

**Fix**: Backfilled 13,705 `ghl_contact_id` values from GHL export CSVs using three match passes:
1. Email match (lower+trim): +4,629
2. Phone match (digit-stripped): +5,691
3. Name+company match: +3,385

**Result**: 13,755 with IDs (3,645 brands / 10,110 dispensaries), 113 still missing (not in exports). **5,373 now eligible for DAN dispatch**.

**Export CSVs used** (delete after use):
- `Export_Contacts_brands pool_Jul_2026_5_24_AM.csv`
- `Export_Contacts_Dispensaries pool_Jul_2026_5_28_AM.csv`

### GHL Sequence Tags

| Tag | Purpose |
|-----|---------|
| Enrollment Queue - DAN - Brands | Triggers Brand email sequence |
| Enrollment Queue - DAN - Dispensaries | Triggers Dispensary email sequence |
| dan_seq_completed | Finished all 5 emails |
| dan_seq_no_engagement | No opens on emails 1-3 |
| dan_seq_replied_or_booked | Replied or booked meeting |

### GHL Workflows (all published)

- DAN - Brands Sequence (5d25147c-cd63-4c4f-ba49-a0e62c53ee0c)
- DAN - Dispensaries Sequence (ec24cbb8-bd0b-4e6e-8607-d93886a02034)
- DAN - Stop on Reply or Booked (d7ff2fc2-cdc2-4952-afa7-71cd9edfc490)

### Deck Download Automations

- WL - Micro - DAN Brand Deck Download -- trigger link bNK7txDSQJkvrgmmH9aZ -> tag/source metadata -> Warm; no SDR assignment before the Janvi qualification gate
- WL - Micro - DAN Dispensary Deck Download -- trigger link DDPOwxFCexuf3cYGOAPt -> tag/source metadata -> Warm; no SDR assignment before the Janvi qualification gate
- 3x open handling via WL - Micro - Email Open Counter + Assignment to Jason (42aa5940) is an engagement signal only; it must not independently assign an SDR or promote a Warm record

### GHL Email Folders

| Folder | ID |
|--------|-----|
| Brands | 6a4f6b06a3e9bfb4f9ebe8ad |
| Dispensaries | 6a4f6b128c6f614ebf8ba9e9 |

### Signature (all templates)

Cameron Karkut
Co-Founder / Head of Sales and Strategy
714-469-6406
LiveTransparent.com

## Reporting System

### Data Pipeline (4 Layers)

```
Raw Ingest → Attribution Bridge → Daily Rollups → Executive Summary API (GET /lt-report-executive-summary)
```

### Raw Ingest Workflows

| Workflow | ID | Schedule | Target Table |
|----------|----|----------|--------------|
| GHL Daily Leads Ingest | osIJOgBmWITF5Yuv | Every 60 min | `report_raw_ghl_contacts` |
| GHL Daily Sales Ingest | aYT5oHcgmBALzHy5 | Daily | `report_raw_ghl_opportunities` |
| GA4 Daily Ingest | 6pCSGzFmrMDFL5Yq | Daily (24h) | `report_raw_ga4_sessions` |
| GSC Daily Ingest | xHqmCC1vOeZ11gCd | Daily | `report_raw_gsc_queries` |
| GHL Daily Calls Ingest | SqNQ0BYaTdcqyt1l | Every 4 hr | `report_raw_ghl_calls` + `outcomes` |
| GHL Daily Appointments Ingest | yWZVSqEcjTbMT3kG | Daily | `report_raw_ghl_appointments` |
| GHL Daily Social Ingest | QZoqCaTwDhbym80O | Daily | `report_raw_ghl_social_posts` |

### GHL Leads Ingest Rate-Limit Guard

`LT - GHL Daily Leads Ingest` (`osIJOgBmWITF5Yuv`) uses direct `this.helpers.httpRequest` calls in `Fetch + Normalize Leads`. Do not restore the `doHttpRequest`/`$httpRequest` wrapper pattern. GHL contact pagination retries HTTP 429 responses up to four attempts, waits 500 ms between pages, and must send both `startAfter` and `startAfterId`. Repeated pages and missing/stalled cursors fail closed. Published version `d29b7af9-0b69-4fc7-a53c-c23dd24b0825` uses an atomic direct-`pg` transaction for contacts plus sync/watermark/health metadata. Controlled execution `742843` persisted 500/500 distinct contacts with healthy metadata.

### Bridge & Rollup Workflows

| Workflow | ID | Status |
|----------|----|--------|
| GA4 Traffic Rollup Bridge | 0P2AZcQYWYZjXbRi | Active |
| GSC Rollup Bridge | fOVBHwti9rC3qrLV | Active |
| Report Attribution Bridge | Y0TU7Il71JswxOBp | Active (daily, 90-day window) |
| Report Daily Rollups | EUeOiRttoVLQ9zF9 | Active (daily, 90-day backfill) |
| Report Pipeline Velocity | iFfwh0jpYUZoDhDR | Active |

### API & Frontend

| Workflow | ID | Status |
|----------|----|--------|
| Report Executive Summary API | Bukc0mgOD2r7V6ED | Active (webhook GET) |
| Report Outgoing Calls Detail | VXFHc8IrF9DDEEdj | Active (webhook GET; published version `d004556d-0b11-4a86-8827-f8f58a1eeee3`) |
| Report QA and Alerts | M5mXcDTFSko6EdHb | Active |
| Report Config Sync | aomO3Z4AXJIgEvvN | Active |
| Report Publish Refresh | 3gXztCnBEN6sGINb | Active |
| Report Postgres Bootstrap Apply | 3XHThUiUSNa4sTb9 | Active |
| LT - MQL Tag Event Ingest | U9oc2tZRsr4zq6IM | Active webhook (`POST /webhook/lt-mql-tag-event`, secret header; logs `mql` tag adds to `mql_tag_events`) |

### Executive Summary Runtime Recovery (2026-08-12)

- The report regressed to zeroes because the Executive Summary webhook returned an empty HTTP 200 after PostgreSQL rejected `v.report_date`; `report_stage_velocity_summary` stores `computed_at`, not `report_date`.
- Corrected the stage-velocity filter to `DATE(v.computed_at) BETWEEN $1::date AND $2::date`.
- The query then completed, but the response still exceeded nginx's 60-second proxy window because `Shape Response` synchronously called the Campaign Channel Summary endpoint even though the frontend already fetches that endpoint in parallel.
- Removed the redundant internal HTTP lookup and projected the existing `email_direct` totals/rates into the summary response. Final active version is `d177a923-da94-43ac-ac97-dbba1a664ab4` with `versionId == activeVersionId`.
- Verification: current 30-day summary returned HTTP 200 with a 33.7 KB body in 19.9 seconds; the prior equal-length period returned HTTP 200 with a 22.1 KB body in 12.3 seconds. Browser verification rendered 1,847 visits, 160 contacts, 4,368 opportunities, 5,743 email opens, and 362 email clicks.

### Executive Report Accuracy Audit (2026-08-25)

Full 30d cross-check of the Executive Summary, Campaign Channel Summary, and Outgoing Calls against source Postgres tables. Most figures were already exact (`emailsSent`/`opened`/`clicked`/`bounced`/`unsubscribed`, Vapi 50 calls by disposition + campaign, LinkedIn 44 invites/26 DMs/4 replies, Instagram 204 DMs, social posts/account stats, appointments 4, calls 828, Meta ads spend/clicks/impressions, MQL summary, SMS). Fixed these reporting bugs:

- **Raw pipeline/stage IDs exposed** — `pipelineDropoff` showed Partnership pipeline as `tQkFYrHjALgoLz6oq0uz`; `stageDropoff`/`stageVelocity`/`opportunityStageBreakdown` showed raw stage IDs (`91517911…`=Sales Outreach Qualified, `16fb26a2…`=Warm vapi_qualified, `67d47ef7…`=Warm New_Not Qualified, etc.). Added the full canonical pipeline/stage name CASE mappings (incl. Partnership Pipeline `tQkFYrHjALgoLz6oq0uz` and its 4 stages, plus `91517911`, `67d47ef7`, `0741e8b5`, `967292f9`, `16fb26a2`, `5112b5c8`, `268ed432`) to: Exec Summary `Build Query` (opportunity_snapshots CTE), Daily Rollups `Build Rollup SQL` (both tmp_report_opps and opp_transitions CASE blocks), and Pipeline Velocity `Build Velocity SQL` (timeline CTE). Re-ran the rollup and velocity workflows; stage tables now fully resolved. Exec Summary `stageVelocity` filter changed from `DATE(computed_at) BETWEEN window` to `computed_at = MAX(computed_at)` so it always shows the latest velocity compute (was going to return empty after a fresh compute lands outside the window).
- **Campaign Channel Partnership email undercount** — `Partnership emails email_sent` showed 59 (COUNT DISTINCT contacts) while the release log has 233 sent emails (59 contacts × 4 steps); Exec Summary correctly counted 233. Changed `email_sent` to `COUNT(*)` for DAN/Emerald/Partnership in the Campaign Channel Query so it matches the Exec Summary definition (release-log rows = emails sent). Now 2692 total on both.
- **Email rates were hardcoded `NULL`** — Exec Summary now computes cohort-based `emailOpenRate`/`emailClickRate`/`emailBounceRate` = unique recipients opened/clicked/bounced among the window send cohort / unique sent recipients (e.g. 44.6% / 11.4% / 4.7% for 30d). The `email_direct` CTE gained `emails_sent_unique`/`emails_opened_unique`/`emails_clicked_unique`/`emails_bounced_unique` (opens/clicks/bounces restricted to the window send cohort to avoid inflation from historical sends opening in-window). `emailRateBasis` = `unique_recipient_rates_over_window_sent_cohort`.
- **`salesQuality.topLossReason` mislabeled** — returned a stage name (e.g. "New") instead of a loss reason; renamed to `topLossStage` (GHL has no structured loss-reason field captured).
- **MQL tag ledger (2026-08-25)**: the business counts MQLs by the `mql` **tag being added** (e.g. past week), not by the Warm Qualified (MQL) stage. GHL does not expose tag-add timestamps and the hourly contact snapshot can't reconstruct them, so we built a forward-looking ledger: `mql_tag_events` table (UNIQUE `(contact_id, tag)`, first-add wins) + active workflow `LT - MQL Tag Event Ingest` (`U9oc2tZRsr4zq6IM`, POST `/webhook/lt-mql-tag-event`, requires `X-LT-MQL-Tag-Secret` from its Config node; 403 on unauthorized/missing contact, `duplicate` on re-add). **Pending operator step**: create the GHL automation `WL - MQL Tag Ledger` (Contact → Tag Added → `mql` → webhook POST with the secret header and `{"contact_id":"{{contact.id}}",...}` body) — runbook: `docs/sessions/2026-08-25-mql-tag-ledger.md`. Exec Summary `mqlSummary` now also returns `taggedMqlsTotal`/`taggedMqlsThisPeriod`/`taggedAsOfDate`/`tagBasis: mql_tag_events_ledger` (0 until events flow; forward-looking only). The 443 current `mql`-tagged contacts are noisy (mailer-daemon bounces, `not qualified`) — the ledger records whatever GHL fires.
- **Workflow version notes**: Exec Summary `Bukc0mgOD2r7V6ED` active `f49277bb-dc64-4855-933e-c38e53991bff`; Daily Rollups `EUeOiRttoVLQ9zF9` active `ddded785-2d31-4818-8ced-8a9c881a689f`; Pipeline Velocity `iFfwh0jpYUZoDhDR` active `43515531-dd9f-4462-bbe6-e58e321ab130`; Campaign Channel Summary `MvPLbUAN9IIQikxb` active `6ec148ff-6f1c-42b5-8b72-157d40d0a74a`; MQL Tag Event Ingest `U9oc2tZRsr4zq6IM` active `298be9d4-692b-4787-9bcb-a7f5de138e8c`. All `versionId == activeVersionId` after the REST PUT (PUT auto-publishes; the Query Summary postgres credential was restored to `pgAzUqpwOiGkGXzO` after the first PUT stripped it).

**Remaining data-source issues (need operator action, not logic fixes):**
- **GA4 credential is expired** — `LT - GA4 Daily Ingest` (`6pCSGzFmrMDFL5Yq`) has errored on every hourly run since 2026-08-14 (`The credential "Google Analytics account" needs to be reconnected`). `report_raw_ga4_sessions`/daily summary sessions freeze at 08-13, so `traffic` is UNDERCOUNTED (the 30d window's last ~13 days are missing). The `health` section already flags GA4 as stale. Reconnect the Google OAuth credential in n8n.
- **Pipeline Velocity schedule stopped firing** — active but 0 executions since ~08-07; data was stale until the manual re-run above. Verify the 24h Schedule Trigger is registering.
- **GSC ingest stale** since 08-07 (low volume: 1 click/41 impressions in window).
- **Sales Ingest snapshot gap 08-12…08-20** — no `report_raw_ghl_opportunities` snapshot rows those days (resumed 08-21), so stage-movement history for that span is absent.
- **`poolDistribution` always 0** — the GHL Leads Ingest snapshots only ~500 contacts, so pool tags (`brands_pool` 3k+, `dispensaries_pool` 7k+) never appear. Not a logic bug; data-coverage limitation.
- **`metaAttribution` empty / Meta leads 0** — no contacts in the 500-row snapshot carry Meta UTM attribution; genuine 0 given current data coverage.

### MQL / Company Sync

| Workflow | ID | Status |
|----------|----|--------|
| LT - Company MQL Google Sheets Sync | 9Y3Kedm768kkwwSV | Active (daily 6am ET) |

### Executive Report Data Sections (2026-07-21)

The `Report Executive Summary API` (`GET /webhook/lt-report-executive-summary?range=30d`) returns these top-level keys:

| Section | Source | Description |
|---------|--------|-------------|
| `traffic` / `leads` / `sales` | `report_daily_summary` | GA4 sessions, GHL contacts created, closed-won count |
| `summary` | `metric_summary` CTE | Full nested metrics: funnel rates, coverage, revenue, calls, timezone |
| `channelBreakdown` | `report_channel_daily_summary` | Top 8 channels by sessions/leads/opps |
| `utmBreakdown` | `report_utm_daily_summary` | Top 15 UTM source/medium/campaign combos |
| `metaAttribution` | `report_bridge_traffic_to_lead` | Meta (Facebook/Instagram) attribution |
| `pipelineDropoff` | `report_pipeline_daily_summary` | Per-pipeline stage counts + moved-in/moved-out |
| `stageDropoff` | `report_stage_daily_summary` | Top 10 stages by movement |
| `stageVelocity` | `report_stage_velocity_summary` | Avg days per stage |
| `opportunityStageBreakdown` | `report_raw_ghl_opportunities` | Active/worked/stage-mover counts per pipeline+stage |
| `socialPosts` | `report_raw_ghl_social_posts` | Post totals and engagement (likes/comments/shares/saves/reach/impressions; reads plural and singular keys from `insights` and preserved post payloads since 2026-08-04) |
| `health` | `report_source_health` | Source system health statuses |
| `callStatusBreakdown` | `report_raw_ghl_calls` | Top 10 call statuses by direction |
| `callOutcomeBreakdown` | `report_raw_ghl_call_outcomes` | Top 12 dispositions by direction |
| `appointments` | `report_raw_ghl_appointments` | Top 8 appointment statuses |
| **`emailsSent` / `emailsOpened` / `emailsClicked` / `emailsBounced`** | `report_daily_summary` + `Email_Events` + Release Logs | Email campaign metrics (added 2026-07-21) |
| **`emailOpenRate` / `emailClickRate` / `emailBounceRate`** | Computed from above | Email engagement rates (added 2026-07-21) |
| **`linkedinFunnel`** | `linkedin_connection_state` | ready→requested→connected→DM active→completed (added 2026-07-21) |
| **`vapiCampaignBreakdown`** | `voice_call_attempt` JOIN `voice_call_queue` | Per-campaign call totals, answered, qualified, booked (added 2026-07-21) |
| **Outgoing Call Detail** | `voice_call_attempt` JOIN `voice_call_queue` + latest `report_raw_ghl_contacts` snapshot | Seven completed days of paginated Vapi call rows with disposition, duration, contact ID/name fallback, campaign, first-attempt flag, and signed recording URL |
| **`vapiQueueDistribution`** | `voice_call_queue` (status=pending) | Pending queue by campaign (added 2026-07-21) |
| **`mqlSummary`** | `report_raw_ghl_opportunities` (stage IDs) + `mql_tag_events` (tag ledger) | Total MQLs (ever in Warm Qualified (MQL)), converted-to-SQL (also in Sales Outreach pipeline), current MQLs awaiting sales, entered/converted in the selected window, plus `taggedMqlsTotal`/`taggedMqlsThisPeriod` from the `mql` tag-add ledger |
| **`sqlContacts`** | `report_raw_ghl_contacts` (tag search) | Contacts with SQL tag (added 2026-07-21) |
| **`poolDistribution`** | `report_raw_ghl_contacts` (tag counts) | brands_pool, dispensaries_pool, vapi brand/dispensary (added 2026-07-21) |

### Stage Name Resolution (2026-07-21 Fix)

GHL stage names (`pipeline_stage_name`) are NULL in `report_raw_ghl_opportunities`. The report resolves stage names by falling back to `pipeline_stage_id` with a CASE mapping matching the Daily Rollups workflow. Pipeline names use the same ID-based resolution. This fixes `stage_movers` (was 0, now 93), `meetingsBooked`, and `closedWonCount` which previously depended on NULL stage name fields.

### report_daily_summary New Columns (2026-07-21)

| Column | Source |
|--------|--------|
| `emails_sent` | `DAN_Release_Log` + `Emerald_Release_Log` (release_date) |
| `emails_opened` | `Email_Events` (event_type='opened') |
| `emails_clicked` | `Email_Events` (event_type='clicked') |
| `emails_bounced` | `Email_Events` (event_type='bounced') |
| `emails_unsubscribed` | `Email_Events` (event_type='unsubscribed') |
| `emails_complained` | `Email_Events` (event_type='complained') |

### Executive Report Campaign Improvement Plan (2026-08-08)

The Executive Report at `https://reports.livetransparent.com` (build `2026-08-17-v26-social-reporting-accuracy`) has campaign/channel filters, separate Vapi filters, LinkedIn and Instagram ledger metrics, campaign drill-downs, comparison view, SMS delivery diagnostics, campaign opportunity counts, resolved GHL stage names, explicit Social Planner placement definitions, and responsive wide-table containment. The following remaining improvements complement the GHL Native Report:

**High Priority — Campaign Detail Page:**
1. **Per-campaign funnel metrics** — Each campaign row (DAN, Emerald, Partnership Emails, Partnership LinkedIn, Vapi Brand, Vapi Dispensary, SMS) should expand to show:
   - **Email campaigns**: Sent, delivered, opened, clicked, replied, bounced, unsubscribed with rates
   - **LinkedIn campaigns**: Invites sent, accepted, connected, DM sent, replied with rates
   - **Vapi campaigns**: Calls attempted, answered, voicemail, qualified, booked with rates
   - **SMS**: Sent, delivered, failed, replied with rates
2. **Campaign comparison table** — Side-by-side view of all active campaigns with key metrics and period-over-period deltas
3. **Partnership cross-channel view** — Combined email + LinkedIn funnel for partnership contacts showing overlap

**Medium Priority — Pipeline Integration:**
4. **Pipeline + Campaign bridge** — Show opportunities created per campaign source, with stage distribution and conversion rates
5. **Vapi-to-pipeline conversion** — Track Vapi qualified → MQL → Sales Outreach conversion rates
6. **LinkedIn-to-meeting rate** — Connected → replied → meeting booked funnel

**Low Priority — Data Quality:**
7. **Source health dashboard** — Per-campaign data freshness indicators (last ingest time, row counts, error rates)
8. **Campaign cohort analysis** — Time-to-first-action metrics per campaign (days to first open, days to first reply)
9. **SMS failure breakdown** — The GHL report shows 33/70 SMS failed (47%). Add a root-cause investigation widget (invalid numbers, rate limits, carrier blocks)

**Data Sources Available:**
| Data | Table/Workflow | Current Status |
|------|---------------|----------------|
| DAN + Emerald email metrics | `Email_Events`, `DAN_Release_Log`, `Emerald_Release_Log` | Already flowing into `report_daily_summary` |
| Partnership email + LinkedIn | `partnership_release_log`, `partnership_linkedin_connection_state`, `linkedin_activity_events` | Already in Campaign Channel Summary |
| Vapi call outcomes | `voice_call_attempt` JOIN `voice_call_queue` | Already in `vapiCampaignBreakdown` |
| SMS delivery | `SimpleTexting_Campaign_Event_Log` | Available via campaign_key routing |
| LinkedIn DM state | `linkedin_connection_state` | Already in `linkedinFunnel` |
| Per-campaign opportunity attribution | All opportunities have pipeline + tag affiliation | Needs bridge CTE added to Executive Summary API |

**Implementation Notes:**
- The `LT - Report Campaign Channel Summary` (`MvPLbUAN9IIQikxb`) endpoint already provides campaign-level aggregates; expand it with the detail fields listed above
- The frontend at `reports/embed/executive/index.html` already supports campaign/channel toggles; add a drill-down panel
- Add a `/webhook/lt-report-campaign-detail?campaign=<key>&range=<period>` endpoint that returns the per-campaign detail view
- For SMS, reconcile `SimpleTexting_Campaign_Event_Log` delivery/failure rates with the GHL-native SMS widget data (33/70 failure rate needs investigation)

### Voice Dialer Fix (2026-07-21)

`LT - Voice Agent V1 Outbound Dialer (Vapi)` (`r7UjWLndmc6EqEUW`): `GHL - Create Call Note` node now has `onError: continueRegularOutput`. Previously the dialer errored on every run because deleted GHL contact `AX3wfQNpRwm6DG0HgUE2` (still in `voice_call_queue`) caused a 400 on the note creation endpoint. Calls go out successfully; note failure is cosmetic.

## Partnership Marketing Pipeline (Infrastructure Live, Outbound Live 2026-07-31)

The original 131 content partnership contacts remain enrolled. A separate August 26 cohort added 404 new contacts and 427 actionable contacts to both partnership selectors. Two parallel sequences from Cameron's accounts: a 4-step email sequence and a 4-step LinkedIn DM cadence. All infrastructure isolated from DAN/Emerald (separate Postgres tables, workflows, GHL pipeline).

### Pipeline

- **GHL Pipeline**: `Partnership Pipeline` (`tQkFYrHjALgoLz6oq0uz`) — New Partner Lead → Contacted → Proposal Sent → Closed
- **Contacts**: original 131 contacts plus 404 new August 26 contacts; the 404 new contacts are identified by `august_26_partnership_contact`
- **Tags**: `partner_candidate_email`, `partner_candidate_linkedin`, `august_26_partnership_contact`, `partner_email_queued`, `partner_linkedin_requested`, `partner_email_sequence_completed`, `partner_replied`, `partner_not_interested`, `partner_do_not_contact`
- **GHL API key**: configured in the live dispatcher Config nodes and Reply Poller runtime; value intentionally omitted from documentation
- **14 contacts excluded** from original CSVs due to wrong company/email domain mismatches — awaiting corrections

### Email Templates

4 templates in GHL folder `Partnership Email Campaign` (`6a6b768aa43d24a7ce1514f1`):

| # | ID | Name |
|---|----|------|
| 1 | 6a6b8dfba3c113f06dee9e26 | Partnership - Email 1: Initial Outreach |
| 2 | 6a6b8e05264ebab67f776e9c | Partnership - Email 2: Follow Up |
| 3 | 6a6b8e06a3c113f06dee9ee6 | Partnership - Email 3: Value Proposition |
| 4 | 6a6b8e07a4bd9f4493fc536e | Partnership - Email 4: Breakup |

**Important**: The Email Dispatcher sends via `POST /conversations/messages` with inline HTML, not through GHL templates. The Code node HTML is the canonical message content; templates exist for open tracking and deliverability.

### Postgres Tables

| Table | Purpose |
|-------|---------|
| `partnership_linkedin_connection_state` | Mirrors `linkedin_connection_state` with `source_key = 'partnership'` |
| `partnership_release_log` | Tracks every sent email. UNIQUE on `(ghl_contact_id, email_step)`. |

### n8n Workflows

| Workflow | ID | Status | Role |
|----------|----|--------|------|
| LT - Partnership Email Dispatcher | Xshck23cKo1yXL9D | Active | 60/day, 11am ET Mon-Fri, 2-weekday intervals |
| LT - Partnership LinkedIn Dispatcher | crKIsaL5k3YBfqDZ | Active | 30 connection-request/day, 3pm CT Mon-Fri, state seeding + atomic claim |
| LT - Partnership LinkedIn DM Sequence | nspggypNF245xzeL | Active | 4-step DM, 2-weekday intervals |
| LT - Partnership Reply Handler | mRDw57IHtnQe4wOo | Active webhook | `/webhook/lt-partnership-reply` — tags `partner_replied`, creates opportunity, Slack alert, and writes a `replied` event to `Email_Events` |
| LT - Partnership Reply Poller | 0SQ7tTk03okegp9V | Active | Every 5 min — polls GHL for inbound email replies via `GET /conversations/search`, triggers Reply Handler |
| LT - Partnership Bulk Import | zmrYrUjVcyXaS7PJ | Active webhook | `/webhook/lt-partnership-bulk-import` |
| LT - Partnership LinkedIn URL Update | ew6uQQnAjgCbjeGn | Active webhook | Set LinkedIn URLs on LinkedIn-only contacts |

### LinkedIn Workflow Patches

3 existing LinkedIn workflows query `partnership_linkedin_connection_state` in addition to main table:

| Workflow | ID | Patch |
|----------|----|-------|
| LT - LinkedIn Connection Acceptance Checker | 3ttEvr5NMcQCS4Hp | SQL UNION + `source_table` routing |
| LT - LinkedIn Reply Backfill | QfJ2EZcc7lZwNgxj | UNION ALL + separate Update node |
| LT - LinkedIn Unipile New Messages | 7o5EBdvwAuIaWW7k | UNION ALL + routing + separate update node |

### Remaining

- **August 26 shared-email records**: resolve the two skipped shared-email groups before adding them to email outreach.
- **August 26 campaign monitoring**: monitor the next scheduled email and LinkedIn dispatcher runs; confirm release-log/state writes and verify that no Vapi selector tags appear on the cohort.

- **GHL Custom Report**: Partnership widgets are configured and verified in native report `6a67dce4a51a4360c60963a3`; MQL, owner, and stage-split widgets remain limited by the builder. PIT REST access cannot mutate widget layouts; do not guess undocumented report-builder endpoints.
- **Re-import 14 excluded contacts** after corrected company names provided
- **Outbound activation**: Approved and enabled 2026-07-31. Email Dispatcher, LinkedIn Dispatcher, and LinkedIn DM Sequence now use `defaultDryRun=false`; their published active versions are `6b7490a9-05d8-44e1-8f94-3c4427a7f969`, `29089175-1b37-4271-8b03-d4722b809692`, and `3bd0b759-4740-4e67-85ef-9540bf31c08e`. The dispatcher seeds 127 partnership `ready` state rows before queue fetch.
- **Live workflow verification 2026-07-31**: All 7 partnership workflows are active and published. Fixed the Email Dispatcher schedule to `0 11 * * 1-5` America/New_York, the LinkedIn Dispatcher schedule to `0 15 * * 1-5` America/Chicago, and the LinkedIn DM schedule to `0 12 * * 1-5` America/Chicago; prior interval definitions were firing hourly. Fixed the DM terminal completion scan to include `sequence_step <= 4` and corrected the shared LinkedIn Acceptance Checker state-upsert header. Safe manual smoke executions `281269` (email), `281268` (LinkedIn), and `281270` (DM) succeeded with outbound dry-run enabled.
- **Live outbound activation 2026-07-31**: Explicit user approval changed all three outbound `defaultDryRun` controls to `false`; all three drafts were published and verified with `versionId == activeVersionId`. Do not manually execute these workflows unless intentionally sending an additional live batch; scheduled runs now send real outreach.
- **Release-log single-row bug fixed 2026-08-20**: `Build SQL - Write Release Log` used `mode: runOnceForAllItems` with `$json` (first item only), so each run persisted exactly 1 `partnership_release_log` row. Actively manifesting: run `766371` (2026-08-19) sent 3 step-4 emails but logged only 1 (robert@herb.co), leaving the other 2 contacts unlogged for their step → duplicate re-send risk. Fixed by iterating `$input.all()` + `queryBatching: "independently"` on the Postgres node; published `2663f32b-4e45-4a5c-9b7f-e9db58ff9bc4` (versionId == activeVersionId). Functional test (`test_workflow` execution `769961`) confirmed 3 sent items → 3 release-log writes; the 3 live test rows were deleted afterward (`partnership_release_log` restored to 188).
- **Credential migration**: Move partnership GHL, Unipile, and state-upsert secrets out of Config/Code literals and rotate them after migration.
- **Reply Poller API gap resolved 2026-08-04**: `LT - Partnership Reply Poller` (`0SQ7tTk03okegp9V`) uses supported `GET /contacts/` pagination for active contacts and `GET /conversations/search` for inbound email reply lookup. It records lookup failures and fails closed instead of treating an ambiguous lookup as no reply. Smoke execution `522221` returned `checked: 58`, `replied: 0`, and `errors: []`; current published version is `736386a2-a7d2-434d-b9ba-72026e49c98b`.
- **Executive Report response-rate + social fixes (2026-08-04)**: User reported 1 partnership email reply and 1 partnership LinkedIn reply showing as 0 response rate, and incorrect LinkedIn/email data for the 3 campaigns. Four root causes fixed and published:
  1. **Reply Poller used `POST /conversations/search` (404)** — the correct endpoint is `GET /conversations/search` (200). Every poll run failed with `email_reply_lookup_failed` on all ~59 contacts, so the email reply was never detected. Fixed to GET with query params; smoke-tested execution `522241` returns `errors: []`. Published version `736386a2-a7d2-434d-b9ba-72026e49c98b`.
  2. **Reply Handler never wrote a reply event** — `LT - Partnership Reply Handler` (`mRDw57IHtnQe4wOo`) only tagged `partner_replied` + created an opportunity + Slack. Added a `Store Reply Event` Postgres node that inserts `event_type='replied'` into `Email_Events` (campaign_id `partnership`, workflow `LT - Partnership Reply Handler`). Published version `ad993fc2-4822-49bb-ad3e-f045a86b465d`.
  3. **Reply Backfill was one-shot** — `LT - LinkedIn Reply Backfill (Unipile)` (`QfJ2EZcc7lZwNgxj`) only selected rows where `dm_backfill_checked_at` was empty, so it ran once on 2026-07-31 (all partnership rows `idle`) and never re-checked. The `Select Pending Backfill Rows` query now also re-checks rows older than 6 hours with `dm_conversation_status <> 'active'`. Published version `0620c314-befb-4620-b23a-ad96b55cf4a0`.
  4. **Social insights key mismatch** — the Executive Summary `social_posts` CTE read `insights->>'likes'/'comments'/'shares'` (plural) but GHL stores `like`/`comment`/`share` (singular). The `Build Query` node now `COALESCE`s both. Verified: `totalLikes: 24, totalShares: 4, totalComments: 3` (was all 0). Published version `ff6fdc52-5eef-44b2-a50a-358cace45228`.
  - **Historical reply backfill completed 2026-08-04**: the verified Strider Peterson email reply was recorded in `Email_Events` with its actual GHL inbound timestamp (`2026-08-03T15:41:03Z`), and the verified Jaret Christopher LinkedIn reply was recorded in `linkedin_activity_events` at `2026-08-01T03:05:55Z`. The one-time helper workflows were executed successfully and archived. At that point, the selected-window Campaign Channel Summary showed `Partnership emails`: 59 sent, 1 reply, 1.69% response rate; and `Partnership LinkedIn`: 17 invites, 1 reply. The 2026-08-12 recovery added verified David Schachter and Gretchen Gailey replies, bringing the current Partnership LinkedIn reply total to 3.
  - **Account-level social statistics live (2026-08-17)**: the GHL PIT now authenticates `/social-media-posting/statistics`, so `LT - GHL Social Statistics Ingest` (`veg9jbN1P67Xmqy8`) stores 7/30/90-day reach/impressions/likes/followers/posts windows daily and the Executive Summary returns them. Saves is not supplied by the statistics source and stays N/A. |

### Audit (2026-07-31)

Full audit passed:
- All 7 partnership workflows published and active (versionId == activeVersionId for all)
- 3 patched LinkedIn workflows verified: correct SQL UNION/UNION ALL queries, source_table routing, and dedicated partnership update nodes in Reply Backfill and New Messages
- Campaign Channel Summary (`MvPLbUAN9IIQikxb`) published with `partnership_release_log` UNION ALL in `email_sent` CTE (version `6641aa9a`). Endpoint confirmed returning "Partnership emails" row.
- Postgres tables `partnership_release_log` and `partnership_linkedin_connection_state` bootstrapped on live VPS; the LinkedIn state table has 127 seeded `ready` rows. The release log was empty during the initial dry-run audit; outbound is now live.
- Partnership candidate lookups use supported `GET /contacts/` pagination with explicit failure handling. LinkedIn state seeding checks existing IDs first; validation execution `278675` found 127 existing rows, seeded 0, and completed the dry-run request plan without outbound sends.
- Post-remediation scheduled executions `278513` (email), `278515` (LinkedIn), `278634` (DM), and `278611` (reply polling) succeeded with no error/crash executions after the fixes.
- Executive Report frontend deployed as build `2026-08-01-v12-campaign-breakdown` to reports.livetransparent.com. It directly fetches campaign channel data, renders LinkedIn Invites/Accepted/Replies, and displays social likes/comments/shares/saves/reach/impressions when supplied.
- GHL contacts verified: 98 `partner_candidate_email`, 127 `partner_candidate_linkedin` (94 overlap + 33 LinkedIn-only), 131 total. All assigned to Janvi.
- 4 email templates confirmed in folder `Partnership Email Campaign` (`6a6b768aa43d24a7ce1514f1`)
- Partnership Pipeline (`tQkFYrHjALgoLz6oq0uz`) with 4 stages confirmed in GHL
- No regressions detected — all existing DAN/Emerald/LinkedIn/Vapi workflows unaffected

## Other Live Systems

- **SimpleTexting**: Automated outbound remains paused. Step Runner (`dUyOfxllvkxZavaw`), Warmup Dispatcher (`dZQLlbTLkpE1843X`), Pool Dispatcher (`usxYXSuc4ahw40V3`), and Campaign Sequencer (`7mSiivR3NhtLIcNz`) are unpublished. Phone Backfill (`8hQKQi1PooYDFxNR`) is active but non-sending. The active send webhook defaults to dry-run; no sender schedule may be published and no live SMS may be sent without explicit approval. Inbound replies add `simpletext_replied`, remove `simpletext_ongoing`, mark campaign state `replied`, and suppress future sends; `simpletext_stop` remains the hard opt-out.
- **SimpleTexting GHL Conversations provider**: **LIVE** as of 2026-07-20. Separate GHL private app `LiveTransparent SimpleTexting SMS` with provider `SimpleTexting SMS` (`6a5b91913953360948dd59f1`). Delivery URL: `https://automations.livetransparent.com/webhook/lt-simpletexting-provider-outbound`. `LT - SimpleTexting Provider Outbound Router` (`f4VoO1lBWkYRcQai`) receives GHL outbound replies, validates provider ID, normalizes phone to E.164, checks `simpletext_stop` tag, reads GHL `attachments[]`, and sends via the idempotent send workflow (`gwaEpWDpTIwsafi8`) → SimpleTexting API. One HTTPS attachment selects `MMS_PREFERRED`; if SimpleTexting rejects it, one URL-bearing SMS fallback is attempted. Outbound campaign sends mirror into GHL Conversations via `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`). `simpletexting_conversation_map` table created in Postgres keyed by `(conversation_provider_id, alt_id)`. GHL Conversations is the primary operator inbox for SimpleTexting SMS; Slack alert for inbound replies is preserved. Multiple attachments are not supported in v1 and fail closed.
  - **Unipile/Instagram**: Instagram DM Sequence (`iCnY6ccdHhfJg3sf`) remains **unpublished**. The real Instagram account is `F2UprZ8aQc6Qm9CYYWU6cg`, but the old workflow must not be republished because it used the LinkedIn account and old state model. Build the company-page workflow against the approved identity/state plan instead.
- **Instagram inbound bridge**: `LT - Instagram Unipile New Messages` (`pISlgYUsyJIrLuJd`) is active at `/webhook/lt-unipile-instagram-new-messages`. It normalizes Unipile Instagram inbound payloads, conservatively resolves an existing GHL contact before creating one, persists `instagram_conversation_map`, converts the stored agency OAuth token to a location token via `POST /oauth/locationToken`, and posts inbound messages into GHL Conversations under the `Instagram via Unipile` tab. Post-merge cleanup on 2026-07-16 repointed `instagram_conversation_map.id = 1` for chat `yx-R-9J6XdWaFpGOQd1JFA` to canonical GHL contact `XZ4yChllGBdcsVxhFRDe`; the temporary duplicate `4V2oTmM7lWya3Nmtmp1Y` created during verification was deleted.
- **Social provider outbound router**: `LT - Social Provider Outbound Router` (`kqIi8i1RjFAZKrK3`) is active at `/webhook/lt-social-provider-outbound`. Fixed 2026-07-16: POST webhook `responseMode` now uses `responseNode`, map tables are created defensively, payload message text is preserved through Postgres lookup, and Unipile send uses the working `api42.unipile.com:17256/api/v1` base. Canonical provider IDs are SMS-type additional custom conversation providers: `Instagram via Unipile` = `6a58a1193cdfc36997580a68` and `LinkedIn via Unipile` = `6a58a14ff3023bea3783c152`. Inbound message API must use `type: "Custom"` with `conversationProviderId` + `altId`; do not include `emailTo`/`emailFrom`/`subject` or dummy contact phone/email data. Deleted Email provider IDs `6a5893d11e9368345005f66e` and `6a5892b9107668309b3f85ac` must not be reused. Verified Instagram and LinkedIn inbound as `TYPE_CUSTOM_PROVIDER_SMS`; Instagram chat `yx-R-9J6XdWaFpGOQd1JFA` and LinkedIn chat `60Ult1SrWhOuvuZp1u7nXw` both map to canonical GHL contact `XZ4yChllGBdcsVxhFRDe`, with LinkedIn conversation `Ze8o3KbsrwuAXQ3KK5ge`. LinkedIn normalizer handles Unipile's form-encoded single-JSON-key webhook shape. Direct outbound router smoke tests after map repair passed: Instagram message `vjdEYSk9XD6R0I46oPWLwA`, LinkedIn message `C7I9944kWsSKutX2XhZEpA`.
- **Social provider bridge handoff**: Full build context, operator inbox runbook, monitoring gaps, and next steps for `LinkedIn via Unipile` + `Instagram via Unipile` GHL bidirectional messaging are in `docs/strategy/unipile-ghl-bidirectional-integration.md`. Read this before changing provider workflows.
- **Unipile/LinkedIn**: Active production path is dispatcher → acceptance/state sync → canonical DM sequence. Follower DM (`pq7XVajNFnnwMUTr`) is **unpublished**. Current published workflow inventory is documented in `Current Published Workflow Inventory` above. Guardrails block former-owner-branded copy.
- **LinkedIn invite copy**: n8n defaults say Transparent eCom. If LiveTransparent appears, check GHL-side body.message overrides first. Use [/] character class instead of \/ in regex literals to avoid SDK serialization corruption.
- **GHL warm intake/routing**, Apollo enrichment, Emerald and DAN email campaigns are active.
- **SMS campaign**: The canonical send webhook is `https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms`; template registry details are in `docs/outreach/sms_edited_templatekeys.md`. Send, provider-router, idempotency, and callback boundaries were hardened on 2026-08-17, with automatic SMS/MMS routing published on 2026-09-24. Registered provider callbacks use protected secret URLs because SimpleTexting cannot attach custom headers. Historical reconciliation restored 41 confirmed sends, terminalized 202 exhausted provider failures, quarantined 55 `send_unknown` rows, and replayed nothing. Keep sender schedules and legacy diagnostics inactive until an approved live provider test or natural traffic verifies the final boundary.

### Weekly Newsletter Pipeline (Built 2026-08-21 — LIVE; capacity retuned 2026-09-01)

Recurring weekly newsletter to all eligible GHL contacts, spread over Monday-Friday with 15-minute dispatcher runs from 07:00-13:00 LA, from 3 senders (`.co`, `.agency`, `.org` — NOT `.com`). Content lives in a GHL **Email Template** (NOT Campaigns) named `Newsletter <n> <Monday-date> (<subject>)`, pulled automatically at send time. Custom open/click/unsubscribe tracking is injected by the dispatcher into `newsletter_events` (GHL does NOT emit webhooks for `POST /conversations/messages` sends, so native GHL Campaign stats are unavailable on this path).

**DNS gate cleared:** go-live was completed on 2026-08-21. Do not revert the live dispatcher to dry-run or unpublished without explicit approval.

| Workflow | ID | Schedule | Status |
|---|---|---|---|
| LT - Newsletter Contact Prep | vvPdJMzBJMgcf5I9 | Mon 06:30 America/Los_Angeles (`30 6 * * 1`) | Active/published; weekday buckets 1-5 |
| LT - Newsletter Dispatcher | vru7OtCkDnPJkWt2 | Every 15 minutes, 07:00-13:00 LA (`*/15 7-13 * * 1-5`) | Active/published; `maxPerRun=250`, `maxPerSenderPerDay=2333`, live |
| LT - Newsletter Open Pixel | HkTQ9mqwHcpg3AIM | `GET /webhook/lt-newsletter-pixel` | **Active** |
| LT - Newsletter Click Track | HZ8ndNF4p80PrQjf | `GET /webhook/lt-newsletter-click` | **Active** |
| LT - Newsletter Unsubscribe | RvYusUSGB79K2e2k | `GET /webhook/lt-newsletter-unsub` | **Active** |

- **Eligibility (measured 2026-08-21):** 31,800 GHL contacts → 22,169 eligible (excludes no-email + `do not contact`/`do not nurture`, email-deduped). Per sender: ~7,390/week, ~1,478/day across five weekday buckets (under the live `maxPerSenderPerDay=2333` cap).
- **Dispatcher behavior:** `maxPerRun=250`, `maxPerSenderPerDay=2333` enforced from database sent counts in the current LA day, 400–600ms delay, 429/transient retry (4 attempts, 2/4/6s backoff), dry-run emits `planned` and never mutates DB. Template matcher accepts `builder` OR `html` types and fails closed if the week's template is missing.
- **Runner recovery (2026-09-01):** The custom JavaScript runner stays warm for 300 seconds with concurrency 10 and uses isolated `pg` plus `coolify-shared`. Full pinned graph test `837185` passed; controlled live send `838055` succeeded. August 31 sent 695 newsletters and recorded 39 HTTP 400 failures. Do not launch large single executions; use the 250-row cadence.
- **Tracking:** HMAC-signed URLs (`trackSecret` in Config nodes). Pixel `log_id`+`tok`, click `log_id|u`+`tok`, unsub `log_id`+`tok`. Tables `newsletter_send_log` (UNIQUE `(ghl_contact_id, week_key)`) + `newsletter_events` in the `postgres` DB.
- **Template:** ID `6a87716221922afe5eda9e6f` (`Newsletter 1 2026-08-24 (The real reason regulated ads get disapproved)`), proper logo applied 2026-08-21.
- **Deliverability audit + DND suppression (2026-09-09):** the ~2.7% GHL 400 rejection rate is `CONVERSATIONS_MSG_INVALID_EMAILTO` from contacts whose **Email DND suppression is active** (prior bounce/spam/unsubscribe) — not sender-related and not stale email. Dispatcher now retries `invalid_email` rejects once with the contact's current GHL email and marks terminal `invalid_email`, tagging the contact `newsletter_dnd_suppressed`; Prep's `blockedTags` now includes that tag so suppressed contacts are never re-queued. Dispatcher active `9774bd27-0e23-48da-a512-889ac49a6c61`; Prep active `8c3342d0-793d-4c22-9d5b-b8191aeeaea4` (Prep Config edited via direct n8n REST PUT; Set v3.4 node). Full record + remaining DKIM/DMARC/Postmaster steps: `docs/sessions/2026-09-09-newsletter-deliverability-audit-and-dnd-suppression.md`.
- **Full build + Go-Live runbook + verification:** `docs/sessions/2026-08-21-weekly-newsletter-pipeline.md`.

**Go-Live sequence (after DNS confirmed):** (1) re-check SPF/DMARC on `.co`/`.agency`/`.org` (one `v=spf1` and one `v=DMARC1` each; mxtoolbox recommended), (2) confirm this week's `Newsletter 1 <next-Monday> (<subject>)` exists in GHL Templates, (3) `publish_workflow` both prep + dispatcher, (4) flip dispatcher `defaultDryRun=false` via direct n8n REST PUT (Config Set node is unsafe via MCP pointer ops), (5) verify `versionId == activeVersionId` after each mutation, (6) monitor first run.

### SimpleTexting SMS via GHL — Bidirectional Provider (LIVE 2026-07-20)

GHL App: `LiveTransparent SimpleTexting SMS`, provider `SimpleTexting SMS` (`6a5b91913953360948dd59f1`), SMS-type, Custom Conversation Provider, Delivery URL: `https://automations.livetransparent.com/webhook/lt-simpletexting-provider-outbound`.

#### Workflows

| Workflow | ID | Status | Role |
|----------|----|--------|------|
| LT - SimpleTexting Provider Outbound Router | f4VoO1lBWkYRcQai | Active | Receives GHL outbound messages at `/webhook/lt-simpletexting-provider-outbound`, validates provider ID, normalizes phone to E.164, sends via idempotent boundary → SimpleTexting API. Skips business-hours guard for human replies. |
| LT - SimpleTexting Inbound Reply (Webhook) | i0pROHpFtN4LYR0Q | Active | Slack alert preserved. Now also posts inbound messages to GHL Conversations under `SimpleTexting SMS` via `type: "Custom"` + `conversationProviderId`. |
| LT - SimpleTexting SMS Send (Webhook, Staged) | Q3Ivnwe4z2Y3cD7A | Active | Mirrors successful outbound campaign sends into GHL Conversations under `SimpleTexting SMS`. |
| LT - SMS Idempotent Send | gwaEpWDpTIwsafi8 | Active | Canonical deduplicated SMS boundary. Called by outbound router and campaign send paths. |
| LT - SimpleTexting Campaign Phone Backfill | 8hQKQi1PooYDFxNR | Active | Non-sending phone-state repair; supports `awaiting_phone_refresh` and terminal `phone_unavailable`. |
| LT - SimpleTexting Campaign Step Runner | dUyOfxllvkxZavaw | Unpublished | Canonical scheduled sender candidate; dry-run guard enabled. |
| LT - SimpleTexting Warmup Dispatcher (Staged) | dZQLlbTLkpE1843X | Unpublished | Sender-capable; keep paused pending explicit approval. |
| LT - SimpleTexting Pool Dispatcher (Staged) | usxYXSuc4ahw40V3 | Unpublished | `sms_drip`, 10/run; dry-run/small-batch gate required. |
| LT - SimpleTexting Campaign Sequencer (Staged) | 7mSiivR3NhtLIcNz | Unpublished | 6-step flow; keep disabled until the canonical sender path is selected. |
| LT - SimpleTexting Delivery Events (Webhook) | AEi1VCzkLvaYFr4U | Active | Registered protected callback for delivery and non-delivery reports. |
| LT - SimpleTexting Unsubscribe Events (Webhook) | IyBKMkpYQ7pa0C8V | Active | Registered protected callback for unsubscribe reports. |

#### DB Table

`simpletexting_conversation_map` — UNIQUE on `(conversation_provider_id, alt_id)`, with indexes on `ghl_contact_id` and `normalized_phone`. Created on first outbound router execution.

#### Phone Format Contract

- Canonical phone: E.164, e.g. `+17144696406`.
- Conversation `altId`: `simpletexting:+17144696406`.
- `simpletexting_conversation_map.normalized_phone`: E.164 only.
- Outbound router has full E.164 normalization (`normalizePhoneE164`). AltId for inbound/outbound mirroring uses `simpletexting:+1<10-digit>` which works for US numbers. Full E.164 migration across delivery/unsubscribe workflows is deferred.
- `simpletext_replied` blocks automated sends; `simpletext_stop` blocks all sends including human GHL provider replies.

#### Guardrails

- Human replies bypass business-hours limits but still enforce STOP suppression.
- Outbound router validates `conversationProviderId` against `6a5b91913953360948dd59f1`.
- Idempotent send deduplicates on `(contact_id, workflow_id, message_hash)` per day.
- `simpletext_stop` tag check in outbound router blocks provider-originated sends to opted-out contacts.
- SMS Send mirroring runs on `onError: continueRegularOutput` so mirror failures don't block sends.
- Inbound reply still posts to Slack AND GHL Conversations; Slack alert preserved as secondary channel.
- A provider result is accepted only when the idempotent boundary confirms `sent` or `duplicate`; ambiguous responses fail closed.
- Controlled live validation still requires explicit approval. Safe pinned/dry-run tests are not proof of provider acceptance.

## Local Script And Archive Boundaries

- `local-scripts/` is an intentionally Git-ignored workspace for reusable operator-only helpers and machine-specific probes.
- `local-archive/n8n/` is an intentionally Git-ignored workspace for historical n8n exports, backups, and one-off patch inputs. Live n8n remains authoritative; these files are for audit/reference only and must not be redeployed without reconciliation.
- Keep reviewed, versioned automation and migration sources in `scripts/` and the retained `n8n/**/*.ts` blueprints; do not move them into the ignored archive merely because they contain code.
- Retained source blueprints must use environment placeholders and must not contain live PITs, API keys, webhook secrets, or provider tokens.

## Key Files

- repomix-output.md
- .env
- Project Status and Next Steps.md
- Export_Contacts_brands pool_Jul_2026_5_24_AM.csv (GHL export, used for DAN backfill)
- Export_Contacts_Dispensaries pool_Jul_2026_5_28_AM.csv (GHL export, used for DAN backfill)
- Export_Contacts_for fresh Linkedin connections_Jul_2026_2_16_AM.csv (GHL export, 14,987 contacts, used for LinkedIn dispatcher bulk feed 2026-07-13)
- GHL Live Transparent CRM/
- postgres/reporting-bootstrap.sql
- n8n/docker-compose.yml
- n8n/voice-agent/
- n8n/lt-linkedin-dispatcher.ts
- local-archive/n8n/workflows/
- local-scripts/suppress_linkedin_dms.py
- local-scripts/_vps_psql.py
- local-archive/n8n/
- scripts/n8n/fix_intake_poller.js
- reports/embed/executive/index.html
- reports/nginx.conf
- Backup of all n8n workflows/
- Project Specifications.md
- docs/campaigns/Vapi_Brand_Campaign.docx
- docs/campaigns/Vapi_Dispensary_Campaign.docx
- docs/strategy/unipile-ghl-bidirectional-integration.md
- docs/sessions/2026-08-21-weekly-newsletter-pipeline.md
- docs/dns-email-authentication-fix.md
- plan.md
- marketing/email-marketing/emerald-email-campaign/plan.md
- marketing/email-marketing/emerald-email-campaign/dispatcher-plan.md
- marketing/email-marketing/emerald-email-campaign/workflow-mapping.md
- Partnership Marketing/partnership_master.json
- Partnership Marketing/Content Partnerships - Email - Consolidated List.csv
- Partnership Marketing/Content Partnerships - Linkedln - Consolidated List.csv
- Partnership Marketing/Email Partnership Outreach Sequence.docx
- Partnership Marketing/Linkedln Partnership Outreach Sequence.docx
- scripts/partnerships/clean_partnership_data.py
- postgres/partnership-bootstrap.sql

## VPS SSH Access

- Host: 89.117.21.29 (hostname vmi3077218), user root
- SSH key: C:\Users\edmon\.ssh\local-upload (Ed25519, no passphrase, generated via Coolify)
- Permission fix: paramiko works directly. To use ssh.exe: icacls $keyPath /reset /inheritance:r /grant "$env:USERNAME:(R)"
- Reference keys on server: vps_caddy_key, vps_upload, id_ed25519_vps_whitefriar -- all passphrase-encrypted
- GHL-ready CSV files on n8n server: /home/node/.n8n-files/GHL_Ready_{Brands,Dispensaries}.csv
- Local copies: data/GHL_Ready_{Brands,Dispensaries}.csv

### Postgres Reference

- emerging_pool_contacts: 13,868 contacts (3,668 brands + 10,200 dispensaries)
  Fields: emerald_contact_id, source_list, first_name, last_name, primary_email, primary_phone, company_name, tags, ghl_contact_id, ghl_opportunity_id, ghl_import_status, raw_json (JSONB). UNIQUE on (emerald_contact_id, source_list).
  ghl_contact_id coverage: 12,639 filled (from GHL export CSVs), 1,229 null (not in exports).

## Former SDR Identity Cleanup (2026-07-07)

### What changed

- Message content and email signatures were changed from the former SDR identity to the active sales-owner identity in the customer-facing templates.
- Sender defaults and transfer wording were changed to the active sales-owner identity.
- All assistant system prompts updated

### What stayed the same (keys NOT changed)

- Legacy SMS payload aliases remain as internal compatibility identifiers because existing GHL automations reference them; they are not customer-facing implementation names.

### User IDs

- Jason Bornillo (jason@livetransparent.com): yU85G6kfhtW4vUtx3QE6
- Cameron Karkut (cameron@livetransparent.com): 03p5GatJBH7i9zjMaIzm
- Ed Cadorniga (ed@livetransparent.com): gePIeuHOEsAiPVA1mfOR

### GHL Status (2026-07-10)

- **Former-owner-branded LinkedIn invite resolved**: Workflow 25cd82a2 repointed from "Create Task" to n8n webhook with Cameron default message + send:true.
- **SMS failed-send workflows verified clean**: 41c6aecd and a99f96d9 -- no former-owner customer-facing messages.
- **GHL Sales Followup Emails and SMS** (f6b44e34): all Send email actions use the active sales-owner routing and sender defaults. The implementation should retain this neutral display name in future documentation.
- **Jason user ID found**: yU85G6kfhtW4vUtx3QE6 -- was agency-level, reassigned to sub-account.

## Tool & CLI Preferences

These CLI tools are installed and available via PATH. Prefer them over slower alternatives:

| Tool | Use instead of | Why |
|------|---------------|-----|
| rg | findstr, Select-String, grep | 10-100x faster text search, .gitignore-aware |
| fd | Get-ChildItem, dir | Blazing fast file finding by name/pattern |
| bat | cat, Get-Content | Syntax-highlighted file viewing with line numbers |
| jq | manual JSON parsing | Process API/LLM JSON responses inline |
| yq | manual YAML parsing | YAML equivalent of jq |
| xsv | CSV processing in Python/JS | Fast CSV search, slice, stats, join |
| delta | default git diff | Syntax-highlighted, side-by-side git diffs |
| fzf | scrolling through lists | Interactive fuzzy finder |
| zoxide | cd | Learns your navigation patterns, z <fragment> jumps anywhere |
| hyperfine | manual timing | Benchmark any command with statistical analysis |
| sd | sed, regex replaces | Simpler find-and-replace syntax |
| ast-grep | regex-only code search | Structural code search that understands syntax trees |
| eza | ls, dir | Modern ls with icons, colors, tree view |

## repomix-output.md Refresh

After any significant work session (workflow fixes, new automations, config changes), regenerate repomix-output.md so next-session context is up to date:

The current PowerShell profile's `packlive` function hardcodes `C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent`. **Check that this matches the active workspace before invoking it.** For another checkout (including `C:\1_Ed's Active Work\Projects\LiveTransparent`), run Repomix from that repository root with an explicit `--include` set and `--output repomix-output.md`; verify the output contains the latest handoff before closing the session. Do not assume sourcing the profile makes `packlive` target the current directory.
````

## File: Project Status and Next Steps.md
````markdown
# LiveTransparent Project Status and Next Steps

### Executive Report V1 GHL Call Export Investigation — 2026-09-29

- **New supported source found:** HighLevel publicly documents `GET /conversations/messages/export` with `channel=Call`, `startDate`, `endDate`, and cursor pagination. A read-only request using the current GHL PIT returned HTTP 200; records include stable message IDs, `dateAdded`, `direction`, `userId`, and `status`. This corrects the prior statement that no documented messages-export endpoint exists.
- **Two-window feasibility:** complete cursor scans succeeded for `2026-09-22..2026-09-28` and prior LA week `2026-09-15..2026-09-21`, returning 1,990 and 1,227 messages with no duplicate or missing IDs in the scan.
- **Parity blocker:** the exact native-widget week `2026-09-20..2026-09-26` (`Asia/Manila`) returned 1,747 outbound export records (Marc 1,288; Jason 460), versus native widget totals of 1,006 and 350. Export `completed` does not map directly to native `answered`; do not replace the dated snapshot or publish export-derived counts until reconciled by exact call IDs and status semantics.
- **Authenticated Call Reporting route test:** the GHL UI's private `POST backend.leadconnectorhq.com/reporting/calls/get-all-phone-calls-new` returned 1,377 rows over 28 pages for the exact week. Filtering outbound rows by SDR `userId` and `callStatus` exactly matched the native widgets (Marc 1,006: 802 answered, 105 busy, 59 no-answer, 40 failed; Jason 350: 285 answered, 19 busy, 35 no-answer, 11 failed). The endpoint included 21 inbound rows beyond the 1,356 outbound total.
- **Automation boundary:** the same private endpoint returned HTTP 401 `The token is not authorized for this scope` when called with the GHL PIT outside the authenticated browser. It is undocumented/private and must not be integrated into n8n as an API contract without GHL support/approval. The supported export endpoint remains the public API candidate but does not match the native widget. A forward-only webhook cannot supply history.
- **Prior poller change:** `LT - GHL Daily Calls Ingest` (`SqNQ0BYaTdcqyt1l`) has a conflict guard so poller upserts cannot overwrite rows marked with verified-webhook provenance. This is only collision protection; it does not make polling the reporting source or solve historical data.
- **Next:** ask GHL whether the Call Reporting route can be made available through a supported API/scope, or obtain a supported report CSV/export for multiple windows. Preserve the private endpoint's exact-week parity result as diagnostic evidence only. Keep V1's exact-week snapshot and do not publish export-derived counts until the access/source contract is approved.

Updated: 2026-09-29 (supported GHL Call export investigation)

### Executive Report V1 GHL Call Source EOS — 2026-09-29

- **What was established:** authenticated GHL native report `69bbeb2d088aabd9058eaf44`, selected `2026-09-20`–`2026-09-26`, reports outbound calls by `dateAdded` and SDR `userId` (report timezone `Asia/Manila`). Marc (`sqGx5rp3oAUG610NXyjU`) = 1,006 (802 answered, 105 busy, 59 no-answer, 40 failed); Jason (`yU85G6kfhtW4vUtx3QE6`) = 350 (285 answered, 19 busy, 35 no-answer, 11 failed). The visible Marc card rounds to 1.01K; an earlier 982 note is superseded by the current native widget result.
- **V1 snapshot/UI:** V1 Facts API `oxYDg6XnRBKhl1Xd` is active/published at `9a17c3c2-45d2-477e-9c01-3bea0a537ae3`; it returns the native counts only for that exact week and states the dated snapshot basis. The SDR panel now renders the API-supplied source basis. V1-only files are deployed to `/embed/executive-v1/`; current report `/embed/executive/` was not touched.
- **Supported API investigation (superseded by the export investigation above):** the PIT can read supported Conversations/location APIs but cannot access the private native-report widget route. Official Voice AI call logs do not cover the human SDR widgets. The documented location-level message export was subsequently found and tested; it returns historical CALL messages but does not yet reconcile to the native widgets. The older paginated Conversations scan remains incomplete.
- **Webhook path built:** active/published `LT - GHL Outbound Call Event Ledger (Webhook)` (`SA5SF1cZQcVf3IyB`, version `15b2944f-5b71-40fe-b97a-d87718cd6cdb`, 5 nodes) at `https://automations.livetransparent.com/webhook/lt-ghl-outbound-message-call`. It verifies raw-body GHL signatures and upserts outbound CALL events by `messageId`. Marketplace `OutboundMessage` subscription is not configured. Negative-signature production endpoint tests (executions `1062819`, `1062820`) returned HTTP 401 `invalid_signature`, were execution-successful, and bypassed the database node. No valid signed event, subscription delivery, real call, or DB-write test has occurred.
- **Boundary and next action (superseded by the export investigation above):** the receiver remains unsubscribed and is only forward-looking; do not treat it as the historical-data fix. Prioritize reconciling the documented export API to the native report. Keep historical coverage claims limited to the exact-week snapshot until parity passes.

Updated: 2026-09-29 (Executive Report V1 GHL call-source EOS)

### LinkedIn Sales Navigator and Identity EOS — 2026-09-29

- **Personal identity guard:** Alexis Mora's GHL contact is `RGjMxzMqOR2L14ao8qmg` with `firstName=Alexis`, company `A.MORA Marketing`, and LinkedIn URL `alexistaylormora`. No authoritative source for the historical `Angel` greeting was found.
- **Live behavior:** personal dispatcher `fXxw5lanZcDmUrst` and personal DM sequence `d0tEtijajisIsYcs` now require a non-empty LinkedIn provider first name and use it for outbound copy. Partnership/company dispatcher `crKIsaL5k3YBfqDZ` and DM sequence `nspggypNF245xzeL` remain GHL-based.
- **Conversation mirroring:** outbound mirrors use `/conversations/messages`; inbound LinkedIn events continue using `/conversations/messages/inbound`. The helper scope defect found during review was corrected.
- **Published versions:** dispatcher `ca663633-143f-4312-9cc3-d0a4ac262661`; personal DM `96f7cf60-97c2-4f54-ba13-20ebf9d49ef1`; partnership dispatcher `44c4ed5f-d5e3-4c75-94f0-1ac21cd7355e`; partnership DM `9c04b07a-812d-4755-850d-125cadec8c7a`. REST readback confirmed `versionId == activeVersionId` for all four.
- **Sales Navigator research:** Unipile Hosted Auth must be configured with `products: ["classic", "sales_navigator"]`; Sales Navigator recipient IDs use `ACw...`, v2 account IDs use `acc_...`, and `SALES_NAVIGATOR_PRIMARY` is the inbox for starting a new Sales Navigator conversation. The current legacy `/api/v1` account has not been migrated or verified for that v2 inbox.
- **Safety boundary:** no live LinkedIn send, account registration, or historical message backfill was performed. Cameron must authenticate directly in Unipile; never request or store `li_at`, `li_a`, cookies, API keys, or other session secrets in the repository.
- **Next:** provision/verify the Sales Navigator-capable v2 account, preserve the existing Classic connection during transition, add durable personal/hiring exclusions, then produce a deduplicated historical report limited to canonical DM-sequence messages, connection requests, and connection approvals before any import.
- **Detailed handoff:** [`docs/sessions/2026-09-29-linkedin-sales-navigator-and-identity-eos-closeout.md`](docs/sessions/2026-09-29-linkedin-sales-navigator-and-identity-eos-closeout.md).

Updated: 2026-09-29 (LinkedIn identity and Sales Navigator EOS)

### SimpleTexting Follow-up SMS Sender Personalization — LIVE 2026-09-29

- **Objective/scope:** ensure Jason/Marc GHL follow-up SMS messages identify the opportunity owner/assignee, retain Jason as the fallback, and run through the SimpleTexting text-only path.
- **Root cause found:** the GHL webhook already supplied top-level `owner` and `user` data, but the SMS sender ignored both; `john_sms1`/`john_sms2` hardcoded Jason and `john_sms3`–`john_sms5` had no sender name. A real invocation, execution `1062395`, returned `outside_business_hours` because the sender gate was Eastern-time based.
- **Live fix:** active `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`) now has `Resolve Sender + SMS Templates` between `Config` and `Validate + Send SMS`. It prefers GHL opportunity `owner`, then named assignee, then workflow `user`; it renders Marc/Jason and falls back to Jason. The gate is now weekdays 10:00–17:00 `America/Los_Angeles`.
- **Templates:** the resolver dynamically overrides `john_sms1` through `john_sms5` per invocation. Each message includes the resolved sender name; the current GHL template keys are retained. No media is included, so these sends remain `AUTO` SMS, not MMS.
- **Published state:** active version `b69a183e-273a-43f9-b06d-b2bd1575543b`; `versionId == activeVersionId`; 7 nodes; active, not archived.
- **Verification:** dry-run executions `1062414` (Marc owner vs Jason workflow user) and `1062422` (Jason owner vs Marc workflow user) both succeeded and rendered the owner-preferred name. No SimpleTexting provider call was made. Final read-only execution search found no `new`, `running`, or `waiting` executions. `git diff --check` passed with only existing LF→CRLF warnings.
- **Delivery boundary:** execution `1062395` was rejected before provider dispatch by the former time-zone gate, so it is not proof of delivery. Previously blocked GHL runs are not automatically replayed. The next step is to observe a natural GHL invocation in Pacific business hours and verify the provider message ID plus delivery event; a controlled SMS requires explicit approval.
- **Files:** [`AGENTS.md`](AGENTS.md), this status handoff, and [`GHL_To_SimpleTexting_SMS_Send_Runbook.md`](GHL%20Live%20Transparent%20CRM/GHL_To_SimpleTexting_SMS_Send_Runbook.md).

### Continuation — Inbound Priority Router Integration 2026-09-26

- Published `LT - Inbound Intent Priority Router` (`URpjcm2k5isHUyls`) at active version `3a3a6ab2-79a3-4fcc-822f-52677b6ae38c`; `versionId == activeVersionId`. Its execute-workflow trigger remains `triggerCount=0` because it is invoked by caller workflows rather than a schedule/webhook.
- The router targets `Sales Outreach` (`dhdlf3O4tymxFtHk4aqq`) → `Priority` (`be636da7-3c15-48ab-b589-c75bcd6f9955`), atomically claims `(contact_id, source_event_id)`, uses a short contact lock, preserves owner/attribution fields, and fails closed for duplicate, closed, already-Priority, or ambiguous opportunity states.
- Mocked pin-data tests passed for create, update, already-Priority, closed-protected, duplicate-terminal, and ambiguous-open branches. Pinning bypassed Postgres and GHL nodes, so no database table, CRM record, or opportunity was changed.
- The router accepts normalized LinkedIn, Instagram, SMS, call, voicemail, and qualifying email events. All four inbound source families are now attached after their persistence/qualification boundaries.
- Executive Report API caching is now active in the reports proxy with a 30-minute TTL for Summary, Campaign Channels, and V1 Facts. The V1 Facts endpoint was previously uncached; cold 7-day requests measured about 3.8 seconds after queue recovery, and immediate cached repeats measured about 0.5 seconds.
- LinkedIn workflow `7o5EBdvwAuIaWW7k` is published at `dd98c27b-0fca-491c-bac1-3ff38b1b147b`. Main and partnership branches route after conversation-state persistence using resolved `ghl_contact_id`, Unipile `message_id`, normalized `timestamp`, `sender_name`, and the normalized event payload. The router fetches the live contact owner before a create and fails closed when unresolved.
- Instagram workflow `pISlgYUsyJIrLuJd` is published at `e09111d7-2c63-4925-b335-741c57f5ab5d` and routes after durable reply claiming, contact resolution/message persistence, and mapping upsert. SMS workflow `i0pROHpFtN4LYR0Q` is published at `599995a9-72ce-467d-9892-c7ddf496c3fa` and routes after state upsert; STOP/unsubscribe events are excluded.
- Read-only official GHL opportunity search returned the exact normal response fields parsed by the router: `id`, `pipelineId`, `pipelineStageId`, `assignedTo`, `status`, and `contactId`. Create/update responses remain unverified because testing them would mutate CRM data.
- No live CRM mutation smoke test has been run. Caller routing nodes use non-blocking error handling so inbound persistence and webhook responses are not made dependent on Priority routing.
- Call/voicemail integration is published in `PUCfTZBANSPcgS0c` version `f9388b9a-ab70-45b2-bc77-4f5c2efef829`; its non-blocking branch emits only inbound events with resolved contact ID, original timestamp, and stable call ID/composite. Voicemail uses `channel=voicemail`.
- DAN/Emerald email integration is published in `hxiiYCpEfMuoSt5H` version `6e60f832-f175-41a8-a4b7-193f286bef18`; it re-fetches the actual message and rejects automated mail before routing. Partnership email integration is published in `mRDw57IHtnQe4wOo` version `42da3b2e-4b6a-4f2f-9341-880b36292eb4` with the same qualifier.
- GHL request contracts are otherwise grounded: read-only opportunity search returned the parsed fields, official update inputs are `pipelineId`/`pipelineStageId`, and historical successful create execution `1050287` returned a usable opportunity ID. No Priority opportunity was created or updated.
- Failure-path blocker: expired contact locks can be reacquired after five minutes, but recovery requires a source replay or reconciler. Define a durable retry handoff that does not silently swallow router failures or break existing inbound-message persistence before caller integration.

### Continuation — Executive Report QA and V1 Meeting Window Repair 2026-09-26

- `ghl_opp_owner_coverage` is red by design, not because the QA workflow failed. The latest successful probe evaluated 11,569 opportunities: 4,371 had a direct opportunity owner and 243 received a contact-owner fallback, for 4,614/11,569 = 39.9%. The QA threshold is 50%, so status remains `attention`.
- The appointment owner coverage probe is separate and currently `ready`; the latest health row contains 38 appointment rows.
- V1 meeting detail was incorrectly using the API's 30-day default whenever the frontend sent only `range=7d`. The query filters scheduled `start_at` dates, not booking/creation dates. The API now converts `range=7d|30d|90d` into the correct LA date window.
- Published `LT - Executive Report V1 Facts API` (`oxYDg6XnRBKhl1Xd`) at `677e728d-8f33-4e78-a406-3a0dca56b19e`; `versionId == activeVersionId`.
- Verification: `/api/report/executive-v1/facts?range=7d` returned `from=2026-09-18`, `to=2026-09-24`, and 3 appointment rows, all inside that window. No sender workflow or email was executed.
- **Superseded by the draft above:** the canonical destination and shared router are now defined, but no live source is attached. Source-contract audit and activation approval remain required.

### Continuation — Newsletter Fail-Closed Repair 2026-09-26

- Live inspection confirmed `LT - Newsletter Dispatcher` (`vru7OtCkDnPJkWt2`) already selected the newest pending week dynamically and contained no hardcoded historical week keys.
- Scheduled runs were failing because no GHL template matched active pending week `2026-09-21`. `Fetch Newsletter Template` now returns a closed no-op result when the active template is absent; the bucket query consequently selects no rows.
- Published active version: `dacd2df9-4647-4910-8ea3-857cf889f9b5`; `versionId == activeVersionId`. No manual execution or email send was performed.
- A matching current-week GHL template is still required before newsletter delivery can resume. DAN event wiring and fresh attribution coverage measurement remain open.

Updated: 2026-09-26 (Executive Report V1 credential replacement and EOS health verification)

### EOS Authoritative TODOs — 2026-09-26

The following list supersedes scattered older “next session” lists. Historical sections below remain for traceability; use this order for new work.

1. [ complete ] Verify the first post-repair scheduled execution of `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) after published version `07e53f3b-c427-4aea-b286-e1071e2b7839`. Execution `1052265` succeeded at `2026-09-25T22:00:20Z`: 10 DeepSeek classifications (7 accept, 3 reject), 10 tag actions plus 3 cleanups, 11 writes with 0 failures, successful qualified-domain upsert, and 1 Warm MQL skipped as `not qualified`.
2. Define and audit the separate Warm -> New qualification path. The campaign/Vapi classifier does not classify the entire Warm -> New backlog; do not broaden it without confirming the explicit AI qualification contract.
3. Reconcile the report's 22 current MQLs against the 15 currently returned by the live GHL Warm -> Qualified (MQL) search. Separate snapshot lag, moved records, bounce records, and `not qualified` conflicts before routing.
4. Reconcile `ghl_opp_owner_coverage` by exact opportunity/contact ID. Current accepted result is 4,614 assigned/fallback owners of 11,569 opportunities (39.9%), below the intentional 50% threshold. Do not lower the threshold or write owners without an approved definition.
5. Obtain approval for the minimal Attribution Bridge alias repair identified in execution `1045692`; publish only after approval, verify a successful run, and confirm public `bridge: ready`.
6. Verify the next GA4/GSC bridges and Report Daily Rollups after ingest executions `1048537` and `1048538`, then re-fetch V1 with a cache-busting query.
7. Build a durable retry/reconciler for inbound Priority events whose claimed router executions fail or expire.
8. Preserve all outbound-send, CRM-mutation smoke-test, campaign-activation, and sender-change approval gates.

Classifier repair is runtime-accepted for scheduled execution `1052265`. The operator verification was read-only; the scheduled workflow performed its normal production tag/write actions. No manual CRM mutation smoke test or outbound send was performed for this EOS review.

### Executive Report V1 — GA4/GSC credential replacement and health closeout — 2026-09-26

- Created operator-owned n8n credentials `Google Analytics account - Ed OAuth` (`rhKm0YiMSBu0Lval`) and `GSC - Ed OAuth` (`awVQ5MnyCYFFCT0v`). GSC uses `https://www.googleapis.com/auth/webmasters.readonly`.
- Active production workflow references now use the operator credentials: GA4 `LT - GA4 Daily Ingest` (`6pCSGzFmrMDFL5Yq`, version `34a63b5f-db3b-43d1-ba12-4961cc15e2c3`) and GSC `LT - GSC Daily Ingest` (`xHqmCC1vOeZ11gCd`, version `ed3c59c1-05fc-4c2a-ab88-eef523c13651`). The prior Cameron GSC credential record (`EKnNrSvlEd0A99AX`) was restored from the local Cameron environment entries and is no longer referenced by the active GSC workflow. The archived inactive GA4 test workflow remains unchanged because n8n refuses edits to archived workflows.
- Post-connection verification: GA4 execution `1048537` succeeded with 925 rows; GSC execution `1048538` succeeded with 5 rows. The public Executive Summary returned HTTP 200 with populated JSON and health `ga4=success`, `gsc=success`; V1 returned HTTP 200 with 25,060 bytes.
- `bridge: stale` is the separate general Attribution Bridge, not GA4/GSC. Its last accepted success is 2026-09-12; latest checked execution `1045692` failed. Keep this warning visible until a successful bridge execution is verified.
- `ghl_opp_owner_coverage: attention` is fresh QA coverage status (11,569 measured rows, updated 2026-09-26), not an OAuth or freshness failure. Exact coverage percentages and the direct-owner/contact-fallback split still require node-level/metadata inspection.
- Next order: diagnose Attribution Bridge execution `1045692`; inspect Report QA execution `1048389`/health metadata for exact owner coverage; verify post-ingest GA4/GSC bridges and Daily Rollups; then re-fetch V1 with a cache-busting query. No sender workflow, outbound message, CRM write, or deployment was performed for this closeout.

### Executive Report V1 — EOS superseding state — 2026-09-25

- V1 remains isolated at `https://reports.livetransparent.com/embed/executive-v1/`; the current report at `/embed/executive/` was preserved. V1 static deployment uses image `v3ud1lum1svamymuor21upog:social-mql-20260817`; the current-report build remains `2026-08-17-v27-social-mql`.
- Meetings are now restricted to the canonical `Regulated Ads On Social/Search` calendar (`SrtXcFVyea7pFl3nTiIK`) and count distinct contact IDs. The V1 title is `Meetings - Regulated Ads On Social/Search`; repeated owner/calendar text was removed. The contact-name join fix is live in materializer version `47c5aaf8-047c-4cfe-996f-bdcbb97bb04d`; execution `988447` verified the six previously missing names.
- V1 Facts API is published at `677e728d-8f33-4e78-a406-3a0dca56b19e`. Executive Summary is published at `4c5b5611-841b-48a4-9d78-c0700e599e6a`; Campaign Channel Summary is published at `24492be1-3b62-436a-8dbe-7f46c64c314e`; Leads Ingest is published at `7057fd10-a7db-4888-98ad-4adb1af1c2cc` with the repaired pagination boundary.
- Attribution now checks LinkedIn request/DM/reply ledgers, Apollo tags, and Emerald tags before using Unknown. Apollo/Emerald labels are explicitly evidence-based, not inferred from campaign membership alone. The next successful Executive Summary run must verify the exact classification of the prior 83 unattributed opportunities; do not report that split as final until verified.
- SMS reporting is repaired: the Campaign Channel Summary now reads `report_sms_sent` plus provider delivery events; the verified 30-day check returned 909 sent, 529 delivered, 14 replies, and 0 failed. Voicemail remains unavailable for the 30-day window because no Vapi attempts exist there; the 90-day facts response returned 57 unique voicemail dispositions.
- **Next session:** perform one read-only successful Executive Summary execution after the latest attribution version, capture the exact opportunity-source breakdown, reconcile the residual Unknown rows by contact/opportunity ID, and update this section plus `executive_report_v1_plan.md`. Do not send messages or alter the current report as part of that audit.

- **EOS verification boundary:** Executive Summary execution `989640` and V1 Facts execution `989659` were still `new`/queued at closeout. Last accepted successes were `988482` and `988484`, before the final attribution fallback was verified end-to-end. Exact post-fallback source counts remain unverified.
- **Reporting health repair boundary:** Attribution Bridge (`Y0TU7Il71JswxOBp`) is active/published at `08d15fa4-e513-4ada-939e-51c3584440a7` with deterministic identity-key deduplication; Leads Ingest is active/published at `7057fd10-a7db-4888-98ad-4adb1af1c2cc` with contact-owner preservation; Report QA (`M5mXcDTFSko6EdHb`) is active/published at `004f260e-7153-4ab7-9e30-dc066ea2458`. Queued bridge executions `989774` and `989781` remain unaccepted; verify the next successful bridge and QA runs before calling `bridge` or owner coverage healthy.

### EOS Closeout — LinkedIn Inbound OAuth Renewal and Retry — 2026-09-24

- **Root causes:** the LinkedIn inbound fallback SQL referenced the nonexistent live column `linkedin_conversation_map.payload_json` instead of `raw_payload`; the stored GHL OAuth access token then returned HTTP 401 from `/oauth/locationToken`; and the six-hour OAuth renewal workflow was failing at `Check Refresh Token Source` with `Could not get parameter "jsCode"`.
- **Live fixes:** published the map SQL correction; refreshed the OAuth token; replaced the OAuth renewal workflow's two successful-path Code nodes with native Set nodes and expressions; and changed inbound OAuth 401s to enter a durable retry queue instead of bypassing renewal with the location PIT.
- **Post-renewal retry:** `LT - LinkedIn Inbound OAuth Retry` (`4Qww6KyTxnoRAs9m`) runs at `10 */6 * * *`, ten minutes after the six-hour renewal, claims up to 50 queued messages, exchanges the renewed agency token for a location token, replays the GHL inbound message, and finalizes each row with bounded retry state (maximum five attempts). Its active path uses native HTTP Request/Set/IF/Postgres nodes and has no Code node.
- **Recovered messages:** Andrew Timmons → conversation `XuidkqTq5Mk6eZqSmDxo`, message `c9vhcydCCtoSV3hs6wQZ`; Anthony Riley → conversation `NVqlWtYpYDCrUZNVg0Vb`, message `J1UZapNyJEHEEwus4k0V`.
- **Verification:** LinkedIn executions `986969` and `986971` succeeded with `status=processed`. OAuth renewal execution `986997` succeeded with GHL HTTP 200, `expires_in=86399`, active token row `42`, and expiry `2026-09-25T11:36:12.632Z`.
- **Current live state:** inbound workflow `7o5EBdvwAuIaWW7k` is active/published at `ec870256-8946-4ff6-be46-e55eab4710b7` (reverted Sales Navigator exclusion; all LinkedIn DMs accepted); OAuth refresh workflow `Mf4wdFNurt5vyQu4` is active/published at `c04eadaa-507f-4066-90ea-341ea2b2be45`; retry workflow `4Qww6KyTxnoRAs9m` is active/published at `c0f666a1-fb11-4423-955f-b284fdc600d0`.
- **Verification:** empty-queue retry execution `987023` completed successfully through claim, token-exchange/context, no-token branch, and finalizer with no outbound GHL message. No live send was performed for this change.
- **Cron verification 2026-09-25:** the six-hour OAuth renewal cron ran at `2026-09-24T13:00:00Z` as execution `987233` and completed successfully. It refreshed and stored a new active token; the stored expiry was `2026-09-25T13:00:00Z`. The workflow remains active/published at version `c04eadaa-507f-4066-90ea-341ea2b2be45` with schedule `0 */6 * * *`.
- **Next session:** verify the next scheduled renewal at the next six-hour boundary and inspect node-level data if it fails. Detailed handoff: [`docs/sessions/2026-09-24-linkedin-inbound-and-ghl-oauth-eos-closeout.md`](docs/sessions/2026-09-24-linkedin-inbound-and-ghl-oauth-eos-closeout.md).

### SimpleTexting Automatic SMS/MMS Routing — LIVE 2026-09-24

- The canonical SimpleTexting path now reads GHL provider `attachments[]` and automatically chooses text-only `AUTO` mode or `MMS_PREFERRED` for one HTTPS attachment.
- The first implementation supports one attachment. More than one attachment, invalid/non-HTTPS media, and invalid send modes fail closed before the provider call.
- The idempotency hash now includes the media URL, mode, and fallback text, so an SMS and an MMS with the same caption cannot collide. Successful GHL mirroring carries the media URL in `attachments`.
- If SimpleTexting rejects the MMS provider request, the idempotent boundary sends one fallback `AUTO` SMS containing the original text plus the hosted media URL. The result records `deliveryMode = SMS_LINK_FALLBACK` and `fallbackUsed = true`.
- **Live versions:** Send `Q3Ivnwe4z2Y3cD7A` = `47de44fe-d1bf-4f3d-8040-a70f759466a1`; Provider Router `f4VoO1lBWkYRcQai` = `444e2709-b6c1-4e61-9087-2e79387e8648`; Idempotent Sender `gwaEpWDpTIwsafi8` = `52eefd2a-70be-41c9-a60a-2fce0f037929`. All three are active and each `versionId` matches `activeVersionId`.
- **Verification:** dry-run webhook checks passed for text-only (`AUTO`), one attachment (`MMS_PREFERRED`), and two attachments (`multiple_attachments_unsupported`). JavaScript syntax checks and `git diff --check` passed. No provider send, live MMS, fallback send, campaign activation, or sender schedule change was performed.
- **Backups:** exact pre-change workflow definitions are in `local-archive/n8n/workflows/*-before-simpletexting-mms-20260924T112004Z.json`.
- **Repository source:** [`scripts/utilities/fix_simpletexting_boundaries.py`](scripts/utilities/fix_simpletexting_boundaries.py). The operator payload contract is documented in [`GHL Live Transparent CRM/GHL_To_SimpleTexting_SMS_Send_Runbook.md`](GHL%20Live%20Transparent%20CRM/GHL_To_SimpleTexting_SMS_Send_Runbook.md).

### SimpleTexting GHL Conversation Mirror Guard — LIVE 2026-09-24

- **Follow-up finding:** the contact URL showed two identical GHL custom-provider conversation records (`nc6gtHV3I8SijxVNDxZe` and `7ytLOPgjzWcASmXZoCR3`) even though the idempotent sender recorded only one SimpleTexting provider message (`6ab4344e1cfe7305284262c8`). The duplicate was the successful-send mirror branch, not a second provider API send.
- **Fix:** `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`) now includes the resolved source on successful output and requires `source != ghl_workflow` before `Mirror to GHL Conversations` runs. Normal GHL-originated sends therefore retain the GHL-created message and skip the second mirror; explicitly external sources can still mirror.
- **Live version:** `17dae562-5f38-4438-a8bd-ee19adc6eb57`, active and equal to `activeVersionId`; read-back confirmed the three-condition success route and `sms-no-ghl-mirror` guard.
- **Verification boundary:** no SMS was sent or manually executed. `git diff --check` passed. Next validation is one natural or explicitly approved controlled send, confirming one GHL custom-provider record and one provider message ID.

### EOS Closeout — SimpleTexting Duplicate Send Loop — 2026-09-24

- **Objective:** stop each SimpleTexting message from being delivered twice.
- **Root cause:** the legacy SimpleTexting send workflow sent the SMS, then mirrored it into GHL Conversations. GHL emitted that mirror as a provider-outbound event, and the SimpleTexting Provider Outbound Router sent the same body again. The two paths used different idempotency identities (`Q3Ivnwe4z2Y3cD7A` versus `provider_outbound`), so the second path was not deduplicated.
- **Live fix:** Provider Router `f4VoO1lBWkYRcQai` now calls the canonical idempotent sender with workflow identity `Q3Ivnwe4z2Y3cD7A`. Idempotent Sender `gwaEpWDpTIwsafi8` now hashes the message body consistently instead of preferring a template label, making the original send and its GHL mirror share one idempotency key.
- **Live versions:** Provider Router `8aa3dc21-2178-4d45-85d1-7081f35164e9`; Idempotent Sender `9d587b17-fa9a-409c-90ac-0cc8a68c2fba`. Both are active and each `versionId` matches `activeVersionId`.
- **Evidence:** paired live executions showed the original send followed by the provider-mirror send, with distinct provider message IDs; the later provider retry was then recognized as `duplicate_send`. No live SMS was sent as part of the repair. No pending executions remained at verification.
- **Repository:** the reproducible source change is in [`scripts/utilities/fix_simpletexting_boundaries.py`](scripts/utilities/fix_simpletexting_boundaries.py). `git diff --check` passed. The worktree also contains the prior uncommitted SimpleTexting 2026-09-22 closeout changes; do not stage unrelated work.
- **Next session:** observe one natural outbound event or obtain approval for one controlled SMS to an approved recipient. Confirm exactly one SimpleTexting provider message ID, one GHL mirror, and a duplicate/accepted router result. Do not activate campaign schedules or send additional tests without approval.
- **Detailed closeout:** [`docs/sessions/2026-09-24-simpletexting-duplicate-send-closeout.md`](docs/sessions/2026-09-24-simpletexting-duplicate-send-closeout.md).

### EOS Closeout — SimpleTexting Router Response Fix — 2026-09-22

- **Objective:** correctly classify provider-accepted GHL outbound SMS responses without sending a live SMS during the fix.
- **Root cause:** the live Provider Outbound Router accepted only `status=sent` or `status=duplicate`, while the canonical sender returned `action=message_sent` with a provider message ID. Accepted sends were therefore reported as `provider_send_failed`.
- **Live fix:** Router `f4VoO1lBWkYRcQai`, node `Process Provider Outbound`, now accepts `action=message_sent`, preserves `status=sent`, and preserves duplicate handling. The workflow remains active with 7 nodes; live version `02483e18-3776-415a-9630-160adb66cb94` matches `activeVersionId`.
- **Verification:** read-back confirmed the exact code is live; `git diff --check` passed; no live SMS was sent. Pre-change backup: `local-archive/n8n/workflows/f4VoO1lBWkYRcQai-before-simpletexting-response-fix-20260921T182447Z.json`.
- **Next session:** obtain explicit approval for one controlled GHL SMS to an approved recipient, then verify router/canonical execution success, provider message ID, GHL conversation mirroring, and delivery callback state. Keep campaign sender workflows paused/staged.
- **Detailed closeout:** [`docs/sessions/2026-09-22-simpletexting-router-response-fix-closeout.md`](docs/sessions/2026-09-22-simpletexting-router-response-fix-closeout.md).

### EOS Closeout — Hide Executive Report Outgoing Calls — 2026-09-19

- **Objective:** hide the Executive Report's empty `Outgoing Call Detail` panel while retaining aggregate Calls & Conversations metrics and the diagnostic endpoint.
- **Repository implementation:** `reports/embed/executive/index.html` removes the sidebar link, section markup, outgoing-call loader/pagination code, and client request to `/api/report/executive/outgoing-calls`; build stamp is `2026-09-19-v34-hide-outgoing-calls`.
- **Documentation:** `reports/README.md` now records that the endpoint remains available for diagnostics while the report UI hides the detail section.
- **Verification:** `git diff --check` passed; the Executive Report inline script parsed successfully with Node; no outgoing-call UI or API-request references remain in the frontend.
- **Live-state boundary:** no deployment, publish, container mutation, n8n change, or external-service write was performed in this session. The worktree contains the uncommitted frontend and documentation changes recorded in the dated closeout handoff.
- **Next session:** review the diff, deploy the report host when approved, then verify the public page returns build stamp `2026-09-19-v34-hide-outgoing-calls`, the sidebar and panel are absent, and aggregate call metrics still render. Keep the outgoing-call endpoint and nginx route available for diagnostics.

### Executive Report Source Health and Cache — DEPLOYED 2026-09-19

- Source Health now exposes runtime-path rows for `n8n` and `postgres`, plus appointment snapshot freshness from `report_raw_ghl_appointments`; the dashboard maps all three instead of leaving misleading `—`/`Pending` placeholders.
- The primary report now renders as soon as the Executive Summary response arrives; Campaign Channels and prior-period comparison load asynchronously afterward.
- Executive Summary workflow `Bukc0mgOD2r7V6ED` is active/published at `00285be3-e4b5-4741-95a9-474b2c74ce00`.
- This older 2026-09-19 cache state is superseded by the 2026-09-26 deployment: Summary, Campaign Channels, and V1 Facts now use a 30-minute successful-response TTL, cache locking, and stale-if-error fallback. Cache keys include selected range/from/to values.
- Live 7-day verification returned HTTP 200, 29,909 bytes, cache `HIT`, and health `appointments=ready`, `n8n=ready`, `postgres=ready`.
- Detailed closeout: [`docs/sessions/2026-09-19-executive-report-source-health-cache-closeout.md`](docs/sessions/2026-09-19-executive-report-source-health-cache-closeout.md).

### GHL OAuth Renewal Hardening — SUPERSEDED BY 2026-09-24 CLOSEOUT

- The 2026-09-19 runtime follow-up below is historical. The runtime `jsCode` failure was reproduced and repaired on 2026-09-24; see the current closeout at the top of this file and [`docs/sessions/2026-09-24-linkedin-inbound-and-ghl-oauth-eos-closeout.md`](docs/sessions/2026-09-24-linkedin-inbound-and-ghl-oauth-eos-closeout.md).

- `LT - GHL OAuth Token Refresh` (`Mf4wdFNurt5vyQu4`) is active at schedule `0 */6 * * *`; current active/published version is `3ee6b021-c45b-47cc-a428-d1b7f8fb9e15`, with `versionId == activeVersionId`.
- The former Slack failure alert node was removed. Failure handling now resolves `edmundocadorniga@gmail.com` as a GHL contact, prepares a sanitized failure email, sends it through the authenticated GHL Conversations Email boundary, and then fails the n8n execution. The email includes status/failure details, an uninstall/reinstall recommendation, and the GHL app renewal link.
- Read-only verification found no `new`, `running`, or `waiting` executions, and n8n `/healthz` returned HTTP 200. Prior scheduled executions `953348`, `958394`, and `961802` completed successfully.
- **OPEN runtime issue:** latest scheduled execution `964056` at `2026-09-18T19:00:00Z` failed at `Check Refresh Token Source` with `Could not get parameter "jsCode"`. The current workflow read-back contains non-empty `jsCode` for every Code node, so the failure may reflect a stale/partial runtime workflow cache or an n8n execution-state discrepancy. Do not claim the next renewal is proven until the next scheduled run is observed.
- A one-time GHL email transport test returned `Email queued successfully`; this proves API acceptance only, not inbox delivery. No manual OAuth-failure replay was run during EOS.
- **Next session:** inspect the next scheduled execution and its node-level run data. If the `jsCode` error recurs, investigate/reload the active workflow under explicit approval before changing the renewal logic. If it succeeds, verify that the normal path stores the refreshed token and that the failure route remains fail-closed.
- Detailed handoff: [`docs/sessions/2026-09-19-ghl-oauth-renewal-hardening.md`](docs/sessions/2026-09-19-ghl-oauth-renewal-hardening.md).

### Executive Report Backfill Accuracy Repair — DEPLOYED 2026-09-19

- Fixed the September 6–12 contradiction where Contacts showed 260 but Attribution Coverage showed 259. A shared distinct, non-backfill contact cohort now drives Contacts, coverage, source attribution, and funnel denominators.
- Excluded Unipile/historical-backfill contacts from current-period Contacts, opportunities, MQL/SQL facts, Lead Source totals, and SDR SQL counts. Raw records remain preserved for historical/audit use.
- Restored Campaign Channels and Campaign Breakdown in the Executive Report. Fully zero activity rows are now hidden in both tables; any non-zero metric keeps the row/campaign visible. The API/source data remains unchanged. Sept 6–12 verification: Contacts `25`, cohort `25`, Lead Source SQL total `52`, SDR SQL total `52`; campaign APIs returned 13 and 7 rows.
- Executive Summary workflow and frontend state in this intermediate repair were superseded later on 2026-09-19 by the Source Health and Cache closeout below; the backfill-accuracy findings remain valid.
- Detailed closeout: [`docs/sessions/2026-09-19-executive-report-backfill-accuracy-repair.md`](docs/sessions/2026-09-19-executive-report-backfill-accuracy-repair.md).

### Executive Report Presentation Cleanup — DEPLOYED 2026-09-19

- Live frontend build `2026-09-19-v30-executive-report-cleanup` hides the duplicate deal panels, zero/empty Vapi and campaign panels, observed UTM/ad traffic, unvalidated Forms metrics, and Search Console panel from the Executive Report while preserving source data and API fields.
- The Metric Glossary is collapsed. LinkedIn via Unipile lead-source variants are merged only for display, with MQL/SQL counts summed; no attribution rows were deleted.
- Public frontend returned HTTP 200 with the new build stamp. Executive Summary API returned HTTP 200 with a non-empty response. Reversible container backup: `/usr/share/nginx/html/embed/executive/index.html.bak-20260919-v30`.
- Detailed closeout: [`docs/sessions/2026-09-19-executive-report-cleanup-closeout.md`](docs/sessions/2026-09-19-executive-report-cleanup-closeout.md).

Updated: 2026-09-18 (Executive Report GA4/GSC freshness restored and end-to-end rollup verification)

### EOS Closeout — Executive Report Data Freshness — 2026-09-18

- **Objective:** verify that the operator's reconnected GA4 and GSC credentials propagated through ingest, bridge, and report rollup workflows.
- **Verified successful executions:** GA4 ingest `959043` (866 rows), GSC ingest `959044` (9 rows), GA4 bridge `959047`, GSC bridge `959048`, and Report Daily Rollups `959072` (8 rows). All completed with `success`.
- **Current report health:** GA4 `success`, GSC `success`, and rollups `ready`; no GA4/GSC OAuth error remains. Last successes were approximately `2026-09-17 16:47 UTC`; rollups completed at approximately `16:53 UTC`.
- **Endpoint verification:** the public 30-day Executive Summary endpoint returned current metrics including traffic `1,906`, organic search users `42`, GSC clicks `2`, impressions `125`, CTR `1.60%`, and average position `20.728`.
- **Safety boundary:** no sender workflow, email send, CRM mutation, deployment, commit, or push was performed for this closeout.
- **Next action:** monitor the next scheduled GA4/GSC ingest and rollup runs. If either source becomes stale again, inspect the latest ingest execution and OAuth credential before changing report SQL or frontend behavior.

Updated: 2026-09-17 (Apollo September 2026 GHL import/tag/opportunity closeout, mass-email activation state, repository organization, and Executive Report attribution audit reconciled)

### Executive Report Email Attribution Audit — API REGRESSION RESOLVED; FOLLOW-UPS OPEN 2026-09-17

- Read-only audit handoff: [`docs/sessions/2026-09-17-executive-report-api-regression-and-email-attribution-audit.md`](docs/sessions/2026-09-17-executive-report-api-regression-and-email-attribution-audit.md).
- **RESOLVED:** `LT - Report Executive Summary API` (`Bukc0mgOD2r7V6ED`) had five ambiguous `contact_id` references in `email_campaign_attribution`. They were qualified as `s.contact_id`; the response projection was also updated to expose `emailCampaignAttribution` and `emailAttributionCoverage`. Active/published version: `4816fea0-3722-4d59-b552-bc84a616e948`.
- **Verification:** `GET https://reports.livetransparent.com/api/report/executive/summary?range=30d` returned HTTP 200 with a 36,184-byte body, 8 attribution rows, and coverage metadata (`sendRows=78,729`, `uniqueRecipients=26,350`, `unambiguousRecipients=271`).
- **RESOLVED 2026-09-17:** `LT - Newsletter Dispatcher` (`vru7OtCkDnPJkWt2`) now derives the newest pending week/template dynamically and fails closed if the matching builder is absent. The next scheduled run will be the first runtime validation; no manual sender execution was used.
- **RESOLVED 2026-09-17:** Campaign Channel Summary now honors stored campaign keys and explicitly maps the live Emerald event labels (`campaign_id = Emerald Cannabis Ads` and `WL - Event - Emerald Email Event Ingest - *`) to `Emerald - Email Event`.
- **PARTIALLY RESOLVED 2026-09-17:** Email Event Ingest now persists message ID, provider message ID, source event ID, campaign key, and sender email for new events. DAN event automations are still not wired to the ingest; do not attempt historical campaign recovery until that wiring and a fresh coverage measurement are complete.
- **Next session order:** (1) wire DAN event automations to the enriched Email Event Ingest, (2) observe the next newsletter scheduled run without manually triggering a sender, (3) remeasure attribution coverage after new enriched events arrive, and (4) investigate only genuinely unresolved/ambiguous historical rows. Do not guess ambiguous historical events.
- **Attribution improvements applied 2026-09-17:** Newsletter Dispatcher `vru7OtCkDnPJkWt2` now derives the newest pending week from `newsletter_send_log`, discovers its matching GHL builder by week key, and generates claim SQL dynamically; active version `88c53670-6e0a-4f2d-a4c4-3f27ca3ffdff` equals `activeVersionId`. Campaign Channel Summary `MvPLbUAN9IIQikxb` now honors explicit `Email_Events.campaign_key` and maps the live Emerald event label/workflow values to `Emerald - Email Event`; active version `9bcb5e46-f2a4-484a-ad6e-7761c6538cef` equals `activeVersionId`. Email Event Ingest `ZrqFN8qLKO8eVHDc` now persists message ID, provider message ID, source event ID, campaign key, and sender email; active version `e57c2664-f0f1-484f-b3a6-32bba41ff125` equals `activeVersionId`.
- **Follow-up regression repaired 2026-09-17:** The new `Email_Events.campaign_key` column made `campaign_key` ambiguous inside the Executive Summary attribution CTE. This caused recent Query Summary executions to fail and the embed's fail-soft loader to show placeholders/zeros. The CTE now qualifies `s.campaign_key` and `s.campaign_group`. Executive Summary active/published version: `da17ea49-6473-4e33-9df5-9d93bf6cf273`. Fresh verification returned HTTP 200 with a 36,184-byte body; latest execution succeeded. An HTTP 200 with an empty body is now treated as a failure symptom, not valid report data.

### Repository File Organization — CLOSEOUT 2026-09-17

- File organization and cleanup closeout: [`docs/sessions/2026-09-17-file-organization-closeout.md`](docs/sessions/2026-09-17-file-organization-closeout.md).
- All 117 versioned root scripts are now categorized under `scripts/<domain>/`; navigation: [`scripts/README.md`](scripts/README.md) and [`docs/repository-file-map.md`](docs/repository-file-map.md).
- The Apollo September 2026 preparation/import artifacts are grouped under `data/runs/2026-09-16-apollo-vp-ghl/`.
- Disposable caches/browser artifacts were removed; `.monitor/` state and the identifying untracked LinkedIn screenshot were preserved.
- Verification passed for JavaScript syntax, path references, required artifacts, and `git diff --check`. Python compilation still reports pre-existing syntax errors in three retained one-off scripts: `scripts/instagram/batch_instagram_validate_and_send.py`, `scripts/social-reporting/fix_brands_code.py`, and `scripts/utilities/x.py`.
- No commit, push, deployment, restart, production workflow execution, CRM mutation, campaign send, or external-system write was performed.

### Apollo C-Suite and Marketing September 2026 GHL Batch — CLOSED OUT 2026-09-17

- Source `Apollo_VP_Contacts.csv` contained 485 rows. Preparation produced 477 apparent new-contact rows after 8 exact-email matches; one prepared row had no email. The operator completed the CSV imports, including a 32-row phone-collision retry with phone values moved to `Em_All_Known_Phones`.
- The expected tag count did not appear in GHL after the operator’s email/tag-only update import. The assistant directly reconciled the 114 source emails absent from the tag-search result with email-based GHL upserts, omitting phone values to avoid phone-collision errors. All 114 upserts returned contact IDs and verified the tag.
- The GHL tag search remained an incomplete/lagging cohort indicator and returned 395 contacts on the final check. This count must not be treated as proof that the full 476 email-bearing source cohort is absent from GHL.
- Opportunities were created/reconciled for the 395 contacts currently returned by the tag search. Destination: `Sales Outreach` pipeline (`dhdlf3O4tymxFtHk4aqq`) → `New` stage (`3529dd3d-cab0-4279-967c-1aea203de4fb`). Final state: 361 in the requested pipeline/stage; 25 already had an opportunity elsewhere and were left unchanged; 9 transient 400 responses were confirmed afterward to already have the requested opportunity. No duplicate opportunities were created by the final state.
- Artifacts: `data/runs/2026-09-16-apollo-vp-ghl/Apollo_VP_Contacts_Sep2026_GHL_New_Contacts_Import.csv`, `data/runs/2026-09-16-apollo-vp-ghl/Apollo_VP_Contacts_Sep2026_GHL_Phone_Collision_Retry.csv`, `data/runs/2026-09-16-apollo-vp-ghl/apollo_114_upsert_log.csv`, `data/runs/2026-09-16-apollo-vp-ghl/apollo_tag_opportunity_create_log.csv`, and `docs/sessions/2026-09-17-apollo-csuite-sep2026-ghl-import-closeout.md`.
- Remaining caveat: the visible GHL tag search does not currently expose the full source cohort. Any further recovery should use an exact-email/contact-ID reconciliation and should not create additional opportunities solely from the visible tag count.
- Organization: the complete Apollo preparation bundle is now under `data/runs/2026-09-16-apollo-vp-ghl/`; the file-level repository map is `docs/repository-file-map.md`; versioned automation is categorized under `scripts/<domain>/` and indexed by `scripts/README.md`. The identifying screenshot remains intentionally untracked at the repository root.

### GHL Email-Template Mass Delivery and Reporting — ACTIVE, DRY-RUN PROTECTED 2026-09-17

- **Objective:** allow a GHL automation to submit any GHL email template—newsletter, announcement, follow-up, promotion, or another approved message—to a protected n8n webhook. n8n snapshots eligible GHL contacts, excludes suppression/DND states, distributes delivery across the three existing sender identities, and retains delivery/event reporting.
- **Template contract:** the webhook requires `event=email_template.requested`, a stable `idempotencyKey`, `campaignKey`, and `templateId`. `templateName` and `subject` are optional; `subject` is snapshotted when supplied. The immutable campaign label is `Template Name — campaign-key`; template renames do not rewrite historical attribution.
- **PostgreSQL schema — APPLIED (non-sending):** `postgres/mass-email-bootstrap.sql` was executed against the `postgres` DB. Live tables `lt_mass_email_campaigns`, `lt_mass_email_deliveries`, `lt_mass_email_events`, 4 indexes, and the `lt_mass_email_campaign_metrics` view exist. Additive columns for the claim model were added (`campaigns.subject/queued_at/planned_count`, `deliveries.claimed_at/run_id`). The live intake schema node matches the versioned file byte-for-byte. One test campaign/delivery is intentionally retained (see below); all other test rows were removed.
- **Intake — ACTIVE/PUBLISHED:** `LT - GHL Email Template Trigger Intake (STAGED)` (`t5frjtbuKzVZI294`, version `9523da34-9306-462b-b24f-72594a62a023`). Webhook `/webhook/lt-email-template-trigger-stage`. Validates the dedicated `X-LT-Mass-Email-Secret`, ensures the schema, and idempotently upserts one campaign row (`ON CONFLICT (idempotency_key)`), returning `202` with `campaignId`/`created`; unauthorized requests return `401`, invalid requests return `400` with no row.
- **Queue — ACTIVE/PUBLISHED:** `LT - GHL Email Template Campaign Queue (STAGED)` (`vRXRFC6IwIxUME2k`, active version `714b2d22-777c-4006-a233-d7e0fa6eb930`). Claims `accepted` campaigns, paginates all GHL contacts, excludes no-email/duplicate/blocked-tag/`validEmail=false` contacts, assigns `.co`, `.org`, and `.agency` senders round-robin, and writes idempotent delivery rows. Temporary recipient/contact allowlists are cleared. `defaultDryRun=true` remains enabled.
- **Dispatcher — ACTIVE/PUBLISHED:** `LT - GHL Email Template Campaign Dispatcher (STAGED)` (`b41Sas8FVVrytZrl`, active version `bf892c33-edca-416d-9b74-cff2ccea9fdf`). Resolves each campaign's GHL template HTML, atomically claims planned deliveries, re-fetches each contact and fails closed on suppression/lookup errors, enforces per-sender daily caps (2333), sends via the GHL Conversations Email boundary, injects signed open/click tracking, captures provider message IDs, retries 429/5xx, and finalizes campaign status. `defaultDryRun=true` remains enabled, so provider calls are still disabled.
- **Tracking — BUILT/FIXED:** `LT - Mass Email Open Tracking (STAGED)` (`J7xZH6BBnoXEQsoB`), `LT - Mass Email Click Tracking (STAGED)` (`TbYFpB80xSlRZ6gy`), `LT - Mass Email Provider Event Ingest (STAGED)` (`f87KRQ1Slhs9VUxJ`). All inactive. The `Config` node is now wired between webhook and record node; open/click also stamp delivery timestamps; the provider-event responder returns JSON.
- **Acceptance tests PASSED (all non-sending):** duplicate webhook retry returned the existing campaign (`created:false`); invalid request returned `400` with no row; queue dry-run produced planned counts with zero writes; queue live-planning created 5 deliveries with round-robin senders; dispatcher dry-run produced 5 planned and **0 sent**; dispatch-time suppression blocked a tagged contact (`suppressed:1`, `sent:0`); signed open/click tokens resolved only to the intended delivery (bad token rejected); provider `delivered` event updated the delivery; the metrics view reported 2 open events as `total_opens=2`/`unique_opens=1` without inflating planned/sent/delivered. All test rows were deleted afterward (0 campaigns/deliveries/events).
- **Recipient allowlist:** both Config nodes now have empty `recipientAllowlist` values and the queue has an empty `contactIdAllowlist`; the temporary single-contact boundary is removed. The suppression blocklist remains active.
- **First controlled live send (2026-09-16):** with the allowlist set, one campaign (`allowlist-test-2026-09-16`, template `6a87716221922afe5eda9e6f` "Newsletter 1 2026-08-24", subject "The real reason regulated ads get disapproved") was planned to exactly one recipient and sent. Delivery `id=8` reached `status='sent'`; the campaign finalized as `completed`. The dispatcher was returned to `defaultDryRun=true` immediately after.
- **DELIVERABILITY ROOT CAUSE + FIX (2026-09-16, historical `.com` transport test):** the first `.co` test was delivered through the `.com` Mailgun transport and failed DMARC alignment; the aligned `.com` test scored 8.8/10. This remains historical evidence about the previous transport path. The generic queue/dispatcher are now configured for `.co`, `.org`, and `.agency`, but each sender still requires a fresh transport-level SPF/DKIM/DMARC verification before live sending.
- **Known limitation:** the GHL email-builder API does not expose a template subject. The dispatcher resolves the subject as: operator-supplied `subject` → parenthesized text in the template name → template name. There is no mass-email unsubscribe webhook; unsubscribe is handled via provider events. The open/click/provider tracking workflows remain **inactive**, so open/click events are not recorded until they are activated.
- **Activation verification:** publishing automatically activated the queue and dispatcher. Queue execution `956286` succeeded with `campaigns=0`; dispatcher execution `956284` succeeded with `sent=0` and `dryRun=true`. Earlier queue execution `956269` also completed successfully. Final verification found no `new`, `running`, or `waiting` executions. Activation did not enable live provider sends because `defaultDryRun=true` remains set.
- **GHL caller state:** workflow `fe14c3bf-c1ed-4b91-b0fc-e9b5e55d3e71` remains unpublished, so it is not currently submitting new campaigns to intake.
- **Pre-activation hardening applied:** the intake validates `X-LT-Mass-Email-Secret`; the provider-event webhook validates a separate `X-LT-Mass-Email-Provider-Secret`, uses `POST` for body-bearing callbacks, and maps handler status codes to the actual response. Open/click tracking remains `GET`. The intake is active/published; provider events and open/click tracking remain inactive pending caller configuration and approval.
- **Detailed handoff:** `docs/sessions/2026-09-16-ghl-triggered-newsletter-design.md`.

**2026-09-17 live-state supersession:** Queue `vRXRFC6IwIxUME2k` and dispatcher `b41Sas8FVVrytZrl` are active/published at versions `714b2d22-777c-4006-a233-d7e0fa6eb930` and `bf892c33-edca-416d-9b74-cff2ccea9fdf`. Both use `cameron@livetransparent.co`, `cameron@livetransparent.org`, and `cameron@livetransparent.agency`; temporary recipient/contact allowlists are empty and the suppression blocklist is preserved. Both retain `defaultDryRun=true`, so activation has not enabled provider sends. Queue execution `956286` and dispatcher execution `956284` succeeded with zero live sends; execution `956269` also completed. No `new`, `running`, or `waiting` executions remained at final verification. Treat older inactive/.com-only statements in this historical section as superseded. Next: verify transport-level SPF/DKIM/DMARC per sender, then approve and change `defaultDryRun=false` for the intended campaign.

**Next steps, in order:**

1. **[ASSISTANT, completed]** Intake authentication and provider-event `POST` hardening are deployed; open/click tracking remains `GET`.
2. **[USER, GHL UI] Fix the newsletter DMARC failure** — the screenshot shows `mg.livetransparent.com`, `mg.livetransparent.agency`, `mg.livetransparent.co`, and `mg.livetransparent.org` already present with `SSL Issued`. Only `.com` is selected; `.agency`, `.co`, and `.org` are unselected and at warmup Stage 1 (0/1000). Select/enable the additional domain(s) only if GHL permits them for this sub-account. If only one domain can be selected, keep `.com` selected and use only its sender. No API exposes this; it is a UI task.
 3. **[ASSISTANT] Verify the newsletter fix** — after each domain is selected, send a mail-tester test from its sender and confirm the envelope/signature domain matches the From domain and authentication passes. Do not retain a multi-domain newsletter pool based on DNS records alone; each domain needs transport-level proof.
4. **[ASSISTANT, pending]** Change dispatcher `defaultDryRun=false` for the approved campaign only after transport-level sender verification and confirmation of the template, cohort, maximum recipient count, sender boundary, and send window.
 5. Decide whether to add a mass-email unsubscribe link/webhook (currently provider-event only), and whether to activate the open/click/provider tracking workflows (they are inactive, so opens/clicks are not recorded).
 6. Replace/raise the per-sender daily cap (2333) if `@livetransparent.com` is used for bulk, since one sender cannot cover ~22k/week.

**EOS closeout — 2026-09-16 (mass-email build + deliverability root cause)**

- **Objective/scope:** build the GHL-triggered generic email-template mass-delivery pipeline (intake → queue → dispatcher + tracking), verify with non-sending tests, then run one controlled send to the owner's address.
- **Completed:**
  - Applied `postgres/mass-email-bootstrap.sql` as a non-sending migration (tables, 4 indexes, metrics view, additive claim-model columns).
  - Built/rewrote intake `t5frjtbuKzVZI294` (idempotent campaign upsert), queue `vRXRFC6IwIxUME2k`, dispatcher `b41Sas8FVVrytZrl`, and fixed tracking `J7xZH6BBnoXEQsoB` / `TbYFpB80xSlRZ6gy` / `f87KRQ1Slhs9VUxJ` (wired `Config`, added delivery timestamps, JSON responder).
  - Added `recipientAllowlist` (queue+dispatcher) and `contactIdAllowlist` (queue) for controlled sends.
  - Ran the full inactive/dry-run acceptance suite (duplicate retry, invalid→400, dry-run zero-write, round-robin planning, dispatch dry-run 0 sent, dispatch-time suppression, signed-token validation, provider event, metrics non-inflation). All passed; test rows deleted.
  - Ran the first controlled live send and diagnosed why it was not received.
- **Live state (fresh API read-back):** the authenticated intake is **active/published** at `fb82073e-…`; queue `0d292f47-…` (6 nodes, `defaultDryRun=true`, `recipientAllowlist=edmundocadorniga@gmail.com`, `senders=cameron@livetransparent.com`), dispatcher `a005c68a-…` (8 nodes, `defaultDryRun=true`, same allowlist/senders), open `13f7e658-…`, click `bbc4fd13-…`, and provider `296ad86b-…` (4 nodes each) remain inactive. Newsletter prep `vvPdJMzBJMgcf5I9` and dispatcher `vru7OtCkDnPJkWt2` remain **active** (unchanged). No executions in `new`/`running`/`waiting`.
- **DB state:** 1 campaign (`allowlist-test-2026-09-16`, `completed`) and 1 delivery (`id=8`, `sent`, `cameron@livetransparent.com`, provider `ShpyiNhtPKv5C8WHtByl`) retained as the evidenced test send; 0 events.
- **Root cause (deliverability):** GHL LC Email for this location sends **all** mail via `mg.livetransparent.com` (Mailgun) regardless of `emailFrom`; a `From:` on `.co`/`.agency`/`.org` does not align → SPF/DKIM unaligned → **DMARC fails** → Gmail spam. mail-tester: `.co` 5.6/10 "not fully authenticated" vs `.com` 8.8/10 "properly authenticated". **Confirmed:** the `.com` send arrived in the inbox (not spam) with `mailed-by`/`signed-by: mg.livetransparent.com`.
- **Not accepted / caveats:** the disposable `mail.tm` inbox never received the probe (provider-level filtering, not a pipeline fault); the tracking workflows are inactive so no open/click events were recorded; the `.co`/`.agency`/`.org` newsletter senders are still broken.
- **Worktree:** intentionally uncommitted. Modified: `AGENTS.md`, `Project Status and Next Steps.md`, `docs/sessions/2026-09-16-ghl-triggered-newsletter-design.md`, `postgres/mass-email-bootstrap.sql`. `git diff --check` passes (LF→CRLF warnings only). Many unrelated untracked Apollo-CSV/import artifacts exist in the worktree — do not stage them. Helper scripts are git-ignored under `local-scripts/`.
- **Historical safety snapshot (superseded 2026-09-17):** the earlier closeout kept all six workflows inactive and the test allowlist in place. Current state is recorded above; queue and dispatcher are active, temporary allowlists are empty, and `defaultDryRun=true` remains the live-send guard.


### LinkedIn Outbound Safety Bug Fixes — CLOSED 2026-09-16

- **Objective:** prevent malformed/garbage-character LinkedIn messages and correct confirmed daily-limit, duplicate-send, state-secret, and outbound-validation defects in the active LinkedIn paths. Scope was limited to the active dispatcher/DM and Partnership dispatcher/DM workflows plus the active suppression workflow; inactive Follower/Test copies and repository archive sources were not changed.
- **Live workflows updated and published:** `LT - GHL LinkedIn Connect Dispatcher` (`fXxw5lanZcDmUrst`, active version `6ae708aa-990f-4784-87b2-573ab81dc4f4`, 10 nodes); `LT - LinkedIn DM Sequence (Unipile)` (`d0tEtijajisIsYcs`, active version `afcdad57-a770-4bb0-8eae-be1f7623e674`, 12 nodes); `LT - Partnership LinkedIn Dispatcher` (`crKIsaL5k3YBfqDZ`, active version `0fc1611f-80c9-45f8-8c93-89c74f2eeca1`, 10 nodes); `LT - Partnership LinkedIn DM Sequence` (`nspggypNF245xzeL`, active version `92e85568-3e4a-4677-b3ee-ab66dd0915a4`, 6 nodes); and `LT - LinkedIn DM Suppression from GHL Tag` (`IPN8jnR3XSurX0o1`, active version `ededf18b-1355-4f8d-ad4d-1b0381382cb8`, 5 nodes). All five were fresh-GET verified active with `versionId == activeVersionId`.
- **Fixes applied:** daily counter now accumulates passed sends (`dailySent + passed`); Partnership DM and invite paths have stable event deduplication; state-upsert callers use evaluated runtime secrets rather than literal placeholder text; active senders have final fail-closed printable-ASCII/message validation, unresolved-placeholder and mojibake checks, and per-contact failure handling where applicable.
- **Copy proof:** fresh live GETs parsed the actual template registries: dispatcher invites and the five DM literals in both DM sender nodes contain zero apostrophes and zero non-ASCII characters; the ten canonical rewritten strings remain present. A whole-node character scan was rejected as unreliable because it counts JavaScript syntax and sanitizer tables; literal-level parsing is authoritative.
- **Verification artifacts:** temporary backups and proof outputs are under `%LOCALAPPDATA%\\Temp\\lt_bugfix_*`; no project files or credentials were copied into the report. The apply script returned an initial false-negative on two prefix-insertion checks; computed expected-text re-verification passed, followed by the fresh GET and literal-level copy proof.
- **Not run:** no manual sender execution, provider test send, CRM mutation, activation change, commit, or push was performed during EOS. Do not execute a production sender merely as a smoke test without explicit approval.
- **Remaining risks/blockers:** the LinkedIn state-upsert receiver still needs a separate approved change to validate `X-LT-LinkedIn-State-Secret`; hardcoded credential fallbacks remain in some node JS and should be migrated under a separate approval. The broader LinkedIn reply-suppression design in the next section remains pending and was not silently combined with this fix.
- **Closeout:** [`docs/sessions/2026-09-16-linkedin-outbound-safety-bugfix-closeout.md`](docs/sessions/2026-09-16-linkedin-outbound-safety-bugfix-closeout.md).

### LinkedIn Reply Suppression — IMPLEMENTATION PLAN / APPROVAL PENDING 2026-09-14

- Read-only audit and detailed next-session handoff: [`docs/sessions/2026-09-14-linkedin-reply-suppression-audit-and-plan.md`](docs/sessions/2026-09-14-linkedin-reply-suppression-audit-and-plan.md). The same handoff is linked near the top of `AGENTS.md`.
- Live checks found uneven protections: the main DM sequence and GHL connection-request dispatcher perform a GHL inbound-conversation lookup before sending; the partnership DM sequence relies only on cached `dm_conversation_status`. The active inbound webhook writes that cache only after GHL inbound posting and conversation-map persistence. The 10-minute reply poller rechecks an individual row only when its prior check is at least 6 hours old. Therefore the partnership path has a confirmed stale-state window, and inbound suppression can be delayed by preceding CRM/map work.
- The existing GHL filter `lastMessageDirection=inbound` describes the latest message direction, not a durable “has ever replied” fact, and current sender checks are not restricted to LinkedIn-provider conversations. Retain it as a fail-closed fallback/reconciliation check, not the primary suppression source.
- **Recommended design:** record confirmed inbound LinkedIn replies idempotently in a canonical suppression table keyed by Unipile account + sender provider ID (with GHL/contact aliases and message ID). Persist it immediately after inbound/outbound direction is established, before GHL post/map work. Gate every automated LinkedIn connection invite and DM sequence on this record immediately before the provider send; fail closed on read errors. Keep existing GHL and cached-state checks as defense in depth. Preserve human-initiated replies through the GHL custom-provider outbound router.
- Screenshot attribution remains unverified. The repeated text matches the connection-invite template; confirm the prospect/contact and sender execution before naming the exact workflow. The partnership sender gap is independent and verified.
- No production workflow, CRM record, sender, or live test changed. **No implementation or live send without explicit approval.** The supplied screenshot is local, untracked prospect data and is intentionally excluded from commits.

### LinkedIn Backfill Encoding / Provider-Routing Incident — CONTAINED 2026-09-11

- The Caio Aguilar example was reproduced in live GHL conversation `ekMEbotkDTlLayytKs6Z`: the outbound body was stored as `canΓÇÖt`, and the source Unipile payload already contained the malformed `\u0393\u00C7\u0096` sequence.
- Root cause had two layers: the historical batch helper posted raw Unipile outbound messages without applying the 60-day filter, and GHL's live custom-provider callback routed those outbound history posts back to Unipile. Router execution `938260` confirmed Caio's historical post was sent to chat `lv_RFArVVG-esf6_QQrZWg` at `2026-09-11T12:07:50Z`.
- The worklist is drained: 381 chats done, 16 held for ambiguous GHL contact matching, 12 held for Unipile profile `422` failures; 1,528 messages posted and 78 skipped. No further backfill batch should run without redesign.
- Containment: `scripts/linkedin/run_linkedin_backfill_batch.py` now skips historical outbound messages so it cannot invoke the live provider sender. The earlier canonical LinkedIn DM Sequence sanitizer version `4ca4d791-37d1-4da0-a4ef-6fbe40db1b3f` was superseded by the permanent formatter/eligibility hardening recorded below.
- Existing malformed/duplicate messages were not deleted or edited. Do not send a cleanup reply until the operator decides whether to leave them, manually remove them, or send a corrected follow-up.

### LinkedIn Outbound Formatting and Eligibility Audit — CLOSED 2026-09-11

- **DM workflow**: `LT - LinkedIn DM Sequence (Unipile)` (`d0tEtijajisIsYcs`) is active and published on `fcb0d053-7cac-456f-a4ad-41ba240966c0` (`versionId == activeVersionId`, 12 nodes).
- **Connection dispatcher**: `LT - GHL LinkedIn Connect Dispatcher` (`fXxw5lanZcDmUrst`) is active and published on `346f28be-a6a4-4fc1-99c3-5b5d6ba2d0ea` (`versionId == activeVersionId`, 10 nodes).
- Both workflows now use regex-free placeholder replacement and character/code-point normalization, with fail-closed rejection of unresolved placeholders and known mojibake markers before provider sends.
- Real GHL contacts require a successful GHL inbound-reply check; an existing inbound reply skips the message and a failed check also skips it. LinkedIn-only records with synthetic IDs beginning `linkedin:` bypass only the GHL check because no GHL contact exists; they remain subject to LinkedIn state, suppression, and provider eligibility checks.
- Audit verification: both live workflows retained their expected schedules and graph connections; recent DM runs `938923` and `937817` completed without Code-node errors but sent zero before the synthetic-ID eligibility change because all five candidates failed the invalid GHL lookup. Dispatcher execution `936647` completed without a workflow crash but had 10 provider `422` invite failures before the formatter patch. No uncontrolled or manual production test was run.
- **Next verification**: observe the next scheduled DM run and inspect its `Send DM Sequence Messages` result for `sent`, `skipped`, and `dm_failed` outcomes. Do not manually execute either sender workflow or send a test message without explicit approval.

### LinkedIn 60-Day Message Backfill — EXECUTION CONTAINED 2026-09-11

- **Approved scope (user):** backfill the last 60 days of LinkedIn messages into GHL Conversations.
- **Discovery baseline:** 8,753 total Unipile LinkedIn chats; **409 chats** with last activity on/after the 2026-07-12 cutoff; **818 messages** in the window (**176 inbound / 642 outbound**). Largest single chat: 24 messages. Artifacts are preserved in git-ignored `local-scripts/` (no secrets).
- **GHL automation impact assessed:** `WL - Micro - LinkedIn DM` and `WL - Micro - LinkedIn` (both published) trigger on LinkedIn DM reply/engagement events but only add tags (`Warm  LinkedIn DM` / `Warm  LinkedIn`) and set UTM First-if-empty / Last attribution — no Slack, tasks, or SDR assignment. Backfilled inbound messages will mark conversations unread in the operator inbox.
- **Execution outcome:** the worklist-driven backfill completed 381 chats, posting 1,528 messages and skipping 78. Sixteen chats remain held for ambiguous GHL contact matching and 12 for Unipile profile `422` failures. No further broad batch should run without redesign and manual resolution of held rows.
- **Containment:** `scripts/linkedin/run_linkedin_backfill_batch.py` now skips historical outbound messages so it cannot invoke the live provider sender. Existing malformed or duplicate messages were not deleted or edited.
- **Safety gates:** the backfill remains inactive; production posts require explicit user approval; do not clear `only_chat_id` or launch another broad batch without a redesigned/idempotent process and a fresh operator decision.
- **Foundation verified earlier 2026-09-11:** the live inbound workflow (`7o5EBdvwAuIaWW7k`, version `3dab7e61-b2e4-45c6-8e6d-055b8c05623e`, active, 19 nodes) and the patched backfill (outbound endpoint + dedup + `only_chat_id`, draft `11378e3a-8c81-46f1-bda7-933b1884c78d`, inactive, 5 nodes) are the correct building blocks; see the LinkedIn Conversations Fix section below.
- **Held rows:** do not post the 16 ambiguous-match or 12 profile-failure chats without manual resolution and explicit approval.

### LinkedIn Conversations Inbound Fix — CLOSED + E2E VERIFIED 2026-09-11

- **Objective**: Fix GHL `/conversations/messages` 422 errors in `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`) to enable proper inbound message posting to GHL Conversations.
- **Root cause 1 (endpoint)**: the node posted to `/conversations/messages` instead of `/conversations/messages/inbound` — the `/inbound` suffix is required for posting inbound messages. Fixed and published in the 2026-09-10 session.
- **Root cause 2 (response misinterpretation, fixed 2026-09-11)**: the node used `resolveWithFullResponse: true` with `this.helpers.httpRequest` — silently ignored, so every successful post was misread as `inbound_failed: status=undefined body={}`. Fixed to `returnFullResponse: true` with a hardened error describer; prior test posts had actually landed in GHL.
- **Root cause 3 (jsonb corruption, fixed 2026-09-11)**: all 6 `Build * SQL` Code nodes double-escaped backslashes in `'...'::jsonb` literals, crashing `Upsert LinkedIn Map` ("invalid input syntax for type json") and preventing `linkedin_conversation_map` persistence whenever a payload contained an embedded quote. Backslash doubling removed; `'` → `''` retained.
- **Published version**: `3dab7e61-b2e4-45c6-8e6d-055b8c05623e` (`versionId == activeVersionId`), active, 19 nodes. Script: `scripts/linkedin/fix_linkedin_inbound_response_and_jsonb.py`.
- **E2E verified (approved)**: one labeled test post through the production webhook returned `status=processed` with extracted `ghl_conversation_id`/`ghl_message_id` and `mapping_row_id=42` persisted. The 3 test messages were then removed by deleting the test conversation (`B6Enrm2D2LtsXPhi1qLY`); the synthetic `Test Sender` contact remains by user choice.
- **Gretchen 422 resolved**: the inactive backfill routed historical OUTBOUND messages to the nonexistent `/conversations/messages/outbound` path (the 422 cause). Backfill patched (outbound → `/conversations/messages`, conversation-message dedup, Config `only_chat_id` = Gretchen chat) and a Gretchen-only retry posted both historical outbound messages (execution `934099`, verified in conversation `I3w8fRaPzecv7CXnI8oe`). GHL stamps `dateAdded` at post time; historical dates are not backdated.
- **Postgres timeout theory disproven**: lookup/upsert Postgres nodes complete in ~2s; the OAuth token is read from `ghl_oauth_tokens` in-reach of n8n. Local python calls to `services.leadconnectorhq.com` need a browser `User-Agent` (Cloudflare 1010 blocks python-urllib).
- **Remaining follow-ups**: controlled reply test from GHL Conversations against a backfilled chat (user-requested, not yet run); clear the backfill `only_chat_id` before any broader backfill; broader historical backfill still requires idempotency review.
- **Closeout**: `docs/sessions/2026-09-10-linkedin-conversations-fix-closeout.md` (with 2026-09-11 follow-up section).

### LinkedIn Inbound DM Contact-Gating — DECISION PENDING 2026-09-11

- **Verified (live, read-only):** `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`, active, version `3dab7e61-b2e4-45c6-8e6d-055b8c05623e`) has **NO connection-invite gate** — Unipile webhook `linkedin-new-messages` (enabled, `message_received`) fires for any chat on the account; the code only gates on payload valid → `is_inbound` → account LINKEDIN. New incoming DMs from non-invited senders ARE processed today.
- **Verified behavior mismatch:** when the sender has no state/map row and no scored GHL match, the `Create LinkedIn Contact and Add Inbound Message` node **creates a brand-new GHL contact** (`reason: created_new_contact`, tags `linkedin_inbound`/`unipile_linkedin`) and imports the message anyway; `mapped_id_fallback` can also post to a contact ID that no longer exists in GHL. This does NOT match Ed's rule: *"import them as long as the contact is in GHL."*
- **PENDING DECISION (Ed, 2026-09-11):** apply "import only if contact exists in GHL" — skip with `status: skipped / reason: contact_not_in_ghl`, never create contacts, drop `mapped_id_fallback` (or require a live fetched contact). Ed wants to decide later, flag as resolve-soon. **No workflow change made.**
- **Scope note for the eventual fix:** revisit the backfill's "safe contact-create fallback only when GHL returns no candidates" (line 15 above) so the contact-gating rule is consistent across webhook inbound AND backfill execution.
- **Closeout**: `docs/sessions/2026-09-11-linkedin-inbound-dm-gating-decision.md`.

### Script And n8n Archive Organization — CLOSEOUT 2026-09-10

- Reusable operator helpers are kept in ignored `local-scripts/`; historical n8n exports, backups, and one-off patch inputs are kept in ignored `local-archive/n8n/`.
- Fifty historical n8n snapshot files were moved out of Git but retained locally for audit/reference. Live n8n remains the production source of truth; archived files must not be redeployed without reconciliation.
- Retained generator/reporting sources use environment placeholders instead of credential literals. `node --check` passed for `n8n/gen.js` and `scripts/n8n/fix_intake_poller.js`; `git diff --check` and the added-change credential scan passed.
- At that closeout, the branch was clean and synchronized with `origin/codex/social-outreach-sync` at `daf0432`. This organization pass made no live workflow, CRM, campaign, sender, deployment, or production-test changes. The current worktree has since accumulated documented session changes; do not treat this historical statement as current branch status.
- Closeout: `docs/sessions/2026-09-10-script-and-n8n-archive-closeout.md`.
- Next: treat `local-archive/n8n/` as workstation-only storage, keep future raw exports ignored, and run a dedicated full-repository secret audit before any broad staging operation.

### Business Improvement Plan and Shareable Guides — CLOSEOUT 2026-09-10

- The review-only strategy plan is `improvementPlan.md`. It now opens with a plain-language `Start Here` guide, a 60-second summary, document map, jump links, role-specific reading paths, video-informed positioning, customer FAQ, reusable messaging, booking bridge to Cameron, and Executive Report recommendations.
- The full plan was converted to `Transparent eCom Business Improvement Plan - Full.docx` with a table of contents and heading structure. The generated DOCX remains untracked and has not been committed.
- The condensed Google Doc is `https://docs.google.com/document/d/1UmDOLE1ujd7MQqmZGWwOOzpLnIqOILw2I6EMYEvtiGQ/edit`. It was verified under `ed@livetransparent.com`, saved to Drive, set to anyone-with-link access, and contains the full-plan link at the top.
- The full converted Google Doc is `https://docs.google.com/document/d/1Fb98oS5xztVfb-hW_qiqVUdTFuDQe2Vi/edit`; it was verified under `ed@livetransparent.com` and saved. Its title still includes `.docx`, so confirm native Google Docs conversion if required.
- No production message, template, website, workflow, CRM record, campaign, sender, or live test was changed or executed for this strategy/documentation work.
- Verification: `git diff --check` passed with only existing LF/CRLF warnings. The exact full-plan URL was confirmed in the condensed guide after the initial link insertion did not persist.
- Current risks: claims and FAQ answers need Cameron/owner approval and proof references; the homepage video supports the positioning direction but was not fully transcribed or claim-audited; the worktree contains unrelated dirty and untracked files, so stage only reviewed files.
- The sample landing page was built and deployed as an isolated review preview on 2026-09-10. It remains separate from production and still requires Cameron approval before any production implementation. Deployment details: `docs/sessions/2026-09-10-sample-landing-page-preview-deployment.md`.
- Detailed closeout: `docs/sessions/2026-09-10-business-improvement-plan-and-shareable-guides-closeout.md`.

### Sample Landing Page — REVIEW PREVIEW DEPLOYED 2026-09-10

- **Objective:** review the isolated landing-page sample demonstrating the intended Transparent eCom positioning, visitor journey, qualification language, proof areas, FAQ, and direct booking CTA.
- **Plan:** `Sample Landing Page/PLAN.md`.
- **Implementation boundary:** use plain HTML, CSS, and JavaScript. Keep the prototype isolated from the production website, CRM, GHL workflows, campaigns, senders, and live tracking.
- **Preview:** `http://vkrlibgdjdi4u6iz8hokue00.89.117.21.29.sslip.io/`.
- **Deployment status:** the container is running on the Coolify Docker network with Coolify/Traefik routing labels. The normal Coolify image-pull deployment failed because the original image was not registry-backed; the final container was started manually from a temporary VPS-local registry. Coolify's application record still needs reconciliation before normal Coolify lifecycle controls can be trusted.
- **Verification:** HTTP 200, page assets loaded, no console errors, no unexpected network requests, and no horizontal overflow at approximately 390px. HTTPS is not currently working for the generated preview hostname.
- **Booking boundary:** use a placeholder CTA during early review. Add the approved GHL calendar widget only after page structure and copy are accepted; do not add a duplicate lead form before it.
- **Next review:** test keyboard navigation, focus states, contrast, copy, proof references, and CTA behavior with Cameron. Do not add the GHL booking widget or production tracking before approval.
- **Approval gate:** Cameron must approve positioning, claims, proof references, qualification language, and CTA before this sample becomes a production implementation pattern.

### Business Improvement Plan and Platinum Email Pilot — PLANNING ONLY 2026-09-10

- **Objective:** create a full business improvement plan covering positioning, ICP, offers, funnel, sales operations, fulfillment, compliance, measurement, email strategy, deliverability, and controlled channel scaling.
- **Plan artifact:** `improvementPlan.md` is now the review-only strategic plan. It includes a 0-90 day roadmap, confirmed evidence versus hypotheses, decision gates, specific email cadences and draft messages, proposed workflow improvements, a no-traction decision tree, a dedicated campaign landing-page specification, and a separate main-website improvement strategy.
- **Email recommendation:** do not add SendGrid or more GHL senders yet. First reconcile email execution history against newsletter/campaign release logs and Email Event Ingest, verify SPF/DKIM/DMARC and sender reputation, reduce reliance on opens, and run one bounded segment/message test.
- **Current email risks:** the system already has multiple sender identities and high theoretical newsletter capacity; the newsletter runbook notes that `2,333` per sender per day is materially above the documented `300/day` warm-up guidance. Additional senders must not be used to bypass deliverability, suppression, or platform limits.
- **Platinum pilot:** the Platinum GHL tag is a candidate cohort, not proof of verified business quality. Before any send, use a read-only cohort review to classify records as verified business, needs research, out of scope, duplicate, suppressed/active, or unusable. Start with 25 manual reviews and no more than 10-15 verified contacts in the first email cohort.
- **Platinum email approach:** use a low-pressure, relationship-oriented three-email sequence; one segment and role at a time; no calendar link in the first email unless intent exists; stop on reply, correction, suppression, or final close-the-loop message. Personalization observations require a source URL, observed date, confidence, expiry, and approval.
- **Proposed future workflows:** Email Program Controller, Email Preflight and Health Monitor, Reply and Intent Router, Booking Nurture, Post-Meeting Follow-up, Reactivation, Deliverability Ledger, and Email-to-Revenue Attribution Bridge. These are recommendations only and have not been built or activated.
- **Strategy boundary:** the deployed sample (`Sample Landing Page/`) remains a non-production review artifact. Its placeholders, unsupported claims, proof state, legal links, and tracking configuration remain strategy gates; no production website or landing-page copy was changed.
- **Verification performed:** reviewed `improvementPlan.md`, current project status, project specifications, email runbook, Emerald campaign plan, and relevant live-state findings. `git diff --check` produced no content errors; line-ending warnings are environmental. No live message, campaign, workflow, sender, CRM record, or production test was changed or executed in this session.
- **Documentation refresh:** the required `packlive` command was attempted after the strategy update but is not available in the current shell/profile, so `repomix-output.md` was not regenerated. This is a documentation-refresh follow-up only and does not affect the strategy artifact.
- **Unaccepted tests:** no Platinum cohort was queried or sent; no sender/domain change was made; no SendGrid migration was tested; no production email workflow was executed; no claim is made that the email execution-history discrepancy is resolved.
- **Next session order:** (1) fetch the exact live Platinum tag and cohort count; (2) produce a read-only quality and suppression report; (3) reconcile email workflow executions, send logs, and event ingest; (4) audit sender authentication and domain reputation; (5) obtain approval for one segment, offer, and 10-15-contact pilot; (6) build only the approved research/review and measurement pieces before any send.
- **Safety gates:** do not send live email, SMS, LinkedIn, Instagram, or Vapi tests without explicit approval; do not add senders to evade limits; do not publish new email workflows; do not place unreviewed or unverified Platinum contacts into an automated sequence; preserve DND, unsubscribe, complaint, reply, duplicate, and active-opportunity suppression.

### LinkedIn OAuth and Historical Message Backfill — HISTORICAL SNAPSHOT, SUPERSEDED 2026-09-11

- **OAuth reinstall verified:** `Transparent eCom Social Inbox` was reinstalled for Live Transparent. Social Provider Outbound Router (`kqIi8i1RjFAZKrK3`) received the authorization callback and exchanged the code successfully in execution `930484` (HTTP 200); a fresh token is stored in `ghl_oauth_tokens`.
- **Redirect contract clarified:** The app's default Auth redirect must remain `https://automations.livetransparent.com/webhook/lt-social-provider-outbound`. Its GET branch handles OAuth installation; its POST branch handles LinkedIn/Instagram provider payloads. Do not replace or remove this route from the app Auth configuration.
- **Backfill workflow hardened:** Inactive `LT - LinkedIn Conversation Backfill` (`JUvrA7qMa24SwAZG`) now reads the current OAuth token from `ghl_oauth_tokens` through the `Postgres account` credential; the embedded stale token was removed. It remains inactive.
- **Historical snapshot:** Execution `930588` posted six messages and left Gretchen's two outbound messages at HTTP 422. This was superseded by the 2026-09-11 backfill repair and incident closeout: the worklist is now drained for 381 chats, with 16 ambiguous matches and 12 Unipile profile failures held; no further broad batch should run without redesign.
- **Current verification boundary:** The backfill remains inactive. Existing malformed or duplicate messages were not deleted or edited. A controlled reply test against a backfilled chat remains optional and requires explicit approval.
- **Current closeout:** [`docs/sessions/2026-09-10-linkedin-conversations-fix-closeout.md`](docs/sessions/2026-09-10-linkedin-conversations-fix-closeout.md) and the 2026-09-11 incident section above are authoritative for this work.

### SimpleTexting GHL Provider Route — FIXED 2026-09-09

- **Incident:** SMS sent from GHL Conversations reached the live provider router, but outbound delivery was rejected. The latest retained attempt (`f4VoO1lBWkYRcQai`, execution `916048`) returned a provider-side HTTP 409 with no provider message ID.
- **Root cause fixed:** The Provider Outbound Router was calling the stale internal `/webhook/lt-sms-send` path and using its retired authentication value instead of the canonical active send workflow `Q3Ivnwe4z2Y3cD7A` at `/webhook/lt-simpletexting-send-sms`. It also did not explicitly pass `dryRun=false`, so the canonical workflow would have applied its safe dry-run default.
- **Live fix:** Router `f4VoO1lBWkYRcQai` now calls the canonical send webhook, uses its configured internal authentication value, and explicitly passes `dryRun=false`. It remains active and published with matching draft/active version `302ec7de-0b82-462f-9a22-b1420abf62c6`; graph remains 7 nodes with 2 webhook triggers.
- **Other paths checked:** Inbound reply (`i0pROHpFtN4LYR0Q`), delivery events (`AEi1VCzkLvaYFr4U`), unsubscribe events (`IyBKMkpYQ7pa0C8V`), and phone backfill (`8hQKQi1PooYDFxNR`) were active with successful recent executions. Automated campaign sender workflows remain intentionally unpublished.
- **Verification boundary:** No live SMS was sent as a test. The next operator-initiated GHL SMS is the required functional validation; inspect the router and canonical send execution for `sent` plus a provider message ID. If it still returns HTTP 409 after this route fix, investigate the SimpleTexting account/provider response rather than changing retry behavior blindly.
- **Detailed closeout:** [`docs/sessions/2026-09-09-simpletexting-ghl-provider-route-fix.md`](docs/sessions/2026-09-09-simpletexting-ghl-provider-route-fix.md).

### Executive Report — SDR Performance & Owner Attribution (IMPLEMENTED 2026-09-09 — Phases 1–5; monitoring/sign-off remains)

- **Request:** Cameron needs booked meetings tracked by SDR for the end-of-month SDR assessment (focus on SQL / booked meetings; MQL secondary). Marketing requires per-SDR owner attribution, booked meetings, showed/no-show, SQLs created, MQL→SQL conversion, clarification of the former owner-labelled active deals view, and lead-source breakdown for MQL/SQL.
- **Verified:** owner data is ALREADY captured in the ingests — `report_raw_ghl_opportunities.dimensions_json->>'assigned_to'` (Sales Ingest extracts `assignedTo`/`ownerId`), `report_raw_ghl_appointments.assigned_user_id` + `contact_id` (Appointments Ingest), and full contact objects in `report_raw_ghl_contacts.payload_json`. The Executive Summary SQL previously never projected any owner field.
- **Root causes of the marketing findings:** (1) top KPI `meetingsBooked` (opportunity-stage-based, via Daily Rollups) vs the Meetings panel (appointments table by `start_at`) were two different sources → 3 vs 7. (2) "Showed" is stuck at 0 because GHL `appointmentStatus` is never flipped post-meeting (GHL-side data-entry gap; report bucket logic is correct). (3) "Team Active Deals" is the same team-wide opportunity payload relabeled, not owner-filtered.
- **Phases 1–2 live 2026-09-09:** `report_sdr_registry` (user map) + owner-coverage health probes (`ghl_opp_owner_coverage` 34.6%, `ghl_appt_owner_coverage` 11/31) in `report_source_health`; Daily Rollups carries `assigned_to`; Exec Summary returns `sdrPerformance` per-owner rows (booked / showed / no-show / cancelled / SQLs / MQL→SQL / won / lost / revenue) and `meetingsBooked` now uses appointments-by-`start_at` (basis `appointments_start_at`; `meetingsBookedStageBasis` preserved); query runs `SET jit=off` (16–19s vs ~71s before). Frontend deployed as build `2026-09-09-v28-sdr-performance` (SDR Performance table + nav + glossary; Team Active Deals; desktop + 390px verified).
- **Phase 4 live 2026-09-09:** Exec Summary adds `leadSourceBreakdown` (per source+medium: MQLs Entered / SQLs Created in window) + `leadSourceCoverage` (attributed/total), resolving each MQL/SQL contact → first UTM source/medium/campaign → bridge fallback → GHL `source`; "Unknown / Unattributed" groups unresolvable rows (30d: 32/164 SQLs, 0/3 MQLs attributed — bounded by the ~500-row Leads snapshot). Frontend build `2026-09-09-v29-lead-source` with a Lead Source panel + nav + glossary, desktop + 390px verified. Active version `162bbba8…`; timing unchanged (~17s). See `docs/sessions/2026-09-09-executive-report-sdr-attribution-phase4-lead-source.md`.
- **Remaining:** monitor the live meeting-outcome reminder and confirm Showed/No-show updates; Cameron/Janvi sign-off on ranking wording; reconcile MQL definitions if needed; verify future booking SDR capture at runtime. Janvi and the previously unknown owner IDs have been resolved/seeded.
- **Full plan + verified findings + gates:** `docs/sessions/2026-09-09-executive-report-sdr-attribution-plan.md`. **Implementation + verification:** `docs/sessions/2026-09-09-executive-report-sdr-attribution-phase1-2.md` (Phases 1–2) and `docs/sessions/2026-09-09-executive-report-sdr-attribution-phase4-lead-source.md` (Phase 4).

### SDR Attribution for Regulated-Ads Bookings — Capture-at-Booking Fix (Option A) — Booking webhook deployed 2026-09-10

- **Problem:** When an SDR (Jason `yU85G6kfhtW4vUtx3QE6`, Marc `sqGx5rp3oAUG610NXyjU`) books a regulated-ads meeting on Cameron's "Regulated Ads" calendar (`SrtXcFVyea7pFl3nTiIK`), the SDR never gets credit in the Exec Summary `sdr_booked` bucket. Root cause confirmed at GHL (system of record): the handoff automation flips opportunity ownership to Cameron, and the SDR is not captured in any field that survives (appointments `createdBy.source=booking_widget` with null userId; opp `assigned_to` unassigned/Cameron from creation; contact `assignedTo` never an SDR). Historical bookings are unrecoverable from every source checked — the fix is future-only.
- **Chosen fix (Ed, 2026-09-09): (A) Capture-at-booking**, contact-side. The hourly "GHL Leads Ingest" (`osIJOgBmWITF5Yuv`) already persists contact `customFields` into `report_raw_ghl_contacts` (2,173/2,696 rows carry them), so a GHL-stamped contact field flows into the report DB automatically — **no ingest change needed**.
- **GHL capture configuration:** Contact field `Originating SDR` is live as `TEXT`, id `wBGXjev0rKowcfxTSWNa`. GHL workflow `Appointment with Cameron for Regulated Ads` (`971c3016-946a-4612-ad0a-2afc9a0ee6f0`) is confirmed `published`, version 14, updated 2026-09-09 17:09:26 UTC, and is distinct from `LT - Opportunity Owner Alignment`. The public GHL workflow-list API does not expose action bodies, so the `assignedSDR` payload still requires runtime webhook confirmation.
- **n8n booking handler LIVE:** `WL - Webhook to Slack Channel Update` (`lQTW0QPwBcf3o7j8`) version `1cb05fcd-e0c0-4ae1-9413-637878325e8e`, active and published. `Build Slack Payload` maps Jason/Marc/Cameron email values to GHL user IDs and stamps `Originating SDR` before SQL-tag/opportunity writes.
- **Exec Summary activation LIVE:** `Bukc0mgOD2r7V6ED` reads field id `wBGXjev0rKowcfxTSWNa` in active version `08abd9cb-7100-4e31-88d1-4413aadee625`; the placeholder is removed and the fallback owner chain remains intact.
- **Verification boundary:** Workflow state/version reads passed and no production test execution was run because the handler mutates GHL and posts Slack. No executions are currently `new`, `running`, or `waiting`.
- **Next session:** observe the next real booking, verify the already-published GHL workflow supplies the expected `assignedSDR` value, confirm the contact custom field contains the expected GHL user ID, check n8n `sync.originatingSdr = stamped`, and confirm the Exec Summary SDR booked count. Historical bookings remain unrecoverable.
- **Docs:** diagnosis `docs/sessions/2026-09-09-sdr-attribution-success-booking-gap-diagnosis.md`; design `docs/sessions/2026-09-09-sdr-attribution-fix-design-option-a.md`; this closeout `docs/sessions/2026-09-10-sdr-attribution-booking-webhook-closeout.md`.

### Coolify Runner PostgreSQL Network Path — RESOLVED and under monitoring — 2026-09-07

- Detailed record: [`docs/sessions/2026-09-07-runner-network-path-verification.md`](docs/sessions/2026-09-07-runner-network-path-verification.md) and post-fix results in [`docs/sessions/2026-09-07-runner-network-path-fix-applied.md`](docs/sessions/2026-09-07-runner-network-path-fix-applied.md).
- Root cause: the authoritative live Coolify-generated Compose file had `n8n-runner` with `extra_hosts: postgres:host-gateway` and attached only to the private resource network `n44wksswcocwk88ogcog8c48`. This caused `postgres` to resolve to the Docker host gateway (stale `10.0.0.1`) instead of the healthy PostgreSQL container on `coolify-shared` (`10.0.2.3`).
- **FIX APPLIED 2026-09-07 UTC**: removed the runner `extra_hosts` entry and attached `n8n-runner` to `coolify-shared` (alongside its private broker network) in the live Coolify-generated Compose file. A timestamped backup of the file was created before the edit; compose syntax validation passed; the runner container was recreated.
- **VERIFIED**: runner is dual-homed (`10.0.2.5` on `coolify-shared`, `10.0.4.4` on the private network); `getent hosts postgres` from the runner resolves to `10.0.2.3` (not `10.0.0.1`); TCP `postgres:5432` reachable from runner and n8n main; n8n `/healthz` returns `{"status":"ok"}`; runner registered (`launcher-javascript`, `launcher-python`).
- **END-TO-END PROOF**: workflow `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`r7UjWLndmc6EqEUW`) failed every 2 minutes with `connect ECONNREFUSED 10.0.0.1:5432` before the fix (through 14:52 UTC) and now succeeds post-fix (14:54, 14:56, 14:58, 15:00, 15:06, 15:07 UTC — all `status=success`).
- Monitoring continues via the Hermes monitor cron + email alerting (see below). The n8n internal pool-closure incident is SEPARATE and remains unresolved at root-cause level.

### n8n 2.37.10 Force Redeploy and Monitoring — 2026-09-07

- Detailed record: [`docs/sessions/2026-09-07-n8n-force-redeploy-and-monitoring.md`](docs/sessions/2026-09-07-n8n-force-redeploy-and-monitoring.md).
- The authoritative live Coolify Compose stack was force-recreated with build/pull enabled. n8n is running `n8nio/n8n:2.37.10`; the external runner was rebuilt and both containers had zero restarts at verification time.
- A VPS-native root cron monitor is installed at `/usr/local/sbin/livetransparent-n8n-health.sh`, scheduled for minute 5 of every hour (`5 * * * *`). It is monitor-only and performs no automatic remediation.
- **HERMES HOURLY MONITOR (live, replaced 2026-09-09)**: job `LT hourly infra+email monitor (Telegram)` (`9622fde81b78`) runs every 60 minutes with Telegram delivery (`deliver=telegram`). A deterministic gate (`C:\1_Ed's Active Work\AI\Hermes\scripts\lt_alert_gate.py`) SSHes to the VPS and checks n8n `/healthz`, PostgreSQL container health, runner state/restarts, and Gmail alert-subject emails (`[LiveTransparent]` `UNHEALTHY|RECOVERED|ALERT`). The agent runs ONLY when the gate output changes, then classifies from FULL email bodies, applies read-only + safe auto-fix (reversible/idempotent/credential-safe only), and escalates to Ed via Telegram — ONE message per issue, ids marked processed only on resolution. Old 30-min jobs `33eea46dd9b3` and `b3f164cd1746` are PAUSED (folded into the hourly monitor). Record: [`docs/sessions/2026-09-09-workflow-incident-alerts-skill-review-and-hourly-telegram-monitor.md`](docs/sessions/2026-09-09-workflow-incident-alerts-skill-review-and-hourly-telegram-monitor.md).
- **TELEGRAM DELIVERY: CONFIGURED AND VERIFIED 2026-09-09** (`message_id=416` delivered to `telegram:8712052921` on the manual 13:47 run).
- **EMAIL TRANSPORT: CONFIGURED AND TESTED.** Hermes Google OAuth token has Gmail scopes (`gmail.send`, `gmail.readonly`, `gmail.modify`) for `edmundocadorniga@gmail.com`. A test message was sent and confirmed (`SENT_OK id=1a07c62cb42810a4`). The OAuth access token auto-refreshes via the refresh token when expired.
- The earlier n8n pool-closure incident remains unresolved at root-cause level; it is tracked separately and the watch-fix never auto-fixes that class.
- Required alert recipient: `edmundocadorniga@gmail.com` (configured).

### n8n PostgreSQL Pool Closure Investigation — 2026-09-07

- Follow-up investigation documented in [`docs/sessions/2026-09-07-n8n-pool-closure-investigation.md`](docs/sessions/2026-09-07-n8n-pool-closure-investigation.md).
- Confirmed immediate mechanism: n8n remained alive while its internal PostgreSQL pool was already ended; `Cannot use a pool after calling end on the pool` caused readiness failure and authenticated workflow API HTTP 503 (`Database is not ready!`).
- The process, deployment event, database/network event, or n8n code path that first called `pool.end()` remains unresolved. Do not assume the pool issue is fixed because a redeploy succeeded.
- Do not restart PostgreSQL/Redis or rotate `N8N_ENCRYPTION_KEY` without evidence and explicit approval. If n8n remains unhealthy, a targeted n8n-only restart through Coolify requires approval and post-restart verification.

### Next Session Checklist

1. The runner network-path fix is APPLIED and VERIFIED (see above). Re-inspect live state only if the monitor alerts; do not re-apply blindly.
2. The hourly monitor job `9622fde81b78` is live (replaced the two 30-min jobs on 2026-09-09). Verify it stays healthy via `hermes cron list` / `hermes cron runs 9622fde81b78`; expect NO agent run and NO Telegram message while the gate output is unchanged (dedup working).
3. If the runner-network alert recurs, the hourly agent auto-applies only the bounded, reversible fix class and escalates via Telegram; manual re-verification of the next pg-using workflow is still recommended.
4. If a pool-closure alert (`Cannot use a pool after calling end on the pool`) recurs: capture the workflow execution, runner and n8n logs, container network/DNS state, and PostgreSQL reachability BEFORE any restart. Do not restart PostgreSQL/Redis or rotate `N8N_ENCRYPTION_KEY` without evidence and explicit approval.
5. Separately investigate the original `pool.end()` caller that caused the pool-closure incident; the runner network fix does not establish that n8n's internal pool lifecycle bug is resolved.
- The previously separate GA4/GSC credential issue was resolved and verified on 2026-09-09; investigate again only if the report source-health monitor regresses.

### Newsletter Dispatcher Timeout Optimization (2026-09-04)

- Execution `887738` of `LT - Newsletter Dispatcher` (`vru7OtCkDnPJkWt2`) was canceled at the 10-minute execution boundary while `Dispatch Emails` was still sending. The failure was throughput-related: up to 250 emails were sent serially, with per-message database writes and 250-400 ms pacing. Recent execution `886414` had taken approximately 9 minutes.
- Replaced only the `Dispatch Emails` Code node loop with a bounded five-worker pool. Sender-cap reservations are made before work starts, each send retains the existing retry policy and idempotent status update, and each worker retains the pacing delay. No manual production execution was run.
- Live workflow verification: workflow is active and unarchived, with 8 nodes and matching `versionId`/`activeVersionId` `366610f7-acaf-4d32-980e-1c0d08485185`. The updated Code node passed a syntax-only async-context check.
- The next scheduled execution is the required live functional verification. Do not manually execute this workflow or increase concurrency without reviewing GHL rate-limit behavior and sender-cap results.

### Executive Report Audit + Fixes (2026-08-30 / 2026-08-31)

### Executive Report Runtime Recovery (2026-09-04)

- n8n readiness briefly failed with `Database is not ready!` because the JavaScript task runner had a stale `postgres:host-gateway` entry resolving to `10.0.0.1`, while the healthy PostgreSQL service is on `coolify-shared`.
- Recreated the live Coolify runner without the stale `extra_hosts` override and attached it to both the private n8n broker network and `coolify-shared`. The runner now resolves `postgres` to the Docker service at `10.0.2.3`.
- Restarted n8n once to clear the ended connection pool. PostgreSQL was healthy and was not restarted.
- Verified `healthz/readiness`, Executive Summary, Campaign Channels, and Outgoing Calls all return HTTP 200. Browser verification returned zero console errors.
- Changed `LT - GSC Daily Ingest` (`xHqmCC1vOeZ11gCd`) from a 24-hour interval trigger to the explicit daily cron `0 2 * * *` UTC. Successful executions `887723` and `887730` completed after the change; GSC health is now `success` with 30 rows.
- The first post-change Summary request hung while the runner and n8n were recovering. One controlled n8n restart cleared the in-flight request; no PostgreSQL restart was performed.
- Final endpoint checks returned HTTP 200: readiness, Executive Summary, Campaign Channels, Outgoing Calls, and the report page. Browser console verification returned zero errors.
- Executive Summary source health now reports every source as `ready` or `success`, including `email_events` and `linkedin_activity_events`. Event-ledger sources use their recorded workflow status rather than being marked stale solely because their health timestamp is not a scheduled-ingest heartbeat.
- Live workflow verification: Executive Summary `Bukc0mgOD2r7V6ED` is active, unarchived, 7 nodes, version `92507a83-2a82-4a1d-8fb0-43a86d116a2d`, with matching `versionId` and `activeVersionId`. GSC workflow `xHqmCC1vOeZ11gCd` is active, unarchived, 9 nodes, version `b72f6cb4-2337-47ab-8a10-54c5a2b87f5b`, with matching `versionId` and `activeVersionId`.
- Current performance risk: Executive Summary completes successfully but took approximately 59 seconds in the final sequential check. Campaign Channels took approximately 10 seconds and Outgoing Calls approximately 1 second. No further SQL optimization was applied without an execution plan.

### Session Closeout (2026-09-04)

- **Objective completed:** restore report availability and source-health accuracy after the n8n runner/PostgreSQL DNS failure, repair the GSC schedule, and verify the live report path.
- **Repository changes:** `n8n/docker-compose.yml` removes the stale runner `extra_hosts` PostgreSQL override; this prevents the Coolify runner from resolving `postgres` to the host gateway. `repomix-output.md` was refreshed. This status document records the verified closeout.
- **Accepted verification:** readiness HTTP 200; Executive Summary HTTP 200; Campaign Channels HTTP 200; Outgoing Calls HTTP 200; report page HTTP 200; zero browser console errors; PostgreSQL healthy; GSC executions `887723` and `887730` successful; no recent GSC executions left in `new`, `running`, or `waiting`.
- **Not accepted as tests:** direct n8n MCP workflow lookup/execution calls returned permission/not-found errors; the legacy REST `/run` attempt returned HTTP 405; one concurrent Summary curl was locally aborted/timeouted while the server request was in flight. These were harness limitations or interrupted requests, not evidence of a workflow failure.
- **Open risks:** Executive Summary latency remains high at approximately 59 seconds; the Coolify deployment should be rebuilt or checked to ensure the repository compose change persists; the 1,229 unmatched `emerging_pool_contacts.ghl_contact_id` rows and embedded workflow secrets remain existing project risks.
- **Next session order:**
  1. Profile the Executive Summary SQL with `EXPLAIN (ANALYZE, BUFFERS)` during a controlled low-traffic window before changing query logic.
  2. Rebuild or inspect the Coolify n8n deployment and verify runner `pg` resolution, `getent hosts postgres`, and `coolify-shared` membership after deployment.
  3. Continue the documented secret migration and rotate exposed credentials only after credential-backed replacements are verified.
  4. Decide whether to resolve, skip, or re-export the 1,229 unmatched pool contacts.
- **Safety gates:** do not run live LinkedIn, Instagram, Vapi, newsletter, or SMS sends for testing without explicit approval. Do not restart PostgreSQL or rotate `N8N_ENCRYPTION_KEY` casually.

Full 7d/30d/90d cross-check of the Executive Report against source Postgres tables. The page was completely down (nginx 504 — summary query took 76.5s vs 60s proxy timeout). Fixed everything; query now ~15–27s per range and the page loads.

- **nginx 504** — `reports/nginx.conf` now sets `proxy_read_timeout 300s` on the API locations, applied to the running `reports-livetransparent` container + reloaded. **Image must be rebuilt on next deploy or it reverts to 60s.**
- **Calls read wrong table** — the calls CTEs read `report_raw_ghl_call_outcomes` (stale since 08-10) → showed 0 calls. Now read `report_raw_ghl_calls` (working GHL Conversations ingest, every 4h). 7d window: 201 calls (115 completed, 51 no-answer, 19 busy, 12 failed, 4 ringing; 115 answered / 82 missed).
- **Duplicate "Unassigned" channel rows** — rollup-only rows were mislabeled via `COALESCE(g.channel,'Unassigned')`. Fixed to `COALESCE(g.channel, r.channel)`.
- **Vapi timezone buckets** — counted all-time queue (2708) and used camelCase keys the frontend can't read. Now `status='pending'` (39) and emits snake_case too.
- **Stage moved-in boundary bug** — `stage_daily` included the LAG baseline day in output, inflating moved-in (Warm New 5,476→1,679). Added a window filter.
- **Query perf** — vapi timezone cross-join (6.28M-row nested loop) replaced with a single equality join; total 73s→~15s.
- **Pipeline Velocity** — 24h interval schedule had **0 executions ever**. Changed to daily `0 9 * * *` UTC cron + manual refresh (exec `832368`). Health `ready`.
- **GA4** (2026-08-31) — user reconnected the Google OAuth credential; manually re-ran the ingest (exec `832654`), which backfilled 08-14…08-29; re-ran the rollups. 7d now shows traffic 174 / users 166 with real channels. Health `ready`.
- **LinkedIn senders** (2026-08-31) — the 08-28 17:00 UTC outage was a **temporary LinkedIn restriction** (all `/users/invite` + `/chats` 422; verified cleared with a live 201 invite). Fixed the underlying accumulation: dispatcher claimed `ready`→`requested_pending` and never released on daily-limit early-return, leaving 5,046 stuck rows — released all to `ready` and added a self-healing `released` CTE (30-min stale claims recycle). Dispatcher published `7b002976`. DM sequence: 5 connected contacts have genuinely unreachable profiles (Unipile `invalid_recipient`) and clogged the hourly batch — selection now excludes `dm_unreachable`, send code flags them, and the 5 current ones are marked. DM Sequence published `e99b0d0d`.
- **GSC** (2026-08-31) — user reconnected the Search Console credential; ingest re-ran (exec `832997`), health `success`. 3-day rolling window so the 08-08…08-29 gap was not backfilled (negligible volume).
- **Contact acquisition UI** — `contact_sources` CTE relabels GHL/msgsndr tracking-link landings as a single `Email/SMS link` row (18 contacts) instead of ~17 one-contact rows with unreadable JWT URLs.
- **`sqlContacts`/`poolDistribution`** (2026-08-31) — pool tags are NOT real GHL tags (`brands_pool`/`dispensaries_pool`/`vapi_campaign_*` return 0 via GHL search). `pool_distribution` now reads `emerging_pool_contacts` (brandsPool 3,668 / dispensariesPool 10,200) + `voice_call_queue` (vapiBrand 106 / vapiDispensary 66). `sqlContacts` reads the real GHL `sql` tag (36) — backfilled once + re-snapshotted daily by a `sql`-tag fetch in `LT - GHL Daily Leads Ingest`. Exec Summary active version `9c43be7d-7160-448f-82be-00e5f8303b88`.
- **n8n runner pg + network** (2026-08-31 diagnosis, resolved and verified 2026-09-07) — the runner initially had an incompatible `NODE_PATH` and stale PostgreSQL host mapping. The live Coolify stack was corrected, the runner was recreated on `coolify-shared`, DNS/TCP resolution was verified, and a pg-using dialer workflow returned continuous success. Re-inspect only if the monitor alerts; do not re-apply the old drift diagnosis blindly.

**Remaining known limitations (not report bugs):** `metaAttribution` empty (no Meta-UTM contacts in the 500-contact snapshot); OpenRouter 402s previously affected enrichment (credits restored 2026-08-31).



## Source Of Truth

### Weekly Newsletter Pipeline (LIVE 2026-08-27 — capacity retuned 2026-09-01)

Recurring weekly newsletter to all eligible GHL contacts (Monday-Friday, 15-minute runs from 07:00-13:00 LA, senders `.co`/`.agency`/`.org` — NOT `.com`). **Go-live happened** — the DNS gate is cleared; `newsletter_send_log` shows 19,739 sent + 101 failed in the 08-23…08-29 window, and the Executive Report folds newsletter metrics into email metrics with these definitions:
  - `emailsSent` = **unique sends** (one row per `ghl_contact_id + week_key` in `newsletter_send_log`; UNIQUE constraint ensures no duplicates)
  - `emailsOpened` = **total open events** (counted from `newsletter_events`; a single contact can have multiple open events tracked via HMAC pixel)
  - `emailsClicked` = **total click events** (counted from `newsletter_events`; a single contact can have multiple clicks tracked via HMAC link rewriting)
  - `emailsUnsubscribed` = **unique unsubscribes** (one row per contact who clicked unsubscribe link; logged in `newsletter_events` and `newsletter_send_log`)
  - `newsletterFailed` = **failed send attempts** (rows marked `status='failed'` in `newsletter_send_log`; 101 in last window)
  - Rates (`emailOpenRate`/`emailClickRate`/`emailBounceRate`) are computed from **unique recipients** in the window send cohort

- **Eligible count:** 31,800 GHL contacts → **22,169 eligible** (excludes no-email + `do not contact`/`do not nurture`, email-deduped). Per sender: ~7,390/week, ~1,478/day across five weekday buckets (under the live `maxPerSenderPerDay=2333` cap).
- **Workflows:** Prep `vvPdJMzBJMgcf5I9` (Mon 06:30 LA, active/published) + Dispatcher `vru7OtCkDnPJkWt2` (every 15 minutes, 07:00-13:00 LA, Monday-Friday, active/published, `defaultDryRun=false`). Dispatcher uses `maxPerRun=250` and a database-backed `maxPerSenderPerDay=2333` cap. Tracking handlers all active: Open Pixel `HkTQ9mqwHcpg3AIM`, Click Track `HZ8ndNF4p80PrQjf`, Unsubscribe `RvYusUSGB79K2e2k`.
- **Capacity recovery (2026-09-01):** Prep now assigns weekday buckets 1-5. Thursday/Friday dispatch runs drain remaining pending/failed rows across all buckets. The custom JavaScript runner was rebuilt with `N8N_RUNNERS_AUTO_SHUTDOWN_TIMEOUT=300`, `N8N_RUNNERS_MAX_CONCURRENCY=10`, isolated `pg`, and `coolify-shared` access. Full pinned graph test `837185` passed; controlled live send `838055` sent one newsletter. August 31 finished with 695 sent and 39 failed; 3,398 rows remain claimed and require normal stale-claim recycling.
- **Verified:** prep exec `774082` wrote 22,169 rows (0 sends); dispatcher dry run `773957` matched template + emitted `planned` with 0 DB mutation; tracking pixel/click/unsub E2E tested. Test artifacts cleaned.
- **Template:** `Newsletter 1 2026-08-24 (The real reason regulated ads get disapproved)` (ID `6a87716221922afe5eda9e6f`), proper logo applied.
- **Deliverability audit + DND suppression (2026-09-09):** the ~2.7% GHL 400 rejection rate is `CONVERSATIONS_MSG_INVALID_EMAILTO` from contacts with **active Email DND suppression** (prior bounce/spam-complaint/unsubscribe) — verified live on sampled contacts; NOT sender-related and NOT stale email. Dispatcher (`vru7OtCkDnPJkWt2`, active `9774bd27`) now retries `invalid_email` rejects once with the contact's current GHL email, marks terminal `invalid_email`, and tags the contact `newsletter_dnd_suppressed`; Prep (`vvPdJMzBJMgcf5I9`, active `8c3342d0`) `blockedTags` now includes that tag and its insert is `DO UPDATE` on email conflict. 1,589 unique emails have failed historically (191 every week); those will now self-suppress. Remaining: add GHL custom-domain DKIM to `.co/.agency/.org`, move those domains `p=none`→`p=quarantine`→`p=reject`, and stand up Google Postmaster + a placement seed test (no bounce/complaint visibility exists on this path). Record: `docs/sessions/2026-09-09-newsletter-deliverability-audit-and-dnd-suppression.md`.
- **Go-Live sequence + full runbook:** `docs/sessions/2026-08-21-weekly-newsletter-pipeline.md`.


### Instagram Company Page DM Sender Live — Brands First (2026-08-18)

- The company-page Instagram DM sender `LT - Instagram Company Page Partnership Sender` (`IeovbYnhCsetXS89`) is **live** (dryRun=false), Mon-Fri 10:00-15:00 America/Los_Angeles, 45/day cap, 10/hour. Unipile key verified working.
- `campaign_priority` in `instagram_company_dm_state` flipped to **dan_brands=1, dan_dispensaries=2, partnerships=3** (379 rows: 245 Brands, 58 Dispensaries, 76 Partnerships). Brands are sent first starting tomorrow, then Dispensaries, then the remaining Partnerships.
- Message 2 is enabled in the live company-page sender (`IeovbYnhCsetXS89`, published version `3d721cec-04e6-45cc-9ebb-fb21589b61a6`). It selects Message-1-complete rows after a two-business-day gate and advances them idempotently to step 2. Message 3 remains disabled.
- `brand_pool - IG & FB` enrichment is COMPLETE (`BIVAw1AWTTzC0igW` unpublished, 0 unresolved). Dispensary (`Qd7sn9MPq4W24WKi`) and Partnership (`RlogFNDYjtjkuRFJ`) enrichment remain active on a 5-minute schedule; an OpenRouter weekly key limit blocked them until the user fixed it on 2026-08-18.
- Session details: [`docs/sessions/2026-08-18-instagram-company-page-dm-priority.md`](docs/sessions/2026-08-18-instagram-company-page-dm-priority.md).

### LinkedIn DM Pipeline Repair (2026-08-18)

- Connection invites and DMs had stalled for ~3 weeks (invites near-zero, `dm_sent` events at 0 in 30 days). Four root causes were found and fixed; two audit passes confirmed no new bugs, logic errors, or duplicates.
- **Dispatcher** (`fXxw5lanZcDmUrst`, `f2f52041`): fixed the corrupted `\\/` regex in `identifier()` (SDK-serialization bug that threw `SyntaxError: Invalid regular expression flags` on every dispatch) and enforced the declared `dailyLimit: 60` (was ignored, would have sent ~240/day). Verified 60 distinct invites today, exactly capped, zero errors.
- **DM Sequence** (`d0tEtijajisIsYcs`, `bc79f0d1`): the 422 came from always creating a new Unipile chat; now routes to the existing chat via `POST /chats/{chat_id}/messages` when a `last_chat_id` exists, with `err.cause` body capture. Added a durable `dm_sent:{contact}:{step}` event (ON CONFLICT DO NOTHING) written after a successful send and before the state upsert, and the `Find Contacts Ready for DM` query excludes steps already sent — preventing re-sends if the state upsert fails. This also starts populating the previously-empty `dmsSent` report metric.
- **Reply Backfill** (`QfJ2EZcc7lZwNgxj`, `9e0131f4`): no longer forces `dm_conversation_status='active'` on conversation-check errors; only on confirmed replies (self-healing). Repaired 918 stale `active` rows that were confirmed no-reply.
- **State Upsert** (`Old7ZvyVYgFaJgDr`, `4045c96c`): removed the over-broad `active`-preservation clause that blocked `requested_pending -> requested`; added a guard preventing `requested -> ready`/`requested_pending` downgrade. Repaired 39 invited-but-stuck rows to `requested`.
- **Duplicate safety verified**: 0 contacts with multiple state rows, 0 duplicate invites today, DM sends idempotent by `event_key`. 29 "provider duplicates" are distinct GHL contacts (same profile in multiple pools).
- **Net result**: DM-eligible connected (non-relation) contacts 30 -> 66; invites flowing at 60/day.
- Full details: [`docs/sessions/2026-08-18-linkedin-dm-pipeline-repair.md`](docs/sessions/2026-08-18-linkedin-dm-pipeline-repair.md). The DM send chat-routing path is next exercised by the DM Sequence's scheduled run (12-22 UTC = 05:00-15:00 LA).

### LinkedIn Send-Path Double-Escape Corruption Fixed (2026-08-19)

- The remaining, silent layer of the LinkedIn text-corruption bug was fixed. An 08-11 MCP mutation (`3b70854e`) double-escaped regex literals in the Code nodes, producing **syntactically valid JS that does the wrong thing** — distinct from the 07-15 mojibake (Unicode decode at write time).
- **Two distinct failures, not one**: (1) `identifier()` `/^https?:\\\\/\\\\//i` crashed the Dispatcher at parse time, so it sent **no invites at all** 08-11→08-18; (2) after the 08-18 REST PUT fixed only that crash, `sanitize()` matched literal `u`/`C`/`D`+digits (garbling `Cameron`→`"ameron`, `co-founder`→`co-fo'nder`) and `/\\{first_name\\}/gi` left `{first_name}` unreplaced. **Garbled invites were sent only from 08-18 00:15 → 08-19 04:45**, bounded by the 60/day cap — not since 08-11.
- **Fixed** with `scripts/linkedin/fix_linkedin_sanitize_double_escape.py`: Dispatcher `fXxw5lanZcDmUrst` → published `0a349cdb-295f-45a5-978a-2f3e46022ace`; DM Sequence `d0tEtijajisIsYcs` → published `db7dde63-2f6e-42e8-92f0-7f68c66e7445`. Both verified `versionId == activeVersionId`. A full-instance scan of all 164 workflows confirmed no other Code nodes affected.
- Full timeline, root cause, and prevention notes: [`docs/sessions/2026-08-19-linkedin-double-escape-fix.md`](docs/sessions/2026-08-19-linkedin-double-escape-fix.md).

### Executive Report Accuracy Audit (2026-08-25)

- Full 30d cross-check of the Executive Summary, Campaign Channel Summary, and Outgoing Calls against source Postgres tables. Already-exact figures: `emailsSent` 2,692 / `opened` 7,505 / `clicked` 467 / `bounced` 459 / `unsubscribed` 51, Vapi 50 calls, LinkedIn 44 invites / 26 DMs / 4 replies, Instagram 204 DMs, social 29 posts + account stats, appointments 4, calls 828, Meta ads spend $14,832.79 / 9,460 clicks / 488,777 impressions, MQL summary, SMS 184 sent / 1,095 failed.
- **Raw pipeline/stage IDs exposed** in `pipelineDropoff` (Partnership pipeline), `stageDropoff`, `opportunityStageBreakdown`, and `stageVelocity`. Added the full canonical CASE mappings (Partnership Pipeline `tQkFYrHjALgoLz6oq0uz` + 4 stages, plus Sales Outreach `91517911`=Qualified/`5112b5c8`=Discovery No Shows for Rescheduling, Warm `67d47ef7`=New_Not Qualified/`0741e8b5`=vapi_voicemail/`967292f9`=vapi_nurture/`16fb26a2`=vapi_qualified, Sales `268ed432`=Discovery No Shows) to Exec Summary `Build Query` (opportunity_snapshots), Daily Rollups `Build Rollup SQL` (tmp_report_opps + opp_transitions), and Pipeline Velocity `Build Velocity SQL` (timeline). Re-ran rollup + velocity; `stageVelocity` now uses `computed_at = MAX(computed_at)` so it always shows the latest compute. No raw IDs remain in the current window.
- **Campaign Channel Partnership email undercount**: `Partnership emails email_sent` was 59 (COUNT DISTINCT contacts); the release log has 233 (59 contacts × 4 steps) and the Exec Summary counted 233. Changed `email_sent` to `COUNT(*)` for DAN/Emerald/Partnership. Both endpoints now report 2,692 total.
- **Email rates hardcoded NULL** → now cohort-based `emailOpenRate`/`ClickRate`/`BounceRate` = unique recipients opened/clicked/bounced within the window send cohort ÷ unique sent recipients (44.6% / 11.4% / 4.7% for 30d; `emailRateBasis=unique_recipient_rates_over_window_sent_cohort`). Restricting to the send cohort avoids inflation from historical sends opening in-window.
- **`salesQuality.topLossReason` renamed `topLossStage`** (it returned a stage name; GHL has no structured loss-reason).
- **Workflow versions (all `versionId == activeVersionId`)**: Exec Summary `d01f7757-eb14-4072-9a96-c4fbf8017091`; Daily Rollups `ddded785-2d31-4818-8ced-8a9c881a689f`; Pipeline Velocity `43515531-dd9f-4462-bbe6-e58e321ab130`; Campaign Channel `6ec148ff-6f1c-42b5-8b72-157d40d0a74a`. (REST PUT auto-publishes; the Query Summary postgres credential `pgAzUqpwOiGkGXzO` had to be re-attached after the first PUT stripped it.)
- **Remaining data-source issues (operator action, not logic)**: GA4 credential expired 08-14 (traffic undercounted; reconnect the Google OAuth credential in n8n — `health` already flags GA4 stale); Pipeline Velocity schedule stopped firing ~08-07 (now manually refreshed); GSC stale since 08-07; opportunities snapshot gap 08-12…08-20; `poolDistribution` always 0 (leads ingest only snapshots ~500 contacts); `metaAttribution` empty (no Meta-UTM contacts in the 500-row snapshot).

### MQL Tag Ledger (2026-08-25)

- The business counts MQLs by the **`mql` tag being added** (e.g. past week), not by the Warm Qualified (MQL) stage. GHL does not expose tag-add timestamps and the hourly contact snapshot can't reconstruct them, so we built a forward-looking ledger.
- `mql_tag_events` table (UNIQUE `(contact_id, tag)`, first-add wins) + active workflow `LT - MQL Tag Event Ingest` (`U9oc2tZRsr4zq6IM`, POST `/webhook/lt-mql-tag-event`, requires `X-LT-MQL-Tag-Secret` from its Config node; 403 on unauthorized/missing contact, `duplicate` on re-add). Tested: unauthorized 403, authorized insert, duplicate no-op, then test rows deleted.
- Exec Summary `mqlSummary` now returns `taggedMqlsTotal`/`taggedMqlsThisPeriod`/`taggedAsOfDate`/`tagBasis: mql_tag_events_ledger` (0 until events flow).
- **GHL automation created and published**: `WL - MQL Tag Ledger` (`203163a4-262a-4195-9a15-b4aa0b712c5a`) uses Contact → Tag Added → `mql` → authenticated webhook POST with `{"contact_id":"{{contact.id}}",...}`. Forward-looking only; cannot backfill prior weeks. Runbook: [`docs/sessions/2026-08-25-mql-tag-ledger.md`](docs/sessions/2026-08-25-mql-tag-ledger.md).

### August 2026 Emerald Contact Enrollment (2026-08-26)

- Reconciled 2,620 cleaned Brand, Agency, and Dispensary source rows against live GHL. Final dry run: 0 unmatched rows and 0 pending tag actions.
- Created 36 additional email-only contacts where the source email was genuinely absent from GHL. Existing contacts were not overwritten.
- Completed 319 contact-level repair groups representing 325 tag assignments: 313 Emerald MSO queue enrollments plus six Dispensary pool and six DAN queue assignments. Queue tags use the existing GHL enrollment automations; no manual email sends were performed.
- Five AURI addresses were intentionally skipped because GHL stores them as additional emails on existing contact `Amy Lund` (`ZtDaBakEXm0yPi2jW8mi`). The reconciliation script now recognizes these duplicates and will not retry them.
- Detailed handoff: [`docs/sessions/2026-08-26-august-emerald-contact-enrollment.md`](docs/sessions/2026-08-26-august-emerald-contact-enrollment.md).

### Executive Report MQL and Account Statistics (2026-08-17)

- The MQL panel now shows the three requested figures plus period movement. Verified live: Total MQLs 137, MQLs Converted to SQL 48 (opportunities that also entered the Sales Outreach pipeline `dhdlf3O4tymxFtHk4aqq`), Current MQLs awaiting Sales 89. The 30-day window reports 119 entered and 44 converted; the 7-day window reports 0 entered and 0 converted.
- The previous `Active = Total = 137` display was misleading: it counted only the Warm Qualified (MQL) stage snapshot, so 48 MQLs that had already moved to Sales Outreach were still shown as active. The reworked `mqlSummary` CTE (Executive Summary version `e4fa3d18-1a61-47db-b255-d34e20051d7f`) resolves current pipeline per opportunity.
- Reach, impressions, posts, likes, and followers are now live from GHL Social Planner account statistics. The PIT authenticates `/social-media-posting/statistics` (it returned 401 on 2026-08-04, so this unblocked the feature without needing GHL OAuth). 7-day window: 45 reach, 159 impressions, 4 posts; 30-day: 4,018 reach, 1,821 impressions, 10 posts. Saves is not provided by the statistics endpoint and remains N/A.
- `LT - GHL Social Statistics Ingest` (`veg9jbN1P67Xmqy8`, active version `bee234fb-5234-4fb4-88e9-4dd611b937fb`) runs daily 06:00 America/Los_Angeles, calls the statistics endpoint with the GHL PIT from its Config node, and stores per-window `all` plus per-platform rows in `report_ghl_social_statistics` (report `postgres` database). Verification execution `760249` stored 12 rows.
- Executive Report build `2026-08-17-v27-social-mql` is deployed. Desktop (1440px) and 390px mobile verified: all report APIs HTTP 200, no console errors, no page-level horizontal overflow, and the new MQL and account-statistics cards render correct values for 7d and 30d.
- Full audit and implementation notes: [`docs/sessions/2026-08-17-social-and-mql-reporting.md`](docs/sessions/2026-08-17-social-and-mql-reporting.md).

### Executive Report Social Accuracy (2026-08-17)

- The official GHL Social Planner post API and the report ledger both return 8 platform/account placements and 3 likes for the completed `2026-08-10` through `2026-08-16` window: 6 LinkedIn placements and 2 Instagram placements. The report now labels these as placements rather than unique composer posts.
- Executive Summary (`Bukc0mgOD2r7V6ED`) is active and published on version `bc4856aa-e640-4477-a9fc-3ed14ae53707`. Reach, impressions, and saves return `null` and render as `N/A` when the source payload lacks those fields; unavailable account analytics are no longer represented as measured zeroes.
- The LinkedIn snapshot now groups both `requested` and `requested_pending` into Requested. Verified live totals are 10,469 Ready, 1,365 Requested, 2,040 Connected, 100 Follower Messaged, and 13,977 total state rows. The selected-window activity ledger reports 2 requests and 2 replies from 2 responders.
- `LT - GHL Daily Social Ingest` (`QZoqCaTwDhbym80O`) is published on version `2ed24c59-1fc8-40ae-bdb0-aba9744a37a1`. It uses GHL API version `2021-07-28`, paginates the full 366-day report horizon, fails closed on fetch errors, refreshes every mutable post field, and reports the actual upsert count. Read-only verification execution `759065` refreshed 229 posts; the table retains 250 rows and refreshed at `2026-08-17T14:51:02Z`.
- Executive Report build `2026-08-17-v26-social-reporting-accuracy` is deployed. Desktop and 390px mobile checks returned all report APIs as HTTP 200, no console errors, and no page-level horizontal overflow.
- Exact-range account statistics remain blocked because the active `ghl_oauth_tokens` row has an empty access token. The experimental workflow was unpublished and archived. Do not cache or fabricate reach/impression totals; reconnect GHL OAuth before adding the official statistics endpoint.
- Full audit and verification notes: [`docs/sessions/2026-08-17-social-reporting-accuracy.md`](docs/sessions/2026-08-17-social-reporting-accuracy.md).

### SimpleTexting Safety Reconciliation (2026-08-17)

- Automated outbound remains paused. Campaign Step Runner (`dUyOfxllvkxZavaw`), Warmup Dispatcher (`dZQLlbTLkpE1843X`), Pool Dispatcher (`usxYXSuc4ahw40V3`), and Campaign Sequencer (`7mSiivR3NhtLIcNz`) are unpublished. Phone Backfill (`8hQKQi1PooYDFxNR`) is active but cannot send SMS.
- The active send webhook (`Q3Ivnwe4z2Y3cD7A`, version `47dd0303-3d36-49e4-9bd9-e34873edbad2`) now defaults to dry-run, validates malformed GHL `customData`, normalizes US/Canada numbers, resolves the Jason/campaign/Emerald template registry, rejects unresolved merge fields, and enforces business hours plus live GHL DND/tag suppression before a real send.
- Provider Router (`f4VoO1lBWkYRcQai`, version `dfbb09db-890c-48ef-83a6-9cf4a64863f4`) and Idempotent Send (`gwaEpWDpTIwsafi8`, version `bcc7d22e-58b8-4419-a56f-753ff80773b8`) fail closed on invalid provider, contact, phone, message, suppression, or non-confirmed provider responses. Safe tests `757212`, `757213`, `757214`, `757227`, and `757239` produced no live SMS.
- SimpleTexting webhooks are registered for inbound messages, delivery/non-delivery reports, and unsubscribe reports. Their active workflows are protected through secret callback URLs: Inbound `i0pROHpFtN4LYR0Q` version `d657c79b-f075-4241-a78d-0be33f67f627`; Delivery `AEi1VCzkLvaYFr4U` version `31e884de-b4fe-4f03-af22-49cb64b766a1`; Unsubscribe `IyBKMkpYQ7pa0C8V` version `c21eb489-9561-4393-8d52-f8a8231fa0a7`. Pinned delivery test `757225` verified protected routing without a state write.
- Database reconciliation restored 41 confirmed `sent_step_*` events from provider IDs, terminalized 202 exhausted historical provider failures as `delivery_failed`, retained 55 unmatched `send_unknown` rows in quarantine, and marked one unsupported/missing number `phone_unavailable`. No uncertain historical send was replayed.
- Remaining production validation requires either natural provider traffic or one explicitly approved controlled live SMS. Do not publish sender schedules or run a live test without approval.

### Executive Report Campaign Accuracy (2026-08-16)

- The 7-day preset now returns exactly seven completed local dates, verified as `2026-08-09` through `2026-08-15`. Executive Summary (`Bukc0mgOD2r7V6ED`) is published on `be29cdcb-efdf-4e43-a17a-cdbd1ef622b7`; Campaign Channel Summary (`MvPLbUAN9IIQikxb`) is published on `12f28e56-dd02-4afd-81cd-e7a2c8fa6086`.
- Vapi `interest_unknown` and `human_answered` outcomes count as answered, not qualified. The verified window has 42 calls and 7 answered: Brand 22/3 and Dispensary 20/4.
- Global email rates now return `null` with basis `event_counts_without_matching_send_denominator` when event counts lack a compatible sent-recipient denominator. Campaign email rates remain based on tracked delivered recipients.
- LinkedIn inbound (`7o5EBdvwAuIaWW7k`) preserves source timestamps and reconstructs malformed form-encoded Unipile payloads. Missed message `4pX8FcptXnSl5aADrrfm8A` was inserted idempotently at its original timestamp: first insert 1, second insert 0. The live 7-day campaign API now reports 2 LinkedIn replies: 1 Partnership and 1 unattributed. Final workflow version `9f61f384-f481-467f-a13e-47bf9a1b6e52` is active with no temporary recovery nodes.
- Instagram inbound (`pISlgYUsyJIrLuJd`) and social outbound routing (`kqIi8i1RjFAZKrK3`) now maintain `instagram_activity_events`. The report exposes explicit ledger coverage and currently reports 0 DMs and 0 replies rather than implying historical completeness.
- Executive Report build `2026-08-17-v26-social-reporting-accuracy` supersedes v24 while retaining its Instagram channel/filter support, DM/reply columns, drill-down/comparison metrics, and ledger coverage.
- Full implementation and verification notes: [`docs/sessions/2026-08-16-executive-report-campaign-accuracy.md`](docs/sessions/2026-08-16-executive-report-campaign-accuracy.md).

### Company Instagram Page Delivery (2026-08-18 Update)

The company-page Instagram DM sender is **LIVE**: `LT - Instagram Company Page Partnership Sender` (`IeovbYnhCsetXS89`), active and published (dryRun=false), Mon-Fri 10:00-15:00 America/Los_Angeles, 45/day cap, 10/hour. It reads `instagram_company_dm_state` and sends via Unipile account `F2UprZ8aQc6Qm9CYYWU6cg`. Do not republish `LT - Instagram DM Sequence (Unipile)` (`iCnY6ccdHhfJg3sf`): it used the LinkedIn account and old `instagram_dm_state` model.

- **Send priority (2026-08-18):** `campaign_priority` is `dan_brands`=1, `dan_dispensaries`=2, `partnerships`=3 (379 rows: 245 Brands, 58 Dispensaries, 76 Partnerships). Brands go first, then Dispensaries, then Partnerships.
- **Message strategy:** Message 2 is now enabled after the Message-1-first rollout. The sender uses the approved campaign-specific Message 2 copy, a two-business-day delay, and step-2 idempotency/state transitions. Message 3 remains disabled.
- **Unipile key verified working** on 2026-08-18 (HTTP 200 accounts list; Instagram account status OK).
- **IG/FB enrichment:** `brand_pool - IG & FB` is COMPLETE (workflow `BIVAw1AWTTzC0igW` unpublished, 0 unresolved). Dispensary (`Qd7sn9MPq4W24WKi`) and Partnership (`RlogFNDYjtjkuRFJ`) enrichment remain active on a 5-minute schedule; temporarily blocked by an OpenRouter weekly key limit the user fixed on 2026-08-18.
- Session details: [`docs/sessions/2026-08-18-instagram-company-page-dm-priority.md`](docs/sessions/2026-08-18-instagram-company-page-dm-priority.md). Full contract: [`docs/sessions/2026-08-14-company-instagram-page-dm-handoff.md`](docs/sessions/2026-08-14-company-instagram-page-dm-handoff.md).

The approved Instagram/FB DM copy is unchanged. Phase one targets verified company Instagram pages through Unipile account `F2UprZ8aQc6Qm9CYYWU6cg`, not employee profiles. Facebook Messenger is deferred to native GHL Messenger; public Facebook URLs and Page IDs are not Messenger recipient IDs.

Audience selectors: `brands_pool` for Brands, `dispensaries_pool` for Dispensaries, and `partner_candidate_email` or `partner_candidate_linkedin` for Partnerships. Original-source audit: `data/Brands.csv` has 3,668 rows, 3,224 with Instagram URL occurrences, and 2,799 with Facebook URL occurrences; `data/Dispensaries.csv` has 10,200 rows, 6,875 with Instagram URL occurrences, and 6,431 with Facebook URL occurrences. Relevant columns are `Company non-LinkedIn URL(s)`, `Location non-LinkedIn URL(s)`, and `Contact non-LinkedIn URL(s)`. Counts are preliminary and require normalization, deduplication, and company-page validation. Partnership source files lack reliable Instagram/Facebook URL fields and require separate enrichment.

Existing contact-level Instagram fields are protected: `Instagram Username` (`8k6vF61VBIysdIXXFQD5`), `Instagram Profile URL` (`beGMXoidqHdYqAQDORWX`), `Instagram Profile Provider ID` (`fYYUrFLABP5l0w7RdK7Y`), `Instagram Chat Attendee ID` (`SQdQw0MNvk8uQbr4yDZU`), and `Instagram Chat ID` (`ab6euY7qo5klhUSe7VWu`). Create separate company-level fields named exactly: `Company Instagram Username`, `Company Instagram Profile URL`, `Company Instagram Profile Provider ID`, `Company Instagram Chat Attendee ID`, `Company Instagram Chat ID`, `Company Facebook Page URL`, `Company Facebook Page ID`, and `Company Facebook Messenger PSID`. Do not repurpose `Apollo Facebook URL`; a Facebook PSID may only be populated from an eligible GHL Messenger event.

The enrichment workflow matches source rows to GHL by Emerald Contact ID, source metadata, exact normalized email, exact normalized phone, then company-plus-contact-name as a review fallback. It extracts and normalizes company/location URLs, resolves Instagram pages through Unipile, rejects personal or ambiguous pages, updates only the new company-level fields, and produces an unresolved/conflict report. One company page may map to multiple GHL contacts; Postgres stores associated IDs and a primary attribution contact. A dedicated company-page identity/state model is authoritative for delivery and lifecycle, with identity uniqueness by campaign/account/profile provider ID and send idempotency by campaign/profile/step. Use direct `require('pg')` transactions for writes.

Any prior reply or suppression from any associated contact stops the full company-page sequence, including relevant GHL/email/LinkedIn reply evidence; email and LinkedIn campaigns may continue independently when no reply exists. Identity/reply-check errors fail closed. Cadence: Message 1 on the first eligible weekday, then Messages 2 and 3 two business days apart; never send on weekends. Lifecycle remains in Postgres; no lifecycle tags are required. All eight company-level fields are `TEXT`; provider/profile fields require validated Unipile resolution, and chat fields require a usable messaging identity. The existing `instagram_conversation_map` remains the contact-level inbound bridge, not campaign state.

### Session 3 Fixes (2026-08-12)

- **Executive Summary duplicate JSON keys removed**: `vapiWeeklyPerformance` and `vapiWeeklyBreakdown` appeared 5 times each in the `Build Query` node's `summary_json` CTE. Removed 4 duplicate pairs; 1 of each remains. Published version `d458117c-63a0-4666-a5dd-1620e9bde4fe`.
- **Executive Summary timezone drift fixed**: `Normalize Request` node computed `startDate` using pure UTC operations (`new Date().setUTCDate()`) instead of the configured `America/Los_Angeles` timezone. Now uses `isoDateInTimezone()` for timezone-aware date subtraction. Same fix applied.
- **Date filters added to unfiltered CTEs**: `stageVelocity`, `sql_contacts`, and `pool_distribution` (4 sub-queries) in the Executive Summary API now include `WHERE report_date BETWEEN $1::date AND $2::date`, matching the selected period.
- **Executive Summary zero/timeout regression repaired**: The stage-velocity filter referenced nonexistent `v.report_date`, causing PostgreSQL failure and an empty HTTP 200 that the frontend rendered as zeroes. Changed it to `DATE(v.computed_at)`. Removed the redundant Campaign Channel Summary HTTP call from `Shape Response` and projected existing `email_direct` totals/rates instead, reducing current/prior summary requests to 19.9s/12.3s. Final active version `d177a923-da94-43ac-ac97-dbba1a664ab4`; browser verification rendered 1,847 visits, 160 contacts, 4,368 opportunities, 5,743 email opens, and 362 clicks.
- **Partnership LinkedIn replies corrected**: Campaign Channels undercounted replies because malformed form-encoded Unipile webhook payloads lost sender/message fields. Verified David Schachter and Gretchen Gailey directly through Unipile, restored their original message IDs/timestamps to `linkedin_activity_events`, and raised Partnership LinkedIn replies from 1 to 3. Published inbound workflow version `f96dafba-9818-4aab-8656-c2e4e2ab8480` adds a field-level malformed-payload fallback for future events.
- **Campaign Channel Summary timezone drift fixed**: `Normalize Campaign Window` node used `new Date().toISOString()` (UTC) for default end date. Now uses `isoDateInTimezone()` with `America/New_York`. Published version `e3b9f13f-e589-4dd9-bc8d-98801ed8c654`.
- **Voice dialer Postgres migration**: Migrated 4 broken Postgres v2.6 nodes (`Postgres - Release Lock`, `Postgres - Release Lock (Timezone)`, `Postgres - Mark Attempted`, `Postgres - Mark Vapi Start Failed`) to direct `require('pg')` Code nodes. The dialer was crashing on every execution due to the `queryReplacement` parameter bug. Published version `b8e9c57a-f81f-49fd-b469-1388320568c5`.
- **Voice dialer release-lock resolution verified (2026-08-14)**: This was the shared scheduled Vapi outbound dialer path, not a manual dialer and not Twilio. Queue items skipped for phone, suppression/DNC, qualification, or calling-hours reasons could hit `Postgres - Release Lock`; the n8n Postgres v2.6 `$1/$2/$3` binding failure caused `there is no parameter $1`. The published direct-`pg` migration removes that dependency. Thirteen consecutive scheduled executions on 2026-08-13, including execution `746845`, completed successfully with no recurrence.
- **Voice enqueue residual error resolved (2026-08-14)**: The same n8n/Postgres binding defect remained in the active `LT - Voice Queue Enqueue` webhook (`XzcpOBi9YcIhJPck`) at `Postgres - Insert or Noop`, which still used `$1`-`$5` with `queryReplacement`. Replaced it with a direct `require('pg')` Code node using the same advisory-lock and deduplication behavior. Published version `42aba803-09b0-4118-a105-9161bebe66e9`; fresh live details confirm `versionId == activeVersionId`. This was the residual shared voice-queue path, not Twilio.
- **Voice intake poller audit fixes (2026-08-14)**: Published `LT - Voice Queue Vapi Intake Poller` (`bYk1Ai6MJLyhTsDZ`) on `5c464233-c79a-4f49-a809-de303f3b6136`. The poller now uses the full terminal voice blocklist, routes suppressed contacts to the skip branch, reports tag mutation failures instead of silently claiming success, and returns explicit inserted/deduplicated queue outcomes. Smoke execution `747051` succeeded.
- **Voice intake Apollo tag-context fix (2026-08-14)**: The Apollo HTTP response replaced the classified item and caused `Remove Tag - Enriching` to fall back to `vapi_queue`, leaving the actual campaign tag behind. Published version `d852a93d-b468-4b9b-8cc9-d4995131f926` now resolves the original campaign tag from `Classify Contacts`; verification execution `747053` removed `vapi_campaign_brand` successfully.
- **Voice callback Postgres migration**: Migrated 8 Postgres v2.5/v2.6 nodes (`Postgres - Update Status`, `Postgres - Set DNC`, `Postgres - Log Outcome`, `Postgres - Insert Attempt`, `Postgres - Mark Queue Completed`, `Postgres - Resolve Queue By Call ID`, `Postgres - Claim Timer State`, `Postgres - Advance Phone Index`) to direct `require('pg')` Code nodes. Published version `c97480db-d741-4c7c-8705-f173296800ac`.
- **ghl_contact_id re-backfill**: All 13,868 rows had NULL `ghl_contact_id` (lost during DB recovery). Re-ran 3-pass matching from GHL export CSVs: email (4,642), phone (5,742), name+company (2,255) = 12,639 matched. 1,229 unmatched (contacts not in exports).
- **Embedded secrets audit**: Scanned all 83 active workflows. Found 12 critical (GHL PIT in 8+ workflows, Vapi key, Unipile key, Postgres creds, GHL OAuth creds), 5 high (webhook secrets, Slack token), 2 medium (OAuth client creds). Full remediation plan documented — requires credential creation and rotation.
- **LinkedIn state backfill**: Executed LinkedIn Reply Backfill (`QfJ2EZcc7lZwNgxj`) successfully (execution `743291`). State Sync (`ceaKnz6E3onQrZpt`) timed out at 60s task runner limit; will populate on normal 6-hour schedule.

### Immediate Runtime Update (2026-08-12)

- The external n8n JavaScript runner blocker is resolved. `n8nio/runners-custom:latest` now contains an isolated npm `pg@8.21.0` tree at `/opt/pg-node_modules`; `NODE_PATH` is configured in the container and task-runner config. VPS verification returns `typeof require('pg').Client === 'function'`, and runner logs show no allowlist/module errors.
- The n8n container was recreated with the persisted Coolify encryption key after a mismatch caused `Credentials could not be decrypted` and empty report responses. The public report endpoint now returns HTTP 200 with a real approximately 33 KB JSON payload.
- The external runner's direct `require('pg')` path is verified by controlled GHL leads ingest execution `742843`; the atomic transaction completed successfully.
- GHL leads ingest is active hourly on published version `d29b7af9-0b69-4fc7-a53c-c23dd24b0825`. Execution `742843` wrote 500 distinct contacts and matching sync-run, watermark, and source-health records.
- **GHL Sales Ingest repaired (2026-08-12)**: Workflow `aYT5oHcgmBALzHy5` published on version `91603d56`. Migrated from broken Postgres v2.6 template-literal injection to atomic direct-`pg` transaction (`require('pg')` BEGIN/COMMIT). Execution `743094` wrote 7,984 opportunities + 7,984 pipeline history rows. Sync run completed (15,968 row_count, 0 errors). Watermark `2026-08-12`. Health `ghl_opportunities` status `ready`.
- **GHL Sales Ingest cadence corrected (2026-08-14)**: Invalid `minutesInterval: 1440` caused hourly executions because Schedule Trigger minute intervals support only 1-59. Published version `c1b5020c-757b-4515-8c51-3066a15326aa` runs once daily at 1:15 AM `America/Los_Angeles`, after the hourly Leads Ingest. Post-timeout scheduled executions `749695`, `749902`, and `750085` all succeeded before the cadence correction.
- **Call Outcome Ingest secured (2026-08-12)**: Workflow `PUCfTZBANSPcgS0c` published on version `7af98411`. Now requires `X-LT-Call-Outcome-Secret` header (secret stored in Config node of `PUCfTZBANSPcgS0c`). Unauthorized requests throw before any DB write.
- Executive Report build `2026-08-17-v26-social-reporting-accuracy` is deployed. Pipeline/stage charts resolve live GHL IDs; campaign tables include LinkedIn and Instagram ledger metrics; social post/account definitions are explicit; desktop and 390px mobile checks found no raw stage IDs or page-level horizontal overflow.

For the complete recovery narrative and continuation order, read [`docs/handoff/2026-08-12-report-recovery.md`](docs/handoff/2026-08-12-report-recovery.md). For the company Instagram-page DM implementation and current live sender state, read [`docs/sessions/2026-08-18-instagram-company-page-dm-priority.md`](docs/sessions/2026-08-18-instagram-company-page-dm-priority.md) and [`docs/sessions/2026-08-14-company-instagram-page-dm-handoff.md`](docs/sessions/2026-08-14-company-instagram-page-dm-handoff.md).

### Documentation Review (2026-08-12)

Full cross-file review of AGENTS.md, plan.md, this document, and docs/handoff/2026-08-12-report-recovery.md. Fixed 18 issues across 4 files:
- **Security**: Redacted 3 exposed secrets (Apollo webhook key, Apollo API key, Call Outcome secret)
- **Stale data**: Updated `ghl_contact_id` from `0/13,868` to `13,755/13,868` across all files; updated plan.md Data Pipeline Status; marked Sales Ingest + Call Outcome auth as DONE in plan.md
- **Contradictions**: Fixed SimpleTexting status (AGENTS.md said "active/published" vs Status.md "unpublished"), DAN candidateLimit (85 vs 65), Partnership dry-run→live, Reply Backfill version ID (`462e`→`4620`), Emerald HTTP wrapper severity
- **Formatting**: Fixed plan.md step 6 indentation
- **Remaining**: `repomix-output.md` was regenerated via `packlive` at end of this session.

### Severity-Ranked Open Work

1. ~~**Critical: repair and prove GHL Sales Ingest**~~ **DONE.** Published version `91603d56`; execution `743094` wrote 7,984 opportunities + 7,984 pipeline history rows.
2. **Critical: restore source coverage with provenance**. Opportunities now restored. Voice, email, LinkedIn, SMS still at zero — will populate through live workflow activity. LinkedIn Reply Backfill executed successfully (execution `743291`).
3. ~~**Critical: authenticate public write boundaries**~~ **DONE for Call Outcome Ingest and SimpleTexting send/callback boundaries.** Review the remaining Warm intake webhooks; retain explicit approval gates for manual sends/calls.
4. ~~**High: audit then backfill `ghl_contact_id`~~ **DONE.** Re-backfilled 12,639/13,868 from GHL export CSVs (email/phone/name+company matching). 1,229 unmatched (not in exports).
5. ~~**High: verify voice persistence safely**~~ **DONE.** Migrated dialer (4 nodes) and callback (8 nodes) from broken Postgres v2.6 to direct `require('pg')`. Both published and verified.
6. **High: migrate embedded secrets** to Config nodes (Community Edition cannot use env vars in Code nodes) or n8n managed credentials where available, then rotate exposed values. Full audit completed — 12 critical, 5 high, 2 medium findings documented.
7. ~~**Medium: fix report correctness debt**~~ **DONE.** Removed duplicate Executive Summary JSON keys, fixed timezone drift in both report workflows, added date filters to `stageVelocity`, `sql_contacts`, `pool_distribution`.
8. **High: 1,229 unmatched ghl_contact_id rows** — contacts in `emerging_pool_contacts` not in GHL export CSVs. Decide: skip, manual GHL lookup, or re-export.
9. **Medium: Warm intake authentication** — review webhook auth on `5nYzp9DgQUopzWhR`, `OowP3sAd8c9paSKf`, and `SmMf8QIfysuxQJbG`. SimpleTexting send and provider callback boundaries were hardened on 2026-08-17.
10. **Medium: add OAuth-backed social statistics** ~~for reach, impressions, and saves~~ — reach/impressions/likes/followers now live via PIT-backed `LT - GHL Social Statistics Ingest` (saves stays N/A); complete approved native GHL report widgets/page names through the UI.
11. ~~**Low: monitor migrated voice dialer**~~ **DONE 2026-08-14.** Thirteen consecutive scheduled executions succeeded after the direct-`pg` migration, including execution `746845` through `Postgres - Release Lock`.
12. **Low: clean legacy nodes/scripts and stale historical prose** only after live paths are stable.

The exact restart procedure, evidence, and guardrails are in [`docs/handoff/2026-08-12-report-recovery.md`](docs/handoff/2026-08-12-report-recovery.md), section `Next Agent: Start Here`.

### Post-Recovery Baseline

Measured directly on live Postgres after execution `743094` (Sales Ingest repair):

| Source | Current Rows |
|--------|-------------:|
| `report_raw_ghl_contacts` | 500 |
| `report_raw_ghl_opportunities` | 7,984 |
| `report_raw_ghl_pipeline_history` | 7,984 |
| `voice_call_queue` | 3 pending |
| `voice_call_attempt` | 0 |
| `report_raw_ghl_call_outcomes` | 0 |
| `Email_Events` | 0 |
| DAN / Emerald / Partnership release logs | 0 / 0 / 0 |
| Main / Partnership LinkedIn state | 0 / 18 |
| SimpleTexting campaign state / events | 0 / 0 |
| `emerging_pool_contacts` / with GHL ID | 13,868 / 12,639 |

Pre-recovery throughput and row-count claims are historical until each source is re-ingested or restored. **Updated 2026-08-20**: `Emerald_Campaign_Contacts` now has 20,238 rows (16,672 pending, 3,566 released) and `Emerald_Release_Log` has 16,154 rows; `partnership_release_log` has 188 rows; `DAN_Release_Log` has 4,664 rows (dormant since 07-22).

This document is the canonical project status and next-steps reference. It supersedes duplicated planning notes in plan.md and other plan documents.

> **Historical traceability**: Fix narratives, root-cause analyses, and execution histories are preserved in git history. This file contains only current live state and actionable next steps.

## Current State Summary

- **Emerald release-log fix + Apollo August 2026 batch enrollment (2026-08-20)**: All three campaign dispatchers (Emerald `8UXlpoMJnQ229AuG`→`d6737e68`, DAN `toUG1yPDmFG48KEP`→`f8f29288`, Partnership `Xshck23cKo1yXL9D`→`2663f32b`) had the same release-log single-row write bug (`mode: runOnceForAllItems` + `$json` read only the first item, so 1 row persisted per run regardless of how many were queued/sent). All fixed by iterating `$input.all()` in `Build SQL - Write Release Log` and setting `queryBatching: "independently"` on the Postgres node. Separately, 73 clean `apollo_august2026` contacts (from `Sales - New Leads - Cannabis _ Hemp _ CBD.csv`, 86 imported) were enrolled into the Emerald **Executives MSO** sequence via dispatcher run `769889`; all 73 confirmed enrolled in GHL (`seq emerald - executives mso` + `seq enrolled - emerald`) and marked released + release-logged. The 58 prior-run contacts left unlogged by the bug were backfilled to released + release-logged, leaving **0 pending+unlogged candidates** so no re-dispatch occurs.

- **Executive Report response-rate + social-engagement fixes (2026-08-04)**: User reported that 1 LinkedIn partnership response and 1 email partnership response showed as 0 response rate, and that LinkedIn/email data for the 3 campaigns (New attribution model - brands, New attribution model - dispensaries, Partnerships) looked wrong. Root-cause investigation found 4 bugs, all fixed and published:
  1. **Reply Poller wrong HTTP method (CRITICAL)**: `LT - Partnership Reply Poller` (`0SQ7tTk03okegp9V`) called `POST /conversations/search` which returns 404; the correct endpoint is `GET /conversations/search` (200). Every poll run failed with `email_reply_lookup_failed` on all ~59 contacts, so the email reply was never detected. Fixed to GET with query params; smoke-tested execution `522221` now returns `errors: []` (was 59 errors). Published version `736386a2-a7d2-434d-b9ba-72026e49c98b`.
  2. **Reply Handler never wrote a reply event (CRITICAL)**: `LT - Partnership Reply Handler` (`mRDw57IHtnQe4wOo`) only tagged `partner_replied` + created an opportunity + Slack alert; it never wrote to `Email_Events`. Added a `Store Reply Event` Postgres node that inserts `event_type='replied'` into `Email_Events` (campaign_id `partnership`, workflow `LT - Partnership Reply Handler`). The handler now also passes `email`/`event_ts` through. Published version `ad993fc2-4822-49bb-ad3e-f045a86b465d`.
  3. **Reply Backfill one-shot (CRITICAL)**: `LT - LinkedIn Reply Backfill (Unipile)` (`QfJ2EZcc7lZwNgxj`) only selected rows where `dm_backfill_checked_at` was empty, so it ran once on 2026-07-31 (all partnership rows set to `idle`) and never re-checked. The `Select Pending Backfill Rows` query now also re-selects rows whose last check is older than 6 hours and whose `dm_conversation_status <> 'active'`, so new replies are picked up. Published version `0620c314-befb-4620-b23a-ad96b55cf4a0`.
  4. **Social insights key mismatch**: The Executive Summary's `social_posts` CTE read `insights->>'likes'/'comments'/'shares'` (plural) but the social ingest stores `like`/`comment`/`share` (singular). Fixed the `Build Query` node to `COALESCE` both plural and singular keys. Verified live: `socialPosts` now shows `totalLikes: 24, totalShares: 4, totalComments: 3` (was all 0). Published version `ff6fdc52-5eef-44b2-a50a-358cace45228`.
  5. **Historical reply recovery completed**: Verified GHL/Unipile records for Strider Peterson's email reply and Jaret Christopher's LinkedIn reply were inserted idempotently on 2026-08-04. On 2026-08-12, verified Unipile records for David Schachter (`rvWEW2K2WYeQ7v6zypDdZQ`, `2026-08-10T15:09:07.711Z`) and Gretchen Gailey (`8UF3lxibUmKYaG87h1F5Pg`, `2026-08-06T16:20:35.281Z`) were also inserted idempotently. Partnership LinkedIn now reports 3 replies. The temporary 2026-08-04 backfill workflows were archived after successful executions `522402` and `522416`.
  6. **Social metric availability corrected**: Executive Summary exposes post-ledger likes/comments/shares and returns `null` for saves/reach/impressions when those fields are absent. Build `2026-08-17-v26-social-reporting-accuracy` renders unavailable statistics as `N/A`, not zero. OAuth-backed statistics ingestion remains pending because the active stored OAuth token is empty and PIT access returns 401.

- **Partnership LinkedIn reporting (2026-07-31)**: The Campaign Channel Summary now returns 10 durable, idempotent `connection_request_sent` events in the `Partnership LinkedIn` row for the verified execution `281366`. The live dispatcher records future successful invites after Unipile success and records provider/state-transition diagnostics without issuing any reporting-time outbound requests.

- **Campaign reporting optimization (2026-08-08)**: Campaign summary workflow `LT - Report Campaign Channel Summary` (`MvPLbUAN9IIQikxb`) is active and published on version `1cea3b9c-d587-4135-806d-46d301e2c7f4`. The response-shaping layer keeps `DAN`, `Emerald`, `Partnership`, `Vapi Brand`, and `Vapi Dispensary` separate. The selected-window response now includes SMS sent/failed/reply totals, normalized failure reasons, and distinct campaign-attributed opportunity counts. The verified 2026-07-09 through 2026-08-07 window returned 294 SMS sent, 1,095 failed, 0 replies, Emerald 3,909 opportunities, Partnership 8, and Vapi Brand 13.

- **Executive Report optimization (2026-08-08)**: Public build `2026-08-08-v18-opportunity-attribution` is deployed. Campaign filters, Vapi filters, campaign drill-downs, comparison view, SMS delivery diagnostics, campaign opportunity counts, LinkedIn metrics, and outgoing-call detail are live. The reports container nginx route for `/api/report/executive/outgoing-calls` was restored and verified HTTP 200.

- **Native GHL report cleanup (2026-08-08)**: Report `6a67dce4a51a4360c60963a3` is saved with the `Last 30 days` date range. The duplicate page-3 `Outgoing calls by status` widget was removed. The report still has three pages. Additional stage, campaign-tag, email, page-name, and custom-metric widgets remain open.

- **Voice stack**: ACTIVE since 2026-07-14, hardened 2026-07-16, optimized 2026-07-20, and call-path hardened 2026-07-23. All 3 outbound assistants (Jordan/Dispensary, Alex/Brand, Savannah/V1) updated: compliance disclosure removed from voicemail, discovery questions restructured to one-at-a-time with turn-taking enforcement, IVR/voicemail disambiguation added, stage-direction/throat-clearing ban, pronunciation fixes, `{{contact_name}}`→`{{first_name}}` variable corrected. On 2026-07-25, the Brand assistant and dialer were patched to remove the unresolved `{{company_name}}` opener dependency, pass `company_name` from GHL when available, and explicitly guard against missing placeholders. The dialer uses n8n's native Schedule Trigger every 2 minutes plus a timezone-aware business-hours guard; no external cron job is used. The callback webhook no longer automatically invokes the dequeue helper, and `LT - Voice Dequeue Next` is unpublished so it cannot start unscheduled calls. Callback metadata extraction, GHL note JSON handling, queue completion parameters, tag failure handling, and the 8-tag plus DNC suppression blocklist were hardened. The dialer now marks selected rows `in_progress` before the Vapi request, preventing ambiguous request failures from retrying the same contact; no-phone and outside-hours branches restore `pending`. Poller searches 4 tag pools with rotation, 30/cycle, and removes the source campaign tag after enqueueing. On 2026-07-25, the dialer was changed to continue fetching and filtering blocked/invalid contacts within the same execution, up to 25 queue checks, instead of waiting two minutes after every skipped contact. On 2026-07-30, the dialer and Call Outcome Ingest were repaired after a prolonged outage: GHL `Version` header corrected from `2023-02-21`→`2021-07-28`, the same-run loop guard was rewritten to read from Code-node items instead of invisible Postgres `RETURNING` columns, an empty-queue guard was added before GHL contact lookup, and the ingest workflow's `new Date()` expression was removed from the `queryReplacement` path. The 1,047 failed + 4 cooling_down queue rows were reset to `pending`, restoring 1,051 contacts to the active dialing pool.
- **n8n runtime**: upgraded to target `2.33.3`; redeployment of n8n and PostgreSQL is planned after the August 5 database connection-timeout incident. Native Schedule Trigger is the standard for recurring workflows. The Python task-runner warning during deployment is expected for JavaScript-only workflows; the stale queued-execution incident was resolved by deleting 745 orphaned `new` executions after the initial targeted cleanup, leaving legitimate `waiting` executions intact. The dialer was unpublished/republished, manually smoke-tested, and confirmed to select different queue contacts. It is active and published with the same-run queue loop.
- **n8n stale execution cleanup (2026-08-05)**: after the PostgreSQL/n8n redeploy, the database was healthy but `execution_entity` contained 6,946 `new` executions, 102 `crashed`, and 38 `error` records. The oldest `new` execution was from 2026-07-27. The largest backlogs were SimpleTexting Step Runner (1,915), SimpleTexting Phone Backfill (1,905), Partnership Reply Poller (788), Vapi Intake Poller (396), LinkedIn Reply Backfill (386), Vapi Dialer (313), and Campaign Contact Classifier (261). This is regular-mode stale scheduled execution state, not missing Queue Mode workers. Follow [docs/n8n-stale-execution-recovery.md](docs/n8n-stale-execution-recovery.md): pause high-volume schedules, preserve recent webhook executions, delete stale scheduled `new` records through n8n UI/API in batches, then re-enable workflows gradually. Do not delete directly from PostgreSQL.
- **n8n stale execution cleanup completed (2026-08-05)**: n8n's PostgreSQL pool was rebuilt by restarting the n8n container, then nine high-volume scheduled workflows were unpublished. The supported n8n execution API deleted 6,964 stale `new` trigger executions with zero failures and preserved all webhook executions. The current `new` count is zero; 102 crashed and 38 error records remain as diagnostic history. The schedules remain paused pending controlled reactivation. `N8N_CONCURRENCY=10` is now staged in `n8n/docker-compose.yml` and will take effect on the next Coolify redeploy. See [docs/n8n-stale-execution-recovery.md](docs/n8n-stale-execution-recovery.md).
- **n8n reactivation/optimization plan**: after the redeploy, reactivate paused workflows in tiers: allocator/classifier, reply-state pollers, intake/enrichment, then outbound senders and dialer last. SimpleTexting now has its own one-by-one re-enable sequence because both dispatcher recovery and provider acceptance require controlled verification. Proposed improvements are bounded batches, cheap no-work exits, atomic claims/idempotency, watermarks instead of full scans, and overlap guards. Full gates and cadence proposals are documented in [docs/n8n-stale-execution-recovery.md](docs/n8n-stale-execution-recovery.md).
- **n8n reactivation and recovery**: after redeploy, the seven non-SimpleTexting workflows were republished and verified with matching `versionId`/`activeVersionId`. SimpleTexting production workflows were then temporarily paused after the execution-dispatcher incident recurred. The stale scheduled queue was cleared through the n8n API; nine webhook `new` executions were preserved and one webhook execution remained running. Timeout and pool settings are staged in `n8n/docker-compose.yml` for the next Coolify redeploy.
- **SimpleTexting workflow hardening (2026-08-06 through 2026-08-17)**: bootstrapped campaign state/event tables and indexes, removed runtime DDL, split Warmup preparation from sending, removed unsafe HTTP wrappers, added overlap/claim guards, hardened send/provider/callback boundaries, and reconciled historical state without replaying uncertain sends. Step Runner, Warmup, Pool, and Campaign Sequencer are unpublished; Phone Backfill is active and non-sending. See [docs/n8n-stale-execution-recovery.md](docs/n8n-stale-execution-recovery.md).
- **SimpleTexting audit/authentication pass (2026-08-06)**: live definitions and recent executions were rechecked. Step Runner and Phone Backfill exited cleanly with no work; provider health returned HTTP 200. Fixed provider-ID validation, active-event runtime DDL, webhook payload preservation, the stale nested Set assignment, the GHL intake HTTP wrapper, unresolved-contact handling, duplicate-event claims, and internal webhook authentication. Unauthorized requests now short-circuit without provider/state side effects; authorized dry-run sending succeeds. The authenticated GHL manual-send caller was updated in the UI to send `x-lt-simpletexting-key` and is published. SimpleTexting provider event headers are only required for inbound reply, delivery, and unsubscribe tracking; they do not block outbound API sending.
- **Emerald email campaign**: ACTIVE since 2026-07-07. Dispatches ~14,702 unenrolled contacts through GHL email sequences. Reply suppression was repaired in GHL on 2026-07-26 after an inbound email continued into a later sequence step. **2026-08-20**: fixed the dispatcher's release-log single-row write bug (published `d6737e68`) and enrolled 73 `apollo_august2026` imports into `executives_mso` (GHL enrollment confirmed on all 73).
- **DAN email campaign**: FULLY LIVE AND SENDING since 2026-07-14. 10 templates, 3 GHL workflows, n8n dispatcher active (85/run every 30 min). ghl_contact_id backfilled 2026-07-13 (13,705 IDs). 181+ contacts queued first day with verified email delivery. **2026-08-20**: fixed the dispatcher's release-log single-row write bug (published `f8f29288`); DAN pool currently exhausted so the fix is dormant until candidates reappear.
- **Apollo phone enrichment**: ACTIVE and hardened 2026-07-16. Production path is polling + V4 callback + reaper. Legacy staged webhook orphans were canceled, poller now re-discovers `queued_phone`, callback provider failures map to `callback_failed`, and known blank contacts were backfilled into `queued_phone`.
- **LinkedIn**: Production path is dispatcher -> acceptance/state sync -> canonical 4-message DM sequence. Follower DM and misconfigured Instagram DM sender paths are unpublished. The dispatcher now explicitly reads Config, atomically claims `ready` rows as `requested_pending`, performs immediate GHL tag/reply checks, and fails closed on provider/state errors. State sync uses direct HTTP requests, bounded contact/API budgets, retries/timeouts, explicit error reporting, and preserves terminal/replied state. The shared state-upsert workflow promotes explicit terminal payloads to `completed` and preserves active replies. The state-upsert webhook now requires the protected `X-LT-LinkedIn-State-Secret` header; all discovered callers were updated and published, and unauthorized requests return `403`.
- **Instagram**: old DM Sequence is unpublished after it was found using the LinkedIn Unipile account. New inbound bridge is active and posts messages into GHL Conversations under `Instagram via Unipile`. **Company-page DM sender is LIVE (2026-08-18)**: `IeovbYnhCsetXS89`, brands-first priority, Message 1 only until everyone has it.
- **Social provider bridge**: Instagram and LinkedIn inbound both work through SMS-type custom conversation providers (`LinkedIn: 6a58a14ff3023bea3783c152`, `Instagram: 6a58a1193cdfc36997580a68`). Inbound uses `type: "Custom"`, not `SMS`, and avoids dummy phone/email data. GHL duplicate cleanup consolidated Edmundo Cadorniga to canonical contact `XZ4yChllGBdcsVxhFRDe`; both Instagram chat `yx-R-9J6XdWaFpGOQd1JFA` and LinkedIn chat `60Ult1SrWhOuvuZp1u7nXw` now map there. GHL Conversations is the operator-facing inbox; no dedicated macro dashboard or alert digest is live yet. Detailed handoff and operator runbook live in `docs/strategy/unipile-ghl-bidirectional-integration.md`.
- **Reporting**: GA4, GHL, and GSC ingestion are live. **Call reporting fix (2026-08-01)**: the Executive Report's `GHL Calls` panel undercounted calls because the `calls`/`call_status_breakdown` CTEs read `report_raw_ghl_calls`, which `LT - GHL Daily Calls Ingest` (`SqNQ0BYaTdcqyt1l`) only populates by scanning 2 pages × 25 conversations where the last message is a call (85 calls in 30d). The authoritative `report_raw_ghl_call_outcomes` table is fed by the GHL Call Details webhook (`LT - Call Outcome Ingest`, `PUCfTZBANSPcgS0c`, 348 calls / 333 outbound in 30d). Both CTEs now read the webhook-fed outcomes table; verified live at Total 348 / Answered 261 / Missed 75 / Voicemail 11 / Inbound 14 / Outbound 333. **Channel/UTM attribution fix (2026-08-01)**: `report_channel_daily_summary` and `report_utm_daily_summary` each receive rows from two writers with incompatible keys — the GA4 Traffic Rollup Bridge (`0P2AZcQYWYZjXbRi`, GA4 sessions, `metadata.source='ga4_rollup_bridge'`) and Report Daily Rollups (`EUeOiRttoVLQ9zF9`, GHL contact/opportunity counts, `metadata.source_system='rollups'`). The API's `channels` and `utm_breakdown` CTEs previously grouped all rows by channel/source-medium-campaign and ordered by `sessions DESC`, so GHL-only rows (sessions=0) fell below the LIMIT and the UTM `leads`/`opportunities` columns were always 0. Both CTEs now FULL-JOIN the GA4 rows to the rollups rows on the shared key so each channel/UTM row shows traffic AND CRM outcomes, and channel names are normalized (`unattributed`/`Unassigned`/blank/`(none)`/`not set` → `Unassigned`). Verified live: channel breakdown now clean (Unassigned merges 155 sessions + 4,727 opps; Direct 403 sessions + 229 leads); named UTM campaigns (e.g. `wl_seq_cannabis_ads` 1,159 sessions) correctly show `leads=0` because GHL does not store UTM campaign fields on those contacts (confirmed against raw DB), while the 229 contacts that do carry UTM data land in the unknown bucket. The Executive Report is published on version `b5c67086`. GSC execution `281697` succeeded after OAuth renewal, fetched 10 rows for report date `2026-07-30`, upserted them, and finalized source health as `success`. `LT - GA4 Daily Ingest` (`6pCSGzFmrMDFL5Yq`) is published on version `8f4c63ea-dd33-4c7f-93a5-b3cbb5c8e7fa`; it finalizes success, empty, partial, and failed fetch states, does not advance watermarks on fetch failure, and preserves raw-row idempotency. The reconnected GA4 credential was verified by execution `276731`; pinned failure execution `276747` confirmed health finalization followed by an intentional n8n error. `LT - GHL Daily Sales Ingest` (`aYT5oHcgmBALzHy5`) is published on version `4f3e8068-8864-4b4d-9286-ba4d618cc3a8`; it uses ingest-date snapshots, bounded cursor/retry guards, fail-closed finalization, and health key `ghl_opportunities` to avoid collision with leads. Execution `276626` processed 7,683 opportunities and 7,683 history rows successfully. The Executive Report is deployed as build `2026-07-31-v11-campaign-breakdown`; its campaign/channel table, selected-period comparison, and LinkedIn Invites/Accepted columns are live. After the live 10-contact Partnership LinkedIn test, the Executive Report shows 10 overall LinkedIn invites and attributes them to a `Partnership LinkedIn` campaign row via durable `connection_request_sent` ledger events. Native GHL report `6a67dce4a51a4360c60963a3` loads 11 widgets in an authenticated UI session. Its `Campaign Opportunities` widget is filtered to `Partnership Pipeline`, and its `Contacts by tag` widget uses `Tags -> Is one of` with `partner_candidate_email` and `partner_candidate_linkedin`; the current 2026-07-19 through 2026-07-25 window showed zero/no data after filtering. Native GHL does not consume Unipile activity without explicit CRM synchronization. Detailed gaps and required report fields are documented in `docs/reports/Reporting Gaps and Requirements.md`.
- **Outgoing call detail (2026-08-06)**: Added and published `LT - Report Outgoing Calls Detail` (`VXFHc8IrF9DDEEdj`, version `d004556d-0b11-4a86-8827-f8f58a1eeee3`). Its GET webhook `/webhook/lt-report-outgoing-calls` returns up to 100 Vapi call rows from the seven most recent completed `America/Los_Angeles` days. The report host exposes this through `/api/report/executive/outgoing-calls` and renders it at the bottom of the Executive Report with pagination, disposition, duration, campaign, contact ID/name fallback, first-attempt state, and lazy signed recording playback. Manual execution `703098` succeeded and the production webhook returned 6 rows. This detail surface is separate from aggregate GHL call-status reporting.
 - **GHL PIT verification**: The root `GHL_PIT` was tested directly against the official REST API on 2026-07-31. `GET /locations/Zwz4relUXVPxx8uohnjV` and `GET /contacts/?locationId=Zwz4relUXVPxx8uohnjV&limit=1` both returned HTTP 200 with `Authorization: Bearer` and `Version: 2021-07-28`. The PIT is valid for CRM/API data access. It does not resolve the native Custom Report builder page's Firebase/browser-session failure, and the supported API/SDK still does not expose widget-layout mutation.
- **SMS campaign**: Automated sending is paused. Step Runner, Warmup, Pool, and Campaign Sequencer are unpublished behind dry-run/approval gates. Phone Backfill is active and only repairs campaign phone state. The send webhook, provider router, idempotent sender, inbound, delivery, and unsubscribe workflows are active with fail-closed validation.
- **SimpleTexting remediation**: Boundary hardening, callback registration, and database reconciliation are complete. The next gate is one approved live provider send or natural callback traffic; do not activate schedules solely to perform validation.
- **Former-SDR identity cleanup**: Complete on n8n side. GHL workflows updated. Required legacy compatibility keys preserved.
- **Regulated-business classification / SDR boundary (contract clarified 2026-07-30)**: `qualified` means the contact's business is related to a regulated vertical such as nicotine, cannabis, CBD, vape, or hemp; `not qualified` means it is not a regulated business. The live classifier now writes the canonical classification tags and the Vapi intake is published with a `qualified` gate. Qualified opportunities now enter `Sales Outreach -> Qualified` through published GHL workflow version 10. Existing contact/opportunity ownership alignment is handled separately; the live Jason/Marc allocator handles records entering that stage without a native owner.
- **SDR ownership synchronization**: Published GHL workflow `LT - Opportunity Owner Alignment` (`b26326a5-77af-4df8-8d86-3f636e73afe0`, version 7) now keeps contact owner, native opportunity owner, custom opportunity `Owner`, and routing audit fields aligned for Jason and Marc when the opportunity owner changes. It does not replace the unresolved Janvi qualification gate or allocate unowned Warm records.
- **Classification and promotion implementation (2026-07-30)**: `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) is published on version `9eae8a33-319a-4c8a-9ee7-2b3b3d5fb45f`; `LT - Voice Queue Vapi Intake Poller` (`bYk1Ai6MJLyhTsDZ`) is published on version `99244f60-3c68-4c08-9bcb-1cf5d8bf20d1`; and GHL workflow `Move Contact's Opportunity to Sales Outreach New` (`cd29d8e6-5e0f-45f8-ba4f-c30804ad9b49`) is published as version 10 with both opportunity actions targeting `Sales Outreach -> Qualified`.
- **Ownership double-handling audit (2026-07-30)**: No active duplicate owner writer was found. The classifier writes tags only; Vapi intake writes queue/Apollo state only; the active n8n MQL workflow creates or updates Warm opportunities without owners; and the GHL promotion workflow changes pipeline stage only. The sole active owner-alignment path is GHL `LT - Opportunity Owner Alignment` (`b26326a5-77af-4df8-8d86-3f636e73afe0`, published version 7), triggered by an opportunity `assignedTo` change. It assigns the contact and updates the custom opportunity `Owner` plus routing fields, but does not assign the opportunity owner. The staged n8n workflow `VI39o4X954fYDjOQ` is inactive and must not be activated as-is because it would duplicate those contact/custom-field writes.
- **Legacy-owner migration (2026-07-30)**: Migrated the open Sales Outreach opportunities whose custom opportunity `Owner` was a former owner or Kevin. The final authoritative opportunity search returned zero remaining former-owner/Kevin custom-owner records; native opportunity owners and the published GHL alignment cascade are now the source of truth. The staged n8n owner-sync workflow remains inactive.
- **Jason/Marc no-owner allocator (2026-07-30)**: Published n8n workflow `LT - Sales Outreach Jason Marc No-Owner Allocator` (`eeksgD0fbGHUqh4r`) on a 30-minute native Schedule Trigger. It fetches open `Sales Outreach -> Qualified` opportunities, filters blank native owners in code, assigns Jason (`yU85G6kfhtW4vUtx3QE6`) or Marc (`sqGx5rp3oAUG610NXyjU`) using deterministic opportunity-ID hashing, and writes only native opportunity ownership. The first controlled run assigned 73 records successfully; sample verification confirmed contact owner and custom opportunity `Owner` cascaded correctly through GHL workflow version 7. Remaining unowned Qualified records are draining in bounded batches.
- **Follow-up sender routing - COMPLETE (2026-07-29, audited 2026-07-30)**: Workflow `Jason Followup Emails and SMS` (`f6b44e34-779e-4959-b41d-b05641f134e7`) is published as version 39 with Jason workflow defaults (`Jason from Transparent eCom` / `jason@livetransparent.com`). All 7 Send Email actions use `From Name = {{opportunity.owner}} from Transparent eCom` and `From Email = {{user.email}}`. The six templates (one reused by 2 actions) retain literal Jason sender metadata as safe fallback. The workflow triggers on Sales Outreach stages: New, Attempting Contact 1st Attempt, 2nd Attempt, 3rd Attempt, Engaged. Marc routing path (`sqGx5rp3oAUG610NXyjU`) is configured but untested — zero Marc-owned opportunities have entered a trigger stage. Do not send a live test email unless explicitly requested.
- **Vapi transfer hardening**: Live transfer tool `86d380a3-34d2-41f8-96a0-acf5f0124ccb` and all four assistants now use neutral Sales Lead wording while preserving the compatibility function name `ok_transfer_to_jason` and shared destination `+15622474600`.
- **RB2B assignment hardening**: Live workflow `3kjsIUeoEQFx26cC` no longer runs its hardcoded Kevin task during Warm intake. The legacy task node is disconnected/disabled and the workflow is published with contact persistence ending at `Result`.
- **Classifier per-contact fetch hardening (2026-08-07)**: `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) `Process Warm MQL Contacts` now emits self-diagnosing `fetch_error` records (`error` message + `status_code`) and retries GHL HTTP 429 rate-limit responses up to 3 attempts with linear backoff (1s, 2s) before failing. Root cause was a GHL per-window rate limit on the contact-lookup burst, confirmed by run `723561` (all 12 failures reported `status_code: 429`). Published active version `adcc6622-2e7e-4519-8acf-ba6a628dc8d9` (15-min schedule intact).
- **PIT token rotation (2026-07-30)**: Full GHL PIT token rotation completed and verified. The old token was replaced with the rotated PIT across both Config nodes that embedded it (Intake Poller `bYk1Ai6MJLyhTsDZ`, Dialer `r7UjWLndmc6EqEUW`). Full REST API audit of all 67 active n8n workflows confirmed zero occurrences of the old token remain in live production paths. Both modified workflows were published with matching `versionId === activeVersionId`. Documentation (`AGENTS.md`, `repomix-output.md`, `Operating Snapshot.md`) updated. Historical archive files in `local-archive/n8n/` retain reference snapshots.

## Prioritized Next Steps

0. **Executive Report SDR Performance & Owner Attribution (2026-09-10 closeout)** — Phases 1–5 are implemented/live. Remaining: (a) monitor the daily meeting-outcome digest and confirm Showed/No-show updates; (b) Cameron/Janvi final sign-off on ranking wording; (c) nightly Rollups/QA monitoring; (d) verify the deployed booking-webhook attribution on the next real booking. Do not regress Exec Summary `SET jit=off` performance (~16–19s).
1. ~~**Repair GHL Daily Sales Ingest first**~~ **DONE.** Published version `91603d56`; execution `743094` wrote 7,984 opportunities.
2. **Restore source coverage one system at a time** with supported ingest/replay and provenance. Opportunities now restored; **email is flowing again (73 `apollo_august2026` contacts enrolled into Emerald Executives MSO on 2026-08-20)**; voice, LinkedIn, SMS still need recovery.
3. ~~**Authenticate public write boundaries**~~ **DONE for Call Outcome Ingest and SimpleTexting.** Review the remaining Warm intake boundaries; retain explicit approval gates for manual sends/calls.
4. **Audit and backfill `emerging_pool_contacts.ghl_contact_id`** — Sales Ingest is now healthy, audit can proceed.
5. **Verify voice persistence safely**, then recover campaign/email/LinkedIn/SMS reporting state.
6. **Migrate and rotate embedded secrets** using protected credential/runtime paths.
7. **Fix Executive Summary/date correctness debt** after source recovery.
8. **Add OAuth social statistics and finish native GHL report UI configuration**.
9. **Clean legacy artifacts and reconcile historical prose last**.
10. ~~**Build company-page Instagram enrichment and delivery**~~ **LIVE (2026-08-18; Message 2 enabled 2026-08-24).** The weekday sender `IeovbYnhCsetXS89` is active and published with send priority brands (1) → dispensaries (2) → partnerships (3). Message 2 now uses the approved campaign copy, a two-business-day gate, and step-2 idempotent state updates. Message 3 remains disabled. Remaining work: finish Dispensary/Partnership IG/FB enrichment and create the eight company-level GHL fields (still not created). Facebook Messenger remains deferred to native GHL Messenger and cannot use public Page URLs/Page IDs as recipient IDs.

### Explicit Reporting Notes

- The campaign summary workflow is live and published as `1cea3b9c-d587-4135-806d-46d301e2c7f4`; live 7-day/30-day endpoint checks return named rows, SMS diagnostics, and campaign opportunity counts.
- The `2026-07-20` through `2026-07-26` email engagement gap is a historical `Email_Events` coverage gap; no event-ingest executions existed in that window. Do not change valid aggregation logic or fabricate rates.
- Four credential-bearing response captures remain intentionally untracked and must not be committed.

## Newly Confirmed Gaps

### Follow-up Sender Routing Handoff

- **User requirement**: follow-up email sender name and email must follow the opportunity/contact owner; if neither record has an owner, use Jason.
- **Workflow**: `Jason Followup Emails and SMS`, ID `f6b44e34-779e-4959-b41d-b05641f134e7`, currently published version `39`.
- **Template folder**: `Jason Follow Up Emails`, ID `69e0c9069af5986541802d88`.
- **Affected template IDs**:
  - `69e0d86b9af59801b580f4b5`
  - `69e0db27d6a707bbf190d022`
  - `69e0db9ab02114c1ba3c29d3`
  - `69e0dc56d6a707c0ac90e074`
  - `69e0dcad8ffabf47b4d987c5`
  - `69e0ddd0b021145bab3c4569`
- **Current template state**: all six have literal `fromName = Jason from Transparent eCom` and `fromEmail = jason@livetransparent.com`. Keep this as a safe fallback; the live workflow actions already override it for owned records.
- **Current workflow state**: all 7 Send Email actions use owner-driven sender fields. Verify or set Jason as the no-owner fallback user in the workflow UI. Do not hard-code Jason as the sender for owned opportunities/contacts.
- **API limitation**: `PATCH /emails/builder/{templateId}` accepts literal sender emails but rejects `{{user.email}}` with HTTP 422 (`fromEmail must be an email`). The public `GET /workflows/` endpoint confirms metadata/status/version only; workflow action definitions are not writable through the public API.
- **Browser status**: authenticated GHL workflow access was used to set and publish the Jason defaults. The published version 39 API response confirms `senderAddress` and `status: published`.
- **No test send**: no live email was sent during this investigation or patch.
- **Next session exact order**:
  1. Open the authenticated GHL workflow URL from the user-provided link.
  2. Monitor the next normal follow-up execution; do not send a live test email solely for sender verification.
  5. Reopen the workflow and verify all 7 Send Email actions and the published version.
  6. Do not change template HTML or send a live test without explicit approval.

- ~~**Dialer credential rotation**: verified against GHL, full audit of 67 active workflows confirmed PIT rotation complete. Both Config nodes updated and published.~~ **Done 2026-07-30**
- **Callback authentication**: Vapi server authentication is configured on all four tracked assistants and enforced at the callback boundary with `X-Vapi-Secret`. Unauthorized callback, status, and tool payloads are rejected before routing.
- **SMS and Warm webhook authentication**: SimpleTexting send and provider callback boundaries are hardened. Several Warm intake webhooks still have empty shared-secret configuration and require an authentication pass before continued public use.
- **Credential storage**: active n8n Config nodes still contain API keys and webhook secrets. Migrate to n8n credentials or protected runtime configuration, then rotate exposed values.
- **LinkedIn state-upsert boundary**: `LT - LinkedIn Connection State Upsert` (`Old7ZvyVYgFaJgDr`) is published on version `d9168bbc-9c96-44fd-a356-12e645a2ec3d` with terminal-state promotion, reply preservation, and protected `httpHeaderAuth`. All discovered callers are published with the shared header; unauthorized verification returned `403` and malformed authorized verification reached validation without writing state.
- **LinkedIn Config convention**: all eight relevant state-upsert workflows now have exactly one `Config` node. Callers read `Config.stateUpsertSecret` instead of embedding the shared header value in request code. This is the Community Edition variable workaround, not a replacement for managed credentials.
- **Ingest hardening (2026-07-31)**: GA4 empty/failure finalization, sales snapshot-date and cursor guards, sales `ghl_opportunities` health isolation, LinkedIn sync budgets/retries, dispatcher pre-invite claims, and terminal-state promotion are live and published. Dispatcher and sync were not live-executed during verification because they can mutate LinkedIn state or send invites.
- **Reporting owner dimensions**: contact owner, opportunity custom `Owner`, owner conflicts, and canonical SDR identity are now normalized into the reporting read model via `report_sdr_registry` + owner through rollups + Exec Summary `sdrPerformance` (native `assigned_to` primary, contact-owner fallback, explicit Unassigned bucket). Owner-coverage % is surfaced in `report_source_health` (`ghl_opp_owner_coverage`, `ghl_appt_owner_coverage`). **Implemented 2026-09-09** — see `docs/sessions/2026-09-09-executive-report-sdr-attribution-phase1-2.md`.
- **Campaign-level reporting dimensions**: `LT - Report Campaign Channel Summary` (`MvPLbUAN9IIQikxb`) returns canonical DAN, Emerald, Partnership, Instagram, Vapi Brand, Vapi Dispensary, and SMS rows. Public report build `2026-08-17-v27-social-mql` has campaign/channel filters, drill-downs, comparison view, opportunity counts, SMS diagnostics, LinkedIn and Instagram activity columns, resolved GHL stage labels, explicit Social Planner placement/account-statistics definitions, MQL conversion metrics, and responsive table containment. Native GHL campaign-tag and email-detail widgets remain open.
- **Partnership state and outbound safety (2026-07-31)**: The email, LinkedIn dispatcher, and LinkedIn DM workflows were activated after explicit approval and use `defaultDryRun=false`. Their live schedules and suppression/idempotency guards remain authoritative; do not manually execute them unless an additional live batch is intentional. `partnership_linkedin_connection_state` remains the isolated Partnership state store.
- **Tag-based attribution audit (2026-07-30)**: DAN has reliable queue tags (`Enrollment Queue - DAN - Brands/Dispensaries`) plus `DAN_Release_Log.campaign` and `enrollment_tag`; `brands_pool`/`dispensaries_pool` should remain supporting audience evidence. Emerald has eight bucket-specific queue tags and matching `Seq Emerald - ...` tags, with stronger backend fields in `Emerald_Campaign_Contacts.bucket/email_campaign` and `Emerald_Release_Log.bucket`. SMS has lifecycle tags but its durable campaign identifier is `SimpleTexting_Campaign_State/Event_Log.campaign_key`; `sms_drip` is only the eligibility pool. LinkedIn has lifecycle/suppression tags but no durable campaign tag, so current Brand/Dispensary attribution must use `emerging_pool_contacts.source_list` or historical pool-tag observations until a campaign key is added to state.
- **Vapi correlation**: end-of-call callbacks now recover missing `queue_id` values from prior `voice_call_attempt` records when possible. The dialer also reclaims stale `in_progress` locks after 15 minutes, while unresolved provider correlation remains observable through the callback execution path.
- **Gap fixes applied 2026-07-25**: silent human Vapi answers now classify as `interest_unknown`; dialer global hours are 9am-5pm CT; invalid campaign tags fail closed; source-tag cleanup is dynamic; report config/publish schedules are connected and tested; superseded Apollo Sheet First webhook is unpublished.
- **Vapi hardening applied 2026-07-27**: intake, direct enqueue, and dialer paths require the `not qualified` suppression guard plus an open Warm → New opportunity; callback requests require the Vapi server secret; tool outcomes complete queue rows; timer scheduling uses an atomic Postgres claim; stale queue locks are reclaimed; timer and GHL cleanup requests retry transient failures. The intake still needs to require positive `qualified` classification so raw pool tags cannot bypass the classifier.

## Email Campaign — Emerald (Active 2026-07-07)

### Pipeline

```
Snapshot -> Postgres (Emerald_Campaign_Contacts) -> Dispatcher -> GHL tags + sender field
-> GHL "Enrollment Queue Entry" workflow -> Emerald Sequence -> Email
-> GHL Event webhook -> n8n Event Ingest -> Postgres (Email_Events)
```

### n8n Workflows

| Workflow | ID | Status |
|----------|----|--------|
| LT - Emerald Campaign Sender Release Dispatcher (Staged) | 8UXlpoMJnQ229AuG | Active, hourly |
| LT - Email Event Ingest | ZrqFN8qLKO8eVHDc | Active, webhook |
| LT - Emerald Campaign Snapshot -> Postgres Ingest (Staged) | 0jDKgG8VvmfyORQn | Active, webhook |

### GHL Workflows (All Published)

- **5 Event automations**: WL - Event - Emerald Email Event Ingest - {Opened,Clicked,Bounced,Complained,Unsubscribed}
- **Bridge**: WL - Seq - Enrollment Queue Entry (v13)
- **12 Emerald sequences**: WL - Seq - Cannabis Ads Emerald - {Executives, Marketing, Finance, Retail and Sales} {MSO, SSO}, including the applicable P2 variants
- **Supporting**: WL - Seq - Cannabis Ads - Variant A/B, WL - Seq - Stop on Booked/Reply/Closed (published version 17), WL - Micro - Email Inbound/Outbound/Open Counter

### Dispatch State

- 250 contacts dispatched first batch, 0 errors
- 4 senders: cameron@livetransparent.{com,co,agency,org}, 300/day each Week 1
- Backlog: ~10,618 unreleased after DNC/DND SQL filtering
- Email events flowing within 3 min of dispatch

### Release-Log Single-Row Bug + Apollo August Batch (2026-08-20)

- **Bug fixed (dispatcher `8UXlpoMJnQ229AuG`, published `d6737e68`)**: `Build SQL - Write Release Log` used `mode: runOnceForAllItems` with `$json`, so only **1 release-log row persisted per run** even when 60–132 contacts were queued. The unlogged contacts stayed `pending` and were re-selected on the next hour (re-tag risk). Fixed by iterating `$input.all()` and setting `queryBatching: "independently"` on the Postgres node. Verified `versionId == activeVersionId`.
- **Apollo August 2026 batch enrolled**: 86 contacts imported with tag `apollo_august2026` from `Sales - New Leads - Cannabis _ Hemp _ CBD.csv`. Of these, 73 were clean and enrolled into `bucket=executives_mso` via dispatcher run `769889` (queue tag `Enrollment Queue - Emerald - Executives MSO` → GHL `WL - Seq - Enrollment Queue Entry` → Cannabis Ads Emerald - Executives MSO). All 73 confirmed with `seq emerald - executives mso` + `seq enrolled - emerald` in GHL, and all 73 marked `released` + release-logged. 12 were already Emerald-enrolled (dedup) and 1 was DAN-only (skipped). The 58 prior-run contacts the bug had left unlogged were also marked released + release-logged so no re-dispatch occurs.
- **Same bug fixed in DAN (`toUG1yPDmFG48KEP`, published `f8f29288`) and Partnership (`Xshck23cKo1yXL9D`, published `2663f32b`) dispatchers**: identical `$json` single-row write in their `Build SQL - Write Release Log` nodes. Partnership was actively manifesting (run `766371` sent 3 step-4 emails but logged only 1, creating duplicate re-send risk). Functional test (`test_workflow` execution `769961`) confirmed 3 sent items → 3 release-log writes; the 3 live test rows were deleted (partnership log restored to 188).

### Reply Suppression Repair (2026-07-26)

- **Incident**: Christy Essex replied on 2026-07-23 that she had left Vangst and referred new/current-project questions to Logan Humiston. An automated Emerald follow-up was still sent on 2026-07-26.
- **Root cause**: `WL - Seq - Stop on Booked/Reply/Closed` had the correct `Customer Replied to Sequence Emails` trigger filtered to Email, but its `Remove from Workflow` action only removed the legacy Variant A/B workflows. It did not include the Emerald sequence workflows.
- **Fix**: Through the GHL UI, added all 12 Emerald sequence workflows, including P2 variants, to the removal action. Published as version 17.
- **Immediate containment**: Removed Christy's `seq enrolled - emerald` and `seq emerald - executives sso` tags. Her Warm/MQL context and opportunity were preserved.
- **Boundary**: n8n `LT - Email Event Ingest` remains reporting-only; it stores events in `Email_Events` and is not the sequence suppression mechanism.

### Postgres Tables

| Table | Rows | Notes |
|-------|------|-------|
| Emerald_Campaign_Contacts | 20,238 | 16,672 pending, 3,566 released (includes 73 `apollo_august2026` in `executives_mso` released 2026-08-20) |
| Emerald_Release_Log | 16,154 | Dispatched contacts by sender |
| Email_Events | growing | From 5 GHL event automations |

## Email Campaign — DAN Brands & Dispensaries (LIVE 2026-07-10, Backfilled 2026-07-13)

### Status

- Templates: CREATED (10/10 -- 5 Brand + 5 Dispensary)
- Tags: CREATED (5/5 -- deployed via GHL API)
- Dispatcher: LIVE (toUG1yPDmFG48KEP, active with defaultDryRun=false, every 30 min, candidateLimit=85)
- GHL Workflows: ALL PUBLISHED (3/3)
- Deck Download automations: CREATED in GHL
- ghl_contact_id backfill: COMPLETED 2026-07-13 (13,705 IDs backfilled via email/phone/name matching)
- **5,373 contacts now eligible for DAN dispatch (up from 13 before backfill)**
- **First dispatches confirmed**: Emails sending via GHL (TYPE_EMAIL outbound automated verified)
- **Rate limiting fix**: 250ms delay added between GHL API calls — errors dropped from 40% to 0%
- **2026-07-15 audit**: 5 fixes applied (brand starvation, HTTP wrapper, sender rotation, error logging, jitter)
- **GHL templates verified**: All 10 DAN templates in GHL match repo HTML files exactly
- **2026-08-20 release-log fix**: `Build SQL - Write Release Log` (published `f8f29288`) now iterates `$input.all()` instead of `$json`, so every dispatched/skipped contact is logged per run (was 1 row per run). `Write Release Log` uses `queryBatching: "independently"`. DAN pool currently exhausted (no log entries since 07-22; dispatcher runs with zero candidates).

### GHL Workflows

| Workflow | ID |
|----------|-----|
| DAN - Brands Sequence | 5d25147c-cd63-4c4f-ba49-a0e62c53ee0c |
| DAN - Dispensaries Sequence | ec24cbb8-bd0b-4e6e-8607-d93886a02034 |
| DAN - Stop on Reply or Booked | d7ff2fc2-cdc2-4952-afa7-71cd9edfc490 |

### GHL Sequence Tags

| Tag | Purpose |
|-----|---------|
| Enrollment Queue - DAN - Brands | Triggers Brand email sequence |
| Enrollment Queue - DAN - Dispensaries | Triggers Dispensary email sequence |
| dan_seq_completed | Finished all 5 emails |
| dan_seq_no_engagement | No opens on emails 1-3 |
| dan_seq_replied_or_booked | Replied or booked meeting |

### GHL Email Folders

| Folder | ID |
|--------|-----|
| Brands | 6a4f6b06a3e9bfb4f9ebe8ad |
| Dispensaries | 6a4f6b128c6f614ebf8ba9e9 |

### Template IDs (Brands, folder 6a4f6b06a3e9bfb4f9ebe8ad)

| # | ID | Name |
|---|----|------|
| 1 | 6a4f6fdf525ebffbb911d88c | DAN - Brand 1 - Quick Question |
| 2 | 6a4f6fe0f34b953ec0cfcf5d | DAN - Brand 2 - How It Works |
| 3 | 6a4f6fe15e7d25184dafed44 | DAN - Brand 3 - Housing Works |
| 4 | 6a4f6fe2525ebffbb911d899 | DAN - Brand 4 - Short Version |
| 5 | 6a4f6fe3890f1fb4ac750664 | DAN - Brand 5 - Closing |

### Template IDs (Dispensaries, folder 6a4f6b128c6f614ebf8ba9e9)

| # | ID | Name |
|---|----|------|
| 1 | 6a4f6fe4890f1fb4ac750680 | DAN - Dispensary 1 - Foot Traffic |
| 2 | 6a4f6fe41ad559bda229477d | DAN - Dispensary 2 - How It Works |
| 3 | 6a4f6fe55e7d25184dafed8a | DAN - Dispensary 3 - Housing Works |
| 4 | 6a4f6fe6f74b73e4b5b9ad8d | DAN - Dispensary 4 - Founding Partner |
| 5 | 6a4f6fe71ad559bda2294793 | DAN - Dispensary 5 - Closing |

**Duplicate**: 6a4f6fcdf74b73e4b5b9ac0b — already removed from GHL (verified 2026-07-15)

## Voice Workflows

Phone: +1 (562) 534 1977
Callback webhook: https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback

### Active

| Workflow | ID | Schedule |
|----------|----|----------|
| LT - Voice Agent V1 Vapi Callback + Tools | fx4UvKUWbqJEY3LK | Webhook |
| LT - Call Outcome Ingest | PUCfTZBANSPcgS0c | Webhook |
| LT - Voice Dequeue Next | KsBMFcz1YpBGrjDW | Unpublished helper |
| LT - Voice Queue Enqueue | XzcpOBi9YcIhJPck | Webhook |
| LT - Apollo Queued Timeout Reaper | RL5ZyUoshSPbmVA1 | Hourly (monitors queued + queued_phone) |
| LT - Campaign Contact Classifier | IduCoT5YOs0g2faT | Active (native Schedule Trigger every 15 min; 10 Brand + 10 Dispensary candidates/run) |
| LT - Vapi Campaign Queue Feeder | RFIZ9Bcfl3Yvms2b | Inactive helper |
| LT - Emerging Pool Go Live Helper | OGnADUQKd5z5f905 | Manual helper |
| LT - Voice Agent V1 Outbound Dialer (Vapi) | r7UjWLndmc6EqEUW | Active (native Schedule Trigger every 2 minutes; business-hours guard) |
| LT - Voice Queue Vapi Intake Poller | bYk1Ai6MJLyhTsDZ | Active (native Schedule Trigger every 10 min, 30 contacts/cycle, tag rotation) |

### Campaign Contact Classifier Audit (2026-07-29)

- `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) is active on a native 15-minute Schedule Trigger.
- It selects up to 10 Brand and 10 Dispensary candidates per run, uses live GHL suppression checks, and applies Vapi campaign tags only after DeepSeek acceptance or a qualified-domain match.
- `vapi_qualified_domains` is updated only after a successful campaign-tag write; free-email domains, cleanup rows, failed writes, and rejected model output are excluded.
- Manual execution `268658` and scheduled execution `268659` passed after the audit patch with zero failed writes.

### Fixes Applied — Original (2026-07-14)

- **Published** both Intake Poller and Outbound Dialer (were paused for quality gate)
- **Trigger Apollo Enrichment auth**: changed `predefinedCredentialType` → `none` (was crashing because GHL API key is already in headers)
- **Remove Tag - Enriching URL**: changed `$json.contact_id` → `$json.contact.id` (Apollo response nests ID under `contact`)
- **Full pagination**: GHL contact search was limited to first 20 contacts per tag. Added pagination loop with 250ms delays.
- **30-contact batch cap**: prevents GHL rate limiting on downstream API calls
- **Pool tag search**: added `brands_pool` (3,024) and `dispensaries_pool` (7,953) to search tags alongside `vapi_campaign_brand` (926) and `vapi_campaign_dispensary` (19)
- **Tag rotation**: cycles through one tag per 10-min run to ensure all pools are scanned evenly
- **Timezone inference**: added state-to-timezone mapping in both intake poller (`Classify Contacts`) and outbound dialer (`Code - Check Phone`). Maps US state/Canadian province codes to IANA timezone names (e.g. `NY`→`America/New_York`). Most pool contacts lack timezone data, so this ensures ET contacts get called at 9am ET.
- **Historical ET-forward timing**: the previous cron-based schedule shifted from `*/2 14-22` to `*/2 13-22` UTC to start calling at 9am ET instead of 10am ET. The current implementation uses a native two-minute Schedule Trigger; the timezone-aware business-hours guard remains authoritative.

### Fixes Applied — Round 2 (2026-07-14, Full Vapi Audit)

A comprehensive logic/code/optimization audit of all 12 Vapi workflows found 5 bugs across 3 active workflows, all fixed and published:

**1. Race condition: Dialer could send duplicate calls** (r7UjWLndmc6EqEUW)
`Postgres - Fetch Next Queue Item` was a read-only `SELECT...LIMIT 1`. Between the read and the write, `LT - Voice Dequeue Next` could `UPDATE...RETURNING` the same item. Fixed: changed to `UPDATE...FROM...RETURNING` that atomically locks the row at fetch time.

**2. `report_referral` tool was dead code** (fx4UvKUWbqJEY3LK)
Routed to end-of-call handler that checked `endedReason`/`analysis.summary` — absent on tool call payloads. Node returned `[]` silently. Fixed: re-routed to `Respond - 200`.

**3. Intake Poller could create duplicate queue entries** (bYk1Ai6MJLyhTsDZ)
INSERT lacked `WHERE NOT EXISTS` dedup check. Fixed: wrapped INSERT with `WHERE NOT EXISTS (SELECT 1 FROM voice_call_queue WHERE contact_id = $1 AND status IN ('pending', 'in_progress'))`. Also fixed `Transform Postgres Output` to return `[]` gracefully when dedup blocks insertion (was throwing).

**4. Workflow-crashing tag removals** (bYk1Ai6MJLyhTsDZ)
Three HTTP DELETE nodes lacked `continueOnFail`. A flaky GHL API call crashed the workflow after enqueue/enrich/skip already succeeded. Fixed: enabled `continueOnFail: true` on all three.

**5. Timer race condition** (fx4UvKUWbqJEY3LK)
`$getWorkflowStaticData('global')` not atomic across concurrent executions. Two rapid status-update webhooks could both start a 465-second timer chain. Fixed: replaced `timersScheduled` boolean with `timersScheduledAt` timestamp and 60-second dedup window.

### Fixes Applied — Call-Path and Callback Hardening (2026-07-22 to 2026-07-23)

- **Unscheduled call path removed**: the callback workflow previously posted to `LT - Voice Dequeue Next` after every end-of-call event. That helper could start another Vapi call without the dialer's Schedule Trigger. The callback trigger was removed and `LT - Voice Dequeue Next` was unpublished; it is now an explicit helper only.
- **Callback payload recovery**: the callback Config Set node replaced the webhook input before detection. `Code - Detect Tool vs Callback` now reads the original `Webhook - Vapi` item directly.
- **End-of-call metadata coverage**: the normalizer now reads IDs from Vapi `assistant.metadata`, `assistant.variableValues`, and `artifact.variables` paths.
- **GHL note safety**: completion-note JSON now uses an object expression instead of interpolating unescaped summaries into a JSON string. Note and tag writes are non-blocking so a CRM note failure cannot prevent queue completion.
- **Queue completion safety**: `Postgres - Mark Queue Completed` now passes query replacements as an array, preventing the scalar-parameter error that previously stopped completion.
- **Scheduler standardization**: the outbound dialer uses a fresh native Schedule Trigger with a two-minute interval. The business-hours guard remains the call eligibility authority. Resolved 2026-07-30: the dialer was crashing on every execution due to three separate bugs (GHL `Version` header, Postgres `RETURNING` visibility, empty-queue 403) — fixed and verified end-to-end.

### Fixes Applied — Brand Prompt and Variable Context (2026-07-25)

- **Execution audit**: callback execution `241579` received an `in-progress` status update and entered the background timer as designed. The corresponding end-of-call callback `241581` completed successfully for queue `7aed3bdb-fe22-4b98-a4ce-33b9018fe32b`, normalized the outcome as `voicemail`, applied `vapi_voicemail` and `vapi_voicemail_left`, inserted the call attempt, and marked the queue row completed.
- **Brand assistant prompt** (`1d7c5d42-f0a4-4b58-9494-dbda3be3c657`): removed `{{company_name}}` from the first-message opener so a missing company value cannot be spoken as an unresolved placeholder. Added explicit runtime-variable handling, IVR-versus-voicemail disambiguation, one-question turn-taking, and no-stage-direction rules. The live-call AI/recording disclosure remains system-prompt-only and is excluded from voicemail.
- **Outbound dialer** (`r7UjWLndmc6EqEUW`): `Code - Check Phone` now extracts `company_name` from the GHL contact; `Build Vapi Body` passes it through `assistantOverrides.variableValues` and metadata. The workflow was republished and verified with matching `versionId` and `activeVersionId`.

### Queue State

**1,051 contacts pending** (reset 2026-07-30 from 1,047 failed + 4 cooling_down), 1,615 completed. New pool contacts fed in at 30/cycle via tag rotation. SQL `WHERE NOT EXISTS` prevents duplicate enqueue. Outbound dialer is configured for a native two-minute Schedule Trigger and picks up from queue only during timezone-aware business hours. Blocked/invalid/outside-hours candidates are released and skipped within the same execution, capped at 25 queue checks.

### Final Production Hardening — 2026-07-23

- Callback timer state now has the existing 60-second duplicate-start guard plus 30-minute pruning of ended/inactive records.
- `LT - Voice Queue Enqueue` now requires `X-LT-Voice-Queue-Secret`; callers use `VOICE_QUEUE_ENQUEUE_SECRET` and unauthenticated requests fail closed before queue insertion.
- Apollo phone-request failures are counted as `apollo_phone_request_failed` for monitoring.
- `LT - Apollo Queued Timeout Reaper` now connects its Slack summary builder to `Post to Slack #reaper`.
- Removed the stale response-code option from `LT - Call Outcome Ingest`.
- All modified live workflow versions were verified published with matching `versionId` and `activeVersionId`.

### LinkedIn Queue State

Legacy step-4 LinkedIn DM rows are now marked with `linkedin_dm_sequence_completed` and excluded from future DM selection. The GHL connect dispatcher was stuck with 0 `ready` contacts because its feeder tag check was broken (never detected blocking tags). Fixed 2026-07-14 by unwrapping GHL's nested `contact.tags` response. 14,987 contacts from CSV bulk-upserted as `connection_status = 'ready'` on 2026-07-13. Dispatcher should now find contacts on its next scheduled run.

### Call History Summary (voice_call_attempt)

1,711 total attempts across 1,045 unique contacts. Dispositions: voicemail=782, qualified/booked=305, connected=288, no_answer=212, busy=106, failed=18.

## LinkedIn Workflows (Production Active + Duplicate Send Paths Stopped)

| Workflow | ID | Schedule | Notes |
|----------|----|----------|-------|
| LT - LinkedIn DM Sequence (Unipile) | d0tEtijajisIsYcs | 0 12-22 * * 1-5 | Fixed trailing backtick in jsCode; added template pre-sanitize + send-time sanitize in both DM sender nodes |
| LT - LinkedIn Follower DM Sequence (Unipile) | pq7XVajNFnnwMUTr | Unpublished | Redundant one-touch follower DM path; stopped 2026-07-16 after canonical connected-contact DM sequence was confirmed as the only production DM path |
| LT - GHL LinkedIn Connect Dispatcher (Unipile) | fXxw5lanZcDmUrst | */15 15-21 * * 1-5 | Fixed GHL response unwrap in tag check; added send-time sanitize for invites; added linkedin_dm_sequence_completed to Feeder tag block |
| LT - LinkedIn Connection State Sync (Unipile) | ceaKnz6E3onQrZpt | 15 */6 * * * | Reduced maxPages 15→5, maxContacts 200→50 |
| LT - LinkedIn Connection Acceptance Checker (Unipile) | 3ttEvr5NMcQCS4Hp | Webhook | Replaced $env.UNIPILE_ACCOUNT_ID with hardcoded value |
| LT - LinkedIn Connection State Upsert (Unipile) | Old7ZvyVYgFaJgDr | Webhook | No changes |
| LT - LinkedIn Unipile New Messages (Unipile) | 7o5EBdvwAuIaWW7k | Webhook | Active on `f96dafba-9818-4aab-8656-c2e4e2ab8480`; malformed form-payload field recovery preserves inbound reply data |
| LT - LinkedIn DM Sequence Test (No Delay) | wnpVYUNFLyNe5cS6 | Manual only | No changes |
| **LT - LinkedIn DM Suppression from GHL Tag** | **IPN8jnR3XSurX0o1** | **Webhook** | **NEW 2026-07-15. GHL tag stop_linkedin_dms → webhook → Unipile lookup → GHL tag + state table terminal** |

Intentionally stopped non-canonical sender: `LT - Instagram DM Sequence (Unipile)` (`iCnY6ccdHhfJg3sf`) is unpublished. It was using the LinkedIn Unipile account ID and sending Instagram templates as LinkedIn DMs via `instagram_dm_state`.

Guardrails: former-owner-branded copy blocked before Unipile send. Invite defaults say Transparent eCom (not LiveTransparent).

Outbound guardrails: DM sends now fail closed if the reply lookup fails, and both DM / request paths skip when an inbound conversation is already present.

### 2026-07-15 Unicode Encoding Fix
 All audited Unipile message sender nodes now sanitize message text before API calls, and template registries are pre-sanitized where present. Coverage includes LinkedIn DM Sequence (`Sync Connected from Unipile` and `Send DM Sequence Messages`), LinkedIn Follower DM, LinkedIn Dispatcher invites, and Instagram DM Sequence. `sanitizeMessage()` handles smart punctuation plus mojibake forms like `canâ€™t` / `canΓÇÖt`. Final live audit passed: active versions published, send-time sanitization present, registry pre-sanitization present where applicable, and no remaining bad literal template text in audited sender nodes. Created the local operator helper `local-scripts/suppress_linkedin_dms.py` for one-command DM suppression.

### 2026-07-16 Sender Path Cleanup
Malformed LinkedIn screenshot messages were traced to `LT - Instagram DM Sequence (Unipile)`, not the canonical LinkedIn DM Sequence. Unpublished both `iCnY6ccdHhfJg3sf` and redundant `pq7XVajNFnnwMUTr`; production LinkedIn outreach is now dispatcher → acceptance/state sync → canonical 4-message DM sequence only.

### 2026-07-14 Fixes Summary
- **Connection Acceptance Checker**: `$env.UNIPILE_ACCOUNT_ID` blocked by N8N_BLOCK_ENV_ACCESS_IN_NODE → hardcoded
- **Connection State Sync**: Code node timed out at 300s → reduced batch sizes
- **Follower DM Sequence**: Code referenced missing Config fields → added them
- **DM Sequence**: Trailing backtick in `jsCode` caused syntax error → removed
- **Dispatcher feeder tag check**: `GET /contacts/{id}` returns tags at `contact.tags`, not flat `tags`. Whole pipeline was stuck because blocking tags were never detected. Fixed by unwrapping through `.contact` first.

### Dispatcher Queue State
The `linkedin_connection_state` table was exhausted (all contacts at `requested`/`connected` from June). User exported 14,987 contacts from GHL with LinkedIn URLs and no blocking tags. Batch-upserted via state upsert webhook as `connection_status = 'ready'`. Dispatcher's Fetch Ready Queue should now find contacts on next run.

## Instagram

### Active

| Workflow | ID | Status | Notes |
|----------|----|--------|-------|
| LT - Instagram Unipile New Messages | pISlgYUsyJIrLuJd | Active webhook | Receives Unipile Instagram inbound payloads at `/webhook/lt-unipile-instagram-new-messages`, normalizes identity, creates/updates GHL contacts, persists `instagram_conversation_map`, converts the stored agency OAuth token to a location token, and posts inbound messages into GHL Conversations under `Instagram via Unipile`. |

### Stopped

| Workflow | ID | Status | Why |
|----------|----|--------|-----|
| LT - Instagram DM Sequence (Unipile) | iCnY6ccdHhfJg3sf | Unpublished | It used LinkedIn account `V9eiHiDpRmCtan0YNdzsQw` and the old `instagram_dm_state` model. Do not republish as-is; rebuild the company-page workflow using Instagram account `F2UprZ8aQc6Qm9CYYWU6cg`, company identity fields, reply suppression, and safe cadence. |

### 2026-07-16 Inbound Mapping Status

- Detailed build context, endpoint contracts, known test payload, and next steps: [docs/strategy/unipile-ghl-bidirectional-integration.md](./docs/strategy/unipile-ghl-bidirectional-integration.md)
- Confirmed real Instagram Unipile account: `F2UprZ8aQc6Qm9CYYWU6cg` (`Transparent eCom`).
- Confirmed test inbound identity: `edmundocadorniga`, profile provider ID `6361495593`, messaging/provider ID `109928757071246`, chat ID `yx-R-9J6XdWaFpGOQd1JFA`.
- Created GHL custom fields for Instagram username/profile URL/profile provider ID/chat attendee ID/chat ID.
- Post-merge cleanup: GHL duplicate contacts for `Edmundo Cadorniga` were consolidated to canonical contact `XZ4yChllGBdcsVxhFRDe`; `instagram_conversation_map.id = 1` now maps chat `yx-R-9J6XdWaFpGOQd1JFA` to that canonical contact.
- Inbound OAuth fix: the workflow converts the stored agency token to a location token inline before calling GHL inbound APIs.
- Direct outbound router test: POST to `/webhook/lt-social-provider-outbound` routed the known Instagram contact/chat to Unipile successfully with message id `DOfjxs8_Xm26V5Ee1IO7PQ`.
- Map repair verification: temporary maintenance workflow `nuuB3qCKxr7J6iPw` repointed Instagram map row `1` and LinkedIn map row `2` to `XZ4yChllGBdcsVxhFRDe`, then was archived. Direct outbound router checks succeeded for Instagram (`vjdEYSk9XD6R0I46oPWLwA`) and LinkedIn (`C7I9944kWsSKutX2XhZEpA`).
- GHL UI outbound verification: message `this is a test reply from GHL to Instagram` routed through `LT - Social Provider Outbound Router` to Unipile message `iEJO1vnvWVGwbk7ril1__A`.

### Social Provider Next Steps

- Monitor the next real Instagram inbound after duplicate cleanup; avoid artificial replays unless needed because they create visible conversation messages.
- Confirm Unipile Instagram webhook delivery to `/webhook/lt-unipile-instagram-new-messages` in production.
- `LT - Social Provider Outbound Router` (`kqIi8i1RjFAZKrK3`) direct webhook path is fixed and routes canonical contact `XZ4yChllGBdcsVxhFRDe` to Instagram and LinkedIn via Unipile successfully using canonical provider IDs.
- Optionally run a controlled LinkedIn GHL UI outbound reply test from conversation `Ze8o3KbsrwuAXQ3KK5ge`.
- Build and verify a lightweight macro alert/digest path for inbound LinkedIn/Instagram messages after they are successfully posted to GHL Conversations.
- Rebuild Instagram outbound/follower DM only after the bidirectional inbox path is stable and guarded.

## Apollo Phone Enrichment (Repaired 2026-07-14, Audited + Hardened 2026-07-15)

### Before Fix (2026-07-14)

All 3 webhook-based workflows had 0 executions since 2026-05-13. 1,279 contacts collected `callback_timeout`. Entire pipeline was dead.

### After Fix (2026-07-14)

New **LT - Apollo Phone Enrichment Polling** (JH8ShfpglWmLMZ3l) replaces the webhook-based intake:

1. **Sync profile match**: Calls Apollo `/v1/people/match`, writes name/email/company/LinkedIn/title/dept/revenue to GHL immediately
2. **Async phone request**: Calls Apollo with `webhook_url` pointing to existing V4 callback handler
3. **V4 callback** receives phone data and updates GHL

State as of activation (first hour): 60 contacts enriched, 30/run at 30-min cadence.

### 2026-07-15 Full Audit (7 workflows)

Full review found 2 CRITICAL bugs (`queued_phone` invisible to reaper, Intake Poller re-trigger), 2 HIGH issues (HTTP wrapper, V3 no error handling), and several medium/low cleanups. **10 fixes applied across 6 workflows**:

| # | Severity | Fix |
|---|----------|-----|
| 1 | CRITICAL | Reaper now monitors both `queued` + `queued_phone`; polling writes `Queued At` date |
| 2 | CRITICAL | Intake Poller routes `queued_phone` to `waiting` (was defaulting to `enrich`) |
| 3 | CRITICAL | Sheet First SQL injection fixed — parameterized query replacing template literal |
| 4 | HIGH | `doHttpRequest` wrapper removed from all 4 active workflows (V4, V3, Intake Poller, Sheet First) |
| 5 | HIGH | V3 callback: added error handling catch block with `callback_failed`, then **unpublished** V3 |
| 6 | MEDIUM | Polling `ghl()` now returns status codes; 429 triggers 5s retry on all 3 search sources |
| 7 | MEDIUM | V4 `Apollo Contact Id` now always set (was phone-gated) |
| 8 | LOW | Reaper Config node corruption cleaned (nested `parameters.parameters` removed) |
| 9 | LOW | Intake Poller `removeTag()` — removed `$httpRequest` fallback, now direct `this.helpers.httpRequest` |
| 10 | N/A | `$httpRequest` reference eliminated from all Apollo workflows |

### Pipeline Status (end-to-end)

| Step | Workflow | Handles |
|------|----------|---------|
| Discovery | Intake Poller (bYk1) | Tags contacts, sets `Enrich Phone via Apollo = Yes` |
| Sync match | Polling (JH8Sh) | Apollo `/v1/people/match` → writes profile, sets `queued_phone` + date |
| Async phone | Polling (JH8Sh) | Apollo with webhook → V4 callback |
| Phone callback | V4 Callback (U7c6) | Writes phone to GHL + `enriched` status |
| Re-enqueue | Intake Poller (bYk1) | Finds `enriched` contacts → inserts to voice_call_queue |
| Timeout | Reaper (RL5Zy) | Hourly scan for `queued` + `queued_phone` → `callback_timeout` after 24h |

### Workflow Summary

| Workflow | ID | Status | Purpose |
|----------|-----|--------|---------|
| LT - Apollo Phone Enrichment Polling | JH8ShfpglWmLMZ3l | Active, every 30 min | Polls GHL, calls Apollo sync+async, writes profile + triggers phone callback |
| GHL Apollo Phone Enrichment - Callback Handler V4 | U7c6byTLXAMgcS75 | Active, webhook | Receives Apollo async phone callbacks, writes phone to GHL |
| GHL Apollo Phone Enrichment - Callback Handler V3 | YaWizRnw7XmkcvZH | **Unpublished** | Legacy V3, fully superseded by V4 |
| GHL Apollo Enrichment - Webhook Intake (Sheet First) | WmKAhG7mIaXonNsh | Active, webhook | 0 executions — superseded by polling, SQL injection fixed |
| GHL Apollo Enrichment - Phone Webhook Intake (Staged) | WuxgTa0EEL1mb2SA | **Unpublished** | Legacy path. 1,008 orphaned webhook executions canceled on 2026-07-16; not part of production enrichment |
| LT - Apollo Queued Timeout Reaper | RL5ZyUoshSPbmVA1 | Active, hourly | Flips stale `queued` + `queued_phone` to `callback_timeout` |

### 2026-07-16 Production Hardening

- Verified live production workflows are active and published:
  - Polling `JH8ShfpglWmLMZ3l`
  - Callback V4 `U7c6byTLXAMgcS75`
  - Reaper `RL5ZyUoshSPbmVA1`
- Canceled **1,008** orphaned `running` executions on legacy staged workflow `WuxgTa0EEL1mb2SA`. Sample stuck runs never progressed past the `Webhook` node.
- Polling workflow fix: orphan status rediscovery now includes both `queued` and `queued_phone`.
- Callback V4 fix: Apollo provider-level callback failures now map to `callback_failed` rather than silently landing as `no_match`.
- Polling write-path fix: hardened GHL `PUT /contacts/{id}` fallback after reproducing live API behavior.
  Working update shape is `customFields` without `locationId`; payloads containing `locationId` or `customField` can return `422`.
- Polling now has a minimal fallback write so contacts are not left blank when the full Apollo profile write fails.
- Backfilled 6 previously blank contacts into `queued_phone` on 2026-07-16:
  `VXwNjbZyBm1DMNljim6g`, `K9otZl89OAFlWmGk8fY7`, `mUgGwrkOB8CW8reYmpMd`, `e7eu0xGixu3ATmA61OqN`, `KA8xGJbf0QZHxXV6HXWF`, `8uobjmgriFLAdtmHfjk7`.

## SMS Campaign — SimpleTexting via GHL (LIVE 2026-07-20)

GHL App: `LiveTransparent SimpleTexting SMS`, provider `SimpleTexting SMS` (`6a5b91913953360948dd59f1`), SMS-type, Custom Conversation Provider, Delivery URL: `https://automations.livetransparent.com/webhook/lt-simpletexting-provider-outbound`.

### Live n8n Workflow State

| Workflow | ID | Status | Role |
|----------|----|--------|------|
| LT - SimpleTexting Provider Outbound Router | f4VoO1lBWkYRcQai | Active | Fail-closed provider validation, E.164 normalization, GHL suppression check, canonical send handoff, and confirmed-result enforcement; version `302ec7de-0b82-462f-9a22-b1420abf62c6`. |
| LT - SimpleTexting Inbound Reply (Webhook) | i0pROHpFtN4LYR0Q | Active | Registered protected callback; Slack alert and GHL Conversations mirroring preserved; version `d657c79b-f075-4241-a78d-0be33f67f627`. |
| LT - SimpleTexting SMS Send (Webhook, Staged) | Q3Ivnwe4z2Y3cD7A | Active | Defaults to dry-run; validates auth, templates, business hours, suppression, and provider result; version `47dd0303-3d36-49e4-9bd9-e34873edbad2`. |
| LT - SMS Idempotent Send | gwaEpWDpTIwsafi8 | Active | Canonical deduplicated boundary with strict input and boolean validation; version `bcc7d22e-58b8-4419-a56f-753ff80773b8`. |
| LT - SimpleTexting Warmup Dispatcher (Staged) | dZQLlbTLkpE1843X | Unpublished | Sender-capable; keep paused pending explicit approval. |
| LT - SimpleTexting Campaign Step Runner | dUyOfxllvkxZavaw | Unpublished | Dry-run guard enabled; smoke `757254` stopped before claims. |
| LT - SimpleTexting Campaign Phone Backfill | 8hQKQi1PooYDFxNR | Active | Non-sending phone-state repair; supports `awaiting_phone_refresh` and `phone_unavailable`; version `83202303-bca2-4786-9bce-eed8147307c3`. |
| LT - SimpleTexting Pool Dispatcher (Staged) | usxYXSuc4ahw40V3 | Unpublished | `sms_drip`, 10/run, weekdays 10:15am + 3:00pm ET; dry-run/small-batch gate required. |
| LT - SimpleTexting Campaign Sequencer (Staged) | 7mSiivR3NhtLIcNz | Unpublished | 6-step flow; do not run concurrently with Step Runner until canonical path is decided. |
| LT - SimpleTexting Delivery Events (Webhook) | AEi1VCzkLvaYFr4U | Active | Registered protected callback for delivery/non-delivery; version `31e884de-b4fe-4f03-af22-49cb64b766a1`. |
| LT - SimpleTexting Unsubscribe Events (Webhook) | IyBKMkpYQ7pa0C8V | Active | Registered protected callback for unsubscribe reports; version `c21eb489-9561-4393-8d52-f8a8231fa0a7`. |

### DB Table

`simpletexting_conversation_map` — UNIQUE on `(conversation_provider_id, alt_id)`, with indexes on `ghl_contact_id` and `normalized_phone`. Created on first outbound router execution.

### Phone Format Contract

- Canonical phone: E.164, e.g. `+17144696406`.
- Conversation `altId`: `simpletexting:+17144696406`.
- `simpletexting_conversation_map.normalized_phone`: E.164 only.
- Outbound router has full E.164 normalization (`normalizePhoneE164`). AltId for inbound/outbound mirroring uses `simpletexting:+1<10-digit>` which works for US numbers. Full E.164 migration across delivery/unsubscribe workflows is deferred.
- `simpletext_replied` blocks automated sends; `simpletext_stop` blocks all sends including human GHL provider replies.

### Guardrails

- Human replies bypass business-hours limits but still enforce STOP suppression.
- Outbound router validates `conversationProviderId` against `6a5b91913953360948dd59f1`.
- Idempotent send deduplicates on `(contact_id, workflow_id, message_hash)` per day.
- `simpletext_stop` tag check in outbound router blocks provider-originated sends to opted-out contacts.
- SMS Send mirroring runs on `onError: continueRegularOutput` so mirror failures don't block sends.
- SimpleTexting send boundary uses `AUTO` mode so multi-segment campaign messages are accepted; provider errors are persisted for diagnosis and can be reclaimed on retry.
- Campaign mirroring is gated on `action = message_sent` and a non-empty provider message ID. Dry runs, blocked sends, duplicates, and provider errors do not call GHL Conversations.
- Inbound reply still posts to Slack AND GHL Conversations; Slack alert preserved as secondary channel.

### Current Template Registry

- Send webhook: `https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms`.
- Canonical keys: `sms_1` through `sms_6`.
- Updated 2026-07-26: `sms_1`, `sms_3`, and `sms_5`.
- Unchanged 2026-07-26: `sms_2` and `sms_6`.
- Updated 2026-07-29: `sms_4` removed cannabis product terms and the unreliable Facebook ad preview link while retaining `regulated-industry` positioning. The published active version is `506303a9-8c6f-466d-9cb6-3e1f68cfc40c`.
- Existing legacy SMS payload aliases remain in place for compatibility and were not renamed.

### 2026-07-24 Fix And Next-Run Check

- Root cause of the `409` provider errors: `LT - SMS Idempotent Send` hardcoded `SINGLE_SMS_STRICTLY`, while SMS 1 is 320 characters and requires multi-segment delivery.
- Root cause of the GHL `404 Contact id not given`: `LT - SimpleTexting SMS Send` mirrored blocked and dry-run outcomes instead of only successful provider sends.
- Fixed and published workflows: `LT - SMS Idempotent Send` (`gwaEpWDpTIwsafi8`) and `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`).
- Safe checks passed: idempotent `simulate:true` execution `241272`; campaign dry run `241275` stopped before the mirror node.
- **Next scheduled dispatcher check:** confirm at least one `status = sent` result with a real SimpleTexting provider message ID, no HTTP `409`, no GHL `Contact id not given` errors, and a matching `report_sms_sent.provider_response` record. Then confirm the campaign state advances to `sent_step_1` only for an actual provider send.

## Partnership Marketing Pipeline (LIVE 2026-07-31)

The original 131 content partnership contacts remain in the partnership pipeline. On 2026-08-27, a separate August 26 source cohort was reconciled as 431 people, with 427 actionable contacts enrolled in both partnership selectors. Two parallel outbound sequences run from Cameron's accounts: a 4-step email sequence (60/day, 11am ET Mon-Fri) and a 4-step LinkedIn DM cadence dispatched through Unipile (30 connection requests/day, 3pm CT Mon-Fri). Both sequences use 2-weekday intervals between steps. All infrastructure is fully isolated from the main DAN/Emerald pipelines (separate Postgres tables, separate n8n workflows, separate GHL pipeline).

### Import

- 131 unique contacts after dedup/merge (script: `scripts/partnerships/clean_partnership_data.py`)
- 98 email contacts imported via n8n batch workflow (`zmrYrUjVcyXaS7PJ`, webhook `/webhook/lt-partnership-bulk-import`)
- 33 LinkedIn-only contacts created in GHL via MCP (no email; LinkedIn URLs set via `ew6uQQnAjgCbjeGn` webhook)
- All contacts assigned to Janvi (`ck6TRlU3wnTmMxuVpn5F`)
- Tags: `partner_candidate_email` (email contacts), `partner_candidate_linkedin` (LinkedIn contacts), or both
- August 26 cohort: 404 newly created contacts carry `august_26_partnership_contact`; 427 actionable contacts carry both campaign selector tags. Four rows across two shared-email groups were skipped pending manual resolution.
- 14 contacts excluded from original CSV due to wrong company/email domain mismatches — awaiting corrections from user
- Test contact `NVAp2GdpbWXLheyUgVf2` (edmundocadorniga@gmail.com) cleaned — partnership tags removed

### GHL Pipeline

- Pipeline: `Partnership Pipeline` (`tQkFYrHjALgoLz6oq0uz`)
- Stages: New Partner Lead (`ccc3d423-ff86-46b4-bd53-064458910eba`) → Contacted → Proposal Sent → Closed
- Opportunities created automatically by Reply Handler when a contact replies (email or LinkedIn)

### Email Templates

4 templates created in GHL folder `Partnership Email Campaign` (`6a6b768aa43d24a7ce1514f1`), populated with HTML via PATCH API and `{{contact.first_name}}` merge fields:

| # | ID | Name |
|---|----|------|
| 1 | 6a6b8dfba3c113f06dee9e26 | Partnership - Email 1: Initial Outreach |
| 2 | 6a6b8e05264ebab67f776e9c | Partnership - Email 2: Follow Up |
| 3 | 6a6b8e06a3c113f06dee9ee6 | Partnership - Email 3: Value Proposition |
| 4 | 6a6b8e07a4bd9f4493fc536e | Partnership - Email 4: Breakup |

**Important**: The Email Dispatcher currently sends via `POST /conversations/messages` with inline HTML, not through GHL templates. The templates exist for open tracking and deliverability but are not the primary send path. The dispatcher's inline HTML in the Code node is the canonical message content.

### Postgres Tables

| Table | Purpose |
|-------|---------|
| `partnership_linkedin_connection_state` | Mirrors `linkedin_connection_state` with `source_key = 'partnership'`. Tracks connection status, sequence step, and DM state. |
| `partnership_release_log` | Tracks every sent email (contact, step, status, message ID). UNIQUE on `(ghl_contact_id, email_step)`. |

### GHL API Key

GHL, Unipile, and state-upsert values remain configured in the live workflow runtime; values are intentionally omitted from documentation. Credential migration and rotation remain open.

All 7 partnership workflows are active and published. The dispatcher schedules are explicit weekday cron schedules: email at 11:00 America/New_York, LinkedIn requests at 15:00 America/Chicago, and LinkedIn DMs at 12:00 America/Chicago. Outbound was explicitly activated on 2026-07-31 with `defaultDryRun=false`; do not manually execute these workflows unless intentionally sending an additional batch. `partnership_release_log` currently holds 188 rows (restored to 188 on 2026-08-20 after a 3-row functional test was cleaned up). On 2026-08-20 the Email Dispatcher's `Build SQL - Write Release Log` node was fixed (published `2663f32b`) to persist **all** sent emails per run instead of only 1 (previously run `766371` sent 3 step-4 emails but logged only 1, creating a duplicate re-send risk).

### Tags

| Tag | Purpose |
|-----|---------|
| `partner_candidate_email` | Import tag — marks contact for email sequence |
| `partner_candidate_linkedin` | Import tag — marks contact for LinkedIn sequence |
| `august_26_partnership_contact` | Source tag — identifies contacts newly created from the August 26, 2026 partnership cohort |
| `partner_email_queued` | Applied after first email send — marks contact as active in email sequence |
| `partner_linkedin_requested` | Applied after LinkedIn connection request sent |
| `partner_email_sequence_completed` | Terminal — all 4 emails sent |
| `partner_replied` | Terminal — contact replied (stops all sequences, creates opportunity) |
| `partner_not_interested` | Terminal — manual override |
| `partner_do_not_contact` | Terminal — manual override |

### n8n Workflows

| Workflow | ID | Status | Role |
|----------|----|--------|------|
| LT - Partnership Email Dispatcher | Xshck23cKo1yXL9D | Active | Sends 4-step email sequence via GHL Conversations API. 60/day cap, 11am ET Mon-Fri, 2-weekday intervals. Release-log write fixed 2026-08-20 (`2663f32b`). |
| LT - Partnership LinkedIn Dispatcher | crKIsaL5k3YBfqDZ | Active | Sends LinkedIn connection requests via Unipile. 30/day cap, 3pm CT Mon-Fri. Atomic ready→requested_pending claim. |
| LT - Partnership LinkedIn DM Sequence | nspggypNF245xzeL | Active | 4-step LinkedIn DM cadence for connected partnership contacts. 2-weekday intervals. |
| LT - Partnership Reply Handler | mRDw57IHtnQe4wOo | Active webhook | POST `/webhook/lt-partnership-reply`. Tags contact `partner_replied`, creates opportunity in Partnership Pipeline → New Partner Lead, posts Slack alert. |
| LT - Partnership Reply Poller | 0SQ7tTk03okegp9V | Active | Schedule Trigger every 5 min. Polls GHL for inbound email replies from `partner_email_queued` contacts, triggers Reply Handler on detection. |
| LT - Partnership Bulk Import | zmrYrUjVcyXaS7PJ | Active webhook | Bulk-imported 98 email contacts into GHL. |
| LT - Partnership LinkedIn URL Update | ew6uQQnAjgCbjeGn | Active webhook | Set LinkedIn URLs on 33 LinkedIn-only contacts. |

### LinkedIn Workflow Patches

3 existing LinkedIn workflows were patched to also query `partnership_linkedin_connection_state`:

| Workflow | ID | Patch |
|----------|----|-------|
| LT - LinkedIn Connection Acceptance Checker | 3ttEvr5NMcQCS4Hp | SQL UNION to include partnership rows; `source_table` routing |
| LT - LinkedIn Reply Backfill | QfJ2EZcc7lZwNgxj | UNION ALL select + separate Update node for partnership table |
| LT - LinkedIn Unipile New Messages | 7o5EBdvwAuIaWW7k | UNION ALL + routing node + separate partnership update |

### Audit (2026-07-31)

Full post-build audit completed:
- All 7 partnership workflows published and active
- 3 patched LinkedIn workflows verified with correct partnership table queries, routing, and update nodes
- Campaign Channel Summary (`MvPLbUAN9IIQikxb`) SQL includes `partnership_release_log` via UNION ALL (published version `6641aa9a`)
- Postgres tables `partnership_release_log` and `partnership_linkedin_connection_state` bootstrapped and verified
- Executive Report frontend later updated to build `2026-08-01-v12-campaign-breakdown`; the dated audit below records the original partnership deployment.
- GHL contacts verified: 98 with `partner_candidate_email`, 127 with `partner_candidate_linkedin` (94 overlap), 131 total
- 4 email templates confirmed in folder `Partnership Email Campaign`, all with correct HTML content
- Partnership Pipeline (`tQkFYrHjALgoLz6oq0uz`) with 4 stages confirmed in GHL
- No regressions detected

### Remaining

- **GHL Custom Report**: Partnership widgets are configured and verified in native report `6a67dce4a51a4360c60963a3`; MQL, owner, and stage-split widgets remain limited by the builder.
- **Social statistics ingestion**: Add a usable GHL OAuth credential to n8n and ingest daily saves, reach, and impressions; the PIT cannot access the official statistics endpoint.
- **Executive weekly LinkedIn KPI**: Adjust the query to count `reply_received` alongside legacy `inbound_reply` events.
- **Reply Poller API gap resolved 2026-07-31**: `LT - Partnership Reply Poller` (`0SQ7tTk03okegp9V`) used the wrong `POST /conversations/search` method in the earlier implementation. The current published implementation uses `GET /conversations/search`; see the 2026-08-04 remediation entry above.
- **14 excluded contacts**: User to provide corrected company names; re-import when available
- **Marc-owned follow-up sender routing**: Untested — zero Marc-owned opportunities exist in trigger stages

## Reporting

### Active Workflows

| Workflow | ID |
|----------|-----|
| LT - GHL Daily Leads Ingest | osIJOgBmWITF5Yuv |
| LT - GHL Daily Sales Ingest | aYT5oHcgmBALzHy5 |
| LT - GHL Daily Calls Ingest | SqNQ0BYaTdcqyt1l |
| LT - GHL Daily Appointments Ingest | yWZVSqEcjTbMT3kG |
| LT - GHL Daily Social Ingest | QZoqCaTwDhbym80O |
| LT - GA4 Daily Ingest | 6pCSGzFmrMDFL5Yq |
| LT - GA4 Traffic Rollup Bridge | 0P2AZcQYWYZjXbRi |
| LT - GSC Daily Ingest | xHqmCC1vOeZ11gCd |
| LT - GSC Rollup Bridge | fOVBHwti9rC3qrLV |
| LT - Report Attribution Bridge | Y0TU7Il71JswxOBp |
| LT - Report Daily Rollups | EUeOiRttoVLQ9zF9 |
| LT - Report Executive Summary API | Bukc0mgOD2r7V6ED |
| LT - Report QA and Alerts | M5mXcDTFSko6EdHb |
| LT - Report Config Sync | aomO3Z4AXJIgEvvN |
| LT - Report Publish Refresh | 3gXztCnBEN6sGINb |
| LT - Report Postgres Bootstrap Apply | 3XHThUiUSNa4sTb9 |
| LT - Report Pipeline Velocity | iFfwh0jpYUZoDhDR |
| LT - Company MQL Google Sheets Sync | 9Y3Kedm768kkwwSV |

### State

GA4, GHL, and GSC ingestion are all live. GSC execution `281697` confirmed the renewed OAuth credential and successful source-health finalization. Executive report live in GHL. Report rollups, attribution bridge, QA/alerts, and executive summary API all running.

### 2026-07-25 GHL Leads Ingest Rate-Limit Hardening

- `LT - GHL Daily Leads Ingest` (`osIJOgBmWITF5Yuv`) failed in `Fetch + Normalize Leads` with GHL HTTP `429 Too Many Requests` during paginated contact retrieval (execution `241845`).
- Replaced the task-runner-incompatible HTTP wrapper with direct `this.helpers.httpRequest` calls.
- Added bounded 429 handling: up to four attempts per page, honoring `Retry-After` when available and otherwise using exponential backoff.
- Added a 500 ms delay between pagination requests to reduce GHL rate-limit pressure.
- Published workflow version `c740c006-fef5-4873-91b5-d2d4218872de` and confirmed it is the active version.
- Manual production-path validation execution `241894` succeeded: 500 contacts fetched, raw lead upserts completed, sync watermark and source health updated, and final status was `success`.
- Updated local reporting SDK snapshots (`leads_ingest_sdk_v2.ts`, `leads_ingest_sdk_v2_clean.ts`, and `leads_ingest_sdk_v3.ts`) with the same HTTP hardening.

## Next Steps -- By Priority

### 1. Vapi Campaign Monitoring

- ~~Monitor Intake Poller executions to confirm steady 30/cycle churn through all 4 pools~~ — Confirmed: poller running successfully every 10 min throughout 2026-07-20 dialer outage
- ~~Monitor Outbound Dialer~~ — Dialer recovered 2026-07-20 after stuck-queue fix (contact `AX3wfQNpRwm6DG0HgUE2` deleted from GHL, `neverError: true` applied to lookup, `onError: continueRegularOutput` on call note)
- Watch for GHL rate limiting on downstream nodes
- Verify `report_referral` tool calls now get proper ack in Vapi logs (Fix #2)

### 2. Voice Hardening

- Test live calls with both Brand and Dispensary assistants after system prompt updates (discovery questions should flow one-at-a-time, no disclosure on voicemail, no "clears throat", "from Transparent eCom" not "with a transparent")
- Consider switching Jordan's voice from Nico to Emma/Layla (both already fallbacks) to eliminate remaining TTS artifacts
- Move remaining secrets out of Config nodes into n8n credentials or env-backed config
- Verify Vapi dashboard tool webhook URLs point to canonical callback

### 3. Emerald Email Campaign Ramp

Monitor first week of dispatcher runs. Verify Email_Events data quality. Increase warmup caps as sender reputation builds. Currently ~250/hr, ~1,200/day capacity with 4 senders.

### 4. Reporting Depth

- Expand contact-capture panel by channel and landing page
- Build matched funnel views by channel, campaign, and landing page

### 5. Attribution Expansion

- Build Meta Ads ingest for spend, clicks, impressions, and cost metrics

### 6. DAN Email Campaign Ramp

- Monitor dispatcher runs at 65/cycle every 30 min — verify consistent deliverability (5 fixes applied 2026-07-15)
- Track Email_Events for DAN campaign data quality (opens, clicks, bounces)
- Monitor DAN_Release_Log growth — ~1,200/day target should exhaust eligible pool in ~4 days
- Recurring DNC contacts (BRĒZ, Teal Cannabis, AYR Wellness, Nova Farms) are not written to release log but reappear each run — address stale tags in report_raw_ghl_contacts to reduce waste
- Verify sender rotation (4 senders) doesn't trigger GHL domain limits

### 7. Apollo Enrichment — MONITORING (audited + hardened 2026-07-15)

- ~~Watch polling workflow runs to confirm steady 30/cycle consumption~~ — Confirmed: batch size 50, steady 30-min runs, all successful
- ~~Verify V4 callback handler starts receiving Apollo async phone responses~~ — Confirmed: 1,058+ callbacks received by 2026-07-16, working
- ~~Confirm `queued_phone` contacts transition to `enriched` as callbacks arrive~~ — Pipeline confirmed end-to-end. Reaper now monitors both statuses.
- ~~Retune maxPerRun and schedule if Apollo rate limits appear~~ — 429 retry with 5s delay added to all 3 search sources
- ~~Ensure legacy blank contacts are not left invisible after poller write failures~~ — Fixed 2026-07-16 with hardened poller fallback + 6-contact backfill to `queued_phone`
- **ACTIVE MONITORING**: Watch Reaper Slack reports for `queued_phone` reaping counts
- **ACTIVE MONITORING**: Confirm polling `Queued At` dates flow correctly so Reaper aging works
- **ACTIVE MONITORING**: Watch for Apollo API rate limits / Apollo credit exhaustion on async phone callback requests; V4 now maps provider failures to `callback_failed`

### 8. Partnership Marketing Monitoring

- Monitor first Partnership Email Dispatcher run at 11am ET — confirm emails send, release log writes, and `partner_email_queued` tag applied
- Monitor first Partnership LinkedIn Dispatcher run at 3pm CT — confirm connection requests send, state table updated, `partner_linkedin_requested` applied
- Verify Partnership Reply Poller detects any inbound replies and triggers Reply Handler correctly
- Confirm Partnership LinkedIn DM Sequence picks up connected contacts after Acceptance Checker processes them
- Verify 3 patched LinkedIn workflows (Acceptance Checker, Reply Backfill, Unipile New Messages) handle partnership rows correctly
- Monitor for GHL rate limiting on per-contact API calls (250ms delay between contacts)
- After first email sends complete, verify the campaign summary endpoint reflects non-zero "Partnership emails" catalog row (may lag until reporting rollup runs)

### Historical LinkedIn Dispatcher Monitoring

- Historical checklist only: the post-recovery main LinkedIn state table currently has 0 rows, so the old 14,987-ready count is not current.
- Verify restored state and current queue counts before expecting dispatcher work.
- Verify dispatcher sends invites (successTag: `linkedin_connection_requested`) and updates state table correctly
- Watch for GHL rate limiting on dispatcher's per-contact API calls (tag check + LinkedIn URL extraction)
- Confirm Acceptance Checker correctly processes new connections and applies `linkedin_connected` tag

### 9. Cleanup and Adjacent Automation

- ~~Build automated LinkedIn DM suppression workflow~~ — DONE 2026-07-15. GHL tag `stop_linkedin_dms` → webhook → state table terminal. Full audit confirms all 3 send paths blocked.
- Build the separate `SimpleTexting SMS` GHL Custom Conversation Provider bridge after the user provides `conversationProviderId`; keep the existing SimpleTexting dispatcher live at low volume.
- Confirm first real SimpleTexting inbound reply posts to the existing Slack alert and suppresses future automated sends; then add GHL Conversations posting as the primary operator inbox.
- Retry and enable blocked GSC ingest workflow
- Monitor LinkedIn outbound guardrails, completion tagging, and reply-state lag after the fail-closed patch
- Clean up temporary fix scripts (scripts/fix_*.py, fix_*.js)
- ~~Delete duplicate DAN template 6a4f6fcdf74b73e4b5b9ac0b in Brands folder~~ (verified already removed 2026-07-15)
- Delete GHL export CSVs after DAN backfill confirmed healthy

## Next Session Start

1. Read `docs/handoff/2026-08-12-report-recovery.md` and re-run `scripts/social-reporting/report_runtime_audit.py`.
2. Re-query the post-recovery baseline because schedules may change counts.
3. ~~Repair GHL Sales Ingest (`aYT5oHcgmBALzHy5`) from failure `742754` before any backfill or report interpretation.~~ **DONE.** Published version `91603d56`; execution `743094` wrote 7,984 opportunities.
4. ~~Verify the repaired workflow's published version and database writes.~~ **DONE.** Sync run completed (15,968 row_count, 0 errors).
5. Restore source coverage one system at a time: voice attempts/outcomes, email/release logs, main LinkedIn state, and SimpleTexting state. Audit `ghl_contact_id` candidate matches before mutation.
6. Ask for explicit approval before any live outbound test.
````
