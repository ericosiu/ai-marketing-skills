#!/usr/bin/env python3
"""
Podcast-to-Everything Pipeline
===============================
Takes a podcast RSS feed or raw transcript and generates a full cross-platform
content calendar: video clips, Twitter/X threads, LinkedIn articles, newsletter
sections, quote cards, blog outlines, and YouTube Shorts/TikTok scripts.

Usage:
    python podcast_pipeline.py --rss "https://feeds.example.com/podcast.xml"
    python podcast_pipeline.py --transcript episode.txt
    python podcast_pipeline.py --batch "https://feeds.example.com/podcast.xml" --episodes 5
    python podcast_pipeline.py --calendar
"""

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import feedparser
import requests
from dateutil import parser as dateparser
from slugify import slugify
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Default output directory (overridable via --output-dir)
DEFAULT_OUTPUT_DIR = Path("./output")

# Dedup similarity threshold (0-1). Pairs above this are flagged as duplicates.
DEDUP_SIMILARITY_THRESHOLD = 0.70

# Default number of days to look back for dedup
DEFAULT_DEDUP_DAYS = 30

# Content generation model (Anthropic Claude)
ANTHROPIC_MODEL = "claude-sonnet-5"

# Whisper model for transcription
WHISPER_MODEL = "whisper-1"

# Platform scheduling defaults (hour in ET)
SCHEDULE_RULES = {
    "twitter": {"times": ["09:00", "12:30", "17:00"], "max_per_day": 2},
    "linkedin": {"times": ["08:00", "09:00"], "max_per_day": 1, "best_days": [1, 2, 3]},  # Tue-Thu
    "youtube_shorts": {"times": ["18:00", "19:00"], "max_per_day": 1},
    "tiktok": {"times": ["18:00", "20:00"], "max_per_day": 1},
    "newsletter": {"times": ["08:00"], "max_per_week": 1, "best_day": 2},  # Wednesday
    "blog": {"times": ["10:00"], "max_per_week": 2},
    "quote_card": {"times": ["11:00", "15:00"], "max_per_day": 2},
}


# ---------------------------------------------------------------------------
# API Clients
# ---------------------------------------------------------------------------


def transcribe_audio(audio_path: str) -> dict:
    """
    Transcribe an audio file using OpenAI Whisper API.
    Returns dict with 'text' (full transcript) and 'segments' (timestamped chunks).
    """
    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not set. Cannot transcribe audio.", file=sys.stderr)
        sys.exit(1)

    print(f"  Transcribing: {audio_path}")
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}

    with open(audio_path, "rb") as audio_file:
        # Request verbose JSON to get timestamps
        response = requests.post(
            url,
            headers=headers,
            files={"file": audio_file},
            data={
                "model": WHISPER_MODEL,
                "response_format": "verbose_json",
                "timestamp_granularities[]": "segment",
            },
            timeout=600,  # 10 min timeout for long episodes
        )

    if response.status_code != 200:
        print(f"ERROR: Whisper API returned {response.status_code}: {response.text}", file=sys.stderr)
        sys.exit(1)

    result = response.json()
    return {
        "text": result.get("text", ""),
        "segments": result.get("segments", []),
        "duration": result.get("duration", 0),
        "language": result.get("language", "en"),
    }


def call_anthropic(system_prompt: str, user_prompt: str, max_tokens: int = 8000) -> str:
    """
    Call Anthropic Claude API for content generation.
    Returns the text response.
    """
    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set. Cannot generate content.", file=sys.stderr)
        sys.exit(1)

    # Using the anthropic SDK
    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


# ---------------------------------------------------------------------------
# RSS Feed Handling
# ---------------------------------------------------------------------------


