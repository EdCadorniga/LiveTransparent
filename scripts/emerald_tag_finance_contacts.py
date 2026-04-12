#!/usr/bin/env python3
"""
Tag Emerald finance contacts without colliding with executive/marketing tags.

Default mode is dry-run:
  - Reads Emerald contacts
  - Detects finance persona from Em_Roles
  - Infers MSO/SSO from existing Emerald source tags
  - Skips contacts already tagged as executive/marketing source types
  - Prints planned finance source tag additions

Live mode (--live):
  - Adds one finance source tag:
    - cannabis-retail-mso-finance-1 or cannabis-retail-sso-finance-1
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests


CODEX_CONFIG = Path.home() / ".codex" / "config.toml"

EMERALD_TAG = "emerald"
EXEC_TAGS = {
    "cannabis-retail-mso-executive-1",
    "cannabis-retail-mso-executive-2",
    "cannabis-retail-sso-executive-1",
    "cannabis-retail-sso-executive-2",
}
MKT_TAGS = {
    "cannabis-retail-mso-marketing-1",
    "cannabis-retail-sso-marketing-1",
}
FIN_MSO_TAG = "cannabis-retail-mso-finance-1"
FIN_SSO_TAG = "cannabis-retail-sso-finance-1"

FINANCE_KEYWORDS = (
    "finance",
    "financial",
    "cfo",
    "controller",
    "accounting",
    "fp&a",
    "treasury",
    "bookkeeper",
    "accounts payable",
    "accounts receivable",
)


@dataclass
class Cfg:
    location_id: str
    pit: str


class GhlClient:
    def __init__(self, pit: str):
        self.base = "https://services.leadconnectorhq.com"
        self.s = requests.Session()
        self.s.headers.update(
            {
                "Authorization": f"Bearer {pit}",
                "Version": "2021-07-28",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        r = self.s.get(f"{self.base}{path}", params=params, timeout=60)
        self._raise(r)
        return r.json()

    def post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        r = self.s.post(f"{self.base}{path}", json=body, timeout=60)
        self._raise(r)
        return r.json() if r.text.strip() else {}

    @staticmethod
    def _raise(r: requests.Response) -> None:
        if r.status_code >= 400:
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:800]}")


def load_cfg() -> Cfg:
    txt = CODEX_CONFIG.read_text(encoding="utf-8", errors="ignore")
    loc = re.search(r'GHL_LOCATION_ID\s*=\s*"([^"]+)"', txt)
    pit = re.search(r'GHL_PIT\s*=\s*"([^"]+)"', txt)
    if not loc or not pit:
        raise RuntimeError("Missing GHL_LOCATION_ID/GHL_PIT in ~/.codex/config.toml")
    return Cfg(location_id=loc.group(1), pit=pit.group(1))


def custom_field_map(client: GhlClient, location_id: str) -> dict[str, str]:
    data = client.get(f"/locations/{location_id}/customFields", params={"model": "contact"})
    out: dict[str, str] = {}
    for row in data.get("customFields", []):
        name = str(row.get("name", "")).strip()
        cid = str(row.get("id", "")).strip()
        if name and cid:
            out[name] = cid
    return out


def fetch_emerald_contacts(
    client: GhlClient, location_id: str, limit: int
) -> list[dict[str, Any]]:
    page = 1
    left = limit
    out: list[dict[str, Any]] = []
    while left > 0:
        page_limit = min(100, left)
        body = {
            "locationId": location_id,
            "page": page,
            "pageLimit": page_limit,
            "filters": [{"field": "tags", "operator": "contains", "value": EMERALD_TAG}],
        }
        try:
            data = client.post("/contacts/search", body)
        except Exception as e:
            # Some tenants return HTTP 400 when paging too deep; keep partial results
            # rather than failing the entire run.
            print(f"WARN  contacts/search stopped at page={page}: {e}")
            break
        rows = data.get("contacts", [])
        out.extend(rows)
        if not rows or len(rows) < page_limit:
            break
        left -= len(rows)
        page += 1
    return out[:limit]


def get_cf(contact: dict[str, Any], field_id: str) -> str:
    for row in contact.get("customFields", []):
        if str(row.get("id")) == field_id:
            return str(row.get("value", "") or "").strip()
    return ""


def has_finance_role(roles_text: str) -> bool:
    roles = (roles_text or "").lower()
    return any(k in roles for k in FINANCE_KEYWORDS)


def infer_company_type(tags: set[str]) -> str:
    if any(t.startswith("cannabis-retail-mso-") for t in tags):
        return "mso"
    if any(t.startswith("cannabis-retail-sso-") for t in tags):
        return "sso"
    return ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=5000, help="Max Emerald contacts to scan")
    ap.add_argument("--live", action="store_true", help="Apply finance source tags")
    args = ap.parse_args()

    cfg = load_cfg()
    client = GhlClient(cfg.pit)
    field_ids = custom_field_map(client, cfg.location_id)
    if "Em_Roles" not in field_ids:
        raise RuntimeError("Missing required custom field: Em_Roles")
    roles_id = field_ids["Em_Roles"]

    contacts = fetch_emerald_contacts(client, cfg.location_id, args.limit)
    print(f"Fetched Emerald contacts: {len(contacts)} (limit={args.limit})")

    stats = {
        "processed": 0,
        "finance_candidates": 0,
        "skip_no_roles": 0,
        "skip_not_finance": 0,
        "skip_company_unknown": 0,
        "skip_conflict_person_type": 0,
        "already_tagged": 0,
        "planned": 0,
        "tagged": 0,
        "errors": 0,
    }

    for c in contacts:
        stats["processed"] += 1
        cid = str(c.get("id", "")).strip()
        email = str(c.get("email", "")).strip()
        tags = {str(t).strip().lower() for t in c.get("tags", [])}
        roles = get_cf(c, roles_id)

        if not roles:
            stats["skip_no_roles"] += 1
            continue
        if not has_finance_role(roles):
            stats["skip_not_finance"] += 1
            continue
        stats["finance_candidates"] += 1

        if tags & EXEC_TAGS or tags & MKT_TAGS:
            stats["skip_conflict_person_type"] += 1
            continue

        company = infer_company_type(tags)
        if not company:
            stats["skip_company_unknown"] += 1
            continue

        finance_tag = FIN_MSO_TAG if company == "mso" else FIN_SSO_TAG
        if finance_tag in tags:
            stats["already_tagged"] += 1
            continue

        stats["planned"] += 1
        print(f"PLAN  {cid} {email} add={finance_tag}")
        if not args.live:
            continue

        try:
            client.post(f"/contacts/{cid}/tags", {"tags": [finance_tag]})
            stats["tagged"] += 1
            print(f"TAG   {cid} {email} added={finance_tag}")
        except Exception as e:
            stats["errors"] += 1
            print(f"ERR   {cid} {email} {e}")

    print("\nSummary")
    for k, v in stats.items():
        print(f"{k}: {v}")
    print(f"mode={'LIVE' if args.live else 'DRY_RUN'}")


if __name__ == "__main__":
    main()
