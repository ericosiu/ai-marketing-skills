# Video Analysis

Read transcripts first. Inspect video when demonstrations, delivery, or edit timing matter. Keep playback silent and verify proposed clips without making the user watch them.

## Quick start

Copy this complete directory into your agent's skills directory. For Codex, the default destination is `~/.codex/skills/video-analysis/`; for Claude Code, use `.claude/skills/video-analysis/` in your project. Preserve existing customizations if the destination already exists.

Example requests:

- “Summarize this video's argument from its transcript.”
- “Check whether the screen demo supports the speaker's claim.”
- “Find a short clip and verify its opening and ending. Keep playback silent.”

## Workflow

`Source → transcript → targeted media checks → grounded answer`

An explicit request for full-video analysis or an editing review uses the required video coverage directly. Transcript access does not require Gemini. Video checks can use a compatible local tool or authorized Gemini access; see [the Gemini reference](references/gemini.md).

This is an instruction-only skill. It does not install a player, add a transcript-service account, or require a bundled implementation script. [YouTubeToTranscript](https://youtubetotranscript.com/) is optional; its extraction and API access have not been integration-tested here.

## Repository integration

When using the full repository, run `python3 telemetry/version_check.py` from its root before the workflow. Log completion with `telemetry/telemetry_log.py`, supplying `--skill video-analysis`, actual elapsed milliseconds via `--duration`, `--success true` or `false`, and `--version 1.0.0`. Preserve the existing opt-in choice; never enable remote telemetry as part of installing or using this skill. Do not log URLs, transcripts, paths, credentials, or model responses. Missing helpers do not block a standalone installation.

## Provenance

The optional Gemini route builds on the workflow introduced by [Agent Native](https://agentnative.inc/resources/give-agents-video-analysis-skill). These instructions add transcript-first routing, silent operation, response parsing guidance, and verification of clip boundaries.

---

<p align="center">
  Built by <a href="https://www.singlegrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Grain</a>. Powered by <a href="https://www.singlebrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Brain</a>.
</p>
