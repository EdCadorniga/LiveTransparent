# Emerald Email Campaign

Last updated: `2026-03-27`

## Summary
- Canonical workspace for the Emerald campaign rollout.
- Source snapshot: `Exported Emerald Contacts.csv`.
- Dispatch source of truth: Postgres, not the live GHL Smart List.
- Delivery system: GHL workflows.
- Release controller: n8n sender-cap dispatcher.

## Locked Decisions
- Use a fixed exported Emerald cohort as the seed set.
- Store release candidates in Postgres table `Emerald_Campaign_Contacts`.
- Use one shared reporting value: `Email Campaign = Emerald Cannabis Ads`.
- Use 4 GHL workflows:
  - `WL - Seq - Cannabis Ads Emerald - Executives MSO`
  - `WL - Seq - Cannabis Ads Emerald - Executives SSO`
  - `WL - Seq - Cannabis Ads Emerald - Marketing MSO`
  - `WL - Seq - Cannabis Ads Emerald - Marketing SSO`
- Use 4 queue tags:
  - `Enrollment Queue - Emerald - Executives MSO`
  - `Enrollment Queue - Emerald - Executives SSO`
  - `Enrollment Queue - Emerald - Marketing MSO`
  - `Enrollment Queue - Emerald - Marketing SSO`
- Use one shared enrolled tag:
  - `Seq Enrolled - Emerald`
- Use one bucket audit tag per workflow:
  - `Seq Emerald - Executives MSO`
  - `Seq Emerald - Executives SSO`
  - `Seq Emerald - Marketing MSO`
  - `Seq Emerald - Marketing SSO`
- Sender warmup:
  - days 1-7: `300` total outbound emails per sender per day, including in-flight sequence sends
  - days 8-14: `400` total outbound emails per sender per day, including in-flight sequence sends
  - day 15 onward: `500` total outbound emails per sender per day, including in-flight sequence sends

## Runtime Model
1. Ingest the exported GHL snapshot into Postgres `Emerald_Campaign_Contacts`.
2. Run the Emerald dispatcher from Postgres.
3. Before queueing, re-check suppression in GHL.
4. Apply one Emerald queue tag and set `marketing_sender_email`.
5. Let the matching GHL workflow remove the queue tag and start the sequence.

## Current Focus
- Seed Postgres from the exported GHL contact snapshot.
- Update the Emerald dispatcher to:
  - use the campaign table
  - route to 4 queue tags
  - exclude prior Cannabis Ads A/B participants
  - assign one of 4 sender emails
- Leave the 4 GHL workflows in draft until queue-tag wiring is confirmed.
