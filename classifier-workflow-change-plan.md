# LT - Campaign Contact Classifier Workflow Change Plan

Target workflow:
- `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`)

## Current Problem

The live workflow currently does not act as a general Emerald classifier.
Its `Called Contacts` Postgres node is hardcoded to 3 specific `voice_call_queue.contact_id` values.

## New Purpose

Repurpose the workflow into a manual or low-volume helper that:
- selects eligible imported pool contacts from `emerging_pool_contacts`
- maps `source_list` directly to campaign tag
- applies `vapi_campaign_brand` or `vapi_campaign_dispensary` in GHL
- returns a summary of what was tagged

## Recommended Node Changes

### 1. `Manual Start`
- Keep as-is.

### 2. Replace `Called Contacts` query
- Keep the node type as Postgres.
- Replace the current hardcoded queue-contact query with the selection query from:
  - `postgres/select-emerging-pool-vapi-candidates.sql`
- For the workflow version, use only the main candidate-select statement, not the summary block.

Expected output fields:
- `emerging_pool_row_id`
- `emerald_contact_id`
- `source_list`
- `contact_id`
- `campaign_id`
- `campaign_tag`
- `first_name`
- `last_name`
- `primary_email`
- `primary_phone`
- `company_name`

### 3. Replace `Classify` node logic
- Current node just returns `$input.all()`.
- Update it to normalize payloads and optionally cap run size for safety.

Recommended behavior:
- pass through only rows with both `contact_id` and `campaign_tag`
- optionally limit to first N rows per run for controlled activation

Recommended output shape:
- `contact_id`
- `campaign_id`
- `campaign_tag`
- `first_name`
- `company_name`
- `emerging_pool_row_id`

### 4. Keep `Apply Campaign Tag`
- The HTTP node is structurally fine.
- It already posts to:
  - `POST /contacts/{contact_id}/tags`
- Keep batching.

Verify it still uses:
- bearer auth credential
- `Version: 2021-07-28`
- `Content-Type: application/json`
- `jsonBody = { tags: [$json.campaign_tag] }`

### 5. Update `Summarize Tags`
- Keep the node type as Code.
- Make it report:
  - total eligible selected
  - total tagged successfully
  - counts by `campaign_id`
  - sample contact IDs
  - sample company names
  - sample Emerald row IDs

Suggested summary fields:
- `eligible_count`
- `tagged_count`
- `brand_count`
- `dispensary_count`
- `sample_contact_ids`
- `sample_companies`
- `sample_emerging_pool_row_ids`

## Recommended Safe Rollout Mode

For the first live pass, constrain the `Classify` node to:
- max 5 Brand rows
- max 5 Dispensary rows

After spot-checking the actual contacts in GHL, remove or raise the cap.

## Why This Is Better

- It removes stale dependence on the old executive-focused `Emerald_Contacts` path.
- It aligns the classifier to the imported pool that was already split into Brand vs Dispensary.
- It makes campaign selection deterministic rather than heuristic.
- It keeps the queue feeder as the downstream pacing mechanism.

## Suggested Validation Steps

1. Run `postgres/select-emerging-pool-vapi-candidates.sql`
2. Confirm there are eligible rows in both pools
3. Update workflow `IduCoT5YOs0g2faT`
4. Execute manually with a small cap
5. Spot-check tags in GHL
6. Let `RFIZ9Bcfl3Yvms2b` pick up the newly tagged rows
