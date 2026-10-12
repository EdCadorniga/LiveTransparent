# Vertical campaign enrollment and send reconciliation — 2026-10-13

## EOS — verified result and first next action

**Re-enrollment is not needed for the audited cohort.** Fully paginated native histories contain **2,263 enrollment records / 1,819 distinct contacts / 1,816 active contacts**. Every active contact has `executeOn` and a resolvable next action; remaining graph paths contain email and SMS actions. Every enrolled contact has a valid **campaign-specific sender email**. The only three inactive-only contacts are Cannabis records with the explicit DAN Dispensary exclusion tag. No contact/tag/sender/enrollment write, provider send, workflow save/publication, report deployment, or event replay occurred in this continuation.

**First next action: diagnose and correct the existing SMS send boundary, not re-enroll contacts.** All **911** past-week vertical SMS webhook actions reviewed are **477 application-level unauthorized responses + 434 timeouts**, not 911 sends. Compare the GHL `x-lt-simpletexting-key` headers with the canonical n8n-lt accepted Config values **in memory without exposing secrets**. The exact mismatch/root cause is not yet established. Reconcile the timeout executions/provider outcomes before considering any replay. Future Crypto SMS is queued Oct 14 around **09:03–09:08 Pacific**, while the effective canonical SMS guard is weekdays **10:00–17:00 Pacific**; review/align scheduling and rejection/retry behavior before calling the SMS path ready.

Ed's latest clarification: **do not re-enroll duplicate historical re-entries**. Priority is to ensure current contacts remain lined up for actual email/SMS delivery and fix Executive Report V1's missing vertical send coverage. Conditional recovery approval does not authorize bulk tag reapplication, bypassing exclusions, or blindly resending timed-out/failed touches.

### Native enrollment and sender readback

| Vertical | Total records | Distinct contacts | Active | Finished records | Missing/invalid sender |
|---|---:|---:|---:|---:|---:|
| Alcohol | 338 | 169 | 169 | 169 | 0 |
| Cannabis Brands | 88 | 44 | 41 | 47 | 0 |
| Mushroom | 348 | 117 | 117 | 231 | 0 |
| Cannabis Dispensaries | 121 | 121 | 121 | 0 | 0 |
| Crypto | 292 | 292 | 292 | 0 | 0 |
| Gambling | 246 | 246 | 246 | 0 | 0 |
| Peptides | 129 | 129 | 129 | 0 | 0 |
| Nicotine | 701 | 701 | 701 | 0 | 0 |

- Alcohol and Mushroom finished entries all have a later/current active enrollment on the same contact; they are not a cohort awaiting recovery.
- Cannabis inactive-only IDs: `ryuw8ioL34Y27ZcUH51T`, `AC4gmoqrY029z3iuW1ih`, `9DH1yEJDRxoLlN3lZMaj`. All have `enrollment queue - dan - dispensaries`, matching the live Cannabis eligibility gate exclusion; all have valid sender and entry tag. Their two entries each finished in about 1–2 seconds at sequence 1. Preserve the exclusion; no re-enrollment.
- One Alcohol contact lacks the entry tag but has an active enrollment. An entry tag is not required to be reapplied for an existing active entry. Its ID is in the local contact audit; do not retag just to normalize counts.
- Sender audit: 1,819/1,819 GHL contacts resolved live, all valid `.com/.co/.agency/.org` values in the correct dedicated field. The shared `marketing_sender_email` is not the routing field. No assignment repair was required.
- Native GHL histories were fully cursor-paginated with deduplication by enrollment ID + SID. The API's next-page result includes the reference record; deduplication is necessary. Earlier cursor-probe failure was resolved; only the completed captures support these totals.
- Contact search was grounded in known enrollment IDs, not lagging tag search. Verified `POST /contacts/search`, `Version:2021-07-28`, `filters:[{field:'id',operator:'eq',value:[...IDs]}]`, pageLimit 100. The unsupported `in` operator probe returned 422 and is not an accepted query; the corrected equality-array probe matched all five IDs and the full scoped read resolved all 1,819.

