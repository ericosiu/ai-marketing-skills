# AI SEO Ops

## Preamble (runs on skill start)

```bash
# Version check (silent if up to date)
python3 telemetry/version_check.py 2>/dev/null || true

# Telemetry opt-in (first run only, then remembers your choice)
python3 telemetry/telemetry_init.py 2>/dev/null || true
```

> **Privacy:** This skill logs usage locally to `~/.ai-marketing-skills/analytics/`. Remote telemetry is opt-in only. No code, file paths, or repo content is ever collected. See `telemetry/README.md`.

---

AI-powered SEO operations: keyword intelligence, competitor gap analysis, GSC optimization, and trend detection.

## When to Use

- User asks for keyword research, content brief, or SEO analysis
- User wants to find quick-win keywords from Google Search Console
- User needs a competitor gap analysis
- User wants to identify trending topics for content creation
- User asks about decaying content or traffic drops
- User wants a prioritized list of keywords to target

## Tools

### Content Attack Brief (`content_attack_brief.py`)

Full keyword intelligence pipeline. Requires `AHREFS_TOKEN` and GSC auth.

```bash
# Run the full brief
python content_attack_brief.py
```

**What it produces:**
- Topic fingerprint from your content library
- BOFU money keywords ranked by Impact × Confidence
- Trending keywords with sparkline visualizations
- Competitor gap analysis (keywords they rank for, you don't)
- Decaying page alerts (traffic drops >30%)
- Execution pipeline (auto-create → semi-auto → team)

**Output:** Prints formatted report to stdout + saves JSON to `OUTPUT_DIR/content-attack-brief-latest.json`

### GSC Client (`gsc_client.py`)

Google Search Console API client. Works as CLI or importable library.

```bash
# CLI usage
python gsc_client.py --queries 50 --days 28
python gsc_client.py --striking                    # Striking distance keywords (pos 4-20)
python gsc_client.py --pages 100 --days 7
python gsc_client.py --trend                       # Daily click/impression trend
python gsc_client.py --devices                     # Mobile vs desktop split
python gsc_client.py --sites                       # List verified properties
python gsc_client.py --json --queries 25           # JSON output
```

```python
# Library usage
from gsc_client import GSCClient

gsc = GSCClient()
rows = gsc.striking_distance(days=28, min_position=4, max_position=20)
for row in rows:
    print(f"{row['keys'][0]}: pos {row['position']:.1f}, {row['impressions']} impressions")
```

### GSC Auth (`gsc_auth.py`)

One-time OAuth setup for Google Search Console access.

```bash
python gsc_auth.py
# Opens browser → Google Sign-In → saves token locally
```

### Trend Scout (`trend_scout.py`)

Multi-source trend detection. No API keys required for basic functionality.

```bash
python trend_scout.py
```

**Sources:** Google Trends RSS, Hacker News, Reddit, X/Twitter (needs `BRAVE_API_KEY`), YouTube outlier detection

**Output:** Prints summary + saves JSON to `OUTPUT_DIR/flash-trends-latest.json` and markdown report.

## Configuration

All scripts read from environment variables. Copy `.env.example` to `.env` and fill in your values.

Required:
- `GSC_SITE_URL` — your Google Search Console property URL
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` — for GSC OAuth
- `YOUR_DOMAIN` — your root domain

Optional:
- `AHREFS_TOKEN` — enables Ahrefs keyword data and competitor analysis
- `COMPETITORS` — comma-separated competitor domains
- `BRAVE_API_KEY` — enables X/Twitter trend scanning
- `CONTENT_VERTICALS` — comma-separated topics for trend relevance scoring
- `TREND_SUBREDDITS` — comma-separated subreddits to monitor

## Scoring Model

Keywords are scored on two axes:

**Impact (0-10):** Volume + CPC + Funnel Stage + Trend direction
**Confidence (0-10):** Keyword Difficulty + Current ranking position + Topic authority

**Priority = Impact × Confidence** (max 100)

## Funnel Classification

- **BOFU:** Commercial/transactional intent, or keywords containing "agency", "services", "pricing", "best", "vs", "hire"
- **MOFU:** Informational with buying signals — "how to", "guide", "roi", "case study"
- **TOFU:** Pure informational

## Recommended Workflow

1. **Weekly:** Run `content_attack_brief.py` for the full intelligence report
2. **Daily:** Run `gsc_client.py --striking` to monitor striking distance keywords
3. **2x/week:** Run `trend_scout.py` to catch trending topics early
4. **Monthly:** Review competitor gaps and adjust `COMPETITORS` list

## Dependencies

```bash
pip install -r requirements.txt
```
