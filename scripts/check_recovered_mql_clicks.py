"""Reporting-only post-recovery totals and live workflow publication readback."""
import json
from repair_v1_facts_sql import api,sql_read
print(sql_read("SELECT jsonb_build_object('recovered_click_rows',(SELECT COUNT(*) FROM lt_booking_link_clicks WHERE source_event_id LIKE 'recovered:n8n:%'),'recovered_contacts',(SELECT COUNT(DISTINCT contact_id) FROM lt_booking_link_clicks WHERE source_event_id LIKE 'recovered:n8n:%'),'mql_source_counts',(SELECT jsonb_agg(to_jsonb(x)) FROM (SELECT source,COUNT(*) AS contacts FROM mql_tag_events WHERE (added_at AT TIME ZONE 'America/Los_Angeles')::date>='2026-10-11' GROUP BY source) x));"))
for wid in ('1diZyFmTqWQUEny3','lQTW0QPwBcf3o7j8','oxYDg6XnRBKhl1Xd','kBuW8Uq3EOJFQKNF','Rrsigvi8AhH3iR55','wBy0fi5lpFUMDS94','U9oc2tZRsr4zq6IM','MI91SutAbAj3QSXp'):
    w=api('/api/v1/workflows/'+wid)
    print(json.dumps({'id':wid,'name':w['name'],'active':w['active'],'version':w['versionId'],'published':w.get('activeVersionId')}))
for wid in ('kBuW8Uq3EOJFQKNF','Rrsigvi8AhH3iR55'):
    print(json.dumps({'workflow':wid,'executions':[{k:e.get(k) for k in ('id','status','startedAt','stoppedAt')} for e in api('/api/v1/executions?workflowId='+wid+'&limit=3')['data']]}))
