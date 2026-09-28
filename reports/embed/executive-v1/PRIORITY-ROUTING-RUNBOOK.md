# Priority routing implementation boundary

Live verification on 2026-09-26 confirms:

- Pipeline: `Sales Outreach` / `dhdlf3O4tymxFtHk4aqq`
- Stage: `Priority` / `be636da7-3c15-48ab-b589-c75bcd6f9955`
- Position: `1`, immediately before `New`
- Cold-outbound eligibility: explicitly excluded

The existing LinkedIn inbound workflow is `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`). The automation must cover four inbound-intent sources: inbound calls, voicemail-left call dispositions, LinkedIn DMs/replies, and qualifying human email replies. Existing partnership email handlers are separate and must be adapted only after their qualifying-event filter is confirmed. The routing implementation must be attached after contact resolution and before any non-idempotent opportunity mutation.

## Current draft

- Workflow: `LT - Inbound Intent Priority Router` (`URpjcm2k5isHUyls`)
- Active version: `3a3a6ab2-79a3-4fcc-822f-52677b6ae38c`
- State: active/published, `versionId == activeVersionId`; LinkedIn, Instagram, and SMS callers are attached after persistence/contact resolution. The execute-workflow trigger itself reports `triggerCount=0` because it is not a schedule/webhook trigger.
- Managed credentials: Postgres `pgAzUqpwOiGkGXzO`; GHL bearer `LIgX7IrOQoG1BusR`
- Supported normalized channels: `linkedin`, `instagram`, `sms`, `call`, `voicemail`, `email`

The draft was validated and branch-tested with pin data only. Create `1050280`, update `1050281`, already Priority `1050282`, closed protected `1050283`, duplicate terminal `1050284`, and ambiguous open `1050285` succeeded. Corrected no-op audit projection was retested in `1050290` and `1050291`. These executions bypassed Postgres and GHL side effects and are not production smoke tests.

## Required transaction boundary

The handler must first insert the `(contact_id, source_event_id)` key into `lt_exec_v1_inbound_priority_events` with `ON CONFLICT DO NOTHING` and acquire the contact lock in `lt_exec_v1_priority_contact_locks`. A conflict returns a duplicate result and stops. Only the row that won the claim may search or mutate GHL. A closed opportunity is an explicit no-op with `disposition=closed_protected`; one unambiguous open Sales Outreach opportunity is moved to Priority; a new Priority opportunity is created only when the reviewed contract permits it. Every result is written back to the same audit row and the contact lock is released.

No live inbound execution or outbound send is used as a test fixture. Verification uses a mocked GHL adapter and exact IDs; a production smoke test requires a real qualifying event and operator approval because it writes CRM data.

Before attachment, audit the exact source contract for each caller and confirm the real GHL opportunity search response shape. Required source fields are a resolved `contact_id`, stable `source_event_id`, `occurred_at`, normalized `channel`, qualifying `reason`, optional owner/name fields, and preserved source payload. LinkedIn, Instagram, SMS, calls/voicemail, and qualifying email replies now meet this boundary. No live CRM mutation smoke test has been run.

## LinkedIn caller contract

Read-only workflow and execution inspection accepted this mapping for `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`, active version `1208f803-7fb9-4bf5-a25a-e09181874ed2`):

| Router input | LinkedIn source field |
|---|---|
| `contact_id` | `ghl_contact_id` after contact resolution |
| `source_event_id` | Unipile `message_id` |
| `occurred_at` | normalized `timestamp` |
| `channel` | literal `linkedin` |
| `reason` | literal `linkedin_inbound_reply` |
| `contact_name` | `sender_name` |
| `payload` | normalized inbound event |

Executions `986965`/`986969` and `986966`/`986971` replayed the same two message IDs, validating `message_id` as the idempotency key. The caller gate must require `is_inbound=true`, `account_type=LINKEDIN`, `event_type=message_received`, and non-empty `ghl_contact_id`, `message_id`, and valid `timestamp`.

The caller is attached in published version `dd98c27b-0fca-491c-bac1-3ff38b1b147b` after main/partnership conversation-state persistence. The router performs a live contact-owner lookup before a create and returns `owner_unresolved` rather than creating an unassigned opportunity. No live CRM mutation smoke test has been run.

## Instagram and SMS caller contracts

- Instagram `pISlgYUsyJIrLuJd` is attached in published version `e09111d7-2c63-4925-b335-741c57f5ab5d` after the durable message claim, GHL contact/message handling, and mapping upsert. It uses the provider `message_id`, original message timestamp, resolved GHL contact ID, and `channel=instagram`.
- SMS `i0pROHpFtN4LYR0Q` is attached in published version `599995a9-72ce-467d-9892-c7ddf496c3fa` after event claim, contact resolution, and SMS state upsert. It uses the provider message ID and received timestamp. STOP/unsubscribe messages are intentionally excluded from Priority routing.
- Both caller branches invoke the router with non-blocking error handling, preserving the existing inbound persistence and response path if Priority routing fails.

## Call and voicemail caller contract

The protected production candidate is `LT - Call Outcome Ingest` (`PUCfTZBANSPcgS0c`). Do not attach its output as currently normalized. It allows an empty `contact_id` and can generate a random fallback source key. An accepted caller must require:

- `direction=inbound`
- resolved non-empty GHL `contact_id`
- valid original call timestamp
- stable GHL/provider `call_id`, or a verified deterministic composite of immutable call fields
- `channel=voicemail` only when the normalized disposition is voicemail; otherwise `channel=call`
- a fixed audited reason that distinguishes inbound call from voicemail-left disposition

`LT - GHL Call Outcomes Ingest` (`CFfNeRBRuo7YRBjl`) has a call-ID-first normalizer but lacks retained live executions and has an unauthenticated webhook boundary. It is not an accepted replacement without identifying the real GHL caller and verifying payload/authentication.

## Email caller contract

Current email workflows are insufficient for Priority routing:

- `SmMf8QIfysuxQJbG` has no durable event ID/timestamp and defaults to dry-run.
- `0SQ7tTk03okegp9V` and `hxiiYCpEfMuoSt5H` detect conversation-level inbound email but do not preserve message ID or inspect the actual sender/body.
- `ZrqFN8qLKO8eVHDc` supports message/provider/event IDs, but sampled live event payloads left them empty and were opens/clicks rather than replies.

Before attachment, fetch the actual inbound email message, require a stable message ID and original timestamp, and explicitly exclude bounce, unsubscribe, out-of-office/provider, and other automated events. Use `channel=email` and a fixed qualifying reason only after that filter passes.

## Retry boundary

Call/voicemail is published in `PUCfTZBANSPcgS0c` version `f9388b9a-ab70-45b2-bc77-4f5c2efef829`. DAN/Emerald email is published in `hxiiYCpEfMuoSt5H` version `6e60f832-f175-41a8-a4b7-193f286bef18`; partnership email is published in `mRDw57IHtnQe4wOo` version `42da3b2e-4b6a-4f2f-9341-880b36292eb4`. These branches qualify stable message/call events and invoke the router non-blockingly after persistence.

The five-minute lock self-recovers only when the same event is replayed. Caller branches are non-blocking after persistence so inbound handling is preserved, but a durable claimed-event reconciler remains the next hardening item for failures that are not replayed.
