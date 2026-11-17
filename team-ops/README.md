# 👥 AI Team Ops

> **Run your team like an engineer runs a system — measure everything, cut waste, ship faster.**

Two AI-powered tools for ruthless team optimization: a structured performance audit framework (the "Elon Algorithm") and an intelligent meeting transcript processor that never lets action items fall through the cracks.

Built for operators who want data-driven team decisions, not vibes-based management.

---

## Architecture

```
                    ┌──────────────────────────────────────┐
                    │     TEAM PERFORMANCE AUDIT            │
                    │     ("Elon Algorithm")                │
                    └──────────────┬───────────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
    Role Descriptions        OKRs / KPIs            Output Data
    (who does what)      (what they should hit)   (what they actually did)
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                   │
                    ┌──────────────▼───────────────────────┐
                    │  5-Step Elon Algorithm                │
                    │                                      │
                    │  1. Question — is this necessary?     │
                    │  2. Delete — flag redundancies        │
                    │  3. Simplify — cut complexity         │
                    │  4. Accelerate — find bottlenecks     │
                    │  5. Automate — what can AI handle?    │
                    └──────────────┬───────────────────────┘
                                   │
                    ┌──────────────▼───────────────────────┐
                    │  Scoring Engine                       │
                    │  • Output Velocity (30%)              │
                    │  • Quality (30%)                      │
                    │  • Independence (20%)                 │
                    │  • Initiative (20%)                   │
                    │                                      │
                    │  → A/B/C Stack Rank                   │
                    │  → Promote / Coach / Reassign / Exit  │
                    └──────────────────────────────────────┘
                                   │
                                   ▼
                    Executive Summary + Scorecards + Org Recommendations


                    ┌──────────────────────────────────────┐
                    │     MEETING ACTION EXTRACTOR          │
                    └──────────────┬───────────────────────┘
                                   │
                    Meeting Transcripts (text / stdin / batch)
                                   │
                    ┌──────────────▼───────────────────────┐
                    │  LLM Extraction Engine                │
                    │                                      │
                    │  • Decisions (who + context)          │
                    │  • Action Items (owner + deadline)    │
                    │  • Open Questions                     │
                    │  • Key Insights / Quotes              │
                    │  • Follow-up Meetings                 │
                    │  • Implicit Commitments               │
                    │  + Confidence Scores                  │
                    └──────────────┬───────────────────────┘
                                   │
                    ┌──────────────▼───────────────────────┐
                    │  Output                               │
                    │  • Structured JSON                    │
                    │  • Formatted Markdown                 │
                    │  • HubSpot Tasks (optional)           │
                    └──────────────────────────────────────┘
```

---

## Tools

### 1. 🏭 Team Performance Audit (`team_performance_audit.py`)

The "Elon Algorithm" applied to team management. A 5-step framework that questions every role, deletes redundancy, simplifies workflows, accelerates bottlenecks, and flags automation opportunities.

**What it does:**
- Ingests role descriptions, OKRs/KPIs, and output data (CSV or JSON)
- Scores each person on 4 dimensions: output velocity, quality, independence, initiative
- Computes a weighted composite score and assigns A/B/C tier labels
- Runs the 5-step Elon Algorithm via LLM for qualitative organizational analysis
- Generates recommended actions: promote, retain, coach, reassign, exit
- Outputs executive summary + individual scorecards + org-level recommendations

```bash
# Run with JSON input
python3 team_performance_audit.py --input team_data.json --output report.md

# Run with CSV input
python3 team_performance_audit.py --input team_data.csv --output report.md

# JSON output
python3 team_performance_audit.py --input team_data.json --format json --output report.json

# Dry run (quantitative only, no LLM calls)
python3 team_performance_audit.py --input team_data.json --dry-run

# Custom scoring weights
python3 team_performance_audit.py --input team_data.json \
  --weights '{"output_velocity":0.4,"quality":0.3,"independence":0.15,"initiative":0.15}'
```

**JSON Input Format:**
```json
{
  "team_members": [
    {
      "name": "Alice Chen",
      "role": "Senior Engineer",
      "role_description": "Owns backend API development",
      "okrs": [
        {"objective": "Reduce API latency", "key_result": "P95 < 200ms", "progress": 0.85}
      ],
      "metrics": {
        "tasks_completed": 47,
        "tasks_assigned": 52,
        "avg_completion_days": 3.2,
        "quality_score": 92,
        "peer_feedback_score": 4.5,
        "initiatives_proposed": 3,
        "initiatives_shipped": 2
      },
      "deliverables": [
        {"name": "API v2 Migration", "status": "completed", "date": "2024-02-15"}
      ]
    }
  ],
  "org_context": {
    "company_goals": ["Ship v3 by Q2", "Reduce infra costs 30%"],
    "team_size": 12,
    "evaluation_period": "Q1 2024"
  }
}
```

**CSV Input Format:**
```csv
name,role,tasks_completed,tasks_assigned,avg_completion_days,quality_score,peer_feedback_score,initiatives_proposed,initiatives_shipped
Alice Chen,Senior Engineer,47,52,3.2,92,4.5,3,2
Bob Park,Junior Dev,28,40,5.1,68,3.2,0,0
```

