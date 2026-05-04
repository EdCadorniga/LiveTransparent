const schedTrigger = trigger({ type: 'n8n-nodes-base.scheduleTrigger', version: 1.2, config: { name: 'Schedule Trigger', parameters: { rule: { interval: [{ field: 'minutes', minutesInterval: 1440 }] } }, position: [240, 160] }, output: [{}] });

const manTrigger = trigger({ type: 'n8n-nodes-base.manualTrigger', version: 1, config: { name: 'Manual Trigger', position: [240, 320] }, output: [{}] });

const cfgNode = node({ type: 'n8n-nodes-base.set', version: 3.4, config: { name: 'Config', parameters: { mode: 'manual', assignments: { assignments: [{ id: '1', name: 'workflowName', type: 'string', value: 'LT - Report Rollup Corrections' }, { id: '2', name: 'sourceSystem', type: 'string', value: 'corrections' }] } }, position: [480, 240] }, output: [{ workflowName: 'LT - Report Rollup Corrections' }] });

const buildCode = `const sql = \`-- LT Report Rollup Corrections
-- Fixes: 1) opportunities_created dedup (COUNT DISTINCT)
--        2) closed_won checks stage name (not just status)
--        3) meetings_booked dedup

WITH opps_fixed AS (
  SELECT
    DATE(COALESCE(
      NULLIF(dimensions_json->>'source_created_at', '')::timestamptz,
      NULLIF(payload_json->>'createdAt', '')::timestamptz,
      make_date(
        substring(report_date::text from 1 for 4)::int,
        substring(report_date::text from 6 for 2)::int,
        substring(report_date::text from 9 for 2)::int
      ),
      NOW()
    )) AS report_date,
    COUNT(DISTINCT source_key) AS opps_count,
    COUNT(DISTINCT source_key) FILTER (
      WHERE LOWER(dimensions_json->>'pipeline_stage_name') = 'closed won'
         OR LOWER(dimensions_json->>'status') IN ('won', 'closed_won', 'closed won')
    ) AS won_count,
    COALESCE(SUM(DISTINCT
      CASE WHEN (LOWER(dimensions_json->>'pipeline_stage_name') = 'closed won'
             OR LOWER(dimensions_json->>'status') IN ('won', 'closed_won', 'closed won'))
      THEN COALESCE(NULLIF(metrics_json->>'monetary_value', ''), NULLIF(payload_json->>'monetaryValue', ''), '0')::numeric
      ELSE 0 END
    ), 0) AS won_revenue,
    COUNT(DISTINCT source_key) FILTER (
      WHERE LOWER(dimensions_json->>'pipeline_stage_name') = 'closed lost'
         OR LOWER(dimensions_json->>'status') IN ('lost', 'closed_lost', 'closed lost')
    ) AS lost_count,
    COUNT(DISTINCT source_key) FILTER (
      WHERE LOWER(dimensions_json->>'pipeline_stage_name') IN ('booked', 'discovery scheduled', 'meeting scheduled', 'meeting requested')
    ) AS meetings_count
  FROM report_raw_ghl_opportunities
  WHERE DATE(COALESCE(
    NULLIF(dimensions_json->>'source_created_at', '')::timestamptz,
    NULLIF(payload_json->>'createdAt', '')::timestamptz,
    make_date(
      substring(report_date::text from 1 for 4)::int,
      substring(report_date::text from 6 for 2)::int,
      substring(report_date::text from 9 for 2)::int
    ),
    NOW()
  )) >= CURRENT_DATE - INTERVAL '95 days'
  GROUP BY 1
)
UPDATE report_daily_summary d
SET
  opportunities_created = COALESCE(of.opps_count, 0),
  closed_won_count = COALESCE(of.won_count, 0),
  closed_won_revenue = COALESCE(of.won_revenue, 0),
  closed_lost_count = COALESCE(of.lost_count, 0),
  meetings_booked = COALESCE(of.meetings_count, 0),
  updated_at = NOW()
FROM opps_fixed of
WHERE d.report_date = of.report_date;\`;

return [{ json: { sql, workflowName: 'LT - Report Rollup Corrections' } }];`;

const buildSql = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Build Corrections SQL', parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: buildCode }, position: [720, 240] }, output: [{ json: { sql: 'SELECT 1;' } }] });

const execSql = node({ type: 'n8n-nodes-base.postgres', version: 2.6, config: { name: 'Execute Corrections', parameters: { operation: 'executeQuery', query: '={{ $json.sql }}', options: { queryBatching: 'independently' } }, position: [960, 240] }, output: [{ json: { command: 'UPDATE' } }] });

const summaryCode = 'return [{ json: { status: "success", workflow_name: "LT - Report Rollup Corrections", tables_corrected: 1, fixes: ["opportunities_created dedup", "closed_won stage check", "meetings_booked dedup"] } }];';

const summarize = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Summarize', parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: summaryCode }, position: [1200, 240] }, output: [{ json: { status: 'success' } }] });

const resultCode = 'var s = $node["Summarize"].json; return [{ json: { ok: true, workflow: s.workflow_name, status: s.status, fixes: s.fixes } }];';

const resultNode = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Result', parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: resultCode }, position: [1440, 240] }, output: [{ json: { ok: true } }] });

export default workflow('rollup-corrections', 'LT - Report Rollup Corrections').add(schedTrigger).to(cfgNode).add(manTrigger).to(cfgNode).add(cfgNode).to(buildSql).add(buildSql).to(execSql).add(execSql).to(summarize).add(summarize).to(resultNode);
