#!/usr/bin/env python3
"""
Editorial Brain — Top-down clip discovery using LLM analysis.

Instead of bottom-up keyword matching, this gives the full transcript to an LLM
and asks it to find the best clip-worthy moments like a human editor would.

Two-pass approach:
1. Sonnet scans transcript chunks cheaply, finds candidate moments
2. Sonnet scores candidates on hook/build/payoff/clean-cut (0-100)
3. Only 90+ clips get cut

Usage:
    python editorial-brain.py --url "https://youtube.com/watch?v=..." [--max-clips 5]
    python editorial-brain.py --vtt /path/to/file.vtt --video-id ID [--max-clips 5]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

# ── Configuration ──

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = Path(os.environ.get("CONTENT_OPS_DATA_DIR", PROJECT_DIR / "data"))
CLIPS_DIR = DATA_DIR / "clips"

# Model configuration
DEFAULT_MODEL = os.environ.get("EDITORIAL_BRAIN_MODEL", "claude-sonnet-5")


def call_claude(prompt, model=None, max_tokens=4000):
    """Call Claude API."""
    model = model or DEFAULT_MODEL
    data = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01"
        }
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())
        return result['content'][0]['text']


def download_vtt(url):
    """Download VTT subtitles from YouTube."""
    video_id = re.search(r'(?:v=|/)([a-zA-Z0-9_-]{11})', url).group(1)
    vtt_path = f"/tmp/editorial_{video_id}.en.vtt"

    if os.path.exists(vtt_path):
        return vtt_path, video_id

    subprocess.run([
        'yt-dlp', '--write-auto-subs', '--sub-lang', 'en', '--sub-format', 'vtt',
        '--skip-download', '--output', f'/tmp/editorial_{video_id}.%(ext)s', url
    ], capture_output=True, check=True)

    return vtt_path, video_id


def parse_vtt(vtt_path):
    """Parse YouTube auto-caption VTT into clean, deduplicated transcript.

    YouTube auto-captions use a scrolling format where each block contains
    the previous line + new text. We filter out repeat blocks (< 20ms duration)
    and strip overlapping prefixes to get clean text.
    """
    content = open(vtt_path).read()
    blocks = content.split('\n\n')
    segments = []
    prev_clean = ''

    for block in blocks:
        lines = block.strip().split('\n')
        if not lines:
            continue
        ts = re.match(r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})', lines[0])
        if not ts:
            continue

        p1 = ts.group(1).split(':')
        p2 = ts.group(2).split(':')
        s1 = int(p1[0]) * 3600 + int(p1[1]) * 60 + float(p1[2])
        s2 = int(p2[0]) * 3600 + int(p2[1]) * 60 + float(p2[2])

        if s2 - s1 < 0.02:
            continue

        raw_text = '\n'.join(lines[1:])
        clean = re.sub(r'<[^>]+>', '', raw_text).strip()
        clean = re.sub(r'\s+', ' ', clean)

        if not clean or clean == prev_clean:
            continue

        new_text = clean
        if prev_clean:
            for overlap_len in range(min(len(prev_clean), len(clean)), 0, -1):
                if clean[:overlap_len] == prev_clean[-overlap_len:]:
                    new_text = clean[overlap_len:].strip()
                    break

        if new_text:
            segments.append({'start': s1, 'end': s2, 'text': new_text})
        prev_clean = clean

    return segments


def build_readable_transcript(segments):
    """Build a human-readable transcript with timestamps every ~30s."""
    output = ''
    last_ts = -30
    for seg in segments:
        if seg['start'] - last_ts >= 30:
            m, s = divmod(int(seg['start']), 60)
            output += f'\n\n[{m}:{s:02d}] '
            last_ts = seg['start']
        output += seg['text'] + ' '
    return output


def chunk_transcript(transcript_text, chunk_size=12000):
    """Split transcript into chunks at timestamp boundaries."""
    chunks = []
    remaining = transcript_text

    while remaining:
        if len(remaining) <= chunk_size:
            chunks.append(remaining)
            break
        break_at = remaining.rfind('\n\n[', 0, chunk_size)
        if break_at < chunk_size * 0.3:
            break_at = chunk_size
        chunks.append(remaining[:break_at])
        remaining = remaining[break_at:]

    return chunks


def find_moments_full_transcript(full_transcript, video_title=""):
    """Analyze the ENTIRE transcript in one call."""
    prompt = f"""You are a legendary short-form video editor (think: the team behind Hormozi's clips, Chris Williamson's best moments).

