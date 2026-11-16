import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import factory_ledger


class Ledger(unittest.TestCase):
    def setUp(self):
        self.root = self._tmp()
        os.environ["FACTORY_ROOT"] = self.root
        os.environ["FACTORY_LEDGER_DIR"] = os.path.join(self.root, "ledger")
        os.environ["FACTORY_TZ"] = "UTC"
        factory_ledger.append({"event": "merged", "repo": "example-org/app", "pr": 101,
                               "title": "Fix typo", "head_sha": "abc12345deadbeef",
                               "merge_sha": "def12345deadbeef", "merged_by": "auto",
                               "blast_tier": "LOW", "portback": "pending"}, render_md=True)

    def _tmp(self):
        import tempfile
        return tempfile.mkdtemp(prefix="factory-ledger-")

    def test_append_is_append_only(self):
        factory_ledger.append({"event": "portback_update", "repo": "example-org/app",
                               "pr": 101, "portback": "LIVE"}, render_md=True)
        rows = factory_ledger.rows()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["portback"], "pending")
        self.assertEqual(rows[1]["portback"], "LIVE")

    def test_render_markdown(self):
        md = os.path.join(os.environ["FACTORY_LEDGER_DIR"], "MERGES.md")
        text = open(md, encoding="utf-8").read()
        self.assertIn("app#101", text)

    def test_pr_url_filled(self):
        self.assertEqual(factory_ledger.rows()[0]["pr_url"], "https://github.com/example-org/app/pull/101")


if __name__ == "__main__":
    unittest.main()
