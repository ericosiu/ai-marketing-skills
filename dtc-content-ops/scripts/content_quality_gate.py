#!/usr/bin/env python3
"""
content_quality_gate.py — Content quality scoring and compliance checking.

Scores DTC content on four dimensions (25 points each, total 100):
  1. Problem-First Hook — Does it lead with the customer's pain?
  2. Voice Authenticity — Does it sound like the brand founder, not ChatGPT?
  3. Value Density — Does every sentence teach something or solve a problem?
  4. Compliance + Platform Fit — Correct limits, no banned phrases, native formatting?

Usage:
    python3 content_quality_gate.py --input pending.json --banned-phrases banned.json
    python3 content_quality_gate.py --input pending.json --threshold 90
    python3 content_quality_gate.py --input pending.json --verbose
"""

import argparse
import json
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Default banned phrases (override with --banned-phrases JSON)
# ---------------------------------------------------------------------------

DEFAULT_BANNED_PHRASES = [
    "game changer", "game-changer", "revolutionary", "groundbreaking",
    "you won't believe", "limited time offer", "act now", "buy now",
    "don't miss out", "best ever", "miracle", "guaranteed results",
    "secret formula", "hack your", "life hack", "unlock your potential",
    "check out", "click the link", "link in bio",
]

DEFAULT_GENERIC_AI_PHRASES = [
    "in today's fast-paced world", "let's dive in", "let's dive into",
    "without further ado", "in conclusion", "it's important to note",
    "at the end of the day", "the journey of", "on this journey",
    "embark on", "elevate your", "supercharge your", "transform your",
    "level up your", "harness the power", "delve into", "navigate the",
    "in the realm of", "game-changing", "cutting-edge",
]

DEFAULT_CHAR_LIMITS = {
    "x": 280,
    "threads": 500,
    "instagram": 2200,
    "instagram_feed": 2200,
    "instagram_story": None,
    "instagram_reel": 2200,
    "tiktok": 2200,
    "shopify_blog": None,
    "blogger": None,
}


def load_banned_phrases(path):
    """Load banned phrases from JSON file."""
    if not path:
        return DEFAULT_BANNED_PHRASES, DEFAULT_GENERIC_AI_PHRASES

    p = Path(path)
    if not p.exists():
        print(f"Warning: Banned phrases file not found: {path}, using defaults")
        return DEFAULT_BANNED_PHRASES, DEFAULT_GENERIC_AI_PHRASES

    data = json.loads(p.read_text())
    banned = data.get("banned_phrases", DEFAULT_BANNED_PHRASES)
    generic = data.get("generic_ai_phrases", DEFAULT_GENERIC_AI_PHRASES)
    return banned, generic


def get_text_from_post(post):
    """Extract the main text content from a post object."""
    for field in ["text", "caption", "long_caption", "text_overlay"]:
        if post.get(field):
            return post[field]
    return ""


def check_banned_phrases(text, banned_phrases):
    """Check for banned marketing phrases. Returns list of found phrases."""
    text_lower = text.lower()
    return [phrase for phrase in banned_phrases if phrase.lower() in text_lower]


def check_generic_ai(text, generic_phrases):
    """Check for generic AI-sounding phrases. Returns list of found phrases."""
    text_lower = text.lower()
    return [phrase for phrase in generic_phrases if phrase.lower() in text_lower]


def check_char_limit(text, platform):
    """Check if text exceeds platform character limit. Returns (over, limit) or (False, None)."""
    limit = DEFAULT_CHAR_LIMITS.get(platform)
    if limit and len(text) > limit:
        return True, limit
    return False, limit


def score_problem_first_hook(text):
    """
    Score 0-25: Does the content lead with a problem/pain point?

    Heuristics:
    - Starts with a question (likely addressing a problem)
    - First sentence contains problem indicators (struggle, issue, problem, etc.)
    - Does NOT start with the product name or "Introducing"
    """
    score = 25
    deductions = []

    if not text:
        return 0, ["No text content"]

    first_sentence = text.split(".")[0].strip() if "." in text else text[:100]
    first_lower = first_sentence.lower()

    # Bonus indicators (problem-first)
    problem_words = ["struggle", "problem", "issue", "challenge", "frustrated",
                     "tired of", "sick of", "why do", "what if", "ever wonder",
                     "how to", "the real reason", "most people"]
    has_problem_framing = any(w in first_lower for w in problem_words)

    # Penalty indicators (product-first)
    product_first_words = ["introducing", "meet our", "new product", "our latest",
                           "announcing", "just launched", "now available"]
    is_product_first = any(w in first_lower for w in product_first_words)

    if is_product_first:
        score -= 15
        deductions.append("Leads with product instead of problem")
    elif not has_problem_framing and not first_sentence.endswith("?"):
        score -= 8
        deductions.append("No clear problem framing in opening")

    return max(0, score), deductions


