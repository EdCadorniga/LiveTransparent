# LinkedIn Outbound Safety Bug-Fix Closeout

**Date:** 2026-09-16
**Project:** LiveTransparent
**Scope:** Active LinkedIn outbound workflows only; no repository application code or archive sources changed.

## Objective

Fix the confirmed LinkedIn outbound defects and ensure malformed or garbage-character messages fail closed before reaching Unipile. The approved scope covered the active main dispatcher/DM sequence, Partnership dispatcher/DM sequence, and active suppression workflow. Inactive Follower/Test workflows and `local-archive/n8n/workflows/` were intentionally left untouched.

## Live changes

Published via the proven full-object n8n workflow update path, with local backups under `%LOCALAPPDATA%\\Temp\\lt_bugfix_*`:

- `LT - GHL LinkedIn Connect Dispatcher` — ID `fXxw5lanZcDmUrst`; active version `6ae708aa-990f-4784-87b2-573ab81dc4f4`; active; 10 nodes; 9 connections.
- `LT - LinkedIn DM Sequence (Unipile)` — ID `d0tEtijajisIsYcs`; active version `afcdad57-a770-4bb0-8eae-be1f7623e674`; active; 12 nodes; 10 connections.
- `LT - Partnership LinkedIn Dispatcher` — ID `crKIsaL5k3YBfqDZ`; active version `0fc1611f-80c9-45f8-8c93-89c74f2eeca1`; active; 10 nodes; 9 connections.
- `LT - Partnership LinkedIn DM Sequence` — ID `nspggypNF245xzeL`; active version `92e85568-3e4a-4677-b3ee-ab66dd0915a4`; active; 6 nodes; 5 connections.
- `LT - LinkedIn DM Suppression from GHL Tag` — ID `IPN8jnR3XSurX0o1`; active version `ededf18b-1355-4f8d-ad4d-1b0381382cb8`; active; 5 nodes; 3 connections.

For each workflow, a fresh GET confirmed `versionId == activeVersionId`.

## Defects fixed

1. **Daily limit accumulation:** the DM sequence now records `dailySent + passed`; the intended 200/day limit no longer resets to the current batch count.
2. **Partnership DM deduplication:** stable event keys and SQL exclusion prevent a successful provider send from being repeated when a later state write fails.
3. **Partnership invite deduplication:** the ready queue excludes contacts with an existing partnership invite event.
4. **Runtime state secrets:** suppression and Partnership DM callers now send evaluated runtime secret values rather than literal placeholder text.
5. **Fail-closed outbound message safety:** active senders perform final message validation before provider requests, including normalization, printable-ASCII rejection, unresolved-placeholder rejection, mojibake-marker rejection, and safe sanitization. Per-contact validation failures do not release a malformed message.
6. **Per-contact dispatcher handling:** the main dispatcher catches a bad contact/message without aborting the whole batch and records the failure path.

## Verification accepted

- Fresh GET fix-presence proof: **12/12 checks passed**.
- All five modified workflows: **active** and published; `versionId == activeVersionId`.
- Literal-level copy proof using the actual template registries: dispatcher invites and five DM literals in both DM sender nodes had **0 apostrophes and 0 non-ASCII characters**; all ten canonical rewritten strings remained present.
- Literal-secret sweep across nine state-upsert callers found **no literal-secret artifacts**.
- Local dry-run anchor validation: **all anchors passed**.
- Baseline-versus-patched syntax delta validation: **no new parser delta**; the Partnership node's standalone-wrapper parse quirk existed in the original live code and production n8n execution history showed successful runs.
- No manual sender execution, provider test send, CRM mutation, activation change, commit, or push was performed during closeout.

The initial broad whole-node copy scan reported false positives because JavaScript syntax, sanitizer tables, and SQL escaping contain apostrophes and non-ASCII code-point literals. That scan was superseded by the literal-level registry parser, which is the accepted copy proof.

## Remaining blockers and risks

- The state-upsert receiver still lacks validation of `X-LT-LinkedIn-State-Secret`. This is a separate approved change; do not assume the sender-side secret fix authenticates the receiver.
- Hardcoded credential fallbacks remain in some workflow JavaScript. Migrate them separately with credential-safe inventory and approval; no secret values are reproduced here.
- The durable LinkedIn reply-suppression design remains pending from the 2026-09-14 read-only review. This closeout did not silently implement it.
- Existing malformed or duplicate historical messages were not edited or deleted. No cleanup reply should be sent without a separate decision and approval.

## Next session order

1. Read this closeout and the top LinkedIn sections of `Project Status and Next Steps.md` and `AGENTS.md`.
2. If Ed approves, implement and verify receiver-side `X-LT-LinkedIn-State-Secret` validation as a separate minimal workflow change.
3. Separately inventory and migrate hardcoded credential fallbacks without exposing values.
4. Continue the durable inbound-reply suppression design only after explicit scope approval.
5. Observe scheduled executions read-only; do not manually execute sender workflows or send test messages without explicit approval.

## Repository state at EOS

- Branch: `codex/social-outreach-sync`, tracking `origin/codex/social-outreach-sync`.
- Existing untracked file: `repeated linkedin messages.png` (identifying prospect data; do not stage).
- This closeout, the Project Status update, and the `AGENTS.md` handoff are the documentation changes from EOS; no commit or push was made.
