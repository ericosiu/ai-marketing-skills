#!/usr/bin/env python3
"""
process_videos.py — Transcribe new videos from a Google Drive folder,
deduplicate by content, and generate captions + YT/FB titles via Claude API.

Usage:
    python3 process_videos.py --folder-id <DRIVE_FOLDER_ID> [--processed-log <path>]

Output: prints formatted results to stdout
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# --- Configuration: update these for your environment ---
# Path to your Google Drive CLI tool (e.g., gws-gateway.sh, gdrive, rclone wrapper)
GWS_GATEWAY = os.environ.get("GWS_GATEWAY", "gws-gateway.sh")
# Path to your Whisper binary
WHISPER_BIN = os.environ.get("WHISPER_BIN", "whisper")
# Working directory for subprocess calls
WORKSPACE = os.environ.get("WORKSPACE", str(Path.cwd()))


def gws(args: list[str]) -> dict:
    """Call the Google Drive CLI and return parsed JSON output."""
    cmd = [GWS_GATEWAY] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=WORKSPACE)
    try:
        return json.loads(result.stdout)
    except Exception:
        return {"error": result.stderr or result.stdout}


def list_videos(folder_id: str) -> list[dict]:
    """List video files in a Google Drive folder."""
    data = gws([
        "drive", "files", "list",
        "--params", json.dumps({
            "q": f'"{folder_id}" in parents and mimeType contains "video/"',
            "fields": "files(id,name,mimeType,createdTime)",
            "orderBy": "createdTime desc"
        })
    ])
    return data.get("files", [])


def download_video(file_id: str, dest: str) -> bool:
    """Download a video file from Google Drive."""
    data = gws([
        "drive", "files", "get",
        "--params", json.dumps({"fileId": file_id, "alt": "media"}),
        "-o", dest
    ])
    return data.get("status") == "success"


def transcribe(video_path: str, out_dir: str) -> str | None:
    """Transcribe a video file using Whisper."""
    result = subprocess.run(
        [WHISPER_BIN, video_path,
         "--model", "turbo",
         "--output_format", "txt",
         "--output_dir", out_dir,
         "--language", "en"],
        capture_output=True, text=True
    )
    txt_path = Path(out_dir) / (Path(video_path).stem + ".txt")
    if txt_path.exists():
        return txt_path.read_text().strip()
    return None


def content_hash(text: str) -> str:
    """Generate a content hash for deduplication."""
    return hashlib.md5(text.lower().split().__str__().encode()).hexdigest()


def generate_caption_and_title(transcript: str, api_key: str) -> tuple[str, str]:
    """Use Claude API to generate a social caption and video title."""
    import urllib.request
    prompt = f"""Given this video transcript, write:
1. A punchy social media caption (2-4 sentences, first person, no hashtags, conversational)
2. A YouTube/Facebook title (under 60 chars, curiosity-driven, no clickbait)

Transcript:
{transcript}

Respond in this exact format:
CAPTION: <caption here>
TITLE: <title here>"""

    payload = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 300,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    text = data["content"][0]["text"]
    caption = ""
    title = ""
    for line in text.splitlines():
        if line.startswith("CAPTION:"):
            caption = line[len("CAPTION:"):].strip()
        elif line.startswith("TITLE:"):
            title = line[len("TITLE:"):].strip()
    return caption, title


def load_processed(log_path: str) -> set[str]:
    """Load set of already-processed video IDs."""
    if not Path(log_path).exists():
        return set()
    with open(log_path) as f:
        return set(json.load(f))


def save_processed(log_path: str, processed: set[str]):
    """Save updated set of processed video IDs."""
    with open(log_path, "w") as f:
        json.dump(list(processed), f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe Drive videos and generate social captions + titles"
    )
    parser.add_argument("--folder-id", required=True,
                        help="Google Drive folder ID to scan for videos")
    parser.add_argument("--processed-log", default="processed_ids.json",
                        help="Path to JSON file tracking processed video IDs")
    args = parser.parse_args()

    # Load Anthropic API key from environment
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    processed_ids = load_processed(args.processed_log)
    videos = list_videos(args.folder_id)

    new_videos = [v for v in videos if v["id"] not in processed_ids]
    if not new_videos:
        print("No new videos found.")
        return

    seen_hashes: dict[str, str] = {}  # hash -> first video name (within this batch)
    results = []

    with tempfile.TemporaryDirectory() as tmpdir:
        for video in new_videos:
            vid_id = video["id"]
            vid_name = video["name"]
            dest = str(Path(tmpdir) / (vid_name.replace(" ", "_")))

            print(f"Downloading {vid_name}...", file=sys.stderr)
            ok = download_video(vid_id, dest)
            if not ok:
                print(f"  SKIP (download failed)", file=sys.stderr)
                processed_ids.add(vid_id)
                continue

            print(f"Transcribing {vid_name}...", file=sys.stderr)
            transcript = transcribe(dest, tmpdir)
            if not transcript:
                print(f"  SKIP (transcription failed)", file=sys.stderr)
                processed_ids.add(vid_id)
                continue

            h = content_hash(transcript)
            is_ab_variant = h in seen_hashes
            if is_ab_variant:
                print(f"  A/B variant of {seen_hashes[h]} — processing anyway", file=sys.stderr)
            else:
                seen_hashes[h] = vid_name

            print(f"Generating caption + title for {vid_name}...", file=sys.stderr)
            caption, title = generate_caption_and_title(transcript, api_key)

            result_entry = {
                "name": vid_name,
                "transcript": transcript,
                "caption": caption,
                "title": title
            }
            if is_ab_variant:
                result_entry["ab_variant_of"] = seen_hashes[h]
            results.append(result_entry)
            processed_ids.add(vid_id)

    save_processed(args.processed_log, processed_ids)

    # Print formatted output
    for r in results:
        ab_tag = f" (A/B variant of {r['ab_variant_of']})" if r.get('ab_variant_of') else ""
        print(f"\n*{r['name']}*{ab_tag}")
        print(f"📝 *Transcript:* {r['transcript']}")
        print(f"🎬 *Caption:* {r['caption']}")
        print(f"📺 *YT/FB Title:* {r['title']}")

    if not results:
        print("All new videos were duplicates — nothing new to report.")


if __name__ == "__main__":
    main()
