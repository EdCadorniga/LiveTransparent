# Developer transition inventory — EOS, 2026-11-04

## Objective and decisions

Prepare a safe LiveTransparent developer handoff and repository cleanup plan. Ed authorized read-only inventory. Markdown is the deliverable format; no Word version. Retain project-work history unless superseded, but do not present superseded claims as current. Personal invoicing is outside this project and must not appear in project documentation or handoff.

## Completed

- Created [`docs/transition-plan.md`](../transition-plan.md) with scope, evidence standards, safety gates, ordered workstreams, acceptance criteria, and cleanup approval boundary.
- Captured all 212 n8n-lt workflow definitions read-only: 107 active, 32 archived, zero detail-read failures, and no active/draft version mismatches. See the dated [Markdown inventory](../transition/n8n-workflow-inventory-2026-11-04.md), [sanitized JSON](../transition/n8n-workflow-inventory-2026-11-04.json), and [relationship inventory](../transition/n8n-workflow-relationships-2026-11-04.md).
- Flagged ten workflows whose DRAFT/STAGED/TEMP names conflict with their API-active state. No workflow was run or toggled.
- Captured read-only Docker/Coolify host metadata: Docker 29.6.2, seven Compose projects, 21 containers, eight networks, six volumes. See [Coolify host inventory](../transition/coolify-host-inventory-2026-11-04.md) and sanitized JSON.
- Added read-only inventory helper scripts under `docs/transition/`; both passed `py_compile` and were run successfully. They use the approved n8n-lt endpoint and host SSH path, omit credential values, and perform metadata reads only.
- Updated the transition status pointer in `AGENTS.md`, `plan.md`, and `Project Status and Next Steps.md`.
- Removed the personal-only invoice-preparation session note from the project documentation per Ed's scope instruction. No invoice/PDF or financial details were added to project artifacts.

## Verification and repository state

- `git diff --check` passed. Git emitted only the existing line-ending conversion warning for `Project Status and Next Steps.md`.
- Python syntax compilation passed for both inventory scripts.
- No workflow execution, GHL mutation, CRM write, service restart, deployment, credential rotation, or Repomix/pack operation occurred.
- No commit was made. Preserve the remaining existing modified/untracked work; do not reset or broadly clean the worktree.

## Open gaps

1. **Resolved in the EOS continuation below:** the initial plan review is complete; follow its progress ledger rather than repeating that review.
2. GHL Developer/Marketplace portal was unavailable in this session. Three app names are known from supplied screenshot/project records; the fourth live app and app-by-app configuration/install relationships remain unknown. Evidence must be labeled by source.
3. Coolify work remains host-metadata-only. Verify saved/generated Compose drift, service ownership, routes/domains, networks, volume mapping, environment-variable names only, dependencies, backups, restore procedures, and rollback evidence without reading or publishing secret values.
4. The n8n workflow inventory is a dated snapshot. Reconcile the ten DRAFT/STAGED/TEMP name-vs-active-state items and enrich high-risk workflow rows with purpose, sending/write capability, external systems, source/runbook, error handling, and accepted execution evidence. Do not execute workflows to obtain evidence.
5. GHL→n8n and provider callback edges are incomplete until the GHL and external-provider surfaces are read-only checked.
6. Repository file/script/export cleanup has not started. Produce and review a keep/consolidate/archive/delete/owner-decision manifest before any additional cleanup. Personal invoicing remains outside scope.
7. The three project-control docs have only received a transition pointer; full reconciliation/cleanup remains a later plan phase after the inventory review and evidence verification.

## Next-session safety boundaries

- Start with the reviewed plan and its progress ledger; record any newly discovered risks there before proceeding.
- Keep all system checks read-only and use only n8n-lt for n8n.
- Do not activate/deactivate/run workflows, test provider callbacks, edit GHL apps, restart/redeploy services, rotate credentials, or alter CRM/schema/data without separate scoped approval.
- Do not delete or move artifacts except within a specifically approved manifest. Preserve historical project evidence unless superseded; exclude personal invoicing.
- Do not refresh Repomix/`packlive` without renewed authorization.

## EOS continuation — reviewed 2026-11-04 (supersedes the earlier “plan review first” instruction)

