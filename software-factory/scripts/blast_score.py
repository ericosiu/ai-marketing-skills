#!/usr/bin/env python3
"""Deterministic blast-radius scorer for a unified diff.

Reads a unified diff (file arg or stdin). Prints LOW, MEDIUM or HIGH plus a
color (green, yellow or red), a review level and the rules that hit.

Default HIGH (red) when unsure. Reviewers may only raise this score.
Nothing may lower it.

Usage:
  blast_score.py [diff.patch] [--repo owner/name]
"""
from __future__ import annotations

import json
import re
import sys

HIGH_PATH = re.compile(
    r"(send|publish|gate|ledger|receipt|routine|schedule|cron|"
    r"secret|auth|token|credential|billing|spend|deploy|release|suppression|"
    r"conftest\.py|"
    r"\.github/|workflows/|gitlab-ci|Jenkinsfile|azure-pipelines|\.circleci|"
    r"travis\.yml|CODEOWNERS|AGENTS\.md|CLAUDE\.md|SKILL\.md|prompt|"
    r"stripe|invoice|payment|checkout|subscription|payout|refund|pricing|"
    r"oauth|rbac|\.env|calendars?|"
    r"migrat|alembic|prisma|schemas?|backfill|"
    r"\bpii\b|data.?export|"
    r"Dockerfile|docker-compose|\.tfvars$|\.tf$|terraform|\bhelm\b|\bk8s\b|"
    r"kubernetes|\becs\b|release\.sh|"
    r"package-lock|yarn\.lock|pnpm-lock|poetry\.lock|Pipfile|"
    r"requirements[^/]*\.txt|Gemfile|go\.sum|go\.mod|Cargo\.(lock|toml)|"
    r"composer\.(lock|json)|bun\.lock|package\.json|pyproject\.toml)",
    re.I,
)
HIGH_TEXT = {
    "sends": r"(send|sent|\bemails?\b|smtplib|gmail|slack.?post|chat\.postMessage|"
             r"post_tweet|\bsms\b|\bdms?\b|direct.?message|twilio)",
    "publish": r"\b(publish|go.?live|upload|vercel|--prod|create_posts)\b",
    "payments": r"\b(spend|budget|payment|invoice|billing|charge|purchase|"
                r"top.?up|stripe|refund|payout|subscription|pricing|checkout|"
                r"credit.?cards?|debit.?cards?|card.?number|payment.?card|"
                r"\bcards?\b|\bbanks?\b|bank.?account)\b",
    "gates": r"\b(do.not.contact|dedupe|unsubscribe|consent|suppression|"
             r"send.?caps?|daily.?caps?|rate.?caps?)\b",
    "secrets_auth": r"\b(secret|token|api.?key|password|credential|oauth|bearer|"
                    r"\.env|ssh|login|auth|hosts\.yml|sessions?|rbac|"
                    r"role.?based|\broles?\b|permissions?|\bacl\b)\b",
    "data_schema": r"\b(migrations?|schemas?|drop table|\bDROP\b|\bTRUNCATE\b|"
                   r"truncate|backfill|prod.?database|alembic|prisma)\b",
    "pii_export": r"\b(pii|personally.?identif|data.?export|export.?csv|"
                  r"export.?users?|csv.?export|gdpr|\bssn\b|social.?security|"
                  r"passport|date.?of.?birth|phone.?numbers?)\b",
    "deletes": r"\b(delete[ds]?|rm -rf|drop table|purge[ds]?|truncate|unlink|pause[ds]?)\b",
    "routines": r"\b(routine|cron|hourly|watchdog|schedule)\b",
    "egress": r"(requests\.(post|put|patch|delete)|urllib|urlopen|os\.system|"
              r"subprocess|base64|curl|git push|gh.{0,24}pr.{0,24}merge)",
    "infra": r"\b(Dockerfile|docker-compose|terraform|\.tfvars\b|\becs\b|"
             r"kubernetes|\bk8s\b|helm|release\.sh)\b",
}
LOW_PATH = re.compile(r"(^docs/.*\.(md|txt|rst)$|\.md$|/reports?/)", re.I)
EXEC_PATH = re.compile(r"\.(py|sh|bash|zsh|js|ts|mjs|cjs|rb|go|rs)$", re.I)
PY_PATH = re.compile(r"\.py$", re.I)
TEST_PATH = re.compile(r"(^tests?/|test_[^/]*\.py$|_test\.py$)", re.I)


def _is_high_path(path: str) -> bool:
    return bool(HIGH_PATH.search(path or ""))


def _is_clearly_low_path(path: str) -> bool:
    if not path or _is_high_path(path) or EXEC_PATH.search(path):
        return False
    return bool(LOW_PATH.search(path))


