# Executive Report V1 Plan and Session Handoff

Last updated: 2026-09-26 (EOS closeout; classifier repair, V1 meeting range repair, and inbound Priority routing confirmation)

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
