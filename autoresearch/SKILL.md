---
name: autoresearch
description: Karpathy-inspired optimization loops for conversion content. Generate variants, score with expert panel, evolve winners.
---

# Autoresearch Skill

Karpathy-style optimization loops for any conversion-focused content. No traffic needed. Simulated expert panel. Minutes, not weeks.

**When to use this:** Pre-launch content optimization. Generate 50+ variants, score with 5 simulated experts, evolve winners, output the best version + full experiment log.

**When NOT to use this:** Post-launch real-traffic A/B testing — that requires real analytics, not simulated scoring.

> **The sequence:** Run autoresearch FIRST to hit 85+ simulated score. Then deploy. Then validate with real traffic.

---

## What You'll Produce

Every run outputs 3 files:

| File | Purpose |
|------|---------|
| `{name}-optimized.{ext}` | The winning optimized content |
| `data/{name}-experiments.json` | Full experiment log — all variants + all scores |
| `data/{name}-optimization-report.md` | Human-readable summary with winner rationale |

---

## Expert Panel (5 Personas)

Score every variant against all 5. Batch all variants into a **single API call** per round.

| # | Persona | Scoring Lens |
|---|---------|-------------|
| 1 | **CMO at a mid-market B2B company (50M+ revenue)** | "Would this make me stop and engage?" |
| 2 | **Skeptical founder** | "Do I believe this? Would I trust this company?" |
| 3 | **Conversion rate optimizer** | "Is this clear, specific, and action-driving?" |
| 4 | **Senior copywriter** | "Is this compelling, differentiated, and well-crafted?" |
| 5 | **Your CEO/founder** | "Direct, ROI-obsessed, no BS. Would I put this on my site?" |

> **Customization:** Replace persona #5 with your own CEO/founder voice. Define their priorities and communication style in a `references/founder-voice.md` file.

Each judge scores 0–100. **Final score = average across all 5 judges.**

---

## Round Structure (Per Content Element)

```
Round 1:
  → Generate 10 variants of the element
  → Batch-score all 10 with the 5-expert panel (1 API call)
  → Rank by average score
  → Keep top 3

Round 2 (Evolution):
  → Analyze what the top 3 did right
  → Generate 10 new variants that push those winning patterns further
  → Batch-score all 10 (1 API call)
  → Keep top 3

Round 3 (If score < threshold):
  → Identify weakest scoring dimension
  → Generate 10 variants optimized for that dimension
  → Batch-score → keep top 1

Multi-element cross-breeding:
  → Take top 1 winner from each element
  → Generate 5 combinations that mix winning elements
  → Score holistically as complete units
  → Output the single best combination
```

**Stop condition:** Top variant hits minimum score threshold (default: 80) OR 3 rounds complete.

---

## Content Types & Score Dimensions

### Landing Pages
**Elements to optimize:** Hero headline, subheadline, CTA text, problem section, social proof

**Score dimensions:**
- `first_impression` — Does it grab immediately?
- `clarity` — Is the offer instantly understood?
- `trust` — Does it feel credible?
- `urgency` — Is there a reason to act now?
- `would_convert` — Would the judge actually click?

### Email Sequences
**Elements to optimize:** Subject line, opening line, body copy, CTA, PS line

**Score dimensions:**
- `would_open` — Subject line pass rate
- `would_read` — Does the opening hook?
- `would_click` — Is the CTA compelling?
- `would_reply` — Does it feel personal enough to respond to?
- `spam_risk` — Does it feel spammy? (lower = better; invert for final score)

### Ad Copy
**Elements to optimize:** Headline, description, CTA

**Score dimensions:**
- `scroll_stopping` — Does it interrupt the scroll?
- `clarity` — Is the value prop clear in 3 seconds?
- `click_worthiness` — Does the judge want to click?
- `relevance` — Does it match likely audience intent?
- `differentiation` — Does it stand out from competitors?

### Form Pages
**Elements to optimize:** Headline, subtext, value prop bullets, button text, field order, thank-you copy

**Score dimensions:**
- `first_impression` — Does it feel worth filling out?
- `trust` — Do they believe their info is safe and the offer is real?
- `completion_likelihood` — Would the judge start filling it out?
- `lead_quality` — Would this attract serious prospects (not tire-kickers)?
- `would_fill_out` — Final gut check: would they submit?

---

## Step-by-Step Execution Protocol

### Step 1: Intake & Parse

