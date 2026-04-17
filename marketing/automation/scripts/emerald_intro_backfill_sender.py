#!/usr/bin/env python3
"""
Emerald intro backfill sender.

Default mode is dry-run:
  - Reads contacts tagged "seq emerald - intro backfill pending"
  - Resolves profile key (mso/sso + executive/marketing/finance)
  - Prints planned actions

Live mode (--live):
  - Sends intro email via template
  - Writes intro tracking custom fields
  - Adds sent/done tags
  - Removes pending tag
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "emerald-email-campaign" / "profile-intro-template-map.json"
CODEX_CONFIG = Path.home() / ".codex" / "config.toml"


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

    def put(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        r = self.s.put(f"{self.base}{path}", json=body, timeout=60)
        self._raise(r)
        return r.json() if r.text.strip() else {}

    def delete(self, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        r = self.s.delete(f"{self.base}{path}", json=body or {}, timeout=60)
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


def load_template_map() -> dict[str, dict[str, str]]:
    data = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    out: dict[str, dict[str, str]] = {}
    for row in data.get("templates", []):
        k = str(row.get("profileKey", "")).strip().lower()
        v = str(row.get("templateId", "")).strip()
        if k and v:
            out[k] = {"templateId": v, "name": str(row.get("name", "")).strip()}
    return out


def custom_field_map(client: GhlClient, location_id: str) -> dict[str, str]:
    data = client.get(f"/locations/{location_id}/customFields", params={"model": "contact"})
    out: dict[str, str] = {}
    for row in data.get("customFields", []):
        name = str(row.get("name", "")).strip()
        cid = str(row.get("id", "")).strip()
        if name and cid:
            out[name] = cid
    return out


def fetch_contacts_with_pending_tag(
    client: GhlClient, location_id: str, pending_tag: str, limit: int
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
            "filters": [{"field": "tags", "operator": "contains", "value": pending_tag}],
        }
        data = client.post("/contacts/search", body)
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


def has_any(text: str, terms: list[str]) -> bool:
    t = text.lower()
    return any(term in t for term in terms)


def resolve_profile_key(contact: dict[str, Any], roles_text: str) -> str:
    tags = [str(t).strip().lower() for t in contact.get("tags", [])]
    tag_blob = " | ".join(tags)
    roles = roles_text.lower()

    if "mso" in tag_blob:
        company = "mso"
    elif "sso" in tag_blob:
        company = "sso"
    else:
        company = "sso"

    if has_any(roles, ["finance", "financial", "cfo", "controller", "accounting", "fp&a"]):
        person = "finance"
    elif has_any(tag_blob, ["marketing"]):
        person = "marketing"
    elif has_any(tag_blob, ["executive"]):
        person = "executive"
    elif has_any(roles, ["marketing", "growth", "demand", "brand", "media"]):
        person = "marketing"
    elif has_any(
        roles,
        [
            "executive",
            "founder",
            "owner",
            "ceo",
            "coo",
            "president",
            "vp",
            "chief",
            "director",
            "head",
        ],
    ):
        person = "executive"
    else:
        # Conservative fallback to executive if ambiguous.
        person = "executive"

    return f"{company}_{person}"


def should_suppress(contact: dict[str, Any]) -> tuple[bool, str]:
    tags = [str(t).strip().lower() for t in contact.get("tags", [])]
    if "seq emerald - intro sent".lower() in tags:
        return True, "already_intro_sent"
    if "do not nurture" in tags:
        return True, "do_not_nurture"
    if "meeting booked" in tags:
        return True, "meeting_booked"
    if bool(contact.get("dnd")):
        return True, "dnd_true"
    if not str(contact.get("email", "")).strip():
        return True, "missing_email"
    return False, ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=200, help="Max contacts per run")
    ap.add_argument("--live", action="store_true", help="Execute writes and sends")
    args = ap.parse_args()

    cfg = load_cfg()
    template_map = load_template_map()
    client = GhlClient(cfg.pit)

    pending_tag = "seq emerald - intro backfill pending"
    sent_tag = "seq emerald - intro sent"
    done_tag = "seq emerald - intro backfill done"

    field_ids = custom_field_map(client, cfg.location_id)
    required_fields = {
        "roles": "Em_Roles",
        "sender": "marketing_sender_email",
        "intro_sent_at": "Em_Profile_Intro_Sent_At",
        "intro_template_id": "Em_Profile_Intro_Template_Id",
        "intro_profile_key": "Em_Profile_Intro_Profile_Key",
    }
    for k, v in required_fields.items():
        if v not in field_ids:
            raise RuntimeError(f"Missing custom field: {v}")

    # Pull current template metadata (id -> previewUrl) so Email Builder templates
    # can be sent as HTML via conversations/messages.
    tmpl_meta = client.get(
        "/emails/builder",
        params={"locationId": cfg.location_id, "templatesOnly": "true", "limit": 200},
    )
    by_template_id: dict[str, dict[str, str]] = {}
    for row in tmpl_meta.get("builders", []):
        tid = str(row.get("id", "")).strip()
        if tid:
            by_template_id[tid] = {
                "name": str(row.get("name", "")).strip(),
                "previewUrl": str(row.get("previewUrl", "")).strip(),
            }

    contacts = fetch_contacts_with_pending_tag(client, cfg.location_id, pending_tag, args.limit)
    print(f"Fetched pending contacts: {len(contacts)} (limit={args.limit})")

    summary: dict[str, int] = {
        "processed": 0,
        "planned": 0,
        "sent": 0,
        "suppressed": 0,
        "terminal_skips": 0,
        "missing_template": 0,
        "missing_sender": 0,
        "errors": 0,
    }

    for c in contacts:
        summary["processed"] += 1
        cid = str(c.get("id", ""))
        email = str(c.get("email", "")).strip()

        suppress, reason = should_suppress(c)
        if suppress:
            summary["suppressed"] += 1
            print(f"SKIP  {cid} {email} reason={reason}")
            continue

        roles_text = get_cf(c, field_ids[required_fields["roles"]])
        sender_email = get_cf(c, field_ids[required_fields["sender"]])
        profile_key = resolve_profile_key(c, roles_text)
        trow = template_map.get(profile_key, {})
        template_id = str(trow.get("templateId", "")).strip()
        template_name = str(trow.get("name", "")).strip()

        if not template_id:
            summary["missing_template"] += 1
            print(f"SKIP  {cid} {email} reason=missing_template profile={profile_key}")
            continue
        if not sender_email:
            summary["missing_sender"] += 1
            print(f"SKIP  {cid} {email} reason=missing_sender profile={profile_key}")
            continue

        summary["planned"] += 1
        meta = by_template_id.get(template_id, {})
        preview_url = str(meta.get("previewUrl", "")).strip()
        if not preview_url:
            summary["missing_template"] += 1
            print(
                f"SKIP  {cid} {email} reason=missing_template_preview profile={profile_key} template={template_id}"
            )
            continue

        print(f"PLAN  {cid} {email} profile={profile_key} template={template_id} from={sender_email}")

        if not args.live:
            continue

        now_iso = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        try:
            html = requests.get(preview_url, timeout=60).text
            client.post(
                "/conversations/messages",
                {
                    "contactId": cid,
                    "type": "Email",
                    "subject": template_name or f"Emerald Intro - {profile_key}",
                    "html": html,
                    "emailFrom": sender_email,
                },
            )
            client.put(
                f"/contacts/{cid}",
                {
                    "customFields": [
                        {"id": field_ids[required_fields["intro_sent_at"]], "value": now_iso},
                        {"id": field_ids[required_fields["intro_template_id"]], "value": template_id},
                        {"id": field_ids[required_fields["intro_profile_key"]], "value": profile_key},
                    ]
                },
            )
            client.post(f"/contacts/{cid}/tags", {"tags": [sent_tag, done_tag]})
            client.delete(f"/contacts/{cid}/tags", {"tags": [pending_tag]})
            summary["sent"] += 1
            print(f"SENT  {cid} {email}")
        except Exception as e:
            msg = str(e).lower()
            # Do not keep retrying permanently blocked recipients.
            if "has unsubscribed" in msg or "is invalid" in msg:
                try:
                    client.post(f"/contacts/{cid}/tags", {"tags": [done_tag]})
                    client.delete(f"/contacts/{cid}/tags", {"tags": [pending_tag]})
                except Exception:
                    pass
                summary["terminal_skips"] += 1
                print(f"SKIP  {cid} {email} reason=terminal_email_block")
            else:
                summary["errors"] += 1
                print(f"ERR   {cid} {email} {e}")

    print("\nSummary")
    print(json.dumps(summary, indent=2))
    print(f"mode={'LIVE' if args.live else 'DRY_RUN'}")


if __name__ == "__main__":
    main()
