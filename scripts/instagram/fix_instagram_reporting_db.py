"""Mirror authoritative Instagram ledger events into the reporting database."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from fix_executive_report_metrics import (  # noqa: E402
    INSTAGRAM_TABLE_DDL,
    node_map,
    request,
    update_workflow,
)


SENDER_ID = "IeovbYnhCsetXS89"
INBOUND_ID = "pISlgYUsyJIrLuJd"


def replace_once(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return updated


def assert_live(workflow: dict) -> None:
    if workflow.get("versionId") != workflow.get("activeVersionId"):
        raise RuntimeError(f"Refusing to patch unpublished workflow {workflow.get('id')}")


def sender_patch(workflow: dict) -> None:
    nodes = node_map(workflow)
    node = nodes["Send Partnership DM Batch"]
    code = str(node["parameters"].get("jsCode") or "")
    if "reportClient" in code:
        return

    client_pattern = r"const client = new Client\(\{ host: 'postgres', port: 5432, database: 'n8n', user: 'postgres', password: String\(cfg\.pgPassword \|\| ''\) \}\);"
    client_replacement = """const client = new Client({ host: 'postgres', port: 5432, database: 'n8n', user: 'postgres', password: String(cfg.pgPassword || '') });
const reportClient = new Client({ host: 'postgres', port: 5432, database: 'postgres', user: 'postgres', password: String(cfg.pgPassword || '') });
let reportClientReady = false;
let reportingWriteFailures = 0;
let reportingBackfillRows = 0;"""
    code = replace_once(code, client_pattern, client_replacement, "sender client config")

    sender_reporting_connection = (
        "  await client.connect();\n"
        "  try {\n"
        "    await reportClient.connect();\n"
        "    await reportClient.query(`"
        + INSTAGRAM_TABLE_DDL
        + "`);\n"
        "    reportClientReady = true;\n"
        "    const existingEvents = await client.query('SELECT event_key, event_type, event_at, ghl_contact_id, campaign_key, chat_id, message_id, provider_id, workflow_name, payload_json FROM instagram_activity_events');\n"
        "    for (const event of existingEvents.rows) {\n"
        "      await reportClient.query(`INSERT INTO instagram_activity_events (event_key, event_type, event_at, ghl_contact_id, campaign_key, chat_id, message_id, provider_id, workflow_name, payload_json) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10::jsonb) ON CONFLICT (event_key) DO NOTHING`, [event.event_key, event.event_type, event.event_at, event.ghl_contact_id || '', event.campaign_key || 'instagram', event.chat_id || '', event.message_id || '', event.provider_id || '', event.workflow_name || '', JSON.stringify(event.payload_json || {})]);\n"
        "      reportingBackfillRows += 1;\n"
        "    }\n"
        "  } catch (error) {\n"
        "    reportingWriteFailures += 1;\n"
        "  }"
    )
    code = replace_once(
        code,
        r"  await client\.connect\(\);",
        sender_reporting_connection,
        "sender reporting connection",
    )

    event_insert = """      try {
        if (reportClientReady) await reportClient.query(`INSERT INTO instagram_activity_events (event_key, event_type, event_at, ghl_contact_id, campaign_key, chat_id, message_id, provider_id, workflow_name, payload_json) VALUES ($1,'dm_sent',NOW(),$2,$3,$4,$5,$6,$7,$8::jsonb) ON CONFLICT (event_key) DO NOTHING`, ['dm_sent:' + c.id + ':1', c.primary_ghl_contact_id || '', c.campaign_key, chatId, msgId, c.instagram_profile_provider_id, 'LT - Instagram Company Page Sender', JSON.stringify({ source: 'instagram_company_page_sender', workflow_run_id: runId })]);
      } catch (error) {
        reportingWriteFailures += 1;
      }
