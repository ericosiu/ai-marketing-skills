# Product Rotation Health Rubric

**Evaluates whether the product rotation is balanced, fresh, and strategically sound.**

Use this rubric to audit rotation state and detect issues like over-featuring, stale products, or tier imbalance.

---

## Metrics

### 1. Tier Balance (25 points)

Are products being featured at their intended frequency?

| Score | Criteria |
|-------|----------|
| 25 | Tier 1 at 2x frequency, Tier 2 at 1x, Tier 3 at 1x — within 10% of target. |
| 20 | Within 20% of target frequencies. |
| 15 | One tier significantly over or under-represented. |
| 10 | Two tiers off balance. |
| 5 | Rotation is stuck on a single product or tier. |

### 2. Recency Spread (25 points)

Is there enough variety between features?

| Score | Criteria |
|-------|----------|
| 25 | No product featured twice within cooldown window. All products featured at least once in last 2 cycles. |
| 20 | One product slightly under cooldown threshold. |
| 15 | One product featured twice within cooldown window. |
| 10 | Multiple cooldown violations. |
| 5 | Same product featured 3+ times in cooldown window. |

### 3. Education Angle Diversity (25 points)

Are education angles being rotated, not repeated?

| Score | Criteria |
|-------|----------|
| 25 | No angle repeated within 7 days. Each product's angles used evenly. |
| 20 | Minor angle repetition (same angle within 5-7 days). |
| 15 | Same angle used twice within 3 days. |
| 10 | Limited angle variety — cycling through only 2-3 angles per product. |
| 5 | Same angle every day. |

### 4. Cross-Sell CTA Cadence (25 points)

Are cross-sell CTAs distributed evenly?

| Score | Criteria |
|-------|----------|
| 25 | CTAs appear at configured frequency (default every 3rd post) +/- 1. |
| 20 | CTAs slightly irregular but within acceptable range. |
| 15 | CTAs clustered (3 in a row) or absent for 5+ posts. |
| 10 | CTA cadence broken — either too frequent or too rare. |
| 5 | No CTAs in last 10 posts, or CTA on every post. |

---

## Usage

```bash
python3 product_rotation.py status --config rotation.json
python3 product_rotation.py history --config rotation.json --days 14
```

Review the history output against this rubric to identify rotation health issues before they affect content quality.
