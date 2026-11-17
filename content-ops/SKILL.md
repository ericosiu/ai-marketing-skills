---
name: content-ops
description: Use when you need expert panel scoring to improve content quality before publishing. Auto-assembled expert panels with iterative feedback loops.
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

# Expert Panel

General-purpose scoring and iterative improvement engine. Auto-assembles the
right experts for whatever is being evaluated, scores it, and loops until 90+.

---

## Step 1: Intake — Understand What's Being Scored

Collect or infer from context:

1. **Content/artifact** — The thing(s) to score (paste, file path, or URL)
2. **Content type** — Copy, sequence, landing page, strategy, title, chart, candidate eval, etc.
3. **Offer context** — What's being sold/promoted? To whom? What domain/industry?
4. **Variants** — Are there multiple versions to compare? (A/B/C)
5. **Source skill** — Is this output from another skill? (e.g., cold-outbound-optimizer)
   If yes, note the source for feedback-to-source routing in Step 6.

If context is obvious from the conversation, don't ask — just proceed.

---

## Step 2: Auto-Assemble the Expert Panel

Build a panel of **7–10 experts** tailored to the content type and domain.

### Assembly rules

1. **Start with content-type experts.** Read `experts/` directory for pre-built panels matching
   the content type. If an exact match exists (e.g., `experts/linkedin.md` for a LinkedIn post),
   use it as the base.

2. **Add domain/offer experts.** Based on the offer context, add 1–3 experts who understand
   the specific industry or domain. Examples:
   - Scoring bakery marketing → add Food & Beverage Marketing Expert
   - Scoring SaaS landing page → add SaaS Conversion Expert
   - Scoring recruiting outreach → add Agency Recruiter + Talent Market Expert
   - Scoring medical device copy → add Healthcare Compliance Expert

3. **Always include these two:**
   - **AI Writing Detector** — See `experts/humanizer.md`. Weight: 1.5x. Non-negotiable.
   - **Brand Voice Match** — Checks alignment with the configured brand voice and
     known rejection patterns from `references/patterns.md` (if present).

4. **Check learned patterns.** If `references/patterns.md` exists, read it. If any patterns
   apply to this content type, brief the panel on them. Dock points for known-bad patterns.

5. **Cap at 10 experts.** If you have more than 10, merge overlapping roles.

### Panel output format
List each expert with: Name, lens/focus, what they check.

---

## Step 3: Select Scoring Rubric

Choose the appropriate rubric from `scoring-rubrics/`:

| Content type | Rubric file |
|---|---|
| Blog, social, email, newsletter, scripts | `scoring-rubrics/content-quality.md` |
| Strategy, recommendations, analysis | `scoring-rubrics/strategic-quality.md` |
| Landing pages, ads, CTAs | `scoring-rubrics/conversion-quality.md` |
| Charts, data viz, infographics | `scoring-rubrics/visual-quality.md` |
| Candidate evaluations | `scoring-rubrics/evaluation-quality.md` |
| Other | Synthesize a rubric from the two closest matches |

Read the selected rubric file for detailed criteria and point allocation.

---

## Step 4: Score — Recursive Loop Until 90+

**Target: 90/100 across all experts. Non-negotiable. Max 3 rounds.**

### Each round produces:

```
## Round [N] — Score: [AVG]/100

| Expert | Score | Key Feedback |
|--------|-------|--------------|
| [Name] | [0-100] | [One-line rationale] |
| ... | ... | ... |

**Aggregate:** [weighted average — humanizer at 1.5x]
**Top 3 weaknesses:** [ranked]
**Changes made:** [specific edits addressing each weakness]
```

Then the revised content/artifact.

### Rules

- Scores must be brutally honest. No padding to 90.
- Humanizer score weighted 1.5x in the aggregate.
- If aggregate < 90: identify top 3 weaknesses → revise → next round.
- If aggregate ≥ 90: finalize and proceed to output.
- After 3 rounds, if still < 90: return best version with honest score + note on what's
  holding it back.
