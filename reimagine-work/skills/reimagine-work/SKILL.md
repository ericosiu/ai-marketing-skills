---
name: reimagine-work
description: >-
  Use when someone asks to find the "stupid human steps" in how work gets done,
  where a person is the bottleneck for a team of agents, how to redesign a
  process from zero, or to run the weekly "Elon algorithm" pass (question,
  delete, simplify, speed up, automate) over an agent fleet. Also use as a
  routine: weekly full pass with an outside reviewer, plus weekday incremental
  runs that propose at most one new change or stay silent. Also use when
  work arrives "one drop at a time" (batch waits, daily-only runs, per-item
  human review) and should become a continuous stream. It proposes and
  builds only internal, reversible checks. It never sends, posts, spends,
  enrolls, deletes, merges or changes a routine.
---

# Reimagine work (public template, based on v3.1: weekly Elon loop + continuous stream + escalation ladder)

> Template. Replace every `<PLACEHOLDER>` with your own values. Nothing in this skill sends, posts, spends or approves anything; it only proposes. The judge it refers to ships in shadow mode (log only) with hard gates on.

Find every place a human is what work waits on, remove that wait, and do it
again next week. The deliverable is a short ranked list and exact yes lines,
not a long report.


## Asks that are already answered (never re-ask)

Before any yes line reaches the human, check these in order. If any one is true, the work proceeds with no new ask, and it gets logged with what authorized it:
1. **The human already said it.** If the owner's own words in this conversation asked for this exact action ("send these follow-ups, by email and chat"), that is the yes. A copy tweak they asked for ("keep it simple like the outbound") is still inside that yes. Do not send a confirm line for the same batch.
2. **A lane owner approved it.** If the person who owns the lane (for example, the content lead for publishing) approved, proceed under their conditions. Don't ask the top owner for a second yes.
3. **A standing approval with a cap covers it.** Check the approval ledger. A matching row with owner_bots, a cap and a scope is the yes.
4. **It's reversible or read-only.** No yes at all.

The human gets a yes line only for a new send, spend, publish, delete or gate change that none of the four covers. Each yes line that does reach them gets counted. If any lane sends more than 2 a day, flag it in the next pass as a defect to fix.

## Where the idea comes from

These principles come from a public write-up by a ten-person company that runs
a fleet of permanent agents. Its founder says they "found what work was waiting
on and removed it, over and over." Use these principles to judge each redesign:

1. **Own an area.** Each agent is permanent and owns one part of the company.
   Two agents doing the same job is a SIMPLIFY finding.
2. **Coordinate through the world, not through messages.** Agents stop
   "telling each other what they were about to do." They read and change a
   shared record (queue, ledger, state file). A human relaying a message
   between agents is a finding.
3. **Fix forward.** A small reversible change goes in, a later check catches
   problems, and any break is fixed with a new change on top. Asking before a
   reversible internal fix is a finding.
4. **Test on a clock, not per change.** Run the full check on a schedule
   against the latest state. "It broke since the last run" is enough to find
   the cause.
5. **Review by someone who didn't write it.** Helper agents try to break a
   change before it lands.
6. **Agents read production themselves.** Errors, receipts and metrics go
   straight to the owning agent, and no human relays them.
7. **A stall is an incident.** A lane that ships nothing for a full working
   period pages its owner agent.
8. **AI judges from recorded decisions.** A judge either decides and cites
   where the owner already answered, sends back a wrong question, or holds the
   question for a human. "When a judge gets one wrong we say so, and the
   judges read that next time."
9. **Nothing waits on the queue.** Open asks that sit for days are the loop's
   main measure of failure.
10. **Hard gates stay small and dumb.** Anything that touches the outside world
    and can't be undone goes through "a small set of dumb, hard-coded gates."
11. **Humans keep taste.** That means saying no, deleting what the last model
    needed, and asking for 10x or 100x, which models do not ask for on their
    own.

