# Video Content Engine

Turn any authorized video link, upload, recording, transcript, podcast, interview, webinar, tutorial, or ad into a source-grounded diagnosis and the strongest justified content portfolio.

## What it does

- Scores hook, clarity, proof, pacing, and payoff.
- Recommends the right editorial and operating modes.
- Inventories long-form, mid-form, short-form, micro, carousel, packaging, and written opportunities.
- Enforces complete-thought edit boundaries and post-render join review.
- Defaults to burned captions, matching SRT, and a designed opening overlay.
- Packages deliverables into a versioned, validated manifest.

## Public package and scope

This is the sanitized, brand-neutral public derivative of the Leveling Up Content Engine. It includes portfolio routing, editorial and delivery contracts, and runnable boundary and file-integrity validators. It excludes private recordings, transcripts, review comments, brand reference assets, credentials, and machine-specific configuration.

The current workflow covers screen-share completeness, spoken hooks, full-length review, versioned revisions, and editable team handoff. The shared editing workspace is a design contract, not a bundled or deployed application. No hosting, cloud rendering, or multiplayer service is installed by this skill.

## Quick start

```text
Use $video-content-engine on this authorized video: <URL-or-path>.
Diagnose it and recommend the highest-leverage first release wave before producing anything.
```

The skill defaults to diagnosis. Uploading, scheduling, publishing, changing sharing, spending quota, or activating a campaign requires explicit approval and readback.

For an approved production pass:

```text
Produce the agreed portfolio from the authorized source. Inventory all camera,
screen-share, and audio tracks. Show the cut plan and opening beats, then
provide full-duration versioned previews and an editable project for review.
Keep all files private and do not publish.
```

Read [editorial review](references/editorial-review.md) for edit acceptance and [editing workflow](references/editing-workflow.md) for preview, revision, and team handoff requirements.

## Validation

```bash
python3 -m unittest discover -s video-content-engine/tests -v
python3 security/sanitizer.py --scan --dir video-content-engine --recursive
```

The validators do not prove editorial quality or approval. Full output review remains required.

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
