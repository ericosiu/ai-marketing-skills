# AI Team Ops

## Preamble (runs on skill start)

```bash
# Version check (silent if up to date)
python3 telemetry/version_check.py 2>/dev/null || true

# Telemetry opt-in (first run only, then remembers your choice)
python3 telemetry/telemetry_init.py 2>/dev/null || true
```

> **Privacy:** This skill logs usage locally to `~/.ai-marketing-skills/analytics/`. Remote telemetry is opt-in only. No code, file paths, or repo content is ever collected. See `telemetry/README.md`.

---

AI-powered team performance analysis and meeting intelligence: ruthless performance audits using the "Elon Algorithm" + automatic extraction of action items, decisions, and follow-ups from meeting transcripts.

## When to Use

Use this skill when:
- Evaluating team performance against OKRs/KPIs with a structured framework
- Stack ranking team members to identify A/B/C players
- Finding redundant roles, bottlenecks, and automation opportunities in your org
- Extracting action items and decisions from meeting transcripts
- Processing batch meeting notes into structured follow-up lists
- Pushing meeting action items to CRM (HubSpot) as tasks

## Tools

### Team Performance

| Script | Purpose | Key Command |
|--------|---------|-------------|
| `team_performance_audit.py` | Elon Algorithm: 5-step team audit + stack rank + scorecards | `python3 team_performance_audit.py --input team_data.json --output report.md` |

### Meeting Intelligence

| Script | Purpose | Key Command |
|--------|---------|-------------|
| `meeting_action_extractor.py` | Extract decisions, actions, follow-ups from transcripts | `python3 meeting_action_extractor.py --transcript meeting.txt --format markdown` |

## Configuration

All scripts use environment variables for LLM API access. Copy `.env.example` to `.env` and fill in your values.

### Required Environment Variables

- `ANTHROPIC_API_KEY` — Anthropic API key (Claude for analysis)
- `OPENAI_API_KEY` — OpenAI API key (alternative LLM provider)

### Optional Environment Variables

- `HUBSPOT_API_KEY` — HubSpot private app token (for pushing meeting action items as tasks)
- `LLM_PROVIDER` — `anthropic` (default) or `openai`
- `LLM_MODEL` — Model name override (default: `claude-sonnet-4-20250514` or `gpt-4o`)

## Data Flow

```
Role Descriptions + OKRs + Output Data (CSV/JSON)
        │
        ▼
┌──────────────────────────────────┐
│   team_performance_audit.py      │
│   5-Step Elon Algorithm:         │
│   1. Question requirements       │
│   2. Delete redundancies         │
│   3. Simplify workflows          │
│   4. Accelerate bottlenecks      │
│   5. Automate what's possible    │
│                                  │
│   + Score: velocity, quality,    │
│     independence, initiative     │
│   + Stack rank: A/B/C players    │
│   + Actions: promote/coach/exit  │
└──────────────────────────────────┘
        │
        ▼
Executive Summary + Individual Scorecards + Org Recommendations


Meeting Transcripts (text files or stdin)
        │
        ▼
┌──────────────────────────────────┐
│   meeting_action_extractor.py    │
│   Extract:                       │
│   • Decisions (who + context)    │
│   • Action items (owner +        │
│     deadline + priority)         │
│   • Open questions               │
│   • Key insights / quotes        │
│   • Follow-up meetings needed    │
│   • Implicit commitments         │
│   + Confidence scores            │
└──────────────────────────────────┘
        │
        ▼
Structured JSON / Markdown + Optional CRM Push
```

## Dependencies

- Python 3.9+
- `anthropic` or `openai` (for LLM-powered analysis)
- `requests` (for optional HubSpot integration)
