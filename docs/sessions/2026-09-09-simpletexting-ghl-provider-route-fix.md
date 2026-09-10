# SimpleTexting GHL Provider Route Fix

Date: 2026-09-09

## Objective

Restore the GHL Conversations to SimpleTexting outbound path without sending an uncontrolled test SMS.

## Findings

The live GHL provider router `LT - SimpleTexting Provider Outbound Router` (`f4VoO1lBWkYRcQai`) was active and receiving POST callbacks from GHL. The latest retained outbound execution, `916048`, completed at the n8n level but returned `routed=false`, `accepted=false`, and no provider message ID after an HTTP 409 response.

The router's Code node called the stale internal path `/webhook/lt-sms-send`. The active canonical send workflow `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`) listens at `/webhook/lt-simpletexting-send-sms`. The router also carried the retired internal header value, while the canonical workflow validates its own configured internal header value. The canonical workflow defaults to dry-run unless the caller explicitly passes `dryRun=false`; the router previously passed only `simulate=false`.

## Changes Applied

Only the live router was changed:

- Updated `Process Provider Outbound` to call `/webhook/lt-simpletexting-send-sms`.
- Updated the existing `Config` assignment `internalSendHeaderValue` to match the canonical send workflow.
- Added an explicit `dryRun=false` field to the canonical send request (while retaining `simulate=false` for compatibility with the existing boundary).
- Preserved provider ID validation, GHL contact lookup, DND and `simpletext_stop` suppression, phone normalization, response handling, and all existing connections.
- Published the corrected router.

## Verification

Post-change live state:

- Router active: yes
- Router archived: no
- Node count: 7
- Trigger count: 2
- Draft version: `302ec7de-0b82-462f-9a22-b1420abf62c6`
- Active version: `302ec7de-0b82-462f-9a22-b1420abf62c6`
- Draft and active versions match: yes
- No production SMS test performed

Recent read-only checks also showed successful executions for inbound reply, delivery-event, unsubscribe-event, and phone-backfill workflows. Campaign sender workflows remain unpublished by design.

## Remaining Validation

1. Send one intentional SMS from GHL Conversations to an approved recipient.
2. Confirm the router execution reaches the canonical send workflow.
3. Confirm the canonical send response is `sent` with a provider message ID, or capture the new provider error if it remains 409.
4. Confirm the outbound message is mirrored into GHL Conversations and delivery callbacks update campaign state.

Do not run a live SMS test to an arbitrary contact. Do not enable the paused campaign sender workflows as part of this validation.

## Repository State

The worktree already contained unrelated user/agent changes before this closeout. This session added only this session record and the corresponding status entry; no unrelated files were reverted or modified.
