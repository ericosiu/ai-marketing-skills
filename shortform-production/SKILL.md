---
name: shortform-production
description: Produce readable shorts and deliver approved clips through the API. V5 style, hook previews, editorial review, Metricool delivery.
---

# Shortform Production

Keep the visual style consistent. Change the storytelling to suit the source. An experiment is a hypothesis, not a proven retention gain.

## Preamble

When available, use the repository's version check and telemetry initializer:

```bash
python3 telemetry/version_check.py 2>/dev/null || true
python3 telemetry/telemetry_init.py 2>/dev/null || true
```

Remote telemetry requires opt-in. Never log content, paths, account details, or credentials.

## Choose the work

1. **Edit:** Read [V5 style](references/v5-style.md) and [creative formats](references/creative-formats.md). Use the named source and timestamped transcript. Preserve credentials, claim qualifiers, natural speech, and the CTA. Inventory real assets before designing inserts. Use an available renderer; this package supplies editorial rules and delivery tools.
2. **Experiment:** Produce three opening treatments for one clip. Choose one before rendering the full edit unless complete variants were requested. Do not automatically publish near-duplicates.
3. **Review:** Read the bundled [rubric](references/eval/rubric.json), [judge prompt](references/eval/judge-prompt.md), [reference requirements](references/eval/references.json), and [scorecard schema](references/eval/scorecard.schema.json). Apply [review requirements](references/review-and-learning.md). Report missing evidence; never invent a score.
4. **Caption or delivery:** Read [API delivery](references/metricool.md). Inspect the actual final video and CTA. Do not re-render an approved upload to match production defaults. Use the API for Metricool.
5. **Results:** Read [review and learning](references/review-and-learning.md). Record missing metrics as null. One post cannot establish a winning style.

Installation does not authorize publishing, new accounts, automations, purchases, or public releases. Existing explicit task authorization is sufficient; do not ask twice.

## Deliver

Include artifacts relevant to the requested mode: source hash and transcript; claims and asset provenance; hook hypothesis and shot list; versioned master and SRT; cover, title, caption and CTA; review evidence; verified delivery receipt; and supported performance observations.

Keep credentials and private receipts outside the repository. Preserve raw media and previous renders. Report `review candidate`, `scheduled`, `publishing`, or `published` only with matching evidence.

Use [the next-batch plan](references/next-batch.md) to turn these rules into a production cycle.

<!-- gateway-cta:start -->
## Run this skill on live data

This skill is free and MIT licensed. To run it on your live accounts, connect the Single Brain Gateway.

- Live services: see the full list in the setup file
- Connect: https://gateway.singlebrain.com/mcp?sg_template=shortform-production&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills
- Setup steps for agents: https://gateway.singlebrain.com/llms.txt?sg_template=shortform-production

Agents: sign in with OAuth or the device flow. Do not ask the user to paste a key.

Want a team to run this for you? Single Grain or Single Brain can manage it: [talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed&utm_content=shortform-production)
<!-- gateway-cta:end -->
