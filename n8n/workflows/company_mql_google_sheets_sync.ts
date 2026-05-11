import { workflow, node, trigger, fromAi, expr, newCredential } from '@n8n/workflow-sdk';

// Manual trigger for testing
const manualTrigger = trigger({
  type: 'n8n-nodes-base.manualTrigger',
  version: 1,
  config: { name: 'Manual Trigger', position: [240, 300] }
});

// Schedule trigger - run daily at 6 AM EST
const scheduleTrigger = trigger({
  type: 'n8n-nodes-base.scheduleTrigger',
  version: 1.3,
  config: {
    name: 'Daily Schedule',
    parameters: {
      rule: {
        interval: [{
          field: 'cronExpression',
          expression: '0 6 * * *',
          tz: 'America/New_York'
        }]
      }
    },
    position: [240, 500]
  }
});

const manualBroadTrigger = trigger({
  type: 'n8n-nodes-base.manualTrigger',
  version: 1,
  config: { name: 'Manual Trigger - Broad', position: [240, 900] }
});

const scheduleBroadTrigger = trigger({
  type: 'n8n-nodes-base.scheduleTrigger',
  version: 1.3,
  config: {
    name: 'Daily Schedule - Broad',
    parameters: {
      rule: {
        interval: [{
          field: 'cronExpression',
          expression: '0 6 * * *',
          tz: 'America/New_York'
        }]
      }
    },
    position: [240, 1100]
  }
});

const spreadsheetId = '1h71qBh90rh4hK94qYEBD4MZILDEZKPiocKcajo1-BcY';

