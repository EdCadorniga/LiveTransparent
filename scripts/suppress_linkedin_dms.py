"""
LinkedIn DM Suppression Script
===============================
Usage: python suppress_linkedin_dms.py <name_or_linkedin_url>

Suppresses all future LinkedIn DMs to a contact by:
1. Resolving their LinkedIn profile via Unipile
2. Finding their GHL contact (if one exists)
3. Adding the linkedin_dm_sequence_completed tag in GHL
4. Marking their linkedin_connection_state row as terminal

Required env vars (can be set in .env or inline):
  UNIPILE_API_KEY, UNIPILE_ACCOUNT_ID, UNIPILE_API_BASE_URL
  GHL_API_KEY, GHL_LOCATION_ID, GHL_API_BASE_URL
  STATE_UPSERT_URL
"""

import sys, json, os, re, urllib.parse, urllib.request

# --- Config (override via env) ---
UNIPILE_KEY = os.environ.get("UNIPILE_API_KEY", "Mb1oWs6Z.YZWq+uQp/V4DPMLf2UN6i9bbS2IqGX/MDJ4y3DExshc=")
UNIPILE_ACCOUNT = os.environ.get("UNIPILE_ACCOUNT_ID", "V9eiHiDpRmCtan0YNdzsQw")
UNIPILE_BASE = os.environ.get("UNIPILE_API_BASE_URL", "https://api42.unipile.com:17256/api/v1")
GHL_KEY = os.environ.get("GHL_API_KEY", "pit-b278b3ad-96bd-41fb-ba03-9f927039eb28")
GHL_BASE = os.environ.get("GHL_API_BASE_URL", "https://services.leadconnectorhq.com")
GHL_LOCATION = os.environ.get("GHL_LOCATION_ID", "Zwz4relUXVPxx8uohnjV")
STATE_UPSERT_URL = os.environ.get("STATE_UPSERT_URL", "https://automations.livetransparent.com/webhook/lt-linkedin-connection-state-upsert")

DM_COMPLETE_TAG = "linkedin_dm_sequence_completed"

# --- Helpers ---

def http_request(method, url, headers=None, body=None):
    """Minimal HTTP client using urllib (no external deps)."""
    if headers is None:
        headers = {}
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {"error": str(e), "body": body}
    except Exception as e:
        return {"error": str(e)}


def extract_linkedin_identifier(input_str):
    """Extract public identifier from a LinkedIn URL or return plain name."""
    input_str = input_str.strip()
    # Match linkedin.com/in/<identifier>
    m = re.search(r"linkedin\.com/in/([^/?\s]+)", input_str, re.IGNORECASE)
    if m:
        return m.group(1).rstrip("/")
    # Match linkedin.com/in/<identifier>/...
    m = re.search(r"linkedin\.com/in/([^/?\s]+)/?", input_str, re.IGNORECASE)
    if m:
        return m.group(1).rstrip("/")
    return input_str  # assume it's a name


def unipile_lookup(identifier):
    """Look up a LinkedIn profile by public identifier or search by name."""
    # Try direct lookup first (for /in/<id> format)
    if "/" not in identifier and " " not in identifier:
        url = f"{UNIPILE_BASE}/users/{urllib.parse.quote(identifier)}?account_id={urllib.parse.quote(UNIPILE_ACCOUNT)}"
        headers = {"X-API-KEY": UNIPILE_KEY, "Accept": "application/json"}
        resp = http_request("GET", url, headers=headers)
        if resp.get("provider_id"):
            return resp
    # Search by name
    url = f"{UNIPILE_BASE}/users/search?account_id={urllib.parse.quote(UNIPILE_ACCOUNT)}&q={urllib.parse.quote(identifier)}&limit=5"
    headers = {"X-API-KEY": UNIPILE_KEY, "Accept": "application/json"}
    resp = http_request("GET", url, headers=headers)
    items = resp.get("items", [])
    if items:
        return items[0]
    return None


