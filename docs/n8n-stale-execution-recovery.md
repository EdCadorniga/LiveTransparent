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
