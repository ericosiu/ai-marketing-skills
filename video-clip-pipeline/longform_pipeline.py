#!/usr/bin/env python3
"""
longform_pipeline.py — End-to-end long-form clip pipeline
Segments long YouTube videos into 5-15 minute highlight clips for YouTube.

Usage:
  python3 longform_pipeline.py --url URL [--max-clips 3]
  python3 longform_pipeline.py --channel my-podcast [--max-clips 3]
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

# ── Paths (configure these for your setup) ─────────────────────────────────────
WORKSPACE = Path(os.environ.get("PIPELINE_WORKSPACE", Path.cwd()))
DATA_DIR = WORKSPACE / "data" / "youtube-clips"
PROCESSED_FILE = DATA_DIR / "processed-longform.json"
KB_BASE = WORKSPACE / "knowledge_base" / "youtube"

LONGFORM_SEGMENTATION_PROMPT = """You are a YouTube video editor specializing in extracting high-value highlight clips from long-form content.

You will be given a transcript of a long-form YouTube video with timestamps.

Your job: Find {n} self-contained segments of 5-15 minutes each that would work as standalone YouTube videos.

## Rules for Segment Selection

### Structure
- Each segment must have a CLEAR NARRATIVE ARC: setup → development → resolution
- The segment must open with a STRONG HOOK that gives viewers immediate context
- The segment must end NATURALLY — at a conclusion, insight landing, or story resolution
- Never end mid-topic or mid-story

### Content criteria (pick the best)
1. A complete story or case study with a clear result
2. A step-by-step tutorial or walkthrough
3. A debate, discussion, or analysis that reaches a conclusion
4. A "how we did X and got Y result" narrative
5. A contrarian take with supporting evidence and a conclusion

### Length
- Minimum: 5 minutes (300 seconds)
- Maximum: 15 minutes (900 seconds)
- Sweet spot: 7-12 minutes

### What to avoid
- Starting in the middle of a thought
- Ending with a question or cliffhanger (viewers came for answers)
- Topics that require external context from earlier in the video

## Output Format

Return ONLY valid JSON array. No markdown, no commentary.

[
  {{
    "title": "descriptive YouTube-style title (under 70 chars)",
    "start_time": "MM:SS",
    "end_time": "MM:SS",
    "hook_sentence": "exact words from transcript that open the segment — must immediately establish context",
    "payoff_sentence": "exact words from transcript where the key insight/resolution lands",
    "narrative_arc": "1-2 sentences describing setup → development → resolution",
    "why": "2-3 sentences on why this works as a standalone YouTube video"
  }}
]

## Important

- `hook_sentence` and `payoff_sentence` must be verbatim from the transcript
- Each segment must be fully self-contained — someone who hasn't seen the full video should understand and benefit
- Find exactly {n} segments
- Spread across the video — don't cluster at the beginning

## Transcript

{TRANSCRIPT}"""


# ── Helpers ─────────────────────────────────────────────────────────────────────

def log(msg: str):
    print(f"[longform] {msg}", flush=True)


def run(cmd: list, **kwargs) -> subprocess.CompletedProcess:
    log(f"$ {' '.join(str(c) for c in cmd)}")
    return subprocess.run(cmd, **kwargs)


def get_anthropic_client() -> anthropic.Anthropic:
    """Get Anthropic client from environment variable."""
    key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_KEY")
    if not key:
        raise RuntimeError(
            "No ANTHROPIC_API_KEY found. Set the environment variable:\n"
            "  export ANTHROPIC_API_KEY='sk-ant-...'"
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
    parts = t.strip().split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    return float(t)


def seconds_to_mmss(s: float) -> str:
    m = int(s) // 60
    sec = int(s) % 60
    return f"{m:02d}:{sec:02d}"


def get_video_duration(video_path: str) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", video_path],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def parse_vtt(vtt_path: str) -> list[dict]:
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


def download_video(url: str, out_dir: str) -> tuple[str, str]:
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


def call_claude_segmentation(client: anthropic.Anthropic, transcript: str, n: int = 3) -> list[dict]:
    prompt = LONGFORM_SEGMENTATION_PROMPT.format(n=n, TRANSCRIPT=transcript)
    log(f"Calling Claude for long-form segmentation ({n} clips)...")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = message.content[0].text.strip()
    json_match = re.search(r'(\[[\s\S]+\])', raw)
    if not json_match:
        json_match = re.search(r'(\{[\s\S]+\})', raw)
        if not json_match:
            raise ValueError(f"No JSON found in Claude response:\n{raw[:500]}")
        parsed = [json.loads(json_match.group(1))]
    else:
        parsed = json.loads(json_match.group(1))
    if isinstance(parsed, dict):
        parsed = [parsed]
    return parsed[:n]


def verify_cut(client: anthropic.Anthropic, clip: dict, entries: list[dict]) -> dict:
    end_sec = parse_time_to_seconds(clip["end_time"])
    window_text = get_transcript_window(entries, end_sec, window=10.0)

    prompt = f"""You are verifying whether a long-form YouTube clip ends at a clean, complete point.

Proposed end time: {clip['end_time']}
Expected payoff: "{clip.get('payoff_sentence', '')}"

Transcript around the proposed end time (±10 seconds):
{window_text}

Does the thought/narrative complete at {clip['end_time']}, or does it continue?
If it continues, provide the corrected end_time where the thought actually resolves.
The clip must end on a complete thought, insight, or story beat — never mid-sentence or mid-idea.

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
        log("Warning: no JSON in verification, keeping original")
        return clip
    verification = json.loads(json_match.group(1))
    if not verification.get("end_is_clean") and verification.get("corrected_end_time"):
        old_end = clip["end_time"]
        clip["end_time"] = verification["corrected_end_time"]
        log(f"  ✂️  Cut corrected: {old_end} → {clip['end_time']} ({verification.get('reason', '')})")
    else:
        log(f"  ✅ Cut is clean at {clip['end_time']}")
    return clip


