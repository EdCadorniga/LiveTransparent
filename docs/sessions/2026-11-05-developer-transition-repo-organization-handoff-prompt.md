# Copy-ready handoff prompt — developer transition, repo organization & completeness audit (2026-11-05)

You are starting the **LiveTransparent developer transition — repository organization &
completeness-audit session** in this repository
(`C:\1_Ed's Active Work\Projects\LiveTransparent`). Read first, in this order:
1. `AGENTS.md` (operating rules/safety).
2. `docs/transition-plan.md` — **the task ledger; update it after every discrete action.**
3. `docs/transition/README.md`, `docs/transition/owner-review-package-2026-11-05.md`.
4. Latest EOS: `docs/sessions/2026-11-05-developer-transition-cleanup-eos.md` (and, before
   it, `docs/sessions/2026-11-05-developer-transition-evidence-eos.md`).
5. The five batch manifests: `docs/transition/retention-manifest-2026-11-05-batch-{0,1,2,3,4}-*.md`.
6. `docs/transition/scripts-classification-2026-11-05.md`,
   `n8n-archive-classification-2026-11-05.md`, `tmp-artifacts-classification-2026-11-05.md`,
   `phase4-source-backup-strategy-2026-11-05.md`, `repository-retention-proposal-2026-11-04.md`,
   plus `docs/repository-file-map.md` and `scripts/README.md`.

Do not stop early; update the ledger after **every** discrete action.

## Mandate (Ed, 2026-11-05, continuing the YOLO/high-autonomy mode)

1. **Completeness audit:** ensure everything planned in `docs/transition-plan.md` was
   executed and that nothing was missed. Verify every ledger row's acceptance criterion is
   met or explicitly blocked-on-owner; hunt for orphaned promises (e.g., "Next:" pointers
   that were never revisited).
2. **Repository organization:** ensure all files in this repo are organized (families
   classified, canonical locations documented, no orphaned/undocumented material).
3. **Repository cleanup:** this repo must be clean of unnecessary files. You may execute
   archive/delete batches yourself for anything matching the plan's own removal categories
   — duplicates whose byte-identical/set content is retained elsewhere, regenerable
   caches/temp/bytecode, superseded-by-date captures with a retained replacement or
   documented archive destination — always with the per-batch manifest protocol below.
   Everything ambiguous, multi-contact, financial/legal, or a sole last-known-good — ask
   Ed or archive-with-note instead of deleting.

## Standing hard boundaries (never violate)

1. **Production stays read-only.** No workflow runs/toggles, sends, CRM writes,
   schema/data changes, service changes, restores, Coolify state changes, credential
   rotations. Any live reads (only if truly needed): use only `n8n-lt`
   (`N8N_LT_API_KEY` from `.env`, base `https://automations.livetransparent.com/api/v1`),
   Coolify panel via SSH tunnel, `docker exec postgres-uokgs4c04ko0s4scccg40cgg psql …`
   read-only catalog; the proven read-only generators under `docs/transition/` are the
   pattern. Do not run classified/other scripts against production.
2. **Untouchable paths:** `local-scripts/linkedin-invite-withdrawals/` (310-unledgered
   invitation investigation open — whole family incl. its `__pycache__`); anything with
   invoice/invoicing path segments; your own personal-only billing documents at the repo
   root (outside project scope — do not open, move, describe, or disposition them);
   VPS/host files and Docker volumes/backups; root `repomix-output.md` (stays deleted;
   never recreate — do NOT confuse this with the leftover authoring files
   `repomix.config.json`/`.repomixignore`, which ARE cleanable candidates); sample-page /
   PII-bearing artifacts like `repeated linkedin messages.png` and the `.env`
   (leave in place).
3. **Never delete a sole last-known-good or live system-of-record artifact**; if the
   archive copy becomes the only copy, it still counts as retained.
4. **Never print/copy secret values** (`.env`, Config-node contents, member exports).
   Keep the PIT-retention decision as recorded; keep `<redacted-pit>` redactions.
5. **No commits unless Ed asks** (he has previously asked to "commit and push all" —
   if he repeats that, do it; otherwise leave the working copy).
6. Preserve the documented operating boundaries (`docs/repository-file-map.md` §Operating
   boundaries, `Sample Landing Page/` boundary, `data/runs/`, `.monitor/`).

## Cleanup execution protocol (per batch, mandatory)

1. Exact-path manifest first: path, bytes, classification basis (quote the plan/artifact),
   dependency result, sensitivity note, recovery, destination →
   `docs/transition/retention-manifest-2026-11-06-batch<N>-<topic>.md`.
   Archive-before-delete into `local-archive/<dated-topic-folder>/` (git-ignored) unless
   the deletion is a pure duplicate/regenerable/empty-path case.
2. Only delete what the manifest covers. Small batches.
3. After each batch: verify paths, `git diff --check`, targeted reference re-check
   (Markdown + scripts referencing moved basenames), update the ledger row + progress note.

## Ordered work

### A. Ledger completeness audit (do this first)

