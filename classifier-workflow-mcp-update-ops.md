# LT - Campaign Contact Classifier MCP Update Ops

Target workflow:
- `IduCoT5YOs0g2faT`

Use these operation payloads with `n8n-lt update_workflow` after imported contacts are landed and `ghl_contact_id` backfill is done.

## Operation 1: Update `Called Contacts`

```json
{
  "type": "updateNodeParameters",
  "nodeName": "Called Contacts",
  "replace": false,
  "parameters": {
    "operation": "executeQuery",
    "query": "WITH latest_ghl_contacts AS (\n  SELECT DISTINCT ON (source_key)\n    source_key,\n    regexp_replace(source_key, '^contact:', '') AS ghl_contact_id,\n    payload_json,\n    dimensions_json,\n    loaded_at\n  FROM report_raw_ghl_contacts\n  WHERE source_system = 'ghl'\n    AND source_key LIKE 'contact:%'\n  ORDER BY source_key, report_date DESC, loaded_at DESC\n),\neligible_contacts AS (\n  SELECT\n    epc.id AS emerging_pool_row_id,\n    epc.emerald_contact_id,\n    epc.source_list,\n    epc.first_name,\n    epc.last_name,\n    epc.primary_email,\n    epc.primary_phone,\n    epc.company_name,\n    epc.tags AS pool_tags,\n    epc.ghl_contact_id AS contact_id,\n    epc.ghl_opportunity_id,\n    lgc.dimensions_json->>'tags' AS ghl_tags,\n    lgc.dimensions_json->>'phone' AS ghl_phone,\n    lgc.dimensions_json->>'email' AS ghl_email,\n    CASE\n      WHEN epc.source_list = 'brands' THEN 'brand'\n      WHEN epc.source_list = 'dispensaries' THEN 'dispensary'\n      ELSE NULL\n    END AS campaign_id,\n    CASE\n      WHEN epc.source_list = 'brands' THEN 'vapi_campaign_brand'\n      WHEN epc.source_list = 'dispensaries' THEN 'vapi_campaign_dispensary'\n      ELSE NULL\n    END AS campaign_tag\n  FROM emerging_pool_contacts epc\n  LEFT JOIN latest_ghl_contacts lgc\n    ON lgc.ghl_contact_id = epc.ghl_contact_id\n  WHERE epc.ghl_contact_id IS NOT NULL\n    AND epc.source_list IN ('brands', 'dispensaries')\n    AND COALESCE(epc.primary_phone, '') <> ''\n    AND NOT EXISTS (\n      SELECT 1\n      FROM voice_call_attempt a\n      WHERE a.contact_id = epc.ghl_contact_id\n    )\n    AND NOT EXISTS (\n      SELECT 1\n      FROM voice_call_queue q\n      WHERE q.contact_id = epc.ghl_contact_id\n        AND q.status IN ('pending', 'in_progress')\n    )\n    AND NOT EXISTS (\n      SELECT 1\n      WHERE lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_already_called%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_call_attempted%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_dnc%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%do not contact%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_human_answered%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_interested%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_not_interested%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_interest_unknown%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_voicemail%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_voicemail_left%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_no_answer%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_busy%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_wrong_number%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_contact_disconnected%'\n    )\n)\nSELECT\n  emerging_pool_row_id,\n  emerald_contact_id,\n  source_list,\n  contact_id,\n  campaign_id,\n  campaign_tag,\n  first_name,\n  last_name,\n  primary_email,\n  primary_phone,\n  company_name,\n  ghl_phone,\n  ghl_email\nFROM eligible_contacts\nWHERE campaign_tag IS NOT NULL\nORDER BY source_list, emerging_pool_row_id;"
  }
}
```

## Operation 2: Update `Classify`

```json
{
  "type": "updateNodeParameters",
  "nodeName": "Classify",
  "replace": false,
  "parameters": {
    "mode": "runOnceForAllItems",
    "language": "javaScript",
    "jsCode": "const MAX_PER_CAMPAIGN = 5;\nconst rows = $input.all().map((item) => item.json || {});\n\nconst grouped = { brand: [], dispensary: [] };\n\nfor (const row of rows) {\n  const campaignId = String(row.campaign_id || '').trim();\n  const contactId = String(row.contact_id || '').trim();\n  const campaignTag = String(row.campaign_tag || '').trim();\n  if (!campaignId || !contactId || !campaignTag) continue;\n  if (!grouped[campaignId]) continue;\n  if (grouped[campaignId].length >= MAX_PER_CAMPAIGN) continue;\n\n  grouped[campaignId].push({\n    json: {\n      emerging_pool_row_id: row.emerging_pool_row_id || null,\n      emerald_contact_id: row.emerald_contact_id || null,\n      source_list: row.source_list || null,\n      contact_id: contactId,\n      campaign_id: campaignId,\n      campaign_tag: campaignTag,\n      first_name: row.first_name || '',\n      last_name: row.last_name || '',\n      primary_email: row.primary_email || '',\n      primary_phone: row.primary_phone || '',\n      company_name: row.company_name || ''\n    }\n  });\n}\n\nreturn [...grouped.brand, ...grouped.dispensary];"
  }
}
```

## Operation 3: Update `Summarize Tags`

```json
{
  "type": "updateNodeParameters",
  "nodeName": "Summarize Tags",
  "replace": false,
  "parameters": {
    "mode": "runOnceForAllItems",
    "language": "javaScript",
    "jsCode": "const classified = $items('Classify').map((item) => item.json || {});\nconst applied = $input.all().map((item) => item.json || {});\n\nconst byCampaign = {\n  brand: { eligible: 0, tagged: 0 },\n  dispensary: { eligible: 0, tagged: 0 }\n};\n\nfor (const row of classified) {\n  const key = String(row.campaign_id || '').trim();\n  if (byCampaign[key]) byCampaign[key].eligible += 1;\n}\n\nfor (const row of applied) {\n  const key = String(row.campaign_id || '').trim();\n  if (byCampaign[key]) byCampaign[key].tagged += 1;\n}\n\nreturn [{\n  json: {\n    ok: true,\n    workflow: 'LT - Campaign Contact Classifier',\n    eligible_count: classified.length,\n    tagged_count: applied.length,\n    brand_count: byCampaign.brand.eligible,\n    dispensary_count: byCampaign.dispensary.eligible,\n    brand_tagged_count: byCampaign.brand.tagged,\n    dispensary_tagged_count: byCampaign.dispensary.tagged,\n    sample_contact_ids: classified.slice(0, 10).map((row) => row.contact_id),\n    sample_companies: classified.slice(0, 10).map((row) => row.company_name || row.first_name || row.contact_id),\n    sample_emerging_pool_row_ids: classified.slice(0, 10).map((row) => row.emerging_pool_row_id)\n  }\n}];"
  }
}
```

## Suggested Batch Apply

Pass the three operations in one atomic `update_workflow` call.

## First Manual Validation

After patching:
- execute the workflow manually
- verify it selects only up to 5 Brand + 5 Dispensary rows
- spot-check those contact IDs in GHL before letting the queue feeder continue
