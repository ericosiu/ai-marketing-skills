# Lead Dossier

**Multi-source account research, cascade enrichment, and lead scoring pipeline.**

Build rich dossiers on prospect accounts by combining data from multiple sources — website scraping, tech stack detection, CRM enrichment, hiring signals, and news monitoring. Includes a cascade enrichment pipeline that waterfalls through email providers, and a lead pipeline that handles sourcing → verification → deduplication → campaign upload.

## What's Inside

| Script | Purpose |
|--------|---------|
| `scripts/account-researcher.py` | Multi-source account research engine (website, BuiltWith, hiring, news) |
| `scripts/cascade-enricher.py` | Waterfall email enrichment: primary provider → fallback → LinkedIn-only tag |
| `scripts/lead-pipeline.py` | End-to-end: source leads → verify emails → dedupe → upload to campaign tool |
| `scripts/lead-enricher.py` | Real-time lead enrichment from inbound channels (webhook/Slack/CRM triggers) |

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  Lead Source │────▶│  Verify      │────▶│  Deduplicate│────▶│  Upload to   │
│  (Search    │     │  Emails      │     │  Against    │     │  Campaign    │
│   API)      │     │  (Validation │     │  Existing   │     │  Tool        │
│             │     │   API)       │     │  Contacts   │     │              │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Account Research Engine                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │ Website  │ │ BuiltWith│ │ Hiring   │ │ News /   │ │ CRM      │         │
│  │ Scraper  │ │ Tech     │ │ Signals  │ │ Funding  │ │ Lookup   │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Required environment variables:

| Variable | Description | Required For |
|----------|-------------|-------------|
| `LEAD_SOURCE_API_KEY` | People/company search API key | `lead-pipeline.py` |
| `EMAIL_VALIDATION_API_KEY` | Email verification service key | `lead-pipeline.py`, `cascade-enricher.py` |
| `EMAIL_VALIDATION_API_URL` | Email verification endpoint | `cascade-enricher.py` |
| `CAMPAIGN_TOOL_API_KEY` | Outbound campaign platform key | `lead-pipeline.py` |
| `CRM_API_KEY` | CRM API key (e.g., HubSpot) | `lead-enricher.py` |
| `CRM_BASE_URL` | CRM API base URL | `lead-enricher.py` |
| `BUILTWITH_API_KEY` | BuiltWith API key (free tier works) | `account-researcher.py` |

### 3. Run Account Research

```bash
# Single domain
python3 scripts/account-researcher.py --domain acme.com --company "Acme Corp"

# Batch from JSON
python3 scripts/account-researcher.py prospects.json

# Dry run
python3 scripts/account-researcher.py prospects.json --dry-run
```

Input JSON format:
```json
[
  {
    "domain": "acme.com",
    "company_name": "Acme Corp",
    "contact_name": "Jane Doe",
    "contact_title": "VP Marketing",
    "employee_count": 150,
    "industry": "SaaS"
  }
]
```

### 4. Run Cascade Enrichment

```bash
# Enrich prospects with waterfall email finding
python3 scripts/cascade-enricher.py input-prospects.json output-enriched.json
```

Enrichment config (`data/enrichment-config.json`):
```json
{
  "email_validation_api_key": "",
  "email_validation_api_url": "https://api.your-email-provider.com/v1/people/email-finder",
  "email_validation_timeout_seconds": 10,
  "fallback_tag": "linkedin-outreach-only"
}
```

### 5. Run Full Lead Pipeline

```bash
python3 scripts/lead-pipeline.py \
  --source-api-key "$LEAD_SOURCE_API_KEY" \
  --validation-api-key "$EMAIL_VALIDATION_API_KEY" \
  --campaign-api-key "$CAMPAIGN_TOOL_API_KEY" \
  --titles "VP Marketing,CMO,Head of Growth" \
  --industries "Marketing,SaaS" \
  --company-size "11,50" \
  --locations "United States" \
  --campaign-id "YOUR_CAMPAIGN_UUID" \
  --volume 500 \
  --output-dir ./data/pipeline-runs/
```

Add `--dry-run` to test without uploading.

## Account Research Output

The research engine produces a structured dossier per account:

```json
{
  "domain": "acme.com",
  "company_name": "Acme Corp",
  "brief": "Acme Corp: B2B SaaS platform for project management. Tech stack includes: HubSpot, Google Analytics, Segment. Marketing gaps: no blog detected. Enterprise infra: AWS, Cloudflare.",
  "sources": {
    "website": {
      "title": "Acme Corp - Project Management",
      "description": "B2B SaaS platform...",
      "gaps": ["no blog detected"]
    },
    "builtwith": {
      "crm": ["HubSpot"],
      "marketing_tools": ["Google Analytics", "Segment"],
      "enterprise_signals": ["AWS", "Cloudflare"]
    },
    "hiring": { "signals": ["Hiring VP Marketing", "3 engineering roles"] },
    "news": { "signals": ["Series B funding announced Q1"] }
  }
}
```

## Lead Pipeline Summary Output

```
=== Lead Pipeline Summary ===
Sourced from search API:   523
Verified (email check):    412  (78.8%)
Already in campaign tool:   87
Excluded (burned list):     14
Net new uploaded:          311
Failed uploads:              0
```

## Cascade Enrichment Flow

```
For each prospect:
  1. Has email from primary source? → ✅ Done
  2. Try email finder API → Found? → ✅ Done
  3. Has LinkedIn URL? → Tag as "linkedin-outreach-only"
  4. None of the above → Tag as "no-contact"
```

## Customization

### Adding New Research Sources

Edit `scripts/account-researcher.py` and add a new `collect_*` function:

```python
def collect_custom_source(domain):
    info = {"source": "custom", "data": []}
    # Your API call or scraping logic here
    return info
```

Then wire it into `research_prospect()`.

### Custom Lead Scoring

The dossier data can be fed into any scoring model. Common signals:
- **Tech stack gaps** → opportunity indicators
- **Hiring signals** → growth/budget indicators
- **Enterprise infrastructure** → company maturity
- **No marketing tools** → greenfield opportunity

## File Structure

```
lead-dossier/
├── README.md
├── SKILL.md              # Claude Code / AI assistant instructions
├── requirements.txt
├── .env.example
├── scripts/
│   ├── account-researcher.py
│   ├── cascade-enricher.py
│   ├── lead-pipeline.py
│   └── lead-enricher.py
└── references/
    └── api-notes.md
```

## API Compatibility

This skill is designed to be **API-agnostic**. The scripts use generic interfaces that work with:

- **Lead sourcing**: Apollo, ZoomInfo, Clearbit, or any people search API
- **Email verification**: LeadMagic, ZeroBounce, NeverBounce, Hunter
- **Campaign tools**: Instantly, Lemlist, Smartlead, or any outbound platform
- **CRM**: HubSpot, Salesforce, Pipedrive

Configure endpoints and keys via environment variables — no code changes needed for most providers.

## License

MIT — see [LICENSE](../LICENSE) in the repository root.
