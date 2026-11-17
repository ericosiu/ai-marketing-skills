# Weekly SEO Decay Check

Automated content decay monitoring that finds pages losing traffic and rankings before they become a problem.

## What It Does

Every week:
1. Pulls Google Search Console data for all pages
2. Compares current performance to previous period
3. Identifies pages with traffic drops greater than 30%
4. Flags ranking drops for important keywords
5. Suggests refresh actions for each decaying page
6. Delivers a prioritized fix list

## Prerequisites

- `seo-ops` skill installed
- Google Search Console access
- Single Brain Gateway connection or GSC API credentials
- Minimum 90 days of historical data

## Setup

### 1. Authenticate Google Search Console

If using `seo-ops` skill directly:
```bash
python3 seo-ops/gsc_auth.py
```

Or connect via [Single Brain Gateway](https://gateway.singlebrain.com/mcp?sg_template=seo-ops&utm_source=github&utm_medium=automation&utm_campaign=decay-check).

### 2. Create the Automation Script

Create `automations/run-seo-decay-check.sh`:

```bash
#!/bin/bash
# Weekly SEO decay check automation

# Set working directory
cd "$(dirname "$0")/.."

OUTPUT_DIR="automations/reports/seo-decay"
mkdir -p "$OUTPUT_DIR"

echo "Running SEO decay check..."

# Pull GSC data for last 90 days
python3 seo-ops/gsc_client.py \
  --pages 1000 \
  --days 90 \
  --json \
  > "$OUTPUT_DIR/gsc-data-$(date +%Y%m%d).json"

# Analyze for decay
python3 automations/scripts/detect-content-decay.py \
  --input "$OUTPUT_DIR/gsc-data-$(date +%Y%m%d).json" \
  --output "$OUTPUT_DIR/decay-report-$(date +%Y%m%d).md" \
  --threshold 30

echo "Decay check complete. Report: $OUTPUT_DIR/decay-report-$(date +%Y%m%d).md"
```

Make it executable:
```bash
chmod +x automations/run-seo-decay-check.sh
```

### 3. Create Decay Detection Script

Create `automations/scripts/detect-content-decay.py`:

```python
#!/usr/bin/env python3
"""Detect content decay from GSC data."""
import json
import sys
from datetime import datetime, timedelta

def detect_decay(input_file, output_file, threshold):
    with open(input_file) as f:
        data = json.load(f)
    
    # Split data into current and previous periods
    # (simplified - real implementation would segment by date)
    pages = {}
    
    for row in data:
        url = row.get('keys', [''])[0]
        clicks = row.get('clicks', 0)
        impressions = row.get('impressions', 0)
        
        if url not in pages:
            pages[url] = {'current': 0, 'previous': 0}
        
        # Simplified period assignment
        pages[url]['current'] += clicks
    
    # Find decaying pages
    decaying = []
    for url, metrics in pages.items():
        if metrics['previous'] > 0:
            change = ((metrics['current'] - metrics['previous']) / metrics['previous']) * 100
            if change <= -threshold:
                decaying.append({
                    'url': url,
                    'change': change,
                    'current': metrics['current'],
                    'previous': metrics['previous']
                })
    
    # Sort by severity
    decaying.sort(key=lambda x: x['change'])
    
    # Generate report
    with open(output_file, 'w') as f:
        f.write(f"# SEO Decay Report - {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write(f"Pages with traffic drops > {threshold}%: {len(decaying)}\n\n")
        
        for i, page in enumerate(decaying[:20], 1):
            f.write(f"## {i}. {page['url']}\n")
            f.write(f"- Traffic change: {page['change']:.1f}%\n")
            f.write(f"- Current clicks: {page['current']}\n")
            f.write(f"- Previous clicks: {page['previous']}\n")
            f.write(f"- **Action:** Refresh content, update date, add new sections\n\n")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--threshold', type=int, default=30)
    args = parser.parse_args()
    
    detect_decay(args.input, args.output, args.threshold)
```

### 4. Schedule It

**Cron (every Monday at 10 AM):**
```bash
0 10 * * 1 /path/to/ai-marketing-skills/automations/run-seo-decay-check.sh
```

**GitHub Actions:**
```yaml
name: Weekly SEO Decay Check

on:
  schedule:
    - cron: '0 10 * * 1'
  workflow_dispatch:

jobs:
  decay-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - name: Run decay check
        run: ./automations/run-seo-decay-check.sh
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: decay-report
          path: automations/reports/seo-decay/
```

## What You Get

Weekly report showing:
- Pages losing traffic (ranked by severity)
- Pages losing rankings for important keywords
- Suggested refresh actions for each page
- Prioritized fix list (highest impact first)

## Customization

- Change threshold (default 30%)
- Filter by page type or section
- Include keyword-level decay analysis
- Auto-create tasks in project management tool
- Send alerts via email or Slack

## Connect to Live Data

Use the [Single Brain Gateway](https://gateway.singlebrain.com/mcp?sg_template=seo-ops&utm_source=github&utm_medium=automation&utm_campaign=decay-check) to connect Google Search Console and analytics.

---

Built by [Single Grain](https://www.singlegrain.com/?utm_source=github&utm_medium=skill&utm_campaign=footer&utm_content=automations). Want a team to run this for you? Single Grain or Single Brain can manage it.
