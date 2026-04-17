#!/usr/bin/env python3
"""
Clip Cutter - Cut video clips from segments identified by the AI segmenter.
Uses FFmpeg stream copy for speed (under 5 seconds per clip, zero quality loss).

Usage:
    python3 clip_cutter.py --source video.mp4 --segments segments.json --output-dir clips/
    python3 clip_cutter.py --source-dir downloads/ --segments-dir segments/ --output-dir clips/
"""

import argparse
import json
import os
import subprocess
import re
from pathlib import Path
from datetime import datetime


def slugify(text):
    """Convert text to URL-friendly slug"""
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


def seconds_to_timestamp(seconds):
    """Convert seconds to HH:MM:SS.mmm format for FFmpeg"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"


def cut_clip(source_video, start_time, end_time, output_path, reencode=False):
    """Use FFmpeg to cut a clip from source video.

    Args:
        source_video: Path to source MP4
        start_time: Start time in seconds
        end_time: End time in seconds
        output_path: Path for output clip
        reencode: If True, re-encode for frame-accurate cuts (slower but precise)
    """
    start_ts = seconds_to_timestamp(start_time)
    end_ts = seconds_to_timestamp(end_time)

    if reencode:
        # Frame-accurate but slower
        cmd = [
            'ffmpeg', '-y',
            '-ss', start_ts,
            '-i', str(source_video),
            '-to', seconds_to_timestamp(end_time - start_time),
            '-c:v', 'libx264', '-c:a', 'aac',
            '-avoid_negative_ts', 'make_zero',
            str(output_path)
        ]
    else:
        # Stream copy — instant, zero quality loss, but keyframe-aligned (±1-2 sec)
        cmd = [
            'ffmpeg', '-y',
            '-ss', start_ts,
            '-to', end_ts,
            '-i', str(source_video),
            '-c', 'copy',
            '-avoid_negative_ts', 'make_zero',
            str(output_path)
        ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, ""
    except subprocess.CalledProcessError as e:
        return False, f"FFmpeg error: {e.stderr}"


def get_episode_title_slug(filename):
    """Extract a clean title slug from the video filename"""
    name = filename.replace('.mp4', '')
    parts = name.split('_', 1)
    if len(parts) > 1:
        title = parts[1]
    else:
        title = name
    return slugify(title)


def main():
    parser = argparse.ArgumentParser(description="Cut video clips from segment metadata")
    parser.add_argument("--source", help="Path to source video MP4")
    parser.add_argument("--source-dir", help="Directory containing source MP4s (batch mode)")
    parser.add_argument("--segments", help="Path to segment metadata JSON")
    parser.add_argument("--segments-dir", help="Directory of segment JSONs (batch mode)")
    parser.add_argument("--output-dir", default="clips", help="Output directory for clips (default: clips)")
    parser.add_argument("--buffer-start", type=float, default=0, help="Seconds to add before clip start (default: 0)")
    parser.add_argument("--buffer-end", type=float, default=0, help="Seconds to add after clip end (default: 0)")
    parser.add_argument("--naming-prefix", default="", help="Prefix for output filenames")
    parser.add_argument("--reencode", action="store_true", help="Re-encode for frame-accurate cuts (slower)")
    args = parser.parse_args()

    if not args.source and not args.source_dir:
        parser.error("Provide --source or --source-dir")

    clips_dir = Path(args.output_dir)
    clips_dir.mkdir(parents=True, exist_ok=True)

    # Load segments
    if args.segments:
        with open(args.segments, 'r') as f:
            all_segments = json.load(f)
        # Ensure each segment has a video_file reference
        if args.source:
            for seg in all_segments:
                if 'video_file' not in seg:
                    seg['video_file'] = Path(args.source).name
    elif args.segments_dir:
        segments_dir = Path(args.segments_dir)
        combined_file = segments_dir / "all_segments.json"
        if combined_file.exists():
            with open(combined_file, 'r') as f:
                all_segments = json.load(f)
        else:
            all_segments = []
            for seg_file in segments_dir.glob("*_segments.json"):
                with open(seg_file, 'r') as f:
                    all_segments.extend(json.load(f))
    else:
        parser.error("Provide --segments or --segments-dir")

    print(f"Found {len(all_segments)} segments to cut")

    successful_clips = []
    failed_clips = []
    total_duration = 0

    for i, segment in enumerate(all_segments, 1):
        # Find source video
        if args.source:
            source_path = Path(args.source)
        else:
            video_file = segment.get('video_file', '')
            source_path = Path(args.source_dir) / video_file

        if not source_path.exists():
            print(f"❌ {i}/{len(all_segments)}: Source video not found: {source_path}")
            failed_clips.append(segment)
            continue

        # Apply buffers
        start_time = max(0, segment['start_time'] - args.buffer_start)
        end_time = segment['end_time'] + args.buffer_end

        # Generate output filename
        episode_slug = get_episode_title_slug(source_path.name)
        title_slug = slugify(segment.get('suggested_title', f'clip{i}'))
        prefix = f"{args.naming_prefix}_" if args.naming_prefix else ""
        output_filename = f"{prefix}{episode_slug}-clip-{i}-{title_slug}.mp4"
        output_path = clips_dir / output_filename

        # Cut the clip
        duration = end_time - start_time
        print(f"🎬 {i}/{len(all_segments)}: Cutting '{segment.get('suggested_title', 'Untitled')}'")
        print(f"   Duration: {duration:.0f}s | Output: {output_filename}")

        success, error = cut_clip(source_path, start_time, end_time, output_path, reencode=args.reencode)

        if success:
            file_size = output_path.stat().st_size / (1024 * 1024)
            total_duration += duration

            clip_info = {
                **segment,
                'output_file': output_filename,
                'file_size_mb': round(file_size, 1),
                'duration_seconds': duration,
                'start_time_adjusted': start_time,
                'end_time_adjusted': end_time,
            }
            successful_clips.append(clip_info)
            print(f"   ✅ Success! ({file_size:.1f} MB)")
        else:
            print(f"   ❌ Failed: {error}")
            failed_clips.append(segment)

    # Save clip metadata
    clips_metadata_file = clips_dir / "clips_metadata.json"
    with open(clips_metadata_file, 'w') as f:
        json.dump(successful_clips, f, indent=2)

    # Summary
    print(f"\n🎉 Clip cutting complete!")
    print(f"✅ Successfully cut: {len(successful_clips)} clips")
    print(f"❌ Failed: {len(failed_clips)} clips")
    print(f"📁 Total clips duration: {total_duration/60:.1f} minutes")
    print(f"📄 Metadata saved to: {clips_metadata_file}")

    if successful_clips:
        print(f"\n🔥 Top clips by hook strength:")
        top_clips = sorted(successful_clips, key=lambda x: x.get('hook_strength', 0), reverse=True)[:3]
        for i, clip in enumerate(top_clips, 1):
            print(f"{i}. {clip.get('suggested_title', 'Untitled')} (hook: {clip.get('hook_strength', '?')}/10)")
            print(f"   File: {clip['output_file']} ({clip['duration_seconds']:.0f}s)")

    print(f"\n📂 All clips saved to: {clips_dir}")


if __name__ == "__main__":
    main()
