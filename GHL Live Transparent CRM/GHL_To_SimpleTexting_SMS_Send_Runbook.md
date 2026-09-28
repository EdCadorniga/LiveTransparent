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

## Jason Follow-up Owner Personalization

The published `Jason Followup Emails and SMS` GHL workflow posts standard opportunity data to the active n8n SMS webhook, including `owner` and `user`. The live n8n sender (`Q3Ivnwe4z2Y3cD7A`) resolves the sender in this order:

1. Opportunity `owner` name.
2. Named assignee, if present.
3. GHL workflow `user` name.
4. `Jason` fallback.

Only Marc/Jason are selected by the current follow-up templates. The opportunity owner wins if it differs from the GHL workflow user. The resolver dynamically renders legacy keys `john_sms1` through `john_sms5`; each now includes the selected name. Keep `templateKey` unchanged in GHL. These templates contain no media, so the send is text-only `AUTO` SMS.

The sender enforces weekdays 10:00–17:00 `America/Los_Angeles`. A rejected `outside_business_hours` response is not a provider send and is not automatically replayed; verify the GHL workflow's retry/re-entry behavior before assuming a blocked invocation will run later.

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

### Canned Template Sends

For campaign messages, send `templateKey` instead of `message`. The live registry is maintained by `LT - SimpleTexting SMS Send (Webhook, Staged)` and currently supports `sms_1` through `sms_6`.

- `sms_1`, `sms_3`, and `sms_5` were refreshed on 2026-07-26.
- `sms_2`, `sms_4`, and `sms_6` were unchanged on 2026-07-26.
- Preserve legacy `john_sms1` through `john_sms5` aliases because existing GHL workflow actions still reference them.
- See [`docs/outreach/sms_edited_templatekeys.md`](../docs/outreach/sms_edited_templatekeys.md) for the current message bodies.

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

## SMS/MMS Attachment Contract

The GHL Conversations custom-provider outbound payload is the source of truth for media. Pass a hosted HTTPS URL in `attachments` when the operator sends a video or other media attachment:

```json
{
  "contactId": "{{contact.id}}",
  "phone": "{{contact.phone}}",
  "message": "Here is the video.",
  "attachments": ["https://your-host.example/video.mp4"],
  "conversationProviderId": "6a5b91913953360948dd59f1"
}
```

The live boundary applies these rules:

- No attachment: SimpleTexting `AUTO` text message.
- One HTTPS attachment: SimpleTexting `MMS_PREFERRED` with the attachment URL.
- MMS provider rejection: one `AUTO` SMS fallback containing the message and hosted URL; the result is labeled `SMS_LINK_FALLBACK`.
- More than one attachment, an invalid attachment URL, or an invalid mode: fail closed without a provider call.

The media URL is part of the idempotency key, so changing the video does not collide with a prior text-only send. The GHL conversation mirror also carries the URL in `attachments`.

## Practical GHL Setup
Use the `SimpleTexting SMS` custom field for the typed message body and map that field into the webhook payload as `message`. That is the cleanest way to let GHL users send their own reply text instead of picking from predefined snippets.
Add a success-only field update step after the webhook to blank `SimpleTexting SMS`. Do not clear it on failed sends so the user can correct and resend without retyping.
The live endpoint validates a webhook key. Preserve the authentication header already configured on the GHL caller; the existing follow-up workflow's legacy header is supported. Do not remove or change that header independently of the n8n receiver configuration, and do not copy its secret value into documentation.

## Testing Order
1. Dry-run a text-only payload and confirm `mode: AUTO`.
2. Dry-run one attachment and confirm `mode: MMS_PREFERRED`, the media URL, and the fallback text are present.
3. Dry-run two attachments and confirm `multiple_attachments_unsupported` with no provider call.
4. After explicit approval, send one live MMS to an internal phone number.
5. Confirm SimpleTexting receives either an MMS or the single URL-bearing SMS fallback.
6. Confirm GHL gets the note, delivery mode, and any requested tags.
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
