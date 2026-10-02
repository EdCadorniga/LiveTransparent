"""Idempotent, batched backfill of the `linkedin_connected` GHL tag.

Context: the LinkedIn acceptance checker (3ttEvr5NMcQCS4Hp) never applied the
tag historically (systemic parse bug), and the workflows that set
`linkedin_connection_state = connected` (Relations Backfill VPiHfBwzOHaJnHBY,
State Sync ceaKnz6E3onQrZpt) only write the state table, not the GHL tag.

This tool is read-only in `--measure` mode and performs idempotent GHL tag
writes in `--apply` mode. It never sends LinkedIn messages and never mutates
the state table. Synthetic `linkedin:follower:` ids are always skipped.

Usage:
  python backfill_linkedin_connected_tag.py --measure
  python backfill_linkedin_connected_tag.py --apply [--tag linkedin_connected]

Ed pre-approved the bulk GHL tag write on 2026-10-02. Writes are idempotent
(adding an existing tag is a no-op) and rate-limited with 429/5xx retry.
"""

import argparse
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / ".env"
OUT_DIR = ROOT / "local-scripts"
GHL_BASE = "https://services.leadconnectorhq.com"
PG_CONTAINER = "postgres-uokgs4c04ko0s4scccg40cgg"
TAG_MAIN = "linkedin_connected"
TAG_PARTNER = "partner_linkedin_connected"

# connection_status values that imply the contact is a genuine 1st-degree
# connection (i.e. should carry the connected tag).
CONNECTED_STATUSES = ("connected", "completed")


def load_env():
    for raw in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _ssh_key():
    path = os.path.expandvars(os.path.expanduser(os.environ.get("VPS_SSH_KEY_PATH", "")))
    for cls in (paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey):
        try:
            return cls.from_private_key_file(path)
        except Exception:
            continue
    raise SystemExit("VPS SSH key load failed")


def pg_rows(sql, database="postgres"):
    """Run a SQL query over SSH and return split CSV lines (header + rows)."""
    host = os.environ.get("VPS_HOST") or os.environ.get("VPS_HOSTNAME")
    user = os.environ.get("VPS_USER")
    pgpass = os.environ.get("POSTGRES_PASSWORD", "")
    key = _ssh_key()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, pkey=key, timeout=20,
                   auth_timeout=20, banner_timeout=20,
                   look_for_keys=False, allow_agent=False)
    try:
        p = pgpass.replace("'", "'\\''")
        remote = (f"PGPASSWORD='{p}' docker exec -i {PG_CONTAINER} psql -U postgres -d {database} "
                  f"-v ON_ERROR_STOP=1 -X -q --csv 2>&1")
        stdin, stdout, stderr = client.exec_command(remote, timeout=180)
        stdin.write(sql)
        stdin.channel.shutdown_write()
        out = stdout.read().decode(errors="replace")
        err = stderr.read().decode(errors="replace")
    finally:
        client.close()
    if "ERROR:" in out or "ERROR:" in err:
        raise SystemExit("psql error:\n" + out + "\n" + err)
    return [ln for ln in out.splitlines() if ln.strip()]


def fetch_state_rows():
    """Return distinct real GHL contacts that correspond to connected state rows.

    Two sources:
      - state rows that already carry a real GHL contact id (`real_row`)
      - synthetic `linkedin:relation:<slug>` rows whose slug resolves to a real
        GHL contact via the shared `linkedin_contact_profile_index`
        (`resolved_slug`)
    Synthetic rows that resolve to no contact are skipped (nothing to tag).
    `linkedin:follower:`/`linkedin:relation:` ids are never treated as contacts.
    """
    statuses = "('connected','completed')"
    sql = (
        "WITH base AS ("
        "  SELECT ghl_contact_id AS cid, 'real_row' AS src, connection_status "
        "  FROM linkedin_connection_state "
        f"  WHERE connection_status IN {statuses} "
        "    AND ghl_contact_id NOT LIKE 'linkedin:%' "
        "  UNION ALL "
        "  SELECT i.ghl_contact_id AS cid, 'resolved_slug' AS src, s.connection_status "
        "  FROM linkedin_connection_state s "
        "  JOIN linkedin_contact_profile_index i "
        "    ON (i.normalized_profile_slug = s.linkedin_public_identifier "
        "        OR (COALESCE(s.linkedin_provider_id,'') <> '' AND s.linkedin_provider_id = ANY(i.linkedin_provider_ids))) "
        f"  WHERE s.connection_status IN {statuses} "
        "    AND s.ghl_contact_id LIKE 'linkedin:%' "
        "  UNION ALL "
        "  SELECT ghl_contact_id AS cid, 'partnership_real' AS src, connection_status "
        "  FROM partnership_linkedin_connection_state "
        f"  WHERE connection_status IN {statuses} "
        "    AND ghl_contact_id NOT LIKE 'linkedin:%' "
        ") "
        "SELECT cid, "
        "       bool_or(src LIKE 'partnership%') AS is_partnership, "
        "       bool_or(src = 'real_row') AS has_real_row, "
        "       bool_or(src = 'resolved_slug') AS has_resolved_slug, "
        "       max(connection_status) AS status "
        "FROM base "
        "WHERE cid IS NOT NULL AND cid <> '' AND cid NOT LIKE 'linkedin:%' "
        "GROUP BY cid ORDER BY cid;"
    )
    lines = pg_rows(sql)
    rows = []
    for ln in lines[1:]:
        parts = ln.split(",")
        if len(parts) < 5:
            continue
        rows.append({
            "contact_id": parts[0],
            "source": "partnership" if parts[1] == "t" else "main",
            "has_real_row": parts[2] == "t",
            "has_resolved_slug": parts[3] == "t",
            "status": parts[4],
        })
    return rows


