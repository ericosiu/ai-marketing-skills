"""Synthetic example principles for the owner judge.

Replace these with YOUR recorded decisions. Every principle must point to a real,
dated record of the owner's own answer (`precedent`), or it may not decide anything.

kind:
  specific  - may decide on its own when the score clears the threshold
  broad     - a general lean; never decides alone (it can only support a specific one)
decision: "yes" or "no"
match: regexes; any hit means the principle applies to the ask
"""

PRINCIPLES = [
    dict(id="P-RECEIPTS", lane="ops", kind="specific", decision="yes",
         title="Read-only receipts and logs are fine",
         rule="Adding a read-only receipt, log line or shadow measurement that changes nothing outside the box is a yes.",
         match=[r"\b(receipt|log[- ]only|read[- ]only|shadow|measure|metric)\b"],
         precedent=dict(record="examples/decisions.example.jsonl", id="D-0001",
                        words="yes, log it, no need to ask for receipts")),
    dict(id="P-FIX-FORWARD", lane="ops", kind="specific", decision="yes",
         title="Reversible internal fixes with a backup and a test",
         rule="A small internal fix with a backup next to the changed file and a passing test goes in without an ask.",
         match=[r"\b(fix|patch|repair)\b.*\b(backup|\.bak|test)\b"],
         precedent=dict(record="examples/decisions.example.jsonl", id="D-0002",
                        words="fix forward, just keep a backup")),
    dict(id="P-EXPIRE-STALE", lane="ops", kind="specific", decision="yes",
         title="Stale asks expire as unanswered",
         rule="Asks older than 3 business days expire as 'unanswered', never as 'no'.",
         match=[r"\b(expire|stale)\b.*\b(ask|asks|queue)\b"],
         precedent=dict(record="examples/decisions.example.jsonl", id="D-0003",
                        words="let old asks expire, do not count silence as a no")),
    dict(id="P-NO-NEW-BOT", lane="ops", kind="specific", decision="no",
         title="No new agent for a job an existing agent owns",
         rule="One owner per job. Spinning up a second agent for an owned job is a no.",
         match=[r"\b(new|second|another) (bot|agent)\b"],
         precedent=dict(record="examples/decisions.example.jsonl", id="D-0004",
                        words="no, give it to the agent that already owns it")),
    dict(id="P-NO-SECOND-DIGEST", lane="ops", kind="specific", decision="no",
         title="One digest per day",
         rule="Adding a second daily digest for the owner is a no; fold it into the existing one.",
         match=[r"\b(second|another|extra|new) (daily )?(digest|summary|report)\b"],
         precedent=dict(record="examples/decisions.example.jsonl", id="D-0005",
                        words="no more digests, one is enough")),
    dict(id="P-DRAFTS-OK", lane="content", kind="specific", decision="yes",
         title="Drafting is free; publishing is gated",
         rule="Writing a draft that stays a draft is a yes. Publishing stays a hard gate.",
         match=[r"\b(write|create|prepare) (a |the )?drafts?\b"],
         precedent=dict(record="examples/decisions.example.jsonl", id="D-0006",
                        words="draft as many as you want, I publish")),
    dict(id="P-AGREE-RECS", lane="ops", kind="broad", decision="yes",
         title="Owner usually agrees with the recommendations",
         rule="A general lean toward the recommended option. Never decides alone.",
         match=[r"\b(recommend|recommended|recs?)\b"],
         precedent=dict(record="examples/decisions.example.jsonl", id="D-0007",
                        words="agree with your recs")),
]
