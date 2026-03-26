# Emerald Workflow Mapping

Last updated: `2026-03-27`

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

## Notes
- Batch suffixes are ignored for workflow routing.
- The original `emerald` tag alone is not enough to determine workflow bucket.
- Live GHL workflow list access works for publication checks:
  - `WL - Seq - Cannabis Ads Emerald - Executives MSO`
  - `WL - Seq - Cannabis Ads Emerald - Executives SSO`
  - `WL - Seq - Cannabis Ads Emerald - Marketing MSO`
  - `WL - Seq - Cannabis Ads Emerald - Marketing SSO`
- The direct workflow detail endpoint is not readable with the current PIT (`GET /workflow/:id` returned `401`), so use the list endpoint to confirm publish/state and inspect step wiring in the GHL UI.
- Published does not mean enrolling: if the 4 workflows show `published` but enrollments remain at `0`, the queue-tag trigger path still needs attention.