// Query Postgres for company clustering data
const queryCompanyData = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Query Company MQL Data',
    parameters: {
      operation: 'executeQuery',
      query: `
WITH contact_base AS (
  SELECT
    regexp_replace(c.source_key, '^contact:', '') AS ghl_contact_id,
    LOWER(TRIM(NULLIF(split_part(COALESCE(
      c.dimensions_json->>'email',
      c.payload_json->>'email',
      c.payload_json->>'emailAddress',
      ''
    ), '@', 2), ''))) AS email_domain,
    COALESCE(
      NULLIF(c.dimensions_json->>'email', ''),
      NULLIF(c.payload_json->>'email', ''),
      NULLIF(c.payload_json->>'emailAddress', ''),
      ''
    ) AS email,
    COALESCE(
      NULLIF(e.company_domain_key, ''),
      NULLIF(c.dimensions_json->>'company_name_for_emails', ''),
      NULLIF(c.payload_json->>'company_name_for_emails', ''),
      NULLIF(c.dimensions_json->>'company_name', ''),
      NULLIF(c.payload_json->>'companyName', ''),
      NULLIF(c.payload_json->>'company_name', ''),
      regexp_replace(c.source_key, '^contact:', '')
    ) AS company_key_candidate,
    COALESCE(
      NULLIF(e.company_name, ''),
      NULLIF(c.dimensions_json->>'company_name', ''),
      NULLIF(c.payload_json->>'companyName', ''),
      NULLIF(c.payload_json->>'company_name', ''),
      NULLIF(c.dimensions_json->>'company_name_for_emails', ''),
      NULLIF(c.payload_json->>'company_name_for_emails', ''),
      'Unknown'
    ) AS company_name,
    NULLIF(LOWER(TRIM(REGEXP_REPLACE(COALESCE(
      NULLIF(e.company_name, ''),
      NULLIF(c.dimensions_json->>'company_name', ''),
      NULLIF(c.payload_json->>'companyName', ''),
      NULLIF(c.payload_json->>'company_name', ''),
      NULLIF(c.dimensions_json->>'company_name_for_emails', ''),
      NULLIF(c.payload_json->>'company_name_for_emails', '')
    ), '[^a-z0-9]+', '-', 'g'))), '') AS company_key_from_name,
    COALESCE(
      NULLIF(c.dimensions_json->>'em_company_operating_state', ''),
      NULLIF(c.payload_json->>'em_company_operating_state', ''),
      NULLIF(c.dimensions_json->>'company_operating_state', ''),
      NULLIF(c.payload_json->>'company_operating_state', '')
    ) AS operating_state,
    COALESCE(
      NULLIF(c.dimensions_json->>'em_cannabis_marketing_signal', ''),
      NULLIF(c.payload_json->>'em_cannabis_marketing_signal', ''),
      NULLIF(c.dimensions_json->>'company_cannabis_marketing_signal', ''),
      NULLIF(c.payload_json->>'company_cannabis_marketing_signal', '')
    ) AS marketing_signal,
    COALESCE(
      NULLIF(c.payload_json->>'createdAt', ''),
      NULLIF(c.payload_json->>'created_at', ''),
      NULLIF(c.payload_json->>'dateAdded', ''),
      c.loaded_at::text
    )::date AS contact_date,
    CASE
      WHEN NULLIF(LOWER(TRIM(COALESCE(
        NULLIF(e.company_domain_key, ''),
        NULLIF(split_part(COALESCE(
          c.dimensions_json->>'email',
          c.payload_json->>'email',
          c.payload_json->>'emailAddress',
          ''
        ), '@', 2), ''),
        NULLIF(c.dimensions_json->>'company_name_for_emails', ''),
        NULLIF(c.payload_json->>'company_name_for_emails', '')
      ))), '') ~* '^[a-z0-9][a-z0-9.-]*\\.[a-z]{2,}$'
      AND NULLIF(LOWER(TRIM(COALESCE(
        NULLIF(e.company_domain_key, ''),
        NULLIF(split_part(COALESCE(
          c.dimensions_json->>'email',
          c.payload_json->>'email',
          c.payload_json->>'emailAddress',
          ''
        ), '@', 2), ''),
        NULLIF(c.dimensions_json->>'company_name_for_emails', ''),
        NULLIF(c.payload_json->>'company_name_for_emails', '')
      ))), '') !~* '^(gmail\\.com|yahoo\\.com|outlook\\.com|hotmail\\.com|icloud\\.com|aol\\.com|live\\.com|proton\\.me|protonmail\\.com|me\\.com|mail\\.com|twitter\\.com|x\\.com|linkedin\\.com|facebook\\.com|instagram\\.com|tiktok\\.com|youtube\\.com)$'
      THEN LOWER(TRIM(COALESCE(
        NULLIF(e.company_domain_key, ''),
        NULLIF(split_part(COALESCE(
          c.dimensions_json->>'email',
          c.payload_json->>'email',
          c.payload_json->>'emailAddress',
          ''
        ), '@', 2), ''),
        NULLIF(c.dimensions_json->>'company_name_for_emails', ''),
        NULLIF(c.payload_json->>'company_name_for_emails', '')
      )))
      ELSE NULL
    END AS company_key_from_domain,
    NULLIF(LOWER(TRIM(COALESCE(
      NULLIF(c.dimensions_json->>'lead_temperature', ''),
      NULLIF(c.payload_json->>'lead_temperature', ''),
      NULLIF(c.dimensions_json->>'warm_source', ''),
      NULLIF(c.payload_json->>'warm_source', ''),
      NULLIF(c.dimensions_json->>'lt_last_routing_channel', ''),
      NULLIF(c.payload_json->>'lt_last_routing_channel', ''),
      ''
    ))), '') IS NOT NULL AS is_mql
  FROM report_raw_ghl_contacts c
  LEFT JOIN "Emerald_Contacts" e
    ON e.ghl_contact_id = regexp_replace(c.source_key, '^contact:', '')
),
contacts AS (
  SELECT
    ghl_contact_id,
    email,
    company_name,
    operating_state,
    marketing_signal,
    contact_date,
    CASE
      WHEN company_key_from_domain IS NOT NULL
       AND split_part(company_key_from_domain, '.', 1) NOT IN (
        'gmail', 'yahoo', 'outlook', 'hotmail', 'icloud', 'aol', 'live',
        'proton', 'protonmail', 'mail', 'googlemail', 'me', 'mac', 'msn',
        'att', 'verizon', 'comcast', 'yandex', 'gmx', 'zoho', 'mailchimp',
        'twitter', 'x', 'linkedin', 'facebook', 'instagram', 'tiktok', 'youtube'
       )
      THEN company_key_from_domain
      WHEN company_key_from_name IS NOT NULL AND company_key_from_name <> 'unknown'
      THEN company_key_from_name
      ELSE NULL
    END AS company_key,
    is_mql
  FROM contact_base
),
opportunities AS (
  SELECT
    COALESCE(
      NULLIF(o.dimensions_json->>'contact_id', ''),
      NULLIF(o.dimensions_json->>'contact.id', ''),
      NULLIF(o.payload_json->>'contactId', ''),
      NULLIF(o.payload_json->>'contact_id', ''),
      NULLIF(o.payload_json->'contact'->>'id', '')
    ) AS ghl_contact_id,
    COALESCE(
      NULLIF(o.payload_json->>'pipelineId', ''),
      NULLIF(o.dimensions_json->>'pipeline_id', ''),
      ''
    ) AS pipeline_id,
    COALESCE(
      NULLIF(o.payload_json->>'pipelineStageId', ''),
      NULLIF(o.dimensions_json->>'pipeline_stage_id', ''),
      ''
    ) AS stage_id,
    COALESCE(
      NULLIF(o.dimensions_json->>'pipeline_name', ''),
      NULLIF(o.payload_json->>'pipelineName', ''),
      NULLIF(o.payload_json->'pipeline'->>'name', ''),
      'Warm'
    ) AS pipeline_name,
    COALESCE(
      NULLIF(o.dimensions_json->>'pipeline_stage_name', ''),
      NULLIF(o.payload_json->>'pipelineStageName', ''),
      NULLIF(o.payload_json->'pipelineStage'->>'name', ''),
      NULLIF(o.payload_json->>'stage', ''),
      'MQL'
    ) AS stage_name,
    CASE
      WHEN LOWER(TRIM(COALESCE(
        NULLIF(o.dimensions_json->>'pipeline_stage_name', ''),
        NULLIF(o.payload_json->>'pipelineStageName', ''),
        NULLIF(o.payload_json->'pipelineStage'->>'name', ''),
        NULLIF(o.payload_json->>'stage', ''),
        'MQL'
      ))) IN ('disqualified', 'closed lost', 'closed won')
      THEN FALSE
      ELSE TRUE
    END AS is_active_pipeline
  FROM report_raw_ghl_opportunities o
),
company_rollup AS (
  SELECT
    ck.company_key,
    COALESCE(NULLIF(MAX(ck.company_name), ''), 'Unknown') AS company_name,
    COUNT(DISTINCT ck.ghl_contact_id) AS contact_count,
    COUNT(DISTINCT ck.ghl_contact_id) FILTER (WHERE o.ghl_contact_id IS NOT NULL) AS pipeline_contact_count,
    STRING_AGG(DISTINCT ck.email, ', ' ORDER BY ck.email) AS contact_emails,
    jsonb_agg(DISTINCT jsonb_build_object('contact_id', ck.ghl_contact_id, 'email', ck.email)) AS contacts,
    COALESCE(STRING_AGG(DISTINCT o.pipeline_name, '|' ), '') AS pipelines,
    COALESCE(STRING_AGG(DISTINCT o.stage_name, '|' ), '') AS stage_names,
    MAX(ck.operating_state) AS operating_state,
    MAX(ck.marketing_signal) AS marketing_signal,
    MAX(ck.contact_date) AS latest_contact_date,
    COALESCE(BOOL_OR(ck.is_mql), FALSE) AS has_mql,
    COALESCE(BOOL_OR(o.is_active_pipeline), FALSE) AS has_pipeline_contact
  FROM contacts ck
  LEFT JOIN opportunities o
    ON o.ghl_contact_id = ck.ghl_contact_id
   AND o.is_active_pipeline
  WHERE ck.company_key IS NOT NULL
  GROUP BY ck.company_key
)
SELECT
  company_key,
  company_name,
  contact_count,
  pipeline_contact_count,
  contact_emails,
  contacts,
  pipelines,
  stage_names,
  operating_state,
  marketing_signal,
  latest_contact_date
FROM company_rollup
WHERE contact_count >= 1
  AND pipeline_contact_count >= 2
  AND company_key IS NOT NULL
ORDER BY pipeline_contact_count DESC, contact_count DESC, latest_contact_date DESC
LIMIT 5000;
      `,
      options: {
        queryReplacement: '',
        replaceEmptyStrings: false
      }
    },
    position: [540, 300],
    credentials: {
      postgres: newCredential('Postgres account')
    }
  }
});

