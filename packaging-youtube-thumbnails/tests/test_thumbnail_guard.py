import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from thumbnail_guard import (  # noqa: E402
    Box,
    validate_edit,
    validate_final,
    validate_profile,
)


class ProfileValidationTests(unittest.TestCase):
    def test_complete_profile_with_existing_references_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "subject.jpg").write_bytes(b"subject")
            (root / "style.jpg").write_bytes(b"style")
            profile = root / "profile.md"
            profile.write_text(
                """# Channel Profile

- Channel URL: https://youtube.com/@example/videos
- Profile version: 1.0
- Reviewed at: 2026-07-11
- Evidence: 20 recent long-form uploads
- Output root: /tmp/youtube-thumbnails
- Approved subject references: `subject.jpg`
- Approved style references: `style.jpg`

## Core formula
One face + one tool + one consequence.

## Identity rules
Rules.

## Production boundaries
Boundaries.

## Refresh gate
Refresh only when the profile is missing, the user explicitly requests it, or the user supplies replacement brand examples.
"""
            )

            self.assertEqual(validate_profile(profile), [])

    def test_missing_output_root_and_reference_paths_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile = Path(tmp) / "profile.md"
            profile.write_text(
                """# Channel Profile
- Channel URL: https://youtube.com/@example/videos
- Profile version: 1.0
- Reviewed at: 2026-07-11
- Evidence: 20 uploads
## Core formula
Formula.
## Identity rules
Rules.
## Production boundaries
Boundaries.
## Refresh gate
Gate.
"""
            )

            errors = validate_profile(profile)

            self.assertTrue(any("Output root" in error for error in errors))
            self.assertTrue(any("subject reference" in error for error in errors))
            self.assertTrue(any("style reference" in error for error in errors))


class FinalAssetValidationTests(unittest.TestCase):
    def test_valid_dimensions_and_safe_box_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "thumbnail.png"
            Image.new("RGB", (1280, 720), "#f4ead7").save(image)

            errors = validate_final(
                image,
                expected_size=(1280, 720),
                safe_boxes=[Box("fable", 900, 200, 1150, 600)],
                min_horizontal_margin=64,
                min_vertical_margin=36,
                timestamp_safe_size=(154, 72),
            )

            self.assertEqual(errors, [])

    def test_edge_crowding_and_timestamp_overlap_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "thumbnail.png"
            Image.new("RGB", (1280, 720), "#f4ead7").save(image)

            errors = validate_final(
                image,
                expected_size=(1280, 720),
                safe_boxes=[
                    Box("cropped-logo", 1230, 200, 1275, 400),
                    Box("timestamp-collision", 1100, 650, 1240, 710),
                ],
                min_horizontal_margin=64,
                min_vertical_margin=36,
                timestamp_safe_size=(154, 72),
            )

            self.assertTrue(any("cropped-logo" in error and "horizontal" in error for error in errors))
            self.assertTrue(any("timestamp-collision" in error and "timestamp" in error for error in errors))

    def test_unsupported_image_format_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "thumbnail.bmp"
            Image.new("RGB", (1280, 720), "white").save(image)

            errors = validate_final(
                image,
                expected_size=(1280, 720),
                safe_boxes=[],
                min_horizontal_margin=64,
                min_vertical_margin=36,
                timestamp_safe_size=(154, 72),
            )

            self.assertTrue(any("Use PNG, JPEG, or WebP" in error for error in errors))

    def test_decompression_bomb_is_reported_as_validation_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "thumbnail.png"
            Image.new("RGB", (20, 20), "white").save(image)
            original_limit = Image.MAX_IMAGE_PIXELS
            Image.MAX_IMAGE_PIXELS = 100
            try:
                errors = validate_final(
                    image,
                    expected_size=(20, 20),
                    safe_boxes=[],
                    min_horizontal_margin=1,
                    min_vertical_margin=1,
                    timestamp_safe_size=(1, 1),
                )
            finally:
                Image.MAX_IMAGE_PIXELS = original_limit

            self.assertTrue(any("Unsupported or invalid image" in error for error in errors))

    def test_invalid_margins_and_timestamp_dimensions_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "thumbnail.png"
            Image.new("RGB", (1280, 720), "white").save(image)

            margin_errors = validate_final(
                image,
                expected_size=(1280, 720),
                safe_boxes=[Box("edge", 0, 0, 100, 100)],
                min_horizontal_margin=-1,
                min_vertical_margin=-1,
                timestamp_safe_size=(154, 72),
            )
            timestamp_errors = validate_final(
                image,
                expected_size=(1280, 720),
                safe_boxes=[],
                min_horizontal_margin=64,
                min_vertical_margin=36,
                timestamp_safe_size=(2000, -1),
            )

            self.assertTrue(any("non-negative" in error for error in margin_errors))
            self.assertTrue(any("positive" in error for error in timestamp_errors))


