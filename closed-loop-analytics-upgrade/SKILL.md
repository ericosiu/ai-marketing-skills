---
name: closed-loop-analytics-upgrade
description: Upgrade marketing, content, SEO/AEO/GEO, and revenue skills so changes are judged by platform analytics instead of vibes. Use when applying closed-loop learning to X, YouTube, SEO, AEO/GEO, outbound, paid creative, or revenue workflows.
---

# Closed-Loop Analytics Upgrade

## Principle

A workflow is not a closed loop until it checks whether the change worked and updates the playbook from that evidence.

For marketing skills, that means pulling analytics after the change window. Manual opinions are useful. Platform truth wins.

## Core pattern

1. **Input**: usage logs, recommendations, shipped changes, platform analytics, owner feedback, and cost/runtime data.
2. **AI action**: compare baseline vs candidate, find repeatable signals, and propose a skill/playbook patch.
3. **Output**: candidate patch to a prompt, skill, connector, brief template, scoring rubric, or next-action rule.
4. **Judgment**: success rate, speed, cost, quality, human correction rate, and actual performance delta.
5. **Self-improvement**: promote only if it beats baseline. Otherwise keep testing, rollback, or mark unproven.

## Analytics by surface

### X/Twitter
Track:
- impressions
- engagement rate
- replies
- reposts
- bookmarks
- profile clicks
- follower delta
- post length
- hook style
- proof number
- CTA type
- topic bucket

Use for:
- title/hook formulas
- longform structure
- CTA patterns
- post timing
- topic scoring

### YouTube
Track:
- impressions
- CTR
- average view duration
- retention curve
- watch time
- subscribers gained
- comments
- traffic source
- title/thumbnail/hook metadata
- video length and topic bucket

Use for:
- title formulas
- thumbnail rules
- first-15-second hook
- retention beats
- chapter structure
- Shorts cutdowns
- repurposing guidance

### SEO/AEO/GEO
Track:
- GSC clicks, impressions, CTR, average position, query/page mix
- GA4 sessions, engaged sessions, conversions, assisted leads
- Ahrefs rankings, backlinks, traffic estimates, keyword movement
- ClickFlow opportunities
- AI-search / answer-engine visibility where available
- CMS/page change log

Use for:
- content refresh patterns
- AEO/GEO opportunity scoring
- query/page prioritization
- internal linking and schema recommendations
- rollback decisions

### Revenue / outbound
Track:
- HubSpot owner, lead, deal, and pipeline movement
- Gong call language, objections, buying signals, and outcomes
- Instantly/Smartlead positive replies, booked meetings, unsubscribes, spam risk
- Metricool/LinkedIn post performance
- GA4/HubSpot attribution

Use for:
- outbound sequence patches
- offer angle scoring
- sales follow-up language
- content-to-pipeline investment decisions

## Pulling the data

You can use any connectors or APIs you have. To pull GA4, Search Console, HubSpot, Gong, LinkedIn, YouTube, X, Metricool and ad platform data from one place, you can also connect the [Coupler.io MCP server](https://github.com/coupler-io/coupler-io-mcp-server) (requires a Coupler.io account):

```bash
claude mcp add coupler-io --transport http https://mcp.coupler.io/mcp
```

## Required readback fields

Every promoted change needs:

- change made
- owner
- baseline window
- candidate window
- source systems pulled
- primary metric
- secondary metrics
- metric winner
- caveats/confounders
- decision: promote / keep testing / rollback / unproven
- next patch
- next readback date

## Promotion rules

Promote when:
- the candidate beats baseline on the primary metric, or
- the candidate exposes a repeatable audience/customer signal, and
- downside metrics are not meaningfully worse.

Do not promote when:
- volume is too low
- attribution is too dirty
- the result is explained by seasonality or unrelated campaigns
- the connector failed
- only the author liked it

That last one is harsh but spiritually important.

## Safety boundaries

Read-only analytics pulls are fine. External writes still require approval:

- posting to X/LinkedIn/YouTube
- publishing or editing CMS content
- changing ad accounts, bids, budgets, targeting, or creative
- mutating CRM/outbound tools
- sending emails or DMs
- changing credentials or production systems

## Output template

```markdown
# Readback: <skill/change>

## Verdict
Promote / keep testing / rollback / unproven

## Change tested
<what changed>

## Data pulled
| Source | Window | Status |
|---|---|---|

## Baseline vs candidate
| Metric | Baseline | Candidate | Delta | Interpretation |
|---|---:|---:|---:|---|

## Caveats
<confounders and missing data>

## Patch
<what changes in the skill/playbook>

## Next readback
<date + metric>
```
