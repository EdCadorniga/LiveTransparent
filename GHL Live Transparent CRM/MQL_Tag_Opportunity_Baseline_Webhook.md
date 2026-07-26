# MQL Tag Opportunity Baseline Webhook

Purpose: when a contact receives the live `mql` tag, ensure there is a corresponding opportunity in `Warm -> Qualified (MQL)` unless the contact already has an opportunity in the `Sales` pipeline. This MQL baseline does not by itself authorize SDR assignment or promotion to `Sales Outreach`; the Janvi AI cannabis-business qualification gate is required for normal SDR promotion.

## Approved MQL Sources

The `mql` tag should only be applied for high-intent warm triggers:

- `Warm  Meta Lead Form`
- `Warm  LinkedIn Lead Form`
- `Warm  Website` when the contact came from the website lead forms:
  - Hero form
  - Footer form
- `Warm  Referral`
- Booking appointments only when the booked calendar matches `Regulated Ads On Social/Search`
- The normalized internal key can appear as `regulated-ads` or `regulated-ads-on-social-search`

The `mql` tag should not be applied universally to every contact entering `WL - Master Warm Intake and Routing`.

## Behavior

- If the contact already has any opportunity in `Sales`, do nothing.
- If the contact has a non-`Sales` opportunity, move that opportunity to:
  - Pipeline: `Warm`
  - Stage: `Qualified (MQL)`
- If the contact has no opportunity yet, create one in:
  - Pipeline: `Warm`
  - Stage: `Qualified (MQL)`
- Do not assign Jason or Marc from this baseline workflow.
- Do not move the record to `Sales Outreach` from this baseline workflow unless the downstream AI-qualified promotion contract explicitly invokes that path.

## AI-Qualified Promotion Contract

- Janvi's AI assessment is the authoritative promotion gate once its live workflow and result field/tag are confirmed.
- Only the explicit `qualified cannabis business` result may promote the contact/opportunity to `Sales Outreach -> New`.
- AI-pending/unverified records remain in Warm for Vapi verification.
- AI-rejected/non-cannabis records remain out of the Vapi queue unless a later policy explicitly changes that rule.
- SDR ownership is resolved only at Sales Outreach entry:
  - one owner present: align the other record;
  - matching owners: preserve;
  - conflicting owners: flag for review;
  - no owners: deterministic Jason/Marc 50/50 assignment.

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
  - Booking path limited to calendar `Regulated Ads On Social/Search`

The website lead-form path should be limited to contacts created by:

- `Website Lead Intake from Hero form` (`RTV5jUiTt05lad07`)
- `Website Lead Intake from Footer Form` (`RSfLF7LU0rDC4jAI`)

The booking path should be limited by the appointment/calendar identifier sent by GHL:

- allowed calendar name: `Regulated Ads On Social/Search`
- allowed normalized slug/key: `regulated-ads` or `regulated-ads-on-social-search`
- non-matching calendars must not add `mql`
- non-matching calendars must not be posted into the Slack leads alert flow

## Related Regulated Ads Booking Automation

This webhook is the `mql` baseline path only. The regulated ads booking path also has a separate live webhook flow:

- GHL filtered booking automation posts to `https://automations.livetransparent.com/webhook/wl-slack-channel-update-v2`
- n8n workflow `WL - Webhook to Slack Channel Update` sends the Slack alert
- that same n8n flow adds tag `SQL`
- that same n8n flow ensures the opportunity is in `Sales -> Discovery Scheduled`

## Live Validation Note

- The regulated ads booking path was live-tested on `2026-03-19`
- The test contact and opportunity were left in GHL intentionally for internal inspection

## Notes

- This automation intentionally does not pull an opportunity back out of the `Sales` pipeline.
- The webhook accepts multiple payload shapes for `contactId`, but the GHL sender should continue to send the simple flat payload shown above.
- The live system currently uses `mql` as the operational tag even though older docs referenced `Stage: MQL`.
