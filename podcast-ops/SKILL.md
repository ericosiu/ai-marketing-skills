---
name: podcast-pipeline
description: >-
  Podcast-to-Everything content pipeline. Takes a podcast RSS feed or raw
  transcript and generates a full cross-platform content calendar: short-form
  video clips, Twitter/X threads, LinkedIn articles, newsletter sections, quote
  cards, blog outlines with SEO keywords, and YouTube Shorts/TikTok scripts.
  Scores each piece by viral potential (novelty × controversy × utility) and
  deduplicates against recent output. Use when asked to: "repurpose this podcast",
  "turn this episode into content", "podcast content calendar", "extract clips
  from this episode", "podcast to social", "content from RSS feed", "batch
  process episodes", or any request to turn podcast/audio content into a
  multi-platform content plan.
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

# Podcast-to-Everything Pipeline

Turns podcast episodes into a full content calendar across every platform.
One episode in, 15-20 content pieces out — scored, deduplicated, and scheduled.

---

## Step 1: Ingest — Get the Transcript

Determine the input source and obtain a clean transcript.

### Option A: RSS Feed (`--rss <url>`)
1. Fetch the RSS feed XML
2. Extract the latest episode's audio URL (or use `--episodes N` for batch)
3. Download the audio file
4. Transcribe via OpenAI Whisper API (with timestamps)
5. Store transcript with episode metadata (title, date, description, duration)

### Option B: Raw Transcript (`--transcript <file>`)
1. Read the transcript file (plain text, SRT, or VTT)
2. Parse timestamps if present
3. Extract episode metadata from filename or prompt user

### Option C: Batch Mode (`--batch <rss_url> --episodes N`)
1. Fetch RSS feed
2. Extract the last N episodes
3. Process each through the full pipeline
4. Deduplicate across all episodes in the batch

### Transcript cleanup
- Remove filler words (um, uh, like, you know) for written content
- Preserve original with timestamps for video clip suggestions
- Split into logical segments by topic shift

---

## Step 2: Editorial Brain — Deep Analysis

Feed the full transcript to the LLM with this extraction framework:

### Extract these content atoms:

1. **Narrative Arcs** — Complete story segments with setup → tension → resolution.
   Tag with start/end timestamps.

2. **Quotable Moments** — Punchy, shareable statements. One-liners that stand alone.
   Must pass the "would someone screenshot this?" test.

3. **Controversial Takes** — Opinions that go against conventional wisdom.
   The stuff that makes people reply "hard disagree" or "finally someone said it."

4. **Data Points** — Specific numbers, percentages, dollar amounts, timeframes.
   Concrete proof points that add credibility.

5. **Stories** — Personal anecdotes, case studies, client examples.
   Must have a character, a problem, and an outcome.

6. **Frameworks** — Step-by-step processes, mental models, decision matrices.
   Anything structured that people would save or bookmark.

7. **Predictions** — Forward-looking claims about trends, markets, technology.
   Hot takes about where things are going.

### Output format per atom:
```
- Type: [narrative_arc | quote | controversial_take | data_point | story | framework | prediction]
- Content: [extracted text]
- Timestamp: [start - end, if available]
- Context: [what was being discussed]
- Viral Score: [0-100, see Step 4]
- Suggested platforms: [where this atom works best]
```

---

## Step 3: Content Generation — One Episode, Many Pieces

For each episode, generate ALL of these from the extracted atoms:

### 3a. Short-Form Video Clips (3-5 per episode)
```
- Hook: [First 3 seconds — pattern interrupt or bold claim]
- Clip segment: [Timestamp range from transcript]
- Caption overlay: [Text for the screen]
- Platform: [YouTube Shorts / TikTok / Instagram Reels]
- Why it works: [What makes this clippable]
```
Prioritize: controversial takes > stories with payoffs > surprising data points

### 3b. Twitter/X Threads (2-3 per episode)
```
- Thread hook (tweet 1): [Curiosity gap or bold opener]
- Thread body (5-10 tweets): [Each tweet is one complete thought]
- Thread closer: [CTA — follow, reply, retweet trigger]
- Source atoms: [Which content atoms feed this thread]
```
Rules: No tweet over 280 chars. Each tweet must stand alone. Use data points as proof.

### 3c. LinkedIn Article Draft (1 per episode)
```
- Headline: [Specific, benefit-driven]
- Hook paragraph: [Before the "see more" fold — must earn the click]
- Body: [3-5 sections with headers, 800-1200 words]
- CTA: [Engagement driver — question, not link]
- Hashtags: [3-5 relevant, not spammy]
```
Voice: Professional but not corporate. First-person. Story-driven.

### 3d. Newsletter Section (1 per episode)
```
- Section headline: [Scannable, specific]
- TL;DR: [One sentence, the core insight]
- Body: [3-5 bullet points, each with a takeaway]
- Pull quote: [The most shareable line from the episode]
- Link: [Back to full episode]
```

### 3e. Quote Cards (3-5 per episode)
```
- Quote text: [Max 20 words — must work as text overlay]
- Attribution: [Speaker name]
- Background suggestion: [Color/mood that matches the tone]
- Platform sizing: [1080x1080 for IG, 1200x675 for Twitter, 1080x1920 for Stories]
```

