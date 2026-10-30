#!/usr/bin/env python3
"""Pre-publish leak check. Scans a folder for things that should not go public.

Generic patterns: emails, phone numbers, money figures, absolute paths, URLs, chat channel names,
UUIDs, message ids, credential-like env names. Add your own private words (people, clients,
internal agent names) in a deny file that lives OUTSIDE the repo:

  python3 tools/self_check.py . --deny ../private-denylist.txt

Prints file:line and the category only (never the matched text). Exit 1 on any hit.
"""
import argparse
import re
import sys
from pathlib import Path

PATTERNS = {
    "email": r"[\w.+-]+@[\w-]+\.[a-z]{2,}",
    "phone": r"(?<!\d)(\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)",
    "money": r"[\$\u20ac\u00a3]\s?\d",
    "abs_path": r"(?<![\w.])(/home/|/workspace/|/Users/|/root/|[A-Z]:\\\\Users)",
    "url": r"https?://(?!opensource\.org/licenses)",
    "chat_channel": r"(?<![\w&/'\"#])#[a-z][a-z0-9_]*-[a-z0-9_-]+",
    "uuid": r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    "msg_id": r"\bp?t\d{3,5}u\b",
    "credential_env": r"\b[A-Z][A-Z0-9]*_(API_)?(KEY|TOKEN|SECRET|PASSWORD|SIGNIN_CODE)\b",
}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--deny", help="file with one private word or phrase per line (kept outside the repo)")
    a = ap.parse_args()
    deny = []
    if a.deny:
        deny = [w.strip() for w in Path(a.deny).read_text().splitlines() if w.strip() and not w.startswith("#")]
    rxs = {k: re.compile(v) for k, v in PATTERNS.items()}
    deny_rx = [re.compile(r"(?i)\b" + re.escape(w) + r"\b") for w in deny]
    hits = 0
    me = Path(__file__).resolve()
    for p in sorted(Path(a.root).rglob("*")):
        if p.is_dir() or any(part in SKIP_DIRS for part in p.parts) or p.resolve() == me:
            continue
        try:
            raw = p.read_bytes()
        except OSError:
            continue
        if b"\0" in raw[:4096]:
            continue  # binary (images): check them by eye
        lines = raw.decode("utf-8", errors="ignore").splitlines()
        for i, line in enumerate(lines, 1):
            for k, rx in rxs.items():
                if rx.search(line):
                    print(f"{p}:{i}: {k}")
                    hits += 1
            for j, rx in enumerate(deny_rx):
                if rx.search(line):
                    print(f"{p}:{i}: denylist entry #{j + 1}")
                    hits += 1
    print(f"hits: {hits}")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
