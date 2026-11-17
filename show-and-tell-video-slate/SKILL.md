---
name: show-and-tell-video-slate
description: Turn real builds and first-party proof into ranked 15-minute video episodes before production. Evidence inventory, episode scoring.
---

# Show-and-Tell Video Slate

Turn real work into videos whose opening promise is repaid by a visible artifact, workflow, result, or before/after.

## Preamble

From the repository root, run the privacy-preserving version check and telemetry initializer when available:

```bash
python3 telemetry/version_check.py 2>/dev/null || true
python3 telemetry/telemetry_init.py 2>/dev/null || true
```

Remote telemetry is opt-in. Never log content, URLs, paths, credentials, names, business data, or proof artifacts.

## Set the scope

State the authorized sources, owner, channel, viewer, runtime, deliverable, and stop condition. Keep source systems read-only. Never search unrelated accounts, repositories, conversations, or credentials.

Ask the user to rank these outcomes when not already known:

1. money created;
2. money saved;
3. productive capacity created.

Load any supplied creator voice guide before writing titles or hooks. Reject packages that violate it even if their numeric scores pass.

## Inventory filmable evidence

Inspect only supplied or authorized builds, repositories, demos, agent runs, dashboards, analytics, and workflow outputs. For every candidate record:

- viewer and business outcome;
- visible artifact and demonstration path;
- claim status: achieved, estimate, anecdote, forecast, target, or plan;
- proof pointer, freshness, and privacy limits;
- mechanism, lesson, and viewer action;
- missing pickup, capture, redaction, or validation.

Do not upgrade remembered results into verified evidence. Label provisional candidates.

## Apply the show-and-tell gate

Read [references/selection-rubric.md](references/selection-rubric.md). Reject or repair a candidate unless:

- the first 30 seconds can show a real outcome, build, screen, output, or physical artifact;
- the demonstration explains or proves the package;
- one promise can sustain 15 minutes without padding;
- the viewer receives a usable mechanism or decision;
- the ending resolves the opening promise completely.

Framework-only topics must use real case studies. Product walkthroughs must lead with the viewer outcome rather than a feature list.

## Combine carefully

Combine ideas only when they share one mechanism, viewer, and payoff. Examples include sales and recruiting workflows that use the same outreach loop, multiple cost controls inside one audit system, or a demonstrated content result paired with the loop that produced it.

Do not combine unrelated proof points merely to reach the runtime. Route thin ideas to shorter formats.

## Build an exact 15-minute spine

Use 900 seconds unless the user overrides it:

1. `0:00-0:30` show the outcome and promise;
2. `0:30-2:00` establish the stakes and baseline;
3. `2:00-5:00` show what was built;
4. `5:00-10:00` demonstrate how it works;
5. `10:00-13:00` show receipts, limitations, and lessons;
6. `13:00-15:00` give the implementation path and close the promise.

## Score and package

Use the nine episode lenses in [references/selection-rubric.md](references/selection-rubric.md). Require a 90+ average, with Demoability and Payoff Integrity each at least 90.

Create exactly three materially different packages:

1. verdict or contrarian conclusion;
2. specific proof or transformation;
3. decision utility or implementation framework.

Require every package to score at least 9.0/10 with no dimension below 8.5. Use zero to four thumbnail words and no more than three major visual groups. Prefer the real artifact, result screen, dashboard, output, or physical prop over an abstract metaphor.

After the slate passes, use `content-eval` for deeper panel review, `video-content-engine` for the production plan, and `shortform-idea-grill` for complete short-form derivatives when those skills are installed. Use a compatible thumbnail-packaging skill when available. Keep achieved results distinct from plans and forecasts.

## Validate

Read [references/output-contract.md](references/output-contract.md), save the structured slate as JSON, and run:

```bash
python3 scripts/evaluate_slate.py slate.json --output slate-eval.json
python3 scripts/evaluate_slate.py slate.json --validate-only
```

The validator checks runtime, artifact evidence, claim proof, episode scores, packaging lanes, thumbnail word count, component budget, and package score floors.

## Deliver

Return the ranked slate, combination decisions, exact run of show, first-30-second promise, proof and pickup ledger, three packages per episode, evaluation readback, winning package, and shoot order.

Separate `ready` from `repair`. A strong package never overrides missing proof. Do not render, publish, schedule, upload, or change a live asset without explicit approval.

## Lifecycle

- **Tracked state:** keep run evidence, slate JSON, evaluation reports, and decisions in a user-selected private runtime folder, not in the skill.
- **Success test:** at least one episode passes the episode and show-and-tell gates, every surfaced package passes deterministic validation, and every achieved claim has a proof pointer.
- **Repeat trigger:** run when choosing a recording slate, after a meaningful build ships, or when new first-party results arrive. Do not schedule by default.
- **Learning writeback:** store user corrections, failed proof checks, and post-publication performance evidence in the private runtime folder.
- **Promotion:** validate after one real build produces a passing slate and a complete recording. Treat as production-ready after three useful slates and at least two measured content readbacks.
- **Retirement:** archive if three consecutive runs add no differentiated ready episode or another workflow absorbs the complete process.

<!-- gateway-cta:start -->
## Run this skill on live data

This skill is free and MIT licensed. To run it on your live accounts, connect the Single Brain Gateway.

- Live services: see the full list in the setup file
- Connect: https://gateway.singlebrain.com/mcp?sg_template=show-and-tell-video-slate&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills
- Setup steps for agents: https://gateway.singlebrain.com/llms.txt?sg_template=show-and-tell-video-slate

Agents: sign in with OAuth or the device flow. Do not ask the user to paste a key.

Want a team to run this for you? Single Grain or Single Brain can manage it: [talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed&utm_content=show-and-tell-video-slate)
<!-- gateway-cta:end -->
