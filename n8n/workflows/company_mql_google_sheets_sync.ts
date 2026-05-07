import { workflow, node, trigger, fromAi, expr } from '@n8n/workflow-sdk';

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

// Query Postgres for company clustering data
const queryCompanyData = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Query Company MQL Data',
    parameters: {
      operation: 'executeQuery',
      query: `
SELECT 
  COALESCE(e.company_domain_key, c.dimensions_json->>'company_name') AS company_key,
  COALESCE(e.company_name, c.dimensions_json->>'company_name', 'Unknown') AS company_name,
  COUNT(DISTINCT c.contact_id) AS contact_count,
  json_agg(DISTINCT jsonb_build_object('contact_id', c.contact_id, 'email', c.email)) AS contacts,
  STRING_AGG(DISTINCT o.pipeline_name, '|') AS pipelines,
  STRING_AGG(DISTINCT o.stage_name, '|') AS stage_names,
  MAX(e.company_operating_state) AS operating_state,
  MAX(e.company_cannabis_marketing_signal) AS marketing_signal,
  MAX(c.created_at::date) AS latest_contact_date
FROM report_raw_ghl_contacts c
JOIN report_raw_ghl_opportunities o 
  ON o.contact_id = c.contact_id
LEFT JOIN "Emerald_Contacts" e 
  ON e.ghl_contact_id = c.contact_id
WHERE o.pipeline_name IN ('Warm', 'Sales Outreach')
  AND o.stage_name NOT IN ('Disqualified', 'Closed Lost', 'Closed Won')
GROUP BY company_key, company_name, e.company_operating_state, e.company_cannabis_marketing_signal
HAVING COUNT(DISTINCT c.contact_id) >= 1
ORDER BY contact_count DESC, latest_contact_date DESC
LIMIT 500;
      `,
      options: {
        queryReplacement: '',
        replaceEmptyStrings: false
      }
    },
    position: [540, 300]
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
      company_name: json.company_name || 'Unknown',
      contact_count: json.contact_count || 0,
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

// Create Google Spreadsheet
const createSpreadsheet = node({
  type: 'n8n-nodes-base.googleSheets',
  version: 4.7,
  config: {
    name: 'Create Spreadsheet',
    parameters: {
      resource: 'spreadsheet',
      operation: 'create',
      title: 'LiveTransparent - Company MQL Report',
      sheetsUi: {
        sheetValues: [{
          title: 'Company MQLs',
          hidden: false
        }]
      },
      options: {
        locale: 'en_US',
        autoRecalc: 'ON_CHANGE'
      }
    },
    position: [1140, 200]
  }
});

// Clear existing data from sheet (keep headers)
const clearSheet = node({
  type: 'n8n-nodes-base.googleSheets',
  version: 4.7,
  config: {
    name: 'Clear Sheet',
    parameters: {
      resource: 'sheet',
      operation: 'clear',
      documentId: {
        __rl: true,
        mode: 'list',
        value: '={{ $json.spreadsheetId }}'
      },
      sheetName: {
        __rl: true,
        mode: 'list',
        value: 'Company MQLs'
      },
      clear: 'wholeSheet',
      keepFirstRow: true
    },
    position: [1140, 400]
  }
});

// Append data to Google Sheet
const appendToSheet = node({
  type: 'n8n-nodes-base.googleSheets',
  version: 4.7,
  config: {
    name: 'Append to Sheet',
    parameters: {
      resource: 'sheet',
      operation: 'append',
      documentId: {
        __rl: true,
        mode: 'list',
        value: '={{ $json.spreadsheetId }}'
      },
      sheetName: {
        __rl: true,
        mode: 'list',
        value: 'Company MQLs'
      },
      columns: {
        mappingMode: 'defineBelow',
        value: {
          company_key: '={{ $json.company_key }}',
          company_name: '={{ $json.company_name }}',
          contact_count: '={{ $json.contact_count }}',
          contact_emails: '={{ $json.contact_emails }}',
          contact_ids: '={{ $json.contact_ids }}',
          pipelines: '={{ $json.pipelines }}',
          stages: '={{ $json.stages }}',
          operating_state: '={{ $json.operating_state }}',
          marketing_signal: '={{ $json.marketing_signal }}',
          latest_contact_date: '={{ $json.latest_contact_date }}'
        }
      },
      options: {
        cellFormat: 'USER_ENTERED',
        useAppend: true
      }
    },
    position: [1440, 300]
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
            value: '={{ "https://docs.google.com/spreadsheets/d/" + $json.spreadsheetId }}'
          },
          {
            name: 'generated_at',
            value: '={{ new Date().toISOString() }}'
          },
          {
            name: 'total_companies',
            value: '={{ $items().length }}'
          }
        ]
      }
    },
    position: [1740, 300]
  }
});

// Build workflow with multiple triggers
export default workflow('LT - Company MQL Google Sheets Sync', 'Syncs company-level MQL data to Google Sheets')
  .add(manualTrigger)
  .to(queryCompanyData)
  .to(prepareData)
  .to(createSpreadsheet)
  .to(clearSheet)
  .to(appendToSheet)
  .to(updateTimestamp)
  .add(scheduleTrigger)
  .to(queryCompanyData);
