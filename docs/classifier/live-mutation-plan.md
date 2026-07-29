# Live Mutation Plan For Emerging Pool -> Vapi Resume

## Goal

Safe execution sequence once GHL import processing has completed and the imported contacts are available in reporting data.

## Preconditions

- GHL imports for `GHL_Ready_Brands.csv` and `GHL_Ready_Dispensaries.csv` are finished
- reporting ingest has landed the imported contacts into `report_raw_ghl_contacts`
- no one else is actively editing the same Vapi classifier workflow at the same time

## Execution Sequence

### Phase 1: Read-only validation

Run in this order:

1. `postgres/check-emerging-pool-import-readiness.sql`
2. `postgres/emerging-pool-go-live-check.sql`

Decision gate:
- proceed only if both `brands` and `dispensaries` show landed contacts and `Em_Emerald_Contact_ID` coverage looks healthy

### Phase 2: Contact linkage mutation

Run:

1. `postgres/backfill-emerging-pool-ghl-ids.sql`
2. `postgres/audit-emerging-pool-linkage.sql`

Decision gate:
- proceed only if contact linkage looks healthy and duplicate collisions are limited / explainable

### Phase 3: Optional opportunity linkage

Run only if needed for downstream reporting or manual review:

1. `postgres/backfill-emerging-pool-ghl-opportunity-ids.sql`

This is optional for initial Vapi seeding.

### Phase 4: Seed cohort preview

Run:

1. `postgres/select-vapi-seed-test-batch.sql`

Manual review:
- inspect the returned Brand and Dispensary contacts in GHL
- confirm they look correct for the campaign persona and are callable

### Phase 5: Classifier workflow verification

Target workflow:
- `IduCoT5YOs0g2faT`

The workflow is already published. Do not apply the historical patch payload without first fetching live state.

Confirm the live version has the 15-minute Schedule Trigger, DeepSeek gate, qualified-domain table, live-phone fallback, and successful-write domain guard.

### Phase 6: Classifier execution

Run the classifier manually.

Expected result:
- at most 10 Brand + 10 Dispensary candidates selected per run
- accepted tags and domain persistence only follow successful GHL writes

Manual check:
- confirm new GHL tags were applied correctly

### Phase 7: Queue feeder verification

Workflow:
- `RFIZ9Bcfl3Yvms2b`

Action:
- run manually only when controlled verification is needed; the classifier is already scheduled
- verify queued results match accepted/tagged contacts

### Phase 8: Controlled voice resume

Only after the seed cohort is confirmed:

1. manual assistant test call for Alex
2. manual assistant test call for Jordan
3. re-check `voice_call_queue` rows for the seed cohort
4. resume paused dialer / poller sequence in the documented order

## Mutation Safety Notes

- Prefer minimal changes to the existing workflow graph.
- Do not touch unrelated nodes in `IduCoT5YOs0g2faT`.
- Keep the first-pass per-campaign cap in place until the first cohort is reviewed.
- Leave `RFIZ9Bcfl3Yvms2b` as the pacing mechanism; do not bypass it for broad rollout.

## Stop Conditions

Pause and reassess if:
- readiness checks show poor landing coverage
- linkage audit shows many-to-one contact collisions at scale
- the classifier returns unexpected executive-style contacts
- the queue feeder inserts rows for contacts that clearly should have been excluded
