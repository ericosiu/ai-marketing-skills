---

## Preamble (runs on skill start)

```bash
# Version check (silent if up to date)
python3 telemetry/version_check.py 2>/dev/null || true

# Telemetry opt-in (first run only, then remembers your choice)
python3 telemetry/telemetry_init.py 2>/dev/null || true
```

> **Privacy:** This skill logs usage locally to `~/.ai-marketing-skills/analytics/`. Remote telemetry is opt-in only. No code, file paths, or repo content is ever collected. See `telemetry/README.md`.

---
name: banned-ai-tells
description: >-
  Catch and eliminate AI writing tells before they ship. Run the checker on
  any draft — posts, emails, pitches, pages, DMs — to flag banned patterns.
  Use before any copy reaches a human reader. Includes 9 tells plus the
  baseline em/en-dash rule, with regex patterns and a CLI checker.
---

# Banned AI Tells

**Stop AI slop before it ships.** A fleetwide rule for writing that sounds human, plus a checker script that flags every banned pattern.

Source: Zephyr (@Zephyr_hg), "I keep a file of the new em dashes my writing bots are never allowed to use", posted 2026-10-31 2:30 PM PT: https://x.com/i/status/2116643887624430055

Shared by: Eric Siu (@ericosiu), https://x.com/ericosiu/status/2116934054620831844

---

## When to Use This

**Before any draft ships.**

- X posts, LinkedIn articles, emails
- Landing pages, product copy, sales decks
- Blog posts, newsletters, Slack DMs
- Any text going to a customer, prospect, or teammate

Run the checker. If it flags a line, rewrite it. No exceptions.

---

## The Rule

Never use these patterns in any copy written for humans. They're tells — signals that a bot wrote it and no human edited.

### How to Check

Before a draft reaches anyone, run the checker:

```bash
python3 banned-ai-tells/check_tells.py draft.md
# or pipe text on stdin:
echo "Your text" | python3 banned-ai-tells/check_tells.py
```

- **Exit 0** = clean
- **Exit 1** = hits found, listed with line numbers
- **Exit 2** = error (missing file or bad pattern)

### How to Fix a Hit

Say what actually happened. What did you do? What broke? What shipped?

Don't just swap the banned word for a synonym — that makes a new tell. If you wouldn't say the line to one person across a table, cut it.

---

## The List (Zephyr's Nine Tells)

Each item: the tell, his example, his fix.

### 1. "Quietly."

**Example:** "Claude quietly shipped the best feature of the year."

**Fix:** Delete the word. If it shipped, it shipped.

---

### 2. "It's not X, it's Y."

**Example:** "It's not a chatbot, it's a coworker."

**Fix:** Say what it does. "It answers my client emails."

---

### 3. The Fake Deadline

**Examples:**
- "Set this up before Monday."
- "Do it this weekend."

**Fix:** Say how long the setup takes. Leave the reader's calendar alone.

---

### 4. Talking to a Crowd

**Example:** "Most people use Claude wrong."

**Fix:** Talk to the one person reading. Say what you do instead.

---

### 5. "Can now X like a pro."

**Example:** "Claude can now research like a $150/hour analyst."

**Fix:** Show what it researched and let them judge the price.

---

### 6. The Little Line That Sounds Deep

**Examples:**
- "Setup is the part everyone skips."
- "That's the whole game."

**Fix:** Delete it. The sentence before it already said it.

---

### 7. Three of Everything Up Top

**Example:** "Write. Edit. Ship."

**Fix:** Keep the one reason you actually believe.

---

### 8. Adjectives in a Pile

**Example:** "A powerful, seamless, game-changing workflow."

**Fix:** Name the workflow. If it's good, the name is enough.

---

### 9. Sirens and Arrows

**Example:** A siren emoji 🚨, the word BREAKING in capitals, an arrow pointing down at the link ⬇️

**Fix:** Write the news as a normal sentence.

---

### Baseline (Em/En Dash Rule)

No em dash (—) or en dash (–). Use a comma, period, or parentheses.

This was the existing rule before Zephyr's nine. The post builds on it.

---

## What the Checker Can and Can't Catch

`banned-ai-tells.txt` holds the regexes (one per line, case-insensitive, grouped under `#@` category lines). They come only from Zephyr's examples above:

**Exact catches:**
- quietly
- it's/this is/that's not X, it's Y
- before Monday (any weekday or "the weekend")
- do/set/try ... this weekend
- most people
- can now X like a
- like a pro
- that's the whole game
- the part everyone skips
- three one-word sentences in a row
- powerful, seamless, game-changing
- siren emoji, BREAKING in capitals, down arrows
- em and en dashes

**Judgment only** (a regex can't see it):
- A deep-sounding closer phrased some other way
- Any other fake deadline
- Adjective piles using other words
- Other crowd talk ("everyone gets this wrong")

Read the draft for these too.

---

## Gaps

- Zephyr's follow-up reply says "The full banned list and the check prompt go out in my newsletter" (zephyr-hq.com/subscribe). That longer list sits behind a newsletter signup and was NOT read or added. Only the nine he posted are here.
- Nothing in the post was unreadable.

---

## Keep It Growing

**Zephyr's habit, adopted:**

Every time you catch a new tell in a draft, add it here and to `banned-ai-tells.txt` that day, with:
1. One example
2. One fix
3. A test in `tests/test_check_tells.py`

The list grows as the tells evolve.

---

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | This document — the rule and how to use it |
| `check_tells.py` | CLI checker (exit 0 clean, 1 hits, 2 error) |
| `banned-ai-tells.txt` | 21 regex patterns (machine list) |
| `tests/test_check_tells.py` | 24 tests covering all nine categories |

---

## Running the Checker

```bash
# Check a file
python3 banned-ai-tells/check_tells.py draft.md

# Check multiple files
python3 banned-ai-tells/check_tells.py draft.md email.txt pitch.md

# Pipe text on stdin
echo "Claude quietly shipped it." | python3 banned-ai-tells/check_tells.py

# Machine-readable JSON output
python3 banned-ai-tells/check_tells.py draft.md --json
```

---

## Running Tests

```bash
cd banned-ai-tells
python3 -m pytest tests/test_check_tells.py -v
# or
python3 -m unittest tests/test_check_tells.py
```

All 24 tests should pass.

---

## Import as a Module

```python
from banned_ai_tells.check_tells import find_tells

text = "Claude quietly shipped the best feature of the year."
hits = find_tells(text)

for h in hits:
    print(f"Line {h['line']}: [{h['category']}] {h['label']}")
    print(f"  Match: {h['match']!r}")
    print(f"  Fix: {h['fix']}")
```

---

## Credit

This rule is Zephyr's work, from his X post: https://x.com/i/status/2116643887624430055

The nine tells, examples, and fixes are his exact wording.

The checker and tests were built to enforce it fleetwide.
