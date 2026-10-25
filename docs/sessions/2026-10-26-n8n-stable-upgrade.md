# n8n Stable Upgrade to 2.44.6

Date: 2026-10-26

## Result

- Upgraded the live `n8n-lt` deployment from `2.37.10` to official stable `2.44.6`.
- Updated both the main image (`n8nio/n8n:2.44.6`) and the external task-runner base image (`n8nio/runners:2.44.6`) to keep their versions aligned, as required by n8n's task-runner documentation.
- Updated local `n8n/docker-compose.yml` and the Coolify-generated live Compose file at `/data/coolify/services/n44wksswcocwk88ogcog8c48/docker-compose.yml`.
- After noticing Coolify's service page still showed `2.37.10`, read its saved service definition through the Coolify API. The UI was reflecting stale `docker_compose_raw` (n8n `2.37.10`, runner base `2.36.9`) even though the generated Compose and live containers were already at `2.44.6`. Updated only the two image references in Coolify's saved Compose via `PATCH /api/v1/services/{uuid}` with `instant_deploy` omitted; Coolify reparsed the definition and the API readback confirmed both saved versions at `2.44.6`. This corrected the source of truth without another deployment.
- Recreated the production n8n and task-runner containers through their existing Coolify Compose project. The stable `2.45.3` build was not selected because GitHub marked it prerelease; the `stable` release tag resolved to `2.44.6`.

## Runner compatibility correction

- First runner build attempt failed before containers were recreated. In the 2.44.6 runner image, the former path `/usr/local/lib/node_modules/pnpm/bin/pnpm.cjs` no longer exists; `pnpm` is available on `PATH` instead.
- Changed the custom runner build step to `pnpm add pg@8.21.0 --dir /opt/pg-node_modules --prod --no-lockfile` in both local and live Compose. The runner then built successfully.
- Verified from the running runner container that `typeof require(String.fromCharCode(112,103)).Client` is `function`.

## Backups

Before editing the live Compose file, created root-only backups on the VPS:

- `/root/n8n-upgrade-backups/pre-2.44.6-20261025T190221Z-f4d632a7-docker-compose.yml`
- `/root/n8n-upgrade-backups/pre-2.44.6-20261025T190221Z-f4d632a7-n8n-db.dump` (PostgreSQL custom-format dump of database `n8n`)
- `/root/n8n-upgrade-backups/pre-2.44.6-20261025T190221Z-f4d632a7-n8n-data.tar.gz` (Docker volume mounted at `/home/node/.n8n`)

All three files were checked non-empty and SHA-256 checksums were recorded in the deployment output. No credential values were included in the output.

## Verification

- `n8n --version` inside the live container returned `2.44.6`.
- `docker inspect` showed the n8n image `n8nio/n8n:2.44.6` and the matching Coolify-managed runner container, both `running` with zero restarts at verification time.
- The public `https://automations.livetransparent.com/healthz/readiness` endpoint initially returned HTTP 502 during startup, then returned HTTP 200 with `{"status":"ok"}` after startup completed.
- n8n startup logs showed the task broker ready on port 5679, both JavaScript and Python launchers registered, and the migrations completed.
- Local Compose validation and `git diff --check` passed.

## Follow-up

- Execution `1193844`, `LT - Partnership Reply Poller`, was marked `crashed` while the n8n container restarted. Its next natural scheduled execution `1193871` succeeded at 2026-10-25 19:15:34 UTC (stopped at 19:16:03 UTC). No manual replay was performed.
- No workflow was manually executed as an upgrade smoke test, avoiding the risk of triggering production sends or CRM writes.

## EOS Closeout

- Changes are limited to this handoff, `AGENTS.md`, `Project Status and Next Steps.md`, and `n8n/docker-compose.yml`.
- Final review and checks were completed on branch `codex/social-outreach-sync`; these files were committed and pushed to the matching origin branch in this closeout.
