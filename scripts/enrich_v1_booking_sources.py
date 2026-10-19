"""Enrich V1 facts with booking-source detail and new-booking rows.

Reads the live n8n V1 Facts workflow, applies additive SQL changes, validates
the full query on the report DB, and only writes when --apply is passed.
"""
import argparse
import json
import os
import pathlib
import urllib.request
from datetime import datetime

from repair_v1_facts_sql import api, sql_read, ID, ROOT


def extract_query(code):
    marker = 'const queryText = "'
    start = code.index(marker) + len(marker)
    end = code.index('";', start)
    return code[start:end].replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')


def wrap_query(sql):
    marker = 'const queryText = "'
    start = sql.index(marker) + len(marker)
    end = sql.index('";', start)
    return sql[:start] + sql[start:end] + sql[end:]


def patch_query(query):
    old_cte = "), canonical_bookings AS ("
    new_cte = """), canonical_mql_sources AS (
  SELECT m.contact_id, m.source, m.added_at,
    c.link_name, c.vertical AS link_vertical, c.utm_source, c.utm_medium, c.utm_campaign
  FROM canonical_mql m
  LEFT JOIN LATERAL (
    SELECT c.link_name, c.vertical, c.utm_source, c.utm_medium, c.utm_campaign
    FROM lt_booking_link_clicks c
    WHERE m.source = 'booking_link_click' AND c.contact_id = m.contact_id
      AND c.clicked_at <= m.added_at + INTERVAL '2 minutes'
    ORDER BY c.clicked_at DESC LIMIT 1
  ) c ON TRUE
), canonical_bookings AS ("""
    if old_cte not in query:
        raise RuntimeError('canonical_bookings anchor missing')
    query = query.replace(old_cte, new_cte, 1)

    old_sql = """'sqlBooking',(SELECT COALESCE(jsonb_agg(to_jsonb(x)),'[]'::jsonb) FROM (SELECT calendar_id,'Verified appointment' AS booked_via,COUNT(DISTINCT contact_id) AS sqls FROM canonical_sql GROUP BY calendar_id) x),"""
    new_sql = """'sqlBooking',(SELECT COALESCE(jsonb_agg(to_jsonb(x)),'[]'::jsonb) FROM (
      SELECT s.calendar_id,'Verified appointment' AS booked_via,
        ba.booked_via_utm_source AS utm_source,ba.booked_via_medium AS utm_medium,ba.booked_via_campaign AS utm_campaign,
        COUNT(DISTINCT s.contact_id) AS sqls
      FROM canonical_sql s LEFT JOIN lt_booking_attribution ba USING(appointment_id)
      GROUP BY 1,2,3,4,5) x),"""
    if old_sql not in query:
        raise RuntimeError('sqlBooking anchor missing')
    query = query.replace(old_sql, new_sql, 1)

    old_appt = """'appointmentDetails',(SELECT COALESCE(jsonb_agg(to_jsonb(b)),'[]'::jsonb) FROM canonical_booking_owners b),"""
    new_appt = old_appt + """
    'newBookingDetails',(SELECT COALESCE(jsonb_agg(jsonb_build_object(
      'appointment_id',appointment_id,'contact_id',contact_id,'contact_name',contact_name,
      'calendar_id',calendar_id,'booked_at',booked_at,'start_at',start_at,'status',status,
      'owner_id',owner_id,'campaign_attributed',campaign_attributed) ORDER BY booked_at),'[]'::jsonb) FROM canonical_new_bookings),"""
    if old_appt not in query:
        raise RuntimeError('appointmentDetails anchor missing')
    query = query.replace(old_appt, new_appt, 1)

    old_mql = """'mqlSourcesByForm',(SELECT COALESCE(jsonb_agg(to_jsonb(x)),'[]'::jsonb) FROM (SELECT source,COUNT(*) AS contacts FROM canonical_mql GROUP BY source) x),"""
    new_mql = old_mql + """
    'mqlSourcesDetailed',(SELECT COALESCE(jsonb_agg(to_jsonb(x) ORDER BY contacts DESC),'[]'::jsonb) FROM (
      SELECT source AS origin_kind,link_name,link_vertical AS vertical,utm_source,utm_medium,utm_campaign,COUNT(*)::int AS contacts
      FROM canonical_mql_sources GROUP BY 1,2,3,4,5,6) x),"""
    if old_mql not in query:
        raise RuntimeError('mqlSourcesByForm anchor missing')
    query = query.replace(old_mql, new_mql, 1)

    query = query.replace("'reportRevision','accuracy-20261015-v1'", "'reportRevision','accuracy-20261019-v1'", 1)
    return query


def run_window(query, start, end):
    payload = json.loads(sql_read(query.replace('$1', "'" + start + "'").replace('$2', "'" + end + "'")))
    assert payload['funnel']['mqls_entered'] == sum(r['contacts'] for r in payload['mqlSourcesDetailed'])
    assert payload['meetingSummary']['new_bookings_created'] == len(payload['newBookingDetails'])
    return {
        'period': [start, end],
        'mqls': payload['funnel']['mqls_entered'],
        'mqlSourcesDetailed': payload['mqlSourcesDetailed'],
        'newBookingDetails': payload['newBookingDetails'],
        'sqlBooking': payload['sqlBooking'],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--window', default='2026-10-11')
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
        base = pathlib.Path(os.environ['LOCALAPPDATA']) / 'Temp' / 'opencode'
        base.mkdir(parents=True, exist_ok=True)
        (base / f'v1-facts-before-sources-{datetime.now():%Y%m%dT%H%M%S}.json').write_text(json.dumps(workflow))
        new_code = code[:code.index('const queryText = "')] + 'const queryText = "' + patched.replace('"', '\\"').replace('\n', '\\n') + '";' + code[code.index('";', code.index('const queryText = "')) + 2:]
        assert extract_query(new_code) == patched, 'round-trip query mismatch'
        node['parameters']['jsCode'] = new_code
        settings = dict(workflow.get('settings') or {})
        settings.pop('availableInMCP', None)
        api('/api/v1/workflows/' + ID, 'PUT', {k: workflow[k] for k in ('name', 'nodes', 'connections')} | {'settings': settings})
        after = api('/api/v1/workflows/' + ID)
        if after['versionId'] != after.get('activeVersionId'):
            api('/api/v1/workflows/' + ID + '/activate', 'POST', {})
            after = api('/api/v1/workflows/' + ID)
        assert after['active'] and after['versionId'] == after.get('activeVersionId')
        print(json.dumps({'appliedVersion': after['versionId']}))
