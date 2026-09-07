# n8n PostgreSQL Pool Closure Investigation — 2026-09-07

## Purpose

Record the state of the later n8n database-readiness incident and provide a reliable restart point for the next session. This is a follow-up to the September 4 runner/DNS recovery documented elsewhere in the project.

## Executive status

- The immediate failure mechanism is confirmed: the n8n process remained alive, but its internal TypeORM PostgreSQL pool was already ended/closed. Subsequent database operations failed with `Cannot use a pool after calling end on the pool`.
- n8n basic liveness and database readiness were different signals: `/healthz` previously returned HTTP 200, while readiness returned `{"status":"error"}` and authenticated workflow access returned HTTP 503 with `{"code":503,"message":"Database is not ready!"}`.
- PostgreSQL itself was healthy and accepting authenticated connections. No evidence showed invalid credentials, a continuously stopped database, or a PostgreSQL restart during the failure window.
- The n8n main container was not restarted during this investigation. Observed container state showed no restart count increase and no OOM-kill evidence.
- The exact upstream event or code path that called `pool.end()` was not identified. Do not describe the trigger as proven.
- No workflow, environment, Compose file, deployment, restart, database, or remote configuration write was performed during this investigation.

## Deployment state observed

- Public n8n URL: `https://automations.livetransparent.com`
- VPS: `89.117.21.29` (`vmi3077218`); access was performed with Paramiko and the configured local key.
- Coolify service Compose path: `/data/coolify/services/n44wksswcocwk88ogcog8c48/docker-compose.yml`
- n8n image: `n8nio/n8n:2.37.9`
- Runner image: `n8nio/runners:2.37.9`
- Main container: `n8n-n44wksswcocwk88ogcog8c48`
- Runner container: `n8n-runner-n44wksswcocwk88ogcog8c48`
- Runner mode: external; broker URI is `http://n8n:5679`.
- n8n and runner use the expected `coolify-shared` network and service names.
- The repository Compose file and the Coolify-generated Compose file were inspected but not synchronized. Their formatting and deployment metadata differ; their substantive n8n/runner settings were already aligned. Do not replace the Coolify file with the repository file without preserving Coolify metadata, networks, volumes, labels, and secret injection.
- Custom `DB_PING_*` and `DB_RECOVERY_*` variables were present but were not found in the installed n8n 2.37.9 application code. Treat them as ineffective unless an external wrapper is proven to consume them.

## Timeline and evidence

### September 4 host anomaly

Host logs contained CPU soft-lockup reports involving both a `postgres` process and a `soketi-server` process, including network-stack frames. This is a plausible transient infrastructure disturbance, but it predates the first retained n8n pool error by approximately three days. It is not sufficient to establish causality.

### September 7 pool failure

- The first retained `Cannot use a pool after calling end on the pool` error occurred at approximately `2026-09-07 12:52:08 UTC`.
- The error appeared in a burst and the stack terminated in a timer callback. This indicates a scheduled n8n database operation encountered an already-ended pool; it does not prove which component ended the pool.
- The retained correlation checks found no preceding PostgreSQL error, n8n connection-refusal message, container restart, OOM event, or disk-exhaustion signal in the available logs.
- PostgreSQL had not restarted since September 2 in the evidence already collected.
- A read-only installed-source inspection was attempted to enumerate pool shutdown paths, but that command was interrupted before producing a usable result. Repeat it with bounded, narrower searches if needed.

## Root-cause boundary

Confirmed:

1. n8n's internal PostgreSQL pool entered an ended/failed state.
2. n8n did not recover that pool while the process stayed alive.
3. This caused readiness failure and the authenticated REST API's 503 response.
4. PostgreSQL, credentials, runner network configuration, and Compose version alignment were not shown to be the primary cause.

Not confirmed:

1. The process, command, deployment action, PostgreSQL event, network event, or n8n code path that first called `pool.end()`.
2. Whether the September 4 kernel soft lockup caused the September 7 failure.
3. Whether the separate runner error `cannot insert multiple commands into a prepared statement` contributed to this pool failure. Treat it as a separate issue until correlated.

## Recommended recovery

The safe immediate recovery remains a targeted restart/recreate of only the n8n main service through Coolify, subject to explicit current-session approval because it can interrupt active workflows. Do not restart PostgreSQL or Redis, rotate `N8N_ENCRYPTION_KEY`, or change the runner authentication token without new evidence and approval.

After an approved n8n restart, verify all of the following:

1. `/healthz/readiness` returns HTTP 200 and a healthy response.
2. Authenticated workflow listing returns HTTP 200 rather than `Database is not ready!`.
3. The UI loads normally.
4. The runner reconnects and broker health is normal.
5. New logs contain no `Cannot use a pool after calling end on the pool` errors.
6. No active or recently scheduled workflow was unintentionally interrupted.

## Next investigation session

Start here, in this order, before changing configuration:

1. Re-check current live state: readiness, authenticated workflow API, container status/restart count, and recent n8n/runner/PostgreSQL logs.
2. Capture the first pool-related error with a narrow timestamp window and retain complete output in a local file; avoid giant combined Docker-log commands that can time out or truncate output.
3. Query Docker/Coolify event history around `2026-09-07 12:52 UTC` for container recreate, stop, health, network, or deployment events.
4. Query PostgreSQL logs around the same minute for connection termination, backend crash, failover, restart, or network errors.
5. Inspect the installed n8n 2.37.9 source with bounded searches for `pool.end`, TypeORM DataSource destruction, shutdown hooks, health-check recovery, and database bootstrap/reconnect paths.
6. Compare the source paths with the exact stack trace and determine whether a scheduled health check, graceful shutdown, or failed initialization can end the pool without terminating the process.
7. Check host journal/kernel/resource events around both September 4 and September 7, including soft lockups, OOM, disk, Docker, and network events.
8. If the trigger remains unprovable, document it as an unresolved transient/application lifecycle failure and proceed with the approved targeted n8n restart plus readiness-based monitoring.

## Safety and handling

- Never document or print API keys, runner tokens, SSH private-key contents, passwords, encryption keys, or `.env` values.
- Use live n8n/MCP state as authoritative for workflow state; repository workflow exports are backups or references.
- Any workflow edit, activation change, execution, deployment, service restart, or remote write requires explicit current-session approval.
- Keep the repository's pre-existing modifications in `Project Status and Next Steps.md`, `n8n/docker-compose.yml`, and `repomix-output.md` intact.
