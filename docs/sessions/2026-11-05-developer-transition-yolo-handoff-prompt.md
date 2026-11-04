# Copy-ready next-agent prompt — LiveTransparent transition

Continue the LiveTransparent developer transition. **Start at `docs/transition-plan.md` and its progress ledger**, then read `docs/transition/README.md`, `AGENTS.md`, and `docs/transition/completeness-audit-2026-11-06-full-plan.md`. The transition is not accepted. Update the ledger after every discrete completed check with date, evidence, method, outcome, remaining dependency, and next action.

## Work style

Ed requests **YOLO mode for all changes**: act autonomously and finish all safe, in-scope repository/documentation work without pausing for routine approval. Preserve existing evidence; use exact-path manifests/recovery notes for any separately authorized repository disposition. Do not stop independent work merely because another item is blocked. Be candid: partial/blocked criteria remain so until evidence or owner-approved narrowing closes them.

## Hard boundaries

- **Production is explicitly read-only.** Do not execute, activate/deactivate, publish, or edit n8n workflows; send messages; mutate GHL contacts/tags/opportunities or database data/schema; test providers; change/restart/deploy Coolify services; rotate credentials; or restore production. Read-only checks only, with fresh evidence and timestamps. Use only verified `n8n-lt` for n8n; never substitute another tenant.
- An isolated **non-production** restore test was authorized only if a dedicated safe target exists with storage/resource/secret containment. It is **not provisioned** and no restore has been tested. Do not copy/extract backups or begin a restore until the target and containment are verified.
- Exactly **three** GHL Marketplace apps are confirmed. Do not search for a fourth or treat the dashboard’s separate “4 total live apps” aggregate as an app count.
- Do not touch `local-scripts/linkedin-invite-withdrawals/` or its `__pycache__`; no worker/process, provider, ledger, or state changes. The previous evidence found 310 provider-pending invitations with no ledger rows plus a separate held-`ready` conflict. Do not derive scope from provider-relative dates.
- Do not process personal invoicing or include personal-only details in project artifacts. Do not expose secrets, token-bearing URLs, execution payloads, or contact PII. The live PIT retention decision is owner-accepted; do not reproduce it. Other credential rotations are separate and unauthorized.
- Check Git status before edits. Preserve user changes; do not reset/clean/checkout. Latest confirmed commit is `7f9ce98`, pushed on `codex/social-outreach-sync`; verify before relying on this. Commit/push only when the current owner instruction authorizes it.

## Remaining work — do not call complete until evidenced

1. Finish independent safe local/read-only acceptance checks and refine documentation where fresh evidence supports it. Full-plan audit lists unmet §1/§3–6 criteria in `docs/transition/completeness-audit-2026-11-06-full-plan.md`.
2. Complete workflow operational/source/recovery details and external GHL/provider caller mapping only from approved authenticated read-only sources. The 212-row structural supplement is metadata-only; 130 workflow timezones are blank and cannot be inferred.
3. If the owner wants full GHL technical acceptance, obtain authenticated read-only evidence for installs/location assignments, grants, callbacks, and runtime behavior for the three known apps. Do not repeat app discovery.
4. Coolify: keep reports-app network drift, sample-page duplicate route, existing backup handling, scheduled coverage, and restore acceptance open until owner-approved evidence/decisions. No service or backup mutation.
5. Training/onboarding: obtain guide audiences, active-use/current-procedure evidence, legal/consent review, release/branch process, secure access provisioning and escalation roster. Owner owns/distributes five Markdown guides now; incoming developer is intended future owner. Do not invent missing facts.
6. Scripts: owner chose to retain all 242 as source/history; this does not establish a maintained/safe toolkit. Keep the small maintained subset unselected until reviewed. Per-file review of the February marketing report captures is still required before redistribution.
7. Keep remaining security and accepted-history risks explicit; no rotations or Git-history rewriting without coordinated owner decision.

## Completion discipline

Proceed independently on unblocked work and ask only for precise missing owner evidence/access. Mark every result **PASS / PARTIAL / BLOCKED**, never upgrade a dated snapshot into fresh live proof. No transition-wide completion claim until all mandatory acceptance criteria are evidenced or Ed explicitly narrows them. At EOS: update the ledger after each check, run relevant link/diff validation, record Git status/commit truth, and create the next handoff.
