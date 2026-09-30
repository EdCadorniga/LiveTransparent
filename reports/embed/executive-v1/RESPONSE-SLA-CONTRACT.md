# Same-channel response SLA contract

## Definition

For each inbound prospect interaction in the selected period, measure the elapsed time from the inbound event to the first qualifying outbound response from the business on the same channel.

| Channel | Inbound event | Qualifying response |
|---|---|---|
| LinkedIn | Durable `linkedin_activity_events` row with `event_type` `reply_received` or `inbound_reply` | Later `linkedin_activity_events` row for the same contact/channel with `event_type` `dm_sent` |
| Email | Durable email reply event stored in `Email_Events` with reply/replied classification | Later marketing-email send event for the same contact from the campaign/release ledger |
| Phone | Inbound `report_raw_ghl_calls` row with inbound direction | Later outbound `report_raw_ghl_calls` or Vapi call attempt for the same contact |

## Required output per inbound event

- `inbound_event_id`, `contact_id`, `channel`, `inbound_at`
- `response_event_id`, `response_at`, `response_seconds`
- `response_status`: `responded`, `unmatched`, `ambiguous`, or `source_gap`
- `review_status`: `internal_note_done` after the approved read-only reconciliation finds a qualifying GHL `InternalComment`; CRM note creation is separate
- contact name/ID, channel, inbound timestamp, owner name/ID, stable source event ID, campaign key, and source workflow
- `target_minutes` only when a business SLA is explicitly configured

## Accuracy rules

- Use the first later same-channel outbound event only.
- Never match an outbound event that occurred before the inbound event.
- Do not match across channels.
- Do not count automated bounce, out-of-office, unsubscribe, or system messages as human replies.
- Preserve unmatched inbound events; they are required for the review queue.
- An internal note may close an unmatched event only when it is tied to the same contact/conversation, created after the inbound event, identified as a GHL `InternalComment`, matched one-to-one to the nearest eligible unmatched event, and recorded idempotently against the inbound event key.
- Preserve ambiguous events when multiple same-timestamp candidates exist.
- Report median, average, and percentile response time only with the event count and matched/unmatched coverage.
- “Overdue follow-up” means an unmatched inbound event older than the configured channel target; it must not be shown until targets are configured.

## Initial implementation boundary

LinkedIn, phone, and email are derived from the durable activity/call/release ledgers. Email reply events and every marketing send ledger must expose a common contact ID and timestamp. If a channel has inbound events but no later qualifying response, the facts remain `unmatched`; they are not converted to zero response time. The V1 detail implementation and approved internal-note reconciliation are read-only; CRM note creation is not performed.
