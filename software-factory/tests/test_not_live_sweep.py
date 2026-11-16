import datetime as dt
import os
import sys
import tempfile
import unittest
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import factory_ledger
import not_live_sweep


TZ = ZoneInfo("UTC")


class Sweep(unittest.TestCase):
    def setUp(self):
        root = tempfile.mkdtemp(prefix="factory-nls-")
        os.environ["FACTORY_ROOT"] = root
        os.environ["FACTORY_LEDGER_DIR"] = os.path.join(root, "ledger")
        os.environ["FACTORY_TZ"] = "UTC"
        os.environ["FACTORY_CONFIG"] = os.path.join(root, "config.json")
        open(os.environ["FACTORY_CONFIG"], "w").write('{"not_live":{"warn_hours":4,"stuck_hours":24}}')
        self.now = dt.datetime(2026, 11, 16, 18, 0, tzinfo=TZ)

    def _row(self, pr, hours_ago, portback="pending", event="merged"):
        t = (self.now - dt.timedelta(hours=hours_ago)).isoformat()
        factory_ledger.append({
            "time": t, "event": event, "repo": "example-org/app", "pr": pr,
            "portback": portback, "merge_sha": "abc",
        }, render_md=False)

    def test_pending_under_four_hours(self):
        self._row(1, 2)
        items = {i["pr"]: i for i in not_live_sweep.report(now=self.now)}
        self.assertEqual(items[1]["status"], "pending")

    def test_drive_after_four_hours(self):
        self._row(2, 5)
        items = {i["pr"]: i for i in not_live_sweep.report(now=self.now)}
        self.assertEqual(items[2]["status"], "drive")

    def test_red_after_twenty_four_hours(self):
        self._row(3, 25)
        items = {i["pr"]: i for i in not_live_sweep.report(now=self.now)}
        self.assertEqual(items[3]["status"], "red")

    def test_live_is_ok(self):
        self._row(4, 30, portback="LIVE")
        items = {i["pr"]: i for i in not_live_sweep.report(now=self.now)}
        self.assertEqual(items[4]["status"], "ok")

    def test_claim_blocks_second_worker(self):
        not_live_sweep.claim("example-org/app", 5, files=["bin/a.py"], worker="one")
        with self.assertRaises(SystemExit):
            not_live_sweep.claim("example-org/app", 5, worker="two")


if __name__ == "__main__":
    unittest.main()
