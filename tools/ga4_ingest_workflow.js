import { workflow, node, trigger, newCredential, expr } from '@n8n/workflow-sdk';

const codeNormalize = `const rows = $input.all();
const cfg = $node['Config'].json || {};
const reportDate = new Date().toISOString().slice(0, 10);
const batchId = 'ga4-' + reportDate + '-' + Date.now();

const items = [];
for (const row of rows) {
  const data = row.json || {};
  const dims = data.dimensionHeaders ? data.dimensionHeaders.map(h => h.name) : [];
  const mets = data.metricHeaders ? data.metricHeaders.map(h => h.name) : [];
  
  for (const r of (data.rows || [])) {
    const dimMap = {};
    (r.dimensionValues || []).forEach((v, i) => { if (dims[i]) dimMap[dims[i]] = v.value; });
    const metMap = {};
    (r.metricValues || []).forEach((v, i) => { if (mets[i]) metMap[mets[i]] = v.value; });
    
    const sessionDate = dimMap.date ? dimMap.date.replace(/(\\d{4})(\\d{2})(\\d{2})/, '$1-$2-$3') : reportDate;
    const source = dimMap.sourceMedium || 'unknown';
    const channel = dimMap.sessionDefaultChannelGrouping || 'unattributed';
    const landingPage = dimMap.pageLocation || 'unknown';
    const sessions = Number(metMap.sessions || 0);
    const users = Number(metMap.totalUsers || 0);
    const engagementDuration = Number(metMap.userEngagementDuration || 0);
    const events = Number(metMap.eventCount || 0);
    
    items.push({
      json: {
        report_date: sessionDate,
        source_system: 'ga4',
        source_key: 'ga4:' + batchId + ':' + (items.length + 1),
        source_window_start: sessionDate,
        source_window_end: sessionDate,
        payload_json: { sessionDate, source, channel, landingPage, sessions, users, engagementDuration, events },
        dimensions_json: { ga_session_id: batchId, channel, source, landing_page: landingPage },
        metrics_json: { sessions, users, engagement_duration: engagementDuration, events },
        batch_id: batchId,
        run_id: null,
        loaded_at: new Date().toISOString(),
      }
    });
  }
}

if (!items.length) {
  items.push({ json: { kind: 'noop', workflowName: 'LT - GA4 Daily Ingest', reportDate, batchId, sql: 'SELECT 1 AS noop;' } });
}

return items;`;

const codeSummarize = `const rows = $input.all().filter(i => i.json && i.json.kind !== 'noop').map(i => i.json || {});
const cfg = $node['Config'].json || {};
const reportDate = new Date().toISOString().slice(0, 10);
const batchId = rows[0]?.batch_id || 'ga4-' + reportDate + '-' + Date.now();
const rowCount = rows.length;
const sessions = rows.reduce((s, r) => s + Number(r.metrics_json?.sessions || 0), 0);
const users = rows.reduce((s, r) => s + Number(r.metrics_json?.users || 0), 0);
return [{ json: {
  workflow_name: 'LT - GA4 Daily Ingest',
  source_system: 'ga4',
  report_date: reportDate,
  batch_id: batchId,
  status: rowCount ? 'success' : 'empty',
  started_at: new Date().toISOString(),
  finished_at: new Date().toISOString(),
  row_count: rowCount,
  error_count: 0,
  retry_count: 0,
  cursor_value: String(sessions),
  error_message: null,
  metadata: { workflow: 'LT - GA4 Daily Ingest', sessions, users, source: 'ga4', propertyId: cfg.ga4PropertyId }
} }];`;

