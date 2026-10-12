"""Inspect and repair V1 Facts SQL, validating on the report DB before saving."""
import json
import pathlib
import urllib.request
import argparse
import subprocess
import paramiko
import os
import urllib.parse
from datetime import datetime

def sql_read(sql):
    env = dict(line.split('=', 1) for line in (ROOT / '.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
    env = {k: v.strip().strip('\"').strip("'") for k, v in env.items()}
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(env.get('VPS_HOST') or env.get('VPS_HOSTNAME'), username=env['VPS_USER'],
        key_filename=os.path.expandvars(os.path.expanduser(env['VPS_SSH_KEY_PATH'])), timeout=20)
    try:
        stdin, stdout, stderr = client.exec_command('docker exec -i postgres-uokgs4c04ko0s4scccg40cgg psql -U postgres -d postgres -X -q -A -t -v ON_ERROR_STOP=1', timeout=300)
        stdin.write('BEGIN READ ONLY; SET LOCAL statement_timeout=240000;\n' + sql + '\nROLLBACK;')
        stdin.channel.shutdown_write()
        out, err = stdout.read().decode(), stderr.read().decode()
        if stdout.channel.recv_exit_status() != 0:
            raise RuntimeError(err)
        return out
    finally:
        client.close()

ROOT = pathlib.Path(__file__).resolve().parents[1]
HOST = 'https://automations.livetransparent.com'
ID = 'oxYDg6XnRBKhl1Xd'

def api(path, method='GET', body=None):
    env = dict(line.split('=', 1) for line in (ROOT / '.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
    key = env['N8N_LT_API_KEY'].strip().strip('\"').strip("'")
    req = urllib.request.Request(HOST + path, data=json.dumps(body).encode() if body else None,
        method=method, headers={'X-N8N-API-KEY': key, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=90) as res:
        return json.load(res)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inspect', action='store_true')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--vertical', action='store_true')
    args = parser.parse_args()
    if args.verify:
        for start, end in [('2026-10-04','2026-10-10'),('2026-09-27','2026-10-03')]:
            url = 'https://reports.livetransparent.com/api/report/executive-v1/facts?' + urllib.parse.urlencode({'from':start,'to':end,'retry':str(datetime.now().timestamp())})
            with urllib.request.urlopen(url, timeout=300) as res:
                raw = res.read()
            facts = json.loads(raw)
            print(json.dumps({'period':[start,end],'bytes':len(raw),'keys':list(facts), 'counts':facts.get('authoritativeGhlCounts'),'funnel':facts.get('funnel'),'sqlBookingBreakdown':facts.get('sqlBookingBreakdown')}))
        raise SystemExit(0)
    workflow = api('/api/v1/workflows/' + ID)
    node = next(n for n in workflow['nodes'] if n['name'] == 'Build V1 Facts Query')
    code = node['parameters']['jsCode']
    print(json.dumps({'active': workflow['active'], 'version': workflow['versionId'],
                      'activeVersion': workflow.get('activeVersionId')}))
    query = code.split('const queryText = `', 1)[1].rsplit('`;', 1)[0]
    old = "::numeric/COUNT(*),4)\n      FROM feedback_sql s"
    new = "::numeric/COUNT(*),4) END\n      FROM feedback_sql s"
    if old not in code and new not in code:
        raise RuntimeError('Repair anchor changed')
    repaired = code.replace(old, new, 1)
    if args.vertical:
        if "'verticalPerformance', '[]'::jsonb" not in repaired:
            raise RuntimeError('Vertical source anchor changed')
        ctes = (ROOT / 'reports/embed/executive-v1/lt-exec-v1-vertical-performance.sql').read_text()
        at = repaired.rfind('\nSELECT jsonb_build_object(')
        if at < 0:
            raise RuntimeError('Final SELECT anchor changed')
        repaired = repaired[:at] + ',\n' + ctes + repaired[at:]
        repaired = repaired.replace("'verticalPerformance', '[]'::jsonb", "'verticalPerformance', (SELECT jsonb_agg(to_jsonb(v) ORDER BY vertical) FROM vertical_performance v)")
    query = repaired.split('const queryText = `', 1)[1].rsplit('`;', 1)[0]
    sql_read('EXPLAIN ' + query.replace('$1', "'2026-10-04'").replace('$2', "'2026-10-10'"))
    print('Full query EXPLAIN passed (read-only).')
    if args.vertical:
        for start,end in [('2026-10-04','2026-10-10'),('2026-09-27','2026-10-03')]:
            payload = json.loads(sql_read(query.replace('$1',"'"+start+"'").replace('$2',"'"+end+"'")))
            rows = payload['verticalPerformance']
            totals = {k:sum(r[k] for r in rows) for k in ('leads','linkedin_backfills','mqls','sqls','meetings','responses','won','lost')}
            expected = payload['authoritativeGhlCounts']
            assert totals['leads'] == expected['new_contacts']
            assert totals['linkedin_backfills'] == expected['linkedin_backfill_contacts']
            assert totals['mqls'] == payload['funnel']['mqls_entered']
            assert totals['sqls'] == payload['funnel']['sqls_entered']
            assert totals['meetings'] == payload['meetingSummary']['unique_contacts']
            assert totals['won'] == payload['funnel']['closed_won_sqls']
            assert totals['lost'] == payload['funnel']['closed_lost_sqls']
            assert totals['responses'] == len(payload['responseSlaDetails'])
            print(json.dumps({'period':[start,end],'verticalTotals':totals,'rows':rows}))
    if args.apply and repaired != code:
        base = pathlib.Path(os.environ['LOCALAPPDATA']) / 'Temp' / 'opencode'
        if not base.is_dir():
            raise RuntimeError('Approved backup directory missing')
        (base / f'v1-facts-before-repair-{datetime.now():%Y%m%dT%H%M%S}.json').write_text(json.dumps(workflow))
        node['parameters']['jsCode'] = repaired
        settings = dict(workflow.get('settings') or {})
        settings.pop('availableInMCP', None)
        api('/api/v1/workflows/' + ID, 'PUT', {k:workflow[k] for k in ('name','nodes','connections')} | {'settings':settings})
        after = api('/api/v1/workflows/' + ID)
        if after['versionId'] != after.get('activeVersionId'):
            api('/api/v1/workflows/' + ID + '/activate', 'POST', {})
            after = api('/api/v1/workflows/' + ID)
        assert after['active'] and after['versionId'] == after['activeVersionId']
        assert next(n for n in after['nodes'] if n['name']==node['name'])['parameters']['jsCode'] == repaired
        print(json.dumps({'repairedVersion':after['versionId']}))
