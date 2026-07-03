import json, os, urllib.request

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4NjFmYjY1NS1iMTc2LTRkNjMtYTRlZC0zY2M2NmUyNzk2NDIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiOTEwOThlZTEtZWI4NS00NjAwLTg5NmYtMGM3ZDMwOTg4YTg1IiwiaWF0IjoxNzc3NDIwMDk5fQ.6ZVb5kKoNltBUFYHoS2x4PQABycoJDvdmN9Nrfx-Z7U"
BASE = "https://automations.livetransparent.com/api/v1"
WF_ID = "q7qbjjm6185WeukV"

req = urllib.request.Request(f"{BASE}/workflows/{WF_ID}", headers={"X-N8N-API-KEY": API_KEY})
wf = json.loads(urllib.request.urlopen(req).read())

for n in wf["nodes"]:
    if n["name"] == "Create Google Sheet":
        n["parameters"]["jsCode"] = """var allItems = $("Parse CSV").all();
var rows = [];
var rawHeaders = null;
for (var i = 0; i < allItems.length; i++) {
  var raw = allItems[i].json.raw_json;
  if (raw) {
    try {
      var parsed = JSON.parse(raw);
      if (!rawHeaders) { rawHeaders = Object.keys(parsed); }
      var row = [];
      for (var h = 0; h < rawHeaders.length; h++) { row.push(parsed[rawHeaders[h]] || ''); }
      rows.push(row);
    } catch(e) { }
  }
}
if (!rawHeaders || rows.length === 0) throw new Error('No data to write to sheet');

var poolType = 'Brands';
if (rows.length > 0) {
  var tagsIdx = rawHeaders.indexOf('Tags');
  if (tagsIdx >= 0 && rows[0][tagsIdx] && rows[0][tagsIdx].indexOf('dispensaries_pool') >= 0) { poolType = 'Dispensaries'; }
}
var sheetTitle = 'Emerging ' + poolType + ' Pool';

var createResp = await this.helpers.httpRequestWithAuthentication('googleSheetsOAuth2Api', {
  method: 'POST',
  url: 'https://sheets.googleapis.com/v4/spreadsheets',
  body: { properties: { title: sheetTitle } }
});

var spreadsheetId = createResp.spreadsheetId;
var values = [rawHeaders];
for (var r = 0; r < rows.length; r++) { values.push(rows[r]); }

await this.helpers.httpRequestWithAuthentication('googleSheetsOAuth2Api', {
  method: 'PUT',
  url: 'https://sheets.googleapis.com/v4/spreadsheets/' + spreadsheetId + '/values/Sheet1!A1?valueInputOption=USER_ENTERED',
  body: { values: values }
});

return [{ json: {
  spreadsheetUrl: createResp.spreadsheetUrl,
  spreadsheetId: spreadsheetId,
  rowsImported: rows.length,
  poolType: poolType,
  sheetTitle: sheetTitle
}}];"""

for f in ["versionId", "tags", "active", "createdAt", "updatedAt", "id"]:
    wf.pop(f, None)

body = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf["settings"],
    "description": wf.get("description", "")
}

data = json.dumps(body).encode("utf-8")
req = urllib.request.Request(f"{BASE}/workflows/{WF_ID}", data=data, method="PUT", headers={
    "X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"
})
resp = json.loads(urllib.request.urlopen(req).read())
print(f"Updated: {resp['name']}")

# Verify
req = urllib.request.Request(f"{BASE}/workflows/{WF_ID}", headers={"X-N8N-API-KEY": API_KEY})
wf2 = json.loads(urllib.request.urlopen(req).read())
for n in wf2["nodes"]:
    if n["name"] == "Create Google Sheet":
        code = n["parameters"].get("jsCode", "")
        has_auth = "httpRequestWithAuthentication" in code
        has_data_ref = "$('Parse CSV').all()" in code
        print(f"Create Google Sheet: httpRequestWithAuthentication={has_auth}, referencesParseCSV={has_data_ref}")
