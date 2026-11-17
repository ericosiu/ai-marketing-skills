# Shortform Format Library

Maintain a visual format library and turn source-grounded ideas into recording outlines and editing briefs.

## Quick start

Copy this complete directory into your agent's skills folder, then ask:

```text
Use $shortform-format-library to review these content spikes and my existing
format page. Return a proposed content table, match each idea to two formats,
and prepare three talking prompts. Keep performance claims tied to evidence.
```

## Default content table

Each idea includes priority, proposed hook, idea source, suggested format, a **Watch reference** video link, three talking prompts, visual payoff/claim limit, and CTA. The creator and editor use the same chosen reference. Missing references are labeled rather than invented.

## Architecture

`SKILL.md` routes research, content tables, page updates, and production handoffs. References explain spike interpretation, source freshness, stable outline storage, and editor/ManyChat boundaries. The optional validator checks a portable JSON interchange. Existing page schemas need not change.

## Examples

- Refresh the last 30 days of an authorized creator roster and explain additions.
- Distinguish topic signals from post outliers and retention peaks in supplied analytics.
- Turn a fictional team's product demonstration into a source-linked outline.
- Prepare a comment-to-access demo reel and a draft DM flow for a public library.

The skill can hand off to `manychat-ig-lead-magnet` when installed. It does not bundle that skill or require it for drafting. It does not automatically activate research jobs, publish a site, spend editing credits, or enable live messages.

## Validation

Python 3.10+, standard library only:

```bash
python3 shortform-format-library/scripts/validate_library.py snapshot.json
python3 -m unittest discover -s shortform-format-library/tests
```

See `references/page-and-data.md` for the interchange contract. Source truth and actual page/render behavior need separate review. Keep private source data and generated client output outside this public repository.


<!-- gateway-cta:start -->
## Run this skill on live data

This skill is free and MIT licensed. To run it on your live accounts, connect the Single Brain Gateway.

- Live services: see the full list in the setup file
- Connect: https://gateway.singlebrain.com/mcp?sg_template=shortform-format-library&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills
- Setup steps for agents: https://gateway.singlebrain.com/llms.txt?sg_template=shortform-format-library

Agents: sign in with OAuth or the device flow. Do not ask the user to paste a key.

Want a team to run this for you? Single Grain or Single Brain can manage it: [talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed&utm_content=shortform-format-library)
<!-- gateway-cta:end -->
