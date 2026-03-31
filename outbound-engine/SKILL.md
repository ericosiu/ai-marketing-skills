---
name: cold-outbound-optimizer
description: Design, analyze, and optimize cold outbound email campaigns for Instantly. Handles end-to-end ICP definition, expert panel scoring (recursive to 90+), sequence copywriting, infrastructure audit, capacity planning, and implementation docs. Use when asked to build cold outbound sequences, optimize cold email, analyze outbound campaigns, build sales sequences, build Instantly sequences, create cold outbound strategies, or design email campaigns. Supports both "start from scratch" and "optimize existing" modes.
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

# Cold Outbound Optimizer

---

## Startup: Determine Mode

Ask the user:
1. Do you have an **existing Instantly account** with campaigns to audit, or are you **starting from scratch**?
2. Do you have an **Instantly API key**? (Required for audit mode.)

If API key provided → run `scripts/instantly-audit.py` to pull campaigns, account inventory, and warmup scores before proceeding.

---

## Phase 1: Discovery & Audit

### 1A — Infrastructure Check (if API key available)
Run `python3 scripts/instantly-audit.py --api-key <KEY>` and report:
- Active campaigns (name, status, reply rate, open rate)
- Sending accounts (count, warmup score, daily limit)
- Domain inventory
- Warmup gaps: any account with score <80 or <14 days warmup → flag as NOT ready

### 1B — Performance Data
- Pull campaign analytics from Instantly
- Ask: "Do you have a spreadsheet with historical outbound data?" If yes, request link.

### 1C — ICP Definition
If no ICP defined, collect:
- **Titles:** Who are you targeting? (e.g., VP Marketing, Head of Growth)
- **Industries:** Which verticals?
- **Company size:** Employee count or revenue range?
- **Revenue floor:** Minimum ARR/revenue to qualify?
- **Anti-ICP:** Who to explicitly exclude?

Use `references/icp-template.md` as the collection template.

### 1D — Business Context
Collect:
- What do you sell? (One sentence, no jargon)
- What's the primary offer? (Free trial, audit, demo, consultation)
- Real URLs to reference (pricing page, case studies, relevant content)
- Any proof points? (Client results, stats, social proof)

### 1E — Expert Panel Config
Default: 10 experts (see `references/expert-panel.md`).
Ask: "Any industry-specific experts to add, or panelists to swap?" Confirm roster before scoring.

---

## Phase 2: Expert Panel Recursive Scoring

**Target: 90/100. Non-negotiable. Iterate until reached.**

### Round Structure
Each round produces:
1. **Score table** — all 10 panelists, individual score (0-100), one-line rationale
2. **Aggregate score** — average of all 10
3. **Top weaknesses** — ranked list of what's holding the copy back
4. **Changes made** — specific edits addressing each weakness
5. **Updated copy** — full revised sequence after changes

### Scoring Criteria (per panelist's lens — see `references/expert-panel.md`)
- Subject line curiosity / open rate potential
- First sentence pattern interrupt
- Body clarity and brevity
- CTA softness and specificity
- Sequence flow and follow-up logic
- Deliverability risk signals (spam words, link density)
- Personalization believability

### Rules
- Scores must be brutally honest. No padding to 90 without earning it.
- If round score < 90: identify top 3 weaknesses, revise copy, run next round.
- If round score ≥ 90: finalize copy and proceed to deliverables.
- Show every round in the final doc — the iteration trail is part of the value.

---

## Phase 3: Deliverables

### Strategy Doc
Create a document (Google Doc, Notion, or markdown) with:

1. **Pre-Analysis / Brutal Truth** — what the existing campaigns are doing wrong (or baseline if starting from scratch)
2. **ICP Summary** — confirmed targeting parameters
3. **Infrastructure Status** — account inventory, warmup readiness, capacity math
4. **Scoring Rounds** — full panel vote tables for every round
5. **Final Email Copy** — all steps for all campaigns, Instantly-ready format
6. **Implementation Plan** — step-by-step setup instructions
7. **Capacity Math** — accounts × daily send rate = pipeline projections
8. **Weekly Metrics Targets** — open rate, reply rate, positive reply rate, meetings booked
9. **STOP List** — what to kill immediately
10. **START List** — what to launch first

### Format Rules for Final Copy
Follow all rules in `references/instantly-rules.md` and `references/copy-rules.md`.

### Human Review Gate
**Do NOT push anything to Instantly automatically.** The doc is for human review. Get explicit approval before any API writes.

### Iteration
After review, collect feedback and re-run scoring on revised copy if needed.

---

## Capacity Math Formula

```
Accounts ready (score ≥80, ≥14 days warmup) × 30 emails/day = conservative daily volume
Accounts ready × 50 emails/day = aggressive daily volume
Daily volume × 22 working days = monthly send capacity
Monthly sends × expected reply rate = expected replies
Expected replies × qualification rate = pipeline opportunities
```

---

## Weekly Metrics Targets (Baselines)

| Metric | Good | Great |
|--------|------|-------|
| Open rate | 40%+ | 60%+ |
| Reply rate | 3%+ | 7%+ |
| Positive reply rate | 1%+ | 3%+ |
| Meeting rate | 0.5%+ | 1.5%+ |

Adjust targets based on niche and offer. Cold traffic to a free audit converts differently than a paid trial.

---

## Add-On Recommendations (mention but don't build)

- **LinkedIn automation:** HeyReach or similar for multi-channel sequences. Separate workflow.
- **Lead enrichment:** Clay or Apollo for personalization data before upload.
- **Lead pipeline:** Use `scripts/lead-pipeline.py` for Apollo → LeadMagic → Instantly automation.

---

## Reference Files

| File | Purpose |
|------|---------|
| `references/instantly-rules.md` | Variable syntax, sequence structure, deliverability rules |
| `references/expert-panel.md` | Default 10-expert roster with scoring lenses |
| `references/copy-rules.md` | Email copy rules (first sentence, CTA, stats framing) |
| `references/icp-template.md` | ICP data collection template |
| `scripts/instantly-audit.py` | Pulls campaigns, accounts, warmup scores via Instantly v2 API |
| `scripts/lead-pipeline.py` | End-to-end lead sourcing pipeline |
| `scripts/competitive-monitor.py` | Competitor tracking and intelligence |
| `scripts/cross-signal-detector.py` | Multi-source signal detection |
| `scripts/cold-outbound-sender.py` | Send approved outbound emails |
