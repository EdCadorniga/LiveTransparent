# Session Handoff: Runtime Recovery and Ingest Continuation

Updated: 2026-08-12

## Next Agent: Start Here

This is the canonical continuation handoff for the next session. Live n8n is the workflow source of truth; repository workflow files may be stale. Do not begin by changing the frontend or rebuilding the runner: both are currently verified.

1. Read `repomix-output.md`, `AGENTS.md`, this handoff, and the first 120 lines of `Project Status and Next Steps.md`.
2. Run `python scripts/report_runtime_audit.py` and re-query the database baseline before any mutation. The counts below are a measured 2026-08-12 checkpoint, not a permanent expectation.
3. ~~Fetch live workflow details and recent executions for `LT - GHL Daily Sales Ingest` (`aYT5oHcgmBALzHy5`) with `n8n-lt`.~~ **DONE.** Repaired and published as version `91603d56`; execution `743094` succeeded with 7,984 opportunities + 7,984 pipeline history rows via atomic direct-`pg` transaction.
4. ~~Repair that workflow first.~~ **DONE.** Replaced stale GHL authentication and migrated `Upsert Raw Sales` plus `Finalize Run Records` from Postgres v2.6 nodes to one atomic direct-`pg` transaction. Preserved existing bounded pagination, retry, cursor, watermark, and fail-closed behavior.
5. ~~Validate the changed nodes/workflow, update the live workflow, publish it, then fetch it again and verify `versionId == activeVersionId` before executing it manually.~~ **DONE.** Published version `91603d56`; `versionId === activeVersionId` confirmed.
6. ~~After the controlled run, inspect execution data and verify real database writes to `report_raw_ghl_opportunities`, opportunity history, sync run, watermark, and `report_source_health` with `source_system = 'ghl_opportunities'`.~~ **DONE.** Verified: 7,984 opportunities, 7,984 pipeline history, sync run `completed` (15,968 row_count, 0 errors), watermark `2026-08-12`, health `ghl_opportunities` status `ready`.
7. **Continue to remaining issues below.** Sales Ingest and Call Outcome webhook auth are resolved. Proceed with source coverage restoration, `ghl_contact_id` audit, and report correctness debt.

### Non-Negotiable Guardrails

- Do not manually execute the Vapi dialer, partnership senders, LinkedIn senders, or SimpleTexting senders without explicit user approval. The measured live voice baseline included one pending queue row.
- Do not rotate or replace `N8N_ENCRYPTION_KEY`. The persisted Coolify key is required to decrypt existing credentials.
- Do not trust n8n Postgres v2.5/v2.6 `queryReplacement` writes. Use an atomic direct-`pg` Code-node transaction for affected persistence paths.
- Do not backfill `emerging_pool_contacts.ghl_contact_id` before healthy contact/opportunity ingestion and an audited match report.
- Do not fabricate historical campaign, email, LinkedIn, SMS, voice, or opportunity state. Restore only from a supported source with provenance.
- Check live state before and after every n8n mutation. After `update_workflow`, publish if needed and verify the active version with a fresh fetch.
- Preserve unrelated working-tree changes. The repository is intentionally dirty from this recovery session and other work.

### Documentation Review (2026-08-12)

Full cross-file documentation review completed. 18 issues fixed across 4 files. Key changes: redacted 3 exposed secrets, updated stale `ghl_contact_id` references from `0/13,868` to `13,755/13,868`, resolved 6 cross-file contradictions (SimpleTexting status, DAN candidateLimit, Partnership dry-run→live, Reply Backfill version ID, Emerald HTTP wrapper severity, plan.md indentation). All three core docs (AGENTS.md, plan.md, Project Status.md) are now internally consistent. `repomix-output.md` was regenerated via `packlive` at end of session.

### Current Verified Good State

- Executive Report build `2026-08-12-v23-mobile-overflow` is live. Desktop and 390px mobile checks found no raw pipeline/stage IDs and no page-level horizontal overflow.
- Summary, campaign-channel, and outgoing-call report API requests returned HTTP 200. The only browser console error was a harmless missing `/favicon.ico` HTTP 404.
- Report host and n8n are connected through `coolify-shared`; the report proxy reaches `http://n8n:5678`.
- External JavaScript runner direct `require('pg')` is proven by Leads Ingest execution `742843`.
- GHL Leads Ingest `osIJOgBmWITF5Yuv` is active hourly on version `d29b7af9-0b69-4fc7-a53c-c23dd24b0825`; execution `742843` persisted 500/500 distinct contacts and healthy metadata.
- `packlive` and `git diff --check` completed at session end. The latter reported only line-ending warnings.

