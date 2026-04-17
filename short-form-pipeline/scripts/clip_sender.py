#!/usr/bin/env python3
"""
Clip Sender — Clip delivery and review helper

Loads generated clips and formats them for review with approval/edit/skip actions.
Outputs structured data that can be integrated with any messaging platform.

Usage:
    python3 clip_sender.py [--dry-run] [--batch-size N]
"""

import json
import os
import sys
import argparse
from pathlib import Path

# Configuration
CLIPS_LATEST_FILE = "data/video-clips-latest.json"
DEFAULT_BATCH_SIZE = 5


class ClipSender:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run

    def load_clips(self):
        """Load latest clips to send."""
        if not os.path.exists(CLIPS_LATEST_FILE):
            print(f"No clips file found: {CLIPS_LATEST_FILE}")
            return None

        with open(CLIPS_LATEST_FILE, 'r') as f:
            return json.load(f)

    def format_clip_message(self, clip, video_info):
        """Format message text for a clip."""
        clip_type = "Short" if clip['type'] == 'vertical_short' else "Mid-form"
        duration = f"{int(clip['duration'])}s"
        timestamp = f"{int(clip['start_time']//60)}:{int(clip['start_time']%60):02d}"

        score = clip['score']
        score_text = f"Score: {score['total']}/40 (H:{score['hook']} V:{score['value']} S:{score['standalone']} Voice:{score.get('voice', 0)})"

        message = f"""{clip_type} | {duration} | {timestamp}
From: {video_info['title']}

{score_text}

Preview: "{clip['text'][:200]}{'...' if len(clip['text']) > 200 else ''}"

Generated: {clip['created_at'][:16]}"""

        return message

    def create_clip_actions(self, clip_id):
        """Create action buttons for clip approval."""
        return [
            {"label": "Approve", "action": f"clip_approve_{clip_id}"},
            {"label": "Edit", "action": f"clip_edit_{clip_id}"},
            {"label": "Skip", "action": f"clip_skip_{clip_id}"}
        ]

    def send_clip(self, clip, video_info):
        """Output a single clip for review."""
        clip_path = clip['path']

        if not self.dry_run and not os.path.exists(clip_path):
            print(f"Warning: Clip file not found: {clip_path}")
            return False

        message_text = self.format_clip_message(clip, video_info)
        actions = self.create_clip_actions(clip['id'])

        if self.dry_run:
            print(f"DRY RUN: Would send clip {clip['id']}")
            print(f"   File: {clip_path}")
            print(f"   Message: {message_text[:100]}...")
            print(f"   Actions: {len(actions)} action(s)")
            return True

        # Output structured data for the caller to deliver
        print(f"Sending clip: {os.path.basename(clip_path)}")
        output = {
            "clip_id": clip['id'],
            "file_path": clip_path,
            "message": message_text,
            "actions": actions,
        }
        print(f"CLIP_DATA: {json.dumps(output)}")
        return True

    def send_batch_header(self, video_info, clip_count):
        """Output header message for a batch of clips."""
        header = f"""NEW VIDEO CLIPS READY

{video_info['title']}
{video_info.get('date', '')}
{video_info.get('url', '')}

Generated {clip_count} clips for review:"""

        if self.dry_run:
            print(f"DRY RUN: Would send batch header")
            print(f"   {header}")
            return True

        print(f"Batch header for {video_info['title']}")
        print(f"HEADER: {json.dumps({'text': header})}")
        return True

    def send_batch(self, clips_data, batch_size=DEFAULT_BATCH_SIZE):
        """Send clips for review, grouped by source video."""
        if not clips_data or not clips_data.get('clips'):
            print("No clips to send")
            return False

        video_info = clips_data['source_video']
        clips = clips_data['clips']

        print(f"\nSending {len(clips)} clips from: {video_info['title']}")

        self.send_batch_header(video_info, len(clips))

        success_count = 0
        for i, clip in enumerate(clips):
            if i >= batch_size:
                print(f"Stopping at batch size limit: {batch_size}")
                break

            if self.send_clip(clip, video_info):
                success_count += 1
            else:
                print(f"Warning: Failed to send clip {i+1}")

        print(f"\nSent {success_count}/{min(len(clips), batch_size)} clips successfully")
        return success_count > 0


def main():
    parser = argparse.ArgumentParser(description='Clip Sender — review and delivery helper')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no actual sending)')
    parser.add_argument('--batch-size', type=int, default=DEFAULT_BATCH_SIZE,
                       help=f'Maximum clips to send per batch (default: {DEFAULT_BATCH_SIZE})')

    args = parser.parse_args()

    sender = ClipSender(dry_run=args.dry_run)

    clips_data = sender.load_clips()
    if clips_data:
        success = sender.send_batch(clips_data, args.batch_size)
        sys.exit(0 if success else 1)
    else:
        print("No clips available to send")
        sys.exit(1)


if __name__ == '__main__':
    main()
