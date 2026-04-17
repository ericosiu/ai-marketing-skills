#!/usr/bin/env python3
"""
shortform_pipeline.py — End-to-end short-form clip pipeline
Segments long YouTube videos into viral TikTok/Reels/Shorts clips.

Usage:
  python3 shortform_pipeline.py --url URL [--max-clips 2] [--output-dir DIR]
  python3 shortform_pipeline.py --channel my-podcast [--max-clips 2]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import anthropic

# ── Paths ──────────────────────────────────────────────────────────────────────
# Configure these to match your workspace layout
WORKSPACE = Path(os.environ.get("PIPELINE_WORKSPACE", Path.cwd()))
DATA_DIR = WORKSPACE / "data" / "clips"
PROCESSED_FILE = DATA_DIR / "processed-shortform.json"
SHORTFORM_PROMPT_FILE = DATA_DIR / "segmentation-prompt-shortform.md"
KB_BASE = WORKSPACE / "knowledge_base" / "youtube"

# ── Channel config ─────────────────────────────────────────────────────────────
# Map channel slugs to display names
CHANNEL_DISPLAY = {
    # "my-podcast": "My Podcast Name",
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def log(msg: str):
    print(f"[pipeline] {msg}", flush=True)


def run(cmd: list, **kwargs) -> subprocess.CompletedProcess:
    log(f"$ {' '.join(str(c) for c in cmd)}")
    return subprocess.run(cmd, **kwargs)


def get_anthropic_client() -> anthropic.Anthropic:
    key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_KEY")
    if not key:
        raise RuntimeError(
            "No ANTHROPIC_API_KEY found. Set the environment variable before running."
        )
    return anthropic.Anthropic(api_key=key)


def load_processed() -> set:
    if PROCESSED_FILE.exists():
        try:
            data = json.loads(PROCESSED_FILE.read_text())
            return set(data.get("urls", []))
        except Exception:
            pass
    return set()


def save_processed(processed: set):
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_FILE.write_text(json.dumps({"urls": sorted(processed)}, indent=2))


def parse_time_to_seconds(t: str) -> float:
    """Parse MM:SS or HH:MM:SS to seconds."""
    parts = t.strip().split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    else:
        return float(t)


def format_seconds_to_time(s: float) -> str:
    m = int(s) // 60
    sec = int(s) % 60
    return f"{m}:{sec:02d}"


def seconds_to_mmss(s: float) -> str:
    m = int(s) // 60
    sec = int(s) % 60
    return f"{m:02d}:{sec:02d}"


def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds using ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", video_path],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


# ── VTT Parsing ────────────────────────────────────────────────────────────────

def parse_vtt(vtt_path: str) -> list[dict]:
    """Parse VTT captions into list of {start, end, text} in seconds."""
    entries = []
    with open(vtt_path, encoding="utf-8", errors="replace") as f:
        content = f.read()

    pattern = re.compile(
        r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})[^\n]*\n(.*?)(?=\n\n|\Z)',
        re.DOTALL
    )
    for m in pattern.finditer(content):
        start_str, end_str, text = m.group(1), m.group(2), m.group(3)
        text = re.sub(r'<[^>]+>', '', text).strip()
        text = re.sub(r'\s+', ' ', text)
        if not text:
            continue
        def vtt_time(s):
            h, mi, rest = s.split(":")
            sec, ms = rest.split(".")
            return int(h)*3600 + int(mi)*60 + int(sec) + int(ms)/1000
        entries.append({
            "start": vtt_time(start_str),
            "end": vtt_time(end_str),
            "text": text,
        })
    return entries


def transcript_to_text(entries: list[dict]) -> str:
    """Convert VTT entries to a readable transcript with timestamps."""
    lines = []
    seen = set()
    for e in entries:
        t = e["text"]
        if t in seen:
            continue
        seen.add(t)
        ts = seconds_to_mmss(e["start"])
        lines.append(f"[{ts}] {t}")
    return "\n".join(lines)


def get_transcript_window(entries: list[dict], center_seconds: float, window: float = 10.0) -> str:
    """Get transcript text ±window seconds around center_seconds."""
    lo, hi = center_seconds - window, center_seconds + window
    lines = []
    seen = set()
    for e in entries:
        if e["end"] < lo or e["start"] > hi:
            continue
        t = e["text"]
        if t in seen:
            continue
        seen.add(t)
        ts = seconds_to_mmss(e["start"])
        lines.append(f"[{ts}] {t}")
    return "\n".join(lines)


# ── Download ───────────────────────────────────────────────────────────────────

def download_video(url: str, out_dir: str) -> tuple[str, str]:
    """Download video + captions. Returns (video_path, vtt_path)."""
    log(f"Downloading: {url}")
    cmd = [
        "yt-dlp",
        "--write-auto-sub", "--sub-lang", "en", "--convert-subs", "vtt",
        "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "--merge-output-format", "mp4",
        "-o", f"{out_dir}/%(title)s.%(ext)s",
        url,
    ]
    result = run(cmd, capture_output=False)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed for {url}")

    mp4_files = list(Path(out_dir).glob("*.mp4"))
    vtt_files = list(Path(out_dir).glob("*.vtt"))
    if not mp4_files:
        raise RuntimeError("No MP4 found after download")
    if not vtt_files:
        raise RuntimeError("No VTT found after download")

    return str(mp4_files[0]), str(vtt_files[0])


# ── Segmentation ───────────────────────────────────────────────────────────────

DEFAULT_SEGMENTATION_PROMPT = """You are a short-form video editor for TikTok, Instagram Reels, and YouTube Shorts.

