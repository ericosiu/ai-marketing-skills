# AI Marketing Skills

**Open-source Claude Code skills for marketing and sales teams.** Built by the team at [Single Brain](https://singlebrain.com/?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) — battle-tested on real pipelines generating millions in revenue.

These aren't prompts. They're complete workflows — scripts, scoring algorithms, expert panels, and automation pipelines you can plug into Claude Code (or any AI coding agent) and run today.

---

## 🗂️ Skills

| Category | What It Does | Key Skills |
|----------|-------------|------------|
| [**Growth Engine**](./growth-engine/) | Autonomous marketing experiments that run, measure, and optimize themselves | Experiment Engine, Pacing Alerts, Weekly Scorecard |
| [**Sales Pipeline**](./sales-pipeline/) | Turn anonymous website visitors into qualified pipeline | RB2B Router, Deal Resurrector, Trigger Prospector, ICP Learner |
| [**Content Ops**](./content-ops/) | Ship content that scores 90+ every time | Expert Panel, Quality Gate, Editorial Brain, Quote Miner |
| [**Personal Strategic Signal Intelligence**](./personal-strategic-signal-intelligence/) | Turn private reading, bookmarks, notes, and applied work into source-grounded decision intelligence | Attention Drift, Decision Court, Bookmark-to-Build, Content Negative-Space |
| [**Outbound Engine**](./outbound-engine/) | ICP definition to emails in inbox — fully automated | Cold Outbound Optimizer, Lead Pipeline, Competitive Monitor |
| [**SEO Ops**](./seo-ops/) | Find the keywords your competitors missed | Content Attack Briefs, GSC Optimizer, Trend Scout |
| [**Finance Ops**](./finance-ops/) | Your AI CFO that finds hidden costs in 30 minutes | CFO Briefing, Cost Estimate, Scenario Modeler |
| [**Revenue Intelligence**](./revenue-intelligence/) | Prove content ROI and turn sales calls into strategy | Gong Insight Pipeline, Revenue Attribution, Client Report Generator |
| [**Conversion Ops**](./conversion-ops/) | Score any landing page and turn survey data into lead magnets | CRO Audit, Survey-to-Lead-Magnet Engine |
| [**Podcast Ops**](./podcast-ops/) | One episode → 20+ content pieces across every platform | Podcast-to-Everything Pipeline, Content Calendar |
| [**Team Ops**](./team-ops/) | Ruthless performance audits and meeting intelligence | Elon Algorithm, Meeting-to-Action Extractor |
| [**Sales Playbook**](./sales-playbook/) | Value-based pricing framework that turns $10K deals into $100K deals | Pre-Call Briefing, Tiered Packager, Call Analyzer, Pattern Library |
| [**Autoresearch**](./autoresearch/) | Karpathy-inspired optimization loops for conversion content — 50+ variants, expert scoring, evolved winners | Variant Generator, Expert Panel Scorer, Evolution Engine |
| [**Deck Generator**](./deck-generator/) | AI-generated slide decks with consistent visual styles in minutes | Image Generator, Google Slides Builder, Style Presets |
| [**YT Competitive Analysis**](./yt-competitive-analysis/) | Find outlier videos and packaging patterns across any YouTube channels | Outlier Detector, Title Pattern Extractor, Channel Benchmarker |
| [**Video Content Engine**](./video-content-engine/) | Diagnose any video and route it into the strongest justified content portfolio | Long-form Optimizer, Shorts Engine, Tutorial, Case Study, Paid Creative |
| [**Show-and-Tell Video Slate**](./show-and-tell-video-slate/) | Turn real builds and first-party proof into ranked 15-minute video episodes before production | Evidence Inventory, Episode Scoring, Packaging Gates, Shoot Order |
| [**Shortform Idea Grill**](./shortform-idea-grill/) | Interview, score, and rank proof-led short-form video ideas | Five-Second Hooks, Three-Second Scores, Talking Bullets, CTA Mapping |
| [**Net-New Video Editor**](./net-new-video-editor/) | Turn fresh talking-head recordings into reversible, review-ready vertical drafts | JSON Edit Plans, FFmpeg Rendering, Captions, Hook Cards, Visual QA |
| [**X Long-Form + Humanizer**](./x-longform-post/) | Write X articles that sound human — with a 24-pattern AI slop detector | Post Writer, Humanizer Checklist, ASCII Diagram Builder |

---

## 🚀 Quick Start

Each skill category has its own README with setup instructions. The general pattern:

```bash
# 1. Clone the repo
git clone https://github.com/ericosiu/ai-marketing-skills.git
cd ai-marketing-skills

# 2. Pick a category
cd growth-engine  # or sales-pipeline, content-ops, etc.

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# 5. Run
python experiment-engine.py create \
  --hypothesis "Thread posts get 2x engagement vs single posts" \
  --variable format \
  --variants '["thread", "single"]' \
  --metric impressions
```

---

## 🧠 How These Work with Claude Code

Every category includes a `SKILL.md` file. Drop it into your Claude Code project and the AI agent knows how to use the tools:

```
# In your project directory
cp ai-marketing-skills/growth-engine/SKILL.md .claude/skills/growth-engine.md
```

Then ask Claude Code: *"Run an experiment testing carousel vs. static posts on LinkedIn"* — it handles the rest.

---

## 📊 What Makes These Different

**These aren't toy demos.** Each skill was built to run real business operations:

- **Growth Engine** uses bootstrap confidence intervals and Mann-Whitney U tests — real statistics, not vibes
- **Deal Resurrector** has three intelligence layers including "follow the champion" — tracking departed contacts to their new companies
- **ICP Learner** rewrites your ideal customer profile based on actual win/loss data — your targeting improves automatically
- **Expert Panel** recursively scores content with domain-specific expert personas until quality hits 90+
- **RB2B Router** does intent scoring, seniority-based company dedup, and agency classification before routing to outbound sequences

---

## 📁 Repository Structure

```
ai-marketing-skills/
├── README.md              ← You are here
├── growth-engine/         ← Autonomous experiments
│   ├── SKILL.md
│   ├── experiment-engine.py
│   ├── pacing-alert.py
│   ├── autogrowth-weekly-scorecard.py
│   └── ...
├── sales-pipeline/        ← Visitor → pipeline automation
│   ├── SKILL.md
│   ├── rb2b_instantly_router.py
│   ├── deal_resurrector.py
│   ├── trigger_prospector.py
│   ├── icp_learning_analyzer.py
│   └── ...
├── content-ops/           ← Quality scoring & production
│   ├── SKILL.md
│   ├── scripts/
│   ├── experts/           ← 9 expert panel definitions
│   ├── scoring-rubrics/   ← 5 scoring rubric templates
│   └── ...
├── personal-strategic-signal-intelligence/  ← Private signals → decision intelligence
│   ├── SKILL.md
│   └── README.md
├── outbound-engine/       ← Cold outbound automation
│   ├── SKILL.md
│   ├── scripts/
│   ├── references/        ← ICP template, copy rules
│   └── ...
├── seo-ops/               ← SEO intelligence
│   ├── SKILL.md
│   ├── content_attack_brief.py
│   ├── gsc_client.py
│   ├── trend_scout.py
│   └── ...
├── finance-ops/           ← Financial analysis
│   ├── SKILL.md
│   ├── scripts/
│   ├── references/        ← Metrics, rates, ROI models
│   └── ...
├── revenue-intelligence/  ← Sales call insights + attribution
│   ├── SKILL.md
│   ├── gong_insight_pipeline.py
│   ├── revenue_attribution.py
│   └── client_report_generator.py
├── conversion-ops/        ← CRO + lead magnet generation
│   ├── SKILL.md
│   ├── cro_audit.py
│   └── survey_lead_magnet.py
├── podcast-ops/           ← Podcast → content factory
│   ├── SKILL.md
│   └── podcast_pipeline.py
├── team-ops/              ← Performance audits + meeting intel
│   ├── SKILL.md
│   ├── team_performance_audit.py
│   └── meeting_action_extractor.py
└── sales-playbook/        ← Value-based pricing framework
    ├── SKILL.md
    ├── value_pricing_briefing.py
    ├── value_pricing_packager.py
    ├── call_analyzer.py
    └── pricing_pattern_library.py
```

---

## 🔒 Privacy & Security

Every skill is built with data privacy in mind:

- **PII Sanitizer** scans code and data for sensitive information before commits (`security/sanitizer.py`)
- **Pre-commit hook** blocks commits containing detected PII patterns
- **Configurable blocklists** for company names, person names, and custom patterns
- See [`security/README.md`](./security/README.md) for setup

```bash
# Scan for sensitive data
python3 security/sanitizer.py --scan --dir . --recursive

# Install the pre-commit hook
cp security/pre-commit-hook.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
```

---

## 📡 Telemetry (Opt-In)

Anonymous usage telemetry helps us understand which skills people actually use. Fully opt-in, privacy-first:

- **Local logging always** — see your own usage stats in `~/.ai-marketing-skills/analytics/`
- **Remote reporting optional** — only if you explicitly opt in on first run
- **Data collected:** skill name, duration, success/fail, version, OS. Nothing else. No code, no file paths, no repo content.
- **Version checks** — get notified when new skills are available

```bash
# View your local usage stats
python3 telemetry/telemetry_report.py

# Check for updates
python3 telemetry/version_check.py
```

See [`telemetry/README.md`](./telemetry/README.md) for details.

---

## 🤝 Contributing

Found a bug? Have an improvement? PRs welcome. Read [`CONTRIBUTING.md`](./CONTRIBUTING.md) for guidelines.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/better-scoring`)
3. Run `python3 security/sanitizer.py --scan` before committing
4. Commit your changes
5. Push to the branch
6. Open a Pull Request

---

## 📄 License

MIT License. Use these however you want.

---

*Star this repo if you find it useful. It helps others discover these tools.*

---

<div align="center">

**🧠 [Want these built and managed for you? →](https://singlebrain.com/?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills)**

*This is how we build agents at [Single Brain](https://singlebrain.com/?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) for our clients.*

[Single Grain](https://www.singlegrain.com/?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) · our marketing agency

📬 **[Level up your marketing with 14,000+ marketers and founders →](https://levelingup.beehiiv.com/subscribe)** *(free)*

</div>
