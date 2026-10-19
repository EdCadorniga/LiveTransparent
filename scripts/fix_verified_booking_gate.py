"""Fix confirmed n8n-lt booking SQL writer and click misclassification.

Default: read-only validation. --apply: scoped publication, no workflow execution,
no contact deletion, no historical tag removal, no messages sent.
"""
import argparse
import copy
import json
import os
import pathlib
import subprocess
from datetime import datetime
from repair_v1_facts_sql import api

GATE = r"""
// VERIFIED_BOOKING_GATE_V1: calendar metadata or a click is not booking proof.
const suppliedAppointmentId = String(incoming.appointmentId || incoming.appointment_id || incoming.eventId || customData.appointmentId || incoming.appointment?.id || calendar.appointmentId || '').trim();
const suppliedStart = Date.parse(startRaw);
let verifiedAppointment = null;
try {
  const response = await this.helpers.httpRequest({
    method: 'GET', url: `${baseUrl}/contacts/${encodeURIComponent(contactId)}/appointments`,
    headers, json: true, timeout: 20000,
  });
  const events = Array.isArray(response?.events) ? response.events : null;
  if (!events) throw new Error('appointment_response_shape_unrecognized');
  const matches = events.filter((event) => {
    const id = String(event.id || event.appointmentId || event._id || '');
    const cal = String(event.calendarId || event.calendar_id || '');
    const status = String(event.appointmentStatus || event.status || '').toLowerCase();
    const ownerContact = String(event.contactId || event.contact_id || contactId);
    if (ownerContact !== contactId || !['SrtXcFVyea7pFl3nTiIK','WS6lacfQK2XOhqN7mRaF'].includes(cal)) return false;
    if (['cancelled','canceled','invalid','deleted'].includes(status)) return false;
    if (suppliedAppointmentId) return id === suppliedAppointmentId;
    const eventStart = Date.parse(event.startTime || event.startAt || event.start_at || '');
    return Number.isFinite(suppliedStart) && Number.isFinite(eventStart) && Math.abs(eventStart-suppliedStart) < 60000;
  });
  if (matches.length === 1) verifiedAppointment = matches[0];
  sync.bookingVerification = verifiedAppointment ? 'verified' : 'no_unique_matching_appointment';
} catch (error) {
  sync.bookingVerification = 'lookup_failed';
}
if (!verifiedAppointment) {
  sync.attempted = false;
  sync.reason = 'verified_booking_required';
  textLines.push('GHL sync: skipped (no verified matching appointment on an approved calendar)');
  return [{ json: { text: textLines.join('\n'), sourcePayload: incoming, sync } }];
}
sync.verifiedAppointmentId = String(verifiedAppointment.id || verifiedAppointment.appointmentId || verifiedAppointment._id || '');
"""

def parse(code):
    check = "const AsyncFunction=Object.getPrototypeOf(async function(){}).constructor;new AsyncFunction("+json.dumps(code)+");"
    subprocess.run(['node','-'],input=check,text=True,encoding='utf-8',check=True)

def save(original, revised):
    backup = pathlib.Path(os.environ['LOCALAPPDATA'])/'Temp/opencode'
    assert backup.is_dir()
    (backup/f"booking-gate-before-{original['id']}-{datetime.now():%Y%m%dT%H%M%S}.json").write_text(json.dumps(original))
    api('/api/v1/workflows/'+original['id'],'PUT',
        {k:revised[k] for k in ('name','nodes','connections')} |
        {'settings':{k:v for k,v in revised['settings'].items() if k!='availableInMCP'}})
    after = api('/api/v1/workflows/'+original['id'])
    if original['active'] and after['versionId']!=after.get('activeVersionId'):
        api('/api/v1/workflows/'+original['id']+'/activate','POST',{})
        after=api('/api/v1/workflows/'+original['id'])
    assert len(after['nodes'])==len(revised['nodes'])
    for intended in revised['nodes']:
        actual=next(n for n in after['nodes'] if n['name']==intended['name'])
        for key in ('type','typeVersion','parameters'):
            assert actual[key]==intended[key], (intended['name'],key)
    assert after['connections']==revised['connections']
    assert not original['active'] or (after['active'] and after['versionId']==after['activeVersionId'])
    print(json.dumps({'saved':after['id'],'version':after['versionId'],'active':after['active']}))