// Prepare data for Google Sheets - flatten the JSON
const prepareData = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Prepare Sheet Data',
    parameters: {
      jsCode: `
const items = $input.all();
const result = [];

for (const item of items) {
  const json = item.json || {};
  
  // Parse contacts JSON array
  let contactList = [];
  try {
    contactList = typeof json.contacts === 'string' ? JSON.parse(json.contacts) : (json.contacts || []);
  } catch (e) {
    contactList = [];
  }
  
  const contactEmails = contactList.map(c => c.email || '').filter(Boolean).join(', ');
  const contactIds = contactList.map(c => c.contact_id || '').filter(Boolean).join(', ');
  
  result.push({
      json: {
        company_key: json.company_key || '',
        company_name: json.company_name || json.company_key || 'Unknown',
        contact_count: json.contact_count || 0,
        pipeline_contact_count: json.pipeline_contact_count || 0,
      contact_emails: contactEmails,
      contact_ids: contactIds,
      pipelines: json.pipelines || '',
      stages: json.stage_names || '',
      operating_state: json.operating_state || '',
      marketing_signal: json.marketing_signal || '',
      latest_contact_date: json.latest_contact_date || ''
    }
  });
}

return result;
      `
    },
    position: [840, 300]
  }
});

// Build row items for the Google Sheets update node.
const buildSheetPayload = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Build Sheet Payload',
    parameters: {
      jsCode: `
const headers = [
  'company_key',
  'company_name',
  'contact_count',
  'pipeline_contact_count',
  'contact_emails',
  'contact_ids',
  'pipelines',
  'stages',
  'operating_state',
  'marketing_signal',
  'latest_contact_date',
];

const targetRowCount = 4999;
const sourceRows = $input.all().map((item) => item.json || {}).slice(0, targetRowCount);
const dataRows = sourceRows.map((row) => headers.map((key) => {
  const value = row[key];
  return value === null || value === undefined ? '' : String(value);
}));

while (dataRows.length < targetRowCount) {
  dataRows.push(Array(headers.length).fill(''));
}

return [{
  json: {
    values: [headers, ...dataRows],
    generated_at: new Date().toISOString(),
    total_companies: sourceRows.length,
    spreadsheet_url: 'https://docs.google.com/spreadsheets/d/1h71qBh90rh4hK94qYEBD4MZILDEZKPiocKcajo1-BcY',
  },
}];
      `
    },
    position: [1080, 300]
  }
});

