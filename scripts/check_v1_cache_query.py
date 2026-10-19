"""Read-only validation of the live cache query and cache coverage."""
from repair_v1_facts_sql import api, sql_read

w=api('/api/v1/workflows/oxYDg6XnRBKhl1Xd')
code=next(n for n in w['nodes'] if n['name']=='Build V1 Facts Query')['parameters']['jsCode']
query=code.split('const queryText = `',1)[1].rsplit('`;',1)[0]
print('Live Facts version:',w['versionId'])
try:
    sql_read('EXPLAIN '+query.replace('$1',"'2026-10-04'").replace('$2',"'2026-10-10'").rstrip().rstrip(';')+';')
    print('Live cache query parses.')
except RuntimeError as e:
    print('Live cache query FAILED:',e)
print(sql_read('SELECT window_key,computed_at FROM v1_facts_cache ORDER BY window_key;'))
