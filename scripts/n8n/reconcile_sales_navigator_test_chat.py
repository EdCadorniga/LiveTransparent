"""Reconcile one verified Sales Navigator peer/chat with its existing GHL contact.

The profile URL was independently read from the GHL contact and Unipile user.
This script writes only the shared profile index and V2 conversation map on
the n8n-lt Postgres host. It does not send or backfill messages.
"""
from __future__ import annotations

import base64
import io
import socket
from pathlib import Path

import paramiko

HOST = "automations.livetransparent.com"
CONTAINER = "postgres-uokgs4c04ko0s4scccg40cgg"
ACCOUNT = "acc_01m3sefk22e8jvnmvvfx333pye"
CONTACT = "NVAp2GdpbWXLheyUgVf2"
CONVERSATION = "EjsrNLaDUD46onBsW82A"
PROFILE = "ACwAACeQjiYBfmQfKakCJqijaX9-LVjeHyQrBw8"
SLUG = "edmundo-c-a06372166"
CHAT = "SALES_NAVIGATOR_2-ZWUzNTFlZTgtMWZkZC00NTU2LTg2MjItMmFhNzRlY2JiMDZhXzEwMA=="

SQL = f"""
BEGIN;
LOCK TABLE linkedin_contact_profile_index, linkedin_contact_profile_claims,
  sales_navigator_v2_conversation_map IN SHARE ROW EXCLUSIVE MODE;
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM linkedin_contact_profile_claims
    WHERE normalized_identity_key IN ('{SLUG}', 'provider:{PROFILE.lower()}')
      AND status = 'pending'
  ) THEN
    RAISE EXCEPTION 'profile identity has a pending contact claim';
  END IF;
  IF EXISTS (
    SELECT 1 FROM sales_navigator_v2_conversation_map
    WHERE unipile_account_id = '{ACCOUNT}'
      AND (unipile_chat_id = '{CHAT}' OR ghl_contact_id = '{CONTACT}')
      AND (unipile_chat_id <> '{CHAT}' OR ghl_contact_id <> '{CONTACT}'
        OR provider_profile_id <> '{PROFILE}')
  ) THEN
    RAISE EXCEPTION 'chat or contact has a conflicting Sales Navigator map';
  END IF;
END
$$;
INSERT INTO linkedin_contact_profile_index
  (ghl_contact_id,normalized_profile_slug,profile_url,contact_name,linkedin_provider_ids,refreshed_at)
VALUES
  ('{CONTACT}','{SLUG}','https://www.linkedin.com/in/{SLUG}',
   'Ed Test',ARRAY['{PROFILE}']::text[],NOW())
ON CONFLICT (ghl_contact_id,normalized_profile_slug) DO UPDATE SET
  profile_url=EXCLUDED.profile_url,
  contact_name=EXCLUDED.contact_name,
  linkedin_provider_ids=ARRAY(
    SELECT DISTINCT unnest(linkedin_contact_profile_index.linkedin_provider_ids
      || EXCLUDED.linkedin_provider_ids)),
  refreshed_at=NOW();
INSERT INTO sales_navigator_v2_conversation_map
  (unipile_account_id,provider_profile_id,unipile_chat_id,ghl_contact_id,ghl_conversation_id)
VALUES ('{ACCOUNT}','{PROFILE}','{CHAT}','{CONTACT}','{CONVERSATION}')
ON CONFLICT (unipile_account_id,unipile_chat_id) DO UPDATE SET
  ghl_conversation_id=EXCLUDED.ghl_conversation_id,updated_at=NOW()
WHERE sales_navigator_v2_conversation_map.provider_profile_id=EXCLUDED.provider_profile_id
  AND sales_navigator_v2_conversation_map.ghl_contact_id=EXCLUDED.ghl_contact_id;
COMMIT;
SELECT
  (SELECT COUNT(*) FROM linkedin_contact_profile_index
   WHERE ghl_contact_id='{CONTACT}' AND normalized_profile_slug='{SLUG}'
     AND '{PROFILE}'=ANY(linkedin_provider_ids)),
  (SELECT COUNT(*) FROM sales_navigator_v2_conversation_map
   WHERE unipile_account_id='{ACCOUNT}' AND unipile_chat_id='{CHAT}'
     AND provider_profile_id='{PROFILE}' AND ghl_contact_id='{CONTACT}'
     AND ghl_conversation_id='{CONVERSATION}');
"""


def main() -> None:
    key_text = (Path.home() / ".ssh" / "local-upload").read_text()
    key = paramiko.Ed25519Key.from_private_key(io.StringIO(key_text))
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    ssh.connect(socket.gethostbyname(HOST), username="root", pkey=key, timeout=10, look_for_keys=False)
    try:
        encoded = base64.b64encode(SQL.encode()).decode("ascii")
        command = (
            f"docker exec {CONTAINER} sh -c "
            f"'echo {encoded} | base64 -d | psql -X -v ON_ERROR_STOP=1 -A -t -F \"|\" -U postgres -d postgres'"
        )
        _, stdout, stderr = ssh.exec_command(command, timeout=25)
        result = stdout.read().decode("utf-8", "replace").strip()
        error = stderr.read().decode("utf-8", "replace")
        status = stdout.channel.recv_exit_status()
        counts = result.splitlines()[-1] if result else ""
        if status or counts != "1|1":
            raise RuntimeError(
                f"contact/chat reconciliation failed: status={status}, "
                f"lastOutput={counts[:120]!r}, databaseError={error[:300]!r}"
            )
        print({"indexAndMapRows": counts, "database": "n8n-lt Postgres"})
    finally:
        ssh.close()


if __name__ == "__main__":
    main()
