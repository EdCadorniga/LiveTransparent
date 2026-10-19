"""Read-only recovery audit of retained click webhook inputs. No header output."""
import json
from repair_v1_facts_sql import api
known={'rmFtop1jXctXpz4kJa1l','jxGQ0wfSQ3S4UcQsPHCQ','FiHvJKjHuxfeg1arFRUj','TEkdL5xGyUxXeCmYmAnb','6fqPSWbqb3HVVZdlzk5N','DUh8OO86BA4xPgub1neh','ENEHOrItPwan00GnzyZZ','DYoKxOSoet48F4GHzPBE','quqSUM8bckKaOIktVvgU','nqLFBlEsdm7qccr8Yyog'}
data=api('/api/v1/executions?workflowId=1diZyFmTqWQUEny3&limit=100')
print('Retained click executions:',len(data['data']))
for e in data['data']:
    if e.get('status') not in ('error','success'):continue
    d=api('/api/v1/executions/'+e['id']+'?includeData=true')
    raw=(d.get('data') or {}).get('resultData',{}).get('runData',{}).get('Webhook',[])
    if not raw:continue
    j=raw[0].get('data',{}).get('main',[[{}]])[0][0].get('json',{})
    body=j.get('body',{})
    print(json.dumps({'execution':e['id'],'status':e.get('status'),'startedAt':e.get('startedAt'),'contact_id':body.get('contact_id'),'known_link':body.get('link_id') in known,'link_id':body.get('link_id'),'event':body.get('event')}))
