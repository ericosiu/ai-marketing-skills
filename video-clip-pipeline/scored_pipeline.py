#!/usr/bin/env python3
"""
Scored Video Clipper Pipeline — Score First, Cut Winners Only

Pipeline:
1. Download video + transcribe (Whisper)
2. Extract candidate transcript segments
3. Score ALL candidates with 10-expert LLM panel
4. Only cut segments scoring above threshold into final video clips

Usage:
    python3 scored_pipeline.py --url URL [--dry-run] [--min-score 90]
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import re
from pathlib import Path
from datetime import datetime
import anthropic


SCORE_PROMPT = """You are a panel of 10 experts evaluating whether a video clip segment is worth publishing as a standalone YouTube clip.

Video title: {video_title}

Evaluate this transcript segment:
---
{segment_text}
---

Score this segment on these 10 dimensions (each 1-10):

1. **Hook Strength** — Does the opening grab attention in the first 10 seconds?
2. **Insight Density** — How much value per minute?
3. **Standalone Clarity** — Can a new viewer understand without context?
4. **Emotional Resonance** — Does it trigger curiosity, surprise, or motivation?
5. **Actionability** — Can the viewer do something with this?
6. **Story Arc** — Does it have a clear beginning, middle, end?
7. **Quotability** — Are there shareable one-liners?
8. **Title Potential** — Can you write a compelling YouTube title for this?
9. **Rewatchability** — Would someone watch this twice or share it?
10. **Platform Fit** — Would this perform on YouTube as a standalone clip?

Return ONLY valid JSON:
{{
  "panel": {{
    "hook_strength": N,
    "insight_density": N,
    "standalone_clarity": N,
    "emotional_resonance": N,
    "actionability": N,
    "story_arc": N,
    "quotability": N,
    "title_potential": N,
    "rewatchability": N,
    "platform_fit": N
  }},
  "total": N,
  "reason": "1-2 sentence verdict",
  "suggested_title": "YouTube title if this is worth publishing",
  "kill_shot": "If score < 80, what specific weakness kills it?"
}}

Total = sum of all 10 scores (max 100).
Be ruthless. Most segments are mediocre. A 90+ should genuinely surprise and delight viewers."""


def get_anthropic_client():
    key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_KEY")
    if not key:
        print("Error: Set ANTHROPIC_API_KEY environment variable")
        sys.exit(1)
    return anthropic.Anthropic(api_key=key)


def run_cmd(cmd, desc, check=True):
    print(f"\n🚀 {desc}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        if result.stdout:
            print(result.stdout[-2000:])
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {desc} failed: {(e.stderr or '')[-500:]}")
        raise


def transcribe_video(video_path, tmpdir):
    """Transcribe video with Whisper, return segments and words."""
    audio_path = os.path.join(tmpdir, "audio.wav")
    transcript_path = os.path.join(tmpdir, "transcript.json")

    run_cmd(f'ffmpeg -y -i "{video_path}" -vn -acodec pcm_s16le -ar 16000 -ac 1 "{audio_path}"',
            "Extracting audio")

    print("\n🎙️  Transcribing with Whisper...")
    whisper_script = f"""
import whisper, json
model = whisper.load_model("medium")
result = model.transcribe("{audio_path}", word_timestamps=True, language="en", verbose=False)
words = []
for seg in result.get("segments", []):
    for w in seg.get("words", []):
        words.append({{"word": w["word"].strip(), "start": round(w["start"], 3), "end": round(w["end"], 3)}})
