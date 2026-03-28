# 🎯 AI Sales Pipeline

> **Turn anonymous website visitors into qualified pipeline in under 60 seconds.**

A complete AI-powered sales pipeline automation suite: from website visitor identification through intent scoring, suppression, campaign routing, dead deal resurrection, trigger-based prospecting, and self-learning ICP optimization.

These tools were built in production at [Single Grain](https://www.singlegrain.com/?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills), processing thousands of visitors and deals weekly. Now open-sourced for any company to use.

---

## Architecture

```
                         ┌─────────────────────────────────────────┐
                         │           YOUR WEBSITE(S)               │
                         └──────────────┬──────────────────────────┘
                                        │ RB2B pixel fires
                                        ▼
                    ┌───────────────────────────────────────┐
                    │      rb2b_webhook_ingest.py           │
                    │  Intent Scoring + ICP Classification  │
                    │  (pricing=90, blog=30, services=65)   │
                    └──────────────┬────────────────────────┘
                                   │ High-intent visitors
                                   ▼
              ┌────────────────────────────────────────────────┐
              │        rb2b_suppression_pipeline.py            │
              │  5-Layer Check:                                │
              │  CRM → Outbound → Stripe → Analytics → Block  │
              │  + Company-level dedup (1 per domain/week)     │
              └──────────────┬─────────────────────────────────┘
                             │ Clean leads only
                             ▼
              ┌────────────────────────────────────────────────┐
              │        rb2b_instantly_router.py                │
              │  Agency Detection + Source Site Routing        │
              │  → Routes to correct Instantly campaign        │
              │  → Auto-activates paused campaigns             │
              └────────────────────────────────────────────────┘

  ┌────────────────────┐  ┌────────────────────┐  ┌─────────────────────┐
  │  deal_resurrector  │  │ trigger_prospector  │  │ icp_learning_       │
  │       .py          │  │       .py           │  │    analyzer.py      │
  │                    │  │                     │  │                     │
  │ 3 intelligence     │  │ Monitors:           │  │ Reads approve/      │
  │ layers on dead     │  │ • New CMO hires     │  │ reject decisions    │
  │ deals:             │  │ • Job postings      │  │                     │
  │ 1. Time decay      │  │ • Funding rounds    │  │ Outputs:            │
  │    scoring         │  │ • Agency searches   │  │ • Industry targets  │
  │ 2. POC expansion   │  │                     │  │ • Size sweet spots  │
  │ 3. Follow the      │  │ Scores, enriches,   │  │ • Title patterns    │
  │    champion        │  │ drafts outreach     │  │ • Revenue ranges    │
  └────────────────────┘  └─────────────────────┘  └─────────────────────┘
           │                        │                         │
           └────────────────────────┼─────────────────────────┘
                                    ▼
                        ┌───────────────────────┐
                        │   Your CRM / Outbound │
                        │   (HubSpot, Instantly) │
                        └───────────────────────┘
```

---

## Tools

### 1. 🌐 RB2B Webhook Ingest (`rb2b_webhook_ingest.py`)

Receives RB2B visitor identification webhooks, scores intent based on pages visited, and classifies ICP fit.

**What it does:**
- Scores every page visit against configurable intent patterns (pricing page = 90, blog = 30)
- Checks ICP fit by title seniority + company size
- Outputs structured signals with priority levels (high/medium/low)
- Runs as HTTP server or processes stdin/batch files

```bash
# Run as webhook server
python3 rb2b_webhook_ingest.py --serve --port 4100

# Test with sample data
echo '{"email":"cmo@acme.com","job_title":"CMO","company":"Acme Inc","company_size":500,"pages_visited":["https://yoursite.com/pricing"]}' | python3 rb2b_webhook_ingest.py --dry-run
```

### 2. 🛡️ Suppression Pipeline (`rb2b_suppression_pipeline.py`)

5-layer suppression that prevents embarrassing outreach to existing customers, active leads, or competitors.

**Layers:**
1. **Personal Email Filter** — Skip gmail.com, yahoo.com, etc.
2. **CRM Check** — Already in HubSpot? Don't cold email them.
3. **Outbound Platform** — Already in an Instantly campaign (last 90 days)?
4. **Payment Provider** — Paying Stripe customer? Definitely don't cold email.
5. **Blocklist** — Competitor domains + manual blocks
6. **Company Dedup** — Only 1 contact per company domain per 7-day window

```bash
# Check a single email
python3 rb2b_suppression_pipeline.py --email john@acme.com --company "Acme Inc"

# Output:
# 📋 Suppression check for: john@acme.com
# ──────────────────────────────────────────────────
#   ✅ Personal Email Filter: business email
#   ✅ CRM Check: not in CRM
#   ✅ Outbound Platform: not in outbound platform
#   ✅ Payment Provider: not a paying customer
#   ✅ Blocklist: not blocklisted
#   ✅ Company Dedup: no company dedup conflict
# ──────────────────────────────────────────────────
#   ✅ CLEAR — eligible for enrollment
```

### 3. 🔀 Instantly Router (`rb2b_instantly_router.py`)

The orchestrator: combines intent scoring + suppression + agency classification to route leads to the right Instantly campaign automatically.

**What it does:**
- Scores visitor intent
- Runs full suppression pipeline
- Classifies agency vs. non-agency visitors (2+ signal threshold)
- Detects source site (if you have multiple properties)
- Routes to the correct campaign and auto-enrolls via Instantly API
- Auto-activates paused campaigns when leads are ready

```bash
# Run as webhook server (production mode)
python3 rb2b_instantly_router.py --serve --port 4100

# Dry run test
echo '{"email":"vp@techco.com","job_title":"VP Marketing","company":"TechCo","industry":"SaaS","company_size":"200","pages_visited":["https://yoursite.com/pricing","https://yoursite.com/case-studies"]}' | python3 rb2b_instantly_router.py --dry-run
```

### 4. 🔥 Deal Resurrector (`deal_resurrector.py`)

Three intelligence layers on your closed-lost deals. Finds the best revival opportunities using a composite scoring formula.

**Layer 1 — Time Decay Scoring (0-100):**
- Time component (35 pts): 60-90 days = sweet spot, decays over time
- Value component (30 pts): Normalized deal value
- Reason component (20 pts): "Timing" deals score higher than "bad fit"
- Trigger component (15 pts): Bonus if recent email opens or site visits

**Layer 2 — POC Expansion:**
- Verifies if your contact is still at the company
- Finds replacement decision-makers when contacts leave

**Layer 3 — Follow the Champion:**
- Tracks departed contacts to their new companies
- If they moved to an ICP-fit company, generates outreach for the new org

```bash
# Find top 10 revival opportunities (dry run)
python3 deal_resurrector.py --top 10 --dry-run

# Full run with champion tracking
python3 deal_resurrector.py --top 5 --include-champion

# Exclude a company from future runs
python3 deal_resurrector.py --add-exclusion "Already Won Corp"
```

### 5. 🔍 Trigger Prospector (`trigger_prospector.py`)

Scans the web for buying signals: new marketing leadership hires, job postings, funding rounds, and active agency searches.

**Signal Categories:**
| Signal | What It Means | Score Weight |
|--------|--------------|-------------|
| New CMO/VP hire | Budget reallocation window | 35 pts |
| Job posting | Growth mode, team building | 25 pts |
| Funding round | Capital to deploy | 30 pts |
| Agency search | Active evaluation | 40 pts |

Each prospect gets a composite score (0-100) plus enrichment: estimated company size, industry, suggested services, outreach channel recommendation, and a ready-to-send email draft.

```bash
# Scan last 7 days for signals
python3 trigger_prospector.py --days 7 --top 15

# Wider scan with lower threshold
python3 trigger_prospector.py --days 30 --top 25 --min-score 40
```

### 6. 📊 ICP Learning Analyzer (`icp_learning_analyzer.py`)

Your ICP should evolve from data, not guesswork. This tool reads your prospect approve/reject history and outputs recommended filter changes.

**What it analyzes:**
- Industry patterns (which convert vs. get rejected)
- Company size sweet spots (10th-90th percentile of approvals)
- Title/seniority patterns
- Revenue ranges
- Per-source approval rates (cold vs. trigger vs. warm vs. revival)

```bash
# Run analysis
python3 icp_learning_analyzer.py

# With custom config
python3 icp_learning_analyzer.py --config data/icp-config.json

# Example output:
# 📊 ICP Learning Analyzer Results
#    Total prospects analyzed: 847
#    ────────────────────────────────────────
#    cold      : ready                (n=312, approval=23%)
#              → Target: SaaS, Fintech, E-commerce
#              → Exclude: Crypto/Web3
#              → Employees: 50-500
#    trigger   : ready                (n=156, approval=41%)
#              → Target: SaaS, Healthcare
#              → Employees: 100-1000
#    warm      : ready                (n=289, approval=67%)
#    revival   : insufficient_data    (n=12, min_required=30)
```

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/nichochar/ai-marketing-skills.git
cd ai-marketing-skills/sales-pipeline
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Set up campaign config (for RB2B Router)

```bash
cp data/campaigns.json.example data/campaigns.json
# Add your Instantly campaign UUIDs
```

### 4. Test with dry runs

```bash
# Test suppression pipeline
python3 rb2b_suppression_pipeline.py --email test@example.com

# Test intent scoring
echo '{"email":"test@example.com","pages_visited":["https://yoursite.com/pricing"]}' \
  | python3 rb2b_webhook_ingest.py --dry-run

# Test deal resurrector
python3 deal_resurrector.py --top 5 --dry-run

# Test trigger prospector
python3 trigger_prospector.py --days 7 --top 10
```

### 5. Deploy webhook server

```bash
# Start the full pipeline as a webhook endpoint
python3 rb2b_instantly_router.py --serve --port 4100

# Point your RB2B webhook (or Zapier/Make) at:
# POST http://your-server:4100/
```

---

## Customization

### Intent Scoring
Edit `PAGE_INTENT_SCORES` in `rb2b_webhook_ingest.py` to match your site's URL structure:

```python
PAGE_INTENT_SCORES = {
    "pricing": 90,      # Your pricing page path
    "demo": 85,         # Demo request page
    "case-study": 70,   # Social proof pages
    "blog": 30,         # Low-intent content
    # Add your own patterns...
}
```

### Agency Detection
Modify `AGENCY_KEYWORDS_COMPANY` and `AGENCY_INDUSTRIES` in `rb2b_instantly_router.py` for your market.

### Loss Reason Scoring
Customize `LOSS_REASON_BONUS` in `deal_resurrector.py` based on which loss reasons actually convert when revisited.

### Trigger Queries
Edit `SEARCH_QUERIES` in `trigger_prospector.py` to target your specific market signals.

---

## Integrations

| Tool | Required | Used By |
|------|----------|---------|
| [RB2B](https://rb2b.com) | For visitor ID | Webhook Ingest, Router |
| [Instantly](https://instantly.ai) | For cold email | Router, Suppression |
| [HubSpot](https://hubspot.com) | For CRM | Deal Resurrector, Suppression |
| [Brave Search](https://api.search.brave.com) | For web signals | Trigger Prospector |
| PostgreSQL | For ICP learning | ICP Analyzer |
| Stripe | Optional | Suppression (customer check) |

---

## File Structure

```
sales-pipeline/
├── README.md                          # This file
├── SKILL.md                           # Claude Code skill definition
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variable template
├── rb2b_webhook_ingest.py            # Webhook server + intent scoring
├── rb2b_suppression_pipeline.py      # 5-layer suppression checks
├── rb2b_instantly_router.py          # Full pipeline orchestrator
├── deal_resurrector.py               # Dead deal revival engine
├── trigger_prospector.py             # Web signal prospecting
├── icp_learning_analyzer.py          # Self-learning ICP optimization
└── data/
    ├── campaigns.json.example         # Instantly campaign config template
    └── icp-config.example.json        # ICP analyzer config template
```

---

## How It Works Together

1. **RB2B identifies** anonymous website visitors with name, email, company, title
2. **Webhook Ingest** scores their intent based on which pages they viewed
3. **Suppression Pipeline** checks 5 layers to avoid emailing existing contacts
4. **Router** classifies agency vs. non-agency, picks the right campaign, enrolls
5. **Meanwhile**, Deal Resurrector mines your CRM for revival opportunities
6. **Trigger Prospector** scans the web for companies showing buying signals
7. **ICP Analyzer** learns from your approve/reject decisions and tightens targeting

The result: a self-improving pipeline that gets better the more you use it.

---

<div align="center">

**🧠 [Want these built and managed for you? →](https://singlebrain.com/?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills)**

*This is how we build agents at [Single Brain](https://singlebrain.com/?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) for our clients.*

</div>
