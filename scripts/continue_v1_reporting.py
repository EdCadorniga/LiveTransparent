"""V1 reporting continuation diagnostics; no outbound or CRM writes."""
from repair_v1_facts_sql import api, sql_read
import json
import urllib.request
import sys

if __name__ == '__main__':
    if '--status' in sys.argv:
        for workflow_id in ('oxYDg6XnRBKhl1Xd','Bukc0mgOD2r7V6ED'):
            result = api('/api/v1/executions?workflowId='+workflow_id+'&limit=5')
            print(json.dumps({'workflow':workflow_id,'executions':[{k:e.get(k) for k in ('id','status','startedAt','stoppedAt')} for e in result['data']]}))
        raise SystemExit(0)
    if '--capture-audit' in sys.argv:
        workflow = api('/api/v1/workflows/1diZyFmTqWQUEny3')
        code = '\n'.join(n['parameters'].get('jsCode','') for n in workflow['nodes'])
        print(json.dumps({'active':workflow['active'],'version':workflow['versionId'],
          'activeVersion':workflow.get('activeVersionId'),
          'legacyLinksPresent':{link:link in code for link in ('quqSUM8bckKaOIktVvgU','nqLFBlEsdm7qccr8Yyog')},
          'lastTouchNodes':[{'name':n['name'],'method':n['parameters'].get('method'),
            'customFieldsBody':'customFields' in json.dumps(n['parameters'].get('jsonBody',''))}
            for n in workflow['nodes'] if n['type']=='n8n-nodes-base.httpRequest']}))
        raise SystemExit(0)
    if '--channel-audit' in sys.argv:
        print(sql_read("""SELECT json_agg(x) FROM (SELECT column_name,data_type FROM information_schema.columns WHERE table_name='report_sms_sent' ORDER BY ordinal_position) x;
        SELECT json_agg(x) FROM (SELECT workflow_id,template_id,COUNT(*) AS rows,
          COUNT(*) FILTER(WHERE provider_response IS NOT NULL) AS provider_response_rows
          FROM report_sms_sent WHERE (sent_at AT TIME ZONE 'America/Los_Angeles')::date BETWEEN '2026-10-04' AND '2026-10-10' GROUP BY 1,2) x;"""))
        print(sql_read("""SELECT json_agg(x) FROM (SELECT template_id,provider_response->>'status' AS status,
          provider_response->>'id' AS provider_id,COUNT(*) AS rows
          FROM report_sms_sent WHERE (sent_at AT TIME ZONE 'America/Los_Angeles')::date BETWEEN '2026-10-04' AND '2026-10-10'
          GROUP BY 1,2,3) x;"""))
        raise SystemExit(0)
    mat = api('/api/v1/workflows/knc2wxe4pyYIJ5tw')
    if '--refresh' in sys.argv:
        request = urllib.request.Request('https://automations.livetransparent.com/webhook/lt-executive-report-v1-materializer', data=b'{}', headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(request, timeout=300) as response:
            print('Materializer ack',response.status,response.read().decode())
    summary = api('/api/v1/workflows/Bukc0mgOD2r7V6ED')
    summary_code = ''
    for n in summary['nodes']:
        code = n['parameters'].get('jsCode','')
        if 'period_contacts AS' in code:
            summary_code = code
    facts = api('/api/v1/workflows/oxYDg6XnRBKhl1Xd')
    code = next(n for n in facts['nodes'] if n['name']=='Build V1 Facts Query')['parameters']['jsCode']
    for marker in ('cameron_meeting_summary AS','response_events AS'):
        at = code.find(marker)
        print(code[at:at+1500])
    creation = code.split('WITH ',1)[1].split('), authoritative_ghl_counts AS',1)[0] + ')'
    cohorts = summary_code.split('backfill_contacts AS (',1)[1].split('),period_opportunities AS',1)[0] + ')'
    sql = 'WITH ' + creation + ',backfill_contacts AS (' + cohorts + """,
    stable AS (SELECT regexp_replace(source_key,'^contact:','') AS contact_id FROM contact_creation_facts
      WHERE COALESCE(created_date,first_observed_date) BETWEEN $1::date AND $2::date AND NOT COALESCE(is_linkedin_backfill,FALSE)),
    difference AS (SELECT COALESCE(a.contact_id,b.contact_id) AS contact_id,
      CASE WHEN a.contact_id IS NULL THEN 'summary_only' ELSE 'stable_only' END AS side
      FROM stable a FULL JOIN period_contacts b USING(contact_id) WHERE a.contact_id IS NULL OR b.contact_id IS NULL)
    SELECT json_build_object('stable_count',(SELECT COUNT(*) FROM stable),
      'summary_count',(SELECT COUNT(*) FROM period_contacts),
      'differences',(SELECT json_agg(d) FROM difference d),
      'materialized_count',(SELECT COUNT(*) FROM lt_exec_v1_contact_provenance WHERE (first_seen_at AT TIME ZONE 'America/Los_Angeles')::date BETWEEN $1::date AND $2::date AND NOT is_backfill));"""
    print(sql_read(sql.replace('$1',"'2026-10-04'").replace('$2',"'2026-10-10'")))
    print(sql_read("""SELECT json_agg(x) FROM (
      SELECT DISTINCT source_key, dimensions_json->>'contact_id' AS contact_id,
        dimensions_json->>'source_created_at' AS source_created_at,
        payload_json->>'createdAt' AS created_at,payload_json->>'dateAdded' AS date_added,
        payload_json->>'name' AS name
      FROM report_raw_ghl_contacts WHERE source_key IN ('hWikhd4bEQNJLcQWmXkh','contact:hWikhd4bEQNJLcQWmXkh')
    ) x;"""))
    executions = api('/api/v1/executions?workflowId=knc2wxe4pyYIJ5tw&limit=2')
    print(json.dumps([{k:e.get(k) for k in ('id','status','startedAt','stoppedAt')} for e in executions['data']]))
    print(sql_read("""SELECT json_agg(x) FROM (SELECT table_name,column_name,data_type
      FROM information_schema.columns WHERE table_name ILIKE '%sms%send%' OR table_name='SimpleTexting_Campaign_Event_Log' ORDER BY table_name,ordinal_position) x;
      SELECT json_agg(x) FROM (SELECT field->>'value' AS vertical,COUNT(*) FROM (SELECT DISTINCT ON(source_key) payload_json FROM report_raw_ghl_contacts ORDER BY source_key,report_date DESC,loaded_at DESC) c CROSS JOIN LATERAL jsonb_array_elements(COALESCE(payload_json->'customFields','[]'::jsonb)) field WHERE field->>'id'='ODs8fBt5te5HEfSJ91pY' GROUP BY 1) x;"""))
    print(sql_read("""SELECT json_agg(x) FROM (SELECT campaign_key,event_type,COUNT(*) FROM "SimpleTexting_Campaign_Event_Log" WHERE (created_at AT TIME ZONE 'America/Los_Angeles')::date BETWEEN '2026-10-04' AND '2026-10-10' GROUP BY 1,2) x;
    SELECT json_agg(x) FROM (SELECT campaign_key,event_type,COUNT(*),COUNT(DISTINCT NULLIF(message_id,'')) AS messages FROM "Email_Events" WHERE (event_ts AT TIME ZONE 'America/Los_Angeles')::date BETWEEN '2026-10-04' AND '2026-10-10' GROUP BY 1,2) x;"""))
    print(sql_read("SELECT json_agg(table_name) FROM information_schema.tables WHERE table_schema='public' AND (table_name ILIKE '%sms%' OR table_name ILIKE '%simpletext%' OR table_name ILIKE '%email%');"))
