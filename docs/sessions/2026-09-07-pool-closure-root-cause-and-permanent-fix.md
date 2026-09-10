# 2026-09-07 n8n Postgres Pool Closure — Root Cause & Permanent Fix

Status: RESOLVED + HARDENED (2026-09-07, after the 19:15:19Z UNHEALTHY alert and the
19:30:10Z user-approved n8n restart). This doc supersedes the "OPEN" state of
`2026-09-07-n8n-pool-closure-investigation.md`.

## Symptoms (what everyone saw)

- Monitor email `[LiveTransparent] UNHEALTHY: n8n/postgres/runner monitor` sent
  19:15:19Z (message id `1a07d4bde9bfd14b`).
- n8n readiness `https://automations.livetransparent.com/healthz/readiness` -> 503
  `{"status":"error"}` (`Database is not ready!`).
- n8n container logs: `Cannot use a pool after calling end on the pool` (~59/sec),
  plus `Error while saving insights metadata and raw data`.
- watch_fix misrouted the alert to the runner-network class (subject contains the
  word "runner"; 200-char snippet lacked "pool"), re-created the healthy runner at
  19:19Z, emailed AUTO-FIX COMPLETED. The real issue stayed unfixed until the
  user-approved n8n main restart at 19:30:10Z.

## Evidence chain (all timestamps UTC 2026-09-07)

1. Health log (`/var/log/livetransparent-n8n-health.log`): 18:05:01Z readiness 200;
   19:05:01Z readiness 503 + POOL_ERROR. So pool died in (19:00:06, 19:05:01].
2. Postgres accepted inserts at 19:00:06.307Z, then logged a deduplicationKey
   duplicate-key storm: workflow `hxiiYCpEfMuoSt5H` re-inserting the SAME execution
   `cac1f03d-f0f5-4b28-88d0-350ca2058c52` from many concurrent backends. Same
   pattern (4 skips/hour) persists post-restart at the top of each hour.
3. Postgres checkpoints are pathologically slow on this VPS: 271 checkpoints >20 s
   (slowest 269 s) in retained logs; every-5-min checkpoints currently write
   16-70 s even while `iostat` shows the disk otherwise idle -> fsync-latency
   bound virtual disk (sda).
4. n8n 2.37.10 `@n8n/db` self-heal: `DbConnectionMonitor` (dist/connection/
   db-connection-monitor.js) pings the pool; `recoveryEnabled` is UNCONDITIONAL for
   postgres. The configured env was a hair-trigger:
   `DB_PING_INTERVAL_SECONDS=5`, `DB_PING_TIMEOUT_MS=5000`,
   `DB_PING_MAX_FAILURES_BEFORE_RECOVERY=3`, `DB_POSTGRESDB_POOL_SIZE=10`.
5. The ONLY destroy-capable paths in the code are: process exit (not the case —
   process stayed alive), and the monitor's `recoverDataSource()` ->
   `destroyDataSource()` which overrides `driver.disconnect` and calls
   `pool.end()`. Once the pool is ended, `ping()` silently early-returns on
   `!dataSource.isInitialized || recovering` — the retained logs contain ZERO
   `Database ping failed` / `Recovery attempt` lines across the whole dead window.
   Result: a permanently ended pool, 59 errors/sec, no self-heal, no exit, no
   alert, for 25+ min (and 37 min in the 12:52Z first event, fixed only by the
   Coolify container recreate at 13:29:26Z).

### Root-cause statement

The alert was caused by a feedback loop: scheduled-workload burst -> WAL burst ->
checkpoint stalls (up to 269 s) on a slow virtual disk -> n8n's 10-client pool
saturated -> 3 ping failures -> n8n's own DB "recovery" destroyed the pool
(`pool.end()`) -> the destroy/re-init cycle left the app with an ended pool, and
the recovery logic then went silent (isInitialized=false guard), so nothing
self-healed or escalated until a manual container restart.

## Permanent fixes applied (2026-09-07, each verified)

### A. watch_fix v2 — scripts/watch_fix.py (local repo; cron job b3f164cd1746)
- New highest-priority `pool` class: auto-restart ONLY the n8n main container
  after live preconditions: fresh `Cannot use a pool` in last 600 s, readiness
  != 200, postgres healthy, n8n up > 300 s, <= 3 auto-restarts/hour. Captures
  before/after evidence and emails COMPLETED/INCOMPLETE/SKIPPED.
- Classification is evidence-based; the word "runner" in a subject is NEVER
  enough for the runner class (every alert subject contains all three component
  names). `gmail_read.py --body` returns the full alert so `POOL_SIG:` lines are
  visible.
- Runner class now verify-first: if DNS/TCP check passes, no mutation (this
  prevents the 19:19Z pointless runner recreate).
- Tested: today's alert classifies `pool`; snippet-only view classifies
  `escalate` (old code: `runner` — the defect); synthetic runner -> `runner`;
  synthetic unknown -> `escalate`. `--dry-run` passes.

### B. n8n DB recovery hair-trigger defused — compose env
Backup: `/data/coolify/services/n44wksswcocwk88ogcog8c48/docker-compose.yml.bak-poolfix-*`
(also `.bak-watchfix-*` chain). Applied, n8n main re-created 20:35:57Z (runner
untouched). New values (verified in live container):
`DB_POSTGRESDB_POOL_SIZE=25`, `DB_PING_INTERVAL_SECONDS=10`,
`DB_PING_TIMEOUT_MS=15000`, `DB_PING_MAX_FAILURES_BEFORE_RECOVERY=15`,
`DB_CONNECTION_ACQUISITION_TIMEOUT_MS=15000`,
`DB_RECOVERY_BACKOFF_MAX_MS=60000`, `DB_POSTGRESDB_CONNECTION_TIMEOUT=10000`.
Recovery now only fires when the DB is genuinely unreachable for ~2.5 min.

### C. Postgres checkpoint tune — compose command args
Backup: `/data/coolify/services/uokgs4c04ko0s4scccg40cgg/docker-compose.yml.bak-checkpoint-*`.
Applied: `-c checkpoint_timeout=1800 -c max_wal_size=2GB -c wal_compression=on
-c checkpoint_completion_target=0.9`. Verified live: 30min / 2GB / pglz / 0.9.
Checkpoints go from every 5 min to every 30 min max (fewer stalls), WAL stays
compressed, data volume untouched.

## Verified end state (same day)

- readiness 200; 0 pool-closure errors since 19:30:10Z.
- n8n main StartedAt 20:35:57Z (env tuned); runner StartedAt 19:19:21Z (unchanged).
- postgres healthy, GUCs live.
- No new UNHEALTHY alert email since the 19:15 one.

## Residuals / watch items (NOT the pool cause)

- `Scheduled execution skipped: duplicate deduplication key` still appears ~4x/hour
  post-restart (workflow whose dedupe key collides). Watch whether it escalates.
- Postgres checkpoint writes remain slow (16-70 s) — the disk is the physical
  weak point; if workloads grow, consider faster storage.
- n8n CPU ~88% under `docker stats` post-event — monitor trend.

## Tooling created during this work (in .monitor/)

`probe_*.py` (read-only probes), `apply_changeB.py`, `apply_changeC.py`,
`test_watchfix_classifier*.py`, `probe_now.py`. All safe to reuse; no secrets
inside (env values were only read for non-credential tuning keys).