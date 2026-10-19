from repair_v1_facts_sql import api
from audit_sql_tag_writers import safe
w=api('/api/v1/workflows/U9oc2tZRsr4zq6IM')
for n in w['nodes']:
    print(n['name'],n['type'])
    code=n['parameters'].get('jsCode','')
    if n['name'] in ('Validate + Normalize','Insert Event'):print(safe(code))
    for line in code.splitlines():
        if any(s in line for s in ('source','ON CONFLICT','INSERT INTO','headers','query(','added_at')) and not any(s in line.lower() for s in ('password','secret','token','apikey','pit-')):print(safe(line))
