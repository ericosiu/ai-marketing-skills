#!/usr/bin/env python3
"""Deterministic guards for YouTube thumbnail profiles, renders, and edits."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from PIL import Image, ImageChops, ImageDraw


SUPPORTED_IMAGE_FORMATS = ("PNG", "JPEG", "WEBP")


@dataclass(frozen=True)
class Box:
    label: str
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def width(self) -> int:
        return self.x2 - self.x1 + 1

    @property
    def height(self) -> int:
        return self.y2 - self.y1 + 1

    def intersects(self, other: "Box") -> bool:
        return not (
            self.x2 < other.x1
            or self.x1 > other.x2
            or self.y2 < other.y1
            or self.y1 > other.y2
        )


def _field_value(text: str, field: str) -> str | None:
    match = re.search(rf"(?mi)^\s*-?\s*{re.escape(field)}\s*:\s*(.+?)\s*$", text)
    return match.group(1).strip() if match else None


def _reference_paths(text: str, field: str, profile_dir: Path) -> List[Path]:
    value = _field_value(text, field)
    if not value:
        return []
    raw_paths = re.findall(r"`([^`]+)`", value)
    if not raw_paths:
        raw_paths = [part.strip() for part in value.split(",") if part.strip()]
    return [
        path if path.is_absolute() else (profile_dir / path).resolve()
        for path in map(Path, raw_paths)
    ]


def validate_profile(profile: Path) -> List[str]:
    errors: List[str] = []
    if not profile.is_file():
        return [f"Profile does not exist: {profile}"]

    text = profile.read_text()
    for field in ("Channel URL", "Profile version", "Reviewed at", "Evidence", "Output root"):
        if not _field_value(text, field):
            errors.append(f"Missing required profile field: {field}")

    for heading in ("Core formula", "Identity rules", "Production boundaries", "Refresh gate"):
        if not re.search(rf"(?mi)^##\s+{re.escape(heading)}\s*$", text):
            errors.append(f"Missing required profile section: {heading}")

    for field, label in (
        ("Approved subject references", "subject reference"),
        ("Approved style references", "style reference"),
    ):
        paths = _reference_paths(text, field, profile.parent)
        if not paths:
            errors.append(f"Missing approved {label} paths")
            continue
        for path in paths:
            if not path.is_file():
                errors.append(f"Approved {label} does not exist: {path}")

    return errors


def _box_errors(box: Box, width: int, height: int) -> List[str]:
    errors: List[str] = []
    if box.x1 < 0 or box.y1 < 0 or box.x2 >= width or box.y2 >= height:
        errors.append(f"{box.label} box leaves the canvas: {box}")
    if box.x2 < box.x1 or box.y2 < box.y1:
        errors.append(f"{box.label} box has inverted coordinates: {box}")
    return errors


def validate_final(
    image_path: Path,
    expected_size: Tuple[int, int],
    safe_boxes: Sequence[Box],
    min_horizontal_margin: int,
    min_vertical_margin: int,
    timestamp_safe_size: Tuple[int, int],
) -> List[str]:
    errors: List[str] = []
    if not image_path.is_file():
        return [f"Image does not exist: {image_path}"]

    try:
        with Image.open(image_path, formats=SUPPORTED_IMAGE_FORMATS) as image:
            width, height = image.size
    except (OSError, Image.DecompressionBombError) as exc:
        return [
            f"Unsupported or invalid image {image_path}: {exc}. "
            "Use PNG, JPEG, or WebP."
        ]

    if (width, height) != expected_size:
        errors.append(
            f"Unexpected dimensions for {image_path.name}: {(width, height)} != {expected_size}"
        )

    if min_horizontal_margin < 0 or min_vertical_margin < 0:
        errors.append("Safe margins must be non-negative")

    timestamp_width, timestamp_height = timestamp_safe_size
    if timestamp_width <= 0 or timestamp_height <= 0:
        errors.append("Timestamp-safe dimensions must be positive")
    elif timestamp_width > width or timestamp_height > height:
        errors.append("Timestamp-safe dimensions must fit inside the canvas")
    if errors:
        return errors
    timestamp_box = Box(
        "YouTube timestamp",
        width - timestamp_width,
        height - timestamp_height,
        width - 1,
        height - 1,
    )

    for box in safe_boxes:
        box_errors = _box_errors(box, width, height)
        errors.extend(box_errors)
        if box_errors:
            continue
        horizontal_margin = min(box.x1, width - 1 - box.x2)
        vertical_margin = min(box.y1, height - 1 - box.y2)
        if horizontal_margin < min_horizontal_margin:
            errors.append(
                f"{box.label} horizontal safe margin is {horizontal_margin}px; "
                f"requires {min_horizontal_margin}px"
            )
        if vertical_margin < min_vertical_margin:
            errors.append(
                f"{box.label} vertical safe margin is {vertical_margin}px; "
                f"requires {min_vertical_margin}px"
            )
        if box.intersects(timestamp_box):
            errors.append(f"{box.label} intersects the YouTube timestamp-safe corner")

    return errors


def validate_edit(
    before_path: Path,
    after_path: Path,
    allowed_box: Box,
    pixel_threshold: int,
    max_outside_change: float,
) -> List[str]:
    errors: List[str] = []
    if not before_path.is_file():
        errors.append(f"Before image does not exist: {before_path}")
    if not after_path.is_file():
        errors.append(f"After image does not exist: {after_path}")
    if errors:
        return errors

    if isinstance(pixel_threshold, bool) or not 0 <= pixel_threshold <= 255:
        errors.append("Pixel threshold must be between 0 and 255")
    if isinstance(max_outside_change, bool) or not 0 <= max_outside_change <= 1:
        errors.append("Maximum outside change must be between 0 and 1")
    if errors:
        return errors

    try:
        with Image.open(before_path, formats=SUPPORTED_IMAGE_FORMATS) as before_image:
            before = before_image.convert("RGBA")
        with Image.open(after_path, formats=SUPPORTED_IMAGE_FORMATS) as after_image:
            after = after_image.convert("RGBA")
    except (OSError, Image.DecompressionBombError) as exc:
        return [f"Unsupported or invalid edit image: {exc}. Use PNG, JPEG, or WebP."]

    if before.size != after.size:
        return [f"Edit changed canvas size: {before.size} -> {after.size}"]

    width, height = before.size
    box_errors = _box_errors(allowed_box, width, height)
    if box_errors:
        return box_errors

    diff = ImageChops.difference(before, after)
    ImageDraw.Draw(diff).rectangle(
        (allowed_box.x1, allowed_box.y1, allowed_box.x2, allowed_box.y2),
        fill=(0, 0, 0, 0),
    )

    channel_masks = [
        channel.point(lambda value: 255 if value > pixel_threshold else 0)
        for channel in diff.split()
    ]
    changed_mask = channel_masks[0]
    for channel_mask in channel_masks[1:]:
        changed_mask = ImageChops.lighter(changed_mask, channel_mask)
    changed_pixels = changed_mask.histogram()[255]
    outside_pixels = width * height - allowed_box.width * allowed_box.height
    changed_fraction = changed_pixels / max(1, outside_pixels)

    if changed_fraction > max_outside_change:
        errors.append(
            f"Edit changed {changed_pixels} pixels outside {allowed_box.label} "
            f"({changed_fraction:.6%}); maximum is {max_outside_change:.6%}"
        )

    return errors


def parse_box(value: str) -> Box:
    try:
        label, coordinates = value.split(":", 1)
        x1, y1, x2, y2 = (int(part) for part in coordinates.split(","))
    except (ValueError, TypeError) as exc:
        raise argparse.ArgumentTypeError(
            "box must use label:x1,y1,x2,y2"
        ) from exc
    return Box(label=label, x1=x1, y1=y1, x2=x2, y2=y2)


def _print_result(errors: Iterable[str]) -> int:
    errors = list(errors)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate thumbnail profiles, final renders, and surgical edits."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    profile_parser = subparsers.add_parser("profile", help="validate a channel profile")
    profile_parser.add_argument("--profile", type=Path, required=True)

    final_parser = subparsers.add_parser("final", help="validate a final thumbnail")
    final_parser.add_argument("--image", type=Path, required=True)
    final_parser.add_argument("--expected-width", type=int, default=1280)
    final_parser.add_argument("--expected-height", type=int, default=720)
    final_parser.add_argument("--safe-box", type=parse_box, action="append", default=[])
    final_parser.add_argument("--min-horizontal-margin", type=int, default=64)
    final_parser.add_argument("--min-vertical-margin", type=int, default=36)
    final_parser.add_argument("--timestamp-safe-width", type=int, default=154)
    final_parser.add_argument("--timestamp-safe-height", type=int, default=72)

    edit_parser = subparsers.add_parser("edit", help="validate a surgical edit")
    edit_parser.add_argument("--before", type=Path, required=True)
    edit_parser.add_argument("--after", type=Path, required=True)
    edit_parser.add_argument("--allowed-box", type=parse_box, required=True)
    edit_parser.add_argument("--pixel-threshold", type=int, default=8)
    edit_parser.add_argument("--max-outside-change", type=float, default=0.001)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "profile":
        return _print_result(validate_profile(args.profile))
    if args.command == "final":
        return _print_result(
            validate_final(
                args.image,
                expected_size=(args.expected_width, args.expected_height),
                safe_boxes=args.safe_box,
                min_horizontal_margin=args.min_horizontal_margin,
                min_vertical_margin=args.min_vertical_margin,
                timestamp_safe_size=(args.timestamp_safe_width, args.timestamp_safe_height),
            )
        )
    return _print_result(
        validate_edit(
            args.before,
            args.after,
            allowed_box=args.allowed_box,
            pixel_threshold=args.pixel_threshold,
            max_outside_change=args.max_outside_change,
        )
    )


if __name__ == "__main__":
    sys.exit(main())
