from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_XLSX = ROOT / "Contact List.v5.xlsx"
OUT_DIR = ROOT / "contact-list-v5" / "ed-mapping"
OUT_CSV = OUT_DIR / "ed-mapping-tags.by-email.csv"
OUT_IMPORT_CSV = OUT_DIR / "ed-mapping-tags.ghl-import.csv"
OUT_CONFLICT_CSV = OUT_DIR / "ed-mapping-tags.conflicts.csv"
OUT_SUMMARY = OUT_DIR / "ed-mapping-summary.md"

SHEET_NAME = "Masterlist"
HEADER_ROW = 1

EMAIL_COL = "Primary Email"
MAPPING_COL = "Ed Mapping"
FIRST_NAME_COL = "First Name"
LAST_NAME_COL = "Last Name"


def norm_space(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def norm_mapping_label(value: str) -> str:
    label = norm_space(value).lower()
    label = label.replace("&", "and")
    return norm_space(label)


def mapping_tag(value: str) -> str:
    return f"ed mapping - {norm_mapping_label(value)}"


def mapping_sort_key(value: str) -> tuple[int, str]:
    """Stable sorting with DNC first for readability."""
    lowered = norm_mapping_label(value)
    if lowered == "do not contact":
        return (0, lowered)
    return (1, lowered)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_excel(SOURCE_XLSX, sheet_name=SHEET_NAME, header=HEADER_ROW)
    for col in (EMAIL_COL, MAPPING_COL, FIRST_NAME_COL, LAST_NAME_COL):
        if col not in df.columns:
            raise KeyError(f"Missing required column: {col}")

    work = df[[FIRST_NAME_COL, LAST_NAME_COL, EMAIL_COL, MAPPING_COL]].copy()
    work[EMAIL_COL] = work[EMAIL_COL].fillna("").astype(str).str.strip().str.lower()
    work[MAPPING_COL] = work[MAPPING_COL].fillna("").astype(str).map(norm_space)
    work[FIRST_NAME_COL] = work[FIRST_NAME_COL].fillna("").astype(str).map(norm_space)
    work[LAST_NAME_COL] = work[LAST_NAME_COL].fillna("").astype(str).map(norm_space)

    work = work[(work[EMAIL_COL] != "") & (work[MAPPING_COL] != "")]

    grouped = []
    mapping_counts = Counter()
    conflict_count = 0
    dnc_count = 0

    for email, g in work.groupby(EMAIL_COL, sort=True):
        mappings = sorted(set(g[MAPPING_COL].tolist()), key=mapping_sort_key)
        lowered = {norm_mapping_label(m) for m in mappings}
        has_conflict = len(lowered) > 1
        has_dnc = "do not contact" in lowered

        tags = [mapping_tag(m) for m in mappings]
        if has_dnc:
            tags.extend(["do not contact", "do not nurture"])
            dnc_count += 1
        if has_conflict:
            tags.append("ed mapping - conflict")
            conflict_count += 1

        # Keep tag order stable and dedup.
        dedup_tags = []
        seen = set()
        for t in tags:
            key = t.lower()
            if key in seen:
                continue
            seen.add(key)
            dedup_tags.append(t)

        primary_mapping = "DO NOT CONTACT" if has_dnc else mappings[0]
        for m in mappings:
            mapping_counts[m] += 1

        first_name = next((x for x in g[FIRST_NAME_COL].tolist() if x), "")
        last_name = next((x for x in g[LAST_NAME_COL].tolist() if x), "")

        grouped.append(
            {
                "Email": email,
                "First Name": first_name,
                "Last Name": last_name,
                "Tags": ", ".join(dedup_tags),
                "Ed Mapping Primary": primary_mapping,
                "Ed Mapping All": " | ".join(mappings),
                "Has Mapping Conflict": "Yes" if has_conflict else "No",
                "Has Do Not Contact": "Yes" if has_dnc else "No",
            }
        )

    out_df = pd.DataFrame(grouped).sort_values("Email")
    out_df.to_csv(OUT_CSV, index=False, encoding="utf-8")
    out_df[["Email", "Tags"]].to_csv(OUT_IMPORT_CSV, index=False, encoding="utf-8")
    out_df[out_df["Has Mapping Conflict"] == "Yes"].to_csv(OUT_CONFLICT_CSV, index=False, encoding="utf-8")

    summary_lines = [
        "# Ed Mapping Tagging Summary",
        "",
        f"- Source: `{SOURCE_XLSX}`",
        f"- Sheet: `{SHEET_NAME}` (header row `{HEADER_ROW + 1}`)",
        f"- Output CSV: `{OUT_CSV}`",
        f"- Import CSV (`Email`,`Tags`): `{OUT_IMPORT_CSV}`",
        f"- Conflict review CSV: `{OUT_CONFLICT_CSV}`",
        f"- Unique emails exported: `{len(out_df)}`",
        f"- Emails with mapping conflicts: `{conflict_count}`",
        f"- Emails flagged Do Not Contact: `{dnc_count}`",
        "",
        "## Unique Mapping Counts (By Email)",
        "",
    ]
    for mapping, count in sorted(mapping_counts.items(), key=lambda x: mapping_sort_key(x[0])):
        summary_lines.append(f"- `{mapping}`: `{count}`")
    summary_lines.extend(
        [
            "",
            "## Campaign Guard Rule",
            "",
            "- Add a first branch/if-condition before every email send.",
            "- Block send if contact has either:",
            "  - `do not contact`",
            "  - `do not nurture`",
            "- For persona-specific sends, require the exact persona tag and exclude other persona tags.",
            "",
            "## Import Notes",
            "",
            "- Use `Email` + `Tags` from the CSV for bulk tag update.",
            "- In GHL import, choose tag behavior that appends tags (not overwrite), then dedupe tags.",
            "- Contacts with `Has Mapping Conflict = Yes` should be reviewed before persona drip enrollment.",
        ]
    )
    OUT_SUMMARY.write_text("\n".join(summary_lines), encoding="utf-8")

    print(f"Wrote: {OUT_CSV}")
    print(f"Wrote: {OUT_IMPORT_CSV}")
    print(f"Wrote: {OUT_CONFLICT_CSV}")
    print(f"Wrote: {OUT_SUMMARY}")
    print(f"Unique emails: {len(out_df)}")
    print(f"Conflicts: {conflict_count}")
    print(f"DNC emails: {dnc_count}")


if __name__ == "__main__":
    main()
