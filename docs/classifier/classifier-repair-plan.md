# Emerald Vapi Classifier Repair Plan

## Why This Needs Repair

- The documented classifier intent says `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) should classify Emerald candidates from Postgres and apply `vapi_campaign_brand` / `vapi_campaign_dispensary`.
- The live workflow no longer matches that description. Its current `Called Contacts` node is hardcoded to 3 specific `voice_call_queue.contact_id` values, so it is not a general classifier anymore.
- Once the imported Brand/Dispensary contacts are linked back into `emerging_pool_contacts`, the classifier should be rebuilt around that imported pool instead of the older executive-heavy `Emerald_Contacts` table.

## Target Data Source

Primary table:
- `emerging_pool_contacts`

Required fields before classification:
- `emerald_contact_id`
- `source_list`
- `primary_phone`
- `primary_email`
- `company_name`
- `tags`
- `ghl_contact_id`

Optional enrichment fields later:
- `ghl_opportunity_id`
- `ghl_import_status`

## Classification Goal

Tag imported pool contacts into one of:
- `vapi_campaign_brand`
- `vapi_campaign_dispensary`

while excluding:
- contacts already called
- contacts already queued
- DNC or already-terminal Vapi outcomes
- contacts with an authoritative qualification result that is qualified or rejected/non-cannabis; only explicitly pending/unverified contacts may enter Vapi
- contacts without a usable linked `ghl_contact_id`
- contacts without a callable phone path

## Recommended Rule Set

Do not reuse the old broad `sso` substring heuristic.

### Brand campaign candidates
- `source_list = 'brands'`
- linked `ghl_contact_id` present
- not already called or queued
- not DNC / not terminal Vapi tagged
- qualification state is explicitly pending or unverified; qualified/rejected records are excluded

### Dispensary campaign candidates
- `source_list = 'dispensaries'`
- linked `ghl_contact_id` present
- not already called or queued
- not DNC / not terminal Vapi tagged
- qualification state is explicitly pending or unverified; qualified/rejected records are excluded

This is simpler and safer than role-tag inference, because the new imports are already split into Brand vs Dispensary source pools.

## Recommended Workflow Shape

Manual trigger first, then optionally scheduled later.

1. `Manual Trigger`
2. `Postgres` select eligible rows from `emerging_pool_contacts`
3. `Code` normalize campaign tag payloads
4. `HTTP Request` add GHL tag to matching contacts
5. `Code` summarize counts and sample IDs

## Recommended Eligibility Query Shape

Pull rows from `emerging_pool_contacts` where:
- `ghl_contact_id IS NOT NULL`
- `source_list IN ('brands', 'dispensaries')`
- `primary_phone <> ''` or a later approved fallback exists
- not already present in `voice_call_attempt`
- not already present in `voice_call_queue` with `status IN ('pending', 'in_progress')`

Map tag directly:
- `brands` -> `vapi_campaign_brand`
- `dispensaries` -> `vapi_campaign_dispensary`

## Suggested SQL Skeleton

```sql
SELECT
  epc.id,
  epc.ghl_contact_id AS contact_id,
  epc.source_list,
  epc.first_name,
  epc.primary_phone,
  CASE
    WHEN epc.source_list = 'brands' THEN 'vapi_campaign_brand'
    WHEN epc.source_list = 'dispensaries' THEN 'vapi_campaign_dispensary'
    ELSE NULL
  END AS campaign_tag
FROM emerging_pool_contacts epc
WHERE epc.ghl_contact_id IS NOT NULL
  AND epc.source_list IN ('brands', 'dispensaries')
  AND COALESCE(epc.primary_phone, '') <> ''
  AND NOT EXISTS (
    SELECT 1
    FROM voice_call_attempt a
    WHERE a.contact_id = epc.ghl_contact_id
  )
  AND NOT EXISTS (
    SELECT 1
    FROM voice_call_queue q
    WHERE q.contact_id = epc.ghl_contact_id
      AND q.status IN ('pending', 'in_progress')
  );
```

## Rollout Recommendation

Phase the classifier relaunch:

1. Run once in dry/manual mode and return only a summary
2. Spot-check 10 Brand + 10 Dispensary candidates
3. Enable live tag application for a tiny cohort
4. Let the queue feeder consume those tagged contacts
5. Only then resume dialer/poller activation

## Dependency Order

1. GHL CSV import completes
2. `report_raw_ghl_contacts` lands imported contacts
3. `postgres/backfill-emerging-pool-ghl-ids.sql` runs
4. optional `postgres/backfill-emerging-pool-ghl-opportunity-ids.sql` runs later
5. classifier is rebuilt against `emerging_pool_contacts`
6. queue feeder is rechecked against real imported campaign cohorts

## Notes

- This classifier should become much simpler than the old Emerald heuristic workflow.
- The imported pool split (`brands` vs `dispensaries`) is already the campaign decision, so the main job becomes eligibility filtering, not semantic classification.