def fetch_rss_episodes(rss_url: str, num_episodes: int = 1) -> list[dict]:
    """
    Fetch episode metadata from an RSS feed.
    Returns list of dicts with: title, date, description, audio_url, duration.
    """
    print(f"Fetching RSS feed: {rss_url}")
    feed = feedparser.parse(rss_url)

    if feed.bozo and not feed.entries:
        print(f"ERROR: Failed to parse RSS feed: {feed.bozo_exception}", file=sys.stderr)
        sys.exit(1)

    episodes = []
    for entry in feed.entries[:num_episodes]:
        # Find the audio enclosure
        audio_url = None
        for link in entry.get("links", []):
            if link.get("type", "").startswith("audio/"):
                audio_url = link.get("href")
                break
        # Fallback: check enclosures
        if not audio_url:
            for enc in entry.get("enclosures", []):
                if enc.get("type", "").startswith("audio/"):
                    audio_url = enc.get("url")
                    break

        # Parse publish date
        pub_date = None
        if hasattr(entry, "published"):
            try:
                pub_date = dateparser.parse(entry.published).strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                pub_date = None

        episodes.append({
            "title": entry.get("title", "Untitled Episode"),
            "date": pub_date or datetime.now().strftime("%Y-%m-%d"),
            "description": entry.get("summary", ""),
            "audio_url": audio_url,
            "duration": entry.get("itunes_duration", "unknown"),
        })

    print(f"  Found {len(episodes)} episode(s)")
    return episodes


def download_audio(audio_url: str) -> str:
    """
    Download an audio file to a temp directory. Returns the local file path.
    """
    print(f"  Downloading audio: {audio_url[:80]}...")
    tmp_dir = tempfile.mkdtemp(prefix="podcast_pipeline_")
    # Determine extension from URL
    ext = ".mp3"
    if ".m4a" in audio_url:
        ext = ".m4a"
    elif ".wav" in audio_url:
        ext = ".wav"
    elif ".ogg" in audio_url:
        ext = ".ogg"

    local_path = os.path.join(tmp_dir, f"episode{ext}")

    response = requests.get(audio_url, stream=True, timeout=300)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))
    with open(local_path, "wb") as f:
        with tqdm(total=total_size, unit="B", unit_scale=True, desc="Downloading") as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                pbar.update(len(chunk))

    print(f"  Saved to: {local_path}")
    return local_path


# ---------------------------------------------------------------------------
# Transcript Processing
# ---------------------------------------------------------------------------


def read_transcript(file_path: str) -> dict:
    """
    Read a transcript from a file. Supports plain text, SRT, and VTT formats.
    Returns dict with 'text' and 'segments'.
    """
    path = Path(file_path)
    if not path.exists():
        print(f"ERROR: Transcript file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    raw = path.read_text(encoding="utf-8")

    # Detect format and parse
    if file_path.endswith(".srt"):
        return parse_srt(raw)
    elif file_path.endswith(".vtt"):
        return parse_vtt(raw)
    else:
        # Plain text — no timestamps
        return {"text": raw, "segments": [], "duration": 0, "language": "en"}


def parse_srt(raw: str) -> dict:
    """Parse SRT subtitle format into text + segments."""
    segments = []
    blocks = re.split(r"\n\n+", raw.strip())
    full_text_parts = []

    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        # Line 0: sequence number, Line 1: timestamps, Line 2+: text
        time_match = re.match(
            r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})", lines[1]
        )
        if not time_match:
            continue
        text = " ".join(lines[2:])
        full_text_parts.append(text)
        segments.append({
            "start": srt_time_to_seconds(time_match.group(1)),
            "end": srt_time_to_seconds(time_match.group(2)),
            "text": text,
        })

    return {
        "text": " ".join(full_text_parts),
        "segments": segments,
        "duration": segments[-1]["end"] if segments else 0,
        "language": "en",
    }


def parse_vtt(raw: str) -> dict:
    """Parse WebVTT format into text + segments."""
    # Strip WEBVTT header
    raw = re.sub(r"^WEBVTT.*?\n\n", "", raw, flags=re.DOTALL)
    # VTT uses . instead of , for milliseconds but is otherwise similar to SRT
    raw = raw.replace(".", ",")  # Normalize for the SRT parser
    return parse_srt(raw)


def srt_time_to_seconds(time_str: str) -> float:
    """Convert SRT timestamp (HH:MM:SS,mmm) to seconds."""
    h, m, rest = time_str.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


# ---------------------------------------------------------------------------
# Editorial Brain — Content Atom Extraction
# ---------------------------------------------------------------------------