const writeSheetSnapshot = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.4,
  config: {
    name: 'Write Sheet Snapshot',
    parameters: {
      method: 'PUT',
      url: `https://sheets.googleapis.com/v4/spreadsheets/${spreadsheetId}/values/Company%20MQLs!A1:K5000?valueInputOption=USER_ENTERED&includeValuesInResponse=false`,
      authentication: 'predefinedCredentialType',
      nodeCredentialType: 'googleSheetsOAuth2Api',
      sendHeaders: true,
      specifyHeaders: 'keypair',
      headerParameters: {
        parameters: [
          { name: 'Content-Type', value: 'application/json' },
          { name: 'Accept', value: 'application/json' }
        ]
      },
      sendBody: true,
      contentType: 'json',
      specifyBody: 'json',
      jsonBody: '={{ { majorDimension: "ROWS", values: $json.values } }}',
      options: {
        timeout: 30000
      }
    },
    position: [1320, 300],
    credentials: {
      googleSheetsOAuth2Api: newCredential('Google Sheets account')
    }
  }
});

// Update spreadsheet title with timestamp
const updateTimestamp = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Add Timestamp',
    parameters: {
      values: {
        string: [
          {
            name: 'spreadsheet_url',
            value: `https://docs.google.com/spreadsheets/d/${spreadsheetId}`
          },
          {
            name: 'generated_at',
            value: '={{ new Date().toISOString() }}'
          },
          {
            name: 'total_companies',
            value: '={{ $json.total_companies || 0 }}'
          }
        ]
      }
    },
    position: [1560, 300]
  }
});

