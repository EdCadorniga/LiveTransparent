"""Validate/apply reporting-only V1 corrections against freshly fetched workflow state."""
import argparse
import copy
import json
import re
from audit_v1_accuracy import live_query, reconcile
from repair_v1_facts_sql import api, sql_read, sql_exec, ROOT
from fix_verified_booking_gate import save, parse

REVISION = 'accuracy-20261015-v1'


def revised_query(query):
    # Do not compute legacy values that the canonical payload immediately overwrites.
    start = query.index('\nSELECT jsonb_build_object(\n  \'funnel\'')
    end = query.index('   ) AS payload\n),', start)
    projection = query[start:end]
    redundant = ['sdrOutputs', 'bookingsBySource', 'mqlSourcesByForm', 'mqlsAdded', 'sqlBooking', 'sqlBookingBreakdown', 'meetingSummary', 'appointmentDetails', 'mqlSqlOrigin', 'sourceBreakdown']
    for key in redundant:
        projection, count = re.subn(r"^  '" + key + r"',.*\n", '', projection, flags=re.M)
        assert count == 1, key
    query = query[:start] + projection + query[end:]
    query = query.replace("WHERE sc.created_at::date BETWEEN $1::date AND $2::date", "WHERE sc.opportunity_id IN (SELECT opportunity_id FROM feedback_opps WHERE created_date BETWEEN $1::date AND $2::date)")
    query = query.replace("SELECT appointment_id AS qualification_id,contact_id,appointment_id,calendar_id,owner_id", "SELECT appointment_id AS qualification_id,contact_id,appointment_id,calendar_id,owner_id,booked_at")
    query = query.replace("FROM canonical_sql s JOIN canonical_mql m USING(contact_id))", "FROM canonical_sql s JOIN canonical_mql m USING(contact_id) WHERE m.added_at<=s.booked_at)")
    # Materialize narrow pre-booking ownership evidence once, avoiding repeated TOAST scans.
    anchor = 'canonical_appointment_origins AS ('
    at = query.index(anchor)
    owners = """canonical_vertical_contacts AS (
  SELECT contact_id,COALESCE(NULLIF(trim((SELECT cf->>'value' FROM jsonb_array_elements(
    CASE WHEN jsonb_typeof(payload_json->'customFields')='array' THEN payload_json->'customFields' ELSE '[]'::jsonb END) cf
    WHERE cf->>'id'='ODs8fBt5te5HEfSJ91pY' LIMIT 1)),''),'Unclassified') AS vertical FROM canonical_contacts
), canonical_opportunity_owners AS MATERIALIZED (
  SELECT COALESCE(dimensions_json->>'contact_id',payload_json->>'contactId') AS contact_id,
    loaded_at,COALESCE(NULLIF(dimensions_json->>'assigned_to',''),NULLIF(payload_json->>'assignedTo','')) AS owner_id
  FROM report_raw_ghl_opportunities
), canonical_contact_owners AS MATERIALIZED (
  SELECT regexp_replace(source_key,'^contact:','') AS contact_id,loaded_at,
    NULLIF(payload_json->>'assignedTo','') AS owner_id FROM report_raw_ghl_contacts
), """
    query = query[:at] + owners + query[at:]
    query = query.replace("SELECT COALESCE(NULLIF(o.dimensions_json->>'assigned_to',''),NULLIF(o.payload_json->>'assignedTo','')) AS owner_id\n    FROM report_raw_ghl_opportunities o\n    WHERE COALESCE(o.dimensions_json->>'contact_id',o.payload_json->>'contactId')=a.contact_id", "SELECT o.owner_id FROM canonical_opportunity_owners o\n    WHERE o.contact_id=a.contact_id")
    query = query.replace("SELECT NULLIF(c.payload_json->>'assignedTo','') AS owner_id\n    FROM report_raw_ghl_contacts c\n    WHERE regexp_replace(c.source_key,'^contact:','')=a.contact_id", "SELECT c.owner_id FROM canonical_contact_owners c\n    WHERE c.contact_id=a.contact_id")
    # Qualification requires an actual valid appointment, not successful owner attribution.
    query = query.replace("WHERE booked_at IS NOT NULL AND\n    (owner_id IN ('yU85G6kfhtW4vUtx3QE6','sqGx5rp3oAUG610NXyjU','03p5GatJBH7i9zjMaIzm') OR campaign_attributed)", "WHERE booked_at IS NOT NULL AND lower(COALESCE(status,'')) NOT IN ('cancelled','canceled','invalid','deleted')")
    query = query.replace("'reportRevision','booking-created-v1'", "'reportRevision','" + REVISION + "'")
    query = query.replace('SQL: first qualified approved-calendar booking by creation date, with pre-booking assignee or captured campaign attribution; no Sales Outreach-entry prerequisite', 'SQL: first non-canceled approved-calendar booking by recorded creation date; missing owner or UTM does not disqualify a verified booking')
    # Closed snapshot counts were not a verified SQL closure cohort.
    query = query.replace("'sqlBookingBreakdown','[]'::jsonb,", "'sqlBookingBreakdown','[]'::jsonb,\n    'closedBySource','[]'::jsonb,")
    # Canonical vertical rows must also include both calendars and unmatched contacts.
    at = query.index("    'verticalPerformance',(SELECT jsonb_agg(v ||")
    end = query.index('\n  ) AS payload FROM _base', at)
    query = query[:at] + """    'verticalPerformance',(SELECT jsonb_agg(v || jsonb_build_object(
      'mqls',(SELECT COUNT(*) FROM canonical_mql m LEFT JOIN canonical_vertical_contacts cc USING(contact_id) WHERE COALESCE(cc.vertical,'Unclassified')=v->>'vertical'),
      'sqls',(SELECT COUNT(*) FROM canonical_sql s LEFT JOIN canonical_vertical_contacts cc USING(contact_id) WHERE COALESCE(cc.vertical,'Unclassified')=v->>'vertical'),
      'meetings',(SELECT COUNT(*) FROM canonical_bookings b LEFT JOIN canonical_vertical_contacts cc USING(contact_id) WHERE COALESCE(cc.vertical,'Unclassified')=v->>'vertical'),
      'won',NULL,'lost',NULL)) FROM jsonb_array_elements(_base.payload->'verticalPerformance') v)
""".rstrip() + query[end:]
    return query


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--apply', action='store_true')
    args = p.parse_args()
    w = api('/api/v1/workflows/oxYDg6XnRBKhl1Xd')
    old = live_query(w)
    query = revised_query(old)
    sql_read('EXPLAIN ' + query.replace('$1', "'2026-09-01'").replace('$2', "'2026-09-30'") + ';')
    print('Revised SQL EXPLAIN passed.', flush=True)
    windows = [('2026-10-04','2026-10-10'),('2026-09-27','2026-10-03'),('2026-09-01','2026-09-30'),('2026-10-11','2026-10-14')]
    payloads = []
    for start, end in windows:
        import time
        now = time.monotonic()
        data = json.loads(sql_read('SET LOCAL jit=off; ' + query.replace('$1', "'"+start+"'").replace('$2', "'"+end+"'") + ';'))
        result = reconcile(data)
        print(json.dumps({**result, 'seconds': round(time.monotonic()-now,2)}), flush=True)
        assert not result['mismatches'], result['mismatches']
        payloads.append((start+'|'+end, data))
    if args.apply:
        assert api('/api/v1/workflows/'+w['id'])['versionId'] == w['versionId'], 'Concurrent workflow change'
        rev = copy.deepcopy(w)
        builder = next(n for n in rev['nodes'] if n['name']=='Build V1 Facts Query')
        assert json.dumps(old) in builder['parameters']['jsCode']
        builder['parameters']['jsCode'] = builder['parameters']['jsCode'].replace(json.dumps(old), json.dumps(query), 1)
        node = next(n for n in rev['nodes'] if n['name']=='Query V1 Facts')
        node['parameters']['jsCode'] = node['parameters']['jsCode'].replace("reportRevision==='booking-created-v1'", "reportRevision==='"+REVISION+"'")
        parse(builder['parameters']['jsCode']); parse(node['parameters']['jsCode'])
        refresh = api('/api/v1/workflows/kBuW8Uq3EOJFQKNF')
        rr = copy.deepcopy(refresh)
        refresh_node = next(n for n in rr['nodes'] if n['name']=='Refresh Reporting Cache')
        assert json.dumps(old) in refresh_node['parameters']['jsCode'], 'Refresh query differs; review before mutation'
        refresh_node['parameters']['jsCode'] = refresh_node['parameters']['jsCode'].replace(json.dumps(old), json.dumps(query), 1)
        parse(refresh_node['parameters']['jsCode'])
        save(refresh, rr)
        for key, data in payloads:
            sql_exec("INSERT INTO v1_facts_cache(window_key,payload,computed_at) VALUES('"+key+"','"+json.dumps(data).replace("'","''")+"'::jsonb,NOW()) ON CONFLICT(window_key) DO UPDATE SET payload=EXCLUDED.payload,computed_at=NOW();")
        save(w, rev)
