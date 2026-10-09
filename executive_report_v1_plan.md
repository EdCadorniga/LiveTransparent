# Executive Report V1 Plan and Session Handoff

## 2026-10-09 — SQL booking attribution deployed (EOS)

- Deployed build `2026-10-09-v1-sql-booking-attribution`; the public page returned HTTP 200 with the expected build stamp and SQL-card labels. The live proxied facts endpoint returned HTTP 200 for 2026-09-09 through 2026-10-09, with 582 SQLs entered and 582 classified by the two accepted booking paths (`sdr`, `calendar_link`). The card displays **Booked via / Who / UTM / SQLs**, shows missing UTMs as a repair signal, and reconciles coverage to the SQL denominator.
- Data-quality gap remains: 1 SQL is attributed to Jason Bornillo; 3 calendar-link SQLs have the named Regulated Ads On Social/Search calendar but no UTM; 578 are classified as calendar-link bookings without a captured calendar/link name or UTM. Classification coverage is 100%; source detail coverage is not. Do not treat the fallback category as proof of an individual calendar link.
- GHL has 14 active calendars (including Regulated Ads On Social/Search and Book a demo `WS6lacfQK2XOhqN7mRaF`) and 18 Trigger Links. Published source-attribution workflows exist for Alcohol (`a707d0b6-0717-4903-8b38-3510504a4136`), Cannabis (`c9bbb696-fe29-44b0-81c7-6feffeaac98f`), and Nicotine (`963bf85a-cdff-4eb1-90ea-6a473fb0f32f`). Their legacy source writes and full email-link coverage are not yet verified in the current workflow editor.
- No GHL workflow/contact changes were made. The production workflow-definition v4 API returned 404; the browser was unavailable. Next session: regain supported workflow-editor access; inventory all booking URLs/Trigger Links/calendar destinations in active vertical email templates and workflows; verify appointment creator/booker separately from assigned owner and test reschedule behavior; inspect current source-field consumers; define first-touch-preserving and latest-campaign-touch fields and an idempotent click ledger; implement exact-link click attribution and booking UTMs; verify with a controlled test contact end to end; monitor missing UTMs/link names and refresh report facts. Preserve original acquisition source; a click is not a booked SQL. Detailed runbook: [`docs/sessions/2026-10-09-sql-booking-and-triggerlink-attribution-plan.md`](docs/sessions/2026-10-09-sql-booking-and-triggerlink-attribution-plan.md).

## 2026-10-09 — Report data loading recovery and EOS

- Live report page served HTTP 200, while Summary, Campaign Channels, and V1 Facts requests each took 95–165 seconds in their n8n Postgres query node. A V1 Facts request ran for 99 seconds and shaped a 55 KB response; recent report-host logs also show HTTP 200 responses with 0 bytes. n8n logs report intermittent Postgres connection timeouts. Thus the page's old all-or-nothing `Promise.all` left the entire report at placeholders until every endpoint completed, and empty 200 responses were accepted by nginx's 30-minute cache.
- V1 now renders each source as soon as it responds, reports pending/failed sources, uses `fetch(..., cache: "no-store")` to avoid reusing browser-cached empty responses, and retains the existing empty-body validation/retries.
- The three cached report APIs now skip caching zero-byte upstream responses, bypass proxy cache for retry requests, and use a versioned cache key so existing possibly-empty entries are not reused. The successful-response cache and stale-on-upstream-error directives remain configured. Cache HIT behavior is not yet reverified: initial live checks showed `MISS`, and the later 20-second client recheck timed out while the n8n executions continued to succeed. Confirm normal repeated requests return `HIT` before treating cache recovery as verified. Browser-rendered visual QA was not completed because the available Playwright browser session was already in use.
- Deployment helper build: `v3ud1lum1svamymuor21upog:executive-v1-20261009-streaming-data`; it validates nginx config before replacing the running report container. This fixes the all-or-nothing/empty-cache failure path. Post-deploy read-only checks returned non-empty JSON from all three APIs for the default week (Summary 32,519 B / 75.7 s; Campaign Channels 8,281 B / 4.8 s; V1 Facts 18,228 B / 72.0 s). The slow Postgres queries remain an upstream performance issue; watch the load status and database health if an endpoint stays unavailable. Live read-only workflow checks confirm all three V1 workflows are active and their current version matches active version. Current Facts API version is `9fff955b-96bf-4951-9c75-0054f9792c8d`; Data Materializer is `47c5aaf8-047c-4cfe-996f-bdcbb97bb04d`; Response SLA Materializer is `5957bf7b-a52f-4131-97a6-cc07303cb4b7`. Post-deploy successful API executions: Summary `1113415`, Campaign Channels `1113417`, Facts `1113416`.

