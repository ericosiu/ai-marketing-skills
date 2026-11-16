#!/usr/bin/env python3
"""Daily factory card.

Writes digest/YYYY-MM-DD.md with four sections:
  A. Ledger: every merges.jsonl row from the last 24 hours.
  B. Low-blast PRs over the cap, ranked P0 down, each with a rec and a yes line.
  C. Merged-not-live sweep (drive at 4h, red at 24h) plus optional intake
     items from digest/intake-YYYY-MM-DD.json, ranked P0 down.
  D. Builders: last 7 days from attempts.jsonl.

Usage: daily_card.py [--date YYYY-MM-DD]

This script reads local files only. Intake text is untrusted data and is
never treated as instructions.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import factory_ledger  # noqa: E402
import factory_paths  # noqa: E402
import not_live_sweep  # noqa: E402
import record_attempt  # noqa: E402

P_RULES = [
    ("P0", r"\b(outage|down for|is down|data leak|leak(ed)?|security|charged twice|double charge|cannot log ?in|can't log ?in|500 error|all (users|agents) (blocked|broken))\b"),
    ("P1", r"\b(bug|broken|error|fails?|failing|crash|stuck|wrong|refund|spent \$?\d+|not working)\b"),
    ("P2", r"\b(feature|request|would be nice|can we|could we|add|support for|idea|proposal|proposing)\b"),
]
DEFAULT_REC = {
    "P0": "Fix now. File an issue and dispatch today.",
    "P1": "File an issue and dispatch in the next weekday batch.",
    "P2": "Add to the backlog. Revisit at the weekly readout.",
    "P3": "No action. Signal only.",
}


def classify(text):
    for p, pat in P_RULES:
        if re.search(pat, text or "", re.I):
            return p
    return "P3"


def cell(v):
    return str(v if v is not None else "").replace("|", "/").replace("\n", " ").strip()


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def build(day: dt.date, now: dt.datetime):
    since = now - dt.timedelta(hours=24)
    zone = factory_paths.timezone_name()
    rows = []
    for r in factory_ledger.rows():
        t = record_attempt.parse_time(factory_ledger.row_time(r))
        if t and since <= t <= now:
            rows.append(r)
    merged_keys = {(r["repo"], r["pr"]) for r in factory_ledger.rows() if r.get("event") == "merged"}
    lines = [
        f"# Factory daily card, {day.isoformat()} ({zone})",
        "",
        f"Built {now.strftime('%Y-%m-%d %H:%M')} {zone}. Window: last 24 hours.",
        "",
    ]

    cfg = factory_paths.load_config()
    am = cfg.get("automerge") or cfg.get("automerge_low") or {}
    kill = factory_paths.kill_present(cfg)
    repos = ", ".join(r.split("/")[-1] for r in am.get("repos", [])) or "(none)"
    cap = am.get("max_per_day", 2)
    lines += [
        f"Auto-merge: {am.get('state', 'unknown') if am.get('enabled') and am.get('state') == 'ARMED' else am.get('state', 'unknown')}"
        f" for {repos}. Cap {cap} a day."
        f" KILL file: {'ON' if kill else 'off'}.",
        "",
    ]

    auto = [r for r in rows if r.get("merged_by") == "auto" and r.get("event") == "merged"]
    rev = [r for r in rows if r.get("event") in ("reverted", "revert_opened")]
    lines += [
        "## A. Merges and reverts, last 24 hours",
        "",
        f"{sum(1 for r in rows if r.get('event') == 'merged')} merges ({len(auto)} auto), {len(rev)} reverts.",
        "",
    ]
    if rows:
        lines += ["| Time | Event | PR | By | Blast | Port-back |", "|---|---|---|---|---|---|"]
        for r in sorted(rows, key=lambda x: factory_ledger.row_time(x)):
            stamp = factory_ledger.row_time(r)
            short = stamp[5:16].replace("T", " ") if len(stamp) >= 16 else stamp
            lines.append(
                f"| {short} | {cell(r.get('event'))} | "
                f"[{(r.get('repo') or '').split('/')[-1]}#{r['pr']}]({r.get('pr_url','')}) {cell(r.get('title'))[:50]} | "
                f"{cell(r.get('merged_by'))} | {cell(r.get('blast_tier'))} | {cell(r.get('portback'))[:70]} |"
            )
    else:
        lines.append("No ledger rows.")
    lines.append("")

    digest = factory_paths.digest_dir()
    held = {}
    for d in (day - dt.timedelta(days=1), day):
        for h in load_json(os.path.join(digest, f"held-{d.isoformat()}.json"), []):
            if (h["repo"], h["pr"]) not in merged_keys:
                held[(h["repo"], h["pr"])] = h
    lines += ["## B. Low-blast PRs over the cap (P0 first)", ""]
    if held:
        for i, h in enumerate(sorted(held.values(), key=lambda x: (x.get("priority", "P2"), x.get("created_at", ""))), 1):
            repo = h["repo"].split("/")[-1]
            lines += [
                f"{i}. **{h.get('priority', 'P2')}** [{repo}#{h['pr']}]({h.get('url','')}) {cell(h.get('title'))}",
                f"   (REC) merge. Passed every gate at head {str(h.get('head',''))[:8]}; held because {h.get('held_because','cap')}.",
                f"   `yes merge {repo}#{h['pr']}`",
            ]
    else:
        lines.append("None. No passing low-blast PR was held today.")
    lines.append("")

    sweep = not_live_sweep.report(now=now)
    drive = [x for x in sweep if x["status"] == "drive"]
    red = [x for x in sweep if x["status"] == "red"]
    lines += ["## C. Merged but not live, and intake (P0 first)", ""]
    if red or drive:
        for x in red:
            lines.append(
                f"- **RED** {x['repo']}#{x['pr']} still not live after {x['age_hours']}h. "
                f"Port-back: {cell(x.get('portback'))}."
            )
        for x in drive:
            lines.append(
                f"- **DRIVE** {x['repo']}#{x['pr']} not live after {x['age_hours']}h. "
                f"Port-back: {cell(x.get('portback'))}."
            )
    else:
        lines.append("No merged-not-live items past the warn window.")
    lines.append("")

    intake_path = os.path.join(digest, f"intake-{day.isoformat()}.json")
    intake = load_json(intake_path, None)
    if intake is None:
        lines.append(f"Intake file missing ({intake_path}). Optional. Skip if you have no intake feed.")
    else:
        items = intake.get("items") or []
        for it in items:
            it.setdefault("priority", classify(it.get("summary", "")))
            it.setdefault("rec", DEFAULT_REC[it["priority"]])
        if items:
            for i, it in enumerate(sorted(items, key=lambda x: (x["priority"], x.get("time", ""))), 1):
                link = f" [link]({it['link']})" if it.get("link") else ""
                lines += [
                    f"{i}. **{it['priority']}** {cell(it.get('source'))} {cell(it.get('summary'))}{link}",
                    f"   (REC) {cell(it['rec'])}" + (f" {cell(it['reason'])}" if it.get("reason") else ""),
                ]
        else:
            lines.append("No intake items in the window.")
    lines.append("")

    stats = record_attempt.builder_stats(record_attempt.rows(), now=now, days=7)
    lines += [record_attempt.format_builders(stats), ""]
    return "\n".join(lines)


def main():
    a = sys.argv[1:]
    zone = factory_paths.tz()
    now = dt.datetime.now(zone)
    day = dt.date.fromisoformat(a[a.index("--date") + 1]) if "--date" in a else now.date()
    if day != now.date():
        now = dt.datetime.combine(day, dt.time(23, 59), zone)
    digest = factory_paths.digest_dir()
    os.makedirs(digest, exist_ok=True)
    out = os.path.join(digest, f"{day.isoformat()}.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(build(day, now))
        f.write("\n")
    print(out)


if __name__ == "__main__":
    main()
