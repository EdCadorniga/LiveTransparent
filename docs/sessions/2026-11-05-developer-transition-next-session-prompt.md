# Copy-ready prompt — continue and complete the LiveTransparent developer transition

> **Superseded 2026-11-05:** Use the current app-count closeout and handoff at
> [`2026-11-05-marketplace-app-count-eos.md`](2026-11-05-marketplace-app-count-eos.md) and
> [`2026-11-05-marketplace-app-count-handoff-prompt.md`](2026-11-05-marketplace-app-count-handoff-prompt.md).
> The authenticated portal and owner statement confirm exactly three apps. Do not continue a
> fourth-app search. This older prompt is retained for its broader transition checklist only.

Continue the LiveTransparent developer-transition work in this repository. **Do not stop after summarizing, performing one review, or updating this prompt. Continue through the ordered checklist and complete every task that is authorized and unblocked.** Maintain momentum across independent workstreams while waiting for owner access or decisions. Do not report the overall transition complete until every acceptance criterion is evidenced or an owner-approved scope change explicitly removes it. A blocker is not completion; request the needed access/decision, record it, proceed with other authorized tasks, and return to the blocked item when cleared.

## YOLO / high-autonomy instruction

Operate in **YOLO/high-autonomy mode for all authorized read-only, repository, and documentation work**: make reasonable bounded decisions, carry out the full checklist, update the ledger continuously, and do not pause for routine confirmation. “Do not stop until all is done” means keep advancing every independent/unblocked task and revisit blockers when access or decisions arrive; do not end early with a generic summary. **YOLO does not override the safety gates below, repository `AGENTS.md`, platform permissions, or explicit approval requirements.** Never bypass access controls or invent authorization for production mutations, live sends/tests, deployments/restores, credential changes, or destructive cleanup. When a genuine blocker requires Ed's input, state the precise request, record it, and continue other safe work rather than waiting idle.

## Start here — required

1. Read `AGENTS.md`, `docs/transition/README.md`, and `docs/transition-plan.md` first. The transition plan's progress ledger is the checklist and source of task order. Read `Project Status and Next Steps.md`, `Project Specifications.md`, the training register, onboarding draft, latest inventories, and latest EOS as relevant.
2. Refresh `git status --short --branch`, inspect the current diffs and recent commits before editing. Preserve the existing dirty worktree. Do not stage, reset, clean, commit, or overwrite changes you did not make.
3. **After each discrete check or completed ledger item, immediately update `docs/transition-plan.md`** with date, exact evidence/path, verification method, result (`done`/`partial`/`blocked`), remaining dependency, and next action. Keep dated snapshots; create dated follow-ups instead of silently replacing evidence.
4. Continue from the latest EOS: `docs/sessions/2026-11-05-developer-transition-continuation-eos.md`. Its copy-ready prompt is this file.

## Completion mandate and boundaries

