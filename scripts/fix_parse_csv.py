import json, os, urllib.request

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4NjFmYjY1NS1iMTc2LTRkNjMtYTRlZC0zY2M2NmUyNzk2NDIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiOTEwOThlZTEtZWI4NS00NjAwLTg5NmYtMGM3ZDMwOTg4YTg1IiwiaWF0IjoxNzc3NDIwMDk5fQ.6ZVb5kKoNltBUFYHoS2x4PQABycoJDvdmN9Nrfx-Z7U"
BASE = "https://automations.livetransparent.com/api/v1"

# GET current workflow
req = urllib.request.Request(f"{BASE}/workflows/q7qbjjm6185WeukV", headers={"X-N8N-API-KEY": API_KEY})
wf = json.loads(urllib.request.urlopen(req).read())

# Fix Parse CSV node
for n in wf["nodes"]:
    if n["name"] == "Parse CSV":
        n["parameters"]["jsCode"] = """var buffer = await this.helpers.getBinaryDataBuffer(0, 'data');
var csvContent = buffer.toString('utf-8');
var lines = csvContent.split('\\n').filter(function(l) { return l.trim(); });
var headers = parseLine(lines[0]);
var results = [];
for (var i = 1; i < lines.length; i++) {
  var vals = parseLine(lines[i]);
  var row = {};
  var raw = {};
  for (var c = 0; c < headers.length; c++) { raw[headers[c]] = vals[c] || ''; }
  row.raw_json = JSON.stringify(raw);
  row.emerald_contact_id = raw.Em_Emerald_Contact_ID || null;
  row.first_name = raw['First Name'] || '';
  row.last_name = raw['Last Name'] || '';
  row.primary_email = raw.Email || '';
  row.primary_phone = raw.Phone || '';
  row.company_name = raw['Company Name'] || '';
  row.tags = raw.Tags || '';
  row.source_list = row.tags.indexOf('dispensaries_pool') >= 0 ? 'dispensaries' : 'brands';
  row.ghl_contact_id = null;
  row.ghl_opportunity_id = null;
  results.push({ json: row });
}
return results;
function parseLine(str) {
  var result = [];
  var cur = '';
  var inQ = false;
  for (var i = 0; i < str.length; i++) {
    var ch = str[i];
    if (ch === '\"') {
      if (inQ && i + 1 < str.length && str[i + 1] === '\"') { cur += '\"'; i++; }
      else { inQ = !inQ; }
    } else if (ch === ',' && !inQ) { result.push(cur); cur = ''; }
    else { cur += ch; }
  }
  result.push(cur);
  return result;
}"""
        # Remove nested parameters if present
        if "parameters" in n["parameters"] and isinstance(n["parameters"]["parameters"], dict):
            del n["parameters"]["parameters"]

# Remove read-only fields
for f in ["versionId", "tags", "active", "createdAt", "updatedAt", "id"]:
    wf.pop(f, None)

# Build PUT body
body = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf["settings"],
    "description": wf.get("description", "")
}

# PUT
data = json.dumps(body).encode("utf-8")
req = urllib.request.Request(f"{BASE}/workflows/q7qbjjm6185WeukV", data=data, method="PUT", headers={
    "X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"
})
resp = json.loads(urllib.request.urlopen(req).read())
print(f"Updated: {resp['name']} at {resp['updatedAt']}")

# Verify
req = urllib.request.Request(f"{BASE}/workflows/q7qbjjm6185WeukV", headers={"X-N8N-API-KEY": API_KEY})
wf2 = json.loads(urllib.request.urlopen(req).read())
for n in wf2["nodes"]:
    if n["name"] == "Parse CSV":
        has_code = "jsCode" in n["parameters"]
        has_nested = "parameters" in n["parameters"] and isinstance(n["parameters"]["parameters"], dict)
        print(f"Parse CSV: has jsCode={has_code}, has nested params={has_nested}")
        print(f"jsCode starts with: {n['parameters'].get('jsCode', '')[:80]}...")