A second source adds the stream layer: a public post on agent-written code
("code used to arrive one drop at a time. soon, if not already, code will be
written as if it were a continuous stream") and the engineering manifesto it
quotes. Principles 12 to 16 come from those two texts:

12. **Work is a stream, not drops.** Design for constant small changes, not
    batches that wait for a person. "AI needs to be able to work autonomously
    and continuously with less and less human babysitting."
13. **Make the easy thing the right thing.** Guardrails do the steering, so
    that even agents "with little context about the right way of doing things"
    land work inside them. A rule an agent must remember is weaker than a
    check it cannot skip.
14. **Bottlenecks move.** "what happens when you eliminate a bottleneck?
    Another takes it is place", including "approvals, specifications, and
    code reviews". Re-measure after every fix. Don't assume the old
    bottleneck is still the one.
15. **Rework, don't only speed up.** Phase 1 is speeding up existing steps.
    Phase 2 is "reworking and rethinking them altogether". When the pace
    breaks a workflow, rewrite it instead of adding another patch.
16. **Fix the class, for everyone.** Build the "habit of ensuring that
    repeated failures trigger an investigation and a fix", and put the fix in
    a shared skill, prompt or context file so every agent gets it next time.

## Rules

- Write only your own report, your own state file, and internal checks that
  are reversible, tested and logged, with a backup next to each changed file.
- Never send, post, publish, spend, enroll, delete, merge, change a routine,
  or edit a skill. You recommend these, and the owner decides.
- Never edit a script marked FROZEN. Report what it needs instead.
- Every count comes from a file opened this run, cited by path and date range.
  Label time estimates "estimate" and show the math.
- Never print secrets, tokens or cookies. Never put personal data about
  candidates or leads, money amounts, or deal names in the output. Use counts
  and lane names.
- Hard gates always stay human (see "Classify"). A redesign can make a gate
  faster or batch it, but never remove it.
- Run the existing tests before and after any build. If tests were already
  failing, find out why before you build. A broken shared reader is a finding
  in its own right.

## Evidence: the ledger is the source of truth

Use what exists, in this order:

1. **Approval ledger.** Every owner yes and no, with scope, caps and date.
   Count asks against answers: asks per answer, and re-asks of things already
   answered.
2. **Outcome record.** For each yes: baseline, target, check dates, verdicts,
   and `what_changed` (changed / no_change / unknown / pending / overdue).
   A yes that changed nothing is evidence against that kind of ask.
3. **Judge logs.** Backtest and shadow rows: match rate by ask type, misses,
   decide / send-back / hold counts.
4. **Queues.** Yes-queue files, kickoff queue, open-asks list. Measure age
   (median, max, item-days) and asks per bot per day against the cap.
5. **Gate and receipt logs.** Send and publish gate rows by sender, routine
   receipts, browser and lock logs, missed-run reports.
6. **Correction log.** Every "no, wrong, redo" from the owner.
7. **Chats, Slack, email and calendar** (read only). Relays, pastes and access
   requests.

## The loop (five steps, in this order)

### 1. QUESTION: where did agents wait on a human?
One row per kind of wait, not per instance: step, lane, who (a role, not a
name), evidence (path, count, window), frequency, wait time, and touch time
(estimate). Also look for yes lines, per-item picks, pastes, relayed approvals,
logins and seats, reviews of work that already passed a check, chase messages,
stale asks, and the same correction made twice.

### 2. DELETE: what protects nothing?
Delete candidates include bots, routines and yes lines with no output or
receipt in 14 days, asks the bot itself would answer no to, re-asks already in
the ledger, and scaffolding the current model no longer needs. **Proposals
only.** Expired asks are recorded as "unanswered", never as "no", so a judge
never learns to refuse from silence.

### 3. SIMPLIFY: one owner per job
List duplicate agents and loops. Name one owner per job, using the evidence:
receipts, gate rows by sender, open asks. When the owner has already picked
the owner (for example, a shared team agent so others can use it), that pick
stands. The evidence then becomes a readiness checklist, not a reason to
overrule the pick.

### 4. SPEED UP: remove the wait, not the step
Check for ordering bugs (work that lands after the digest it belongs to),
polling hops, lock clashes, relay hops (a human or coordinator agent passing a
resolve on, when the owning agent could read the shared record), and
bot-to-bot asks parked in the owner's file.

### 5. AUTOMATE: the escalation ladder is this step (default)
Every decision a bot would otherwise hand to the owner climbs this ladder,
cheapest rung first, and stops at the first rung that settles it. A rung
that is unsure, errors, is skipped or times out passes the item UP, never
down and never to "yes".

| Rung | What | Settles | Never |
| --- | --- | --- | --- |
| 1. Deterministic check | Code: hard-gate class match, tampering flags (injection, hidden characters, look-alike letters, relayed yes), malformed or empty ask, already answered, caps, DNC, dedupe; for images the pixel/OCR gate | HOLD on any hard gate or tamper, SENT_BACK on malformed or already answered, pass/fail on measurable facts | Clears a hard gate. A hard-gate item goes straight to the owner (or to a standing rule that covers its exact scope and cap) |
| 2a. Second-opinion text model | One call to `<SECOND_OPINION_MODEL>` (pinned version, fail closed below a confidence cutoff, e.g. 0.55): CLEAR or HOLD plus reason flags (outside world, new judgment, loosens a gate, unclear, irreversible) | CLEAR only internal, reversible asks inside existing rules; everything else HOLD with reasons | Sees or clears a hard-gate item; runs when the host is short on resources (that counts as HOLD) |
| 2b. Second-opinion image model | One image per call (`<IMAGE_CHECK_CALL>`, resized to a fixed max size): featured and in-body images, page screenshots, table renders | Visual facts the pixel gate can't read (404/login wall, caption honesty, third-party logos, palette) | Replaces the pixel/OCR gate. It sits beside it; both must pass |
| 3. Judge | The owner judge (recorded decisions, citations, threshold) | DECIDED with a citation, SENT_BACK, or HOLD | Decides a hard gate without an exact standing approval |
| 4. Owner | The human | Anything still held, every hard gate, taste | Is asked something a lower rung already settled |

Ladder rules:
- New rungs start in **shadow**: they log their answer next to the rung
  above and act on nothing. A rung goes live for an ask type only through the
  go-live gate below.
- Log every rung's answer, reasons, tokens and cost estimate per item, so the
  weekly pass can report, per ask type, how far up items climbed and where
  each rung disagreed with the one above.
- Report second-opinion model cost as tokens (actual, from the API usage field) and dollars
  (labeled estimate, with the rate and its source). Never invent a rate.
- Report second-opinion model accuracy only from an eval file opened this run (backtest
  against the owner's recorded answers, or a labeled fixture set), with
  false-clear count first. A rung with any false CLEAR on a known "no" stays
  in shadow.

For each ask type, look up the judge's (and each shadow rung's) match rate on the ledger:
- **Go-live gate:** at least 30 shadow cases of that declared type with
  **zero misses**, plus the owner's yes for the rule change. Below that, it
  stays in shadow.
- The bot must declare the ask type from a fixed list. No free text.
- Never auto-approve these: retries or "continue" (a retry can re-fire a
  send), changes that loosen a gate, and every hard-gate class.
- Changes that only tighten a gate may skip the ask only when a test proves
  the change only tightens. Otherwise they stay human.
- Feedback: every owner override and every no_change outcome goes back into
  the judge's principles before the next weekly backtest.
- Name the kill switch (one per rung; for the judge and its second-opinion pre-pass,
  `judge/KILL`).

## Continuous-stream layer (runs inside steps 1, 4 and 5)

A lane is a **drop lane** when its work waits for a batch, a clock or a person
before it moves. For each bot, read these from files (receipts, queue
timestamps, yes-queue, routine schedule) and mark each one drop or stream:

| Check | Drop sign | Stream fix |
| --- | --- | --- |
| Trigger | Runs only on a fixed clock, or misses its slot to a lock | Runs when its input lands or the lock frees, with the clock as a backstop |
| Unit of work | Items held for a daily or weekly batch | Each item moves as soon as it clears its checks |
| Review | A human reviews every item, including items the bot itself would drop | The escalation ladder per item (deterministic, then second-opinion text or second-opinion images, then judge); human reviews a sample plus every disagreement |
| Gate | One yes line per item for a recurring kind of ask | One standing rule with a hard cap, approved once by the owner, logged per item |
| Failure | The same break patched again | Fix forward, and after the second repeat, rewrite the step and add a shared check |
| Backlog | Open picks pile up across days | Stale picks expire as "unanswered" and the stream keeps moving |

Measure each stream lane on two numbers:
- **Signal-to-shipped time**: from the input landing (lead, draft, reply,
  error) to the outcome receipt. Report the median and the slowest, and show
  the math.
- **Throughput and batch wait**: items shipped per day, plus the share of
  item-hours spent waiting on a batch, a clock or a person.

Rules for the stream layer:
- A stream never removes a hard gate. Sends, spend, publishing, merges and
  gate changes still need the owner's yes. The stream form of a hard gate is
  a standing rule with a cap, a kill switch and a per-item log. The owner
  approves that rule once, and every change to it needs a new yes.
- Sampling review applies only to work inside an approved gate, or to
  internal and reversible work.
- Re-measure after each change (principle 14). A fix that moved the wait to
  the next step is a partial, not a win.

## Classify each finding

Pick exactly one:
- **delete**: protects nothing.
- **automate**: deterministic, reversible, testable. The agent does it and
  logs a receipt.
- **judge**: needs taste, but the owner has answered this kind of question
  before. It climbs the ladder (deterministic, second-opinion model, judge). Each new rung goes
  through shadow first, then the go-live gate above.
- **batch**: must stay human, but goes in one digest per day or week, or
  becomes one standing rule with a hard cap.
- **keep-human (hard gates)**: outside sends, posts and sequence enrollment
  (unless a written standing rule with a cap covers them), spending, publishing,
  legal and anything signed, hiring decisions, personal-data exposure, deletes,
  merges, and credential actions.
When unsure, pick the safer class: keep-human > batch > judge > automate >
delete.

## Two structural checks the loop always runs

**Per-bot ask cap.** Each agent gets at most N asks a day (default 3) that
show as their own yes line. Asks over the cap stay queued with their id but
fold into one digest block without a yes line each. Report asks per bot per
day and how many went over. A bot that keeps going over the cap is a finding:
merge its asks, add a standing rule, or give it a judge type.

**Outcome record.** Every yes gets a `what_changed` field, filled from the
existing check verdicts and never re-graded by the loop. The weekly pass
reports the changed rate (changed / graded), the no_change and overdue ids,
and which ask types produce yeses that change nothing (candidates for DELETE
or for the judge's "no").

## Redesign from zero

For each top candidate, answer these questions:
1. If we started today with agents that read every system directly, would
   this step exist at all?
2. What is it waiting on? Remove that, not the symptom.
3. Can agents coordinate through one shared record instead of messages?
4. Can the agent fix forward and roll back instead of asking first?
5. Where must a human stay? Make that gate small, dumb and hard-coded.
6. What would make it 10x better, not 10%?
Write the redesign in two or three sentences: what the agent does, what the
human still does, and what the hard gate is.

## Rank and score

Score = estimated minutes saved per instance x instances per week. Show the
math. Break ties by wait time, then by the number of lanes unblocked. Drop
anything under the bar (default 30 min/week).

**Leverage score (0-100), reported weekly.** It shows whether the loop itself
improves:
- 25 points: share of last week's owner asks that a judge, standing rule or
  deterministic check settled without the owner (from the ledger)
- 15: median age of open asks, with full marks at 1 business day or less
- 10: stream share: share of active lanes with no drop sign in the stream
  check, scaled by how much median signal-to-shipped time fell week over week
  (full marks when every lane is stream and none got slower)
- 15: share of yeses with a graded outcome and a changed rate of 70% or more
- 10: no bot over the ask cap on more than 1 day
- 10: no duplicate owners left for any send or publish loop
- 10: no relay hops (owner answers that were retyped elsewhere)
- 5: last week's DELETE and 10x lines were answered
Score only from files. If a part has no data, it scores 0 and is named as a
gap.

## Outside reviewer (weekly)

Once per weekly pass, send the top 3 to 5 moves to a second strong model that
had no part in writing them. Make one call and save the transcript. The
reviewer returns DO / DO WITH CHANGE / DON'T for each move and names the
biggest gap. Fold its changes in, or say why not. Never send it secrets,
personal data, money amounts or deal names.

## Modes and routine

- **Weekly full pass** (routine, for example Friday morning): all five steps,
  the outside reviewer, the leverage score, the judge shadow status by ask
  type, the outcome record summary, and the **per-bot stream check** (each bot
  marked drop or stream on the six checks, with its signal-to-shipped median
  and the week-over-week change). Output: top 3 moves, copy-paste yes
  lines (one per gated move), one DELETE line and one 10x ask for the owner's
  taste.
- **Weekday incremental** (routine): read only what changed since
  `last_run_at`, then surface at most one new finding that clears the bar, or
  stay silent and log why.
- **On demand:** a full pass whenever asked.

### Output format

```
ONE recommendation: <the single change, one sentence>
Why: <evidence path + count + estimated minutes/week (estimate)>
Three options:
  A (recommended): <change>, shadow first, <how long>, <what decides go-live>
  B: <smaller or different change>
  C: <do nothing, and what that costs>
ONE ask: `<exact yes line>`   (only when it touches a hard gate or a rule change)
```
The weekly pass adds a top-10 table (process, evidence, class, redesign,
min/week) and a "spawn check": each principle above marked match, partial or
miss, with evidence. It also adds a stream table (bot, drop signs, fix,
signal-to-shipped now and target, whether it needs a yes).

### State file (one per deployment)

```json
{
  "schema_version": 3,
  "ladder_version": "3.1",
  "last_run_at": "ISO-8601 with offset",
  "last_full_scan_at": "ISO-8601 with offset",
  "bar_minutes_per_week": 30,
  "ask_cap_default": 3,
  "leverage_score_history": [{"week": "YYYY-Www", "score": 0, "parts": {}}],
  "cursors": {"<source path>": {"mtime": "", "lines": 0, "last_id": ""}},
  "stream": {"<bot>": {"week": "YYYY-Www", "drop_signs": [],
             "signal_to_shipped_median_min": null, "items_per_day": null}},
  "findings": [{
    "fingerprint": "lane|step-kind|source-path",
    "title": "", "step": "question|delete|simplify|speed_up|automate",
    "classification": "delete|automate|judge|batch|keep-human",
    "first_seen": "", "last_seen": "",
    "evidence": [{"path": "", "count": 0, "window": ""}],
    "est_minutes_per_week": 0,
    "status": "candidate|surfaced|accepted|declined|shadow|live|retired",
    "surfaced_on": null, "owner_answer": null, "outcome_ref": null,
    "resurface_if": ""
  }],
  "runs": [{"at": "", "mode": "weekly|incremental|full", "new_rows_read": 0,
            "surfaced": null, "silent_reason": null, "reviewer": null}]
}
```
Each run: load the state (do a full pass and create it if it is missing) →
read only changed sources → update counts → skip findings already surfaced,
accepted, declined, shadow, live or retired unless `resurface_if` is true
(never re-ask a declined finding without new evidence) → pick at most one
finding at or above the bar → output it or stay silent → link accepted
findings to their outcome row (`outcome_ref`) → keep the last 60 runs.

## Done means

- Every finding has a path and a real count. Every time is labeled estimate
  with its math.
- Hard gates stayed human. Nothing was sent, posted, enrolled, spent, deleted,
  merged or changed outside the report, the state file and tested internal
  checks.
- The ask cap and outcome record were checked, and their numbers are in the
  report.
- The judge's go-live status is listed by ask type, against the 30 cases and
  zero misses bar, along with each shadow rung (second-opinion text, second-opinion images): items
  seen, CLEAR count, false CLEARs, tokens and estimated cost.
- The outside reviewer's verdicts are folded in (weekly pass).
- The leverage score is reported, along with what would raise it next week.
- Every active bot has a stream check row with its drop signs and its
  signal-to-shipped time, or a named data gap.
