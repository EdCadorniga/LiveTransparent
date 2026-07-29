# Rollback Checklist: Emerging Pool Classifier And Queue Feeder

## Use When

Use this if the first imported Brand / Dispensary cohort behaves incorrectly after classifier tagging or queue staging.

## Common Rollback Triggers

- wrong contacts received `vapi_campaign_brand` or `vapi_campaign_dispensary`
- executive or unrelated contacts appear in the cohort
- queue feeder stages contacts that should have been excluded
- too many contacts were tagged in the first pass
- queue rows appear for contacts outside the intended seed batch

## Immediate Containment

1. Disable or unpublish the classifier schedule if the bad cohort is still being selected.
2. If classifier tags were just applied, stop before re-running `RFIZ9Bcfl3Yvms2b`.
3. If the feeder already ran, do not activate downstream calling.

## Rollback Actions

### 1. Remove accidental campaign tags from GHL contacts

Remove:
- `vapi_campaign_brand`
- `vapi_campaign_dispensary`

Only from the accidentally tagged cohort.

### 2. Clean staged queue rows for that cohort

For seed-batch rollback, target only:
- `campaign_id IN ('brand', 'dispensary')`
- rows created from the bad cohort
- `status = 'pending'`

Do not mass-delete or change historical completed rows.

### 3. Re-check `voice_call_attempt`

Verify no live calls were placed.

If no attempts exist, rollback remains low-risk.

### 4. Disable classifier rerun path

Until fixed:
- do not manually rerun `IduCoT5YOs0g2faT`
- do not let the feeder re-stage the same contacts blindly

## Root Cause Review

Check these in order:

1. `postgres/select-emerging-pool-vapi-candidates.sql`
2. `postgres/select-vapi-seed-test-batch.sql`
3. `IduCoT5YOs0g2faT` live SQL and Code nodes
4. `RFIZ9Bcfl3Yvms2b` manual execution output
5. actual GHL tags on affected contacts

## Safe Resume Criteria

Do not resume until all are true:
- the candidate query returns only expected Brand / Dispensary rows
- a representative Brand and Dispensary sample is manually approved
- accidental tags are removed
- accidental queue rows are cleared or neutralized
- classifier cap remains at 10 Brand + 10 Dispensary per run for the retry

## Practical Rule

For the first imported-pool rollout, rollback should be surgical:
- remove wrong tags
- neutralize wrong pending queue rows
- fix classifier selection
- remove any incorrectly persisted domain rows before retrying
- retry only after live workflow state and suppression checks are reviewed
