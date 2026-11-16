#!/usr/bin/env python3
"""Append-only attempt ledger for factory dispatches, reviews, and merges.

Source of truth: $FACTORY_LEDGER_DIR/attempts.jsonl
This sidecar never edits merges.jsonl or MERGES.md.

Usage:
  record_attempt.py append     # JSON row on stdin, or flags (see --help)
  record_attempt.py rows
  record_attempt.py infer --head-ref R --authors a,b
  record_attempt.py stats

Implementer is one of: cursor-cloud, codex-cli, claude-cli, human, unknown.
Never guess. If the evidence does not name a builder, store unknown.
A personal GitHub login alone is not evidence of who implemented the PR.

Routing: after 7 days of data and at least 5 PRs per builder, route the next
build in that repo and blast tier to the builder with the higher first-try
pass percent. Until that bar is met, use the default builder and reviewers
from config.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import factory_paths  # noqa: E402

IMPLEMENTERS = ("cursor-cloud", "codex-cli", "claude-cli", "human", "unknown")
FIELDS = [
    "time", "repo", "pr", "issue", "implementer", "attempt_no",
    "acceptance_test_pass_first_try", "review_l1", "review_l2", "blast_tier",
    "merged", "merged_by", "reverted", "minutes_open_to_merge",
    "minutes_merge_to_live", "portback_status", "note",
]
BC_RE = re.compile(
    r"bc-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I
)
ISSUE_RE = re.compile(r"\b([A-Z]{2,10}-\d+)\b")
CURSOR_BOT = {"cursoragent", "cursor[bot]", "cursor-agent"}
CODEX_BOT = {"codex", "chatgpt-codex", "openai-codex"}
CLAUDE_BOT = {"claude", "claude[bot]", "claude-code"}


def _jsonl():
    return os.path.join(factory_paths.ledger_dir(), "attempts.jsonl")


def now_stamp():
    return dt.datetime.now(factory_paths.tz()).replace(microsecond=0).isoformat()


def parse_time(s):
    if not s:
        return None
    if isinstance(s, dt.datetime):
        t = s
    else:
        t = dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    zone = factory_paths.tz()
    if t.tzinfo is None:
        t = t.replace(tzinfo=zone)
    return t.astimezone(zone)


def minutes_between(start, end):
    a, b = parse_time(start), parse_time(end)
    if not a or not b:
        return None
    return round((b - a).total_seconds() / 60, 1)


def infer_implementer(meta: dict) -> tuple[str, list[str]]:
    """Return (implementer, evidence tags). Never guesses."""
    ev = []
    head = (meta.get("head_ref") or meta.get("headRefName") or "") or ""
    authors = {str(a).lower() for a in (meta.get("commit_authors") or []) if a}
    for a in meta.get("commit_heads") or []:
        for name in a.get("authors") or []:
            if name:
                authors.add(str(name).lower())
    login = (meta.get("author_login") or (meta.get("author") or {}).get("login") or "") or ""
    body = meta.get("body") or ""
    blob = " ".join([
        head, login, body,
        " ".join(authors),
        json.dumps(meta.get("issue_comments") or [], default=str),
        json.dumps(meta.get("notes") or ""),
    ])

    if head.startswith("cursor/") or "CURSOR_AGENT_PR_BODY" in body or "cursor.com/agents/bc-" in body:
        ev.append("cursor-branch-or-pr-body")
    if authors & CURSOR_BOT or login.lower() in CURSOR_BOT:
        ev.append("cursoragent-author")
    if BC_RE.search(body) or BC_RE.search(blob):
        ev.append("cloud-agent-id")
    if ev:
        return "cursor-cloud", ev

    if head.startswith("codex/") or authors & CODEX_BOT or login.lower() in CODEX_BOT:
        ev.append("codex-branch-or-author")
        return "codex-cli", ev
    if head.startswith("claude/") or authors & CLAUDE_BOT or login.lower() in CLAUDE_BOT:
        ev.append("claude-branch-or-author")
        return "claude-cli", ev

    explicit = (meta.get("implementer") or "").strip()
    if explicit in IMPLEMENTERS and explicit != "unknown":
        ev.append("explicit-field")
        return explicit, ev
    if re.search(r"\bimplementer:\s*human\b", blob, re.I) or meta.get("implementer_human") is True:
        ev.append("explicit-human")
        return "human", ev
    return "unknown", ev


def issue_from_text(*parts):
    for p in parts:
        if not p:
            continue
        m = ISSUE_RE.search(str(p))
        if m:
            return m.group(1)
    return None


def portback_status(text: str):
    t = (text or "").strip()
    if not t:
        return None
    u = t.upper()
    if u.startswith("LIVE"):
        return "LIVE"
    if u.startswith("NOT LIVE") or u.startswith("NOT_LIVE"):
        return "NOT_LIVE"
    if u.startswith("DEPLOYED"):
        return "DEPLOYED"
    if u.startswith("N/A"):
        return "n/a"
    if u.startswith("PENDING"):
        return "pending"
    return None


def append(row: dict) -> dict:
    """Append one attempt row. Never edits or deletes earlier rows."""
    path = _jsonl()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    rec = {k: row.get(k) for k in FIELDS}
    rec.update({k: v for k, v in row.items() if k not in rec})
    if rec.get("time_local") and not rec.get("time"):
        rec["time"] = rec["time_local"]
    if not rec.get("time"):
        rec["time"] = now_stamp()
    rec["repo"] = rec.get("repo") or ""
    impl = rec.get("implementer") or "unknown"
    if impl not in IMPLEMENTERS:
        rec["implementer"] = "unknown"
        rec["note"] = ((rec.get("note") or "") + f" implementer {impl!r} rejected, stored as unknown").strip()
    else:
        rec["implementer"] = impl
    if rec.get("attempt_no") in (None, ""):
        rec["attempt_no"] = 1
    rec["attempt_no"] = int(rec["attempt_no"])
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=False) + "\n")
    return rec


def rows(path=None):
    p = path or _jsonl()
    if not os.path.exists(p):
        return []
    out = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def existing_keys(path=None):
    keys = set()
    for r in rows(path):
        keys.add((r.get("repo") or "", int(r.get("pr") or 0), int(r.get("attempt_no") or 0)))
    return keys


def latest_by_pr(rs=None):
    """Last row for each (repo, pr). Later lines win."""
    out = {}
    for r in (rs if rs is not None else rows()):
        out[(r.get("repo") or "", int(r.get("pr") or 0))] = r
    return out


def attempts_for_pr(rs, repo, pr):
    repo, pr = repo or "", int(pr)
    return [r for r in rs if (r.get("repo") or "") == repo and int(r.get("pr") or 0) == pr]


def builder_stats(rs, now=None, days=7):
    """Per-implementer stats over the window. One PR counted once (latest row)."""
    now = now or dt.datetime.now(factory_paths.tz())
    since = now - dt.timedelta(days=days)
    in_window = []
    for r in rs:
        t = parse_time(r.get("time") or r.get("time_local"))
        if t and since <= t <= now:
            in_window.append(r)
    by_pr = {}
    for r in in_window:
        by_pr[(r.get("repo") or "", int(r.get("pr") or 0))] = r
    groups = {}
    for _key, r in by_pr.items():
        impl = r.get("implementer") or "unknown"
        groups.setdefault(impl, []).append(r)
    order = [i for i in IMPLEMENTERS if i in groups] + [i for i in groups if i not in IMPLEMENTERS]
    out = []
    for impl in order:
        items = groups[impl]
        firsts = [r.get("acceptance_test_pass_first_try") for r in items
                  if r.get("acceptance_test_pass_first_try") is not None]
        attempts = [int(r.get("attempt_no") or 1) for r in items]
        catches = []
        for r in items:
            s = 0
            known = False
            for k in ("review_l1", "review_l2"):
                if r.get(k) is not None:
                    known = True
                    v = r.get(k)
                    if isinstance(v, str) and "=" in v:
                        s += sum(int(n) for _lbl, n in re.findall(r"(BLOCKER|MAJOR)=(\d+)", v))
                    else:
                        try:
                            s += int(v or 0)
                        except (TypeError, ValueError):
                            pass
            if known:
                catches.append(s)
        lives = [r.get("minutes_merge_to_live") for r in items
                 if isinstance(r.get("minutes_merge_to_live"), (int, float))]
        reverts = sum(1 for r in items if r.get("reverted") is True)
        out.append({
            "implementer": impl,
            "prs": len(items),
            "first_try_n": len(firsts),
            "first_try_pass_pct": (round(100.0 * sum(1 for x in firsts if x) / len(firsts)) if firsts else None),
            "avg_attempts": round(sum(attempts) / len(attempts), 1) if attempts else None,
            "reviewer_catches": (sum(catches) if catches else None),
            "reverts": reverts,
            "median_minutes_to_live": (round(statistics.median(lives), 1) if lives else None),
        })
    return out


def routing_ready(stats, min_days=7, min_prs=5) -> bool:
    builders = [s for s in stats if s["implementer"] in ("cursor-cloud", "codex-cli", "claude-cli")]
    if len(builders) < 2:
        return False
    return all(s["prs"] >= min_prs for s in builders)


def _fmt_num(x):
    if x is None:
        return None
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return str(x)


def format_builders(stats, routing_line=True):
    lines = ["## D. Builders (last 7 days)", ""]
    if routing_line:
        lines.append(
            "Routing: after 7 days and 5+ PRs per builder, pick by first-try pass "
            "percent within each repo and tier. Until then, use the default builder "
            "and reviewers from config."
        )
        lines.append("")
    if not stats:
        lines.append("No attempt rows in the 7-day window.")
        return "\n".join(lines)
    for s in stats:
        ft = (
            f"{s['first_try_pass_pct']}% first-try ({s['first_try_n']} scored)"
            if s["first_try_pass_pct"] is not None else "first-try n/a"
        )
        catches = (
            f"{s['reviewer_catches']} reviewer catches"
            if s["reviewer_catches"] is not None else "reviewer catches n/a"
        )
        live = (
            f"median time to live {_fmt_num(s['median_minutes_to_live'])} min"
            if s["median_minutes_to_live"] is not None else "median time to live n/a"
        )
        avg = _fmt_num(s["avg_attempts"])
        rev = f"{s['reverts']} revert" + ("" if s["reverts"] == 1 else "s")
        lines.append(
            f"- {s['implementer']}: {s['prs']} PRs, {ft}, avg {avg} attempts, "
            f"{catches}, {rev}, {live}"
        )
    return "\n".join(lines)


def _cli_append(argv):
    if not sys.stdin.isatty():
        raw = sys.stdin.read().strip()
        if raw:
            row = json.loads(raw)
            print(json.dumps(append(row)))
            return

    def flag(name, default=None):
        return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else default

    def bflag(name):
        v = flag(name)
        if v is None:
            return None
        return v.lower() in ("1", "true", "yes")

    row = {
        "repo": flag("--repo"),
        "pr": int(flag("--pr") or 0) or None,
        "issue": flag("--issue"),
        "implementer": flag("--implementer", "unknown"),
        "attempt_no": int(flag("--attempt") or 1),
        "acceptance_test_pass_first_try": bflag("--first-try"),
        "review_l1": (int(flag("--review-l1")) if flag("--review-l1") is not None else None),
        "review_l2": (int(flag("--review-l2")) if flag("--review-l2") is not None else None),
        "blast_tier": flag("--blast"),
        "merged": bflag("--merged"),
        "merged_by": flag("--merged-by"),
        "reverted": bflag("--reverted") or False,
        "minutes_open_to_merge": (float(flag("--open-min")) if flag("--open-min") else None),
        "minutes_merge_to_live": (float(flag("--live-min")) if flag("--live-min") else None),
        "portback_status": flag("--portback"),
        "note": flag("--note"),
        "time": flag("--time"),
    }
    if not row["repo"] or not row["pr"]:
        print("record_attempt append needs --repo and --pr, or a JSON row on stdin", file=sys.stderr)
        sys.exit(2)
    print(json.dumps(append(row)))


def main():
    a = sys.argv[1:]
    cmd = a[0] if a else ""
    if cmd in ("", "-h", "--help"):
        print(__doc__)
        return
    if cmd == "append":
        _cli_append(a[1:])
        return
    if cmd == "rows":
        for r in rows():
            print(json.dumps(r))
        return
    if cmd == "infer":
        def flag(name):
            return a[a.index(name) + 1] if name in a and a.index(name) + 1 < len(a) else None
        authors = [x for x in (flag("--authors") or "").split(",") if x]
        meta = {
            "head_ref": flag("--head-ref") or "",
            "author_login": flag("--login") or "",
            "commit_authors": authors,
            "body": flag("--body") or "",
            "implementer": flag("--implementer") or "",
        }
        impl, ev = infer_implementer(meta)
        print(json.dumps({"implementer": impl, "evidence": ev}))
        return
    if cmd == "stats":
        print(json.dumps(builder_stats(rows()), indent=2))
        return
    print(__doc__)
    sys.exit(1)


if __name__ == "__main__":
    main()
