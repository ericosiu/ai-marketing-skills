import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("validator", Path(__file__).parents[1] / "scripts/validate_library.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.data = {
            "posts": [{"id": "p1", "url": "https://example.com/reel/one", "published_at": None,
                       "checked_at": "2026-01-02T10:00:00Z", "metrics": {"views": None}}],
            "formats": [{"id": f"f{i}", "post_ids": ["p1"], "prompts": ["Context?", "Action?", "Lesson?"]} for i in (1, 2)],
            "ideas": [{"id": "i1", "source_url": None, "format_ids": ["f1", "f2"],
                       "talking_prompts": ["Show the problem", "Explain the choice", "Show the result"],
                       "claim_limit": "A proposed test; no measured lift."}],
        }

    def test_unknown_metrics_and_shared_reel_are_valid(self):
        before = copy.deepcopy(self.data)
        self.assertEqual(module.validate(self.data), [])
        self.assertEqual(self.data, before)

    def test_archiving_must_not_leave_dangling_draft_references(self):
        self.data["formats"].pop()
        self.assertTrue(any("unresolved" in e for e in module.validate(self.data)))

    def test_bad_metrics_dates_and_incomplete_prompt_are_rejected(self):
        self.data["posts"][0].update(metrics={"views": -1}, checked_at="2026-01-02")
        self.data["ideas"][0]["talking_prompts"] = ["One"]
        self.assertEqual(len(module.validate(self.data)), 3)

    def test_duplicate_ids_and_credential_urls_rejected(self):
        self.data["posts"].append(copy.deepcopy(self.data["posts"][0]))
        self.data["posts"][0]["url"] = "file:///private/example"
        self.assertEqual(len(module.validate(self.data)), 2)

    def test_malformed_input_reports_errors(self):
        self.assertTrue(module.validate([]))
        self.assertTrue(module.validate({"posts": [None], "formats": [], "ideas": []}))


if __name__ == "__main__":
    unittest.main()
