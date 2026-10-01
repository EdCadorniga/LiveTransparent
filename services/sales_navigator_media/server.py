"""Attachment hosting proxy for the Sales Navigator bridge (inbound direction).

GHL can only attach a file to an inbound conversation message by fetching a
public URL. This service accepts authenticated bytes from the n8n bridge (which
already holds the Unipile credential and does the provider fetch) and stores
them under an unguessable bearer token, so GHL can retrieve the file. It never
fetches remote URLs itself, so there is no server-side request forgery surface.

Scope is deliberately tiny: exactly one inbound attachment per message, capped
at 4 MB, images and documents only (the Sales Navigator limits). Outbound
GHL-to-Unipile attachments are handled entirely inside n8n.
"""
from __future__ import annotations

import base64
import binascii
import hmac
import json
import os
import re
import secrets
import sqlite3
import tempfile
import urllib.parse
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

MAX_FILE_BYTES = 4 * 1024 * 1024
MAX_JSON_BYTES = 6 * 1024 * 1024
TOKEN_PATTERN = re.compile(r"^[a-f0-9]{64}$")
ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".heic", ".webp", ".bmp",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".txt", ".csv", ".rtf",
}
PREFIX = "/sales-navigator-attachments"


def settings() -> dict:
    needed = ("MEDIA_SERVICE_KEY", "PUBLIC_BASE_URL", "MEDIA_DATA_DIR")
    values = {key: os.environ.get(key, "").strip() for key in needed}
    if any(not value for value in values.values()):
        raise RuntimeError("Media service configuration is incomplete")
    if not values["PUBLIC_BASE_URL"].startswith("https://"):
        raise RuntimeError("PUBLIC_BASE_URL must use HTTPS")
    values["MEDIA_DATA_DIR"] = Path(values["MEDIA_DATA_DIR"])
    return values


def clean_filename(value: object) -> str:
    name = str(value or "attachment").replace("\\", "/").rsplit("/", 1)[-1]
    name = "".join(ch for ch in name if ch.isprintable() and ch not in '";\r\n')[:180].strip()
    return name or "attachment"


def is_allowed_name(name: str) -> bool:
    return Path(clean_filename(name)).suffix.lower() in ALLOWED_EXTENSIONS


class Store:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.files_dir = data_dir / "files"
        self.files_dir.mkdir(parents=True, exist_ok=True)
        self.database = data_dir / "media.sqlite3"
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS attachments (
                token TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                content_type TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )""")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.database, timeout=15)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def get_token(self, token: str):
        with self.connect() as db:
            return db.execute(
                "SELECT token,filename,content_type,file_size FROM attachments WHERE token=? AND active=1",
                (token,)).fetchone()

    def save(self, filename: str, content_type: str, content: bytes) -> str:
        token = secrets.token_hex(32)
        fd, temporary = tempfile.mkstemp(prefix="store-", dir=self.files_dir)
        try:
            with os.fdopen(fd, "wb") as file:
                file.write(content)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, self.files_dir / token)
            with self.connect() as db:
                db.execute("""INSERT INTO attachments
                  (token,filename,content_type,file_size) VALUES(?,?,?,?)""",
                           (token, filename, content_type, len(content)))
            return token
        finally:
            Path(temporary).unlink(missing_ok=True)


class Handler(BaseHTTPRequestHandler):
    config: dict
    store: Store

    def log_message(self, format: str, *args):  # noqa: A002
        # URL paths contain bearer tokens. Never log request paths or headers.
        pass

    def send_json(self, status: int, payload: dict) -> None:
        data = json.dumps(payload, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def authorized(self) -> bool:
        supplied = self.headers.get("X-Bridge-Media-Key", "")
        return bool(supplied) and hmac.compare_digest(supplied, self.config["MEDIA_SERVICE_KEY"])

    def do_POST(self) -> None:
        if self.path != PREFIX + "/v1/store":
            self.send_json(404, {"error": "not_found"})
            return
        if not self.authorized():
            self.send_json(401, {"error": "unauthorized"})
            return
        length = self.headers.get("Content-Length", "")
        if not length.isdigit() or int(length) > MAX_JSON_BYTES:
            self.send_json(413, {"error": "invalid_request_size"})
            return
        try:
            body = json.loads(self.rfile.read(int(length)))
            filename = clean_filename(body.get("filename"))
            if not is_allowed_name(filename):
                raise ValueError("attachment_type_not_supported_by_sales_navigator")
            encoded = body.get("data")
            if not isinstance(encoded, str) or not encoded:
                raise ValueError("attachment_data_missing")
            try:
                content = base64.b64decode(encoded, validate=True)
            except (binascii.Error, ValueError):
                raise ValueError("attachment_data_invalid") from None
            if not content or len(content) > MAX_FILE_BYTES:
                raise ValueError("attachment_empty_or_too_large")
            content_type = str(body.get("content_type") or "application/octet-stream")[:120]
            token = self.store.save(filename, content_type, content)
            self.send_json(200, {"url": self.config["PUBLIC_BASE_URL"].rstrip("/") + "/" + token})
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self.send_json(422, {"error": str(exc)[:80]})
        except Exception:
            self.send_json(500, {"error": "attachment_store_failed"})

    def do_GET(self) -> None:
        if self.path in ("/healthz", PREFIX + "/v1/healthz"):
            self.send_json(200, {"ok": True})
            return
        token = self.path[len(PREFIX) + 1:] if self.path.startswith(PREFIX + "/") else ""
        if not TOKEN_PATTERN.fullmatch(token):
            self.send_json(404, {"error": "not_found"})
            return
        row = self.store.get_token(token)
        path = self.store.files_dir / token
        if not row or not path.is_file():
            self.send_json(404, {"error": "not_found"})
            return
        filename = urllib.parse.quote(row["filename"], safe="")
        self.send_response(200)
        self.send_header("Content-Type", row["content_type"] or "application/octet-stream")
        self.send_header("Content-Disposition", f"attachment; filename*=UTF-8''{filename}")
        self.send_header("Content-Length", str(row["file_size"]))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'none'")
        self.end_headers()
        with path.open("rb") as file:
            while chunk := file.read(1024 * 1024):
                self.wfile.write(chunk)


def main() -> None:
    config = settings()
    Handler.config = config
    Handler.store = Store(config["MEDIA_DATA_DIR"])
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    main()
