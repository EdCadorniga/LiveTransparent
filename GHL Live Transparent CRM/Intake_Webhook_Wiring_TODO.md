# Intake Webhook Wiring TODO

Last updated: 2026-02-24
Owner location: `Live Transparent`
Canonical n8n host: `https://automations.livetransparent.com`

## Completion Update (2026-02-24)
- Core sender automations are now working end-to-end:
- `WL - Micro - Email Inbound` -> `lt-warm-intake-email-inbound`
- `WL - Micro - Email Outbound` -> `lt-warm-intake-email-outbound`
- `WL - Micro - SMS` -> `lt-warm-intake-sms`
- `WL - Micro - Referral` -> `lt-warm-intake-referral`
- Live validation outcome: inbound, outbound, sms, and referral events are being received by n8n.

## 0) Preconditions
- [ ] Confirm n8n access is healthy via `n8n-lt` MCP.
- [ ] Confirm GHL API/MCP access is healthy (`ghl_official` currently available).
- [ ] Confirm the following n8n workflows are active:
- [ ] `SmMf8QIfysuxQJbG` (`lt-warm-intake-email-inbound`)
- [ ] `J4B0n0QeSeOeqAci` (`lt-warm-intake-email-outbound`)
- [ ] `5nYzp9DgQUopzWhR` (`lt-warm-intake-sms`)
- [ ] `6lp8sIS3YMB1t9Ri` (`lt-warm-intake-referral`)
- [ ] Confirm website intake workflows remain active:
- [ ] `RTV5jUiTt05lad07` (`lt-form-demo-intake`)
- [ ] `RSfLF7LU0rDC4jAI` (`lt-form-footer-intake`)

## 1) Confirm GHL micro-workflow inventory
- [ ] Open `WL - Micro - Email Inbound` in GHL.
- [ ] Open `WL - Micro - Email Outbound` in GHL.
- [ ] Open `WL - Micro - SMS` in GHL.
- [ ] Open `WL - Micro - Referral` in GHL.
- [ ] Confirm trigger conditions are present and enabled for each micro.
- [ ] If missing, create the micro workflow first using existing naming convention.

## 2) Add webhook action to Email Inbound micro
- [ ] In `WL - Micro - Email Inbound`, add a `Webhook` action after trigger/guard checks.
- [ ] Method: `POST`.
- [ ] URL: `https://automations.livetransparent.com/webhook/lt-warm-intake-email-inbound`.
- [ ] Header `Content-Type: application/json`.
- [ ] Payload:
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
- [ ] Save and publish workflow.

## 3) Add webhook action to Email Outbound micro
- [ ] In `WL - Micro - Email Outbound`, add a `Webhook` action after trigger/guard checks.
- [ ] Method: `POST`.
- [ ] URL: `https://automations.livetransparent.com/webhook/lt-warm-intake-email-outbound`.
- [ ] Header `Content-Type: application/json`.
- [ ] Payload:
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
- [ ] Save and publish workflow.

## 4) Add webhook action to SMS micro
- [ ] In `WL - Micro - SMS`, add a `Webhook` action after trigger/guard checks.
- [ ] Method: `POST`.
- [ ] URL: `https://automations.livetransparent.com/webhook/lt-warm-intake-sms`.
- [ ] Header `Content-Type: application/json`.
- [ ] Payload:
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
- [ ] Save and publish workflow.

## 5) Add webhook action to Referral micro
- [ ] In `WL - Micro - Referral`, confirm trigger is `Tag Added = Referral - Intake`.
- [ ] Add a `Webhook` action before final cleanup actions.
- [ ] Method: `POST`.
- [ ] URL: `https://automations.livetransparent.com/webhook/lt-warm-intake-referral`.
- [ ] Header `Content-Type: application/json`.
- [ ] Payload:
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
- [ ] Keep existing end-step: remove tag `Referral - Intake`.
- [ ] Save and publish workflow.

## 6) Optional generic route (only if needed)
- [ ] If a source does not map cleanly to a channel-specific endpoint, use generic endpoint.
- [ ] URL: `https://automations.livetransparent.com/webhook/lt-warm-intake-tag`.
- [ ] Add `intakeType` to payload with one of:
- [ ] `email_inbound`
- [ ] `email_outbound`
- [ ] `sms`
- [ ] `referral`
- [ ] Include `dryRun: false`.

## 7) Validate each webhook path end-to-end (one by one)
- [ ] Test Email Inbound event in GHL with a test contact.
- [ ] Verify n8n execution on `lt-warm-intake-email-inbound`.
- [ ] Verify response contains `ok: true`, `action: intake_tag_added`, `dryRun: false`.
- [ ] Verify contact has tag `Warm Intake - Email Inbound`.

- [ ] Test Email Outbound event in GHL with a test contact.
- [ ] Verify n8n execution on `lt-warm-intake-email-outbound`.
- [ ] Verify response contains `ok: true`, `action: intake_tag_added`, `dryRun: false`.
- [ ] Verify contact has tag `Warm Intake - Email Outbound`.

- [ ] Test SMS event in GHL with a test contact.
- [ ] Verify n8n execution on `lt-warm-intake-sms`.
- [ ] Verify response contains `ok: true`, `action: intake_tag_added`, `dryRun: false`.
- [ ] Verify contact has tag `Warm Intake - SMS`.

- [ ] Test Referral event (`Referral - Intake` tag add) in GHL with a test contact.
- [ ] Verify n8n execution on `lt-warm-intake-referral`.
- [ ] Verify response contains `ok: true`, `action: intake_tag_added`, `dryRun: false`.
- [ ] Verify contact has tag `Referral - Intake` from n8n step and that GHL cleanup removes it at workflow end.

## 8) Verify master routing entry behavior
- [ ] Confirm `WL - Master Warm Intake and Routing` trigger list includes all expected warm tags.
- [ ] Confirm contact enters master routing after each intake event.
- [ ] Confirm field updates happen in expected order:
- [ ] `Warm Source`
- [ ] `Primary Engagement Channel`
- [ ] `Warm Trigger Type`
- [ ] Confirm base tags applied by master route:
- [ ] `Lead Status: Warm`
- [ ] `Stage: MQL`

## 9) Observe for duplicates/collisions
- [ ] Run duplicate-event test (same contact, same channel twice).
- [ ] Run multi-channel collision test (same contact email + SMS).
- [ ] Run referral precedence test.
- [ ] Verify no duplicate/contradictory tags are left after route completion.

## 10) Update documentation after completion
- [ ] Update `AGENTS.md` with completion date and final status.
- [ ] Record which GHL micros are now actively posting webhooks.
- [ ] Record any channels still pending (Instagram/Facebook/etc.).
- [ ] Add test evidence notes (workflow IDs, sample execution timestamps, pass/fail).

## 11) Rollback plan (if issues appear)
- [ ] Disable only the newly added GHL webhook action (not full workflow) for failing channel.
- [ ] Keep channel micro trigger active if business-critical, but stop webhook POST until fixed.
- [ ] Capture failing payload + n8n error response.
- [ ] Re-test with one contact before re-enabling.

## 12) Security follow-up (separate task, required)
- [ ] Remove plaintext API keys from active n8n workflows.
- [ ] Move secrets to credentials/env references.
- [ ] Re-publish workflows and verify behavior unchanged.
