from __future__ import annotations

import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from server import ACCOUNT, Handler, MAX_FILE_BYTES, Store


class MediaServiceTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        Handler.config = {"MEDIA_SERVICE_KEY": "test-secret", "UNIPILE_API_KEY": "private-test-key",
                          "PUBLIC_BASE_URL": "https://reports.livetransparent.com/sales-navigator-attachments",
                          "MEDIA_DATA_DIR": Path(self.temp.name)}
        Handler.store = Store(Path(self.temp.name))
        self.http = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.http.server_address[1]}"
        self.payload = {"account_id": ACCOUNT, "chat_id": "SALES_NAVIGATOR_2-abc==",
                        "message_id": "message-1", "attachment_id": "attachment-1",
                        "filename": "note.pdf", "file_size": 4}

    def tearDown(self):
        self.http.shutdown()
        self.http.server_close()
        self.thread.join(timeout=2)
        self.temp.cleanup()

    def post(self, payload=None, key="test-secret"):
        request = urllib.request.Request(
            self.base + "/sales-navigator-attachments/v1/ingest-unipile",
            data=json.dumps(payload or self.payload).encode(), method="POST",
            headers={"Content-Type": "application/json", "X-Bridge-Media-Key": key},
        )
        try:
            with urllib.request.urlopen(request, timeout=3) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as error:
            return error.code, json.load(error)

    def test_authorization_account_scope_and_idempotency(self):
        with patch("server.get_attachment", return_value=b"test") as fetch:
            self.assertEqual(self.post(key="wrong")[0], 401)
            self.assertEqual(self.post({**self.payload, "account_id": "acc_other"})[0], 422)
            status, first = self.post()
            self.assertEqual(status, 200)
            self.assertEqual(self.post()[1], first)
            self.assertEqual(fetch.call_count, 1)
        token = first["url"].rsplit("/", 1)[-1]
        with urllib.request.urlopen(self.base + "/sales-navigator-attachments/" + token, timeout=3) as response:
            self.assertEqual(response.read(), b"test")
            self.assertEqual(response.headers["Content-Type"], "application/octet-stream")

    def test_size_limit_before_provider_fetch(self):
        with patch("server.get_attachment") as fetch:
            status, result = self.post({**self.payload, "file_size": MAX_FILE_BYTES + 1})
            self.assertEqual(status, 422)
            self.assertEqual(result["error"], "attachment_too_large")
            fetch.assert_not_called()

    def test_ghl_url_rejects_private_and_unknown_hosts(self):
        endpoint = self.base + "/sales-navigator-attachments/v1/prepare-ghl"
        for url in ("http://127.0.0.1/file.pdf", "https://localhost/file.pdf",
                    "https://evil.example/file.pdf"):
            request = urllib.request.Request(endpoint, data=json.dumps({"url": url}).encode(),
                                             method="POST", headers={"X-Bridge-Media-Key": "test-secret"})
            with self.assertRaises(urllib.error.HTTPError) as result:
                urllib.request.urlopen(request, timeout=3)
            self.assertEqual(result.exception.code, 422)


if __name__ == "__main__":
    unittest.main()