- Show ALL rounds in output — the iteration trail is part of the value.

### Variant comparison mode

When scoring multiple variants (A/B/C):
- Score each variant independently through the full panel.
- After scoring, rank variants by aggregate score.
- If top variant is < 90, iterate on the best one (don't iterate all of them).

---

## Step 5: Output Format

### Winner + Score (always at top)

```
## 🏆 Result: [SCORE]/100 — [PASS ✅ | NEEDS WORK ⚠️]

[Final content/artifact here]

**Iterations:** [N] rounds
**Panel:** [Expert names, comma-separated]
```

If variants: show winner first, then runner-up scores.

```
## 🏆 Winner: Variant [X] — [SCORE]/100

[Winning content]

### Runner-up scores
- Variant A: 87/100
- Variant B: 82/100
- Variant C: 91/100 ← Winner
```

### Feedback History (below the result)

Show full scoring rounds.

```
---
<details>
<summary>📊 Scoring History (N rounds)</summary>

[All round tables from Step 4]

</details>
```

---

## Step 6: Feedback-to-Source (When Scoring Another Skill's Output)

When the scored content came from another skill, generate a **Source Improvement Brief**:

```
## 🔁 Feedback for [Source Skill]

### What scored low
- [Pattern]: [Specific example from this content]

### Suggested skill improvements
- [Concrete change to the source skill's process/rubric/prompt]

### Patterns to add to source skill
- [Any recurring weakness that should become a rule]
```

This brief can be used to update the source skill's SKILL.md or rubrics.

---

## Step 7: Memory — Learn from Approvals and Rejections

After the user approves or rejects panel output:

### On approval (score ≥ 90, user accepts)
Note what worked. No action needed unless a new positive pattern emerges.

### On rejection (user overrides the panel or rejects 90+ content)
1. Ask why (or infer from context).
2. Add a new pattern to `references/patterns.md` using this format:

```markdown
## [Pattern Name]
- **Type:** rejection | preference | override
- **Content types:** [which types this applies to]
- **Rule:** [What to always/never do]
- **Example:** [The specific instance that triggered this]
- **Date:** [YYYY-MM-DD]
- **Point dock:** [-N points when detected]
```

3. Confirm: "Added pattern: [one-line summary]. Panel will dock [N] points for this going forward."

### Pattern enforcement
Every scoring round, check `references/patterns.md` against the content. Apply point docks
before expert scoring begins. This means known-bad patterns are penalized even if individual
experts miss them.

---

## Reference Files

| File | Purpose | When to read |
|---|---|---|
| `experts/humanizer.md` | AI writing detection rubric (24 patterns) | Every scoring run |
| `experts/[domain].md` | Pre-built expert panels for common domains | When domain matches |
| `scoring-rubrics/content-quality.md` | Content scoring rubric | Content scoring |
| `scoring-rubrics/strategic-quality.md` | Strategy scoring rubric | Strategy scoring |
| `scoring-rubrics/conversion-quality.md` | Landing page/ad/CTA rubric | Conversion scoring |
| `scoring-rubrics/visual-quality.md` | Chart/data viz/infographic rubric | Visual scoring |
| `scoring-rubrics/evaluation-quality.md` | Candidate/assessment rubric | Eval scoring |
| `references/patterns.md` | Learned rejection patterns | Every scoring run |
| `references/expert-assembly.md` | Domain-expert examples for auto-assembly | When building unfamiliar panels |

<!-- gateway-cta:start -->
## Run this skill on live data

This skill is free and MIT licensed. To run it on your live accounts, connect the Single Brain Gateway.

- Live services: see the full list in the setup file
- Connect: https://gateway.singlebrain.com/mcp?sg_template=content-ops&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills
- Setup steps for agents: https://gateway.singlebrain.com/llms.txt?sg_template=content-ops

Agents: sign in with OAuth or the device flow. Do not ask the user to paste a key.

Want a team to run this for you? Single Grain or Single Brain can manage it: [talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed&utm_content=content-ops)
<!-- gateway-cta:end -->
