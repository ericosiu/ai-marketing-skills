# Video Caption Generator

Automatically transcribe short-form videos from Google Drive, deduplicate by content, and generate social media captions + YouTube/Facebook titles using AI.

## What It Does

1. **Scans** a Google Drive folder for new video files (MP4, MOV, etc.)
2. **Transcribes** each video locally using OpenAI Whisper
3. **Deduplicates** — detects A/B variants (same audio, different on-screen titles) and processes them all with proper tagging
4. **Generates** a social media caption and a YouTube/Facebook title for each clip using Claude API
5. **Tracks** processed video IDs so re-runs skip already-seen files

## Example Output

```
*my-video-clip.mp4*
📝 Transcript: The biggest mistake people make with paid ads is not testing creative fast enough...
🎬 Caption: Most people blow their ad budget because they test one creative at a time. Run 5-10 variants in the first week — kill losers fast, scale winners hard. Speed beats perfection every time.
📺 YT/FB Title: Why 90% of Ad Budgets Get Wasted
```

For A/B variants (same transcript, different filename):

```
*my-clip(1).mp4* (A/B variant of my-clip.mp4)
📝 Transcript: The biggest mistake people make with paid ads...
🎬 Caption: ...
📺 YT/FB Title: The Ad Mistake That Burns Your Budget
```

## Prerequisites

- **Python 3.10+**
- **OpenAI Whisper** installed locally (`pip install openai-whisper` or via Homebrew)
- **Google Drive API access** via a CLI tool that can list and download files (the script uses `gws-gateway.sh` by default — adapt the `gws()` function to your Drive CLI or SDK)
- **Anthropic API key** for caption/title generation

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Install Whisper (if not already):

```bash
pip install openai-whisper
# or on macOS:
brew install whisper
```

3. Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

4. Configure your Google Drive CLI path in `scripts/process_videos.py` (see the `GWS_GATEWAY` variable).

## Usage

```bash
python3 scripts/process_videos.py --folder-id YOUR_FOLDER_ID
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--folder-id` | *(required)* | Google Drive folder ID to scan for videos |
| `--processed-log` | `processed_ids.json` | Path to JSON file tracking already-processed video IDs |

### Multiple Folders

Run against different folders — they share the same `processed_ids.json` since Drive file IDs are globally unique:

```bash
python3 scripts/process_videos.py --folder-id YOUR_MAIN_FOLDER_ID
python3 scripts/process_videos.py --folder-id YOUR_AB_FOLDER_ID
```

## Caption & Title Style Guide

- **Caption:** First person, conversational, no hashtags, 2-4 sentences. Hook first, insight second.
- **Title:** Curiosity-driven, under 60 chars, no clickbait. Lead with tension or a number.

## Customization

- Edit the prompt in `generate_caption_and_title()` to match your brand voice
- Swap `claude-sonnet-4-6` for another model in the API call
- Replace the `gws()` function with your own Google Drive SDK integration
- Add a `log_to_sheet()` implementation to track results in a Google Sheet

## How It Works

```
Google Drive Folder
        │
        ▼
  List new videos (skip already-processed IDs)
        │
        ▼
  Download each → temp directory
        │
        ▼
  Whisper transcription (local, model: turbo)
        │
        ▼
  Content hash for dedup (detect A/B variants)
        │
        ▼
  Claude API → caption + title per clip
        │
        ▼
  Output formatted results + save processed IDs
```

## License

MIT
