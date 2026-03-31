# AI Revenue Intelligence

## Preamble (runs on skill start)

```bash
# Version check (silent if up to date)
python3 telemetry/version_check.py 2>/dev/null || true

# Telemetry opt-in (first run only, then remembers your choice)
python3 telemetry/telemetry_init.py 2>/dev/null || true
```

> **Privacy:** This skill logs usage locally to `~/.ai-marketing-skills/analytics/`. Remote telemetry is opt-in only. No code, file paths, or repo content is ever collected. See `telemetry/README.md`.

---

AI-powered revenue intelligence: sales call insight extraction, content-to-revenue attribution, and multi-source client reporting.

## When to Use

- User wants to extract insights from Gong sales call transcripts
- User needs to identify objections, buying signals, or competitive mentions in calls
- User wants to prove content ROI by mapping content to closed deals
- User needs revenue attribution across first-touch and multi-touch models
- User wants to generate a unified client report from GA4 + HubSpot + Ahrefs + Gong
- User asks about content gaps in the buyer journey
- User needs anomaly detection across marketing metrics

## Tools

### Gong-to-Insight Pipeline (`gong_insight_pipeline.py`)

Extracts structured intelligence from sales call transcripts. Works with Gong API or plain transcript files.

```bash
# Analyze a single transcript file
python gong_insight_pipeline.py --file transcript.txt

# Analyze multiple transcript files
python gong_insight_pipeline.py --dir ./transcripts/

# Pull recent calls from Gong API (last 7 days)
python gong_insight_pipeline.py --gong --days 7

# Pull specific call by ID
python gong_insight_pipeline.py --gong --call-id abc123

# Output as JSON file
python gong_insight_pipeline.py --file transcript.txt --output insights.json

# Generate content topics from recurring objections
python gong_insight_pipeline.py --dir ./transcripts/ --content-topics

# Generate follow-up suggestions for outbound sequences
python gong_insight_pipeline.py --file transcript.txt --follow-ups
```

**What it extracts:**
- Objections (categorized: pricing, timing, competition, authority, need)
- Buying signals (budget confirmed, timeline mentioned, decision maker engaged, champion identified)
- Competitive mentions (who was mentioned, context: positive/negative/neutral)
- Pricing discussions (anchors, pushback, willingness indicators)
- Content topic suggestions from recurring objection patterns
- Personalized follow-up drafts based on call context

**Output:** Structured JSON to stdout or file. Each call produces an `insights` object with `objections`, `buying_signals`, `competitive_mentions`, `pricing_discussions`, `content_topics`, and `follow_ups` arrays.

### Revenue Attribution Mapper (`revenue_attribution.py`)

Maps content pieces to pipeline and closed revenue. Proves content ROI with first-touch and multi-touch attribution.

```bash
# Run full attribution report (GA4 + HubSpot)
python revenue_attribution.py --report

# First-touch attribution only
python revenue_attribution.py --report --model first-touch

# Multi-touch (linear) attribution
python revenue_attribution.py --report --model linear

# Time-decay attribution
python revenue_attribution.py --report --model time-decay

# Filter by date range
python revenue_attribution.py --report --start 2025-01-01 --end 2025-03-31

# Calculate cost-per-acquisition by content type
python revenue_attribution.py --cpa --costs content_costs.json

# Identify content gaps in the buyer journey
python revenue_attribution.py --gaps

# Output as JSON
python revenue_attribution.py --report --json --output attribution.json
```

**What it produces:**
- Content-to-revenue mapping (which blog posts, videos, podcasts drove deals)
- First-touch, linear, and time-decay attribution models
- Cost-per-acquisition by content type (blog, video, podcast, webinar)
- Content ROI report with revenue per piece
- Content gap analysis (funnel stages with no attribution)
- Top-performing content ranked by attributed revenue

**Data sources:** GA4 (page paths, sessions, conversions) + HubSpot (deals, touchpoints, close dates)

### Multi-Source Client Report Generator (`client_report_generator.py`)

Generates unified client-ready BI reports from GA4, HubSpot, Ahrefs, and Gong.

```bash
# Generate full client report
python client_report_generator.py --client "Acme Corp"

# Specify date range
python client_report_generator.py --client "Acme Corp" --start 2025-03-01 --end 2025-03-31

# Output as markdown
python client_report_generator.py --client "Acme Corp" --format markdown --output report.md

# Output as JSON (for rendering in slides/dashboards)
python client_report_generator.py --client "Acme Corp" --format json --output report.json

# Skip specific data sources
python client_report_generator.py --client "Acme Corp" --skip gong
python client_report_generator.py --client "Acme Corp" --skip ahrefs,gong

# Enable anomaly detection
python client_report_generator.py --client "Acme Corp" --anomalies

# Compare to previous period
python client_report_generator.py --client "Acme Corp" --compare previous-month
```

**What it produces:**
- Executive summary with key metrics and period-over-period changes
- Traffic section: sessions, users, top pages, channel breakdown (GA4)
- Pipeline section: deals created, moved, closed, revenue (HubSpot)
- SEO section: keyword rankings, backlinks, domain rating changes (Ahrefs)
- Call quality section: talk ratios, objection frequency, win rates (Gong)
- Anomaly flags: unusual spikes/drops with severity and context
- Output as structured markdown or JSON

## Configuration

All scripts read from environment variables. Copy `.env.example` to `.env` and fill in your values.

### Required Environment Variables

| Variable | Used By | Description |
|----------|---------|-------------|
| `GONG_API_KEY` | Gong Pipeline, Client Report | Gong API access key |
| `GONG_API_BASE_URL` | Gong Pipeline, Client Report | Gong API base URL |
| `HUBSPOT_API_KEY` | Attribution, Client Report | HubSpot private app token |
| `GA4_PROPERTY_ID` | Attribution, Client Report | GA4 property ID |
| `GA4_CREDENTIALS_JSON` | Attribution, Client Report | Path to GA4 service account JSON |

### Optional Environment Variables

| Variable | Used By | Description |
|----------|---------|-------------|
| `AHREFS_TOKEN` | Client Report | Ahrefs API token |
| `OUTPUT_DIR` | All | Directory for output files (default: `./output`) |

## Data Flow

```
Gong Transcripts → Insight Pipeline → Objections, Signals, Competitors → Content Topics + Follow-ups
GA4 + HubSpot   → Attribution Mapper → Content ROI, CPA, Gap Analysis → Revenue Proof
GA4 + HubSpot + Ahrefs + Gong → Client Report → Executive Summary + Anomalies → Client Deliverable
```

## Recommended Workflow

1. **Weekly:** Run `gong_insight_pipeline.py --gong --days 7` to extract call intelligence
2. **Monthly:** Run `revenue_attribution.py --report` to prove content ROI
3. **Monthly:** Run `client_report_generator.py` for each client deliverable
4. **Quarterly:** Run `revenue_attribution.py --gaps` to find content gaps
5. **Ongoing:** Feed Gong insight follow-ups into outbound sequences

## Dependencies

```bash
pip install -r requirements.txt
```
