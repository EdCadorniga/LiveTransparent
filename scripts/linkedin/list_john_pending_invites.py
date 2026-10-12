"""Read-only recon: list all PENDING Unipile LinkedIn invitations and flag the
ones whose connection note contains a search phrase (default "john here").

STRICTLY READ-ONLY: no LinkedIn writes, no GHL writes, no Postgres writes.
Reads .env for UNIPILE_TOKEN / UNIPILE_API_BASE_URL / UNIPILE_ACCOUNT_ID and
never prints those values.

Endpoint: GET {base}/users/invite/sent?account_id=...&limit=250&cursor=...
Returns only PENDING invitations (accepted ones are excluded by the provider),
each with `invitation_text` (the connection note) and `invited_user_public_id`.

Usage:
  python list_john_pending_invites.py
  python list_john_pending_invites.py --match "john here" --out "C:\\path\\review.csv"
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / ".env"


def load_env():
    for raw in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def api_get(url):
    req = urllib.request.Request(
        url,
        headers={"X-API-KEY": os.environ["UNIPILE_TOKEN"], "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode() or "{}")


def fetch_pending(base, acct, max_pages=200):
    items, cursor, pages = [], None, 0
    while pages < max_pages:
        url = f"{base}/users/invite/sent?account_id={urllib.parse.quote(acct)}&limit=100"
        if cursor:
            url += "&cursor=" + urllib.parse.quote(cursor)
        j = None
        for attempt in range(3):
            try:
                j = api_get(url)
                break
            except urllib.error.HTTPError as e:
                body = e.read().decode()[:300]
                if attempt == 2:
                    raise SystemExit(f"HTTP {e.code} from invite/sent: {body}")
                time.sleep(3)
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(3)
        if not isinstance(j, dict):
            break
        batch = j.get("items") or []
        items.extend(batch)
        cursor = j.get("cursor")
        pages += 1
        if not cursor or not batch:
            break
        time.sleep(0.25)
    return items, pages


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--match", default="john here", help="substring to flag in invitation_text")
    ap.add_argument(
        "--out",
        default=str(ROOT / "local-scripts" / "john_pending_invites_review.csv"),
    )
    args = ap.parse_args()

    load_env()
    base = os.environ["UNIPILE_API_BASE_URL"].rstrip("/")
    acct = os.environ["UNIPILE_ACCOUNT_ID"]

    print(f"Fetching pending invitations from {base} ...")
    items, pages = fetch_pending(base, acct)

    needle = args.match.lower()
    matched = [it for it in items if needle in (it.get("invitation_text") or "").lower()]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "invitation_id", "invited_user", "invited_user_public_id",
            "invited_user_id", "date", "parsed_datetime", "invitation_text",
        ])
        for it in matched:
            w.writerow([
                it.get("id", ""), it.get("invited_user", ""),
                it.get("invited_user_public_id", ""), it.get("invited_user_id", ""),
                it.get("date", ""), it.get("parsed_datetime", ""),
                it.get("invitation_text", ""),
            ])

    # note distribution for context
    notes = {}
    for it in items:
        t = (it.get("invitation_text") or "").strip()[:60] or "(no note)"
        notes[t] = notes.get(t, 0) + 1

    print(json.dumps({
        "total_pending": len(items),
        "pages": pages,
        "match": args.match,
        "matched": len(matched),
        "csv": str(out),
    }, indent=2))
    print("distinct pending note prefixes:")
    for k, v in sorted(notes.items(), key=lambda kv: -kv[1])[:15]:
        print(f"  {v:>5}  {k}")
    print("sample matches:")
    for it in matched[:20]:
        print(f"  - {it.get('invited_user','')} | {it.get('invited_user_public_id','')} | "
              f"{(it.get('invitation_text') or '')[:100]}")


if __name__ == "__main__":
    main()
