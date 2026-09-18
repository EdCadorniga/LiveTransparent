import base64
import hashlib
import json
import os
import random
import time
from pathlib import Path
from urllib.request import Request, urlopen

import paramiko

SSH_KEY = Path(r"C:\Users\edmon\.ssh\local-upload")
ACCOUNT_ID = "F2UprZ8aQc6Qm9CYYWU6cg"
UNIPILE_BASE = "https://api42.unipile.com:17256/api/v1"
UNIPILE_KEY = os.environ.get("UNIPILE_TOKEN", "<see .env>")
GHL_BASE = "https://services.leadconnectorhq.com"
GHL_KEY = os.environ.get("GHL_PIT", "<see .env>")
LOCATION_ID = "Zwz4relUXVPxx8uohnjV"
BLOCKING_TAGS = ["do not contact", "do_not_contact", "dnc", "unsubscribed", "opted out", "do not nurture", "partner_replied", "partner_not_interested", "partner_do_not_contact", "stop_linkedin_dms", "linkedin_dm_sequence_completed", "simpletext_stop", "vapi_dnc"]
DAILY_CAP = 45
MAX_BATCH = 10
PG_USER = "postgres"
PG_DB = "n8n"
RUN_ID = "batch_send:" + str(int(time.time()))
RUN_DATE = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 7 * 3600))

def run(client, command):
    _, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    status = stdout.channel.recv_exit_status()
    if status:
        raise RuntimeError(error or output or f"Command failed with status {status}")
    return output

def psql(client, sql, container):
    encoded = base64.b64encode(sql.encode()).decode()
    return run(client, f"docker exec {container} sh -lc 'echo {encoded} | base64 -d | psql -v ON_ERROR_STOP=1 -U {PG_USER} -d {PG_DB} -At'")

def api(method, url, headers, body=None):
    req = Request(url, method=method, headers=headers, data=body)
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode()), resp.status
    except Exception as e:
        return None, getattr(e, "code", 0)

def unipile_get(username):
    url = f"{UNIPILE_BASE}/users/{username}?account_id={ACCOUNT_ID}"
    data, code = api("GET", url, {"X-API-KEY": UNIPILE_KEY, "Accept": "application/json"})
    return data, code

def unipile_send(attendee_id, text):
    url = f"{UNIPILE_BASE}/chats"
    body = json.dumps({"account_id": ACCOUNT_ID, "attendees_ids": [attendee_id], "text": text}).encode()
    data, code = api("POST", url, {"X-API-KEY": UNIPILE_KEY, "Accept": "application/json", "Content-Type": "application/json"}, body)
    return data, code

def ghl_get(path):
    url = f"{GHL_BASE}{path}"
    data, code = api("GET", url, {"Authorization": f"Bearer {GHL_KEY}", "Version": "2021-07-28", "Accept": "application/json"})
    return data, code

def message_for(campaign, company):
    if campaign == "partnerships":
        return "Hey! Love your work. We work with a lot of the same audience in this space and thought there might be a good reason to connect."
    if campaign == "dan_brands":
        return f"Hey! Loved seeing what you're doing with {company} - quick question, are you currently able to tell which dispensary is actually converting your ad spend into sales?"
    return f"Hey! Quick question - does {company} currently have any brand-funded marketing driving foot traffic, or is it mostly word of mouth?"

key = paramiko.Ed25519Key.from_private_key_file(str(SSH_KEY))
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("89.117.21.29", username="root", pkey=key, timeout=30)

