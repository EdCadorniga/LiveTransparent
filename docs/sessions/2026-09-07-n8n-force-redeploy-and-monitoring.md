# n8n 2.37.10 Force Redeploy and Monitoring

Date: 2026-09-07 UTC

## Resolution

- Updated the local Compose definition at `n8n/docker-compose.yml` to n8n `2.37.10` and retained the external-runner fix.
- Updated the live Coolify-generated Compose definition at `/data/coolify/services/n44wksswcocwk88ogcog8c48/docker-compose.yml` to runner `2.37.10`, preserving Coolify routing, networks, volumes, and secret injection.
- Preserved the external-runner settings, including external runner mode, the runner network/alias, `NODE_PATH=/opt/pg-node_modules/node_modules`, and the explicit bundled pnpm executable path.
- A timestamped live Compose backup was created before the live edit; credentials and secret values are intentionally omitted from this document.
- Compose syntax validation passed for both local and live definitions.
- The live stack was force-recreated with the authoritative Coolify Compose project using `--build --force-recreate --pull always`.

## Post-redeploy verification

- n8n container image: `n8nio/n8n:2.37.10`.
- n8n and external-runner containers: running, with zero restarts at verification time.
- Public endpoint `https://automations.livetransparent.com/`: HTTP 200.
- The external runner was rebuilt from the updated runner definition and is running.
- This proves service and endpoint health at the verification time; it does not prove that every workflow dependency is healthy.

## Known runtime error

A scheduled GHL ingest execution logged a database connection refusal to `10.0.0.1:5432` (`ECONNREFUSED`). This is distinct from n8n process health: n8n and the runner remained running and the public endpoint returned HTTP 200. The address is the stale host-gateway path previously associated with runner/database connectivity and requires follow-up if it recurs.

Do not respond to this error by restarting PostgreSQL, rotating encryption keys, editing workflows, or deleting data without evidence and explicit approval. First capture the affected workflow execution, runner and n8n logs, container network/DNS state, and PostgreSQL reachability.

## Hourly monitoring and bounded auto-remediation

An hourly Hermes scheduled monitor is installed for this incident. Each run must:

1. Check the public readiness endpoint and the live n8n/runner container state.
2. Inspect a bounded recent log window for `ECONNREFUSED` involving `10.0.0.1:5432`, stale `postgres:host-gateway`, pool-closure errors, runner broker disconnects, and external-module/runner errors.
3. If n8n or the runner is unhealthy, perform at most one targeted restart/recreate of the affected n8n service or runner, then verify readiness, container state, and endpoint response.
4. Never restart PostgreSQL or Redis, rotate credentials/keys, edit workflows, delete data, or loop on repeated restarts automatically.
5. Record the observed error, action, verification result, and any remaining blocker.
6. Send an incident report to `edmundocadorniga@gmail.com` when the monitored error or an unhealthy service is detected; do not include tokens, passwords, private keys, connection strings, or secret environment values.

The scheduler currently has a **configured and tested** mail transport on this Windows host: the Hermes Google OAuth token for `edmundocadorniga@gmail.com` has Gmail scopes (`gmail.send`, `gmail.readonly`, `gmail.modify`) and a test alert was delivered (`SENT_OK id=1a07c62cb42810a4`). The monitor cron (every 30 min) emails incident reports to `edmundocadorniga@gmail.com`; the watch-email cron (every 30 min) reads that inbox for new alert emails and auto-fixes the known runner-network problem class (backup compose → remove runner `extra_hosts` → add `coolify-shared` → recreate runner → verify), escalating everything else for manual review.

## Recovery procedure if the error returns

- Confirm whether the failure is limited to a workflow execution or whether n8n readiness is failing.
- Capture the workflow execution ID and a bounded, redacted log window from n8n and the runner.
- Verify the runner resolves the PostgreSQL service over `coolify-shared`; do not assume `10.0.0.1` is valid.
- If only the runner is unhealthy, recreate the runner and verify broker connectivity.
- If n8n readiness is unhealthy because of an ended pool, recreate only n8n and verify the persisted encryption-key configuration.
- If the database itself is unhealthy, stop automated remediation and escalate for explicit database-level action.
- After recovery, verify the affected workflow with a controlled, non-destructive run or the next scheduled execution; do not fabricate success from container health alone.
