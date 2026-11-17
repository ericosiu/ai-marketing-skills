# AI Conversion Ops

**Turn landing pages into conversion machines. Turn survey data into lead magnets.**

An AI-powered conversion optimization suite that replaces manual CRO audits and survey analysis. These tools score your landing pages across 8 proven conversion dimensions and transform raw survey responses into segmented lead magnet strategies — all without API keys or headless browsers.

## What's Inside

### 🎯 CRO Audit Tool
Fetches any landing page URL and runs it through a comprehensive conversion heuristics engine. Scores across 8 dimensions, compares against industry benchmarks, and generates specific fix recommendations with before/after suggestions.

**What it finds:**
- Weak or missing headlines that fail the 5-second test
- CTAs that blend in instead of standing out
- Missing social proof that kills trust
- Forms with too much friction
- Mobile responsiveness gaps
- Page weight and speed red flags
- Missing trust signals and urgency elements

### 📊 Survey-to-Lead-Magnet Engine
Ingests survey response CSVs, clusters respondents by pain point themes, ranks segments by size and commercial potential, and auto-generates complete lead magnet briefs for each segment.

**What it produces:**
- Pain point clusters from free-text survey responses
- Segments ranked by commercial opportunity
- Complete lead magnet briefs (title, format, hook, outline, CTA)
- Viral potential and conversion potential scores
- Prioritized implementation roadmap

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run a CRO audit

```bash
# Single page
python cro_audit.py --url https://yoursite.com/landing-page

# With industry benchmarks
python cro_audit.py --url https://yoursite.com/landing-page --industry saas

# Batch mode
python cro_audit.py --file urls.txt --industry ecommerce --output results.json
```

### 3. Generate lead magnets from survey data

```bash
# Basic analysis
python survey_lead_magnet.py --csv survey_responses.csv

# Specify pain point columns
python survey_lead_magnet.py --csv survey.csv --pain-columns "biggest_challenge" "what_keeps_you_up"

# Top 3 segments with JSON output
python survey_lead_magnet.py --csv survey.csv --top-segments 3 --json
```

## CRO Scoring Model

Every page is scored across **8 dimensions** (each 0–100):

| Dimension | What It Measures | Weight |
|-----------|-----------------|--------|
| Headline Clarity | Value prop visible in <5 seconds | 15% |
| CTA Visibility | Prominent, contrasting, above fold | 20% |
| Social Proof | Testimonials, logos, numbers, case studies | 15% |
| Urgency | Scarcity, deadlines, limited availability | 5% |
| Trust Signals | Security badges, guarantees, certifications | 10% |
| Form Friction | Field count, form complexity, required fields | 15% |
| Mobile Responsiveness | Viewport meta, responsive patterns | 10% |
| Page Speed Indicators | Image optimization, script count, resource size | 10% |

**Overall CRO Score** = Weighted average → letter grade (A+ through F).

### Industry Benchmarks

Benchmarks are calibrated per industry:

| Industry | Avg CRO Score | Top Quartile |
|----------|--------------|--------------|
| SaaS | 62 | 78+ |
| E-commerce | 58 | 74+ |
| Agency | 55 | 72+ |
| Finance | 60 | 76+ |
| Healthcare | 52 | 68+ |
| Education | 54 | 70+ |
| B2B | 56 | 73+ |

## Survey Segmentation

The lead magnet engine uses keyword frequency analysis and TF-IDF clustering to group survey responses:

1. **Text preprocessing** — Normalize, tokenize, remove stopwords
2. **Theme extraction** — TF-IDF vectorization of pain point responses
3. **Clustering** — Group similar responses into pain segments
4. **Ranking** — Score segments by size × commercial signal strength
5. **Brief generation** — Create lead magnet briefs targeting each cluster

### Lead Magnet Formats

The engine recommends the best format per segment:

- **Guide** — Deep educational content for complex problems
- **Checklist** — Actionable steps for process-oriented pain points
- **Template** — Fill-in-the-blank tools for recurring tasks
- **Calculator** — Interactive tools for quantifiable decisions
- **Swipe File** — Example collections for creative/copy challenges

## Architecture

```
┌──────────────────────────────────────────────────┐
│                  CRO Audit                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │  HTML    │ │  8-Dim   │ │    Industry      │  │
│  │ Fetcher  │ │  Scorer  │ │   Benchmarks     │  │
│  └────┬─────┘ └────┬─────┘ └────────┬─────────┘  │
│       └─────────────┼────────────────┘            │
│                     ▼                             │
│  ┌──────────────────────────────────────────────┐ │
│  │      Weighted Score + Priority Fixes         │ │
│  │  Before/After · Letter Grade · Benchmarks    │ │
│  └──────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│          Survey-to-Lead-Magnet Engine            │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │   CSV    │ │  TF-IDF  │ │   Pain Point     │  │
│  │  Ingest  │ │ Cluster  │ │    Ranking       │  │
│  └────┬─────┘ └────┬─────┘ └────────┬─────────┘  │
│       └─────────────┼────────────────┘            │
│                     ▼                             │
│  ┌──────────────────────────────────────────────┐ │
│  │    Lead Magnet Briefs + Scoring Matrix       │ │
│  │  Title · Format · Hook · Outline · CTA       │ │
│  └──────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

## Configuration

No API keys required. Both tools run entirely locally.

| Variable | Required | Description |
|----------|----------|-------------|
| `USER_AGENT` | No | Custom user agent for fetching pages |
| `REQUEST_TIMEOUT` | No | HTTP request timeout in seconds (default: 15) |

## Using as a Claude Code Skill

Add this to your `.claude/agents/` directory and use the `SKILL.md` for Claude Code integration. The skill enables Claude to:

1. Audit landing pages for conversion issues on demand
2. Score pages against industry benchmarks
3. Generate lead magnet strategies from survey data
4. Run batch CRO audits across multiple URLs

## File Structure

```
conversion-ops/
├── README.md                  # This file
├── SKILL.md                   # Claude Code agent skill definition
├── cro_audit.py               # Landing page CRO scoring engine
├── survey_lead_magnet.py      # Survey segmentation + lead magnet generator
└── requirements.txt           # Python dependencies
```

## License

MIT

---

<!-- gateway-cta:start -->
## Run this skill on live data

This skill is free and MIT licensed. To run it on your live accounts, connect the Single Brain Gateway.

- Live services: Google Analytics and Search Console, Mixpanel
- Connect: https://gateway.singlebrain.com/mcp?sg_template=conversion-ops&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills
- Setup steps for agents: https://gateway.singlebrain.com/llms.txt?sg_template=conversion-ops

Agents: sign in with OAuth or the device flow. Do not ask the user to paste a key.
<!-- gateway-cta:end -->
<!-- managed-cta:start -->
**Want a team to run this for you?** Single Grain and Single Brain can set up and manage this workflow for you. [Talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed-service&utm_content=conversion-ops)
<!-- managed-cta:end -->