def annotate(tier: str, repo: str = ""):
    """Color, review level and merge rule for a scored tier.

    green / LOW: AI review L1 plus tests. May be auto-merged if every other gate passes.
    yellow / MEDIUM: AI L2 (two reviewers, tests, security scan) plus a human merge.
    red / HIGH: human review and human merge. Never auto-merge.
    """
    del repo  # reserved for a per-repo reviewer map in config
    if tier == "LOW":
        return {
            "color": "green",
            "review_level": "AI L1",
            "review": "AI review L1 plus tests",
            "merge": "operator, or auto-merge under the configured cap and gates",
            "auto_merge_eligible": True,
            "reviewer": "operator",
        }
    if tier == "MEDIUM":
        return {
            "color": "yellow",
            "review_level": "AI L2",
            "review": "AI L2 (two reviewers, tests, security scan) plus a human merge",
            "merge": "human merge",
            "auto_merge_eligible": False,
            "reviewer": "owner",
        }
    return {
        "color": "red",
        "review_level": "human",
        "review": "human review and human merge, never auto-merge",
        "merge": "human review and human merge, never auto-merge",
        "auto_merge_eligible": False,
        "reviewer": "owner",
    }


def score(diff: str):
    if not isinstance(diff, str) or not diff.strip():
        return "HIGH", ["H0:default_high:empty_or_unparseable"]

    files, hits, med, added, removed_tests = {}, [], [], 0, False
    cur = None
    saw_git_header = False
    for line in diff.splitlines():
        if line.startswith("diff --git"):
            saw_git_header = True
            cur = line.split(" b/")[-1]
            files[cur] = {
                "deleted": False, "new": False, "rename_from": None,
                "rename_to": None, "mode_change": False,
            }
        elif line.startswith("rename from ") and cur:
            files[cur]["rename_from"] = line[len("rename from "):]
        elif line.startswith("rename to ") and cur:
            files[cur]["rename_to"] = line[len("rename to "):]
        elif line.startswith("deleted file") and cur:
            files[cur]["deleted"] = True
        elif line.startswith("new file") and cur:
            files[cur]["new"] = True
        elif (line.startswith("old mode") or line.startswith("new mode")) and cur:
            files[cur]["mode_change"] = True
        elif line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
            added += 1
            body = line[1:]
            for k, pat in HIGH_TEXT.items():
                if re.search(pat, body, re.I):
                    hits.append(f"H6:{k}:{cur}")
            if line.startswith("-") and re.search(r"\bassert\b|def test_", body) and cur and re.search(r"test", cur, re.I):
                removed_tests = True

    if not saw_git_header:
        return "HIGH", ["H0:default_high:unparseable"]

    if removed_tests:
        hits.append("H9:removed_test_or_assert")
    if added > 500 or len(files) > 20:
        hits.append("H8:size")

    for f, m in files.items():
        paths = [p for p in (f, m.get("rename_from"), m.get("rename_to")) if p]
        for p in paths:
            if _is_high_path(p):
                hits.append(f"H5:path:{p}")
            if PY_PATH.search(p):
                med.append(f"M6:py:{p}")
        if m["deleted"]:
            hits.append(f"H4:delete:{f}")
        src, dst = m.get("rename_from"), m.get("rename_to") or f
        if src:
            if any(_is_high_path(p) or TEST_PATH.search(p) or PY_PATH.search(p) for p in (src, dst)):
                hits.append(f"H10:rename:{src}->{dst}")
            else:
                med.append(f"M7:rename:{src}->{dst}")
        if m["mode_change"]:
            if any(_is_high_path(p) for p in paths):
                hits.append(f"H11:mode:{f}")
            else:
                med.append(f"M8:mode:{f}")
        if m["new"] and not _is_clearly_low_path(f):
            med.append(f"M2:new_file:{f}")
        if not _is_clearly_low_path(f) and not m["mode_change"] and not src:
            if not _is_high_path(f):
                med.append(f"M:non_low_path:{f}")
        if re.search(r"test|eval|check", f, re.I) and not m["new"] and not m["mode_change"] and not src:
            med.append(f"M3:edits_test_or_checker:{f}")

    if added > 120 or len(files) > 5:
        med.append("M5:size")

    if hits:
        return "HIGH", sorted(set(hits))
    if med:
        return "MEDIUM", sorted(set(med))

    if files and all(
        _is_clearly_low_path(f) and not m["mode_change"] and not m.get("rename_from") and not m["deleted"]
        for f, m in files.items()
    ):
        return "LOW", []
    return "HIGH", ["H0:default_high"]


def report(diff: str, repo: str = ""):
    tier, why = score(diff)
    out = {"tier": tier, "rules": why}
    out.update(annotate(tier, repo))
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    repo = ""
    path = None
    i = 0
    while i < len(args):
        if args[i] in ("--repo", "--lane") and i + 1 < len(args):
            repo = args[i + 1]
            i += 2
        else:
            path = args[i]
            i += 1
    text = open(path, encoding="utf-8").read() if path else sys.stdin.read()
    print(json.dumps(report(text, repo)))
