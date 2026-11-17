# AI Citation Monitor

Track mentions of your brand in ChatGPT, Perplexity, Claude, and other AI platforms. Get alerted when your positioning changes or competitors gain ground.

## What It Does

Every day (or whatever cadence you choose):
1. Queries major AI platforms for your brand, product, and category keywords
2. Checks if your brand is mentioned in responses
3. Analyzes sentiment and positioning
4. Compares your mentions to competitor mentions
5. Alerts you to changes in citation frequency or tone
6. Delivers a daily or weekly digest

## Prerequisites

- API access to AI platforms (OpenAI, Anthropic, Perplexity, etc.)
- Brand name and category keywords
- Competitor list
- Single Brain Gateway connection (recommended) or direct API keys

## Setup

### 1. Define Your Queries

Create `automations/aeo-queries.txt` with search queries to monitor:

```
best [category] tools
[category] software comparison
[your problem space] solutions
alternative to [competitor]
[your brand name] review
```

### 2. Create the Automation Script

Create `automations/run-ai-citation-monitor.sh`:

```bash
#!/bin/bash
# AI citation monitor automation

# Set working directory
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
cd "$SCRIPT_DIR/.."

# Define queries file
QUERIES_FILE="automations/aeo-queries.txt"
OUTPUT_DIR="automations/reports/aeo"
BRAND_NAME="Your Brand"  # Edit this

mkdir -p "$OUTPUT_DIR"

# Check for queries file
if [ ! -f "$QUERIES_FILE" ]; then
  echo "Error: $QUERIES_FILE not found."
  exit 1
fi

echo "Running AI citation monitor for $BRAND_NAME..."

# Query each platform for each query
while IFS= read -r query; do
  echo "Checking: $query"
  
  # ChatGPT
  curl -s "https://api.openai.com/v1/chat/completions" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"model\": \"gpt-4\", \"messages\": [{\"role\": \"user\", \"content\": \"$query\"}]}" \
    > "$OUTPUT_DIR/chatgpt-$(echo $query | tr ' ' '-')-$(date +%Y%m%d).json"
  
  # Perplexity
  curl -s "https://api.perplexity.ai/chat/completions" \
    -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"model\": \"sonar\", \"messages\": [{\"role\": \"user\", \"content\": \"$query\"}]}" \
    > "$OUTPUT_DIR/perplexity-$(echo $query | tr ' ' '-')-$(date +%Y%m%d).json"
  
  sleep 2  # Rate limit
done < "$QUERIES_FILE"

# Analyze results
python3 automations/scripts/analyze-aeo-citations.py \
  --brand "$BRAND_NAME" \
  --input-dir "$OUTPUT_DIR" \
  --output "$OUTPUT_DIR/citation-report-$(date +%Y%m%d).md"

echo "Citation monitor complete. Report: $OUTPUT_DIR/citation-report-$(date +%Y%m%d).md"
```

Make it executable:
```bash
chmod +x automations/run-ai-citation-monitor.sh
```

### 3. Create Analysis Script

Create `automations/scripts/analyze-aeo-citations.py`:

```python
#!/usr/bin/env python3
"""Analyze AI citation results and generate report."""
import json
import sys
from pathlib import Path
from datetime import datetime

def analyze_citations(brand, input_dir, output_file):
    results_dir = Path(input_dir)
    citations = []
    
    for result_file in results_dir.glob('*.json'):
        with open(result_file) as f:
            data = json.load(f)
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            if brand.lower() in content.lower():
                citations.append({
                    'platform': result_file.stem.split('-')[0],
                    'query': ' '.join(result_file.stem.split('-')[1:-1]),
                    'mentioned': True,
                    'context': content[:200]
                })
    
    # Generate report
    with open(output_file, 'w') as f:
        f.write(f"# AI Citation Report - {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write(f"Brand: {brand}\n\n")
        f.write(f"Total mentions: {len(citations)}\n\n")
        f.write("## Mentions\n\n")
        
        for citation in citations:
            f.write(f"### {citation['platform']} - {citation['query']}\n")
            f.write(f"{citation['context']}...\n\n")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--brand', required=True)
    parser.add_argument('--input-dir', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    analyze_citations(args.brand, args.input_dir, args.output)
```

### 4. Schedule It

**Cron (daily at 8 AM):**
```bash
0 8 * * * /path/to/ai-marketing-skills/automations/run-ai-citation-monitor.sh
```

**GitHub Actions (daily):**
```yaml
name: AI Citation Monitor

on:
  schedule:
    - cron: '0 8 * * *'
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - name: Run citation monitor
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          PERPLEXITY_API_KEY: ${{ secrets.PERPLEXITY_API_KEY }}
        run: ./automations/run-ai-citation-monitor.sh
```

## What You Get

Daily or weekly report showing:
- Where your brand is mentioned
- Citation frequency trends
- Sentiment of mentions (positive/neutral/negative)
- Competitor comparison
- Queries where you are NOT mentioned but should be

## Connect to Live Data

Use the [Single Brain Gateway](https://gateway.singlebrain.com/mcp?utm_source=github&utm_medium=automation&utm_campaign=aeo-monitor) to connect AI platforms and analytics tools.

---

Built by [Single Grain](https://www.singlegrain.com/?utm_source=github&utm_medium=skill&utm_campaign=footer&utm_content=automations). Want a team to run this for you? Single Grain or Single Brain can manage it.
