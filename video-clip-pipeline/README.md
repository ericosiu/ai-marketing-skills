# 🎬 Long-Form Video Clip Pipeline

> **Turn full-length YouTube episodes into 3–5 standalone highlight clips — fully automated, end to end.**

An AI-powered pipeline that downloads long-form videos, transcribes them locally with Whisper, uses Claude to identify the best standalone segments, and cuts them into ready-to-upload clips with FFmpeg. A 60-minute episode becomes 3–5 shareable clips in under 15 minutes of compute time.

Proven at scale: channels running this approach have published 1,000+ clips in 6 months, generating millions of views at $5–10/day in operating costs.

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   DOWNLOAD  │────▶│ TRANSCRIBE  │────▶│   SEGMENT   │────▶│     CUT     │────▶│   UPLOAD    │
│             │     │             │     │             │     │             │     │             │
│  yt-dlp     │     │  Whisper    │     │   Claude    │     │   FFmpeg    │     │  YT API     │
│             │     │  (local)    │     │   (API)     │     │             │     │  (optional) │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │                   │                   │
  episode.mp4        transcript.json     segments.json       clip_01.mp4         scheduled
  (video file)    (timestamped text)   (start/end/title)    clip_02.mp4          posts
```

### What Each Step Does

| Step | Tool | Input | Output | Cost |
|------|------|-------|--------|------|
| Download | yt-dlp | YouTube URL | MP4 file | Free |
| Transcribe | Whisper | MP4 file | JSON with timestamps | Free (local) |
| Segment | Claude API | Transcript JSON | Clip metadata JSON | ~$0.50–1.00/episode |
| Cut | FFmpeg | MP4 + metadata | Individual clip MP4s | Free |
| Upload | YouTube Data API | Clip MP4s | Published/scheduled videos | Free (within quota) |

---

## Tools

### 1. 🎬 End-to-End Pipeline (`longform_pipeline.py`)

The full automated pipeline: download → transcribe → segment → verify cuts → export clips.

**What it does:**
- Downloads video + auto-generated subtitles from YouTube
- Parses VTT transcript into timestamped text
- Sends transcript to Claude for AI segmentation (finds 3–5 best standalone segments)
- Verifies each cut point lands on a clean sentence boundary
- Cuts clips with FFmpeg (landscape 16:9, re-encoded for clean cuts)
- Optionally uploads to Google Drive

```bash
# Process a single video
python3 longform_pipeline.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --max-clips 3

# Process videos from a channel knowledge base
python3 longform_pipeline.py --channel my-podcast --max-clips 5

# Specify output directory
python3 longform_pipeline.py --url "https://youtube.com/watch?v=ID" --output-dir ./clips/
```

### 2. 🔍 Clip Segmenter (`clip_segmenter.py`)

Standalone segment identification from Whisper transcripts. Useful when you already have transcripts and want to find clip-worthy segments.

```bash
# Analyze a single transcript
python3 clip_segmenter.py --transcript transcripts/episode.json --output segments/episode_segments.json --episode-title "Episode Title"
```

### 3. ✂️ Clip Cutter (`clip_cutter.py`)

Cuts video clips from segment metadata. Uses FFmpeg stream copy for speed (under 5 seconds per clip, zero quality loss).

```bash
# Cut clips from segment metadata
python3 clip_cutter.py --source downloads/episode.mp4 --segments segments/episode_segments.json --output-dir clips/
```

### 4. 🤖 Scored Pipeline (`scored_pipeline.py`)

Advanced pipeline with a 10-expert LLM scoring panel. Only cuts clips that score above a threshold (default: 90/100). Higher quality, fewer clips.

```bash
# Process with quality scoring (only cuts 90+ scored clips)
python3 scored_pipeline.py --url "https://youtube.com/watch?v=ID" --min-score 90

# Dry run (score only, don't cut)
python3 scored_pipeline.py --url "https://youtube.com/watch?v=ID" --dry-run
```

---

## Quick Start

### 1. Install dependencies

```bash
# System tools
brew install yt-dlp ffmpeg  # macOS
# Or: apt install ffmpeg && pip install yt-dlp  # Linux

# Python dependencies
pip install -r requirements.txt
```

### 2. Set API keys

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# Add to ~/.zshrc or ~/.bashrc to persist
```

### 3. Run on a video

```bash
# Full pipeline — download, transcribe, segment, cut
python3 longform_pipeline.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --max-clips 3

# Or step by step:
# 1. Download
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best" -o "downloads/%(title)s.%(ext)s" "URL"

# 2. Transcribe
whisper "downloads/episode.mp4" --model medium --output_format json --output_dir transcripts/

# 3. Segment
python3 clip_segmenter.py --transcript transcripts/episode.json --output segments/episode_segments.json

# 4. Cut
python3 clip_cutter.py --source downloads/episode.mp4 --segments segments/episode_segments.json --output-dir clips/
```

---

## How the AI Segmentation Works

