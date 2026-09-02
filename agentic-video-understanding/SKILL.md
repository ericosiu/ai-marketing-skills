---
name: Agentic video understanding
description: >-
  Use when an agent must extract moments, quotes, objections, hooks, or evidence
  from long video or audio cheaper than full-frame ingest — sales calls,
  podcasts, YouTube episodes, Loom trials, discovery recordings. Goal-directed
  watch via Gemini agentic video understanding (frames, audio, or transcript).
  Not for cutting, overlays, rendering, scheduling, or publishing.
---

# Agentic video understanding

Hireable understanding layer. The model takes a goal and decides what to watch, at what speed, and through which modality (frames, audio, transcript), fetching only the moments needed. Vendor claims: up to ~66% lower cost and ~88% fewer tokens vs static fixed-FPS ingest, with higher accuracy.

## What this is / is not

**Is:** goal → watch only what you need → timestamps + quotes + confidence.

**Is not:** a video editor. Do not cut, overlay, caption-burn, render, schedule, post, email, or write CRM from this skill. Hand cuts to Overlap, FFmpeg, or `net-new-video-editor`. Approvals stay with the calling lane.

## When to use

- Pre-call / sales-call mining: buyer objection, next step, competitive mention
- Shortform scoring: find a 3-second standalone hook and in/out points
- Longform / X research: named-person + contrast moments in podcast or YouTube tape
- Talent review: bar evidence in a Loom or trial recording
- Client audit: every mention of a keyword across a discovery recording

Skip when the job is already a clean transcript and you only need text search.

## Inputs

| Field | Required | Notes |
|-------|----------|-------|
| `source` | yes | URL or local media path the runtime can read |
| `goal` | yes | One sentence retrieval goal |
| `keywords` | no | Extra strings to bias retrieval |
| `max_moments` | no | Default 5 |
| `modality` | no | `auto` (default), `frames`, `audio`, or `transcript` |

## Process

1. **Restate the goal** as 1–3 retrieval queries. Done when each query is falsifiable (you would know if a moment matched).
2. **Call Gemini agentic video understanding** (Gemini API or AI Studio) with `source`, queries, `max_moments`, and modality preference. Prefer the agentic path over fixed-FPS full ingest when available. Done when the API returns candidate windows or an explicit empty set.
3. **Normalize moments** into the output schema below. Flag paraphrase vs verbatim. Drop fabricated timestamps. Done when every kept moment has `t_start`, `t_end`, `modality`, `quote`, `why`, `confidence`.
4. **Stop and hand off** to the caller. Do not cut, overlay, schedule, publish, email, or CRM-write.

## Output schema

Markdown for humans, optional JSON for machines:

```json
{
  "goal": "",
  "source": "",
  "moments": [
    {
      "t_start": "MM:SS",
      "t_end": "MM:SS",
      "modality": "frames|audio|transcript",
      "quote": "",
      "verbatim": true,
      "why": "",
      "confidence": 0.0
    }
  ],
  "empty_reason": null,
  "tokens_note": "agentic path used|fallback static ingest"
}
```

## Hard gates

- No full fixed-FPS ingest when the agentic path is available
- No invented timestamps or quotes
- No dumping full transcripts or client PII into public artifacts
- No cut / render / overlay / schedule / publish / send from this skill

## Setup

- Gemini API key or Google AI Studio access: https://ai.studio
- See Google’s developer guide for agentic video understanding in Gemini
- Env: `GEMINI_API_KEY` (or the project’s existing Google AI credential)

## Caller one-liners

- Pre-call: `goal="exact next-step commitment and any pricing pushback"`
- Shortform: `goal="best 3-second standalone hook; return in/out for one clip"`
- Talent: `goal="evidence they hit the role bar on X; max 5 moments"`
- Audit: `goal="every mention of Reddit, AEO, or budget"`

## Completion

Done when the caller has the schema above (or a documented empty set) and this skill has performed no side effects beyond the Gemini read.
