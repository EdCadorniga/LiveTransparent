"""Read-only Postgres schema inventory for the developer transition (2026-11-05).

Connects to the VPS with the documented Ed25519 key and runs psql INSIDE the shared
Postgres container via `docker exec` (no database password is transmitted; container-local
trust). Guards:
  - SELECTs and catalog queries only; nothing is created, altered, or deleted.
  - Emits structural metadata ONLY: database names, schemata, table/view names,
    column NAMES + types, approximate rowcounts from pg_stat_user_tables.
  - Never reads or prints table data, role passwords, or connection strings.
Output: docs/transition/postgres-schema-inventory-2026-11-05.md
"""

import os
import datetime

import paramiko

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "postgres-schema-inventory-2026-11-05.md")
VPS_HOST = "89.117.21.29"
VPS_USER = "root"
KEY_PATH = os.path.expanduser(r"~\.ssh\local-upload")

QUERIES = {
    "databases": "SELECT datname FROM pg_database WHERE NOT datistemplate ORDER BY 1;",
    "schemas": "SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT LIKE 'pg_%' AND schema_name <> 'information_schema' ORDER BY 1;",
    "tables": "SELECT schemaname || '|' || relname || '|' || COALESCE(n_live_tup::text,'0') || '|' || COALESCE(last_analyze::text,'never') FROM pg_stat_user_tables WHERE schemaname NOT IN ('pg_catalog','information_schema') ORDER BY 1;",
    "views": "SELECT schemaname || '|' || viewname FROM pg_views WHERE schemaname NOT IN ('pg_catalog','information_schema') ORDER BY 1;",
    "columns": "SELECT table_schema || '|' || table_name || '|' || string_agg(column_name || ' ' || data_type, ', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_schema NOT IN ('pg_catalog','information_schema') GROUP BY 1 ORDER BY 1;",
}


def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, key_filename=KEY_PATH, timeout=30)

    _, out, _ = ssh.exec_command("docker ps --format '{{.Names}}\\t{{.Image}}' | grep -i postgres | head -5")
    pg_lines = [l.strip() for l in out.read().decode().splitlines() if l.strip()]
    print("pg containers:", pg_lines)
    container = None
    for l in pg_lines:
        name = l.split("\t")[0].split()[0]
        # Prefer the project's shared postgres (Coolify service postgres-shared),
        # not Coolify's internal panel database.
        if "uokgs4c04ko0s4scccg40cgg" in name:
            container = name
            break
    if not container:
        # fall back to the non-coolify-db postgres container
        for l in pg_lines:
            name = l.split("\\t")[0]
            if name.lower() != "coolify-db":
                container = name
                break
    if not container:
        raise SystemExit("no postgres container found")

    print("using container:", container)

    def psql(db, sql):
        cmd = f"docker exec {container} psql -X -q -U postgres -d {db} -At -c \"{sql}\""
        _, out_, err = ssh.exec_command(cmd, timeout=120)
        o = out_.read().decode("utf-8", errors="replace")
        e = err.read().decode("utf-8", errors="replace")
        return o, e

    lines = ["# Postgres schema inventory — 2026-11-05", "",
             "Read-only `docker exec psql` catalog queries against the shared Postgres container",
             "(container-local trust; no credentials transmitted). Structural metadata only:",
             "database/schema/table/view NAMES, column NAMES+TYPES, and approximate row counts from",
             "pg_stat_user_tables. **Row counts are planner estimates and 'never' last_analyze is",
             "common on this instance, so counts may be far from reality — treat as indicative",
             "only.** No table data was read. No database object was created, altered, or deleted.",
             ""]

    consumers = [
        ("report_raw_ghl_* / report_daily_summary / report_stage_* / report_ghl_social_statistics",
         "LT - GHL Daily Leads/Sales/Calls/Appointments/Social ingest workflows; Report Daily Rollups; Report QA; Pipeline Velocity; Report Executive Summary API; Report Campaign Channel Summary; Report Outgoing Calls; Executive Report V1 Facts"),
        ("linkedin_connection_state / linkedin_activity_events / linkedin_conversation_map / linkedin_contact_profile_*",
         "LT - GHL LinkedIn Connect Dispatcher; LinkedIn DM Sequence; Connection State Sync/Upsert; Acceptance Checker; Reply Backfill; Relations Backfill; DM Suppression; History Sync"),
        ("partnership_linkedin_connection_state / partnership_release_log",
         "LT - Partnership LinkedIn Dispatcher/DM; LT - Partnership Email Dispatcher; Campaign Channel Summary"),
        ("Emerald_Campaign_Contacts / Emerald_Release_Log / Email_Events",
         "LT - Emerald Campaign Sender Release Dispatcher; LT - Email Event Ingest; LT - Emerald Campaign Snapshot -> Postgres Ingest"),
        ("DAN_Release_Log / ColdOutreach_Release_Log / SimpleTexting_*",
         "LT - DAN Campaign Sender Release Dispatcher; DAN/ColdOutreach partner flows; SimpleTexting campaign/sender workflows"),
        ("linkedin_invitation_withdrawals",
         "Pull-based cleanup tool (`scripts/linkedin/plan_john_invite_withdrawals.py`) + dispatcher_hold checks in state sync/callers"),
        ("lt_* campaign/ledger tables",
         "Campaign/booking/attribution/intake workflows named `LT - *` + GHL webhook callers"),
        ("n8n database (separate DB `n8n`)",
         "n8n Community Edition instance's own tables (execution/entity tables) — maintained by n8n; do not edit directly"),
    ]

    for db in ("postgres", "n8n"):
        lines.append(f"## Database `{db}`")
        dbs, err = psql("postgres", QUERIES["databases"])
        if db == "postgres":
            lines.append("- databases present: " + ", ".join(x for x in dbs.splitlines() if x.strip()))
            if err.strip():
                lines.append(f"  - (error: {err.strip()[:200]})")
        s, e = psql(db, QUERIES["schemas"])
        lines.append("- schemata: " + ", ".join(x for x in s.splitlines() if x.strip()))
        t, e2 = psql(db, QUERIES["tables"])
        lines.append("- tables (schema|name|approx_rows|last_analyze):")
        for x in t.splitlines():
            if x.strip():
                lines.append(f"  - {x.strip()}")
        v, _ = psql(db, QUERIES["views"])
        lines.append("- views (schema|name):")
        for x in v.splitlines():
            if x.strip():
                lines.append(f"  - {x.strip()}")
        c, _ = psql(db, QUERIES["columns"])
        lines.append("- columns by table (schema|table: name type, ...):")
        for x in c.splitlines():
            if x.strip():
                lines.append(f"  - {x.strip()}")

    lines += ["", "## Map to consuming systems (mapped from dated project evidence; verify before operational decisions)", ""]
    for tgt, users in consumers:
        lines.append(f"- `{tgt}` — consumed by: {users}")

    lines += ["", "## Notes",
              "- Approximate row counts (`n_live_tup`) are planner estimates; most tables show",
              "  `never`/outdated ANALYZE timestamps on this instance, so counts are indicative",
              "  only and should not be quoted as report facts.",
              "- Only two user databases exist: `postgres` (project data) and `n8n` (n8n CE runtime).",
              "- No scheduled backup configuration was found via the Coolify API (see",
              "  `coolify-saved-config-2026-11-05.md`); backup/restore acceptance for these data is",
              "  still open."]

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", OUT)
    ssh.close()


if __name__ == "__main__":
    main()