### Next weekly report — performance by vertical (user request, 2026-10-09)

- Ed wants the next week's report to count performance separately for each vertical, grouped by the GHL contact `Vertical` field. The next scheduled weekly report is expected Monday 2026-10-12 and covers `2026-10-04`–`2026-10-10` in `America/Los_Angeles`.
- Before updating the report, inspect the existing `verticalPerformance` API/UI contract and identify the actual source rows and distinctness/date rules. Group by the contact's `Vertical` value; preserve all real values and an explicit `Unclassified` row for missing/unmatched verticals.
- Show only metrics supported by reconciled sources. Proposed performance fields already represented in the V1 table are leads, sends, responses, meetings, SQLs, won, lost, and revenue; verify each field's source and period basis before presenting it. Reconcile vertical totals to corresponding report-wide totals and mark unsupported or stale values unavailable. Do not infer that every event's vertical is known from a campaign label.
- This is a reporting requirement only: no contact/workflow writes, campaign changes, or outbound activity.

Last updated: 2026-10-09 (report loading recovery; vertical-performance request; isolated V1 deployment)

## 2026-10-06 — Rolling date default

- When the V1 URL has no explicit `from`/`to` values, the frontend calculates the last completed Sunday–Saturday period using the `America/Los_Angeles` calendar date. This is independent of browser/host timezone.
- Verified for Oct 6 Manila / Oct 5 Los Angeles: `2026-09-27`–`2026-10-03`. Verified next-week calculation: `2026-10-04`–`2026-10-10` for Oct 12 Los Angeles.
- Explicit `from` and `to` query parameters remain pinned. The URL without date parameters is the rolling default: `https://reports.livetransparent.com/embed/executive-v1/`.
- Deployed image `v3ud1lum1svamymuor21upog:executive-v1-20261006`, marker `2026-10-06-v1-rolling-week`. Live default input values and explicit-date preservation were checked. Legacy `/embed/executive/` remains unchanged.
- Next action: observe the no-date V1 URL after the next completed LA week and confirm it advances to Oct 4–10; no blocker remains for the default-date change.

## 2026-10-02 — Band 1 funnel bloat + Pipeline-to-work fix

