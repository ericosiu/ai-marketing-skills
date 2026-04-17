# Short-Form Video Clip Pipeline

Automatically extract viral short-form clips (TikTok, Reels, Shorts) from long-form YouTube videos. Downloads, transcribes, segments with AI, cuts, crops to vertical 9:16, and burns TikTok-style captions — all in one pipeline.

A 60-minute episode becomes 3–5 platform-ready vertical clips in under 25 minutes.

## Features

- **AI-powered segmentation** — Claude identifies the highest-impact 30–60 second moments based on hook strength, emotional punch, and standalone value
- **Smart vertical cropping** — Face detection (MediaPipe) or audio panning analysis to intelligently crop 16:9 → 9:16 without losing the presenter
- **Layout-aware reformatting** — Handles talking head, screen share overlay, side-by-side, and gallery view layouts with different crop strategies
- **TikTok-style captions** — Word-highlighted ASS subtitles (current word in yellow) burned directly into the video
- **Whisper transcription** — Local word-level timestamps for precise caption sync, with YouTube auto-caption fallback
- **Cut verification** — Second AI pass to ensure clips end on complete thoughts, not mid-sentence
- **Batch processing** — Scan a channel's knowledge base for new episodes and process them automatically
- **Google Drive upload** — Optional automatic upload with retry and local backup on failure

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   DOWNLOAD  │────▶│ TRANSCRIBE  │────▶│   SEGMENT   │────▶│     CUT     │────▶│   REFORMAT  │────▶│  CAPTIONED  │
│             │     │             │     │             │     │             │     │             │     │             │
│  yt-dlp     │     │  Whisper    │     │   Claude    │     │   FFmpeg    │     │   FFmpeg    │     │   FFmpeg    │
│             │     │  (local)    │     │   (API)     │     │  (cut)      │     │  (9:16 crop │     │  (ASS burn  │
│             │     │             │     │             │     │             │     │  + face det) │     │   overlay)  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │                   │                   │                   │
  episode.mp4        transcript.vtt      segments.json       clip_raw.mp4       clip_vert.mp4      clip_final.mp4
  (16:9 video)    (timestamped text)  (start/end/title      (landscape)         (9:16 vertical)    (captioned,
                                       + layout hint)                                                platform-ready)
```

### Pipeline Steps

| Step | Tool | Input | Output | Cost |
|------|------|-------|--------|------|
| Download | yt-dlp | YouTube URL | MP4 + VTT captions | Free |
| Transcribe | Whisper (local) | MP4/audio | Word-level timestamps | Free |
| Segment | Claude API | Transcript text | Clip metadata JSON | ~$0.50–1.00/episode |
| Cut | FFmpeg | MP4 + metadata | Individual clips (16:9) | Free |
| Vertical Crop | FFmpeg + MediaPipe | Landscape clip | 9:16 clip (1080×1920) | Free |
| Caption Burn | FFmpeg | Vertical clip + ASS | Captioned clip | Free |

**Total cost per episode:** $0.50–1.00 (Claude API only)

## Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| Python 3.10+ | Runtime | — |
| yt-dlp | Download YouTube videos | `brew install yt-dlp` or `pip install yt-dlp` |
| FFmpeg | Video cutting, cropping, caption burn | `brew install ffmpeg` |
| openai-whisper | Local transcription | `pip install openai-whisper` |
| mediapipe | Face detection for smart crop | `pip install mediapipe` |
| anthropic | Claude API client | `pip install anthropic` |

## Installation

```bash
# Install system dependencies
brew install yt-dlp ffmpeg

# Install Python dependencies
pip install -r requirements.txt

# Set your Anthropic API key
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Usage

### Process a single video

```bash
python3 scripts/shortform_pipeline.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --max-clips 3
```

### Process with custom output directory

```bash
python3 scripts/shortform_pipeline.py --url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --max-clips 5 --output-dir ./my-clips
```

### Scan a channel for new videos

