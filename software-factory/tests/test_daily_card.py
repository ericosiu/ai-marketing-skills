import datetime as dt
import json
import os
import sys
import tempfile
import unittest
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import daily_card
import factory_ledger


class Card(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="factory-card-")
        os.environ["FACTORY_ROOT"] = self.root
        os.environ["FACTORY_LEDGER_DIR"] = os.path.join(self.root, "ledger")
        os.environ["FACTORY_DIGEST"] = os.path.join(self.root, "digest")
        os.environ["FACTORY_TZ"] = "UTC"
        os.environ["FACTORY_CONFIG"] = os.path.join(self.root, "config.json")
        os.makedirs(os.environ["FACTORY_DIGEST"], exist_ok=True)
        open(os.environ["FACTORY_CONFIG"], "w").write(json.dumps({
            "timezone": "UTC",
            "automerge": {"enabled": True, "state": "ARMED", "max_per_day": 2, "repos": ["example-org/app"]},
        }))
        now = dt.datetime(2026, 11, 16, 18, 0, tzinfo=ZoneInfo("UTC"))
        factory_ledger.append({
            "time": now.isoformat(), "event": "merged", "repo": "example-org/app",
            "pr": 9, "title": "Docs typo", "merged_by": "auto", "blast_tier": "LOW",
            "portback": "pending",
        }, render_md=False)
        open(os.path.join(os.environ["FACTORY_DIGEST"], "held-2026-11-16.json"), "w").write(json.dumps([{
            "repo": "example-org/app", "pr": 10, "url": "https://github.com/example-org/app/pull/10",
            "title": "More docs", "head": "abcd1234", "priority": "P1",
            "held_because": "daily cap reached", "created_at": "2026-11-16T10:00:00+00:00",
        }]))
        self.text = daily_card.build(dt.date(2026, 11, 16), now)

    def test_sections_present(self):
        self.assertIn("## A. Merges and reverts", self.text)
        self.assertIn("## B. Low-blast PRs over the cap", self.text)
        self.assertIn("## C. Merged but not live", self.text)
        self.assertIn("## D. Builders", self.text)
        self.assertIn("app#9", self.text)
        self.assertIn("(REC) merge", self.text)
        self.assertIn("yes merge app#10", self.text)


if __name__ == "__main__":
    unittest.main()