I'm going to give you a full transcript of a video with timestamps. Your job: Find the **best clips** that would work as 30–60 second short-form clips.

CRITERIA for a great short-form clip:
- HOOK in the first 3 seconds — the opening line must immediately grab attention (surprising stat, bold claim, counterintuitive take, or a story that starts in the middle of action)
- ONE COMPLETE IDEA — one framework, one stat, one story, one revelation. Not a summary of multiple points.
- EMOTIONAL PUNCH — surprise, humor, a strong opinion, or data that shocks
- CLIFFHANGER OR TAKEAWAY — ends with a clear insight or leaves the viewer wanting more
- Ideal length: 30–45 seconds. Hard max: 60 seconds.

AVOID:
- Segments that start mid-sentence or mid-thought
- Segments longer than 60 seconds
- Meandering setup before the hook
- Segments that reference earlier content ("as I mentioned...")
- Segments with multiple unrelated ideas

For each clip, return a JSON object with:
- start_time: "MM:SS" format
- end_time: "MM:SS" format
- title: short descriptive title
- hook_sentence: the exact first sentence of the clip (becomes the hook text overlay)
- payoff_sentence: the key takeaway or punchline
- why: brief explanation of why this will perform on short-form
- layout_hint: one of "talking_head", "screen_share_overlay", "side_by_side", "gallery_view"

layout_hint options:
- "talking_head" — standard presenter only, use center crop
- "screen_share_overlay" — full screen share with small webcam bubble
- "side_by_side" — presenter and screen share split horizontally
- "gallery_view" — multiple people visible

Return ONLY valid JSON array. No markdown, no commentary.

