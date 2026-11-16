#!/usr/bin/env python3
"""Port a merged factory PR into the live copy.

A merged PR reaches live code only after a shadow run passes on the same
merge commit. This tool never merges.

Usage:
  portback.py plan   <owner/name> <pr>
  portback.py shadow <owner/name> <pr> [--env K=V ...]
  portback.py apply  <owner/name> <pr> --execute [--env K=V]

plan is read-only. shadow copies live files to a temp tree, applies the PR
diff, and runs the PR tests with no network and no sends. apply needs a
shadow PASS for the same merge SHA. It backs up each live file as
<file>.bak-YYYYMMDD-pr-N before writing.

Set PORTBACK_LIVE to the live root (default: $FACTORY_ROOT/live).
Optional strip prefixes and exclude patterns live in config.json under
portback.strip_prefixes and portback.exclude.
Never ports secrets, keys, env files, or .github workflows.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import factory_paths  # noqa: E402

BIN = os.path.dirname(os.path.abspath(__file__))
GH = os.getenv("PORTBACK_GH") or os.path.join(BIN, "factory_gh.sh")
DEFAULT_EXCLUDE = [
    r"(^|/)\.[^/]*key[^/]*$",
    r"(^|/)\.env",
    r"secret",
    r"token",
    r"^\.github/",
    r"(^|/)MANIFEST\.json$",
    r"(^|/)private-key",
]
TEST_RE = re.compile(r"(^|/)tests?/|(^|/)test_[^/]+\.py$")


def sh(*a, cwd=None, env=None, check=True):
    return subprocess.run(list(a), cwd=cwd, env=env, check=check, capture_output=True, text=True)


def gh(*a):
    return sh(GH, *a).stdout


def now():
    return dt.datetime.now(factory_paths.tz()).isoformat(timespec="seconds")


def portback_cfg():
    return factory_paths.load_config().get("portback") or {}


def live_root():
    return os.getenv("PORTBACK_LIVE") or portback_cfg().get("live_root") or os.path.join(factory_paths.factory_root(), "live")


def proofs_dir():
    return os.getenv("PORTBACK_PROOFS") or os.path.join(factory_paths.proofs_dir(), "portback")


def kill_path():
    return os.getenv("PORTBACK_KILL") or factory_paths.kill_file()


def exclude_patterns():
    extra = portback_cfg().get("exclude") or []
    return DEFAULT_EXCLUDE + list(extra)


def excluded(p):
    return any(re.search(x, p, re.I) for x in exclude_patterns())


def live_path(p):
    rel = p
    for prefix in portback_cfg().get("strip_prefixes") or []:
        if rel.startswith(prefix):
            rel = rel[len(prefix):]
            break
    return os.path.join(live_root(), rel)


def repo_slug(repo):
    if "/" not in repo:
        raise SystemExit("portback needs a repo as owner/name")
    return repo


def pr_info(repo, pr):
    repo = repo_slug(repo)
    j = json.loads(gh(
        "pr", "view", str(pr), "-R", repo, "--json",
        "number,state,mergedAt,mergedBy,mergeCommit,headRefOid,files,url,title",
    ))
    j["files"] = [f["path"] for f in j["files"]]
    return j


def plan(repo, pr):
    j = pr_info(repo, pr)
    rows = []
    for p in j["files"]:
        lp = live_path(p)
        rows.append({
            "path": p,
            "live": lp,
            "excluded": excluded(p),
            "test": bool(TEST_RE.search(p)),
            "live_exists": os.path.exists(lp),
        })
    return j, rows


def write_proof(name, rec):
    d = proofs_dir()
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    return p


def apply_diff(diff, tree, rows, skip_tests=False):
    """Apply only ported files' hunks to tree with a 3-way fallback."""
    keep = {r["path"] for r in rows if not r["excluded"] and (not skip_tests or not r["test"])}
    prefixes = portback_cfg().get("strip_prefixes") or []
    parts = re.split(r"(?m)^(?=diff --git )", diff)
    out = []
    for part in parts:
        m = re.match(r"diff --git a/(\S+) b/(\S+)", part)
        if m and m.group(2) in keep:
            text = part
            for prefix in prefixes:
                text = text.replace(prefix, "")
            out.append(text)
    patch = "".join(out)
    if not patch:
        return True, "nothing to apply"
    pf = os.path.join(tree, ".portback.patch")
    with open(pf, "w", encoding="utf-8") as f:
        f.write(patch)
    if not os.path.isdir(os.path.join(tree, ".git")):
        sh("git", "init", "-q", cwd=tree)
        sh("git", "add", "-A", cwd=tree)
        sh("git", "-c", "user.email=" + "factory" + "@" + "example.test", "-c", "user.name=factory",
           "commit", "-qm", "base", "--allow-empty", cwd=tree)
    r = sh("git", "apply", "--3way", "--whitespace=nowarn", ".portback.patch", cwd=tree, check=False)
    os.remove(pf)
    return r.returncode == 0, (r.stdout + r.stderr)[-2000:]


def run_tests(tree, rows, extra_env):
    env = dict(os.environ, NO_NETWORK="1", PYTHONDONTWRITEBYTECODE="1", FACTORY_NO_SEND="1")
    env.pop("GH_TOKEN", None)
    env.pop("GITHUB_TOKEN", None)
    env.update(extra_env)
    res = []
    for r in rows:
        if not r["test"] or not r["path"].endswith(".py"):
            continue
        rel = r["path"]
        for prefix in portback_cfg().get("strip_prefixes") or []:
            if rel.startswith(prefix):
                rel = rel[len(prefix):]
        p = os.path.join(tree, rel)
        if not os.path.exists(p):
            res.append({"test": rel, "ok": False, "out": "missing in shadow tree"})
            continue
        x = subprocess.run([sys.executable, p], cwd=tree, env=env, capture_output=True, text=True, timeout=600)
        res.append({"test": rel, "ok": x.returncode == 0, "rc": x.returncode, "out": (x.stdout + x.stderr)[-1500:]})
    return res


