# AI Conversion Ops

## Preamble (runs on skill start)

```bash
# Version check (silent if up to date)
python3 telemetry/version_check.py 2>/dev/null || true

# Telemetry opt-in (first run only, then remembers your choice)
python3 telemetry/telemetry_init.py 2>/dev/null || true
```

> **Privacy:** This skill logs usage locally to `~/.ai-marketing-skills/analytics/`. Remote telemetry is opt-in only. No code, file paths, or repo content is ever collected. See `telemetry/README.md`.

---

AI-powered conversion rate optimization: landing page audits, CRO scoring, survey segmentation, and lead magnet generation.

## When to Use

- User asks for a landing page audit or CRO analysis
- User wants to score a page across conversion dimensions
- User needs to identify conversion bottlenecks on a URL
- User has survey data and wants to segment respondents by pain point
- User wants lead magnet ideas generated from survey responses
- User needs batch CRO analysis across multiple URLs

## Tools

### CRO Audit (`cro_audit.py`)

Fetches a landing page and scores it across 8 conversion dimensions. No headless browser needed.

```bash
# Single URL audit
python cro_audit.py --url https://example.com/landing-page

# Batch mode — multiple URLs
python cro_audit.py --urls https://example.com/page1 https://example.com/page2

# URLs from a file (one per line)
python cro_audit.py --file urls.txt

# Specify industry for benchmark comparison
python cro_audit.py --url https://example.com --industry saas

# JSON output
python cro_audit.py --url https://example.com --json

# Save report to file
python cro_audit.py --url https://example.com --output report.json
```

**Scoring dimensions (each 0–100):**
1. **Headline Clarity** — Is the value prop obvious in <5 seconds?
2. **CTA Visibility** — Are CTAs prominent, contrasting, above the fold?
3. **Social Proof** — Testimonials, logos, case studies, numbers?
4. **Urgency** — Scarcity, deadlines, limited offers?
5. **Trust Signals** — Security badges, guarantees, privacy, certifications?
6. **Form Friction** — How many fields? Is the form intimidating?
7. **Mobile Responsiveness** — Viewport meta, responsive patterns, touch targets?
8. **Page Speed Indicators** — Image optimization, script count, resource size?

**Overall CRO Score** = Weighted average across all 8 dimensions.

**Output includes:**
- Per-dimension score with specific findings
- Priority fixes ranked by impact
- Before/after suggestions for each issue
- Industry benchmark comparison
- Overall letter grade (A+ through F)

**Supported industries:** `saas`, `ecommerce`, `agency`, `finance`, `healthcare`, `education`, `b2b`, `general`

### Survey-to-Lead-Magnet Engine (`survey_lead_magnet.py`)

Ingests survey CSV data, clusters respondents by pain point, and generates lead magnet briefs for each segment.

```bash
# Basic usage — analyze survey CSV
python survey_lead_magnet.py --csv survey_responses.csv

# Specify which columns contain pain points / challenges
python survey_lead_magnet.py --csv survey.csv --pain-columns "biggest_challenge" "top_frustration"

# Limit number of segments
python survey_lead_magnet.py --csv survey.csv --top-segments 5

# JSON output
python survey_lead_magnet.py --csv survey.csv --json

# Save output
python survey_lead_magnet.py --csv survey.csv --output lead_magnets.json
```

**What it produces:**
- Pain point clusters with respondent counts
- Segments ranked by size and commercial potential
- For each top segment, a lead magnet brief:
  - Title, format (guide/checklist/template/calculator), hook
  - Content outline (5–7 sections)
  - Target CTA and distribution channel
  - Viral potential score + conversion potential score
- Prioritized implementation roadmap

**CSV format:** Questions as column headers, one respondent per row. Works with any survey tool export (Typeform, Google Forms, SurveyMonkey, etc.)

## Configuration

No API keys required. Both tools work with local analysis only.

Optional environment variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `USER_AGENT` | No | Custom user agent for page fetching (default provided) |
| `REQUEST_TIMEOUT` | No | HTTP timeout in seconds (default: 15) |

## Recommended Workflow

1. **Weekly:** Run `cro_audit.py` on your top landing pages to track CRO scores over time
2. **Post-survey:** Run `survey_lead_magnet.py` to turn survey data into content strategy
3. **Pre-launch:** Audit new landing pages before driving paid traffic
4. **Monthly:** Batch audit competitor landing pages to benchmark against

## Dependencies

```bash
pip install -r requirements.txt
```