- **Root cause 1 (band 1 bloat):** the V1 Facts API `feedback_funnel.opportunities_created` counted every opportunity *observed* in any snapshot inside the window (`COUNT(DISTINCT opportunity_id) ... WHERE observed_date BETWEEN`), so 30d showed **11,461** instead of opportunities *created* in the window. `feedback_opps` now derives a per-row `created_date` (same COALESCE as `authoritative_ghl_counts`: `source_created_at` → `createdAt` → `dateAdded` → `report_date`, `America/Los_Angeles`) and the funnel counts by it → **1,387**, matching `authoritativeGhlCounts`.
- **Root cause 2 (blank "Pipeline to work"):** the frontend derived its number from `summary.pipelineDropoff` filtered by stage name `/qualif|mql/i`, which never matches pipeline-level rows (`Sales Outreach`/`Warm`/…), so it rendered "—". Added `pipelineToWork` to the V1 Facts API: distinct contacts on open `Sales Outreach` (`dhdlf3O4tymxFtHk4aqq`) opportunities currently in `New` (`3529dd3d-cab0-4279-967c-1aea203de4fb`) or `Qualified` (`91517911-3eee-45a0-b432-e36209495c16`), from the latest raw opportunity snapshot. Frontend `story()` now reads `f.pipelineToWork.total_contacts`. Live 30d: New 211, Qualified 847, total distinct **1,057**.
- Published `LT - Executive Report V1 Facts API` (`oxYDg6XnRBKhl1Xd`) version `9fff955b-96bf-4951-9c75-0054f9792c8d` (`versionId == activeVersionId`, active). Patch: `scripts/social-reporting/patch_v1_funnel_and_pipeline_to_work.py` (`--dump-sql` / `--apply`).
- Redeployed `reports/embed/executive-v1/index.html` via `scripts/deploy/deploy_report_vps_local.py`. Current report `/embed/executive/` unchanged (sha256 `E675C97C…`).
- Browser-verified live 30d (`2026-09-02`–`2026-10-01`): headline & funnel `Opportunities = 1,387`, `Pipeline to work = 1,057`.
- Not addressed (not requested): `funnel.sql_to_closed_rate` is absent from the API, so the funnel strip still shows `SQL→Closed = —`.

## 2026-09-29 EOS — Response-SLA unmatched-event detail

- Read-only response-SLA detail is implemented and deployed in the isolated V1 report. The Facts API returns the exact `from`/`to` window plus `responseSlaDetails` rows with contact name/ID, channel, inbound timestamp, owner name/ID, source event ID, response metadata, status, and review metadata.
- `responseSla` aggregates are calculated from the same event-detail CTE as the UI table. The UI shows Responded, Internal note done, Unmatched, and Ambiguous tallies and lists unmatched/reviewed contacts with owner.
- `lt_exec_v1_response_sla_reviews` supports `internal_note_done`. The approved read-only GHL `InternalComment` reconciler is now part of the materializer workflow; execution `1064337` processed 100 candidates and found 0 qualifying notes, so no review rows were written. CRM note creation remains separately approval-gated.
- Final active versions: Response SLA Materializer `KlBw3ThLbNlMfE2J` → `5957bf7b-a52f-4131-97a6-cc07303cb4b7`; V1 Facts API `oxYDg6XnRBKhl1Xd` → `4039aea2-787a-420b-81ef-829b076d5cef`. Materializer executions `1064144`, `1064303`, and post-approval `1064337` succeeded; final Facts API checks `1064291`–`1064293` succeeded.
- Verification window `2026-09-23`–`2026-09-28` returned 8 detail rows: 2 LinkedIn unmatched, 2 phone responded, 4 phone unmatched, 0 ambiguous, and 0 internal-note-done. The legacy `/embed/executive/` path remained unchanged.
- Further Speed-to-lead & follow-up implementation—including SLA targets, automatic tasks, CRM note creation, or outbound follow-up—is **not approved for implementation**. The approved read-only internal-note reconciliation is implemented; see `docs/sessions/2026-09-29-executive-report-v1-response-sla-closeout.md` for the exact handoff and verification history.

## 2026-09-29 EOS — Executive Report V1 feedback-retention ledger

This checklist preserves the original structural feedback and is authoritative for the next V1 planning session. “Wired” means the report has a data/UI placeholder or read-only contract; it does not mean the requested behavior is fully accepted.

