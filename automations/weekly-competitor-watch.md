# Weekly Competitor Watch

Automated competitor monitoring that runs the `seo-ops` skill on a schedule to track competitor content, keywords, and positioning changes.

## What It Does

Every week (or whatever cadence you choose):
1. Runs competitor gap analysis from `seo-ops` skill
2. Checks for new content published by competitors
3. Finds keywords competitors are ranking for that you are not
4. Alerts you to significant positioning changes
5. Delivers a summary report

## Prerequisites

- `seo-ops` skill installed
- `brand/competitors.md` file created (run `start-here` first)
- Ahrefs API key (or alternative SEO tool via [Single Brain Gateway](https://gateway.singlebrain.com/mcp?sg_template=seo-ops&utm_source=github&utm_medium=automation&utm_campaign=competitor-watch))
- Competitor domain list

## Setup

### 1. Create Competitor List

Create a file `automations/competitor-domains.txt` with one domain per line:

```
competitor1.com
competitor2.com
competitor3.com
```

### 2. Create the Automation Script

Create `automations/run-competitor-watch.sh`:

```bash
#!/bin/bash
# Weekly competitor watch automation

# Set working directory
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
cd "$SCRIPT_DIR/.."

# Check for brand files
if [ ! -f "brand/competitors.md" ]; then
  echo "Error: brand/competitors.md not found. Run start-here skill first."
  exit 1
fi

# Run competitor gap analysis for each domain
while IFS= read -r domain; do
  echo "Analyzing $domain..."
  python3 seo-ops/content_attack_brief.py --competitor "$domain" --output "automations/reports/competitor-$domain-$(date +%Y%m%d).json"
done < automations/competitor-domains.txt

# Generate summary report
python3 automations/scripts/summarize-competitor-changes.py

echo "Competitor watch complete. Report saved to automations/reports/competitor-summary-$(date +%Y%m%d).md"
```

Make it executable:
```bash
chmod +x automations/run-competitor-watch.sh
```

### 3. Schedule It

**Option A: Cron (Linux/Mac)**

```bash
# Edit crontab
crontab -e

# Add this line to run every Monday at 9 AM
0 9 * * 1 /path/to/ai-marketing-skills/automations/run-competitor-watch.sh
```

**Option B: GitHub Actions**

Create `.github/workflows/competitor-watch.yml`:

```yaml
name: Weekly Competitor Watch

on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC
  workflow_dispatch:  # Allow manual trigger

jobs:
  competitor-watch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Run competitor watch
        env:
          AHREFS_TOKEN: ${{ secrets.AHREFS_TOKEN }}
        run: ./automations/run-competitor-watch.sh
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: competitor-report
          path: automations/reports/
```

**Option C: Agent Scheduler**

If your agent supports scheduled tasks, create a prompt:

```
Run the seo-ops skill competitor gap analysis for domains in automations/competitor-domains.txt.
Save results to automations/reports/.
Schedule this to run every Monday at 9 AM.
```

## What You Get

Weekly report showing:
- New keywords competitors are ranking for
- Content gaps (topics they cover, you don't)
- Ranking changes (up/down movements)
- New backlinks competitors acquired
- Suggested action items

## Customization

Edit the script to:
- Change frequency (daily, bi-weekly, monthly)
- Add more competitors
- Filter by keyword difficulty or search volume
- Send results via email or Slack
- Connect to your CRM or project management tool

## Connect to Live Data

Use the [Single Brain Gateway](https://gateway.singlebrain.com/mcp?sg_template=seo-ops&utm_source=github&utm_medium=automation&utm_campaign=competitor-watch) to connect SEO tools, analytics, and data sources.

---

Built by [Single Grain](https://www.singlegrain.com/?utm_source=github&utm_medium=skill&utm_campaign=footer&utm_content=automations). Want a team to run this for you? Single Grain or Single Brain can manage it.
