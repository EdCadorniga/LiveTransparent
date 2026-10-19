"""Read-only inspection and explicit deployment support for vertical LinkedIn outreach.

Only the LiveTransparent n8n instance is addressed. Never print Config values.
"""
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[2]
ENV = dotenv_values(ROOT / '.env')
for key, value in ENV.items():
    if value is not None:
        os.environ.setdefault(key, value)
from plan_john_invite_withdrawals import Database as BaseDatabase

BASE = 'https://automations.livetransparent.com'


def api(method, path, body=None):
    response = requests.request(method, BASE + '/api/v1' + path,
                                headers={'X-N8N-API-KEY': ENV['N8N_LT_API_KEY']},
                                json=body, timeout=60)
    if not response.ok:
        raise RuntimeError(f'n8n-lt HTTP {response.status_code}')
    return response.json() if response.content else {}


def redact(text):
    for key, value in ENV.items():
        if value and len(value) > 8 and any(x in key.upper() for x in ('KEY', 'TOKEN', 'SECRET', 'PASSWORD', 'PIT')):
            text = text.replace(value, '[REDACTED]')
    import re
    text = re.sub(r'pit-[a-zA-Z0-9-]+', '[REDACTED_PIT]', text)
    return text


class Database(BaseDatabase):
    def execute(self, sql):
        command = 'docker exec -i postgres-uokgs4c04ko0s4scccg40cgg psql -U postgres -d postgres -X -q -tA -v ON_ERROR_STOP=1'
        stdin, stdout, stderr = self.client.exec_command(command, timeout=180)
        stdin.write('SET standard_conforming_strings=on;\n' + sql + '\n')
        stdin.flush(); stdin.channel.shutdown_write()
        out=stdout.read().decode('utf-8'); err=stderr.read().decode('utf-8')
        if stdout.channel.recv_exit_status()!=0:
            raise RuntimeError('Postgres operation failed: '+redact(err)[:1500])
        return out.strip()


def inspect():
    with Database() as db:
        for table in ('linkedin_connection_state', 'linkedin_contact_profile_index',
                      'report_raw_ghl_contacts', 'linkedin_activity_events',
                      'sales_navigator_v2_conversation_map', 'sales_navigator_v2_message_events',
                      'linkedin_invitation_withdrawals'):
            print(table, json.dumps(db.rows(f"SELECT column_name,data_type FROM information_schema.columns WHERE table_name='{table}' ORDER BY ordinal_position")))
        print('withdrawals', json.dumps(db.rows('SELECT withdraw_status, reinvite_status, count(*), min(cooldown_until), max(cooldown_until) FROM linkedin_invitation_withdrawals GROUP BY 1,2')))
    for wid in ('fXxw5lanZcDmUrst', 'd0tEtijajisIsYcs', '3ttEvr5NMcQCS4Hp', 'ZiYEBuP7xdddhnUB'):
        wf = api('GET', '/workflows/' + wid)
        print('workflow', wf['id'], wf['name'], wf['active'])
        for node in wf['nodes']:
            if node['name'] == 'Config':
                print('Config names', [x.get('name') for x in node['parameters'].get('assignments', {}).get('assignments', [])])
            else:
                params = node.get('parameters', {})
                if 'jsCode' in params:
                    text = redact(params['jsCode'])
                    # Inspection exports are local-only, sanitized and never redeployed.
                    out = ROOT / 'local-scripts' / ('vertical-inspect-' + wid + '-' + node['id'] + '.js')
                    out.write_text(text, encoding='utf-8')
                    print('code', node['name'], str(out.relative_to(ROOT)))
                elif node['type'].endswith('postgres'):
                    print('sql', node['name'], redact(params.get('query', '')))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'sql':
        with Database() as db:
            print(db.execute(sys.argv[2]))
    else:
        inspect()
