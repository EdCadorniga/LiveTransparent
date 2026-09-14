# LinkedIn Reply Suppression Audit and Next-Session Plan

Date: 2026-09-14
Status: Read-only workflow audit complete; implementation plan recorded; no production change made.

## Request and outcome

Ed reported a LinkedIn conversation where an automated-looking message was sent after the prospect had replied. The request was to inspect the LinkedIn DM and incoming-reply workflows, then reconsider whether a last-minute GHL lookup was the best fix.

The first recommendation—add a live GHL check to every sender—was incomplete. The live workflows already have such a check in two paths, while the partnership sequence does not. More fundamentally, the GHL query checks the direction of the latest conversation message; it is not a durable record that the prospect has ever replied. The recommended primary safeguard is a persistent, LinkedIn-specific reply suppression record, written before slower inbound-processing work and checked by every automated sender. Existing GHL and cached-state checks should remain as secondary defenses.

## Live workflow audit

Live n8n state was read through the n8n API on 2026-09-14. Each listed workflow had matching draft and published version IDs at inspection time.

| Workflow | ID | Published version | Verified behavior |
| --- | --- | --- | --- |
| LT - LinkedIn Unipile New Messages | `7o5EBdvwAuIaWW7k` | `3dab7e61-b2e4-45c6-8e6d-055b8c05623e` | Receives Unipile events; identifies inbound messages by event type and sender/account user IDs. Finds a main or partnership state row by provider ID/account. Posts the message to GHL, persists the conversation map, then marks the matched state row active and records a reply event. |
| LT - LinkedIn Reply Backfill (Unipile) | `QfJ2EZcc7lZwNgxj` | `4174c177-bcb8-4e25-a837-d045d46b7c50` | Polls both main and partnership state tables. A row is selected for another check only if `dm_backfill_checked_at` is absent or at least six hours old, despite the workflow running every ten minutes. It is a delayed reconciliation path, not an immediate per-send gate. |
| LT - GHL LinkedIn Connect Dispatcher | `fXxw5lanZcDmUrst` | `346f28be-a6a4-4fc1-99c3-5b5d6ba2d0ea` | Checks contact tags and calls GHL conversation search with `lastMessageDirection=inbound` before sending a connection invite. A failed lookup skips the send. The invite template matches the repeated copy in the supplied screenshot, but the exact execution is not yet correlated. |
| LT - LinkedIn DM Sequence (Unipile) | `d0tEtijajisIsYcs` | `fcb0d053-7cac-456f-a4ad-41ba240966c0` | Candidate SQL excludes cached `dm_conversation_status=active`; the send node also checks GHL for a latest inbound conversation and skips on a failed lookup. Its message templates differ from the repeated invite copy. |
| LT - Partnership LinkedIn DM Sequence | `nspggypNF245xzeL` | `39fc0a3f-efdd-4c45-b1e5-7fb4a6990805` | Reads connected rows and suppresses only when cached `payload_json.dm_conversation_status` is `active`. It has no GHL preflight or canonical reply-event lookup immediately before `POST /chats`. This is a confirmed stale-state gap. |
| LT - Partnership LinkedIn Dispatcher | `crKIsaL5k3YBfqDZ` | `de4f7dad-dd50-470e-928a-4aaba2221aa7` | Separate partnership connection-request path; review its enrollment/invite scope when implementing the shared reply gate. |
| LT - Social Provider Outbound Router | `kqIi8i1RjFAZKrK3` | `4a688b2b-540e-401b-8bdf-8909172c138a` | GHL custom-provider outbound route. Preserve this path for human-initiated replies; do not apply automated-sequence suppression to every outbound GHL message. |
| LT - Campaign LinkedIn Reply Poller | `RIszKsd6dAh6GrU4` | `1a130f72-f104-4d43-a2e4-68096949d96d` | Reporting-only: records reply events but does not mutate send-state suppression. |
| LT - LinkedIn Follower DM Sequence (Unipile) | `pq7XVajNFnnwMUTr` | Not checked in this review | Search showed this workflow inactive. Keep inactive unless a future audit verifies otherwise. |

### Inbound ordering and key limitations

The active inbound graph currently runs:

