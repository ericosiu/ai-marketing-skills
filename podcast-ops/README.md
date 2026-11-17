# AI Podcast Ops

**One podcast episode in, 15-20 content pieces out. Scored, deduplicated, and scheduled.**

Most podcast teams publish an episode and maybe pull one audiogram. This pipeline treats every episode as a content mine — extracting narrative arcs, quotable moments, controversial takes, data points, and stories, then generating platform-native content for every channel with viral scoring and deduplication.

## What's Inside

### 🎙️ Podcast-to-Everything Pipeline (`podcast_pipeline.py`)
End-to-end pipeline that ingests podcast episodes (via RSS feed or raw transcript) and produces a full cross-platform content calendar.

**Ingest modes:**
- RSS feed → auto-download + Whisper transcription
- Raw transcript file (text, SRT, VTT)
- Batch mode: process last N episodes from a feed

**Content generated per episode:**
- 3-5 short-form video clip suggestions (with timestamps + hooks)
- 2-3 Twitter/X thread outlines
- 1 LinkedIn article draft
- 1 newsletter section
- 3-5 quote cards (text overlays for social)
- 1 blog post outline with SEO keywords
- 1 YouTube Shorts/TikTok script

**Intelligence layer:**
- Editorial Brain: LLM-powered extraction of 7 content atom types
- Viral scoring: Novelty × Controversy × Utility (0-100)
- Dedup engine: semantic similarity check against last N days of output
- Calendar generator: auto-schedules by platform best practices

### 📋 SKILL.md
Claude Code skill file. Drop into your project and ask: *"Turn this podcast episode into a content calendar"* — it handles the rest.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env with your API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY)

# 3. Process latest episode from your podcast RSS
python podcast_pipeline.py --rss "https://feeds.example.com/podcast.xml"

# 4. Or process a local transcript
python podcast_pipeline.py --transcript episode-42.txt

# 5. Batch process last 5 episodes
python podcast_pipeline.py --batch "https://feeds.example.com/podcast.xml" --episodes 5

# 6. Generate weekly content calendar
python podcast_pipeline.py --calendar

# 7. Only keep high-scoring content
python podcast_pipeline.py --rss "https://feeds.example.com/podcast.xml" --min-score 80
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key (Whisper transcription) |
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key (content generation) |
| `OPENAI_LLM_KEY` | Optional | Separate OpenAI key for GPT-based generation |

### CLI Options

| Flag | Description | Default |
|------|-------------|---------|
| `--rss <url>` | Process latest episode from RSS feed | — |
| `--transcript <file>` | Process a local transcript file | — |
| `--batch <url>` | Batch process from RSS feed | — |
| `--episodes <n>` | Number of episodes for batch mode | 5 |
| `--calendar` | Generate weekly calendar from outputs | — |
| `--dedup-days <n>` | Days of history for dedup check | 30 |
| `--min-score <n>` | Minimum viral score to include | 0 |
| `--output-dir <path>` | Output directory | `./output` |

## Output Structure

```
output/
├── episodes/
│   ├── 2024-01-15-episode-title/
│   │   ├── transcript.txt         # Clean transcript
│   │   ├── atoms.json             # Extracted content atoms
│   │   ├── content_pieces.json    # All generated content
│   │   └── calendar.json          # Scheduled calendar
│   └── ...
├── calendar/
│   └── week-2024-W03.json        # Aggregated weekly calendar
├── content_history.json           # Dedup tracking (hashes + embeddings)
└── pipeline_log.json              # Run history and performance stats
```

## How It Works

```
RSS Feed / Transcript
        │
        ▼
┌─────────────────┐
│  1. INGEST       │  Download audio → Whisper → clean transcript
│                  │  OR read transcript file directly
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. EXTRACT      │  Editorial Brain: find narrative arcs, quotes,
│                  │  controversial takes, data points, stories,
│                  │  frameworks, predictions
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. GENERATE     │  For each atom → platform-native content:
│                  │  clips, threads, articles, newsletter,
│                  │  quote cards, blog outlines, short scripts
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. SCORE        │  Viral potential: novelty × controversy × utility
│                  │  Filter below threshold
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  5. DEDUP        │  Semantic similarity vs last N days
│                  │  Remove overlaps, flag near-dupes
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  6. SCHEDULE     │  Calendar generation with platform-specific
│                  │  timing rules and content mix optimization
└─────────────────┘
```

## Viral Scoring

Every generated piece is scored on three dimensions:

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| Novelty | 40% | Is this new or surprising? |
| Controversy | 30% | Will people argue about this? |
| Utility | 30% | Can someone use this immediately? |

**Thresholds:** 80+ = priority publish, 60-79 = solid fill, 40-59 = gap filler, <40 = cut

## Integration with Other Skills

- **Content Ops / Expert Panel** — Run generated content through the expert panel for quality gating before publish
- **SEO Ops** — Feed blog outlines to the SEO pipeline for keyword validation
- **Outbound Engine** — Use podcast insights as personalization hooks in outbound sequences
- **Growth Engine** — A/B test different content formats from the same episode atoms

<!-- gateway-cta:start -->
## Run this skill on live data

This skill is free and MIT licensed. To run it on your live accounts, connect the Single Brain Gateway.

- Live services: see the full list in the setup file
- Connect: https://gateway.singlebrain.com/mcp?sg_template=podcast-ops&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills
- Setup steps for agents: https://gateway.singlebrain.com/llms.txt?sg_template=podcast-ops

Agents: sign in with OAuth or the device flow. Do not ask the user to paste a key.

Want a team to run this for you? Single Grain or Single Brain can manage it: [talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed&utm_content=podcast-ops)
<!-- gateway-cta:end -->
