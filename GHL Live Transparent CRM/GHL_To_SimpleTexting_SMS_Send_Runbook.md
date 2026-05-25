# GHL To SimpleTexting SMS Send Runbook

## Purpose
Let a user initiate an SMS send from GHL while keeping SimpleTexting as the provider and n8n as the control layer.

This is a workflow-action integration, not a rewrite of the GHL conversation composer.

## Locked Decision
- Use a GHL workflow action or manual workflow trigger to POST to n8n.
- Do not send SMS directly from the native GHL SMS action for this path.
- Keep `LT - SimpleTexting SMS Send (Webhook, Staged)` as the canonical send boundary.
- Keep the existing idempotency, note-writing, tag-sync, and stop-tag suppression behavior.

## Operator Flow
1. A user opens a contact in GHL.
2. The user chooses either a template or a freeform message.
3. A GHL workflow posts the request to the n8n webhook.
4. n8n resolves the contact, validates the message, checks suppression, and sends through SimpleTexting.
5. n8n writes the result back to GHL as a note and any requested tag changes.

## Recommended GHL Workflow Shape
Use one workflow dedicated to SMS sends, for example `WL - SimpleTexting - Send SMS`.

Trigger options:
- Manual workflow execution from a contact record.
- A tag-based send request if the team wants a queue-driven model.
- A custom-field update if the team wants the message body stored in GHL first.

Guard conditions before the webhook:
- Contact has a phone number.
- Contact is not on `simpletext_stop`.
- Contact is not otherwise suppressed or DND.
- The send request has either a template key or a message body.

Webhook action:
- Method: `POST`
- URL: `https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms`
- Header: `x-lt-webhook-key: Lt9Qv2Xm`
- Content-Type: `application/json`

## Recommended Payload Contract

### Freeform Send
Use this when the user types the actual SMS body in GHL.

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

### Template-Based Send
Use this when the operator selects a known template instead of writing a custom body.

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

## Suggested GHL Custom Fields
If the workflow needs the user to draft the message before sending, use dedicated custom fields:
- `LT SMS Send Body`
- `LT SMS Template Key`
- `LT SMS Campaign Key`
- `LT SMS Send Request ID`

These fields keep the payload explicit and make retries auditable.

## Expected n8n Response
The GHL workflow should treat these outcomes as success paths:
- `ok: true`
- `action: message_sent`
- `provider: SimpleTexting`

The workflow should surface these as blocking outcomes:
- `missing_phone`
- `invalid_phone`
- `contact_opted_out`
- `simpletexting_send_failed`
- `duplicate_send`

## Testing Order
1. Dry run one test contact from GHL.
2. Confirm n8n receives the webhook and resolves the contact.
3. Confirm the response returns a successful dry-run result.
4. Send one live SMS to an internal phone number.
5. Confirm SimpleTexting receives the send.
6. Confirm GHL gets the note and any requested tags.
7. Repeat the same payload and verify duplicate suppression.

## Rollback
- Disable only the GHL webhook action if something fails.
- Keep the rest of the GHL workflow intact.
- Leave the n8n send workflow active so other callers are not impacted.