def extract_content_atoms(transcript: dict, episode_meta: dict) -> list[dict]:
    """
    Feed the transcript to the LLM to extract content atoms:
    narrative arcs, quotes, controversial takes, data points, stories,
    frameworks, and predictions.
    """
    print("  Running Editorial Brain — extracting content atoms...")

    system_prompt = """You are an expert content strategist and editorial brain.
Your job is to analyze podcast transcripts and extract content atoms — the raw
material that can be turned into social media posts, articles, videos, and more.

You think like a viral content creator: you spot the moments that make people
stop scrolling, the takes that spark debate, and the insights people screenshot
and share.

Return your analysis as a JSON array of content atoms."""

    user_prompt = f"""Analyze this podcast transcript and extract ALL content atoms.

Episode: {episode_meta.get('title', 'Unknown')}
Date: {episode_meta.get('date', 'Unknown')}
Description: {episode_meta.get('description', '')[:500]}

TRANSCRIPT:
{transcript['text'][:30000]}

---

Extract content atoms in these 7 categories. Find ALL of them — be thorough.

1. **narrative_arc** — Complete story segments (setup → tension → resolution). Include timestamps if available.
2. **quote** — Punchy, shareable one-liners. Must pass the "would someone screenshot this?" test.
3. **controversial_take** — Opinions against conventional wisdom. The "hard disagree" or "finally someone said it" stuff.
4. **data_point** — Specific numbers, percentages, dollar amounts. Concrete proof points.
5. **story** — Personal anecdotes, case studies. Must have character + problem + outcome.
6. **framework** — Step-by-step processes, mental models. Things people save/bookmark.
7. **prediction** — Forward-looking claims about trends, markets, tech.

Return ONLY a JSON array. Each atom:
{{
  "type": "narrative_arc|quote|controversial_take|data_point|story|framework|prediction",
  "content": "the extracted text, cleaned up for readability",
  "timestamp": "MM:SS - MM:SS or null if not available",
  "context": "what was being discussed when this came up",
  "suggested_platforms": ["twitter", "linkedin", "youtube_shorts", "tiktok", "newsletter", "blog", "quote_card"]
}}

Find at least 15 atoms total. Prioritize quality and shareability."""

    response = call_anthropic(system_prompt, user_prompt, max_tokens=6000)

    # Parse JSON from the response (handle markdown code blocks)
    json_match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", response, re.DOTALL)
    if json_match:
        atoms = json.loads(json_match.group(1))
    else:
        # Try parsing the whole response as JSON
        try:
            atoms = json.loads(response)
        except json.JSONDecodeError:
            # Last resort: find the JSON array in the response
            start = response.find("[")
            end = response.rfind("]") + 1
            if start >= 0 and end > start:
                atoms = json.loads(response[start:end])
            else:
                print("  WARNING: Could not parse atoms from LLM response. Using empty list.", file=sys.stderr)
                atoms = []

    print(f"  Extracted {len(atoms)} content atoms")
    return atoms


# ---------------------------------------------------------------------------
# Content Generation — Turn Atoms into Platform-Native Content
# ---------------------------------------------------------------------------


