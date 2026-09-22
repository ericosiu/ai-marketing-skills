# Leveling Up Content Engine

Turn any authorized video link, upload, recording, transcript, podcast, interview, webinar, tutorial, or ad into a source-grounded diagnosis and the strongest justified content portfolio.

## Scope and installation

This is a portable adaptation of the updated Leveling Up Content Engine, not a copy of private episode history. It carries current editor-note, moment-selection, visual-proof and version-bound review rules in [workflow updates](references/editorial-and-release-updates.md). The existing Video Content Engine remains available separately.

Copy this entire folder into your agent's skills directory. Load `SKILL.md`; keep `references`, `scripts`, `agents` and `tests` together. Supply your own authorized source, brand assets, editing profile and channel preferences. This does not provide access to accounts, recordings, publishing tools or paid APIs.

The bundled scripts check source boundaries and delivery files. Human audiovisual and editorial review is still required. No model accuracy or performance uplift is claimed.

## What it does

- Scores hook, clarity, proof, pacing, and payoff.
- Recommends the right editorial and operating modes.
- Inventories long-form, mid-form, short-form, micro, carousel, packaging, and written opportunities.
- Enforces complete-thought edit boundaries and post-render join review.
- Defaults to burned captions, matching SRT, and a designed opening overlay.
- Packages deliverables into a versioned, validated manifest.

## Quick start

```text
Use $leveling-up-content-engine on this authorized video: <URL-or-path>.
Diagnose it and recommend the highest-leverage first release wave before producing anything.
```

The skill defaults to diagnosis. Uploading, scheduling, publishing, changing sharing, spending quota, or activating a campaign requires explicit approval and readback.

## Requirements

- Python 3.10+
- FFmpeg and FFprobe for media rendering and technical QC
- A transcription tool with word- or sentence-level timestamps
- Authorized access to the source and third-party assets

The bundled validators use only the Python standard library.

---

<p align="center">
  Built by <a href="https://www.singlegrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Grain</a>. Powered by <a href="https://www.singlebrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Brain</a>.
</p>