segments = [{{"start": s["start"], "end": s["end"], "text": s["text"].strip()}} for s in result.get("segments", [])]
json.dump({{"words": words, "segments": segments}}, open("{transcript_path}", "w"), indent=2)
print(f"✅ {{len(words)}} words, {{len(segments)}} segments")
"""
    result = subprocess.run(['python3', '-c', whisper_script], capture_output=True, text=True)
    print(result.stdout)

    if result.returncode != 0 or not os.path.exists(transcript_path):
        print(f"⚠️ Whisper failed: {result.stderr[-500:]}")
        return None, None

    data = json.load(open(transcript_path))
    return data['segments'], data.get('words', [])


def find_candidate_segments(segments, min_duration=60, max_duration=900):
    """Find candidate segments from transcript using basic heuristics."""
    candidates = []
    current_segment = None

    for seg in segments:
        text = seg['text'].strip()
        if not text:
            continue

        # Start a new candidate on topic shifts (questions, transitions)
        is_topic_start = any(marker in text.lower() for marker in [
            "so let me", "the first thing", "here's what", "one of the",
            "the biggest", "let me tell you", "the question is",
            "what i've learned", "here's the thing", "the reason",
            "let's talk about", "the mistake", "what most people",
        ])

        if is_topic_start or current_segment is None:
            if current_segment:
                duration = current_segment['end_time'] - current_segment['start_time']
                if min_duration <= duration <= max_duration:
                    candidates.append(current_segment)
            current_segment = {
                'start_time': seg['start'],
                'end_time': seg['end'],
                'text': text,
            }
        else:
            current_segment['end_time'] = seg['end']
            current_segment['text'] += ' ' + text

    # Don't forget the last segment
    if current_segment:
        duration = current_segment['end_time'] - current_segment['start_time']
        if min_duration <= duration <= max_duration:
            candidates.append(current_segment)

    return candidates


def score_segment(client, segment_text, video_title):
    """Score a single segment with the expert panel."""
    prompt = SCORE_PROMPT.format(video_title=video_title, segment_text=segment_text[:3000])

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        json_match = re.search(r'\{[\s\S]+\}', raw)
        if json_match:
            return json.loads(json_match.group(0))
    except Exception as e:
        print(f"  ⚠️ Scoring failed: {e}")

    return {"total": 0, "reason": "Scoring failed"}


def cut_clip(video_path, start_time, end_time, output_path):
    """Cut a clip using FFmpeg with re-encoding for accuracy."""
    duration = end_time - start_time
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_time),
        "-i", video_path,
        "-t", str(duration),
        "-c:v", "libx264", "-c:a", "aac",
        "-avoid_negative_ts", "make_zero",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description='Scored Video Clipper Pipeline')
    parser.add_argument('--url', required=True, help='YouTube URL')
    parser.add_argument('--dry-run', action='store_true', help='Score only, do not cut clips')
    parser.add_argument('--min-score', type=int, default=90, help='Minimum LLM score (default: 90)')
    parser.add_argument('--output-dir', default='clips', help='Output directory for clips')
    args = parser.parse_args()

    print("🎬 Scored Video Clipper Pipeline — Score First, Cut Winners")
    print(f"   URL: {args.url}")
    print(f"   Min score: {args.min_score}")

    # Extract video ID
    m = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)', args.url)
    if not m:
        print("❌ Invalid YouTube URL")
        sys.exit(1)
    video_id = m.group(1)

    client = get_anthropic_client()

    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = os.path.join(tmpdir, f"{video_id}.mp4")

        # Step 1: Download
        run_cmd(f'yt-dlp --format "best[height<=1080]" --output "{video_path}" --no-playlist "{args.url}"',
                "Downloading video")

        # Step 2: Transcribe
        segments, words = transcribe_video(video_path, tmpdir)
        if not segments:
            print("❌ No transcript available")
            sys.exit(1)
        print(f"📝 Transcript: {len(segments)} segments, {len(words)} words")

        # Step 3: Get video title
        title_result = subprocess.run(
            f'yt-dlp --get-title "{args.url}"', shell=True, capture_output=True, text=True)
        video_title = title_result.stdout.strip() if title_result.returncode == 0 else video_id

        # Step 4: Find candidates
        print("\n🔍 Finding candidate segments...")
        candidates = find_candidate_segments(segments)
        print(f"   Found {len(candidates)} candidate segments")

        if not candidates:
            print("❌ No candidate segments found")
            sys.exit(1)

        # Step 5: Score each candidate
        print(f"\n🤖 Scoring {len(candidates)} candidates with expert panel...")
        for i, seg in enumerate(candidates):
            score = score_segment(client, seg['text'], video_title)
            seg['score'] = score
            total = score.get('total', 0)
            status = "✅" if total >= args.min_score else "❌"
            mins = int(seg['start_time']) // 60
            secs = int(seg['start_time']) % 60
            print(f"   {status} #{i+1} [{mins}:{secs:02d}] Score: {total}/100 — {score.get('reason', 'N/A')[:80]}")

        # Filter winners
        winners = [s for s in candidates if s.get('score', {}).get('total', 0) >= args.min_score]
        all_scores = [s.get('score', {}).get('total', 0) for s in candidates]
        best_score = max(all_scores) if all_scores else 0

        # Save scores
        score_data = {
            'video_id': video_id,
            'video_title': video_title,
            'url': args.url,
            'scored_at': datetime.now().isoformat(),
            'total_candidates': len(candidates),
            'winners': len(winners),
            'min_score': args.min_score,
            'best_score': best_score,
            'scores': [{'index': i+1, **s.get('score', {})} for i, s in enumerate(candidates)],
        }
        os.makedirs('data', exist_ok=True)
        with open('data/clip-scores-latest.json', 'w') as f:
            json.dump(score_data, f, indent=2)

        if not winners:
            print(f"\n⚠️  No clips scored {args.min_score}+. Best: {best_score}/100")
            sys.exit(0)

        if args.dry_run:
            print(f"\n🏁 Dry run — {len(winners)} clips would be cut (scored {args.min_score}+)")
            for w in winners:
                s = w.get('score', {})
                print(f"   🎬 {s.get('suggested_title', 'Untitled')} — {s.get('total', 0)}/100")
            sys.exit(0)

        # Step 6: Cut winners
        print(f"\n🎬 Cutting {len(winners)} winning clips...")
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        clips_created = []
        for i, seg in enumerate(winners, 1):
            score = seg.get('score', {})
            title = score.get('suggested_title', f'clip_{i}')
            safe_title = re.sub(r'[^\w\s-]', '', title)[:50].replace(' ', '_')
            output_path = str(output_dir / f"{safe_title}_clip{i}.mp4")

            success = cut_clip(video_path, seg['start_time'], seg['end_time'], output_path)
            if success:
                clips_created.append({
                    'title': title,
                    'start_time': seg['start_time'],
                    'end_time': seg['end_time'],
                    'duration': seg['end_time'] - seg['start_time'],
                    'score': score.get('total', 0),
                    'path': output_path,
                })
                print(f"   ✅ {title} ({score.get('total', 0)}/100)")
            else:
                print(f"   ❌ Failed to cut: {title}")

        print(f"\n✅ Pipeline complete! Created {len(clips_created)} clips in {args.output_dir}/")


if __name__ == '__main__':
    main()