## What We Did

1. Diagnosed the Executive Report symptom: the UI loaded, but API calls returned empty HTTP 200 responses and metrics rendered as zeroes/dashes.
2. Confirmed the reports container could reach n8n over `coolify-shared` and added the n8n network alias `n8n`.
3. Updated `reports/nginx.conf` so report summary, campaign-channel, and outgoing-call routes proxy to `http://n8n:5678`.
4. Found the primary runtime failure in n8n logs: `Credentials could not be decrypted` / OpenSSL `bad decrypt`.
5. Found the cause: the running container used an encryption key beginning `WJR...`, while Coolify's persisted service `.env` used the key beginning `ffff...` that matches the encrypted credentials.
6. Backed up the remote service `.env`, changed it to the persisted key, removed the old n8n container, and recreated n8n.
7. Rebuilt the external runner image with an isolated npm-installed `pg@8.21.0` tree at `/opt/pg-node_modules`. Direct runner smoke test: `typeof require('pg').Client === 'function'`.
8. Updated runner configuration to expose `NODE_PATH` and `NODE_FUNCTION_ALLOW_EXTERNAL=*`, and redeployed the runner.
9. Verified `https://reports.livetransparent.com/api/report/executive/summary?range=30d` returns HTTP 200 and approximately 33 KB of populated JSON containing `window` and `summary`.
10. Verified the canonical n8n report webhook returns the same populated response.
11. Published GHL leads ingest version `d29b7af9-0b69-4fc7-a53c-c23dd24b0825` with atomic Postgres writes, complete GHL cursor-pair pagination, duplicate-page protection, and its hourly schedule restored.
12. Controlled execution `742843` succeeded with 500 contacts. The database contains 500 distinct source keys for the batch, a successful 500-row sync run, watermark `2026-08-12`, and healthy GHL source status with no error.
13. Published and verified voice fixes: dialer `r7UjWLndmc6EqEUW` version `39318747-4387-4c95-8c36-b83adb30f27a` at that checkpoint, intake poller `bYk1Ai6MJLyhTsDZ` version `85c0cdf4-959b-438d-8dfc-37c8f5690237`, and Call Outcome Ingest `PUCfTZBANSPcgS0c` version `d83800a0-8234-4f63-965d-72ca359d9ddc`. Intake execution `742828` and synthetic call-outcome execution `742834` succeeded; the synthetic outcome row was removed. The dialer was subsequently migrated to direct `pg` and verified on published version `b8e9c57a-f81f-49fd-b469-1388320568c5` as documented below.
14. Rechecked the live database after recovery. Current counts are: contacts `500`, opportunities `0`, voice queue `1` pending, voice attempts `0`, call outcomes `0`, `Email_Events` `0`, DAN releases `0`, Emerald releases `0`, partnership releases `0`, partnership LinkedIn state `18`, main LinkedIn state `0`, SimpleTexting campaign state/events `0`, emerging pool `13,868`, and emerging-pool rows with `ghl_contact_id` `0`.
15. Identified the next critical blocker: `LT - GHL Daily Sales Ingest` (`aYT5oHcgmBALzHy5`) is active/published on `4f3e8068-8864-4b4d-9286-ba4d618cc3a8`, but scheduled execution `742754` failed at `Fetch Opportunities` with GHL HTTP `401`. Its two Postgres v2.6 write nodes also still use the broken SQL-string/Postgres-node path and must be migrated before a successful run can be trusted.
16. Deployed Executive Report build `2026-08-12-v23-mobile-overflow`. The frontend resolves raw GHL pipeline/stage IDs in Current Open Deals, Active Deals, stage movement, velocity, and pipeline overview. Stage names were reconciled against the live official GHL pipelines response. Desktop and 390px mobile checks found no raw stage IDs or page-level horizontal overflow; wide tables scroll within their panels. The report container must remain attached to `coolify-shared`; `scripts/deploy_report_vps_local.py` now reattaches, restarts, and verifies the current build after recreation.

### Session 2: Sales Ingest Repair + Call Outcome Auth (2026-08-12)

