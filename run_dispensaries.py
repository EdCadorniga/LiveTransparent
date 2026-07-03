import json, os, urllib.request

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4NjFmYjY1NS1iMTc2LTRkNjMtYTRlZC0zY2M2NmUyNzk2NDIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiOTEwOThlZTEtZWI4NS00NjAwLTg5NmYtMGM3ZDMwOTg4YTg1IiwiaWF0IjoxNzc3NDIwMDk5fQ.6ZVb5kKoNltBUFYHoS2x4PQABycoJDvdmN9Nrfx-Z7U"
BASE = "https://automations.livetransparent.com/api/v1"
WF_ID = "q7qbjjm6185WeukV"

req = urllib.request.Request(f"{BASE}/workflows/{WF_ID}", headers={"X-N8N-API-KEY": API_KEY})
wf = json.loads(urllib.request.urlopen(req).read())

for n in wf["nodes"]:
    if n["name"] == "Read File":
        n["parameters"]["fileSelector"] = "/home/node/.n8n-files/GHL_Ready_Dispensaries.csv"

wf["name"] = "LT - Dispensaries Pool to Postgres + Sheets"

for f in ["versionId", "tags", "active", "createdAt", "updatedAt", "id"]:
    wf.pop(f, None)

body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"], "settings": wf["settings"], "description": wf.get("description", "")}
data = json.dumps(body).encode("utf-8")
req = urllib.request.Request(f"{BASE}/workflows/{WF_ID}", data=data, method="PUT", headers={"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"})
resp = json.loads(urllib.request.urlopen(req).read())
print(f"Renamed and updated: {resp['name']}")
print("Read File -> Dispensaries")

req2 = urllib.request.Request(f"{BASE}/workflows/{WF_ID}/execute", method="POST", headers={"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"})
exec_resp = json.loads(urllib.request.urlopen(req2).read())
print(f"Execution started: ID {exec_resp.get('executionId', exec_resp)}")
