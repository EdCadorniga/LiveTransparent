"""Read only: inspect the n8n-lt Postgres Sales Navigator map for one GHL contact."""
from __future__ import annotations

import base64
import io
import socket
from pathlib import Path

import paramiko

HOST = "automations.livetransparent.com"
CONTACT_ID = "NVAp2GdpbWXLheyUgVf2"
PROFILE_ID = "ACwAACeQjiYBfmQfKakCJqijaX9-LVjeHyQrBw8"
PROFILE_SLUG = "edmundo-c-a06372166"
CHAT_ID = "SALES_NAVIGATOR_2-ZWUzNTFlZTgtMWZkZC00NTU2LTg2MjItMmFhNzRlY2JiMDZhXzEwMA=="
CONTAINER = "postgres-uokgs4c04ko0s4scccg40cgg"
KEY_PATH = Path.home() / ".ssh" / "local-upload"


def query(ssh: paramiko.SSHClient, database: str, sql: str) -> tuple[int, str]:
    encoded = base64.b64encode(sql.encode("utf-8")).decode("ascii")
    command = (
        f"docker exec {CONTAINER} sh -c "
        f"'echo {encoded} | base64 -d | psql -X -v ON_ERROR_STOP=1 -A -t -F \"|\" -U postgres -d {database}'"
    )
    _, stdout, stderr = ssh.exec_command(command, timeout=20)
    output = stdout.read().decode("utf-8", "replace").strip()
    error = stderr.read().decode("utf-8", "replace").strip()
    return stdout.channel.recv_exit_status(), output if not error else ""


def main() -> None:
    address = socket.gethostbyname(HOST)
    key = paramiko.Ed25519Key.from_private_key(io.StringIO(KEY_PATH.read_text()))
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    ssh.connect(address, username="root", pkey=key, timeout=10, look_for_keys=False)
    try:
        for database in ("postgres", "n8n"):
            code, exists = query(
                ssh, database,
                "SELECT to_regclass('public.sales_navigator_v2_conversation_map') IS NOT NULL;",
            )
            if code != 0 or exists != "t":
                continue
            sql = (
                "SELECT unipile_account_id,provider_profile_id,unipile_chat_id,"
                "ghl_contact_id,COALESCE(ghl_conversation_id,'') "
                "FROM sales_navigator_v2_conversation_map "
                f"WHERE ghl_contact_id='{CONTACT_ID}' ORDER BY unipile_chat_id;"
            )
            code, rows = query(ssh, database, sql)
            identity_sql = (
                "SELECT DISTINCT ghl_contact_id FROM linkedin_contact_profile_index "
                f"WHERE normalized_profile_slug='{PROFILE_SLUG}' "
                f"OR '{PROFILE_ID}'=ANY(linkedin_provider_ids) ORDER BY ghl_contact_id;"
            )
            identity_code, identity_rows = query(ssh, database, identity_sql)
            identity_detail_sql = (
                "SELECT ghl_contact_id,normalized_profile_slug,"
                "COALESCE(profile_url,''),COALESCE(contact_name,''),"
                "COALESCE(array_length(linkedin_provider_ids,1),0) "
                "FROM linkedin_contact_profile_index "
                f"WHERE normalized_profile_slug='{PROFILE_SLUG}' "
                f"OR '{PROFILE_ID}'=ANY(linkedin_provider_ids) ORDER BY ghl_contact_id;"
            )
            detail_code, detail_rows = query(ssh, database, identity_detail_sql)
            chat_sql = (
                "SELECT ghl_contact_id,provider_profile_id FROM sales_navigator_v2_conversation_map "
                f"WHERE unipile_chat_id='{CHAT_ID}';"
            )
            chat_code, chat_rows = query(ssh, database, chat_sql)
            event_sql = (
                "SELECT status,COUNT(*) FROM sales_navigator_v2_message_events "
                f"WHERE unipile_chat_id='{CHAT_ID}' GROUP BY status ORDER BY status;"
            )
            event_code, event_rows = query(ssh, database, event_sql)
            event_detail_code, event_details = query(
                ssh, database,
                "SELECT event_id,status,COALESCE(unipile_message_id,''),"
                "COALESCE(failure_code,''),claimed_at,updated_at "
                "FROM sales_navigator_v2_message_events "
                f"WHERE unipile_chat_id='{CHAT_ID}' ORDER BY id DESC LIMIT 5;",
            )
            snapshot_sql = (
                "SELECT COUNT(*),COUNT(*) FILTER (WHERE EXISTS "
                "(SELECT 1 FROM linkedin_extract_profile_slugs(c.payload_json) s "
                f"WHERE s.normalized_profile_slug='{PROFILE_SLUG}')) "
                "FROM report_raw_ghl_contacts c "
                f"WHERE c.source_system='ghl' AND c.source_key='contact:{CONTACT_ID}';"
            )
            snapshot_code, snapshot_rows = query(ssh, database, snapshot_sql)
            owner_code, owner_rows = query(
                ssh, database,
                "SELECT current_user,tableowner FROM pg_tables "
                "WHERE schemaname='public' AND tablename='linkedin_contact_profile_index';",
            )
            invalid_code, invalid_rows = query(
                ssh, database,
                "SELECT COUNT(*),COUNT(DISTINCT ghl_contact_id) "
                "FROM linkedin_contact_profile_index "
                "WHERE ghl_contact_id !~ '^[A-Za-z0-9]{20}$';",
            )
            invalid_groups_code, invalid_groups = query(
                ssh, database,
                "SELECT split_part(ghl_contact_id,':',1),COUNT(*) "
                "FROM linkedin_contact_profile_index "
                "WHERE ghl_contact_id !~ '^[A-Za-z0-9]{20}$' "
                "GROUP BY 1 ORDER BY 2 DESC LIMIT 8;",
            )
            claim_sql = (
                "SELECT normalized_identity_key,status,COALESCE(ghl_contact_id,'') "
                "FROM linkedin_contact_profile_claims "
                f"WHERE normalized_identity_key IN ('{PROFILE_SLUG}','provider:{PROFILE_ID.lower()}');"
            )
            claim_code, claim_rows = query(ssh, database, claim_sql)
            print({
                "database": database,
                "queryOk": code == identity_code == detail_code == chat_code == event_code == snapshot_code == claim_code == 0,
                "mapRows": rows.splitlines() if rows else [],
                "identityContacts": identity_rows.splitlines() if identity_rows else [],
                "identityDetails": detail_rows.splitlines() if detail_rows else [],
                "existingChatMap": chat_rows.splitlines() if chat_rows else [],
                "chatEventStatusCounts": event_rows.splitlines() if event_rows else [],
                "recentChatEvents": event_details.splitlines() if event_details else [],
                "snapshotCountAndProfileMatches": snapshot_rows,
                "databaseUserAndTableOwner": owner_rows,
                "nonGhlIdIndexRowsAndContacts": invalid_rows,
                "nonGhlIdGroups": invalid_groups.splitlines() if invalid_groups else [],
                "profileClaims": claim_rows.splitlines() if claim_rows else [],
            })
            return
        print({"databaseFound": False})
    finally:
        ssh.close()


if __name__ == "__main__":
    main()