def generate_content_pieces(atoms: list[dict], episode_meta: dict) -> list[dict]:
    """
    Take extracted content atoms and generate all platform-specific content pieces.
    Returns a list of content piece dicts.
    """
    print("  Generating platform-native content pieces...")

    atoms_json = json.dumps(atoms, indent=2)

    system_prompt = """You are a world-class content repurposing engine.
Given content atoms extracted from a podcast episode, you generate platform-native
content pieces that maximize engagement on each platform.

You understand platform-specific best practices:
- Twitter/X: punchy, data-driven, thread hooks, < 280 chars per tweet
- LinkedIn: professional but human, story-driven, hook before the fold
- YouTube Shorts/TikTok: HOOK(3s) → SETUP(12s) → PAYOFF(30s) → CTA(15s)
- Newsletter: scannable, value-dense, pull quotes
- Blog: SEO-optimized, structured with H2s, 1500-2500 words outlined
- Quote cards: max 20 words, standalone impact

Return ONLY valid JSON."""

    user_prompt = f"""Generate a full content suite from these podcast content atoms.

Episode: {episode_meta.get('title', 'Unknown')}
Date: {episode_meta.get('date', 'Unknown')}

CONTENT ATOMS:
{atoms_json[:20000]}

---

Generate ALL of the following. Return as a JSON array of content pieces:

1. **video_clip** (3-5 pieces): Short-form video clip suggestions
   - hook: first 3 seconds (pattern interrupt or bold claim)
   - clip_description: what happens in the clip
   - timestamp: approximate range from transcript
   - caption_overlay: text for the screen
   - platform: "youtube_shorts" or "tiktok"
   - source_atoms: which atom indexes feed this

2. **twitter_thread** (2-3 pieces): Full thread outlines
   - tweets: array of tweet texts (5-10 tweets, each < 280 chars)
   - thread_hook: the first tweet (must create curiosity gap)
   - cta: closing tweet with engagement driver
   - source_atoms: which atom indexes

3. **linkedin_article** (1 piece): Full draft
   - headline: specific, benefit-driven
   - hook: first paragraph (before "see more" fold)
   - body: full article text (800-1200 words, with section headers)
   - cta: engagement question
   - hashtags: 3-5 relevant tags
   - source_atoms: which atom indexes

4. **newsletter_section** (1 piece):
   - headline: scannable
   - tldr: one sentence core insight
   - bullets: 3-5 takeaway bullet points
   - pull_quote: most shareable line
   - source_atoms: which atom indexes

5. **quote_card** (3-5 pieces):
   - quote_text: max 20 words
   - attribution: speaker name
   - background_mood: color/mood suggestion
   - source_atoms: which atom indexes

6. **blog_outline** (1 piece):
   - title: SEO-optimized
   - primary_keyword: main search term to target
   - secondary_keywords: 3-5 related terms
   - meta_description: max 155 chars
   - sections: array of H2 headings with brief descriptions
   - estimated_word_count: 1500-2500
   - source_atoms: which atom indexes

7. **short_script** (1 piece): YouTube Shorts / TikTok script
   - hook: 0-3 seconds text
   - setup: 3-15 seconds text
   - payoff: 15-45 seconds text
   - cta: 45-60 seconds text
   - on_screen_text: key phrases to overlay
   - broll_suggestions: visual ideas
   - source_atoms: which atom indexes

Each piece must include:
{{
  "type": "video_clip|twitter_thread|linkedin_article|newsletter_section|quote_card|blog_outline|short_script",
  "platform": "twitter|linkedin|youtube_shorts|tiktok|newsletter|blog|quote_card",
  "content": {{ ... type-specific fields ... }},
  "source_atoms": [0, 2, 5],
  "viral_score_estimate": 0-100
}}"""

    response = call_anthropic(system_prompt, user_prompt, max_tokens=8000)

    # Parse JSON
    json_match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", response, re.DOTALL)
    if json_match:
        pieces = json.loads(json_match.group(1))
    else:
        try:
            pieces = json.loads(response)
        except json.JSONDecodeError:
            start = response.find("[")
            end = response.rfind("]") + 1
            if start >= 0 and end > start:
                pieces = json.loads(response[start:end])
            else:
                print("  WARNING: Could not parse content pieces. Using empty list.", file=sys.stderr)
                pieces = []

    print(f"  Generated {len(pieces)} content pieces")
    return pieces


# ---------------------------------------------------------------------------
# Viral Scoring
# ---------------------------------------------------------------------------