const createAllCompaniesSheet = node({
  type: 'n8n-nodes-base.googleSheets',
  version: 4.7,
  config: {
    name: 'Ensure All Companies Sheet',
    parameters: {
      resource: 'sheet',
      operation: 'create',
      authentication: 'oAuth2',
      documentId: { __rl: true, mode: 'id', value: spreadsheetId },
      title: 'All Companies',
      options: {
        index: 1
      }
    },
    position: [540, 900],
    onError: 'continueRegularOutput',
    credentials: {
      googleSheetsOAuth2Api: newCredential('Google Sheets account')
    }
  }
});

const queryAllCompaniesData = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Query All Companies Data',
    parameters: {
      operation: 'executeQuery',
      query: `
WITH contact_base AS (
  SELECT
    regexp_replace(c.source_key, '^contact:', '') AS ghl_contact_id,
    LOWER(TRIM(NULLIF(split_part(COALESCE(
      c.dimensions_json->>'email',
      c.payload_json->>'email',
      c.payload_json->>'emailAddress',
      ''
    ), '@', 2), ''))) AS email_domain,
    COALESCE(
      NULLIF(c.dimensions_json->>'email', ''),
      NULLIF(c.payload_json->>'email', ''),
      NULLIF(c.payload_json->>'emailAddress', ''),
      ''
    ) AS email,
    COALESCE(
      NULLIF(e.company_domain_key, ''),
      NULLIF(c.dimensions_json->>'company_name_for_emails', ''),
      NULLIF(c.payload_json->>'company_name_for_emails', ''),
      NULLIF(c.dimensions_json->>'company_name', ''),
      NULLIF(c.payload_json->>'companyName', ''),
      NULLIF(c.payload_json->>'company_name', ''),
      regexp_replace(c.source_key, '^contact:', '')
    ) AS company_key_candidate,
    COALESCE(
      NULLIF(e.company_name, ''),
      NULLIF(c.dimensions_json->>'company_name', ''),
      NULLIF(c.payload_json->>'companyName', ''),
      NULLIF(c.payload_json->>'company_name', ''),
      NULLIF(c.dimensions_json->>'company_name_for_emails', ''),
      NULLIF(c.payload_json->>'company_name_for_emails', ''),
      'Unknown'
    ) AS company_name,
    COALESCE(
      NULLIF(c.dimensions_json->>'em_company_operating_state', ''),
      NULLIF(c.payload_json->>'em_company_operating_state', ''),
      NULLIF(c.dimensions_json->>'company_operating_state', ''),
      NULLIF(c.payload_json->>'company_operating_state', '')
    ) AS operating_state,
    COALESCE(
      NULLIF(c.dimensions_json->>'em_cannabis_marketing_signal', ''),
      NULLIF(c.payload_json->>'em_cannabis_marketing_signal', ''),
      NULLIF(c.dimensions_json->>'company_cannabis_marketing_signal', ''),
      NULLIF(c.payload_json->>'company_cannabis_marketing_signal', '')
    ) AS marketing_signal,
    COALESCE(
      NULLIF(c.payload_json->>'createdAt', ''),
      NULLIF(c.payload_json->>'created_at', ''),
      NULLIF(c.payload_json->>'dateAdded', ''),
      c.loaded_at::text
    )::date AS contact_date,
    CASE
      WHEN NULLIF(LOWER(TRIM(COALESCE(
        NULLIF(e.company_domain_key, ''),
        NULLIF(split_part(COALESCE(
          c.dimensions_json->>'email',
          c.payload_json->>'email',
          c.payload_json->>'emailAddress',
          ''
        ), '@', 2), ''),
        NULLIF(c.dimensions_json->>'company_name_for_emails', ''),
        NULLIF(c.payload_json->>'company_name_for_emails', '')
      ))), '') ~* '^[a-z0-9][a-z0-9.-]*\\.[a-z]{2,}$'
      AND NULLIF(LOWER(TRIM(COALESCE(
        NULLIF(e.company_domain_key, ''),
        NULLIF(split_part(COALESCE(
          c.dimensions_json->>'email',
          c.payload_json->>'email',
          c.payload_json->>'emailAddress',
          ''
        ), '@', 2), ''),
        NULLIF(c.dimensions_json->>'company_name_for_emails', ''),
        NULLIF(c.payload_json->>'company_name_for_emails', '')
      ))), '') !~* '^(gmail\\.com|yahoo\\.com|outlook\\.com|hotmail\\.com|icloud\\.com|aol\\.com|live\\.com|proton\\.me|protonmail\\.com|me\\.com|mail\\.com|twitter\\.com|x\\.com|linkedin\\.com|facebook\\.com|instagram\\.com|tiktok\\.com|youtube\\.com)$'
      THEN LOWER(TRIM(COALESCE(
        NULLIF(e.company_domain_key, ''),
        NULLIF(split_part(COALESCE(
          c.dimensions_json->>'email',
          c.payload_json->>'email',
          c.payload_json->>'emailAddress',
          ''
        ), '@', 2), ''),
        NULLIF(c.dimensions_json->>'company_name_for_emails', ''),
        NULLIF(c.payload_json->>'company_name_for_emails', '')
      )))
      ELSE NULL
    END AS company_key_from_domain,
    NULLIF(LOWER(TRIM(COALESCE(
      NULLIF(c.dimensions_json->>'lead_temperature', ''),
      NULLIF(c.payload_json->>'lead_temperature', ''),
      NULLIF(c.dimensions_json->>'warm_source', ''),
      NULLIF(c.payload_json->>'warm_source', ''),
      NULLIF(c.dimensions_json->>'lt_last_routing_channel', ''),
      NULLIF(c.payload_json->>'lt_last_routing_channel', ''),
      ''
    ))), '') IS NOT NULL AS is_mql
  FROM report_raw_ghl_contacts c
  LEFT JOIN "Emerald_Contacts" e
    ON e.ghl_contact_id = regexp_replace(c.source_key, '^contact:', '')
),
contacts AS (
  SELECT
    ghl_contact_id,
    email,
    company_name,
    operating_state,
    marketing_signal,
    contact_date,
    CASE
      WHEN company_key_from_domain IS NOT NULL
       AND split_part(company_key_from_domain, '.', 1) NOT IN (
        'gmail', 'yahoo', 'outlook', 'hotmail', 'icloud', 'aol', 'live',
        'proton', 'protonmail', 'mail', 'googlemail', 'me', 'mac', 'msn',
        'att', 'verizon', 'comcast', 'yandex', 'gmx', 'zoho', 'mailchimp',
        'twitter', 'x', 'linkedin', 'facebook', 'instagram', 'tiktok', 'youtube'
       )
      THEN company_key_from_domain
      ELSE NULL
    END AS company_key,
    is_mql
  FROM contact_base
),
opportunities AS (
  SELECT
    COALESCE(
      NULLIF(o.dimensions_json->>'contact_id', ''),
      NULLIF(o.dimensions_json->>'contact.id', ''),
      NULLIF(o.payload_json->>'contactId', ''),
      NULLIF(o.payload_json->>'contact_id', ''),
      NULLIF(o.payload_json->'contact'->>'id', '')
    ) AS ghl_contact_id,
    COALESCE(
      NULLIF(o.payload_json->>'pipelineId', ''),
      NULLIF(o.dimensions_json->>'pipeline_id', ''),
      ''
    ) AS pipeline_id,
    COALESCE(
      NULLIF(o.payload_json->>'pipelineStageId', ''),
      NULLIF(o.dimensions_json->>'pipeline_stage_id', ''),
      ''
    ) AS stage_id,
    COALESCE(
      NULLIF(o.dimensions_json->>'pipeline_name', ''),
      NULLIF(o.payload_json->>'pipelineName', ''),
      NULLIF(o.payload_json->'pipeline'->>'name', ''),
      'Warm'
    ) AS pipeline_name,
    COALESCE(
      NULLIF(o.dimensions_json->>'pipeline_stage_name', ''),
      NULLIF(o.payload_json->>'pipelineStageName', ''),
      NULLIF(o.payload_json->'pipelineStage'->>'name', ''),
      NULLIF(o.payload_json->>'stage', ''),
      'MQL'
    ) AS stage_name
  FROM report_raw_ghl_opportunities o
),
company_rollup AS (
  SELECT
    ck.company_key,
    COALESCE(NULLIF(MAX(ck.company_name), ''), 'Unknown') AS company_name,
    COUNT(DISTINCT ck.ghl_contact_id) AS contact_count,
    COUNT(DISTINCT ck.ghl_contact_id) FILTER (WHERE o.ghl_contact_id IS NOT NULL) AS pipeline_contact_count,
    STRING_AGG(DISTINCT ck.email, ', ' ORDER BY ck.email) AS contact_emails,
    jsonb_agg(DISTINCT jsonb_build_object('contact_id', ck.ghl_contact_id, 'email', ck.email)) AS contacts,
    COALESCE(STRING_AGG(DISTINCT COALESCE(NULLIF(o.pipeline_name, ''), NULLIF(o.stage_name, ''), 'Warm'), '|' ORDER BY COALESCE(NULLIF(o.pipeline_name, ''), NULLIF(o.stage_name, ''), 'Warm')), '') AS pipelines,
    COALESCE(STRING_AGG(DISTINCT o.stage_name, '|' ORDER BY o.stage_name) FILTER (WHERE o.ghl_contact_id IS NOT NULL), '') AS stage_names,
    MAX(ck.operating_state) AS operating_state,
    MAX(ck.marketing_signal) AS marketing_signal,
    MAX(ck.contact_date) AS latest_contact_date,
    COALESCE(BOOL_OR(ck.is_mql), FALSE) AS has_mql
  FROM contacts ck
  LEFT JOIN opportunities o
    ON o.ghl_contact_id = ck.ghl_contact_id
  WHERE ck.company_key IS NOT NULL
  GROUP BY ck.company_key
)
SELECT
  company_key,
  company_name,
  contact_count,
  pipeline_contact_count,
  contact_emails,
  contacts,
  pipelines,
  stage_names,
  operating_state,
  marketing_signal,
  latest_contact_date
FROM company_rollup
WHERE contact_count >= 1
  AND company_key IS NOT NULL
ORDER BY pipeline_contact_count DESC, contact_count DESC, latest_contact_date DESC
LIMIT 5000;
      `,
      options: {
        queryReplacement: '',
        replaceEmptyStrings: false
      }
    },
    position: [780, 900],
    credentials: {
      postgres: newCredential('Postgres account')
    }
  }
});

