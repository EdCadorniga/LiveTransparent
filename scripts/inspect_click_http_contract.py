"""Inspect expression/binding structure only; never print resolved credentials."""
import json
from repair_v1_facts_sql import api
w=api('/api/v1/workflows/1diZyFmTqWQUEny3')
for n in w['nodes']:
    if n['type']=='n8n-nodes-base.httpRequest':
        p=n['parameters'];print(json.dumps({'name':n['name'],'authentication':p.get('authentication'),'credential_types':list(n.get('credentials',{})),'url':p.get('url'),'jsonBody':p.get('jsonBody'),
            'headers':[{'name':h['name'],'dynamic': '{{' in str(h['value']),'expression_prefix':str(h['value']).startswith('=')} for h in p.get('headerParameters',{}).get('parameters',[])]}))
