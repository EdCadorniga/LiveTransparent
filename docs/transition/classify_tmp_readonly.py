"""Phase 5 temporary/build/data artifact classification generator (2026-11-05).

Read-only enumeration of `tmp/` and the nine root `tmp*` files:
- exact paths + sizes + mtimes;
- credential-pattern hit NAMES + counts only (values never emitted);
- bounded kind classification (screenshot/YAML/data-dump/workflow-snapshot).
No file content is moved, deleted, or modified; not a deletion manifest.
"""

import os
import re
import subprocess
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp-artifacts-classification-2026-11-05.md")

PATTERNS = {
    "password_literal": r"(?i)\b(password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{8,}['\"]",
    "apikey_literal": r"(?i)\b(api[_-]?key|apikey)\s*[:=]\s*['\"][A-Za-z0-9_\-\.]{16,}['\"]",
    "jwt": r"eyJ[A-Za-z0-9_\-]{20,}",
    "ghl_pit": r"pit-[A-Za-z0-9_\-]{8,}",
    "n8n_api_key": r'(?i)x-n8n-api-key\s*[:=]\s*["\'][^"\'\s]{10,}["\']',
    "lt_header_secret": r'(?i)(X-LT-[A-Za-z-]+)\s*[:=]\s*["\'][^"\'\s]{12,}["\']',
}


def hits_for(path):
    h = {}
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
            h[name] = cnt
    return h


def main():
    entries = []
    tmpdir = os.path.join(ROOT, "tmp")
    for fn in sorted(os.listdir(tmpdir)):
        p = os.path.join(tmpdir, fn)
        entries.append({"path": p.replace(os.sep, "/"), "bytes": os.path.getsize(p), "mtime": os.stat(p).st_mtime})
    for fn in sorted(os.listdir(ROOT)):
        if fn.lower().startswith("tmp") and os.path.isfile(os.path.join(ROOT, fn)):
            p = os.path.join(ROOT, fn)
            entries.append({"path": p.replace(os.sep, "/"), "bytes": os.path.getsize(p), "mtime": os.stat(p).st_mtime})

    lines = ["# Phase 5 — temporary/build/data artifact classification — 2026-11-05", "",
             "Read-only path/size/mtime enumeration + credential-pattern scan (hit NAMES + counts only).",
             "No file was read for classification beyond pattern counts; no file was changed, moved, or",
             "deleted. NOT a deletion manifest; nothing is approved for cleanup.", ""]
    lines += ["| path | kind (by extension/provenance) | bytes | mtime | credential-pattern hits | provisional class |",
              "|---|---|---|---|---|---|"]
    for e in entries:
        name = os.path.basename(e["path"])
        ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        if ext in ("png", "jpg"):
            kind, cls = "screenshot capture", "keep pending content/sensitivity review (campaign-build UI evidence)"
        elif ext in ("yml", "yaml"):
            kind, cls = "config/template capture", "keep pending review (may hold template HTML/credentials)"
        elif ext in ("json",):
            kind, cls = "workflow/execution response snapshot", "keep pending review (may hold PII/credentials)"
        elif ext in ("txt",):
            kind, cls = "capture/log", "keep pending review (may hold credentials)"
        elif ext in ("sql", "js"):
            kind, cls = "query/hasource scratch", "keep pending review"
        elif ext in ("pyc",):
            kind, cls = "bytecode", "delete candidate (regenerable) — pending review"
        else:
            kind, cls = f"{ext or 'no-extension'}", "keep pending review"
        h = hits_for(e["path"])
        hs = ", ".join(f"{k}({v})" for k, v in h.items())
        cls = cls + ("; credential-hit review required" if h else "")
        lines.append(f"| `{name}` | {kind} | {e['bytes']:,} | {datetime.datetime.fromtimestamp(e['mtime']).strftime('%Y-%m-%d')} | {hs} | {cls} |")

    lines += ["",
              "**Notes:** `tmp/` files map to the October Alcohol vertical template-build session (UI state",
              "captures and template YAML). Root `tmp*` files are October report-workflow query/response",
              "captures (bucketed JSON responses and SQL/JS scratch) — they may contain contact rows or",
              "workflow definition text and require content review before any disposition. The bounded",
              "pattern scan does not rule out secrets for the PNG/YAML/SQL/JS kinds whose formats the",
              "pattern list doesn't cover; treat 'no hits' as scan-bounded, not cleared."]
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", OUT, "entries:", len(entries), "hits files:", sum(1 for e in entries if hits_for(e["path"])))


if __name__ == "__main__":
    main()
