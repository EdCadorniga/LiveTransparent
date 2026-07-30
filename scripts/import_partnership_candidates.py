"""
Partnership Marketing — GHL Import Script
===========================================
Reads partnership_master.json and upserts contacts into GHL via the
contacts/upsert endpoint. Applies partner_candidate_email and/or
partner_candidate_linkedin tags, sets custom fields, and assigns
ownership to Janvi.

Usage:
  python import_partnership_candidates.py [--dry-run] [--limit N]
  python import_partnership_candidates.py --test-ed

Environment variables (from .env if available):
  GHL_PIT              — GHL Personal Access Token
  GHL_LOCATION_ID      — Default: Zwz4relUXVPxx8uohnjV
  GHL_API_BASE_URL     — Default: https://services.leadconnectorhq.com
"""

import json, os, sys, time, urllib.request, urllib.error, re
from pathlib import Path

# ─── Config ─────────────────────────────────────────────────────────────────
MASTER_JSON = Path(__file__).resolve().parent.parent / "Partnership Marketing" / "partnership_master.json"
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

def load_env():
    """Load .env file into os.environ if it exists."""
    if ENV_FILE.exists():
        with open(ENV_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, val = line.partition("=")
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key not in os.environ:
                        os.environ[key] = val

load_env()

GHL_PIT = os.environ.get("GHL_PIT", "")
GHL_BASE = os.environ.get("GHL_API_BASE_URL", "https://services.leadconnectorhq.com")
GHL_LOCATION = os.environ.get("GHL_LOCATION_ID", "Zwz4relUXVPxx8uohnjV")
GHL_VERSION = "2021-07-28"

OWNER_ID = "ck6TRlU3wnTmMxuVpn5F"  # Janvi

CUSTOM_FIELD_LINKEDIN_ID = "jE6P7IRuB6usZDFOMxrg"  # contact.apollo_person_linkedin_url
DEFAULT_SOURCE = "partnership_outreach"
TAG_EMAIL = "partner_candidate_email"
TAG_LINKEDIN = "partner_candidate_linkedin"

DRY_RUN = "--dry-run" in sys.argv
LIMIT = None
if "--limit" in sys.argv:
    idx = sys.argv.index("--limit")
    if idx + 1 < len(sys.argv):
        LIMIT = int(sys.argv[idx + 1])

# ─── Helpers ────────────────────────────────────────────────────────────────

def clean(v):
    return str(v or "").strip()

def api_request(method, path, body=None):
    """Make a GHL API request."""
    url = GHL_BASE + path
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {GHL_PIT}",
        "Version": GHL_VERSION,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return {"ok": True, "status": resp.status, "data": json.loads(resp.read().decode("utf-8"))}
    except urllib.error.HTTPError as e:
        body_text = ""
        try:
            body_text = e.read().decode("utf-8")
        except Exception:
            pass
        return {"ok": False, "status": e.code, "error": body_text[:500]}

def add_tags(contact_id, tags):
    """Add tags to a GHL contact."""
    if DRY_RUN:
        return {"ok": True, "status": 200, "dry_run": True}
    return api_request("POST", f"/contacts/{contact_id}/tags", {"tags": tags})

def set_custom_field(contact_id, field_id, value):
    """Update a custom field on a GHL contact. Uses PUT /contacts/{id}."""
    if DRY_RUN:
        return {"ok": True, "status": 200, "dry_run": True}
    return api_request("PUT", f"/contacts/{contact_id}", {
        "customFields": [{"id": field_id, "key": field_id, "field_value": str(value)}]
    })

def upsert_contact(contact):
    """Create or update a GHL contact via upsert."""
    body = {
        "locationId": GHL_LOCATION,
        "firstName": contact["first_name"],
        "lastName": contact["last_name"],
        "companyName": contact["company_name"],
        "title": contact["title"],
        "source": DEFAULT_SOURCE,
        "assignedTo": OWNER_ID,
    }

    email = clean(contact.get("email", ""))
    if email:
        body["email"] = email

    if DRY_RUN:
        return {"ok": True, "status": 200, "dry_run": True, "data": {"contact": {"id": "dry-run-id", "new": True}}}

    return api_request("POST", "/contacts/upsert", body)

# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    if not GHL_PIT:
        print("ERROR: GHL_PIT not set. Check .env file or set the environment variable.")
        sys.exit(1)

    with open(MASTER_JSON, "r", encoding="utf-8") as f:
        master = json.load(f)

    total = len(master)
    print(f"Loaded {total} contacts from {MASTER_JSON}")
    print(f"GHL Location: {GHL_LOCATION}")
    print(f"Owner: Janvi ({OWNER_ID})")
    print(f"Mode: {'DRY RUN — no real API calls' if DRY_RUN else 'LIVE'}")
    if LIMIT:
        print(f"Limit: {LIMIT} contacts")

    imported = 0
    skipped = 0
    errors = 0
    tagged_email = 0
    tagged_li = 0

    for i, contact in enumerate(master):
        if LIMIT and imported >= LIMIT:
            break

        fn = contact["first_name"]
        ln = contact["last_name"]
        email = contact.get("email", "")
        tags = contact["tags"]

        print(f"[{i+1}/{total}] {fn} {ln} ... ", end="", flush=True)

        # Upsert contact
        result = upsert_contact(contact)
        if not result["ok"]:
            print(f"FAILED (HTTP {result['status']}): {result.get('error','')[:100]}")
            errors += 1
            continue

        contact_id = result["data"]["contact"]["id"] if result.get("data", {}).get("contact") else None
        is_new = result["data"]["contact"].get("new", False) if result.get("data", {}).get("contact") else False

        if not contact_id:
            print("FAILED (no contact ID)")
            errors += 1
            continue

        # Apply email tag
        if "partner_candidate_email" in tags:
            tag_result = add_tags(contact_id, [TAG_EMAIL])
            if tag_result["ok"]:
                tagged_email += 1

        # Apply LinkedIn tag
        if "partner_candidate_linkedin" in tags:
            tag_result = add_tags(contact_id, [TAG_LINKEDIN])
            if tag_result["ok"]:
                tagged_li += 1

        # Set LinkedIn URL custom field
        li_url = clean(contact.get("linkedin_url", ""))
        if li_url and "partner_candidate_linkedin" in tags:
            set_custom_field(contact_id, CUSTOM_FIELD_LINKEDIN_ID, li_url)

        status = "NEW" if is_new else "EXISTING"
        print(f"OK ({status}) id={contact_id} tags={tags}")
        imported += 1

        # Rate limit
        if not DRY_RUN:
            time.sleep(0.25)

    # Summary
    print(f"\n=== IMPORT SUMMARY ===")
    print(f"  Total in master:  {total}")
    print(f"  Imported:         {imported}")
    print(f"  Skipped:          {skipped}")
    print(f"  Errors:           {errors}")
    print(f"  Email tags applied:  {tagged_email}")
    print(f"  LinkedIn tags applied: {tagged_li}")
    if DRY_RUN:
        print("  MODE: DRY RUN — no actual API calls made")


if __name__ == "__main__":
    main()