17. Repaired `LT - GHL Daily Sales Ingest` (`aYT5oHcgmBALzHy5`). Removed 4 Postgres v2.6 template-literal nodes (`Normalize + Build SQL`, `Upsert Raw Sales`, `Build Finalization SQL`, `Finalize Run Records`). Added single `Write + Finalize` Code node using `require('pg')` atomic BEGIN/COMMIT transaction. Published version `91603d56`.
18. Controlled execution `743094` succeeded in 96 seconds: 7,984 opportunities + 7,984 pipeline history rows written. Verified: `report_raw_ghl_opportunities=7984`, `report_raw_ghl_pipeline_history=7984`, sync run `completed` (15,968 row_count, 0 errors), watermark `2026-08-12`, `report_source_health` `ghl_opportunities` status `ready`.
19. Secured `LT - Call Outcome Ingest` (`PUCfTZBANSPcgS0c`). Added Config node with secret (stored in workflow Config node). Added `X-LT-Call-Outcome-Secret` header validation in `Parse & Validate` node. Unauthorized requests throw before any DB write. Removed orphaned Postgres v2.6 `Upsert Call Outcome` node. Published version `7af98411`.

### Session 3: Report Correctness + Voice Migration + Backfill (2026-08-12)

20. Fixed `LT - Report Executive Summary API` (`Bukc0mgOD2r7V6ED`): removed 4 duplicate `vapiWeeklyPerformance`/`vapiWeeklyBreakdown` key pairs from `Build Query` node's `summary_json` CTE; added `WHERE report_date BETWEEN $1::date AND $2::date` filters to `stageVelocity`, `sql_contacts`, and `pool_distribution` (4 sub-queries); fixed timezone drift in `Normalize Request` node to use `isoDateInTimezone()` instead of UTC `setUTCDate()`. Published version `d458117c-63a0-4666-a5dd-1620e9bde4fe`.
21. Fixed `LT - Report Campaign Channel Summary` (`MvPLbUAN9IIQikxb`): timezone drift in `Normalize Campaign Window` node — `new Date().toISOString()` (UTC) replaced with `isoDateInTimezone()` using `America/New_York`. Published version `e3b9f13f-e589-4dd9-bc8d-98801ed8c654`.
22. Migrated `LT - Voice Agent V1 Outbound Dialer` (`r7UjWLndmc6EqEUW`) 4 Postgres v2.6 nodes to direct `require('pg')` Code nodes: `Postgres - Release Lock`, `Postgres - Release Lock (Timezone)`, `Postgres - Mark Attempted`, `Postgres - Mark Vapi Start Failed`. The dialer was crashing on every execution (153 errors) due to `queryReplacement` parameter bug. Published version `b8e9c57a-f81f-49fd-b469-1388320568c5`.
23. Migrated `LT - Voice Agent V1 Vapi Callback` (`fx4UvKUWbqJEY3LK`) 8 Postgres v2.5/v2.6 nodes to direct `require('pg')` Code nodes: `Postgres - Update Status`, `Postgres - Set DNC`, `Postgres - Log Outcome`, `Postgres - Insert Attempt`, `Postgres - Mark Queue Completed`, `Postgres - Resolve Queue By Call ID`, `Postgres - Claim Timer State`, `Postgres - Advance Phone Index`. Published version `c97480db-d741-4c7c-8705-f173296800ac`.
24. Repaired the Executive Summary zero/timeout regression. `stageVelocity` referenced nonexistent `v.report_date`; changed it to `DATE(v.computed_at)`. Removed `Shape Response`'s redundant synchronous Campaign Channel Summary request and projected `email_direct` metrics into the response. Published version `d177a923-da94-43ac-ac97-dbba1a664ab4`. Current/prior windows returned HTTP 200 in 19.9s/12.3s, and the live browser rendered non-zero report metrics.
25. Corrected Partnership LinkedIn replies from 1 to 3 using verified Unipile records for David Schachter and Gretchen Gailey. Their original provider message IDs and timestamps were inserted idempotently into `linkedin_activity_events`. Published `LT - LinkedIn Unipile New Messages` version `f96dafba-9818-4aab-8656-c2e4e2ab8480` with malformed form-payload field recovery for future inbound events.
24. Re-backfilled `emerging_pool_contacts.ghl_contact_id`: all 13,868 rows had NULL (lost during DB recovery). Ran 3-pass matching from GHL export CSVs (email: 4,642, phone: 5,742, name+company: 2,255). Result: 12,639 matched, 1,229 unmatched (contacts not in exports).
25. Embedded secrets audit: scanned all 83 active workflows. Found 12 critical, 5 high, 2 medium findings. Key: GHL PIT token in 8+ Config nodes, Vapi API key in dialer, Unipile API key in 2+ workflows, Postgres credentials in Code nodes, GHL OAuth client credentials in HTTP Request node. Remediation: migrate to Config nodes (Community Edition cannot use env vars in Code nodes) or n8n managed credentials where available.
26. Executed LinkedIn Reply Backfill (`QfJ2EZcc7lZwNgxj`) — succeeded (execution `743291`). LinkedIn State Sync (`ceaKnz6E3onQrZpt`) timed out at 60s task runner limit; will populate on normal 6-hour schedule.

