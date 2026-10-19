"""Add contact-action opportunity attribution to V1 facts.

Campaign and medium are inferred from the contact's current campaign/action
tags, not from the import source. Validates on the report DB before --apply.
"""
import argparse
import json
import os
import pathlib
import sys
from datetime import datetime

from repair_v1_facts_sql import api, sql_read, ID
from enrich_v1_booking_sources import extract_query

VERTICALS = "('Alcohol','Cannabis','Cannabis Dispensaries','Crypto','Gambling','Mushroom','Nicotine','Peptides')"


def patch_query(query):
    old = "), canonical_mql AS ("
    new = """), canonical_opportunity_actions AS (
  SELECT o.source_key AS opportunity_id,
    COALESCE(NULLIF(trim((SELECT cf->>'value' FROM jsonb_array_elements(
      CASE WHEN jsonb_typeof(c.payload_json->'customFields')='array' THEN c.payload_json->'customFields' ELSE '[]'::jsonb END) cf
      WHERE cf->>'id'='ODs8fBt5te5HEfSJ91pY' LIMIT 1)),''),'') AS vertical,
    replace(replace(replace(COALESCE(c.payload_json->>'tags',''),'[',''),']',''),'"','') AS tags
  FROM (
    SELECT DISTINCT ON (source_key) source_key, dimensions_json, payload_json
    FROM report_raw_ghl_opportunities
    WHERE NULLIF(source_key,'') IS NOT NULL
    ORDER BY source_key, report_date ASC
  ) o
  LEFT JOIN canonical_contacts c ON c.contact_id = o.dimensions_json->>'contact_id'
  WHERE (COALESCE(NULLIF(o.dimensions_json->>'source_created_at','')::timestamptz,
                  NULLIF(o.payload_json->>'createdAt','')::timestamptz,
                  NULLIF(o.payload_json->>'dateAdded','')::timestamptz) AT TIME ZONE 'America/Los_Angeles')::date BETWEEN $1::date AND $2::date
), opportunity_action_sources AS (
  SELECT
    CASE
      WHEN tags ILIKE '%simpletext%' THEN 'SMS'
      WHEN tags ILIKE '%linkedin%' THEN 'LinkedIn'
      WHEN tags ILIKE '%meeting booked%' OR tags ILIKE '%booking%' THEN 'Calendar'
      WHEN tags ILIKE '%email open%' OR tags ILIKE '%dan_seq_replied_or_booked%' OR tags ILIKE '%partner_replied%' OR tags ILIKE '%clicked_website_trigger%' THEN 'Email'
      ELSE 'No captured action'
    END AS medium,
    CASE WHEN vertical IN """ + VERTICALS + """
      THEN vertical || ' Brands Multi-Channel Outbound - Oct 2026'
      ELSE 'Campaign not captured' END AS campaign,
    COUNT(*)::int AS opportunities
  FROM canonical_opportunity_actions
  GROUP BY 1,2
), canonical_mql AS ("""
    if old not in query:
        raise RuntimeError('canonical_mql anchor missing')
    query = query.replace(old, new, 1)
    anchor = "    'sdrOutputs',(SELECT jsonb_agg(to_jsonb(s) ORDER BY owner_name) FROM canonical_sdr s),"
    add = anchor + """
    'opportunityActionSources',(SELECT COALESCE(jsonb_agg(to_jsonb(x) ORDER BY opportunities DESC),'[]'::jsonb) FROM opportunity_action_sources x),
    'opportunityActionCoverage',jsonb_build_object(
      'total',(SELECT COUNT(*)::int FROM canonical_opportunity_actions),
      'with_campaign',(SELECT COUNT(*)::int FROM canonical_opportunity_actions WHERE vertical IN """ + VERTICALS + """)
    ),"""
    if anchor not in query:
        raise RuntimeError('sdrOutputs anchor missing')
    query = query.replace(anchor, add, 1)
    return query


def run_window(query, start, end):
    payload = json.loads(sql_read(query.replace('$1', "'" + start + "'").replace('$2', "'" + end + "'")))
    rows = payload['opportunityActionSources']
    total = sum(r['opportunities'] for r in rows)
    assert total == payload['funnel']['opportunities_created'], (total, payload['funnel']['opportunities_created'])
    return {'period': [start, end], 'opportunityActionSources': rows, 'opportunityActionCoverage': payload['opportunityActionCoverage']}


def apply(workflow, node, new_code, label):
    base = pathlib.Path(os.environ['LOCALAPPDATA']) / 'Temp' / 'opencode'
    base.mkdir(parents=True, exist_ok=True)
    (base / f'v1-{label}-before-actions-{datetime.now():%Y%m%dT%H%M%S}.json').write_text(json.dumps(workflow))
    node['parameters']['jsCode'] = new_code
    settings = dict(workflow.get('settings') or {})
    settings.pop('availableInMCP', None)
    api('/api/v1/workflows/' + workflow['id'], 'PUT', {k: workflow[k] for k in ('name', 'nodes', 'connections')} | {'settings': settings})
    after = api('/api/v1/workflows/' + workflow['id'])
    if after['versionId'] != after.get('activeVersionId'):
        api('/api/v1/workflows/' + workflow['id'] + '/activate', 'POST', {})
        after = api('/api/v1/workflows/' + workflow['id'])
    assert after['active'] and after['versionId'] == after.get('activeVersionId')
    print(json.dumps({label: after['versionId']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    workflow = api('/api/v1/workflows/' + ID)
    node = next(n for n in workflow['nodes'] if n['name'] == 'Build V1 Facts Query')
    code = node['parameters']['jsCode']
    query = extract_query(code)
    patched = patch_query(query)
    assert patched != query
    sql_read('EXPLAIN ' + patched.replace('$1', "'2026-10-11'").replace('$2', "'2026-10-17'"))
    print('EXPLAIN passed')
    for start, end in [('2026-10-11', '2026-10-17'), ('2026-10-04', '2026-10-10')]:
        print(json.dumps(run_window(patched, start, end), indent=2))
    if args.apply:
        marker = 'const queryText = "'
        start = code.index(marker) + len(marker)
        end = code.index('";', start)
        new_code = code[:start] + patched.replace('"', '\\"').replace('\n', '\\n') + code[end:]
        assert extract_query(new_code) == patched
        apply(workflow, node, new_code, 'facts')
        refresh = api('/api/v1/workflows/kBuW8Uq3EOJFQKNF')
        rn = next(n for n in refresh['nodes'] if n['name'] == 'Refresh Reporting Cache')
        rcode = rn['parameters']['jsCode']
        rmarker = 'const sql="'
        rs = rcode.index(rmarker) + len(rmarker)
        re_ = rcode.index('";', rs)
        rsql = rcode[rs:re_].replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
        rpatched = patch_query(rsql)
        new_rcode = rcode[:rs] + rpatched.replace('"', '\\"').replace('\n', '\\n') + rcode[re_:]
        s2 = new_rcode.index(rmarker) + len(rmarker)
        e2 = new_rcode.index('";', s2)
        assert new_rcode[s2:e2].replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\') == rpatched
        apply(refresh, rn, new_rcode, 'refresh')
