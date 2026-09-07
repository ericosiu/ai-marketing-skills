#!/usr/bin/env python3
"""Validate the optional format-library interchange; never writes input files."""
import argparse
from datetime import datetime
import json
import math
from pathlib import Path
from urllib.parse import urlsplit


def validate(data):
    errors = []
    if not isinstance(data, dict):
        return ["snapshot must be an object"]
    groups = {}
    for group in ("posts", "formats", "ideas"):
        rows = data.get(group)
        if not isinstance(rows, list):
            errors.append(f"{group} must be an array")
            rows = []
        groups[group] = {}
        for index, row in enumerate(rows):
            if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"].strip():
                errors.append(f"{group}[{index}] needs a nonempty string id")
            elif row["id"] in groups[group]:
                errors.append(f"{group}: duplicate id {row['id']}")
            else:
                groups[group][row["id"]] = row

    def url(value, label, nullable=False):
        if value is None and nullable:
            return
        try:
            parsed = urlsplit(value) if isinstance(value, str) else None
            valid = parsed and parsed.scheme in ("http", "https") and parsed.hostname and not parsed.username and not parsed.password
        except ValueError:
            valid = False
        if not valid:
            errors.append(f"{label}: expected HTTP(S) URL without credentials")

    def three(value, label):
        if not isinstance(value, list) or len(value) != 3 or any(not isinstance(s, str) or not s.strip() for s in value):
            errors.append(f"{label}: expected three nonempty strings")

    def refs(value, target, label, count=None):
        if not isinstance(value, list) or not value or any(not isinstance(s, str) for s in value):
            errors.append(f"{label}: expected source ID array")
            return
        if len(set(value)) != len(value) or (count is not None and len(value) != count):
            errors.append(f"{label}: invalid reference count or duplicate IDs")
        if any(s not in groups[target] for s in value):
            errors.append(f"{label}: unresolved reference")

    for key, post in groups["posts"].items():
        url(post.get("url"), f"{key}.url")
        dates = {}
        for field in ("published_at", "checked_at"):
            if field not in post:
                errors.append(f"{key}.{field}: required; use null if unknown")
                continue
            value = post[field]
            if value is None:
                continue
            try:
                stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if stamp.tzinfo is None:
                    raise ValueError()
                dates[field] = stamp
            except (ValueError, TypeError, AttributeError):
                errors.append(f"{key}.{field}: expected timezone-aware ISO timestamp or null")
        if len(dates) == 2 and dates["checked_at"] < dates["published_at"]:
            errors.append(f"{key}: check predates publication")
        metrics = post.get("metrics")
        if not isinstance(metrics, dict):
            errors.append(f"{key}.metrics: expected object")
        else:
            for metric, value in metrics.items():
                if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0):
                    errors.append(f"{key}.{metric}: expected finite nonnegative number or null")
    for key, fmt in groups["formats"].items():
        refs(fmt.get("post_ids"), "posts", f"{key}.post_ids")
        three(fmt.get("prompts"), f"{key}.prompts")
    for key, idea in groups["ideas"].items():
        if "source_url" not in idea:
            errors.append(f"{key}.source_url: required; use null for a new premise")
        url(idea.get("source_url"), f"{key}.source_url", nullable=True)
        refs(idea.get("format_ids"), "formats", f"{key}.format_ids", count=2)
        three(idea.get("talking_prompts"), f"{key}.talking_prompts")
        if not isinstance(idea.get("claim_limit"), str) or not idea["claim_limit"].strip():
            errors.append(f"{key}.claim_limit: required")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    args = parser.parse_args()
    try:
        errors = validate(json.loads(args.snapshot.read_text()))
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Cannot read snapshot: {exc}\n")
    for error in errors:
        print(error)
    if not errors:
        print("Library interchange valid; source truth and UI behavior not assessed.")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
