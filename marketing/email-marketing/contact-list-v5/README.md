# Contact List v5 Assets

This folder contains:

- `sms-webhook-payloads.md`
  - Payload-ready SMS copy for use in GHL webhook actions that call the SimpleTexting sender workflow.
- `email-templates/`
  - HTML email templates rebuilt in the same card-style format used in `ghl create sequence plan/email-templates-cannabis-ads/`.

## Link Conventions

- Booking link:
  - `{{trigger_link.quqSUM8bckKaOIktVvgU}}`
- Website link:
  - `{{trigger_link.dxi49iAhAFbdW5cXacD7}}`

## Notes

- SMS copy is written so it can be dropped directly into the JSON payload body of a GHL webhook node.
- Email templates include a body-level `Book a Meeting` link before the signature and retain the existing CTA button pattern.
