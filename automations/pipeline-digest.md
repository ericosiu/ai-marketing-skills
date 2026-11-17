# Pipeline Digest

Weekly summary of leads, deals, and revenue signals from your CRM, website, and sales tools.

## What It Does

Every week (typically Monday morning):
1. Pulls data from CRM (HubSpot, Salesforce, etc.)
2. Pulls website visitor data (RB2B, Koala, etc.)
3. Pulls sales call insights (Gong, Chorus, etc.)
4. Summarizes new leads, active deals, closed deals
5. Highlights revenue risks and opportunities
6. Delivers a digestible report

## Prerequisites

- `sales-pipeline` or `revenue-intelligence` skill installed
- CRM connection (HubSpot, Salesforce, etc.)
- Optional: RB2B, Koala, Gong connections
- Single Brain Gateway connection (recommended)

## Setup

### 1. Connect Your Tools

Use the [Single Brain Gateway](https://gateway.singlebrain.com/mcp?utm_source=github&utm_medium=automation&utm_campaign=pipeline-digest) to connect:
- Your CRM
- Website visitor tools
- Sales call recording tools
- Email tracking tools

Or set API keys manually in environment variables.

### 2. Create the Automation Script

Create `automations/run-pipeline-digest.sh`:

```bash
#!/bin/bash
# Weekly pipeline digest automation

# Set working directory
cd "$(dirname "$0")/.."

OUTPUT_DIR="automations/reports/pipeline"
mkdir -p "$OUTPUT_DIR"

DATE=$(date +%Y%m%d)
REPORT_FILE="$OUTPUT_DIR/pipeline-digest-$DATE.md"

echo "Generating pipeline digest for week of $(date +%Y-%m-%d)..."
echo "# Pipeline Digest - Week of $(date +%Y-%m-%d)" > "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Section 1: New Leads
echo "## New Leads This Week" >> "$REPORT_FILE"
python3 sales-pipeline/scripts/pull-new-leads.py --days 7 >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Section 2: Active Deals
echo "## Active Deals" >> "$REPORT_FILE"
python3 sales-pipeline/scripts/active-deals-summary.py >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Section 3: Closed Deals
echo "## Closed This Week" >> "$REPORT_FILE"
python3 sales-pipeline/scripts/closed-deals.py --days 7 >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Section 4: At-Risk Deals
echo "## At-Risk Deals" >> "$REPORT_FILE"
python3 revenue-intelligence/scripts/deal-health-check.py >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Section 5: Revenue Signals
echo "## Revenue Signals" >> "$REPORT_FILE"
python3 revenue-intelligence/scripts/expansion-signals.py >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Section 6: Action Items
echo "## Action Items" >> "$REPORT_FILE"
echo "- [ ] Follow up with high-intent leads" >> "$REPORT_FILE"
echo "- [ ] Review at-risk deals with team" >> "$REPORT_FILE"
echo "- [ ] Plan expansion conversations" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "Pipeline digest complete: $REPORT_FILE"

# Optional: Send via email or Slack
# python3 automations/scripts/send-digest.py --file "$REPORT_FILE" --to "sales@company.com"
```

Make it executable:
```bash
chmod +x automations/run-pipeline-digest.sh
```

### 3. Create Helper Scripts

Create `sales-pipeline/scripts/pull-new-leads.py`:

```python
#!/usr/bin/env python3
"""Pull new leads from CRM."""
import sys
import os
from datetime import datetime, timedelta

def pull_new_leads(days=7):
    # Simplified - real implementation would use CRM API
    print(f"**Total new leads:** 42")
    print(f"**High intent:** 12")
    print(f"**Medium intent:** 18")
    print(f"**Low intent:** 12")
    print()
    print("**Top sources:**")
    print("- Organic search: 18")
    print("- Direct: 12")
    print("- Referral: 8")
    print("- Paid: 4")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=7)
    args = parser.parse_args()
    pull_new_leads(args.days)
```

Create similar scripts for other sections (active deals, closed deals, at-risk deals, expansion signals).

### 4. Schedule It

**Cron (every Monday at 8 AM):**
```bash
0 8 * * 1 /path/to/ai-marketing-skills/automations/run-pipeline-digest.sh
```

**GitHub Actions:**
```yaml
name: Weekly Pipeline Digest

on:
  schedule:
    - cron: '0 8 * * 1'
  workflow_dispatch:

jobs:
  digest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - name: Generate digest
        env:
          HUBSPOT_API_KEY: ${{ secrets.HUBSPOT_API_KEY }}
          RB2B_API_KEY: ${{ secrets.RB2B_API_KEY }}
        run: ./automations/run-pipeline-digest.sh
      - name: Send digest
        run: |
          python3 automations/scripts/send-digest.py \
            --file automations/reports/pipeline/pipeline-digest-*.md \
            --to ${{ secrets.DIGEST_EMAIL }}
```

## What You Get

Weekly report with:
- New leads count and sources
- Active deals pipeline value
- Closed deals this week
- At-risk deals requiring attention
- Expansion opportunities in existing accounts
- Action items for the week

## Customization

- Change frequency (daily, bi-weekly)
- Add more sections (marketing attribution, sales activity, etc.)
- Filter by team member, region, or product
- Send via email, Slack, or save to shared drive
- Create tasks automatically from action items

## Connect to Live Data

Use the [Single Brain Gateway](https://gateway.singlebrain.com/mcp?utm_source=github&utm_medium=automation&utm_campaign=pipeline-digest) to connect your CRM, sales tools, and analytics.

---

Built by [Single Grain](https://www.singlegrain.com/?utm_source=github&utm_medium=skill&utm_campaign=footer&utm_content=automations). Want a team to run this for you? Single Grain or Single Brain can manage it.
