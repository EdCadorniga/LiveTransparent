import json
from repair_v1_facts_sql import api
w=api('/api/v1/workflows/1diZyFmTqWQUEny3')
vals=next(n for n in w['nodes'] if n['name']=='Config')['parameters']['assignments']['assignments']
registry=json.loads(next(a['value'] for a in vals if a['name']=='linkRegistryJson'))
for value in registry.values():print(json.dumps(value))
