#!/usr/bin/env python3
"""
local_pipeline.py — Short-form clip pipeline for local video files.
Uses Whisper for transcription instead of YouTube captions.

Usage:
  python3 local_pipeline.py --file path/to/video.mov [--max-clips 2] [--output-dir ./output]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import shutil
from pathlib import Path
import anthropic
import whisper

# ── Helpers ────────────────────────────────────────────────────────────────────

def log(msg: str):
    print(f"[pipeline] {msg}", flush=True)


def run(cmd: list, **kwargs) -> subprocess.CompletedProcess:
    log(f"$ {' '.join(str(c) for c in cmd)}")
    return subprocess.run(cmd, **kwargs)


def get_anthropic_client() -> anthropic.Anthropic:
    key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_KEY")
    if not key:
        raise RuntimeError("No ANTHROPIC_API_KEY found. Set the environment variable before running.")
    return anthropic.Anthropic(api_key=key)


def parse_time_to_seconds(t: str) -> float:
    parts = t.strip().split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
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
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", video_path],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


# ── Transcription ──────────────────────────────────────────────────────────────

def transcribe_video(video_path: str, language: str = "fr") -> list[dict]:
    """Transcribe video using Whisper. Returns list of {start, end, text} segments."""
    log(f"Transcribing with Whisper (language={language})...")
    model = whisper.load_model("base")
    result = model.transcribe(video_path, language=language, word_timestamps=True)

    entries = []
    for seg in result["segments"]:
        entries.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"].strip(),
        })
    log(f"Transcription: {len(entries)} segments")
    return entries


def transcript_to_text(entries: list[dict]) -> str:
    lines = []
    for e in entries:
        ts = seconds_to_mmss(e["start"])
        lines.append(f"[{ts}] {e['text']}")
    return "\n".join(lines)


def get_transcript_window(entries: list[dict], center_seconds: float, window: float = 10.0) -> str:
    lo, hi = center_seconds - window, center_seconds + window
    lines = []
    for e in entries:
        if e["end"] < lo or e["start"] > hi:
            continue
        ts = seconds_to_mmss(e["start"])
        lines.append(f"[{ts}] {e['text']}")
    return "\n".join(lines)


# ── Segmentation ───────────────────────────────────────────────────────────────

SEGMENTATION_PROMPT = """Tu es un éditeur vidéo spécialisé en contenu viral pour TikTok, Instagram Reels et YouTube Shorts.

Je vais te donner la transcription complète d'une vidéo avec des horodatages. Ta mission : trouver les **meilleurs moments** qui fonctionneraient comme des clips courts de 20 à 60 secondes.

CRITÈRES pour un bon clip court :
- HOOK dans les 3 premières secondes — la phrase d'ouverture doit capter immédiatement l'attention (stat surprenante, affirmation forte, action en cours, situation concrète)
- UNE IDÉE COMPLÈTE — un concept, une démonstration, une révélation. Pas un résumé de plusieurs points.
- IMPACT ÉMOTIONNEL — surprise, humour, opinion forte, ou quelque chose d'authentique et relatable
- FIN NETTE — se termine sur une pensée complète ou un moment fort
- Durée idéale : 20–45 secondes. Maximum absolu : 60 secondes.

