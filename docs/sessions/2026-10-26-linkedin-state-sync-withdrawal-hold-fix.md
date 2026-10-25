# LinkedIn State Sync Withdrawal-Hold Fix — 2026-10-26

## Objective

Diagnose and fix execution `1194006` from `LT - LinkedIn Connection State Upsert` (`Old7ZvyVYgFaJgDr`) without weakening the invitation-withdrawal safety hold.

## Finding

The `LT - LinkedIn Connection State Sync (Unipile)` workflow (`ceaKnz6E3onQrZpt`) submitted a `connection_status='ready'` upsert for an identity with an active row in `linkedin_invitation_withdrawals`. The database trigger `lt_invitation_withdrawal_hold` raised `Invitation cleanup hold blocks automated queue entry`. This was a correct rejection by the protective database guard; the defect was that the state-sync caller did not filter held identities before submitting its upsert.

Read-only database verification found 1,427 active `dispatcher_hold` rows and confirmed the failed identity matched a hold. Its existing state remained `requested`. No invitation, CRM contact, or withdrawal state was changed by the fix.

Follow-up inspection of execution `1194007` confirmed the same guard rejection for contact `6fo8QL63DDus0NbrSjLx`, with `source_workflow_name=LT - LinkedIn Connection State Sync (Unipile)` and `connection_status=ready`. It ran caller version `4cf9b218-0edd-41f1-88f3-b5d9a4e7ad94`, before the hold-aware release. The state-upsert workflow and database trigger are behaving as designed; do not replay this payload or change the state-upsert endpoint to bypass the hold.

## Change

Added `scripts/linkedin/fix_connection_state_sync_withdrawal_holds.py` to patch the live state-sync workflow. It adds a read-only Postgres query for active holds, then filters matches by contact ID, candidate contact IDs, LinkedIn public identifier, and provider ID before calling the state-upsert webhook. The result now includes `held_skipped` for operational visibility. The database trigger and state-upsert workflow were left unchanged.

## Live state and verification

- Workflow `ceaKnz6E3onQrZpt` is active and published; current `versionId` and `activeVersionId` both equal `b387672d-ef20-4ce6-a65f-220d1078cc70`.
- Live readback confirmed six nodes, including `Read Invitation Withdrawal Holds`, its Postgres query, the connection into the sync Code node, and the held-skip counter.
- The hold query ran read-only and returned 1,427 rows; it confirmed the failed identity is covered.
- The most recent recorded sync execution `1193849` (19:15 UTC) succeeded on pre-fix version `4cf9b218-0edd-41f1-88f3-b5d9a4e7ad94` with 57 processed, 38 synced, and 0 errors. It predates the hold-aware graph and does not establish runtime acceptance of `b387672d-ef20-4ce6-a65f-220d1078cc70`.
- `python -m py_compile scripts/linkedin/fix_connection_state_sync_withdrawal_holds.py` passed.
- `git diff --check` passed.
- No manual state-sync execution was run because that workflow performs legitimate connection-state writes for other contacts. Runtime acceptance is pending the next natural scheduled run; do not claim end-to-end verification until it reports held skips and no child State Upsert failure.

## Next action

After the next natural state-sync execution (expected 2026-10-26 01:15 UTC), inspect the result for `held_skipped > 0`, zero execution errors, and no failed `Old7ZvyVYgFaJgDr` child execution. Preserve the database hold trigger and do not manually replay the failed payload. If no held rows are encountered in that cycle, leave runtime acceptance pending until a natural cycle reports a held skip; do not manufacture a test upsert against a held identity.

## Security follow-up

During read-only diagnosis, existing live workflow Config credentials were inadvertently returned in a local diagnostic result. No credential values were copied into the helper or documentation. Treat the affected GHL, Unipile, and state-upsert credentials as exposed; coordinate a rotation and update all callers before considering the follow-up closed. No credential rotation was performed in this fix.