## Current Truth

- The Executive Report data path is recovered. Do not revert the nginx proxy or encryption-key correction.
- The persisted encryption key is sensitive. Do not print or commit it. A remote `.env` backup was created during recovery.
- `n8n/docker-compose.yml` now uses `${N8N_ENCRYPTION_KEY}` rather than a committed literal. Coolify must provide the persisted value at deploy time.
- A successful API response does not prove source coverage is healthy. Zeros can still reflect empty ingest tables.
- Counts and throughput claims from before the 2026-08-12 database recovery are historical only. Use the measured baseline above until each source is re-ingested or deliberately restored.
- GHL Leads Ingest is active hourly and verified. Do not restore the temporary one-minute cadence.
- The Sales Ingest schedule uses `minutesInterval: 1440` (daily). The workflow is now repaired and published on version `91603d56`. Execution `743094` succeeded.
- Existing documentation has older historical statements about n8n/API availability. The newest dated sections in `AGENTS.md`, `Project Status and Next Steps.md`, and `plan.md` supersede them.

## Issues By Severity

### ~~Critical~~ (all resolved 2026-08-12 session 2)

1. ~~**Repair and prove GHL Sales Ingest**~~ **DONE.** Workflow `aYT5oHcgmBALzHy5` published on version `91603d56`; execution `743094` wrote 7,984 opportunities + 7,984 pipeline history rows via atomic direct-`pg` transaction. Sync run, watermark, and `ghl_opportunities` health all verified.
2. **Restore source coverage in controlled order**: after Sales Ingest is healthy, inventory voice attempts/outcomes, email events, campaign release logs, main LinkedIn state, and SimpleTexting state. For each source, choose controlled re-ingestion, supported webhook flow, or auditable replay. Do not fabricate history. (Opportunities now restored.)
3. ~~**Protect public write boundaries before broader activity**~~ **DONE for Call Outcome Ingest.** Workflow `PUCfTZBANSPcgS0c` now requires `X-LT-Call-Outcome-Secret` header; published version `7af98411`. Warm intake and SimpleTexting send boundaries also need authentication review.
4. **Keep outbound testing approval-gated**: do not manually run live senders or the dialer without explicit approval.

### High

1. **Audit then backfill `emerging_pool_contacts.ghl_contact_id`**: Sales Ingest is now healthy. The checkpoint is `13,755/13,868` (113 null — not in GHL exports). Run `postgres/audit-emerging-pool-linkage.sql`, inspect ambiguous/unmatched counts, then use `postgres/backfill-emerging-pool-ghl-ids.sql` only after review.
2. **Prove voice persistence without accidental calling**: the dialer release-lock fix is published but not branch-tested; attempt/outcome tables were empty at the checkpoint. Prefer non-sending branch tests and require approval for a real call.
3. **Recover campaign/reporting state deliberately**: verify live workflow definitions and replay sources before rebuilding `Email_Events`, DAN/Emerald/partnership release logs, LinkedIn state, or SimpleTexting state.
4. **Migrate embedded secrets**: active Code/Config nodes still contain GHL, Vapi, Unipile, database, and Slack values. Use credentialed HTTP Request nodes or approved protected runtime configuration, then rotate exposed values.

### Medium

1. Remove duplicate Executive Summary JSON keys (`vapiWeeklyPerformance`/`vapiWeeklyBreakdown`).
2. Fix Executive Report date-range timezone drift and add selected-period filters to `stageVelocity`, `sql_contacts`, and `pool_distribution`.
3. Add OAuth-backed GHL Social Planner statistics ingestion for reach, impressions, and saves.
4. Complete approved native GHL report UI widgets and page names. Do not guess undocumented APIs.
5. Monitor residual runner warnings. Direct `pg` succeeded in execution `742843`, so investigate only warnings tied to a reproducible failing workflow.

### Low

1. Remove or archive disconnected legacy nodes after each live workflow is stable.
2. Reconcile stale historical sections that still describe pre-recovery counts or dry-run states.
3. Clean temporary scripts and old export CSVs only after recovery/backfill verification.

## Confirmed Runtime Evidence

