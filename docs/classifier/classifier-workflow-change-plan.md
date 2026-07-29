# LT - Campaign Contact Classifier Workflow Change Plan

Target workflow:
- `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`)

## Current Production State

The old hardcoded queue-contact selection described below is historical and no longer represents the live graph. The workflow is now a published regulated-business campaign gate.

Live behavior as of 2026-07-29:
- native Schedule Trigger every 15 minutes, plus a Manual Start for controlled tests
- up to 10 Brand and 10 Dispensary candidates per run
- live GHL contact lookup and suppression cleanup
- DeepSeek acceptance for candidates without a qualified domain
- persistent qualified-domain bypass through `vapi_qualified_domains`
- GHL writes only after an accepted classification or domain match

## New Purpose

The workflow now:
- selects eligible imported pool contacts from `emerging_pool_contacts`
- maps `source_list` directly to campaign tag
- applies `vapi_campaign_brand` or `vapi_campaign_dispensary` in GHL
- returns a summary of what was tagged
- records accepted non-free email domains only after a successful tag write

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

## Current Safety Controls

- `Called Contacts` selects up to 250 rows per source pool, while `Classify` caps the live run at 10 Brand and 10 Dispensary rows.
- Candidate ranking prefers imported-pool/report phones, but the live GHL lookup can supply the phone when those fields are blank; candidates still without a live phone are skipped.
- Suppression and terminal Vapi tags are checked in SQL and again against the live GHL contact.
- DeepSeek reasoning is limited to concise English and the model output budget is 600 tokens.
- Malformed model output is ignored by `Normalize AI Classification`; it cannot reach GHL tagging.
- Qualified-domain upsert requires an accepted tag action, a recognized qualification source, and a successful GHL response containing the campaign tag.

## Why This Is Better

- It removes stale dependence on the old executive-focused `Emerald_Contacts` path.
- It aligns the classifier to the imported pool that was already split into Brand vs Dispensary.
- It makes campaign selection deterministic rather than heuristic.
- It keeps the queue feeder as the downstream pacing mechanism.

## Suggested Validation Steps

1. Run `postgres/select-emerging-pool-vapi-candidates.sql`
2. Confirm there are eligible rows in both pools
3. Update workflow `IduCoT5YOs0g2faT`
4. Execute manually or wait for the native schedule
5. Confirm the summary reports zero failed writes
6. Spot-check tags and domain persistence in GHL/Postgres
7. Let `RFIZ9Bcfl3Yvms2b` pick up the newly tagged rows
