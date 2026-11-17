---
name: shortform-idea-grill
description: Interview, score, and rank proof-led short-form video ideas. Five-second hooks, three-second scores, talking bullets.
---

# Shortform Idea Grill

Turn current work into success-led videos that earn attention quickly and fully repay the opening promise.

## Load the right context

Inspect supplied chats, briefs, transcripts, analytics, creator research, offers, and prior content before asking questions. Prefer work from the current week and ideas not already published.

Read:

- `references/intake-schema.md` before interviewing.
- `references/output-contract.md` before drafting.
- `references/scoring-rubric.md` before scoring.
- `references/ideas-schema.md` when saving machine-readable output.

Do not ask for information already present. Distinguish live evidence from remembered context.

## Interview one question at a time

Resolve these items in order:

1. desired outcome;
2. target viewer and relevant moment;
3. owned proof and measurable results;
4. current builds, experiments, opinions, and predictions;
5. claim boundaries;
6. CTA and destination;
7. available screens, artifacts, and recording constraints.

Ask only the single question most likely to improve the queue. Let the user answer freely, then press for numbers, mechanisms, examples, or proof. Stop when further interviewing would not materially change the ranking.

If essential context is missing, return `needs_intake` with the next question and a recommended answer. A provisional slate may continue only when labeled.

## Generate net-new candidates

Mine active work rather than recycling old videos. Cover at least five evidence-supported lanes:

- money created;
- money saved;
- productive capacity created;
- proof-led workflow demonstration;
- contrarian operating belief;
- timely prediction;
- founder lesson or corrected failure;
- teardown, comparison, or myth correction.

Reject any idea without a specific viewer, credible proof path, useful payoff, or filmable treatment.

Prefer success language. A failure may establish tension, but the video must resolve into a useful mechanism, result, or decision.

## Write hooks that can be repaid

Write one strongest five-second overlay per idea. It must:

- communicate the premise in the first three seconds;
- use a number, result, contrast, or consequential verdict when justified;
- remain visible for roughly five seconds;
- avoid unsupported certainty;
- lead directly to the promised demonstration or explanation.

For number hooks, specify the evidence behind the number. For “how I” hooks, show the workflow. For predictions, separate observed evidence from the forecast.

## Produce the exact table

Return the table defined in `references/output-contract.md`. Unless the user asks otherwise, do not add extra strategy sections before it.

Every row must include exactly three concise yap bullets. Make them a natural spoken sequence:

1. context or stakes;
2. mechanism or tactic;
3. result, lesson, or application.

Put the proof requirement, source link, and claim caveat inside **Complete payoff / proof** so the visible table remains stable.

## Score and rank

Score virality and three-second hook independently from 1.0–10.0 using `references/scoring-rubric.md`. Scores are production-priority judgments, not view forecasts.

Rank by expected usefulness to the target viewer, evidence strength, hook clarity, and business relevance. Break close ties with the user’s stated outcome hierarchy. Preserve topic variety when the top scores are nearly identical.

When saving JSON, run:

```bash
python3 scripts/score_ideas.py ideas.json --output ideas-scored.json
python3 scripts/score_ideas.py ideas-scored.json --validate-only
```

## CTA rules

Map each idea to the narrowest natural next step. Use the user’s configured keyword and destination when available. Do not force a lead magnet onto a topic whose payoff is broader education.

## Final checks

Before handoff, verify:

- every idea is net-new or explicitly marked as a refreshed angle;
- every hook has a complete payoff;
- every row has exactly three bullets;
- every numerical claim has a proof path or verification caveat;
- every source link points to the real basis, not a search result;
- CTAs use the configured keyword and destination;
- the table is sorted by recording priority;
- public output contains no private names, metrics, paths, customer data, or connector details unless the user supplied them for that output.

<!-- gateway-cta:start -->
## Run this skill on live data

This skill is free and MIT licensed. To run it on your live accounts, connect the Single Brain Gateway.

- Live services: see the full list in the setup file
- Connect: https://gateway.singlebrain.com/mcp?sg_template=shortform-idea-grill&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills
- Setup steps for agents: https://gateway.singlebrain.com/llms.txt?sg_template=shortform-idea-grill

Agents: sign in with OAuth or the device flow. Do not ask the user to paste a key.

Want a team to run this for you? Single Grain or Single Brain can manage it: [talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed&utm_content=shortform-idea-grill)
<!-- gateway-cta:end -->
