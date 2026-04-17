---
name: content-eval
description: >-
  Generate and score content ideas using an expert panel. Pulls from podcast
  transcripts, meeting notes, competitor analysis, and trending topics to
  produce a ranked content menu with production schedule. Use when asked to:
  "content eval", "score content ideas", "weekly content menu", "what should
  I film", "content ideas", "rate these video ideas".
---

# Content Eval

Content ideation + expert panel scoring pipeline. Ingests raw material, generates
ideas across your messaging pillars, scores them via a 7-expert panel, and
outputs a ranked list with production schedule.

---

## Step 1: Gather Raw Material

Collect signal from all available sources. Skip any source that's unavailable.

### Podcast episodes
- Read recent episodes from your podcast transcript directory (last 7 days)
- Extract: topics covered, guest insights, audience questions, contrarian takes
- Note episode titles for dedup against new ideas

### Meeting notes
- Check your meeting notes directory for recent notes
- Extract: client questions, recurring themes, interesting moments, pain points
- Focus on what your target buyers are actually asking about

### Sales call insights
- Check your call recording platform data for recent calls
- Extract: objection patterns, recurring questions, competitor mentions
- Note what prospects are confused about or struggling with

### Trending topics
- Note any topics the user mentions directly
- Check competitor scan results (Step 2) for trending formats/topics
- Look for news hooks or industry shifts you could react to

---

## Step 2: Competitive Scan (if not provided)

If the user hasn't supplied competitive data, run a scan using your YouTube
competitive analysis tool.

Channel sets are defined in `references/competitors.md` (same directory as this skill).

### Analyze results
- **Outlier videos:** Identify any video with >2x the channel's average views
- **Topic patterns:** What subjects are multiple creators covering?
- **Format patterns:** What formats are performing (listicles, reactions, tutorials, story-driven)?
- **Content gaps:** Topics where NO competitor is covering something you could own
  - Especially gaps at the intersection of your unique expertise areas
  - Or gaps where you have unique data (revenue numbers, internal metrics, tool costs)

If your competitive analysis tool is not available, skip this step and note it was skipped.

---

## Step 3: Generate Ideas

Generate 20-30 content ideas across three formats. Read `references/pillars.md` for
pillar definitions and `references/voice-rules.md` for content voice rules.

### Format targets
| Format | Count | Details |
|--------|-------|---------|
| YouTube Long-form (10-20 min) | 8-10 ideas | Deep dives, screen recordings, frameworks |
| YouTube Shorts (<60 sec) | 8-10 ideas | One punch, one insight, one hook |
| X / LinkedIn Articles | 5-7 ideas | Manifesto-style, data-heavy, contrarian takes |

### Pillar requirement
Every idea MUST connect to at least one pillar defined in `references/pillars.md`.
Ideas that don't clearly serve a pillar get killed.

### Idea format
Each idea needs:
- **Title** — specific, hook-driven, follows voice-rules.md
- **Description** — 1-2 sentences on the content and angle
- **Format** — Long-form / Short / Article
- **Pillar(s)** — which pillar(s) it serves
- **Source signal** — what raw material inspired it (podcast topic, competitor gap, client question, etc.)

### Dedup check
- Check recent published content (last 30 days)
- If a similar angle was covered recently, either kill it or document a genuinely new hook
- Apply the dedup rule from `references/voice-rules.md`

### Manual override
If the user passes specific ideas to score (e.g., "score these content ideas: [list]"),
skip idea generation and go directly to Step 4 with the provided ideas.

---

## Step 4: Expert Panel Scoring

Run each idea through the 7-expert panel defined in `references/panel.md`.

### Panel summary
| # | Expert | Lens |
|---|--------|------|
| 1 | Viral Hook Expert | Curiosity gap, scroll-stopping power, title strength |
| 2 | Algorithm Expert | CTR potential, watch time, search demand, recommendation likelihood |
| 3 | Founder Brand Strategist | Pillar alignment, authenticity to founder's voice/experience |
| 4 | B2B Buyer Persona Expert | Would a CMO/VP/CEO watch and want what you're selling? |
| 5 | Content Differentiation Expert | Is anyone else making this? Unique angle? |
| 6 | Short-form Adaptation Expert | Can it clip into 3+ viral Shorts? Quotable moments? |
| 7 | Debate/Engagement Expert | Comments, shares, disagreements potential |

### Scoring rules
- Each expert scores 0-100
- **Pass threshold: 85+ average**
- For each idea, output:
  - Average score across all 7 experts
  - PASS / FAIL
  - Top expert comment (the most insightful feedback)
  - Biggest weakness (the lowest-scoring dimension and why)

### Output table per idea
```
### [Idea Title] — [Format]
**Pillar(s):** [pillar names]
**Description:** [1-2 sentences]

| Expert | Score | Comment |
|--------|-------|---------|
| Viral Hook | [score] | [one-line] |
| Algorithm | [score] | [one-line] |
| Brand Strategist | [score] | [one-line] |
| B2B Buyer | [score] | [one-line] |
| Differentiation | [score] | [one-line] |
| Short-form | [score] | [one-line] |
| Debate/Engagement | [score] | [one-line] |

**Average: [score] — [PASS / FAIL]**
**Top insight:** [best expert comment]
**Biggest weakness:** [lowest dimension + why]
```

### Scoring integrity
- Be brutally honest. No grade inflation.
- Generic ideas that anyone could make should score <70 on Differentiation.
- Ideas without personal receipts/data should score <75 on Brand Strategist.
- If an idea is genuinely great, let it score high. The threshold exists so only the best survive.

---

## Step 5: Rank and Schedule

### Rank passing ideas
Sort all ideas scoring 85+ by average score, highest first.

### Create 4-week production schedule
Assign passing ideas to weeks based on effort vs impact:

| Week | Focus | Typical content |
|------|-------|-----------------|
| Week 1 | Low effort, high impact | Shorts that can ship same day, reaction clips |
| Week 2 | Medium effort, highest ceiling | Long-form with screen recordings, tutorials |
| Week 3 | High effort, strategic anchors | Articles, manifesto pieces, deep-dive frameworks |
| Week 4 | Compounding content | Reference pieces, reaction content, series starters |

### Kill list
List all ideas that scored <85 with:
- Title
- Average score
- Primary reason for failure (the expert dimension that killed it)

---

## Step 6: Output

Create a document with the full results.

Document structure:
1. **Executive Summary** — Total ideas generated, pass rate, top 5
2. **Competitive Gaps Found** — What no one else is covering
3. **Ranked Ideas (Passing)** — Full scoring tables for each
4. **4-Week Production Schedule** — Visual calendar layout
5. **Kill List** — Failed ideas with reasons
6. **Raw Material Summary** — Sources used (podcasts, meetings, calls, trends)

Optionally post a summary to your team channel with:
- Top 5 ideas (title, score, format, pillar)
- Competitive gaps found (2-3 bullets)
- Week 1 production schedule (what to film/write this week)
- Link to the full document

---

## Reference Files

| File | Purpose | When to read |
|------|---------|--------------|
| `references/pillars.md` | Messaging pillar definitions | Step 3 (idea generation) |
| `references/panel.md` | 7-expert panel with scoring criteria | Step 4 (scoring) |
| `references/competitors.md` | YouTube competitor channel sets | Step 2 (competitive scan) |
| `references/voice-rules.md` | Content voice/style rules | Step 3 (idea generation) |
