# Developer transition continuation — onboarding and training review, 2026-11-05

Resumed from `docs/transition-plan.md` and the 2026-11-04 continuation EOS. Preserved all existing modified/untracked files. No production workflow/service reads or mutations, workflow executions/toggles, provider tests, CRM writes, deployment, restore, cleanup, staging, or commit occurred in this continuation.

## Completed

- Read all five registered Markdown training guides in full and compared time-sensitive statements with current repository control docs, dated Power Dialer build evidence, and transition inventories. Checked the `.docx` companion's presence/size/timestamp only; its contents were not extracted or compared.
- Updated [`docs/transition/training-doc-register.md`](../transition/training-doc-register.md) with per-guide review status, concrete conflicts, evidence boundaries, and owner/live-access blockers. No guide content was changed because owners, audiences, active use, and several live procedures are not confirmed.
- Added [`docs/transition/developer-onboarding.md`](../transition/developer-onboarding.md). It distinguishes safe repo orientation from unresolved runtime, dependency, access, release, owner, route, and restore facts; no secret or production data is copied.
- Added onboarding/register pointers to the transition README, AGENTS, and Project Status. Updated the transition-plan ledger after the discrete review/build checks.
- `git diff --check` passed. It emitted only existing Git line-ending conversion notices for modified files. Worktree state and existing changes were preserved.

## Training findings requiring owner/live verification

- **Power Dialer:** guide asserts live queue names, outcomes, stage moves, ringless voicemail, and suppression behavior. The Aug 19 recipe and session disagree on names/tags/action order and whether the disposition workflow was actually built. GHL authenticated Builder readback is required; consent handling is an explicit gap to resolve, not infer.
- **Pipeline Process:** 517-line guide mixes durable definitions with older runtime claims (including n8n 2.33.3 vs the Nov 4/5 host inventory's 2.44.6) and Feb 2026 warm-channel snapshots. Current status for Apollo and campaign paths needs fresh owner-authorized verification.
- **Vapi:** workflow IDs are known, but the guide's version, tool inventory, consent/timezone gates, and operational acceptance need fresh validation. Its AI/disclosure language is an owner/legal policy decision. Its described live smoke tests can place calls/write CRM and cannot be treated as routine training steps.
- **Executive Report:** guide points to the Aug 17 V0 build, while later status records V1 at `/embed/executive-v1/`, an Oct 19 build, and Oct 26 source-coverage correction. Report metric/source definitions need reconciliation to the current V1 glossary/API before edits.
- **Marketing Pipeline:** MQL and booking statements are mostly aligned to durable rules but omit ownership/qualification constraints and have inconsistent booking scope wording. Verify against the Oct 13 verified writer correction and current GHL implementation before editing.
- **DOCX companion:** metadata shows a file exists (4,887 bytes; 2026-03-20 UTC). Its active/distribution status and owner are unknown; no disposition or deletion is authorized.

## Still open / next actions

1. Continue only bounded read-only Coolify/n8n evidence from the plan; leave Developer portal and saved Coolify/restore gaps blocked without owner access.
2. Confirm each guide's owner, audience, and active use. Obtain authenticated read-only GHL access for current Power Dialer workflows; ask the accountable owner to review Vapi disclosure wording.
3. Reconcile `AGENTS.md`, `plan.md`, `Project Status and Next Steps.md`, and `Project Specifications.md` as a deliberate documentation pass. Existing transition pointers do not complete the required stale-current-state cleanup.
4. Complete onboarding with owner-confirmed runtimes, release/PR conventions, access/escalation owners, and recovery procedures; do not infer them from a lockfile or historical runbook.
5. Continue preserving the existing worktree. GHL app inventory, safe invitation reconciliation, Coolify saved config/routes, backup coverage, and restore acceptance remain blocked or partial as recorded in the plan ledger.

## EOS closeout — 2026-11-05

- Final read-only Git check: branch `codex/social-outreach-sync`, ahead of origin by 2. Pre-existing modifications remain in `AGENTS.md`, `Project Specifications.md`, `Project Status and Next Steps.md`, `docs/campaigns/Plan - VAPI Pause & Queued Goals.md`, `docs/handoff/2026-08-12-report-recovery.md`, `docs/sessions/2026-08-14-company-instagram-page-dm-handoff.md`, `docs/sessions/2026-09-29-executive-report-v1-ghl-call-source-closeout.md`, `marketing/email-marketing/emerald-email-campaign/plan.md`, and `plan.md`. The authorized root `repomix-output.md` removal remains present. Transition plan/docs and dated EOS files remain untracked. No staging, reset, cleanup, or commit.
- Review checks: `git diff --check` passed; targeted relative-link checks passed for transition docs. Git emitted only existing LF/CRLF conversion notices. No application tests were applicable. No live service/workflow reads or mutations were performed during this training-review continuation; do not represent earlier dated inventories as fresh November 5 full-state verification beyond the checks recorded in the ledger.
- No production workflow/service changes, workflow executions/toggles, provider tests, CRM writes, deployment, restore, or artifact cleanup occurred. Existing production and data safety gates remain unchanged.
- Transition remains **in progress**. The next agent must begin with `docs/transition-plan.md`, update its ledger immediately after each completed item, and preserve the dirty worktree. Do not mark training, onboarding, GHL app verification, Coolify recovery, or cleanup acceptance complete based on this EOS.

### Copy-ready handoff prompt

> **Superseded 2026-11-05:** the Marketplace authentication blocker below was resolved in a later read-only session. Exactly three apps are confirmed; do not search for a fourth. Use [`2026-11-05-marketplace-app-count-handoff-prompt.md`](2026-11-05-marketplace-app-count-handoff-prompt.md) for the current continuation.

> Continue the LiveTransparent developer transition from `docs/transition-plan.md`; this is a documentation/evidence task, not authorization for production changes or cleanup. First re-read `AGENTS.md`, `docs/transition/README.md`, `docs/transition-plan.md`, `Project Status and Next Steps.md`, and this EOS. Preserve the current dirty worktree on `codex/social-outreach-sync` (ahead of origin by 2); do not stage, reset, clean, or commit. Start with the remaining ledger items and update the plan immediately after every discrete check. Keep GHL Developer portal verification blocked until authenticated read-only access is available; do not guess the fourth app. Do not change, execute, or toggle workflows/services; use only n8n-lt if authorized n8n read-only verification is needed. Do not infer invitation dates from provider-relative labels or mutate the 310 unledgered invitations, ledger, state rows, local worker, or held `ready` row; obtain scoped owner approval before further investigation. Existing backups remain untouched and restore remains untested despite Ed's statement that backups need not be retained. Confirm training-guide owners/audiences/active use before editing guide text, reconcile `AGENTS.md`, `plan.md`, `Project Status and Next Steps.md`, and `Project Specifications.md` as a deliberate documentation pass, and fill onboarding gaps only from owner-confirmed evidence. No other cleanup is authorized; the root Repomix bundle is retired and must not be recreated or replaced. Exclude personal invoicing from all project docs and handoff.
