import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRUB = os.path.join(os.path.dirname(__file__), "..", "scripts", "scrub_snapshot.py")
AT = chr(64)
BAD_MAIL = "jane.doe" + AT + "gmail.com"
BAD_PROFILE = "linkedin.com/in/" + "janedoe"
KEEP_MAIL = "owner" + AT + "example.test"


class Scrub(unittest.TestCase):
    def test_replaces_name_and_email(self):
        src_dir = Path(tempfile.mkdtemp(prefix="factory-scrub-src-"))
        out = Path(tempfile.mkdtemp(prefix="factory-scrub-out-"))
        src = src_dir / "notes.md"
        src.write_text(f"Hello Jane Doe, write {BAD_MAIL} or see {BAD_PROFILE}.\n")
        mapping = out / "map.json"
        names = out / "names.txt"
        mapping.write_text(json.dumps({"docs/notes.md": str(src)}))
        names.write_text("Jane Doe\n")
        subprocess.check_call([
            sys.executable, SCRUB, "--map", str(mapping), "--names", str(names), "--out", str(out),
        ])
        text = (out / "docs" / "notes.md").read_text()
        self.assertNotIn("Jane Doe", text)
        self.assertNotIn(BAD_MAIL, text)
        self.assertNotIn(BAD_PROFILE, text)
        self.assertIn("Person-", text)
        self.assertIn(AT + "example.test", text)
        self.assertIn("linkedin.com/in/" + "li-", text)
        man = json.loads((out / "MANIFEST.json").read_text())
        self.assertFalse(man["files"][0]["repo_sha256_equals_src"])
        self.assertGreater(man["totals"]["name"], 0)
        self.assertGreater(man["totals"]["email"], 0)

    def test_keeps_placeholder_domain(self):
        src_dir = Path(tempfile.mkdtemp(prefix="factory-scrub-src-"))
        out = Path(tempfile.mkdtemp(prefix="factory-scrub-out-"))
        src = src_dir / "notes.md"
        src.write_text(f"Contact {KEEP_MAIL} please.\n")
        mapping = out / "map.json"
        names = out / "names.txt"
        mapping.write_text(json.dumps({"docs/notes.md": str(src)}))
        names.write_text("")
        subprocess.check_call([
            sys.executable, SCRUB, "--map", str(mapping), "--names", str(names), "--out", str(out),
        ])
        self.assertIn(KEEP_MAIL, (out / "docs" / "notes.md").read_text())


if __name__ == "__main__":
    unittest.main()
