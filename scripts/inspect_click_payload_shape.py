"""Print only click identity envelope fields (never headers/config)."""
import json
from repair_v1_facts_sql import api
d=api('/api/v1/executions/1137890?includeData=true')
raw=d['data']['resultData']['runData']['Webhook'][0]['data']['main'][0][0]['json']
b=raw['body']
for attr in ('attributionSource','lastAttributionSource'):
    print(json.dumps({attr:b.get('contact',{}).get(attr,{})}))
for k in ('customData','triggerData','workflow','attributionSource','contact'):
    v=b.get(k)
    if k in ('contact','attributionSource') and isinstance(v,dict):
        print(k,'keys:',list(v))
        print(json.dumps({k:{x:v.get(x) for x in ('medium','utmSource','utmMedium','utmCampaign','url','pageUrl') if x in v}}))
    else:print(json.dumps({k:v}))