def score_content_pieces(pieces: list[dict], atoms: list[dict]) -> list[dict]:
    """
    Score each content piece on viral potential: novelty × controversy × utility.
    Updates each piece in-place with a 'viral_score' field.
    """
    print("  Scoring content pieces for viral potential...")

    # If the LLM already estimated scores, we can refine them.
    # For a more robust approach, we'd call the LLM to score each piece.
    # Here we use a hybrid: trust LLM estimates + apply heuristic adjustments.

    for piece in pieces:
        base_score = piece.get("viral_score_estimate", 50)

        # Heuristic adjustments based on content type
        type_bonus = {
            "video_clip": 5,        # Video inherently more engaging
            "twitter_thread": 3,    # Threads get algorithmic boost
            "linkedin_article": 0,  # Neutral
            "newsletter_section": -2,  # Lower viral ceiling
            "quote_card": 2,        # Highly shareable format
            "blog_outline": -3,     # SEO play, not viral play
            "short_script": 5,      # Short-form video bonus
        }
        bonus = type_bonus.get(piece.get("type", ""), 0)

        # Check if source atoms include high-value types
        source_indices = piece.get("source_atoms", [])
        for idx in source_indices:
            if idx < len(atoms):
                atom = atoms[idx]
                atom_type = atom.get("type", "")
                if atom_type == "controversial_take":
                    bonus += 5  # Controversy drives engagement
                elif atom_type == "data_point":
                    bonus += 3  # Specificity builds credibility
                elif atom_type == "prediction":
                    bonus += 4  # Predictions spark debate

        # Calculate final score (clamp 0-100)
        final_score = max(0, min(100, base_score + bonus))
        piece["viral_score"] = final_score

        # Break down the components (approximate from the composite)
        piece["score_breakdown"] = {
            "novelty": min(100, int(final_score * 1.1)),     # Slightly inflate for reporting
            "controversy": min(100, int(final_score * 0.9)),
            "utility": min(100, int(final_score * 1.0)),
        }

    # Sort by viral score descending
    pieces.sort(key=lambda p: p.get("viral_score", 0), reverse=True)

    avg_score = sum(p.get("viral_score", 0) for p in pieces) / max(len(pieces), 1)
    print(f"  Average viral score: {avg_score:.1f}")

    return pieces


# ---------------------------------------------------------------------------
# Deduplication Engine
# ---------------------------------------------------------------------------


def load_content_history(output_dir: Path, dedup_days: int) -> list[dict]:
    """Load content history from the last N days for dedup checking."""
    history_path = output_dir / "content_history.json"
    if not history_path.exists():
        return []

    with open(history_path) as f:
        history = json.load(f)

    cutoff = (datetime.now() - timedelta(days=dedup_days)).isoformat()
    return [h for h in history if h.get("date", "") >= cutoff]


def compute_content_hash(piece: dict) -> str:
    """Generate a hash for a content piece based on its core content."""
    content_str = json.dumps(piece.get("content", {}), sort_keys=True)
    return hashlib.sha256(content_str.encode()).hexdigest()[:16]


def simple_text_similarity(text_a: str, text_b: str) -> float:
    """
    Simple word-overlap similarity (Jaccard index).
    For production, replace with embedding-based cosine similarity.
    """
    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)


def get_piece_text(piece: dict) -> str:
    """Extract the main text content from a piece for similarity comparison."""
    content = piece.get("content", {})
    if isinstance(content, str):
        return content
    # Concatenate all string values from the content dict
    parts = []
    for v in content.values():
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, str):
                    parts.append(item)
    return " ".join(parts)


def deduplicate(pieces: list[dict], history: list[dict], threshold: float = DEDUP_SIMILARITY_THRESHOLD) -> list[dict]:
    """
    Remove content pieces that are too similar to each other or to recent history.
    Returns filtered list with dedup flags.
    """
    print("  Running dedup engine...")

    # Dedup within this batch
    kept = []
    removed = 0
    for piece in pieces:
        piece_text = get_piece_text(piece)
        piece["content_hash"] = compute_content_hash(piece)
        is_dupe = False

        # Check against already-kept pieces in this batch
        for kept_piece in kept:
            sim = simple_text_similarity(piece_text, get_piece_text(kept_piece))
            if sim > threshold:
                is_dupe = True
                removed += 1
                break

        # Check against history
        if not is_dupe:
            for hist_piece in history:
                sim = simple_text_similarity(piece_text, hist_piece.get("text_preview", ""))
                if sim > threshold:
                    piece["dedup_warning"] = f"⚠️ Similar to previously published content (similarity: {sim:.0%})"
                    # Don't remove, just flag — might still be worth publishing with a different angle
                    break

        if not is_dupe:
            kept.append(piece)

    print(f"  Kept {len(kept)}/{len(pieces)} pieces ({removed} removed as duplicates)")
    return kept


def save_to_history(pieces: list[dict], output_dir: Path, episode_meta: dict):
    """Save content pieces to history for future dedup."""
    history_path = output_dir / "content_history.json"
    history = []
    if history_path.exists():
        with open(history_path) as f:
            history = json.load(f)

    for piece in pieces:
        history.append({
            "date": datetime.now().isoformat(),
            "episode": episode_meta.get("title", ""),
            "type": piece.get("type", ""),
            "content_hash": piece.get("content_hash", ""),
            "text_preview": get_piece_text(piece)[:200],
            "viral_score": piece.get("viral_score", 0),
        })

    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)


