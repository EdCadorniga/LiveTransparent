"""Preserve and withdraw defective Classic LinkedIn invitations.

Default report only reads remote systems and writes a new local snapshot.
capture explicitly writes the ledger and installs a durable database sender hold.
withdraw requires --yes, a captured snapshot, and paused invite dispatchers.
There is deliberately no re-invite operation here.

  python scripts/linkedin/plan_john_invite_withdrawals.py
  python scripts/linkedin/plan_john_invite_withdrawals.py capture
  python scripts/linkedin/plan_john_invite_withdrawals.py withdraw --snapshot PATH
  python scripts/linkedin/plan_john_invite_withdrawals.py withdraw --snapshot PATH --yes --limit 10

Only run capture/live withdrawal after Ed confirms the scope and policy.
Secrets are read at runtime; exceptions and provider response bodies are not printed.
"""

import argparse
import csv
import hashlib
import json
import os
import random
import shlex
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import paramiko

from list_john_pending_invites import load_env
from enrich_john_invites_vertical import vertical_of

ROOT = Path(__file__).resolve().parents[2]
ACCOUNT = "V9eiHiDpRmCtan0YNdzsQw"
LOCATION = "Zwz4relUXVPxx8uohnjV"
PG_CONTAINER = "postgres-uokgs4c04ko0s4scccg40cgg"
N8N = "https://automations.livetransparent.com"
DISPATCHERS = ("fXxw5lanZcDmUrst", "crKIsaL5k3YBfqDZ", "Zt8p2aYtIuY0HK18")
NOTES = {
    "Alcohol": "Hi {first_name} - I help alcohol and spirits brands run compliant Meta/Google ads without the disapprovals and account limits. Would love to connect.",
    "Cannabis": "Hi {first_name} - I work with cannabis brands on compliant Meta/Google ads and in-store attribution. Would love to connect.",
    "Cannabis Dispensaries": "Hi {first_name} - I work with dispensaries on bringing in brand-funded ad budgets and verified foot-traffic attribution. Would love to connect.",
    "Crypto": "Hi {first_name} - I help crypto and fintech apps run compliant Meta/Google campaigns that don't get banned mid-scale. Would love to connect.",
    "Gambling": "Hi {first_name} - I help gambling and gaming brands run compliant Meta/Google campaigns that don't get banned mid-scale. Would love to connect.",
    "Mushroom": "Hi {first_name} - I help mushroom and functional-wellness brands run compliant Meta/Google ads without the disapprovals. Would love to connect.",
    "Nicotine": "Hi {first_name} - I help nicotine brands run compliant Meta/Google ads through the right account setup. Would love to connect.",
    "Peptides": "Hi {first_name} - I help peptide brands run compliant ads on Meta/Google without the constant account shutdowns. Would love to connect.",
}


class Stop(RuntimeError):
    """Safe, deliberately sanitized operational error."""


def sql_text(value):
    """UTF-8 hex keeps quotes/backslashes/Unicode out of SQL syntax."""
    return "convert_from(decode('%s','hex'),'UTF8')" % str(value).encode().hex()


def sql_nullable_text(value):
    """Absent provider text becomes SQL NULL, never the literal string 'None'."""
    return "NULL" if value is None else sql_text(value)


