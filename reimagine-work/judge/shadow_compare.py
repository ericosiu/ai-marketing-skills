#!/usr/bin/env python3
"""Three-way scorecard: judge vs a second model vs the owner's real answer. Counts only.

Input: a JSONL file, one row per item:
  {"item": "...", "judge": {"verdict": "DECIDED", "decision": "yes"},
   "model": {"verdict": "HOLD"}, "owner": "yes", "hard_gate": false}
Usage: python3 shadow_compare.py rows.jsonl
"""
import json
import sys
from collections import Counter


def score(side: dict, owner: str | None, hard_gate: bool) -> str:
    v, d = side.get("verdict"), side.get("decision")
    if owner is None:
        return "unanswered"
    if hard_gate:
        return "required_hold" if v == "HOLD" else ("hard_gate_not_held" if v == "DECIDED" else "sent_back")
    if v == "DECIDED":
        if d == owner:
            return "match"
        return "false_yes" if d == "yes" else "false_no"
    return "hold" if v == "HOLD" else "sent_back"


def main(path: str) -> dict:
    out = {"judge": Counter(), "model": Counter()}
    agree = n = 0
    for line in open(path):
        if not line.strip():
            continue
        r = json.loads(line)
        n += 1
        for k in ("judge", "model"):
            out[k][score(r.get(k, {}), r.get("owner"), bool(r.get("hard_gate")))] += 1
        agree += (r.get("judge", {}).get("verdict"), r.get("judge", {}).get("decision")) == \
                 (r.get("model", {}).get("verdict"), r.get("model", {}).get("decision"))
    res = {"items": n, "judge_vs_owner": dict(out["judge"]), "model_vs_owner": dict(out["model"]),
           "judge_model_agree": agree}
    return res


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), indent=1))
