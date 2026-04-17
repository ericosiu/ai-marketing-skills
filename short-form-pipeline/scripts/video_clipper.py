#!/usr/bin/env python3
"""
Video Clipper — Standalone clip extraction engine (v2)

Extracts short-form and mid-form clips from YouTube videos using
heuristic scoring (no Claude API required). Features Whisper transcription,
smart face-detected crop, and TikTok-style word-highlighted captions.

Usage:
    python3 video_clipper.py --url URL [--dry-run] [--test-one] [--use-whisper] [--no-whisper]
"""

import json
import os
import sys
import subprocess
import re
import argparse
from datetime import datetime
from pathlib import Path
import uuid
import tempfile
import shutil
import math
import logging
logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────────
CLIPS_DIR = "data/clips"
CLIPS_LATEST_FILE = "data/video-clips-latest.json"
CLIPS_HISTORY_FILE = "data/video-clips-history.json"
CONTENT_ATOMS_FILE = "data/content-atoms-latest.json"

# Scoring thresholds
MIN_CLIP_SCORE = 18
MIN_SHORT_DURATION = 15
MAX_SHORT_DURATION = 60
MIN_MID_DURATION = 300
MAX_MID_DURATION = 600

# ── Voice patterns ─────────────────────────────────────────────────────────────
# Customize these to match your creator's speaking style.
# These regex patterns boost clip scores when matched.
VOICE_PATTERNS = [
    r"high performers", r"here's the thing", r"here are \d+",
    r"when I was \d+", r"criteria:", r"main benefits:",
    r"\$\d+[MK]?\+", r"revenue", r"founders?", r"entrepreneurs?",
    r"masterminds?", r"network", r"trajectory", r"game-chang\w+",
    r"operating experience", r"true wisdom comes from",
    r"business creators"
]

# ── ASS subtitle styling ──────────────────────────────────────────────────────
ASS_HEADER = """[Script Info]
Title: Video Clip Captions
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,40,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,0,2,40,40,270,1
Style: Highlight,Arial Black,40,&H0000D4FF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,0,2,40,40,270,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

ASS_HEADER_HORIZONTAL = """[Script Info]
Title: Video Clip Captions
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,20,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,0,2,40,40,60,1
Style: Highlight,Arial Black,20,&H0000D4FF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,0,2,40,40,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