def test_gate():
    # Run only the new verification block with mocked GHL reads; no external I/O.
    harness = r"""
const AsyncFunction=Object.getPrototypeOf(async function(){}).constructor;
const gate=GATE;
const prefix=`const incoming=$json.incoming||{},customData={},calendar={},startRaw=incoming.startTime||'',contactId='test-contact',baseUrl='https://example.invalid',headers={},sync={},textLines=[];`;
async function run(incoming,response,fail=false){
 const fn=new AsyncFunction('$json',prefix+gate+'return [{json:{sync,passed:true}}];');
 return (await fn.call({helpers:{httpRequest:async()=>{if(fail)throw Error('network');return response;}}},{incoming}))[0].json;
}
(async()=>{
 const event={id:'a1',calendarId:'SrtXcFVyea7pFl3nTiIK',contactId:'test-contact',startTime:'2026-10-13T17:00:00Z'};
 const tests=[
 ['click cannot qualify',{}, {events:[event]},false,false],
 ['matching appointment ID',{appointmentId:'a1'}, {events:[event]},false,true],
 ['matching booking start',{startTime:event.startTime},{events:[event]},false,true],
 ['wrong calendar',{appointmentId:'a1'},{events:[{...event,calendarId:'other'}]},false,false],
 ['canceled',{appointmentId:'a1'},{events:[{...event,status:'cancelled'}]},false,false],
 ['lookup failure',{appointmentId:'a1'},{},true,false],
 ['duplicate match',{appointmentId:'a1'},{events:[event,event]},false,false],
 ['Book a demo qualifies',{appointmentId:'a1'},{events:[{...event,calendarId:'WS6lacfQK2XOhqN7mRaF'}]},false,true]
 ];
 for(const [name,input,response,fail,expected] of tests){const got=await run(input,response,fail);if(!!got.passed!==expected)throw Error(name);console.log('PASS '+name);}
})().catch(e=>{console.error(e);process.exit(1)});
""".replace('const gate=GATE;', 'const gate='+json.dumps(GATE)+';')
    subprocess.run(['node','-'],input=harness,text=True,encoding='utf-8',check=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');args=p.parse_args()
    test_gate()
    w=api('/api/v1/workflows/lQTW0QPwBcf3o7j8');rev=copy.deepcopy(w)
    n=next(n for n in rev['nodes'] if n['name']=='Build Slack Payload')
    code=n['parameters']['jsCode']
    if 'VERIFIED_BOOKING_GATE_V1' not in code:
        anchor='if (originatingSdrId) {'
        assert code.count(anchor)==1
        code=code.replace(anchor,GATE+'\n'+anchor,1)
        code=code.replace("body: { tags: ['SQL'] }", "body: { tags: ['SQL', 'meeting booked'] }")
        n['parameters']['jsCode']=code
    parse(code)
    print('SQL writer parsed; appointment gate precedes all CRM writes.')
    click=api('/api/v1/workflows/1diZyFmTqWQUEny3');crev=copy.deepcopy(click)
    tag=next(n for n in crev['nodes'] if n['name']=='Apply MQL Tag')
    tag['parameters']['jsonBody']='{"tags":["mql"]}'
    tag['parameters']['url']='=https://services.leadconnectorhq.com/contacts/{{$json.contact_id}}/tags'
    for h in tag['parameters']['headerParameters']['parameters']:
        if h['name']=='Authorization':h['value']="=Bearer {{$('Config').first().json.ghlApiKey}}"
    # Preserve contact identity across the UTM HTTP response, then tag and respond once.
    tag['parameters']['url']="=https://services.leadconnectorhq.com/contacts/{{$('Process Click').item.json.contact_id}}/tags"
    crev['connections']['Has Mapped UTM?']['main'][0]=[{'node':'Update Contact Last UTM Fields','type':'main','index':0}]
    crev['connections']['Update Contact Last UTM Fields']={'main':[[{'node':'Apply MQL Tag','type':'main','index':0}]]}
    print('Click path: known click -> UTM update -> MQL only -> one response.')
    if args.apply:
        # Remove false booking signal first, then harden the actual SQL writer.
        if crev!=click:save(click,crev)
        if rev!=w:save(w,rev)
