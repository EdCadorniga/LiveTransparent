$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$apiKey = (Select-String -Path .env -Pattern '^N8N_API_KEY_LT=').Line.Split('=', 2)[1]
$headers = @{
  'X-N8N-API-KEY' = $apiKey
  'Content-Type' = 'application/json'
}

$workflowId = 'xHqmCC1vOeZ11gCd'
$workflow = Invoke-RestMethod -Uri "https://automations.livetransparent.com/api/v1/workflows/$workflowId" -Headers $headers

$keep = @(
  'Schedule Trigger',
  'Manual Trigger',
  'Config',
  'Fetch GSC Data',
  'Process Rows',
  'Upsert GSC Rows',
  'Build Finalization SQL',
  'Finalize Run Records',
  'Result'
)

$workflow.nodes = @($workflow.nodes | Where-Object { $keep -contains $_.name })

foreach ($node in $workflow.nodes) {
  switch ($node.name) {
    'Config' {
      $node.type = 'n8n-nodes-base.code'
      $node.typeVersion = 2
      $node.parameters = [pscustomobject]@{
        jsCode = @'
const end = new Date();
end.setUTCDate(end.getUTCDate() - 1);
const start = new Date(end);
start.setUTCDate(start.getUTCDate() - 2);
const iso = (d) => d.toISOString().slice(0, 10);
return [{ json: {
  startDate: iso(start),
  endDate: iso(end),
  reportDate: iso(end),
  siteUrl: 'sc-domain:livetransparent.com',
  dimensions: ['query', 'page', 'country', 'device'],
  rowLimit: 1000
} }];
'@
      }
    }
    'Fetch GSC Data' {
      $node.parameters = [pscustomobject]@{
        method = 'POST'
        url = '=https://www.googleapis.com/webmasters/v3/sites/{{$json.siteUrl}}/searchAnalytics/query'
        authentication = 'predefinedCredentialType'
        nodeCredentialType = 'googleOAuth2Api'
        sendBody = $true
        specifyBody = 'json'
        jsonBody = [pscustomobject]@{
          startDate = '={{ $json.startDate }}'
          endDate = '={{ $json.endDate }}'
          dimensions = '={{ $json.dimensions }}'
          rowLimit = '={{ $json.rowLimit }}'
          aggregationType = 'byPage'
          startRow = 0
        }
        options = [pscustomobject]@{
          response = [pscustomobject]@{}
          sendCredentialsOnCrossOriginRedirect = $true
        }
      }
      $node.credentials = [pscustomobject]@{
        googleOAuth2Api = [pscustomobject]@{
          id = 'EKnNrSvlEd0A99AX'
          name = 'GSC - Cameron Livetransparent Google account'
        }
      }
    }
    'Process Rows' {
      $node.parameters = [pscustomobject]@{
        jsCode = @'
const input = $input.all();
const first = input[0]?.json || {};
const apiRows = Array.isArray(first.rows)
  ? first.rows
  : Array.isArray(first.data?.rows)
    ? first.data.rows
    : Array.isArray(first)
      ? first
      : [];
const reportDate = first.reportDate || $node['Config'].json.reportDate || new Date(Date.now() - 86400000).toISOString().slice(0, 10);

function clean(value) {
  return String(value ?? '').trim();
}

const records = apiRows.map((row) => {
  const keys = Array.isArray(row.keys) ? row.keys : [];
  const query = clean(row.query ?? keys[0]);
  const page = clean(row.page ?? row.page_url ?? keys[1]);
  const country = clean(row.country ?? keys[2]);
  const device = clean(row.device ?? keys[3]);
  const clicks = Number(row.clicks ?? 0);
  const impressions = Number(row.impressions ?? 0);
  const ctr = Number(row.ctr ?? 0);
  const position = Number(row.position ?? 0);
  const sourceKey = ['gsc', page, query, country, device, reportDate].join(':');
  return {
    source_key: sourceKey,
    source_system: 'gsc',
    report_date: reportDate,
    query,
    page_url: page,
    country,
    device,
    payload_json: JSON.stringify(row),
    dimensions_json: JSON.stringify({ query, page, country, device }),
    metrics_json: JSON.stringify({ clicks, impressions, ctr, position }),
    batch_id: `gsc-${reportDate}`
  };
});

return records.length
  ? records.map((json) => ({ json }))
  : [{ json: { skipped: true, report_date: reportDate, batch_id: `gsc-${reportDate}`, rows: 0 } }];
'@
      }
    }
    'Upsert GSC Rows' {
      $node.parameters = [pscustomobject]@{
        operation = 'executeQuery'
        query = @'
INSERT INTO report_raw_gsc_queries (
  report_date, source_system, source_key,
  payload_json, dimensions_json, metrics_json, batch_id
) VALUES (
  $1::date,
  'gsc',
  $2,
  $3::jsonb,
  $4::jsonb,
  $5::jsonb,
  $6
)
ON CONFLICT (source_system, report_date, source_key) DO UPDATE SET
  payload_json = EXCLUDED.payload_json,
  dimensions_json = EXCLUDED.dimensions_json,
  metrics_json = EXCLUDED.metrics_json,
  batch_id = EXCLUDED.batch_id,
  loaded_at = NOW();
'@
        options = [pscustomobject]@{
          queryBatching = 'independently'
          queryReplacement = '={{ [$json.report_date, $json.source_key, $json.payload_json || "{}", $json.dimensions_json || "{}", $json.metrics_json || "{}", $json.batch_id] }}'
        }
      }
    }
    'Build Finalization SQL' {
      $node.parameters = [pscustomobject]@{
        jsCode = @'
const rows = $input.all().filter((item) => !item.json?.skipped);
const total = rows.length;
const reportDate = $node['Config'].json.reportDate || new Date(Date.now() - 86400000).toISOString().slice(0, 10);
const wfName = 'LT - GSC Daily Ingest';
const batchId = 'gsc-' + reportDate;
const runSql = `INSERT INTO report_sync_runs (
  workflow_name, source_system, report_date, batch_id, status, started_at, finished_at,
  row_count, error_count, retry_count, cursor_value, error_message, metadata
) VALUES (
  '${wfName}', 'gsc', '${reportDate}'::date, '${batchId}',
  'completed', NOW() - INTERVAL '5 minutes', NOW(),
  ${total}, 0, 0, NULL, NULL, '{}'::jsonb
);`;
const healthSql = `INSERT INTO report_source_health (source_system,status,last_success_at,last_attempt_at,last_row_count,stale_after_hours,last_error,metadata,updated_at)
VALUES ('gsc','success',NOW(),NOW(),${total},48,NULL,'{}'::jsonb,NOW())
ON CONFLICT (source_system) DO UPDATE SET
  status='success',last_success_at=NOW(),last_attempt_at=NOW(),last_row_count=${total},last_error=NULL,updated_at=NOW();`;
return [{ json: { sql: runSql } }, { json: { sql: healthSql } }];
'@
      }
    }
    'Result' {
      $node.parameters = [pscustomobject]@{
        jsCode = "return [{ json: { ok: true, workflow: 'LT - GSC Daily Ingest', source: 'gsc', reportDate: `$node['Config'].json.reportDate } }];"
      }
    }
  }
}

