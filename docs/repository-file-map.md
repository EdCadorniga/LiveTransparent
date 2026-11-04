# LiveTransparent Repository File Map

Updated: 2026-09-17

> **Freshness notice (2026-11-05):** the script filename lists/counts below are a 2026-09-17 snapshot and are stale. A bounded metadata-only census now finds 242 script-like files (1,256,534 bytes) under `scripts/`, compared with the older per-domain lists below. See [`scripts/README.md`](../scripts/README.md) for current directory counts. Do not use the old lists as a complete inventory or infer that any listed/unlisted file is safe, maintained, or disposable. Exact-path review remains part of the developer transition; nothing was run or removed for this census.
>
> **Dated exact-path evidence (2026-11-05), supersedes treating this map as an inventory:** reviewed per-path classification with sensitivity/doc-reference data is now maintained as a transition artifact — see [`docs/transition/scripts-classification-2026-11-05.md`](transition/scripts-classification-2026-11-05.md), [`docs/transition/n8n-archive-classification-2026-11-05.md`](transition/n8n-archive-classification-2026-11-05.md), and [`docs/transition/tmp-artifacts-classification-2026-11-05.md`](transition/tmp-artifacts-classification-2026-11-05.md) (all review-only proposals, not deletions).
>
> **Cleanup execution status (2026-11-05, batches 0–4):** the transition cleanup batches were executed under Ed's YOLO mandate with dated recovery manifests — see [`docs/transition/retention-manifest-2026-11-05-batch-0-regenerable-junk.md`](transition/retention-manifest-2026-11-05-batch-0-regenerable-junk.md) (bytecode), [`retention-manifest-2026-11-05-batch-1-credential-hardening.md`](transition/retention-manifest-2026-11-05-batch-1-credential-hardening.md) (9 files redacted to `.env` loaders; 1 JWT capture archived), [`retention-manifest-2026-11-05-batch-2-tmp-captures.md`](transition/retention-manifest-2026-11-05-batch-2-tmp-captures.md) (36 tmp files moved to `local-archive/campaign-template-captures-2026-11/` and `local-archive/report-captures-2026-11/`), [`retention-manifest-2026-11-05-batch-3-archive-dedup.md`](transition/retention-manifest-2026-11-05-batch-3-archive-dedup.md) (2 hash-duplicate archive files deleted; archive now 66 files), and [`retention-manifest-2026-11-05-batch-4-node-modules.md`](transition/retention-manifest-2026-11-05-batch-4-node-modules.md) (`node_modules/` deleted; regenerate with `npm ci` from the retained lockfile). `tmp/` and root `tmp*` no longer exist in the working tree; the sections below mentioning them are historical.

This map describes the repository boundaries after the file-organization cleanup. Git and the live system remain authoritative for current state; this file is a navigation index, not a substitute for runbooks.

## Operating boundaries

- `scripts/` — versioned, reviewed automation grouped by operational domain. See `scripts/README.md`.
- `local-scripts/` — ignored operator-only helpers, probes, and campaign working files; may contain machine-specific or sensitive runtime material.
- `local-archive/` — ignored historical n8n exports/backups and one-off patch inputs; never redeploy without reconciliation.
- `data/runs/` — dated campaign/import artifacts, notes, reconciliation outputs, and machine-readable snapshots.
- `.monitor/` — active monitor state/logs; do not prune while the monitor depends on them.
- `.tmp/`, `.npm-cache/`, `.playwright-cli/`, `.playwright-mcp/` — disposable ignored runtime/browser artifacts; safe to recreate.
- `.env` — local secret material; presence may be documented, contents must not be copied into repository maps.

## Dated run bundles

- `data/runs/2026-09-16-apollo-vp-ghl/` — Apollo VP/C-Suite September 2026 GHL preparation and reconciliation outputs, including `IMPORT_NOTES.md`, prepared CSVs, import logs, `summary.json`, and tagged-contact snapshots.
- `repeated linkedin messages.png` remains at repository root intentionally untracked because it contains identifying prospect data; do not stage or relocate without a separate decision.

## Versioned scripts by domain

### `scripts/apollo/`

2 files.
- `add_apollo_fields.py`
- `remove_apollo.py`

### `scripts/deploy/`

8 files.
- `deploy_acceptance_checker.py`
- `deploy_report_proxy.py`
- `deploy_report_vps.py`
- `deploy_report_vps_local.py`
- `deploy_runner.py`
- `fix_runner_pg.py`
- `patch_runner_pg.py`
- `restart_n8n.py`

### `scripts/diagnostics/`

