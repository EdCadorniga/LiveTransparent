"""Phase 4 archive classification generator (2026-11-05).

Read-only analysis of `local-archive/n8n/`:
- enumerates exact paths and sizes;
- for JSON workflow exports, extracts workflow `id`/`name`/`versionId`/node count and compares
  `versionId` with the CURRENT live n8n-lt version (version IDs are non-secret);
- scans every file for credential-pattern hits (hit NAMES + counts only; values never emitted);
- emits an exact-path table with bounded, evidence-based provisional classification.
Nothing in the archive is modified, deleted, or deployed beyond these reads.
"""

import json
import os
import re
import subprocess
import datetime
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ARCH = os.path.join(ROOT, "local-archive", "n8n")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "n8n-archive-classification-2026-11-05.md")
BASE = "https://automations.livetransparent.com/api/v1"

PATTERNS = {
    "password_literal": r"(?i)\b(password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{8,}['\"]",
    "apikey_literal": r"(?i)\b(api[_-]?key|apikey)\s*[:=]\s*['\"][A-Za-z0-9_\-\.]{16,}['\"]",
    "jwt": r"eyJ[A-Za-z0-9_\-]{20,}",
    "ghl_pit": r"pit-[A-Za-z0-9_\-]{8,}",
    "n8n_api_key": r'(?i)x-n8n-api-key\s*[:=]\s*["\'][^"\'\s]{10,}["\']',
    "lt_header_secret": r'(?i)(X-LT-[A-Za-z-]+)\s*[:=]\s*["\'][^"\'\s]{12,}["\']',
}