```bash
python3 scripts/shortform_pipeline.py --channel my-podcast --max-clips 2
```

### Use the standalone clipper (auto-scoring, no Claude)

```bash
python3 scripts/video_clipper.py --url "https://www.youtube.com/watch?v=VIDEO_ID"

# Without Whisper (YouTube captions only)
python3 scripts/video_clipper.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --no-whisper

# Dry run
python3 scripts/video_clipper.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --dry-run
```

## How It Works

### AI Segmentation

The pipeline sends the full transcript to Claude with a specialized prompt that evaluates:

- **Hook strength (1–10):** Does the first sentence stop the scroll? Only clips scoring ≥7 are included.
- **Single-idea constraint:** Each clip must contain exactly one complete idea — no summaries of multiple points.
- **Layout detection:** Claude infers the video layout (talking head, screen share, side-by-side, gallery) from transcript context and outputs a `layout_hint` for each clip.

### Smart Vertical Cropping

Standard center-crop fails whenever screen share content is visible. The pipeline uses layout-aware cropping:

| Layout | Strategy |
|--------|----------|
| `talking_head` | Face-detected center crop (MediaPipe) or audio-panning fallback |
| `screen_share_overlay` | Stack: screen content on top, webcam bubble on bottom |
| `side_by_side` | Stack: screen on top, presenter face on bottom |
| `gallery_view` | Crop to active speaker quadrant |

### Caption System

Two caption modes:

1. **ASS word-highlight (default with Whisper):** Shows 3-4 words at a time, current word highlighted in yellow. TikTok-native look.
2. **SRT sentence-level (fallback):** When word-level timestamps aren't available. Bold white text with black outline.

### Scoring (Standalone Clipper)

The `video_clipper.py` script can find clips without Claude using a heuristic scoring system (0–40 points):

- **Hook strength (0–10):** Questions, superlatives, numbers, contrarian framing
- **Value content (0–10):** Actionable advice, revenue/growth data, personal stories
- **Standalone quality (0–10):** Clean start/end, low pronoun density, logical flow
- **Voice match (0–10):** Patterns matching the creator's speaking style

Minimum score threshold: 18/40.

## Output Specifications

| Platform | Resolution | Max Duration | Format |
|----------|-----------|-------------|--------|
| TikTok | 1080×1920 | 60s | MP4 (H.264 + AAC) |
| Instagram Reels | 1080×1920 | 90s | MP4 (H.264 + AAC) |
| YouTube Shorts | 1080×1920 | 60s | MP4 (any codec) |

## Directory Structure

```
short-form-pipeline/
├── README.md
├── SKILL.md              # Claude Code / AI assistant instructions
├── requirements.txt
└── scripts/
    ├── shortform_pipeline.py   # End-to-end pipeline (Claude-powered)
    ├── video_clipper.py         # Standalone clipper (heuristic scoring)
    └── clip_sender.py           # Clip delivery/review helper
```

## Customization

### Voice Patterns

Edit the `VOICE_PATTERNS` list in `video_clipper.py` to match your creator's speaking style. These patterns boost the scoring for segments that sound authentically like the creator.

### Segmentation Prompt

The Claude segmentation prompt is embedded in `shortform_pipeline.py`. Customize the criteria, hook strength threshold, or layout hint options to match your content style.

### Crop Parameters

Face detection zoom factors and positioning can be tuned in `video_clipper.py`:
- `scale_factor` — Base zoom level (default 1.08 for single face)
- `desired_face_y` — Vertical face position target (default: upper 35% of frame)

## Cost Breakdown

| Volume | Daily Cost | Monthly Cost |
|--------|-----------|--------------|
| 1 episode/day (3 clips) | $0.50–1.00 | $15–30 |
| 3 episodes/day (10 clips) | $1.50–3.00 | $45–90 |
| 6 episodes/day (20 clips) | $3.00–6.00 | $90–180 |

All costs are Claude API only. Transcription, cutting, cropping, and captioning are free (local).

## License

MIT
