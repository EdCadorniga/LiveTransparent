from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path
from typing import Iterable


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "ghl-import"

GHL_HEADERS = [
    "First Name",
    "Last Name",
    "Email",
    "Phone",
    "Corporate Phone",
    "Company Name",
    "Company Name for Emails",
    "Title",
    "Website",
    "City",
    "State",
    "Person Linkedin Url",
    "Company Linkedin Url",
    "Facebook Url",
    "Twitter Url",
    "Tags",
    "Batch_Upload",
    "Em_Emerald_Contact_ID",
    "Em_All_Known_Emails",
    "Em_All_Known_Phones",
    "Em_Roles",
    "Em_Seniorities",
    "Em_Contact_LinkedIn_URLs",
    "Em_Contact_Non_LinkedIn_URLs",
    "Em_Location_Legal_Names",
    "Em_Location_Display_Names",
    "Em_Location_LinkedIn_URLs",
    "Em_Location_Non_LinkedIn_URLs",
    "Em_HQ_Names",
    "Em_Ultimate_HQ_Names",
    "Em_Company_LinkedIn_URLs",
    "Em_Company_Non_LinkedIn_URLs",
    "Em_Source_File",
]


def clean(value: str | None) -> str:
    return (value or "").strip()


def split_multi(value: str | None) -> list[str]:
    raw = clean(value)
    if not raw:
        return []
    parts = re.split(r"\s*\|\s*|\s*,\s*", raw)
    return [part.strip() for part in parts if part.strip()]


def normalize_phone(value: str | None) -> str:
    digits = re.sub(r"\D", "", clean(value))
    if not digits:
        return ""
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        return f"+1{digits}"
    if 8 <= len(digits) <= 15:
        return f"+{digits}" if not digits.startswith("+") else digits
    return ""


def first_non_empty(values: Iterable[str]) -> str:
    for value in values:
        value = clean(value)
        if value:
            return value
    return ""


def first_url_matching(urls: list[str], pattern: str) -> str:
    rx = re.compile(pattern, re.IGNORECASE)
    for url in urls:
        if rx.search(url):
            return url
    return ""


def first_website(urls: list[str]) -> str:
    for url in urls:
        lower = url.lower()
        if any(domain in lower for domain in ["linkedin.com", "facebook.com", "instagram.com", "twitter.com", "x.com", "youtube.com", "yelp.com", "crunchbase.com", "pinterest.com"]):
            continue
        if lower.startswith("http://") or lower.startswith("https://"):
            return url
    return ""


def derive_segment(file_name: str) -> str:
    stem = Path(file_name).stem
    return stem.lower().replace(" ", "-")


def build_tags(file_name: str) -> str:
    stem = Path(file_name).stem
    segment_tag = stem.lower()
    return ", ".join(["emerald", segment_tag])


def is_valid_phone(value: str) -> bool:
    return bool(re.fullmatch(r"\+\d{8,15}", clean(value)))


def map_row(row: dict[str, str], source_file: str) -> dict[str, str]:
    person_linkedins = split_multi(row.get("Contact LinkedIn URL(s)"))
    company_linkedins = split_multi(row.get("Company LinkedIn URL(s)"))
    company_non_linkedin = split_multi(row.get("Company non-LinkedIn URL(s)"))
    contact_non_linkedin = split_multi(row.get("Contact non-LinkedIn URL(s)"))

    all_candidate_urls = company_non_linkedin + contact_non_linkedin

    company_name = first_non_empty(split_multi(row.get("Company Name(s)")))
    source_stem = Path(source_file).stem
    mapped = {
        "First Name": clean(row.get("First Name")),
        "Last Name": clean(row.get("Last Name")),
        "Email": clean(row.get("Primary Email")),
        "Phone": normalize_phone(row.get("Primary Phone")),
        "Corporate Phone": "",
        "Company Name": company_name,
        "Company Name for Emails": company_name,
        "Title": first_non_empty(split_multi(row.get("Titles"))),
        "Website": first_website(all_candidate_urls),
        "City": clean(row.get("Contact City")),
        "State": clean(row.get("Contact State")),
        "Person Linkedin Url": first_non_empty(person_linkedins),
        "Company Linkedin Url": first_non_empty(company_linkedins),
        "Facebook Url": first_url_matching(all_candidate_urls, r"facebook\.com"),
        "Twitter Url": first_url_matching(all_candidate_urls, r"(twitter\.com|x\.com)"),
        "Tags": build_tags(source_file),
        "Batch_Upload": source_stem,
        "Em_Emerald_Contact_ID": clean(row.get("Emerald Contact ID")),
        "Em_All_Known_Emails": clean(row.get("All Known Emails")) or clean(row.get("Primary Email")),
        "Em_All_Known_Phones": clean(row.get("All Known Phones")) or clean(row.get("Primary Phone")),
        "Em_Roles": clean(row.get("Roles")),
        "Em_Seniorities": clean(row.get("Seniorities")),
        "Em_Contact_LinkedIn_URLs": clean(row.get("Contact LinkedIn URL(s)")),
        "Em_Contact_Non_LinkedIn_URLs": clean(row.get("Contact non-LinkedIn URL(s)")),
        "Em_Location_Legal_Names": clean(row.get("Location Legal Name(s)")),
        "Em_Location_Display_Names": clean(row.get("Location Display Name(s)")),
        "Em_Location_LinkedIn_URLs": clean(row.get("Location LinkedIn URL(s)")),
        "Em_Location_Non_LinkedIn_URLs": clean(row.get("Location non-LinkedIn URL(s)")),
        "Em_HQ_Names": clean(row.get("HQ Name(s)")),
        "Em_Ultimate_HQ_Names": clean(row.get("Ultimate HQ Name(s)")),
        "Em_Company_LinkedIn_URLs": clean(row.get("Company LinkedIn URL(s)")),
        "Em_Company_Non_LinkedIn_URLs": clean(row.get("Company non-LinkedIn URL(s)")),
        "Em_Source_File": source_stem,
    }
    return mapped


