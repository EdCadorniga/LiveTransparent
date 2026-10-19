"""Verify recovery-triggered MQL handler outcomes without exposing contacts/config."""
import json
from repair_v1_facts_sql import api
rows=api('/api/v1/executions?workflowId=MI91SutAbAj3QSXp&limit=10')['data']
for e in rows:
    d=api('/api/v1/executions/'+e['id']+'?includeData=true')
    outputs=d.get('data',{}).get('resultData',{}).get('runData',{}).get('Ensure Warm Qualified Opportunity',[])
    if not outputs:continue
    values=outputs[0].get('data',{}).get('main',[[{}]])[0][0].get('json',{})
    print(json.dumps({'id':e['id'],'execution_status':e.get('status'),'action':values.get('status'),'reason':values.get('reason')}))
