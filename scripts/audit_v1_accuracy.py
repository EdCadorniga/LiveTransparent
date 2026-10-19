"""Read-only V1 reconciliation. Prints metrics and discrepancies, never config secrets."""
import json
import urllib.request
from repair_v1_facts_sql import api, sql_read


def live_query(workflow):
    code = next(n['parameters']['jsCode'] for n in workflow['nodes'] if n['name'] == 'Build V1 Facts Query')
    tail = code.split('const queryText = ', 1)[1]
    if tail.startswith('`'):
        return tail[1:].rsplit('`;', 1)[0]
    return json.JSONDecoder().raw_decode(tail)[0]


def reconcile(data):
    f = data['funnel']
    checks = {}
    for key, field in [('mqls', 'mqls_entered'), ('sqls', 'sqls_entered')]:
        checks['vertical_' + key] = [sum(r.get(key) or 0 for r in data.get('verticalPerformance') or []), f.get(field)]
        checks['owners_' + key] = [sum(r.get(key) or 0 for r in data.get('sdrOutputs') or []), f.get(field)]
    checks['vertical_meetings'] = [sum(r.get('meetings') or 0 for r in data.get('verticalPerformance') or []), data.get('meetingSummary', {}).get('unique_contacts')]
    checks['sources_mql'] = [sum(r.get('contacts') or 0 for r in data.get('mqlSourcesByForm') or []), f.get('mqls_entered')]
    checks['sources_sql'] = [sum(r.get('sqls') or 0 for r in data.get('sqlBooking') or []), f.get('sqls_entered')]
    checks['sources_opportunities'] = [sum(r.get('opportunities') or 0 for r in data.get('opportunityOrigin') or []), f.get('opportunities_created')]
    checks['sources_mql_detailed'] = [sum(r.get('contacts') or 0 for r in data.get('mqlSourcesDetailed') or []), f.get('mqls_entered')]
    checks['new_bookings'] = [len(data.get('newBookingDetails') or []), data.get('meetingSummary', {}).get('new_bookings_created')]
    checks['opportunity_actions'] = [sum(r.get('opportunities') or 0 for r in data.get('opportunityActionSources') or []), f.get('opportunities_created')]
    return {'window': data.get('window'), 'funnel': f, 'meetings': data.get('meetingSummary'), 'cache': data.get('cache'), 'checks': checks, 'mismatches': {k: v for k, v in checks.items() if v[0] != v[1]}}


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--direct', action='store_true')
    args = p.parse_args()
    workflow = api('/api/v1/workflows/oxYDg6XnRBKhl1Xd')
    print(json.dumps({'workflow': workflow['id'], 'version': workflow['versionId'], 'published': workflow.get('activeVersionId')}), flush=True)
    query = live_query(workflow) if args.direct else None
    for start, end in [('2026-10-04', '2026-10-10'), ('2026-09-27', '2026-10-03'), ('2026-09-01', '2026-09-30'), ('2026-10-11', '2026-10-14')]:
        if query:
            data = json.loads(sql_read('SET LOCAL jit=off; ' + query.replace('$1', "'" + start + "'").replace('$2', "'" + end + "'") + ';'))
        else:
            url = 'https://reports.livetransparent.com/api/report/executive-v1/facts?from=' + start + '&to=' + end
            with urllib.request.urlopen(url, timeout=300) as response:
                data = json.load(response)
        result = reconcile(data)
        print(json.dumps(result), flush=True)
        assert not result['mismatches'], result['mismatches']
