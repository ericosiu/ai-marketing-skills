import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import record_attempt


class Infer(unittest.TestCase):
    def test_cursor_branch(self):
        impl, ev = record_attempt.infer_implementer({"head_ref": "cursor/fix-typo"})
        self.assertEqual(impl, "cursor-cloud")
        self.assertTrue(ev)

    def test_codex_author(self):
        impl, ev = record_attempt.infer_implementer({"head_ref": "feat/x", "commit_authors": ["codex"]})
        self.assertEqual(impl, "codex-cli")

    def test_claude_branch(self):
        impl, ev = record_attempt.infer_implementer({"head_ref": "claude/review-fix"})
        self.assertEqual(impl, "claude-cli")

    def test_unknown_without_evidence(self):
        impl, ev = record_attempt.infer_implementer({"head_ref": "feat/x", "author_login": "alice"})
        self.assertEqual(impl, "unknown")
        self.assertEqual(ev, [])

    def test_explicit_human(self):
        impl, ev = record_attempt.infer_implementer({"body": "implementer: human"})
        self.assertEqual(impl, "human")


class Ledger(unittest.TestCase):
    def setUp(self):
        root = tempfile.mkdtemp(prefix="factory-attempts-")
        os.environ["FACTORY_ROOT"] = root
        os.environ["FACTORY_LEDGER_DIR"] = os.path.join(root, "ledger")
        os.environ["FACTORY_TZ"] = "UTC"

    def test_rejects_unknown_implementer_label(self):
        rec = record_attempt.append({"repo": "example-org/app", "pr": 7, "implementer": "mystery"})
        self.assertEqual(rec["implementer"], "unknown")
        self.assertIn("rejected", rec["note"])

    def test_builder_stats(self):
        record_attempt.append({
            "repo": "example-org/app", "pr": 7, "implementer": "cursor-cloud",
            "acceptance_test_pass_first_try": True, "attempt_no": 1,
            "review_l1": 0, "review_l2": 1, "minutes_merge_to_live": 40,
        })
        stats = record_attempt.builder_stats(record_attempt.rows())
        by = {s["implementer"]: s for s in stats}
        self.assertEqual(by["cursor-cloud"]["prs"], 1)
        self.assertEqual(by["cursor-cloud"]["first_try_pass_pct"], 100)
        self.assertEqual(by["cursor-cloud"]["reviewer_catches"], 1)


if __name__ == "__main__":
    unittest.main()
