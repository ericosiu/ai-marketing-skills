# Content Repurposing

Automatically turn existing content into new formats. One podcast episode becomes 20+ pieces across every platform.

## What It Does

On a schedule (daily or weekly):
1. Scans for new content (podcast episodes, blog posts, videos)
2. Extracts key moments, quotes, and insights
3. Generates repurposed content in multiple formats
4. Saves drafts for human review
5. Optionally publishes approved pieces automatically

## Prerequisites

- `podcast-ops` or `content-ops` skill installed
- Source content library (podcasts, videos, blog posts)
- Destination platforms (X, LinkedIn, YouTube, blog)
- Single Brain Gateway connection (recommended)

## Setup

### 1. Define Source Content

Create `automations/content-sources.txt`:

```
https://example.com/podcast/rss-feed.xml
https://youtube.com/channel/UC...
https://example.com/blog/
```

### 2. Create the Automation Script

Create `automations/run-content-repurposing.sh`:

```bash
#!/bin/bash
# Content repurposing automation

# Set working directory
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
cd "$SCRIPT_DIR/.."

OUTPUT_DIR="automations/reports/repurposed-content"
SOURCES_FILE="automations/content-sources.txt"

mkdir -p "$OUTPUT_DIR"

echo "Running content repurposing pipeline..."

# Check for new content
python3 automations/scripts/check-new-content.py \
  --sources "$SOURCES_FILE" \
  --since "7 days ago" \
  > "$OUTPUT_DIR/new-content-$(date +%Y%m%d).json"

# Process each new piece
jq -r '.[]' "$OUTPUT_DIR/new-content-$(date +%Y%m%d).json" | while read -r url; do
  echo "Repurposing: $url"
  
  # Run podcast-ops pipeline
  python3 podcast-ops/repurpose_episode.py \
    --url "$url" \
    --output-dir "$OUTPUT_DIR/$(date +%Y%m%d)"
done

echo "Repurposing complete. Drafts saved to $OUTPUT_DIR"
```

Make it executable:
```bash
chmod +x automations/run-content-repurposing.sh
```

### 3. Create Content Checker Script

Create `automations/scripts/check-new-content.py`:

```python
#!/usr/bin/env python3
"""Check for new content from sources."""
import json
import sys
from datetime import datetime, timedelta
import feedparser

def check_new_content(sources_file, since_days):
    with open(sources_file) as f:
        sources = [line.strip() for line in f if line.strip()]
    
    new_content = []
    cutoff = datetime.now() - timedelta(days=since_days)
    
    for source in sources:
        if 'rss' in source or 'feed' in source:
            # RSS feed
            feed = feedparser.parse(source)
            for entry in feed.entries:
                pub_date = datetime(*entry.published_parsed[:6])
                if pub_date > cutoff:
                    new_content.append(entry.link)
        
        # Add more source types (YouTube, blog scraping, etc.)
    
    print(json.dumps(new_content))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--sources', required=True)
    parser.add_argument('--since', default='7 days ago')
    args = parser.parse_args()
    
    since_days = int(args.since.split()[0])
    check_new_content(args.sources, since_days)
```

### 4. What Gets Created

For each source content piece, the automation creates:

**From Podcast Episodes:**
- 1 blog post (transcript + key points)
- 5-10 social posts (quotes)
- 3-5 short video clips (highlight moments)
- 1 LinkedIn article
- 1 X thread
- 1 newsletter section
- 5-10 quote graphics
- 1 YouTube video (edited highlights)

**From Blog Posts:**
- 5-10 social posts
- 1 video script
- 1 slide deck
- 1 LinkedIn article (rephrased)
- 3-5 quote graphics
- 1 infographic outline

**From Videos:**
- 1 blog post (transcript summary)
- 3-10 short clips
- 5-10 social posts
- 1 X thread
- Quote graphics from key moments

### 5. Schedule It

**Cron (daily at 6 AM):**
```bash
0 6 * * * /path/to/ai-marketing-skills/automations/run-content-repurposing.sh
```

**GitHub Actions:**
```yaml
name: Daily Content Repurposing

on:
  schedule:
    - cron: '0 6 * * *'
  workflow_dispatch:

jobs:
  repurpose:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - name: Install dependencies
        run: pip install feedparser jq
      - name: Run repurposing
        run: ./automations/run-content-repurposing.sh
      - name: Upload drafts
        uses: actions/upload-artifact@v3
        with:
          name: repurposed-content
          path: automations/reports/repurposed-content/
```

## Human Review Gate

All generated content is saved as drafts. A human must review and approve before publishing.

To auto-publish approved pieces, add a publication step:

```bash
# After repurposing
python3 automations/scripts/publish-approved.py \
  --drafts-dir "$OUTPUT_DIR/$(date +%Y%m%d)" \
  --platforms "x,linkedin,youtube"
```

## What You Get

For each new piece of source content:
- 20+ repurposed assets in multiple formats
- Drafts ready for review
- Optional auto-publishing for approved content
- Content calendar populated weeks in advance

## Customization

- Change source types (add newsletters, webinars, etc.)
- Change output formats
- Filter by topic or keyword
- Add brand voice consistency checks
- Connect to content management tools
- Auto-schedule publishing times

## Connect to Live Data

Use the [Single Brain Gateway](https://gateway.singlebrain.com/mcp?utm_source=github&utm_medium=automation&utm_campaign=content-repurposing) to connect podcast hosting, YouTube, social platforms, and CMS tools.

---

Built by [Single Grain](https://www.singlegrain.com/?utm_source=github&utm_medium=skill&utm_campaign=footer&utm_content=automations). Want a team to run this for you? Single Grain or Single Brain can manage it.
