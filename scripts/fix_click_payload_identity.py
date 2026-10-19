"""Handle observed GHL nested click envelope and contact-bound tracking URL.

Link UTMs come from a verified current registry snapshot, not contact acquisition.
No event replay is performed by this script.
"""
import copy
import json
import re
import subprocess
import urllib.parse
import urllib.request
from repair_v1_facts_sql import api, ROOT
from fix_verified_booking_gate import save,parse

HELPER=r"""
function trackingIdentity(envelope,contactId){
 const url=envelope.contact?.lastAttributionSource?.url||'';
 try{const u=new URL(url);if(!['services.leadconnectorhq.com','msgsndr.com','services.msgsndr.com'].includes(u.hostname))return {};
   const match=u.pathname.match(/[/]links[/]r[/]2[/]([^/]+)|[/]r[/]2[/]([^/]+)/);if(!match)return {};
   const token=match[1]||match[2];const decoded=JSON.parse(Buffer.from(token.split('.')[1],'base64url').toString('utf8'));
   if(decoded.contact_id!==contactId)return {};return decoded;
 }catch{return {};}
}
"""

if __name__=='__main__':
    env=dict(line.split('=',1) for line in (ROOT/'.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
    key=env['GHL_PIT'].strip().strip('"').strip("'")
    request=urllib.request.Request('https://services.leadconnectorhq.com/links/?locationId=Zwz4relUXVPxx8uohnjV',headers={'Authorization':'Bearer '+key,'Version':'2021-07-28','User-Agent':'Mozilla/5.0','Accept':'application/json'})
    with urllib.request.urlopen(request,timeout=30) as response:links=json.load(response)['links']
    w=api('/api/v1/workflows/1diZyFmTqWQUEny3');rev=copy.deepcopy(w)
    node=next(n for n in rev['nodes'] if n['name']=='Process Click');code=node['parameters']['jsCode']
    ids=set(re.findall(r"'([A-Za-z0-9]{20})':",code))
    registry={}
    for link in links:
        if link['id'] not in ids:continue
        url=link.get('redirectTo') or link.get('url') or ''
        qs=urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
        registry[link['id']]={'name':link['name'],'utm_source':qs.get('utm_source',[''])[0],
            'utm_medium':qs.get('utm_medium',[''])[0],'utm_campaign':qs.get('utm_campaign',[''])[0]}
    cfg=next(n for n in rev['nodes'] if n['name']=='Config')
    vals=cfg['parameters']['assignments']['assignments']
    assignment=next((a for a in vals if a['name']=='linkRegistryJson'),None)
    if assignment:assignment['value']=json.dumps(registry)
    else:vals.append({'id':'registry','name':'linkRegistryJson','type':'string','value':json.dumps(registry)})
    if 'function trackingIdentity' not in code:
        code=HELPER+'\n'+code
        code=code.replace("const raw = (j.body && typeof j.body === 'object') ? j.body : j;", "const envelope = (j.body && typeof j.body === 'object') ? j.body : j;\n    const raw = {...envelope,...(envelope.customData || {})};")
        code=code.replace("const contactId = String(raw.contact_id || '');", "const contactId = String(raw.contact_id || '').trim();\n    if(!/^[a-zA-Z0-9]{15,30}$/.test(contactId)){out.push({json:{ok:false,error:'missing_contact_id'}});continue;}")
        code=code.replace("const linkId = String(raw.link_id || '');", "const recovered = trackingIdentity(envelope,contactId);\n    const linkId = String(raw.link_id || recovered.link_id || '').trim();")
        code=code.replace('const m = MAP[linkId];', "let m = MAP[linkId];\n    const registry = JSON.parse(cfgValues.linkRegistryJson || '{}');\n    const meta=registry[linkId];\n    if(m && meta)m=[m[0],meta.utm_source || m[1],meta.utm_campaign || m[2],meta.utm_medium || m[3] || 'email'];")
        node['parameters']['jsCode']=code
    parse(code)
    # Exact identity helper checks without GHL/DB I/O.
    harness=HELPER+r"""
const token=(contact,link)=>'header.'+Buffer.from(JSON.stringify({contact_id:contact,link_id:link})).toString('base64url')+'.signature';
const good={contact:{lastAttributionSource:{url:'https://services.leadconnectorhq.com/links/r/2/'+token('contact1','link1')}}};
if(trackingIdentity(good,'contact1').link_id!=='link1')throw Error('valid identity');
if(trackingIdentity(good,'other').link_id)throw Error('foreign contact');
if(trackingIdentity({contact:{lastAttributionSource:{url:'https://evil.invalid/links/r/2/'+token('contact1','link1')}}},'contact1').link_id)throw Error('foreign host');
console.log('PASS valid contact-bound identity, reject mismatched contact and foreign host');
"""
    subprocess.run(['node','-'],input=harness,text=True,encoding='utf-8',check=True)
    print('Known booking links in registry:',len(registry))
    if rev!=w:save(w,rev)
