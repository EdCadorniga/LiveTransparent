# Emerald Dispatcher Plan

Last updated: `2026-03-27`

## Postgres Table
- Table: `Emerald_Campaign_Contacts`
- Purpose: stable release pool for the Emerald campaign snapshot.

## Expected Columns
- `record_key`
- `ghl_contact_id`
- `first_name`
- `last_name`
- `full_name`
- `email`
- `phone`
- `created_at_source`
- `last_activity_source`
- `tags_raw`
- `bucket`
- `bucket_queue_tag`
- `marketing_sender_email`
- `email_campaign`
- `release_status`
- `released_at`
- `release_tag`
- `sender_assigned_at`
- `raw_payload`
- `ingested_at`
- `updated_at`

## Bucket Rules
- `executives_mso`
  - tags contain `cannabis-retail-mso-executive-1` or `cannabis-retail-mso-executive-2`
- `executives_sso`
  - tags contain `cannabis-retail-sso-executive-1` or `cannabis-retail-sso-executive-2`
- `marketing_mso`
  - tags contain `cannabis-retail-mso-marketing-1`
- `marketing_sso`
  - tags contain `cannabis-retail-sso-marketing-1`

## Candidate Selection
- Do not use a straight `ORDER BY id ASC` scan for live dispatch.
- Use bucket-ranked ordering so each batch interleaves:
  - `executives_mso`
  - `executives_sso`
  - `marketing_mso`
  - `marketing_sso`
- This keeps daily inflight releases mixed across MSO and SSO instead of exhausting one bucket first.

## Queue Tags
- `Enrollment Queue - Emerald - Executives MSO`
- `Enrollment Queue - Emerald - Executives SSO`
- `Enrollment Queue - Emerald - Marketing MSO`
- `Enrollment Queue - Emerald - Marketing SSO`

## GHL Exclusion Guards
- Exclude if tag `Seq Enrolled - Cannabis Ads`
- Exclude if tag `Seq Variant A`
- Exclude if tag `Seq Variant B`
- Exclude if `Email Campaign = Cannabis Ads Sequence`
- Exclude if tag `Seq Enrolled - Emerald`
- Exclude if tag `Do Not Nurture`
- Exclude if email is blank
- Exclude if email DND blocks sending

## Sender Assignment
- Field: `marketing_sender_email`
- Use the 4 verified sender emails.
- Apply cap as total outbound/day, not new-enrollment/day.
- Warmup ramp:
  - days 1-7: `300` outbound emails per sender per day
  - days 8-14: `400` outbound emails per sender per day
  - day 15 onward: `500` outbound emails per sender per day
- Keep sender assignment inside the dispatcher, not the seed import.

## Release Logging
- Table: `Emerald_Release_Log`
- Log only `queued` rows.
- Deferred or failed rows stay eligible for future retry unless explicitly marked otherwise.
