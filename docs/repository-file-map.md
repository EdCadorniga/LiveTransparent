# LiveTransparent Repository File Map

Entry-point reconciliation: 2026-11-05 local-clock (script directories rechecked against this checkout)

> **Freshness notice:** the script filename lists below preserve a 2026-09-17 snapshot and are incomplete. The current directory mapping and exact-path inventory are linked below. A path appearing in either list is not evidence that its script is safe, maintained, or approved to run.
>
> **Dated exact-path evidence (2026-11-05), supersedes treating this map as an inventory:** reviewed per-path classification with sensitivity/doc-reference data is now maintained as a transition artifact — see [`docs/transition/scripts-classification-2026-11-05.md`](transition/scripts-classification-2026-11-05.md), [`docs/transition/n8n-archive-classification-2026-11-05.md`](transition/n8n-archive-classification-2026-11-05.md), and [`docs/transition/tmp-artifacts-classification-2026-11-05.md`](transition/tmp-artifacts-classification-2026-11-05.md) (all review-only proposals, not deletions).
>
> **Cleanup execution status (2026-11-05, batches 0–4):** the transition cleanup batches were executed under Ed's YOLO mandate with dated recovery manifests — see [`docs/transition/retention-manifest-2026-11-05-batch-0-regenerable-junk.md`](transition/retention-manifest-2026-11-05-batch-0-regenerable-junk.md) (bytecode), [`retention-manifest-2026-11-05-batch-1-credential-hardening.md`](transition/retention-manifest-2026-11-05-batch-1-credential-hardening.md) (9 files redacted to `.env` loaders; 1 JWT capture archived), [`retention-manifest-2026-11-05-batch-2-tmp-captures.md`](transition/retention-manifest-2026-11-05-batch-2-tmp-captures.md) (36 tmp files moved to `local-archive/campaign-template-captures-2026-11/` and `local-archive/report-captures-2026-11/`), [`retention-manifest-2026-11-05-batch-3-archive-dedup.md`](transition/retention-manifest-2026-11-05-batch-3-archive-dedup.md) (2 hash-duplicate archive files deleted; archive now 66 files), and [`retention-manifest-2026-11-05-batch-4-node-modules.md`](transition/retention-manifest-2026-11-05-batch-4-node-modules.md) (`node_modules/` deleted; regenerate with `npm ci` from the retained lockfile). `tmp/` and root `tmp*` no longer exist in the working tree; the sections below mentioning them are historical.

This map combines a current directory index with a **historical filename snapshot**, not a complete post-cleanup inventory. The [organization census](transition/repository-organization-2026-11-06.md), [closeout decisions](transition/closeout-decisions-2026-11-05.md), Git and fresh authorized live reads supersede old per-file lists. Do not use listed paths as run/deploy instructions.

## Operating boundaries

- `scripts/` — versioned source/history grouped by operational domain; **none preapproved for operational execution**. See [`scripts/README.md`](../scripts/README.md).
- `local-scripts/` — ignored operator-only helpers, probes, and campaign working files; may contain machine-specific or sensitive runtime material. `local-scripts/linkedin-invite-withdrawals/` is held untouched while the 310-unledgered-invitation investigation is open.
- `local-archive/` — ignored historical captures/archives; never redeploy without reconciliation. Dated archive destinations (2026-11-05): `n8n/`, `campaign-template-captures-2026-11/`, `report-captures-2026-11/`, `historical-captures-2026-11/`, `repomix-authoring-2026-11/`, `contact-division-2026-07/`, `ghl-export-csvs-2026-11/`, `contacts-import-august-2026/`, `campaign-design-docx-2026-11/` (incl. `_qa_remove_exec/` staging), `scripts-legacy-2026-07/`.
- `data/runs/` — dated campaign/import artifacts, notes, reconciliation outputs, and machine-readable snapshots.
- `.monitor/` — active monitor state/logs; do not prune while the monitor depends on them.
- `.tmp/`, `.npm-cache/`, `.playwright-cli/` — runtime/browser cache families; check ownership and use before any future deletion. **(2026-11-05: `.playwright-mcp/` and `.pip-cache/` were removed under manifest batch 5.)**
- `.env` — local secret material; presence may be documented, contents must not be copied into repository maps.

### Dated reorganization note (2026-11-05, batches 5–11)

Per [`docs/transition/repository-organization-2026-11-06.md`](transition/repository-organization-2026-11-06.md) and
manifests [`retention-manifest-2026-11-06-batch-…`](transition/retention-manifest-2026-11-06-batch-5-regenerable-caches.md) 5–11:

- Root loose files were resolved: report-era captures (16 files), contact-division working
  files (12), three `Export_Contacts_*.csv`, `Contacts added August 25 2026/`, the root
  `_*.py` probes, the 8 campaign/design `.docx`, `_qa_remove_exec/`, and
  `repomix.config.json`/`.repomixignore` were archived (nothing deleted; tracked copies
  removed from the tracked tree in subsequently pushed transition commits (local ignored archive copies are not part of a Git handoff).
- Root `Dockerfile` is **load-bearing** (Coolify `reports.livetransparent_server` builds from
  `/Dockerfile`) — do not move.
- Deleted (regenerable/dedup only): `.pip-cache/`, `.playwright-mcp/`, and one
  byte-identical duplicate in `marketing/email-marketing/cold-outreach-prep/reports/`
  (identical twin retained).
- Kept + documented: `bookstack/` and `qdrant/` (deployable compose templates referenced by
  chatbot/knowledgebase plans), `landing/` (undeployed tracked website build pending owner
  decision), `AppScript for IG and FB enhancement/` (tracked Apps Script sources),
  `.kilo/`, `.qwen/`, `.gemini/` (tool state).
- Out of project scope, untouched at root: the three `Billing Report …` files and
  `repeated linkedin messages.png`.


## Dated run bundles

- `data/runs/2026-09-16-apollo-vp-ghl/` — Apollo VP/C-Suite September 2026 GHL preparation and reconciliation outputs, including `IMPORT_NOTES.md`, prepared CSVs, import logs, `summary.json`, and tagged-contact snapshots.
- `repeated linkedin messages.png` remains at repository root intentionally untracked because it contains identifying prospect data; do not stage or relocate without a separate decision.

## Versioned scripts by domain

**Current directory mapping (filesystem check, 2026-11-05 local clock):** 242 script-like files in `scripts/`. The [exact-path classification](transition/scripts-classification-2026-11-05.md) is the full file inventory; the lists below are historical and incomplete. In particular, 55 files live directly under `scripts/` (mainly reporting helpers), which the older list omitted entirely. Current counts: root 55; `apollo/` 15; `deploy/` 13 (9 directly plus 4 in `deploy/acceptance_checker/`); `diagnostics/` 39; `email/` 2; `emerald/` 5; `instagram/` 8; `linkedin/` 43; `monitoring/` 1; `n8n/` 37; `partnerships/` 6; `social-reporting/` 10; `utilities/` 8. Counts are metadata only, not maintained-toolkit selections.

### Historical filename snapshot (2026-09-17; not a current file map)

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
