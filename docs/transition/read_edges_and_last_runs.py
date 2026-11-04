"""Read-only n8n-lt evidence generator for the developer transition, 2026-11-05.

Scope of the generated artifact:
  A. Workflow census counts (from GET /workflows + per-ID GET /workflows/{id}).
  B. Literal same-instance relationship edges only:
     - n8n-nodes-base.executeWorkflow nodes -> target workflow ID.
     - HTTP Request nodes wrapping `automations.livetransparent.com` -> path only
       (query strings dropped), matched against workflows that serve the path.
     - Code-node (jsCode) literal references to the same host, path-only, redacted.
  C. Last observed execution metadata for a fixed allowlist of ten workflow IDs:
     status / startedAt / stoppedAt only, `includeData=false`. Never payloads.
  D. Schedule Trigger interval parameters and workflow timezone.

Safety design (differs from inventory_n8n_readonly.py):
  - Emits ONLY the fields above; never arbitrary node parameters, JSON payloads,
    credential values, or query strings.
  - Redacts UUID-like path segments (unguessable webhook tokens).
  - The API key is read from .env and is never written to any output file nor printed.
  - GET requests only; nothing is executed, toggled, or changed.
"""

import json
import os
import re
import sys
import datetime
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = "https://automations.livetransparent.com/api/v1"
OUT_MD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "n8n-edges-and-exception-runs-2026-11-05.md")
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "n8n-edges-and-exception-runs-2026-11-05.json")