- Work through all six phases in `docs/transition-plan.md`, including the unstarted script/artifact classification and review/approval work. Do not stop merely because Phase 1 or the docs pass is done.
- Continue all independent, read-only/documentation tasks while GHL portal access, owner answers, or other dependencies are pending. Request missing access/decisions from Ed clearly and record the blocker; do not guess or bypass it.
- Preserve dated history but remove or explicitly supersede stale factual claims only when evidence supports the correction. A heading relabeled `DATED CHECKPOINT` is not fact verification.
- **Production and cleanup remain read-only/approval-gated.** No workflow/service changes, workflow executions/tests/replays, CRM/state/schema writes, sends/provider tests, activation/deactivation, deployments, restores, service restarts, credential rotations, or archive/delete/cleanup batches unless Ed gives separate, exact-scope authorization. Do not execute a script just to classify it.
- Use only **n8n-lt** for any n8n reads. If access/tenant cannot be verified, stop n8n operations, record the block, and continue other tasks. Never use another customer's n8n instance.
- **Superseded portal status:** authenticated read-only portal review is documented in `docs/transition/ghl-marketplace-apps-2026-11-04.md`; exactly three apps exist. No fourth-app search is needed. Install/location assignments and runtime behavior remain unverified; do not infer them from the dashboard aggregate.
- Do not infer LinkedIn invitation send dates from provider-relative labels. Leave the **310 unledgered invitations** and the distinct held `ready` row untouched; further investigation/reconciliation requires scoped owner approval.
- **PIT decision (2026-11-05, superseding the prompt's rotation request):** Ed directed **retention** of the latest PIT from `.env`; no rotation. Git-history/local-archive token presence is owner-accepted; keep the working-copy redactions and keep values out of new docs.
- Existing root-only upgrade backups remain untouched. Ed said backup retention is not needed, but this does not authorize deleting/moving/changing existing backups or establish restore acceptance. Restore remains untested.
- The only authorized cleanup recorded is removal of the tracked root `repomix-output.md`, already completed. Never recreate it or make a substitute context bundle. Exclude personal invoicing completely.

## Ordered work to finish

### A. Close out the current documentation pass

1. Review the full diffs for `AGENTS.md`, `Project Status and Next Steps.md`, `Project Specifications.md`, `plan.md`, and all transition/EOS files. Distinguish this session's edits from pre-existing edits; investigate any unexplained line-ending or broad-churn change before proceeding. Do not revert unexplained/user changes.
2. Verify the heading relabels: only the 2026-11-04 transition heading remains `CURRENT` in `AGENTS.md` and `Project Status and Next Steps.md`; older dated labels are historical checkpoints. Preserve the contents and chronology.
3. Check links and consistency between the transition README, ledger, onboarding draft, training register, and project-control documents. Update the ledger after each check.
4. Run `git diff --check` and targeted link/reference checks; record exact outcomes. Recheck worktree state and confirm nothing was staged or committed.

### B. Complete the remaining read-only evidence and documentation work

Use the phases and acceptance criteria in `docs/transition-plan.md` as the full checklist; do not omit items. In order:

1. **Phase 0:** preserve baseline and user changes. Reconcile the LinkedIn worker/process question only within the recorded safe scope; do not touch the worker, snapshot, provider, ledger, or held row. Reflect Ed's backup decision accurately without implying restore acceptance.
2. **Phase 1A/1B:** finish the ten n8n-lt exception acceptance records and workflow relationship map gaps. Fresh-read only where needed and permitted. Record guards, reachable caller paths, send/write capability, relevant last observed outcome, and unknowns; never execute send-capable workflows. Keep external/GHL callers unknown absent evidence.
 3. **Phase 1C:** the three-app inventory and available portal settings have already been read-only verified. Do not search for a fourth app. If Ed requests the remaining optional depth, use authenticated read-only access to verify install/location assignments and runtime caller/callback behavior; record date and provenance. No app edit, install, OAuth grant, or provider test is authorized.
4. **Phase 1D:** complete only through an authorized read-only Coolify surface: saved-vs-generated-vs-repository config comparison, route/dependency/network/volume ownership map, backup metadata and recovery procedure. Keep restore acceptance explicitly untested unless separately authorized and actually completed; no service changes.
5. **Phase 2:** finish reconciliation of `AGENTS.md`, root `plan.md`, `Project Status and Next Steps.md`, `Project Specifications.md`, repository file map, scripts/subsystem READMEs, deployment/runbooks, and training documents. Use the training register, preserve distinct audiences, obtain owner-confirmed guide ownership/use and procedure facts, and do not rewrite guides from stale snapshots. Complete onboarding only from verified repo facts and owner-confirmed release/access/escalation/recovery details.
6. **Phase 3:** perform the exact-path script/local-artifact classification required by the plan. Inventory without running files; classify keep/source/consolidate/archive/delete/owner-decision; note paths, sizes, dependencies, sensitivity, recovery and evidence. Exclude personal invoicing. Do not inspect personal-only contents. No cleanup without separate exact-path authorization.
7. **Phase 4:** inventory workflow exports/backups and compare against fresh read-only n8n-lt state where authorized. Identify canonical source and last-known-good/recovery gaps. Do not delete or alter any export/backup. Existing backups remain untouched.
8. **Phase 5:** classify temporary files/build products/datasets by exact path and dependency without deleting, moving, or opening sensitive content unnecessarily. Preserve PII/audit evidence and ignored data unless separately approved.
9. **Phase 6:** present concise evidence, remaining owner decisions, and a proposed per-path keep/archive/delete manifest for Ed's review. Obtain explicit approval before any destructive batch or production change. Do not treat the already-approved Repomix removal as broader authorization.

### C. Completion and acceptance

- Reconcile the ledger against all six plan phases and the stated acceptance criteria. Every item must be `done` with evidence or remain explicitly `partial/blocked` with an owner/dependency and next action; do not falsely mark blocked work complete.
- Verify the new developer can follow the entry guide using the documented access path. Do not ask for or place credentials in repository files; owner provisions them through secure channels.
- Run final `git diff --check`, link/reference checks, `git status --short --branch`, and review the full final diff. Preserve all pre-existing modifications/untracked artifacts; no staging or commit.
- Write a dated EOS documenting scope, work completed, test/check results, current Git state, evidence freshness, blockers, and exact next action. Keep transition status in progress until the criteria are met or Ed approves a documented scope change.

## Current snapshot (historical; refresh before operational decisions)

- As of the 2026-11-05 recorded Git checks, branch was `codex/social-outreach-sync`, ahead of origin by 2; existing modified/untracked project files and the authorized Repomix deletion were present. Recheck before work; do not assume this remains current.
- The latest bounded read-only inventory evidence is dated 2026-11-05 and linked from `docs/transition/README.md`. It does not establish a fresh live state for a later session.
- Latest handoff: `docs/sessions/2026-11-05-developer-transition-continuation-eos.md`; canonical task ledger: `docs/transition-plan.md`.
