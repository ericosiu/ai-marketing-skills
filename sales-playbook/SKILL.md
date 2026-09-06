---
name: sales-playbook
description: Prepare sales calls, build value-based pricing packages, and review sales transcripts. Use for proposals, deal preparation, and pricing analysis.
---

# AI Sales Playbook — Value-Based Pricing & Deal Upselling

## Preamble (runs on skill start)

```bash
# Version check (silent if up to date)
python3 telemetry/version_check.py 2>/dev/null || true

# Telemetry opt-in (first run only, then remembers your choice)
python3 telemetry/telemetry_init.py 2>/dev/null || true
```

> **Privacy:** This skill logs usage locally to `~/.ai-marketing-skills/analytics/`. Remote telemetry is opt-in only. No code, file paths, or repo content is ever collected. See `telemetry/README.md`.

---

Framework for value-based pricing that moves deals from $10K/mo → $40-100K/mo. Pre-call briefings, tiered package generation, post-call analysis, and a pattern library for training sales teams on proven pricing techniques.

## When to Use

Use this skill when:
- Preparing for a sales call and need competitive data to anchor on value
- Building tiered pricing proposals for prospects at different deal sizes
- Analyzing sales call transcripts to score against the value-based pricing framework
- Training sales reps on proven pricing patterns and objection handling
- Upselling existing deals by identifying missed value levers

## Tools

### Pre-Call Preparation

| Script | Purpose | Key Command |
|--------|---------|-------------|
| `value_pricing_briefing.py` | Generate pre-call briefing with competitive data, value calcs, and conversation hooks | `python3 value_pricing_briefing.py --domain acme.com --competitors "comp1.com,comp2.com"` |
| `value_pricing_packager.py` | Generate tiered S/M/L + performance pricing packages | `python3 value_pricing_packager.py --target-monthly 80000 --services "seo,cro,content,paid"` |

### Post-Call Analysis

| Script | Purpose | Key Command |
|--------|---------|-------------|
| `call_analyzer.py` | Score a call transcript against the value-based pricing framework | `python3 call_analyzer.py --transcript call.txt` |
| `pricing_pattern_library.py` | Reference library of 10 proven pricing patterns + training mode | `python3 pricing_pattern_library.py --list` |

## Configuration

All scripts use environment variables for API keys:

### Optional Environment Variables

- `AHREFS_API_KEY` — Ahrefs API key (Briefing Generator, optional — uses stubs without it)
- `SEMRUSH_API_KEY` — SEMrush API key (Briefing Generator, optional — uses stubs without it)
- `ANTHROPIC_API_KEY` — Anthropic API key (Call Analyzer, Pattern Library scenario mode)
- `OPENAI_API_KEY` — OpenAI API key (alternative to Anthropic for LLM features)

Scripts work without API keys using built-in stubs and sample data for testing.

## Key Concepts

### The Value-Based Pricing Framework

1. **Lead with data, not your pitch** — Show the prospect their competitive gaps before discussing services
2. **Anchor high** — Present the premium tier first so the target tier feels reasonable
3. **Tie price to value** — Every dollar of investment maps to projected ROI
4. **Use competitive triggers** — Competitor rankings activate urgency without being pushy
5. **Present tiered options** — 3-4 tiers with clear tradeoffs, always including a performance option

### Pricing Framework Score (0-100)

The call analyzer scores calls against these criteria:
- Showed data before pitching (20 pts)
- Presented tiered options (20 pts)
- Anchored high first (15 pts)
- Tied price to value/ROI (15 pts)
- Used competitive triggers (15 pts)
- Got prospect to state their own pain (15 pts)

## Dependencies

- Python 3.9+
- `requests` (for API integrations)
- No other external dependencies