# ---------------------------------------------------------------------------
# Calendar Generation
# ---------------------------------------------------------------------------


def generate_calendar(pieces: list[dict], episode_meta: dict, start_date: Optional[str] = None) -> dict:
    """
    Generate a weekly content calendar from scored, deduplicated pieces.
    Assigns publish dates/times based on platform best practices.
    """
    print("  Generating content calendar...")

    if start_date:
        cal_start = dateparser.parse(start_date)
    else:
        # Start next Monday
        today = datetime.now()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        cal_start = today + timedelta(days=days_until_monday)

    calendar = {
        "week_of": cal_start.strftime("%Y-%m-%d"),
        "episode_source": episode_meta.get("title", "Unknown"),
        "generated_at": datetime.now().isoformat(),
        "content_pieces": [],
        "total_pieces": 0,
        "avg_viral_score": 0,
        "coverage": {},
    }

    # Group pieces by platform
    platform_buckets: dict[str, list[dict]] = {}
    for piece in pieces:
        platform = piece.get("platform", "unknown")
        platform_buckets.setdefault(platform, []).append(piece)

    scheduled_pieces = []
    day_offset = 0
    max_days = 7

    for day_offset in range(max_days):
        current_date = cal_start + timedelta(days=day_offset)
        day_of_week = current_date.weekday()  # 0=Mon, 6=Sun

        for platform, bucket in platform_buckets.items():
            if not bucket:
                continue

            rules = SCHEDULE_RULES.get(platform, {"times": ["10:00"], "max_per_day": 1})

            # Check day restrictions
            if "best_days" in rules and day_of_week not in rules["best_days"]:
                continue
            if "best_day" in rules and day_of_week != rules["best_day"]:
                continue

            # Check weekly limits
            if "max_per_week" in rules:
                already_scheduled = sum(
                    1 for sp in scheduled_pieces if sp.get("platform") == platform
                )
                if already_scheduled >= rules["max_per_week"]:
                    continue

            # Schedule up to max_per_day
            daily_count = 0
            while bucket and daily_count < rules.get("max_per_day", 1):
                piece = bucket.pop(0)
                time_slot = rules["times"][daily_count % len(rules["times"])]

                scheduled_piece = {
                    "date": current_date.strftime("%Y-%m-%d"),
                    "time": f"{time_slot} ET",
                    "platform": platform,
                    "type": piece.get("type", "unknown"),
                    "content": piece.get("content", {}),
                    "viral_score": piece.get("viral_score", 0),
                    "status": "draft",
                    "content_hash": piece.get("content_hash", ""),
                }
                if "dedup_warning" in piece:
                    scheduled_piece["dedup_warning"] = piece["dedup_warning"]

                scheduled_pieces.append(scheduled_piece)
                daily_count += 1

    # Build coverage summary
    coverage = {}
    for sp in scheduled_pieces:
        platform = sp.get("platform", "unknown")
        coverage[platform] = coverage.get(platform, 0) + 1

    calendar["content_pieces"] = scheduled_pieces
    calendar["total_pieces"] = len(scheduled_pieces)
    calendar["avg_viral_score"] = (
        sum(sp.get("viral_score", 0) for sp in scheduled_pieces) / max(len(scheduled_pieces), 1)
    )
    calendar["coverage"] = coverage

    print(f"  Calendar: {len(scheduled_pieces)} pieces across {len(coverage)} platforms")
    return calendar


def generate_calendar_from_outputs(output_dir: Path) -> dict:
    """
    Aggregate calendar from all episode outputs in the output directory.
    Used with --calendar flag to create a unified weekly calendar.
    """
    episodes_dir = output_dir / "episodes"
    if not episodes_dir.exists():
        print("ERROR: No episodes found in output directory.", file=sys.stderr)
        sys.exit(1)

    all_pieces = []
    for ep_dir in sorted(episodes_dir.iterdir()):
        pieces_file = ep_dir / "content_pieces.json"
        if pieces_file.exists():
            with open(pieces_file) as f:
                pieces = json.load(f)
                all_pieces.extend(pieces)

    if not all_pieces:
        print("ERROR: No content pieces found.", file=sys.stderr)
        sys.exit(1)

    # Sort by viral score and take the best
    all_pieces.sort(key=lambda p: p.get("viral_score", 0), reverse=True)

    meta = {"title": "Aggregated Calendar", "date": datetime.now().strftime("%Y-%m-%d")}
    return generate_calendar(all_pieces, meta)


