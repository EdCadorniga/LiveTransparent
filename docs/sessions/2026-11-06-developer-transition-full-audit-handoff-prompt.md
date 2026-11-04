# Copy-ready handoff prompt — developer transition, FULL transition-plan fulfillment audit (2026-11-06)

You are starting the **LiveTransparent developer transition — full transition-plan
fulfillment-audit session** in this repository
(`C:\1_Ed's Active Work\Projects\LiveTransparent`). Read first, in this order:

1. `AGENTS.md` — operating rules/safety (n8n-lt only; never print/commit secrets).
2. `docs/transition-plan.md` — **the object of your audit; read the WHOLE file**, Sections 1–7
   and Phases 0–6, not just the progress ledger.
3. `docs/transition/README.md`, `docs/transition/owner-review-package-2026-11-05.md`.
4. The prior session evidence base (so you audit against it rather than re-deriving):
   - `docs/transition/completeness-audit-2026-11-06.md` (previous audit — ledger rows only;
     your scope is deeper, see below)
   - `docs/transition/repository-organization-2026-11-06.md` (full-repo census)
   - retention manifests batch 0–4 (`retention-manifest-2026-11-05-batch-*.md`) and
     batch 5–11 (`retention-manifest-2026-11-06-batch-*.md`)
   - the three classification artifacts (`*-classification-2026-11-05.md`) + their tail
     addenda
   - latest EOS records: `docs/sessions/2026-11-05-developer-transition-cleanup-eos.md`,
     `docs/sessions/2026-11-05-developer-transition-evidence-eos.md`,
     `docs/sessions/2026-11-06-developer-transition-repo-organization-eos.md`
   - dated inventories: `n8n-workflow-inventory-2026-11-04.md`, relationships, exception
     register, the `coolify-*.md` family, `postgres-schema-inventory-2026-11-05.md`
5. Supporting indexes: `docs/repository-file-map.md`, `scripts/README.md`,
   `docs/transition/training-doc-register.md`, `docs/transition/developer-onboarding.md`,
   `docs/transition/phase4-source-backup-strategy-2026-11-05.md`.

Update `docs/transition-plan.md` ledger after **every** discrete action. Do not stop early.

## Mandate (Ed, 2026-11-06, continuing YOLO/high-autonomy mode)

**Produce an independent, line-by-line fulfillment audit of every expectation,
instruction, deliverable, and acceptance criterion written in `docs/transition-plan.md`
itself.** The previous session's audit verified only the ledger's progress rows; your scope is
the plan text, including those ledger rows and any other items listed below as changed by Ed.

Specifically:

1. **Phases 0–6:** for each numbered item and stated acceptance criterion, verify it was
   executed with evidence (spot-check artifacts, counts, file presence/absence) or is
   explicitly marked blocked/owner-gated. Include "Deliverables and acceptance criteria"
   (§5, documentation + repository-cleanup + handoff-readiness tables) as a separate pass —
   each bullet is a checkable claim.
2. **§6 owner-decisions list:** confirm each question is resolved and recorded, or is an
   explicit open owner decision (not silently dropped).
3. **§7 scope/actions-to-date:** re-verify the recorded statements are still true today.
4. **Cross-consistency:** `AGENTS.md`, root `plan.md`, `Project Status and Next Steps.md`,
   `Project Specifications.md`, the file map, `scripts/README.md`, and repository/link
   targets must not contradict the audited state. Re-run link validation.
5. **Record the audit** in `docs/transition/completeness-audit-2026-11-07.md` (or latest date)
   with a per-item table: expectation → evidence → PASS / BLOCKED-ON-OWNER / FAIL→fixed.
   Anything FAILed or missed is **fixed in the same session** (edit, ledger entry, manifest
   batch if destructive, or explicit blocker note).

### Known areas likely to still be open (do not re-classify; verify state)

- Owner-gated groups: Coolify backup governance + isolated restore test + reports-app network
  drift + duplicate sample-page preview containers; LinkedIn 310-unledgered-invitation
  residue and the held `ready` row (withdrawal family untouched including its
  `__pycache__`); training-guide owner/audience confirmations (five guides); onboarding
  facts (runtime/tool versions, release process, access provisioning, escalation roster).
- New owner-review flag from 2026-11-05/06: `marketing/email-marketing/cold-outreach-prep/reports/`
  (~140 dated Feb-2026 run captures, incl. `workflow-T28iLcm4Hszo19MG.apiKey-env-payload-…json`) —
  per-file sensitivity review pending; none opened.
