# External n8n Runner PostgreSQL Network-Path Verification

Date: 2026-09-07
Project: LiveTransparent
Status: RESOLVED — fix applied and verified 2026-09-07 UTC; ongoing monitoring. Post-fix results below.

## Purpose

Record the live verification that the external n8n runner is using the wrong PostgreSQL network path, and preserve the exact next steps for the next session.

## Repository configuration

The repository Compose file at `n8n/docker-compose.yml` is functionally configured for the intended topology:

- `n8n-runner` uses `N8N_RUNNERS_TASK_BROKER_URI=http://n8n:5679`.
- The runner's inline image is `n8nio/runners:2.37.10`.
- The runner's JavaScript task runner uses `NODE_PATH=/opt/pg-node_modules/node_modules`.
- The runner is configured for the external `coolify-shared` network.
- The repository file does not define `extra_hosts: postgres:host-gateway`.
- The n8n service retains the `n8n` network alias needed by the runner broker URI.

Do not replace the live Coolify-generated Compose file wholesale with this repository file. Coolify-generated labels, injected environment, volume names, service identifiers, and network metadata must be preserved.

## Live Coolify inspection

The authoritative generated Compose file was inspected read-only at:

`/data/coolify/services/n44wksswcocwk88ogcog8c48/docker-compose.yml`

The live `n8n-runner` service currently contains:

```yaml
extra_hosts:
  - postgres:host-gateway
networks:
  n44wksswcocwk88ogcog8c48: null
```

The live Compose configuration also declares `coolify-shared`, but the runner is not attached to it. The runner therefore cannot use Docker DNS on the shared application network for PostgreSQL.

The live runner has the following relevant database environment values, with no secret values recorded:

```text
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=postgres
DB_POSTGRESDB_PORT=5432
```

## Observed network state

The `coolify-shared` network inspection showed the healthy PostgreSQL container at approximately `10.0.2.3`. The monitor and recent workflow logs showed the runner resolving `postgres` to the stale host-gateway address `10.0.0.1`, followed by repeated:

```text
ECONNREFUSED 10.0.0.1:5432
```

This is a network/DNS path problem, not evidence that PostgreSQL itself is unhealthy. The hourly monitor separately verified PostgreSQL Docker health as `healthy` and n8n readiness as HTTP 200 during the recorded run.

## Root cause

The explicit `extra_hosts` mapping overrides normal Docker service-name resolution for `postgres`, mapping it to the host gateway. The runner is also missing `coolify-shared`, the network on which the PostgreSQL service is reachable by its service name.

Both conditions must be corrected. Adding the shared network while leaving the host-gateway mapping would still be unsafe because `/etc/hosts` can continue to take precedence.

## Required minimal fix

Change the authoritative Coolify source configuration for `n8n-runner` as follows:

1. Remove the runner-level `extra_hosts` entry:

   ```yaml
   extra_hosts:
     - postgres:host-gateway
   ```

2. Preserve the existing private resource network for the n8n broker.

3. Add `coolify-shared` to the runner's networks:

   ```yaml
   networks:
     n44wksswcocwk88ogcog8c48:
     coolify-shared:
   ```

4. Preserve Coolify labels, environment injection, service names, volume declarations, build definition, runner token wiring, and all unrelated generated metadata.

5. Recreate/redeploy the runner after the configuration change. A file edit alone does not change the networks of an existing container.

No remote write, container recreation, restart, or redeploy was performed during this verification.

## Required verification after explicit approval

Use the actual current runner container name from Docker if it changes; the observed name was:

`n8n-runner-n44wksswcocwk88ogcog8c48`

Verify network membership:

```bash
docker inspect <runner> --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{$net.IPAddress}}{{"\\n"}}{{end}}'
```

Expected: both the private resource network and `coolify-shared`.

Verify Docker DNS:

```bash
docker exec <runner> getent hosts postgres
```

Expected: the PostgreSQL container address, currently approximately `10.0.2.3`.

Failure condition: `postgres` resolves to `10.0.0.1`.

Verify TCP reachability without printing credentials:

```bash
docker exec <runner> node -e "const net=require('net'); const s=net.createConnection({host:'postgres',port:5432},()=>{console.log('postgres tcp ok');s.end()}); s.on('error',e=>{console.error(e.message);process.exit(1)})"
```

