# n8n Stale Execution Recovery Plan

## Incident Snapshot

Observed after the August 5, 2026 PostgreSQL/n8n outage and redeployment:

- n8n version: `2.33.3`
- Execution mode: regular mode; no `EXECUTIONS_MODE`, `QUEUE_BULL_*`, or n8n worker configuration was present
- PostgreSQL: healthy with 1 active connection out of 100
- `new` executions: 6,946
- `crashed` executions: 102
- `error` executions: 38
- Oldest `new` execution: 2026-07-27

The `new` executions are displayed as `Queued` in the n8n UI. They are stale scheduled-trigger records from the outage and are not evidence that an n8n Queue Mode worker is missing.

## Largest Backlog Sources

| Workflow | Queued executions |
|----------|-------------------:|
| LT - SimpleTexting Campaign Step Runner | 1,915 |
| LT - SimpleTexting Campaign Phone Backfill | 1,905 |
| LT - Partnership Reply Poller | 788 |
| LT - Voice Queue Vapi Intake Poller | 396 |
| LT - LinkedIn Reply Backfill (Unipile) | 386 |
| LT - Voice Agent V1 Outbound Dialer (Vapi) | 313 |
| LT - Campaign Contact Classifier | 261 |

## Cleanup Procedure

1. Capture a read-only snapshot of execution counts by status, workflow, and trigger mode.
2. Temporarily deactivate the highest-volume scheduled workflows, especially campaign runners, backfills, pollers, dialers, and the campaign classifier.
3. Separate scheduled/trigger executions from webhook executions. Preserve recent webhook executions because they may contain real inbound events.
4. Delete stale scheduled `new` executions through the n8n UI or supported API, in batches. Start with records created before the August 5 outage window.
5. Never delete rows directly from PostgreSQL. n8n must remove execution data through its own API so related execution records remain consistent.
6. After each batch, verify that the `new` count decreases and does not immediately grow again.
7. Re-enable one low-risk scheduled workflow and verify a current execution starts and finishes normally.
8. Re-enable remaining workflows gradually, with outbound senders and dialers last. Do not replay every missed schedule tick.

## Cleanup Execution

Completed during the August 5, 2026 recovery:

- Restarted the n8n container after confirming its PostgreSQL connection pool was still timing out while PostgreSQL itself was healthy.
- Unpublished the nine high-volume scheduled workflows listed in the incident snapshot.
- Deleted 6,964 stale `new` executions with `mode = 'trigger'` through the supported n8n execution API.
- Preserved all webhook executions; no webhook execution was deleted.
- Verified the current `new` execution count is zero.
- Left `crashed` and `error` execution history intact for follow-up diagnosis.

The remaining activation and concurrency steps are intentionally separate from deletion so the schedules do not immediately recreate the backlog.

## Gradual Reactivation Plan

Do not reactivate all nine workflows together. After the Coolify redeploy, verify that `N8N_CONCURRENCY=10` is active in the container, `/healthz/readiness` is HTTP 200, PostgreSQL is healthy, and the `new` execution count remains zero for at least 10 minutes.

Reactivate one workflow at a time. Wait at least two scheduled intervals, or 15 minutes when the interval is shorter, before adding the next workflow. Capture execution status, runtime, database connections, API errors, and new-execution count after every step.

### Tier 1: Low-Risk State and Ownership Work

1. `LT - Sales Outreach Jason Marc No-Owner Allocator` (`eeksgD0fbGHUqh4r`): reactivate first. Keep the 30-minute schedule initially. It is idempotent and only selects open Qualified opportunities with blank native owners. Consider moving to 60 minutes after confirming the unowned backlog is drained.
2. `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`): reactivate after the allocator is stable. Keep the 15-minute schedule while validating classification, then consider 30 minutes once the Warm-New stage webhook input is added. Keep the 10 Brand + 10 Dispensary cap and add a fast empty-result exit.

### Tier 2: Reply and Suppression State

3. `LT - Partnership Reply Poller` (`0SQ7tTk03okegp9V`): reactivate after Tier 1. Increase the cadence from 5 minutes to 15 minutes initially. Query only active `partner_email_queued` contacts, keep the supported `GET /conversations/search` path, and preserve fail-closed reply handling.
4. `LT - LinkedIn Reply Backfill (Unipile)` (`QfJ2EZcc7lZwNgxj`): reactivate next. Increase the cadence from 10 minutes to 30 minutes or hourly because rows are already eligible only after a six-hour recheck window. Keep the bounded row limit and update watermark/checked timestamps in the same transaction.

