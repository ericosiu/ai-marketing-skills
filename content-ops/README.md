# AI Content Ops

**Ship content that scores 90+ every time. Automatically.**

Most content teams publish and pray. This pipeline scores, gates, and iterates every piece of content through an AI expert panel before it goes live. Nothing ships below 90/100.

## What's Inside

### 🎯 Expert Panel (`SKILL.md`)
Claude Code skill that auto-assembles a panel of 7-10 domain experts tailored to whatever you're scoring. Works on:
- Blog posts, social content, email sequences
- Landing pages, ads, CTAs
- Strategy docs, pitch decks, charts
- Recruiting outreach, vendor evaluations
- Literally anything that needs a quality gate

The panel scores your content, identifies weaknesses, revises, and loops until every expert scores 90+. Max 3 rounds. Includes a 1.5x-weighted AI Writing Detector that catches all 24 known AI writing patterns.

### 🚦 Content Quality Gate (`scripts/content-quality-gate.py`)
CI/CD-style gate for your content pipeline. Runs the quality scorer on a batch of drafts and filters out anything below threshold. Nothing publishes without passing.

### 📊 Content Quality Scorer (`scripts/content-quality-scorer.py`)
Automated scoring engine with 5 dimensions:
- **Voice similarity** (35%) — matches your brand voice patterns
- **Specificity** (25%) — real numbers, named entities, concrete examples
- **AI slop penalty** (20%) — detects and penalizes 50+ banned AI words and 8 AI writing patterns
- **Length appropriateness** (10%) — platform-specific character limits
- **Engagement potential** (10%) — hooks, CTAs, debate invitations

### 🧠 Editorial Brain (`scripts/editorial-brain.py`)
Two-pass LLM analysis for finding clip-worthy moments in video transcripts:
1. **Pass 1**: Scans transcript chunks for candidate moments (hook → build → payoff arcs)
2. **Pass 2**: Deep-scores each candidate on hook/build/payoff/clean-cut (0-100)
3. Only 90+ clips get cut

Fundamentally different from keyword matching. Thinks like a human editor.

### ⛏️ Quote Mining Engine (`scripts/quote-mining-engine.py`)
Scans podcast RSS feeds and meeting notes to extract quotable, contrarian, viral-worthy moments. Scoring heuristics:
- Contrarian signals (wrong, myth, overrated, secret...)
- Specificity signals ($amounts, percentages, multipliers)
- Emotional triggers (fear, love, shocking, AI...)
- Shareability signals (how to, framework, lesson learned...)

### 🔄 Content Transform (`scripts/content-transform.py`)
Repurposes long-form content into platform-native formats:
- **X threads/posts** — punchy, data-driven, with ASCII diagrams
- **LinkedIn posts** — hook before the fold, story arc, engagement CTA
- **YouTube Short scripts** — HOOK/SETUP/PAYOFF/CTA structure with visual cues
- **Newsletter sections** — scannable, value-dense, "why this matters"

Includes optional expert panel integration for iterative quality improvement.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env with your API keys

# 3. Score a batch of content drafts
python scripts/content-quality-scorer.py --input drafts.json --verbose

# 4. Run the quality gate
python scripts/content-quality-gate.py --input drafts.json --threshold 70

# 5. Mine quotes from your podcast RSS
python scripts/quote-mining-engine.py --days 90 --min-score 60

# 6. Find clip-worthy moments in a video
python scripts/editorial-brain.py --url "https://youtube.com/watch?v=..." --min-score 90

# 7. Transform content atoms into platform drafts
python scripts/content-transform.py --atoms atoms.json --top-n 10
```

## Configuration

All scripts use environment variables for configuration. See `.env.example` for the full list.

### Voice Customization
The quality scorer and content transformer use configurable voice patterns. Edit these in your `.env` or pass custom config files:

- `VOICE_MARKERS` — regex patterns that signal your brand voice
- `BANNED_WORDS` — AI slop vocabulary to penalize
- `PLATFORM_LIMITS` — character limits per platform

### Scoring Weights
Adjust scoring weights via a JSON config file:
```json
{
  "weights": {
    "voice_similarity": 0.35,
    "specificity": 0.25,
    "slop_penalty": 0.20,
    "length_appropriateness": 0.10,
    "engagement_potential": 0.10
  },
  "threshold": 70
}
```

## Expert Panel Domains

Pre-built expert panels included:
- `experts/humanizer.md` — AI writing detection (24 patterns, mandatory)
- `experts/x-articles.md` — X/Twitter long-form posts
- `experts/linkedin.md` — LinkedIn posts
- `experts/newsletter.md` — Email newsletters
- `experts/youtube-shorts.md` — YouTube Shorts scripts
- `experts/instagram.md` — Instagram visual content
- `experts/podcast-quotes.md` — Podcast quote cards
- `experts/recruiting.md` — Recruiting outreach
- `experts/seo-strategy.md` — SEO strategy docs

Scoring rubrics:
- `scoring-rubrics/content-quality.md` — Blog, social, email, scripts
- `scoring-rubrics/strategic-quality.md` — Strategy and analysis
- `scoring-rubrics/conversion-quality.md` — Landing pages, ads, CTAs
- `scoring-rubrics/visual-quality.md` — Charts, infographics, slides
- `scoring-rubrics/evaluation-quality.md` — Candidate/vendor evaluations

## Input Formats

### Content Drafts (for scorer/gate)
```json
{
  "drafts": [
    {
      "id": "draft-001",
      "platform": "x",
      "draft": "Your content text here..."
    }
  ]
}
```

### Content Atoms (for transformer)
```json
{
  "atoms": [
    {
      "id": "atom-001",
      "content": "Long-form source content...",
      "tags": ["AI", "marketing"],
      "platforms_missing": ["x", "linkedin"],
      "repurpose_score": 8
    }
  ]
}
```

## Architecture

```
Content Source → Content Transform → Quality Scorer → Quality Gate → Publish
                      ↑                    ↓
                Expert Panel ←── Revision Loop (max 3 rounds)
```

The pipeline is modular. Use any script standalone or wire them together.

## License

MIT


---

<div align="center">

**🧠 [Want these built and managed for you? →](https://singlebrain.com/?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills)**

*This is how we build agents at [Single Brain](https://singlebrain.com/?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) for our clients.*

</div>