Here is the transcript:
{TRANSCRIPT}"""


def call_claude_segmentation(client: anthropic.Anthropic, transcript: str, n: int = 2) -> list[dict]:
    """Ask Claude to find the best N short-form clips."""
    # Use custom prompt file if it exists, otherwise use default
    if SHORTFORM_PROMPT_FILE.exists():
        prompt = SHORTFORM_PROMPT_FILE.read_text().replace("{TRANSCRIPT}", transcript)
    else:
        prompt = DEFAULT_SEGMENTATION_PROMPT.replace("{TRANSCRIPT}", transcript)

    prompt += f"\n\nReturn exactly {n} clips as a JSON array."

    log("Calling Claude for segmentation...")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = message.content[0].text.strip()

    # Parse JSON from response
    json_match = re.search(r'(\[[\s\S]+\]|\{[\s\S]+\})', raw)
    if not json_match:
        raise ValueError(f"No JSON found in Claude response:\n{raw}")

    parsed = json.loads(json_match.group(1))
    if isinstance(parsed, dict):
        parsed = [parsed]

    # Filter out clips shorter than 30 seconds or longer than 90 seconds
    filtered = []
    for clip in parsed[:n]:
        try:
            start = parse_time_to_seconds(clip.get("start_time", "0:00"))
            end = parse_time_to_seconds(clip.get("end_time", "0:30"))
            duration = end - start
            if duration < 30:
                log(f"  Clip '{clip.get('title','?')[:40]}' too short ({duration:.0f}s < 30s). Skipping.")
                continue
            if duration > 90:
                log(f"  Clip '{clip.get('title','?')[:40]}' too long ({duration:.0f}s > 90s). Trimming end.")
                clip["end_time"] = format_seconds_to_time(start + 75)
            filtered.append(clip)
        except Exception:
            filtered.append(clip)

    return filtered[:n]


# ── Cut Verification ───────────────────────────────────────────────────────────

def verify_cut(client: anthropic.Anthropic, clip: dict, entries: list[dict]) -> dict:
    """Send a second prompt to verify the end cut is clean."""
    end_sec = parse_time_to_seconds(clip["end_time"])
    window_text = get_transcript_window(entries, end_sec, window=10.0)

    prompt = f"""You are verifying whether a short-form video clip ends at a clean, complete thought.

Proposed end time: {clip['end_time']}
Payoff sentence: "{clip.get('payoff_sentence', '')}"

Transcript around the proposed end time (±10 seconds):
{window_text}

Does the thought complete at {clip['end_time']}, or does it continue?
If it continues, provide the corrected end_time where the thought actually resolves.
The clip must end on a complete thought or reaction, never mid-sentence or mid-idea.