def shadow(repo, pr, extra_env):
    j, rows = plan(repo, pr)
    sha = (j.get("mergeCommit") or {}).get("oid") or j["headRefOid"]
    diff = gh("pr", "diff", str(pr), "-R", repo_slug(repo))
    tree = tempfile.mkdtemp(prefix=f"portback-{pr}-")
    live = live_root()
    for r in rows:
        if r["excluded"]:
            continue
        src_dir = os.path.dirname(r["live"])
        rel_dir = os.path.relpath(src_dir, live)
        dst = os.path.join(tree, rel_dir)
        if os.path.isdir(src_dir) and not os.path.exists(dst):
            shutil.copytree(src_dir, dst, ignore=shutil.ignore_patterns("*.bak*", "__pycache__", ".*key*", "*.env"))
    ok_apply, apply_log = apply_diff(diff, tree, rows)
    portable = [r for r in rows if not r["excluded"] and not r["test"]]
    tests = run_tests(tree, rows, extra_env) if ok_apply else []
    if j["state"] != "MERGED":
        ok = False
        why = "PR not merged"
    elif not ok_apply:
        ok = False
        why = "apply failed"
    elif portable and (not tests or not all(t["ok"] for t in tests)):
        ok = False
        why = "tests failed or no tests"
    else:
        ok = True
        why = None
    rec = {
        "kind": "shadow", "repo": repo, "pr": pr, "sha": sha, "state": j["state"],
        "at": now(), "env": extra_env, "apply_ok": ok_apply, "apply_log": apply_log,
        "tests": tests, "excluded": [r["path"] for r in rows if r["excluded"]],
        "verdict": "PASS" if ok else "FAIL", "why_not_pass": why, "shadow_tree": tree,
    }
    print(json.dumps({
        "verdict": rec["verdict"], "why_not_pass": why, "sha": sha, "apply_ok": ok_apply,
        "tests": [(t["test"], t["ok"]) for t in tests],
    }, indent=1))
    print("proof:", write_proof(f"{repo.replace('/', '-')}-pr{pr}-shadow-{sha[:10]}.json", rec))
    return rec


def apply_live(repo, pr, extra_env):
    j, rows = plan(repo, pr)
    if j["state"] != "MERGED":
        sys.exit("REFUSED: PR is not merged")
    sha = j["mergeCommit"]["oid"]
    proof = os.path.join(proofs_dir(), f"{repo.replace('/', '-')}-pr{pr}-shadow-{sha[:10]}.json")
    if not os.path.exists(proof) or json.load(open(proof, encoding="utf-8")).get("verdict") != "PASS":
        sys.exit(f"REFUSED: no shadow PASS for merge {sha[:10]} ({proof})")
    if os.path.exists(kill_path()):
        sys.exit("REFUSED: KILL file present")
    stamp = dt.datetime.now(factory_paths.tz()).strftime("%Y%m%d")
    backups = []
    for r in rows:
        if r["excluded"] or r["test"]:
            continue
        if os.path.exists(r["live"]):
            b = f"{r['live']}.bak-{stamp}-pr-{pr}"
            shutil.copy2(r["live"], b)
            backups.append(b)
    diff = gh("pr", "diff", str(pr), "-R", repo_slug(repo))
    live_rows = [r for r in rows if not r["test"]]
    tmp = tempfile.mkdtemp(prefix="portback-live-")
    live = live_root()
    for r in live_rows:
        if r["excluded"]:
            continue
        rel = os.path.relpath(r["live"], live)
        d = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        if os.path.exists(r["live"]):
            shutil.copy2(r["live"], d)
    ok, log = apply_diff(diff, tmp, live_rows, skip_tests=True)
    if not ok:
        print(log)
        sys.exit("REFUSED: patch does not apply to live; live untouched (backups kept)")
    changed = []
    for r in live_rows:
        if r["excluded"]:
            continue
        rel = os.path.relpath(r["live"], live)
        s = os.path.join(tmp, rel)
        if os.path.exists(s):
            os.makedirs(os.path.dirname(r["live"]), exist_ok=True)
            shutil.copy2(s, r["live"])
            changed.append(r["live"])
    rec = {
        "kind": "live_apply", "repo": repo, "pr": pr, "sha": sha, "at": now(),
        "changed": changed, "backups": backups, "env_to_set": extra_env,
        "rollback": "copy each .bak-YYYYMMDD-pr-N file back over its live file",
    }
    print("proof:", write_proof(f"{repo.replace('/', '-')}-pr{pr}-live-{sha[:10]}.json", rec))
    print(json.dumps(rec, indent=1))


def main():
    a = sys.argv[1:]
    if len(a) < 3:
        print(__doc__)
        sys.exit(1)
    cmd, repo, pr = a[0], a[1], a[2]
    env = dict(x.split("=", 1) for i, x in enumerate(a) if i > 0 and a[i - 1] == "--env")
    if cmd == "plan":
        j, rows = plan(repo, pr)
        print(json.dumps({
            "pr": pr, "state": j["state"], "title": j["title"],
            "merged_by": (j.get("mergedBy") or {}).get("login"), "files": rows,
        }, indent=1))
    elif cmd == "shadow":
        shadow(repo, pr, env)
    elif cmd == "apply":
        if "--execute" not in a:
            sys.exit("dry run only: add --execute")
        apply_live(repo, pr, env)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
