# Proposed retention register — review only, 2026-11-04

**Status: NOT APPROVED for movement or deletion.** This is family-level triage, not a per-file deletion manifest. File counts are local recursive counts at review time (include ignored/untracked files). Before any batch, expand candidates to exact paths with sizes, references/dependencies, sensitivity, owner, recovery source, retention policy and explicit approval. No content was removed or executed.

> **Update 2026-11-05 (later, same day):** the repository-side families governed by this
> register were executed within Ed's explicit YOLO cleanup mandate, per batch, with dated
> recovery manifests — see
> [batch 0](retention-manifest-2026-11-05-batch-0-regenerable-junk.md),
> [batch 1](retention-manifest-2026-11-05-batch-1-credential-hardening.md),
> [batch 2](retention-manifest-2026-11-05-batch-2-tmp-captures.md),
> [batch 3](retention-manifest-2026-11-05-batch-3-archive-dedup.md), and
> [batch 4](retention-manifest-2026-11-05-batch-4-node-modules.md), plus the ledger rows in
> [docs/transition-plan.md](../transition-plan.md). Settings unchanged by execution:
> `local-scripts/linkedin-invite-withdrawals/` remains held (310-invitation boundary), and
> the `scripts/`+`New Campaigns October 2026/`+`marketing/` families were **kept** (only the
> credential-hardening edits listed in batch 1 touched them). This register's strike-through
> era is historical.

| Family (observed files) | Proposed classification | Reason / required review before action |
|---|---|---|
| `scripts/` (284) | **Keep** maintained source; **consolidate** demonstrable duplicates only | Production repair, deployment and migration helpers may be sole reproducible source. Scan per-script references and secrets safely before choosing candidates. |
| `docs/sessions/` (107) | **Keep** dated project evidence; **archive** only superseded copies with confirmed replacement | Do not erase project chronology merely because current status changed. |
| `local-scripts/` (247) | **Needs owner decision**; mix of keep/archive/delete candidates | Includes withdrawal ledger/captures and operator scripts. Confirm worker state, ledger and provenance before any proposal about that subfamily. Ignored ≠ disposable. |
| `local-archive/n8n/` (68) | **Archive / needs owner decision** | Compare critical workflow rollback versions with fresh live graphs and approved restricted backup location before any deduplication. |
| `tmp/` (27) plus root `tmp*` (not enumerated here) | **Delete candidate only after per-path review** | Scratch appearance does not prove absence of incident evidence or secrets. |
| `node_modules/` (4,617) | **Delete candidate only after lockfile/build verification and owner approval** | Regenerable only when package manifest, lockfile and installation procedure are confirmed; local user workspace remains untouched. |
| Docker volumes and `/root/n8n-upgrade-backups/` | **Keep / needs owner decision** | One-time pre-upgrade rollback set; no scheduled backup or restore test verified. No Docker/host cleanup in this manifest. |

Personal-only material is **outside this register** and excluded from the developer handoff; no contents inspected or copied. Owner must arrange separate disposition. Next gate: agree on restricted backup owner/destination and retention, verify caller/worker and recovery dependencies, then generate a per-path manifest for review before any cleanup.

**Members of this register are review-only data. Nothing in the linked exact-path artifacts assigns a retention action as approved; they are evidence for owner decision-making. Exact-path classifications are maintained as dated artifacts, not duplicated here:**
- [Scripts classification — 2026-11-05](scripts-classification-2026-11-05.md) — per-path table for all 443 script-like files in `scripts/`, `local-scripts/`, `tools/`, `marketing/`, and `New Campaigns October 2026/` (460 path rows, sizes, mtimes, markdown-reference counts, 12 sensitive-hit rows for owner review; no values emitted).
- [n8n archive classification — 2026-11-05](n8n-archive-classification-2026-11-05.md) — per-path table for the 68-file `local-archive/n8n/` tree; 13 workflow IDs compared against current live versions (all archived JSON rows differ from the current published version → rollback evidence, not current source).
- [tmp artifacts classification — 2026-11-05](tmp-artifacts-classification-2026-11-05.md) — 36 paths in `tmp/` and root `tmp*`; bounded zero credential-pattern hits; all marked keep pending content review except `.pyc`-style regenerable kinds if any appear later.
- [Coolify saved-configuration read — 2026-11-05](coolify-saved-config-2026-11-05.md) — first saved-config facts for the Coolify project (n8n 2.44.6 with runner, postgres-shared healthy; reports-app destination network `coolify` while running attaches also to `coolify-shared` — the earlier drift statement is now grounded in saved data).


