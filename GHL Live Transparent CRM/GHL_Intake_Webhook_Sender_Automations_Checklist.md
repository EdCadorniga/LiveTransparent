# GHL Intake Webhook Sender Automations Checklist

Last verified: 2026-06-30 (against live n8n via n8n-lt MCP)
Canonical n8n host: https://automations.livetransparent.com
n8n version: `2.25.3`

Status: Wired for `Email Inbound`, `Email Outbound`, `SMS`, and `Referral` sender automations.
Live as of 2026-06-30: `SMS` and `Referral` webhook handlers are active; `Email Inbound` and `Email Outbound` handlers are inactive (no recent event traffic).

## What this fixes
Some n8n intake workflows are active and waiting for upstream GHL automations to send webhook events.
This checklist defines the GHL automations that should POST to those n8n endpoints.

## Important current behavior
- Website intake webhooks are already live-default (`defaultDryRun=false`).
- Warm intake tag webhooks are active but dry-run by default (`defaultDryRun=true`).
- For warm intake webhook actions below, include `"dryRun": false` in payload.

## Standard webhook action template (GHL)
- Action: `Webhook`
- Method: `POST`
- Content-Type: `application/json`
- URL format: `https://automations.livetransparent.com/webhook/<path>`

Recommended payload base:
```json
{
  "contactId": "{{contact.id}}",
  "email": "{{contact.email}}",
  "phone": "{{contact.phone}}",
  "firstName": "{{contact.first_name}}",
  "lastName": "{{contact.last_name}}",
  "dryRun": false
}
```

## Required GHL sender automations

1) Email Inbound -> n8n warm intake
- GHL workflow name: `WL - Micro - Email Inbound`
- Trigger: inbound email event condition used in your warm channel pattern
- Webhook URL: `https://automations.livetransparent.com/webhook/lt-warm-intake-email-inbound`
- Payload: standard payload base above

2) Email Outbound -> n8n warm intake
- GHL workflow name: `WL - Micro - Email Outbound`
- Trigger: outbound email event condition used in your warm channel pattern
- Webhook URL: `https://automations.livetransparent.com/webhook/lt-warm-intake-email-outbound`
- Payload: standard payload base above

3) SMS -> n8n warm intake
- GHL workflow name: `WL - Micro - SMS`
- Trigger: inbound/outbound SMS condition per your warm definition
- Webhook URL: `https://automations.livetransparent.com/webhook/lt-warm-intake-sms`
- Payload: standard payload base above

4) Referral intake -> n8n warm intake
- GHL workflow name: `WL - Micro - Referral`
- Trigger: tag added `Referral - Intake`
- Webhook URL: `https://automations.livetransparent.com/webhook/lt-warm-intake-referral`
- Payload: standard payload base above
- Keep existing end-of-flow cleanup: remove tag `Referral - Intake`

5) Optional generic intake endpoint (for future channels)
- Workflow name: any source micro where webhook path is not channel-specific
- Webhook URL: `https://automations.livetransparent.com/webhook/lt-warm-intake-tag`
- Payload:
```json
{
  "contactId": "{{contact.id}}",
  "email": "{{contact.email}}",
  "phone": "{{contact.phone}}",
  "firstName": "{{contact.first_name}}",
  "lastName": "{{contact.last_name}}",
  "intakeType": "sms",
  "dryRun": false
}
```
- Allowed `intakeType` values: `email_inbound`, `email_outbound`, `sms`, `referral`

## Already wired intake endpoints (do not duplicate blindly)
1) Website hero form intake
- n8n path: `lt-form-demo-intake`
- Full URL: `https://automations.livetransparent.com/webhook/lt-form-demo-intake`

2) Website footer form intake
- n8n path: `lt-form-footer-intake`
- Full URL: `https://automations.livetransparent.com/webhook/lt-form-footer-intake`

## Post-build validation
1) In each GHL micro workflow, use a test contact and run once.
2) Confirm n8n execution exists for matching path.
3) Confirm response JSON shows:
- `ok: true`
- `action: intake_tag_added` (for warm intake tag flows)
- `dryRun: false`
4) Confirm contact in GHL received expected intake tag.
5) Confirm contact enters `WL - Master Warm Intake and Routing` through existing tag-based trigger logic.

## If no execution appears in n8n
- If GHL shows `404 webhook is not registered`, ensure the n8n workflow is `Active` and you are hitting the production URL path (not an inactive test path).
- Verify GHL workflow trigger actually fires.
- Verify webhook URL path exactly matches (no trailing slash changes).
- Verify request payload includes either `contactId` or `email/phone`.
- Verify `dryRun` is boolean `false` (not string).
