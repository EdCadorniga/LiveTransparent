# Executive Report V1 Response-SLA Detail Closeout

Date: 2026-09-29
Scope: response-SLA/unmatched-event audit only. Other Executive Report V1 planning items were not implemented in this closeout.

## Completed

- The V1 Facts API now returns the exact selected `from`/`to` window in `window` and event-level `responseSlaDetails` rows.
- Each detail row includes contact name/ID, channel, inbound timestamp, owner name/ID, source event ID, response event metadata, status, and review metadata.
- Aggregate `responseSla` counts are calculated from the same event-detail CTE as the detail rows.
- The V1 UI now shows Responded, Internal note done, Unmatched, and Ambiguous tallies plus an event-level review table. Unmatched rows display the contact and owner.
- A reporting-only review ledger, `lt_exec_v1_response_sla_reviews`, supports `review_status = internal_note_done`. It is keyed by `inbound_event_key` and stores review timestamp, reviewer, and note reference.
- The approved read-only GHL `InternalComment` reconciler is now wired into the materializer. It searches bounded unmatched candidates, verifies contact/conversation and post-inbound timing, matches notes one-to-one, and upserts idempotently. Verification execution `1064337` processed 100 candidates and found 0 qualifying notes; the review ledger therefore remains empty.
- CRM note creation was not implemented, invoked, or tested. No outbound message or CRM mutation was performed for this work.

## Live state

| Component | ID | Final active version | State |
|---|---|---|---|
| Response SLA Materializer | `KlBw3ThLbNlMfE2J` | `5957bf7b-a52f-4131-97a6-cc07303cb4b7` | active/published, 7 nodes |
| V1 Facts API | `oxYDg6XnRBKhl1Xd` | `4039aea2-787a-420b-81ef-829b076d5cef` | active/published, 5 nodes |

The isolated V1 frontend was redeployed at `/embed/executive-v1/`. The legacy `/embed/executive/` path was checked at HTTP 200 and was not changed intentionally.

## Verification

- Response-SLA materializer webhook execution `1064144`: `success`.
- Latest scheduled materializer execution checked: `1064303`, `success`.
- Final Facts API executions checked: `1064291`, `1064292`, and `1064293`, all `success`.
- Post-approval reconciler verification: webhook execution `1064337`, `success`; 100 unmatched candidates fetched, 0 internal-note matches, 0 review rows written.
- Public API verification with `range=7d&from=2026-09-23&to=2026-09-28` returned HTTP 200 and populated JSON, including the exact window and 8 detail rows.
- That checked window returned 2 LinkedIn unmatched, 2 phone responded, 4 phone unmatched, 0 ambiguous, and 0 internal-note-done events.
- V1 page returned HTTP 200 and contained the Inbound response review card.
- `git diff --check` passed.

The first verification attempts `1064277`, `1064278`, and `1064280` were not accepted: they exposed temporary query defects (duplicate `health` CTE and an incorrect `source_event_id` reference). Those defects were repaired and the later executions above succeeded. Do not cite the failed attempts as successful tests.

## Internal-note boundary

`internal_note_done` is a supported ledger/API/UI status. The approved reconciler reads existing GHL `InternalComment` messages through the documented Conversations API and writes only the reporting review ledger. The first verification found no qualifying notes, so no rows are populated yet.

Before implementation, define and approve:

1. A structured internal-note convention that identifies the inbound event and review outcome.
2. Continued monitoring of GHL message-shape/API access and pagination.
3. The reconciler verifies contact, conversation, event ordering, note type, one-to-one matching, and idempotency before writing the review ledger.
4. Rules prevent a note on the wrong conversation, a pre-inbound note, or a normal outbound reply from closing an unmatched event.

CRM note creation remains separate and approval-gated. The report must not create notes, send follow-ups, or mutate CRM records automatically.

## Speed-to-lead/follow-up approval boundary

The current metric remains the same-channel inbound response measure, not MQL-to-first-phone-call:

- inbound LinkedIn reply → later LinkedIn DM;
- inbound call → later outbound call;
- marketing-email reply → later qualifying marketing-email send.

The read-only detail/audit enhancement and internal-note reconciliation are complete. Further Speed-to-lead & follow-up implementation—including SLA targets, automatic task creation, CRM note creation, or outbound follow-up—is **not approved for implementation**.

## Next session

1. Read this closeout, `executive_report_v1_plan.md`, `AGENTS.md`, and `RESPONSE-SLA-CONTRACT.md`.
2. Monitor the next scheduled reconciler executions and review any future `internal_note_done` rows.
3. Do not create CRM notes, tasks, follow-ups, or outbound messages without separate explicit approval.
