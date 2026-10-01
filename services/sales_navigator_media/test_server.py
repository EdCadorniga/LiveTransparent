from __future__ import annotations

import base64
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from server import Handler, MAX_FILE_BYTES, Store


class MediaServiceTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        Handler.config = {"MEDIA_SERVICE_KEY": "test-secret",
                          "PUBLIC_BASE_URL": "https://reports.livetransparent.com/sales-navigator-attachments",
                          "MEDIA_DATA_DIR": Path(self.temp.name)}
        Handler.store = Store(Path(self.temp.name))
        self.http = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.http.server_address[1]}"
        self.payload = {"filename": "note.pdf", "content_type": "application/pdf",
                        "data": base64.b64encode(b"test").decode()}

    def tearDown(self):
        self.http.shutdown()
        self.http.server_close()
        self.thread.join(timeout=2)
        self.temp.cleanup()

    def post(self, payload=None, key="test-secret"):
        request = urllib.request.Request(
            self.base + "/sales-navigator-attachments/v1/store",
            data=json.dumps(payload or self.payload).encode(), method="POST",
            headers={"Content-Type": "application/json", "X-Bridge-Media-Key": key},
        )
        try:
            with urllib.request.urlopen(request, timeout=3) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as error:
            return error.code, json.load(error)

    def test_authorization_store_and_download(self):
        self.assertEqual(self.post(key="wrong")[0], 401)
        status, first = self.post()
        self.assertEqual(status, 200)
        self.assertRegex(first["url"], r"^https://reports\.livetransparent\.com/sales-navigator-attachments/[a-f0-9]{64}$")
        token = first["url"].rsplit("/", 1)[-1]
        with urllib.request.urlopen(self.base + "/sales-navigator-attachments/" + token, timeout=3) as response:
            self.assertEqual(response.read(), b"test")
            self.assertEqual(response.headers["Content-Type"], "application/pdf")

    def test_size_limit(self):
        big = base64.b64encode(b"a" * (MAX_FILE_BYTES + 1)).decode()
        status, result = self.post({**self.payload, "data": big})
        self.assertEqual(status, 422)
        self.assertEqual(result["error"], "attachment_empty_or_too_large")

    def test_unsupported_extension_rejected(self):
        status, result = self.post({**self.payload, "filename": "payload.exe"})
        self.assertEqual(status, 422)
        self.assertEqual(result["error"], "attachment_type_not_supported_by_sales_navigator")

    def test_healthz(self):
        with urllib.request.urlopen(self.base + "/healthz", timeout=3) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.load(response), {"ok": True})


if __name__ == "__main__":
    unittest.main()
