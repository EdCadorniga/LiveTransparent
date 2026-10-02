"""Fix the GHL LinkedIn Connect Dispatcher mirror 401.

Root cause (verified live 2026-10-02): `mirrorLinkedInToGhl` sends the stored
`ghl_oauth_tokens.access_token`, which is a **Company/agency** token
(`user_type = Company`). GHL `/conversations/messages` rejects company tokens
with HTTP 401 ("This authClass type is not allowed to access this scope"). The
correct flow is to exchange it for a **Location** token via
`POST /oauth/locationToken` and use that as the Bearer.

This patch replaces only the token-selection block inside `mirrorLinkedInToGhl`
in workflow `fXxw5lanZcDmUrst`. Invites are unaffected; only the outbound GHL
conversation mirror changes. Publishing via REST PUT auto-activates.
"""

import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / ".env"
N8N_BASE = "https://automations.livetransparent.com"
WF_ID = "fXxw5lanZcDmUrst"
NODE = "Dispatch LinkedIn Requests"

OLD = """    const tokenRows = await client.query("SELECT access_token FROM ghl_oauth_tokens WHERE active IS TRUE AND COALESCE(access_token, '') <> '' ORDER BY received_at DESC LIMIT 1");
    const locationToken = String(tokenRows.rows?.[0]?.access_token || '').trim();
    if (!locationToken) return { ok: false, reason: 'missing_active_ghl_oauth_token' };"""

NEW = """    const tokenRows = await client.query("SELECT access_token, user_type, company_id, location_id FROM ghl_oauth_tokens WHERE active IS TRUE AND COALESCE(access_token, '') <> '' ORDER BY received_at DESC LIMIT 1");
    const tokenRow = tokenRows.rows?.[0] || {};
    const companyToken = String(tokenRow.access_token || '').trim();
    const companyId = String(tokenRow.company_id || '').trim();
    const tokenLocationId = String(tokenRow.location_id || CFG.locationId || '').trim();
    if (!companyToken) return { ok: false, reason: 'missing_active_ghl_oauth_token' };
    let locationToken = companyToken;
    if (companyId && String(tokenRow.user_type || '').toLowerCase() === 'company') {
      const exchange = await this.helpers.httpRequest({
        method: 'POST',
        url: 'https://services.leadconnectorhq.com/oauth/locationToken',
        headers: { Authorization: 'Bearer ' + companyToken, Version: '2021-07-28', Accept: 'application/json', 'Content-Type': 'application/json' },
        body: { companyId: companyId, locationId: tokenLocationId },
        json: true,
        returnFullResponse: true,
      });
      const exchangeStatus = Number(exchange?.statusCode || 200);
      const exchangedToken = String(exchange?.body?.access_token || '').trim();
      if (!(exchangeStatus >= 200 && exchangeStatus < 300) || !exchangedToken) {
        return { ok: false, reason: 'location_token_exchange_failed', status: exchangeStatus };
      }
      locationToken = exchangedToken;
    }"""


def load_env():
    for raw in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def api(method, path, key, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(N8N_BASE + path, data=data, method=method,
                                 headers={"X-N8N-API-KEY": key, "Accept": "application/json",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode() or "{}")


def main():
    load_env()
    key = os.environ["N8N_LT_API_KEY"]
    w = api("GET", f"/api/v1/workflows/{WF_ID}", key)
    node = next(n for n in w["nodes"] if n["name"] == NODE)
    code = node["parameters"]["jsCode"]
    if NEW in code:
        print("already patched; nothing to do")
        return
    if OLD not in code:
        raise SystemExit("OLD token block not found — live code drifted; aborting")
    node["parameters"]["jsCode"] = code.replace(OLD, NEW, 1)
    settings = {k: v for k, v in (w.get("settings") or {}).items() if k != "availableInMCP"}
    body = {"name": w["name"], "nodes": w["nodes"], "connections": w["connections"], "settings": settings}
    res = api("PUT", f"/api/v1/workflows/{WF_ID}", key, body)
    back = api("GET", f"/api/v1/workflows/{WF_ID}", key)
    patched = NEW in next(n for n in back["nodes"] if n["name"] == NODE)["parameters"]["jsCode"]
    print(json.dumps({
        "versionId": back.get("versionId"),
        "activeVersionId": back.get("activeVersionId"),
        "active": back.get("active"),
        "patched": patched,
        "nodes": len(back.get("nodes", [])),
    }, indent=2))


if __name__ == "__main__":
    main()
