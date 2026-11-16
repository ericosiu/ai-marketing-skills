#!/usr/bin/env python3
"""Copy live source files into a factory repo after replacing personal data
with stable hashed stand-ins.

Usage:
  scrub_snapshot.py --map map.json --names names.txt --out DIR

map.json is a dict of repo_relative_path -> live_source_path.
names.txt is one name per line. Keep that list out of the repo.

Replaces:
  listed names -> Person-<hash6>
  emails (except keep domains) -> email-<hash6>@example.test
  LinkedIn profile slugs -> a li- stand-in plus a 6-character hash

Writes MANIFEST.json with source hashes and replacement counts. Files with
repo_sha256_equals_src=false differ from live only by those stand-ins.
Port the PR diff for those files. Never copy the whole file over live.

Never copies logs, receipts, ledgers, state, proof, backups, or .bak files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
LI = re.compile(r"linkedin\.com/in/[A-Za-z0-9_%-]+")
DEFAULT_KEEP_DOMAINS = ("example.com", "example.test")
SKIP_NAME_RE = re.compile(
    r"(log|receipt|ledger|state|proof|backup|\.bak)s?$",
    re.I,
)


def stand_in(kind, s):
    return f"{kind}-{hashlib.sha256(s.lower().encode()).hexdigest()[:6]}"


def should_skip(rel, src):
    parts = Path(rel).parts + Path(src).parts
    return any(SKIP_NAME_RE.search(p) for p in parts) or rel.endswith(".bak") or src.endswith(".bak")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", required=True, help="JSON dict of repo path -> live source path")
    ap.add_argument("--names", required=True, help="One name per line. Do not commit this file.")
    ap.add_argument("--out", default=".")
    ap.add_argument("--keep-domain", action="append", default=list(DEFAULT_KEEP_DOMAINS))
    args = ap.parse_args()
    mapping = json.loads(Path(args.map).read_text(encoding="utf-8"))
    names = sorted(
        {n.strip() for n in Path(args.names).read_text(encoding="utf-8").splitlines() if n.strip()},
        key=len,
        reverse=True,
    )
    keep = tuple(d.lower() for d in args.keep_domain)
    out = Path(args.out)
    manifest = []
    for rel, src in sorted(mapping.items()):
        if should_skip(rel, src):
            print(f"skip {rel}", file=sys.stderr)
            continue
        raw = Path(src).read_bytes()
        text = raw.decode("utf-8")
        reps = {}
        for n in names:
            rx = re.compile(r"(?<![A-Za-z])" + re.escape(n) + r"(?![A-Za-z])")
            text, c = rx.subn(stand_in("Person", n), text)
            if c:
                reps["name"] = reps.get("name", 0) + c

        def em(m):
            addr = m.group(0)
            domain = addr.rsplit("@", 1)[-1].lower()
            if domain in keep:
                return addr
            reps["email"] = reps.get("email", 0) + 1
            return stand_in("email", addr) + "@example.test"

        text = EMAIL.sub(em, text)

        def li(m):
            reps["linkedin"] = reps.get("linkedin", 0) + 1
            return "linkedin.com/in/" + stand_in("li", m.group(0))

        text = LI.sub(li, text)
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text, encoding="utf-8")
        if Path(src).exists():
            shutil.copymode(src, dst)
        manifest.append({
            "path": rel,
            "src": src,
            "src_sha256": hashlib.sha256(raw).hexdigest(),
            "repo_sha256_equals_src": not reps,
            "bytes": len(raw),
            "pii_replacements": reps,
        })
    tot = {}
    for m in manifest:
        for k, v in m["pii_replacements"].items():
            tot[k] = tot.get(k, 0) + v
    (out / "MANIFEST.json").write_text(json.dumps({
        "built": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "note": (
            "Copies of live files. Names, non-kept emails and LinkedIn slugs "
            "are replaced with stable hashed stand-ins. Files with "
            "repo_sha256_equals_src=false differ from live only by those "
            "stand-ins: port back the PR delta, never the whole file."
        ),
        "totals": tot,
        "files": manifest,
    }, indent=1) + "\n", encoding="utf-8")
    print("files", len(manifest), "totals", tot)


if __name__ == "__main__":
    main()
