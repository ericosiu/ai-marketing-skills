# Content Eval

**Expert panel scoring for content ideation.** Generate, score, and schedule content ideas using a simulated 7-expert panel — so only your best ideas make it to production.

## What It Does

1. **Gathers raw material** — Pulls from podcast transcripts, meeting notes, competitor analysis, and trending topics
2. **Runs competitive scan** — Identifies outlier videos, topic patterns, content gaps across your competitor set
3. **Generates ideas** — 20-30 ideas across long-form video, short-form video, and written formats, mapped to your messaging pillars
4. **Scores via expert panel** — Each idea is evaluated by 7 simulated experts (viral hooks, algorithm, brand, B2B buyer, differentiation, short-form adaptation, engagement)
5. **Ranks and schedules** — Passing ideas (85+ average) get sorted into a 4-week production calendar; everything else goes to the kill list with reasons

## Expert Panel

| # | Expert | What They Score |
|---|--------|-----------------|
| 1 | Viral Hook Expert | Curiosity gap, scroll-stopping power, title strength |
| 2 | Algorithm Expert | CTR potential, watch time, search demand |
| 3 | Founder Brand Strategist | Pillar alignment, authenticity, personal experience |
| 4 | B2B Buyer Persona Expert | Would your target buyer watch this and want what you sell? |
| 5 | Content Differentiation Expert | Is anyone else making this? What's your unique angle? |
| 6 | Short-form Adaptation Expert | Can it clip into 3+ viral Shorts? Quotable moments? |
| 7 | Debate/Engagement Expert | Comments, shares, disagreements potential |

Pass threshold: **85+ average across all 7 experts.** No grade inflation.

## Configuration

Customize the skill by editing the reference files:

| File | Purpose |
|------|---------|
| `references/pillars.md` | Your 3 messaging pillars (what your content ladder maps to) |
| `references/panel.md` | Expert panel definitions and scoring criteria |
| `references/competitors.md` | YouTube competitor channel sets for scanning |
| `references/voice-rules.md` | Your brand's content voice and style rules |

## Usage

Works with Claude Code or any AI coding agent. Trigger with:

- "content eval"
- "score content ideas"
- "weekly content menu"
- "what should I film"
- "rate these video ideas"

You can also pass specific ideas to score directly:
> "Score these content ideas: [your list]"

## Output

- Ranked list of passing ideas with full scoring breakdowns
- 4-week production schedule
- Kill list with reasons (so you learn what doesn't work)
- Competitive gaps found
- Optional: Google Doc export

## Requirements

- Claude Code or any AI coding agent
- Optional: YouTube competitive analysis tool (for Step 2 competitor scanning)
- Optional: Google Workspace API access (for Doc export)

## Getting Started

1. Copy this directory into your Claude Code skills folder
2. Edit `references/pillars.md` with your actual messaging pillars
3. Edit `references/competitors.md` with your competitor YouTube channels
4. Edit `references/voice-rules.md` with your brand voice rules
5. Run: "content eval" in your Claude Code session

## License

MIT
