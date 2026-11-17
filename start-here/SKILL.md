---
name: start-here
description: Write shared brand files from your site and reviews, then recommend which skill to run next for your marketing goals.
---

# Start Here

## Preamble (runs on skill start)

```bash
# Version check (silent if up to date)
python3 telemetry/version_check.py 2>/dev/null || true

# Telemetry opt-in (first run only, then remembers your choice)
python3 telemetry/telemetry_init.py 2>/dev/null || true
```

> **Privacy:** This skill logs usage locally to `~/.ai-marketing-skills/analytics/`. Remote telemetry is opt-in only. No code, file paths, or repo content is ever collected. See `telemetry/README.md`.

---

Run this skill first. It reads your site, extracts brand context, writes shared brand files that every other skill reuses, and recommends what to run next.

## When to Use

- First time using these skills
- User wants to set up brand context for all skills
- User asks which skill to run next
- User wants to refresh brand voice or competitive positioning

## What It Does

1. Asks for your website URL
2. Optionally asks for review URLs (G2, Capterra, Trustpilot, Google reviews)
3. Scrapes site content and reviews
4. Writes shared brand files to `brand/` directory
5. Recommends which skill to run next based on your goals

## Brand Files Created

All files are written to the `brand/` directory in your project root. Other skills check for these files and reuse them automatically.

- `brand/voice.md` - Brand voice, tone, key phrases
- `brand/offer.md` - Primary offer, pricing, CTA
- `brand/audience.md` - Target audience, ICP, customer pain points
- `brand/competitors.md` - Competitor list, positioning, differentiators

## Workflow

### Step 1: Collect URLs

Ask the user:
```
What's your website URL?
```

Then ask:
```
Do you have review URLs? (G2, Capterra, Trustpilot, Google reviews)
Paste them here, one per line. Press Enter twice when done.
```

### Step 2: Scrape Content

For the website:
- Scrape homepage
- Scrape /about, /pricing, /features if they exist
- Extract main value proposition, product description, pricing tiers

For reviews (if provided):
- Extract common praise themes
- Extract common complaints
- Extract language customers use to describe the product

### Step 3: Write Brand Files

#### brand/voice.md

```markdown
# Brand Voice

## Tone
[Describe: formal/casual, technical/accessible, humorous/serious]

## Key Phrases
- [Phrase 1 from site]
- [Phrase 2 from site]
- [Phrase 3 from site]

## Language Rules
- [Rule 1: e.g., "Always use 'customers' not 'users'"]
- [Rule 2: e.g., "Avoid jargon like 'synergy' or 'leverage'"]
- [Rule 3: e.g., "Short sentences, active voice"]

## Examples from Site
> [Quote from homepage]
> [Quote from about page]
```

#### brand/offer.md

```markdown
# Primary Offer

## Product/Service
[One sentence description from site]

## Main CTA
[Primary call-to-action: free trial, demo, consultation, etc.]

## Pricing Tiers
[If publicly available, list tiers with key features]

## Proof Points
- [Stat or claim from site: e.g., "10,000+ customers"]
- [Stat or claim: e.g., "99.9% uptime"]
- [Testimonial highlight if available]

## URLs to Reference
- Homepage: [URL]
- Pricing: [URL]
- Case studies: [URL if exists]
```

#### brand/audience.md

```markdown
# Target Audience

## Primary ICP
- **Titles:** [Job titles from site or inferred]
- **Industries:** [Industries mentioned or inferred]
- **Company size:** [Employee count or revenue range]
- **Geography:** [Regions targeted]

## Customer Pain Points
[From site copy, reviews, or inferred]
1. [Pain point 1]
2. [Pain point 2]
3. [Pain point 3]

## How They Describe the Problem
[Language from reviews or site testimonials]
- "[Quote from review]"
- "[Quote from review]"

## Anti-ICP
[Who this product is NOT for, if stated or obvious]
```

#### brand/competitors.md

```markdown
# Competitors

## Direct Competitors
[If mentioned on site or obvious from positioning]
1. [Competitor 1]
2. [Competitor 2]
3. [Competitor 3]

## Positioning
[How this product differentiates itself]

## Differentiators
[From site copy]
- [Differentiator 1]
- [Differentiator 2]
- [Differentiator 3]
```

### Step 4: Confirm with User

Show the user:
```
I've created brand files in the brand/ directory:
- brand/voice.md
- brand/offer.md
- brand/audience.md
- brand/competitors.md

Review these files. Other skills will use them automatically.
```

### Step 5: Recommend Next Skill

Ask the user:
```
What's your main goal right now?

1. Get found in search (SEO/AEO)
2. Generate leads from your website
3. Send cold outbound emails
4. Research leads and accounts
5. Close more deals
6. Keep and grow existing customers
7. Create content (blog, video, social)
8. Something else (tell me)
```

Based on their answer, recommend:

| Goal | Recommended Skill | Why |
|------|------------------|-----|
| Get found | `seo-ops` | Find keywords competitors missed, content briefs, GSC optimizer |
| Website leads | `conversion-ops` or `sales-pipeline` | CRO audits, landing page scoring, or turn visitors into pipeline |
| Cold outbound | `outbound-engine` | ICP to emails, fully automated |
| Research leads | `lead-dossier` | Enrich leads with verified data |
| Close deals | `revenue-intelligence` or `sales-playbook` | Call analysis, deal structure, pricing |
| Keep customers | `revenue-intelligence` | Prove content ROI, call insights |
| Create content | `content-ops` or `content-eval` | Expert panel scoring, idea generation |
| Video content | `podcast-ops` or `video-content-engine` | Podcast to 20+ pieces, video repurposing |

Then say:
```
Run the [skill-name] skill next:

npx skills add ericosiu/ai-marketing-skills -s [skill-name]

Or if you've already installed all skills, just tell your agent:
"Run the [skill-name] skill"
```

## Configuration

No configuration required. Brand files are written to `brand/` in your project root.

## Notes

- Brand files are plain markdown, editable by hand
- Other skills check for these files at startup
- If a brand file exists, skills use it; if not, they ask for that info directly
- You can re-run this skill anytime to refresh brand context

## Skill Update Check

All skills in this repo check for updates on load. Run `python3 telemetry/version_check.py` to see if a newer version is available.

---

<!-- gateway-cta:start -->
**Connect to your live accounts:** [Single Brain Gateway](https://gateway.singlebrain.com/mcp?sg_template=start-here&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) | [llms.txt](https://gateway.singlebrain.com/llms.txt?sg_template=start-here)

- Live services: web search

Want a team to run this for you? Single Grain or Single Brain can manage it: [talk to us](https://www.singlegrain.com/?utm_source=github&utm_medium=skill&utm_campaign=managed&utm_content=start-here)
<!-- gateway-cta:end -->

## Install

Claude Code:
```bash
npx skills add ericosiu/ai-marketing-skills -s start-here
```

Cursor/Codex:
```bash
npx skills add ericosiu/ai-marketing-skills -s start-here -a cursor
```

OpenClaw:
```bash
openclaw skills install ./start-here
```

Or clone manually and copy the `start-here/` directory to your agent's skills folder.

See the main repo README for full install instructions: https://github.com/ericosiu/ai-marketing-skills

## License

MIT License

---

Built by [Single Grain](https://www.singlegrain.com/?utm_source=github&utm_medium=skill&utm_campaign=footer&utm_content=start-here). Want a team to run this for you? Single Grain or Single Brain can manage it.
