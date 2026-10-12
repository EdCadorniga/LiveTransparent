"""Read-only GHL sender/entry audit grounded in captured enrollment IDs."""
import argparse
import json
import pathlib
import time
import urllib.request
import urllib.error
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCATION = 'Zwz4relUXVPxx8uohnjV'
VERTICAL_FIELD = 'ODs8fBt5te5HEfSJ91pY'
FIELDS = {
    'Alcohol': ('AIzg8FR3PEDr7PSGMuXN','alcohol'),
    'Cannabis Brands': ('qoQxuEiX5kwKvvrOvDVm','cannabis'),
    'Cannabis Dispensaries': ('wR5Az25TIyETr5E3NwoN','cannabis_dispensaries'),
    'Crypto': ('UKLWo0PbkyZh34XExfHc','crypto'),
    'Gambling': ('sBbIGke6cvkCTpW9n1yQ','gambling'),
    'Mushroom': ('IJ1yrUihuKD7DkLgWHYM','mushroom'),
    'Nicotine': ('oFHCH0QL8wsrkHiXKE3F','nicotine'),
    'Peptides': ('ADJQKqlJzjhnGiCpQQgg','peptides'),
}

def ghl(path, body=None):
    env = {}
    for line in (ROOT/'.env').read_text(encoding='utf-8').splitlines():
        if '=' in line and not line.startswith('#'):
            k,v = line.split('=',1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    headers = {'Authorization':'Bearer '+env['GHL_PIT'],'Version':'2021-07-28',
               'User-Agent':'Mozilla/5.0','Accept':'application/json','Content-Type':'application/json'}
    for attempt in range(4):
        try:
            req = urllib.request.Request('https://services.leadconnectorhq.com'+path,
                data=json.dumps(body).encode() if body is not None else None,headers=headers)
            with urllib.request.urlopen(req,timeout=45) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(2*(attempt+1)); continue
            detail = json.loads(e.read().decode()) if e.code in (400,422) else {}
            raise RuntimeError('GHL HTTP '+str(e.code)+' '+str(detail.get('message',''))[:500]) from None
    raise RuntimeError('GHL retry bound')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--probe',action='store_true')
    parser.add_argument('--audit',action='store_true')
    args = parser.parse_args()
    artifact = ROOT/'local-scripts/vertical-enrollment-audit-20261013.json'
    audit = json.loads(artifact.read_text(encoding='utf-8'))
    wanted = {r['contactId'] for w in audit['workflows'] for r in w['rows']}
    if args.probe:
        test_ids = sorted(wanted)[:5]
        result = ghl('/contacts/search',{'locationId':LOCATION,'page':1,'pageLimit':100,
            'filters':[{'field':'id','operator':'eq','value':test_ids}]})
        returned = {c['id'] for c in result.get('contacts',[])}
        print(json.dumps({'idFilterVerified':returned==set(test_ids),'wanted':len(test_ids),
                          'returned':len(returned),'keys':list(result)}))
        raise SystemExit(0)
    contacts = {}
    for start in range(0,len(wanted),100):
        batch = sorted(wanted)[start:start+100]
        result = ghl('/contacts/search',{'locationId':LOCATION,'page':1,'pageLimit':100,
            'filters':[{'field':'id','operator':'eq','value':batch}]})
        returned = {c['id']:c for c in result.get('contacts',[])}
        if not set(returned).issubset(set(batch)):
            raise RuntimeError('Contact filter returned out-of-scope records')
        contacts.update(returned)
        time.sleep(.3)
    output = {'capturedAt':audit['capturedAt'],'contactCount':len(contacts),'missingContacts':sorted(wanted-set(contacts)),'workflows':[]}
    for w in audit['workflows']:
        sender_field,slug = FIELDS[w['label']]
        entry_tag = 'lt_campaign_'+slug+'_brands_oct_2026_enroll'
        populations = {}
        for r in w['rows']:
            populations.setdefault(r['contactId'],[]).append(r)
        rows = []
        for cid,entries in populations.items():
            c = contacts.get(cid,{})
            cf = {f['id']:f.get('value') for f in c.get('customFields',[])}
            sender = str(cf.get(sender_field) or '').strip()
            tags = c.get('tags') or []
            rows.append({'contactId':cid,'vertical':cf.get(VERTICAL_FIELD),'sender':sender,
                'senderValid':sender in ['cameron@livetransparent.'+x for x in ('com','co','agency','org')],
                'hasEntryTag':entry_tag in tags,'tags':tags,'dnd':c.get('dnd'),'dndSettings':c.get('dndSettings'),
                'hasEmail':bool(c.get('email')),'hasPhone':bool(c.get('phone')),
                'active':any(r['status'] not in ('finished','removed','stopped') for r in entries),
                'entries':entries})
        output['workflows'].append({'id':w['id'],'label':w['label'],'senderField':sender_field,'entryTag':entry_tag,'contacts':rows})
        print(json.dumps({'label':w['label'],'contacts':len(rows),'active':sum(r['active'] for r in rows),
            'missingSender':sum(not r['sender'] for r in rows),'invalidSender':sum(not r['senderValid'] for r in rows),
            'missingEntryTag':sum(not r['hasEntryTag'] for r in rows),
            'inactiveOnly':[r for r in rows if not r['active']],
            'senderCounts':dict(Counter(r['sender'] for r in rows))}))
    destination = artifact.with_name('vertical-campaign-contact-audit-20261013.json')
    destination.write_text(json.dumps(output,indent=2),encoding='utf-8')
    print(json.dumps({'missingContacts':output['missingContacts'],'artifact':str(destination)}))