def dedupe_key(row: dict[str, str]) -> tuple[str, str]:
    email = clean(row["Email"]).lower()
    name = f"{clean(row['First Name']).lower()}|{clean(row['Last Name']).lower()}|{clean(row['Company Name']).lower()}"
    phone = clean(row["Phone"])
    if email:
        return "email", email
    if name.strip("||"):
        return "name_company", name
    return "phone", phone


def choose_better(existing: dict[str, str], candidate: dict[str, str]) -> dict[str, str]:
    def score(row: dict[str, str]) -> int:
        important = [
            "Email",
            "Phone",
            "Company Name",
            "Title",
            "Website",
            "City",
            "State",
            "Person Linkedin Url",
            "Company Linkedin Url",
            "Facebook Url",
            "Twitter Url",
        ]
        return sum(1 for field in important if clean(row.get(field)))

    if score(candidate) > score(existing):
        return candidate
    return existing


def row_is_importable(row: dict[str, str]) -> bool:
    return bool(clean(row["Email"]) or clean(row["Phone"]))


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    source_files = sorted(BASE_DIR.glob("*.csv"))
    all_rows: list[dict[str, str]] = []
    counts = Counter()

    for csv_path in source_files:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            for raw_row in reader:
                mapped = map_row(raw_row, csv_path.name)
                counts["source_rows"] += 1
                if row_is_importable(mapped):
                    all_rows.append(mapped)
                    counts["importable_rows"] += 1
                else:
                    counts["skipped_missing_email_and_phone"] += 1

    deduped: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in all_rows:
        key = dedupe_key(row)
        if key not in deduped:
            deduped[key] = row
        else:
            deduped[key] = choose_better(deduped[key], row)
            counts["dedupe_collisions"] += 1

    deduped_rows = list(deduped.values())
    phone_counts = Counter(
        clean(row["Phone"])
        for row in deduped_rows
        if clean(row["Phone"]) and is_valid_phone(clean(row["Phone"]))
    )

    safe_rows: list[dict[str, str]] = []
    excluded_rows: list[dict[str, str]] = []
    for row in deduped_rows:
        email = clean(row["Email"])
        phone = clean(row["Phone"])
        keep_phone = bool(phone and is_valid_phone(phone) and phone_counts[phone] == 1)
        if phone and not keep_phone and is_valid_phone(phone):
            row["Corporate Phone"] = phone
            row["Phone"] = ""
        elif phone and not is_valid_phone(phone):
            row["Phone"] = ""

        if clean(row["Email"]) or clean(row["Phone"]):
            safe_rows.append(row)
        else:
            excluded_rows.append(row)

    all_path = OUTPUT_DIR / "emerald-contacts.ghl.csv"
    with all_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=GHL_HEADERS)
        writer.writeheader()
        writer.writerows(all_rows)

    deduped_path = OUTPUT_DIR / "emerald-contacts.dedup.ghl.csv"
    with deduped_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=GHL_HEADERS)
        writer.writeheader()
        writer.writerows(safe_rows)

    review_headers = GHL_HEADERS + ["exclude_reason"]
    review_path = OUTPUT_DIR / "emerald-contacts.dedup.review-shared-phone.csv"
    with review_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=review_headers)
        writer.writeheader()
        for row in excluded_rows:
            out = dict(row)
            out["exclude_reason"] = "phone_only_shared_or_invalid"
            writer.writerow(out)

    summary_path = OUTPUT_DIR / "emerald-contacts.import-summary.txt"
    summary_lines = [
        f"Source files: {len(source_files)}",
        f"Source rows: {counts['source_rows']}",
        f"Importable rows: {counts['importable_rows']}",
        f"Skipped rows missing both email and phone: {counts['skipped_missing_email_and_phone']}",
        f"Deduped rows before phone safety filter: {len(deduped_rows)}",
        f"Deduped rows in GHL-safe import: {len(safe_rows)}",
        f"Rows moved to review file (phone-only shared/invalid): {len(excluded_rows)}",
        f"Deduplication collisions resolved: {counts['dedupe_collisions']}",
        "Export shape: GHL-safe standard headers + live Em_* custom-field headers + Batch_Upload",
        "",
        f"All rows CSV: {all_path.name}",
        f"Deduped CSV: {deduped_path.name}",
        f"Review CSV: {review_path.name}",
    ]
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")

    print("\n".join(summary_lines))


if __name__ == "__main__":
    main()
