# n8n Cold-Outreach Workflows Runbook (Current State)

Last updated: `2026-02-21`

## Staged Workflows
- Postgres ingest (active): `kVCTmy1m8fEyP6Q7`
- GHL import (active): `T28iLcm4Hszo19MG`
- Sender release dispatcher (active/live): `NTpQnMrpjzusPXHX`

## Webhook Endpoints
- Postgres intake:
  - `https://automations.livetransparent.com/webhook/lt-cold-outreach-postgres-intake`
- GHL intake:
  - `https://automations.livetransparent.com/webhook/lt-cold-outreach-ghl-import`

## Dispatcher Behavior (Live)
- Workflow: `NTpQnMrpjzusPXHX`
- Trigger: hourly
- Mode: live (`defaultDryRun=false`)
- Global dispatch window: `Mon-Sat`, `8:00 AM ET` to `5:00 PM PT`
- Sunday behavior: summary-only execution, no dispatch
- Per-contact local-hour rule: contact local `8:00 AM-4:59 PM`
- Contact lookup path:
  - find contact by email in GHL
  - if missing, upsert/create
  - set `marketing_sender_email`
  - add `Enrollment Queue - Cannabis Ads`
  - write `ColdOutreach_Release_Log`

## Payload Contract (Both Workflows)
- Accepts either:
  - `records`: JSON array of objects (recommended for controlled batches)
  - `csvText`: CSV string including header row
- Optional fields:
  - `dryRun`: boolean (default `true`)
  - `locationId`: string (GHL workflow only; default pre-set)
  - `apiKey`: string (GHL workflow only; required when `dryRun=false` unless `GHL_PIT` env is set)

## Recommended Input Files
- Postgres:
  - `cold-outreach-prep/postgres/cold-outreach-all.dedup-email.workflow-input.csv`
- GHL:
  - `cold-outreach-prep/ghl/cold-outreach-all.dedup-email.ghl.csv`

## Dry-Run Example (PowerShell)
```powershell
$csv = Get-Content "cold-outreach-prep/ghl/cold-outreach-all.dedup-email.ghl.csv" -Raw
$body = @{
  dryRun = $true
  csvText = $csv
} | ConvertTo-Json -Depth 8

Invoke-RestMethod `
  -Method Post `
  -Uri "https://automations.livetransparent.com/webhook/lt-cold-outreach-ghl-import" `
  -ContentType "application/json" `
  -Body $body
```

## Live-Run Toggle (When Ready)
- Change only:
  - `"dryRun": false`
- For GHL live runs, provide `apiKey` in request body or set `GHL_PIT` in n8n environment.

## Safety Notes
- `kVCTmy1m8fEyP6Q7` and `T28iLcm4Hszo19MG` are active and accept webhook requests.
- Dispatcher `NTpQnMrpjzusPXHX` is active/live and self-scheduled.
- n8n API requires header auth:
  - `X-N8N-API-KEY: <key>`
  - do not use Bearer auth for n8n API endpoints.