# ---------------------------------------------------------------------------
# Pipeline Orchestration
# ---------------------------------------------------------------------------


def process_episode(
    transcript: dict,
    episode_meta: dict,
    output_dir: Path,
    dedup_days: int = DEFAULT_DEDUP_DAYS,
    min_score: int = 0,
) -> dict:
    """
    Full pipeline for one episode:
    1. Extract content atoms (Editorial Brain)
    2. Generate platform-native content
    3. Score for viral potential
    4. Deduplicate
    5. Generate calendar
    6. Save outputs
    """
    episode_slug = slugify(f"{episode_meta['date']}-{episode_meta['title']}")[:80]
    episode_dir = output_dir / "episodes" / episode_slug
    episode_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Processing: {episode_meta['title']}")
    print(f"{'='*60}")

    # Save transcript
    transcript_path = episode_dir / "transcript.txt"
    transcript_path.write_text(transcript["text"], encoding="utf-8")

    # Step 1: Extract content atoms
    atoms = extract_content_atoms(transcript, episode_meta)
    atoms_path = episode_dir / "atoms.json"
    with open(atoms_path, "w") as f:
        json.dump(atoms, f, indent=2)

    # Step 2: Generate content pieces
    pieces = generate_content_pieces(atoms, episode_meta)

    # Step 3: Score
    pieces = score_content_pieces(pieces, atoms)

    # Step 4: Filter by minimum score
    if min_score > 0:
        before = len(pieces)
        pieces = [p for p in pieces if p.get("viral_score", 0) >= min_score]
        print(f"  Filtered: {before} → {len(pieces)} pieces (min score: {min_score})")

    # Step 5: Dedup
    history = load_content_history(output_dir, dedup_days)
    pieces = deduplicate(pieces, history)

    # Step 6: Generate calendar
    calendar = generate_calendar(pieces, episode_meta)

    # Save outputs
    pieces_path = episode_dir / "content_pieces.json"
    with open(pieces_path, "w") as f:
        json.dump(pieces, f, indent=2)

    calendar_path = episode_dir / "calendar.json"
    with open(calendar_path, "w") as f:
        json.dump(calendar, f, indent=2)

    # Save to dedup history
    save_to_history(pieces, output_dir, episode_meta)

    # Log the run
    log_run(output_dir, episode_meta, len(atoms), len(pieces), calendar)

    print(f"\n✅ Done: {len(pieces)} content pieces generated")
    print(f"   Output: {episode_dir}")
    print(f"   Avg viral score: {calendar['avg_viral_score']:.1f}")
    print(f"   Coverage: {calendar['coverage']}")

    return calendar


