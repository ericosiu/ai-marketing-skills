#!/usr/bin/env python3
"""Validate an evidence-enriched label plan without changing any task."""
import argparse
from datetime import datetime, timedelta
import json
from pathlib import Path
import re
import sys

PREFIX = re.compile(r"^P([0-4])(B7)?\s*[-–—]\s*")


def timestamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("timestamps must include a timezone")
    return result


def plan_labels(records, now, limit=57):
    if not isinstance(records, list):
        raise ValueError("input must be a JSON array")
    seen = set()
    result = []
    for record in records:
        key = (record["host"], record["id"])
        if key in seen:
            raise ValueError("duplicate host/task ID")
        seen.add(key)
        old = record["old_title"]
        category = record["category"].strip()
        label = record["label"].strip()
        priority = record["priority"]
        if priority is not None and (type(priority) is not int or priority not in range(5)):
            raise ValueError("priority must be null or an integer from 0 to 4")
        if not category or not label or any(c in category + label for c in "\n\r\t"):
            raise ValueError("category and label must be nonempty single-line text")
        # Permit already-formatted labels as input without accumulating prefixes.
        label = PREFIX.sub("", label)
        if label.startswith(category + " - "):
            label = label[len(category) + 3:]
        if not label:
            raise ValueError("label needs a task description")
        previous = PREFIX.match(old)
        flags = []
        activity = record.get("last_activity")
        stale = bool(previous and previous.group(2))
        if activity:
            last = timestamp(activity)
            if last > now:
                flags.append("future_activity")
            else:
                stale = now - last > timedelta(days=7)
        else:
            flags.append("unknown_activity")
        if priority is None:
            flags.append("unranked")
            prefix = ""
        else:
            prefix = f"P{priority}{'B7' if stale else ''} - "
        new = f"{prefix}{category} - {label}"
        if len(new) > limit:
            raise ValueError(f"task {record['id']}: title exceeds {limit} characters; shorten the label")
        result.append({"id": record["id"], "host": record["host"],
                       "old_title": old, "new_title": new,
                       "changed": old != new, "review_flags": flags,
                       "last_activity": activity})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Private JSON array of evidence-enriched task records")
    parser.add_argument("--now", required=True, help="Fixed ISO timestamp with timezone for this run")
    parser.add_argument("--limit", type=int, default=57, help="Maximum title characters (default: 57)")
    args = parser.parse_args()
    try:
        if args.limit < 1:
            raise ValueError("limit must be positive")
        output = plan_labels(json.loads(args.input.read_text()), timestamp(args.now), args.limit)
    except (ValueError, KeyError, TypeError, AttributeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
