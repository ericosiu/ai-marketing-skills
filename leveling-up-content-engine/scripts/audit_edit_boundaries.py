#!/usr/bin/env python3
"""Validate retained edit clips against exact transcript boundaries."""

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transcript", type=Path, required=True)
    parser.add_argument("--clips", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--tolerance", type=float, default=0.12)
    args = parser.parse_args()
    transcript = json.loads(args.transcript.read_text())
    clip_data = json.loads(args.clips.read_text())
    segments = transcript.get("segments", [])
    clips = clip_data.get("retained_clips", clip_data if isinstance(clip_data, list) else [])
    errors, audited = [], []
    if transcript.get("granularity") not in {"word", "sentence"}:
        errors.append("transcript granularity must be word or sentence")
    if not segments or not clips:
        errors.append("transcript segments and retained clips are required")
    starts = [float(item["start"]) for item in segments]
    ends = [float(item["end"]) for item in segments]
    for index, clip in enumerate(clips, 1):
        clip_id = str(clip.get("id", f"clip-{index}"))
        clip_errors = []
        try:
            source_start, content_start = float(clip["source_start"]), float(clip["content_start"])
            content_end, source_end = float(clip["content_end"]), float(clip["source_end"])
            nearest_start = min(starts, key=lambda value: abs(value - content_start))
            nearest_end = min(ends, key=lambda value: abs(value - content_end))
            if abs(nearest_start - content_start) > args.tolerance:
                clip_errors.append("content_start is not a complete-thought start")
            if abs(nearest_end - content_end) > args.tolerance:
                clip_errors.append("content_end is not a complete-thought end")
            if not source_start <= content_start < content_end <= source_end:
                clip_errors.append("source/content times are not properly ordered")
        except (KeyError, TypeError, ValueError) as exc:
            nearest_start = nearest_end = 0.0
            clip_errors.append(f"malformed time fields: {exc}")
        audited.append({"id": clip_id, "matched_start": nearest_start, "matched_end": nearest_end, "status": "PASS" if not clip_errors else "FAIL", "errors": clip_errors})
        errors.extend(f"{clip_id}: {message}" for message in clip_errors)
    report = {"status": "PASS" if not errors else "FAIL", "memo_timestamps_are_guides": True, "transcript_granularity": transcript.get("granularity"), "retained_clips": audited, "errors": errors}
    rendered = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n")
    print(rendered)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
