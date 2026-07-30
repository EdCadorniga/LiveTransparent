"""Align all imported partnership contacts to Janvi's GHL owner ID."""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OWNER_ID = "ck6TRlU3wnTmMxuVpn5F"
LOCATION_ID = "Zwz4relUXVPxx8uohnjV"
BASE_URL = os.environ.get("GHL_API_BASE_URL", "https://services.leadconnectorhq.com")
ENV_FILE = ROOT / ".env"


def load_env():
    if not ENV_FILE.exists():
        return
    for raw in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def request(method, path, body=None, params=None):
    token = os.environ.get("GHL_PIT", "")
    if not token:
        raise RuntimeError("GHL_PIT is not configured")
    query = f"?{urllib.parse.urlencode(params)}" if params else ""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        f"{BASE_URL}{path}{query}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Version": "2021-07-28",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "curl/8.0",
        },
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == 3:
                detail = error.read().decode("utf-8", errors="replace")[:300]
                raise RuntimeError(f"{method} {path}: HTTP {error.code}: {detail}") from error
            time.sleep(2 ** attempt)


def partnership_contacts():
    contacts = {}
    for tag in ("partner_candidate_email", "partner_candidate_linkedin"):
        start_after = None
        start_after_id = None
        while True:
            params = {"locationId": LOCATION_ID, "query": tag, "limit": 100}
            if start_after is not None:
                params["startAfter"] = start_after
                params["startAfterId"] = start_after_id
            _, payload = request("GET", "/contacts/", params=params)
            rows = payload.get("contacts", [])
            for contact in rows:
                tags = set(contact.get("tags") or [])
                if contact.get("source") == "partnership_outreach" and tags.intersection({
                    "partner_candidate_email",
                    "partner_candidate_linkedin",
                }):
                    contacts[contact["id"]] = contact
            if len(rows) < 100:
                break
            cursor = rows[-1].get("startAfter") or []
            if len(cursor) != 2:
                raise RuntimeError(f"Missing pagination cursor for {tag}")
            start_after, start_after_id = cursor
    return contacts


def main():
    load_env()
    contacts = partnership_contacts()
    unassigned = [contact for contact in contacts.values() if not contact.get("assignedTo")]
    already_aligned = [contact for contact in contacts.values() if contact.get("assignedTo") == OWNER_ID]
    other_owner = [contact for contact in contacts.values() if contact.get("assignedTo") and contact.get("assignedTo") != OWNER_ID]
    print(f"Partnership contacts: {len(contacts)}")
    print(f"Already Janvi: {len(already_aligned)}")
    print(f"Unassigned: {len(unassigned)}")
    print(f"Other owner: {len(other_owner)}")
    if "--apply" not in sys.argv:
        print("Dry run. Pass --apply to assign only currently unassigned contacts.")
        return
    failures = 0
    for index, contact in enumerate(unassigned, 1):
        try:
            request("PUT", f"/contacts/{contact['id']}", body={"assignedTo": OWNER_ID})
            print(f"[{index}/{len(unassigned)}] assigned {contact['id']}")
        except Exception as error:
            failures += 1
            print(f"[{index}/{len(unassigned)}] failed {contact['id']}: {error}", file=sys.stderr)
        time.sleep(0.25)
    print(f"Updated: {len(unassigned) - failures}; failures: {failures}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
