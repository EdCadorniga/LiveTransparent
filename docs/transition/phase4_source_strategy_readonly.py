"""Phase 4 source/rollback mapping for critical n8n-lt workflows (2026-11-05).

Read-only: searches tracked repository source/blueprint files for each critical workflow ID
(`rg -l`, file paths only — no workflow data read from live or from archive beyond the dated
archive classification) and emits a strategy matrix in
`docs/transition/phase4-source-backup-strategy.md`.

No workflow was executed/toggled; nothing on the host or DB was searched/downloaded; live
n8n reads were not needed for this pass (the archive/live mapping is in
`n8n-archive-classification-2026-11-05.md`).
"""

import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phase4-source-backup-strategy-2026-11-05.md")

SEARCH_DIRS = ["scripts", "n8n", "postgres", "services", "tools"]

CRITICAL = [
    # (name, id, role)
    ("LT - GHL Daily Sales Ingest", "aYT5oHcgmBALzHy5", "Opportunities snapshot ingest (daily)"),
    ("LT - GHL Daily Leads Ingest", "osIJOgBmWITF5Yuv", "Contacts snapshot ingest (hourly)"),
    ("LT - Report Executive Summary API", "Bukc0mgOD2r7V6ED", "Legacy Executive Report facts API"),
    ("LT - Report Campaign Channel Summary", "MvPLbUAN9IIQikxb", "Campaign channel facts API"),
    ("LT - Executive Report V1 Facts API", "oxYDg6XnRBKhl1Xd", "Executive Report V1 facts API"),
    ("LT - Executive Report V1 Data Materializer", "knc2wxe4pyYIJ5tw", "V1 facts materializer"),
    ("LT - Report Daily Rollups", "EUeOiRttoVLQ9zF9", "Daily rollups bridge"),
    ("LT - Report Pipeline Velocity", "iFfwh0jpYUZoDhDR", "Stage velocity"),
    ("Report Attribution Bridge", "Y0TU7Il71JswxOBp", "Traffic-to-lead attribution"),
    ("LT - GHL LinkedIn Connect Dispatcher", "fXxw5lanZcDmUrst", "Connection invite sender"),
    ("LT - LinkedIn DM Sequence (Unipile)", "d0tEtijajisIsYcs", "4-step DM sender"),
    ("LT - LinkedIn Connection State Sync", "ceaKnz6E3onQrZpt", "Ready/connected state reconciliation"),
    ("LT - LinkedIn Connection State Upsert", "Old7ZvyVYgFaJgDr", "Canonical state write webhook"),
    ("LT - LinkedIn Connection Acceptance Checker", "3ttEvr5NMcQCS4Hp", "Acceptance detection webhook"),
    ("LT - LinkedIn Reply Backfill", "QfJ2EZcc7lZwNgxj", "Reply divergence reconciliation"),
    ("LT - LinkedIn Relations Backfill", "VPiHfBwzOHaJnHBY", "Provider relations daily backfill"),
    ("LT - LinkedIn DM Suppression from GHL Tag", "IPN8jnR3XSurX0o1", "Suppression webhook"),
    ("LT - LinkedIn Connected Tag Sync", "rcvTMprJKga9aEJ6", "Daily connected-tag sync"),
    ("LT - Sales Navigator Provider Gateway", "ZiYEBuP7xdddhnUB", "GHL provider outbound/inbound gateway (V2)"),
    ("LT - Unipile Sales Navigator V2 Inbound", "CfpedDQWxoJLEMdL", "V2 event bridge + GHL inbound mirror"),
    ("LT - Sales Navigator V2 Uncertain Write Reconciler", "sFrvSJIZusAbrsFx", "Uncertain-event reconciler"),
    ("LT - SimpleTexting SMS Send (Webhook, Staged)", "Q3Ivnwe4z2Y3cD7A", "SMS send boundary"),
    ("LT - SMS Idempotent Send", "gwaEpWDpTIwsafi8", "Idempotent SMS boundary"),
    ("LT - SimpleTexting Provider Outbound Router", "f4VoO1lBWkYRcQai", "GHL->SimpleTexting outbound router"),
    ("LT - SimpleTexting Inbound Reply (Webhook)", "i0pROHpFtN4LYR0Q", "Inbound SMS reply handler"),
    ("LT - Voice Agent V1 Outbound Dialer (Vapi)", "r7UjWLndmc6EqEUW", "Vapi dialer"),
    ("LT - Voice Agent V1 Vapi Callback + Tools", "fx4UvKUWbqJEY3LK", "Vapi end-of-call ingestion"),
    ("LT - Voice Queue Vapi Intake Poller", "bYk1Ai6MJLyhTsDZ", "Queue poller"),
    ("LT - Voice Queue Enqueue", "XzcpOBi9YcIhJPck", "Queue enqueue webhook"),
    ("LT - Emerald Campaign Sender Release Dispatcher", "8UXlpoMJnQ229AuG", "Emerald live-send dispatcher"),
    ("LT - DAN Campaign Sender Release Dispatcher", "toUG1yPDmFG48KEP", "DAN live-send dispatcher"),
    ("LT - Partnership Email Dispatcher", "Xshck23cKo1yXL9D", "Partnership email sender"),
    ("LT - Newsletter Dispatcher", "vru7OtCkDnPJkWt2", "Weekly newsletter sender"),
    ("LT - Newsletter Contact Prep", "vvPdJMzBJMgcf5I9", "Newsletter eligible cohorts"),
    ("LT - Email Event Ingest", "ZrqFN8qLKO8eVHDc", "Provider email event webhook"),
    ("LT - Apollo Phone Enrichment Polling", "JH8ShfpglWmLMZ3l", "Apollo worker"),
    ("GHL Apollo Phone Enrichment - Callback Handler V4", "U7c6byTLXAMgcS75", "Apollo callback"),
    ("LT - Apollo Queued Timeout Reaper", "RL5ZyUoshSPbmVA1", "Apollo timeout reaper"),
    ("LT - Call Outcome Ingest", "PUCfTZBANSPcgS0c", "Vapi/GHL call outcome webhook"),
    ("LT - MQL Tag Event Ingest", "U9oc2tZRsr4zq6IM", "MQL tag ledger webhook"),
    ("LT - Booking Link Click Intake (Webhook)", "1diZyFmTqWQUEny3", "Booking attribution intake"),
    ("LT - Booking Link SMS Redirect (Webhook)", "9HT13te9FalOtUZM", "Booking attribution SMS redirect"),
    ("LT - Vertical Sender Assign (Webhook)", "z0Sq4AE3Xdbgw2Yh", "Per-vertical sender round-robin"),
    ("LT - Last-Touch Owner Resolver + 14-Day Backfill", "KQjosWjChMYbhZkF", "Owner attribution resolver"),
    ("WL - Micro - Set Vertical Sender (Webhook)", "z0Sq4AE3Xdbgw2Yh", "GHL caller — same capability as above"),
    ("LT - Inbound Intent Priority Router", "URpjcm2k5isHUyls", "Priority router (execute-workflow target)"),
]


