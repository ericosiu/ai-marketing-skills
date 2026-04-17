---
name: lead-dossier
description: >
  Multi-source account research, cascade enrichment, and lead pipeline.
  Combines website scraping, tech stack detection, CRM enrichment, hiring/news signals
  into structured dossiers. Includes full lead sourcing pipeline: search → verify → dedupe → upload.
  Triggers on: "research account", "build dossier", "enrich leads", "lead pipeline",
  "source leads", "prospect research", "account intel", "cascade enrichment",
  "lead scoring", "find leads", "verify emails", "upload leads".
---

# Lead Dossier Skill

Multi-source account research and lead enrichment pipeline for AI coding assistants.

## Prerequisites

- Python 3.9+ with `requests` installed
- API keys configured as environment variables (see `.env.example`)
- Optional: CRM access for contact/company enrichment

## Environment Variables

All API keys are configured via environment variables. Copy `.env.example` to `.env`:

| Variable | Description |
|----------|-------------|
| `LEAD_SOURCE_API_KEY` | People/company search API |
| `EMAIL_VALIDATION_API_KEY` | Email verification service |
| `EMAIL_VALIDATION_API_URL` | Email verification endpoint |
| `CAMPAIGN_TOOL_API_KEY` | Outbound campaign platform |
| `CRM_API_KEY` | CRM API key |
| `CRM_BASE_URL` | CRM API base URL |
| `BUILTWITH_API_KEY` | BuiltWith tech detection (free tier works) |

## Workflow 1: Account Research

Use when asked to research a company or build a prospect dossier.

### Collect Parameters

| Parameter | Required | Example |
|-----------|----------|---------|
| Domain | Yes | acme.com |
| Company name | No | Acme Corp |
| Contact name | No | Jane Doe |
| Contact title | No | VP Marketing |

### Run Research

```bash
python3 scripts/account-researcher.py --domain acme.com --company "Acme Corp"
```

For batch research:
```bash
python3 scripts/account-researcher.py prospects.json
```

Results are cached for 7 days in `data/account-research/`.

### Output Format

The engine produces a structured JSON dossier with:
- Website analysis (title, description, body snippet, marketing gaps)
- Tech stack (CRM, marketing tools, enterprise signals)
- Hiring signals (growth indicators)
- News/funding signals
- 3-5 sentence research brief

## Workflow 2: Cascade Enrichment

Use when enriching a list of prospects with verified email addresses.

### Prepare Config

Create `data/enrichment-config.json`:
```json
{
  "email_validation_api_key": "YOUR_KEY",
  "email_validation_api_url": "https://api.your-provider.com/v1/people/email-finder",
  "email_validation_timeout_seconds": 10,
  "fallback_tag": "linkedin-outreach-only"
}
```

### Run Enrichment

```bash
python3 scripts/cascade-enricher.py input.json output.json
```

Waterfall logic:
1. Has email from primary source? → Done
2. Try email finder API → Found? → Done
3. Has LinkedIn URL? → Tag as fallback
4. None → Tag as no-contact

## Workflow 3: Full Lead Pipeline

Use when sourcing, verifying, and uploading leads end-to-end.

### Collect Parameters

| Parameter | Required | Example |
|-----------|----------|---------|
| Titles | Yes | VP Marketing, CMO |
| Industries | Yes | Marketing, SaaS |
| Company size | Yes | 11-50, 51-200 |
| Locations | Yes | United States |
| Campaign ID | Yes | Campaign UUID |
| Volume | Yes | 500 |

### Run Pipeline

```bash
python3 scripts/lead-pipeline.py \
  --source-api-key "$LEAD_SOURCE_API_KEY" \
  --validation-api-key "$EMAIL_VALIDATION_API_KEY" \
  --campaign-api-key "$CAMPAIGN_TOOL_API_KEY" \
  --titles "VP Marketing,CMO,Head of Growth" \
  --industries "Marketing,Advertising" \
  --company-size "11,50" \
  --locations "United States" \
  --campaign-id "CAMPAIGN_UUID" \
  --volume 500 \
  --output-dir ./data/pipeline-runs/
```

Optional flags:
- `--exclude-file /path/to/burned-emails.csv` — additional exclusion list
- `--dry-run` — run everything except the final upload
- `--keywords "SaaS,B2B"` — additional search keywords

### Review Output

Pipeline saves a JSON run log to the output directory with full stats:
- Sourced count, verification rate, dedup stats, upload results
- Complete list of leads processed

## Workflow 4: Real-Time Lead Enrichment

Use for enriching inbound leads from webhooks, forms, or CRM triggers.

### Run Enricher

```bash
python3 scripts/lead-enricher.py [--dry-run] [--backfill N]
```

The enricher:
1. Parses inbound lead data (website forms, voice agent calls, etc.)
2. Looks up contact and company in CRM
3. Runs account research for context
4. Builds an enriched lead card with all available data

## Safety Rules

1. **Never upload unverified leads** — every email must pass validation
2. **Always deduplicate** — check existing contacts before uploading
3. **Log everything** — every run produces an auditable JSON log
4. **Rate limit aware** — built-in delays and exponential backoff
5. **Idempotent** — safe to re-run; duplicates are caught by dedup step
6. **Security gates** — scan all inbound web content before processing

## Troubleshooting

- **Search API returns no results**: Check title/industry spelling; try broader criteria
- **Email validation 429s**: Script handles with backoff; if persistent, reduce volume
- **Campaign tool silent failures**: Some APIs silently block at high request rates; scripts include batch delays
- **Cache stale**: Delete files in `data/account-research/` to force refresh
