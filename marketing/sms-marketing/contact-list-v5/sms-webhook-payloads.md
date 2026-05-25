# Contact List v5 SMS Webhook Payloads

Use these in a GHL webhook action where the body is sent as JSON to the n8n SimpleTexting sender.

## Endpoint and Header

- Webhook URL: `https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms`
- Header key: `x-lt-webhook-key`
- Header value: `Lt9Qv2Xm`

## GHL Send Mode

Use the same webhook for outbound SMS initiated from GHL. The recommended pattern is a GHL workflow action or manual workflow trigger that posts a JSON payload to n8n, which then validates, dedupes, sends through SimpleTexting, and writes the result back to GHL.

Recommended fields for a GHL-originated send:
- `contactId`
- `contactPhone`
- `message` or `templateKey`
- `campaignKey`
- `externalId`
- `source`
- `dryRun`
- `contact`

## Business Hours Enforcement (Live)

- n8n now blocks sends outside business hours.
- Current live window:
- Timezone: `America/New_York` (EST/EDT)
- Days: `Mon-Fri` (`1,2,3,4,5`)
- Hours: `10:00-17:00` (local timezone above)
- If blocked, response returns `error: outside_business_hours`.
- Recommended in GHL: add a `Wait` step before webhook so contacts are only sent during this same window.

## Recommended Payload Shape

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "templateKey": "PASTE_TEMPLATE_KEY_HERE",
  "campaignKey": "ghl_manual_sms",
  "externalId": "{{contact.id}}:template",
  "source": "ghl_workflow",
  "contact": {
    "first_name": "{{contact.first_name}}",
    "last_name": "{{contact.last_name}}",
    "email": "{{contact.email}}"
  },
  "dryRun": false
}
```

## Freeform Send From GHL

If the operator is drafting the text directly in GHL, use `message` instead of `templateKey`.

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "message": "PUT_THE_OPERATOR_MESSAGE_HERE",
  "campaignKey": "ghl_manual_sms",
  "externalId": "{{contact.id}}:manual",
  "source": "ghl_workflow",
  "contact": {
    "first_name": "{{contact.first_name}}",
    "last_name": "{{contact.last_name}}",
    "email": "{{contact.email}}"
  },
  "dryRun": false
}
```

## MSO Executive

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "templateKey": "emerald_mso_executive_intro",
  "contact": {
    "first_name": "{{contact.first_name}}",
    "last_name": "{{contact.last_name}}",
    "email": "{{contact.email}}"
  },
  "dryRun": false
}
```

## MSO Marketing

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "templateKey": "emerald_mso_marketing_intro",
  "contact": {
    "first_name": "{{contact.first_name}}",
    "last_name": "{{contact.last_name}}",
    "email": "{{contact.email}}"
  },
  "dryRun": false
}
```

## MSO Finance

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "templateKey": "emerald_mso_finance_intro",
  "contact": {
    "first_name": "{{contact.first_name}}",
    "last_name": "{{contact.last_name}}",
    "email": "{{contact.email}}"
  },
  "dryRun": false
}
```

## MSO Retail & Sales

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "templateKey": "emerald_mso_retail_sales_intro",
  "contact": {
    "first_name": "{{contact.first_name}}",
    "last_name": "{{contact.last_name}}",
    "email": "{{contact.email}}"
  },
  "dryRun": false
}
```

## SSO Executive

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "templateKey": "emerald_sso_executive_intro",
  "contact": {
    "first_name": "{{contact.first_name}}",
    "last_name": "{{contact.last_name}}",
    "email": "{{contact.email}}"
  },
  "dryRun": false
}
```

## SSO Marketing

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "templateKey": "emerald_sso_marketing_intro",
  "contact": {
    "first_name": "{{contact.first_name}}",
    "last_name": "{{contact.last_name}}",
    "email": "{{contact.email}}"
  },
  "dryRun": false
}
```

## SSO Finance

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "templateKey": "emerald_sso_finance_intro",
  "contact": {
    "first_name": "{{contact.first_name}}",
    "last_name": "{{contact.last_name}}",
    "email": "{{contact.email}}"
  },
  "dryRun": false
}
```

## SSO Retail & Sales

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "templateKey": "emerald_sso_retail_sales_intro",
  "contact": {
    "first_name": "{{contact.first_name}}",
    "last_name": "{{contact.last_name}}",
    "email": "{{contact.email}}"
  },
  "dryRun": false
}
```