def score_voice_authenticity(text, generic_phrases):
    """
    Score 0-25: Does it sound like a human brand founder?

    Penalizes generic AI voice patterns.
    """
    score = 25
    deductions = []

    found = check_generic_ai(text, generic_phrases)
    if found:
        penalty = min(20, len(found) * 5)
        score -= penalty
        deductions.append(f"Generic AI phrases found: {', '.join(found[:3])}")

    # Check for excessive exclamation marks (AI pattern)
    excl_count = text.count("!")
    if excl_count > 3:
        score -= 5
        deductions.append(f"Excessive exclamation marks ({excl_count})")

    # Check for emoji density (more than 1 per 50 chars is AI-like)
    import re
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002600-\U000026FF]+",
        flags=re.UNICODE
    )
    emojis = emoji_pattern.findall(text)
    if len(emojis) > max(1, len(text) // 100):
        score -= 5
        deductions.append("High emoji density suggests AI-generated content")

    return max(0, score), deductions


def score_value_density(text):
    """
    Score 0-25: Does every sentence teach or solve?

    Penalizes filler, fluff, and empty calories.
    """
    score = 25
    deductions = []

    if not text:
        return 0, ["No text content"]

    sentences = [s.strip() for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()]

    filler_patterns = [
        "in this post", "today we're going to", "let me tell you",
        "stay tuned", "follow for more", "share this with",
        "tag a friend", "drop a comment", "what do you think",
    ]

    filler_count = 0
    for sentence in sentences:
        s_lower = sentence.lower()
        if any(f in s_lower for f in filler_patterns):
            filler_count += 1

    if sentences:
        filler_ratio = filler_count / len(sentences)
        if filler_ratio > 0.3:
            score -= 15
            deductions.append(f"High filler ratio: {filler_count}/{len(sentences)} sentences are filler")
        elif filler_ratio > 0.1:
            score -= 8
            deductions.append(f"Some filler: {filler_count} filler sentence(s)")

    # Very short content for non-story platforms
    if len(text) < 50:
        score -= 5
        deductions.append("Very short content — may lack substance")

    return max(0, score), deductions


def score_compliance_platform_fit(text, platform, banned_phrases):
    """
    Score 0-25: Correct limits, no banned phrases, platform-native formatting.
    """
    score = 25
    deductions = []

    # Banned phrases
    found_banned = check_banned_phrases(text, banned_phrases)
    if found_banned:
        penalty = min(20, len(found_banned) * 7)
        score -= penalty
        deductions.append(f"Banned phrases: {', '.join(found_banned[:3])}")

    # Character limit
    over, limit = check_char_limit(text, platform)
    if over:
        score -= 10
        deductions.append(f"Over character limit: {len(text)}/{limit}")

    # Platform-specific checks
    if platform in ("instagram", "instagram_feed") and "#" not in text:
        score -= 3
        deductions.append("Instagram post missing hashtags")

    if platform == "x" and len(text) > 250 and "..." not in text:
        score -= 2
        deductions.append("X post very close to limit — consider tightening")

    return max(0, score), deductions


def score_post(text, platform, banned_phrases, generic_phrases):
    """Score a single post across all four dimensions. Returns (total, breakdown)."""
    hook_score, hook_notes = score_problem_first_hook(text)
    voice_score, voice_notes = score_voice_authenticity(text, generic_phrases)
    value_score, value_notes = score_value_density(text)
    compliance_score, compliance_notes = score_compliance_platform_fit(
        text, platform, banned_phrases
    )

    total = hook_score + voice_score + value_score + compliance_score

    breakdown = {
        "total": total,
        "problem_first_hook": {"score": hook_score, "max": 25, "notes": hook_notes},
        "voice_authenticity": {"score": voice_score, "max": 25, "notes": voice_notes},
        "value_density": {"score": value_score, "max": 25, "notes": value_notes},
        "compliance_platform_fit": {"score": compliance_score, "max": 25, "notes": compliance_notes},
    }

    # Overall verdict
    if total >= 90:
        breakdown["verdict"] = "PASS"
    elif total >= 70:
        breakdown["verdict"] = "WARN"
    else:
        breakdown["verdict"] = "FAIL"

    return total, breakdown


def cmd_score(args):
    """Score all content in a pending JSON file."""
    content = json.loads(Path(args.input).read_text())
    banned, generic = load_banned_phrases(args.banned_phrases)
    threshold = args.threshold or DEFAULT_QUALITY_THRESHOLD

    results = {}
    pass_count = 0
    warn_count = 0
    fail_count = 0

    for brand_key, brand_data in content.get("businesses", {}).items():
        brand_results = {}

        for platform, post in brand_data.get("platforms", {}).items():
            text = get_text_from_post(post)
            total, breakdown = score_post(text, platform, banned, generic)

            brand_results[platform] = breakdown

            if breakdown["verdict"] == "PASS":
                pass_count += 1
            elif breakdown["verdict"] == "WARN":
                warn_count += 1
            else:
                fail_count += 1

            if args.verbose:
                status = breakdown["verdict"]
                print(f"  [{status}] {brand_key}:{platform} — {total}/100")
                for dim, detail in breakdown.items():
                    if isinstance(detail, dict) and "notes" in detail:
                        for note in detail["notes"]:
                            print(f"         {note}")

        results[brand_key] = brand_results

    # Summary
    total_posts = pass_count + warn_count + fail_count
    print(f"\nQuality Gate Summary:")
    print(f"  Total posts:  {total_posts}")
    print(f"  PASS (>={threshold}): {pass_count}")
    print(f"  WARN (70-{threshold-1}): {warn_count}")
    print(f"  FAIL (<70):   {fail_count}")

    if args.output:
        Path(args.output).write_text(json.dumps(results, indent=2) + "\n")
        print(f"\nDetailed results saved to: {args.output}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="DTC content quality scoring and compliance checking"
    )
    parser.add_argument("--input", required=True, help="Path to pending content JSON")
    parser.add_argument("--banned-phrases", help="Path to banned phrases JSON")
    parser.add_argument("--threshold", type=int, default=DEFAULT_QUALITY_THRESHOLD,
                        help=f"Quality threshold (default: {DEFAULT_QUALITY_THRESHOLD})")
    parser.add_argument("--output", help="Path to save detailed results JSON")
    parser.add_argument("--verbose", action="store_true", help="Show detailed scoring")

    args = parser.parse_args()
    cmd_score(args)


if __name__ == "__main__":
    main()