def cut_clip_landscape(video_path: str, start: str, end: str, output_path: str):
    """Cut a clip, keeping 16:9 landscape. No crop or caption burn."""
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
        log(f"FFmpeg error: {result.stderr[-500:]}")
        raise RuntimeError("FFmpeg cut failed")


def scan_channel(channel: str, processed: set) -> list[dict]:
    """Scan a channel knowledge base directory for new videos to process."""
    kb_dir = KB_BASE / channel
    if not kb_dir.exists():
        log(f"Channel KB dir not found: {kb_dir}")
        return []

    today = datetime.now()
    week_start = (today - timedelta(days=today.weekday())).replace(hour=0, minute=0, second=0)
    week_end = (week_start + timedelta(days=6)).replace(hour=23, minute=59, second=59)
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


def process_video(url: str, client: anthropic.Anthropic, args, work_dir: str) -> list[dict]:
    results = []
    video_dir = tempfile.mkdtemp(dir=work_dir, prefix="video_")

    try:
        video_path, vtt_path = download_video(url, video_dir)

        duration = get_video_duration(video_path)
        if duration < 600:
            log(f"Video too short ({duration:.0f}s < 600s). Skipping.")
            return []
        log(f"Video duration: {duration:.0f}s ({duration/60:.1f} min)")

        entries = parse_vtt(vtt_path)
        if not entries:
            raise RuntimeError("No transcript entries found in VTT")

        transcript = transcript_to_text(entries)
        log(f"Transcript: {len(transcript)} chars, {len(entries)} entries")

        clips = call_claude_segmentation(client, transcript, n=args.max_clips)
        log(f"Got {len(clips)} clip suggestions")

        for clip in clips:
            clip = verify_cut(client, clip, entries)

        video_stem = Path(video_path).stem[:40].replace(" ", "_").replace("/", "-")
        output_dir = args.output_dir or os.path.join(work_dir, "output")
        os.makedirs(output_dir, exist_ok=True)

        for i, clip in enumerate(clips, 1):
            safe_title = re.sub(r'[^\w\s-]', '', clip.get('title', f'clip{i}'))[:50].replace(' ', '_')
            clip_name = f"{safe_title}_clip{i}"

            log(f"\n--- Clip {i}: {clip.get('title', 'Untitled')} ---")
            log(f"  Start: {clip['start_time']} | End: {clip['end_time']}")

            start_sec = parse_time_to_seconds(clip["start_time"])
            end_sec = parse_time_to_seconds(clip["end_time"])
            seg_dur = end_sec - start_sec
            if seg_dur < 60:
                log(f"  ⚠️  Clip too short ({seg_dur:.0f}s), skipping")
                continue
            if seg_dur > 1200:
                log(f"  ⚠️  Clip very long ({seg_dur:.0f}s), but proceeding")

            final_path = os.path.join(output_dir, f"{clip_name}_landscape.mp4")

            try:
                cut_clip_landscape(video_path, clip["start_time"], clip["end_time"], final_path)

                results.append({
                    "title": clip.get("title", clip_name),
                    "start_time": clip["start_time"],
                    "end_time": clip["end_time"],
                    "duration_seconds": seg_dur,
                    "hook_sentence": clip.get("hook_sentence", ""),
                    "payoff_sentence": clip.get("payoff_sentence", ""),
                    "narrative_arc": clip.get("narrative_arc", ""),
                    "why": clip.get("why", ""),
                    "local_path": final_path,
                    "source_url": url,
                })
                log(f"  ✅ Clip {i} done: {final_path}")

            except Exception as e:
                log(f"  ❌ Clip {i} failed: {e}")

    except Exception as e:
        log(f"Video processing failed: {e}")
        import traceback
        traceback.print_exc()

    return results


def main():
    parser = argparse.ArgumentParser(description="YouTube long-form clip pipeline")
    parser.add_argument("--url", help="Single YouTube URL to process")
    parser.add_argument("--channel", help="Channel name in knowledge base directory")
    parser.add_argument("--max-clips", type=int, default=3, help="Max clips per episode (default: 3)")
    parser.add_argument("--output-dir", help="Output directory for clips")
    args = parser.parse_args()

    if not args.url and not args.channel:
        parser.error("Provide --url or --channel")

    client = get_anthropic_client()
    processed = load_processed()
    work_dir = tempfile.mkdtemp(prefix="/tmp/longform_")
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
            results = process_video(url, client, args, work_dir)
            all_results.extend(results)
            if results:
                processed.add(url)
                save_processed(processed)

        print("\n" + "="*60)
        print(f"DONE — {len(all_results)} long-form clip(s) produced")
        print("="*60)
        for r in all_results:
            dur = r["duration_seconds"]
            print(f"\n🎬 {r['title']}")
            print(f"   Duration: {dur:.0f}s ({dur/60:.1f}m)")
            print(f"   Arc: {r.get('narrative_arc', '')[:150]}")
            print(f"   Hook: {r['hook_sentence'][:100]}")
            print(f"   Path: {r['local_path']}")

        results_path = DATA_DIR / "last-run-longform.json"
        results_path.parent.mkdir(parents=True, exist_ok=True)
        results_path.write_text(json.dumps(all_results, indent=2, default=str))
        log(f"Results written to {results_path}")

    finally:
        log(f"Work dir: {work_dir}")


if __name__ == "__main__":
    main()
