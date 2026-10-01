"""Authenticated Unipile attachment ingestion and revocable bearer-link downloads.

This service stores only attachment bytes and minimal identity metadata. The
public link is an unguessable bearer token; possession of the URL grants read
access until the token is revoked. It never accepts a caller supplied fetch URL.
"""
from __future__ import annotations

import hmac
import base64
import ipaddress
import json
import os
import re
import secrets
import socket
import sqlite3
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ACCOUNT = "acc_01m3sefk22e8jvnmvvfx333pye"
MAX_FILE_BYTES = 50 * 1024 * 1024
MAX_JSON_BYTES = 16 * 1024
MAX_GHL_FILE_BYTES = 5 * 1024 * 1024
ID_PATTERN = re.compile(r"^[A-Za-z0-9_+&=/-]{1,320}$")
TOKEN_PATTERN = re.compile(r"^[a-f0-9]{64}$")
GHL_HOST_SUFFIXES = (".leadconnectorhq.com", ".msgsndr.com", ".gohighlevel.com",
                     ".googleapis.com", ".googleusercontent.com", ".amazonaws.com")
SALES_NAVIGATOR_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".heic",
                              ".pdf", ".doc", ".docx", ".xls", ".xlsx",
                              ".ppt", ".pptx", ".txt", ".csv"}


def settings() -> dict:
    needed = ("MEDIA_SERVICE_KEY", "UNIPILE_API_KEY", "PUBLIC_BASE_URL", "MEDIA_DATA_DIR")
    values = {key: os.environ.get(key, "").strip() for key in needed}
    if any(not value for value in values.values()):
        raise RuntimeError("Media service configuration is incomplete")
    if not values["PUBLIC_BASE_URL"].startswith("https://"):
        raise RuntimeError("PUBLIC_BASE_URL must use HTTPS")
    values["MEDIA_DATA_DIR"] = Path(values["MEDIA_DATA_DIR"])
    return values


class Store:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.files_dir = data_dir / "files"
        self.files_dir.mkdir(parents=True, exist_ok=True)
        self.database = data_dir / "media.sqlite3"
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS attachments (
                token TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                chat_id TEXT NOT NULL,
                message_id TEXT NOT NULL,
                attachment_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(account_id,chat_id,message_id,attachment_id)
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

    def get_identity(self, account: str, chat: str, message: str, attachment: str):
        with self.connect() as db:
            return db.execute("""SELECT token,filename,file_size,active FROM attachments
                WHERE account_id=? AND chat_id=? AND message_id=? AND attachment_id=?""",
                              (account, chat, message, attachment)).fetchone()

    def get_token(self, token: str):
        with self.connect() as db:
            return db.execute("SELECT token,filename,file_size FROM attachments WHERE token=? AND active=1",
                              (token,)).fetchone()

    def save(self, account: str, chat: str, message: str, attachment: str,
             filename: str, content: bytes):
        prior = self.get_identity(account, chat, message, attachment)
        if prior:
            if not prior["active"]:
                raise ValueError("attachment_revoked")
            return prior["token"]
        token = secrets.token_hex(32)
        fd, temporary = tempfile.mkstemp(prefix="ingest-", dir=self.files_dir)
        try:
            with os.fdopen(fd, "wb") as file:
                file.write(content)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, self.files_dir / token)
            try:
                with self.connect() as db:
                    db.execute("""INSERT INTO attachments
                      (token,account_id,chat_id,message_id,attachment_id,filename,file_size)
                      VALUES(?,?,?,?,?,?,?)""",
                               (token, account, chat, message, attachment, filename, len(content)))
            except sqlite3.IntegrityError:
                (self.files_dir / token).unlink(missing_ok=True)
                prior = self.get_identity(account, chat, message, attachment)
                if not prior or not prior["active"]:
                    raise ValueError("attachment_identity_conflict") from None
                return prior["token"]
            return token
        finally:
            Path(temporary).unlink(missing_ok=True)


def clean_filename(value: object) -> str:
    name = str(value or "attachment").replace("\\", "/").rsplit("/", 1)[-1]
    name = "".join(ch for ch in name if ch.isprintable() and ch not in '";\r\n')[:180].strip()
    return name or "attachment"


