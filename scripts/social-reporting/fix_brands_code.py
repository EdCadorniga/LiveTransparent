import json, urllib.request

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4NjFmYjY1NS1iMTc2LTRkNjMtYTRlZC0zY2M2NmUyNzk2NDIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiOTEwOThlZTEtZWI4NS00NjAwLTg5NmYtMGM3ZDMwOTg4YTg1IiwiaWF0IjoxNzc3NDIwMDk5fQ.6ZVb5kKoNltBUFYHoS2x4PQABycoJDvdmN9Nrfx-Z7U"
BASE = "https://automations.livetransparent.com/api/v1"
WF_BRANDS = "fg06Ip8wT3EapfdD"

req = urllib.request.Request(f"{BASE}/workflows/{WF_BRANDS}", headers={"X-N8N-API-KEY": API_KEY})
wf = json.loads(urllib.request.urlopen(req).read())

for n in wf["nodes"]:
    if n["name"] == "Parse CSV":
        n["parameters"]["jsCode"] = (
            "var buffer = await this.helpers.getBinaryDataBuffer(0, 'data');\n"
            + "var csvContent = buffer.toString('utf-8');\n"
            + "var lines = csvContent.split(/\\r?\\n/).filter(function(l) { return l.trim(); });\n"
            + "var headers = parseLine(lines[0]);\n"
            + "var results = [];\n"
            + "for (var i = 1; i < lines.length; i++) {\n"
            + "  var vals = parseLine(lines[i]);\n"
            + "  var row = {};\n"
            + "  var raw = {};\n"
            + "  for (var c = 0; c < headers.length; c++) { raw[headers[c]] = vals[c] || ''; }\n"
            + "  row.raw_json = JSON.stringify(raw);\n"
            + "  row.emerald_contact_id = raw.Em_Emerald_Contact_ID || null;\n"
            + "  row.first_name = raw['First Name'] || '';\n"
            + "  row.last_name = raw['Last Name'] || '';\n"
            + "  row.primary_email = raw.Email || '';\n"
            + "  row.primary_phone = raw.Phone || '';\n"
            + "  row.company_name = raw['Company Name'] || '';\n"
            + "  row.tags = raw.Tags || '';\n"
            + "  row.source_list = 'brands';\n"
            + "  row.ghl_contact_id = null;\n"
            + "  row.ghl_opportunity_id = null;\n"
            + "  results.push({ json: row });\n"
            + "}\n"
            + "return results;\n"
            + "function parseLine(str) {\n"
            + "  var result = [];\n"
            + "  var cur = '';\n"
            + "  var inQ = false;\n"
            + "  for (var i = 0; i < str.length; i++) {\n"
            + "    var ch = str[i];\n"
            + "    if (ch === '\"') {\n"
            + "      if (inQ && i + 1 < str.length && str[i + 1] === '\"') { cur += '\"'; i++; }\n"
            + "      else { inQ = !inQ; }\n"
            + "    } else if (ch === ',' && !inQ) { result.push(cur); cur = ''; }\n"
            + "    else { cur += ch; }\n"
            + "  }\n"
            + "  result.push(cur);\n"
            + "  return result;\n"
            + "}"
        )

for f in ["versionId", "tags", "active", "createdAt", "updatedAt", "id"]:
    wf.pop(f, None)

body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"], "settings": wf["settings"], "description": wf.get("description", "")}
data = json.dumps(body).encode("utf-8")
req = urllib.request.Request(f"{BASE}/workflows/{WF_BRANDS}", data=data, method="PUT", headers={"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"})
resp = json.loads(urllib.request.urlopen(req).read())
print(f"Fixed: {resp['name']}")

# Verify
req2 = urllib.request.Request(f"{BASE}/workflows/{WF_BRANDS}", headers={"X-N8N-API-KEY": API_KEY})
wf2 = json.loads(urllib.request.urlopen(req2).read())
for n in wf2["nodes"]:
    if n["name"] == "Parse CSV":
        code = n["parameters"].get("jsCode", "")
        print(f"jsCode starts: {code[:80]}...")
        print(f"Uses regex split: {r'/\\r?\\n/' in code}")
        print(f"No raw newlines in split: {not chr(10) in code.split('split(')[1].split(')')[0] if 'split(' in code else 'N/A'}")
