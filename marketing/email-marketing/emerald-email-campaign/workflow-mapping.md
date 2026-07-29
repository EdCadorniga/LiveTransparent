# Emerald Workflow Mapping

Last updated: `2026-07-26`

## GHL Workflows

### 1. Executives MSO
- Workflow: `WL - Seq - Cannabis Ads Emerald - Executives MSO`
- Workflow ID: `a3f96d18-3cd1-4182-b08d-8e6bde6f77c1`
- Trigger tag: `Enrollment Queue - Emerald - Executives MSO`
- Add tag: `Seq Emerald - Executives MSO`

### 2. Executives SSO
- Workflow: `WL - Seq - Cannabis Ads Emerald - Executives SSO`
- Workflow ID: `e7a4dd5b-c6da-459c-9c48-2d5ca2bc3421`
- Trigger tag: `Enrollment Queue - Emerald - Executives SSO`
- Add tag: `Seq Emerald - Executives SSO`

### 3. Marketing MSO
- Workflow: `WL - Seq - Cannabis Ads Emerald - Marketing MSO`
- Workflow ID: `141d878e-7a27-43bc-97ab-c67c69b18f14`
- Trigger tag: `Enrollment Queue - Emerald - Marketing MSO`
- Add tag: `Seq Emerald - Marketing MSO`

### 4. Marketing SSO
- Workflow: `WL - Seq - Cannabis Ads Emerald - Marketing SSO`
- Workflow ID: `18eced4d-958a-49e4-9a23-899eabc94833`
- Trigger tag: `Enrollment Queue - Emerald - Marketing SSO`
- Add tag: `Seq Emerald - Marketing SSO`

### 5. Finance MSO
- Workflow: `WL - Seq - Cannabis Ads Emerald - Finance MSO`
- Trigger tag: `enrollment queue - emerald - finance mso`
- Add tag: `seq emerald - finance mso`

### 6. Finance SSO
- Workflow: `WL - Seq - Cannabis Ads Emerald - Finance SSO`
- Trigger tag: `enrollment queue - emerald - finance sso`
- Add tag: `seq emerald - finance sso`

### 7. Retail and Sales MSO
- Workflow: `WL - Seq - Cannabis Ads Emerald - Retail and Sales MSO`
- Trigger tag: `Enrollment Queue - Emerald - Retail and Sales MSO`
- Add tag: `Seq Emerald - Retail and Sales MSO`

### 8. Retail and Sales SSO
- Workflow: `WL - Seq - Cannabis Ads Emerald - Retail and Sales SSO`
- Trigger tag: `Enrollment Queue - Emerald - Retail and Sales SSO`
- Add tag: `Seq Emerald - Retail and Sales SSO`

## P2 Workflows

The following P2 workflows are also active and must be covered by reply/booked suppression:

- `WL - Seq - Cannabis Ads Emerald - Executives MSO - P2`
- `WL - Seq - Cannabis Ads Emerald - Executives SSO - P2`
- `WL - Seq - Cannabis Ads Emerald - Marketing MSO - P2`
- `WL - Seq - Cannabis Ads Emerald - Marketing SSO - P2`

## Common Workflow Actions
- Remove the matching Emerald queue tag on entry.
- Add `Seq Enrolled - Emerald`.
- Set `Email Campaign = Emerald Cannabis Ads`.
- Keep `From Email = {{contact.marketing_sender_email}}`.
- Keep only the first 3 emails active for v1.
- Update:
  - `Last Marketing Email`
  - `Last Marketing Email Sent At`

## Queue Routing Source Tags
- `cannabis-retail-mso-executive-1`
- `cannabis-retail-mso-executive-2`
- `cannabis-retail-mso-marketing-1`
- `cannabis-retail-sso-executive-1`
- `cannabis-retail-sso-executive-2`
- `cannabis-retail-sso-marketing-1`
- `cannabis-retail-mso-finance-1` (new)
- `cannabis-retail-sso-finance-1` (new)

## Person-Type Conflict Rule
- Every Emerald person-type campaign must exclude contacts tagged for the other person types.
- Executive campaigns exclude all marketing and finance source tags.
- Marketing campaigns exclude all executive and finance source tags.
- Finance campaigns exclude all executive and marketing source tags.
- A contact must have at most one Emerald enrollment queue tag at a time.

## Notes
- Batch suffixes are ignored for workflow routing.
- The original `emerald` tag alone is not enough to determine workflow bucket.
- Live GHL workflow list access works for publication checks:
  - `WL - Seq - Cannabis Ads Emerald - Executives MSO`
  - `WL - Seq - Cannabis Ads Emerald - Executives SSO`
  - `WL - Seq - Cannabis Ads Emerald - Marketing MSO`
  - `WL - Seq - Cannabis Ads Emerald - Marketing SSO`
- The direct workflow detail endpoint is not readable with the current PIT (`GET /workflow/:id` returned `401`), so use the list endpoint to confirm publish/state and inspect step wiring in the GHL UI.
- Published does not mean enrolling: if an Emerald workflow shows `published` but enrollments remain at `0`, the queue-tag trigger path still needs attention.

## Reply Suppression Contract

- GHL workflow: `WL - Seq - Stop on Booked/Reply/Closed`
- Workflow ID: `3dd33ec4-d8c2-40c6-b72f-d1cba57b8c39`
- Published version: `17` (2026-07-26)
- Reply trigger: `Customer Replied to Sequence Emails`, filtered to `Email`
- Removal action: remove the contact from both legacy Variant A/B workflows and all 12 Emerald sequence workflows, including P2 variants.
- The n8n `LT - Email Event Ingest` workflow is for event reporting only. It must not be treated as the suppression control.

### Incident Record: Christy Essex (2026-07-26)

An inbound reply was visible in GHL Conversations on 2026-07-23, but a later Emerald email still sent because the stop action did not include Emerald workflows. The contact was immediately removed from `seq enrolled - emerald` and `seq emerald - executives sso`; the stop workflow was then expanded and published as version 17.