Return ONLY valid JSON:
{{
  "end_is_clean": true/false,
  "corrected_end_time": "MM:SS or same as proposed if clean",
  "reason": "one-sentence explanation"
}}"""

    log(f"Verifying cut at {clip['end_time']}...")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = message.content[0].text.strip()
    json_match = re.search(r'(\{[\s\S]+\})', raw)
    if not json_match:
        log(f"Warning: no JSON in cut verification response, keeping original end time")
        return clip

    verification = json.loads(json_match.group(1))
    if not verification.get("end_is_clean") and verification.get("corrected_end_time"):
        old_end = clip["end_time"]
        clip["end_time"] = verification["corrected_end_time"]
        log(f"  Cut corrected: {old_end} -> {clip['end_time']} ({verification.get('reason', '')})")
    else:
        log(f"  Cut is clean at {clip['end_time']}")

    return clip


# ── FFmpeg ─────────────────────────────────────────────────────────────────────

def cut_clip(video_path: str, start: str, end: str, output_path: str):
    """Cut a clip from video."""
    start_sec = parse_time_to_seconds(start)
    end_sec = parse_time_to_seconds(end)
    duration = end_sec - start_sec
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_sec),
        "-i", video_path,
        "-t", str(duration),
        "-c:v", "libx264", "-c:a", "aac",
        "-avoid_negative_ts", "make_zero",
        output_path,
    ]
    result = run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log(f"FFmpeg cut error: {result.stderr[-500:]}")
        raise RuntimeError("FFmpeg cut failed")


def crop_vertical(input_path: str, output_path: str):
    """Crop to 1080x1920 vertical with letterbox padding."""
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf", "scale=1080:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
        "-c:a", "aac",
        output_path,
    ]
    result = run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log(f"FFmpeg crop error: {result.stderr[-500:]}")
        raise RuntimeError("FFmpeg vertical crop failed")


def burn_captions(input_path: str, output_path: str):
    """Burn captions using an external burn-captions script (if available).

    Falls back to a simple copy if the script is not found.
    Provide your own burn-captions.py or integrate Whisper + FFmpeg subtitle burn.
    """
    script = WORKSPACE / "scripts" / "burn-captions.py"
    if script.exists():
        cmd = ["python3", str(script), input_path, output_path]
        result = run(cmd, capture_output=False)
        if result.returncode != 0:
            raise RuntimeError("burn-captions.py failed")
    else:
        # Fallback: copy without captions
        log("No burn-captions.py found, copying without caption burn")
        shutil.copy2(input_path, output_path)


# ── Channel Scanning ───────────────────────────────────────────────────────────

def get_current_week_range() -> tuple[datetime, datetime]:
    """Return (monday, sunday) of the current week."""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday.replace(hour=0, minute=0, second=0), sunday.replace(hour=23, minute=59, second=59)


def scan_channel(channel: str, processed: set) -> list[dict]:
    """Scan channel knowledge base directory for new videos from this week.

    Expects markdown files named YYYY-MM-DD-title.md with a `url:` field
    in YAML frontmatter pointing to a YouTube watch URL.
    """
    kb_dir = KB_BASE / channel
    if not kb_dir.exists():
        log(f"Channel KB dir not found: {kb_dir}")
        return []

    week_start, week_end = get_current_week_range()
    videos = []

    for md_file in sorted(kb_dir.glob("*.md")):
        name = md_file.stem
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', name)
        if not date_match:
            continue

        try:
            file_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
        except ValueError:
            continue

        if not (week_start <= file_date <= week_end):
            continue

        if "summary" in name.lower():
            continue

        content = md_file.read_text(encoding="utf-8", errors="replace")
        url_match = re.search(r'^url:\s*(https://www\.youtube\.com/watch\?v=\S+)', content, re.MULTILINE)
        if not url_match:
            url_match = re.search(r'(https://www\.youtube\.com/watch\?v=[\w-]+)', content)
        if not url_match:
            continue

        url = url_match.group(1).strip()
        if url in processed:
            log(f"Skipping already processed: {url}")
            continue

        title_match = re.search(r'^title:\s*"?(.+?)"?\s*$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else name

        videos.append({"url": url, "title": title, "date": file_date})
        log(f"Found new video: {title} ({url})")

    return videos


# ── Main Pipeline ──────────────────────────────────────────────────────────────

def process_video(url: str, client: anthropic.Anthropic, args, work_dir: str) -> list[dict]:
    """Process a single video. Returns list of clip result dicts."""
    results = []
    video_dir = tempfile.mkdtemp(dir=work_dir, prefix="video_")

    try:
        # Download
        video_path, vtt_path = download_video(url, video_dir)

        # Validate duration (10+ minutes)
        duration = get_video_duration(video_path)
        if duration < 600:
            log(f"Video too short ({duration:.0f}s < 600s). Skipping.")
            return []
        log(f"Video duration: {duration:.0f}s ({duration/60:.1f} min)")

        # Parse transcript
        entries = parse_vtt(vtt_path)
        if not entries:
            raise RuntimeError("No transcript entries found in VTT")

        transcript = transcript_to_text(entries)
        log(f"Transcript: {len(transcript)} chars, {len(entries)} entries")

        # Segment with Claude
        clips = call_claude_segmentation(client, transcript, n=args.max_clips)
        log(f"Got {len(clips)} clip suggestions")

        # Cut verification
        for i, clip in enumerate(clips):
            clips[i] = verify_cut(client, clip, entries)

        # Process each clip
        video_stem = Path(video_path).stem[:40].replace(" ", "_").replace("/", "-")

        for i, clip in enumerate(clips, 1):
            safe_title = re.sub(r'[^\w\s-]', '', clip.get('title', f'clip_{i}'))[:50].replace(' ', '_')
            clip_name = f"{safe_title}_clip{i}"

            log(f"\n--- Clip {i}: {clip.get('title', 'Untitled')} ---")
            log(f"  Start: {clip['start_time']} | End: {clip['end_time']}")

            raw_path = os.path.join(video_dir, f"{clip_name}_raw.mp4")
            vertical_path = os.path.join(video_dir, f"{clip_name}_vertical.mp4")
            output_dir = args.output_dir or os.path.join(work_dir, "output")
            os.makedirs(output_dir, exist_ok=True)
            final_path = os.path.join(output_dir, f"{clip_name}_final.mp4")

            try:
                # Cut
                cut_clip(video_path, clip["start_time"], clip["end_time"], raw_path)

                # Crop vertical
                crop_vertical(raw_path, vertical_path)

                # Burn captions
                burn_captions(vertical_path, final_path)

                duration_sec = parse_time_to_seconds(clip["end_time"]) - parse_time_to_seconds(clip["start_time"])
                results.append({
                    "title": clip.get("title", clip_name),
                    "start_time": clip["start_time"],
                    "end_time": clip["end_time"],
                    "duration_seconds": duration_sec,
                    "hook_sentence": clip.get("hook_sentence", ""),
                    "payoff_sentence": clip.get("payoff_sentence", ""),
                    "why": clip.get("why", ""),
                    "local_path": final_path,
                    "source_url": url,
                })
                log(f"  Done: {final_path}")

            except Exception as e:
                log(f"  Clip {i} failed: {e}")

    except Exception as e:
        log(f"Video processing failed: {e}")
        import traceback
        traceback.print_exc()

    return results


def main():
    parser = argparse.ArgumentParser(description="YouTube short-form clip pipeline")
    parser.add_argument("--url", help="Single YouTube URL to process")
    parser.add_argument("--channel", help="Channel slug to scan for new videos")
    parser.add_argument("--max-clips", type=int, default=2, help="Max clips per video")
    parser.add_argument("--output-dir", help="Local output directory for final clips")
    args = parser.parse_args()

    if not args.url and not args.channel:
        parser.error("Provide --url or --channel")

    client = get_anthropic_client()
    processed = load_processed()
    work_dir = tempfile.mkdtemp(prefix="/tmp/shortform_")
    all_results = []

    try:
        if args.url:
            urls = [{"url": args.url, "title": args.url}]
        else:
            urls = scan_channel(args.channel, processed)
            if not urls:
                log("No new videos found for this week.")
                return

        for video_info in urls:
            url = video_info["url"]
            log(f"\n{'='*60}")
            log(f"Processing: {video_info.get('title', url)}")
            log(f"URL: {url}")
            results = process_video(url, client, args, work_dir)
            all_results.extend(results)
            if results:
                processed.add(url)
                save_processed(processed)

        # Print summary
        print("\n" + "="*60)
        print(f"DONE — {len(all_results)} clip(s) produced")
        print("="*60)
        for r in all_results:
            dur = r["duration_seconds"]
            print(f"\n  {r['title']}")
            print(f"   Duration: {dur:.0f}s ({dur/60:.1f}m)")
            print(f"   Hook: {r['hook_sentence'][:100]}")
            print(f"   Payoff: {r['payoff_sentence'][:100]}")
            print(f"   Path: {r['local_path']}")

        # Write results JSON
        results_path = DATA_DIR / "last-run-shortform.json"
        results_path.parent.mkdir(parents=True, exist_ok=True)
        results_path.write_text(json.dumps(all_results, indent=2, default=str))
        log(f"Results written to {results_path}")

    finally:
        log(f"Work dir: {work_dir}")


if __name__ == "__main__":
    main()