### Scheduling readback (snapshot, not a delivery guarantee)

All eight workflows are Published, Contact timezone, weekdays 09:00–17:00, no scheduled pause dates. All 96 SMS webhook nodes retain `dryRun=false`. All active entries are `wait_time`; no missing `executeOn`, unresolved frontier, or unresolved downstream branch was found.

| Vertical | Published version | Next queued action | Next queued time in Pacific | Minimum remaining email / SMS actions per active path |
|---|---:|---|---|---:|
| Alcohol | 40 | Voicemail | Oct 14, 09:03–09:08 | 3 / 2 |
| Cannabis Brands | 75 | Voicemail | Oct 14, 09:01–09:08 | 3 / 2 |
| Mushroom | 23 | Email 2 | Oct 13, 09:04–09:05 | 4 / 2 |
| Cannabis Dispensaries | 10 | Email 2 | Oct 13, 13:22 | 4 / 2 |
| Crypto | 50 | SMS 1 | Oct 14, 09:03–09:08 | 4 / 3 |
| Gambling | 13 | Email 2 | Oct 13, 13:24–13:25 | 4 / 2 |
| Peptides | 19 | Email 2 | Oct 13, 09:46 | 4 / 2 |
| Nicotine | 42 | Voicemail | Oct 14, 09:03–09:08 | 3 / 2 |

These are captured queue times, not a promise that every later action has its own independent scheduled job already created. Graph traversal confirms remaining connected actions; verify current queue times on resume. Contact phone availability, current suppression, sender transport, provider outcomes and the canonical SMS auth/business-hours boundary still govern actual sends.

### Past-week execution evidence: Oct 4–10 Pacific

Fully paginated native logs were read for all eight workflows and email/webhook action types, using exact UTC bounds `2026-10-04T07:00:00.000Z` through `2026-10-11T06:59:59.999Z`.

| Vertical | Email actions | Email queued successfully | Email errors | Email skipped | SMS webhook actions | Unauthorized responses | Timeouts |
|---|---:|---:|---:|---:|---:|---:|---:|
| Alcohol | 169 | 169 | 0 | 0 | 169 | 169 | 0 |
| Cannabis Brands | 41 | 39 | 2 | 0 | 41 | 41 | 0 |
| Mushroom | 117 | 117 | 0 | 0 | 0 | 0 | 0 |
| Cannabis Dispensaries | 121 | 116 | 3 | 2 | 0 | 0 | 0 |
| Crypto | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Gambling | 246 | 244 | 2 | 0 | 0 | 0 | 0 |
| Peptides | 129 | 128 | 1 | 0 | 0 | 0 | 0 |
| Nicotine | 701 | 688 | 13 | 0 | 701 | 267 | 434 |
| **Total** | **1,524** | **1,501** | **21** | **2** | **911** | **477** | **434** |

- Email success log bodies say **`Email queued successfully.`** The 1,501 are accepted/queued native workflow actions, not independently verified delivered emails. Errors: **20 `CONVERSATIONS_MSG_INVALID_EMAIL` + 1 `CONVERSATIONS_MSG_UNSUBSCRIBED_EMAIL`** (Dispensaries). The two skipped reasons remain unclassified. Do not bypass invalid-email or unsubscribe state or re-enroll for these failures.
- GHL webhook `success` is misleading here: for 477 actions its message is HTTP 200 with application body **`{"ok":false,"error":"unauthorized"}`**. The 434 Nicotine failures explicitly report a 60-second webhook timeout. A timeout remains uncertain until matching n8n/provider evidence establishes the outcome. None of these log statuses is proof of a delivered SMS.
- A supported GHL **Email message export** completed separately for the same week: **1,560 messages**, **1,552 outbound `sent`**, **1,538 messages with `source=workflow`** (source count is not yet a vertical-only or direction-qualified denominator). Native export has no explicit workflowId in the captured rows. **Exact-ID/campaign reconciliation with the 1,501 queued actions is pending.** A sample `GET /conversations/messages/{queuedMessageId}` returned 400 `Message does not exist`; do not assume queued IDs map directly to public message IDs without testing the export.
- V1 reporting has **not yet been updated with this new evidence**. Existing `Email_Events`/SMS ledgers are incomplete for these native vertical actions. Ed's concern about missing past-week email activity is supported; do not manufacture SMS sends from the 911 webhooks or replace unavailable delivery with queue counts.

