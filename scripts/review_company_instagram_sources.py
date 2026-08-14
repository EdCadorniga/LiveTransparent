"""Build a read-only company Instagram source and GHL matching review.

This script never writes to GHL, Unipile, n8n, or Postgres. It intentionally
leaves Instagram identity resolution as ``pending_unipile_validation`` until a
later, approved step can validate company-page account type through Unipile.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / ".tmp" / "company-instagram-review"
GHL_BASE = "https://services.leadconnectorhq.com"
GHL_VERSION = "2021-07-28"
LOCATION_ID = "Zwz4relUXVPxx8uohnjV"

AUDIENCE_BY_FILE = {
    "Brands.csv": ("dan_brands", "brands_pool"),
    "Dispensaries.csv": ("dan_dispensaries", "dispensaries_pool"),
}

FIELD_IDS = {
    "emerald_contact_id": "R0wbDRyzZz34PMlQSRWN",
    "source_file": "ILurFacMbAaHz2DdGjPa",
    "company_urls": "z5nj8ENOnnNJcbKCvNtO",
    "location_urls": "JF2P7HzqL75SXXXfgTvQ",
    "contact_urls": "EyaG9tSvOfMqCAilq2nj",
}

PROTECTED_INSTAGRAM_FIELDS = {
    "Instagram Username": "8k6vF61VBIysdIXXFQD5",
    "Instagram Profile URL": "beGMXoidqHdYqAQDORWX",
    "Instagram Profile Provider ID": "fYYUrFLABP5l0w7RdK7Y",
    "Instagram Chat Attendee ID": "SQdQw0MNvk8uQbr4yDZU",
    "Instagram Chat ID": "ab6euY7qo5klhUSe7VWu",
}

URL_COLUMNS = (
    "Company non-LinkedIn URL(s)",
    "Location non-LinkedIn URL(s)",
    "Contact non-LinkedIn URL(s)",
)


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def normalized_text(value: Any) -> str:
    return re.sub(r"\s+", " ", clean(value)).strip().casefold()


def normalized_email(value: Any) -> str:
    return clean(value).casefold()


def normalized_phone(value: Any) -> str:
    digits = re.sub(r"\D", "", clean(value))
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return digits


def split_values(value: Any) -> list[str]:
    raw = clean(value)
    if not raw:
        return []
    return [part.strip() for part in re.split(r"\s*[|,]\s*", raw) if part.strip()]


def source_urls(row: dict[str, str]) -> list[dict[str, str]]:
    urls: list[dict[str, str]] = []
    for column in URL_COLUMNS:
        for raw_url in split_values(row.get(column)):
            urls.append({"source_column": column, "source_url": raw_url})
    return urls


def normalize_url(value: str) -> str:
    raw = clean(value)
    if not raw:
        return ""
    candidate = raw if re.match(r"^https?://", raw, re.I) else f"https://{raw}"
    try:
        parsed = urllib.parse.urlsplit(candidate)
    except ValueError:
        return ""
    host = clean(parsed.hostname).casefold().removeprefix("www.")
    if not host:
        return ""
    path = re.sub(r"/{2,}", "/", parsed.path or "/").rstrip("/") or "/"
    return urllib.parse.urlunsplit(("https", host, path, "", ""))


def instagram_candidate(value: str) -> tuple[str, str]:
    normalized = normalize_url(value)
    if not normalized:
        return "", "invalid_url"
    parsed = urllib.parse.urlsplit(normalized)
    if parsed.hostname not in {"instagram.com", "instagr.am"}:
        return "", "not_instagram"
    parts = [part for part in parsed.path.split("/") if part]
    if not parts:
        return "", "missing_handle"
    if parts[0].casefold() in {"p", "reel", "reels", "tv", "stories", "explore"}:
        return "", "content_url"
    handle = parts[0].lstrip("@").casefold()
    if not re.fullmatch(r"[a-z0-9._]{1,30}", handle, re.I):
        return "", "invalid_handle"
    return handle, "candidate"


def load_env_file() -> dict[str, str]:
    values: dict[str, str] = {}
    env_path = ROOT / ".env"
    if not env_path.exists():
        return values
    for line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def ghl_token() -> str:
    env = load_env_file()
    return clean(os.environ.get("GHL_PIT") or os.environ.get("GHL_API_KEY") or env.get("GHL_PIT") or env.get("GHL_API_KEY"))


def ghl_get(path: str, token: str, query: dict[str, Any] | None = None) -> dict[str, Any]:
    params = dict(query or {})
    params.setdefault("locationId", LOCATION_ID)
    url = f"{GHL_BASE}{path}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Version": GHL_VERSION,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "LiveTransparent-read-only-review/1.0",
        },
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        body = response.read().decode("utf-8")
    parsed = json.loads(body)
    return parsed if isinstance(parsed, dict) else {}


def contact_custom_fields(contact: dict[str, Any]) -> dict[str, str]:
    fields = contact.get("customFields") or contact.get("custom_fields") or []
    if isinstance(fields, dict):
        return {clean(key): clean(value) for key, value in fields.items()}
    result: dict[str, str] = {}
    for field in fields if isinstance(fields, list) else []:
        if not isinstance(field, dict):
            continue
        field_id = clean(field.get("id") or field.get("fieldId"))
        value = clean(field.get("value") or field.get("fieldValue"))
        if field_id:
            result[field_id] = value
    return result


def contact_value(contact: dict[str, Any], field_id: str) -> str:
    return clean(contact_custom_fields(contact).get(field_id))


def contact_name(contact: dict[str, Any]) -> str:
    return clean(contact.get("name") or " ".join(filter(None, [contact.get("firstName"), contact.get("lastName")]))).strip()


def contact_tags(contact: dict[str, Any]) -> set[str]:
    tags = contact.get("tags") or []
    if isinstance(tags, str):
        tags = split_values(tags)
    return {normalized_text(tag) for tag in tags if clean(tag)}


def fetch_audience_contacts(token: str, max_pages: int = 200) -> list[dict[str, Any]]:
    contacts: list[dict[str, Any]] = []
    start_after = 0
    start_after_id = ""
    seen: set[str] = set()
    for _ in range(max_pages):
        query: dict[str, Any] = {"limit": 100}
        if start_after:
            query["startAfter"] = start_after
        if start_after_id:
            query["startAfterId"] = start_after_id
        response = ghl_get("/contacts/", token, query)
        page = response.get("contacts") or []
        if not isinstance(page, list) or not page:
            break
        for contact in page:
            if not isinstance(contact, dict):
                continue
            contact_id = clean(contact.get("id") or contact.get("contactId"))
            if contact_id and contact_id not in seen:
                seen.add(contact_id)
                contacts.append(contact)
        meta = response.get("meta") or {}
        cursor = page[-1].get("startAfter") if isinstance(page[-1], dict) else None
        if isinstance(cursor, list) and len(cursor) >= 2:
            next_start, next_id = cursor[0], cursor[1]
        else:
            next_start = meta.get("startAfter") or response.get("startAfter")
            next_id = meta.get("startAfterId") or response.get("startAfterId")
        if next_start is None or not next_id or (next_start == start_after and next_id == start_after_id):
            break
        start_after = int(next_start)
        start_after_id = clean(next_id)
    return [contact for contact in contacts if contact_tags(contact) & {"brands_pool", "dispensaries_pool"}]


def source_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for file_name in AUDIENCE_BY_FILE:
        path = ROOT / "data" / file_name
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row_number, row in enumerate(csv.DictReader(handle), start=2):
                campaign, source_tag = AUDIENCE_BY_FILE[file_name]
                rows.append(
                    {
                        "source_file": file_name,
                        "source_row": str(row_number),
                        "campaign_key": campaign,
                        "source_tag": source_tag,
                        **{key: clean(value) for key, value in row.items()},
                    }
                )
    return rows


def build_contact_indexes(contacts: Iterable[dict[str, Any]]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    indexes = {key: defaultdict(list) for key in ("emerald", "source_file", "email", "phone", "company_name")}
    for contact in contacts:
        fields = contact_custom_fields(contact)
        source_file = clean(fields.get(FIELD_IDS["source_file"]))
        source_stem = re.sub(r"\.csv$", "", source_file, flags=re.I)
        values = {
            "emerald": contact_value(contact, FIELD_IDS["emerald_contact_id"]),
            "source_file": normalized_text(source_file),
            "email": normalized_email(contact.get("email")),
            "phone": normalized_phone(contact.get("phone")),
            "company_name": normalized_text(contact.get("companyName") or contact.get("company_name")),
        }
        for key, value in values.items():
            if value:
                indexes[key][value].append(contact)
        if source_stem:
            indexes["source_file"][normalized_text(source_stem)].append(contact)
    return indexes


def match_row(row: dict[str, str], indexes: dict[str, dict[str, list[dict[str, Any]]]]) -> tuple[list[dict[str, Any]], str, str]:
    emerald_id = clean(row.get("Emerald Contact ID"))
    email = normalized_email(row.get("Primary Email"))
    phone = normalized_phone(row.get("Primary Phone"))
    company = normalized_text(row.get("Company Name(s)"))
    candidates: list[dict[str, Any]] = []
    method = "unmatched"
    for key, value, label in (
        ("emerald", emerald_id, "emerald_contact_id"),
        ("source_file", normalized_text(clean(row.get("Em_Source_File") or row.get("source_file"))), "source_file"),
        ("email", email, "email"),
        ("phone", phone, "phone"),
    ):
        if not value:
            continue
        candidates = indexes[key].get(value, [])
        if candidates:
            method = label
            break
    if not candidates and company:
        candidates = indexes["company_name"].get(company, [])
        if candidates:
            method = "company_name_review_only"
    unique = {clean(contact.get("id")): contact for contact in candidates if clean(contact.get("id"))}
    contacts = list(unique.values())
    if len(contacts) > 1:
        return contacts, "conflict", method
    if len(contacts) == 1:
        return contacts, "matched", method
    return [], "unresolved", method


def review_row(row: dict[str, str], contacts: list[dict[str, Any]], status: str, match_method: str) -> dict[str, Any]:
    candidates: list[dict[str, str]] = []
    malformed: list[str] = []
    for source in source_urls(row):
        normalized = normalize_url(source["source_url"])
        handle, reason = instagram_candidate(source["source_url"])
        if reason == "candidate":
            candidates.append({**source, "normalized_url": normalized, "normalized_handle": handle})
        elif "instagram" in source["source_url"].casefold() or reason not in {"not_instagram", ""}:
            malformed.append({**source, "normalized_url": normalized, "reason": reason})
    handles = sorted({candidate["normalized_handle"] for candidate in candidates})
    if status == "matched" and not candidates:
        status = "unresolved"
    if len(handles) > 1:
        status = "ambiguous"
    primary_contact = contacts[0] if len(contacts) == 1 else {}
    return {
        "source_file": row["source_file"],
        "source_row": int(row["source_row"]),
        "campaign_key": row["campaign_key"],
        "source_tag": row["source_tag"],
        "emerald_contact_id": clean(row.get("Emerald Contact ID")),
        "first_name": clean(row.get("First Name")),
        "last_name": clean(row.get("Last Name")),
        "company_name": clean(row.get("Company Name(s)")),
        "primary_email": clean(row.get("Primary Email")),
        "primary_phone": clean(row.get("Primary Phone")),
        "ghl_contact_ids": [clean(contact.get("id")) for contact in contacts],
        "ghl_contact_names": [contact_name(contact) for contact in contacts],
        "match_status": status,
        "match_method": match_method,
        "instagram_resolution_status": "pending_unipile_validation" if handles else "no_candidate_url",
        "instagram_handles": handles,
        "instagram_candidates": candidates,
        "malformed_or_rejected_urls": malformed,
        "review_required": status != "matched" or len(handles) != 1,
        "protected_contact_instagram_fields": PROTECTED_INSTAGRAM_FIELDS,
    }


def write_reports(rows: list[dict[str, Any]], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "review.json").write_text(json.dumps(rows, indent=2, ensure_ascii=True), encoding="utf-8")
    fields = [
        "source_file", "source_row", "campaign_key", "source_tag", "emerald_contact_id",
        "first_name", "last_name", "company_name", "primary_email", "primary_phone",
        "ghl_contact_ids", "ghl_contact_names", "match_status", "match_method",
        "instagram_resolution_status", "instagram_handles", "review_required",
    ]
    with (output / "review.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: json.dumps(row[field], ensure_ascii=True) if isinstance(row[field], list) else row[field] for field in fields})
    summary: dict[str, Any] = {
        "read_only": True,
        "rows": len(rows),
        "by_match_status": counts(rows, "match_status"),
        "by_resolution_status": counts(rows, "instagram_resolution_status"),
        "unique_handles": len({handle for row in rows for handle in row["instagram_handles"]}),
        "duplicate_handle_rows": duplicate_handle_rows(rows),
        "contact_level_fields_mutated": False,
        "company_level_fields_created": False,
        "unipile_messages_sent": False,
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8")


def counts(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    result: dict[str, int] = defaultdict(int)
    for row in rows:
        result[clean(row.get(field))] += 1
    return dict(sorted(result.items()))


def duplicate_handle_rows(rows: list[dict[str, Any]]) -> int:
    by_handle: dict[str, set[tuple[str, int]]] = defaultdict(set)
    for row in rows:
        for handle in row["instagram_handles"]:
            by_handle[handle].add((row["source_file"], row["source_row"]))
    return sum(len(items) for items in by_handle.values() if len(items) > 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--offline", action="store_true", help="Build source-only review without fetching live GHL contacts")
    args = parser.parse_args()

    rows = source_rows()
    if args.offline:
        contacts: list[dict[str, Any]] = []
    else:
        token = ghl_token()
        if not token:
            print("GHL_PIT or GHL_API_KEY is required unless --offline is used", file=sys.stderr)
            return 2
        try:
            contacts = fetch_audience_contacts(token)
        except Exception as exc:  # pragma: no cover - depends on live API
            print(f"Live GHL read failed: {exc}", file=sys.stderr)
            return 1

    indexes = build_contact_indexes(contacts)
    reviewed: list[dict[str, Any]] = []
    for row in rows:
        matched, status, method = match_row(row, indexes)
        reviewed.append(review_row(row, matched, status if contacts else "unresolved", method if contacts else "offline"))
    write_reports(reviewed, args.output)
    print(json.dumps({"output": str(args.output), "rows": len(reviewed), "ghl_contacts_read": len(contacts), "read_only": True}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