def search_ghl_contacts(query):
    """Search GHL contacts by name or email."""
    url = f"{GHL_BASE}/contacts/search"
    headers = {
        "Authorization": f"Bearer {GHL_KEY}",
        "Version": "2021-07-28",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    body = {"locationId": GHL_LOCATION, "page": 1, "pageLimit": 10, "query": query}
    resp = http_request("POST", url, headers=headers, body=body)
    return resp.get("contacts", [])


def search_ghl_by_linkedin_url(linkedin_url):
    """Search GHL contacts by LinkedIn URL in custom fields."""
    contacts = search_ghl_contacts(linkedin_url)
    if contacts:
        return contacts
    # Try with just the identifier
    identifier = extract_linkedin_identifier(linkedin_url)
    return search_ghl_contacts(identifier)


def add_ghl_tag(contact_id, tag):
    """Add a tag to a GHL contact."""
    url = f"{GHL_BASE}/contacts/{urllib.parse.quote(contact_id)}/tags"
    headers = {
        "Authorization": f"Bearer {GHL_KEY}",
        "Version": "2021-07-28",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    body = {"tags": [tag]}
    return http_request("POST", url, headers=headers, body=body)


def upsert_state(contact_data):
    """Upsert a row in linkedin_connection_state."""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    return http_request("POST", STATE_UPSERT_URL, headers=headers, body=contact_data)


# --- Main ---

def suppress(input_str):
    print(f"=== Suppressing LinkedIn DMs for: {input_str} ===\n")

    identifier = extract_linkedin_identifier(input_str)
    print(f"[1] Identifier: {identifier}")

    # Step 1: Unipile lookup
    print("[2] Looking up on Unipile...")
    profile = unipile_lookup(identifier)
    if not profile or not profile.get("provider_id"):
        print("ERROR: Could not find LinkedIn profile on Unipile.")
        print(f"Profile data: {json.dumps(profile)[:200]}")
        return False

    provider_id = profile["provider_id"]
    public_id = profile.get("public_identifier", identifier)
    first_name = profile.get("first_name", "")
    last_name = profile.get("last_name", "")
    profile_url = f"https://www.linkedin.com/in/{public_id}/"
    print(f"  Name: {first_name} {last_name}")
    print(f"  Provider ID: {provider_id}")
    print(f"  Profile: {profile_url}")

    # Step 2: GHL contact search
    print("[3] Searching GHL contacts...")
    ghl_contacts = search_ghl_contacts(f"{first_name} {last_name}")
    if not ghl_contacts:
        # Try by LinkedIn URL
        ghl_contacts = search_ghl_by_linkedin_url(profile_url)

    ghl_contact_id = None
    if ghl_contacts:
        ghl_contact_id = ghl_contacts[0]["id"]
        cname = ghl_contacts[0].get("contactName", "?")
        print(f"  Found GHL contact: {ghl_contact_id} ({cname})")
    else:
        print("  No GHL contact found (follower/synthetic contact)")

    # Step 3: Suppress in GHL (if GHL contact exists)
    if ghl_contact_id:
        print("[4] Adding GHL tag: linkedin_dm_sequence_completed...")
        tag_resp = add_ghl_tag(ghl_contact_id, DM_COMPLETE_TAG)
        print(f"  Tag result: {json.dumps(tag_resp)[:200]}")
    else:
        print("[4] Skipping GHL tag (no GHL contact)")

    # Step 4: Suppress in linkedin_connection_state
    print("[5] Updating linkedin_connection_state to terminal...")
    now = "2026-07-15T00:00:00.000Z"  # use server-side NOW() via webhook

    suppressed_ids = []

    # If there's a real GHL contact ID, suppress that row
    if ghl_contact_id:
        suppressed_ids.append(ghl_contact_id)
        body = {
            "ghl_contact_id": ghl_contact_id,
            "location_id": GHL_LOCATION,
            "unipile_account_id": UNIPILE_ACCOUNT,
            "linkedin_profile_url": profile_url,
            "linkedin_public_identifier": public_id,
            "linkedin_provider_id": provider_id,
            "connection_status": "completed",
            "sequence_step": 4,
            "source_workflow_name": "manual_suppression_script",
            "source_key": f"manual:suppress:{public_id}",
            "payload_json": {
                "dm_sequence_status": "completed",
                "dm_conversation_status": "active",
                "suppressed_at": now,
            },
            "metadata_json": {
                "source": "manual_suppression",
                "reason": "user_requested_stop_DMs",
            },
        }
        resp = upsert_state(body)
        print(f"  GHL contact row: ok={resp.get('ok')} status={resp.get('connection_status')}")

    # Also suppress the synthetic follower row (in case it exists)
    synth_id = f"linkedin:follower:{provider_id}"
    if synth_id not in suppressed_ids:
        suppressed_ids.append(synth_id)
        body = {
            "ghl_contact_id": synth_id,
            "location_id": GHL_LOCATION,
            "unipile_account_id": UNIPILE_ACCOUNT,
            "linkedin_profile_url": profile_url,
            "linkedin_public_identifier": public_id,
            "linkedin_provider_id": provider_id,
            "connection_status": "completed",
            "sequence_step": 4,
            "source_workflow_name": "manual_suppression_script",
            "source_key": f"manual:suppress:{public_id}:follower",
            "payload_json": {
                "dm_sequence_status": "completed",
                "dm_conversation_status": "active",
                "suppressed_at": now,
            },
            "metadata_json": {
                "source": "manual_suppression",
                "reason": "user_requested_stop_DMs",
            },
        }
        resp = upsert_state(body)
        print(f"  Follower row: ok={resp.get('ok')} status={resp.get('connection_status')}")

    print(f"\n=== SUPPRESSED: {first_name} {last_name} ===")
    print(f"  GHL tag: {'applied' if ghl_contact_id else 'N/A (no GHL contact)'}")
    print(f"  State rows suppressed: {', '.join(suppressed_ids)}")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        print("Examples:")
        print("  python suppress_linkedin_dms.py 'Jack Reamer'")
        print("  python suppress_linkedin_dms.py https://www.linkedin.com/in/jackreamer/")
        sys.exit(1)

    target = " ".join(sys.argv[1:])
    success = suppress(target)
    sys.exit(0 if success else 1)
