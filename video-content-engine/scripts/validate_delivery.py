#!/usr/bin/env python3
"""Validate a video-content delivery manifest and referenced files."""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


HASH = re.compile(r"^[0-9a-f]{64}$")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    manifest_path = root / "delivery-manifest.json"
    if not manifest_path.is_file():
        print(json.dumps({"status": "FAIL", "errors": ["delivery-manifest.json is missing"]}, indent=2))
        return 1
    manifest = json.loads(manifest_path.read_text())
    errors, checks = [], []
    if manifest.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    def require(relative: str, label: str):
        if not relative or Path(relative).is_absolute():
            errors.append(f"{label}: path must be relative")
            return None
        target = (root / relative).resolve()
        if root not in target.parents or not target.is_file():
            errors.append(f"{label}: missing or unsafe path {relative}")
            return None
        checks.append(f"{label}: exists")
        return target

    def verify(path, expected: str, label: str):
        if path is None:
            return
        if not HASH.fullmatch(expected or "") or digest(path) != expected:
            errors.append(f"{label}: invalid or mismatched SHA-256")
        else:
            checks.append(f"{label}: hash matches")

    source = manifest.get("source", {})
    source_path = Path(source.get("path", ""))
    if not source_path.is_absolute() or not source_path.is_file():
        errors.append("source.path must be an existing absolute file")
    else:
        verify(source_path, source.get("sha256", ""), "source")
    require(manifest.get("opportunity_inventory", ""), "opportunity inventory")
    outputs = manifest.get("outputs", {})
    if not isinstance(outputs, dict) or not any(outputs.values()):
        errors.append("outputs must contain a produced asset")
        outputs = {}
    for module, entries in outputs.items():
        if not isinstance(entries, list):
            errors.append(f"{module}: output must be a list")
            continue
        for index, entry in enumerate(entries, 1):
            label = f"{module} {index}"
            master = entry.get("master") if isinstance(entry, dict) else None
            if isinstance(master, dict):
                path = require(master.get("path", ""), f"{label} master")
                verify(path, master.get("sha256", ""), f"{label} master")
                if not isinstance(master.get("render_version"), int) or master["render_version"] < 1:
                    errors.append(f"{label}: render_version must be positive")
            if isinstance(entry, dict) and entry.get("image"):
                path = require(entry["image"], f"{label} image")
                verify(path, entry.get("sha256", ""), f"{label} image")
            for slide_index, slide in enumerate(entry.get("slides", []) if isinstance(entry, dict) else [], 1):
                path = require(slide.get("path", ""), f"{label} slide {slide_index}")
                verify(path, slide.get("sha256", ""), f"{label} slide {slide_index}")
    for index, document in enumerate(manifest.get("documents", []), 1):
        require(document, f"document {index}")
    report = {"status": "PASS" if not errors else "FAIL", "checks": checks, "errors": errors}
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
