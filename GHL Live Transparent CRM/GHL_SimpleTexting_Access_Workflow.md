# GHL SimpleTexting Access Workflow

> Operational status: automated campaign execution and phone backfill are temporarily paused during n8n dispatcher recovery. Use this manual-send path only for controlled operator sends and verify a real provider message ID before treating a send as successful.

## Goal
Give GHL users a direct, repeatable way to send their own typed reply through SimpleTexting while keeping n8n as the provider boundary and audit layer.

## Canonical Boundary
- n8n workflow: `LT - SimpleTexting SMS Send (Webhook, Staged)`
- Webhook path: `https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms`

## Recommended GHL Workflow
Workflow name:
- `WL - SimpleTexting - Send SMS`

Trigger options:
- Manual workflow execution from a contact record
- Custom-field-backed send request
- Tag-driven queue if the team wants a staged send model

Pre-send checks:
- Contact has a phone number
- Contact is not on `simpletext_stop`
- Contact is not otherwise suppressed or DND
- Send request contains `message`
- Optional fallback: `templateKey` if the operator chooses a canned reply

Webhook action:
- Method: `POST`
- URL: `https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms`
- Content-Type: `application/json`

## Exact GHL Fields
Create these contact custom fields in GHL:

- `SimpleTexting SMS`

Recommended field types:
- `SimpleTexting SMS` -> long text

Recommended defaults:
- Workflow default `campaignKey` = `ghl_manual_sms`
- Workflow default `dryRun` = `false`

## Workflow Steps
Use this order inside GHL:

1. Start from a manual action or a contact-based trigger.
2. Let the user type the reply into `SimpleTexting SMS`.
3. Send a webhook to n8n with that field mapped into `message`.
4. If the webhook response has `ok: true`, update `SimpleTexting SMS` to blank.
5. If the webhook response is not successful, leave `SimpleTexting SMS` untouched so the user can edit and resend.
6. Let n8n handle suppression, note writing, tagging, and provider delivery.

## Freeform Send Payload
Use this when the operator types the SMS body in GHL.

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "message": "PUT_THE_OPERATOR_MESSAGE_HERE",
  "campaignKey": "ghl_manual_sms",
  "externalId": "{{contact.id}}:manual",
  "source": "ghl_workflow",
  "dryRun": false,
  "contact": {
    "first_name": "{{contact.first_name}}",
    "last_name": "{{contact.last_name}}",
    "email": "{{contact.email}}"
  }
}
```

## Template Send Payload
Use this when the operator selects a known template key.

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "templateKey": "john_sms4",
  "campaignKey": "ghl_manual_sms",
  "externalId": "{{contact.id}}:john_sms4",
  "source": "ghl_workflow",
  "dryRun": false,
  "contact": {
    "first_name": "{{contact.first_name}}",
    "last_name": "{{contact.last_name}}",
    "email": "{{contact.email}}"
  }
}
```

## Recommended Freeform Pattern
If the operator is typing the reply in GHL, store the message body in a custom field first, then map that field into the webhook payload as `message`.

Example webhook body shape:

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "message": "{{contact.custom_field.SimpleTexting_SMS}}",
  "campaignKey": "ghl_manual_sms",
  "externalId": "{{contact.id}}",
  "source": "ghl_workflow",
  "dryRun": false,
  "contact": {
    "first_name": "{{contact.first_name}}",
    "last_name": "{{contact.last_name}}",
    "email": "{{contact.email}}"
  }
}
```

## Optional Custom Fields
If you need extra control, add:
- `LT SMS Send Request ID` for retry tracking
- `LT SMS Campaign Key` if you want the campaign name editable in GHL
- `LT SMS Dry Run` if you want a field-level test toggle
- `LT SMS Template Key` for optional canned replies
- `LT SMS Send Notes` for operator notes
- `LT SMS Target User` for routing or auditing

## Expected Responses
Treat these as success:
- `ok: true`
- `action: message_sent`
- `provider: SimpleTexting`

Treat these as blocking or review states:
- `missing_phone`
- `invalid_phone`
- `invalid_account_phone`
- `missing_text`
- `unknown_template_key`
- `contact_opted_out`
- `outside_business_hours`
- `duplicate_send`
- `idempotent_webhook_error`

## Practical GHL Setup
Use the `SimpleTexting SMS` custom field for the typed message body and map that field into the webhook payload as `message`. That is the cleanest way to let GHL users send their own reply text instead of picking from predefined snippets.
Add a follow-up field update step after the webhook that blanks `SimpleTexting SMS` only when the webhook response indicates success.
The published GHL workflow `Send Simpletexting SMS from field to Contact` sends the required `x-lt-simpletexting-key` header. Keep that header aligned with the n8n-derived internal-send secret; do not remove it or substitute the legacy `x-lt-webhook-key`. This protects the outbound n8n API boundary; it does not require a SimpleTexting dashboard login.

## QA Checklist
1. Run a dry-run payload from GHL.
2. Confirm n8n resolves the contact and returns `ok: true`.
3. Confirm the note is written back into GHL.
4. Confirm requested tags are applied or removed.
5. Send one live SMS to an internal number.
6. Repeat the same payload and confirm duplicate suppression.
