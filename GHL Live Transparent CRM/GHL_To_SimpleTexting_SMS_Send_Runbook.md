# GHL To SimpleTexting SMS Send Runbook

## Purpose
Let a user initiate a freeform SMS reply from GHL while keeping SimpleTexting as the provider and n8n as the control layer.

This is a workflow-action integration, not a rewrite of the GHL conversation composer.
For the operator-facing setup, use the companion workflow spec in
[`GHL_SimpleTexting_Access_Workflow.md`](./GHL_SimpleTexting_Access_Workflow.md).

## Locked Decision
- Use a GHL workflow action or manual workflow trigger to POST to n8n.
- Do not send SMS directly from the native GHL SMS action for this path.
- Keep `LT - SimpleTexting SMS Send (Webhook, Staged)` as the canonical send boundary.
- Keep the existing idempotency, note-writing, tag-sync, and stop-tag suppression behavior.

## Operator Flow
1. A user opens a contact in GHL.
2. The user types the reply they want to send.
3. A GHL workflow posts that typed body to the n8n webhook.
4. If n8n returns success, GHL clears `SimpleTexting SMS`.
5. n8n resolves the contact, validates the message, checks suppression, and sends through SimpleTexting.
6. n8n writes the result back to GHL as a note and any requested tag changes.

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
- The send request has a message body.
- Optional fallback: a template key if the operator chooses a canned reply.

Webhook action:
- Method: `POST`
- URL: `https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms`
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

## Suggested GHL Custom Fields
If the workflow needs the user to draft the message before sending, the only required custom field is:
- `SimpleTexting SMS`

Optional fields if you want more control:
- `LT SMS Campaign Key`
- `LT SMS Send Request ID`
- `LT SMS Dry Run`

`SimpleTexting SMS` is the field that actually holds the message the user wants sent.
The others are only for retry tracking, campaign labeling, or test mode.

## Expected n8n Response
The GHL workflow should treat these outcomes as success paths:
- `ok: true`
- `action: message_sent`
- `provider: SimpleTexting`

The workflow should surface these as blocking outcomes:
- `missing_phone`
- `invalid_phone`
- `contact_opted_out`
- `idempotent_webhook_error`
- `duplicate_send`

## Practical GHL Setup
Use the `SimpleTexting SMS` custom field for the typed message body and map that field into the webhook payload as `message`. That is the cleanest way to let GHL users send their own reply text instead of picking from predefined snippets.
Add a success-only field update step after the webhook to blank `SimpleTexting SMS`. Do not clear it on failed sends so the user can correct and resend without retyping.
Do not add any auth header on this webhook path; the live n8n endpoint is intentionally accepting the GHL call without header auth to avoid webhook-step timeouts from header mismatch.

## Testing Order
1. Dry run one test contact from GHL.
2. Confirm n8n receives the webhook and resolves the contact.
3. Confirm the response returns a successful dry-run result.
4. Send one live SMS to an internal phone number.
5. Confirm SimpleTexting receives the send.
6. Confirm GHL gets the note and any requested tags.
7. Repeat the same payload and verify duplicate suppression.

## GHL Operator Notes
- Use a manual workflow action if the sender needs to choose between a template and freeform message.
- Use a custom-field-backed payload if the team wants the message drafted in GHL before send.
- Do not use the native GHL SMS action for this path. The n8n webhook is the control boundary.
- Keep `source`, `campaignKey`, `externalId`, and `contact` in the payload so note sync and audit trails stay usable.

## Rollback
- Disable only the GHL webhook action if something fails.
- Keep the rest of the GHL workflow intact.
- Leave the n8n send workflow active so other callers are not impacted.
