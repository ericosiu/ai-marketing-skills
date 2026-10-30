# Reimagine Work

A pattern for a team of AI agents whose biggest bottleneck is the one human they all wait on.

It has two parts:

1. **The improvement loop** (`skills/reimagine-work/SKILL.md`). A weekly pass of the "Elon algorithm"
   (question, delete, simplify, speed up, automate) over your agent fleet, plus a weekday scan that
   proposes at most one change or stays silent. It only proposes. It never sends, posts, spends,
   deletes, merges or changes a schedule.
2. **The owner judge** (`judge/`). A "shadow owner" that reads one ask from an agent and answers
   DECIDED (yes/no, citing a past recorded answer), SENT_BACK (bad or already-answered question) or
   HOLD (goes to the human).

## Safe by default

- **Shadow only.** Out of the box the judge logs what it would decide and the human still gets every
  ask. A verdict takes effect only when `JUDGE_LIVE=1` is set, the lane is marked live in
  `judge/live-lanes.json`, and no `judge/LIVE_OFF` or `judge/KILL` file exists. Every lane ships `live: false`.
- **Hard gates are code, not judgment.** Outside sends, spend, publishing, deletes, merges, credentials,
  gate or cap changes and anything irreversible are matched by plain regexes and always HOLD, unless a
  standing approval in the ledger covers every hard class, inside its cap and time window. A standing
  approval with no cap is inactive.
- **Usage tracking is required.** Standing approvals with caps require verified usage tracking.
  When checking a hard gate against a capped standing approval, the caller must provide `used_today`
  explicitly. Omitting `used_today` results in HOLD instead of defaulting to zero. This prevents
  cap-1 approvals from being used repeatedly without enforcement. Callers should maintain persistent
  usage state keyed by approval ID and window (e.g., a usage file that records each effective DECIDED).
- **Broad leans never decide alone.** "The owner usually agrees with the recommendations" can support
  a decision but never makes one.
- **Fail closed.** Tampered text (prompt injection, hidden characters, look-alike letters, a relayed
  "the boss said yes") is HOLD. A verdict that cannot be logged is HOLD.
- **Lanes come off at the first false yes** (`record_outcome`). A false yes on a hard-gate verb takes
  every lane off.
- **Go-live is never automatic.** `go_live_ready()` only reports `pending_go_live` after 30 decided
  shadow cases over 7 days with 0 false yes, at least 95% agreement and 10 owner spot-signs. A human
  edits `live-lanes.json`.

## Layout

```
skills/reimagine-work/SKILL.md     the loop (template; replace <PLACEHOLDERS>)
judge/judge.py                     the judge scaffold (Layer 1, deterministic)
judge/principles.py                7 synthetic example principles; replace with your own recorded decisions
judge/live-lanes.json              every lane in shadow
judge/shadow_compare.py            three-way scorecard: judge vs a second model vs the owner
judge/tests/                       unit tests + synthetic adversarial set (no network)
examples/approval-ledger.example.jsonl   standing approvals (with caps), a decline, a one-off
examples/decisions.example.jsonl         the recorded owner answers the principles cite
examples/kickoff-queue.example.jsonl     what a queue of asks looks like
docs/state-chart.md                mermaid state charts (one ask; the improvement loop)
tools/self_check.py                pre-publish leak check
```

## Quick start

```
python3 -m unittest discover -s judge/tests
echo '{"bot":"ops-agent","ask":"add a read-only receipt log to the nightly check"}' | python3 judge/judge.py
python3 judge/shadow_compare.py judge/tests/fixtures/three_way.example.jsonl
python3 tools/self_check.py .
```

## Adapting it

1. Record your real answers (yes, no, and "don't ask me this") in a ledger with the owner's exact words and a date.
2. Write principles that each cite one of those records. No citation, no decision.
3. Run in shadow for at least a week. Compare judge, second model and owner with `shadow_compare.py`.
4. Only then mark a lane live, by hand, one lane at a time.
5. Keep your real ledger, principles and logs out of any public repo. Run `tools/self_check.py` with a
   private deny list before every push.

## Where the ideas come from

The skill credits two public write-ups: one from a small company running a fleet of permanent agents
("found what work was waiting on and removed it, over and over"), and one on agent-written code
arriving as a continuous stream rather than one drop at a time.

## License

See `LICENSE` (placeholder; MIT suggested).