def ghl_request(method, url, token, body=None, tries=4):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    for attempt in range(1, tries + 1):
        req = urllib.request.Request(url, data=data, method=method, headers={
            "Authorization": f"Bearer {token}",
            "Version": "2021-07-28",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "curl/8.0",
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8") or "{}")
        except urllib.error.HTTPError as e:
            code = e.code
            if code in (429, 500, 502, 503, 504) and attempt < tries:
                time.sleep(1.5 * attempt)
                continue
            try:
                payload = json.loads(e.read().decode("utf-8") or "{}")
            except Exception:
                payload = {}
            return code, payload
        except Exception as e:  # network
            if attempt < tries:
                time.sleep(1.5 * attempt)
                continue
            return 0, {"error": str(e)}
    return 0, {}


def get_contact(token, cid):
    return ghl_request("GET", f"{GHL_BASE}/contacts/{cid}", token)


def add_tags(token, cid, tags):
    return ghl_request("POST", f"{GHL_BASE}/contacts/{cid}/tags", token, {"tags": tags})


def tag_for(row, override=None):
    if override:
        return override
    return TAG_PARTNER if row["source"] == "partnership" else TAG_MAIN


def cmd_measure(rows, token):
    stats = {"total": len(rows), "tagged": 0, "untagged": 0, "not_found": 0,
             "by_status": {}, "untagged_ids": [], "not_found_ids": []}
    for i, row in enumerate(rows, 1):
        tag = tag_for(row)
        status, payload = get_contact(token, row["contact_id"])
        st = stats["by_status"].setdefault(row["status"], {"total": 0, "tagged": 0, "untagged": 0, "not_found": 0})
        st["total"] += 1
        if status == 200:
            contact = payload.get("contact", payload)
            tags = set(contact.get("tags") or [])
            if tag in tags:
                stats["tagged"] += 1
                st["tagged"] += 1
            else:
                stats["untagged"] += 1
                st["untagged"] += 1
                stats["untagged_ids"].append(row["contact_id"])
        else:
            stats["not_found"] += 1
            st["not_found"] += 1
            stats["not_found_ids"].append(row["contact_id"])
        if i % 100 == 0:
            print(f"  measured {i}/{len(rows)} ... tagged={stats['tagged']} untagged={stats['untagged']} not_found={stats['not_found']}", flush=True)
        time.sleep(0.15)
    return stats


def cmd_apply(rows, token, tag_override=None):
    stats = {"total": len(rows), "tagged": 0, "untagged_before": 0, "added": 0,
             "already": 0, "failed": 0, "not_found": 0, "failed_ids": [], "not_found_ids": []}
    for i, row in enumerate(rows, 1):
        tag = tag_for(row, tag_override)
        status, payload = get_contact(token, row["contact_id"])
        if status == 404:
            stats["not_found"] += 1
            stats["not_found_ids"].append(row["contact_id"])
            time.sleep(0.15)
            continue
        if status != 200:
            stats["failed"] += 1
            stats["failed_ids"].append(row["contact_id"])
            time.sleep(0.3)
            continue
        contact = payload.get("contact", payload)
        tags = set(contact.get("tags") or [])
        if tag in tags:
            stats["already"] += 1
        else:
            stats["untagged_before"] += 1
            code, resp = add_tags(token, row["contact_id"], [tag])
            if code in (200, 201):
                new_tags = set((resp.get("tags") if isinstance(resp, dict) else None) or [])
                if new_tags and tag not in new_tags:
                    stats["failed"] += 1
                    stats["failed_ids"].append(row["contact_id"])
                else:
                    stats["added"] += 1
            else:
                stats["failed"] += 1
                stats["failed_ids"].append(row["contact_id"])
            time.sleep(0.2)
        if i % 100 == 0:
            print(f"  applied {i}/{len(rows)} ... already={stats['already']} added={stats['added']} failed={stats['failed']}", flush=True)
        time.sleep(0.12)
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--tag", default=None, help="override tag name (testing)")
    args = ap.parse_args()
    if not args.measure and not args.apply:
        ap.error("choose --measure or --apply")

    load_env()
    token = os.environ["GHL_PIT"]
    print("Fetching connected/completed state rows from Postgres ...", flush=True)
    rows = fetch_state_rows()
    print(f"  {len(rows)} rows to process", flush=True)
    if not rows:
        print("nothing to do"); return

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if args.measure:
        stats = cmd_measure(rows, token)
        out = OUT_DIR / f"linkedin_connected_measure_{ts}.json"
        out.write_text(json.dumps(stats, indent=2), encoding="utf-8")
        print(json.dumps({k: v for k, v in stats.items() if not k.endswith("_ids")}, indent=2))
        print(f"detail: {out}")
    else:
        stats = cmd_apply(rows, token, args.tag)
        out = OUT_DIR / f"linkedin_connected_apply_{ts}.json"
        out.write_text(json.dumps(stats, indent=2), encoding="utf-8")
        print(json.dumps({k: v for k, v in stats.items() if not k.endswith("_ids")}, indent=2))
        print(f"detail: {out}")


if __name__ == "__main__":
    main()
