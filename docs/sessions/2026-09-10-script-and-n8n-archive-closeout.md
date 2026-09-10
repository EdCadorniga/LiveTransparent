# Script And n8n Archive Closeout

Date: 2026-09-10

## Objective

Organize reusable local helpers and historical n8n exports without committing live credentials or treating repository snapshots as the production source of truth.

## Completed

- Added the ignored `local-scripts/` boundary for reusable operator helpers.
- Retained `local-scripts/suppress_linkedin_dms.py` and `local-scripts/_vps_psql.py` locally; the suppression helper now requires environment-provided credentials instead of embedded fallbacks.
- Added the ignored `local-archive/` boundary for historical n8n exports, backups, and one-off patch inputs.
- Moved 50 n8n JSON, TypeScript, JavaScript, and MJS snapshots into `local-archive/n8n/` while preserving them on the workstation for audit/reference.
- Removed obsolete root probes, temporary diagnostics, and the obsolete image artifact from version control.
- Retained reviewed generator/reporting sources in Git and replaced credential literals in those retained sources with environment placeholders.
- Updated `AGENTS.md`, project status, campaign/session references, and `repomix-output.md` to reflect the new boundaries.

## Verification

- `node --check n8n/gen.js` passed.
- `node --check scripts/fix_intake_poller.js` passed.
- `git diff --check` passed.
- Added-change credential scan found no live PIT, Unipile key, SimpleTexting token, webhook secret, or Bearer credential.
- `local-archive/n8n/` contains 50 retained local files and is covered by `.gitignore`.
- `git status -sb` is clean and branch `codex/social-outreach-sync` matches `origin`.
- Published commits: `2de493c`, `7549eba`, and `daf0432`.

## Safety Boundary

- Live n8n remains authoritative. Archived files must not be redeployed without reconciling them against current live workflow state.
- The ignored archive may contain historical secrets inherited from old exports. Do not copy those values into tracked files or documentation; rotate any credential if an archived value is exposed.
- No live workflow was read, mutated, published, activated, executed, or deployed during this organization pass.

## Next Session

1. Treat `local-archive/n8n/` as workstation-only reference storage and include it in secure local backups if historical recovery is required.
2. Use `n8n/gen.js`, `n8n/lt-linkedin-dispatcher.ts`, reporting SDK sources, and `scripts/` only after confirming they remain credential-free.
3. Before adding any new workflow export, classify it as tracked sanitized source or ignored local archive; do not add raw n8n exports to Git.
4. Run a separate full repository secret audit before any future broad staging operation; this closeout only audited the added/retained organization changes.
