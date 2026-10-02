"""Reconcile LinkedIn `requested`/`requested_pending` state rows against Unipile.

Many contacts accepted our connect request but were never marked connected
(the acceptance checker only caught note-bearing accepts, and Relations
Backfill was a silent no-op). This tool fetches the real 1st-degree relation
set from Unipile, finds state rows still in requested* whose provider/public
id is now a relation, marks them `connected` through the canonical state-upsert
webhook, and applies `linkedin_connected` in GHL.

Idempotent. No LinkedIn message is sent. Reads the state-upsert secret at
runtime from the live workflow Config (never prints it).

Usage:
  python reconcile_requested_connections.py            # dry run (report only)
  python reconcile_requested_connections.py --apply
"""

import argparse
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / ".env"
N8N_BASE = "https://automations.livetransparent.com"
GHL_BASE = "https://services.leadconnectorhq.com"
STATE_UPSERT_URL = N8N_BASE + "/webhook/lt-linkedin-connection-state-upsert"
PG_CONTAINER = "postgres-uokgs4c04ko0s4scccg40cgg"
LOCATION_ID = "Zwz4relUXVPxx8uohnjV"
MAIN_TAG = "linkedin_connected"


def load_env():
    for raw in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def n8n_api(method, path, key, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(N8N_BASE + path, data=data, method=method,
                                 headers={"X-N8N-API-KEY": key, "Accept": "application/json",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode() or "{}")


def state_secret(n8n_key):
    """Read stateUpsertSecret from a live workflow Config (never printed)."""
    w = n8n_api("GET", "/api/v1/workflows/ceaKnz6E3onQrZpt", n8n_key)
    for n in w["nodes"]:
        if n["name"] == "Config":
            for a in n["parameters"].get("assignments", {}).get("assignments", []):
                if a.get("name") == "stateUpsertSecret":
                    return str(a.get("value") or "")
    raise SystemExit("stateUpsertSecret not found in live Config")


def ssh():
    host = os.environ.get("VPS_HOST") or os.environ.get("VPS_HOSTNAME")
    user = os.environ.get("VPS_USER")
    keypath = os.path.expandvars(os.path.expanduser(os.environ["VPS_SSH_KEY_PATH"]))
    k = None
    for cls in (paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey):
        try:
            k = cls.from_private_key_file(keypath); break
        except Exception:
            pass
    c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(hostname=host, username=user, pkey=k, timeout=20,
              look_for_keys=False, allow_agent=False)
    return c


def pg_query(sql):
    c = ssh()
    try:
        remote = ("PGPASSWORD='%s' docker exec -i %s psql -U postgres -d postgres -tA -c \"%s\""
                  % (os.environ["POSTGRES_PASSWORD"].replace("'", "'\\''"), PG_CONTAINER, sql))
        _, out, _ = c.exec_command(remote, timeout=90)
        return out.read().decode()
    finally:
        c.close()


def unipile_relations():
    tok = os.environ["UNIPILE_TOKEN"]; acct = os.environ["UNIPILE_ACCOUNT_ID"]
    base = os.environ.get("UNIPILE_API_BASE_URL", "https://api42.unipile.com:17256/api/v1").rstrip("/")
    prov, pubs, created = set(), set(), {}
    cursor, total, pages = None, 0, 0
    while pages < 120:
        url = f"{base}/users/relations?account_id={acct}&limit=100"
        if cursor:
            url += "&cursor=" + urllib.parse.quote(cursor)
        j = None
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers={"X-API-KEY": tok, "Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=45) as r:
                    j = json.loads(r.read().decode()); break
            except Exception:
                if attempt == 2:
                    raise
                import time; time.sleep(3)
        items = j.get("items", []) if isinstance(j, dict) else []
        total += len(items)
        for it in items:
            pid = it.get("member_id")
            pub = it.get("public_identifier")
            ts = it.get("created_at")
            if pid:
                prov.add(pid); created.setdefault(pid, ts)
            if pub:
                pubs.add(pub.lower()); created.setdefault(pub.lower(), ts)
        cursor = j.get("cursor") if isinstance(j, dict) else None
        pages += 1
        if not cursor or not items:
            break
        import time; time.sleep(0.25)
    print(f"  unipile relations fetched={total} providers={len(prov)} exhausted={not bool(cursor)}")
    return prov, pubs, created


def to_iso_ms(ms):
    if not ms:
        return datetime.now(timezone.utc).isoformat()
    try:
        return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).isoformat()
    except Exception:
        return datetime.now(timezone.utc).isoformat()


def post_state(row, connected_at, secret):
    payload = {
        "ghl_contact_id": row["cid"],
        "location_id": LOCATION_ID,
        "unipile_account_id": os.environ["UNIPILE_ACCOUNT_ID"],
        "linkedin_profile_url": row.get("pub") and f"https://www.linkedin.com/in/{row['pub']}" or "",
        "linkedin_public_identifier": row.get("pub", ""),
        "linkedin_provider_id": row.get("prov", ""),
        "connection_status": "connected",
        "connected_at": connected_at,
        "source_workflow_name": "LT - LinkedIn Requested Reconcile",
        "source_key": f"reconcile:{row.get('prov') or row.get('pub')}",
        "event_type": "connection_accepted",
        "event_at": connected_at,
        "payload_json": {"reconciled": True, "providerId": row.get("prov", ""), "publicId": row.get("pub", "")},
        "metadata_json": {"source": "requested_reconcile"},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(STATE_UPSERT_URL, data=data, method="POST", headers={
        "Content-Type": "application/json", "Accept": "application/json",
        "X-LT-LinkedIn-State-Secret": secret, "User-Agent": "curl/8.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode()[:200]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:200]


def add_tag(cid, tag, ghl_key):
    data = json.dumps({"tags": [tag]}).encode("utf-8")
    req = urllib.request.Request(f"{GHL_BASE}/contacts/{cid}/tags", data=data, method="POST", headers={
        "Authorization": f"Bearer {ghl_key}", "Version": "2021-07-28",
        "Accept": "application/json", "Content-Type": "application/json", "User-Agent": "curl/8.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    load_env()
    n8n_key = os.environ["N8N_LT_API_KEY"]
    secret = state_secret(n8n_key)
    print("Fetching Unipile relations ...")
    prov, pubs, created = unipile_relations()
    raw = pg_query(
        "SELECT ghl_contact_id||E'\\t'||COALESCE(linkedin_provider_id,'')||E'\\t'||"
        "COALESCE(linkedin_public_identifier,'')||E'\\t'||COALESCE(linkedin_profile_url,'') "
        "FROM linkedin_connection_state WHERE connection_status IN ('requested','requested_pending')")
    rows = []
    for ln in raw.splitlines():
        if not ln.strip():
            continue
        p = ln.split("\t")
        if len(p) < 4:
            p += [""] * (4 - len(p))
        rows.append({"cid": p[0], "prov": p[1], "pub": p[2], "url": p[3]})
    matched = []
    for r in rows:
        if (r["pub"] and r["pub"].lower() in pubs) or (r["prov"] and r["prov"] in prov):
            matched.append(r)
    print(f"requested rows={len(rows)} now-first-degree={len(matched)}")
    if not args.apply:
        for r in matched[:15]:
            print("  would reconcile", r["cid"], (r["prov"] or "")[:22], r["pub"])
        print("dry run only; pass --apply to write")
        return
    ok = fail = tagged = tag_fail = 0
    for r in matched:
        connected_at = to_iso_ms(created.get(r["pub"].lower()) or created.get(r["prov"]))
        st, body = post_state(r, connected_at, secret)
        if 200 <= st < 300:
            ok += 1
            ts = add_tag(r["cid"], MAIN_TAG, os.environ["GHL_PIT"])
            if ts in (200, 201):
                tagged += 1
            else:
                tag_fail += 1
        else:
            fail += 1
            if fail <= 5:
                print("  state fail", r["cid"], st, body)
        import time; time.sleep(0.15)
    print(json.dumps({"matched": len(matched), "state_ok": ok, "state_fail": fail,
                      "tagged": tagged, "tag_fail": tag_fail}, indent=2))


if __name__ == "__main__":
    main()