- Reduced-toolkit decisions on the 242 `scripts/` files; `landing/` deploy-vs-delete.
- Ed may have committed since the last session (the 2026-11-06 EOS left 62 staged index
  deletions + 11 doc edits ready). **Check fresh `git status` first** and do not assume
  either state; if the staged surface is still uncommitted, ask Ed before committing (he
  has previously asked to "commit and push all" — if he repeats it, do it).

## Standing hard boundaries (never violate)

1. **Production stays read-only.** No workflow runs/toggles, sends, CRM writes, schema/data
   changes, service changes, restores, Coolify state changes, credential rotations. Any live
   read (only if truly needed): `n8n-lt` only (`N8N_LT_API_KEY` from `.env`, base
   `https://automations.livetransparent.com/api/v1`), Coolify panel via SSH tunnel, or
   `docker exec postgres-uokgs4c04ko0s4scccg40cgg psql …` read-only catalog.
2. **Untouchable paths:** `local-scripts/linkedin-invite-withdrawals/` (310-unledgered
   invitation investigation open — whole family incl. its `__pycache__`); anything with
   invoice/invoicing path segments; the three root `Billing Report …` files and
   root `repeated linkedin messages.png` (personal/sensitive — do not open, move, describe,
   or disposition); VPS/host files and Docker volumes/backups; root `repomix-output.md`
   (stays deleted; never recreate).
3. **Never delete a sole last-known-good or live system-of-record artifact.** Root
   `Dockerfile` is load-bearing (Coolify `reports.livetransparent_server` builds from
   `/Dockerfile`) — never move it.
4. **Never print/copy secret values** (`.env`, Config-node contents, member exports).
   PIT retention stays as Ed decided (retain; no rotation now).
5. **No commits unless Ed asks** (previous "commit and push all" precedent is recorded —
   if he repeats it, commit AND push).
6. **Per-batch manifest protocol** for any new destructive step: exact-path manifest first
   (`docs/transition/retention-manifest-YYYY-MM-DD.md`), dependency check, archive-before-
   delete unless regenerable/pure-duplicate, verify after.

## Stop-and-ask conditions (do not self-authorize)

- Any file whose dependency check is ambiguous → ask Ed.
- Multi-contact exports/reports, pricing/legal/financial documents → archive-with-note,
  then ask.
- Moving any canonical root control doc (AGENTS.md, plan.md, Project Status,
  executive_report_v1_plan.md, improvementPlan.md).
- Anything requiring a live-state change (Coolify, n8n, GHL, VPS) or resembling credential
  rotation.
- Editing anything in the personal billing / personal-invoicing or `repeated linkedin
  messages.png` families — no processing at all.

## Ordered work

1. Fresh `git status` + `git log --oneline -5` baseline; record ledger Phase 0 refresh.
2. Build the expectation inventory: extract every acceptance item from transition-plan.md
   (§3 gates, §4 Phase 0–6, §5 deliverables/acceptance, §6 decisions, §7 scope record) into
   the audit artifact's checklist form, with pointers to existing evidence per item.
3. Verify each item (filesystem spot-checks only; no script execution; live reads only if
   something is genuinely unverifiable otherwise — use the allowed read-only channels).
4. Run the §5 "Repository cleanup" acceptance checks explicitly: manifests complete,
   `git diff --check`, documentation/link checks, no sole-last-known-good removed,
   `repomix-output.md` absent, training register current.
5. Run the §5 "Handoff readiness" checks: entry guide, tenant rule, rollback path, dated
   verification basis.
6. Fix or clearly block everything FAILed, in this session; ledger after each fix.
7. Close: link the audit from `docs/transition/README.md`, add an EOS
   (`docs/sessions/<date>-developer-transition-full-audit-eos.md`), hand Ed the residual
   owner-decision list. Commit only on request.

## Quick access notes

- n8n-lt REST: base `https://automations.livetransparent.com/api/v1`, key in `.env`
  `N8N_LT_API_KEY` (never the katwill/other tenants).
- Coolify panel API: on the VPS at `localhost:8000`, key in `.env`, via SSH tunnel like
  `docs/transition/read_coolify_readonly.py`; `/backups` endpoints are absent from that API.
- Postgres (VPS read-only catalog): `docker exec postgres-uokgs4c04ko0s4scccg40cgg psql …`;
  SSH `root@89.117.21.29` with `C:\Users\edmon\.ssh\local-upload`.
- Git: branch `codex/social-outreach-sync`. Expected baseline at handoff time: possibly a
  commit containing the 2026-11-06 batch surface (62 staged deletions + 11 doc edits + 10 new
  artifacts) — verify fresh, do not assume.
- Recent evidence anchors: `local-archive/n8n/` = 66 files / 66 unique hashes;
  `local-archive/` = 10 dated folders / ~165 files; root = 19 files exactly.