try:
    containers = run(client, "docker ps --format '{{.Names}}\t{{.Image}}' | grep -i postgres")
    pg = next(row.split("\t")[0] for row in containers.strip().splitlines() if row.split("\t")[0].startswith("postgres-"))
    env = {}
    for line in run(client, f"docker exec {pg} env").splitlines():
        if "=" in line:
            name, val = line.split("=", 1)
            env[name] = val
    PG_USER = env.get("POSTGRES_USER", "postgres")

    # 1. Get sent today count
    row = psql(client, f"SELECT COUNT(1)::int FROM instagram_company_dm_send_log WHERE status = 'sent' AND (sent_at AT TIME ZONE 'America/Los_Angeles')::date = (NOW() AT TIME ZONE 'America/Los_Angeles')::date;", pg)
    sent_today = int(row.strip()) if row.strip() else 0
    remaining = DAILY_CAP - sent_today
    batch = min(remaining, MAX_BATCH)
    print(f"Sent today: {sent_today}, Remaining: {remaining}, Batch: {batch}")

    if batch <= 0:
        print("Daily cap reached")
        exit(0)

    # 2. Validate remaining candidates (resolve provider IDs)
    while True:
        validate_sql = """
        WITH picked AS (
          SELECT id, campaign_priority, campaign_key, company_name, normalized_username
          FROM instagram_company_dm_state
          WHERE unipile_account_id = '""" + ACCOUNT_ID + """'
            AND sequence_status = 'pending'
            AND identity_status IN ('candidate', 'resolving')
            AND (claim_owner = '' OR claimed_at < NOW() - INTERVAL '30 minutes')
          ORDER BY campaign_priority, source_row NULLS LAST, id
          FOR UPDATE SKIP LOCKED LIMIT 20
        )
        UPDATE instagram_company_dm_state s
        SET identity_status = 'resolving', claim_owner = '""" + RUN_ID + """', claimed_at = NOW(), workflow_run_id = '""" + RUN_ID + """', updated_at = NOW()
        FROM picked
        WHERE s.id = picked.id
        RETURNING s.id, s.campaign_key, s.company_name, s.normalized_username;
        """
        candidates = psql(client, validate_sql, pg).strip()
        if not candidates:
            print("No more candidates to validate")
            break

        for line in candidates.strip().splitlines():
            parts = line.split("|")
            if len(parts) < 4:
                continue
            cid, campaign, company, username = parts[0], parts[1], parts[2], parts[3]
            profile, code = unipile_get(username)
            time.sleep(0.35)

            if profile and profile.get("provider") == "INSTAGRAM":
                provider_id = profile.get("provider_id", "")
                messaging_id = profile.get("provider_messaging_id", "")
                public_id = (profile.get("public_identifier") or "").lower().replace("@", "")
                profile_type = (profile.get("profile_type") or "").upper()
                category = profile.get("category") or ""
                is_biz = "true" if profile_type == "BUSINESS" else "false"
                username_match = "true" if public_id == username.lower() else "false"

                if not provider_id or not public_id or username_match != "true":
                    status = "rejected"
                    reason = "username_mismatch" if username_match != "true" else "missing_provider_identity"
                    psql(client, f"UPDATE instagram_company_dm_state SET identity_status = '{status}', resolution_method = 'unipile_profile_lookup', resolution_confidence = 'rejected', failure_reason = '{reason}', instagram_profile_provider_id = '{provider_id}', instagram_chat_attendee_id = '{messaging_id}', identity_account_type = '{profile_type}', identity_is_business = {is_biz}, identity_category = '{category}', profile_payload = '{base64.b64encode(json.dumps(profile).encode()).decode()}'::jsonb, claim_owner = '', claimed_at = NULL, updated_at = NOW() WHERE id = {cid} AND claim_owner = '{RUN_ID}'", pg)
                else:
                    psql(client, f"UPDATE instagram_company_dm_state SET identity_status = 'validated', resolution_method = 'unipile_profile_lookup', resolution_confidence = 'provider_verified', failure_reason = '', instagram_profile_provider_id = '{provider_id}', instagram_chat_attendee_id = '{messaging_id}', identity_account_type = '{profile_type}', identity_is_business = {is_biz}, identity_category = '{category}', profile_payload = '{base64.b64encode(json.dumps(profile).encode()).decode()}'::jsonb, claim_owner = '', claimed_at = NULL, updated_at = NOW() WHERE id = {cid} AND claim_owner = '{RUN_ID}'", pg)
            elif code in (404, 422):
                psql(client, f"UPDATE instagram_company_dm_state SET identity_status = 'rejected', resolution_method = 'unipile_profile_lookup', resolution_confidence = 'rejected', failure_reason = 'profile_not_found', claim_owner = '', claimed_at = NULL, updated_at = NOW() WHERE id = {cid} AND claim_owner = '{RUN_ID}'", pg)
            else:
                psql(client, f"UPDATE instagram_company_dm_state SET identity_status = 'candidate', claim_owner = '', claimed_at = NULL, failure_reason = 'provider_lookup_failed:{code}', updated_at = NOW() WHERE id = {cid} AND claim_owner = '{RUN_ID}'", pg)
        print(f"Validated batch, checking for more...")

    # 3. Send DMs to eligible candidates
    email_table = chr(34) + "Email_Events" + chr(34)
    send_sql = f"""
    SELECT state.id, state.campaign_key, state.company_name, state.normalized_username,
           state.instagram_profile_provider_id, state.instagram_chat_attendee_id,
           state.primary_ghl_contact_id, state.associated_ghl_contact_ids
    FROM instagram_company_dm_state state
    WHERE state.unipile_account_id = '{ACCOUNT_ID}'
      AND state.identity_status <> 'rejected'
      AND state.message_step = 0
      AND state.sequence_status IN ('pending', 'ready')
      AND state.reply_status = ''
      AND state.suppressed_at IS NULL
      AND state.instagram_profile_provider_id <> ''
      AND state.instagram_chat_attendee_id <> ''
      AND (state.claim_owner = '' OR state.claimed_at < NOW() - INTERVAL '30 minutes')
      AND NOT EXISTS (SELECT 1 FROM instagram_company_dm_send_log sl WHERE sl.state_id = state.id AND sl.message_step = 1)
      AND NOT EXISTS (SELECT 1 FROM instagram_inbound_reply_events r WHERE r.unipile_account_id = state.unipile_account_id AND ((r.instagram_profile_provider_id IS NOT NULL AND r.instagram_profile_provider_id = state.instagram_profile_provider_id) OR LOWER(COALESCE(r.instagram_username, '')) = LOWER(state.normalized_username)))
    ORDER BY state.campaign_priority, state.source_row NULLS LAST, state.id
    LIMIT {batch};
    """
    rows = psql(client, send_sql, pg).strip()
    if not rows:
        print("No eligible candidates found after validation")
        exit(0)

    sent = 0
    skipped = 0
    failed = 0
    claimed = 0
    for line in rows.strip().splitlines():
        if sent >= batch:
            break
        parts = line.split("|")
        if len(parts) < 8:
            continue
        cid, campaign, company, username, provider_id, attendee_id, primary_ghl, associated_raw = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6], parts[7]
        associated = [x.strip() for x in associated_raw.strip("{}").split(",") if x.strip()] if associated_raw.strip("{}") else []

        claim = psql(client, f"UPDATE instagram_company_dm_state SET claim_owner = '{RUN_ID}', claimed_at = NOW(), workflow_run_id = '{RUN_ID}', updated_at = NOW() WHERE id = {cid} AND message_step = 0 AND (claim_owner = '' OR claimed_at < NOW() - INTERVAL '30 minutes') RETURNING id", pg)
        if not claim.strip():
            continue
        claimed += 1

        # Suppression check
        suppressed = False
        for ghl_id in associated:
            contact, code = ghl_get(f"/contacts/{ghl_id}")
            time.sleep(0.5)
            if contact:
                tags = [str(t).lower() for t in (contact.get("contact") or contact).get("tags", [])]
                blocking = [t for t in tags if any(b in t for b in BLOCKING_TAGS)]
                if blocking:
                    psql(client, f"UPDATE instagram_company_dm_state SET sequence_status = 'suppressed', reply_status = 'blocked_tag:{blocking[0]}', suppressed_at = NOW(), next_due_at = NULL, claim_owner = '', claimed_at = NULL, failure_reason = 'blocked_tag:{blocking[0]}', updated_at = NOW() WHERE id = {cid} AND claim_owner = '{RUN_ID}'", pg)
                    skipped += 1
                    suppressed = True
                    break
                conv, _ = ghl_get(f"/conversations/search?locationId={LOCATION_ID}&contactId={ghl_id}&lastMessageDirection=inbound&status=all&limit=1")
                time.sleep(0.5)
                if conv:
                    conversations = conv.get("conversations") or conv.get("items") or conv.get("data", {}).get("conversations") or conv.get("data", {}).get("items") or []
                    if conversations:
                        psql(client, f"UPDATE instagram_company_dm_state SET sequence_status = 'suppressed', reply_status = 'inbound_conversation', suppressed_at = NOW(), next_due_at = NULL, claim_owner = '', claimed_at = NULL, failure_reason = 'inbound_conversation', updated_at = NOW() WHERE id = {cid} AND claim_owner = '{RUN_ID}'", pg)
                        skipped += 1
                        suppressed = True
                        break
        if suppressed:
            continue

        msg = message_for(campaign, company)
        msg_hash = hashlib.sha256(msg.encode()).hexdigest()

        reserve = psql(client, f"INSERT INTO instagram_company_dm_send_log (state_id, campaign_key, message_step, message_text, message_hash, status, workflow_run_id, updated_at) VALUES ({cid}, '{campaign}', 1, '{msg.replace(chr(39), chr(39)+chr(39))}', '{msg_hash}', 'sending', '{RUN_ID}', NOW()) ON CONFLICT (state_id, message_step) DO NOTHING RETURNING id", pg)
        if not reserve.strip():
            psql(client, f"UPDATE instagram_company_dm_state SET claim_owner = '', claimed_at = NULL, updated_at = NOW() WHERE id = {cid} AND claim_owner = '{RUN_ID}'", pg)
            continue

        log_id = reserve.strip()
        resp, code = unipile_send(attendee_id, msg)
        if resp:
            msg_id = resp.get("message_id") or resp.get("id") or ""
            chat_id_val = resp.get("chat_id") or resp.get("object_id") or ""
            psql(client, f"UPDATE instagram_company_dm_send_log SET status = 'sent', unipile_message_id = '{msg_id}', unipile_chat_id = '{chat_id_val}', sent_at = NOW(), updated_at = NOW() WHERE id = {log_id}", pg)
            psql(client, f"UPDATE instagram_company_dm_state SET instagram_chat_id = CASE WHEN '{chat_id_val}' <> '' THEN '{chat_id_val}' ELSE instagram_chat_id END, message_step = 1, sequence_status = 'sent', started_at = COALESCE(started_at, NOW()), last_sent_at = NOW(), next_due_at = NULL, last_message_id = '{msg_id}', last_message_hash = '{msg_hash}', claim_owner = '', claimed_at = NULL, failu