class VideoClipper:
    def __init__(self, dry_run=False, use_whisper=True):
        self.dry_run = dry_run
        self.use_whisper = use_whisper
        self._whisper_model = None
        self.ensure_directories()

    def ensure_directories(self):
        Path(CLIPS_DIR).mkdir(parents=True, exist_ok=True)

    @property
    def whisper_model(self):
        if self._whisper_model is None and self.use_whisper:
            try:
                import whisper
                print("Loading Whisper model (medium)...")
                self._whisper_model = whisper.load_model("medium")
                print("Whisper model loaded")
            except Exception as e:
                print(f"Warning: Failed to load Whisper: {e}")
                self._whisper_model = False  # sentinel for "tried and failed"
        return self._whisper_model

    def load_content_atoms(self):
        if not os.path.exists(CONTENT_ATOMS_FILE):
            print(f"Content atoms file not found: {CONTENT_ATOMS_FILE}")
            return []
        with open(CONTENT_ATOMS_FILE, 'r') as f:
            data = json.load(f)
        youtube_atoms = [a for a in data.get('atoms', [])
                         if a.get('source', '').startswith('youtube') and a.get('source_url')]
        print(f"Found {len(youtube_atoms)} YouTube video atoms")
        return youtube_atoms

    def load_processed_videos(self):
        if not os.path.exists(CLIPS_HISTORY_FILE):
            return set()
        try:
            with open(CLIPS_HISTORY_FILE, 'r') as f:
                return set(json.load(f).get('processed_video_ids', []))
        except Exception:
            return set()

    def extract_video_id(self, url):
        for pattern in [r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)',
                        r'youtube\.com\/embed\/([a-zA-Z0-9_-]+)']:
            m = re.search(pattern, url)
            if m:
                return m.group(1)
        return None

    def download_video(self, video_url, output_path):
        cmd = ['yt-dlp', '--format', 'best[height<=1080]', '--output', output_path,
               '--no-playlist', video_url]
        if self.dry_run:
            print("DRY RUN: Would download video")
            return True
        print("Downloading video...")
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("Video downloaded")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Download failed: {e.stderr[:300]}")
            return False

    # ── Whisper transcription ──────────────────────────────────────────

    def transcribe_with_whisper(self, audio_path):
        """Transcribe audio with Whisper, returning word-level timestamps."""
        model = self.whisper_model
        if not model:
            return None

        print("Transcribing with Whisper (this may take a few minutes)...")
        try:
            result = model.transcribe(
                audio_path,
                word_timestamps=True,
                language="en",
                verbose=False
            )
        except Exception as e:
            print(f"Warning: Whisper transcription failed: {e}")
            return None

        words = []
        for segment in result.get("segments", []):
            for w in segment.get("words", []):
                words.append({
                    "word": w["word"].strip(),
                    "start": round(w["start"], 3),
                    "end": round(w["end"], 3)
                })

        segments = []
        for seg in result.get("segments", []):
            segments.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip()
            })

        print(f"Whisper: {len(words)} words, {len(segments)} segments")
        return {"words": words, "segments": segments}

    def extract_audio(self, video_path, output_path):
        """Extract audio from video for Whisper."""
        cmd = ['ffmpeg', '-y', '-i', video_path, '-vn', '-acodec', 'pcm_s16le',
               '-ar', '16000', '-ac', '1', output_path]
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    # ── YouTube caption fallback ───────────────────────────────────────

    def extract_transcript(self, video_url):
        """Extract transcript using yt-dlp YouTube captions (fallback)."""
        cmd = ['yt-dlp', '--write-subs', '--write-auto-subs', '--sub-lang', 'en',
               '--sub-format', 'vtt', '--skip-download', '--output', 'temp_transcript.%(ext)s',
               video_url]
        if self.dry_run:
            return self._mock_transcript()
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            vtt_files = [f for f in os.listdir('.') if f.startswith('temp_transcript') and f.endswith('.vtt')]
            if not vtt_files:
                return []
            transcript = self.parse_vtt(vtt_files[0])
            for f in vtt_files:
                os.unlink(f)
            return transcript
        except subprocess.CalledProcessError as e:
            print(f"Warning: Transcript extraction failed: {e.stderr[:200]}")
            return []

    def parse_vtt(self, vtt_file):
        with open(vtt_file, 'r') as f:
            content = f.read()
        transcript = []
        seen_texts = set()
        for block in content.split('\n\n'):
            lines = block.strip().split('\n')
            if not lines:
                continue
            ts_match = re.match(r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})', lines[0])
            if not ts_match:
                continue
            raw_text = ' '.join(lines[1:])
            clean_text = re.sub(r'<[^>]+>', '', raw_text).strip()
            clean_text = re.sub(r'\s+', ' ', clean_text)
            if not clean_text or clean_text in seen_texts:
                continue
            seen_texts.add(clean_text)
            transcript.append({
                "start": self.vtt_time_to_seconds(ts_match.group(1)),
                "end": self.vtt_time_to_seconds(ts_match.group(2)),
                "text": clean_text
            })
        return transcript

    def vtt_time_to_seconds(self, time_str):
        parts = time_str.split(':')
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])

    def _mock_transcript(self):
        return [
            {"start": 0, "end": 30, "text": "High performers want to hang out with other high performers."},
            {"start": 30, "end": 75, "text": "When I was 25, I called a founder and asked what changed his trajectory."},
        ]

    # ── Deduplication ──────────────────────────────────────────────────

    def deduplicate_segments(self, segments):
        """Remove segments with >80% text overlap with previous."""
        if not segments:
            return segments
        result = [segments[0]]
        for seg in segments[1:]:
            prev_words = set(result[-1]['text'].lower().split())
            curr_words = set(seg['text'].lower().split())
            if not prev_words or not curr_words:
                result.append(seg)
                continue
            overlap = len(prev_words & curr_words) / max(len(prev_words), len(curr_words))
            if overlap < 0.8:
                result.append(seg)
            else:
                result[-1]['end'] = max(result[-1]['end'], seg['end'])
        return result

    # ── ASS caption generation ─────────────────────────────────────────

    def create_ass_captions(self, words, clip_start, clip_end, clip_type, output_path):
        """Create ASS file with TikTok-style word-highlighted captions.

        Shows 3 words at a time, current word highlighted in yellow.
        words: list of {"word": str, "start": float, "end": float} (absolute times)
        clip_start/clip_end: absolute times of the clip
        """
        clip_words = [w for w in words
                      if w['end'] > clip_start and w['start'] < clip_end]
        if not clip_words:
            return None

        is_vertical = clip_type == 'vertical_short'
        header = ASS_HEADER if is_vertical else ASS_HEADER_HORIZONTAL

        CHUNK_SIZE = 3
        chunks = []
        for i in range(0, len(clip_words), CHUNK_SIZE):
            chunk = clip_words[i:i + CHUNK_SIZE]
            chunks.append(chunk)

        events = []
        for chunk in chunks:
            for wi, w in enumerate(chunk):
                w_start = max(0, w['start'] - clip_start)
                w_end = max(w_start + 0.05, w['end'] - clip_start)

                parts = []
                for wj, w2 in enumerate(chunk):
                    escaped = w2['word'].replace('\\', '\\\\').replace('{', '\\{').replace('}', '\\}')
                    if wj == wi:
                        parts.append(r"{\c&H0000D4FF&}" + escaped + r"{\c&H00FFFFFF&}")
                    else:
                        parts.append(escaped)
                line_text = " ".join(parts)

                start_ts = self._seconds_to_ass_time(w_start)
                end_ts = self._seconds_to_ass_time(w_end)
                events.append(f"Dialogue: 0,{start_ts},{end_ts},Default,,0,0,0,,{line_text}")

        ass_content = header + "\n".join(events) + "\n"
        with open(output_path, 'w') as f:
            f.write(ass_content)
        return output_path

    def _seconds_to_ass_time(self, seconds):
        """Convert seconds to ASS timestamp H:MM:SS.cc"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds % 1) * 100)
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    # ── SRT fallback ───────────────────────────────────────────────────

    def create_srt_file(self, text, start_time, end_time, srt_path):
        """Create SRT subtitle file with sentence-level captions (fallback)."""
        duration = end_time - start_time
        raw_sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        chunks = []
        for sent in raw_sentences:
            words = sent.split()
            if len(words) <= 10:
                chunks.append(sent)
            else:
                for i in range(0, len(words), 6):
                    chunk = ' '.join(words[i:i + 6])
                    if chunk:
                        chunks.append(chunk)
        if not chunks:
            chunks = [text]

        seen = set()
        deduped = []
        for c in chunks:
            c_clean = c.strip().lower()
            if c_clean and c_clean not in seen:
                seen.add(c_clean)
                deduped.append(c.strip())
        chunks = deduped or chunks

        time_per_chunk = duration / len(chunks)
        srt_lines = []
        for i, chunk in enumerate(chunks):
            cs = i * time_per_chunk
            ce = min((i + 1) * time_per_chunk, duration)
            srt_lines.append(f"{i+1}")
            srt_lines.append(f"{self._seconds_to_srt_time(cs)} --> {self._seconds_to_srt_time(ce)}")
            srt_lines.append(chunk)
            srt_lines.append("")

        if not self.dry_run:
            with open(srt_path, 'w') as f:
                f.write('\n'.join(srt_lines))

    def _seconds_to_srt_time(self, seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    # ── Smart cropping ─────────────────────────────────────────────────

    def detect_face_position(self, video_path, start_time, duration):
        """Detect face positions using MediaPipe.

        Returns (center_x_ratio, center_y_ratio, num_faces, face_spread)
        or None if no faces found.
        """
        try:
            import cv2
            import mediapipe as mp
        except ImportError:
            print("   Warning: mediapipe/cv2 not available, skipping face detection")
            return None

        sample_times = [start_time + i * (duration / 6) for i in range(1, 6)]
        temp_frames = []

        for t in sample_times:
            frame_path = f"/tmp/face_frame_{uuid.uuid4().hex[:8]}.jpg"
            cmd = ['ffmpeg', '-y', '-ss', str(t), '-i', video_path,
                   '-frames:v', '1', '-q:v', '2', frame_path]
            try:
                subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
                if os.path.exists(frame_path):
                    temp_frames.append(frame_path)
            except Exception as e:
                logger.error(f"Frame extraction error: {e}")

        if not temp_frames:
            return None

        mp_face = mp.solutions.face_detection
        all_face_centers_x = []
        all_face_centers_y = []
        all_face_widths = []
        face_counts = []

        with mp_face.FaceDetection(model_selection=1, min_detection_confidence=0.5) as detector:
            for fp in temp_frames:
                img = cv2.imread(fp)
                if img is None:
                    continue
                rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = detector.process(rgb)

                frame_faces = 0
                if results.detections:
                    for det in results.detections:
                        bb = det.location_data.relative_bounding_box
                        cx = bb.xmin + bb.width / 2
                        cy = bb.ymin + bb.height / 2
                        all_face_centers_x.append(cx)
                        all_face_centers_y.append(cy)
                        all_face_widths.append(bb.width)
                        frame_faces += 1
                face_counts.append(frame_faces)
                os.unlink(fp)

        if not all_face_centers_x:
            for fp in temp_frames:
                if os.path.exists(fp):
                    os.unlink(fp)
            return None

        avg_cx = sum(all_face_centers_x) / len(all_face_centers_x)
        avg_cy = sum(all_face_centers_y) / len(all_face_centers_y)
        avg_faces = sum(face_counts) / len(face_counts) if face_counts else 1
        spread = max(all_face_centers_x) - min(all_face_centers_x) + max(all_face_widths)

        print(f"   Face detection: center=({avg_cx:.2f}, {avg_cy:.2f}), faces={avg_faces:.1f}, spread={spread:.2f}")
        return (avg_cx, avg_cy, avg_faces, spread)

    def build_crop_filter_with_faces(self, src_w, src_h, face_info):
        """Build ffmpeg crop filter centered on detected faces."""
        target_w, target_h = 1080, 1920
        avg_cx, avg_cy, num_faces, spread = face_info

        if num_faces >= 1.5:
            scale_factor = max(1.0, 1.0 + spread * 0.5)
        else:
            scale_factor = 1.08

        scaled_h = int(target_h * scale_factor)
        scale_filter = f"scale=-2:{scaled_h}"

        scaled_w = int(scaled_h * src_w / src_h)
        max_x = max(0, scaled_w - target_w)

        face_pixel_x = int(avg_cx * scaled_w)
        crop_x = max(0, min(max_x, face_pixel_x - target_w // 2))

        max_y = max(0, scaled_h - target_h)
        face_pixel_y = int(avg_cy * scaled_h)
        desired_face_y = int(target_h * 0.35)
        crop_y = max(0, min(max_y, face_pixel_y - desired_face_y))

        crop_filter = f"crop={target_w}:{target_h}:{crop_x}:{crop_y}"
        return f"{scale_filter},{crop_filter}"

    def analyze_audio_panning(self, video_path, start_time, duration):
        """Analyze left/right audio levels to estimate speaker position.
        Returns 'left', 'right', or 'center'."""
        try:
            cmd_l = ['ffmpeg', '-y', '-ss', str(start_time), '-t', str(duration),
                     '-i', video_path, '-af', 'pan=mono|c0=c0,astats=metadata=1:reset=1',
                     '-f', 'null', '-']
            cmd_r = ['ffmpeg', '-y', '-ss', str(start_time), '-t', str(duration),
                     '-i', video_path, '-af', 'pan=mono|c0=c1,astats=metadata=1:reset=1',
                     '-f', 'null', '-']

            result_l = subprocess.run(cmd_l, capture_output=True, text=True)
            result_r = subprocess.run(cmd_r, capture_output=True, text=True)

            def extract_rms(stderr):
                matches = re.findall(r'RMS level dB:\s*([-\d.]+)', stderr)
                if matches:
                    return float(matches[-1])
                return -60.0

            rms_l = extract_rms(result_l.stderr)
            rms_r = extract_rms(result_r.stderr)

            diff = rms_l - rms_r
            if diff > 3:
                return 'left'
            elif diff < -3:
                return 'right'
            else:
                return 'center'
        except Exception:
            return 'center'

    def get_video_dimensions(self, video_path):
        """Get video width and height."""
        cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
               '-show_entries', 'stream=width,height', '-of', 'json', video_path]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            info = json.loads(result.stdout)
            stream = info['streams'][0]
            return stream['width'], stream['height']
        except Exception:
            return 1920, 1080

    def build_crop_filter(self, src_w, src_h, speaker_pos):
        """Build ffmpeg filter for smart 9:16 crop from 16:9 source."""
        target_w, target_h = 1080, 1920
        scale_factor = 1.05
        scaled_h = int(target_h * scale_factor)
        scale_filter = f"scale=-2:{scaled_h}"

        scaled_w = int(scaled_h * src_w / src_h)
        max_x = max(0, scaled_w - target_w)

        if speaker_pos == 'left':
            crop_x = int(max_x * 0.25)
        elif speaker_pos == 'right':
            crop_x = int(max_x * 0.75)
        else:
            crop_x = max_x // 2

        crop_filter = f"crop={target_w}:{target_h}:{crop_x}:0"
        return f"{scale_filter},{crop_filter}"

    # ── Clip creation ──────────────────────────────────────────────────

    def create_single_clip(self, video_path, segment, clip_type, output_path):
        """Create a single clip with ffmpeg. Uses ASS captions + smart crop."""
        start_time = segment['start_time']
        end_time = segment['end_time']
        duration = end_time - start_time

        if clip_type == 'vertical_short' and duration > MAX_SHORT_DURATION:
            end_time = start_time + MAX_SHORT_DURATION
            duration = MAX_SHORT_DURATION
        elif clip_type == 'horizontal_mid' and duration > MAX_MID_DURATION:
            end_time = start_time + MAX_MID_DURATION
            duration = MAX_MID_DURATION

        if self.dry_run:
            print(f"DRY RUN: Would create {clip_type} clip: {output_path}")
            return True

        # Generate captions
        word_timestamps = segment.get('word_timestamps')
        ass_path = output_path.replace('.mp4', '.ass')
        srt_path = output_path.replace('.mp4', '.srt')
        sub_filter = ""

        if word_timestamps:
            self.create_ass_captions(word_timestamps, start_time, end_time, clip_type, ass_path)
            ass_escaped = ass_path.replace('\\', '/').replace(':', '\\:').replace("'", "\\'")
            sub_filter = f",ass='{ass_escaped}'"
        else:
            self.create_srt_file(segment['text'], start_time, end_time, srt_path)
            srt_escaped = srt_path.replace('\\', '/').replace(':', '\\:').replace("'", "\\'")
            sub_style = "FontName=Arial Black,FontSize=14,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Shadow=1,Alignment=2,MarginV=60"
            sub_filter = f",subtitles='{srt_escaped}':force_style='{sub_style}'"

        src_w, src_h = self.get_video_dimensions(video_path)

        if clip_type == 'vertical_short':
            face_info = self.detect_face_position(video_path, start_time, duration)
            if face_info:
                print(f"   Using face-detected crop")
                crop_filter = self.build_crop_filter_with_faces(src_w, src_h, face_info)
            else:
                speaker_pos = self.analyze_audio_panning(video_path, start_time, duration)
                print(f"   No faces found, using audio panning: {speaker_pos}")
                crop_filter = self.build_crop_filter(src_w, src_h, speaker_pos)
            vf = crop_filter + sub_filter
        else:
            vf = f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" + sub_filter

        cmd = [
            'ffmpeg', '-y',
            '-ss', str(start_time),
            '-i', video_path,
            '-t', str(duration),
            '-vf', vf,
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
            '-c:a', 'aac', '-b:a', '192k',
            output_path
        ]

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"Created {clip_type}: {os.path.basename(output_path)}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Clip creation failed: {e.stderr[-500:]}")
            # Retry without subtitles
            print("Retrying without subtitles...")
            if clip_type == 'vertical_short':
                fallback_vf = self.build_crop_filter(src_w, src_h, 'center')
            else:
                fallback_vf = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2"
            cmd_fb = [
                'ffmpeg', '-y', '-ss', str(start_time), '-i', video_path,
                '-t', str(duration), '-vf', fallback_vf,
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
                '-c:a', 'aac', '-b:a', '192k', output_path
            ]
            try:
                subprocess.run(cmd_fb, capture_output=True, text=True, check=True)
                print(f"Created {clip_type} (no subs): {os.path.basename(output_path)}")
                return True
            except subprocess.CalledProcessError as e2:
                print(f"Fallback failed: {e2.stderr[-300:]}")
                return False

    # ── Segment analysis and scoring ───────────────────────────────────

    def analyze_transcript_segments(self, transcript):
        segments = []
        STORY_STARTERS = [
            'so here\'s what happened', 'let me tell you', 'here\'s the thing',
            'true story', 'i remember when', 'when i was', 'the crazy thing is',
            'nobody talks about', 'most people don\'t', 'here\'s what most',
            'the truth is', 'i believe', 'unpopular opinion', 'hot take',
            'the biggest mistake', 'one thing that changed', 'the secret is',
            'here are', 'here\'s how', 'step one', 'the first thing',
            'what happened was', 'so we', 'i learned', 'the lesson',
        ]
        PAYOFF_MARKERS = [
            'and that\'s why', 'the point is', 'so the takeaway',
            'bottom line', 'that\'s the key', 'that changed everything',
            'and that was it', 'that\'s how', 'so remember',
            'the moral', 'and it worked', 'the result was',
        ]

        for i in range(len(transcript)):
            text_lower = transcript[i]['text'].lower()
            is_story_start = any(marker in text_lower for marker in STORY_STARTERS)
            if is_story_start:
                start_time = transcript[i]['start']
                window_text = []
                end_time = start_time
                found_payoff = False
                for j in range(i, min(i + 200, len(transcript))):
                    seg = transcript[j]
                    elapsed = seg['start'] - start_time
                    if elapsed > 90:
                        break
                    window_text.append(seg['text'])
                    end_time = seg.get('end', seg['start'] + 2)
                    if elapsed >= 15 and any(m in seg['text'].lower() for m in PAYOFF_MARKERS):
                        found_payoff = True
                        for k in range(j+1, min(j+5, len(transcript))):
                            if transcript[k]['start'] - start_time <= 90:
                                window_text.append(transcript[k]['text'])
                                end_time = transcript[k].get('end', transcript[k]['start'] + 2)
                        break
                duration = end_time - start_time
                if duration >= MIN_SHORT_DURATION:
                    full_text = ' '.join(window_text)
                    score = self.score_segment(full_text, start_time, end_time)
                    if found_payoff:
                        score['total'] += 5
                        score['standalone'] = min(10, score.get('standalone', 0) + 3)
                    segments.append({
                        'start_time': start_time, 'end_time': end_time,
                        'duration': duration, 'text': full_text,
                        'score': score, 'clips': self.determine_clip_types(duration),
                        'has_payoff': found_payoff
                    })

        # Sliding window fallback
        for i in range(0, len(transcript) - 1, 10):
            start_time = transcript[i]['start']
            window_text = []
            end_time = start_time
            for j in range(i, len(transcript)):
                seg = transcript[j]
                if seg['start'] - start_time <= 60:
                    window_text.append(seg['text'])
                    end_time = seg.get('end', seg['start'] + 2)
                else:
                    break
            if end_time - start_time >= MIN_SHORT_DURATION:
                full_text = ' '.join(window_text)
                score = self.score_segment(full_text, start_time, end_time)
                segments.append({
                    'start_time': start_time, 'end_time': end_time,
                    'duration': end_time - start_time, 'text': full_text,
                    'score': score, 'clips': self.determine_clip_types(end_time - start_time),
                    'has_payoff': False
                })

        # Dedup overlapping segments
        segments.sort(key=lambda x: x['score']['total'], reverse=True)
        kept = []
        used_buckets = set()
        for seg in segments:
            bucket = int(seg['start_time'] / 15)
            if bucket not in used_buckets:
                kept.append(seg)
                used_buckets.add(bucket)
                used_buckets.add(bucket - 1)
                used_buckets.add(bucket + 1)

        return [s for s in kept if s['score']['total'] >= MIN_CLIP_SCORE]

    def score_segment(self, text, start_time, end_time):
        hook_score = self.score_hook_strength(text)
        value_score = self.score_value_content(text)
        standalone_score = self.score_standalone_quality(text)
        voice_score = self.score_voice_match(text)
        return {
            'total': hook_score + value_score + standalone_score + voice_score,
            'hook': hook_score, 'value': value_score,
            'standalone': standalone_score, 'voice': voice_score
        }

    def score_hook_strength(self, text):
        score = 0
        tl = text.lower()
        if re.search(r'^(what|why|how|when|where)', tl): score += 3
        if re.search(r'(always|never|best|worst|only|secret|truth)', tl): score += 2
        if re.search(r'\d+%|\$\d+|\d+x|#\d+', text): score += 2
        if re.search(r'(but|however|actually|reality|truth is)', tl): score += 2
        if re.search(r'(most|biggest|fastest|smallest)', tl): score += 1
        return min(score, 10)

    def score_value_content(self, text):
        score = 0
        tl = text.lower()
        if re.search(r'(here\'s how|here are \d+|steps?|ways?|methods?)', tl): score += 3
        if re.search(r'(revenue|profit|growth|customers?|business)', tl): score += 2
        if re.search(r'\$\d+[MKB]?|\d+%|\d+x', text): score += 2
        if re.search(r'(when i|i learned|experience|mistake)', tl): score += 2
        if re.search(r'(should|need to|have to|must|can)', tl): score += 1
        return min(score, 10)

    def score_standalone_quality(self, text):
        score = 0
        if re.search(r'^(so|now|here|this|when|if)', text.lower()): score += 2
        if text.endswith('.') or text.endswith('!') or text.endswith('?'): score += 2
        pronouns = len(re.findall(r'\b(it|they|this|that|these|those)\b', text.lower()))
        words = len(text.split())
        if words > 0 and pronouns / words < 0.15: score += 3
        if re.search(r'(first|then|next|finally|because|so)', text.lower()): score += 2
        if 50 <= words <= 150: score += 1
        return min(score, 10)

    def score_voice_match(self, text):
        """Score how well the text matches the creator's voice patterns."""
        score = 0
        tl = text.lower()
        matches = sum(1 for p in VOICE_PATTERNS if re.search(p, tl))
        if matches >= 3: score += 5
        elif matches >= 2: score += 3
        elif matches >= 1: score += 2
        if re.search(r'here are \d+', tl): score += 2
        if re.search(r'criteria:', tl): score += 2
        if re.search(r'main benefits?:', tl): score += 1
        return min(score, 10)

    def determine_clip_types(self, duration):
        clip_types = []
        if duration >= MIN_SHORT_DURATION:
            clip_types.append('vertical_short')
        if 120 <= duration <= MAX_MID_DURATION:
            clip_types.append('horizontal_mid')
        return clip_types

    # ── Clip orchestration ─────────────────────────────────────────────

    def create_clips(self, video_path, segments, video_info, word_timestamps=None):
        """Create video clips from scored segments."""
        clips_created = []
        vertical_count = 0
        horizontal_count = 0

        if word_timestamps:
            for seg in segments:
                seg['word_timestamps'] = word_timestamps

        for segment in segments:
            if vertical_count >= 5 and horizontal_count >= 2:
                break
            for clip_type in segment['clips']:
                if clip_type == 'vertical_short' and vertical_count >= 5:
                    continue
                if clip_type == 'horizontal_mid' and horizontal_count >= 2:
                    continue

                clip_id = str(uuid.uuid4())[:8]
                clip_filename = f"{video_info['video_id']}_{clip_type}_{clip_id}.mp4"
                clip_path = os.path.join(CLIPS_DIR, clip_filename)

                success = self.create_single_clip(video_path, segment, clip_type, clip_path)
                if success:
                    clips_created.append({
                        'id': clip_id, 'type': clip_type,
                        'filename': clip_filename, 'path': clip_path,
                        'start_time': segment['start_time'],
                        'end_time': segment['end_time'],
                        'duration': segment['duration'],
                        'text': segment['text'],
                        'score': segment['score'],
                        'source_video': video_info,
                        'created_at': datetime.now().isoformat()
                    })
                    if clip_type == 'vertical_short':
                        vertical_count += 1
                    else:
                        horizontal_count += 1

        print(f"Created {len(clips_created)} clips ({vertical_count} vertical, {horizontal_count} horizontal)")
        return clips_created

    def save_results(self, clips_created, video_info):
        history = []
        if os.path.exists(CLIPS_HISTORY_FILE):
            try:
                with open(CLIPS_HISTORY_FILE, 'r') as f:
                    history = json.load(f).get('clips', [])
            except Exception:
                pass
        history.extend(clips_created)
        history_data = {
            'generated_at': datetime.now().isoformat(),
            'total_clips': len(history),
            'clips': history,
            'processed_video_ids': list(set(c['source_video']['video_id'] for c in history))
        }
        if not self.dry_run:
            with open(CLIPS_HISTORY_FILE, 'w') as f:
                json.dump(history_data, f, indent=2)

        latest_data = {
            'generated_at': datetime.now().isoformat(),
            'source_video': video_info,
            'clips_count': len(clips_created),
            'clips': clips_created
        }
        if not self.dry_run:
            with open(CLIPS_LATEST_FILE, 'w') as f:
                json.dump(latest_data, f, indent=2)
        print(f"Saved {len(clips_created)} clips")

    # ── Main processing ────────────────────────────────────────────────

    def process_video(self, video_url=None, video_atom=None):
        if video_atom:
            video_url = video_atom['source_url']
            video_info = {
                'video_id': self.extract_video_id(video_url),
                'title': video_atom.get('source_title', 'Unknown'),
                'url': video_url,
                'date': video_atom.get('source_date'),
                'atom_id': video_atom.get('id')
            }
        else:
            video_info = {
                'video_id': self.extract_video_id(video_url),
                'title': 'Manual Processing',
                'url': video_url,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'atom_id': None
            }

        if not video_info['video_id']:
            print(f"Could not extract video ID from: {video_url}")
            return False

        print(f"\nProcessing: {video_info['title']}")
        print(f"   Video ID: {video_info['video_id']}")

        with tempfile.TemporaryDirectory() as temp_dir:
            video_path = os.path.join(temp_dir, f"{video_info['video_id']}.mp4")

            # Step 1: Download
            if not self.download_video(video_url, video_path):
                return False

            # Step 2: Transcribe
            word_timestamps = None
            transcript = None

            if self.use_whisper and not self.dry_run:
                audio_path = os.path.join(temp_dir, "audio.wav")
                if self.extract_audio(video_path, audio_path):
                    whisper_result = self.transcribe_with_whisper(audio_path)
                    if whisper_result:
                        word_timestamps = whisper_result['words']
                        transcript = self.deduplicate_segments(whisper_result['segments'])
                        print(f"Whisper transcript: {len(transcript)} segments, {len(word_timestamps)} words")

            # Fallback to YouTube captions
            if transcript is None:
                print("Falling back to YouTube captions...")
                transcript = self.extract_transcript(video_url)
                if transcript:
                    transcript = self.deduplicate_segments(transcript)

            if not transcript:
                print("No transcript available, skipping")
                return False

            print(f"Using {len(transcript)} transcript segments")

            # Step 3: Analyze
            segments = self.analyze_transcript_segments(transcript)
            if not segments:
                print("No segments above score threshold")
                return False

            print(f"Found {len(segments)} high-scoring segments")
            for i, seg in enumerate(segments[:3]):
                s = seg['score']
                print(f"   #{i+1}: Score {s['total']}/40 (H:{s['hook']} V:{s['value']} S:{s['standalone']} Voice:{s['voice']})")
                print(f"        {seg['text'][:100]}...")

            # Step 4: Create clips
            clips_created = self.create_clips(video_path, segments, video_info, word_timestamps)

            # Step 5: Save
            self.save_results(clips_created, video_info)

        return True

    def process_new_videos(self):
        youtube_atoms = self.load_content_atoms()
        if not youtube_atoms:
            print("No YouTube videos found")
            return
        processed_ids = self.load_processed_videos()
        new_videos = [a for a in youtube_atoms
                      if self.extract_video_id(a.get('source_url', '')) and
                      self.extract_video_id(a.get('source_url', '')) not in processed_ids]
        if not new_videos:
            print("All videos already processed")
            return
        print(f"Found {len(new_videos)} new videos")
        success = 0
        for atom in new_videos:
            try:
                if self.process_video(video_atom=atom):
                    success += 1
            except Exception as e:
                print(f"Error: {e}")
        print(f"\nProcessed {success}/{len(new_videos)} videos")