### Canonical n8n-lt readback

| Workflow | ID | Active/published version |
|---|---|---|
| SimpleTexting SMS Send | `Q3Ivnwe4z2Y3cD7A` | `b69a183e-273a-43f9-b06d-b2bd1575543b` |
| SMS Idempotent Send | `gwaEpWDpTIwsafi8` | `52eefd2a-70be-41c9-a60a-2fce0f037929` |
| V1 Facts | `oxYDg6XnRBKhl1Xd` | `e8c3dd1a-1000-4162-b784-93ad161d0e06` |
| Booking-click intake | `1diZyFmTqWQUEny3` | `548c2d96-aec1-4dcd-8e22-cbb055ba5c99` |

All four were re-read active/not archived with matching active/draft versions. No workflow was executed manually for this audit. The SMS auth header name is `x-lt-simpletexting-key`. Config has stale `businessTimezone=America/New_York`, but `Resolve Sender + SMS Templates` sets the effective item timezone to **America/Los_Angeles**; the validator uses the configured 10–17 hours and weekday set. Verify this data path before changing timing; do not base a fix only on the Config timezone label.

EOS execution readback: Facts 1132921/1132920 succeeded; canonical SMS latest retained 1131313/1131311 succeeded as n8n executions, which is not proof of a provider send. Click intake still shows the two parser failures. No `new`/`running`/`waiting` rows were returned in each checked workflow's latest20; idempotent history returned no records. This bounded read/retention result is not proof that the idempotent workflow has never executed.

The previous booking-click blocker remains: duplicate `const cfgValues` in Process Click, failures 1132673/1132676. The booking-link clicker → GHL query/filter TODO remains unimplemented. New SMS delivery evidence is now the first operational priority.

### Evidence, review and worktree

Local-only, Git-ignored sanitized artifacts:

- `local-scripts/vertical-enrollment-audit-20261013.json` — enrollment rows and safe graph fields; no webhook auth header values.
- `local-scripts/vertical-campaign-contact-audit-20261013.json` — sender/tag/eligibility booleans and exact contact IDs.
- `local-scripts/vertical-scheduling-summary-20261013.json` and `vertical-future-schedule-audit-20261013.json` — graph/queue timing summaries.
- `local-scripts/vertical-campaign-log-audit-20261013.json` — sanitized exact native action IDs, queue message IDs, outcomes/timestamps.
- `local-scripts/vertical-email-exceptions-20261013.json` — email error codes and unresolved skipped rows.
- `local-scripts/vertical-email-message-export-20261013.json` — supported message export with status/identity/date/source fields, no bodies/auth values.

Versioned read-only helpers added: `scripts/audit_vertical_campaign_contacts.py` (scoped ID sender audit) and `scripts/audit_vertical_campaign_messages.py` (supported export; its sample get-message probe failed as noted). Both passed `py_compile`. Authenticated browser access is working through Live Transparent launchpad → Automation → cross-origin workflow-builder iframe. The outer route's 404 is not a login failure. Native histories/logs were captured through observed UI request paths; do not automate private widget routes into production without a supported access contract.

Branch remains `codex/social-outreach-sync`, HEAD `5613544`, dirty/uncommitted. Preserve pre-existing CSV/LinkedIn cleanup artifacts and previous V1 changes. No production writes/deployments/sends/tests occurred in this continuation or EOS. The native log/export reads are accepted; failed filter/get-message probes are not accepted tests. Browser auth remains in memory only; the next session must reacquire it rather than write tokens to disk.

### Ordered next-session TODOs