class Database:
    def __enter__(self):
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.RejectPolicy())
        key = os.path.expandvars(os.path.expanduser(os.environ["VPS_SSH_KEY_PATH"]))
        self.client.connect(
            hostname=os.environ.get("VPS_HOST") or os.environ["VPS_HOSTNAME"],
            username=os.environ["VPS_USER"], key_filename=key,
            timeout=20, look_for_keys=False, allow_agent=False,
        )
        return self

    def __exit__(self, *args):
        self.client.close()

    def execute(self, sql):
        command = (f"docker exec -i {shlex.quote(PG_CONTAINER)} "
                   "psql -U postgres -d postgres -X -q -tA -v ON_ERROR_STOP=1")
        stdin, stdout, stderr = self.client.exec_command(command, timeout=180)
        stdin.write("SET standard_conforming_strings=on;\n" + sql + "\n")
        stdin.flush()
        stdin.channel.shutdown_write()
        out = stdout.read().decode("utf-8")
        stderr.read()
        if stdout.channel.recv_exit_status() != 0:
            # psql errors can include whole SQL statements/raw contact data.
            raise Stop("Postgres operation failed; no provider write may follow.")
        return out.strip()

    def execute_statements(self, statements, timeout=1800):
        """Run many statements in ONE psql session (and therefore one transaction).

        Used for large captures: the payload is written in chunks so a multi-megabyte
        script cannot exhaust the SSH channel buffer, while BEGIN/COMMIT still wrap
        the whole batch atomically.
        """
        command = (f"docker exec -i {shlex.quote(PG_CONTAINER)} "
                   "psql -U postgres -d postgres -X -q -tA -v ON_ERROR_STOP=1")
        stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
        stdin.write("SET standard_conforming_strings=on;\n")
        buffer, size = [], 0
        for statement in statements:
            buffer.append(statement)
            size += len(statement) + 1
            if size >= 262144:
                stdin.write("\n".join(buffer) + "\n")
                buffer, size = [], 0
                stdin.flush()
        if buffer:
            stdin.write("\n".join(buffer) + "\n")
        stdin.flush()
        stdin.channel.shutdown_write()
        out = stdout.read().decode("utf-8")
        stderr.read()
        if stdout.channel.recv_exit_status() != 0:
            raise Stop("Postgres operation failed; no provider write may follow.")
        return out.strip()

    def rows(self, select):
        out = self.execute(f"SELECT COALESCE(json_agg(t),'[]'::json) FROM ({select}) t;")
        return json.loads(out)


