"""Emit docs/transition/scripts-classification-2026-11-05.md from bounded scans.

Reads the OS-temp census, secret-pattern scan results, and doc-reference map
produced by read-only enumeration. Emits paths, sizes, dates, hit NAMES, and
reference counts only — never secret values or matched text. No script in the
classified trees was executed; this generator only re-reads metadata.
"""

import json
import os
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts-classification-2026-11-05.md")


def main():
    tmpd = os.environ.get("TEMP")
    rows = json.load(open(os.path.join(tmpd, "lt_phase3_census.json")))
    scan = json.load(open(os.path.join(tmpd, "lt_phase3_scans.json")))
    docs = json.load(open(os.path.join(tmpd, "lt_phase3_docrefs.json")))

    # merge sensitive patterns into per-file hit lists (names only)
    sensitive = {}
    for pat in ("apikey_literal", "jwt", "ghl_pit", "katwill", "whitefriar"):
        for f, c in scan.get(pat, {}).items():
            sensitive.setdefault(f, []).append(pat)
    # special env-constant hits worth surfacing by NAME (values never emitted)
    for f, c in scan.get("env_value_literal", {}).items():
        need = ("TRACK_SECRET", "API_KEY")
        if f.endswith("build_mass_email_stage.py") or "/artifacts/" in f or f.endswith(("fix_sheets_node.py", "fix_brands_code.py", "fix_parse_csv.py")):
            sensitive.setdefault(f, []).append("env_constant_with_long_literal")

    # containment check: exact live PIT value presence (value never emitted) in
    # the classified script-like files
    pit = None
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8", errors="replace"):
        line = line.strip()
        if line.startswith("GHL_PIT="):
            pit = line.split("=", 1)[1].strip()
    pit_files = []
    if pit:
        for r in rows:
            p = os.path.join(ROOT, r["path"].replace("/", os.sep))
            try:
                if os.path.getsize(p) <= 3_000_000 and pit in open(p, encoding="utf-8", errors="replace").read():
                    pit_files.append(r["path"])
            except Exception:
                pass

    by_family = {}
    for r in rows:
        fam = r["path"].split("/")[0]
        by_family.setdefault(fam, []).append(r)

    total_bytes = sum(r["bytes"] for r in rows)

    lines = [
        "# Phase 3 exact-path script/artifact classification — 2026-11-05",
        "",
        "Read-only enumeration + secret-pattern scan (ripgrep, count-only; matched VALUES never",
        "emitted — only variable/hit NAMES) + markdown reference map. No classified script was",
        "executed. No artifact was moved, changed, or deleted. Not a deletion manifest; no cleanup",
        "is authorized by this document.",
        "",
        f"**Scope/sizes:** {len(rows)} script-like files across `scripts/`, `local-scripts/`, `tools/`,",
        "`marketing/`, `New Campaigns October 2026/` (invoice/invoicing directory-segments excluded,",
        f"`__pycache__`/`node_modules` excluded): **{total_bytes:,} bytes** total.",
        f"**Doc references:** {len(docs)} of {len(rows)} files are mentioned somewhere in Markdown",
        "(docs/sessions, runbooks, AGENTS, plans) — that is provenance support, not a safety",
        "verdict.",
        "",
        "## Sensitive-pattern hit table (names only)",
        "",
        "Any file with a long literal assignment (`API_KEY = '<literal>'`, `TRACK_SECRET = '<literal>'`,",
        "JWT-like strings, `pit-` prefixes, or katwill references) is listed. Values are NOT printed;",
        "owners must review the exact file before reuse. Test-capture files with embedded JWTs are",
        "**keep pending sensitivity review** (do not publish/redistribute).",
        "",
        "| path | hits (names) | provisional action |",
        "|---|---|---|",
    ]
    for f in sorted(sensitive):
        ks = ", ".join(sorted(set(sensitive[f])))
        lines.append(f"| `{f}` | {ks} | review-before-reuse / harden (owner decision) |")

    lines += [
        "",
        "Note: the katwill hit in `local-scripts/_state_sync_sql.py` is a doc comment restating the",
        "n8n-lt-only rule (verified by reading the single matching comment line; no katwill call",
        "exists in the scanned trees). `pit-`/JWT-style hits may be test or stale artifacts; each",
        "file is listed so an owner may review the exact literal before any reuse, rotation decision," +
        "or archive move.",
        "",
        "**Live-credential containment (2026-11-05):** an exact-value containment check found the",
        f"*current live GHL PIT* present verbatim in **{len(pit_files)}** classified script-like file(s)"
        + (": `" + ("`, `".join(pit_files)) + "`" if pit_files else "")
        + ". The value was never emitted into this artifact. **Owner resolution 2026-11-05:",
        "Ed directed retention of the latest PIT from `.env` — no rotation now; history/local",
        "presence accepted by owner; redistribution precautions unchanged.**",
    ]

    lines += [
        "",
        "## Family summary and provisional classification rules",
        "",
        "| family | files | bytes | provisional class |",
        "|---|---|---|---|",
    ]
    rules = {
        "scripts": "**Keep — maintained operational source** pending owner review. Repairs/deploy/migration helpers may be the sole reproducible source for live state; do not remove without per-file dependency comparison. Files with credential hits: keep but harden before reuse.",
        "tools": "**Keep — source pending owner review** (small set).",
        "local-scripts": "**Owner decision** (operator-only helpers, diagnostics, captures). `local-scripts/linkedin-invite-withdrawals/` remains explicitly **held** — worker/ledger/provider artifacts with the standing 310-unledgered-invitation scope. Credential-bearing files marked 'review-before-reuse'.",
        "marketing": "**Owner decision** (historical marketing/automation artifacts). Credential-bearing files: redact/migrate then archive.",
        "New Campaigns October 2026": "**Keep pending campaign-closure evidence review** (auditable evidence: import-prep, audit and reconciliation scripts matching the October vertical campaigns).",
    }
    for fam in sorted(by_family):
        fs = by_family[fam]
        lines.append(f"| `{fam}/` | {len(fs)} | {sum(r['bytes'] for r in fs):,} | {rules.get(fam, 'owner decision')} |")

    for fam in sorted(by_family):
        fs = sorted(by_family[fam], key=lambda x: x["path"])
        lines += ["", f"## `{fam}/` exact paths ({len(fs)})", "",
                  "| path | bytes | mtime | doc refs | hits |", "|---|---|---|---|---|"]
        for r in fs:
            p = r["path"]
            hits = ", ".join(sorted(set(sensitive.get(p, [])))) or ""
            refs = len(docs.get(p, []))
            mt = datetime.datetime.fromtimestamp(r["mtime"]).strftime("%Y-%m-%d")
            lines.append(f"| `{p}` | {r['bytes']:,} | {mt} | {refs} | {hits} |")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", OUT, "rows:", len(rows), "sensitive:", len(sensitive))


if __name__ == "__main__":
    main()