const prepareAllCompaniesData = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Prepare All Companies Sheet Data',
    parameters: {
      jsCode: `
const items = $input.all();
const result = [];

for (const item of items) {
  const json = item.json || {};

  result.push({
    json: {
      company_key: json.company_key || '',
      company_name: json.company_name || json.company_key || 'Unknown',
      contact_count: json.contact_count || 0,
      pipeline_contact_count: json.pipeline_contact_count || 0,
      contact_emails: json.contact_emails || '',
      pipelines: json.pipelines || '',
      stages: json.stages || '',
      operating_state: json.operating_state || '',
      marketing_signal: json.marketing_signal || '',
      latest_contact_date: json.latest_contact_date || ''
    }
  });
}

return result;
      `
    },
    position: [1080, 900]
  }
});

const buildAllCompaniesSheetPayload = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Build All Companies Sheet Payload',
    parameters: {
      jsCode: `
const headers = [
  'company_key',
  'company_name',
  'contact_count',
  'pipeline_contact_count',
  'contact_emails',
  'pipelines',
  'stages',
  'operating_state',
  'marketing_signal',
  'latest_contact_date',
];

const targetRowCount = 4999;
const sourceRows = $input.all().map((item) => item.json || {}).slice(0, targetRowCount);
const dataRows = sourceRows.map((row) => headers.map((key) => {
  const value = row[key];
  return value === null || value === undefined ? '' : String(value);
}));

while (dataRows.length < targetRowCount) {
  dataRows.push(Array(headers.length).fill(''));
}

return [{
  json: {
    values: [headers, ...dataRows],
    generated_at: new Date().toISOString(),
    total_companies: sourceRows.length,
    spreadsheet_url: 'https://docs.google.com/spreadsheets/d/1h71qBh90rh4hK94qYEBD4MZILDEZKPiocKcajo1-BcY',
  },
}];
      `
    },
    position: [1320, 900]
  }
});