Pour chaque clip, retourne un objet JSON avec :
- start_time: format "MM:SS"
- end_time: format "MM:SS"
- title: titre court descriptif
- hook_sentence: la première phrase exacte du clip (devient le texte d'accroche en overlay)
- payoff_sentence: le message clé ou la conclusion
- why: brève explication de pourquoi ça performera en short-form
- layout_hint: "talking_head" (personne seule face caméra), "action_shot" (personne en action/mouvement), "screen_share_overlay", ou "side_by_side"

Retourne UNIQUEMENT un tableau JSON valide. Pas de markdown, pas de commentaires.

Voici la transcription :
{TRANSCRIPT}"""


def call_claude_segmentation(client: anthropic.Anthropic, transcript: str, n: int = 2) -> list[dict]:
    prompt = SEGMENTATION_PROMPT.replace("{TRANSCRIPT}", transcript)
    prompt += f"\n\nRetourne exactement {n} clip(s) sous forme de tableau JSON."

    log("Appel Claude pour la segmentation...")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = message.content[0].text.strip()

    json_match = re.search(r'(\[[\s\S]+\]|\{[\s\S]+\})', raw)
    if not json_match:
        raise ValueError(f"Pas de JSON dans la réponse Claude :\n{raw}")

    parsed = json.loads(json_match.group(1))
    if isinstance(parsed, dict):
        parsed = [parsed]

    filtered = []
    for clip in parsed[:n]:
        try:
            start = parse_time_to_seconds(clip.get("start_time", "0:00"))
            end = parse_time_to_seconds(clip.get("end_time", "0:30"))
            duration = end - start
            if duration < 15:
                log(f"  Clip '{clip.get('title','?')[:40]}' trop court ({duration:.0f}s). Ignoré.")
                continue
            if duration > 90:
                log(f"  Clip '{clip.get('title','?')[:40]}' trop long ({duration:.0f}s). Tronqué.")
                clip["end_time"] = format_seconds_to_time(start + 60)
            filtered.append(clip)
        except Exception:
            filtered.append(clip)

    return filtered[:n]


def verify_cut(client: anthropic.Anthropic, clip: dict, entries: list[dict]) -> dict:
    end_sec = parse_time_to_seconds(clip["end_time"])
    window_text = get_transcript_window(entries, end_sec, window=10.0)

    prompt = f"""Tu vérifies si un clip vidéo se termine sur une pensée complète.

Temps de fin proposé : {clip['end_time']}
Phrase de conclusion : "{clip.get('payoff_sentence', '')}"

Transcription autour du temps de fin (±10 secondes) :
{window_text}

La pensée est-elle complète à {clip['end_time']}, ou continue-t-elle ?
Si elle continue, donne le temps de fin corrigé où la pensée se résout vraiment.

Retourne UNIQUEMENT un JSON valide :
{{
  "end_is_clean": true/false,
  "corrected_end_time": "MM:SS ou identique si propre",
  "reason": "explication en une phrase"
}}"""

    log(f"Vérification de la coupe à {clip['end_time']}...")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = message.content[0].text.strip()
    json_match = re.search(r'(\{[\s\S]+\})', raw)
    if not json_match:
        return clip

    verification = json.loads(json_match.group(1))
    if not verification.get("end_is_clean") and verification.get("corrected_end_time"):
        old_end = clip["end_time"]
        clip["end_time"] = verification["corrected_end_time"]
        log(f"  Coupe corrigée : {old_end} -> {clip['end_time']} ({verification.get('reason', '')})")
    else:
        log(f"  Coupe propre à {clip['end_time']}")

    return clip


# ── FFmpeg ─────────────────────────────────────────────────────────────────────

def cut_clip(video_path: str, start: str, end: str, output_path: str):
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
    """Crop to 1080x1920 vertical. Detects if input is portrait or landscape."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", input_path],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    video_stream = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    if not video_stream:
        raise RuntimeError("No video stream found")

    w = int(video_stream.get("width", 1920))
    h = int(video_stream.get("height", 1080))

    # Handle rotation metadata (iOS MOV files are often rotated)
    rotation = 0
    if "tags" in video_stream:
        rotation = int(video_stream["tags"].get("rotate", 0))
    if rotation in (90, 270):
        w, h = h, w  # swap after rotation

    log(f"  Video dimensions: {w}x{h} (rotation={rotation}°)")

    if h > w:
        # Already portrait — scale to 1080 wide, pad to 1920 tall
        vf = "scale=1080:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black"
    else:
        # Landscape — center crop to 9:16
        # Target: 1080x1920. From landscape, crop height=full, width=h*9/16
        vf = "scale=-2:1920,crop=1080:1920"

    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf", vf,
        "-c:v", "libx264", "-c:a", "aac",
        output_path,
    ]
    result = run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log(f"FFmpeg crop error: {result.stderr[-500:]}")
        raise RuntimeError("FFmpeg vertical crop failed")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Local video short-form clip pipeline")
    parser.add_argument("--file", required=True, help="Path to local video file")
    parser.add_argument("--max-clips", type=int, default=2, help="Max number of clips")
    parser.add_argument("--output-dir", default="./output", help="Output directory")
    parser.add_argument("--language", default="fr", help="Transcription language (default: fr)")
    args = parser.parse_args()

    video_path = args.file
    if not Path(video_path).exists():
        print(f"ERROR: File not found: {video_path}")
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    client = get_anthropic_client()

    duration = get_video_duration(video_path)
    log(f"Vidéo : {Path(video_path).name} — {duration:.0f}s ({duration/60:.1f} min)")

    # Transcribe
    entries = transcribe_video(video_path, language=args.language)
    if not entries:
        print("ERROR: Transcription vide")
        sys.exit(1)

    transcript = transcript_to_text(entries)
    log(f"Transcription : {len(transcript)} caractères")
    print("\n--- TRANSCRIPTION ---")
    print(transcript[:2000])
    print("--- FIN TRANSCRIPTION ---\n")

    # Segment
    clips = call_claude_segmentation(client, transcript, n=args.max_clips)
    log(f"{len(clips)} clip(s) identifié(s)")

    # Verify cuts
    for i, clip in enumerate(clips):
        clips[i] = verify_cut(client, clip, entries)

    # Process each clip
    results = []
    for i, clip in enumerate(clips, 1):
        safe_title = re.sub(r'[^\w\s-]', '', clip.get('title', f'clip_{i}'))[:50].replace(' ', '_')
        clip_name = f"{i:02d}_{safe_title}"

        log(f"\n--- Clip {i}: {clip.get('title', 'Sans titre')} ---")
        log(f"  Début: {clip['start_time']} | Fin: {clip['end_time']}")
        log(f"  Hook: {clip.get('hook_sentence', '')}")

        raw_path = output_dir / f"{clip_name}_raw.mp4"
        final_path = output_dir / f"{clip_name}_vertical.mp4"

        try:
            cut_clip(video_path, clip["start_time"], clip["end_time"], str(raw_path))
            crop_vertical(str(raw_path), str(final_path))
            raw_path.unlink(missing_ok=True)  # clean up raw

            duration_sec = parse_time_to_seconds(clip["end_time"]) - parse_time_to_seconds(clip["start_time"])
            results.append({
                "title": clip.get("title", clip_name),
                "start_time": clip["start_time"],
                "end_time": clip["end_time"],
                "duration_seconds": duration_sec,
                "hook_sentence": clip.get("hook_sentence", ""),
                "payoff_sentence": clip.get("payoff_sentence", ""),
                "why": clip.get("why", ""),
                "path": str(final_path),
            })
            log(f"  Clip prêt : {final_path}")

        except Exception as e:
            log(f"  Clip {i} échoué : {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "="*60)
    print(f"TERMINÉ — {len(results)} clip(s) produit(s)")
    print("="*60)
    for r in results:
        print(f"\n  {r['title']}")
        print(f"   Durée : {r['duration_seconds']:.0f}s")
        print(f"   Hook  : {r['hook_sentence'][:100]}")
        print(f"   Payoff: {r['payoff_sentence'][:100]}")
        print(f"   Fichier: {r['path']}")

    # Save results JSON
    results_path = output_dir / "results.json"
    results_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    log(f"Résultats sauvegardés : {results_path}")


if __name__ == "__main__":
    main()