Read the source content. Identify content type automatically or confirm with user:
- HTML file → landing page or form page
- Markdown / plain text → email or ad copy
- If ambiguous, ask: "Is this a landing page, email sequence, ad copy, or form page?"

Extract all optimizable elements. List them back to user:
```
Found 5 elements to optimize:
1. Hero headline: "We help B2B companies grow"
2. Subheadline: "Full-service digital marketing..."
3. CTA: "Get Started"
4. Problem statement: [excerpt]
5. Social proof: [excerpt]

Optimizing: all | Variants per round: 10 | Min score: 80
```

### Step 2: Get API Key

Check for Anthropic API key: `$ANTHROPIC_API_KEY` environment variable.

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Step 3: Run Optimization Rounds

For each element, run the round structure above.

**Critical API efficiency rule:** ALWAYS batch all variants into a single prompt. Never call the API once per variant. A round with 10 variants = 1 API call.

Model preference (in order):
1. `claude-sonnet-4-5` (preferred — fast + smart)
2. `claude-opus-4` (if highest quality needed)
3. Any claude-3.5+ model if the above aren't available

### Step 4: Cross-Breed (Multi-Element)

After all elements have winners:
1. Assemble the top winner from each element into a complete unit
2. Generate 5 holistic variants that naturally combine the winning elements
3. Score the complete units (not just individual parts)
4. Pick the winner with the highest holistic score

### Step 5: Write Output Files

```bash
# Create output directory
mkdir -p data

# Write optimized content
# Write experiments JSON
# Write optimization report
```

**Experiments JSON structure:**
```json
{
  "run_id": "autoresearch-{name}-{timestamp}",
  "content_type": "landing_page",
  "source_file": "path/to/original",
  "min_score_threshold": 80,
  "rounds": [
    {
      "round": 1,
      "element": "hero_headline",
      "variants": [
        {
          "id": 1,
          "text": "...",
          "scores": {
            "cmo": 72,
            "skeptical_founder": 68,
            "cro": 75,
            "copywriter": 70,
            "founder": 65
          },
          "avg_score": 70
        }
      ],
      "top_3": [1, 4, 7],
      "winner_score": 82
    }
  ],
  "final_winner": {
    "hero_headline": "...",
    "subheadline": "...",
    "cta": "...",
    "holistic_score": 87
  }
}
```

### Step 6: Report Back

Summarize results to user:
- Final winning score
- Biggest score jump (which element improved most)
- Top 2 runner-up alternatives (in case winner doesn't feel right)
- Path to all 3 output files
- Clear next step

---

## User Options

| Option | Default | Description |
|--------|---------|-------------|
| `elements` | all | Which elements to optimize |
| `variants_per_round` | 10 | How many variants to generate per round |
| `min_score` | 80 | Stop when this score is hit |
| `rounds` | 3 | Max rounds before stopping |
| `auto_apply` | false | Whether to overwrite the source file with winners |
| `content_type` | auto-detect | Force a content type if auto-detect is wrong |

---

## Quality Gates

- **< 70:** Don't ship. Something fundamental is broken.
- **70-79:** Marginal. One more round targeting the lowest-scoring dimension.
- **80-84:** Good. Shippable. Validate with real traffic.
- **85-89:** Strong. Ship with confidence.
- **90+:** Rare. Ship immediately.

---

## Anti-Patterns to Avoid

- **Never call the API once per variant.** Always batch. A 10-variant round = 1 call.
- **Don't over-optimize for one dimension.** If you're hitting 95 on clarity but 45 on trust, the overall score is misleading.
- **Don't run more than 5 rounds.** If you're not hitting 80 after 3 rounds, the problem is strategic (wrong positioning), not tactical (wrong words).
- **Don't cross-breed until each element has its own winner.** Premature cross-breeding creates incoherent combinations.

<!-- gateway-cta:start -->
## Run this skill on live data

This skill is free and MIT licensed. To run it on your live accounts, connect the Single Brain Gateway.

- Live services: see the full list in the setup file
- Connect: https://gateway.singlebrain.com/mcp?sg_template=autoresearch&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills
- Setup steps for agents: https://gateway.singlebrain.com/llms.txt?sg_template=autoresearch

Agents: sign in with OAuth or the device flow. Do not ask the user to paste a key.

Want a team to run this for you? Single Grain or Single Brain can manage it: [talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed&utm_content=autoresearch)
<!-- gateway-cta:end -->