| Feedback item | Current state | Next-session requirement |
|---|---|---|
| Keep sections in funnel order: Opportunities → MQL → SQL → Closed; keep New contacts outside it | The Band 1 funnel strip follows the requested order and New contacts is separate. The full page still needs a structural review to ensure every related detail section follows the same jump order. | Preserve one consistent funnel sequence across headline, detail, and movement sections; do not pull New contacts into the funnel denominator. |
| Band 1: SQL→Closed % plus MQL→SQL % and raw number; closed SQLs/revenue may be empty | SQL→Closed % is wired in the funnel facts and MQL→SQL is present in the headline row. The funnel-outcomes detail strip still needs explicit MQL→SQL percentage plus raw conversion parity. | Add/verify both raw MQL→SQL and MQL→SQL % in the same Band 1 story, with empty closed values shown as unavailable/zero only when the source explicitly says none closed. |
| Band 2: combine Meetings and Meeting outcomes into one rep · count · showed · no-show · rescheduled card | Not completed; the current V1 has separate meeting and meeting-outcome cards. | Combine them only after appointment-status and owner attribution are reliable; never infer showed/no-show. |
| Band 2: Closed by source | Card and API contract are wired; it may be empty when no closed outcomes exist. Referral and other valid sources must remain in the denominator, with residual Unknown/Unattributed. | Validate source coverage and reconciliation against closed SQL totals. |
| Band 3: weekly lead flow/movement | Weekly lead-flow table and API shape exist, but the current data may be unavailable/empty. | Populate unique/new leads fed in weekly and distinct movement through MQL, SQL, and later stages; distinguish intake counts from current-stage snapshots. |
| Band 3: retargeting | Read-only retargeting card/contract exists for eligible contacts, latest touch, suppression/reply state, and next action; it must not authorize sending. | Surface newsletter-audience contacts and clickers explicitly, with deduplication and suppression rules. |
| Lead-source coverage definition | It is coverage of attributed MQL/SQL rows over the matching MQL/SQL denominator, not only paid marketing SQLs. Referral and other source values count; unresolved rows remain Unknown/Unattributed. | Confirm the denominator and display separate MQL/SQL coverage if needed; do not imply ~100% while source snapshots are incomplete. |
| Speed-to-lead meaning | Confirmed as same-channel inbound reply/call response time, not MQL→first phone call. Unmatched, ambiguous, and internal-note-done are auditable. | Keep the definition visible; SLA targets, automatic tasks, CRM note creation, and outbound follow-up remain unapproved. |
| New contacts / LinkedIn backfill | Acquisition-mechanism support exists, but LinkedIn backfill must remain separately identifiable rather than inflating ordinary new-contact volume. | Reconcile the backfill classifier against the selected window and show the backfill portion separately. |

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
| LT - Executive Report V1 Facts API | `oxYDg6XnRBKhl1Xd` | `9fff955b-96bf-4951-9c75-0054f9792c8d` | Read-only selected-window facts endpoint; meetings restricted to the canonical Regulated Ads calendar; `range=7d|30d|90d` maps to LA date windows |
| LT - Executive Report V1 Response SLA Materializer | `KlBw3ThLbNlMfE2J` | `5957bf7b-a52f-4131-97a6-cc07303cb4b7` | Refreshes inbound-to-response facts every 15 minutes |

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
- The authenticated browser also exposes the native widget route `POST /reporting/dashboards/revex/calls`; its status response directly returned Jason `350` (`285 answered, 35 no-answer, 19 busy, 11 failed`) and Marc `1,006` (`802 answered, 59 no-answer, 105 busy, 40 failed`). It uses `dateAdded`, outbound direction, SDR `userId`, and `Asia/Manila` timezone. This is useful for read-only browser verification, but it remains private/unsupported and must not be automated unattended without GHL approval.

### Decision and next validation

- Two date-bounded queries (selected 7d and prior 7d) are technically possible using the documented export. Cursor pagination is required, and cursors are valid for two minutes; collect each window promptly within that cursor lifetime. The private Call Reporting UI route also paginated the exact snapshot week in 28 pages, but it rejected the PIT and remains unsupported for automation.
- Reconcile the supported export against a supported GHL CSV/report detail export for the exact snapshot week by call ID, `dateAdded`, direction, user, status/disposition, and timezone. If no supported detail export can establish parity, retain the exact-week snapshot and label other periods unavailable/incomplete rather than showing unvalidated numbers. Ask GHL whether the privately tested Call Reporting data can be exposed through a documented API/scope.
- The Marketplace webhook remains optional as a forward-looking event ledger; it cannot provide history. No subscription was configured, and no call/report records were changed. Next, ask GHL for documented API access to the proven Call Reporting data or obtain supported report exports; do not automate the private browser route.

