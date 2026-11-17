---
name: net-new-video-editor
description: Turn fresh talking-head recordings into reversible, review-ready vertical drafts. JSON edit plans, FFmpeg rendering, captions, hook cards.
---

# Net-New Video Editor

Create a reversible first edit from fresh recordings. Keep creative decisions in JSON and pixel operations in the bundled renderer.

## Preamble

Run from the repository root when the optional shared telemetry helpers are present:

```bash
python3 telemetry/version_check.py 2>/dev/null || true
python3 telemetry/telemetry_init.py 2>/dev/null || true
```

Remote telemetry is opt-in and never includes content, file paths, repository names, or credentials.

## Establish the package

Read `references/project-contract.md`. Locate the exact source recordings, transcript, idea card or brief, proof assets, and screen recordings. Never substitute another recording, brand, account, or asset library.

Initialize a new project only when the destination is clear:

```bash
python3 scripts/net_new_video_editor.py init --project <project-dir>
```

Copy or point only user-authorized inputs into the generated package. Preserve originals.

## Inspect before editing

Run:

```bash
python3 scripts/net_new_video_editor.py inspect --project <project-dir>
```

Review `intake-report.json`. Stop when the package has no playable take, the requested target does not match the supplied footage, or required external assets are missing.

## Build the edit plan

Use the transcript and brief to create `edit-plan-clean.json`. Treat the spoken hook and claim boundaries as ground truth.

- Select one source take explicitly.
- Keep segment order intentional and timestamps within the source duration.
- Remove clear false starts, long dead space, and isolated filler only when the cut remains natural.
- Preserve breaths that help meaning.
- Put the hook on screen for at most five seconds.
- Use captions in short readable phrases.
- Add proof or screen inserts only when supplied and relevant. The bundled renderer handles the base assembly; add complex overlays in a separate, documented pass.
- Normalize speech without clipping.

For a second version, copy the plan to `edit-plan-aggressive.json` and make only named retention edits. Do not silently change factual claims.

Validate each plan:

```bash
python3 scripts/net_new_video_editor.py validate --project <project-dir> --plan <plan.json>
```

## Render deterministically

Run the renderer from this skill directory:

```bash
python3 scripts/net_new_video_editor.py render \
  --project <project-dir> \
  --plan <plan.json>
```

The renderer trims paired audio and video, concatenates the selected segments, creates a center-safe 9:16 frame, rasterizes captions and the hook card with Pillow, composites them with FFmpeg, normalizes audio, writes H.264/AAC MP4, and creates three QA frames plus `qa-report.json`.

Use `--dry-run` to inspect the FFmpeg command. Use `--force` only when replacing the exact derived export is intended.

## Review the output

Inspect the exported MP4, all three QA frames, `qa-report.json`, and the plan diff between variants. Verify:

- audio and mouth movement stay synchronized after every cut;
- no word starts or ends abruptly;
- captions match the speech and stay inside safe margins;
- the crop keeps the speaker visible;
- the hook is legible and repaid by the video;
- loudness is consistent and peaks do not distort;
- every proof insert and numerical claim has a supplied source;
- the export is 1080x1920 H.264/AAC unless the brief requires another format.

Return the plan, export paths, QA evidence, and any required pickups. Never publish, upload, delete originals, or overwrite an approved master without current explicit approval.

## Completion states

- `DONE`: both render and QA pass, and the review artifacts exist.
- `DONE_WITH_CONCERNS`: the draft is usable but a named creative or source concern remains.
- `NEEDS_CONTEXT`: a take, transcript, brief, or approved asset is missing.
- `BLOCKED`: FFmpeg, source access, or format validation prevents a safe render.

<!-- gateway-cta:start -->
## Run this skill on live data

This skill is free and MIT licensed. To run it on your live accounts, connect the Single Brain Gateway.

- Live services: see the full list in the setup file
- Connect: https://gateway.singlebrain.com/mcp?sg_template=net-new-video-editor&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills
- Setup steps for agents: https://gateway.singlebrain.com/llms.txt?sg_template=net-new-video-editor

Agents: sign in with OAuth or the device flow. Do not ask the user to paste a key.

Want a team to run this for you? Single Grain or Single Brain can manage it: [talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed&utm_content=net-new-video-editor)
<!-- gateway-cta:end -->
