#!/usr/bin/env python3
"""Watch a live port-back for a configured window (default 24 hours).

If a metric drifts past a threshold, or error logs exceed a cap, restore
every live file from its .bak-YYYYMMDD-pr-N copy (all or nothing).

Usage:
  postrelease_watch.py CONFIG.json            # evaluate once, dry run
  postrelease_watch.py CONFIG.json --execute  # restore on breach

A window that has already closed exits 0. A breach exits 2. A config or
read error exits 1. Decisions append to the watch log in the config.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_datetime(s):
    return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))


def read_metric(source, read_spec):
    path = Path(source)
    if not path.exists():
        return None, "missing source"
    text = path.read_text(encoding="utf-8")
    kind = (read_spec or {}).get("type") or "json"
    if kind == "regex":
        pat = read_spec.get("pattern")
        if not pat:
            return None, "no pattern"
        m = re.search(pat, text)
        if not m:
            return None, "no match"
        try:
            return float(m.group(1) if m.lastindex else m.group(0)), None
        except (TypeError, ValueError):
            return None, "not a number"
    if kind == "jsonl":
        field = read_spec.get("field")
        agg = read_spec.get("aggregation") or "last"
        values = []
        for line in text.splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if field in row and isinstance(row[field], (int, float)):
                values.append(float(row[field]))
        if not values:
            return None, "no values"
        if agg == "sum":
            return sum(values), None
        if agg == "count":
            return float(len(values)), None
        return values[-1], None
    # json
    data = json.loads(text)
    key_path = read_spec.get("key_path") or []
    cur = data
    for k in key_path:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return None, "missing key"
    if isinstance(cur, (int, float)):
        return float(cur), None
    return None, "not a number"


def check_metric_breach(current, baseline, threshold, direction):
    if current is None or baseline is None:
        return False
    delta = current - baseline
    if direction == "above":
        return delta > threshold
    if direction == "below":
        return -delta > threshold
    return abs(delta) > threshold


def count_errors_since(log_paths, patterns, applied_at):
    pats = [re.compile(p) for p in (patterns or [])]
    total = 0
    hits = []
    applied = parse_datetime(applied_at)
    for path in log_paths or []:
        p = Path(path)
        if not p.exists():
            continue
        mtime = dt.datetime.fromtimestamp(p.stat().st_mtime, tz=applied.tzinfo)
        if mtime < applied:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            for pat in pats:
                if pat.search(line):
                    total += 1
                    hits.append({"path": path, "line": i})
                    break
    return total, hits


def restore_files(live_files, dry_run=False):
    restored, errors = [], []
    for item in live_files:
        live = item["live_path"]
        bak = item["bak_path"]
        if not os.path.exists(bak):
            errors.append(f"missing backup: {bak}")
            continue
        if dry_run:
            restored.append({"live": live, "bak": bak, "dry_run": True})
            continue
        os.makedirs(os.path.dirname(live) or ".", exist_ok=True)
        shutil.copy2(bak, live)
        restored.append({"live": live, "bak": bak})
    if errors and not dry_run:
        raise RuntimeError("rollback aborted, not all-or-nothing: " + "; ".join(errors))
    return restored, errors


def window_open(config, now):
    applied = parse_datetime(config["applied_at"])
    if applied.tzinfo is None:
        applied = applied.replace(tzinfo=now.tzinfo)
    hours = float(config.get("watch_hours") or 24)
    return now <= applied + dt.timedelta(hours=hours), applied, hours


def run_watch(config, now=None, execute=False):
    now = now or dt.datetime.now(dt.timezone.utc)
    open_, applied, hours = window_open(config, now)
    decision = {
        "fix_id": config.get("fix_id"),
        "pr": config.get("pr"),
        "at": now.isoformat(),
        "execute": bool(execute),
    }
    if not open_:
        decision["decision"] = "WINDOW_CLOSED"
        return decision
    metric_cfg = config.get("metric") or {}
    metric_error = ""
    current = None
    if metric_cfg.get("source"):
        current, metric_error = read_metric(metric_cfg["source"], metric_cfg.get("read_spec") or {})
    metric_breach = check_metric_breach(
        current,
        metric_cfg.get("baseline"),
        float(metric_cfg.get("threshold") or 0),
        metric_cfg.get("direction") or "above",
    )
    err_cfg = config.get("errors") or {}
    err_count, _hits = count_errors_since(
        err_cfg.get("log_paths") or [],
        err_cfg.get("patterns") or ["Traceback", "ERROR", "CRITICAL"],
        config["applied_at"],
    )
    max_errors = int(err_cfg.get("max_errors") or 0)
    error_breach = max_errors > 0 and err_count > max_errors
    decision.update({
        "metric_value": current,
        "metric_error": metric_error,
        "metric_breach": metric_breach,
        "error_count": err_count,
        "error_breach": error_breach,
        "window_hours": hours,
        "applied_at": applied.isoformat(),
    })
    if metric_error and metric_cfg.get("source") and metric_cfg.get("fail_on_read_error", True):
        decision["decision"] = "ERROR_READING_METRIC"
        breach = True
    elif metric_breach or error_breach:
        decision["decision"] = "BREACH"
        breach = True
    else:
        decision["decision"] = "OK"
        breach = False
    if breach:
        restored, errors = restore_files(config.get("live_files") or [], dry_run=not execute)
        decision["restored"] = restored
        decision["restore_errors"] = errors
    return decision


def append_log(config, decision):
    path = config.get("watch_log")
    if not path:
        return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(decision) + "\n")


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(1)
    execute = "--execute" in a
    path = next(x for x in a if not x.startswith("-"))
    with open(path, encoding="utf-8") as f:
        config = json.load(f)
    decision = run_watch(config, execute=execute)
    append_log(config, decision)
    print(json.dumps(decision, indent=1))
    if decision["decision"] == "WINDOW_CLOSED":
        sys.exit(0)
    if decision["decision"] == "OK":
        sys.exit(0)
    if decision["decision"] == "ERROR_READING_METRIC":
        sys.exit(1)
    sys.exit(2)


if __name__ == "__main__":
    main()
