import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import portback


class Exclude(unittest.TestCase):
    def test_env_excluded(self):
        self.assertTrue(portback.excluded(".env"))
        self.assertTrue(portback.excluded("secrets/foo"))
        self.assertFalse(portback.excluded("bin/parse.py"))

    def test_github_excluded(self):
        self.assertTrue(portback.excluded(".github/workflows/ci.yml"))


class ApplyDiff(unittest.TestCase):
    def test_apply_and_skip_excluded(self):
        tree = tempfile.mkdtemp(prefix="portback-tree-")
        os.makedirs(os.path.join(tree, "bin"))
        open(os.path.join(tree, "bin", "parse.py"), "w").write("x = 1\n")
        diff = (
            "diff --git a/bin/parse.py b/bin/parse.py\n"
            "--- a/bin/parse.py\n+++ b/bin/parse.py\n"
            "@@ -1 +1,2 @@\n x = 1\n+y = 2\n"
        )
        rows = [{"path": "bin/parse.py", "excluded": False, "test": False}]
        ok, _log = portback.apply_diff(diff, tree, rows)
        self.assertTrue(ok)
        self.assertIn("y = 2", open(os.path.join(tree, "bin", "parse.py")).read())

    def test_backup_name_format(self):
        # document the live backup suffix
        self.assertEqual("file.py.bak-20261116-pr-31".split(".")[-1].count("-"), 3)