1. Re-read the current eight campaign queues and the canonical SMS sender/idempotent boundary. Diagnose unauthorized responses by comparing accepted header names/values and compatibility rules **without printing secrets**. Determine whether the mismatch is on all 96 GHL nodes, the receiver, or its legacy compatibility path. Plan the smallest correction; obtain scoped approval for live boundary/workflow changes and verify saved/published state afterward.
2. Reconcile all 434 timed-out Nicotine webhook events by exact contact/action timestamp against n8n executions, idempotency/provider IDs and delivery callbacks. Never replay uncertain sends. Separately inspect the 477 unauthorized results as confirmed rejections at the application boundary.
3. Align future SMS scheduling with the effective Pacific 10–17 guard (Crypto's next queued SMS is before 10). Confirm phone availability and suppression, choose an approved scheduling/retry treatment, preserve current enrollments and completed touches, and verify natural send/provider delivery. Do not force actions or bulk re-enroll.
4. Join the 1,501 successful native email queue events to the supported GHL Email export/native campaign evidence using stable message/provider/contact/time/step identities. Explain unmatched/deleted IDs; obtain only supported native delivery/open/click evidence. Retain 21 errors and 2 skips separately. Implement report-only source capture/period snapshots or ingestion after agreement on the source contract; prevent overlap/double-counting with legacy/Newsletter sources. Update V1 Band 3 and supported vertical metrics with explicit queue/send/delivery bases, and validate both weeks.
5. Investigate the 20 invalid-email, one unsubscribe and two skipped actions as contact/channel exceptions. Respect suppression; no automatic re-enrollment/resend. Scope any genuine field correction/retry with Ed.
6. Resume booking-click Process Click parse repair (duplicate cfgValues), scoped publication approval, and approved internal click verification. Then implement Ed's booking-link clicker → supported GHL query/filter drill-down with exact ledger IDs/date-window reconciliation and no implicit tags.
7. Update the authoritative V1 status table, verify desktop/mobile and delayed-source rendering after approved changes, preserve legacy report SHA, and record remaining performance/source gaps. No commit or Repomix refresh unless Ed requests it.

### Copy-ready next LLM prompt

> Continue LiveTransparent from `docs/sessions/2026-10-13-vertical-enrollment-send-reconciliation.md` (EOS opening section) and `executive_report_v1_plan.md`. Use only n8n-lt REST via `.env` N8N_LT_API_KEY; never the n8n-katwill connectors. Preserve the dirty worktree and accepted V1 build `2026-10-13-v1-vertical-facts`; no commit/packlive unless requested.
>
> Ed's priority is ensuring the existing vertical cohorts remain scheduled for real email/SMS and fixing missing past-week V1 send coverage. Full native histories: 2,263 enrollment records / 1,819 contacts / 1,816 active, all active executeOn present and remaining email/SMS paths connected. All 1,819 have valid dedicated sender fields. Alcohol/Mushroom excess finished rows are historical duplicate entries, not recovery candidates. Three inactive Cannabis contacts have the explicit DAN Dispensary exclusion; do not re-enroll. One Alcohol contact lacks the entry tag but is active; do not retag. Ed explicitly said duplicate re-entries need no re-enrollment.
>
> FIRST fix the SMS delivery boundary after read-only diagnosis/scoped approval. Last week Oct 4–10 Pacific had 911 vertical webhook actions: 477 returned HTTP 200 application `ok:false,error:unauthorized` (Alcohol169, Cannabis41, Nicotine267); 434 Nicotine calls timed out at60s. None proves SMS delivery. Compare GHL x-lt-simpletexting-key headers against canonical sender Q3Ivnwe4z2Y3cD7A and idempotent gwaEpWDpTIwsafi8 in memory; no credential values in output. Reconcile timeouts against n8n/provider/idempotency evidence before any replay. All96 GHL payloads are dryRun=false, but that does not fix authorization. Crypto's next SMS is Oct14 09:03–09:08 Pacific; effective SMS guard is weekdays10–17 Pacific despite stale NY Config label. Review scheduling/rejection/retry alignment without forcing steps or re-enrolling contacts.
>
> NEXT reconcile reporting: native vertical email logs show 1,524 actions = 1,501 queued successfully + 21 errors + 2 skipped. Errors are20 invalid email +1 unsubscribed. Supported Email export has1,560 messages /1,552 outbound sent /1,538 source=workflow, but exact join to the queued vertical events is unfinished; don't call queued emails delivered or assign every workflow-source message to these campaigns. A sample queued message ID returned400 on get-message. Sanitized exact-ID enrollment/contact/log/export artifacts are in local-scripts/*20261013.json; helper scripts audit_vertical_campaign_contacts.py and audit_vertical_campaign_messages.py are read-only. Complete source/event identity and overlap reconciliation, then implement reporting-only capture/snapshots with clear bases and verify V1 both weeks. No report deployment occurred in this continuation.
>
> After SMS/reporting integrity, resume booking-click intake1diZyFmTqWQUEny3 duplicate cfgValues parse repair, approved internal test, and Ed's booking-link clicker→supported GHL query/filter link. Facts workflow oxYDg6XnRBKhl1Xd remains healthy at e8c3dd1a-1000-4162-b784-93ad161d0e06. Keep current27 SQLs without booking evidence; no fabrication, sends, contact/tag writes, credential exposure, uncontrolled event replay, campaign activation or workflow publication without scoped authorization. Update docs/status after each verified step.

## Initial request checkpoint (superseded by EOS results above)

## Ed's request and supplied screenshot

Continue V1 reporting/click work; investigate whether contacts left vertical campaigns and re-enroll those who genuinely need recovery. Reconcile the expectation of more vertical sends in the past completed report week against native delivery evidence.

Screenshot transcription (user-supplied evidence, not a fresh API/UI readback):

| Vertical workflow | Status | Total enrolled | Active enrolled |
|---|---|---:|---:|
| Alcohol | Published | 338 | 169 |
| Cannabis Brands | Published | 88 | 41 |
| Cannabis Dispensaries | Published | 121 | 121 |
| Crypto | Published | 292 | 292 |
| Gambling | Published | 246 | 246 |
| Mushroom | Published | 348 | 117 |

The Nicotine row is cut off; no count is inferred. Visible workflow last-updated dates are Oct 9; screenshot capture time and UI timezone are not independently established.

**Interpretation boundary:** Total enrolled minus Active enrolled is not a count of unique removed contacts. Totals may contain repeated enrollments, finished sequences, eligibility/sender-router exits, reply/booked removals, or other legitimate stops. Enrollment is not send/delivery evidence. Raw differences (169 Alcohol, 47 Cannabis, 231 Mushroom) require contact/enrollment-ID reconciliation before recovery.

## Authorization and acceptance

- Ed conditionally authorized re-enrollment **if the investigation establishes that it is appropriate**. Recover only identified eligible contacts with no active enrollment and a supported interrupted/premature exit. Preserve suppressed, replied, booked, completed, ineligible, duplicate, and already-active contacts. Check sender field and entry requirements first; don't bulk remove/re-add tags based on the aggregate difference.
- Re-enrollment can resume live outreach. Record IDs, original path/exit, previous touches, active-entry check, eligibility, intended resume/re-entry behavior and actual result. Do not resend completed touches merely to increase report counts.
- Past-week send reconciliation uses **2026-10-04–2026-10-10 America/Los_Angeles** and the equal-length prior week unless Ed specifies otherwise. Obtain native workflow email/message events and SMS provider IDs/outcomes; keep attempted, accepted/sent, delivered, failed, skipped and enrollment counts separate.
- Preserve existing V1 counts and Unclassified. Add only reconciled historical source events with their original timestamps and stable identities; never fabricate sends from enrolled counts or expected cadence.

## Investigation status

- Started authenticated browser check through Live Transparent launchpad; outer route returned 404 initially, so inspect the loaded shell before treating it as unavailable.
- Screenshot evidence recorded; no re-enrollment, tag/contact write, or report data mutation performed at this checkpoint.
- Continue the remaining booking-click parser repair and GHL clicker drill-down from `2026-10-13-executive-v1-facts-vertical-eos.md`; prioritize enrollment/send evidence now per Ed's new request.
