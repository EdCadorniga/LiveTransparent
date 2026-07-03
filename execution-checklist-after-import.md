# Execution Checklist After Import

## Goal

Concrete operator checklist for the moment the GHL Brand / Dispensary imports are fully processed.

## Step 1: Run go-live check

Run:
- `postgres/emerging-pool-go-live-check.sql`

Record:
- landed Brand count
- landed Dispensary count
- seed cohort preview rows

## Step 2: If landing looks healthy, backfill contact IDs

Run:
- `postgres/backfill-emerging-pool-ghl-ids.sql`

Record:
- updated Brand rows
- updated Dispensary rows

## Step 3: Audit linkage

Run:
- `postgres/audit-emerging-pool-linkage.sql`

Check:
- duplicate Emerald IDs
- duplicate `ghl_contact_id` mappings
- missing `Em_Emerald_Contact_ID` on landed pool contacts
- queued contacts not linked back to pool rows

## Step 4: Preview seed cohort

Run:
- `postgres/select-vapi-seed-test-batch.sql`

Manual review:
- 5 Brand rows
- 5 Dispensary rows
- confirm in GHL they are correct and callable

## Step 5: Patch classifier workflow

Patch source:
- `n8n/workflow-update-payloads/lt-campaign-contact-classifier-update-ops.json`

Target workflow:
- `IduCoT5YOs0g2faT`

## Step 6: Run classifier manually

Expected:
- up to 5 Brand contacts tagged
- up to 5 Dispensary contacts tagged

## Step 7: Validate tags in GHL

Check newly tagged contacts for:
- correct campaign tag
- correct company / persona fit
- no obvious mis-tagged executive rows

## Step 8: Run queue feeder manually

Workflow:
- `RFIZ9Bcfl3Yvms2b`

Expected:
- staged rows only for the reviewed cohort
- no unexpected candidates

## Step 9: Decide on voice activation

Only proceed if all prior checks look correct.

Then:
- do manual assistant test calls
- verify queue rows
- resume paused Vapi components in controlled order

## Abort Conditions

Stop if:
- low landing coverage
- weak contact ID backfill rate
- duplicate collision pattern looks unsafe
- wrong contacts appear in seed cohort
- classifier tags wrong contacts
- feeder stages unexpected rows
