import json
from repair_v1_facts_sql import api
for wid in ('Bukc0mgOD2r7V6ED','MvPLbUAN9IIQikxb'):
    w=api('/api/v1/workflows/'+wid)
    print(w['id'],w['name'])
    print(json.dumps({'nodes':[{k:n.get(k) for k in ('name','type','typeVersion')} for n in w['nodes']],'connections':w['connections']}))
    for n in w['nodes']:
        if n['name'] in ('Normalize Request','Normalize Campaign Window'):print(n['parameters']['jsCode'][-1500:])
        if n['type']=='n8n-nodes-base.postgres':print(n['parameters'].get('options'))
ifnode=next(n for n in api('/api/v1/workflows/1diZyFmTqWQUEny3')['nodes'] if n['type']=='n8n-nodes-base.if')
print(json.dumps(ifnode['parameters']))
