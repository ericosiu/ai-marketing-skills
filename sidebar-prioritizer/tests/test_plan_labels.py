import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("planner", Path(__file__).parents[1] / "scripts/plan_labels.py")
planner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(planner)
NOW = planner.timestamp("2026-09-08T12:00:00Z")


class LabelTests(unittest.TestCase):
    def record(self, **changes):
        value = dict(id="task-a", host="local", old_title="P2 - Revenue - Renewals",
                     priority=2, category="Revenue", label="Renewals",
                     last_activity="2026-09-01T11:59:59Z")
        value.update(changes)
        return value

    def run_plan(self, **changes):
        return planner.plan_labels([self.record(**changes)], NOW)[0]

    def test_strict_seven_day_boundary(self):
        self.assertEqual(self.run_plan()["new_title"], "P2B7 - Revenue - Renewals")
        self.assertFalse(self.run_plan(last_activity="2026-09-01T12:00:00Z")["changed"])

    def test_timezone_equivalence(self):
        self.assertFalse(self.run_plan(last_activity="2026-09-01T05:00:00-07:00")["changed"])

    def test_recent_work_removes_marker(self):
        self.assertEqual(self.run_plan(old_title="P2B7 - Revenue - Renewals",
                         last_activity="2026-09-08T11:00:00Z")["new_title"],
                         "P2 - Revenue - Renewals")

    def test_missing_or_future_activity_preserves_marker_and_flags(self):
        for date, flag in [(None, "unknown_activity"), ("2026-09-09T00:00:00Z", "future_activity")]:
            result = self.run_plan(old_title="P2B7 - Revenue - Renewals", last_activity=date)
            self.assertFalse(result["changed"])
            self.assertIn(flag, result["review_flags"])

    def test_metadata_time_does_not_hide_old_work(self):
        self.assertIn("P2B7", self.run_plan(updated_at="2026-09-08T12:00:00Z")["new_title"])

    def test_idempotent_and_no_duplicate_prefix(self):
        first = self.run_plan()
        second = self.run_plan(old_title=first["new_title"], label=first["new_title"])
        self.assertFalse(second["changed"])

    def test_overlong_title_is_rejected_not_truncated(self):
        with self.assertRaises(ValueError):
            self.run_plan(label="A" * 60 + " Sep 08 09:30")

    def test_unranked_is_not_assigned_an_invented_priority(self):
        result = self.run_plan(priority=None)
        self.assertEqual(result["new_title"], "Revenue - Renewals")
        self.assertIn("unranked", result["review_flags"])

    def test_bad_priority_and_duplicate_id_are_rejected(self):
        for priority in [True, 5, "2"]:
            with self.assertRaises(ValueError):
                self.run_plan(priority=priority)
        with self.assertRaises(ValueError):
            planner.plan_labels([self.record(), self.record()], NOW)

    def test_naive_date_is_rejected(self):
        with self.assertRaises(ValueError):
            self.run_plan(last_activity="2026-09-01T12:00:00")


if __name__ == "__main__":
    unittest.main()
