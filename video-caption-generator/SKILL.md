---
name: video-caption-generator
description: >
  Transcribe short videos from a Google Drive folder, deduplicate by content,
  and generate social captions + YouTube/Facebook titles. Use when new video
  clips are dropped into a Drive folder and you need transcript, caption, and
  title for each unique clip.
  Trigger phrases: "process videos in drive", "transcribe new clips",
  "caption these videos", "generate titles for these clips".
---

# Video Caption Generator

Processes new MP4s from a Google Drive folder: transcribes, deduplicates, generates captions + titles.

## Drive Folder Setup

Configure your Google Drive folder IDs before first use:

| Folder | Purpose |
|--------|---------|
| Main / To Schedule | New clips are dropped here for processing |
| Scheduled | Already posted/scheduled clips (moved after publishing) |
| A/B | Title variants for later posting |

Set your folder IDs in `folder-map.json` or pass them directly via `--folder-id`.

## Quick Run

```bash
python3 skills/video-caption-generator/scripts/process_videos.py \
  --folder-id YOUR_FOLDER_ID
```

Processed video IDs are logged to `processed_ids.json` so already-seen videos are skipped on future runs.

## A/B Variant Handling

Videos with identical transcripts but different filenames (e.g., `0411.mp4`, `0411(1).mp4`) are A/B title variants — same audio, different on-screen title. The script processes ALL variants (no dedup skipping) and tags them as A/B variants in the output.

## Output Format

For each unique new clip, output:

```
*<filename>*
📝 *Transcript:* <raw spoken words>
🎬 *Caption:* <social-friendly 2-4 sentence caption>
📺 *YT/FB Title:* <punchy title under 60 chars>
```

## Caption + Title Style Guide

- **Caption:** First person, conversational, no hashtags, 2-4 sentences. Hook first, insight second.
- **Title:** Curiosity-driven, under 60 chars, no "How I..." unless earned. Lead with the tension or number.

## Dependencies

- `whisper` (local installation, model: turbo)
- Google Drive CLI or SDK for listing/downloading files
- Anthropic API key (set via `ANTHROPIC_API_KEY` environment variable)

## Configuration

1. Set `ANTHROPIC_API_KEY` in your environment
2. Update `GWS_GATEWAY` in `scripts/process_videos.py` to point to your Google Drive CLI
3. Update `WHISPER_BIN` if Whisper is installed at a different path

## Adding New Folders

Pass `--folder-id <ID>` for different folders. Each folder uses the same shared `processed_ids.json` log (Drive IDs are globally unique so there's no collision).
