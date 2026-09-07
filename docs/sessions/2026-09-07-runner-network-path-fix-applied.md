# Runner Network-Path Fix Applied and Verified

Date: 2026-09-07 UTC
Project: LiveTransparent
Status: RESOLVED — fix applied and verified; monitoring + email alerting live
Related: `2026-09-07-runner-network-path-verification.md` (diagnosis), `2026-09-07-n8n-force-redeploy-and-monitoring.md`, `2026-09-07-n8n-pool-closure-investigation.md`

## Summary

The external n8n runner's broken PostgreSQL network path was fixed in the live
Coolify environment and verified end-to-end. The failure signature
`connect ECONNREFUSED 10.0.0.1:5432` (every 2 minutes on the pg-using
`LT - Voice Agent V1 Outbound Dialer (Vapi)` workflow) is gone.

## What was wrong

The authoritative live Coolify-generated Compose file
(`/data/coolify/services/n44wksswcocwk88ogcog8c48/docker-compose.yml`) had the
`n8n-runner` service defined with:

```yaml
extra_hosts:
  - postgres:host-gateway
networks:
  n44wksswcocwk88ogcog8c48: null
```

`extra_hosts` overrides Docker DNS for `postgres`, mapping it to the Docker host
gateway (observed as stale `10.0.0.1`), while the runner was not attached to
`coolify-shared` — the network where the healthy PostgreSQL container
(`postgres-uokgs4c04ko0s4scccg40cgg`, `10.0.2.3`) is reachable by service name.

## What was done

1. **Backup** — timestamped backup of the generated Compose file created before editing.
2. **Edit** — removed the runner `extra_hosts: postgres:host-gateway` entry; added
   `coolify-shared` to the runner's `networks` (keeping the private broker network).
   All other Coolify labels, environment injection, service names, volumes, and
   metadata preserved.
3. **Validate** — `docker compose config -q` passed.
4. **Apply** — `docker compose up -d --force-recreate n8n-runner` (runner only;
   n8n main untouched and remained running).
5. **Idempotency** — the same procedure was re-run once during watch-fix validation;
   it is safe to re-apply (the edit is a no-op when already correct).

## Verification evidence

- Runner dual-homed: `10.0.4.4` private + `10.0.2.5` coolify-shared.
- `docker exec <runner> getent hosts postgres` → `10.0.2.3` (not `10.0.0.1`).
- TCP `postgres:5432` from runner: `TCP_OK`.
- n8n `/healthz` → HTTP 200 `{"status":"ok"}`; image `n8nio/n8n:2.37.10`.
- Runner registered: `launcher-javascript`, `launcher-python`.
- `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`r7UjWLndmc6EqEUW`):
  - Pre-fix: `status=error`, `connect ECONNREFUSED 10.0.0.1:5432` every 2 min
    (through 14:52 UTC).
  - Post-fix: `status=success` at 14:54, 14:56, 14:58, 15:00, 15:06, 15:07 UTC.
- One transient `TCP_FAIL` immediately after the first recreation (postgres
  checkpoint contention); healthy on re-check. Not a regression.

## Monitoring contract (live)

Two Hermes cron jobs run every 30 minutes (local Hermes install on the Windows
host; VPS-native root monitor additionally exists at
`/usr/local/sbin/livetransparent-n8n-health.sh`, `5 * * * *`, monitor-only):

1. **Monitor** (`LT n8n-postgres-runner monitor`, job `33eea46dd9b3`) — SSHes to
   the VPS and checks n8n `/healthz`, PostgreSQL container health, runner→postgres
   DNS (must be `10.0.2.x`, never `10.0.0.1`), TCP `postgres:5432` reachability,
   and bounded recent logs for `ECONNREFUSED`, `10.0.0.1`, pool-closure, and
   broker signatures. On any problem it emails a deduplicated alert to
   `edmundocadorniga@gmail.com`.
2. **Watch-email auto-fix** (`LT watch-email auto-fix`, job `b3f164cd1746`) —
   reads Gmail (`edmundocadorniga@gmail.com`) for new monitor alert emails. For
   the known runner-network problem class it applies the bounded fix above,
   verifies, and emails a resolution. Everything else (postgres/db/pool-closure)
   is escalated via email, never auto-fixed.

Email transport: Hermes Google OAuth token with `gmail.send`/`gmail.readonly`/
`gmail.modify`; access token auto-refreshes. Test alert delivered
(`SENT_OK id=1a07c62cb42810a4`).

## Safety gates (unchanged)

- Never restart PostgreSQL/Redis or rotate `N8N_ENCRYPTION_KEY` without evidence
  and explicit approval.
- The n8n internal pool-closure incident is SEPARATE and unresolved at
  root-cause level. Do not treat the network fix as proof the pool issue is fixed.
- The GA4 Daily Ingest has a separate Google Analytics credential error; out of
  scope.
- Any commit/push of repository changes requires explicit approval.