### 3f. Blog Post Outline (1 per episode)
```
- Title: [SEO-optimized, includes primary keyword]
- Primary keyword: [Search volume + difficulty estimate]
- Secondary keywords: [3-5 related terms]
- Meta description: [155 chars max]
- H2 sections: [5-7, each maps to a content atom]
- Internal linking opportunities: [Topics that connect to existing content]
- Estimated word count: [1500-2500]
```

### 3g. YouTube Shorts / TikTok Script (1 per episode)
```
- HOOK (0-3s): [Pattern interrupt — question, bold claim, or visual]
- SETUP (3-15s): [Context — why should they care]
- PAYOFF (15-45s): [The insight, data, or story resolution]
- CTA (45-60s): [Follow, comment prompt, or part 2 tease]
- On-screen text: [Key phrases to overlay]
- B-roll suggestions: [Visual ideas if not talking-head]
```

---

## Step 4: Content Scoring — Viral Potential

Score every generated piece on three dimensions (each 0-100):

| Dimension | What It Measures | Signals |
|-----------|-----------------|---------|
| **Novelty** | Is this new or surprising? | Contrarian takes, unexpected data, first-to-say |
| **Controversy** | Will people argue about this? | Strong opinions, challenges norms, picks a side |
| **Utility** | Can someone use this immediately? | Frameworks, how-tos, templates, specific numbers |

**Viral Score = (Novelty × 0.4) + (Controversy × 0.3) + (Utility × 0.3)**

### Score thresholds:
- **80+** → Priority publish. Schedule for peak engagement windows.
- **60-79** → Solid content. Fill the calendar.
- **40-59** → Filler. Use only if calendar has gaps.
- **Below 40** → Cut it. Not worth the publish slot.

---

## Step 5: Dedup Engine

Before finalizing, check all generated content against:
1. **This batch** — No two pieces should cover the same angle
2. **Recent history** — Compare against last N days of output (default: 30)
3. **Similarity threshold** — Flag any pair with >70% semantic overlap

### Dedup rules:
- If two pieces overlap >70%: keep the higher-scored one, cut the other
- If a piece overlaps with recently published content: flag with ⚠️ and suggest a differentiation angle
- Track all published content hashes in `output/content_history.json`

---

## Step 6: Calendar Generation (`--calendar`)

Assemble scored, deduplicated content into a weekly publish calendar.

### Scheduling rules:
- **Twitter/X:** 1-2 per day, peak hours (8-10am, 12-1pm, 5-7pm ET)
- **LinkedIn:** 1 per day max, Tuesday-Thursday mornings
- **YouTube Shorts/TikTok:** 1 per day, evenings
- **Newsletter:** Weekly, same day each week
- **Blog:** 1-2 per week
- **Quote cards:** Intersperse on low-content days

### Calendar output format:
```json
{
  "week_of": "2024-01-15",
  "episode_source": "Episode Title - Guest Name",
  "content_pieces": [
    {
      "date": "2024-01-15",
      "time": "09:00 ET",
      "platform": "twitter",
      "type": "thread",
      "content": "...",
      "viral_score": 85,
      "status": "draft"
    }
  ],
  "total_pieces": 18,
  "avg_viral_score": 72,
  "coverage": {
    "twitter": 6,
    "linkedin": 3,
    "youtube_shorts": 3,
    "newsletter": 1,
    "blog": 1,
    "quote_cards": 4
  }
}
```

---

## Step 7: Output

All output goes to `output/` directory:

```
output/
├── episodes/
│   ├── YYYY-MM-DD-episode-slug/
│   │   ├── transcript.txt
│   │   ├── atoms.json          # Extracted content atoms
│   │   ├── content_pieces.json # All generated content
│   │   └── calendar.json       # Scheduled calendar
│   └── ...
├── calendar/
│   └── week-YYYY-WNN.json     # Aggregated weekly calendar
├── content_history.json        # Dedup tracking
└── pipeline_log.json           # Run history and stats
```

---

## CLI Reference

```bash
# Process latest episode from RSS feed
python podcast_pipeline.py --rss "https://feeds.example.com/podcast.xml"

# Process a local transcript
python podcast_pipeline.py --transcript episode-42.txt

# Batch process last 5 episodes
python podcast_pipeline.py --batch "https://feeds.example.com/podcast.xml" --episodes 5

# Generate weekly calendar from existing outputs
python podcast_pipeline.py --calendar

# Process with custom dedup window
python podcast_pipeline.py --rss "https://feeds.example.com/podcast.xml" --dedup-days 60

# Process and only keep 80+ viral score content
python podcast_pipeline.py --rss "https://feeds.example.com/podcast.xml" --min-score 80
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes (for Whisper) | OpenAI API key for audio transcription |
| `ANTHROPIC_API_KEY` | Yes (for generation) | Anthropic API key for content generation |
| `OPENAI_LLM_KEY` | Optional | Separate OpenAI key if using GPT for generation instead |

---

## Reference Files

| File | Purpose |
|------|---------|
| `podcast_pipeline.py` | Main pipeline script |
| `requirements.txt` | Python dependencies |
| `README.md` | Setup and usage guide |
