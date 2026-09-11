"""Run one bounded LinkedIn backfill batch from the live Postgres worklist."""
import json
import os
import paramiko
import requests
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
GHL_BASE = "https://services.leadconnectorhq.com"
UNIPILE_BASE = "https://api42.unipile.com:17256/api/v1"
LOCATION_ID = "Zwz4relUXVPxx8uohnjV"
PROVIDER_ID = "6a58a14ff3023bea3783c152"
ACCOUNT_ID = "V9eiHiDpRmCtan0YNdzsQw"


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
UNIPILE_TOKEN = ENV.get("UNIPILE_TOKEN", "")
if not UNIPILE_TOKEN:
    raise SystemExit("UNIPILE_TOKEN is required")


def sql_literal(value):
    if value is None or value == "":
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


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
        raise RuntimeError("SSH key load failed")
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


claim_sql = """
WITH reset_stale AS (
  UPDATE linkedin_backfill_worklist
  SET status='pending', claimed_at=NULL, updated_at=NOW()
  WHERE status='processing' AND claimed_at < NOW() - INTERVAL '1 hour'
), claimed AS (
  UPDATE linkedin_backfill_worklist
  SET status='processing', claimed_at=NOW(), updated_at=NOW()
  WHERE chat_id IN (
    SELECT chat_id FROM linkedin_backfill_worklist
    WHERE status='pending' ORDER BY last_ts ASC LIMIT 30 FOR UPDATE SKIP LOCKED
  )
  RETURNING *
), token AS (
  SELECT access_token FROM ghl_oauth_tokens
  WHERE active IS TRUE AND access_token <> ''
  ORDER BY received_at DESC NULLS LAST LIMIT 1
)
SELECT token.access_token || E'\t' || COALESCE((SELECT json_agg(row_to_json(claimed))::text FROM claimed), '[]') FROM token;
""".strip()
claimed_line = psql(claim_sql)
if not claimed_line:
    print("No pending worklist rows or OAuth token")
    raise SystemExit(0)
oauth_token, rows_json = claimed_line.split("\t", 1)
rows = json.loads(rows_json)
if not rows:
    print("No pending worklist rows")
    raise SystemExit(0)

ghl_headers = {"Authorization": "Bearer " + oauth_token, "Version": "2021-07-28", "Accept": "application/json", "User-Agent": UA}
ghl_json_headers = {**ghl_headers, "Content-Type": "application/json"}
unipile_headers = {"X-API-KEY": UNIPILE_TOKEN, "Accept": "application/json", "User-Agent": UA}
session = requests.Session()


def get(url, headers, params=None):
    response = session.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def contact_name(contact):
    return str(contact.get("contactName") or contact.get("name") or " ".join(filter(None, [contact.get("firstName"), contact.get("lastName")]))).strip().lower()


def score_contact(contact, row):
    identifier = str(row.get("profile_public_identifier") or "").lower()
    name = str(row.get("profile_full_name") or "").strip().lower()
    fields = json.dumps(contact.get("customFields") or []).lower()
    website = str(contact.get("website") or "").lower()
    score = 0
    if identifier and (identifier in fields or identifier in website):
        score += 100
    if name and contact_name(contact) == name:
        score += 30
    return score


def resolve_contact(row):
    candidates = []
    for query in [row.get("profile_public_identifier"), row.get("profile_full_name")]:
        if not query:
            continue
        data = get(GHL_BASE + "/contacts/", ghl_headers, {"query": query, "locationId": LOCATION_ID, "limit": 20})
        for contact in data.get("contacts") or []:
            if not any(existing.get("id") == contact.get("id") for existing in candidates):
                candidates.append(contact)
        if candidates:
            break
    ranked = sorted(((score_contact(contact, row), contact) for contact in candidates), reverse=True, key=lambda item: item[0])
    if not ranked:
        full_name = str(row.get("profile_full_name") or "").strip()
        parts = full_name.split()
        if not full_name:
            return ""
        payload = {
            "firstName": parts[0],
            "lastName": " ".join(parts[1:]) or "LinkedIn",
            "source": "LinkedIn via Unipile historical backfill",
            "website": row.get("profile_url") or ("https://www.linkedin.com/in/" + str(row.get("profile_public_identifier"))),
            "locationId": LOCATION_ID,
        }
        created = session.post(GHL_BASE + "/contacts/", headers={**ghl_json_headers, "Content-Type": "application/json"}, json=payload, timeout=30)
        created.raise_for_status()
        return (created.json().get("contact") or {}).get("id") or created.json().get("id") or ""
    if ranked[0][0] < 30 or (len(ranked) > 1 and ranked[0][0] == ranked[1][0]):
        return ""
    return ranked[0][1].get("id") or ""


