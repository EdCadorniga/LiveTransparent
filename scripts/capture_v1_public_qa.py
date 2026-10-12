"""Capture public reporting payloads for local QA (no credentials)."""
import concurrent.futures
import json
import pathlib
import urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
def capture(name,path):
    url='https://reports.livetransparent.com'+path+'?from=2026-10-04&to=2026-10-10'
    with urllib.request.urlopen(url,timeout=300) as r:
        data=json.load(r)
    (ROOT/'local-scripts'/('v1-band-qa-'+name+'.json')).write_text(json.dumps(data),encoding='utf-8')
    print(name,json.dumps({k:v for k,v in data.items() if k in ('campaignChannelBreakdown','leadSourceBreakdown','opportunitySourceBreakdown','sdrOutputs')}))
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        jobs=[ex.submit(capture,*pair) for pair in [('summary','/api/report/executive/summary'),('channels','/api/report/executive/campaign-channels'),('facts','/api/report/executive-v1/facts')]]
        for job in jobs: job.result()
