"""Read-only query plans and schema for V1 accuracy/performance investigation."""
from repair_v1_facts_sql import api, sql_read
from audit_v1_accuracy import live_query
import json

if __name__ == '__main__':
    import sys
    query = live_query(api('/api/v1/workflows/oxYDg6XnRBKhl1Xd'))
    if '--query' in sys.argv:
        print(query)
    elif '--schema' in sys.argv:
        print(sql_read("SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_name IN ('lt_exec_v1_appointment_facts','v1_facts_cache','report_ghl_social_statistics') ORDER BY table_name,ordinal_position;"))
    else:
        plan = json.loads(sql_read('EXPLAIN (FORMAT JSON) ' + query.replace('$1', "'2026-09-01'").replace('$2', "'2026-09-30'") + ';'))[0]['Plan']
        rows = []
        def walk(node):
            rows.append({k: node[k] for k in ['Node Type', 'Total Cost', 'Plan Rows', 'Subplan Name', 'CTE Name', 'Relation Name', 'Join Filter', 'Filter'] if k in node})
            for child in node.get('Plans', []):
                walk(child)
        walk(plan)
        print(json.dumps(sorted(rows, key=lambda r: r['Total Cost'], reverse=True)[:35], indent=2))
