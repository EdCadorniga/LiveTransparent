"""Enrich the John pending-invite review with each contact's GHL `Vertical`.

Read-only against GHL (GET /contacts/{id}) and Postgres outputs already captured.
Writes an enriched CSV only. Never prints secrets.

Inputs (from the recon run):
  local-scripts/john_pending_invites_review.csv   (invitation rows)
  <tmp>/resolve.out                                (psql TSV: pub | cid | status | ...)

Usage:
  python enrich_john_invites_vertical.py
"""

import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / ".env"
GHL_BASE = "https://services.leadconnectorhq.com"
VERTICAL_FIELD = "ODs8fBt5te5HEfSJ91pY"
INV_CSV = ROOT / "local-scripts" / "john_pending_invites_review.csv"
RESOLVE_OUT = Path(r"C:\Users\edmon\AppData\Local\Temp\opencode\lt_pdf\resolve.out")
OUT_CSV = ROOT / "local-scripts" / "john_pending_invites_vertical_review.csv"


def load_env():
    for raw in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def get_contact(cid, pit):
    req = urllib.request.Request(
        f"{GHL_BASE}/contacts/{cid}",
        headers={
            "Authorization": f"Bearer {pit}",
            "Version": "2021-07-28",
            "Accept": "application/json",
            "User-Agent": "curl/8.0",
        },
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                time.sleep(2 * (attempt + 1))
                continue
            return {"_error": f"HTTP {e.code}", "_body": e.read().decode()[:200]}
        except Exception as e:
            time.sleep(1.5)
            if attempt == 3:
                return {"_error": str(e)[:200]}
    return {"_error": "exhausted"}


def vertical_of(contact_obj):
    c = contact_obj.get("contact", contact_obj)
    for cf in (c.get("customFields") or []):
        if cf.get("id") == VERTICAL_FIELD:
            v = cf.get("value")
            if isinstance(v, list):
                v = ", ".join(str(x) for x in v)
            return str(v or "")
    return ""


def parse_resolve():
    m = {}
    for ln in RESOLVE_OUT.read_text(encoding="utf-8", errors="replace").splitlines():
        if "|" not in ln or ln.strip().startswith("pub") or "---" in ln:
            continue
        parts = [p.strip() for p in ln.split("|")]
        if len(parts) < 3:
            continue
        pub, cid, status = parts[0], parts[1], parts[2]
        if pub and (cid or status):
            m[pub.lower()] = {"cid": cid, "status": status}
    return m


def main():
    load_env()
    pit = os.environ["GHL_PIT"]
    resolved = parse_resolve()

    rows = []
    with INV_CSV.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)

    cache = {}
    enriched = []
    fetched = 0
    for r in rows:
        pub = (r.get("invited_user_public_id") or "").strip()
        info = resolved.get(pub.lower(), {})
        cid = info.get("cid", "")
        vertical, verr = "", ""
        if cid:
            if cid not in cache:
                cache[cid] = get_contact(cid, pit)
                fetched += 1
                time.sleep(0.07)
            obj = cache[cid]
            if obj.get("_error"):
                verr = obj.get("_error", "")
            else:
                vertical = vertical_of(obj)
        enriched.append({
            "invitation_id": r.get("invitation_id", ""),
            "invited_user": r.get("invited_user", ""),
            "invited_user_public_id": pub,
            "date": r.get("date", ""),
            "ghl_contact_id": cid,
            "connection_status": info.get("status", ""),
            "vertical": vertical,
            "vertical_lookup": verr or ("ok" if cid else "no_ghl_match"),
            "invitation_text": r.get("invitation_text", ""),
        })

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(enriched[0].keys()))
        w.writeheader()
        w.writerows(enriched)

    blank = sum(1 for e in enriched if e["ghl_contact_id"] and e["vertical"] == "")
    nonblank = sum(1 for e in enriched if e["vertical"])
    nomatch = sum(1 for e in enriched if not e["ghl_contact_id"])
    err = sum(1 for e in enriched if e["vertical_lookup"] not in ("ok", "no_ghl_match"))
    dist = {}
    for e in enriched:
        if e["vertical"]:
            dist[e["vertical"]] = dist.get(e["vertical"], 0) + 1
    print(json.dumps({
        "total": len(enriched), "ghl_fetched": fetched,
        "vertical_blank": blank, "vertical_set": nonblank,
        "no_ghl_match": nomatch, "lookup_errors": err,
        "vertical_distribution": dist, "csv": str(OUT_CSV),
    }, indent=2))


if __name__ == "__main__":
    main()
