"""Inspect only relevant code around the confirmed SQL-tag write."""
from audit_sql_tag_writers import safe
from repair_v1_facts_sql import api

w = api('/api/v1/workflows/lQTW0QPwBcf3o7j8')
print(w['name'], w['versionId'], w.get('activeVersionId'))
for n in w['nodes']:
    if n['name'] == 'Build Slack Payload':
        lines=n['parameters']['jsCode'].splitlines()
        for start,end in ((90,145),(280,340)):
            for i in range(start-1,min(end,len(lines))):
                if any(s in lines[i].lower() for s in ('apikey','password','secret','token','pit-')):
                    print(str(i+1)+': [credential line omitted]')
                else:
                    print(str(i+1)+': '+safe(lines[i]))