Read this FULL transcript of "{video_title}" and find the 3-5 BEST moments that could become viral 30-60 second clips.

CRITICAL RULES:
- ONLY identify moments that ACTUALLY EXIST in the transcript below
- Quote the EXACT words from the transcript — do not paraphrase or invent
- Each moment must have a clear HOOK → BUILD → PAYOFF arc
- A stranger scrolling at 2am should stop, watch the whole clip, and feel smarter

What makes a 90+ clip:
- HOOK (0-3s): Pattern interrupt — shocking stat, bold claim, provocative question
- BUILD (3-30s): Stakes rise — story tension, framework develops, insight escalates
- PAYOFF (last 5-10s): The insight LANDS — counterintuitive truth, surprising number, emotional resolution
- CLEAN END: Cut immediately after the payoff. Silence > trailing off.

FULL TRANSCRIPT:
{full_transcript}

Return a JSON array of the best moments (3-5 max). For each:
{{
    "start_timestamp": "[M:SS] exact timestamp from transcript",
    "end_timestamp": "[M:SS] where to cut",
    "hook_quote": "EXACT opening words from transcript",
    "payoff_quote": "EXACT closing words/punchline from transcript",
    "why_viral": "One sentence on why this stops scrolls",
    "estimated_score": 0-100,
    "narrative_arc": "Hook: ... → Build: ... → Payoff: ..."
}}

Be EXTREMELY selective. If nothing scores above 70, return fewer moments or an empty array. Quality > quantity."""

    try:
        response = call_claude(prompt, max_tokens=3000)
        json_match = re.search(r'\[[\s\S]*\]', response)
        if json_match:
            moments = json.loads(json_match.group())
            for m in moments:
                m['hook'] = m.get('hook_quote', m.get('hook', ''))
                m['payoff'] = m.get('payoff_quote', m.get('payoff', ''))
                m['suggested_clip_text'] = m.get('narrative_arc', '')
            return moments
        return []
    except Exception as e:
        print(f"  ⚠️ Full transcript analysis failed: {e}")
        return []


def find_moments_in_chunk(chunk_text, chunk_idx, video_title=""):
    """Ask LLM to find clip-worthy moments in a transcript chunk."""
    prompt = f"""You are a legendary short-form video editor.

Analyze this transcript section from "{video_title}" and find ANY moments that could become a viral 30-60 second clip.

A great clip moment has:
- A clear HOOK (bold claim, shocking stat, provocative question, emotional statement)
- A STORY ARC or BUILD (tension rises, framework develops, stakes increase)
- A PAYOFF (insight lands, number drops, counterintuitive truth revealed, punchline hits)
- Works STANDALONE — a stranger with zero context would stop scrolling and watch

TRANSCRIPT SECTION:
{chunk_text}

Return a JSON array of moments found. If no moments qualify, return an empty array.
For each moment:
{{
    "start_timestamp": "[M:SS] from the transcript",
    "end_timestamp": "[M:SS] approximate end",
    "hook": "The opening line/moment that grabs attention",
    "payoff": "How this moment resolves/lands",
    "why_viral": "One sentence on why this would stop a scroll",
    "estimated_score": 0-100,
    "suggested_clip_text": "The key 2-3 sentences a viewer would remember"
}}

Be SELECTIVE. Most transcript sections have 0-1 clip-worthy moments. Only include moments you'd bet could score 70+."""

    try:
        response = call_claude(prompt, max_tokens=2000)
        json_match = re.search(r'\[[\s\S]*\]', response)
        if json_match:
            return json.loads(json_match.group())
        return []
    except Exception as e:
        print(f"  ⚠️ Chunk {chunk_idx} failed: {e}")
        return []


