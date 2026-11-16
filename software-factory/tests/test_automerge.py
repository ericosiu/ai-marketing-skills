import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import automerge


class EvalChecks(unittest.TestCase):
    def test_missing_required_fails_closed(self):
        out = {g[0]: g[1] for g in automerge.eval_checks(["ci"], [], {}, "abc")}
        self.assertTrue(out["required_checks_present"])
        self.assertFalse(out["check:ci"])

    def test_zero_required_fails_closed(self):
        out = {g[0]: g[1] for g in automerge.eval_checks([], [], {}, "abc")}
        self.assertFalse(out["required_checks_present"])

    def test_success_at_pinned_sha(self):
        runs = [{"name": "ci", "status": "completed", "conclusion": "success", "head_sha": "abc"}]
        out = {g[0]: g[1] for g in automerge.eval_checks(["ci"], runs, {}, "abc")}
        self.assertTrue(out["required_checks_present"])
        self.assertTrue(out["check:ci"])
        self.assertTrue(out["no_failing_or_pending_checks"])

    def test_wrong_sha_fails(self):
        runs = [{"name": "ci", "status": "completed", "conclusion": "success", "head_sha": "fff"}]
        out = automerge.eval_checks(["ci"], runs, {}, "abc")
        self.assertEqual(out[0][0], "checks_pinned_to_sha")
        self.assertFalse(out[0][1])


class Armed(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="factory-am-")
        os.environ["FACTORY_ROOT"] = self.root
        os.environ["FACTORY_KILL"] = os.path.join(self.root, "KILL")
        self.cfg = {
            "kill_switch_file": os.environ["FACTORY_KILL"],
            "automerge": {"enabled": True, "state": "ARMED", "max_per_day": 2, "repos": ["example-org/app"]},
        }

    def test_armed(self):
        self.assertIsNone(automerge.armed_reason(self.cfg))

    def test_kill_file(self):
        open(self.cfg["kill_switch_file"], "w").write("stop\n")
        self.assertEqual(automerge.armed_reason(self.cfg), "KILL file present")

    def test_disarmed(self):
        self.cfg["automerge"]["state"] = "DISARMED_BY_REVERT"
        self.assertIn("DISARMED_BY_REVERT", automerge.armed_reason(self.cfg))


class Priority(unittest.TestCase):
    def test_p0_label(self):
        self.assertEqual(automerge.priority(["p0"]), "P0")

    def test_urgent(self):
        self.assertEqual(automerge.priority(["urgent"]), "P0")

    def test_default(self):
        self.assertEqual(automerge.priority([]), "P2")


class DraftOnly(unittest.TestCase):
    def test_draft_only_repos(self):
        # inject via a temp config file
        root = tempfile.mkdtemp(prefix="factory-do-")
        cfg_path = os.path.join(root, "config.json")
        open(cfg_path, "w").write('{"lanes":{"draft_only":{"enabled":true,"repos":["example-org/gateway"]}}}')
        os.environ["FACTORY_CONFIG"] = cfg_path
        os.environ["FACTORY_ROOT"] = root
        self.assertEqual(automerge.draft_only_repos(), ["example-org/gateway"])


if __name__ == "__main__":
    unittest.main()
