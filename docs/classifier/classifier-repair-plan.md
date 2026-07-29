# Emerald Vapi Classifier Repair Plan

## Historical Repair Context

The original repair is complete. The old hardcoded `voice_call_queue` selection and executive-focused classifier path are no longer live. This document remains as design history; current production behavior is documented in `classifier-workflow-change-plan.md` and the audit note in `AGENTS.md`.

The current workflow is built around `emerging_pool_contacts`, uses live GHL checks, and runs on a 15-minute native schedule with a 10 + 10 candidate cap.

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

Manual Start is retained for controlled tests; production uses a native 15-minute Schedule Trigger.

1. `Manual Trigger` or `Schedule Trigger 15m`
2. `Postgres` select eligible rows from `emerging_pool_contacts`
3. `Code` normalize campaign tag payloads
4. `AI Gate` and DeepSeek classification when no qualified domain exists
5. `Merge AI and Cleanup Results`
6. `HTTP Request` add/remove GHL campaign tags
7. `Postgres` persist accepted non-free domains after successful tag writes
8. `Code` summarize counts, writes, failures, and qualification sources

## Recommended Eligibility Query Shape

The query below is the historical design skeleton. The live workflow deliberately lets candidates reach the live GHL lookup when imported/report phone fields are blank, then skips rows that remain uncallable.

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

1. Execute the manual or scheduled path and confirm the run completes
2. Confirm failed writes are zero and suppression cleanup is working
3. Spot-check accepted Brand and Dispensary tags in GHL
4. Confirm only successful accepted writes can create/update `vapi_qualified_domains`
5. Let the queue feeder consume newly tagged contacts

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