`Normalize event → lookup contact/state → post inbound message to GHL → upsert conversation map → find state row → mark state active / record reply event`

This means the suppression flag is not persisted at the earliest inbound boundary. A scheduled sender can race the GHL post and map operations. Also, the inbound state lookup updates only the matched main or partnership row; if no state row matches the exact account/provider pair, no state flag is written.

The sender GHL queries use `lastMessageDirection=inbound` but do not identify the LinkedIn provider or require a historical inbound message. HighLevel documents this field as the direction of the **last message** in the conversation. The filter can therefore miss an older inbound reply after a later outbound message and can over-suppress on an inbound from another channel. Official reference: [HighLevel Search Conversations](https://marketplace.gohighlevel.com/docs/ghl/conversations/search-conversation/).

Unipile’s v1 new-message webhook reports both received and sent messages as `message_received`; direction must be derived by comparing the connected account user ID with the sender provider ID. The active normalizer does this. Official references: [Unipile New Messages](https://developer.unipile.com/docs/new-messages-webhook), [Unipile Webhooks overview and retries](https://developer.unipile.com/docs/webhooks-2). Webhook retries improve delivery reliability but do not replace durable suppression state.

## Best next design

1. **Create a canonical suppression record** keyed by `(unipile_account_id, linkedin_provider_id)` and store the inbound message ID/time, source, linked GHL contact IDs, and suppression reason. Enforce uniqueness/idempotency by provider message ID as well. This covers a reply even when contact/state mapping is missing or multiple campaign tables contain the same person.
2. **Write suppression immediately after classifying a confirmed inbound Unipile event**, before the GHL post, conversation-map work, or reporting side effects. Never classify the connected account’s own sent event as a prospect reply.
3. **Gate all automated outbound paths**—main connection invites, main DM sequence, partnership invites, and partnership DM sequence—on the canonical record immediately before the Unipile send call. Any suppression-read error must skip the send and produce a clear diagnostic result.
4. **Keep current checks as defense in depth.** Retain cached `dm_conversation_status` and use a fail-closed GHL lookup for reconciliation. Narrow GHL fallback checks to LinkedIn custom-provider conversations when the API supports that safely; do not use general inbound activity from unrelated channels as the permanent reply record.
5. **Preserve human replies.** Do not gate or disable the GHL custom-provider outbound router globally. Scope the terminal suppression to automated outreach, while allowing an operator to intentionally respond in the conversation.
6. **Reconcile historical replies before rollout.** Use the existing reply ledger plus Unipile/GHL conversation history to seed suppression records for contacts already in an active sequence. Establish how duplicate GHL records/provider identities map before mutating live state.

There is an unavoidable boundary race if a prospect’s message arrives after the final suppression read but immediately before the external provider accepts the outbound send. Persisting at webhook ingress and checking immediately before send minimizes this window. Do not hold a database transaction open over the external network request as a substitute; that cannot make Unipile and PostgreSQL atomic.

## Verification plan

- Add offline/unit-style coverage for direction classification, duplicate webhook delivery, unmatched state rows, multi-campaign/contact aliases, suppression-read errors, and send-path gating. Confirm the outbound call is not reached for a suppressed contact.
- Dry-run or inspect candidate/query results without invoking `/users/invite`, `/chats`, or `/chats/{id}/messages`.
- Verify each active sender reads the same canonical gate and reports `skipped: linkedin_reply_suppressed` (or an equivalent unambiguous reason).
- Do not manually execute live senders or send test LinkedIn messages without explicit approval. If production workflow changes are approved, back up current active definitions, validate draft/active parity and graph wiring, publish, then verify via read-only workflow/execution inspection.
- Correlate the supplied screenshot to a GHL contact and exact n8n execution before attributing its send. The repeated text resembles the connection invite; current evidence does not establish which workflow sent it or why its existing GHL check did not block.

## Files and current work boundary

- This handoff contains the full workflow audit and implementation plan.
- `AGENTS.md` links here near the top; `Project Status and Next Steps.md` has a concise status entry.
- No workflow, CRM record, campaign, sender, database, or live test was changed in this session.
- The supplied screenshot contains prospect-identifying conversation data. Keep it local/untracked; do not include it in Git commits.
