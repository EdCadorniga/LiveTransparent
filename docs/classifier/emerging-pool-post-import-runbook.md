# Emerging Pool Post-Import Runbook

## Purpose

Operational sequence for taking newly imported `GHL_Ready_Brands.csv` and `GHL_Ready_Dispensaries.csv` contacts from GHL import completion to Vapi-ready campaign cohorts.

## Order Of Operations

### 1. Confirm GHL import completed
- Wait until both GHL CSV imports finish processing in the GHL UI.
- Do not backfill early while contacts are still being created.

### 2. Confirm imported contacts landed in reporting raw contacts
- Run:
  - `postgres/check-emerging-pool-import-readiness.sql`

What to look for:
- both `brands` and `dispensaries` show landed contacts
- `with_emerald_contact_id` is close to landed contacts
- `landed_in_report_raw_contacts` is moving toward imported row counts

### 3. Backfill `ghl_contact_id`
- Run:
  - `postgres/backfill-emerging-pool-ghl-ids.sql`

Expected result:
- `emerging_pool_contacts.ghl_contact_id` fills for imported rows that landed in `report_raw_ghl_contacts`

### 4. Audit linkage quality
- Run:
  - `postgres/audit-emerging-pool-linkage.sql`

Pay attention to:
- duplicate Emerald IDs
- multiple Emerald rows mapping to one GHL contact
- imported pool contacts missing `Em_Emerald_Contact_ID`
- queue-linked rows and orphaned queued contacts

### 5. Optional second pass: backfill `ghl_opportunity_id`
- Run only after contact linkage looks clean:
  - `postgres/backfill-emerging-pool-ghl-opportunity-ids.sql`

### 6. Select eligible campaign candidates
- Run:
  - `postgres/select-emerging-pool-vapi-candidates.sql`

This becomes the basis for the rebuilt classifier workflow.

### 7. Select a tiny manual seed batch
- Run:
  - `postgres/select-vapi-seed-test-batch.sql`

Use this to manually inspect a representative Brand and Dispensary sample before relying on the scheduled classifier. Production runs select up to 10 Brand + 10 Dispensary candidates.

### 8. Verify classifier workflow
- Use `classifier-workflow-change-plan.md` for the current production design.
- Use `classifier-repair-plan.md` only for historical repair context.

Target workflow:
- `IduCoT5YOs0g2faT`

### 9. Scheduled tag application / controlled validation
- The published classifier runs every 15 minutes and selects up to 10 Brand + 10 Dispensary candidates per run.
- It applies campaign tags only after DeepSeek acceptance or a prior qualified-domain match, with live GHL suppression checks.
- Let queue feeder workflow `RFIZ9Bcfl3Yvms2b` stage accepted contacts gradually.

### 10. Controlled Vapi resume
- Manual assistant test calls first
- Then recheck queue rows
- Then resume paused dialer / poller in controlled order

## Recommended Safety Gates

Do not proceed to the next phase unless:
- readiness query shows contacts really landed
- `ghl_contact_id` backfill produced healthy coverage
- audit query does not show widespread duplicate collisions
- the seed batch looks correct in GHL by manual inspection

## Files In This Sequence

- `postgres/check-emerging-pool-import-readiness.sql`
- `postgres/backfill-emerging-pool-ghl-ids.sql`
- `postgres/audit-emerging-pool-linkage.sql`
- `postgres/backfill-emerging-pool-ghl-opportunity-ids.sql`
- `postgres/select-emerging-pool-vapi-candidates.sql`
- `postgres/select-vapi-seed-test-batch.sql`
- `classifier-repair-plan.md`
- `classifier-workflow-change-plan.md`