function New-MainConnection($targetNode) {
  [pscustomobject]@{
    main = [object[]]@(,[object[]]@([pscustomobject]@{
      node = $targetNode
      type = 'main'
      index = 0
    }))
  }
}

$workflow.connections = [pscustomobject]@{
  'Schedule Trigger' = New-MainConnection 'Config'
  'Manual Trigger' = New-MainConnection 'Config'
  'Config' = New-MainConnection 'Fetch GSC Data'
  'Fetch GSC Data' = New-MainConnection 'Process Rows'
  'Process Rows' = New-MainConnection 'Upsert GSC Rows'
  'Upsert GSC Rows' = New-MainConnection 'Build Finalization SQL'
  'Build Finalization SQL' = New-MainConnection 'Finalize Run Records'
  'Finalize Run Records' = New-MainConnection 'Result'
}

$bodyObj = [ordered]@{
  name = $workflow.name
  nodes = $workflow.nodes
  connections = $workflow.connections
  settings = [pscustomobject]@{
    saveExecutionProgress = $true
    saveManualExecutions = $true
    saveDataErrorExecution = 'all'
    saveDataSuccessExecution = 'all'
    executionTimeout = 3600
    timezone = 'UTC'
    executionOrder = 'v1'
  }
}

$body = $bodyObj | ConvertTo-Json -Depth 100
Invoke-RestMethod -Method Put -Uri "https://automations.livetransparent.com/api/v1/workflows/$workflowId" -Headers $headers -Body $body |
  Select-Object id, name, updatedAt, versionId |
  ConvertTo-Json
