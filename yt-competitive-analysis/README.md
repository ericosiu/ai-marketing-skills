# YouTube Competitive Analysis

Find what's actually working on YouTube. Analyzes any set of channels, identifies outlier videos (2x+ average views), and extracts packaging patterns from winners.

No manual spreadsheet work. No guessing. Data-driven competitive intel in minutes.

## What It Does

1. Pulls recent videos from any YouTube channel(s)
2. Separates long-form from Shorts
3. Calculates per-channel averages
4. Flags outliers (videos performing 2x+ above the channel average)
5. Extracts title patterns from winners
6. Exports to console, JSON, or Google Sheets

## Quick Start

```bash
# Set your YouTube API key
export YOUTUBE_API_KEY="your-key-here"

# Analyze specific channels
python3 analyze.py "$YOUTUBE_API_KEY" --channels "@AlexHormozi,@garyvee,@CodieSanchezCT"

# Use predefined channel sets
python3 analyze.py "$YOUTUBE_API_KEY" --set ai          # AI creator set
python3 analyze.py "$YOUTUBE_API_KEY" --set business    # Business creator set
python3 analyze.py "$YOUTUBE_API_KEY" --set both        # All channels

# Export to JSON for programmatic use
python3 analyze.py "$YOUTUBE_API_KEY" --set both --output json > results.json

# Custom lookback period
python3 analyze.py "$YOUTUBE_API_KEY" --channels "@mkbhd" --days 60
```

## Setup

1. Get a [YouTube Data API v3 key](https://console.cloud.google.com/apis/api/youtube.googleapis.com)
2. Set it as an environment variable: `export YOUTUBE_API_KEY="your-key"`
3. Install dependencies: `pip install -r requirements.txt`

## Output

### Console (default)

```
================================================================================
  AI Creators — LAST 30 DAYS
================================================================================

📊 CHANNEL SUMMARY:
  Alex Hormozi             |  2,400,000 subs |  12 videos (3.0/wk) | L:  8 S:  4

🔥 LONG-FORM OUTLIERS (top 15):
  4.2x |  1,200,000 | [Alex Hormozi] How I'd Start a Business in 2025
       2025-01-15 | https://youtube.com/watch?v=...

📦 TOP TITLE PATTERNS:
   8x  business
   6x  money
   5x  started
```

### JSON

Full structured data including all video metadata, scores, and multipliers.

## Predefined Channel Sets

**AI Creators:** Jeff Su, Alex Finn, Riley Brown, Dan Martell, Matt Wolfe, Nate Herk, Grace Leung, Matt Berman

**Business Creators:** Alex Hormozi, Gary Vaynerchuk, Patrick Bet-David, Codie Sanchez, Leila Hormozi, Iman Gadzhi, My First Million

Edit the channel dictionaries in `analyze.py` to customize.

## Interpreting Results

| Metric | What It Means |
|--------|--------------|
| **Multiplier** | How many times above channel average (2.0x = double normal) |
| **Outlier threshold** | 2x average. Videos above this are worth studying. |
| **Title patterns** | Common words in outlier titles = proven formats |
| **Cadence** | Videos per week. Higher cadence may mean lower per-video averages. |

## Proven Packaging Formats

Based on outlier analysis, these title formats consistently overperform:

**Long-form:**
- "X, Clearly Explained" (definitive explainer)
- "X hours of Y in Z minutes" (condensed value)
- "The Laziest Way to X" (low-effort promise)
- "Give me X minutes and I'll Y" (time-boxed promise)
- "X INSANE Use Cases for Y" (listicle + power word)

**Shorts:**
- "2024 vs 2025 X" (year comparison)
- "Bad Good Great X" (tier ranking)
- "Stop doing X, do Y instead" (contrarian)

## Weekly Automation

Run weekly to surface new outliers automatically:

```bash
# Cron: every Sunday at 8am
0 8 * * 0 YOUTUBE_API_KEY="your-key" python3 /path/to/analyze.py "$YOUTUBE_API_KEY" --set both --output json > /path/to/weekly-results.json
```

## Requirements

- Python 3.8+
- YouTube Data API v3 key
- No external Python dependencies (uses only stdlib)

## License

MIT

---

<!-- gateway-cta:start -->
## Run this skill on live data

This skill is free and MIT licensed. To run it on your live accounts, connect the Single Brain Gateway.

- Live services: see the full list in the setup file
- Connect: https://gateway.singlebrain.com/mcp?sg_template=yt-competitive-analysis&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills
- Setup steps for agents: https://gateway.singlebrain.com/llms.txt?sg_template=yt-competitive-analysis

Agents: sign in with OAuth or the device flow. Do not ask the user to paste a key.
<!-- gateway-cta:end -->
<!-- managed-cta:start -->
**Want a team to run this for you?** Single Grain and Single Brain can set up and manage this workflow for you. [Talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed-service&utm_content=yt-competitive-analysis)
<!-- managed-cta:end -->
