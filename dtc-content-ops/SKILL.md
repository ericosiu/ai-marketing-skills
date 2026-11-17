---
name: dtc-content-engine
description: >-
  Generate, score, and manage daily multi-brand social media content for DTC
  (direct-to-consumer) businesses. Handles product rotation with tier-based
  featuring and cooldowns, platform-specific content formatting, quality scoring
  with expert panels, and interactive HTML review dashboards for human approval.
  Use when asked to: "generate daily content", "run the content engine",
  "create product posts", "build a review dashboard", "check product rotation",
  "score this content", "multi-brand content", "DTC content pipeline".
---

## Preamble

```bash
python3 telemetry/version_check.py 2>/dev/null || true
python3 telemetry/telemetry_init.py 2>/dev/null || true
```

## Workflow

### Step 1 — Brand Configuration Intake

Load the multi-brand configuration that defines your DTC businesses, platforms, and tone rules.

- Read `config/defaults.json` for engine defaults (cooldown days, CTA frequency, quality threshold)
- Read the user's `multi-brand-config.json` (or use `references/multi-brand-config.example.json` as a starting point)
- For each brand, confirm: name, platforms enabled, tone/voice rules, platform-specific constraints (char limits, aspect ratios, media types)
- If no config exists, walk the user through creating one interactively

### Step 2 — Product Rotation

Select today's featured product(s) using tier-weighted round-robin with configurable cooldowns.

```bash
python3 dtc-content-ops/scripts/product_rotation.py status --config <rotation_config>
python3 dtc-content-ops/scripts/product_rotation.py next --config <rotation_config>
```

- **Tier system**: Tier 1 products are featured more frequently (configurable: default 2x per cycle), Tier 2 once per cycle, Tier 3 once at end of cycle
- **Cooldown enforcement**: No product featured again within N days (configurable, default 3)
- **Cross-sell CTA**: Every Nth post (configurable, default 3) includes a cross-sell CTA for a secondary product or subscription
- **Education angle rotation**: Each product has multiple education angles; rotated daily by day-of-year

### Step 3 — Content Generation

Generate platform-specific content for each brand using an education-first approach.

```bash
python3 dtc-content-ops/scripts/content_engine.py generate \
  --brand-config <multi_brand_config.json> \
  --rotation-config <product_rotation.json> \
  --date <YYYY-MM-DD>
```

For each enabled brand × platform combination:
- Load the brand's voice/tone rules
- Load today's product and education angle
- Generate content that **leads with the problem the product solves**, then references the product naturally
- Respect platform constraints (character limits, hashtag conventions, media format requirements)
- Output structured JSON per platform: text, media references, metadata

### Step 4 — Expert Panel Scoring

Auto-assemble a DTC-specific expert panel and iteratively score content to 90/100.

The panel draws from `experts/` markdown files:
- **DTC Product Copy Expert** (`experts/dtc-product-copy.md`) — Evaluates problem-first framing, mechanism clarity, educational value, CTA placement
- **Claims Compliance Expert** (`experts/supplement-claims.md`) — Flags unsubstantiated health claims, regulatory violations, banned phrases
- **Platform Native Expert** (`experts/social-platform-native.md`) — Validates platform-specific formatting, character limits, hashtag best practices

Scoring uses `scoring-rubrics/dtc-content-quality.md`:
- **Problem-First Hook** (25 pts): Does it lead with the customer's pain?
- **Voice Authenticity** (25 pts): Does it sound like the brand founder, not ChatGPT?
- **Value Density** (25 pts): Does every sentence teach or solve?
- **Compliance + Platform Fit** (25 pts): Correct limits, no banned phrases, native formatting?

**Iteration loop**: If score < 90, provide specific feedback and regenerate. Max 3 iterations.

### Step 5 — Quality Gate

Run final compliance checks before content enters the review dashboard.

```bash
python3 dtc-content-ops/scripts/content_quality_gate.py \
  --input <pending_content.json> \
  --banned-phrases <banned_phrases.json>
```

Checks:
- Character limit enforcement per platform
- Banned phrase detection (marketing hype, generic AI voice, regulatory violations)
- Brand routing validation (correct brand → correct platform → correct account)
- Image/media cooldown enforcement
- Duplicate content detection (no repeat posts within rolling window)

Each post receives a verdict: `PASS`, `WARN`, or `FAIL` with specific issue descriptions.

### Step 6 — Review Dashboard

Generate an interactive HTML dashboard for human approval.

```bash
python3 dtc-content-ops/scripts/review_dashboard.py \
  --input <pending_content.json> \
  --output <review_dashboard.html>
```

Dashboard features:
- Per-post approve/reject buttons
- Inline media previews (base64 embedded for offline viewing)
- Quality score badges per post
- Bulk approve/reject all
- Export approved content as JSON
- Copy individual post text to clipboard

### Step 7 — Output and Logging

Save approved content and update rotation state.

- Write approved content to `output/approved/<date>.json`
- Update product rotation log (which product was featured, when)
- Update image/media usage log for cooldown tracking
- Generate summary: posts approved, rejected, by brand and platform

```bash
python3 dtc-content-ops/scripts/content_engine.py status --date <YYYY-MM-DD>
```

## Reference Files

- `experts/dtc-product-copy.md` — DTC product content expert panel definition
- `experts/supplement-claims.md` — Regulated claims compliance expert
- `experts/social-platform-native.md` — Platform-specific formatting expert
- `scoring-rubrics/dtc-content-quality.md` — Four-dimension quality rubric (100 pts)
- `scoring-rubrics/product-rotation-health.md` — Rotation freshness scoring
- `references/platform-specs.md` — Character limits, aspect ratios, posting rules
- `references/multi-brand-config.example.json` — Example multi-brand configuration
- `references/product-rotation-config.example.json` — Example product rotation config
- `references/banned-phrases.example.json` — Example banned phrase list
- `config/defaults.json` — Default engine configuration