class SurgicalEditValidationTests(unittest.TestCase):
    def test_changes_inside_allowed_box_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            before = root / "before.png"
            after = root / "after.png"
            Image.new("RGB", (320, 180), "white").save(before)
            edited = Image.new("RGB", (320, 180), "white")
            for x in range(220, 281):
                for y in range(40, 121):
                    edited.putpixel((x, y), (255, 0, 0))
            edited.save(after)

            errors = validate_edit(
                before,
                after,
                allowed_box=Box("allowed", 215, 35, 285, 125),
                pixel_threshold=8,
                max_outside_change=0.0,
            )

            self.assertEqual(errors, [])

    def test_changes_outside_allowed_box_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            before = root / "before.png"
            after = root / "after.png"
            Image.new("RGB", (320, 180), "white").save(before)
            edited = Image.new("RGB", (320, 180), "white")
            edited.putpixel((20, 20), (0, 0, 0))
            edited.save(after)

            errors = validate_edit(
                before,
                after,
                allowed_box=Box("allowed", 215, 35, 285, 125),
                pixel_threshold=8,
                max_outside_change=0.0,
            )

            self.assertTrue(any("outside" in error for error in errors))

    def test_unsupported_edit_image_format_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            before = root / "before.bmp"
            after = root / "after.png"
            Image.new("RGB", (320, 180), "white").save(before)
            Image.new("RGB", (320, 180), "white").save(after)

            errors = validate_edit(
                before,
                after,
                allowed_box=Box("allowed", 215, 35, 285, 125),
                pixel_threshold=8,
                max_outside_change=0.0,
            )

            self.assertTrue(any("Use PNG, JPEG, or WebP" in error for error in errors))

    def test_alpha_only_changes_outside_allowed_box_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            before = root / "before.png"
            after = root / "after.png"
            Image.new("RGBA", (100, 100), (255, 255, 255, 255)).save(before)
            edited = Image.new("RGBA", (100, 100), (255, 255, 255, 0))
            for x in range(40, 60):
                for y in range(40, 60):
                    edited.putpixel((x, y), (255, 255, 255, 255))
            edited.save(after)

            errors = validate_edit(
                before,
                after,
                allowed_box=Box("allowed", 40, 40, 59, 59),
                pixel_threshold=8,
                max_outside_change=0.0,
            )

            self.assertTrue(any("outside" in error for error in errors))

    def test_out_of_range_thresholds_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            before = root / "before.png"
            after = root / "after.png"
            Image.new("RGB", (100, 100), "white").save(before)
            Image.new("RGB", (100, 100), "black").save(after)

            invalid_pixel = validate_edit(
                before,
                after,
                allowed_box=Box("allowed", 40, 40, 59, 59),
                pixel_threshold=256,
                max_outside_change=0.0,
            )
            invalid_fraction = validate_edit(
                before,
                after,
                allowed_box=Box("allowed", 40, 40, 59, 59),
                pixel_threshold=8,
                max_outside_change=2.0,
            )

            self.assertTrue(any("0 and 255" in error for error in invalid_pixel))
            self.assertTrue(any("0 and 1" in error for error in invalid_fraction))


if __name__ == "__main__":
    unittest.main()
