# n8n-lt Workflow Relationships — 2026-11-04

Explicit execute-workflow targets and literal same-instance HTTP URLs only; dynamic destinations are not inferred.

## LT - LinkedIn Unipile New Messages (`7o5EBdvwAuIaWW7k`)
- execute node `Route LinkedIn Reply to Priority` → workflow `URpjcm2k5isHUyls`
- execute node `Route Partnership LinkedIn Reply to Priority` → workflow `URpjcm2k5isHUyls`
## WL - Webhook to Slack Channel - Website Visitor (`8USvJkRlKzbj6Fu1`)
- HTTP node `Sync Website Attribution` → https://automations.livetransparent.com/webhook/1ee13bc4-a95f-49ef-9e4f-28d1e0b8c6d9/lt-email-event-ingest
## LT - Call Outcome Ingest (`PUCfTZBANSPcgS0c`)
- execute node `Route Call to Priority` → workflow `URpjcm2k5isHUyls`
## LT - SimpleTexting Campaign Step Runner (`dUyOfxllvkxZavaw`)
- HTTP node `Send Claimed SMS Step` → https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms
## LT - Campaign Email Reply Poller (`hxiiYCpEfMuoSt5H`)
- execute node `Route Email Reply to Priority` → workflow `URpjcm2k5isHUyls`
## LT - SimpleTexting Inbound Reply (Webhook) (`i0pROHpFtN4LYR0Q`)
- execute node `Route SMS Reply to Priority` → workflow `URpjcm2k5isHUyls`
## LT - Partnership Reply Handler (`mRDw57IHtnQe4wOo`)
- execute node `Route Partnership Email Reply to Priority` → workflow `URpjcm2k5isHUyls`
## LT - Instagram Unipile New Messages (`pISlgYUsyJIrLuJd`)
- execute node `Route Instagram Reply to Priority` → workflow `URpjcm2k5isHUyls`

## Coverage limits

- GHL and external-provider subscriptions/callers are not discoverable from n8n alone.
- URL query strings and dynamic expressions are omitted to protect secrets and avoid guessing.
