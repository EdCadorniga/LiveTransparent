# SimpleTexting GHL Mirror Guard Closeout

Date: 2026-09-24

## Finding

The supplied GHL contact showed two identical custom-provider SMS records:

- `nc6gtHV3I8SijxVNDxZe` at `2026-09-23T20:19:24.658Z`
- `7ytLOPgjzWcASmXZoCR3` at `2026-09-23T20:19:28.436Z`

The live idempotent trace recorded only one SimpleTexting provider message ID, `6ab4344e1cfe7305284262c8`, and returned `duplicate_send` for the second path. The remaining duplication was therefore in GHL conversation records: the GHL-originated message plus the n8n mirror.

## Change applied

Workflow: `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`).

- Successful send output now carries the resolved `source` value.
- The `Route Successful SMS Only` switch now requires `source != ghl_workflow` before entering `Mirror to GHL Conversations`.
- Normal GHL-originated sends keep the GHL-created custom-provider message and skip the duplicate mirror. Explicit external sources retain mirror behavior.

## Verification

- Active version: `17dae562-5f38-4438-a8bd-ee19adc6eb57`.
- `versionId == activeVersionId` and workflow remains active.
- Read-back confirmed three route conditions, including `sms-no-ghl-mirror`.
- No SMS was sent and no manual execution was run.
- `git diff --check` passed.

## Next action and safety gate

Observe natural traffic or obtain approval for one controlled SMS to an approved recipient. Confirm exactly one GHL custom-provider record and one SimpleTexting provider message ID. Do not activate campaign schedules or run additional live tests without approval.