39 files.
- `_check_npm.py`
- `_check_npm_shim.py`
- `_check_pg_v2.py`
- `_check_pg_version.py`
- `_check_runner.py`
- `_find_pg.py`
- `check_db.py`
- `check_db2.py`
- `check_dms.py`
- `check_partnership_db.py`
- `check_runner_paths.py`
- `check_send_status.py`
- `db_check.py`
- `db_check2.py`
- `db_check3.py`
- `db_check4.py`
- `db_check5.py`
- `db_check6.py`
- `db_check7.py`
- `db_check8.py`
- `db_check9.py`
- `db_query.py`
- `find_anywhere.py`
- `find_pg.py`
- `find_pg_protocol.py`
- `find_table.py`
- `find_table2.py`
- `query_pg.py`
- `ssh_baseline.py`
- `ssh_fix1_edit.py`
- `ssh_fix2_apply.py`
- `ssh_health2.py`
- `ssh_inv_tcp.py`
- `ssh_pgrecheck.py`
- `ssh_probe2.py`
- `ssh_probe3.py`
- `ssh_probe4.py`
- `ssh_probe5.py`
- `ssh_verify_fix.py`

### `scripts/email/`

2 files.
- `gmail_read.py`
- `gmail_send.py`

### `scripts/emerald/`

5 files.
- `check_emerald.py`
- `clean_august_2026_emerald_contacts.ps1`
- `enroll_august_2026_emerald.ps1`
- `reconcile_august_2026_emerald_live.ps1`
- `run_dispensaries.py`

### `scripts/instagram/`

8 files.
- `apply_instagram_company_dm_bootstrap.py`
- `backfill_instagram_reporting_events.py`
- `batch_instagram_validate_and_send.py`
- `fix_instagram_reporting_db.py`
- `match_instagram_company_dm_contacts.py`
- `process_ig_fb_local.js`
- `reset_instagram_test_401_failures.py`
- `review_company_instagram_sources.py`

### `scripts/linkedin/`

14 files.
- `enforce_linkedin_daily_limit.py`
- `fix_linkedin_backfill_outbound_direction.py`
- `fix_linkedin_dm_pipeline.py`
- `fix_linkedin_inbound_response_and_jsonb.py`
- `fix_linkedin_sanitize_double_escape.py`
- `fix_linkedin_state_upsert.py`
- `guard_linkedin_requested_state.py`
- `harden_linkedin_dm_dedup.py`
- `load_linkedin_backfill_worklist.py`
- `patch_linkedin_backfill_workflow.py`
- `recover_missed_linkedin_reply.py`
- `run_linkedin_backfill_batch.py`
- `update_follower_dm.py`
- `watch_fix.py`

### `scripts/monitoring/`

1 files.
- `monitor.py`

### `scripts/n8n/`

18 files.
- `align_n8n_encryption_key.py`
- `check_n8n.py`
- `check_n8n_db.py`
- `copy_to_n8n.py`
- `copy_to_n8n_files.py`
- `fix_intake_poller.js`
- `fix_sheets_node.py`
- `fix_workflow.py`
- `inventory_n8n_pits.py`
- `n8n_api_probe.py`
- `n8n_exec_check.py`
- `n8n_find_pgerr.py`
- `n8n_ga4_err.py`
- `n8n_vapi_check.py`
- `patch_simpletexting_auth.ps1`
- `patch_simpletexting_event_safety.ps1`
- `refresh_ghl_oauth_token.py`
- `repair_failed_ghl_pits.py`

### `scripts/partnerships/`

6 files.
- `clean_partnership_data.py`
- `import_partnership_candidates.py`
- `reconcile_august_2026_partnership_live.ps1`
- `repair_partnership_owners.py`
- `seed_partnership_linkedin_state.py`
- `tag_august_26_partnership_contacts.ps1`

### `scripts/social-reporting/`

6 files.
- `audit_social_reporting.py`
- `fix_brands_code.py`
- `fix_executive_report_metrics.py`
- `fix_social_mql_reporting.py`
- `fix_social_reporting_accuracy.py`
- `report_runtime_audit.py`

### `scripts/utilities/`

8 files.
- `_run_commands.py`
- `decrypt_credential.py`
- `fix_parse_csv.py`
- `fix_simpletexting_boundaries.py`
- `upload_updated.py`
- `vapi_audit.py`
- `verify_tags.py`
- `x.py`

## Maintenance rules

- Add reusable/versioned automation to the relevant `scripts/<domain>/` directory, not the scripts root.
- Keep one-off operator probes and machine-specific helpers in ignored `local-scripts/`.
- Put campaign/import outputs in a dated `data/runs/YYYY-MM-DD-<slug>/` bundle with a local README or notes file.
- Put historical n8n exports in `local-archive/n8n/`; do not treat them as deployable source.
- Remove generated caches only after confirming they are not active monitor/runtime state.
- Update this map when adding a new script category or run bundle.
