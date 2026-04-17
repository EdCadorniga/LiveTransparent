#!/usr/bin/env python3
import argparse
import csv
import json
import re
from pathlib import Path


def nk(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (s or "").strip().lower()).strip("_")


def load_headers(csv_path: Path):
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f)
        return [h.strip() for h in next(r)]


def build_report(spec: dict, headers: list[str], csv_path: str):
    header_norm = {nk(h): h for h in headers}
    header_norm_set = set(header_norm.keys())

    field_reports = []
    matched_header_norms = set()
    covered_header_norms = set()

    for field in spec["fields"]:
        aliases = field.get("aliases", [])
        alias_norms = [nk(a) for a in aliases]
        for a in alias_norms:
            if a in header_norm_set:
                covered_header_norms.add(a)
        matched = None
        for a in alias_norms:
            if a in header_norm_set:
                matched = header_norm[a]
                matched_header_norms.add(a)
                break
        field_reports.append(
            {
                "target": field["target"],
                "destination": field.get("destination", "postgres_column"),
                "transform": field.get("transform"),
                "aliases": aliases,
                "matched_header": matched,
                "status": "matched" if matched else "missing",
            }
        )

    unmatched_headers = [h for h in headers if nk(h) not in covered_header_norms]

    rule = spec.get("record_rules", {}).get("at_least_one_of", [])
    rule_status = []
    for token in rule:
        candidates = [f for f in field_reports if f["target"] == token]
        matched = any(c["status"] == "matched" for c in candidates)
        rule_status.append({"target": token, "present_in_headers": matched})

    if rule:
        has_any = any(x["present_in_headers"] for x in rule_status)
    else:
        has_any = True

    return {
        "csv_path": csv_path,
        "workflow": spec.get("description"),
        "workflow_id": spec.get("workflowId"),
        "header_count": len(headers),
        "matched_field_count": sum(1 for f in field_reports if f["status"] == "matched"),
        "missing_field_count": sum(1 for f in field_reports if f["status"] == "missing"),
        "unmatched_headers": unmatched_headers,
        "record_rule": {
            "type": "at_least_one_of",
            "targets": rule,
            "per_target": rule_status,
            "pass": has_any,
        },
        "fields": field_reports,
    }


def main():
    p = argparse.ArgumentParser(description="Validate Apollo CSV headers against ingestion mapping spec")
    p.add_argument("--mode", choices=["postgres_ingestion", "ghl_ingestion"], required=True)
    p.add_argument("--csv", required=True)
    p.add_argument("--spec", default="cold-outreach-prep/mapping/apollo_csv_mappings.json")
    p.add_argument("--out-json", required=True)
    p.add_argument("--out-md", required=True)
    args = p.parse_args()

    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))["workflows"][args.mode]
    headers = load_headers(Path(args.csv))
    report = build_report(spec, headers, args.csv)

    Path(args.out_json).write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = []
    lines.append(f"# CSV Mapping Validation: {args.mode}")
    lines.append("")
    lines.append(f"- CSV: `{args.csv}`")
    lines.append(f"- Workflow: `{report['workflow']}` (`{report['workflow_id']}`)")
    lines.append(f"- Headers: `{report['header_count']}`")
    lines.append(f"- Mapped fields: `{report['matched_field_count']}`")
    lines.append(f"- Missing mapped fields: `{report['missing_field_count']}`")
    lines.append(f"- Record rule pass (at least one id channel): `{report['record_rule']['pass']}`")
    lines.append("")
    lines.append("## Field Matrix")
    lines.append("")
    lines.append("| Target | Destination | Transform | Matched Header | Status |")
    lines.append("|---|---|---|---|---|")
    for f in report["fields"]:
        lines.append(
            f"| {f['target']} | {f['destination']} | {f['transform'] or ''} | {f['matched_header'] or ''} | {f['status']} |"
        )

    lines.append("")
    lines.append("## Unmatched CSV Headers")
    lines.append("")
    if report["unmatched_headers"]:
        for h in report["unmatched_headers"]:
            lines.append(f"- `{h}`")
    else:
        lines.append("- none")

    Path(args.out_md).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