## 2026-09-29 read-only runtime audit continuation

- Public V1 checks passed for `range=7d`, `range=30d`, and `range=90d`: each returned HTTP 200 with non-empty JSON, and the four V1 health rows were `ready`. The checked window values were 7d `2026-09-22`–`2026-09-28` (MQL 1, new contacts 71, SQL 49, opportunities 107), 30d `2026-08-30`–`2026-09-28` (MQL 6, new contacts 676, SQL 786, opportunities 1,662), and 90d `2026-07-01`–`2026-09-28` (MQL 136, new contacts 12,940, SQL 2,684, opportunities 8,533). These remain smoke observations, not direct GHL sign-off.
- The exact snapshot request `from=2026-09-20&to=2026-09-26` still returned the accepted native-report basis: 1,356 outbound attempts, Marc 1,006, Jason 350, with `callInputs=ready`. A 30-day request returned 793 supported-export call facts and explicitly labeled `callInputs=incomplete`; this source boundary remains correct.
- The live raw-ingest audit found Sales (`aYT5oHcgmBALzHy5`), Appointments (`yWZVSqEcjTbMT3kG`), Calls (`SqNQ0BYaTdcqyt1l`), Attribution Bridge (`Y0TU7Il71JswxOBp`), and Report QA (`M5mXcDTFSko6EdHb`) succeeding on their latest checked runs. Leads ingest (`osIJOgBmWITF5Yuv`) is currently failing on five consecutive scheduled runs in `Fetch + Normalize Leads` with an n8n task-runner disconnect after about 114 seconds; no GHL HTTP status or data-contract error was surfaced. Do not mark contact-source freshness green or publish headline reconciliation until this is repaired and a successful run is verified.
- No production workflow definition, CRM record, outbound send, Marketplace subscription, or report deployment was changed during this audit. The Leads runner issue requires an explicitly approved production repair before modification.

## 2026-09-29 call-summary parity repair deployed

- The isolated V1 frontend now exposes native-report status columns in the Team call summary and per-SDR table: Attempted, Answered, Busy, No answer, and Failed.
- For the referenced native report window `2026-09-20`–`2026-09-26`, the deployed page now renders the verified per-SDR values exactly: Marc `1,006 / 802 / 105 / 59 / 40`; Jason `350 / 285 / 19 / 35 / 11` in that column order. The team totals are `1,356 / 1,087 / 175 / 94` with no unknown rows.
- The frontend uses the verified dated snapshot only for that exact window. For other windows, it does not reinterpret supported-export `completed` rows as native `answered` rows; unavailable status detail remains visible instead.
- Deployment verification passed: V1 page HTTP 200, live page contains the new status headers and snapshot mapping, browser-rendered values match the native report, and the original `/embed/executive/` page still contains build `2026-08-17-v27-social-mql`.

## 2026-09-29 Monday-week correction

- The operator clarified that the accepted reporting week is Monday–Sunday `2026-09-21`–`2026-09-27`, despite the supplied screenshots visibly displaying `Sep 20, 2026 -> Sep 26, 2026`. The V1 snapshot override now follows the operator's Monday-week definition and uses the supplied verified native totals: Marc `1,006` and Jason `350`, with Marc `802/105/59/40` and Jason `285/19/35/11` for answered/busy/no-answer/failed.
- The supported API still returns the incomplete `185` Marc / `26` Jason rows for that same date query. V1 no longer treats those rows as authoritative for the accepted weekly snapshot; it applies the verified native-report snapshot and labels the date-label discrepancy in the source note.
- The SDR table now falls back to the native call rows when the broader Executive Summary `sdrPerformance` array is empty, preventing the call rows from disappearing.
- The isolated V1 deployment was rebuilt and live HTML verification confirmed the Monday-week override, fallback renderer, and status columns. The legacy report remains unchanged.

## 2026-09-29 Sunday-week correction — supersedes Monday-week note