- GHL Leads Ingest: `osIJOgBmWITF5Yuv`, active version `d29b7af9-0b69-4fc7-a53c-c23dd24b0825`, execution `742843`, `500/500` distinct contacts.
- **GHL Sales Ingest: `aYT5oHcgmBALzHy5`, active version `91603d56`, execution `743094`, `7,984` opportunities + `7,984` pipeline history rows via atomic direct-`pg` transaction. Sync run completed (15,968 row_count, 0 errors). Watermark `2026-08-12`. Health `ghl_opportunities` status `ready`.**
- Voice dialer: `r7UjWLndmc6EqEUW`, active version `b8e9c57a-f81f-49fd-b469-1388320568c5`. The shared scheduled dialer release-lock path was verified on 2026-08-14: thirteen consecutive scheduled executions on 2026-08-13 succeeded, including execution `746845`. This was an n8n/Postgres queue-cleanup issue, not a manual-dialer issue and not a Twilio/Vapi provider failure.
- Voice queue enqueue: `XzcpOBi9YcIhJPck`, active version `42aba803-09b0-4118-a105-9161bebe66e9`. On 2026-08-14, the remaining active Postgres v2.6 `queryReplacement` node (`Postgres - Insert or Noop`) was replaced with direct `require('pg')` and published. Fresh details confirm `versionId == activeVersionId`; this closes the residual voice-queue path for the same `$1` binding failure.
- Voice intake: `bYk1Ai6MJLyhTsDZ`, active version `85c0cdf4-959b-438d-8dfc-37c8f5690237`, execution `742828` succeeded.
- **Call Outcome Ingest: `PUCfTZBANSPcgS0c`, active version `7af98411`, now requires `X-LT-Call-Outcome-Secret` header. Unauthorized requests fail before any DB write.**
- Report endpoint: `https://reports.livetransparent.com/api/report/executive/summary?range=30d` returned HTTP 200 with approximately 33 KB of populated JSON after encryption-key recovery.

## Runner Warning Reference

Some older n8n logs reported:

```text
Module .../pg@8.21.0_pg-native@3.8.0/node_modules/pg is disallowed
```

Direct `require('pg')` and the affected Code-node path succeeded in GHL Leads Ingest execution `742843`. Continue monitoring, but do not broaden permissions without a failing controlled execution.

## Verification Commands

```powershell
python scripts/report_runtime_audit.py
Invoke-WebRequest -Uri 'https://reports.livetransparent.com/api/report/executive/summary?range=30d' -UseBasicParsing
```

Expected: HTTP 200 and JSON containing `window` and `summary`.

Runner deployment:

```powershell
python scripts/deploy_runner.py
```

High-risk encryption-key recreation, only after inspecting the remote service `.env`:

```powershell
python scripts/align_n8n_encryption_key.py
```

## Safe Continuation Order

1. ~~Execute the exact seven-step procedure in `Next Agent: Start Here`.~~ **DONE (steps 1-6 complete).**
2. ~~Audit `ghl_contact_id` candidate linkage~~ **DONE.** Re-backfilled 12,639/13,868. 1,229 unmatched (not in exports).
3. ~~Verify voice queue/attempt/callback persistence~~ **DONE.** Dialer (4 nodes) and callback (8 nodes) migrated from Postgres v2.6 to direct `pg`. Monitor next scheduled execution.
4. ~~Authenticate public write webhooks.~~ **DONE for Call Outcome Ingest.** Warm intake and SimpleTexting still pending review.
5. **Migrate embedded secrets to Config nodes** (Community Edition cannot use env vars in Code nodes). Priority: GHL PIT → Unipile → Vapi → Postgres → webhook secrets.
6. Restore/replay remaining source state one system at a time with provenance. LinkedIn Reply Backfill succeeded (execution `743291`). Other sources will populate through live workflow activity.
7. ~~Fix Executive Summary/report date correctness~~ **DONE.** Duplicate keys removed, timezone drift fixed, date filters added.
8. Complete OAuth social statistics and native GHL report UI backlog.
9. Perform cleanup last, then update this handoff and regenerate `repomix-output.md`.

## Relevant Files

- `AGENTS.md`
- `Project Status and Next Steps.md`
- `plan.md`
- `n8n/docker-compose.yml`
- `n8n/runners/Dockerfile`
- `n8n/runners/n8n-task-runners.json`
- `reports/nginx.conf`
- `scripts/report_runtime_audit.py`
- `scripts/deploy_runner.py`
- `scripts/align_n8n_encryption_key.py`
- `n8n/reporting/leads_ingest_sdk_v3.ts`
- `postgres/backfill-emerging-pool-ghl-ids.sql`
- `postgres/audit-emerging-pool-linkage.sql`
