import datetime as dt
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import postrelease_watch


class Watch(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="factory-watch-"))
        self.live = self.root / "app.py"
        self.bak = self.root / "app.py.bak-20261116-pr-8"
        self.live.write_text("new\n")
        self.bak.write_text("old\n")
        self.metric = self.root / "metric.json"
        self.metric.write_text(json.dumps({"errors": 0}))
        self.log = self.root / "app.log"
        self.log.write_text("ok\n")
        applied = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)).isoformat()
        self.config = {
            "fix_id": "demo",
            "pr": 8,
            "applied_at": applied,
            "watch_hours": 24,
            "live_files": [{"live_path": str(self.live), "bak_path": str(self.bak)}],
            "metric": {
                "source": str(self.metric),
                "read_spec": {"type": "json", "key_path": ["errors"]},
                "baseline": 0,
                "threshold": 0,
                "direction": "above",
            },
            "errors": {"log_paths": [str(self.log)], "patterns": ["Traceback"], "max_errors": 0},
        }

    def test_ok(self):
        d = postrelease_watch.run_watch(self.config, execute=False)
        self.assertEqual(d["decision"], "OK")

    def test_metric_breach_restores(self):
        self.metric.write_text(json.dumps({"errors": 5}))
        d = postrelease_watch.run_watch(self.config, execute=True)
        self.assertEqual(d["decision"], "BREACH")
        self.assertEqual(self.live.read_text(), "old\n")

    def test_window_closed(self):
        self.config["applied_at"] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=30)).isoformat()
        d = postrelease_watch.run_watch(self.config, execute=True)
        self.assertEqual(d["decision"], "WINDOW_CLOSED")
        self.assertEqual(self.live.read_text(), "new\n")


if __name__ == "__main__":
    unittest.main()
