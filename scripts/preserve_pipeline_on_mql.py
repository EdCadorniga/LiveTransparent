"""Prevent an MQL tag signal from moving an existing non-Warm opportunity back."""
import copy
from repair_v1_facts_sql import api
from fix_verified_booking_gate import save,parse
w=api('/api/v1/workflows/MI91SutAbAj3QSXp');rev=copy.deepcopy(w)
n=next(n for n in rev['nodes'] if n['name']=='Ensure Warm Qualified Opportunity')
code=n['parameters']['jsCode']
if 'existing_non_warm_opportunity_preserved' not in code:
    anchor='const existingOpportunityName = cleanString(existingOpportunity?.name);'
    assert anchor in code
    guard="if(existingOpportunity && pipelineIdOf(existingOpportunity)!==ids.warmPipelineId){return [{json:{status:'skipped',reason:'existing_non_warm_opportunity_preserved',contactId,opportunityId:opportunityId(existingOpportunity)}}];}\n"
    code=code.replace(anchor,guard+anchor,1);n['parameters']['jsCode']=code
parse(code)
if rev!=w:save(w,rev)
