#!/usr/bin/env python3
"""Owner judge scaffold ("shadow owner"): one ask in, one verdict out.

Verdicts:
  DECIDED    yes/no, with a citation to a past recorded owner answer
  SENT_BACK  the ask is malformed, empty, or already answered (note for the filing agent)
  HOLD       goes to the human (every hard gate, anything unsure, anything tampered)

SAFE DEFAULTS (do not weaken these when you adapt it):
  * Shadow mode by default. A verdict only takes effect when ALL of these are true:
    env JUDGE_LIVE=1, the ask's lane is live in live-lanes.json, and no LIVE_OFF / KILL file exists.
    Otherwise the effective result is HOLD (the human still decides) and the verdict is only logged.
  * Hard gates (outside sends, spend, publish, delete, merge, credentials, gate/cap changes,
    irreversible actions) are deterministic regexes and are ALWAYS HOLD, unless a standing approval
    in the ledger covers every hard class in the ask, inside its cap and window.
  * Broad principles never decide alone. Below the threshold means HOLD.
  * Anything that errors, times out or cannot be logged is HOLD. Never "yes".
  * A lane comes off live at its first false yes (record_outcome).

Usage:
  echo '{"bot":"ops-agent","ask":"add a read-only receipt log to the nightly check"}' | python3 judge.py
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from principles import PRINCIPLES  # noqa: E402

THRESHOLD = 0.70          # a specific principle must score at least this to decide
THRESHOLD_FLOOR = 0.50    # the shipped threshold may never go below this
MAX_ASK_CHARS = 1500

# --- 1. untrusted text --------------------------------------------------------------------
ZERO_WIDTH = re.compile("[\u00ad\u180e\u200b-\u200f\u202a-\u202e\u2060-\u2064\ufeff]")
INJECTION_RX = [
    r"\bignore (all |any |the )?(previous|prior|above|earlier|your) (instructions|rules|prompt)",
    r"\b(system|developer) (prompt|message)\b",
    r"<!--.*judge.*-->",
]
RELAY_RX = [  # a yes relayed by someone else is never a yes
    r"\b(owner|boss|manager|ceo)(?:'s)? (?:already |has |just )?(?:said|says|gave|approved) (?:a |his |her |their )?(?:yes|ok|okay|go|approval)",
    r"\bpre-?approved\b",
    r"\bper (the )?(owner|ceo|coordinator)\b",
]

# --- 2. hard gates (small, dumb, hard-coded) -----------------------------------------------
HARD_RX = {
    "external_send": r"\b(send|email|e-mail|dm|message|text|reply|post|tweet|inmail|call|dial|enroll|sequence|campaign|outreach)\b",
    "spend": r"\b(buy|purchase|spend|pay|top ?up|upgrade|subscribe|invoice|credits?)\b",
    "publish": r"\b(publish|ship|go live|make public|release)\b",
    "delete": r"\b(delete|remove|purge|archive|void|drop table|wipe)\b",
    "merge": r"\b(merge|push to main|force[- ]push|deploy)\b",
    "credential": r"\b(password|token|api key|secret|credential|login|sign[- ]in|2fa)\b",
    "gate_change": r"\b(raise|lift|increase|widen|waive|bypass|disable|exempt)\b.*\b(cap|limit|gate|rule|threshold|check)\b",
    "irreversible": r"\b(irreversible|cannot be undone|permanent(ly)?)\b",
}
# phrases that mention a hard verb but do not perform it
NOT_ACTION = [r"\bdraft(s|ed)?\b(?!.*\bsend\b)", r"\b(log|logs|logged)[- ]only\b", r"\bread[- ]only\b",
              r"\bshadow\b", r"\bdry[- ]run\b", r"\breceipts?\b"]

CONTENTLESS = re.compile(r"^(yes |ok |okay )?(do it|ok|okay|go|yes|both|sure|fine|that|this|\d+)[.!?]*$")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"\s+", " ", s).strip().lower()


def toks(s: str) -> set[str]:
    stop = {"a", "an", "the", "and", "or", "of", "to", "for", "in", "on", "at", "by", "with", "it", "this", "that", "is"}
    return {t for t in re.findall(r"[a-z0-9][a-z0-9_.-]*", norm(s)) if t not in stop}


def jaccard(a: str, b: str) -> float:
    x, y = toks(a), toks(b)
    return len(x & y) / len(x | y) if x | y else 0.0


def scan_flags(raw: str) -> list[str]:
    flags = []
    if ZERO_WIDTH.search(raw or ""):
        flags.append("hidden_characters")
    if any(ord(c) > 0x2FF and unicodedata.category(c).startswith("L") for c in raw or ""):
        flags.append("look_alike_letters")
    t = norm(raw)
    if any(re.search(rx, t) for rx in INJECTION_RX):
        flags.append("injection")
    if any(re.search(rx, t) for rx in RELAY_RX):
        flags.append("relayed_yes")
    return flags


def hard_classes(text: str) -> list[str]:
    t = norm(text)
    found = [k for k, rx in HARD_RX.items() if re.search(rx, t)]
    # Only suppress a hard verb when EVERY occurrence is the non-acting thing
    # (e.g. "draft the email" with no explicit send, "shadow run only")
    # Never suppress when the non-acting word describes an object that comes after the verb
    # (e.g. "send a read-only receipt log", "delete the read-only receipt log")
    # If even ONE occurrence is acting, keep the hard class.
    # 
    # Strategy: fail closed. Only suppress if NOT_ACTION comes RIGHT BEFORE the verb
    # with at most "the" or "a" between, so we're confident it modifies the verb, not an object.
    if found:
        keep = []
        for k in found:
            if k not in ("external_send", "publish", "delete"):
                keep.append(k)
                continue
            # Find all occurrences of this hard verb
            verb_matches = list(re.finditer(HARD_RX[k], t))
            all_non_acting = True  # Assume all are non-acting until we find an acting one
            for vm in verb_matches:
                verb_word = vm.group(0)
                # Check if a NOT_ACTION phrase immediately precedes this verb
                # Look back up to 20 chars for NOT_ACTION + optional article
                before_start = max(0, vm.start() - 20)
                before_text = t[before_start:vm.start()]
                # Pattern: NOT_ACTION followed by optional article/prep and then immediately the verb
                # e.g., "draft the email", "log-only send", "shadow delete"
                this_verb_is_non_acting = False
                for na_rx in NOT_ACTION:
                    na_matches = list(re.finditer(na_rx, before_text))
                    if na_matches:
                        # Check if the last NOT_ACTION match is close to the verb
                        last_na = na_matches[-1]
                        # Text between NOT_ACTION and verb
                        between = before_text[last_na.end():]
                        # Only suppress if between is just whitespace and/or articles/determiners
                        if re.match(r'^\s*(the|a|an)?\s*$', between):
                            this_verb_is_non_acting = True
                            break
                # If this occurrence is acting (no NOT_ACTION prefix), keep the class
                if not this_verb_is_non_acting:
                    all_non_acting = False
                    break  # Found an acting verb, no need to check other occurrences
            # Only suppress if ALL occurrences were non-acting
            if not all_non_acting:
                keep.append(k)
        found = keep
    return found


# --- ledger helpers ----------------------------------------------------------------------
def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def active(row: dict, today: dt.date) -> bool:
    if row.get("status", "active") != "active":
        return False
    exp = row.get("expires")
    return not exp or dt.date.fromisoformat(exp) >= today


def standing_covers(row: dict, ask: str, context: str, classes: list[str], used_today: int, count: int) -> bool:
    """A standing approval covers an ask only with a cap, a window, every hard class, every require regex.
    Positive requirements must match the ask (the requested action) only.
    Exclusions check both ask and context (so context can block)."""
    if row.get("kind") != "standing" or not row.get("cap") or not row.get("window"):
        return False  # capless standing = inactive
    if not set(classes) <= set(row.get("covers", [])):
        return False
    ask_norm = norm(ask)
    full_text_norm = norm(ask + " " + context)
    # Require patterns must match the ask only (prevents context from authorizing out-of-scope actions)
    if not all(re.search(rx, ask_norm) for rx in row.get("require", [])):
        return False
    # Exclude patterns check both ask and context (so context can block)
    if any(re.search(rx, full_text_norm) for rx in row.get("exclude", [])):
        return False
    return used_today + max(count, 1) <= int(row["cap"])


def ask_count(ask: str) -> int:
    m = re.search(r"\b(\d{1,4})\b", ask)
    return int(m.group(1)) if m else 1


# --- live-lane switch --------------------------------------------------------------------
def lanes_file(base: Path) -> Path:
    return base / "live-lanes.json"


def lane_live(base: Path, lane: str) -> bool:
    if os.environ.get("JUDGE_LIVE") != "1":
        return False
    if (base / "LIVE_OFF").exists() or (base / "KILL").exists():
        return False
    try:
        data = json.loads(lanes_file(base).read_text())
    except Exception:
        return False  # missing or bad file = nothing live
    return bool(data.get("lanes", {}).get(lane, {}).get("live"))


# --- the judge ---------------------------------------------------------------------------
def verdict(kind: str, reason: str, *, decision: str | None = None, cite: dict | None = None,
            lane: str = "ops", score: float = 0.0, classes: list[str] | None = None) -> dict:
    return dict(verdict=kind, decision=decision, reason=reason, cite=cite, lane=lane,
                score=round(score, 2), hard_classes=classes or [])


def lane_of(text: str) -> str:
    return "content" if re.search(r"\b(draft|article|post|page|blog|copy)\b", norm(text)) else "ops"


def judge(q: dict, base: Path = HERE, today: dt.date | None = None) -> dict:
    today = today or dt.date.today()
    raw = q.get("ask", "") or ""
    ask = norm(raw)
    ctx = norm(q.get("context", ""))
    if (base / "KILL").exists():
        return verdict("HOLD", "kill switch on")
    flags = scan_flags(raw + " " + (q.get("context", "") or ""))
    if flags:
        return verdict("HOLD", "untrusted text: " + ", ".join(flags))
    if not ask or CONTENTLESS.match(ask) or len(ask) > MAX_ASK_CHARS:
        return verdict("SENT_BACK", "malformed: say exactly what you want done, in one line")
    lane = lane_of(ask)
    ledger_path = Path(q["ledger_path"]) if q.get("ledger_path") else base.parent / "examples" / "approval-ledger.example.jsonl"
    ledger = load_jsonl(ledger_path)

    # already answered: same ask, recorded owner answer -> send back with the cite
    for row in ledger:
        if row.get("kind") in ("one-off", "decline") and active(row, today) and jaccard(ask, row.get("ask", "")) >= 0.9:
            return verdict("SENT_BACK", "already answered; act on the recorded answer",
                           cite=dict(id=row["id"], words=row.get("owner_words", "")), lane=lane)

    classes = hard_classes(ask + " " + ctx)
    if classes:
        # Enforce cap usage tracking: HOLD when verified usage is unavailable
        if "used_today" not in q:
            return verdict("HOLD", "hard gate with standing approval requires verified usage tracking", 
                         lane=lane, classes=classes)
        for row in ledger:
            if active(row, today) and standing_covers(row, ask, ctx, classes, int(q.get("used_today", 0)), ask_count(ask)):
                return verdict("DECIDED", "covered by a capped standing approval", decision="yes",
                               cite=dict(id=row["id"], words=row.get("owner_words", "")), lane=lane,
                               score=1.0, classes=classes)
        return verdict("HOLD", "hard gate: " + ", ".join(classes), lane=lane, classes=classes)

    # recorded declines beat principles
    for row in ledger:
        if row.get("kind") == "decline" and active(row, today) and jaccard(ask, row.get("ask", "")) >= 0.6:
            return verdict("DECIDED", "owner declined this before", decision="no",
                           cite=dict(id=row["id"], words=row.get("owner_words", "")), lane=lane, score=0.9)

    best, best_score, broad_hit = None, 0.0, False
    for p in PRINCIPLES:
        if not any(re.search(rx, ask) for rx in p["match"]):
            continue
        if p["kind"] == "broad":
            broad_hit = True
            continue
        score = 0.6 + 0.4 * jaccard(ask, p["title"] + " " + p["rule"]) * 2
        score = min(score, 0.95)
        # tie goes to no
        if score > best_score or (score == best_score and best and p["decision"] == "no"):
            best, best_score = p, score
    if best is None:
        return verdict("HOLD", "broad lean only; needs the owner" if broad_hit else "new judgment", lane=lane, score=0.45 if broad_hit else 0.0)
    if best_score < max(THRESHOLD, THRESHOLD_FLOOR):
        return verdict("HOLD", f"under threshold ({best_score:.2f})", lane=lane, score=best_score)
    return verdict("DECIDED", best["title"], decision=best["decision"],
                   cite=dict(principle=best["id"], id=best["id"], record=best["precedent"]["record"], record_id=best["precedent"]["id"], words=best["precedent"]["words"]), lane=best["lane"], score=best_score)


def decide(q: dict, base: Path = HERE, log_path: Path | None = None, today: dt.date | None = None) -> dict:
    """judge() plus the shadow/live switch and a log line. Effective result is what the system does."""
    v = judge(q, base, today)
    live = v["verdict"] != "HOLD" and lane_live(base, v["lane"])
    v["mode"] = "live" if live else "shadow"
    v["effective"] = v["verdict"] if live else "HOLD"
    v["ts"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    v["ask"] = q.get("ask", "")
    log_path = log_path or (base / "verdicts.jsonl")
    try:
        with open(log_path, "a") as fh:
            fh.write(json.dumps(v) + "\n")
    except OSError:
        v["effective"] = "HOLD"  # a verdict that cannot be logged is HOLD
        v["reason"] += " (log failed)"
    return v


def record_outcome(v: dict, owner_answer: str, base: Path = HERE) -> dict:
    """Compare a verdict with the owner's real answer. A false yes takes the lane off live at once."""
    false_yes = v.get("verdict") == "DECIDED" and v.get("decision") == "yes" and owner_answer == "no"
    if false_yes:
        path = lanes_file(base)
        data = json.loads(path.read_text()) if path.exists() else {"lanes": {}}
        lanes = data.setdefault("lanes", {})
        targets = list(lanes) if v.get("hard_classes") else [v.get("lane", "ops")]
        for lane in targets:
            lanes.setdefault(lane, {})["live"] = False
            lanes[lane]["pulled_reason"] = "false yes"
        path.write_text(json.dumps(data, indent=1))
    return dict(false_yes=false_yes, match=(v.get("decision") == owner_answer))


def go_live_ready(rows: list[dict], lane: str, crit: dict) -> str:
    """Never flips a lane live. Returns 'pending_go_live' or 'shadow'. A human makes the change."""
    r = [x for x in rows if x.get("lane") == lane and x.get("verdict") == "DECIDED"]
    if not r:
        return "shadow"
    days = {x["ts"][:10] for x in r if x.get("ts")}
    fy = sum(1 for x in r if x.get("decision") == "yes" and x.get("owner") == "no")
    agree = sum(1 for x in r if x.get("decision") == x.get("owner")) / len(r)
    signed = sum(1 for x in r if x.get("spot_signed"))
    ok = (len(r) >= crit["min_decided_in_shadow"] and len(days) >= crit["min_days"] and fy <= crit["max_false_yes"]
          and agree >= crit["min_decided_only_agreement"] and signed >= crit["owner_spot_signs"])
    return "pending_go_live" if ok else "shadow"


if __name__ == "__main__":
    q = json.loads(sys.stdin.read() or "{}")
    print(json.dumps(decide(q), indent=1))
