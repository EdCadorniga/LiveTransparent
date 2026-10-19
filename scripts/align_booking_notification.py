"""Ensure Slack wording does not claim a booking before verification succeeds."""
import copy
from repair_v1_facts_sql import api
from fix_verified_booking_gate import save,parse
w=api('/api/v1/workflows/lQTW0QPwBcf3o7j8');rev=copy.deepcopy(w)
n=next(n for n in rev['nodes'] if n['name']=='Build Slack Payload');code=n['parameters']['jsCode']
code=code.replace("'New booking received (#leads)'","'Lead event received (booking verification pending)'")
code=code.replace("'MQL-qualified booking: yes'","'MQL classification: recorded separately'")
code=code.replace("`SQL-qualified booking: ${isTargetBooking ? 'yes' : 'no'}`","`Calendar metadata matches target: ${isTargetBooking ? 'yes' : 'no'}`")
if 'SQL-qualified booking: yes (verified GHL appointment)' not in code:
    anchor="sync.verifiedAppointmentId = String(verifiedAppointment.id || verifiedAppointment.appointmentId || verifiedAppointment._id || '');"
    assert anchor in code
    code=code.replace(anchor,anchor+"\ntextLines[0]='Verified booking received (#leads)';\ntextLines.push('SQL-qualified booking: yes (verified GHL appointment)');",1)
n['parameters']['jsCode']=code;parse(code)
if rev!=w:save(w,rev)
