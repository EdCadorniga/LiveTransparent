"""Read-only reporting source inspection; never outputs workflow credentials."""
import json
from repair_v1_facts_sql import api, sql_read

for wid in ('oxYDg6XnRBKhl1Xd', 'Bukc0mgOD2r7V6ED', 'MvPLbUAN9IIQikxb'):
    w = api('/api/v1/workflows/' + wid)
    print(json.dumps({'id': wid, 'active': w['active'], 'version': w['versionId'], 'published': w.get('activeVersionId')}))
    for n in w['nodes']:
        code = n['parameters'].get('jsCode', '')
        if 'const queryText = `' in code:
            query = code.split('const queryText = `', 1)[1].rsplit('`;', 1)[0]
            payload = json.loads(sql_read(query.replace('$1', "'2026-10-04'").replace('$2', "'2026-10-10'")))
            print(json.dumps({k:v for k,v in payload.items() if k in ('sdrPerformance','sdrFacts','meetingDetails','meetings','campaignChannelBreakdown','leadSourceBreakdown','opportunitySourceBreakdown','leadSourceCoverage')}))
        for marker in ('feedback_opps AS', 'cameron_meetings AS', 'cameron_meeting', 'sdr_sqls AS', 'sdr_booked AS'):
            at = code.find(marker)
            if at >= 0:
                print(marker, code[at:at+4500])

logs = json.load(open('local-scripts/vertical-campaign-log-audit-20261013.json', encoding='utf-8'))
export = json.load(open('local-scripts/vertical-email-message-export-20261013.json', encoding='utf-8'))
index = {r['id']:r for r in export['rows']}
for s in logs['sources']:
    if s['actionType'] != 'email':
        continue
    queued = [r for r in s['rows'] if r.get('queuedSuccessfully')]
    matches = [index[r['messageId']] for r in queued if r.get('messageId') in index]
    print(json.dumps({'campaign':s['label'],'queued':len(queued),'exactIds':len(matches),'sent':sum(r['status']=='sent' and r['direction']=='outbound' for r in matches)}))
