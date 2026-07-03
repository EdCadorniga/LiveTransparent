# LT - Campaign Contact Classifier Patch Snippets

Target workflow:
- `IduCoT5YOs0g2faT`

Use this after:
- `postgres/backfill-emerging-pool-ghl-ids.sql`
- optional review of `postgres/select-emerging-pool-vapi-candidates.sql`

## Replace `Called Contacts` Query

Node name:
- `Called Contacts`

Replace the current SQL with:

```sql
WITH latest_ghl_contacts AS (
  SELECT DISTINCT ON (source_key)
    source_key,
    regexp_replace(source_key, '^contact:', '') AS ghl_contact_id,
    payload_json,
    dimensions_json,
    loaded_at
  FROM report_raw_ghl_contacts
  WHERE source_system = 'ghl'
    AND source_key LIKE 'contact:%'
  ORDER BY source_key, report_date DESC, loaded_at DESC
),
eligible_contacts AS (
  SELECT
    epc.id AS emerging_pool_row_id,
    epc.emerald_contact_id,
    epc.source_list,
    epc.first_name,
    epc.last_name,
    epc.primary_email,
    epc.primary_phone,
    epc.company_name,
    epc.tags AS pool_tags,
    epc.ghl_contact_id AS contact_id,
    epc.ghl_opportunity_id,
    lgc.dimensions_json->>'tags' AS ghl_tags,
    lgc.dimensions_json->>'phone' AS ghl_phone,
    lgc.dimensions_json->>'email' AS ghl_email,
    CASE
      WHEN epc.source_list = 'brands' THEN 'brand'
      WHEN epc.source_list = 'dispensaries' THEN 'dispensary'
      ELSE NULL
    END AS campaign_id,
    CASE
      WHEN epc.source_list = 'brands' THEN 'vapi_campaign_brand'
      WHEN epc.source_list = 'dispensaries' THEN 'vapi_campaign_dispensary'
      ELSE NULL
    END AS campaign_tag
  FROM emerging_pool_contacts epc
  LEFT JOIN latest_ghl_contacts lgc
    ON lgc.ghl_contact_id = epc.ghl_contact_id
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
    )
    AND NOT EXISTS (
      SELECT 1
      WHERE lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_already_called%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_call_attempted%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_dnc%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%do not contact%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_human_answered%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_interested%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_not_interested%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_interest_unknown%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_voicemail%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_voicemail_left%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_no_answer%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_busy%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_wrong_number%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_contact_disconnected%'
    )
)
SELECT
  emerging_pool_row_id,
  emerald_contact_id,
  source_list,
  contact_id,
  campaign_id,
  campaign_tag,
  first_name,
  last_name,
  primary_email,
  primary_phone,
  company_name,
  ghl_phone,
  ghl_email
FROM eligible_contacts
WHERE campaign_tag IS NOT NULL
ORDER BY source_list, emerging_pool_row_id;
```

## Replace `Classify` Code

Node name:
- `Classify`

Recommended safe first-pass code:

```javascript
const MAX_PER_CAMPAIGN = 5;
const rows = $input.all().map((item) => item.json || {});

const grouped = {
  brand: [],
  dispensary: [],
};

for (const row of rows) {
  const campaignId = String(row.campaign_id || '').trim();
  const contactId = String(row.contact_id || '').trim();
  const campaignTag = String(row.campaign_tag || '').trim();
  if (!campaignId || !contactId || !campaignTag) continue;
  if (!grouped[campaignId]) continue;
  if (grouped[campaignId].length >= MAX_PER_CAMPAIGN) continue;

  grouped[campaignId].push({
    json: {
      emerging_pool_row_id: row.emerging_pool_row_id || null,
      emerald_contact_id: row.emerald_contact_id || null,
      source_list: row.source_list || null,
      contact_id: contactId,
      campaign_id: campaignId,
      campaign_tag: campaignTag,
      first_name: row.first_name || '',
      last_name: row.last_name || '',
      primary_email: row.primary_email || '',
      primary_phone: row.primary_phone || '',
      company_name: row.company_name || '',
    },
  });
}

return [...grouped.brand, ...grouped.dispensary];
```

After validation, raise or remove `MAX_PER_CAMPAIGN`.

## Replace `Summarize Tags` Code

Node name:
- `Summarize Tags`

Use this summary code:

```javascript
const classified = $items('Classify').map((item) => item.json || {});
const applied = $input.all().map((item) => item.json || {});

const byCampaign = {
  brand: { eligible: 0, tagged: 0 },
  dispensary: { eligible: 0, tagged: 0 },
};

for (const row of classified) {
  const key = String(row.campaign_id || '').trim();
  if (byCampaign[key]) byCampaign[key].eligible += 1;
}

for (const row of classified) {
  const key = String(row.campaign_id || '').trim();
  if (byCampaign[key]) byCampaign[key].tagged += 1;
}

return [{
  json: {
    ok: true,
    workflow: 'LT - Campaign Contact Classifier',
    eligible_count: classified.length,
    tagged_count: applied.length,
    brand_count: byCampaign.brand.eligible,
    dispensary_count: byCampaign.dispensary.eligible,
    sample_contact_ids: classified.slice(0, 10).map((row) => row.contact_id),
    sample_companies: classified.slice(0, 10).map((row) => row.company_name || row.first_name || row.contact_id),
    sample_emerging_pool_row_ids: classified.slice(0, 10).map((row) => row.emerging_pool_row_id),
  },
}];
```

## Suggested MCP Update Sequence

When you're ready to patch the workflow, use targeted updates only:

1. `updateNodeParameters` for `Called Contacts` (safe for Postgres node)
2. `updateNodeParameters` for `Classify` (safe for Code node)
3. `updateNodeParameters` for `Summarize Tags` (safe for Code node)

Avoid editing unrelated nodes.

## Validation Checklist

After patching the workflow:

1. Execute manually
2. Confirm returned candidates are only from `brands` / `dispensaries`
3. Confirm no already-called or already-queued contacts are included
4. Confirm only 5 Brand + 5 Dispensary contacts are tagged on the first pass
5. Spot-check those contacts in GHL before letting the queue feeder consume them
