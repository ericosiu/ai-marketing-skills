#!/usr/bin/env python3
"""Auto-merge gate for blast:low pull requests.

Usage:
  automerge.py check <pr> --repo owner/name
  automerge.py merge <pr> --repo owner/name --execute
  automerge.py scan [--execute]
  automerge.py watch [--execute]

The script enforces every gate itself at one pinned head SHA. GitHub rulesets
can be bypassed by an admin token, so this tool never uses admin rights.

Gates:
  no KILL file; auto-merge enabled and state ARMED; repo in scope and not in
  a draft-only lane; weekday not in no_merge_days; auto-merges today under
  max_per_day (default 2); PR open, not draft, mergeable; label blast:low and
  no higher blast label; blast_score.py says LOW on the PR diff and on the
  compare diff base...sha; every required check is success at that SHA; a repo
  with zero required checks fails closed; no check at that SHA is pending or
  failing; the GitHub App (contents and pull-requests only) is staged.

Merge: REST PUT pulls/<n>/merge with sha=<pinned sha> and merge_method=squash.
Never pass an admin flag. Before the PUT, the PR is read again. Head SHA and
labels must be unchanged.

Every merge and every revert appends a row to the merge ledger.
PRs that pass every gate but hit the cap or a blocked weekday go to the daily
card, ranked P0 down.
On a red check after an auto-merge, watch disables auto-merge and opens a
revert PR. Only the owner re-enables auto-merge.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import factory_ledger  # noqa: E402
import factory_paths  # noqa: E402
from blast_score import score  # noqa: E402

BIN = os.path.dirname(os.path.abspath(__file__))
FACTORY_GH = os.environ.get("FACTORY_GH") or os.path.join(BIN, "factory_gh.sh")
BOT_ENV = os.environ.get("FACTORY_GH_ENV", os.path.expanduser("~/.config/factory/github-bot.env"))
APP_DIR = os.environ.get("FACTORY_GH_APP_DIR", os.path.expanduser("~/.config/factory/github-app"))
OK_CONCLUSIONS = {"success", "neutral", "skipped"}
CAP_GATES = {"under_daily_cap", "not_blocked_weekday"}
RED_CONCLUSIONS = {"failure", "timed_out", "cancelled", "action_required"}
RED_STATES = {"failure", "error"}


def gh(*a):
    return subprocess.run([FACTORY_GH, *a], check=True, capture_output=True, text=True).stdout


def cfg():
    return factory_paths.load_config()


def save_cfg(c):
    path = factory_paths.config_path()
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(c, f, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def now():
    return dt.datetime.now(factory_paths.tz())


def automerge_cfg(c=None):
    return (c or cfg()).get("automerge") or (c or cfg()).get("automerge_low") or {}


def repos_in_scope(am):
    rs = am.get("repos") or ([am["repo"]] if am.get("repo") else [])
    return [r for r in rs if r]


def draft_only_repos(c=None):
    c = c or cfg()
    lanes = (c.get("lanes") or {}).get("draft_only") or {}
    if lanes.get("enabled") is False:
        return []
    return list(lanes.get("repos") or [])


def log_paths():
    proofs = factory_paths.proofs_dir()
    return (
        os.path.join(proofs, "automerge-log.jsonl"),
        os.path.join(proofs, "automerge-watched.json"),
    )


def auto_merges_today():
    today = now().date().isoformat()
    n = sum(
        1 for r in factory_ledger.rows()
        if r.get("event") == "merged" and r.get("merged_by") == "auto"
        and factory_ledger.row_time(r)[:10] == today
    )
    log, _watched = log_paths()
    if os.path.exists(log):
        extra = 0
        with open(log, encoding="utf-8") as f:
            for line in f:
                x = json.loads(line)
                if x.get("action") == "merged" and x.get("date") == today:
                    extra += 1
        n = max(n, extra)
    return n


def armed_reason(c):
    """None when armed. Fails closed on any doubt."""
    try:
        am = automerge_cfg(c)
    except Exception as e:
        return f"config unreadable: {e}"
    if factory_paths.kill_present(c):
        return "KILL file present"
    if am.get("enabled") is not True:
        return "enabled is not true"
    if am.get("state") != "ARMED":
        return f"state is {am.get('state')!r}, not ARMED"
    return None


def _mode600(path):
    return oct(os.stat(path).st_mode & 0o777) == "0o600"


def identity_ready():
    """App credentials preferred. A bot env file is a fallback."""
    app_id = os.path.join(APP_DIR, "app-id")
    pem = os.path.join(APP_DIR, "private-key.pem")
    if os.path.isfile(app_id) and os.path.isfile(pem):
        for path in (app_id, pem):
            if not _mode600(path):
                return False, f"{path} is not mode 600"
        return True, "github-app"
    if os.path.isfile(BOT_ENV):
        if not _mode600(BOT_ENV):
            return False, f"{BOT_ENV} is not mode 600"
        return True, "staged"
    return False, (
        f"GitHub App credentials absent ({APP_DIR}) and bot token not staged ({BOT_ENV}); "
        "factory_gh.sh refuses writes (exit 6)"
    )


def configured_required_checks(repo, am):
    raw = am.get("required_checks", [])
    if isinstance(raw, dict):
        return set(raw.get(repo, []) or [])
    if repo == am.get("repo"):
        return set(raw or [])
    return set()


def required_checks(repo, base, am):
    rules = json.loads(gh("api", f"repos/{repo}/rules/branches/{base}"))
    live = {
        x["context"]
        for r in rules if r.get("type") == "required_status_checks"
        for x in (r.get("parameters") or {}).get("required_status_checks", [])
    }
    return sorted(live | configured_required_checks(repo, am))


def check_state_at(repo, sha):
    data = json.loads(gh("api", f"repos/{repo}/commits/{sha}/check-runs?per_page=100"))
    runs = data.get("check_runs", [])
    if data.get("total_count", len(runs)) > len(runs):
        raise RuntimeError(f"{data.get('total_count')} check runs, only {len(runs)} read")
    st = json.loads(gh("api", f"repos/{repo}/commits/{sha}/status"))
    statuses = {s["context"]: s["state"] for s in st.get("statuses", [])}
    return runs, statuses


def eval_checks(req, runs, statuses, sha):
    """Pure function: list of (gate, ok, info) for checks at sha."""
    out = []
    for r in runs:
        if r.get("head_sha") and r["head_sha"] != sha:
            out.append(("checks_pinned_to_sha", False, f"{r.get('name')} is for {r['head_sha'][:8]}"))
            return out
    out.append(("required_checks_present", bool(req), ",".join(req) or "none found"))
    for name in req:
        mine = [r for r in runs if r.get("name") == name]
        if mine:
            ok = all(r.get("status") == "completed" and r.get("conclusion") == "success" for r in mine)
            info = ",".join(f"{r.get('status')}/{r.get('conclusion')}" for r in mine)
        elif name in statuses:
            ok, info = statuses[name] == "success", f"status/{statuses[name]}"
        else:
            ok, info = False, "missing"
        out.append((f"check:{name}", ok, info))
    bad = [r.get("name") for r in runs if r.get("status") != "completed" or r.get("conclusion") not in OK_CONCLUSIONS]
    bad += [k for k, v in statuses.items() if v != "success"]
    out.append(("no_failing_or_pending_checks", not bad, ",".join(map(str, bad))))
    return out


def gates(pr, repo=None):
    c = cfg()
    am = automerge_cfg(c)
    scope = repos_in_scope(am)
    blocked = set(draft_only_repos(c))
    repo = repo or (scope[0] if scope else "")
    out = []

    def g(name, ok, info=""):
        out.append({"gate": name, "ok": bool(ok), "info": str(info)})

    g("no_kill_file", not factory_paths.kill_present(c), factory_paths.kill_file(c))
    g("enabled", am.get("enabled") is True)
    g("state_armed", am.get("state") == "ARMED", am.get("state"))
    g("repo_in_scope", repo in scope, f"{repo} in {scope}")
    g("not_draft_only_lane", repo not in blocked, repo)
    t = now()
    blocked_days = set(am.get("no_merge_days") or [])
    g("not_blocked_weekday", t.strftime("%A") not in blocked_days, t.strftime("%a %Y-%m-%d %H:%M"))
    cap = int(am.get("max_per_day") or 2)
    n = auto_merges_today()
    g("under_daily_cap", n < cap, f"{n}/{cap}")
    ok_id, info_id = identity_ready()
    g("write_identity_ready", ok_id, info_id)
    sha = None
    meta = {}
    try:
        p = json.loads(gh(
            "pr", "view", str(pr), "-R", repo, "--json",
            "labels,headRefOid,baseRefOid,mergeable,baseRefName,state,isDraft,title,url",
        ))
        sha = p["headRefOid"]
        labels = [l["name"] for l in p["labels"]]
        g(
            "label_blast_low",
            "blast:low" in labels and not ({"blast:medium", "blast:high"} & set(labels)),
            ",".join(labels),
        )
        g("open_not_draft", p["state"] == "OPEN" and not p["isDraft"], f"{p['state']} draft={p['isDraft']}")
        g("mergeable", p["mergeable"] == "MERGEABLE", p["mergeable"])
        t1, r1 = score(gh("pr", "diff", str(pr), "-R", repo))
        t2, r2 = score(gh(
            "api", f"repos/{repo}/compare/{p['baseRefOid']}...{sha}",
            "-H", "Accept: application/vnd.github.v3.diff",
        ))
        g("blast_score_LOW", t1 == "LOW" and t2 == "LOW", f"pr_diff={t1} {r1[:3]} pinned_diff={t2} {r2[:3]}")
        req = required_checks(repo, p["baseRefName"], am)
        runs, statuses = check_state_at(repo, sha)
        for name, ok, info in eval_checks(req, runs, statuses, sha):
            g(name, ok, info)
        meta = {
            "title": p.get("title", ""),
            "url": p.get("url", ""),
            "labels": labels,
            "checks": {x["name"]: x.get("conclusion") for x in runs} | statuses,
        }
    except Exception as e:
        g("github_reads_ok", False, f"{type(e).__name__}: {str(e)[:200]}")
    return out, sha, repo, meta


def log(rec):
    path, _watched = log_paths()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rec["date"] = now().date().isoformat()
    rec["at"] = now().isoformat()
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def do_merge(pr, repo, sha, meta):
    """Re-read the PR, then merge through the REST API pinned to sha. Never admin."""
    p = json.loads(gh("pr", "view", str(pr), "-R", repo, "--json", "headRefOid,labels"))
    if p["headRefOid"] != sha or "blast:low" not in [l["name"] for l in p["labels"]]:
        log({"action": "blocked", "repo": repo, "pr": str(pr), "reason": "head or label changed before merge"})
        return None
    res = json.loads(gh(
        "api", "-X", "PUT", f"repos/{repo}/pulls/{pr}/merge",
        "-f", f"sha={sha}", "-f", "merge_method=squash",
    ))
    merge_sha = res.get("sha", "")
    log({"action": "merged", "repo": repo, "pr": str(pr), "head": sha, "merge": merge_sha})
    factory_ledger.append({
        "event": "merged",
        "repo": repo,
        "pr": int(pr),
        "pr_url": meta.get("url", ""),
        "title": meta.get("title", ""),
        "head_sha": sha,
        "merge_sha": merge_sha,
        "merged_by": "auto",
        "blast_tier": "LOW",
        "checks": meta.get("checks", {}),
        "portback": "pending",
        "revert": "none",
    })
    return merge_sha


def priority(labels):
    for l in labels:
        m = re.match(r"^(?:priority[:/ ]?)?p([0-3])$", l.strip(), re.I)
        if m:
            return f"P{m.group(1)}"
    low = {l.lower() for l in labels}
    if "urgent" in low:
        return "P0"
    if "high" in low or "bug" in low:
        return "P1"
    return "P2"


def write_held(held):
    digest = factory_paths.digest_dir()
    os.makedirs(digest, exist_ok=True)
    path = os.path.join(digest, f"held-{now().date().isoformat()}.json")
    old = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else []
    keep = {(h["repo"], h["pr"]): h for h in old}
    for h in held:
        keep[(h["repo"], h["pr"])] = h
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sorted(keep.values(), key=lambda h: (h["priority"], h.get("created_at", ""))), f, indent=1)
    return path


def scan(execute):
    c = cfg()
    am = automerge_cfg(c)
    report, held = [], []
    reason = armed_reason(c)
    for repo in repos_in_scope(am):
        prs = json.loads(gh(
            "pr", "list", "-R", repo, "--state", "open", "--label", "blast:low",
            "--json", "number,title,url,labels,createdAt", "--limit", "50",
        ))
        for p in sorted(prs, key=lambda x: x["createdAt"]):
            res, sha, _, meta = gates(p["number"], repo)
            failed = {r["gate"] for r in res if not r["ok"]}
            item = {"repo": repo, "pr": p["number"], "head": sha, "failed": sorted(failed)}
            if not failed and execute and reason is None:
                item["merge_sha"] = do_merge(p["number"], repo, sha, meta)
            elif failed and failed <= (CAP_GATES | {"write_identity_ready"}):
                labels = [l["name"] for l in p["labels"]]
                if "under_daily_cap" in failed:
                    why = "daily cap reached"
                elif "not_blocked_weekday" in failed:
                    why = "merges blocked on this weekday"
                else:
                    why = "write identity not staged"
                held.append({
                    "repo": repo, "pr": p["number"], "url": p["url"], "title": p["title"],
                    "head": sha, "priority": priority(labels), "held_because": why,
                    "created_at": p["createdAt"],
                })
            report.append(item)
    path = write_held(held)
    print(json.dumps({"armed": reason is None, "armed_reason": reason, "results": report, "held_file": path}, indent=1))


def _disable_automerge(c, reason):
    am = automerge_cfg(c)
    am["enabled"] = False
    am["state"] = "DISARMED_BY_REVERT"
    am["disabled_reason"] = reason
    if "automerge" in c:
        c["automerge"] = am
    elif "automerge_low" in c:
        c["automerge_low"] = am
    else:
        c["automerge"] = am
    return c


def watch(execute):
    c = cfg()
    _log, watched = log_paths()
    seen = set(json.load(open(watched, encoding="utf-8"))) if os.path.exists(watched) else set()
    for r in factory_ledger.rows():
        key = f"{r.get('repo')}#{r.get('pr')}"
        if r.get("event") != "merged" or r.get("merged_by") != "auto" or key in seen or not r.get("merge_sha"):
            continue
        runs, statuses = check_state_at(r["repo"], r["merge_sha"])
        red = [x["name"] for x in runs if x.get("conclusion") in RED_CONCLUSIONS]
        red += [k for k, v in statuses.items() if v in RED_STATES]
        pending = [x["name"] for x in runs if x.get("status") != "completed"]
        pending += [k for k, v in statuses.items() if v == "pending"]
        if red:
            c = _disable_automerge(c, f"auto-revert: {key} red on main ({','.join(red)}); only the owner re-enables")
            if execute:
                save_cfg(c)
            opened = "dry run (no --execute)"
            if execute:
                pr_out = subprocess.run(
                    [FACTORY_GH, "pr", "revert", str(r["pr"]), "-R", r["repo"], "--title",
                     f"Revert #{r['pr']} (factory auto-revert: red check)"],
                    capture_output=True, text=True, check=False,
                )
                opened = pr_out.stdout.strip() or f"FAILED: {pr_out.stderr.strip()[:200]}"
            factory_ledger.append({
                "event": "revert_opened",
                "repo": r["repo"],
                "pr": r["pr"],
                "pr_url": r.get("pr_url", ""),
                "title": r.get("title", ""),
                "head_sha": r.get("head_sha", ""),
                "merge_sha": r["merge_sha"],
                "merged_by": "auto",
                "blast_tier": r.get("blast_tier", ""),
                "checks": {n: "red" for n in red},
                "portback": r.get("portback", ""),
                "revert": f"revert PR: {opened}",
                "note": "auto-merge set enabled=false; only the owner re-enables",
            })
            log({"action": "revert_opened", "repo": r["repo"], "pr": str(r["pr"]), "checks": red})
            print(json.dumps({"red": key, "checks": red, "revert": opened, "automerge": "disabled"}))
            seen.add(key)
        elif not pending:
            seen.add(key)
    os.makedirs(os.path.dirname(watched), exist_ok=True)
    json.dump(sorted(seen), open(watched, "w", encoding="utf-8"))


def arg(flag, default=None):
    a = sys.argv
    return a[a.index(flag) + 1] if flag in a and a.index(flag) + 1 < len(a) else default


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    execute = "--execute" in sys.argv
    if cmd in ("check", "merge"):
        if len(sys.argv) < 3:
            print(__doc__)
            sys.exit(1)
        pr = sys.argv[2]
        repo = arg("--repo")
        if not repo:
            print("automerge needs --repo owner/name", file=sys.stderr)
            sys.exit(2)
        if cmd == "merge" and execute:
            reason = armed_reason(cfg())
            if reason:
                print(json.dumps({"verdict": "REFUSED", "reason": f"auto-merge not armed: {reason}"}))
                sys.exit(4)
        res, sha, repo, meta = gates(pr, repo)
        ok = all(r["ok"] for r in res)
        print(json.dumps({"pr": pr, "repo": repo, "head": sha, "verdict": "PASS" if ok else "BLOCK", "gates": res}, indent=1))
        if cmd == "merge" and execute:
            if not ok:
                log({"action": "blocked", "repo": repo, "pr": pr})
                sys.exit(3)
            if not do_merge(pr, repo, sha, meta):
                sys.exit(3)
    elif cmd == "scan":
        if execute and armed_reason(cfg()):
            print(json.dumps({"verdict": "REFUSED", "reason": armed_reason(cfg())}))
            sys.exit(4)
        scan(execute)
    elif cmd == "watch":
        if execute and factory_paths.kill_present():
            print(json.dumps({"verdict": "REFUSED", "reason": "KILL file present"}))
            sys.exit(4)
        watch(execute)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
