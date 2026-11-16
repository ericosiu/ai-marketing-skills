#!/usr/bin/env python3
"""Build a 24h post-release watch config from live files and backups.

Usage:
  make_watch_config.py --fix-id F --pr N --applied-at ISO --live-root DIR \\
    --live-file rel:live:bak [--live-file ...] \\
    --metric-source FILE --metric-type json --metric-key a.b --metric-baseline 10 \\
    --metric-threshold 0 --metric-direction above \\
    --error-log FILE --max-errors 0 --watch-hours 24 --output watch.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_live_file(spec):
    parts = spec.split(":", 2)
    if len(parts) != 3:
        raise SystemExit(f"live file must be rel:live_path:bak_path, got {spec!r}")
    rel, live, bak = parts
    item = {"rel": rel, "live_path": live, "bak_path": bak}
    if Path(live).is_file():
        item["sha256"] = sha256_file(live)
    return item


def main():
    ap = argparse.ArgumentParser(description="Build a post-release watch config.")
    ap.add_argument("--fix-id", required=True)
    ap.add_argument("--pr", required=True)
    ap.add_argument("--applied-at", required=True)
    ap.add_argument("--live-root", required=True)
    ap.add_argument("--live-file", action="append", default=[], dest="live_files")
    ap.add_argument("--watch-hours", type=float, default=24)
    ap.add_argument("--metric-name", default="metric")
    ap.add_argument("--metric-source")
    ap.add_argument("--metric-type", default="json", choices=["json", "jsonl", "regex"])
    ap.add_argument("--metric-key", default="")
    ap.add_argument("--metric-field")
    ap.add_argument("--metric-agg", default="last")
    ap.add_argument("--metric-pattern")
    ap.add_argument("--metric-baseline", type=float)
    ap.add_argument("--metric-threshold", type=float, default=0)
    ap.add_argument("--metric-direction", default="above", choices=["above", "below", "abs"])
    ap.add_argument("--error-log", action="append", default=[], dest="error_logs")
    ap.add_argument("--error-pattern", action="append", default=["Traceback", "ERROR", "CRITICAL"], dest="error_patterns")
    ap.add_argument("--max-errors", type=int, default=0)
    ap.add_argument("--watch-log")
    ap.add_argument("--output", default="watch.json")
    args = ap.parse_args()
    if not args.live_files:
        print("need at least one --live-file rel:live:bak", file=sys.stderr)
        return 2
    live_files = [parse_live_file(s) for s in args.live_files]
    read_spec = {"type": args.metric_type}
    if args.metric_type == "json":
        read_spec["key_path"] = [k for k in args.metric_key.split(".") if k]
    elif args.metric_type == "jsonl":
        read_spec["field"] = args.metric_field
        read_spec["aggregation"] = args.metric_agg
    elif args.metric_type == "regex":
        read_spec["pattern"] = args.metric_pattern
    config = {
        "fix_id": args.fix_id,
        "pr": args.pr,
        "applied_at": args.applied_at,
        "watch_hours": args.watch_hours,
        "live_root": args.live_root,
        "live_files": live_files,
        "metric": {
            "name": args.metric_name,
            "source": args.metric_source,
            "read_spec": read_spec,
            "baseline": args.metric_baseline,
            "threshold": args.metric_threshold,
            "direction": args.metric_direction,
        },
        "errors": {
            "log_paths": args.error_logs,
            "patterns": args.error_patterns,
            "max_errors": args.max_errors,
        },
        "watch_log": args.watch_log,
    }
    Path(args.output).write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