def main():
    parser = argparse.ArgumentParser(description='Video Clipper — standalone clip extraction')
    parser.add_argument('--url', help='Process single YouTube URL')
    parser.add_argument('--video-id', help='Process single video by ID from content atoms')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--test-one', action='store_true', help='Process first unprocessed video only')
    parser.add_argument('--use-whisper', dest='use_whisper', action='store_true', default=True)
    parser.add_argument('--no-whisper', dest='use_whisper', action='store_false',
                        help='Skip Whisper, use YouTube captions only')

    args = parser.parse_args()
    clipper = VideoClipper(dry_run=args.dry_run, use_whisper=args.use_whisper)

    if args.url:
        sys.exit(0 if clipper.process_video(video_url=args.url) else 1)
    elif args.video_id:
        atoms = clipper.load_content_atoms()
        target = next((a for a in atoms if clipper.extract_video_id(a.get('source_url', '')) == args.video_id), None)
        if target:
            sys.exit(0 if clipper.process_video(video_atom=target) else 1)
        else:
            print(f"Video ID {args.video_id} not found")
            sys.exit(1)
    elif args.test_one:
        atoms = clipper.load_content_atoms()
        processed = clipper.load_processed_videos()
        for atom in atoms:
            vid = clipper.extract_video_id(atom.get('source_url', ''))
            if vid and vid not in processed:
                sys.exit(0 if clipper.process_video(video_atom=atom) else 1)
        print("All processed")
    else:
        clipper.process_new_videos()


if __name__ == '__main__':
    main()
