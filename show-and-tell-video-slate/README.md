# Show-and-Tell Video Slate

Turn real builds, workflows, dashboards, and results into proof-led 15-minute YouTube episodes before spending time on recording and editing.

## What it does

- Inventories authorized first-party work and visible evidence.
- Prioritizes money created, money saved, and productive capacity.
- Combines thin ideas only when they share one mechanism and payoff.
- Requires a real artifact or result inside the first 30 seconds.
- Builds an exact 15-minute run of show.
- Creates verdict, proof, and utility packaging hypotheses.
- Rejects packages below the configured quality floors.
- Keeps achieved results separate from estimates, tests, and plans.

## Quick start

```text
Use $show-and-tell-video-slate on these authorized builds and analytics.
Select the strongest three 15-minute episodes, show me what evidence to capture,
and create three title-thumbnail packages for each.
```

The skill defaults to planning and evaluation. It does not render, upload, publish, schedule, or change a live video.

## Validate a slate

Create a JSON slate using the fields described in `SKILL.md`, then run:

```bash
python3 show-and-tell-video-slate/scripts/evaluate_slate.py slate.json \
  --output slate-eval.json

python3 show-and-tell-video-slate/scripts/evaluate_slate.py slate.json \
  --validate-only
```

The validator uses only the Python standard library.

## Quality gates

- Episode panel average: at least 90/100.
- Demoability and Payoff Integrity: at least 90 each.
- Runtime: exactly 900 seconds unless intentionally overridden upstream.
- Packages: exactly one verdict, one proof, and one utility lane.
- Package score: at least 9.0/10, with every dimension at least 8.5.
- Thumbnail copy: zero to four words.
- Visual component budget: no more than three major groups.
- Achieved claims: require a proof pointer.

Scores prioritize production. They are not predictions of views, clicks, or revenue.

## Privacy

Use only authorized source material. Keep raw conversations, customer data, private screenshots, exports, credentials, and proof artifacts outside this repository. Redact sensitive information before showing a screen or publishing a case study.


<!-- gateway-cta:start -->
## Run this skill on live data

This skill is free and MIT licensed. To run it on your live accounts, connect the Single Brain Gateway.

- Live services: see the full list in the setup file
- Connect: https://gateway.singlebrain.com/mcp?sg_template=show-and-tell-video-slate&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills
- Setup steps for agents: https://gateway.singlebrain.com/llms.txt?sg_template=show-and-tell-video-slate

Agents: sign in with OAuth or the device flow. Do not ask the user to paste a key.
<!-- gateway-cta:end -->
<!-- managed-cta:start -->
**Want a team to run this for you?** Single Grain and Single Brain can set up and manage this workflow for you. [Talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed-service&utm_content=show-and-tell-video-slate)
<!-- managed-cta:end -->
