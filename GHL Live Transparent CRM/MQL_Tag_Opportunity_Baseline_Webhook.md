# MQL Tag Opportunity Baseline Webhook

Purpose: when a contact receives the live `mql` tag, ensure there is a corresponding opportunity in `Warm -> Qualified (MQL)` unless the contact already has an opportunity in the `Sales` pipeline.

## Approved MQL Sources

The `mql` tag should only be applied for high-intent warm triggers:

- `Warm  Meta Lead Form`
- `Warm  LinkedIn Lead Form`
- `Warm  Website` when the contact came from the website lead forms:
  - Hero form
  - Footer form
- `Warm  Referral`
- Booking appointments only when the booked calendar matches `cameron-1on1-30min`

The `mql` tag should not be applied universally to every contact entering `WL - Master Warm Intake and Routing`.

## Behavior

- If the contact already has any opportunity in `Sales`, do nothing.
- If the contact has a non-`Sales` opportunity, move that opportunity to:
  - Pipeline: `Warm`
  - Stage: `Qualified (MQL)`
- If the contact has no opportunity yet, create one in:
  - Pipeline: `Warm`
  - Stage: `Qualified (MQL)`

## Locked IDs

- Warm pipeline: `FRjpDZ1HWj3UPgczsu3t`
- Warm `Qualified (MQL)`: `3b3bd98d-cbb9-4c50-8cf3-b4eba29061c2`
- Sales pipeline: `MThKauqlvnEFuFmAkyWX`

## Live n8n Workflow

- Name: `GHL - MQL Tag -> Ensure Warm Qualified Opportunity (Webhook)`
- Webhook path: `/webhook/ghl-mql-opportunity-baseline-v2`
- Full URL: `https://automations.livetransparent.com/webhook/ghl-mql-opportunity-baseline-v2`

## GHL Wiring

Create a small GHL workflow with:

- Suggested name: `WL - Micro - Stage MQL Opportunity Baseline`
- Trigger: `Contact Tag`
- Filter: tag added equals `mql`
- Action: `Webhook`
- Method: `POST`
- URL: `https://automations.livetransparent.com/webhook/ghl-mql-opportunity-baseline-v2`

Headers:

- `Content-Type: application/json`
- No authorization header is currently required for this webhook.

Recommended JSON payload:

```json
{
  "contactId": "{{contact.id}}",
  "contactName": "{{contact.name}}",
  "tag": "mql"
}
```

## Required GHL Workflow Change

In `WL - Master Warm Intake and Routing`:

- Remove `Add Tag mql` from the universal standardization block.
- Add `Add Tag mql` only inside these branches:
  - Meta Lead Form
  - LinkedIn Lead Form
  - Referral
  - Website lead-form path
  - Booking path limited to calendar `cameron-1on1-30min`

The website lead-form path should be limited to contacts created by:

- `Website Lead Intake from Hero form` (`RTV5jUiTt05lad07`)
- `Website Lead Intake from Footer Form` (`RSfLF7LU0rDC4jAI`)

The booking path should be limited by the appointment/calendar identifier sent by GHL:

- allowed calendar slug/name: `cameron-1on1-30min`
- non-matching calendars must not add `mql`
- non-matching calendars must not be posted into the Slack leads alert flow

## Notes

- This automation intentionally does not pull an opportunity back out of the `Sales` pipeline.
- The webhook accepts multiple payload shapes for `contactId`, but the GHL sender should continue to send the simple flat payload shown above.
- The live system currently uses `mql` as the operational tag even though older docs referenced `Stage: MQL`.