- The operator confirmed that GHL's native report week is Sunday–Saturday and will reset GHL's calendar preference accordingly. V1 now follows the native selected window `2026-09-20`–`2026-09-26` for the verified snapshot.
- The V1 call summary and per-SDR rows use the native totals: Marc `1,006 / 802 / 105 / 59 / 40`; Jason `350 / 285 / 19 / 35 / 11`; team `1,356 / 1,087 / 175 / 94 / 51` in attempted / answered / busy / no-answer / failed order.
- The earlier Monday-week override is superseded. The private browser endpoint remains read-only diagnostic evidence; no unattended private-route integration was added.
- The V1 base URL now defaults to the verified Sunday–Saturday window `2026-09-20`–`2026-09-26`; previously, opening the base URL without query parameters used a 30-day range and exposed the unrelated `206/125` SDR rows.
- Team call KPIs now show week-over-week percentage movement against the prior native GHL comparison week: attempted `+46.9%`, answered `+56.9%`, no-answer `0.0%`, busy `+173.4%`, and failed `-29.2%`.
- Each native per-SDR call cell now also shows its week-over-week percentage: Marc attempted `+73.1%`, answered `+82.7%`, busy `+162.5%`, no-answer `+11.3%`, failed `-18.4%`; Jason attempted `+2.3%`, answered `+12.2%`, busy `-20.8%`, no-answer `-14.6%`, failed `-52.2%`.

## EOS closeout — 2026-09-29

- Objective completed: V1 now defaults to the native Sunday–Saturday window `2026-09-20`–`2026-09-26`, displays the verified Marc/Jason call totals and status breakdowns, and shows current-versus-prior-week percentages for both Team KPIs and each SDR call cell.
- Live browser verification passed on the base V1 URL: period `2026-09-20 → 2026-09-26`; Marc `1,006 / 802 / 105 / 59 / 40`; Jason `350 / 285 / 19 / 35 / 11`; Team KPIs show `+46.9%`, `+56.9%`, `0.0%`, `+173.4%`, and `-29.2%` for attempted, answered, no-answer, busy, and failed respectively.
- The same live verification shows the previously blank output columns: Marc `0` booked, `3` SQLs, `0` MQL→SQL; Jason `0` booked, `1` SQL, `1` MQL→SQL. The Hermes runbook explicitly requires gathering these values on every weekly run.
- The isolated V1 frontend was redeployed through `scripts/deploy/deploy_report_vps_local.py`; the container verification reported build `2026-08-17-v27-social-mql`. The legacy `/embed/executive/` path was not changed.
- The browser-native report route remains private/unsupported. The documented Conversations export does not reconcile to native widget totals, so future weekly refreshes remain an approved-source blocker; do not automate private browser bearer material or publish unverified export counts.
- Worktree remains intentionally dirty. Relevant changed artifacts are `reports/embed/executive-v1/index.html`, `executive_report_v1_plan.md`, `Project Status and Next Steps.md`, and the dated session handoff; existing unrelated/user changes and supplied report images remain unstaged. No commit or push was made.

Next session: verify the operator's GHL Sunday calendar preference, obtain documented Call Reporting access or supported weekly exports, then replace the one-period native snapshot only after exact status/call-ID parity is proven. Keep outbound sends, CRM mutations, Marketplace subscription, and private-route automation approval-gated.

Hermes automation handoff: [`docs/runbooks/executive-report-v1-weekly-hermes-refresh.md`](docs/runbooks/executive-report-v1-weekly-hermes-refresh.md). The intended schedule is Monday 03:00 `America/Los_Angeles`, reading the prior Sunday–Saturday native GHL window with fail-closed validation.

## 2026-09-29 EOS — unmatched response review UI refinement

- The isolated V1 frontend card is now titled **Unmatched Inbound Response Review** and only renders `unmatched` detail rows.
- The detail table contains Contact, Channel, Inbound, and Owner. The Status column was removed because every displayed row is unmatched.
- The card remains full width beneath Speed-to-lead & follow-up using `.response-review{grid-column:1 / -1}`.
- Deployment used `scripts/deploy/deploy_report_vps_local.py`. Live verification returned HTTP 200 and confirmed the new title, absent Status header/cell, and full-width CSS rule. The legacy `/embed/executive/` report was not changed.
- No CRM, workflow, API, outbound-send, or other production data mutation was performed. No commit or push was made.

