# Contact List v5 SMS Webhook Payloads

Use these in a GHL webhook action where the body is sent as JSON to the n8n SimpleTexting sender.

## Recommended Payload Shape

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "message": "PASTE_SEGMENT_SMS_COPY_HERE"
}
```

## MSO Executive

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "message": "Hi {{contact.first_name}}, Cameron from Transparent. Most cannabis brands still can't properly run Meta ads. We help teams get live through compliant accounts and keep them running without constant restrictions. Let me know if this is relevant."
}
```

## MSO Marketing

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "message": "Hi {{contact.first_name}}, Cameron from Transparent. Most teams still can't fully run paid social. We help marketing teams get live and keep campaigns running without disruption. Let me know if this is relevant."
}
```

## MSO Finance

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "message": "Hi {{contact.first_name}}, Cameron from Transparent. Many teams still can't fully use paid social as a revenue channel. We help operators unlock it and keep it running reliably. Let me know if this is relevant."
}
```

## MSO Retail & Sales

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "message": "Hi {{contact.first_name}}, Cameron from Transparent. When Meta ads go down, traffic and sales usually drop too. We help teams get live and keep things running without constant restrictions. Let me know if this is relevant."
}
```

## SSO Executive

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "message": "Hi {{contact.first_name}}, Cameron from Transparent. We've seen cases where teams have to reset more often than they should when ads get interrupted. Let me know if this sounds familiar."
}
```

## SSO Marketing

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "message": "Hi {{contact.first_name}}, Cameron from Transparent. We've seen cases where campaigns get interrupted mid-execution and teams lose momentum. Let me know if this sounds familiar."
}
```

## SSO Finance

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "message": "Hi {{contact.first_name}}, Cameron from Transparent. We've seen cases where revenue becomes uneven when advertising gets interrupted. Let me know if this sounds familiar."
}
```

## SSO Retail & Sales

```json
{
  "contactId": "{{contact.id}}",
  "contactPhone": "{{contact.phone}}",
  "message": "Hi {{contact.first_name}}, Cameron from Transparent. We've seen cases where interruptions in advertising quietly create gaps in traffic and conversions. Let me know if this is something you've noticed."
}
```