def score_and_refine_moment(moment, full_transcript_context, video_title=""):
    """Deep-score a candidate moment and suggest exact trim points."""
    prompt = f"""You are scoring a potential short-form clip from "{video_title}".

CANDIDATE MOMENT:
Hook: {moment.get('hook', 'N/A')}
Payoff: {moment.get('payoff', 'N/A')}
Why viral: {moment.get('why_viral', 'N/A')}
Key text: {moment.get('suggested_clip_text', 'N/A')}

SURROUNDING TRANSCRIPT (for context):
{full_transcript_context}

Score this clip candidate on a 0-100 scale:
- HOOK (0-25): Does the first sentence stop the scroll?
- BUILD (0-25): Does tension/interest rise through the middle?
- PAYOFF (0-25): Does the insight LAND? Would the viewer feel smarter/moved?
- CLEAN CUT (0-25): Can this end on a strong note without trailing off?

Also provide:
- Exact start quote (the first words of the clip)
- Exact end quote (the last words before cutting)
- Any adjustments to improve the score

Return JSON:
{{
    "total_score": 0-100,
    "hook_score": 0-25,
    "build_score": 0-25,
    "payoff_score": 0-25,
    "clean_cut_score": 0-25,
    "start_quote": "exact first words",
    "end_quote": "exact last words",
    "adjustments": "how to improve",
    "would_you_post_this": true/false,
    "reason": "one line summary"
}}"""

    try:
        response = call_claude(prompt, max_tokens=1500)
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            return json.loads(json_match.group())
        return {"total_score": 0, "reason": "Failed to parse"}
    except Exception as e:
        return {"total_score": 0, "reason": f"API error: {e}"}


def get_context_around_timestamp(segments, timestamp_str, context_seconds=180):
    """Get clean transcript text around a timestamp."""
    parts = timestamp_str.replace('[', '').replace(']', '').split(':')
    if len(parts) == 2:
        target_sec = int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        target_sec = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    else:
        target_sec = 0

    context = ''
    last_ts = -15
    for seg in segments:
        if target_sec - context_seconds <= seg['start'] <= target_sec + context_seconds:
            if seg['start'] - last_ts >= 15:
                m, s = divmod(int(seg['start']), 60)
                context += f'\n[{m}:{s:02d}] '
                last_ts = seg['start']
            context += seg['text'] + ' '

    return context[:5000]


