"""Output non-sensitive runtime node topology and reporting query fragments."""
from repair_v1_facts_sql import api
w=api('/api/v1/workflows/oxYDg6XnRBKhl1Xd')
for n in w['nodes']:
    print(n['name'], n['type'], list(n['parameters']))
    if n['type']=='n8n-nodes-base.postgres':print(n['credentials'],n['parameters'])
    code=n['parameters'].get('jsCode','')
    if n['name']=='Build V1 Facts Query':print(code[:1200])
    if n['name']=='Shape V1 Facts Response':print(code[:3000])