def get_attachment(config: dict, account: str, chat: str, message: str,
                   attachment: str) -> bytes:
    encoded = [urllib.parse.quote(part, safe="") for part in (account, chat, message, attachment)]
    url = ("https://api.unipile.com/v2/{}/chats/{}/messages/{}/attachments/{}"
           .format(*encoded))
    request = urllib.request.Request(url, headers={"X-API-KEY": config["UNIPILE_API_KEY"],
                                                "Accept": "application/octet-stream"})
    with urllib.request.urlopen(request, timeout=90) as response:
        if response.status != 200:
            raise ValueError("provider_attachment_unavailable")
        size_header = response.headers.get("Content-Length", "")
        if size_header.isdigit() and int(size_header) > MAX_FILE_BYTES:
            raise ValueError("attachment_too_large")
        content = response.read(MAX_FILE_BYTES + 1)
    if not content or len(content) > MAX_FILE_BYTES:
        raise ValueError("attachment_empty_or_too_large")
    return content


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise ValueError("attachment_redirect_not_allowed")


def prepare_ghl_url(url: str, filename_hint: str) -> tuple[str, str, bytes]:
    parsed = urllib.parse.urlsplit(url)
    hostname = (parsed.hostname or "").lower()
    if (parsed.scheme != "https" or not hostname or parsed.username or parsed.password or
            parsed.port not in (None, 443) or not any(hostname.endswith(suffix)
                                                   for suffix in GHL_HOST_SUFFIXES)):
        raise ValueError("attachment_url_not_allowed")
    addresses = socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
        raise ValueError("attachment_address_not_public")
    filename = clean_filename(filename_hint or urllib.parse.unquote(parsed.path.rsplit("/", 1)[-1]))
    extension = Path(filename).suffix.lower()
    if extension not in SALES_NAVIGATOR_EXTENSIONS:
        raise ValueError("attachment_type_not_supported_by_sales_navigator")
    opener = urllib.request.build_opener(NoRedirect())
    request = urllib.request.Request(url, headers={"Accept": "application/octet-stream"})
    with opener.open(request, timeout=60) as response:
        if response.status != 200:
            raise ValueError("ghl_attachment_unavailable")
        declared = response.headers.get("Content-Length", "")
        if declared.isdigit() and int(declared) > MAX_GHL_FILE_BYTES:
            raise ValueError("attachment_too_large")
        content = response.read(MAX_GHL_FILE_BYTES + 1)
        content_type = response.headers.get("Content-Type", "application/octet-stream").split(";", 1)[0]
    if not content or len(content) > MAX_GHL_FILE_BYTES:
        raise ValueError("attachment_empty_or_too_large")
    return filename, content_type, content


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
        if self.path not in ("/sales-navigator-attachments/v1/ingest-unipile",
                             "/sales-navigator-attachments/v1/prepare-ghl"):
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
            if self.path.endswith("/prepare-ghl"):
                filename, content_type, content = prepare_ghl_url(
                    str(body.get("url", "")), str(body.get("filename", "")))
                self.send_json(200, {"filename": filename, "content_type": content_type,
                                     "content": base64.b64encode(content).decode("ascii"),
                                     "file_size": len(content)})
                return
            account = str(body.get("account_id", ""))
            chat = str(body.get("chat_id", ""))
            message = str(body.get("message_id", ""))
            attachment = str(body.get("attachment_id", ""))
            if account != ACCOUNT or not all(ID_PATTERN.fullmatch(item) for item in
                                             (account, chat, message, attachment)):
                raise ValueError("invalid_provider_identity")
            filename = clean_filename(body.get("filename"))
            declared = body.get("file_size")
            if declared is not None and (not isinstance(declared, int) or declared < 0 or
                                         declared > MAX_FILE_BYTES):
                raise ValueError("attachment_too_large")
            prior = self.store.get_identity(account, chat, message, attachment)
            if prior and prior["active"]:
                token = prior["token"]
            else:
                content = get_attachment(self.config, account, chat, message, attachment)
                token = self.store.save(account, chat, message, attachment, filename, content)
            self.send_json(200, {"url": self.config["PUBLIC_BASE_URL"].rstrip("/") + "/" + token})
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self.send_json(422, {"error": str(exc)[:80]})
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            self.send_json(502, {"error": "provider_attachment_unavailable"})
        except Exception:
            self.send_json(500, {"error": "attachment_ingest_failed"})

    def do_GET(self) -> None:
        if self.path == "/healthz":
            self.send_json(200, {"ok": True})
            return
        prefix = "/sales-navigator-attachments/"
        token = self.path[len(prefix):] if self.path.startswith(prefix) else ""
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
        self.send_header("Content-Type", "application/octet-stream")
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
