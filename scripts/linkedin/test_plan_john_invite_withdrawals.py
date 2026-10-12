"""Isolated cleanup safety tests: no remote access or database/provider writes."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import plan_john_invite_withdrawals as tool


class CleanupTests(unittest.TestCase):
    def invitation(self, iid="123", note="Hey Alex - John here with Transparent eCom."):
        return {"id": iid, "invitation_text": note, "invited_user_public_id": "alex", "invited_user_id": "provider-1"}

    def test_issue_scope_and_mapping(self):
        self.assertEqual(tool.issue_of(self.invitation()), "john_note")
        self.assertEqual(tool.issue_of(self.invitation(note='Hi {first_name}, I\'m "ameron co-fo\'nder of Transparent e"om.')), "mojibake")
        self.assertEqual(tool.issue_of(self.invitation(note="Hi John, would love to connect.")), "")
        self.assertEqual(len(tool.NOTES), 8)
        self.assertTrue(all(note.isascii() for note in tool.NOTES.values()))

    def test_sql_text_cannot_inject(self):
        value = "O'Brien \\ x'); DROP TABLE x; -- Ramírez"
        expression = tool.sql_text(value)
        self.assertNotIn("DROP TABLE", expression)
        self.assertEqual(bytes.fromhex(expression.split("'")[1]).decode(), value)

    @patch.object(tool, "unipile")
    def test_incomplete_pagination_rejected(self, api):
        api.return_value = (200, {"items": [self.invitation()], "cursor": "same"})
        with patch.object(tool.time, "sleep"), self.assertRaises(tool.Stop):
            tool.pending_invites()

    @patch.object(tool, "unipile")
    def test_malformed_list_rejected(self, api):
        api.return_value = (200, {"items": None})
        with self.assertRaises(tool.Stop):
            tool.pending_invites()

    @patch.object(tool, "request_once")
    def test_delete_not_retried_on_restriction(self, req):
        req.return_value = (429, {"type": "errors/too_many_requests"})
        self.assertEqual(tool.request("DELETE", "unused", {}), req.return_value)
        self.assertEqual(req.call_count, 1)

    @patch.object(tool, "request_once")
    def test_read_retries_bounded(self, req):
        req.return_value = (429, {})
        with patch.object(tool.time, "sleep"):
            self.assertEqual(tool.request("GET", "unused", {}), (429, {}))
        self.assertEqual(req.call_count, 4)

    def test_unmatched_preserved_for_review(self):
        db = Mock()
        db.rows.side_effect = [[], []]
        inv = self.invitation()
        rows = tool.collect(db, [inv], False)
        self.assertEqual(rows[0]["raw_invitation"], inv)
        self.assertEqual(rows[0]["reinvite_status"], "needs_review")
        self.assertEqual(rows[0]["reinvite_message"], tool.NOTES["Cannabis"])

    def test_ambiguous_contacts_preserved_without_choosing(self):
        db = Mock()
        db.rows.side_effect = [[{"ghl_contact_id": cid, "normalized_profile_slug": "alex", "linkedin_provider_ids": []} for cid in ("a", "b")], []]
        def get(method, url, headers):
            cid = url.rsplit("/", 1)[1]
            return 200, {"contact": {"id": cid, "locationId": tool.LOCATION, "firstName": "Alex"}}
        with patch.object(tool, "request", side_effect=get), patch.dict(tool.os.environ, {"GHL_PIT": "dummy"}), patch.object(tool.time, "sleep"):
            row = tool.collect(db, [self.invitation()], False)[0]
        self.assertEqual(row["ghl_contact_id"], "")
        self.assertEqual(set(row["raw_ghl_contact"]), {"a", "b"})
        self.assertEqual(row["reinvite_status"], "needs_review")

    def run_withdraw(self, *, yes=True, outcome=(200, {"object": "InvitationCanceled"}), tampered=False, missing_hold=False):
        with tempfile.TemporaryDirectory(prefix="lt-withdraw-test-", dir=r"C:\Users\edmon\AppData\Local\Temp\opencode") as directory:
            path = Path(directory) / "capture.json"
            inv = self.invitation()
            doc = {"schema_version": 1, "account_id": tool.ACCOUNT, "rows": [{"invitation_id": "123"}]}
            path.write_text(json.dumps(doc), encoding="utf-8")
            row = {"invitation_id": "123", "withdraw_status": "pending", "dispatcher_hold": True,
                   "snapshot_sha256": "wrong" if tampered else hashlib.sha256(path.read_bytes()).hexdigest(),
                   "snapshot_path": str(path.resolve()), "issue": "john_note", "cooldown_days": 30,
                   "raw_invitation": inv, "ghl_contact_id": "cid"}
            db = Mock()
            db.rows.side_effect = [[row], [] if missing_hold else [{"table_name": name} for name in ("linkedin_connection_state", "partnership_linkedin_connection_state")], [], [{"invitation_id": "123"}]]
            db.execute.return_value = '[{"invitation_id":"123"}]'
            args = SimpleNamespace(snapshot=str(path), yes=yes, limit=10, delay=2)
            with patch.object(tool, "paused_dispatchers"), patch.object(tool, "pending_invites", side_effect=[[inv], []]), patch.object(tool, "unipile") as api, patch.object(tool, "finalize") as finalize, patch.object(tool.time, "sleep"), patch("builtins.print"):
                if isinstance(outcome, Exception):
                    api.side_effect = outcome
                else:
                    api.return_value = outcome
                try:
                    tool.withdraw(db, args)
                    stopped = False
                except tool.Stop:
                    stopped = True
                return api.call_count, finalize.call_args, stopped, db.execute.call_count

    def test_dry_run_has_no_write(self):
        calls, final, stopped, db_writes = self.run_withdraw(yes=False)
        self.assertEqual((calls, final, stopped, db_writes), (0, None, False, 0))

    def test_tampered_snapshot_blocks_delete(self):
        self.assertEqual(self.run_withdraw(tampered=True)[0], 0)
        self.assertTrue(self.run_withdraw(tampered=True)[2])

    def test_missing_hold_blocks_delete(self):
        calls, _, stopped, _ = self.run_withdraw(missing_hold=True)
        self.assertEqual(calls, 0)
        self.assertTrue(stopped)

    def test_success_finalizes_cooldown(self):
        calls, final, stopped, _ = self.run_withdraw()
        self.assertEqual(calls, 1)
        self.assertEqual(final.args[2:5], ("withdrawn", 200, 30))
        self.assertFalse(stopped)

    def test_provider_restriction_halts_without_retry(self):
        calls, final, stopped, _ = self.run_withdraw(outcome=(429, {"type": "errors/too_many_requests"}))
        self.assertEqual(calls, 1)
        self.assertEqual(final.args[2], "uncertain")
        self.assertTrue(stopped)

    def test_network_uncertainty_halts_without_retry(self):
        calls, final, stopped, _ = self.run_withdraw(outcome=tool.Stop("uncertain"))
        self.assertEqual(calls, 1)
        self.assertEqual(final.args[2:4], ("uncertain", 0))
        self.assertTrue(stopped)

    def test_state_sql_preserves_terminal_and_both_queues(self):
        db = Mock()
        tool.finalize(db, {"invitation_id": "123", "raw_invitation": self.invitation(), "ghl_contact_id": "cid"}, "withdrawn", 200, 30)
        sql = db.execute.call_args.args[0]
        self.assertIn("request_sent_at=now()", sql)
        self.assertIn("UPDATE partnership_linkedin_connection_state", sql)
        self.assertEqual(sql.count("AND connected_at IS NULL AND connection_status NOT IN ('connected','completed')"), 2)
        self.assertIn("dispatcher_hold", tool.DDL)

    def test_capture_preserves_originals_and_readback(self):
        with tempfile.TemporaryDirectory(prefix="lt-capture-test-", dir=r"C:\Users\edmon\AppData\Local\Temp\opencode") as directory:
            path = Path(directory) / "capture.json"
            path.write_text("{}", encoding="utf-8")
            row = {"invitation_id": "123", "issue": "john_note", "ghl_contact_id": "cid", "first_name": "Alex",
                   "vertical": "Cannabis", "reinvite_status": "pending", "reinvite_message": tool.NOTES["Cannabis"],
                   "raw_invitation": self.invitation(), "raw_ghl_contact": {"contact": {"id": "cid"}},
                   "raw_connection_states": [], "candidate_contact_ids": ["cid"]}
            db = Mock()
            db.rows.return_value = [{"invitation_id": "123", "raw_invitation": row["raw_invitation"]}]
            with patch.object(tool, "paused_dispatchers"):
                tool.capture(db, [row], path, SimpleNamespace(cooldown_days=30, reinvite_owner="ledger-script"))
            sql = db.execute.call_args.args[0]
            self.assertIn("ON CONFLICT (unipile_account_id,invitation_id) DO NOTHING", sql)
            self.assertIn("::integer", sql)
            self.assertIn("candidate_contact_ids", sql)
            self.assertIn("CREATE TRIGGER", sql)
            self.assertTrue(path.with_suffix(".ledger.json").exists())

    def test_capture_conflict_does_not_silently_replace(self):
        with tempfile.TemporaryDirectory(prefix="lt-capture-test-", dir=r"C:\Users\edmon\AppData\Local\Temp\opencode") as directory:
            path = Path(directory) / "capture.json"
            path.write_text("{}", encoding="utf-8")
            db = Mock()
            db.rows.return_value = []
            row = {"invitation_id": "123", "issue": "john_note", "ghl_contact_id": "", "first_name": "", "vertical": "",
                   "reinvite_status": "needs_review", "reinvite_message": tool.NOTES["Cannabis"], "raw_invitation": self.invitation(),
                   "raw_ghl_contact": {}, "raw_connection_states": [], "candidate_contact_ids": []}
            with patch.object(tool, "paused_dispatchers"), self.assertRaises(tool.Stop):
                tool.capture(db, [row], path, SimpleNamespace(cooldown_days=30, reinvite_owner="ledger-script"))


if __name__ == "__main__":
    unittest.main()
