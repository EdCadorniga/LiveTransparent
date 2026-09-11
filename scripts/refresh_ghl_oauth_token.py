"""Refresh the GHL OAuth token used by the LinkedIn conversation backfill."""
import json
import os
import paramiko
import requests
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW_ID = "kqIi8i1RjFAZKrK3"
N8N_BASE = "https://automations.livetransparent.com/api/v1"
GHL_TOKEN_URL = "https://services.leadconnectorhq.com/oauth/token"


def load_env():
    values = {}
    with open(os.path.join(ROOT, ".env"), encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip().strip('"').strip("'")
    return values


ENV = load_env()


def ssh_client():
    key_path = os.path.expandvars(os.path.expanduser(ENV.get("VPS_SSH_KEY_PATH", "")))
    key = None
    for key_type in (paramiko.Ed25519Key, paramiko.RSAKey, paramiko.ECDSAKey):
        try:
            key = key_type.from_private_key_file(key_path)
            break
        except Exception:
            pass
    if key is None:
        raise SystemExit("SSH key load failed")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ENV.get("VPS_HOST") or ENV.get("VPS_HOSTNAME"), username=ENV.get("VPS_USER"), pkey=key,
                   timeout=20, auth_timeout=20, banner_timeout=20, look_for_keys=False, allow_agent=False)
    return client


def psql(sql):
    client = ssh_client()
    try:
        command = "docker exec -i postgres-uokgs4c04ko0s4scccg40cgg psql -U postgres -d postgres -v ON_ERROR_STOP=1 -X -q -t -A"
        stdin, stdout, stderr = client.exec_command(command, timeout=180)
        stdin.write(sql)
        stdin.channel.shutdown_write()
        output = stdout.read().decode(errors="replace").strip()
        error = stderr.read().decode(errors="replace").strip()
        if error and "NOTICE" not in error:
            raise RuntimeError(error[:2000])
        return output
    finally:
        client.close()


def sql_literal(value):
    return "NULL" if value is None else "'" + str(value).replace("'", "''") + "'"


api_key = ENV.get("N8N_API_KEY_LT") or ENV.get("n8n_API_KEY")
request = urllib.request.Request(f"{N8N_BASE}/workflows/{WORKFLOW_ID}", headers={"X-N8N-API-KEY": api_key, "Accept": "application/json"})
with urllib.request.urlopen(request, timeout=120) as response:
    workflow = json.loads(response.read().decode())
exchange = next(node for node in workflow["nodes"] if node["name"] == "Exchange OAuth Token")
params = exchange["parameters"]["bodyParameters"]["parameters"]
oauth_values = {item["name"]: item["value"] for item in params}
client_id = oauth_values["client_id"]
client_secret = oauth_values["client_secret"]

row = json.loads(psql("SELECT row_to_json(x)::text FROM (SELECT refresh_token, company_id, location_id, user_type FROM ghl_oauth_tokens WHERE active IS TRUE AND refresh_token <> '' ORDER BY received_at DESC NULLS LAST LIMIT 1) x;"))
if not row.get("refresh_token"):
    raise SystemExit("No active GHL refresh token")

response = requests.post(GHL_TOKEN_URL, data={
    "grant_type": "refresh_token",
    "client_id": client_id,
    "client_secret": client_secret,
    "refresh_token": row["refresh_token"],
}, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"}, timeout=30)
if response.status_code >= 400:
    raise SystemExit(f"GHL refresh failed status={response.status_code} body={response.text[:500]}")
token = response.json()
if not token.get("access_token"):
    raise SystemExit("Refresh response did not include access_token")

company_id = token.get("companyId") or row.get("company_id") or "7vMmm4at5OrjQplRN3EO"
location_id = token.get("locationId") or row.get("location_id") or "Zwz4relUXVPxx8uohnjV"
user_type = token.get("userType") or row.get("user_type") or "Company"
scope = token.get("scope") or token.get("scopes") or ""
if isinstance(scope, list):
    scope = " ".join(scope)
raw = json.dumps(token, separators=(",", ":"))

sql = f"""
BEGIN;
UPDATE ghl_oauth_tokens SET active=false WHERE active=true;
INSERT INTO ghl_oauth_tokens (company_id, location_id, user_type, access_token, refresh_token, token_type, expires_at, scopes, raw_response, active)
VALUES ({sql_literal(company_id)}, {sql_literal(location_id)}, {sql_literal(user_type)}, {sql_literal(token['access_token'])}, {sql_literal(token.get('refresh_token') or row['refresh_token'])}, {sql_literal(token.get('token_type') or 'Bearer')}, NOW() + ({int(token.get('expires_in') or 86400)} * INTERVAL '1 second'), {sql_literal(scope)}, {sql_literal(raw)}::jsonb, true);
COMMIT;
"""
psql(sql)
print(f"refreshed expires_in={int(token.get('expires_in') or 0)}")
