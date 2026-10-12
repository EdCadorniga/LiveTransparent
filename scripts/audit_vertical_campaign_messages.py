"""Read supported GHL Email message exports; keep only reporting evidence."""
import json
import pathlib
import time
import urllib.parse
from audit_vertical_campaign_contacts import ghl, ROOT, LOCATION

if __name__ == '__main__':
    import sys
    if '--probe' in sys.argv:
        r = ghl('/conversations/messages/VgpqYChJRAkd9ee4v8D3')
        print(json.dumps({'keys':list(r),'status':r.get('status'),'messageType':r.get('messageType'),
            'source':r.get('source'),'metaKeys':list((r.get('meta') or {}).keys()),
            'workflowId':r.get('workflowId'),'nestedMessageKeys':list((r.get('message') or {}).keys())}))
        raise SystemExit(0)
    q = {'locationId':LOCATION,'channel':'Email','limit':1000,'sortBy':'createdAt','sortOrder':'asc',
         'startDate':'2026-10-04T07:00:00.000Z','endDate':'2026-10-11T06:59:59.999Z'}
    rows,seen = [],set()
    for page in range(200):
        r = ghl('/conversations/messages/export?'+urllib.parse.urlencode(q))
        items = r.get('messages',[])
        for m in items:
            if m.get('id') in seen:
                raise RuntimeError('Export repeated message ID')
            seen.add(m.get('id'))
            meta = m.get('meta') or {}
            email = meta.get('email') or {}
            rows.append({k:m.get(k) for k in ('id','contactId','conversationId','dateAdded','direction','status','messageType','source','workflowId')} |
                {'metaKeys':list(meta),'emailKeys':list(email), 'emailWorkflowId':email.get('workflowId')})
        print(json.dumps({'page':page+1,'pageRows':len(items),'cumulative':len(rows),'reportedTotal':r.get('total')}),flush=True)
        if not r.get('nextCursor'):
            break
        q['cursor'] = r['nextCursor']
        time.sleep(.2)
    else:
        raise RuntimeError('Export page bound reached')
    destination = ROOT/'local-scripts/vertical-email-message-export-20261013.json'
    destination.write_text(json.dumps({'from':q['startDate'],'to':q['endDate'],'complete':True,'rows':rows},indent=2),encoding='utf-8')
    from collections import Counter
    print(json.dumps({'total':len(rows),'sources':dict(Counter(str(r['source']) for r in rows)),
      'outboundStatuses':dict(Counter(str(r['status']) for r in rows if r['direction']=='outbound')),
      'workflowLinked':sum(bool(r.get('workflowId') or r.get('emailWorkflowId')) for r in rows),'artifact':str(destination)}))
