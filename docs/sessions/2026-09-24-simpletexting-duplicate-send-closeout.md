# SimpleTexting Duplicate Send Loop Closeout

Date: 2026-09-24

## Objective

Stop the same SimpleTexting message from being delivered twice when a legacy send is mirrored into GHL Conversations.

## Verified root cause

The legacy send path (`LT - SimpleTexting SMS Send (Webhook, Staged)`, `Q3Ivnwe4z2Y3cD7A`) sent the message and mirrored it into GHL Conversations. GHL then emitted the mirrored message to `LT - SimpleTexting Provider Outbound Router` (`f4VoO1lBWkYRcQai`), which called the idempotent sender using a different workflow identity (`provider_outbound`). Because the dedupe hash also preferred the template ID when present, the mirror did not collide with the original send.

Evidence from paired live executions on 2026-09-23:

- `984154` sent the original `john_sms2` message and returned provider ID `6ab4107a1cfe730528244128`.
- `984156` routed the GHL mirror and sent a second provider message with ID `6ab4107e7f2c1caec0c88567`.
- `984159` was a later retry and was correctly recognized as a duplicate of the second path.

## Change applied

- Provider Router node `Process Provider Outbound` now sends through the canonical workflow identity `Q3Ivnwe4z2Y3cD7A`.
- Idempotent Sender node `Prepare Request` now uses `body:${message_body}` as the dedupe key for all calls, rather than preferring `template_id`.
- No test SMS, manual execution, schedule activation, or unrelated production change was performed.

## Live verification

- Provider Router active version: `8aa3dc21-2178-4d45-85d1-7081f35164e9`.
- Idempotent Sender active version: `9d587b17-fa9a-409c-90ac-0cc8a68c2fba`.
- Both workflows are active and `versionId == activeVersionId`.
- Read-back confirmed the canonical workflow identity and body-based dedupe code are live.
- Provider Router and Idempotent Sender had zero `new`, `running`, or `waiting` executions at final verification.
- `git diff --check` passed.

## Remaining validation and safety gate

The fix has not been validated by a fresh live SMS. The next session should observe natural traffic or, with explicit approval, send one controlled SMS to an approved recipient and verify exactly one provider message ID, one GHL mirror, and the router’s duplicate/accepted response. Keep campaign schedules inactive or dry-run until that validation is complete.

## Repository state

Modified: `scripts/utilities/fix_simpletexting_boundaries.py` and `Project Status and Next Steps.md`. Added this handoff. Existing 2026-09-22 SimpleTexting closeout changes remain in the worktree and were preserved. No commit or push was performed.