The initial plan review is **done**. [The transition plan](../transition-plan.md) now includes the proposed sequencing/acceptance improvements and a phase-by-phase progress ledger. Its former snapshot-only wording and broken relative links were corrected; [transition entry point](../transition/README.md) links the dated evidence without duplicating it. This closeout does **not** mark Phase 1, the full project-control-document reconciliation, an app inventory, or restore acceptance complete.

**Verified in this continuation:** a new read-only API GET against the approved n8n-lt instance confirmed the ten DRAFT/STAGED/TEMP-named workflows remain active, unarchived and published at matching draft/active versions with enabled trigger nodes. [Per-ID register](../transition/n8n-active-name-exceptions-2026-11-04.md). No execution history or configuration guard values were inspected; do not claim current dry-run protection or runtime acceptance. A public Marketplace browser visit showed **Sign In**, not an authenticated Developer portal; no fourth app identity or install configuration is portal-verified ([evidence register](../transition/ghl-marketplace-apps-2026-11-04.md)). Read-only Docker/SSH inspection confirmed generated Compose, mount/network metadata, variable **names**, and a one-time pre-upgrade backup set; saved Coolify definition, backup schedule, off-host copy, and isolated restore remain unverified ([configuration evidence](../transition/coolify-configuration-2026-11-04.md)). Reports generated Compose lists `coolify` while running network metadata also lists `coolify-shared`; resolve this drift before a report redeploy. [Family-level retention proposal](../transition/repository-retention-proposal-2026-11-04.md) is **not** an approved per-path cleanup manifest.

**Repository state:** branch `codex/social-outreach-sync`, ahead of origin by two commits at closeout review. Modified pre-existing project-control docs `AGENTS.md`, `plan.md`, `Project Status and Next Steps.md`; untracked transition plan, transition evidence/helpers and this dated session note. Preserve them; no commit, deletion, archive move, production mutation, workflow run, service restart, or pack operation was performed in this continuation. `git diff --check`, `python -m py_compile` on the three transition inventory helpers, and relative-link checks across the new transition/closeout documentation passed after editing. No test execution IDs were created. Production states are dated snapshots, not timeless guarantees.

**Ordered next session:** (1) read plan ledger and fresh Git status; preserve all existing edits; (2) close remaining Phase 0 access/backup-owner and withdrawal worker/ledger checks read-only; (3) continue Phase 1A/1B guard, execution-metadata and caller mapping without running workflows; (4) with an already authorized authenticated GHL Developer portal session, identify the fourth app and verify installs/scopes/callbacks (otherwise mark blocked); (5) read saved Coolify config without secret values, reconcile generated/live/repo drift and backup coverage; plan an isolated restore test for separate approval, never claim one occurred; (6) only then continue the Phase 2 current-doc reconciliation and newcomer guide, followed by Phase 3–5 exact-path retention review and Phase 6 owner approval. **Immediately after each item or acceptance check, update `docs/transition-plan.md`** with date, evidence, done/partial/blocked status, unresolved dependency and next step. Do not wait until EOS to update the plan.

### Copy-ready next-agent prompt

> Continue the LiveTransparent developer transition on `codex/social-outreach-sync`. Start at `docs/transition-plan.md` (especially its progress ledger) and `docs/transition/README.md`; the plan review is already complete. **Update `docs/transition-plan.md` every time you finish an item or acceptance check**, recording dated evidence, verification method, done/partial/blocked status, remaining dependencies and next action. Preserve existing modified/untracked files and dated history. Continue the remaining read-only Phase 0/1 evidence gates in order: local LinkedIn worker/ledger before related artifact decisions; n8n-lt-only guard/last-execution/caller reconciliation for the ten active DRAFT/STAGED/TEMP names; authenticated GHL Developer portal app list to identify the fourth app (public browser currently only shows Sign In, so do not guess); Coolify saved-vs-generated-vs-live drift, backups and restore evidence without printing secrets. Phase 2 project-control-document reconciliation and the onboarding guide follow verified evidence, with blocked facts labeled. Prepare an exact-path retention manifest after dependency review; the current family-level proposal is not approved. No workflow runs/toggles, GHL/CRM writes, provider sends/tests, service changes, artifact deletions/moves, credential rotation, or Repomix refresh without separate scoped approval. Keep personal-only material outside project docs and handoff. At EOS, update the plan and this handoff with what was actually accepted and what remains open.