def existing_bodies(contact_id):
    data = get(GHL_BASE + "/conversations/search", ghl_headers, {"contactId": contact_id, "limit": 20})
    conversations = [conversation for conversation in data.get("conversations") or []
                     if conversation.get("lastMessageConversationProviderId") == PROVIDER_ID
                     or conversation.get("conversationProviderId") == PROVIDER_ID]
    bodies = set()
    for conversation in conversations:
        data = get(GHL_BASE + f"/conversations/{conversation['id']}/messages", ghl_headers, {"limit": 100})
        messages = (data.get("messages") or {}).get("messages") if isinstance(data.get("messages"), dict) else data.get("messages")
        for message in messages or []:
            bodies.add(str(message.get("body") or message.get("message") or "").strip())
    return bodies


results = []
for row in rows:
    result = {"chat_id": row["chat_id"], "status": "done", "posted_count": 0, "skipped_count": 0, "error_count": 0, "last_error": ""}
    try:
        contact_id = resolve_contact(row)
        if not contact_id:
            raise RuntimeError("no unambiguous GHL contact match")
        messages = get(UNIPILE_BASE + f"/chats/{row['chat_id']}/messages", unipile_headers,
                       {"account_id": ACCOUNT_ID, "limit": 100}).get("items") or []
        bodies = existing_bodies(contact_id)
        for message in messages:
            body = str(message.get("text") or "").strip()
            if not body or body in bodies:
                result["skipped_count"] += 1
                continue
            inbound = message.get("is_sender") != 1
            # Historical outbound posts hit the live GHL custom-provider
            # callback and are sent to LinkedIn. Keep this backfill inbox-only.
            if not inbound:
                result["skipped_count"] += 1
                continue
            endpoint = GHL_BASE + "/conversations/messages" + ("/inbound" if inbound else "")
            payload = {"type": "Custom", "contactId": contact_id, "message": message.get("text"),
                       "conversationProviderId": PROVIDER_ID, "altId": row["chat_id"], "date": message.get("timestamp")}
            response = session.post(endpoint, headers=ghl_json_headers, json=payload, timeout=30)
            response.raise_for_status()
            result["posted_count"] += 1
            bodies.add(body)
            time.sleep(0.25)
    except Exception as exc:
        result["status"] = "error"
        result["error_count"] = 1
        result["last_error"] = str(exc)[:300]
    results.append(result)
    print(json.dumps(result, separators=(",", ":")), flush=True)

updates = ";\n".join(
    "UPDATE linkedin_backfill_worklist SET status={status}, posted_count={posted}, skipped_count={skipped}, error_count={errors}, last_error={last_error}, completed_at={completed}, updated_at=NOW() WHERE chat_id={chat}".format(
        status=sql_literal(result["status"]), posted=result["posted_count"], skipped=result["skipped_count"],
        errors=result["error_count"], last_error=sql_literal(result["last_error"]),
        completed="NOW()" if result["status"] == "done" else "NULL", chat=sql_literal(result["chat_id"])
    ) for result in results
)
psql("BEGIN;\n" + updates + ";\nCOMMIT;")
print(json.dumps({"batch_chats": len(results), "posted": sum(r["posted_count"] for r in results),
                  "skipped": sum(r["skipped_count"] for r in results), "errors": sum(r["error_count"] for r in results)}))
