# Emerald Profile Intro Rollout Plan

Last updated: `2026-04-10`

## Objective
- Send one profile-targeted "Intro" email as the new first touch for Emerald contacts.
- Ensure contacts already in-flight or past the first 3 Emerald emails also receive this new Intro.
- Prevent duplicate intro sends.

## Current Live Context
- Existing Emerald sequence workflows are segmented by bucket and already active for historical flow:
  - Executives MSO
  - Executives SSO
  - Marketing MSO
  - Marketing SSO
- New Intro templates uploaded under folder:
  - `Emerald targeted by profile` (`69d8c788a4e06a2e22244803`)
- Template IDs are tracked in:
  - [profile-intro-template-map.json](/C:/Users/edmon/OneDrive/Documents/Projects/LiveTransparent/emerald-email-campaign/profile-intro-template-map.json)

## Guardrails (Must-Have)
- Intro is one-time per contact.
- Existing stop/suppression logic still applies:
  - `meeting booked`
  - `Do Not Nurture`
  - Email DND
- Continue using `From Email = {{contact.marketing_sender_email}}`.
- Keep current Emerald queue/enrollment routing intact for emails 2+ unless explicitly changed.

## Required Contact Fields / Tags
- Add field: `Em_Profile_Intro_Sent_At` (Date/Time)
- Add field: `Em_Profile_Intro_Template_Id` (Single line text)
- Add field: `Em_Profile_Intro_Profile_Key` (Single line text)
- Add tag: `Seq Emerald - Intro Sent`
- Add tag: `Seq Emerald - Intro Backfill Pending`
- Add tag: `Seq Emerald - Intro Backfill Done`

## Profile Resolution Model
- Resolve profile from role + company type, then map to template:
  - `mso_executive`
  - `mso_marketing`
  - `mso_finance`
  - `mso_retail_sales`
  - `sso_executive`
  - `sso_marketing`
  - `sso_finance`
  - `sso_retail_sales`
- Fallback rule if role parsing is ambiguous:
  - default to the existing active bucket family (`executive` or `marketing`) and corresponding MSO/SSO variant.

## Delivery Design
- Use two workflows:

1. `WL - Seq - Emerald Intro (New Enrollments)`
- Trigger: before enrolling into the existing Emerald sequence workflow path.
- Preconditions:
  - does not have `Seq Emerald - Intro Sent`
  - not suppressed (`meeting booked`, `Do Not Nurture`, Email DND)
  - has `marketing_sender_email`
- Actions:
  - resolve `profileKey`
  - send matching template from `profile-intro-template-map.json`
  - set `Em_Profile_Intro_Sent_At`
  - set `Em_Profile_Intro_Template_Id`
  - set `Em_Profile_Intro_Profile_Key`
  - add tag `Seq Emerald - Intro Sent`
  - continue into current Emerald queue/enrollment path for remaining emails

2. `WL - Seq - Emerald Intro (Backfill)`
- Trigger: tag added `Seq Emerald - Intro Backfill Pending`
- Preconditions:
  - has Emerald membership evidence (`Seq Enrolled - Emerald` OR any `Seq Emerald - ...` tag)
  - does not have `Seq Emerald - Intro Sent`
  - not suppressed
- Actions:
  - resolve `profileKey`
  - send matching template
  - write intro sent fields
  - add tags `Seq Emerald - Intro Sent`, `Seq Emerald - Intro Backfill Done`
  - remove tag `Seq Emerald - Intro Backfill Pending`

## Backfill Execution
- One-time backfill targeting:
  - all contacts with `Seq Enrolled - Emerald` OR `Seq Emerald - Executives MSO` OR `Seq Emerald - Executives SSO` OR `Seq Emerald - Marketing MSO` OR `Seq Emerald - Marketing SSO`
  - exclude already intro-sent contacts
- Apply tag `Seq Emerald - Intro Backfill Pending` in controlled batches.
- Suggested ramp:
  - Batch size: `100-250` contacts
  - Start window aligned with sender limits and work hours
  - Monitor deliverability and throttling between batches

## QA Checklist
- 8 test contacts (one per profile) each receives the correct template.
- Contact already past email 3 still receives Intro once via backfill.
- Re-tagging a completed contact does not re-send Intro.
- `Em_Profile_Intro_*` fields are populated for every sent contact.
- Existing sequence emails continue unaffected after intro insertion for new enrollments.

## Rollback / Safety
- If wrong template mapping is detected:
  - pause intro workflows
  - stop applying backfill pending tags
  - correct mapping and re-test on internal contacts first
- If duplicate sends appear:
  - enforce `Seq Emerald - Intro Sent` as first branch guard
  - enforce non-empty `Em_Profile_Intro_Sent_At` guard

