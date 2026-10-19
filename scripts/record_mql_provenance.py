"""Support explicit authenticated form/click provenance in existing MQL ledger."""
import copy
from repair_v1_facts_sql import api
from fix_verified_booking_gate import save, parse

w=api('/api/v1/workflows/U9oc2tZRsr4zq6IM');rev=copy.deepcopy(w)
n=next(n for n in rev['nodes'] if n['name']=='Insert Event')
code=n['parameters']['jsCode']
if '$5' not in code:
    code=code.replace("const payload = JSON.stringify(item.raw || {});", "const payload = JSON.stringify(item.raw || {});\n  const requestedSource=String(item.raw?.form_source || item.raw?.source || '');\n  const source=['ghl_form','linkedin_form','meta_form','booking_link_click'].includes(requestedSource)?requestedSource:'ghl_automation';")
    code=code.replace("VALUES ($1, $2, $3, 'ghl_automation', $4::jsonb)","VALUES ($1, $2, $3, $5, $4::jsonb)")
    code=code.replace('ON CONFLICT (contact_id, tag) DO NOTHING',"ON CONFLICT (contact_id, tag) DO UPDATE SET source=EXCLUDED.source,payload_json=EXCLUDED.payload_json\n     WHERE mql_tag_events.source='ghl_automation' AND EXCLUDED.source<>'ghl_automation'\n       AND ABS(EXTRACT(EPOCH FROM (mql_tag_events.added_at-EXCLUDED.added_at)))<=120")
    code=code.replace('[item.contactId, item.tag, item.addedAt, payload]','[item.contactId, item.tag, item.addedAt, payload, source]')
    n['parameters']['jsCode']=code
parse(code)
if rev!=w:save(w,rev)
else:print('Provenance already supported.')
