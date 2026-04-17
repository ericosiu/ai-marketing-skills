#!/usr/bin/env python3
"""
Clip Segmenter - Find the best clip-worthy segments from Whisper transcripts
Uses Claude API to analyze transcripts and identify standalone clips.

Usage:
    python3 clip_segmenter.py --transcript path/to/transcript.json --output path/to/segments.json
    python3 clip_segmenter.py --transcript-dir transcripts/ --output-dir segments/
"""

import argparse
import json
import os
import sys
from pathlib import Path
import anthropic
import re
from datetime import datetime


def load_transcript(json_file):
    """Load Whisper JSON transcript"""
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data


def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def create_full_transcript_text(whisper_data):
    """Create a readable transcript with timestamps for Claude"""
    segments = whisper_data.get('segments', [])

    transcript_lines = []
    for segment in segments:
        start = segment['start']
        text = segment['text'].strip()
        timestamp = format_timestamp(start)
        transcript_lines.append(f"[{timestamp}] {text}")

    return '\n'.join(transcript_lines)


def analyze_with_claude(transcript_text, episode_title, anthropic_client,
                        model="claude-haiku-4-5-20250514", max_segments=5, min_hook_strength=6):
    """Send transcript to Claude for segment analysis"""

    prompt = f"""You are analyzing a podcast transcript to identify the best clip-worthy segments.

Episode: {episode_title}

TRANSCRIPT:
{transcript_text}

Please identify {max_segments} standalone segments that would work as viral clips. Each segment should:
- Be 3-15 minutes long
- Have a clear hook/opening that grabs attention
- Contain a complete thought, story, or framework
- Feel satisfying as a standalone watch
- Have viral potential (contrarian takes, practical advice, compelling stories)

For each segment, provide:
- start_time: timestamp in seconds (not HH:MM:SS)
- end_time: timestamp in seconds
- suggested_title: Catchy, clickbait-worthy title (50 chars max)
- one_line_description: What the clip is about
- hook_strength: 1-10 rating for how compelling the opening is (only include if >= {min_hook_strength})
- key_topics: 2-3 main topics covered

Return ONLY a valid JSON array like this:
[
    {{
        "start_time": 65,
        "end_time": 420,
        "suggested_title": "Why 99% of Founders Fail at AI",
        "one_line_description": "A breakdown of the critical mistake most entrepreneurs make when implementing AI",
        "hook_strength": 9,
        "key_topics": ["AI implementation", "founder mistakes", "business strategy"]
    }}
]

Focus on segments with strong hooks, practical advice, and contrarian or surprising insights."""

    try:
        response = anthropic_client.messages.create(
            model=model,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text.strip()

        # Try to extract JSON from response
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            segments = json.loads(json_str)
            return segments
        else:
            print(f"Warning: No JSON found in Claude response for {episode_title}")
            print("Response:", response_text[:200])
            return []

    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return []


def process_single(transcript_file, output_file, episode_title, client,
                    model="claude-haiku-4-5-20250514", max_segments=5, min_hook_strength=6):
    """Process a single transcript file."""
    print(f"\nProcessing: {transcript_file}")

    whisper_data = load_transcript(transcript_file)
    if not episode_title:
        episode_title = Path(transcript_file).stem

    transcript_text = create_full_transcript_text(whisper_data)
    print(f"Transcript length: {len(transcript_text)} chars")

    segments = analyze_with_claude(
        transcript_text, episode_title, client,
        model=model, max_segments=max_segments, min_hook_strength=min_hook_strength
    )
    print(f"Found {len(segments)} segments")

    # Add metadata
    for segment in segments:
        segment['episode_file'] = Path(transcript_file).stem
        segment['video_file'] = Path(transcript_file).stem + '.mp4'

    # Save segments
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(segments, f, indent=2)

    print(f"Saved to: {output_path}")

    # Print summary
    for i, seg in enumerate(segments, 1):
        duration = seg['end_time'] - seg['start_time']
        print(f"  {i}. {seg['suggested_title']} ({duration:.0f}s, hook: {seg['hook_strength']}/10)")

    return segments


def main():
    parser = argparse.ArgumentParser(description="Find clip-worthy segments from Whisper transcripts")
    parser.add_argument("--transcript", help="Path to a single Whisper JSON transcript")
    parser.add_argument("--transcript-dir", help="Directory of Whisper JSON transcripts")
    parser.add_argument("--output", help="Output path for segment JSON (single file mode)")
    parser.add_argument("--output-dir", help="Output directory for segment JSONs (batch mode)")
    parser.add_argument("--episode-title", help="Episode title (optional)")
    parser.add_argument("--model", default="claude-haiku-4-5-20250514", help="Claude model to use")
    parser.add_argument("--max-segments", type=int, default=5, help="Max clips per episode (default: 5)")
    parser.add_argument("--min-hook-strength", type=int, default=6, help="Min hook score to include (default: 6)")
    args = parser.parse_args()

    if not args.transcript and not args.transcript_dir:
        parser.error("Provide --transcript or --transcript-dir")

    # Get Anthropic client
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_KEY")
    if not api_key:
        print("Error: Set ANTHROPIC_API_KEY environment variable")
        sys.exit(1)
    client = anthropic.Anthropic(api_key=api_key)

    if args.transcript:
        # Single file mode
        output = args.output or str(Path(args.transcript).parent / f"{Path(args.transcript).stem}_segments.json")
        process_single(
            args.transcript, output, args.episode_title, client,
            model=args.model, max_segments=args.max_segments, min_hook_strength=args.min_hook_strength
        )
    else:
        # Batch mode
        transcript_dir = Path(args.transcript_dir)
        output_dir = Path(args.output_dir or "segments")
        output_dir.mkdir(parents=True, exist_ok=True)

        transcript_files = list(transcript_dir.glob("*.json"))
        print(f"Found {len(transcript_files)} transcripts to process")

        all_segments = []
        for transcript_file in transcript_files:
            output_file = output_dir / f"{transcript_file.stem}_segments.json"
            segments = process_single(
                str(transcript_file), str(output_file), None, client,
                model=args.model, max_segments=args.max_segments, min_hook_strength=args.min_hook_strength
            )
            all_segments.extend(segments)

        # Save combined segments
        combined_file = output_dir / "all_segments.json"
        with open(combined_file, 'w') as f:
            json.dump(all_segments, f, indent=2)

        print(f"\n✅ Segmentation complete!")
        print(f"Total segments found: {len(all_segments)}")
        print(f"Combined segments saved to: {combined_file}")

        # Show top segments by hook strength
        top_segments = sorted(all_segments, key=lambda x: x.get('hook_strength', 0), reverse=True)[:5]
        print("\n🔥 Top 5 segments by hook strength:")
        for i, seg in enumerate(top_segments, 1):
            duration = seg['end_time'] - seg['start_time']
            print(f"{i}. {seg['suggested_title']} (hook: {seg['hook_strength']}/10, {duration:.0f}s)")
            print(f"   Episode: {seg['episode_file']}")


if __name__ == "__main__":
    main()