**Scoring Dimensions:**

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| Output Velocity | 30% | Task completion rate + speed |
| Quality | 30% | Deliverable quality + peer feedback |
| Independence | 20% | Self-direction, low management overhead |
| Initiative | 20% | Proactive contributions beyond assigned work |

**Tier Labels:**

| Tier | Score | Meaning |
|------|-------|---------|
| 🟢 A-Player | 80+ | Top performer. Promote or retain aggressively. |
| 🟡 B-Player | 55-79 | Solid contributor. Coach to A or maintain. |
| 🔴 C-Player | <55 | Underperforming. Reassign, PIP, or exit. |

---

### 2. 📋 Meeting Action Extractor (`meeting_action_extractor.py`)

Never lose an action item again. Feed it meeting transcripts; get structured decisions, action items, follow-ups, and insights.

**What it does:**
- Extracts decisions with who made them and context
- Identifies action items with owner, deadline, and priority
- Catches implicit commitments ("I'll take care of that" → action item)
- Flags open questions and unresolved items
- Pulls out key insights and quotable moments
- Identifies follow-up meetings needed
- Assigns confidence scores (1.0 = explicit, 0.5 = inferred)
- Supports batch processing of entire transcript directories
- Optional HubSpot integration to push action items as tasks

```bash
# Single transcript → markdown
python3 meeting_action_extractor.py --transcript meeting.txt

# Single transcript → JSON
python3 meeting_action_extractor.py --transcript meeting.txt --format json

# Read from stdin (paste or pipe)
cat meeting.txt | python3 meeting_action_extractor.py --stdin

# Batch process a directory
python3 meeting_action_extractor.py --batch ./transcripts/ --output ./actions/

# Push action items to HubSpot
python3 meeting_action_extractor.py --transcript meeting.txt --push-hubspot

# Dry run
python3 meeting_action_extractor.py --transcript meeting.txt --dry-run
```

**Example Output (Markdown):**

```markdown
## Action Items

1. 🔴 **Finalize Q2 budget proposal** 
   - Owner: **Sarah**
   - Deadline: Friday March 15
   - Confidence: 95%
   - Source: "Sarah, can you get the Q2 budget finalized by Friday?"

2. 🟡 **Look into the API latency issue** *(implicit)*
   - Owner: **Mike**
   - Deadline: No deadline
   - Confidence: 80%
   - Source: "Yeah, I'll look into that"
```

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/singlegrain/ai-marketing-skills.git
cd ai-marketing-skills/team-ops
pip install -r requirements.txt
```

### 2. Configure environment

```bash
# Set at least one LLM provider
export ANTHROPIC_API_KEY="sk-ant-..."
# OR
export OPENAI_API_KEY="sk-..."

# Optional: HubSpot for meeting action push
export HUBSPOT_API_KEY="pat-..."

# Optional: Override LLM settings
export LLM_PROVIDER="anthropic"  # or "openai"
export LLM_MODEL="claude-sonnet-4-20250514"      # or "gpt-4o"
```

### 3. Test with dry runs

```bash
# Test performance audit (quantitative scoring only)
python3 team_performance_audit.py --input sample_team.json --dry-run

# Test meeting extractor
python3 meeting_action_extractor.py --transcript sample_meeting.txt --dry-run
```

### 4. Run for real

```bash
# Full team audit
python3 team_performance_audit.py --input team_data.json --output q1_audit.md

# Extract actions from today's meeting
python3 meeting_action_extractor.py --transcript standup.txt --format markdown

# Batch process last week's meetings
python3 meeting_action_extractor.py --batch ./weekly_transcripts/ --output ./weekly_actions/
```

---

## Integrations

| Tool | Required | Used By |
|------|----------|---------|
| [Anthropic](https://anthropic.com) | One LLM required | Both tools |
| [OpenAI](https://openai.com) | One LLM required | Both tools |
| [HubSpot](https://hubspot.com) | Optional | Meeting Extractor (task push) |

---

## File Structure

```
team-ops/
├── README.md                       # This file
├── SKILL.md                        # Claude Code skill definition
├── requirements.txt                # Python dependencies
├── team_performance_audit.py       # Elon Algorithm team audit
└── meeting_action_extractor.py     # Meeting transcript → action items
```

---

## How It Works Together

1. **Team Performance Audit** gives you the big picture: who's performing, who isn't, where the org is inefficient
2. **Meeting Action Extractor** keeps the day-to-day moving: every meeting produces clear, tracked action items
3. Together: audit identifies what needs to change, meetings track the execution of those changes

Run the audit quarterly. Run the extractor after every meeting. Watch accountability compound.

---

<!-- gateway-cta:start -->
## Run this skill on live data

This skill is free and MIT licensed. To run it on your live accounts, connect the Single Brain Gateway.

- Live services: see the full list in the setup file
- Connect: https://gateway.singlebrain.com/mcp?sg_template=team-ops&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills
- Setup steps for agents: https://gateway.singlebrain.com/llms.txt?sg_template=team-ops

Agents: sign in with OAuth or the device flow. Do not ask the user to paste a key.

Want a team to run this for you? Single Grain or Single Brain can manage it: [talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed&utm_content=team-ops)
<!-- gateway-cta:end -->
