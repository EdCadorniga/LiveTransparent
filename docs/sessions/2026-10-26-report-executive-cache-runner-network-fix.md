# Executive Report cache runner network repair — 2026-10-26

## Objective

Investigate and fix the apparent out-of-memory crash in `LT - Report Executive Summary API` execution `1194021` (`Bukc0mgOD2r7V6ED`).

## Findings

- Execution `1194021` stopped at `Query Summary`. n8n's displayed “possible out-of-memory” message is generic; available evidence does not establish an OOM kill.
- A second workflow, `LT - Executive Summary and Channels Cache Refresh` (`Rrsigvi8AhH3iR55`), also crashed at the same time (`1194020`). The n8n container started a new session at `2026-10-25T19:25:45Z` and recovered both unfinished executions as crashed. The reason for that container replacement was not present in retained host/kernel logs.
- The cache refresher retry (`1194029`) successfully ran `Query Summary` for the same Oct 18–24 window in about 62 seconds, then failed at `Store Report Cache` with `ECONNREFUSED 10.0.0.1:5432`.
- Root cause for repeated uncached cold-query load: the live Coolify runner configuration had drifted from the repository Compose definition. The runner had `extra_hosts: postgres:host-gateway` and was not attached to `coolify-shared`; this forced `postgres` to resolve to unreachable `10.0.0.1`, so `Store Report Cache` could not persist the completed query. The refresh path therefore kept issuing expensive ~98 KB report queries instead of reliably filling/using `v1_facts_cache`.

## Repair applied

- Updated Coolify's saved service `n44wksswcocwk88ogcog8c48` through its API, removing the stale runner `extra_hosts` mapping while preserving the `coolify-shared` network. No redeploy was triggered by the API update.
- Backed up the generated Compose file on the VPS, removed the stale host mapping there, ensured `n8n-runner` uses both its private service network and `coolify-shared`, validated the Compose configuration, and recreated only the runner container.
- No workflow graph, CRM, report facts, or cache rows were manually changed. No full cold refresh was forced.

## Verification and limits

- Live runner now has no `extra_hosts` override and is attached to `coolify-shared` plus the private n8n network.
- From the recreated runner, `postgres` resolved to `10.0.2.5` (the PostgreSQL container) and TCP `5432` connected successfully.
- The checked-in `n8n/docker-compose.yml` already had the correct network configuration; no application source change was needed.
- The next natural cache refresh is runtime acceptance: verify it succeeds through `Store Report Cache`, then verify the next matching request is a cache hit. Until then, do not claim the report endpoint's full cold-refresh path is runtime-accepted.
- The coincident n8n container replacement that marked `1194021` and `1194020` crashed remains unexplained; do not label it a confirmed OOM event. If another cross-workflow crash occurs, correlate Coolify deployment/container events and host/kernel logs at that timestamp.

## Follow-up verification — 2026-10-26

- The adjacent `LT - GHL Email Template Campaign Queue (STAGED)` scheduled run `1194070` succeeded after runner recreation. It was dry-run, found no accepted campaigns, and completed its Postgres-dependent Code node without an error.
- A live `range=7d` report request returned HTTP 200 with a populated 29,644-byte response in 1.1 seconds. Executive Summary execution `1194090` succeeded on the cache-hit branch through `Return Cached Report`.
- This confirms current runner connectivity and the report cache-read path. It did not exercise `Store Report Cache`; no cold refresh was forced because the query is expensive and the desired acceptance is the next natural cache miss/refresh. Keep the write-path runtime check open until that execution succeeds and a subsequent same-key request is a cache hit.
- The current Coolify-generated Compose config has no runner `extra_hosts` and attaches both n8n and the runner to `coolify-shared` plus the private n8n network. Current runner inspection resolves `postgres` to `10.0.2.5` with TCP 5432 open.

## Security and next steps

- Diagnostic execution/config inspection exposed refresh authentication and database configuration values in the tool output. Values are intentionally omitted here. Plan coordinated rotation and caller updates; do not rotate the database password or n8n encryption key casually.
- After the next natural scheduled cache refresh, record the execution ID, confirm zero node errors and successful cache persistence, and verify a cache hit for the same date key.
- If cache persistence still fails, stop and inspect the current live runner DNS/network and the Coolify saved/generated Compose before making another change.

## Repository state

- The worktree was clean before this closeout. This handoff and the two current-status summaries are the only intended repository changes; the live Coolify/VPS configuration repair is separately recorded above.
- No workflow execution was manually triggered, no production report deployment was made, and no secret values are included in this record.
