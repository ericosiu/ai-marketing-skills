import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


class PublicPackageTests(unittest.TestCase):
    def test_private_channel_profile_and_assets_are_not_bundled(self):
        self.assertFalse((SKILL_ROOT / "references" / "leveling-up-profile.md").exists())
        self.assertFalse((SKILL_ROOT / "assets").exists())

    def test_skill_has_public_profile_fallback_and_version(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("version: 1.0.0", skill)
        self.assertIn("This public package does not bundle a creator profile", skill)


if __name__ == "__main__":
    unittest.main()