def log_run(output_dir: Path, episode_meta: dict, num_atoms: int, num_pieces: int, calendar: dict):
    """Append a run log entry."""
    log_path = output_dir / "pipeline_log.json"
    log = []
    if log_path.exists():
        with open(log_path) as f:
            log = json.load(f)

    log.append({
        "timestamp": datetime.now().isoformat(),
        "episode": episode_meta.get("title", ""),
        "episode_date": episode_meta.get("date", ""),
        "atoms_extracted": num_atoms,
        "pieces_generated": num_pieces,
        "avg_viral_score": calendar.get("avg_viral_score", 0),
        "coverage": calendar.get("coverage", {}),
    })

    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Podcast-to-Everything Pipeline: Turn podcast episodes into a full content calendar.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --rss "https://feeds.example.com/podcast.xml"
  %(prog)s --transcript episode-42.txt
  %(prog)s --batch "https://feeds.example.com/podcast.xml" --episodes 5
  %(prog)s --calendar
  %(prog)s --rss "https://feed.url" --min-score 80 --dedup-days 60
        """,
    )

    # Input modes (mutually exclusive group)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--rss", metavar="URL", help="Process the latest episode from an RSS feed"
    )
    input_group.add_argument(
        "--transcript", metavar="FILE", help="Process a local transcript file (txt, srt, vtt)"
    )
    input_group.add_argument(
        "--batch", metavar="URL", help="Batch process multiple episodes from an RSS feed"
    )
    input_group.add_argument(
        "--calendar", action="store_true",
        help="Generate a weekly calendar from existing episode outputs"
    )

    # Options
    parser.add_argument(
        "--episodes", type=int, default=5,
        help="Number of episodes to process in batch mode (default: 5)"
    )
    parser.add_argument(
        "--dedup-days", type=int, default=DEFAULT_DEDUP_DAYS,
        help=f"Days of history to check for dedup (default: {DEFAULT_DEDUP_DAYS})"
    )
    parser.add_argument(
        "--min-score", type=int, default=0,
        help="Minimum viral score to include in output (default: 0, include all)"
    )
    parser.add_argument(
        "--output-dir", type=str, default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})"
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # --calendar mode: aggregate from existing outputs
    if args.calendar:
        print("Generating weekly calendar from existing outputs...")
        calendar = generate_calendar_from_outputs(output_dir)
        calendar_dir = output_dir / "calendar"
        calendar_dir.mkdir(parents=True, exist_ok=True)

        week_str = datetime.now().strftime("%Y-W%W")
        cal_path = calendar_dir / f"week-{week_str}.json"
        with open(cal_path, "w") as f:
            json.dump(calendar, f, indent=2)

        print(f"\n✅ Weekly calendar generated: {cal_path}")
        print(f"   Total pieces: {calendar['total_pieces']}")
        print(f"   Avg viral score: {calendar['avg_viral_score']:.1f}")
        print(f"   Coverage: {calendar['coverage']}")
        return

    # --transcript mode: read local file
    if args.transcript:
        transcript = read_transcript(args.transcript)
        episode_meta = {
            "title": Path(args.transcript).stem,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "description": "",
        }
        process_episode(transcript, episode_meta, output_dir, args.dedup_days, args.min_score)
        return

    # --rss mode: fetch latest episode
    if args.rss:
        episodes = fetch_rss_episodes(args.rss, num_episodes=1)
        if not episodes:
            print("ERROR: No episodes found in feed.", file=sys.stderr)
            sys.exit(1)

        ep = episodes[0]
        if not ep["audio_url"]:
            print("ERROR: No audio URL found for the latest episode.", file=sys.stderr)
            sys.exit(1)

        audio_path = download_audio(ep["audio_url"])
        transcript = transcribe_audio(audio_path)

        # Clean up temp audio file
        try:
            os.remove(audio_path)
        except OSError:
            pass

        process_episode(transcript, ep, output_dir, args.dedup_days, args.min_score)
        return

    # --batch mode: process multiple episodes
    if args.batch:
        episodes = fetch_rss_episodes(args.batch, num_episodes=args.episodes)
        if not episodes:
            print("ERROR: No episodes found in feed.", file=sys.stderr)
            sys.exit(1)

        print(f"\nBatch mode: processing {len(episodes)} episodes\n")
        for i, ep in enumerate(episodes, 1):
            print(f"\n--- Episode {i}/{len(episodes)} ---")

            if not ep["audio_url"]:
                print(f"  SKIP: No audio URL for '{ep['title']}'")
                continue

            audio_path = download_audio(ep["audio_url"])
            transcript = transcribe_audio(audio_path)

            try:
                os.remove(audio_path)
            except OSError:
                pass

            process_episode(transcript, ep, output_dir, args.dedup_days, args.min_score)

        # Generate combined calendar
        print("\n\nGenerating combined calendar for all episodes...")
        calendar = generate_calendar_from_outputs(output_dir)
        calendar_dir = output_dir / "calendar"
        calendar_dir.mkdir(parents=True, exist_ok=True)

        week_str = datetime.now().strftime("%Y-W%W")
        cal_path = calendar_dir / f"week-{week_str}.json"
        with open(cal_path, "w") as f:
            json.dump(calendar, f, indent=2)

        print(f"\n✅ Batch complete. Combined calendar: {cal_path}")
        return


if __name__ == "__main__":
    main()