Next session: preserve the existing response-SLA approval boundary. SLA targets, automatic tasks, CRM note creation, and outbound follow-up remain unapproved.

## 2026-09-30 EOS — V1 renderer and call-snapshot bug repair

- Audited the isolated V1 frontend and confirmed the active load path was calling a renderer that omitted `feedback()`. A later duplicate global renderer included `feedback()` but was never invoked. The active renderer now calls the feedback renderer, so funnel, closed-source, weekly-movement, vertical, and retargeting sections follow one render path.
- Repaired the call-summary logic in `reports/embed/executive-v1/index.html`: the accepted native snapshot is now recognized only for Sunday–Saturday `2026-09-20`–`2026-09-26`; the stale Monday-window override and recurring DOM patch scripts are disabled; the call-source note remains visible and states that other windows are unavailable until supported parity is proven.
- Health rendering now selects the freshest row by `last_attempt_at`/`last_success_at`/`updated_at` per source and marks rows with `last_error` as unhealthy, preventing an older `ready` row from masking a newer failure.
- Local inline JavaScript syntax validation passed for all script blocks, `git diff --check` passed, and the report was deployed with `scripts/deploy/deploy_report_vps_local.py`. Container verification succeeded with image `v3ud1lum1svamymuor21upog:social-mql-20260817`; the legacy `/embed/executive/` path was not changed.
- Live read-only verification passed: V1 page HTTP 200; active feedback renderer present; two legacy call-override blocks disabled; freshness-aware health logic present; Sunday snapshot condition and source note present. Facts API exact-window check returned `2026-09-20`–`2026-09-26`, four health rows, and ten response-SLA detail rows.
- The V1 Facts API still does not return `funnel`, `closedBySource`, `weeklyLeadFlow`, `verticalPerformance`, or `retargeting` fields. No fabricated values were added. The documented workflow ID `oxYDg6XnRBKhl1Xd` was not available through the connected n8n MCP, and the fallback REST lookup returned 404; no n8n workflow was changed.
- Worktree remains intentionally dirty with pre-existing/user changes and the current V1 frontend changes. No commit or push was made.

Next session: obtain the current V1 Facts workflow ID or enable the correct n8n MCP access, read the workflow before editing, then add and verify the missing feedback fields through the approved materializer/API contract. Keep the current read-only report boundary: no outbound sends, CRM mutations, Marketplace subscription, private call-report automation, SLA targets, automatic tasks, or CRM note creation without separate approval.

## 2026-09-30 EOS — LiveTransparent n8n audit after instance correction

- The LiveTransparent n8n instance is `https://automations.livetransparent.com`; use only the repository key `N8N_API_KEY_LT` for this project. The earlier Katwill-host/key test was against the wrong company and is superseded; do not use it for LiveTransparent work.
- Read-only REST access using `N8N_API_KEY_LT` succeeded. Workflow `LT - Executive Report V1 Facts API` (`oxYDg6XnRBKhl1Xd`) is active at version `4039aea2-787a-420b-81ef-829b076d5cef` with five nodes: webhook, query builder, Postgres query, response shaper, and webhook response.
- Recent execution audit returned the latest ten executions as successful. Latest checked execution `1066451` completed all five nodes successfully. Its shaped response contains `window`, `v1Health`, `callTotals`, `callsBySdr`, `responseSla`, `completeness`, `meetingSummary`, `socialStatistics`, `voicemailSummary`, `contactMechanisms`, `appointmentDetails`, `responseSlaDetails`, and `authoritativeGhlCounts`.
- Live V1 page verification passed: HTTP 200; active feedback renderer, Sunday–Saturday call snapshot condition, disabled legacy override blocks, freshness-aware health logic, and call-source note are present. The legacy `/embed/executive/` path retains its expected legacy build marker.
- The remaining accepted blocker is the Facts API contract: the active workflow still does not return `funnel`, `closedBySource`, `weeklyLeadFlow`, `verticalPerformance`, or `retargeting`. No workflow or production data was changed during this audit. The connected n8n MCP still returned Unauthorized, so REST was used read-only.

