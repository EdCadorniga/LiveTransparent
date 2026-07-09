import json, os

# Read from the workflow file or use the API directly
# Let me just query the workflow and dump config info
import subprocess, re

# Get the workflow
env_key = ""
with open(r'C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\.env', 'r') as f:
    for line in f:
        if line.startswith('N8N_API_KEY_LT='):
            env_key = line.split('=', 1)[1].strip()
            break

import urllib.request
req = urllib.request.Request(
    'https://automations.livetransparent.com/api/v1/workflows/8UXlpoMJnQ229AuG',
    headers={'X-N8N-API-KEY': env_key}
)
with urllib.request.urlopen(req) as resp:
    w = json.loads(resp.read())

# Find the Config node
for n in w['activeVersion']['nodes']:
    if 'Config' in n['name']:
        print(f"Node: {n['name']} ({n['type']})")
        params = n['parameters']
        if 'assignments' in params and 'assignments' in params['assignments']:
            for a in params['assignments']['assignments']:
                name = a.get('name', '?')
                value = str(a.get('value', ''))
                if len(value) > 80:
                    value = value[:77] + '...'
                print(f"  {name}: {value}")
    elif 'Setting' in n['name'] or 'setting' in n['name']:
        print(f"Node: {n['name']} ({n['type']})")
        if 'parameters' in n:
            print(f"  {json.dumps(n['parameters'], indent=2)[:500]}")
