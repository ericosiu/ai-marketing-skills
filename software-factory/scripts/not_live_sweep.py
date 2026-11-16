#!/usr/bin/env python3
"""Sweep merged PRs that are not yet live.

Usage:
  not_live_sweep.py            # print a report
  not_live_sweep.py --claim    # append a claim row before a port-back so two
                               # workers never port the same PR or file at once

A merged, live-meant PR that is not LIVE after warn_hours (default 4) is
status "drive". Still stuck at stuck_hours (default 24) is status "red".
Rows append to not-live-sweep.jsonl. Never hand-edit that file.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import factory_ledger  # noqa: E402
import factory_paths  # noqa: E402
import record_attempt  # noqa: E402


def sweep_path():
    return os.path.join(factory_paths.ledger_dir(), "not-live-sweep.jsonl")


def hours_cfg():
    cfg = factory_paths.load_config()
    nls = cfg.get("not_live") or {}
    return float(nls.get("warn_hours") or 4), float(nls.get("stuck_hours") or 24)


def latest_merge_state(rows):
    """Latest event per (repo, pr)."""
    out = {}
    for r in rows:
        key = (r.get("repo") or "", int(r.get("pr") or 0))
        out[key] = r
    return out


def is_live_meant(row):
    status = (row.get("portback") or "").upper()
    if status.startswith("N/A") or status.startswith("N/A".lower()):
        return False
    if "NOT APPLICABLE" in status:
        return False
    if row.get("event") in ("reverted", "revert_opened"):
        return False
    return row.get("event") == "merged"


def is_live(row):
    text = str(row.get("portback") or "")
    st = record_attempt.portback_status(text)
    if st == "LIVE":
        return True
    return text.upper().startswith("LIVE")


def classify(row, now, warn_hours, stuck_hours):
    t = factory_ledger.row_time(row)
    parsed = record_attempt.parse_time(t)
    if not parsed:
        return "unknown", None
    age = (now - parsed).total_seconds() / 3600.0
    if is_live(row):
        return "ok", age
    if not is_live_meant(row):
        return "skip", age
    if age >= stuck_hours:
        return "red", age
    if age >= warn_hours:
        return "drive", age
    return "pending", age


def report(now=None):
    now = now or dt.datetime.now(factory_paths.tz())
    warn_hours, stuck_hours = hours_cfg()
    items = []
    for (_repo, _pr), row in latest_merge_state(factory_ledger.rows()).items():
        status, age = classify(row, now, warn_hours, stuck_hours)
        items.append({
            "repo": row.get("repo"),
            "pr": row.get("pr"),
            "title": row.get("title"),
            "merge_sha": row.get("merge_sha"),
            "portback": row.get("portback"),
            "status": status,
            "age_hours": None if age is None else round(age, 2),
        })
    order = {"red": 0, "drive": 1, "pending": 2, "unknown": 3, "ok": 4, "skip": 5}
    items.sort(key=lambda x: (order.get(x["status"], 9), x.get("age_hours") or 0), reverse=False)
    return items


def active_claims():
    path = sweep_path()
    if not os.path.exists(path):
        return {}
    claims = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            key = (rec.get("repo"), rec.get("pr"))
            if rec.get("event") == "claim":
                claims[key] = rec
            elif rec.get("event") in ("release", "done"):
                claims.pop(key, None)
    return claims


def claim(repo, pr, files=None, worker=""):
    key = (repo, int(pr))
    existing = active_claims()
    if key in existing:
        raise SystemExit(f"REFUSED: {repo}#{pr} already claimed by {existing[key].get('worker')}")
    if files:
        for rec in existing.values():
            overlap = set(files) & set(rec.get("files") or [])
            if overlap:
                raise SystemExit(f"REFUSED: files already claimed: {sorted(overlap)}")
    rec = {
        "event": "claim",
        "time": factory_ledger.now_stamp(),
        "repo": repo,
        "pr": int(pr),
        "files": list(files or []),
        "worker": worker,
    }
    path = sweep_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def main():
    a = sys.argv[1:]
    if "--claim" in a:
        def flag(name):
            return a[a.index(name) + 1] if name in a and a.index(name) + 1 < len(a) else None
        repo, pr = flag("--repo"), flag("--pr")
        if not repo or not pr:
            print("not_live_sweep --claim needs --repo owner/name --pr N", file=sys.stderr)
            sys.exit(2)
        files = [x for x in (flag("--files") or "").split(",") if x]
        print(json.dumps(claim(repo, pr, files, flag("--worker") or "")))
        return
    items = report()
    print(json.dumps({
        "drive": [x for x in items if x["status"] == "drive"],
        "red": [x for x in items if x["status"] == "red"],
        "pending": [x for x in items if x["status"] == "pending"],
        "all": items,
    }, indent=1))


if __name__ == "__main__":
    main()