Next session: extend the active Facts workflow/API contract with the missing feedback fields only after reading the full workflow and confirming the approved SQL/source definitions. Re-run the exact-window and range checks, then verify the deployed V1 sections. Keep all outbound, CRM-mutation, Marketplace, private-route, SLA-target, automatic-task, and CRM-note approval gates in force.

## 2026-09-30 reporting-only feedback extension

- The active V1 Facts API was extended without changing GHL CRM workflows or CRM records. Published version: `64881005-f213-47c4-acfb-07e1b1df8b13` during the verified safe extension; the later weekly/contact-source refinement is active at `ae414181-adc4-4bbf-8f81-2facef5c3c39`.
- The response now includes `funnel`, `closedBySource`, `weeklyLeadFlow`, `verticalPerformance`, `retargeting`, and `contactAcquisition`. The query reads reporting/raw snapshot tables only and keeps `send_authorized=false` for retargeting.
- Successful execution `1067446` returned non-empty JSON with funnel facts, two weekly movement rows, an explicit Unknown/Unattributed closed-source row, and separate `linkedin_backfill` acquisition data. The exact live HTTP response for the selected window also returned the same fields.
- The V1 frontend now prefers `contactAcquisition`, so LinkedIn backfill is shown separately from ordinary contact mechanisms. The existing combined Meetings & outcomes card and MQL→SQL display parity remain isolated to V1; the legacy report path was not changed.
- Deployment verification: V1 HTTP 200/non-empty, legacy `/embed/executive/` HTTP 200 with the expected `2026-08-17-v27-social-mql` marker, inline JavaScript syntax checks passed, and `git diff --check` passed.
- Data caveats: the selected window currently has no closed won/lost records, no vertical rows, and newsletter sends are unavailable even though click events exist; these remain visibly unavailable rather than being converted into trustworthy zeroes. Browser MCP was unavailable in this environment, so responsive verification used static/HTTP checks rather than a live browser screenshot.

## 2026-09-30 EOS — reporting-only V1 closeout

- Active LiveTransparent Facts API: `oxYDg6XnRBKhl1Xd`, version `ae414181-adc4-4bbf-8f81-2facef5c3c39`, active and published. Read-only audit on 2026-09-30 showed latest execution `1069228` successful; recent executions `1069126`, `1069124`, `1067446`, and `1067443` were also successful.
- The deployed V1 page and legacy page were rechecked: V1 returned HTTP 200/non-empty and the legacy `/embed/executive/` path retained its expected build marker. No CRM workflow, CRM record, outbound send, Marketplace subscription, or private call-report automation was changed during the closeout.
- Completed reporting-only scope: Facts API fields, reporting CTEs, V1 frontend wiring, combined Meetings/outcomes presentation, MQL→SQL parity display, weekly movement, contact-acquisition/backfill split, stale-health handling, deployment, syntax validation, and API execution verification.
- Not accepted as complete: exact GHL ID-level reconciliation for all ranges, supported Call Reporting API/export parity, manual calendar-preference verification, browser screenshots/accessibility QA (browser MCP unavailable), durable reporting retry/reconciliation, and the read-only LinkedIn historical candidate report.
- Next session order: (1) reconcile new funnel/weekly/closed-source/vertical values by exact IDs; (2) resolve supported call-reporting access and verify Sunday–Saturday preference; (3) run browser desktop/mobile/accessibility QA; (4) build the reporting-only retry/reconciliation path; (5) prepare the deduplicated LinkedIn candidate report.
- Safety gates remain: no SLA targets, automatic tasks, CRM note creation, outbound follow-up, CRM mutations, outbound sends, Marketplace subscription, or private-route automation without separate approval.