def cut_clip(video_url, start_sec, duration_sec, output_path):
    """Download video and cut a clip using ffmpeg."""
    video_id = re.search(r'(?:v=|/)([a-zA-Z0-9_-]{11})', video_url).group(1)

    video_cache = f"/tmp/editorial_{video_id}.mp4"
    if not os.path.exists(video_cache):
        print(f"  ⬇️ Downloading video...")
        subprocess.run([
            'yt-dlp', '--format', 'best[height<=720]',
            '--output', video_cache, '--no-playlist', video_url
        ], capture_output=True, check=True)

    CLIPS_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [
        'ffmpeg', '-y',
        '-ss', str(start_sec),
        '-i', video_cache,
        '-t', str(duration_sec),
        '-vf', 'crop=ih*9/16:ih,scale=1080:1920',
        '-c:a', 'aac', '-b:a', '128k',
        output_path
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return os.path.exists(output_path)


def timestamp_to_seconds(ts_str):
    """Convert timestamp string like '14:31' to seconds."""
    parts = ts_str.replace('[', '').replace(']', '').strip().split(':')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0


def main():
    parser = argparse.ArgumentParser(description='Editorial Brain — LLM-powered clip discovery')
    parser.add_argument('--url', help='YouTube URL')
    parser.add_argument('--vtt', help='VTT file path')
    parser.add_argument('--video-id', help='Video ID (required with --vtt)')
    parser.add_argument('--title', default='', help='Video title')
    parser.add_argument('--max-clips', type=int, default=5, help='Max clips to produce')
    parser.add_argument('--min-score', type=int, default=90, help='Minimum score threshold')
    parser.add_argument('--skip-cut', action='store_true', help='Skip video cutting (analysis only)')
    parser.add_argument('--output', help='Output JSON path')

    args = parser.parse_args()

    if not ANTHROPIC_API_KEY:
        print("❌ Set ANTHROPIC_API_KEY environment variable")
        sys.exit(1)

    output_path = args.output or str(DATA_DIR / "editorial-clips-latest.json")

    # Step 1: Get transcript
    if args.url:
        print(f"📥 Downloading subtitles...")
        vtt_path, video_id = download_vtt(args.url)
    elif args.vtt:
        vtt_path = args.vtt
        video_id = args.video_id or 'unknown'
    else:
        parser.print_help()
        sys.exit(1)

    print(f"📝 Parsing transcript...")
    segments = parse_vtt(vtt_path)
    print(f"   {len(segments)} segments")

    readable = build_readable_transcript(segments)
    chunks = chunk_transcript(readable)
    print(f"   {len(chunks)} chunks for analysis")

    # Step 2: Scan for moments
    all_moments = []

    if len(readable) < 80000:
        print(f"\n🔍 Pass 1: Full-transcript analysis (single call, {len(readable)//1000}K chars)...")
        moments = find_moments_full_transcript(readable, args.title)
        all_moments = moments
        print(f"   Found {len(moments)} candidate(s)")
    else:
        print(f"\n🔍 Pass 1: Chunked analysis ({len(chunks)} chunks)...")
        for i, chunk in enumerate(chunks):
            moments = find_moments_in_chunk(chunk, i, args.title)
            if moments:
                print(f"   Chunk {i+1}/{len(chunks)}: Found {len(moments)} candidate(s)")
                for m in moments:
                    m['chunk_idx'] = i
                    all_moments.append(m)
            else:
                print(f"   Chunk {i+1}/{len(chunks)}: No moments")

    print(f"\n📊 Pass 1 complete: {len(all_moments)} total candidates")

    if not all_moments:
        print("❌ No clip-worthy moments found in this episode")
        sys.exit(0)

    all_moments.sort(key=lambda x: x.get('estimated_score', 0), reverse=True)
    top_candidates = all_moments[:min(10, len(all_moments))]

    for m in top_candidates:
        print(f"   [{m.get('start_timestamp', '?')}] Score ~{m.get('estimated_score', '?')}: {m.get('hook', '?')[:60]}")

    # Step 3: Deep-score candidates (Pass 2)
    print(f"\n🎯 Pass 2: Deep-scoring top {len(top_candidates)} candidates...")
    scored = []
    for i, moment in enumerate(top_candidates):
        ts = moment.get('start_timestamp', '0:00')
        context = get_context_around_timestamp(segments, ts)
        score = score_and_refine_moment(moment, context, args.title)
        moment['deep_score'] = score
        total = score.get('total_score', 0)
        scored.append(moment)

        status = "✅" if total >= args.min_score else "❌"
        print(f"   {status} [{ts}] Score: {total}/100 — {score.get('reason', '?')[:80]}")

    passed = [m for m in scored if m.get('deep_score', {}).get('total_score', 0) >= args.min_score]
    print(f"\n🏆 {len(passed)} clips scored {args.min_score}+")

    # Step 4: Cut clips
    results = {
        'video_id': video_id,
        'title': args.title,
        'url': args.url or '',
        'total_candidates': len(all_moments),
        'scored': len(scored),
        'passed': len(passed),
        'threshold': args.min_score,
        'clips': []
    }

    if passed and not args.skip_cut and args.url:
        print(f"\n✂️ Cutting {len(passed)} clips...")
        for i, moment in enumerate(passed[:args.max_clips]):
            start_sec = timestamp_to_seconds(moment.get('start_timestamp', '0:00'))
            end_sec = timestamp_to_seconds(moment.get('end_timestamp', '0:00'))
            duration = max(30, min(60, end_sec - start_sec)) if end_sec > start_sec else 45

            clip_id = f"{video_id}_editorial_{i+1}"
            clip_output = str(CLIPS_DIR / f"{clip_id}.mp4")

            try:
                cut_clip(args.url, start_sec, duration, clip_output)
                print(f"   ✅ {clip_id}.mp4 ({duration}s)")
                results['clips'].append({
                    'id': clip_id,
                    'path': clip_output,
                    'start': start_sec,
                    'duration': duration,
                    'score': moment['deep_score'],
                    'hook': moment.get('hook', ''),
                    'payoff': moment.get('payoff', ''),
                })
            except Exception as e:
                print(f"   ❌ Cut failed: {e}")

    results['all_scored'] = [{
        'timestamp': m.get('start_timestamp', '?'),
        'score': m.get('deep_score', {}).get('total_score', 0),
        'hook': m.get('hook', ''),
        'payoff': m.get('payoff', ''),
        'reason': m.get('deep_score', {}).get('reason', ''),
        'adjustments': m.get('deep_score', {}).get('adjustments', ''),
    } for m in scored]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Saved to {output_path}")

    return 0 if passed else 1


if __name__ == '__main__':
    sys.exit(main())