def request_once(method, url, headers):
    req = urllib.request.Request(url, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            data = response.read().decode("utf-8")
            return response.status, json.loads(data or "{}")
    except urllib.error.HTTPError as error:
        try:
            body = json.loads(error.read().decode("utf-8"))
        except (ValueError, UnicodeError):
            body = {}
        return error.code, body
    except (ValueError, OSError):
        # Never automatically retry a DELETE whose outcome is uncertain.
        raise Stop("Network/response failure; provider outcome may be uncertain.") from None


def request(method, url, headers):
    for attempt in range(4):
        code, body = request_once(method, url, headers)
        if method != "GET" or code not in (429, 500, 502, 503, 504) or attempt == 3:
            return code, body
        time.sleep(2 * (attempt + 1))


def unipile(method, path, params=None):
    base = os.environ["UNIPILE_API_BASE_URL"].rstrip("/")
    parsed = urllib.parse.urlparse(base)
    if parsed.scheme != "https" or not parsed.hostname or not parsed.hostname.endswith(".unipile.com") or not parsed.path.endswith("/api/v1"):
        raise Stop("Expected an HTTPS Unipile Classic /api/v1 base.")
    query = urllib.parse.urlencode({"account_id": ACCOUNT, **(params or {})})
    return request(method, f"{base}{path}?{query}",
                   {"X-API-KEY": os.environ["UNIPILE_TOKEN"], "Accept": "application/json"})


def pending_invites():
    items, ids, cursors, cursor = [], set(), set(), None
    for _ in range(200):
        code, body = unipile("GET", "/users/invite/sent", {"limit": 100, **({"cursor": cursor} if cursor else {})})
        if code != 200 or not isinstance(body, dict) or not isinstance(body.get("items"), list):
            raise Stop(f"Pending-invitation read failed (HTTP {code}).")
        for item in body["items"]:
            iid = str(item.get("id") or "")
            if not iid or iid in ids:
                raise Stop("Missing/duplicate invitation ID; pagination is not accepted.")
            ids.add(iid)
            items.append(item)
        cursor = body.get("cursor")
        if not cursor:
            return items
        if cursor in cursors or not body["items"]:
            raise Stop("Stalled invitation cursor; incomplete list rejected.")
        cursors.add(cursor)
        time.sleep(0.25)
    raise Stop("Invitation page budget exhausted; incomplete list rejected.")


def send_day(invitation):
    """Calendar day the provider reports for the invitation (date part only)."""
    raw = str(invitation.get("parsed_datetime") or "")
    return raw[:10] if len(raw) >= 10 else ""


def issue_of(invitation, before_date=None):
    """Classify one invitation.

    Note-based modes (john_note / mojibake) are the default. When before_date is
    given, the scope is purely calendar-based: every invitation sent strictly
    before that day is in scope regardless of the note it carries.
    """
    if before_date:
        day = send_day(invitation)
        if not day:
            return ""
        return "pre_cutoff_date" if day < before_date else ""
    text = str(invitation.get("invitation_text") or "").lower()
    if "john here" in text:
        return "john_note"
    if '"ameron' in text and "co-fo'nder" in text:
        return "mojibake"
    return ""


def matching_identity(alias="s", invitation=None, cid=""):
    invitation = invitation or {}
    pub = str(invitation.get("invited_user_public_id") or "").strip().lower()
    provider = str(invitation.get("invited_user_id") or "")
    terms = []
    if cid:
        terms.append(f"{alias}.ghl_contact_id={sql_text(cid)}")
    if pub:
        terms.append(f"lower({alias}.linkedin_public_identifier)={sql_text(pub)}")
    if provider:
        terms.append(f"{alias}.linkedin_provider_id={sql_text(provider)}")
    return "(" + " OR ".join(terms or ["false"]) + ")"


def collect(db, invitations, include_mojibake, before_date=None):
    index = db.rows("SELECT ghl_contact_id, normalized_profile_slug, linkedin_provider_ids FROM linkedin_contact_profile_index")
    states = db.rows(f"SELECT * FROM linkedin_connection_state WHERE unipile_account_id={sql_text(ACCOUNT)}")
    cache, rows = {}, []
    for invitation in invitations:
        issue = issue_of(invitation, before_date)
        if not issue or (issue == "mojibake" and not include_mojibake):
            continue
        pub = str(invitation.get("invited_user_public_id") or "").strip().lower()
        pid = str(invitation.get("invited_user_id") or "")
        matched_states = [s for s in states if (pub and str(s.get("linkedin_public_identifier") or "").lower() == pub) or (pid and s.get("linkedin_provider_id") == pid)]
        candidates = {i["ghl_contact_id"] for i in index if (pub and i.get("normalized_profile_slug") == pub) or (pid and pid in (i.get("linkedin_provider_ids") or []))}
        candidates.update(s["ghl_contact_id"] for s in matched_states)
        candidates = sorted(c for c in candidates if c and not c.startswith("linkedin:"))
        raw_contacts = {}
        for cid in candidates:
            if cid not in cache:
                code, body = request("GET", f"https://services.leadconnectorhq.com/contacts/{urllib.parse.quote(cid, safe='')}", {
                    "Authorization": "Bearer " + os.environ["GHL_PIT"], "Version": "2021-07-28",
                    "Accept": "application/json", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0",
                })
                if code == 404:
                    # Contact no longer exists in GHL; there is nothing to preserve.
                    cache[cid] = None
                elif code != 200 or body.get("contact", {}).get("id") != cid or body["contact"].get("locationId") != LOCATION:
                    raise Stop(f"GHL contact preservation failed (HTTP {code}); snapshot rejected.")
                else:
                    cache[cid] = body
                time.sleep(0.25)
            if cache[cid] is not None:
                raw_contacts[cid] = cache[cid]
        alive = [c for c in candidates if cache.get(c) is not None]
        cid = alive[0] if len(alive) == 1 else ""
        contact = raw_contacts.get(cid, {})
        vertical = vertical_of(contact).strip() if cid else ""
        first = str(contact.get("contact", {}).get("firstName") or "").strip()
        note = NOTES.get(vertical or "Cannabis", "")
        review = not cid or not first or not note or any(s.get("connected_at") or s.get("connection_status") in ("connected", "completed") for s in matched_states)
        # Store a template, not a GHL-derived greeting to be sent blindly later.
        rows.append({
            "invitation_id": str(invitation["id"]), "issue": issue,
            "ghl_contact_id": cid, "candidate_contact_ids": candidates,
            "candidate_verticals": {candidate: vertical_of(payload).strip() for candidate, payload in raw_contacts.items()},
            "first_name": first, "vertical": vertical,
            "reinvite_status": "needs_review" if review else "pending",
            "reinvite_message": note, "raw_invitation": invitation,
            "raw_ghl_contact": contact or raw_contacts,
            "raw_connection_states": matched_states,
            "sent_day": send_day(invitation),
        })
    return rows


def save_snapshot(rows, args, total):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    directory = ROOT / "local-scripts" / "linkedin-invite-withdrawals"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{args.mode}-{stamp}.json"
    document = {"schema_version": 1, "account_id": ACCOUNT, "created_at": datetime.now(timezone.utc).isoformat(),
                "cooldown_days": args.cooldown_days, "include_mojibake": args.include_mojibake,
                "before_date": args.before_date,
                "reinvite_owner": args.reinvite_owner, "total_pending": total, "rows": rows}
    with path.open("x", encoding="utf-8") as f:
        json.dump(document, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    fields = ("invitation_id", "issue", "ghl_contact_id", "first_name", "vertical", "reinvite_status", "reinvite_message")
    with path.with_suffix(".csv").open("x", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        f.flush()
        os.fsync(f.fileno())
    return path


DDL = """
CREATE TABLE IF NOT EXISTS linkedin_invitation_withdrawals (
  unipile_account_id text NOT NULL, invitation_id text NOT NULL,
  invited_user text, invited_user_public_id text, invited_user_provider_id text,
  ghl_contact_id text, candidate_contact_ids jsonb NOT NULL,
  first_name text, vertical text, linkedin_profile_url text,
  old_invitation_text text, old_invitation_sent_at text, issue text NOT NULL,
  withdraw_status text NOT NULL DEFAULT 'pending'
    CHECK (withdraw_status IN ('pending','withdrawing','withdrawn','already_gone','failed','skipped','uncertain')),
  withdraw_http_status integer, withdrawn_at timestamptz, cooldown_until timestamptz,
  cooldown_days integer NOT NULL CHECK (cooldown_days > 0),
  reinvite_status text NOT NULL CHECK (reinvite_status IN ('pending','sent','failed','skipped','needs_review')),
  reinvite_owner text NOT NULL, reinvite_message text, reinvite_invitation_id text, reinvited_at timestamptz,
  last_error text, raw_invitation jsonb NOT NULL, raw_ghl_contact jsonb NOT NULL,
  raw_connection_states jsonb NOT NULL, snapshot_path text NOT NULL, snapshot_sha256 text NOT NULL,
  dispatcher_hold boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (unipile_account_id, invitation_id)
);
CREATE INDEX IF NOT EXISTS linkedin_withdrawal_hold_idx
 ON linkedin_invitation_withdrawals (unipile_account_id, invited_user_public_id) WHERE dispatcher_hold;
CREATE OR REPLACE FUNCTION lt_invitation_withdrawal_hold() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.connection_status IN ('ready','requested_pending') AND EXISTS (
    SELECT 1 FROM linkedin_invitation_withdrawals w
    WHERE w.dispatcher_hold AND w.unipile_account_id=NEW.unipile_account_id
      AND ((w.ghl_contact_id<>'' AND w.ghl_contact_id=NEW.ghl_contact_id)
        OR w.candidate_contact_ids ? NEW.ghl_contact_id
        OR (w.invited_user_public_id<>'' AND lower(w.invited_user_public_id)=lower(NEW.linkedin_public_identifier))
        OR (w.invited_user_provider_id<>'' AND w.invited_user_provider_id=NEW.linkedin_provider_id))
  ) THEN
    RAISE EXCEPTION 'Invitation cleanup hold blocks automated queue entry';
  END IF;
  RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS lt_invitation_withdrawal_hold ON linkedin_connection_state;
CREATE TRIGGER lt_invitation_withdrawal_hold BEFORE INSERT OR UPDATE ON linkedin_connection_state
 FOR EACH ROW EXECUTE FUNCTION lt_invitation_withdrawal_hold();
DROP TRIGGER IF EXISTS lt_invitation_withdrawal_hold ON partnership_linkedin_connection_state;
CREATE TRIGGER lt_invitation_withdrawal_hold BEFORE INSERT OR UPDATE ON partnership_linkedin_connection_state
 FOR EACH ROW EXECUTE FUNCTION lt_invitation_withdrawal_hold();
"""


def paused_dispatchers():
    """Verify every invite dispatcher is inactive and quiescent.

    n8n-lt occasionally answers the executions endpoint with a transient error, so
    the check is retried before it is allowed to block a withdrawal.
    """
    reason = "unknown"
    for attempt in range(5):
        verified = True
        for wid in DISPATCHERS:
            code, workflow = request("GET", f"{N8N}/api/v1/workflows/{wid}", {
                "X-N8N-API-KEY": os.environ["N8N_LT_API_KEY"], "Accept": "application/json",
            })
            if code != 200 or workflow.get("id") != wid or workflow.get("active") is not False or workflow.get("activeVersionId"):
                reason = f"dispatcher {wid} not verifiably inactive (HTTP {code})"
                verified = False
                break
            code, executions = request("GET", f"{N8N}/api/v1/executions?workflowId={wid}&limit=100", {
                "X-N8N-API-KEY": os.environ["N8N_LT_API_KEY"], "Accept": "application/json",
            })
            if code != 200 or not isinstance(executions.get("data"), list):
                reason = f"dispatcher {wid} executions unreadable (HTTP {code})"
                verified = False
                break
            if any(e.get("status") in ("new", "running", "waiting", "unknown") for e in executions["data"]):
                reason = f"dispatcher {wid} has non-terminal executions"
                verified = False
                break
        if verified:
            return
        time.sleep(5 * (attempt + 1))
    raise Stop(f"Invite dispatcher pause could not be verified on n8n-lt: {reason}.")


def capture(db, rows, path, args):
    paused_dispatchers()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    statements = ["BEGIN; SELECT pg_advisory_xact_lock(102612153);", DDL]
    for row in rows:
        inv = row["raw_invitation"]
        values = {
            "unipile_account_id": ACCOUNT, "invitation_id": row["invitation_id"],
            "invited_user": inv.get("invited_user", ""), "invited_user_public_id": inv.get("invited_user_public_id", ""),
            "invited_user_provider_id": inv.get("invited_user_id", ""), "ghl_contact_id": row["ghl_contact_id"],
            "first_name": row["first_name"], "vertical": row["vertical"],
            "linkedin_profile_url": "https://www.linkedin.com/in/" + str(inv.get("invited_user_public_id") or ""),
            "old_invitation_text": inv.get("invitation_text", ""), "old_invitation_sent_at": inv.get("parsed_datetime") or inv.get("date", ""),
            "issue": row["issue"], "reinvite_status": row["reinvite_status"], "reinvite_message": row["reinvite_message"],
            "cooldown_days": args.cooldown_days, "reinvite_owner": args.reinvite_owner,
            "snapshot_path": str(path), "snapshot_sha256": digest,
        }
        nullable = ("invited_user", "invited_user_public_id", "invited_user_provider_id", "old_invitation_text")
        expressions = [(sql_nullable_text(v) if k in nullable else sql_text(v)) + ("::integer" if k == "cooldown_days" else "")
                       for k, v in values.items()]
        for key in ("raw_invitation", "raw_ghl_contact", "raw_connection_states", "candidate_contact_ids"):
            values[key] = row[key]
            expressions.append(sql_text(json.dumps(row[key], ensure_ascii=False)) + "::jsonb")
        statements.append(f"INSERT INTO linkedin_invitation_withdrawals ({','.join(values)}) VALUES ({','.join(expressions)}) "
                          "ON CONFLICT (unipile_account_id,invitation_id) DO NOTHING;")
    statements.append("COMMIT;")
    db.execute_statements(statements)
    # Read back full original ledger records, including any pre-existing captures.
    ledger = db.rows(f"SELECT * FROM linkedin_invitation_withdrawals WHERE unipile_account_id={sql_text(ACCOUNT)}")
    backup = path.with_suffix(".ledger.json")
    with backup.open("x", encoding="utf-8") as f:
        json.dump(ledger, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    by_id = {r["invitation_id"]: r for r in ledger}
    if any(r["invitation_id"] not in by_id or by_id[r["invitation_id"]]["raw_invitation"] != r["raw_invitation"] for r in rows):
        raise Stop("Capture readback mismatch; withdrawal prohibited. Original capture retained.")


def journal(path, event):
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"at": datetime.now(timezone.utc).isoformat(), **event}, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def summary(document, path, mode):
    rows = document["rows"]
    return {"mode": mode, "total_pending": document["total_pending"], "selected": len(rows),
            "scope_before_date": document.get("before_date"),
            "issues": dict(Counter(r["issue"] for r in rows)),
            "send_days": dict(sorted(Counter(r.get("sent_day") or "unknown" for r in rows).items())),
            "verticals": dict(Counter(r["vertical"] or "(blank/unmatched)" for r in rows)),
            "needs_review": sum(r["reinvite_status"] == "needs_review" for r in rows),
            "review_details": [{"invitation_id": r["invitation_id"],
                                "public_id": r["raw_invitation"].get("invited_user_public_id"),
                                "candidate_contacts": len(r["candidate_contact_ids"]),
                                "candidate_verticals": r.get("candidate_verticals", {}),
                                "resolution": "ambiguous" if len(r["candidate_contact_ids"]) > 1 else "unmatched" if not r["candidate_contact_ids"] else "name/vertical/state_review"}
                               for r in rows if r["reinvite_status"] == "needs_review"],
            "snapshot": str(path)}


def finalize(db, row, status, code, days, error=""):
    where = f"unipile_account_id={sql_text(ACCOUNT)} AND invitation_id={sql_text(row['invitation_id'])}"
    sql = ["BEGIN; SELECT pg_advisory_xact_lock(102612153);"]
    timing = f", withdrawn_at=now(), cooldown_until=now()+make_interval(days=>{days})" if status == "withdrawn" else ""
    sql.append(f"UPDATE linkedin_invitation_withdrawals SET withdraw_status={sql_text(status)}, withdraw_http_status={int(code)}, "
               f"last_error={sql_text(error)}, updated_at=now(){timing}, "
               f"reinvite_status=CASE WHEN {sql_text(status)}='withdrawn' THEN reinvite_status ELSE 'needs_review' END WHERE {where};")
    if status == "withdrawn":
        payload = {"invite_withdrawn": True, "invitation_cleanup_hold": True, "withdrawn_invitation_id": row["invitation_id"]}
        for table in ("linkedin_connection_state", "partnership_linkedin_connection_state"):
            sql.append(f"UPDATE {table} s SET request_sent_at=now(), updated_at=now(), "
                       "connection_status=CASE WHEN connection_status IN ('ready','requested_pending') THEN 'requested' ELSE connection_status END, "
                       f"payload_json=COALESCE(payload_json,'{{}}'::jsonb)||{sql_text(json.dumps(payload))}::jsonb||"
                       f"jsonb_build_object('reinvite_due',now()+make_interval(days=>{days})) "
                       f"WHERE s.unipile_account_id={sql_text(ACCOUNT)} AND {matching_identity('s', row['raw_invitation'], row['ghl_contact_id'])} "
                       "AND connected_at IS NULL AND connection_status NOT IN ('connected','completed');")
    sql.append("COMMIT;")
    db.execute("\n".join(sql))


def withdraw(db, args):
    path = Path(args.snapshot).resolve()
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("schema_version") != 1 or document.get("account_id") != ACCOUNT:
        raise Stop("Snapshot schema/account mismatch.")
    before_date = document.get("before_date") or None
    ledger = db.rows(f"SELECT * FROM linkedin_invitation_withdrawals WHERE unipile_account_id={sql_text(ACCOUNT)}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    ids = {r["invitation_id"] for r in document["rows"]}
    selected = [r for r in ledger if r["invitation_id"] in ids and r["withdraw_status"] == "pending"]
    if any(r["snapshot_sha256"] != digest or r["snapshot_path"] != str(path) or not r["dispatcher_hold"] for r in selected):
        raise Stop("Withdrawal requires the original immutable capture snapshot and hold.")
    if ids - {r["invitation_id"] for r in ledger}:
        raise Stop("Snapshot contains uncaptured invitations.")
    # Oldest invitation first, then by ID, so a resumed run is deterministic.
    selected.sort(key=lambda r: (str(r.get("old_invitation_sent_at") or ""), str(r["invitation_id"])))
    paused_dispatchers()
    # Verify the hold is installed on both queues before any DELETE.
    guards = db.rows("SELECT tgrelid::regclass::text AS table_name FROM pg_trigger WHERE tgname='lt_invitation_withdrawal_hold' AND tgenabled='O'")
    if not {"linkedin_connection_state", "partnership_linkedin_connection_state"}.issubset({g["table_name"] for g in guards}):
        raise Stop("Durable dispatcher hold is missing/disabled.")
    pending = {str(i["id"]): i for i in pending_invites()}
    selected = selected[:args.limit]
    print(json.dumps({"mode": "withdraw" if args.yes else "withdraw_dry_run", "batch": len(selected),
                      "still_pending": sum(r["invitation_id"] in pending for r in selected), "snapshot": str(path)}, indent=2))
    if not args.yes:
        return
    log = path.with_name(path.stem + "-" + uuid.uuid4().hex[:8] + ".withdrawal.jsonl")
    for row in selected:
        iid = row["invitation_id"]
        inv = pending.get(iid)
        if not inv:
            journal(log, {"invitation_id": iid, "result": "already_gone"})
            finalize(db, row, "already_gone", 0, row["cooldown_days"], "Absent before DELETE; acceptance/withdrawal unconfirmed")
            continue
        if inv != row["raw_invitation"]:
            # Provider may update ancillary metadata: require note and target identity unchanged.
            keys = ("id", "invitation_text", "invited_user_public_id", "invited_user_id")
            if any(str(inv.get(k) or "") != str(row["raw_invitation"].get(k) or "") for k in keys):
                raise Stop("Live invitation identity/note changed; stop and recapture/review.")
        if issue_of(inv, before_date) != row["issue"]:
            raise Stop("Live invitation is outside the captured defect scope.")
        current = db.rows(f"SELECT * FROM linkedin_connection_state s WHERE s.unipile_account_id={sql_text(ACCOUNT)} AND {matching_identity('s', inv, row['ghl_contact_id'])}")
        if any(s.get("connected_at") or s.get("connection_status") in ("connected", "completed") for s in current):
            finalize(db, row, "skipped", 0, row["cooldown_days"], "Connected/terminal state requires review")
            continue
        paused_dispatchers()
        journal(log, {"invitation_id": iid, "phase": "before_delete", "raw_invitation": inv})
        # Atomic claim avoids two operators withdrawing the same captured row.
        claimed = json.loads(db.execute(
            "WITH claimed AS (UPDATE linkedin_invitation_withdrawals SET withdraw_status='withdrawing', updated_at=now() "
            f"WHERE unipile_account_id={sql_text(ACCOUNT)} AND invitation_id={sql_text(iid)} AND withdraw_status='pending' RETURNING invitation_id) "
            "SELECT COALESCE(json_agg(claimed),'[]'::json) FROM claimed;"))
        if not claimed:
            raise Stop("Invitation already claimed by another operator; stopping.")
        try:
            code, body = unipile("DELETE", "/users/invite/sent/" + urllib.parse.quote(iid, safe=""))
        except Stop:
            journal(log, {"invitation_id": iid, "result": "uncertain", "http_status": 0})
            finalize(db, row, "uncertain", 0, row["cooldown_days"], "Network/response uncertainty; do not replay")
            raise
        ok = 200 <= code < 300 and isinstance(body, dict) and body.get("object") == "InvitationCanceled"
        status = "withdrawn" if ok else "uncertain"
        journal(log, {"invitation_id": iid, "result": status, "http_status": code})
        # Any non-confirmation (including restrictions/429/404) halts the batch, no retries.
        finalize(db, row, status, code, row["cooldown_days"], "" if ok else "DELETE not confirmed; review provider before retry")
        if not ok:
            raise Stop(f"DELETE not confirmed (HTTP {code}); batch stopped, hold retained.")
        # Fixed spacing with a little jitter: keeps the average pacing while
        # avoiding a perfectly metronomic request pattern.
        time.sleep(args.delay + random.uniform(0.0, max(0.5, args.delay * 0.15)))
    verified = {str(i["id"]) for i in pending_invites()}
    written = db.rows(f"SELECT invitation_id FROM linkedin_invitation_withdrawals WHERE unipile_account_id={sql_text(ACCOUNT)} AND withdraw_status='withdrawn'")
    if any(r["invitation_id"] in verified for r in written):
        raise Stop("Provider readback still lists a withdrawn invite; reconcile before continuing.")
    print(json.dumps({"provider_readback": "passed", "journal": str(log)}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", nargs="?", default="report", choices=("report", "capture", "withdraw"))
    parser.add_argument("--include-mojibake", action="store_true")
    parser.add_argument("--before-date", default=None,
                        help="Calendar scope: withdraw every pending invitation sent strictly before this YYYY-MM-DD day")
    parser.add_argument("--cooldown-days", type=int, default=22,
                        help="Days after confirmed withdrawal (default 22: LinkedIn's three weeks plus one day)")
    parser.add_argument("--reinvite-owner", choices=("undecided", "ledger-script", "vertical-dispatcher"), default="undecided")
    parser.add_argument("--snapshot", help="Original capture JSON for withdraw; offline snapshot summary for report")
    parser.add_argument("--yes", action="store_true", help="Explicit approval to execute live DELETEs")
    parser.add_argument("--limit", type=int, default=10, help="Maximum invitations examined in one withdrawal batch")
    parser.add_argument("--delay", type=float, default=30.0,
                        help="Seconds between confirmed withdrawals (default 30, per Ed's pacing rule)")
    args = parser.parse_args()
    if args.cooldown_days < 1 or not 1 <= args.limit <= 100 or args.delay < 1:
        parser.error("Positive cooldown, limit 1..100 and delay >=1 second required")
    if args.before_date is not None:
        try:
            datetime.strptime(args.before_date, "%Y-%m-%d")
        except ValueError:
            parser.error("--before-date must be YYYY-MM-DD")
        args.before_date = args.before_date.strip()
    if args.yes and args.mode != "withdraw":
        parser.error("--yes is valid only with withdraw")
    if args.mode == "withdraw" and not args.snapshot:
        parser.error("withdraw requires --snapshot from capture")
    if args.mode == "capture" and args.snapshot:
        parser.error("capture always takes a fresh remote snapshot")
    if args.mode == "report" and args.snapshot:
        path = Path(args.snapshot).resolve()
        document = json.loads(path.read_text(encoding="utf-8"))
        if document.get("schema_version") != 1 or document.get("account_id") != ACCOUNT:
            raise Stop("Snapshot schema/account mismatch.")
        print(json.dumps(summary(document, path, "offline_snapshot_report"), indent=2))
        return
    load_env()
    if os.environ.get("UNIPILE_ACCOUNT_ID") != ACCOUNT:
        raise Stop("Configured account does not match the authorized Classic account.")
    with Database() as db:
        if args.mode == "withdraw":
            withdraw(db, args)
            return
        invitations = pending_invites()
        rows = collect(db, invitations, args.include_mojibake, args.before_date)
        path = save_snapshot(rows, args, len(invitations))
        if args.mode == "capture":
            capture(db, rows, path, args)
        result = summary({"rows": rows, "total_pending": len(invitations), "before_date": args.before_date},
                          path, args.mode)
        result["mojibake_pending"] = sum(issue_of(i) == "mojibake" for i in invitations)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Stop as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Stopped ({type(exc).__name__}); inspect locally without printing credentials.", file=sys.stderr)
        sys.exit(1)