## Bounded exact-path follow-up — 2026-11-05

Directory-entry review of the ignored `local-archive/n8n/` tree exposed these provisional groups. **No contents were read; this is not a delete/archive approval or complete per-file manifest.** All remain untouched pending comparison to the fresh n8n-lt state, sensitivity review, recovery decision, and explicit owner approval.

| Exact path/group | Observed entries | Provisional classification | Open dependency / recovery caveat |
|---|---|---|---|
| `local-archive/n8n/backups/workflow_Q3Ivnwe4z2Y3cD7A*` | Five files: four timestamped `.json` snapshots and one `.ts` snapshot. | **Keep candidate / needs review** | Related to the SimpleTexting send workflow ID; compare versions against fresh live state and determine whether any is a unique rollback artifact. Contents and secret/PII status unknown. |
| `local-archive/n8n/voice-agent/` and `local-archive/n8n/voice-agent/n8n-workflow/` | Four top-level `.json`/`.mjs`/`.ts`-style workflow artifacts and four nested Vapi workflow JSON files. | **Keep source/rollback candidate / needs review** | Could be source or rollback material for live voice paths. No current-source/last-known-good mapping or sensitivity check completed. |
| `local-archive/n8n/workflows/` | 52 named JSON/TS artifacts, including dated `before-*` snapshots and workflow blueprints. | **Archive/keep candidate / needs review** | Mixed history and potential rollback sources. Each needs exact live ID/version, source, dependency, sensitivity, and recovery mapping before disposition. |
| `local-archive/n8n/test-ghl-search.js`; `local-archive/n8n/update-dispatcher-message.mjs` | Two root helper files. | **Needs owner decision** | Purpose, side effects, secret/PII exposure, and caller/reference status not established from names. Contents were not opened. |

| `local-scripts/linkedin-invite-withdrawals/` | 42 directory entries, including capture/report snapshots, withdrawal journals, status/log files, and three Python helpers. | **Hold / owner decision; do not inspect or alter in this pass** | This is a sensitive active/previously authorized cleanup artifact family. The transition ledger records 310 pending provider invitations without ledger rows and a separate held `ready` state conflict. The latest handoff explicitly forbids touching the worker, snapshots, provider, ledger, or held row. Worker/process state must not be inferred from filenames; do not read/run the worker or inspect snapshots. Further investigation requires exact owner-approved scope. |

This follow-up improves path specificity but does not satisfy the per-file inventory requirement. No files were executed, opened, moved, or deleted.

## Temporary-artifact names-only follow-up — 2026-11-05

The `tmp/` directory contains 27 files: `action-editor.png`; `alcohol-1.png` through `alcohol-5.png`; `alcohol-action-config.yml`; `alcohol-builder.yml`; `alcohol-editor-load.png`; `alcohol-email-template-1-before-cleanup.png`; `alcohol-frame-direct.png`; `alcohol-frame-direct2.png`; `alcohol-parent-confirm.png`; `alcohol-template-editor-state.png`; `alcohol-template2-state.png`; `alcohol-template5-verified.png`; `alcohol-workflow-loaded.png`; `alcohol-workflow-tree.yml`; `alcohol-workflow.png`; `cannabis-new-1.png` through `cannabis-new-5.png`; `email1-config.yml`; `email1-focused.yml`; and `monaco-select-all.png`. These may be campaign UI/evidence captures; **keep pending content sensitivity, provenance, and dependency review**. Contents were not opened.

Nine root `tmp*` files were enumerated by path and size only: `tmp_Bukc0mgOD2r7V6ED.json` (234,474 bytes), `tmp_campaign_query.sql` (21,455), `tmp_knc2wxe4pyYIJ5tw.json` (25,703), `tmp_latest_v1_exec.json` (140,690), `tmp_MvPLbUAN9IIQikxb.json` (65,459), `tmp_summary_query.js` (98,428), `tmp_v1_facts_workflow.json` (40,092), `tmp_v1_headers.txt` (0), and `tmp_weekly_response.json` (11,638). **Keep / needs review**: names suggest report SQL, workflow definitions, headers, or execution/response captures that may contain credentials or personal/customer data. No contents were read. This is a provisional retention note, not a disposition; no cleanup is authorized.

The family count in the opening table (`scripts/` = 284) belongs to the earlier family-level inventory and is not comparable to the 2026-11-05 bounded extension-filter census (`scripts/` = 242 script-like files). Treat the earlier figure as stale, not evidence of files removed. Neither count constitutes a reviewed per-file classification.
