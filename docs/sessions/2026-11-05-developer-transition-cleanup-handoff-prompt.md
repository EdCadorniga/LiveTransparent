# Copy-ready handoff prompt — developer transition, cleanup execution (2026-11-05)

You are starting the **LiveTransparent developer-transition cleanup execution** in this
repository (`C:\1_Ed's Active Work\Projects\LiveTransparent`). Everything evidenced so far is
recorded in `docs/transition-plan.md` (the task ledger), `docs/transition/README.md`, and the
latest EOS: `docs/sessions/2026-11-05-developer-transition-evidence-eos.md`. Do not stop early;
work through the ordered checklist below and update the ledger after **every** discrete action.

## YOLO mandate (Ed, 2026-11-05)

Operate in **YOLO/high-autonomy mode** for read-only, repository, and documentation work. Ed
states: *"I approve all archiving and deletions as long as they were based on what I asked in
the plan."* That means: you may execute archive/delete batches yourself when they follow the
plan's own classification rules (Phases 3–5) and the retention criteria already recorded in
the exact-path artifacts — with per-path records and a recovery path per batch. It does **not**
override the boundaries below.

## Hard boundaries (never do these without a fresh exact-scope request)

1. **Production stays read-only.** No workflow activation/deactivation/execution, no sends,
   tests, replays, CRM writes, schema/data mutations, service restarts/redeploys, restores,
   Coolify state changes (drift fixes, container cleanup), or credential rotation. Use only
   the `n8n-lt` instance for n8n reads. Live n8n/Coolify/Postgres **reads** remain authorized
   (the read-only generators under `docs/transition/` are the proven pattern).
2. **Do not touch these, even for deletion:**
   - `local-scripts/linkedin-invite-withdrawals/` (whole family) while the 310-unledgered
     invitation investigation is unresolved — the plan requires an owner-scoped decision on
     the underlying records before that family's artifacts are dispositioned.
   - Personal invoicing — anything with invoice/invoicing path segments; per the plan it is
     outside this project and must not be moved, inspected beyond path/size, or deleted here.
   - Host/VPS files, Docker volumes, backups on the VPS (e.g. the root-only pre-2.44.6 backup
     set) — the live host is not part of the repository-batch approval. Do not recreate
     `repomix-output.md`. Do not commit anything unless Ed asks; keep the dirty worktree
     pattern of working-copy edits only.
   - License/audit/PII/credential content whose disposition the plan marks as needing a
     separate policy (contact exports, provider responses) — archive them rather than delete.
3. **Never delete a sole last-known-good or live-system-of-record artifact** (plan Phase 4).
   Keep at least one copy (current tree or moved-to-archive) of anything that is the only
   reproducible source of live state.
4. **Never print or copy secret values.** Live PIT stays per Ed's 2026-11-05 decision (retain
   latest `.env` PIT; git-history/local-archive presence accepted). Keep the standing
   `<redacted-pit>` working-copy redactions; keep values out of new docs.

## Cleanup execution protocol (per batch, mandatory)

1. Build the batch from an **exact-path manifest**: path, bytes, classification basis (quote
   the plan/§/artifact rule), dependency check result, sensitivity note, recovery method,
   destination. The classification inputs already exist:
   `docs/transition/scripts-classification-2026-11-05.md` (443 exact paths + markers),
   `docs/transition/n8n-archive-classification-2026-11-05.md` (68 files),
   `docs/transition/tmp-artifacts-classification-2026-11-05.md` (36 files), and the plan's
   Phase 3–5 sections.
2. Record the manifest (dated file under `docs/transition/`, e.g.
   `retention-manifest-2026-11-XX-batch-<n>.md`). Do not delete anything that the manifest
   did not cover.
3. Execute in small batches. Prefer **archive over delete**: move to
   `local-archive/<dated-folder>/` (git-ignored) rather than deleting files with audit or
   forensic value. Use Git only for tracked-file deletions (`git rm` results appear in the
   working tree; do not commit).
4. After each batch: verify paths gone/moved, `git diff --check`, `git status --short`,
   targeted link/reference re-check (the 223 doc-referenced files in the scripts artifact are
   the watch list), and update the ledger row + a fresh progress note immediately.
5. Stop and ask Ed before proceeding with any file where the dependency check is ambiguous,
   any multi-contact export/report data, or anything pricing/legal/financial.

## Ordered work

### A. Baseline (Phase 0 refresh)

1. Fresh `git status --short --branch`, `git diff --stat`, and the recent-commit log; confirm
   you are on `codex/social-outreach-sync` with the expected pre-existing modifications +
   untracked transition artifacts, and reconfirm `repomix-output.md` stays deleted. Do not
   stage/reset/clean anything pre-existing.
2. Check the local withdrawal-artifact boundary: the 310-unledgered-invitation investigation
   remains owner-blocked (record that; do not act).

### B. Credential-hit script hardening (12 flagged files)