def load_env_key():
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8", errors="replace"):
        line = line.strip()
        if line.startswith("N8N_LT_API_KEY=") and len(line) > len("N8N_LT_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("N8N_LT_API_KEY not found")


def live_versions(ids):
    if not ids:
        return {}
    key = load_env_key()
    out = {}
    for wid in sorted(set(ids)):
        req = urllib.request.Request(f"{BASE}/workflows/{wid}")
        req.add_header("X-N8N-API-KEY", key)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                d = json.loads(resp.read().decode("utf-8"))
            out[wid] = {"name": d.get("name"), "active": d.get("active"),
                        "versionId": d.get("versionId"), "activeVersionId": d.get("activeVersionId")}
        except Exception as exc:  # noqa: BLE001
            out[wid] = {"error": type(exc).__name__}
    return out


def secret_hits(path):
    hits = {}
    for name, pat in PATTERNS.items():
        pr = subprocess.run(["rg", "-c", "--no-messages", "--no-heading", pat, path],
                            capture_output=True, text=True)
        cnt = 0
        for x in (pr.stdout or "").splitlines():
            part = x.rsplit(":", 1)[1] if ":" in x else x
            try:
                cnt += int(part.strip())
            except ValueError:
                pass
        if cnt:
            hits[name] = cnt
    return hits


def extract_wf(json_path):
    try:
        d = json.load(open(json_path, encoding="utf-8", errors="replace"))
    except Exception as exc:  # noqa: BLE001
        return {"parse_error": type(exc).__name__}
    if isinstance(d, list) and len(d) == 1 and isinstance(d[0], dict):
        d = d[0]
    if not isinstance(d, dict):
        return {}
    out = {"id": str(d.get("workflow_id") or d.get("id") or ""),
           "name": d.get("name"),
           "versionId": d.get("versionId") or (d.get("meta") or {}).get("versionId"),
           "nodeCount": len(d.get("nodes") or [])}
    return out


def classify(rel, kind, match, hits):
    base = os.path.basename(rel)
    if "/backups/" in rel:
        cls = "keep (rollback evidence, superseded by date)"
    elif "before-" in base or "backup-" in base:
        cls = "keep (rollback evidence)"
    elif kind == "ts":
        cls = "keep (retained blueprint source)"
    elif "/voice-agent/" in rel:
        cls = "keep (voice rollback/source pending mapping)"
    elif rel.endswith(("test-ghl-search.js", "update-dispatcher-message.mjs")):
        cls = "owner decision"
    else:
        cls = "archive/keep pending review"
    if hits:
        cls += "; secret-hit review required before redistribution"
    return cls.strip()


def main():
    # count files containing the exact live PIT value (value never emitted)
    pit = None
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8", errors="replace"):
        line = line.strip()
        if line.startswith("GHL_PIT="):
            pit = line.split("=", 1)[1].strip()
    pit_files = []
    for dp, dns, fns in os.walk(ARCH):
        for fn in fns:
            p = os.path.join(dp, fn)
            try:
                if pit and pit in open(p, encoding="utf-8", errors="replace").read():
                    pit_files.append(p.replace(os.sep, "/"))
            except Exception:
                pass

    files = []
    for dp, dns, fns in os.walk(ARCH):
        for fn in fns:
            p = os.path.join(dp, fn)
            files.append({"path": p.replace(os.sep, "/"),
                          "bytes": os.path.getsize(p),
                          "mtime": os.stat(p).st_mtime})
    files.sort(key=lambda x: x["path"])

    ids = set()
    rows = []
    for f in files:
        rel = f["path"]
        kind = rel.rsplit(".", 1)[-1]
        row = {"path": rel, "bytes": f["bytes"], "mtime": f["mtime"], "kind": kind}
        if kind in ("json", "jsonl"):
            info = extract_wf(f["path"])
            row.update(info)
            wid = info.get("id") or ""
            if len(wid) >= 16:
                ids.add(wid)
        else:
            row["name_guess"] = os.path.basename(rel)
        row["secret_hits"] = secret_hits(f["path"])
        rows.append(row)

    live = live_versions(ids)
    for row in rows:
        wid = row.get("id") or ""
        lv = live.get(wid) or {}
        if lv and "versionId" in lv:
            row["live_version"] = lv.get("versionId")
            row["live_active"] = lv.get("active")
            row["matches_current"] = (row.get("versionId") == lv.get("activeVersionId"))

    lines = ["# Phase 4 — workflow export/backup archive classification — 2026-11-05", "",
             "Read-only: exact paths + sizes; JSON exports parsed for `id`/`name`/`versionId`/node count;",
             "current live version compared via GET (version IDs are non-secret); credential-pattern hit",
             "NAMES + counts only (values never emitted). No archive file was modified; nothing was",
             "deleted, archived, or deployed. Not a deletion manifest.", ""]
    tb = sum(r["bytes"] for r in files)
    lines += [f"**Coverage:** {len(files)} files, {tb:,} bytes under `local-archive/n8n/`; live version "
              f"comparison performed for {len(ids)} workflow ID(s).", ""]
    lines += ["| path | kind | bytes | mtime | wf id | name | vs current active version | secret hits | class |",
              "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        p = r["path"]
        match = "?"
        if r.get("id"):
            match = ("current-active" if r.get("matches_current")
                     else ("differs-from-active" if r.get("live_version") else "wf-not-live") if r.get("id") in live else "not-live-checked")
        name = r.get("name") or r.get("name_guess") or ""
        hits = ", ".join(f"{k}({v})" for k, v in r.get("secret_hits", {}).items()) or ""
        cls = classify(p, r["kind"], match, hits)
        mt = datetime.datetime.fromtimestamp(r["mtime"]).strftime("%Y-%m-%d")
        lines.append(f"| `{p}` | {r['kind']} | {r['bytes']:,} | {mt} | `{r.get('id','')}` | {name} | {match} | {hits} | {cls} |")

    lines += ["", "## Archived JSON workflow IDs vs current live version", "",
              "| id | live name | active | current live versionId | archived row versionId |", "|---|---|---|---|---|"]
    for wid, lv in sorted(live.items()):
        arch = [r for r in rows if r.get("id") == wid and r.get("versionId")]
        lines.append(f"| `{wid}` | {lv.get('name')} | {lv.get('active')} | `{lv.get('versionId')}` | `{arch[0].get('versionId') if arch else ''}` |")

    lines += ["", "## Live-credential containment check (2026-11-05)", "",
              "A follow-up containment check searched for the *exact* current live GHL PIT value",
              "(read from `.env` locally; the value itself was never printed into this artifact).",
              "Result: the exact live PIT text appears in **" + str(len(pit_files)) + " archived",
              "exports/blueprints in this tree plus one `local-scripts/` file — the same",
              "payload values were baked into historical exports while the token is still in use.",
              "This is **not** committed-to-Git material (the archive is git-ignored), but any",
              "redistribution/migration of these files must handle it.",
              "**Owner resolution 2026-11-05 (later): Ed directed retention of the latest PIT from",
              "`.env` — no rotation now; the token's presence here and in Git history is an owner-",
              "accepted residual risk, with redistribution precautions unchanged.**",
              "",
              "**Recovery note:** no archive row is the live system of record; restoring any workflow",
              "requires the documented deploy path plus explicit owner approval. The five May-2026",
              "`workflow_Q3Ivnwe4z2Y3cD7A_*` backups are superseded-by-date history for the current",
              "SimpleTexting send workflow. Sensitive hits must be reviewed before any redistribution.",
              "**Not approved** for movement or deletion.", ""]
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", OUT, "files:", len(files), "live_checked:", len(live))


if __name__ == "__main__":
    main()
