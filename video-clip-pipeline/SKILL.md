# Long-Form Video Clip Pipeline

## Preamble (runs on skill start)

```bash
# Version check (silent if up to date)
python3 telemetry/version_check.py 2>/dev/null || true

# Telemetry opt-in (first run only, then remembers your choice)
python3 telemetry/telemetry_init.py 2>/dev/null || true
```

> **Privacy:** This skill logs usage locally to `~/.ai-marketing-skills/analytics/`. Remote telemetry is opt-in only. No code, file paths, or repo content is ever collected. See `telemetry/README.md`.

---

AI-powered pipeline that converts long-form YouTube episodes into standalone highlight clips. Download → Transcribe → AI Segment → Cut → Upload. A 60-minute episode becomes 3–5 clips in ~15 minutes.

## When to Use

Use this skill when:
- Converting long-form YouTube content (podcasts, interviews, talks) into highlight clips
- Processing a YouTube back catalog into a clips channel
- Finding the best standalone segments from video transcripts
- Cutting video clips with verified sentence boundaries
- Running a high-volume clip publishing operation ($0.50–1.00 per episode)

## Prerequisites

### System Tools

```bash
brew install yt-dlp ffmpeg        # macOS
# Or: apt install ffmpeg && pip install yt-dlp  # Linux
pip install openai-whisper
```

### Environment Variables

- `ANTHROPIC_API_KEY` — Claude API key (required for segmentation)
- YouTube Data API credentials (optional, for automated upload)

## Tools

### End-to-End Pipeline

| Script | Purpose | Key Command |
|--------|---------|-------------|
| `longform_pipeline.py` | Full pipeline: download → transcribe → segment → verify → cut | `python3 longform_pipeline.py --url URL --max-clips 3` |
| `scored_pipeline.py` | Pipeline with 10-expert LLM quality scoring (only cuts 90+ clips) | `python3 scored_pipeline.py --url URL --min-score 90` |

### Individual Steps

| Script | Purpose | Key Command |
|--------|---------|-------------|
| `clip_segmenter.py` | Find clip-worthy segments from Whisper transcripts | `python3 clip_segmenter.py --transcript file.json --output segments.json` |
| `clip_cutter.py` | Cut clips from segment metadata using FFmpeg | `python3 clip_cutter.py --source video.mp4 --segments segments.json --output-dir clips/` |

## Pipeline Flow

```
YouTube URL
    │
    ▼
[yt-dlp] Download video + auto-subs (VTT)
    │
    ▼
[Whisper] Local transcription with word-level timestamps
    │
    ▼
[Claude] AI segmentation — finds 3-5 best standalone segments
    │  • Scores hook strength (1-10, minimum 6)
    │  • Ensures complete narrative arcs
    │  • Verifies clean cut boundaries
    │
    ▼
[FFmpeg] Cut clips (landscape 16:9)
    │
    ▼
[Optional] Upload to YouTube / Google Drive
```

## Usage Examples

### Full Pipeline (most common)

```bash
# Process a single video
python3 longform_pipeline.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --max-clips 3

# Process from channel knowledge base
python3 longform_pipeline.py --channel my-podcast --max-clips 5

# Custom output directory
python3 longform_pipeline.py --url URL --output-dir ./my-clips/ --max-clips 4
```

### Step-by-Step (when you need control)

```bash
# 1. Download
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best" -o "downloads/%(title)s.%(ext)s" "URL"

# 2. Transcribe
whisper "downloads/episode.mp4" --model medium --output_format json --output_dir transcripts/

# 3. Segment (finds best clips)
python3 clip_segmenter.py \
  --transcript transcripts/episode.json \
  --output segments/episode_segments.json \
  --episode-title "Episode Title"

# 4. Cut
python3 clip_cutter.py \
  --source downloads/episode.mp4 \
  --segments segments/episode_segments.json \
  --output-dir clips/
```

### Quality-Scored Pipeline

```bash
# Only cut clips scoring 90+ from 10-expert panel
python3 scored_pipeline.py --url URL --min-score 90

# Dry run — score candidates without cutting
python3 scored_pipeline.py --url URL --dry-run
```

### Batch Processing

```bash
# Transcribe in parallel (4 at a time)
ls downloads/*.mp4 | xargs -P 4 -I {} whisper {} --model medium --output_format json --output_dir transcripts/

# Process multiple URLs
for url in $(cat urls.txt); do
  python3 longform_pipeline.py --url "$url" --max-clips 3
done
```

## Configuration

### Whisper Model Selection

| Model | Speed (30min video) | Accuracy | Use When |
|-------|-------------------|----------|----------|
| `base` | ~3-4 min | ~95% | Quick testing |
| `medium` | ~7-10 min | ~98% | Production (recommended) |
| `large` | ~15-20 min | ~99% | Noisy audio |

### Claude Segmentation Tuning

The segmentation prompt accepts these adjustments:
- **Hook strength threshold** — Default 6. Raise to 7+ for higher quality (fewer clips)
- **Max segments** — Default 5. Lower to 3 for stricter selection
- **Segment length** — Default 5-15 minutes. Adjust in prompt for your format

### FFmpeg Cutting

- Default uses `-c copy` (stream copy) — instant, zero quality loss, but cuts at keyframe boundaries (±1-2 sec)
- The `longform_pipeline.py` uses re-encoding for frame-accurate cuts at the cost of more CPU time
- Add `--buffer-start 2 --buffer-end 2` to `clip_cutter.py` for padding

## Data Flow

```
YouTube URL → yt-dlp (download) → Whisper (transcribe) → Claude (segment) → FFmpeg (cut) → Clips
                                                              │
                                                              ▼
                                                    Claude (verify cut boundaries)
```

## Cost

- **Per episode:** $0.50–1.00 (Claude API only — everything else is free/local)
- **At scale (10 clips/day):** ~$45–90/month
- **At scale (50 clips/day):** ~$225–450/month

## Dependencies

- Python 3.9+
- `anthropic` — Claude API client
- `openai-whisper` — Local transcription
- `yt-dlp` — Video download (system binary)
- `ffmpeg` / `ffprobe` — Video processing (system binary)
- `requests` — HTTP client (for optional upload features)