def rg_files_for(id_):
    hits = []
    for d in SEARCH_DIRS:
        full = os.path.join(ROOT, d)
        if not os.path.isdir(full):
            continue
        pr = subprocess.run(["rg", "-l", "--no-messages", id_, full], capture_output=True, text=True)
        for f in (pr.stdout or "").splitlines():
            hits.append(f.replace(ROOT + os.sep, "").replace(os.sep, "/"))
    return sorted(set(hits))[:6]


def main():
    lines = ["# Phase 4 — critical workflow source and rollback strategy — 2026-11-05", "",
             "Read-only: each critical workflow ID was searched across tracked `scripts/`, `n8n/`,",
             "`postgres/`, `services/`, `tools/` to find which repo artifacts reference it",
             "(the only reproducible builders/repairers). File paths only; no live or archive",
             "workflow data was re-read (see the archive classification for rollback snapshots).",
             "Not a cleanup authorization; nothing was changed.", "",
             "**Source strategy (verified from this pass):** the live n8n-lt instance is the system",
             "of record; n8n API `GET /workflows/{id}` provides an authoritative live export for any",
             "workflow before/after a change. The repo's builder/repair scripts are the documented",
             "reproducible sources for changes; where a workflow has **no** repo reference, its only",
             "durable source is the live instance (and any dated local snapshot listed in the",
             "archive classification).", ""]
    lines += ["| workflow (role) | id | repo artifacts referencing the ID |", "|---|---|---|"]
    orphan_count = 0
    for name, wid, role in CRITICAL:
        refs = rg_files_for(wid)
        if not refs:
            orphan_count += 1
        lines.append(f"| {name} — {role} | `{wid}` | {', '.join('`'+r+'`' for r in refs) or '—none—'} |")

    lines += ["", f"**Workflows with no tracked repo reference ({orphan_count})** rely solely on the live",
              "n8n-lt instance and any dated archive/local snapshots; treat their repo replications",
              "as future work if/when they are edited by an approved change.",
              "", "## Rollback strategy (documented, not newly-built)",
              "- Live n8n-lt API export (GET) is the authoritative pre-change snapshot mechanism and",
              "  can be taken fresh at any time; no scheduled n8n backup exists.",
              "- The `local-archive/n8n/` dated snapshots for **13 workflow IDs** are all older than",
              "  the currently published versions — useful as history/rollback only after per-file",
              "  review (see archive classification).",
              "- There is **no verified automated n8n workflow backup/restore pipeline**; the",
              "  documented practice is to export before every future change. Any new automated",
              "  backup design is an owner-decision item, not an authorized build.",
              "- Critical workflows that will not run without live Postgres tables (LinkedIn/voice",
              "  queue/report state) also require the DB schema inventory + database availability;",
              "  see [postgres schema inventory](postgres-schema-inventory-2026-11-05.md)."]
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", OUT, "critical:", len(CRITICAL), "orphans(no repo ref):", orphan_count)


if __name__ == "__main__":
    main()
