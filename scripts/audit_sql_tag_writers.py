"""Read-only n8n-lt SQL-tag writer audit. Never emit config or credentials."""
import json
import re
from repair_v1_facts_sql import api

def safe(text):
    text = re.sub(r'pit-[A-Za-z0-9-]+', '[REDACTED]', text)
    return text.encode('ascii', 'replace').decode('ascii')

if __name__ == '__main__':
    page = api('/api/v1/workflows?limit=250')
    workflows = page['data']
    while page.get('nextCursor'):
        page = api('/api/v1/workflows?limit=250&cursor=' + page['nextCursor'])
        workflows.extend(page['data'])
    for w in workflows:
        hits = []
        for n in w.get('nodes', []):
            params = n.get('parameters', {})
            code = params.get('jsCode', '')
            if not code:
                raw = json.dumps(params)
                if re.search(r'[\"\x27]sql[\"\x27]', raw, re.I) and ('tags' in raw.lower()):
                    hits.append({'node': n['name'], 'type': n['type'], 'tag_operation': True})
                continue
            for i, line in enumerate(code.splitlines()):
                if re.search(r"['\"]sql['\"]", line, re.I) and not re.search(r'(SELECT|FROM|GROUP BY)', line):
                    hits.append({'node': n['name'], 'line': i+1, 'code': safe(line[:350])})
        if hits:
            print(json.dumps({'id':w['id'], 'name':w['name'], 'active':w['active'], 'hits':hits}))
    for wid in ('1diZyFmTqWQUEny3','oxYDg6XnRBKhl1Xd'):
        w = api('/api/v1/workflows/'+wid)
        print(json.dumps({'inspect':wid,'version':w['versionId'],'published':w.get('activeVersionId'),
            'click_tags':[n['parameters'].get('jsonBody') for n in w['nodes'] if n['name']=='Apply MQL Tag'],
            'cache_wrapper':any('_combined AS' in n['parameters'].get('jsCode','') for n in w['nodes'])}))
