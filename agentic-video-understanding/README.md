# Agentic video understanding

Goal-directed video/audio moment extraction via Gemini agentic video understanding. Cheaper than fixed-FPS full ingest. **Understanding only** — not an editor.

## When to use

Sales calls, podcasts, YouTube episodes, Loom trials, discovery recordings — anywhere an agent needs timestamps + quotes without chewing every frame.

## Setup

1. Gemini API or [AI Studio](https://ai.studio)
2. Set `GEMINI_API_KEY`
3. Drop `SKILL.md` into your agent harness (Claude Code: `.claude/skills/`, Cursor/Grok: skills library)

## Run

Give the agent a `source` + one-sentence `goal`. It returns ranked moments (`t_start` / `t_end` / quote / confidence) and stops. Cuts, overlays, and publishes stay in other skills.

See [SKILL.md](./SKILL.md).

<!-- gateway-cta:start -->
## Run this skill on live data

This skill is free and MIT licensed. To run it on your live accounts, connect the Single Brain Gateway.

- Live services: see the full list in the setup file
- Connect: https://gateway.singlebrain.com/mcp?sg_template=agentic-video-understanding&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills
- Setup steps for agents: https://gateway.singlebrain.com/llms.txt?sg_template=agentic-video-understanding

Agents: sign in with OAuth or the device flow. Do not ask the user to paste a key.

Want a team to run this for you? Single Grain or Single Brain can manage it: [talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed&utm_content=agentic-video-understanding)
<!-- gateway-cta:end -->
