import json, urllib.request, os, tempfile

tmp = os.environ.get('TEMP', r'C:\Users\edmon\AppData\Local\Temp')

# Read API key
key0 = open(r'C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\.env').read()
for line in key0.splitlines():
    if line.startswith('N8N_API_KEY_LT'):
        token = line.split('=', 1)[1].strip()
        break

# Read modified JS
with open(os.path.join(tmp, 'follower-dm-fixed.js'), 'r', encoding='utf-8') as f:
    js = f.read()

# Get the current workflow to find all nodes
req = urllib.request.Request('https://automations.livetransparent.com/api/v1/workflows/pq7XVajNFnnwMUTr')
req.add_header('X-N8N-API-KEY', token)
resp = urllib.request.urlopen(req)
wf = json.loads(resp.read().decode())

# Modify the Code node's jsCode
for n in wf['nodes']:
    if n['name'] == 'Process LinkedIn Followers':
        n['parameters']['jsCode'] = js
        break

# Keep only required fields
wf = {
    'name': wf.get('name', ''),
    'nodes': wf.get('nodes', []),
    'connections': wf.get('connections', {}),
    'settings': {},
}

body = json.dumps(wf).encode()
req2 = urllib.request.Request('https://automations.livetransparent.com/api/v1/workflows/pq7XVajNFnnwMUTr', data=body, method='PUT')
req2.add_header('X-N8N-API-KEY', token)
req2.add_header('Content-Type', 'application/json')

try:
    resp2 = urllib.request.urlopen(req2, timeout=60)
    result = json.loads(resp2.read().decode())
    print('Updated successfully')
    print('Node count:', len(result.get('nodes', [])))
except urllib.error.HTTPError as e:
    err = e.read().decode()[:1000]
    print('Error:', e.code, err)
    # Show keys in body
    print('Body keys:', list(wf.keys()))