1. Read every row of the transition-plan ledger and the five batch manifests; for each,
   verify the recorded evidence still matches reality today (spot-check: file absence,
   archive contents, `git log --oneline -5`, archive file count = 66 with 0 duplicate
   hashes, the 8 redacted scripts still carry `os.environ` loaders and no literal secrets,
   `local-archive/campaign-template-captures-2026-11/` = 27 files,
   `local-archive/report-captures-2026-11/` = 9 files,
   `local-archive/historical-captures-2026-11/` = 1 file, `node_modules/` absent but
   `package.json`/`package-lock.json` present, only the withdrawal-family `__pycache__`
   remains anywhere).
2. Verify nothing planned was missed: Phases 0–6 acceptance criteria; the ten inventory
   generator runs; the GHL "no fourth app" positive; the PIT retention decision; the
   heading relabels; links validation; classification counts vs disk
   (`scripts/` 242 files — excluding nothing new; the four classification artifacts'
   tables should still reconcile modulo batch-1 redactions only).
3. Record the audit in a dated artifact
   `docs/transition/completeness-audit-2026-11-06.md` with a per-item PASS/BLOCKED-ON-OWNER
   table. Anything found missed is immediately scheduled in this same session (edit the
   ledger, execute with a manifest).

### B. Full-repo census + organization classification (new artifact)

Produce `docs/transition/repository-organization-2026-11-06.md` (read-only enumeration:
path/size/count per family; sample-pattern checks only; never echo contents). This covers
everything NOT in the earlier classification. Known starting points (verified 2026-11-05
first-level listing):

- **Root loose files (~50, ~7.1 MB)**: 3 GHL contact-export CSVs (`Export_Contacts_*` ≈
  1.5 MB / 1.4 MB / 4.9 MB — AGENTS says "delete after use"; the backfill-era uses are
  documented as done — verify, then archive-PII-safely, never bare-delete); report-era captures
  (`campaign-channels-7d.json`, `summary-7d.json`, `summary-prior-7d.json`,
  `outgoing-calls-7d.json`, `corrected-7d-audit.json`,
  `executive-7d-snapshot.md`, `exec_report_mockup_v3 (1).png`, `report-ui.png`,
  `Jason's Call Report.png`, `Marc's Call Report.png`, `followup-workflow-canvas.png`,
  `screenshot_stale_executions.jpg`, `ghl-owner-alignment-*.json`,
  `ghl-followup-workflow*.network-response`); working cohort files
  (`contacts_not_qualified_tag.csv`, `to_move_not_qualified.csv`, `warm_not_qualified_opps.csv`,
  `warm_mql_opportunities.txt`, `warm_new_opportunities.txt`,
  `sales_outreach_qualified_opps.txt`, `Test - Leads - Domains classification.csv`,
  `csv_matched_opps.csv`, `csv_unmatched_opps.csv`, `duplicate_opp_contacts.csv`);
  working remnants (`fix_errors.txt`, `move_errors.txt`, `_check_config.py`,
  `_kill_and_fix.py`, `_mark_enrolled.py`, `Dockerfile`); setup leftovers
  (`repomix.config.json`, `.repomixignore`); supporting docs still probably canonical
  (`executive_report_v1_plan.md`, `improvementPlan.md`, `plan.md`, `AGENTS.md`,
  `Project Specifications.md`, `Project Status and Next Steps.md`, `QWEN.md`).
  The three root `Billing Report … <dates>.docx/.md` files are billing/invoicing
  material — treat as outside-scope per the standing invoice rule: do not open, move,
  describe, aggregate, or disposition them; leave in place. Classify the rest: canonical-keep
  / archive / delete (regenerable/stale) / owner. The historical campaign/design working
  `.docx` set at root
  (`Email Content - Dispensary Attribution Network_ *.docx`,
  `Instagram and FB DM - … .docx`, `Executive Summary Edits .docx`,
  `Remove from Executive Report - v1.docx`,
  `Transparent eCom Business Improvement Plan - Full.docx`) are campaign/design history —
  archive candidates after doc-reference check.
- **Unclassified directories**: `_qa_remove_exec/` (268 KB — name literally says
  remove-exec QA staging), `.pip-cache/` (~55 KB regenerable), `.kilo/`, `.qwen/`
  (tool state; `.gemini/settings.json` is tracked — keep), `bookstack/` (3.5 KB),
  `qdrant/` (618 B — stale engine dir?), `landing/` (69 KB), `AppScript for IG and FB
  enhancement/` (17 KB Apps Script sources — organize/document),
  `Contacts added August 25 2026/` (14.6 MB — import cohort source w/ PII; archive), plus
  the previously classified families (`scripts/` 242 files keep,
  `local-scripts/` 153 (macro: withdrawals family held), `marketing/` 28 classified files
  but the directory is ~333 MB total — the mass is import/source data; needs a
  sub-census), `tools/` 5, `New Campaigns October 2026/` 15 script files (keep pending
  campaign-closure evidence), `docs/sessions/` dated records (keep), `data/` 41.7 MB
  (incl. `data/runs/` documented; `GHL_Ready_*.csv` referenced by n8n docs),
  `Sample Landing Page/` (documented boundary), `GHL Live Transparent CRM/` (runbooks),
  `images/`, `postgres/`, `services/`, `n8n/` (35 tracked sources), `reports/`,
  `local-archive/` (retained archive).
