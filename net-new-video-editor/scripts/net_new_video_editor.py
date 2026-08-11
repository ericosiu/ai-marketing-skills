#!/usr/bin/env python3
"""Render reversible vertical-video drafts from an explicit JSON edit plan."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

MEDIA_SUFFIXES = {".mp4", ".mov", ".m4v", ".webm"}


def run(cmd: list[str], capture: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, text=True, capture_output=capture)
    if result.returncode:
        if capture and result.stderr:
            print(result.stderr)
        raise SystemExit(result.returncode)
    return result


def require(name: str) -> str:
    found = shutil.which(name)
    if not found:
        raise SystemExit(f"Missing required command: {name}")
    return found


def inside(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise SystemExit(f"Path must stay inside project: {value}") from exc
    return path


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot read JSON {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"Expected a JSON object: {path}")
    return data


def write_json(path: Path, data: dict[str, Any], overwrite: bool = True) -> None:
    if path.exists() and not overwrite:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def probe(path: Path) -> dict[str, Any]:
    ffprobe = require("ffprobe")
    result = run(
        [ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        capture=True,
    )
    data = json.loads(result.stdout)
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    duration = float(data.get("format", {}).get("duration") or 0)
    if not video or duration <= 0:
        raise SystemExit(f"No playable video stream: {path}")
    return {
        "duration": round(duration, 3),
        "width": int(video.get("width") or 0),
        "height": int(video.get("height") or 0),
        "video_codec": video.get("codec_name"),
        "audio_codec": audio.get("codec_name") if audio else None,
        "has_audio": bool(audio),
    }


def init_project(root: Path) -> None:
    for name in ("raw", "transcript", "screens", "assets", "exports", "qa"):
        (root / name).mkdir(parents=True, exist_ok=True)
    write_json(
        root / "edit-brief.json",
        {
            "viewer": "",
            "promise": "",
            "spoken_hook": "",
            "target_duration_seconds": [30, 75],
            "cta": "",
            "claim_boundaries": [],
            "required_proof": [],
            "available_assets": [],
        },
        overwrite=False,
    )
    write_json(
        root / "edit-plan.json",
        {
            "version": 1,
            "source": "raw/take-1.mp4",
            "output": "exports/video-clean.mp4",
            "segments": [{"start": 0.0, "end": 30.0}],
            "format": {"width": 1080, "height": 1920, "fps": 30},
            "hook": {"text": "", "start": 0.0, "end": 3.0},
            "captions": {"file": "transcript/captions.srt"},
            "audio": {"lufs": -16, "true_peak": -1.5, "lra": 11},
            "notes": [],
        },
        overwrite=False,
    )
    print(f"Initialized {root}")


def inspect_project(root: Path) -> None:
    takes: list[dict[str, Any]] = []
    for path in sorted((root / "raw").glob("*")):
        if path.suffix.lower() in MEDIA_SUFFIXES and path.is_file():
            takes.append({"path": str(path.relative_to(root)), **probe(path)})
    report = {
        "project": str(root),
        "takes": takes,
        "transcripts": [str(p.relative_to(root)) for p in sorted((root / "transcript").glob("*")) if p.is_file()],
        "screens": [str(p.relative_to(root)) for p in sorted((root / "screens").glob("*")) if p.is_file()],
        "assets": [str(p.relative_to(root)) for p in sorted((root / "assets").glob("*")) if p.is_file()],
        "status": "ready" if takes else "needs_source_take",
    }
    write_json(root / "intake-report.json", report)
    print(json.dumps(report, indent=2))


def validate_plan(root: Path, plan_path: Path) -> tuple[dict[str, Any], Path, dict[str, Any]]:
    plan = read_json(plan_path)
    if plan.get("version") != 1:
        raise SystemExit("edit plan version must be 1")
    source = inside(root, str(plan.get("source", "")))
    if not source.is_file():
        raise SystemExit(f"Missing source: {source}")
    source_info = probe(source)
    if not source_info["has_audio"]:
        raise SystemExit("Source must contain an audio stream")
    segments = plan.get("segments")
    if not isinstance(segments, list) or not segments:
        raise SystemExit("segments must be a non-empty list")
    for index, segment in enumerate(segments):
        start = float(segment.get("start", -1))
        end = float(segment.get("end", -1))
        if start < 0 or end <= start or end > source_info["duration"] + 0.05:
            raise SystemExit(f"Invalid segment {index}: {start}-{end}")
    output = inside(root, str(plan.get("output", "")))
    if output.suffix.lower() != ".mp4":
        raise SystemExit("output must be an MP4 inside the project")
    captions = plan.get("captions", {})
    if captions.get("file"):
        caption_path = inside(root, str(captions["file"]))
        if not caption_path.is_file():
            raise SystemExit(f"Missing caption file: {caption_path}")
    print(f"Valid plan: {plan_path}")
    return plan, source, source_info


def parse_srt(path: Path) -> list[dict[str, Any]]:
    pattern = re.compile(
        r"(?:^|\n)\s*\d+\s*\n(\d\d):(\d\d):(\d\d)[,.](\d\d\d)\s*-->\s*"
        r"(\d\d):(\d\d):(\d\d)[,.](\d\d\d)\s*\n(.*?)(?=\n\s*\n|\Z)",
        re.S,
    )
    cues = []
    for match in pattern.finditer(path.read_text(errors="replace").replace("\r\n", "\n")):
        values = [int(value) for value in match.groups()[:8]]
        start = values[0] * 3600 + values[1] * 60 + values[2] + values[3] / 1000
        end = values[4] * 3600 + values[5] * 60 + values[6] + values[7] / 1000
        text = re.sub(r"<[^>]+>", "", match.group(9)).replace("\n", " ").strip()
        if text and end > start:
            cues.append({"start": start, "end": end, "text": text})
    return cues


def load_font(size: int):
    try:
        from PIL import ImageFont
    except ImportError as exc:
        raise SystemExit("Pillow is required for captions: python3 -m pip install pillow") from exc
    candidates = (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "DejaVuSans-Bold.ttf",
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    raise SystemExit("No supported bold font found for caption rendering")


def wrap_text(draw: Any, text: str, font: Any, max_width: int) -> str:
    words = str(text).split()
    if not words:
        return ""
    lines: list[str] = []
    line = words[0]
    for word in words[1:]:
        candidate = f"{line} {word}"
        if draw.textlength(candidate, font=font) <= max_width:
            line = candidate
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return "\n".join(lines[:3])


def make_overlays(root: Path, plan: dict[str, Any], destination: Path) -> list[dict[str, Any]]:
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise SystemExit("Pillow is required for captions: python3 -m pip install pillow") from exc
    fmt = plan.get("format", {})
    width, height = int(fmt.get("width", 1080)), int(fmt.get("height", 1920))
    specs: list[dict[str, Any]] = []
    hook = plan.get("hook", {})
    if str(hook.get("text", "")).strip():
        specs.append({"kind": "hook", "start": float(hook.get("start", 0)), "end": float(hook.get("end", 3)), "text": str(hook["text"])})
    captions = plan.get("captions", {})
    cues = captions.get("cues", [])
    if captions.get("file"):
        cues = parse_srt(inside(root, str(captions["file"])))
    for cue in cues:
        specs.append({"kind": "caption", "start": float(cue["start"]), "end": float(cue["end"]), "text": str(cue["text"])})
    if len(specs) > 120:
        raise SystemExit("Too many overlay cues; group captions into fewer short phrases")
    destination.mkdir(parents=True, exist_ok=True)
    overlays: list[dict[str, Any]] = []
    for index, spec in enumerate(specs):
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        is_hook = spec["kind"] == "hook"
        font = load_font(max(28, round(width * (0.063 if is_hook else 0.061))))
        text = wrap_text(draw, spec["text"], font, round(width * 0.82))
        spacing = round(width * 0.016)
        bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align="center", stroke_width=2)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pad_x, pad_y = round(width * 0.035), round(height * 0.012)
        left = (width - text_width) // 2 - pad_x
        top = round(height * (0.055 if is_hook else 0.64))
        right, bottom = left + text_width + 2 * pad_x, top + text_height + 2 * pad_y
        fill = (232, 24, 56, 242) if is_hook else (0, 0, 0, 218)
        draw.rounded_rectangle((left, top, right, bottom), radius=round(width * 0.018), fill=fill)
        draw.multiline_text(
            ((width - text_width) / 2, top + pad_y - bbox[1]), text, font=font, fill="white",
            spacing=spacing, align="center", stroke_width=2, stroke_fill=(0, 0, 0, 130),
        )
        path = destination / f"overlay-{index:03d}.png"
        image.save(path)
        overlays.append({**spec, "path": path})
    return overlays


def render(root: Path, plan_path: Path, force: bool, dry_run: bool) -> Path:
    ffmpeg = require("ffmpeg")
    plan, source, _ = validate_plan(root, plan_path)
    output = inside(root, str(plan["output"]))
    if output.exists() and not force:
        raise SystemExit(f"Output exists; pass --force to replace this derived file: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    work = root / "qa"
    work.mkdir(parents=True, exist_ok=True)
    overlays = make_overlays(root, plan, work / f"{output.stem}-overlays")
    chains = []
    concat_inputs = []
    for index, segment in enumerate(plan["segments"]):
        start, end = float(segment["start"]), float(segment["end"])
        chains.append(f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{index}]")
        chains.append(f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{index}]")
        concat_inputs.append(f"[v{index}][a{index}]")
    chains.append("".join(concat_inputs) + f"concat=n={len(plan['segments'])}:v=1:a=1[vcat][acat]")
    fmt = plan.get("format", {})
    width, height, fps = int(fmt.get("width", 1080)), int(fmt.get("height", 1920)), int(fmt.get("fps", 30))
    chains.append(
        f"[vcat]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},setsar=1,fps={fps}[vbase]"
    )
    video_label = "vbase"
    for index, overlay in enumerate(overlays):
        input_index = index + 1
        chains.append(f"[{input_index}:v]format=rgba[ov{index}]")
        next_label = f"vo{index}"
        chains.append(
            f"[{video_label}][ov{index}]overlay=0:0:shortest=1:enable='between(t,{overlay['start']},{overlay['end']})'[{next_label}]"
        )
        video_label = next_label
    audio = plan.get("audio", {})
    chains.append(
        f"[acat]loudnorm=I={float(audio.get('lufs', -16))}:TP={float(audio.get('true_peak', -1.5))}:LRA={float(audio.get('lra', 11))},aresample=48000[aout]"
    )
    cmd = [ffmpeg, "-y" if force else "-n", "-i", str(source)]
    for overlay in overlays:
        cmd.extend(["-loop", "1", "-framerate", str(fps), "-i", str(overlay["path"])])
    cmd.extend([
        "-filter_complex", ";".join(chains),
        "-map", f"[{video_label}]", "-map", "[aout]", "-c:v", "libx264", "-preset", "medium",
        "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(output),
    ])
    if dry_run:
        print(json.dumps(cmd))
        return output
    run(cmd)
    qa(root, output, plan)
    print(f"Rendered {output}")
    return output


def qa(root: Path, output: Path, plan: dict[str, Any] | None = None) -> None:
    ffmpeg = require("ffmpeg")
    info = probe(output)
    expected = (plan or {}).get("format", {})
    checks = {
        "has_audio": info["has_audio"],
        "positive_duration": info["duration"] > 0,
        "width": not expected or info["width"] == int(expected.get("width", info["width"])),
        "height": not expected or info["height"] == int(expected.get("height", info["height"])),
        "video_codec_h264": info["video_codec"] == "h264",
        "audio_codec_aac": info["audio_codec"] == "aac",
    }
    qa_dir = root / "qa" / output.stem
    qa_dir.mkdir(parents=True, exist_ok=True)
    for label, ratio in (("opening", 0.1), ("middle", 0.5), ("ending", 0.9)):
        timestamp = max(0.0, info["duration"] * ratio)
        run([ffmpeg, "-y", "-ss", str(timestamp), "-i", str(output), "-frames:v", "1", "-q:v", "2", "-update", "1", str(qa_dir / f"{label}.jpg")])
    report = {"output": str(output.relative_to(root)), "probe": info, "checks": checks, "status": "pass" if all(checks.values()) else "fail"}
    write_json(qa_dir / "qa-report.json", report)
    print(json.dumps(report, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "inspect"):
        command = sub.add_parser(name)
        command.add_argument("--project", required=True)
    for name in ("validate", "render"):
        command = sub.add_parser(name)
        command.add_argument("--project", required=True)
        command.add_argument("--plan", required=True)
        if name == "render":
            command.add_argument("--force", action="store_true")
            command.add_argument("--dry-run", action="store_true")
    command = sub.add_parser("qa")
    command.add_argument("--project", required=True)
    command.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(args.project).expanduser().resolve()
    if args.command == "init":
        init_project(root)
    elif not root.is_dir():
        raise SystemExit(f"Missing project directory: {root}")
    elif args.command == "inspect":
        inspect_project(root)
    elif args.command == "validate":
        validate_plan(root, inside(root, args.plan))
    elif args.command == "render":
        render(root, inside(root, args.plan), args.force, args.dry_run)
    elif args.command == "qa":
        qa(root, inside(root, args.output))


if __name__ == "__main__":
    main()