const writeAllCompaniesSnapshot = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.4,
  config: {
    name: 'Write All Companies Snapshot',
    parameters: {
      method: 'PUT',
      url: `https://sheets.googleapis.com/v4/spreadsheets/${spreadsheetId}/values/All%20Companies!A1:J5000?valueInputOption=USER_ENTERED&includeValuesInResponse=false`,
      authentication: 'predefinedCredentialType',
      nodeCredentialType: 'googleSheetsOAuth2Api',
      sendHeaders: true,
      specifyHeaders: 'keypair',
      headerParameters: {
        parameters: [
          { name: 'Content-Type', value: 'application/json' },
          { name: 'Accept', value: 'application/json' }
        ]
      },
      sendBody: true,
      contentType: 'json',
      specifyBody: 'json',
      jsonBody: '={{ { majorDimension: "ROWS", values: $json.values } }}',
      options: {
        timeout: 30000
      }
    },
    position: [1560, 900],
    credentials: {
      googleSheetsOAuth2Api: newCredential('Google Sheets account')
    }
  }
});

const updateAllCompaniesTimestamp = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Add All Companies Metadata',
    parameters: {
      values: {
        string: [
          {
            name: 'spreadsheet_url',
            value: `https://docs.google.com/spreadsheets/d/${spreadsheetId}`
          },
          {
            name: 'generated_at',
            value: '={{ new Date().toISOString() }}'
          },
          {
            name: 'total_companies',
            value: '={{ $json.total_companies || 0 }}'
          }
        ]
      }
    },
    position: [1800, 900]
  }
});

// Build workflow with multiple triggers
export default workflow('LT - Company MQL Google Sheets Sync', 'Syncs company-level MQL data to Google Sheets')
  .add(manualTrigger)
  .to(queryCompanyData)
  .to(prepareData)
  .to(buildSheetPayload)
  .to(writeSheetSnapshot)
  .to(updateTimestamp)
  .add(scheduleTrigger)
  .to(queryCompanyData)
  .add(manualBroadTrigger)
  .to(queryAllCompaniesData)
  .to(prepareAllCompaniesData)
  .to(buildAllCompaniesSheetPayload)
  .to(writeAllCompaniesSnapshot)
  .to(updateAllCompaniesTimestamp)
  .add(scheduleBroadTrigger)
  .to(queryAllCompaniesData);