"""
    code = replace_once(code, r"      await client\.query\('COMMIT'\);", "      await client.query('COMMIT');\n" + event_insert, "sender reporting event")
    code = replace_once(
        code,
        r"return \[\{ json: \{ ok: sent > 0, mode: 'live', cap: dailyCap, sent_today: sentToday \+ sent, batch: batchTarget, sent, failed, claimed, results \} \}\];",
        "return [{ json: { ok: sent > 0, mode: 'live', cap: dailyCap, sent_today: sentToday + sent, batch: batchTarget, sent, failed, claimed, reportingBackfillRows, reportingWriteFailures, results } }];",
        "sender result",
    )
    code = replace_once(
        code,
        r"} finally \{ await client\.end\(\)\.catch\(\(\) => \{\}\); \}",
        "} finally { await client.end().catch(() => {}); if (reportClientReady) await reportClient.end().catch(() => {}); }",
        "sender client cleanup",
    )
    node["parameters"]["jsCode"] = code


def inbound_patch(workflow: dict) -> None:
    nodes = node_map(workflow)
    node = nodes["Persist and Claim Instagram Reply"]
    code = str(node["parameters"].get("jsCode") or "")
    if "reportClient" in code:
        return

    client_match = re.search(r"const client = new Client\((\{[\s\S]*?\})\);", code)
    if not client_match:
        raise RuntimeError("inbound client config not found")
    client_config = client_match.group(1)
    report_config = client_config.replace("database: 'n8n'", "database: 'postgres'")
    code = code.replace(
        client_match.group(0),
        client_match.group(0)
        + "\n  const reportClient = new Client("
        + report_config
        + ");\n  let reportClientReady = false;\n  let reportingWriteFailures = 0;",
        1,
    )
    inbound_reporting_connection = (
        "  await client.connect();\n"
        "  try {\n"
        "    await reportClient.connect();\n"
        "    await reportClient.query(`"
        + INSTAGRAM_TABLE_DDL
        + "`);\n"
        "    reportClientReady = true;\n"
        "  } catch (error) {\n"
        "    reportingWriteFailures += 1;\n"
        "  }"
    )
    code = replace_once(
        code,
        r"  await client\.connect\(\);",
        inbound_reporting_connection,
        "inbound reporting connection",
    )
    secondary = """  try {
    if (reportClientReady) await reportClient.query(`INSERT INTO instagram_activity_events (event_key, event_type, event_at, ghl_contact_id, campaign_key, chat_id, message_id, provider_id, workflow_name, payload_json) VALUES ($1,'reply_received',COALESCE(NULLIF($2,'')::timestamptz,NOW()),$3,$4,$5,$6,$7,$8,$9::jsonb) ON CONFLICT (event_key) DO NOTHING`, ['reply_received:' + messageId, clean(d.message_timestamp), mappedContactId, campaignKey || 'instagram_unattributed', clean(d.instagram_chat_id), messageId, clean(d.instagram_profile_provider_id), 'LT - Instagram Unipile New Messages', JSON.stringify({ username: clean(d.instagram_username), company_name: companyName || clean(d.display_name) })]);
  } catch (error) {
    reportingWriteFailures += 1;
  }

"""
    code = replace_once(code, r"  await client\.query\('COMMIT'\);", secondary + "  await client.query('COMMIT');", "inbound reporting event")
    code = replace_once(
        code,
        r"await client\.end\(\)\.catch\(\(\) => \{\}\);",
        "await client.end().catch(() => {}); if (reportClientReady) await reportClient.end().catch(() => {});",
        "inbound client cleanup",
    )
    node["parameters"]["jsCode"] = code


def main() -> None:
    sender = request(SENDER_ID)
    inbound = request(INBOUND_ID)
    assert_live(sender)
    assert_live(inbound)
    sender_patch(sender)
    inbound_patch(inbound)
    sender_result = update_workflow(sender)
    inbound_result = update_workflow(inbound)
    for result in (sender_result, inbound_result):
        print({"id": result.get("id"), "versionId": result.get("versionId"), "activeVersionId": result.get("activeVersionId")})


if __name__ == "__main__":
    main()
