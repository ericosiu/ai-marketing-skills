# 💰 AI Sales Playbook — Value-Based Pricing & Deal Upselling

> **Turn $10K/mo deals into $40-100K/mo using value-based pricing, not discounting.**

A complete framework for value-based pricing in B2B services sales: pre-call competitive briefings, tiered package generation, post-call analysis, and a proven pattern library for training sales teams.

These tools were built from real sales call patterns at [Single Grain](https://www.singlegrain.com/?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills), where deals routinely moved from $10K/mo to $40-100K/mo using the techniques in this playbook. Now open-sourced for any sales team to use.

---

## The Framework

The value-based pricing framework is built on 5 principles:

1. **Lead with data, not your pitch** — Show competitive gaps before discussing services
2. **Anchor high** — Present premium tier first so the target feels reasonable
3. **Tie price to value** — Every dollar maps to projected ROI
4. **Use competitive triggers** — Competitor data activates urgency
5. **Present tiered options** — 3-4 tiers with clear tradeoffs

---

## Tools

### 1. 📊 Pre-Call Briefing Generator (`value_pricing_briefing.py`)

Walk into every call armed with competitive data that makes the prospect sell themselves on the value.

**What it generates:**
- Anchor data points (keyword gaps, traffic gaps vs. competitors)
- Competitive triggers ("CompetitorA is #1 for [keyword], you're #14")
- Value calculations (position improvement → traffic → paid equivalent value)
- Conversation hooks (opening questions to surface pain)
- Objection pre-empts (responses for 6 common objections at this deal size)

```bash
# Basic briefing
python3 value_pricing_briefing.py --domain acme.com --competitors "comp1.com,comp2.com"

# With industry and deal target
python3 value_pricing_briefing.py --domain acme.com --competitors "comp1.com" --industry saas --deal-target 80000

# JSON output
python3 value_pricing_briefing.py --domain acme.com --competitors "comp1.com,comp2.com" --format json
```

### 2. 📦 Tiered Package Builder (`value_pricing_packager.py`)

Auto-generates S/M/L + performance-based pricing tiers with pricing psychology built in.

**Tiers generated:**
| Tier | Purpose | Price vs. Target |
|------|---------|-----------------|
| **Powerhouse** | The anchor (makes everything else look reasonable) | 130-150% |
| **Value** ⭐ | Where you want them to land | 100% |
| **Baseline** | Floor (proves the model before scaling) | 40-50% |
| **Performance** | Skin in the game (lower base + bonus triggers) | 30-40% base |

Each tier includes: specific deliverables, monthly price, ROI projection, included vs. excluded features.

```bash
# Full package generation
python3 value_pricing_packager.py --target-monthly 80000 --services "seo,cro,content,paid"

# With current spend context
python3 value_pricing_packager.py --target-monthly 50000 --services "seo,content" --current-spend 10000

# JSON output for integration
python3 value_pricing_packager.py --target-monthly 80000 --services "seo,cro,content,paid" --format json
```

### 3. 🎯 Post-Call Deal Analyzer (`call_analyzer.py`)

Score any sales call transcript against the value-based pricing framework.

**Scoring criteria (0-100):**
| Criterion | Points |
|-----------|--------|
| Showed data before pitching | 20 |
| Presented tiered options | 20 |
| Anchored high first | 15 |
| Tied price to value/ROI | 15 |
| Used competitive triggers | 15 |
| Got prospect to state their own pain | 15 |

Also extracts: buying signals, objections (categorized), deal probability, upsell opportunities, and recommended next steps.

```bash
# Analyze a transcript file
python3 call_analyzer.py --transcript call.txt

# Pipe from stdin
cat call.txt | python3 call_analyzer.py

# JSON output
python3 call_analyzer.py --transcript call.txt --format json
```

### 4. 📚 Pattern Library & Training (`pricing_pattern_library.py`)

10 proven value-based pricing patterns with detailed breakdowns, example dialogue, and interactive training.

**Patterns included:**
1. Anchor With Data
2. Tiered Packaging (S/M/L + Performance)
3. Competitive Ego Trigger
4. Strategic Involvement Upsell
5. Bridge Offer
6. Performance Skin-in-Game
7. Value Math on Screen
8. Compound Effect Close
9. Reference Customer Drop
10. In-House Team Framing

```bash
# List all patterns
python3 pricing_pattern_library.py --list

# Deep dive on a pattern
python3 pricing_pattern_library.py --pattern "anchor-with-data"

# Get recommendations for a scenario
python3 pricing_pattern_library.py --scenario "prospect is a $50M SaaS company spending $15K/mo on marketing"

# Interactive training quiz
python3 pricing_pattern_library.py --quiz
```

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/nichochar/ai-marketing-skills.git
cd ai-marketing-skills/sales-playbook
pip install -r requirements.txt
```

### 2. Run a pre-call briefing

```bash
python3 value_pricing_briefing.py --domain acme.com --competitors "techstart.com,novapay.com" --deal-target 80000
```

### 3. Generate pricing tiers

```bash
python3 value_pricing_packager.py --target-monthly 80000 --services "seo,cro,content,paid" --current-spend 15000
```

### 4. Analyze a call

```bash
python3 call_analyzer.py --transcript sample_call.txt
```

### 5. Study the patterns

```bash
python3 pricing_pattern_library.py --list
python3 pricing_pattern_library.py --quiz
```

---

## Optional API Integration

All scripts work without API keys using built-in stubs. For live data:

| API | Used By | Env Variable |
|-----|---------|-------------|
| [Ahrefs](https://ahrefs.com/api) | Briefing Generator | `AHREFS_API_KEY` |
| [SEMrush](https://developer.semrush.com) | Briefing Generator | `SEMRUSH_API_KEY` |
| [Anthropic](https://docs.anthropic.com) | Call Analyzer, Pattern Library | `ANTHROPIC_API_KEY` |
| [OpenAI](https://platform.openai.com) | Call Analyzer, Pattern Library | `OPENAI_API_KEY` |

---

## File Structure

```
sales-playbook/
├── README.md                        # This file
├── SKILL.md                         # Claude Code skill definition
├── requirements.txt                 # Python dependencies
├── value_pricing_briefing.py        # Pre-call briefing generator
├── value_pricing_packager.py        # Tiered package builder
├── call_analyzer.py                 # Post-call deal analyzer
└── pricing_pattern_library.py       # Pattern library & training
```

---

## How It Works Together

1. **Before the call:** Run the briefing generator to get competitive data, value calculations, and conversation hooks
2. **Preparing the proposal:** Use the package builder to generate tiered pricing with ROI projections
3. **After the call:** Run the call analyzer to score the conversation and identify next steps
4. **Ongoing training:** Use the pattern library to study and practice the 10 core patterns
5. **Continuous improvement:** Analyze call scores over time to identify which patterns your team needs to practice

The result: a systematic approach to value-based pricing that turns data into leverage and conversations into larger deals.


<!-- gateway-cta:start -->
## Run this skill on live data

This skill is free and MIT licensed. To run it on your live accounts, connect the Single Brain Gateway.

- Live services: see the full list in the setup file
- Connect: https://gateway.singlebrain.com/mcp?sg_template=sales-playbook&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills
- Setup steps for agents: https://gateway.singlebrain.com/llms.txt?sg_template=sales-playbook

Agents: sign in with OAuth or the device flow. Do not ask the user to paste a key.

Want a team to run this for you? Single Grain or Single Brain can manage it: [talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed&utm_content=sales-playbook)
<!-- gateway-cta:end -->