Claude reads the full transcript and identifies the best standalone segments using these criteria:

- **Clear narrative arc** — setup → development → resolution
- **Strong hook** — first 30 seconds must grab attention (bold claim, surprising stat, compelling story)
- **Complete thought** — feels satisfying as a standalone watch, not cut off mid-idea
- **Ideal length** — 5–15 minutes for long-form clips (shorter is better if the idea is complete)
- **High insight density** — every minute delivers value

Each segment gets a hook strength score (1–10). Only segments scoring ≥6 make the cut. The pipeline also verifies each cut point against the transcript to ensure sentences aren't split.

---

## Scaling Strategy

### Processing a Full Back Catalog

```
500 episodes × 60 min each:

Step 1 (Download):     500 × 3 min    = 25 hours  (parallelizable)
Step 2 (Transcribe):   500 × 8 min    = 67 hours  (CPU-bound, parallelizable)
Step 3 (Segment):      500 × 1 min    = 8 hours   (API rate-limited)
Step 4 (Cut):          500 × 0.5 min  = 4 hours
Total clips generated: ~2,000–2,500
```

**Parallelizing transcription:**
```bash
ls downloads/*.mp4 | xargs -P 4 -I {} whisper {} --model medium --output_format json --output_dir transcripts/
```

### Recommended Upload Cadence

| Month | Upload Rate | Expected Outcome |
|-------|-------------|-----------------|
| 1 | 3–5/day | Algorithm learning, low views |
| 2 | 5–10/day | First breakout clips |
| 3–4 | 10–15/day | Peak performance window |
| 5+ | Maintain 5–10/day | Shift to fresh episodes |

---

## Cost Breakdown

### Per Episode

| Component | Cost |
|-----------|------|
| yt-dlp download | Free |
| Whisper transcription | Free (local) |
| Claude segmentation | $0.50–1.00 |
| FFmpeg cutting | Free |
| **Total per episode** | **$0.50–1.00** |

### At Scale

| Volume | Monthly Cost |
|--------|-------------|
| 10 clips/day (~3 episodes) | $45–90 |
| 20 clips/day (~6 episodes) | $90–180 |
| 50 clips/day (~15 episodes) | $225–450 |

---

## Quality Control

### Common Issues and Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Clip starts mid-sentence | Keyframe boundary | Add 2–3 sec buffer to start_time |
| Clip ends abruptly | Keyframe boundary | Add 2–3 sec buffer to end_time |
| Transcript gibberish | Audio quality | Use `--model large` for Whisper |
| Claude picks boring segments | Prompt too permissive | Raise hook_strength minimum to 7 |
| Clips too similar | Low topic diversity | Add "ensure variety" to prompt |

### Feedback Loop

After collecting performance data, feed it back into the segmentation prompt:

```
HIGH-PERFORMING TOPICS (prioritize these):
- [Topic 1]: avg 8,200 views
- [Topic 2]: avg 6,100 views

LOW-PERFORMING TOPICS (deprioritize):
- [Topic 3]: avg 800 views
```

This turns the segmentation prompt into a compounding asset that improves with every batch.

---

## File Structure

```
video-clip-pipeline/
├── README.md                    # This file
├── SKILL.md                     # Claude Code skill definition
├── requirements.txt             # Python dependencies
├── longform_pipeline.py         # End-to-end pipeline
├── clip_segmenter.py            # AI transcript segmentation
├── clip_cutter.py               # FFmpeg video cutting
├── scored_pipeline.py           # Pipeline with LLM quality scoring
└── data/
    └── .gitkeep                 # Working directories created at runtime
```

---

## Integrations

| Tool | Required | Purpose |
|------|----------|---------|
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Yes | Video download |
| [Whisper](https://github.com/openai/whisper) | Yes | Local transcription |
| [FFmpeg](https://ffmpeg.org) | Yes | Video cutting |
| [Claude API](https://anthropic.com) | Yes | AI segmentation |
| YouTube Data API | Optional | Automated upload |
| Google Drive API | Optional | Cloud storage |

---

## Proven Results

This pipeline architecture (download → transcribe → AI segment → cut → upload) has been validated across multiple channels:

- **1,000+ clips** published from a single channel in 6 months
- **8M+ total views** generated
- **$5–10/day** operating cost at 6+ videos/day
- **15 minutes** processing time per 60-minute episode
- **Near-zero** manual effort after initial setup

The strategy works best in months 2–4 when processing a back catalog. After the catalog is exhausted, shift to clipping new episodes within 48 hours of release.

---

<div align="center">

**🧠 [Want these built and managed for you? →](https://singlebrain.com/?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills)**

*This is how we build agents at [Single Brain](https://singlebrain.com/?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) for our clients.*

[Single Grain](https://www.singlegrain.com/?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) · our marketing agency

📬 **[Level up your marketing with 14,000+ marketers and founders →](https://levelingup.beehiiv.com/subscribe)** *(free)*

</div>