const codeBuildSQL = `const s = $node['Summarize Run'].json || {};
const q = v => "'" + String(v ?? '').replace(/'/g, "''") + "'";
const jsonQ = v => q(JSON.stringify(v));
const runSql = \`INSERT INTO report_sync_runs (workflow_name, source_system, report_date, batch_id, status, started_at, finished_at, row_count, error_count, retry_count, cursor_value, error_message, metadata) VALUES (\${q(s.workflow_name)}, \${q(s.source_system)}, \${q(s.report_date)}::date, \${q(s.batch_id)}, \${q(s.status)}, \${q(s.started_at)}::timestamptz, \${q(s.finished_at)}::timestamptz, \${Number(s.row_count || 0)}, \${Number(s.error_count || 0)}, 0, \${q(s.cursor_value)}, \${q(s.error_message)}, \${jsonQ(s.metadata || {})}::jsonb);\`;
const watermarkSql = \`INSERT INTO report_sync_watermarks (workflow_name, source_system, watermark_key, watermark_value, updated_at) VALUES (\${q(s.workflow_name)}, \${q(s.source_system)}, 'last_complete_report_date', \${q(s.report_date)}, NOW()) ON CONFLICT (workflow_name, source_system, watermark_key) DO UPDATE SET watermark_value = EXCLUDED.watermark_value, updated_at = NOW();\`;
const healthSql = \`INSERT INTO report_source_health (source_system, status, last_success_at, last_attempt_at, last_row_count, stale_after_hours, last_error, metadata, updated_at) VALUES (\${q(s.source_system)}, \${q(s.status === 'success' ? 'ready' : 'error')}, \${s.status === 'success' ? 'NOW()' : 'NULL'}, NOW(), \${Number(s.row_count || 0)}, 48, \${q(s.error_message)}::text, \${jsonQ({ workflowName: s.workflow_name, batchId: s.batch_id, reportDate: s.report_date, sessions: s.metadata?.sessions })}::jsonb, NOW()) ON CONFLICT (source_system) DO UPDATE SET status = EXCLUDED.status, last_success_at = CASE WHEN EXCLUDED.status = 'ready' THEN EXCLUDED.last_success_at ELSE report_source_health.last_success_at END, last_attempt_at = EXCLUDED.last_attempt_at, last_row_count = EXCLUDED.last_row_count, stale_after_hours = 48, last_error = EXCLUDED.last_error, metadata = EXCLUDED.metadata, updated_at = NOW();\`;
return [{ json: { sql: runSql } }, { json: { sql: watermarkSql } }, { json: { sql: healthSql } }];`;

const codeResult = `const s = $node['Summarize Run'].json || {};
return [{ json: { ok: !s.error_count, workflow: s.workflow_name, status: s.status, source: s.source_system, reportDate: s.report_date, rowCount: s.row_count, sessions: s.metadata?.sessions, users: s.metadata?.users, note: s.row_count ? 'GA4 ingest succeeded.' : 'GA4 returned no rows; workflow is healthy but no data in range.' } }];`;

const scheduleTrigger = trigger({
  type: 'n8n-nodes-base.scheduleTrigger',
  version: 1.2,
  config: {
    name: 'Schedule Trigger',
    parameters: { rule: { interval: [{ field: 'minutes', minutesInterval: 1440 }] } },
    position: [240, 160]
  },
  output: [{}]
});

const manualTrigger = trigger({
  type: 'n8n-nodes-base.manualTrigger',
  version: 1,
  config: {
    name: 'Manual Trigger',
    position: [240, 320]
  },
  output: [{}]
});

const configNode = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Config',
    parameters: {
      mode: 'manual',
      includeOtherFields: true,
      assignments: {
        assignments: [
          { id: 'locationId', name: 'locationId', type: 'string', value: 'Zwz4relUXVPxx8uohnjV' },
          { id: 'workflowName', name: 'workflowName', type: 'string', value: 'LT - GA4 Daily Ingest' },
          { id: 'sourceSystem', name: 'sourceSystem', type: 'string', value: 'ga4' },
          { id: 'preparedState', name: 'preparedState', type: 'string', value: 'ga4_enabled' },
          { id: 'ga4PropertyId', name: 'ga4PropertyId', type: 'string', value: '434472183' },
          { id: 'ga4IngestEnabled', name: 'ga4IngestEnabled', type: 'string', value: 'true' },
          { id: 'runTable', name: 'runTable', type: 'string', value: 'report_sync_runs' },
          { id: 'watermarkTable', name: 'watermarkTable', type: 'string', value: 'report_sync_watermarks' },
          { id: 'healthTable', name: 'healthTable', type: 'string', value: 'report_source_health' }
        ]
      }
    },
    position: [480, 240]
  },
  output: [{ locationId: 'Zwz4relUXVPxx8uohnjV', workflowName: 'LT - GA4 Daily Ingest', ga4PropertyId: '434472183' }]
});

