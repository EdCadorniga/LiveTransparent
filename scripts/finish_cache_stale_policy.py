"""Serve last validated Facts cache immediately while native refresh runs."""
import copy
from repair_v1_facts_sql import api
from fix_verified_booking_gate import save,parse
w=api('/api/v1/workflows/oxYDg6XnRBKhl1Xd');rev=copy.deepcopy(w)
n=next(n for n in rev['nodes'] if n['name']=='Query V1 Facts')
old="if(fresh){payload={...row.payload,cache:{status:'hit',computed_at:row.computed_at}};}"
new="if(valid){payload={...row.payload,cache:{status:fresh?'hit':'stale',computed_at:row.computed_at}};}"
code=n['parameters']['jsCode']
if old in code:n['parameters']['jsCode']=code.replace(old,new,1);parse(n['parameters']['jsCode']);save(w,rev)
else:assert new in code;print('Stale policy already installed.')