Inspect recent runner logs for regression signatures:

```bash
docker logs --since=15m <runner> 2>&1 | grep -E 'ECONNREFUSED|10\\.0\\.0\\.1|Cannot use a pool|pool.*end|pool.*closed'
```

Then verify the next scheduled GHL ingest completes without `ECONNREFUSED` or `10.0.0.1:5432` references. Continue the hourly monitor for at least several cycles.

## Relationship to the n8n pool-closure incident

This runner network correction is separate from the n8n internal pool-closure incident. The earlier n8n error was:

```text
Cannot use a pool after calling end on the pool
```

The current runner network diagnosis explains the stale `10.0.0.1:5432` connection refusals, but it does not prove that n8n's internal pool lifecycle problem is fixed. Continue monitoring n8n logs for pool-closure signatures and investigate the original `pool.end()` cause separately if it recurs.

Do not restart PostgreSQL or Redis, rotate `N8N_ENCRYPTION_KEY`, edit workflows, or configure alert transport as part of this network fix without separate evidence and explicit approval.

## Next session entry point

1. Read this file and the `Current Open Issue: Coolify Runner PostgreSQL Network Path` section at the top of `Project Status and Next Steps.md`.
2. Re-inspect the live Coolify-generated Compose file before writing.
3. Obtain approval for the remote change and runner recreation.
4. Back up the exact generated file before any remote write.
5. Apply only the minimal network/DNS change above.
6. Read back the configuration and verify the running container, DNS, TCP reachability, logs, and next GHL ingest.
7. Update this file and the project status with the actual post-fix results; do not mark the issue resolved based on a successful file write alone.

## POST-FIX RESULTS — 2026-09-07 UTC (fix applied and verified)

The required minimal fix was **APPLIED** and **VERIFIED** live on 2026-09-07 UTC (explicit session approval):

1. **Backup**: a timestamped backup of the live generated Compose file
   `/data/coolify/services/n44wksswcocwk88ogcog8c48/docker-compose.yml` was created before the edit.
2. **Edit**: removed the runner-level `extra_hosts: postgres:host-gateway` entry and added `coolify-shared`
   to the `n8n-runner` networks (alongside `n44wksswcocwk88ogcog8c48`). All other Coolify labels, environment
   injection, service names, volumes, build definition, and metadata preserved.
3. **Validation**: `docker compose config -q` passed (`CONFIG_VALID`).
4. **Recreation**: `docker compose up -d --force-recreate n8n-runner` recreated only the runner; n8n main was
   untouched and remained running.

Verified results after recreation:

- Runner is dual-homed: private network `10.0.4.4` (eth0) + `coolify-shared` `10.0.2.5` (eth1).
- `docker exec <runner> getent hosts postgres` → `10.0.2.3` (the healthy PostgreSQL container on `coolify-shared`);
  no longer `10.0.0.1`.
- TCP `postgres:5432` reachable from the runner (`TCP_OK` via `nc -z -w3`).
- n8n main also reaches `postgres:5432` (`TCP_OK`); n8n `/healthz` → HTTP 200 `{"status":"ok"}`.
- Runner registered successfully: `Registered runner "launcher-javascript"`, `"launcher-python"`, `JS Task Runner`.
- **END-TO-END PROOF**: workflow `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`r7UjWLndmc6EqEUW`), which had been
  failing every 2 minutes with `connect ECONNREFUSED 10.0.0.1:5432` (through 14:52 UTC), now returns `success`
  post-fix (14:54, 14:56, 14:58, 15:00, 15:06, 15:07 UTC). The fix is stable across a second idempotent runner
  recreation (watch-fix validation run).

Notes:

- One transient `TCP_FAIL` was observed immediately after the first recreation (postgres checkpoint contention);
  a re-check within minutes showed both connections healthy. Not a regression.
- The n8n internal pool-closure incident remains SEPARATE and unresolved at root-cause level; this network fix does
  not prove the pool lifecycle issue is fixed.
- The GA4 Daily Ingest has a SEPARATE Google Analytics credential error unrelated to this network issue.
- Monitoring is now handled by Hermes cron jobs (monitor + watch-email auto-fix) with email alerting to
  `edmundocadorniga@gmail.com` (transport verified with a real Gmail message id).