### Tier 3: Intake and Enrichment

5. `LT - Voice Queue Vapi Intake Poller` (`bYk1Ai6MJLyhTsDZ`): reactivate at its existing 10-minute cadence and 30-contact cap. Keep the positive `qualified` gate, `not qualified` suppression, source-tag cleanup, and queue deduplication. Add a cheap database count/eligibility check before paginating GHL contacts.
6. `LT - SimpleTexting Campaign Phone Backfill` (`8hQKQi1PooYDFxNR`): temporarily unpublished during dispatcher recovery. After the timeout-configured redeploy, re-enable only after API and scheduler health is stable.

### Tier 4: Outbound and High-Side-Effect Work

7. `LT - SimpleTexting Campaign Step Runner` (`dUyOfxllvkxZavaw`): temporarily unpublished during dispatcher recovery. After the timeout-configured redeploy, re-enable only after API and scheduler health is stable. Do not replay deleted historical ticks.
8. `LT - DAN Campaign Sender Release Dispatcher (Staged)` (`toUG1yPDmFG48KEP`): reactivate only after email delivery and release-log health are confirmed. Keep the 30-minute schedule and bounded candidate limit; add a preflight query that exits when sender capacity is unavailable.
9. `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`r7UjWLndmc6EqEUW`): reactivate last and only during an approved calling window. Keep the two-minute schedule and business-hours guard, but add a workflow-level overlap guard so a prior dialer execution cannot overlap the next tick. Preserve the atomic queue claim and 25-contact same-run safety cap.

## Runtime Optimization Rules

- Every polling workflow must perform a cheap database eligibility/count query before expensive GHL, Unipile, OpenRouter, or provider API calls.
- Every batch must have a hard maximum and must return immediately when no rows are eligible.
- Use atomic claims or idempotency keys before external side effects.
- Prefer watermarks and `next_attempt_at` windows over repeatedly scanning full contact pools.
- Keep outbound workflows separate from reporting/backfill work; do not increase global concurrency to compensate for inefficient batches.
- Record per-run `selected`, `processed`, `succeeded`, `skipped`, and `failed` counts so runtime and backlog growth are observable.
- Set workflow-level overlap protection for schedules whose runtime can approach their cadence.

## Reactivation Stop Conditions

Pause the most recently reactivated workflow if any of these occur:

- `new` executions increase for two consecutive checks.
- Any workflow produces repeated database connection timeouts.
- PostgreSQL active connections exceed 50% of `max_connections`.
- Provider/API rate-limit or 409 errors recur.
- An outbound workflow produces duplicate/idempotency conflicts.
- Runtime exceeds the scheduled interval for two consecutive runs.

## Concurrency Guard

After stale executions are removed, set regular-mode concurrency conservatively. The deployment compose now declares:

```text
N8N_CONCURRENCY=10
DB_POSTGRESDB_POOL_SIZE=10
DB_POSTGRESDB_CONNECTION_TIMEOUT=3000
DB_CONNECTION_ACQUISITION_TIMEOUT_MS=10000
DB_POSTGRESDB_STATEMENT_TIMEOUT=300000
DB_PING_TIMEOUT_MS=5000
EXECUTIONS_TIMEOUT=1800
EXECUTIONS_TIMEOUT_MAX=3600
```

Redeploy n8n through Coolify for these settings to take effect, then monitor PostgreSQL connections, CPU, memory, API rate limits, execution errors, and the `new` execution count. Increase concurrency only after the system remains stable. Do not enable Queue Mode unless Redis and dedicated n8n workers are intentionally deployed and configured.

## Verification Criteria

- `/healthz/readiness` remains HTTP 200.
- PostgreSQL connections remain comfortably below `max_connections`.
- The oldest `new` execution is recent and continues to advance.
- No historical scheduled-run replay storm occurs.
- Webhook-triggered inbound events remain preserved or are explicitly reconciled.
- Campaign, dialer, classifier, and reporting workflows each complete a controlled current run.

## Monitoring Follow-Up

Add monitoring for:

- `new` execution count above an agreed threshold
- Oldest `new` execution age above the execution SLA
- PostgreSQL connection saturation
- n8n readiness failures
- Repeated crash/error executions by workflow

The concurrency and timeout changes are staged in `n8n/docker-compose.yml` and require the next Coolify redeploy; they are not yet active in the current container.

## Reactivation Execution

Following the n8n redeploy, the seven non-SimpleTexting workflows were republished and verified active with matching `versionId` and `activeVersionId` values:

- `LT - Partnership Reply Poller`
- `LT - Voice Queue Vapi Intake Poller`
- `LT - LinkedIn Reply Backfill (Unipile)`
- `LT - Voice Agent V1 Outbound Dialer (Vapi)`
- `LT - Campaign Contact Classifier`
- `LT - DAN Campaign Sender Release Dispatcher (Staged)`
- `LT - Sales Outreach Jason Marc No-Owner Allocator`

The following remain intentionally inactive because they are manual-only or legacy duplicate paths:

- `LT - SimpleTexting State Diagnostic`
- `LT - SimpleTexting Send Count Check`
- `LT - SimpleTexting Inbound Reply (Webhook, Staged)`

Post-reactivation verification:

- n8n readiness: HTTP 200
- `new` executions: only preserved webhook executions remain
- SimpleTexting production workflows: temporarily paused during dispatcher recovery; manual and legacy duplicate workflows: inactive
- No manual production executions were started as part of reactivation

## SimpleTexting Hardening and Re-enable Plan (2026-08-06)

### Current Production State

The Campaign Sequencer remains intentionally unpublished because it would duplicate the canonical Step Runner. The other four production workflows were enabled and smoke-tested on 2026-08-07:

| Workflow | ID | Current state | Notes |
|----------|----|---------------|-------|
| LT - SimpleTexting Campaign Sequencer (Staged) | `7mSiivR3NhtLIcNz` | Unpublished | Keep disabled until the canonical sender path is selected. |
| LT - SimpleTexting Warmup Dispatcher (Staged) | `dZQLlbTLkpE1843X` | Active | Hourly; `defaultDryRun=false`; smoke `721541` succeeded with zero candidates/sends. |
| LT - SimpleTexting Campaign Step Runner | `dUyOfxllvkxZavaw` | Active | Every 5 minutes; explicit `dryRun=false`; smoke `721562` succeeded. |
| LT - SimpleTexting Campaign Phone Backfill | `8hQKQi1PooYDFxNR` | Active | Every 10 minutes; no-work guard added; smoke `721377` succeeded. |
| LT - SimpleTexting Pool Dispatcher (Staged) | `usxYXSuc4ahw40V3` | Active | Weekday bounded schedules, candidate limit 10, `defaultDryRun=false`; smoke `721576` succeeded with zero eligible contacts. |

The canonical provider router, send boundary, inbound reply, delivery, and unsubscribe workflows remain available. Manual diagnostics, send-count checks, and the legacy staged inbound webhook remain inactive.

### Completed Fixes and Optimizations

- Bootstrapped `SimpleTexting_Campaign_State` and `SimpleTexting_Campaign_Event_Log` in the n8n PostgreSQL database.
- Added indexes for due sends, phone backfill, stale locks, and event-log contact lookups.
- Removed runtime `CREATE TABLE` and `ALTER TABLE` statements from all five production workflows. Schema work is now a bootstrap/migration concern, not a scheduled-run concern.
- Split Warmup Dispatcher `Fetch + Dispatch Warmup Contacts` into `Fetch + Prepare Warmup Contacts` and `Send Warmup Contacts` so candidate preparation and provider sends are separate runner tasks.
- Replaced the known `$httpRequest`/`doHttpRequest` wrapper pattern with direct `this.helpers.httpRequest(...)` in Warmup and all six Sequencer step nodes.
- Changed Step Runner cadence from every 2 minutes to every 5 minutes.
- Changed Phone Backfill cadence from every 2 minutes to every 10 minutes.
- Added row claiming and a transaction-scoped advisory lock to Phone Backfill so overlapping runs cannot process the same rows.
- Added a transaction-scoped advisory lock to Step Runner so overlapping ticks exit without claiming work.
- Preserved Step Runner atomic `FOR UPDATE SKIP LOCKED` claims, five-row batch limit, bounded attempts, stale-claim recovery, and 15-minute failed-send retry delay.
- Added n8n runner request timeout configuration: `N8N_RUNNERS_TASK_REQUEST_TIMEOUT=300`.
- The deployment also declares `N8N_CONCURRENCY=10`, PostgreSQL pool size 10, bounded connection acquisition, statement, ping, and workflow execution timeouts.

### Remaining Configuration Gates

- Warmup is now active with `defaultDryRun=false`; its GHL search body remains blank, so the smoke produced zero candidates and zero sends. Approve the audience query before expecting warmup traffic.
- Pool Dispatcher still loads campaign state through full `ARRAY_AGG` arrays. Replace this with database-side existence checks before scaling the audience beyond a small test set.
- Sequencer is a long-lived six-step Wait-based path while Step Runner is a stateful scheduled sender. Do not activate both as senders until the canonical path is explicitly selected.
- Warmup and Sequencer provider-boundary Config nodes now use `x-lt-simpletexting-key` with the configured internal-send secret.
- The latest n8n timeout/deprecation environment settings require a Coolify redeploy, followed by an environment inspection inside the running container.

### One-by-One Re-enable Test Sequence

Do not activate all five workflows together. Before every step, record readiness, PostgreSQL connections, `new`/`running` counts, oldest queued execution, and recent errors.

1. Confirm the latest Coolify deployment is running n8n `2.33.3` with the timeout and runner settings active. Require `/healthz/readiness` HTTP 200, zero scheduled `new` executions, and zero stale scheduled `running` executions for at least 15 minutes.
2. Enable **Campaign Step Runner** only. Observe at least three five-minute cycles. Expected result: successful no-work exits or bounded sends, no queue growth, no database timeout, no duplicate claims, and no provider 409.
3. Enable **Phone Backfill** only. Observe at least two ten-minute cycles. Confirm row claims release, no overlapping duplicate lookups, and no growth in `new` executions.
4. Enable **Warmup Dispatcher** with `defaultDryRun=false` and its approved search body only for an explicitly authorized bounded live test. Confirm the split preparation/send graph completes without task-runner timeout and produces a bounded summary.
5. Enable **Pool Dispatcher** first in dry-run or with a one-contact approved limit while Step Runner is paused. Confirm only intended enrollment rows are created and no duplicate `(ghl_contact_id, campaign_key)` rows appear.
6. Run one approved live provider test with the smallest possible audience. Confirm a real SimpleTexting provider message ID, `report_sms_sent.provider_response`, campaign state advancement, GHL tags/notes, and conversation mirroring.
7. Enable Step Runner for the controlled enrolled row, observe its successful state transition, then gradually increase the Pool Dispatcher candidate limit.
8. Keep **Campaign Sequencer** unpublished unless it is explicitly chosen as the canonical sender. If it must be tested, set dry-run behavior first and use a synthetic/manual input; never test it concurrently with live Step Runner sends.

### Stop and Rollback Conditions

Immediately deactivate the most recently enabled workflow if any condition occurs:

- Scheduled `new` executions become nonzero for two consecutive checks.
- Any scheduled execution remains `running` beyond its normal interval or 10 minutes, whichever is shorter.
- A PostgreSQL connection acquisition timeout, `idle in transaction` accumulation, or scheduler `NaNms` deadline warning recurs.
- PostgreSQL active connections exceed 50% of `max_connections`.
- A provider 409, missing provider message ID, duplicate-send result, or unexpected live send occurs.
- Campaign state or event-log counts advance without a corresponding successful provider result.
- Warmup or any Code node hits the runner request timeout.

When rolling back, deactivate the last workflow only, preserve webhook executions, and do not delete current successful or waiting executions. Capture the execution ID, workflow ID, database connection count, and n8n logs before further cleanup.

## SimpleTexting Live Audit Pass (2026-08-06)

### Audit Result

The live n8n definitions were audited for all SimpleTexting sender, dispatcher, provider, inbound, delivery, unsubscribe, intake, diagnostic, and send-count workflows. No production campaign schedules were re-enabled during the audit.

Recent execution checks showed:

- Step Runner execution `720852`: successful no-work exit; no claimed rows.
- Phone Backfill execution `720851`: successful no-work exit; no claimed rows.
- Pool Dispatcher execution `703059`: successful state read and no candidate output; it remains unpublished.
- Historical Warmup execution `720733`: task-runner timeout after 60 seconds on the pre-split `Fetch + Dispatch Warmup Contacts` node. This was an old execution/version and is the reason the split graph must be tested after redeploy.
- Provider outbound health check: HTTP 200 with the expected registered-service response.

### Confirmed Fixes Applied During Audit

- Provider Outbound Router now fails closed unless `conversationProviderId` exactly matches configured provider `6a5b91913953360948dd59f1`.
- Runtime table creation/index DDL was removed from the active inbound reply, delivery, unsubscribe, provider-map, and idempotent-send paths. These workflows now depend on the bootstrapped schema.
- Active inbound, delivery, unsubscribe, and GHL SMS intake Config nodes explicitly preserve webhook input fields with `includeOtherFields=true`.
- The active SMS Send Config node's stale nested `parameters` assignment artifact was removed; its canonical outer assignments remain authoritative.
- The GHL SMS intake Code node now uses direct `this.helpers.httpRequest(...)` instead of the deprecated wrapper pattern.
- Live patched workflows were verified with matching `versionId` and `activeVersionId`; inactive production schedules remain unpublished.

### Activation Audit (2026-08-07)

- Step Runner, Phone Backfill, Warmup Dispatcher, and Pool Dispatcher are active and published.
- Successful smoke executions: Step Runner `721562`, Phone Backfill `721377`, Warmup `721541`, and Pool `721576`.
- Step Runner sends explicit `dryRun=false`; Warmup, Pool, and the send boundary use `defaultDryRun=false`.
- Warmup's schedule was corrected to an explicit hourly interval. Its smoke had `dryRun=false`, zero candidates, zero sends, and zero errors.
- Pool's original weekday schedules were restored after a one-minute controlled smoke; its smoke had zero eligible contacts.
- Phone Backfill now uses the dedicated `GHL API - SimpleTexting` credential and skips the GHL lookup when the claim query returns no contact rows.
- No active SimpleTexting workflow has a currently running execution, and the n8n execution API reports zero `new` executions.
- Campaign Sequencer remains unpublished to prevent a duplicate sender path.

### Findings Still Blocking Live Sends

- **Outbound API sending is not blocked by the SimpleTexting dashboard.** The SimpleTexting API credential is already used by n8n for outbound sends, and the authenticated GHL manual-send caller (`Send Simpletexting SMS from field to Contact`) now sends `x-lt-simpletexting-key` and is published. Provider event authentication only affects inbound reply, delivery, and unsubscribe callbacks; those callbacks need matching headers if they are enabled for production tracking.
- **Resolved 2026-08-06: unknown-contact events.** Inbound, delivery, and unsubscribe workflows now claim an event before side effects. If contact resolution fails, they write a synthetic `unresolved:<hash>` event-log record and return a controlled no-op without writing campaign state or touching GHL.
- **Resolved 2026-08-06: duplicate provider events.** Each event now uses a stable provider/event/status key. An advisory transaction lock and event-log lookup ensure only the first event proceeds to GHL notes, tags, Slack, Conversations, and state updates; replays return `duplicate_event_ignored`.
- **Medium: GHL Warm Intake - SMS Tag is active but defaults to `defaultDryRun=true`.** It will not add its intake tag unless the caller explicitly sends `dryRun=false`. Confirm whether this endpoint is intentionally staged or should be made operational before relying on it.
- **Low: the inactive legacy staged inbound workflow still contains runtime DDL.** It remains unpublished and is not part of the production path, but it should be retired or cleaned before any future activation.

Authentication is enforced internally using values derived from the existing n8n encryption key; the values were not printed or committed. The one-by-one outbound re-enable plan is not blocked by provider event headers. Event-driven reply, delivery, and unsubscribe tracking remains gated until the external provider can send the configured header or an approved provider-signature/secret-URL contract is selected.

Header contracts:

- Internal campaign callers to `lt-simpletexting-send-sms`: `x-lt-simpletexting-key`.
- SimpleTexting inbound/delivery/unsubscribe callers: `x-lt-simpletexting-event-key`.
- GHL SMS intake caller: `x-lt-simpletexting-intake-key` (not yet configured in the authenticated GHL session).
- GHL custom-provider outbound remains protected by exact `conversationProviderId` validation because the GHL provider callback contract does not currently expose a configured shared-secret header.
