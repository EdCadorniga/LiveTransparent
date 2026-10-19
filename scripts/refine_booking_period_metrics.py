"""Apply booking-created-date SQL/SDR metrics, preserving legacy movement separately."""
import copy
import json
from repair_v1_facts_sql import api,sql_read,ROOT
from fix_verified_booking_gate import save,parse

if __name__=='__main__':
    w=api('/api/v1/workflows/oxYDg6XnRBKhl1Xd');rev=copy.deepcopy(w)
    builder=next(n for n in rev['nodes'] if n['name']=='Build V1 Facts Query');code=builder['parameters']['jsCode']
    old=json.JSONDecoder().raw_decode(code.split('const queryText = ',1)[1])[0]
    anchor='),\ncanonical_contacts AS (';at=old.find(anchor);assert at>0
    query=old[:at]+'),\n'+(ROOT/'reports/embed/executive-v1/canonical-metrics.sql').read_text()
    sql_read('EXPLAIN '+query.replace('$1',"'2026-10-04'").replace('$2',"'2026-10-10'")+';')
    for start,end in [('2026-10-04','2026-10-10'),('2026-09-27','2026-10-03')]:
        data=json.loads(sql_read('SET LOCAL jit=off; '+query.replace('$1',"'"+start+"'").replace('$2',"'"+end+"'")+';'))
        rows=data['sdrOutputs'];f=data['funnel'];meet=data['meetingSummary']
        assert sum(r['mqls'] for r in rows)==f['mqls_entered']
        assert sum(r['sqls'] for r in rows)==f['sqls_entered']
        assert sum(r['booked'] for r in rows)==meet['new_bookings_created']
        print(json.dumps({'window':data['window'],'funnel':f,'meetings':meet,'outputs':rows}))
    builder['parameters']['jsCode']=code.replace(json.dumps(old),json.dumps(query),1)
    querynode=next(n for n in rev['nodes'] if n['name']=='Query V1 Facts')
    querynode['parameters']['jsCode']=querynode['parameters']['jsCode'].replace("row?.payload?.metricVersion==='verified-booking-v2'","row?.payload?.metricVersion==='verified-booking-v2' && row?.payload?.reportRevision==='booking-created-v1'")
    parse(builder['parameters']['jsCode']);parse(querynode['parameters']['jsCode']);save(w,rev)
    refresh=api('/api/v1/workflows/kBuW8Uq3EOJFQKNF');rr=copy.deepcopy(refresh)
    n=next(n for n in rr['nodes'] if n['name']=='Refresh Reporting Cache')
    assert json.dumps(old) in n['parameters']['jsCode'];n['parameters']['jsCode']=n['parameters']['jsCode'].replace(json.dumps(old),json.dumps(query),1);parse(n['parameters']['jsCode']);save(refresh,rr)
