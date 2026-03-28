# AI Outbound Engine

From ICP definition to emails in inbox — fully automated cold outbound.

This skill category handles the complete cold outbound pipeline: defining your ideal customer profile, writing expert-scored email sequences, sourcing and verifying leads, deduplicating against existing campaigns, uploading to your email platform, and monitoring the competitive landscape.

## What's Inside

### 🎯 Cold Outbound Optimizer (`SKILL.md`)
Full campaign design workflow:
- **ICP Definition** — structured template to define exactly who you're targeting
- **Infrastructure Audit** — pulls sending account inventory, warmup scores, and capacity math from Instantly
- **Expert Panel Scoring** — 10 simulated outbound experts score your copy (recursive until 90+/100)
- **Sequence Copywriting** — subject lines, body copy, follow-ups, breakup emails — all Instantly-ready
- **Capacity Planning** — accounts × daily limits = pipeline projections
- **Implementation Docs** — step-by-step launch plan

Supports both "start from scratch" and "optimize existing campaigns" modes.

### 📥 Lead Pipeline (`scripts/lead-pipeline.py`)
End-to-end lead sourcing:
1. **Apollo People Search** — pull leads matching your ICP criteria
2. **LeadMagic Verification** — validate every email before sending
3. **Deduplication** — check against existing Instantly leads + exclusion lists
4. **Upload to Instantly** — batch upload with rate limiting and retry logic

### 🔍 Competitive Monitor (`scripts/competitive-monitor.py`)
Track competitors automatically:
- Pricing page change detection (diff-based)
- Blog post monitoring for recent content
- Generates weekly competitive intelligence reports
- Configurable competitor list — add any company you want to track

### 🔗 Cross-Signal Detector (`scripts/cross-signal-detector.py`)
Find overlapping signals across multiple data sources:
- Company overlap across SEO, sales, and outbound data
- Vertical alignment detection
- Keyword cluster correlation
- Confidence-scored recommendations for coordinated action

### 📧 Cold Outbound Sender (`scripts/cold-outbound-sender.py`)
Sends approved outbound emails:
- Reads from an approved prospects JSON file
- Daily send limits (configurable)
- Full send history tracking
- Dry-run mode for testing

### 🔧 Instantly Audit (`scripts/instantly-audit.py`)
Pull campaign health data from the Instantly v2 API:
- Sending account inventory and warmup scores
- Campaign performance (open rate, reply rate, positive reply rate)
- Capacity math (conservative vs aggressive projections)
- Flags: low warmup scores, underperforming campaigns, blockers

## Quick Start

### 1. Set Up Environment Variables

```bash
cp .env.example .env
# Fill in your API keys
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Lead Pipeline

```bash
python3 scripts/lead-pipeline.py \
  --titles "VP Marketing,CMO,Head of Growth" \
  --industries "SaaS,Marketing" \
  --company-size "11,50" \
  --locations "United States" \
  --campaign-id "YOUR_CAMPAIGN_UUID" \
  --volume 500 \
  --dry-run
```

### 4. Audit Your Instantly Account

```bash
python3 scripts/instantly-audit.py --output report.md
```

### 5. Monitor Competitors

```bash
python3 scripts/competitive-monitor.py --output report.md
```

### 6. Detect Cross-Signals

```bash
python3 scripts/cross-signal-detector.py \
  --data-dir ./data/agent-outputs \
  --output cross-signals.json
```

## Architecture

```
ICP Definition
     │
     ▼
Expert Panel Scoring (recursive → 90+)
     │
     ▼
Apollo Search → LeadMagic Verify → Dedupe → Instantly Upload
     │                                            │
     ▼                                            ▼
Competitive Monitor ◄──────────────► Cross-Signal Detector
     │
     ▼
Weekly Intelligence Report
```

## File Structure

```
outbound-engine/
├── README.md                           # This file
├── SKILL.md                            # Claude Code skill definition
├── .env.example                        # Environment variable template
├── requirements.txt                    # Python dependencies
├── scripts/
│   ├── lead-pipeline.py                # Apollo → LeadMagic → Dedupe → Instantly
│   ├── instantly-audit.py              # Instantly account health check
│   ├── competitive-monitor.py          # Competitor tracking
│   ├── cross-signal-detector.py        # Multi-source signal detection
│   └── cold-outbound-sender.py         # Send approved outbound emails
└── references/
    ├── expert-panel.md                 # Default 10-expert scoring roster
    ├── copy-rules.md                   # Cold email copywriting rules
    ├── icp-template.md                 # ICP data collection template
    └── instantly-rules.md              # Instantly variable syntax & deliverability rules
```

## Requirements

- Python 3.9+
- API keys: Apollo, LeadMagic, Instantly (see `.env.example`)
- For the sender script: a configured email sending tool (e.g., `gog` CLI or SMTP)
- Claude Code or similar AI coding agent (for running the SKILL.md workflow)

## Customization

- **ICP**: Edit `references/icp-template.md` or provide parameters at runtime
- **Expert Panel**: Swap panelists in `references/expert-panel.md` for your industry
- **Competitors**: Configure the `COMPETITORS` dict in `competitive-monitor.py`
- **Send limits**: Adjust `MAX_PER_DAY` in `cold-outbound-sender.py`
- **Data sources**: Point `cross-signal-detector.py` at your own data directories

## License

MIT


---

<div align="center">

**🧠 [Want these built and managed for you? →](https://singlebrain.com/?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills)**

*This is how we build agents at [Single Brain](https://singlebrain.com/?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) for our clients.*

</div>