- Also: verify no other stale root files (name patterns like `*.bak`, `~$*`, `*.tmp`,
  `.DS_Store`, `Thumbs.db`), empty directories, and orphaned `__pycache__`/caches outside
  the held family.

### C. Execute cleanup batches (with manifests)

Priorities (still follow dependency/reference checks first):
1. Regenerable/empty: `.pip-cache/`, `qdrant/` (if truly stale engine artifacts),
   empty dirs, misc caches — delete per restricted rules.
2. `repomix` authoring leftovers (`repomix.config.json`, `.repomixignore`) — archive
   (the bundle stays deleted; the config files are historical authoring tools).
3. Report-era captures/working files at root — archive (many are dated evidence of the
   Executive Report era; check Markdown references before any deletion — delete only
   byte-identical duplicates or trivially-regenerable ones).
4. Root GHL export CSVs + `Contacts added August 25 2026/` — **archive, do not delete**,
   because they contain mass contact PII and remain the only local record of import
   source provenance; confirm no workflow still reads them from n8n (`GHL_Ready_*.csv`
   under `data/` are referenced by n8n docs — keep `data/` as is unless a doc says they
   were consumed).
5. Root `_check_config.py` / `_kill_and_fix.py` / `_mark_enrolled.py`, `Dockerfile`,
   `fix_errors.txt`, `move_errors.txt` — classify with dependency check (the bare
   `Dockerfile` may belong to a documented deploy path).
6. Directory organization: propose (and with-manifest execute) consolidations only where
   the plan's own rules justify them; do NOT reshuffle canonical control docs/paths
   referenced by AGENTS/plan/README (e.g., root `AGENTS.md`,
   `Project Status and Next Steps.md`, `executive_report_v1_plan.md`): those moves
   require Ed's explicit approval.
7. `scripts/` + `local-scripts/` + `marketing/` + `tools/`: mostly keep — the plan's goal
   is "a small, reviewed set of important reusable tools". Produce a reduced-toolkit
   proposal (which of the 242 scripts remain load-bearing vs. one-off diagnostics —
   mark, archive-with-note, or delete only duplicates/regenerables) and, where safe,
   consolidate the operator-only one-off probes into `local-archive/scripts-*-2026-11/`
   with per-path manifest. Anything that is a sole reproducible source for a live
   workflow (cross-check [phase4-source-backup-strategy](../transition/phase4-source-backup-strategy-2026-11-05.md))
   stays put.
8. Update `scripts/README.md` + `docs/repository-file-map.md` after the tree stops moving;
   reconcile classification-artifact counts with the new state.

### D. Documentation finalize

- Reconcile `docs/transition-plan.md` ledger after every batch; add disposition addenda to
  `repository-organization-2026-11-06.md`; update `owner-review-package-2026-11-05.md` to
  reflect what got executed (or create a dated successor).
- Re-verify transition README links and file-map accuracy.

### E. Closeout

`git diff --check`, fresh `git status`, commit+push **only if Ed asks**. Write
`docs/sessions/2026-11-06-developer-transition-repo-organization-eos.md` with: completeness
verdict per ledger item (nothing missed / what was missed and when fixed), batches executed
with bytes freed/moved, preserved paths, remaining owner decisions, Git validation, and a
best-effort statement that the repo is organized per the file map (or the deltas that
need Ed).

## Stop-and-ask conditions (do not self-authorize)

- Any file where the dependency check is ambiguous → ask Ed.
- Multi-contact exports/reports, pricing/legal/financial documents → archive-with-note, ask.
- Moving any **canonical** root control doc or changing `AGENTS.md`-documented paths.
- The billing-report personal files → do not process at all.
- Anything that would need a live-state change (Coolify, n8n, GHL, VPS).
- Anything resembling "rotate a credential" (still open: Unipile key/Postgres literals/
  stateSecret/callback keys — owner-only).

## Quick access notes

- n8n-lt REST: base `https://automations.livetransparent.com/api/v1`, key in `.env`
  `N8N_LT_API_KEY`.
- Coolify panel API: on the VPS at `localhost:8000`, key in `.env`; use SSH channel like
  `docs/transition/read_coolify_readonly.py`. `/backups**` endpoints are absent.
- Postgres (VPS read-only catalog): `docker exec postgres-uokgs4c04ko0s4scccg40cgg psql …`;
  SSH: `root@89.117.21.29` with `C:\Users\edmon\.ssh\local-upload`.
- Git: branch `codex/social-outreach-sync` (pushed; commits `ccaae01`, `bc75160`);
  `repomix-output.md` intentionally absent; do not recreate; do not commit unless Ed asks.