From `scripts-classification-2026-11-05.md`: 5 files have `API_KEY = '<literal>'`, one has
`TRACK_SECRET = '<literal>'`, one has a `pit-` literal (`local-scripts/build_mass_email_stage.py`),
plus JWT-bearing files in `marketing/` (mostly test captures) — review and decide per file:
- For tracked scripts: **redact the literal in the working copy** (replace with an `.env`-key
  loader like `os.environ.get(...)` or a documented env placeholder), keep the file, and note
  its current state (same as PIT decision: `pit-` values stay in `.env` only).
- For `marketing/` test/capture files with JWTs/prefixes: keep but ensure they are not
  redistributable (add a short header line to the top of the artifact saying values are
  historical/superseded, or archive them if unreferenced) — do not delete silently if
  referenced by any of the 223 doc-referenced paths.
Record each decision in the ledger. Files already referenced in docs stay in the tree.

### C. tmp/ + root tmp* execution (Phase 5)

- `tmp/` Alcohol/cannabis template captures (27 files): move into
  `local-archive/campaign-template-captures-2026-11/` (created by you; stays git-ignored),
  since the Alcohol template work is closed/documented; delete nothing.
- Root `tmp*` report captures (9 files): review each briefly (bounded content check, never
  quoting values); rename to `local-archive/report-captures-2026-11/` in the same pattern.
  If one is clearly stale and unreferenced anywhere in docs/scripts, deleting it is allowed
  by the plan — but prefer archiving.
- Regenerable junk only (`__pycache__`, `*.pyc`): delete freely, per the plan's
  "regenerated temp/caches/bytecode" category.

### D. Workflow-archive dedup + retention (Phase 4)

1. From `n8n-archive-classification-2026-11-05.md`, compute **SHA-256 hashes** of the 68
   files. Delete exact **duplicate files with identical hashes** where the live-era equivalent
   is already retained elsewhere (keep 1 of any fully duplicated set). Record per-path.
2. For the five May-2026 `workflow_Q3Ivnwe4z2Y3cD7A_*` backups: they are superseded-by-date
   history of one workflow the product has since rebuilt. Keep the newest/one file as
   last-known-good; delete the older duplicates **only if** their content-hash duplicates
   something retained. Otherwise archive them as-is.
3. TS blueprints: keep all as retained blueprint sources (the template of record per path);
   reconcile counts with the [phase4-source-backup-strategy matrix](../transition/phase4-source-backup-strategy-2026-11-05.md)
   (31 of 46 critical workflows already have documented repo sources; 15 do not — those
   archive/extract candidates must **not** be deleted).
4. Update the archive's classification artifact with the disposition column; regenerate by
   rerunning `docs/transition/classify_archive_readonly.py` style after the batch if needed
   (read-only generator, allowed).

### E. `node_modules/` decision execution

Per plan §6.4 + the blanket approval: remove `node_modules/` **only after** verifying a
package manifest/lockfile exists and after a dry-run proves regeneration would be possible
(`npm install --dry-run` locally or documented install steps). Delete after confirmation;
record size freed. If verification fails, keep it and record the reason.

### F. Open-owner items (still required from Ed; do not self-authorize)

- Coolify: scheduled-backup governance, isolated restore test, reports-app network drift,
  duplicate sample-page containers — every one is a live-state change needing a specific Ed
  authorization; the check scripts exist under `docs/transition/`.
- LinkedIn 310-unledgered-invitation investigation + held `ready` row — a scoped read/write
  plan first, then Ed's approval.
- Training-guide owners/audience/active-use for the five guides (see
  `docs/transition/training-doc-register.md`); no guide text changes until then.
- Onboarding untouched facts: runtime/tool versions, release process, access provisioning,
  escalation roster. Ask Ed explicitly; fill `developer-onboarding.md` only from his answers.

### G. Documentation close-out (finish the ledger)

- Update the [owner review package](../transition/owner-review-package-2026-11-05.md) and the
  ledger after each executed batch.
- Reconcile `docs/repository-file-map.md` and `docs/transition/README.md` once the tree stops
  moving.
- Keep the dirty worktree. At the end, update the ledger rows and write a dated
  `docs/sessions/2026-11-05-developer-transition-cleanup-eos.md` with executed batches,
  preserved paths, freed bytes, remaining decisions, and fresh Git validation results.

## Quick access notes

- n8n-lt REST: base `https://automations.livetransparent.com/api/v1`, key in `.env`
  `N8N_LT_API_KEY` (the proven read-only generators all read it safely).
- Coolify panel API: reachable from the VPS at `localhost:8000`; use Coolify API key from
  `.env` via SSH channel (see `read_coolify_readonly.py`). `/backups` endpoints are not
  exposed in this panel version.
- Postgres: `docker exec postgres-uokgs4c04ko0s4scccg40cgg psql ...` inside the VPS gives
  read-only catalog access without a password (see `read_postgres_schema_readonly.py`).
- VPS SSH: `root@89.117.21.29` with `C:\Users\edmon\.ssh\local-upload`.
- Git: current branch `codex/social-outreach-sync`; expect pre-existing untracked/modified
  files; do not commit.
