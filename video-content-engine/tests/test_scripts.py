import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ScriptTests(unittest.TestCase):
    def test_boundary_audit_rejects_coarse_cut(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            transcript = root / "transcript.json"
            clips = root / "clips.json"
            transcript.write_text(json.dumps({"granularity": "sentence", "segments": [{"start": 0.35, "end": 2.45, "text": "Complete opening."}, {"start": 2.70, "end": 5.15, "text": "Complete closing."}]}))
            clips.write_text(json.dumps({"retained_clips": [{"id": "c1", "source_start": 0.0, "content_start": 1.0, "content_end": 5.0, "source_end": 5.4}]}))
            result = subprocess.run(["python3", str(ROOT / "scripts/audit_edit_boundaries.py"), "--transcript", str(transcript), "--clips", str(clips)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)["status"], "FAIL")

    def test_minimal_delivery_passes(self):
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as external:
            root, source = Path(temporary), Path(external) / "source.txt"
            source.write_text("authorized sample source")
            (root / "analysis").mkdir()
            (root / "packaging").mkdir()
            (root / "analysis/content-opportunities.json").write_text("[]")
            image = root / "packaging/cover.png"
            image.write_bytes(b"sample-image")
            digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
            manifest = {"schema_version": 1, "project": "sample", "source": {"path": str(source), "sha256": digest(source)}, "requested_modules": ["packaging"], "opportunity_inventory": "analysis/content-opportunities.json", "outputs": {"packaging": [{"image": "packaging/cover.png", "sha256": digest(image)}]}, "documents": []}
            (root / "delivery-manifest.json").write_text(json.dumps(manifest))
            result = subprocess.run(["python3", str(ROOT / "scripts/validate_delivery.py"), "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
