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
| [**Outbound Engine**](./outbound-engine/) | ICP definition to emails in inbox — fully automated | Cold Outbound Optimizer, Lead Pipeline, Competitive Monitor |
| [**SEO Ops**](./seo-ops/) | Find the keywords your competitors missed | Content Attack Briefs, GSC Optimizer, Trend Scout |
| [**Finance Ops**](./finance-ops/) | Your AI CFO that finds hidden costs in 30 minutes | CFO Briefing, Cost Estimate, Scenario Modeler |

---

## 🚀 Quick Start

Each skill category has its own README with setup instructions. The general pattern:

```bash
# 1. Clone the repo
git clone https://github.com/singlegrain/ai-marketing-skills.git
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
└── finance-ops/           ← Financial analysis
    ├── SKILL.md
    ├── scripts/
    ├── references/        ← Metrics, rates, ROI models
    └── ...
```

---

## 🤝 Contributing

Found a bug? Have an improvement? PRs welcome.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/better-scoring`)
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

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

</div>