def load_env_key():
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8", errors="replace"):
        line = line.strip()
        if line.startswith("N8N_LT_API_KEY=") and len(line) > len("N8N_LT_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("N8N_LT_API_KEY not found in .env")


def api(path, key, limit_reached=False):
    req = urllib.request.Request(BASE + path)
    req.add_header("X-N8N-API-KEY", key)
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|[0-9a-f]{16,}", re.I)


def redact_path(path):
    path = path.split("?", 1)[0]
    return UUID_RE.sub("<redacted-token>", path)


def param_strings(node):
    out = []

    def walk(v):
        if isinstance(v, str):
            out.append(v)
        elif isinstance(v, list):
            for x in v:
                walk(x)
        elif isinstance(v, dict):
            for x in v.values():
                walk(x)

    for v in node.get("parameters", {}).values():
        walk(v)
    return out


def main():
    key = load_env_key()
    listing = api("/workflows?limit=250", key)
    data = listing.get("data", listing) if isinstance(listing, dict) else listing
    wf_meta = {w["id"]: {"id": w["id"], "name": w.get("name"), "active": w.get("active")} for w in data}
    print(f"listed={len(wf_meta)}")

    failures = []
    served_paths = {}       # (path, method) -> [wf ids]
    code_path_refs = {}     # path -> [wf ids]
    exec_edges = []
    http_edges = []
    sched_summary = []

    for wid in sorted(wf_meta):
        try:
            wf = api(f"/workflows/{wid}", key)
        except Exception as exc:  # noqa: BLE001
            failures.append({"id": wid, "error": type(exc).__name__})
            continue
        var = wf_meta[wid]
        var["timezone"] = (wf.get("settings", {}) or {}).get("timezone")
        for node in wf.get("nodes", []):
            ntype = node.get("type", "")
            pid = node.get("parameters", {}) or {}
            if ntype in ("n8n-nodes-base.executeWorkflow", "n8n-nodes-base.executeWorkflowTrigger"):
                target = pid.get("workflowId") or pid.get("id") or ""
                if isinstance(target, dict):
                    target = target.get("value", "")
                if target:
                    exec_edges.append({"from": str(wid), "node": node.get("name"), "to": str(target)})
            elif ntype == "n8n-nodes-base.webhook" or ntype == "n8n-nodes-base.formTrigger":
                path = str(pid.get("path", ""))
                method = str(pid.get("httpMethod", "GET"))
                if path:
                    served_paths.setdefault((redact_path(path), method), []).append(str(wid))
            elif ntype == "n8n-nodes-base.scheduleTrigger":
                rule = pid.get("rule") or {}
                rule = rule.get("rule", rule) if isinstance(rule, dict) else {}
                interval = rule.get("interval", [])
                sched_summary.append({
                    "id": str(wid), "name": wf.get("name"), "timezone": var["timezone"],
                    "interval": interval,
                })
            for s in param_strings(node):
                if "automations.livetransparent.com/webhook" in s:
                    for m in re.finditer(r"automations\.livetransparent\.com/webhook/[\w\-/]+", s):
                        path = redact_path(m.group(0).split("automations.livetransparent.com/webhook/", 1)[1])
                        if path.startswith("<redacted-token>"):
                            continue  # already-redacted; stored ref only
                        code_path_refs.setdefault(path, []).append(str(wid))
                if "automations.livetransparent.com" in s and "/webhook/" not in s:
                    for m in re.finditer(r"automations\.livetransparent\.com/[\w\-/]+", s):
                        path = redact_path(m.group(0).split("automations.livetransparent.com/", 1)[1])
                        if path.startswith("<redacted-token>") or path.startswith("<redacted"):
                            continue
                        code_path_refs.setdefault(path, []).append(str(wid))

    # HTTP literal webhook-call edges (non-code nodes)
    for wid in sorted(wf_meta):
        try:
            wf = api(f"/workflows/{wid}", key)
        except Exception:
            continue
        for node in wf.get("nodes", []):
            if node.get("type") != "n8n-nodes-base.httpRequest":
                continue
            url = node.get("parameters", {}).get("url")
            if not isinstance(url, str) or "{{" in url:
                if isinstance(url, str) and "automations.livetransparent.com/webhook" in url:
                    m = re.match(r"https?://automations\.livetransparent\.com/webhook/[\w\-/]+", url, re.I)
                    if m:
                        http_edges.append({"from": str(wid), "node": node.get("name"),
                                           "path": redact_path(m.group(1)), "served_by": None,
                                           "expression_url": True})
                continue
            m = re.match(r"https?://automations\.livetransparent\.com/(webhook/.+?)$", url, re.I)
            if not m:
                continue
            path = redact_path(m.group(1))
            # exact match first, then longest serving prefix
            served_by = []
            for (spath, method), ids in served_paths.items():
                if path == spath or spath == "" or path.startswith(spath.rstrip("/") + "/") or spath.lstrip("/webhook/").rstrip("/") == path.lstrip("/webhook/"):
                    served_by += list(ids)
            http_edges.append({"from": str(wid), "node": node.get("name"), "path": path,
                               "served_by": sorted(set(served_by)) if served_by else None})

    exceptions = ["0jDKgG8VvmfyORQn", "8UXlpoMJnQ229AuG", "CfpedDQWxoJLEMdL", "Q3Ivnwe4z2Y3cD7A",
                  "ToMOV6FElZD4ezZN", "ZiYEBuP7xdddhnUB", "b41Sas8FVVrytZrl", "t5frjtbuKzVZI294",
                  "toUG1yPDmFG48KEP", "vRXRFC6IwIxUME2k"]
    last_runs = []
    for wid in exceptions:
        try:
            ex = api(f"/executions?workflowId={wid}&limit=1&includeData=false", key)
            rows = ex.get("data", ex) if isinstance(ex, dict) else ex
            if rows:
                r = rows[0]
                last_runs.append({"id": wid, "name": wf_meta.get(wid, {}).get("name"),
                                  "status": r.get("status"), "startedAt": r.get("startedAt"),
                                  "stoppedAt": r.get("stoppedAt")})
            else:
                last_runs.append({"id": wid, "name": wf_meta.get(wid, {}).get("name"),
                                  "status": "none-returned", "startedAt": None, "stoppedAt": None})
        except Exception as exc:  # noqa: BLE001
            last_runs.append({"id": wid, "name": wf_meta.get(wid, {}).get("name"),
                              "status": f"read-error:{type(exc).__name__}", "startedAt": None,
                              "stoppedAt": None})

    result = {
        "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "method": "read-only GETs against n8n-lt /api/v1; no execution, toggle, or write",
        "coverage": {"listed_workflows": len(wf_meta), "definition_read_failures": failures},
        "execute_workflow_edges": exec_edges,
        "http_webhook_edges": http_edges,
        "code_literal_path_refs": {k: sorted(set(v)) for k, v in code_path_refs.items()},
        "served_paths_count": len(served_paths),
        "served_paths": [{"path": p, "method": mth, "served_by": sorted(set(ids))} for (p, mth), ids in sorted(served_paths.items())],
        "exception_last_runs_metadata": last_runs,
        "schedule_triggers": sched_summary,
        "workflow_summaries": [{"id": v["id"], "name": v["name"], "active": v["active"],
                                "timezone": v.get("timezone")} for v in wf_meta.values()],
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1)

    md = [f"# n8n-lt relationship edges, exception run metadata, and schedule registry — 2026-11-05", "",
          "Generated by `docs/transition/read_edges_and_last_runs.py` (GET-only, allowlisted fields,",
          "UUID-like path segments redacted, query strings dropped). Supplement to the 2026-11-04",
          "inventory/relationship snapshot. No workflow was executed, toggled, or changed.", ""]
    md.append(f"## Coverage\n\n- listed_workflows: {len(wf_meta)}\n- definition_read_failures: {len(failures)} ({len([f for f in failures if 'error' in f])} errors)\n")
    md.append("## Execute-workflow edges (literal)\n")
    md.append("| caller | node | target workflow | target name |")
    md.append("|---|---|---|---|")
    for e in exec_edges:
        tname = wf_meta.get(e["to"], {}).get("name") or "?"
        md.append(f"| `{e['from']}` | {e['node']} | `{e['to']}` | {tname} |")
    md.append("\n## Literal HTTP webhook-call edges (sub-instance)\n")
    md.append("| caller | node | path (redacted) | served_by | expression URL |")
    md.append("|---|---|---|---|---|")
    for e in http_edges:
        md.append(f"| `{e['from']}` | {e['node']} | `/{e['path']}` | {', '.join('`'+x+'`' for x in e['served_by']) if e['served_by'] else 'unknown'} | {e.get('expression_url', False)} |")
    md.append("\n## Code-node literal webhook-path references\n")
    md.append("| path referenced | referencing workflows |")
    md.append("|---|---|")
    for p, ids in sorted(code_path_refs.items()):
        md.append(f"| `/{p}` | {', '.join('`'+x+'`' for x in sorted(set(ids)))} |")
    md.append("\n## Exception last-observed execution metadata (status only; payloads not read)\n")
    md.append("| id | name | last status | startedAt | stoppedAt |")
    md.append("|---|---|---|---|---|")
    for r in last_runs:
        md.append(f"| `{r['id']}` | {r['name']} | {r['status']} | {r['startedAt']} | {r['stoppedAt']} |")
    md.append("\n## Schedule Trigger registry (all workflows with a Schedule Trigger node)\n")
    md.append("| id | schedule (interval params) | workflow timezone |")
    md.append("|---|---|---|")
    for s in sched_summary:
        iv = json.dumps(s["interval"]) if s["interval"] else "(empty)"
        md.append(f"| `{s['id']}` | `{iv}` | {s['timezone'] or '(unset)'} |")
    md.append("\n## Served webhook paths (internal endpoints)\n")
    md.append("| path (redacted) | method | served_by |")
    md.append("|---|---|---|")
    for r in result["served_paths"]:
        md.append(f"| `/{r['path']}` | {r['method']} | {', '.join('`'+x+'`' for x in r['served_by'])} |")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    print("edges:", len(exec_edges), "http_edges:", len(http_edges), "code_refs:", len(code_path_refs),
          "served:", len(served_paths), "last_runs:", len(last_runs), "sched:", len(sched_summary))
    print("wrote", OUT_MD)
    print("wrote", OUT_JSON)


if __name__ == "__main__":
    main()
