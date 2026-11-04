# Copy-ready handoff — continue the LiveTransparent developer transition

Continue the transition from the repository ledger, **not** from an old status paragraph:

1. Read `AGENTS.md`, `docs/transition/README.md`, and all of `docs/transition-plan.md` first. The plan ledger is authoritative and must be updated immediately after every discrete check.
2. Read `docs/transition/completeness-audit-2026-11-06-full-plan.md` for the remaining acceptance gaps and `docs/transition/owner-review-package-2026-11-05.md` for owner decisions. Refresh Git status and inspect relevant diffs before editing.
3. **Marketplace inventory is settled: exactly three apps exist.** The authenticated My apps listing and Ed's confirmation agree. Do not search for a fourth app. See `docs/transition/ghl-marketplace-apps-2026-11-04.md`. The dashboard's separate “4 total live apps” number is an unexplained aggregate, not an app count. Install/location assignments, access grants, OAuth completion, and runtime callback delivery remain unverified; do not test or mutate them.
4. Continue the remaining authorized read-only/documentation acceptance items in the transition plan. Keep blockers partial/blocked with owner and next action. Work independently on unblocked items; do not stop at a summary.

## Hard boundaries

- Production remains read-only: no workflow execution, toggle, publication, send, CRM/provider/schema/service mutation, credential rotation, deployment, service restart, or restore.
- Use only the verified **n8n-lt** instance for n8n reads. Never fall back to another tenant.
- Do not move, restore, or alter backups. An isolated non-production restore host is not provisioned; restore is untested.
- Preserve all existing staged deletions, modifications, untracked work, and local data. No stage/reset/clean/commit/push unless Ed separately asks.
- Do not touch `local-scripts/linkedin-invite-withdrawals/`, its worker/snapshots/ledger, the 310 unledgered invitations, or the distinct held `ready` row. Never infer send dates from provider-relative labels.
- Keep personal invoicing out of project docs and handoff. Do not recreate `repomix-output.md` or a replacement bundle.
- Never print or copy secrets. The owner-approved PIT retention decision does not authorize exposure in new documentation.

## Current state and closeout links

- Latest app-count EOS: `docs/sessions/2026-11-05-marketplace-app-count-eos.md`.
- App evidence: `docs/transition/ghl-marketplace-apps-2026-11-04.md`.
- Transition ledger: `docs/transition-plan.md`.
- Full-plan audit: `docs/transition/completeness-audit-2026-11-06-full-plan.md`.
- Current entry point: `docs/transition/README.md`.

At the end, reconcile every plan phase and acceptance criterion. Report only what is evidenced; keep the overall transition in progress until every acceptance item is met or Ed approves a documented scope change. Run `git diff --check`, relevant link/reference checks, and fresh `git status --short --branch`; preserve all existing Git state and write a dated EOS with evidence and blockers.
