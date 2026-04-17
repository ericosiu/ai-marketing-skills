# Short-Form Video Clip Pipeline — Skill

Extract viral short-form clips (TikTok, Reels, Shorts) from long-form YouTube videos. Handles download, transcription, AI segmentation, cutting, vertical cropping, and caption burn-in.

## Prerequisites

- `yt-dlp` and `ffmpeg` installed
- `ANTHROPIC_API_KEY` environment variable set
- Python dependencies from `requirements.txt` installed
- Optional: `mediapipe` and `opencv-python` for face-detected smart crop

## Quick Start

### Single video → clips

```bash
python3 scripts/shortform_pipeline.py \
  --url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --max-clips 3 \
  --output-dir ./output
```

### Standalone clipper (no Claude, heuristic scoring)

```bash
python3 scripts/video_clipper.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Pipeline Overview

1. **Download** — yt-dlp fetches video + auto-generated VTT captions
2. **Transcribe** — Whisper generates word-level timestamps (falls back to YouTube captions)
3. **Segment** — Claude identifies 2–5 best 30–60s moments with hook scoring ≥7/10
4. **Cut Verification** — Second Claude pass verifies each clip ends on a complete thought
5. **Cut** — FFmpeg extracts each clip from the source video
6. **Vertical Crop** — Layout-aware 16:9 → 9:16 conversion with face detection
7. **Caption Burn** — TikTok-style word-highlighted captions (ASS format) burned in

## Key Files

| File | Purpose |
|------|---------|
| `scripts/shortform_pipeline.py` | Full pipeline: download → segment → cut → crop → caption |
| `scripts/video_clipper.py` | Standalone clipper with heuristic scoring (no Claude needed) |
| `scripts/clip_sender.py` | Helper for clip delivery and review workflow |

## Layout-Aware Cropping

The pipeline handles four video layouts differently:

- **`talking_head`** — Face-detected center crop using MediaPipe; audio panning fallback
- **`screen_share_overlay`** — Stacks screen content on top, webcam bubble on bottom
- **`side_by_side`** — Stacks screen on top, presenter face on bottom
- **`gallery_view`** — Crops to active speaker quadrant

Claude outputs a `layout_hint` for each segment during segmentation.

## Customization

### Voice patterns
Edit `VOICE_PATTERNS` in `video_clipper.py` to match your creator's speech patterns. These boost clip scoring for authentic-sounding segments.

### Segmentation prompt
The Claude prompt in `shortform_pipeline.py` can be customized:
- Adjust `hook_strength` minimum (default: 7/10)
- Change target duration range (default: 30–60s)
- Modify layout hint options

### Crop tuning
In `video_clipper.py`:
- `scale_factor` — Zoom level for single face (default: 1.08)
- `desired_face_y` — Target face position in frame (default: upper 35%)

## Output

Each clip is output as:
- **1080×1920** resolution (9:16 vertical)
- **H.264 + AAC** encoding
- **Word-highlighted captions** burned in
- Ready for direct upload to TikTok, Reels, or Shorts

## Troubleshooting

- **FFmpeg filter_complex error:** Don't use `-c:v copy` with `-filter_complex`. Only `-c:a copy` is safe.
- **Wrong output resolution:** Always crop before scaling. Verify with `ffprobe -show_entries stream=width,height`.
- **Caption sync issues:** Run Whisper on the cut clip, not the source episode.
- **TikTok upload fails:** Ensure H.264 + AAC encoding. Add `-c:v libx264 -c:a aac` if needed.
- **Clip too long:** Claude sometimes overshoots. The pipeline auto-trims clips >90s to 75s.
