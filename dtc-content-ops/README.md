# DTC Content Ops

**Multi-brand daily content engine for direct-to-consumer businesses.**

Generate, score, and manage daily social media content across multiple DTC brands and platforms with product rotation, expert panel scoring, and human-in-the-loop approval dashboards.

## When to Use

- "Generate daily content for my brands"
- "Run the content engine"
- "Create product posts across all platforms"
- "Build a review dashboard"
- "Check product rotation status"
- "Score this content"
- "Set up multi-brand content pipeline"

## What It Does

1. **Product Rotation** — Tier-weighted round-robin selects today's featured product with configurable cooldowns
2. **Content Generation** — Platform-specific content for each brand using education-first approach (lead with the problem, then reference the product)
3. **Expert Panel Scoring** — Auto-assembled panel of DTC, compliance, and platform experts iteratively scores content to 90/100
4. **Quality Gate** — Banned phrases, character limits, brand routing, and media cooldown enforcement
5. **Review Dashboard** — Interactive HTML dashboard with approve/reject per post, inline media previews, and JSON export
6. **Rotation Logging** — Tracks product featuring history, image usage, and cross-sell CTA cadence

## Tools

| Tool | Command | Purpose |
|------|---------|---------|
| Content Engine | `python3 scripts/content_engine.py generate` | Generate daily content for all brands |
| Product Rotation | `python3 scripts/product_rotation.py next` | Get next product in rotation |
| Quality Gate | `python3 scripts/content_quality_gate.py` | Score and validate content |
| Review Dashboard | `python3 scripts/review_dashboard.py` | Build HTML approval dashboard |
| Brand Router | `python3 scripts/brand_router.py` | Validate brand→platform routing |

## Quick Start

### 1. Configure Your Brands

Copy the example config and customize for your business:

```bash
cp references/multi-brand-config.example.json my-brand-config.json
cp references/product-rotation-config.example.json my-rotation.json
```

Edit `my-brand-config.json` to define your brands, platforms, tone rules, and accounts.

### 2. Generate Content

```bash
python3 scripts/content_engine.py generate \
  --brand-config my-brand-config.json \
  --rotation-config my-rotation.json \
  --date 2026-04-01
```

### 3. Review and Approve

```bash
python3 scripts/review_dashboard.py \
  --input output/pending/2026-04-01.json \
  --output review.html
```

Open `review.html` in your browser. Approve or reject each post. Export the approved JSON.

### 4. Check Rotation Status

```bash
python3 scripts/product_rotation.py status --config my-rotation.json
```

## Architecture

```
┌─────────────────────────────────┐
│        Brand Config JSON        │  ← Define brands, platforms, tone
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│     Product Rotation Engine     │  ← Tier-weighted round-robin
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│      Content Generator          │  ← Education-first, per-platform
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│      Expert Panel Scoring       │  ← 3 experts, iterate to 90/100
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│        Quality Gate             │  ← Banned phrases, limits, routing
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│     Review Dashboard (HTML)     │  ← Human approves/rejects
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│    Approved Content JSON        │  ← Ready for posting scripts
└─────────────────────────────────┘
```

## Configuration

### Environment Variables

```bash
# Required for AI content generation
ANTHROPIC_API_KEY=sk-your-key-here

# Optional: override default model
DTC_CONTENT_MODEL=claude-sonnet-4-6
```

### Multi-Brand Config Schema

See `references/multi-brand-config.example.json` for the full schema. Key sections:

- `businesses` — Map of brand keys to brand definitions
- `businesses.{key}.platform_rules` — Per-platform enable/disable, media types, character limits
- `businesses.{key}.tone` — Brand voice description
- `businesses.{key}.accounts` — Platform account handles and API env var names

### Product Rotation Config Schema

See `references/product-rotation-config.example.json`. Key sections:

- `products` — Array of products with name, tier, category, education angles
- `next_in_rotation` — Current product in queue
- `rotation_log` — History of featured products with dates

## Dependencies

```
anthropic>=0.40.0
jinja2>=3.1.0
```

Install:
```bash
pip install -r requirements.txt
```

## Key Design Decisions

1. **Education-first content**: Every post leads with the customer's problem, then references the product. Never lead with the product. This outperforms promotional content for DTC brands.

2. **Tier-based rotation**: Not all products are equal. Tier 1 (hero products) get 2x featuring frequency. Tier 3 (low performers) get 1x at end of cycle. Configurable.

3. **Human-in-the-loop**: Content is NEVER auto-published. The review dashboard requires explicit per-post approval. This is a safety requirement for regulated industries (supplements, health, finance).

4. **Expert panel scoring**: Content isn't just checked against banned phrases — it's scored by domain experts on four dimensions (hook, voice, value, compliance) and iterated until 90/100.

5. **Platform-native formatting**: Each platform gets purpose-built content, not the same post copy-pasted. X gets 280-char hooks, Instagram gets full captions with hashtags, blogs get SEO-optimized HTML.