const fetchGA4 = node({
  type: 'n8n-nodes-base.googleAnalytics',
  version: 2,
  config: {
    name: 'Fetch GA4 Data',
    parameters: {
      resource: 'report',
      operation: 'get',
      propertyType: 'ga4',
      propertyId: { __rl: true, mode: 'id', value: '434472183' },
      dateRange: 'last30days',
      metricsGA4: {
        metricValues: [
          { listName: 'sessions' },
          { listName: 'totalUsers' },
          { listName: 'userEngagementDuration' },
          { listName: 'eventCount' }
        ]
      },
      dimensionsGA4: {
        dimensionValues: [
          { listName: 'date' },
          { listName: 'sessionDefaultChannelGrouping' },
          { listName: 'pageLocation' },
          { listName: 'sourceMedium' }
        ]
      },
      returnAll: true,
      simple: false
    },
    credentials: { googleAnalyticsOAuth2: newCredential('Google Analytics account - cskarkut') },
    position: [720, 240]
  },
  output: [{ sessions: '100', totalUsers: '50', date: '20260430' }]
});

const normalizeGA4 = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Normalize GA4 Rows',
    parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: codeNormalize },
    position: [960, 240]
  },
  output: [{ report_date: '2026-04-30', source_system: 'ga4', batch_id: 'ga4-test' }]
});

const upsertGA4 = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Upsert GA4 Raw',
    parameters: {
      operation: 'executeQuery',
      query: `INSERT INTO report_raw_ga4_sessions (report_date, source_system, source_key, source_window_start, source_window_end, payload_json, dimensions_json, metrics_json, batch_id, run_id, loaded_at)
VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7::jsonb, $8::jsonb, $9, $10, $11::timestamptz)
ON CONFLICT (source_system, report_date, source_key) DO UPDATE SET
  source_window_start = EXCLUDED.source_window_start,
  source_window_end = EXCLUDED.source_window_end,
  payload_json = EXCLUDED.payload_json,
  dimensions_json = EXCLUDED.dimensions_json,
  metrics_json = EXCLUDED.metrics_json,
  batch_id = EXCLUDED.batch_id,
  run_id = EXCLUDED.run_id,
  loaded_at = EXCLUDED.loaded_at;`,
      options: {
        queryBatching: 'independently',
        queryReplacement: expr('={{ [ $json.report_date, $json.source_system, $json.source_key, $json.source_window_start, $json.source_window_end, JSON.stringify($json.payload_json || {}), JSON.stringify($json.dimensions_json || {}), JSON.stringify($json.metrics_json || {}), $json.batch_id, null, $json.loaded_at ] }}')
      }
    },
    credentials: { postgres: newCredential('Postgres') },
    position: [1200, 240]
  },
  output: [{ success: true }]
});

const summarizeRun = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Summarize Run',
    parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: codeSummarize },
    position: [1440, 240]
  },
  output: [{ workflow_name: 'LT - GA4 Daily Ingest', status: 'success', row_count: 10 }]
});

const buildFinalizeSQL = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Build Finalization SQL',
    parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: codeBuildSQL },
    position: [1680, 240]
  },
  output: [{ sql: 'SELECT 1' }, { sql: 'SELECT 1' }, { sql: 'SELECT 1' }]
});

const finalizeRun = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Finalize Run Records',
    parameters: {
      operation: 'executeQuery',
      query: expr('{{$json.sql}}'),
      options: { queryBatching: 'independently' }
    },
    credentials: { postgres: newCredential('Postgres') },
    position: [1920, 240]
  },
  output: [{ success: true }]
});

const resultNode = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Result',
    parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: codeResult },
    position: [2160, 240]
  },
  output: [{ ok: true, workflow: 'LT - GA4 Daily Ingest' }]
});

export default workflow('6pCSGzFmrMDFL5Yq', 'LT - GA4 Daily Ingest')
  .add(scheduleTrigger)
  .to(configNode)
  .add(manualTrigger)
  .to(configNode)
  .add(configNode)
  .to(fetchGA4)
  .add(fetchGA4)
  .to(normalizeGA4)
  .add(normalizeGA4)
  .to(upsertGA4)
  .add(upsertGA4)
  .to(summarizeRun)
  .add(summarizeRun)
  .to(buildFinalizeSQL)
  .add(buildFinalizeSQL)
  .to(finalizeRun)
  .add(finalizeRun)
  .to(resultNode);
