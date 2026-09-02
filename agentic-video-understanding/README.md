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
