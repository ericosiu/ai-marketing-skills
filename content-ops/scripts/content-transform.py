#!/usr/bin/env python3
"""
Content Transform — Repurpose long-form content into platform-native drafts.

Reads content atoms, generates platform-native drafts using Claude API + optional
expert panel quality gate. Supports X threads/posts, LinkedIn, YouTube Shorts, and
newsletter formats.

LLM mode is DEFAULT. Use --template-only for fast template-based drafts (no API needed).

Usage:
    python content-transform.py --atoms atoms.json --top-n 10
    python content-transform.py --atoms atoms.json --template-only
    python content-transform.py --atoms atoms.json --no-expert-panel
"""

import json
import uuid
import argparse
import os
import re
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

# ── Configuration ──

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = Path(os.environ.get("CONTENT_OPS_DATA_DIR", PROJECT_DIR / "data"))
SKILL_DIR = PROJECT_DIR

ATOMS_FILE = DATA_DIR / "content-atoms-latest.json"

# Voice configuration files (optional, for LLM mode)
VOICE_CONFIG_FILE = os.environ.get("VOICE_CONFIG_FILE", str(PROJECT_DIR / "config" / "voice.md"))
STYLE_GUIDE_FILE = os.environ.get("STYLE_GUIDE_FILE", str(PROJECT_DIR / "config" / "style-guide.md"))

PLATFORM_MAP = {
    "x": ["x_thread", "x_post"],
    "linkedin": ["linkedin_post"],
    "short_form": ["youtube_short_script"],
    "newsletter": ["newsletter_section"],
    "youtube_short": ["youtube_short_script"],
}

MISSING_TO_FORMAT = {
    "x": "x_thread",
    "linkedin": "linkedin_post",
    "short_form": "youtube_short_script",
    "newsletter": "newsletter_section",
    "youtube_short": "youtube_short_script",
}

MISSING_TO_PLATFORM = {
    "x": "x",
    "linkedin": "linkedin",
    "short_form": "youtube_short",
    "newsletter": "newsletter",
    "youtube_short": "youtube_short",
}

PLATFORM_TO_EXPERT = {
    "x": "x-articles.md",
    "linkedin": "linkedin.md",
    "youtube_short": "youtube-shorts.md",
    "newsletter": "newsletter.md",
}

EXPERT_PANEL_THRESHOLD = 95
EXPERT_PANEL_MAX_ITERATIONS = 3


def load_atoms(path=None):
    p = Path(path) if path else ATOMS_FILE
    with open(p) as f:
        data = json.load(f)
    return data.get("atoms", data) if isinstance(data, dict) else data


def rank_atoms(atoms, top_n=10):
    """Sort by repurpose_score * len(platforms_missing), take top N."""
    for a in atoms:
        a["_rank"] = a.get("repurpose_score", 0) * max(len(a.get("platforms_missing", [])), 1)
    ranked = sorted(atoms, key=lambda x: x["_rank"], reverse=True)
    return ranked[:top_n]


def clean_content(content):
    content = re.sub(r'^[\w]+\s*·\s*@[\w]+\s*·.*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content.strip()


def extract_hook(content, max_chars=200):
    content = clean_content(content)
    for sep in [". ", ".\n", "\n"]:
        idx = content.find(sep)
        if 0 < idx < max_chars:
            return content[:idx + 1].strip()
    return content[:max_chars].strip()


def extract_key_points(content, max_points=6):
    lines = content.split("\n")
    points = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith(("•", "-", "→", "*")) or re.match(r"^\d+[\.\)]", line):
            cleaned = re.sub(r"^[•\-→\*\d+\.\)]+\s*", "", line).strip()
            if len(cleaned) > 15:
                points.append(cleaned)
        elif len(line) > 20 and len(line) < 280:
            points.append(line)
    return points[:max_points] if points else [content[:200]]


def extract_numbers(content):
    patterns = [
        r'\$[\d,]+[KkMmBb]?(?:\+)?',
        r'\d+%',
        r'\d+x',
        r'\d+[\.,]?\d*\s*(?:hours?|minutes?|days?|weeks?|months?|years?)',
        r'\d+\s*(?:pages?|pieces?|tools?|agents?|companies|founders?|members)',
    ]
    numbers = []
    for p in patterns:
        numbers.extend(re.findall(p, content, re.IGNORECASE))
    return numbers[:5]


def shorten_sentence(s, max_words=15):
    words = s.split()
    if len(words) <= max_words:
        return s
    return " ".join(words[:max_words]) + "."


def make_punchy(text, max_words=15):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    result = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if len(s.split()) > max_words:
            parts = re.split(r'[,;—]', s)
            for p in parts:
                p = p.strip()
                if p:
                    result.append(shorten_sentence(p) if not p.endswith(('.', '!', '?')) else p)
        else:
            result.append(s)
    return result


# ── TEMPLATE GENERATORS (used with --template-only) ──

def generate_x_thread(atom):
    content = clean_content(atom["content"])
    hook_text = extract_hook(content, 200)
    points = extract_key_points(content)
    numbers = extract_numbers(content)
    tags = atom.get("tags", [])

    atom_type = atom.get("atom_type", "")
    if "data" in atom_type or numbers:
        tweet1 = f"{hook_text}\n\nThe numbers tell a different story. 🧵"
    elif "story" in atom_type or "anecdote" in atom_type:
        tweet1 = f"{hook_text}\n\nHere's what happened next. 🧵"
    else:
        tweet1 = f"Most people get this wrong about {tags[0] if tags else 'this'}.\n\n{hook_text}"

    if len(tweet1) > 280:
        tweet1 = tweet1[:277] + "..."

    tweets = [tweet1]
    for i, point in enumerate(points[:5]):
        point_short = shorten_sentence(point, 15)
        if numbers and i < len(numbers):
            tweet = f"{point_short}\n\n{numbers[i]} — that's the real number."
        else:
            tweet = point_short
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
        tweets.append(tweet)

    ctas = [
        "What's your take? Reply with what you'd add.",
        "What did I miss? Drop your thoughts below.",
        "Agree or disagree? I want to hear your take.",
    ]
    tweets.append(ctas[hash(atom["id"]) % len(ctas)])
    while len(tweets) < 5:
        tweets.insert(-1, "The gap is only getting wider. Those who move now win.")

    thread = "\n\n---\n\n".join([f"🧵 {i+1}/{len(tweets)}\n{t}" for i, t in enumerate(tweets)])
    return thread, tweets[0]


def generate_x_post(atom):
    content = clean_content(atom["content"])
    hook = extract_hook(content, 180)
    numbers = extract_numbers(content)
    num_str = f"\n\n{numbers[0]}." if numbers else ""
    post = f"{hook}{num_str}\n\nWhat's your take?"
    if len(post) > 280:
        post = post[:277] + "..."
    return post, hook


def generate_linkedin_post(atom):
    content = clean_content(atom["content"])
    hook = extract_hook(content, 150)
    points = extract_key_points(content)
    numbers = extract_numbers(content)

    hook_section = f"{hook}\n\nHere's what I learned."
    punchy = make_punchy(content)
    story = "\n\n".join(punchy[:6])

    point_section = "\n".join([f"→ {p}" for p in points[:4]]) if len(points) > 2 else ""
    data_section = f"\nThe data: {', '.join(numbers[:3])}." if numbers else ""

    ctas = [
        "What would you do differently?",
        "What's your experience with this?",
        "Curious — what's your take?",
    ]
    cta = ctas[hash(atom["id"]) % len(ctas)]

    parts = [hook_section, story]
    if point_section:
        parts.append(point_section)
    if data_section:
        parts.append(data_section)
    parts.append(cta)

    post = "\n\n".join(parts)
    if len(post) > 1500:
        post = post[:1497] + "..."
    return post, hook


def generate_youtube_short(atom):
    content = clean_content(atom["content"])
    hook = extract_hook(content, 100)
    points = extract_key_points(content)
    numbers = extract_numbers(content)
    tags = atom.get("tags", [])
    topic = tags[0] if tags else "this"

    hook_line = f"[HOOK] (0:00-0:03)\n[Look directly at camera, energy up]\n\"{hook}\""
    setup_points = points[:2]
    setup_text = " ".join([shorten_sentence(p, 12) for p in setup_points])
    setup_line = f"[SETUP] (0:03-0:13)\n[Cut to B-roll or screen share]\n\"{setup_text}\""
    payoff_points = points[2:5] if len(points) > 2 else points
    payoff_items = "\n".join([f"  → {shorten_sentence(p, 12)}" for p in payoff_points])
    num_callout = f"\n[TEXT OVERLAY: {numbers[0]}]" if numbers else ""
    payoff_line = f"[PAYOFF] (0:13-0:40)\n[Quick cuts between points]{num_callout}\n{payoff_items}"
    cta_line = f"[CTA] (0:40-0:45)\n[Point at camera]\n\"Comment '{topic.upper()}' and I'll show you exactly how.\"\n[TEXT: Follow for more]"

    script = f"{hook_line}\n\n{setup_line}\n\n{payoff_line}\n\n{cta_line}"
    return script, hook


def generate_newsletter_section(atom):
    content = clean_content(atom["content"])
    hook = extract_hook(content, 150)
    points = extract_key_points(content)
    numbers = extract_numbers(content)

    headline = f"**{hook}**"
    punchy = make_punchy(content)
    para1 = " ".join(punchy[:4])
    para2 = " ".join(punchy[4:8]) if len(punchy) > 4 else ""
    data = f"The numbers: {', '.join(numbers[:3])}." if numbers else ""
    why = f"> **Why this matters:** {shorten_sentence(points[-1] if points else content[:100], 15)}"

    parts = [headline, para1]
    if para2:
        parts.append(para2)
    if data:
        parts.append(data)
    parts.append(why)

    return "\n\n".join([p for p in parts if p.strip()]), hook


FORMAT_GENERATORS = {
    "x_thread": generate_x_thread,
    "x_post": generate_x_post,
    "linkedin_post": generate_linkedin_post,
    "youtube_short_script": generate_youtube_short,
    "newsletter_section": generate_newsletter_section,
}


def estimate_engagement(atom, platform):
    score = atom.get("repurpose_score", 5)
    if score >= 8:
        return "high"
    elif score >= 5:
        return "medium"
    return "low"


def generate_drafts_for_atom(atom):
    drafts = []
    missing = atom.get("platforms_missing", [])
    for platform_key in missing:
        fmt = MISSING_TO_FORMAT.get(platform_key)
        platform = MISSING_TO_PLATFORM.get(platform_key)
        if not fmt or fmt not in FORMAT_GENERATORS:
            continue
        generator = FORMAT_GENERATORS[fmt]
        draft_text, hook = generator(atom)
        draft = {
            "id": str(uuid.uuid4()),
            "atom_id": atom["id"],
            "atom_content": atom["content"][:500],
            "atom_source": atom.get("source", "unknown"),
            "platform": platform,
            "format": fmt,
            "draft": draft_text,
            "hook": hook[:200],
            "char_count": len(draft_text),
            "estimated_engagement": estimate_engagement(atom, platform),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "draft",
            "expert_score": None,
            "iterations": 0,
            "key_improvements": [],
        }
        drafts.append(draft)
    return drafts


# ── ANTHROPIC API ──

def get_anthropic_key():
    """Get Anthropic API key from environment."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    print("ERROR: Set ANTHROPIC_API_KEY environment variable")
    return None


def load_file_safe(path):
    """Load a text file, return empty string if missing."""
    try:
        return Path(path).read_text()
    except Exception:
        return ""


def load_expert_panel(platform):
    """Load expert panel for a platform."""
    filename = PLATFORM_TO_EXPERT.get(platform, "x-articles.md")
    return load_file_safe(SKILL_DIR / "experts" / filename)


def load_scoring_rubric():
    """Load content quality scoring rubric."""
    return load_file_safe(SKILL_DIR / "scoring-rubrics" / "content-quality.md")


def load_voice_references():
    """Load voice/style references for content generation."""
    voice_config = load_file_safe(VOICE_CONFIG_FILE)
    style_guide = load_file_safe(STYLE_GUIDE_FILE)
    return voice_config, style_guide


def call_anthropic(client, messages, system=None, model="claude-sonnet-5", max_tokens=2000):
    """Call Anthropic API."""
    kwargs = {"model": model, "max_tokens": max_tokens, "messages": messages}
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)
    return response.content[0].text.strip()


def llm_generate_draft(client, atom, platform, fmt, voice_config, style_guide):
    """Generate a draft using Claude API."""
    platform_instructions = {
        "x": "Write an X article (long-form X post). Include at least one ASCII diagram in a code block. Keep paragraphs to 1-3 sentences. End with a natural CTA.",
        "linkedin": "Write a LinkedIn post. Hook must work before the 'see more' fold (first 2-3 lines). Use line breaks for readability. Professional but personal. 800-1500 chars.",
        "youtube_short": "Write a YouTube Short script. Format: [HOOK] (0:00-0:03), [SETUP] (0:03-0:13), [PAYOFF] (0:13-0:40), [CTA] (0:40-0:45). Include visual directions. 30-60 seconds total.",
        "newsletter": "Write a newsletter section. Subject line + scannable body. Headers, bullets, bold for skimmers. End with 'why this matters'.",
    }

    system_parts = ["You are a content writer creating platform-native content. Follow the configured voice and style EXACTLY."]

    if voice_config:
        system_parts.append(f"\nVOICE CONFIGURATION:\n{voice_config}")
    if style_guide:
        system_parts.append(f"\nSTYLE GUIDE:\n{style_guide[:2000]}")

    system_parts.append("""
RULES:
- Short punchy sentences. Max 15 words.
- Specific numbers always. Never vague.
- Contrarian angles backed by data.
- No corporate speak. No "I'm excited to share."
- Personal stories and specific examples.
- Every sentence earns its place.""")

    system = "\n".join(system_parts)

    topic_tags = atom.get('tags', [])
    prompt = f"""Create a {platform} draft from this content atom.

PLATFORM INSTRUCTIONS:
{platform_instructions.get(platform, platform_instructions['x'])}

SOURCE CONTENT:
{clean_content(atom['content'])}

SOURCE: {atom.get('source_title', 'unknown')}
TAGS: {', '.join(topic_tags)}

Write ONLY the draft content. No preamble, no explanation."""

    return call_anthropic(client, [{"role": "user", "content": prompt}], system=system)


def expert_panel_score(client, draft_text, platform, expert_panel, rubric, voice_config):
    """Run expert panel scoring. Returns (score, feedback_dict)."""
    system = f"""You are simulating 10 domain experts reviewing content for quality.

EXPERT PANEL:
{expert_panel}

SCORING RUBRIC:
{rubric}

VOICE REFERENCE:
{voice_config[:1000] if voice_config else 'No specific voice config provided.'}"""

    prompt = f"""Score this {platform} draft. Each of 11 experts scores 0-100 on the rubric criteria.
Expert #11 is the AI Writing Detector (Humanizer) — scores how AI-generated the draft sounds.

BANNED AI VOCABULARY (flag any occurrence):
delve, tapestry, landscape (abstract), leverage, multifaceted, nuanced, pivotal, realm, robust, seamless, testament, transformative, underscore (verb), utilize, whilst, keen, embark, comprehensive, intricate, commendable, meticulous, paramount, groundbreaking, innovative, cutting-edge, synergy, holistic, paradigm, ecosystem, Additionally, crucial, enduring, enhance, fostering, garner, highlight (verb), interplay, intricacies, showcase, vibrant, valuable, profound, renowned, breathtaking, nestled, stunning

AI PATTERNS TO CHECK:
- Significance inflation ("pivotal moment", "is a testament", "stands as")
- Superficial -ing phrases ("highlighting", "showcasing", "underscoring")
- Promotional language ("boasts", "vibrant", "commitment to")
- Vague attributions ("Experts believe", "Industry reports")
- Formulaic "despite challenges... continues to" structures
- Copula avoidance ("serves as" instead of "is")
- Negative parallelisms ("It's not just X, it's Y")
- Rule-of-three forcing (triple adjectives/clauses)
- Em dash overuse (max 1 per 200 words)
- Filler phrases ("In order to", "It is important to note")
- Excessive hedging ("could potentially")
- Generic positive conclusions ("The future looks bright")

If the Humanizer expert scores below 70, the draft MUST be flagged for revision.

DRAFT:
{draft_text}

Respond in this EXACT JSON format (no other text):
{{
  "average_score": <number>,
  "expert_scores": [<11 numbers>],
  "weaknesses": ["<specific weakness 1>", "<specific weakness 2>", ...],
  "line_feedback": ["<specific line-by-line fix 1>", "<specific line-by-line fix 2>", ...],
  "strengths": ["<strength 1>", "<strength 2>"],
  "ai_patterns_detected": ["<pattern 1>", "<pattern 2>", ...],
  "humanizer_score": <number>
}}

Be harsh. Score honestly."""

    response = call_anthropic(client, [{"role": "user", "content": prompt}], system=system, max_tokens=1500)

    try:
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            result = json.loads(json_match.group())
            return result.get("average_score", 0), result
        else:
            return 0, {"error": "No JSON in response"}
    except json.JSONDecodeError:
        return 0, {"error": "Invalid JSON", "raw": response[:500]}


def expert_panel_revise(client, draft_text, platform, feedback, voice_config, style_guide):
    """Revise draft based on expert feedback."""
    system_parts = ["You are revising content based on expert feedback."]
    if voice_config:
        system_parts.append(f"\nVOICE CONFIGURATION:\n{voice_config}")
    system_parts.append("""
RULES:
- Fix every weakness identified
- Keep all strengths
- Maintain configured voice exactly
- Short punchy sentences, specific numbers, contrarian angles""")

    system = "\n".join(system_parts)

    weaknesses = feedback.get("weaknesses", [])
    line_fixes = feedback.get("line_feedback", [])
    ai_patterns = feedback.get("ai_patterns_detected", [])

    ai_section = ""
    if ai_patterns:
        ai_section = f"""
AI PATTERNS DETECTED (MUST FIX ALL):
{chr(10).join(f'- {p}' for p in ai_patterns)}

BANNED VOCABULARY (replace every occurrence):
delve, tapestry, landscape (abstract), leverage, multifaceted, nuanced, pivotal, realm, robust, seamless, testament, transformative, underscore (verb), utilize, whilst, keen, embark, comprehensive, intricate, commendable, meticulous, paramount, groundbreaking, innovative, cutting-edge, synergy, holistic, paradigm, ecosystem, Additionally, crucial, enduring, enhance, fostering, garner, highlight (verb), interplay, intricacies, showcase, vibrant, valuable, profound, renowned, breathtaking, nestled, stunning
"""

    prompt = f"""Revise this {platform} draft based on expert feedback.

CURRENT DRAFT:
{draft_text}

WEAKNESSES TO FIX:
{chr(10).join(f'- {w}' for w in weaknesses)}

SPECIFIC LINE FIXES:
{chr(10).join(f'- {f}' for f in line_fixes)}
{ai_section}
CURRENT SCORE: {feedback.get('average_score', 'unknown')}
TARGET SCORE: {EXPERT_PANEL_THRESHOLD}+

Write ONLY the revised draft. No preamble."""

    return call_anthropic(client, [{"role": "user", "content": prompt}], system=system)


def process_draft_with_expert_panel(client, atom, platform, fmt, voice_config, style_guide):
    """Full expert panel pipeline: generate → score → revise loop."""
    expert_panel = load_expert_panel(platform)
    rubric = load_scoring_rubric()

    print(f"    Generating {platform} draft via Claude...")
    draft_text = llm_generate_draft(client, atom, platform, fmt, voice_config, style_guide)

    iterations = []
    best_draft = draft_text
    best_score = 0

    for iteration in range(1, EXPERT_PANEL_MAX_ITERATIONS + 1):
        print(f"    Expert panel scoring (iteration {iteration})...")
        score, feedback = expert_panel_score(client, draft_text, platform, expert_panel, rubric, voice_config)
        print(f"    Score: {score}/100")

        iteration_log = {
            "iteration": iteration,
            "score": score,
            "weaknesses": feedback.get("weaknesses", []),
            "line_feedback": feedback.get("line_feedback", []),
            "strengths": feedback.get("strengths", []),
        }
        iterations.append(iteration_log)

        if score > best_score:
            best_score = score
            best_draft = draft_text

        if score >= EXPERT_PANEL_THRESHOLD:
            print(f"    ✓ Passed threshold ({score} >= {EXPERT_PANEL_THRESHOLD})")
            break

        if iteration < EXPERT_PANEL_MAX_ITERATIONS:
            print(f"    Revising based on feedback...")
            draft_text = expert_panel_revise(client, draft_text, platform, feedback, voice_config, style_guide)

    key_improvements = []
    for it in iterations:
        for w in it.get("weaknesses", []):
            key_improvements.append(f"Iter {it['iteration']}: Fixed — {w}")

    return best_draft, best_score, len(iterations), key_improvements, iterations


def rewrite_with_llm(drafts, use_expert_panel=False, expert_panel_top_n=10):
    """Rewrite drafts using Claude API, optionally with expert panel."""
    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic package not installed. Run: pip install anthropic")
        return drafts

    api_key = get_anthropic_key()
    if not api_key:
        return drafts

    client = anthropic.Anthropic(api_key=api_key)
    voice_config, style_guide = load_voice_references()

    rewritten = []
    for i, draft in enumerate(drafts):
        atom = {"content": draft["atom_content"], "source_title": draft.get("atom_source", ""),
                "tags": [], "atom_type": ""}

        if use_expert_panel and i < expert_panel_top_n:
            print(f"\n  [{i+1}/{len(drafts)}] Expert panel: {draft['format']} (atom {draft['atom_id'][:8]})")
            try:
                import time as _time
                _start = _time.time()
                new_text, score, iters, improvements, iter_log = process_draft_with_expert_panel(
                    client, atom, draft["platform"], draft["format"],
                    voice_config, style_guide
                )
                _elapsed = _time.time() - _start
                draft["draft"] = new_text
                draft["hook"] = extract_hook(new_text, 200)
                draft["char_count"] = len(new_text)
                draft["expert_score"] = score
                draft["iterations"] = iters
                draft["key_improvements"] = improvements
                draft["iteration_log"] = iter_log
                status = "✓" if score >= EXPERT_PANEL_THRESHOLD else f"⚠ ({score})"
                print(f"    {status} Final: {score}/100 after {iters} iteration(s) [{_elapsed:.1f}s]")
            except Exception as e:
                print(f"    ✗ Expert panel failed ({type(e).__name__}): {e}")
                try:
                    new_text = llm_generate_draft(client, atom, draft["platform"], draft["format"],
                                                   voice_config, style_guide)
                    draft["draft"] = new_text
                    draft["hook"] = extract_hook(new_text, 200)
                    draft["char_count"] = len(new_text)
                    print(f"    ↳ Fell back to simple LLM rewrite")
                except Exception as e2:
                    print(f"    ✗ LLM rewrite also failed: {e2}")
        else:
            print(f"\n  [{i+1}/{len(drafts)}] LLM rewrite: {draft['format']} (atom {draft['atom_id'][:8]})")
            try:
                new_text = llm_generate_draft(client, atom, draft["platform"], draft["format"],
                                               voice_config, style_guide)
                draft["draft"] = new_text
                draft["hook"] = extract_hook(new_text, 200)
                draft["char_count"] = len(new_text)
                print(f"    ✓ Rewrote")
            except Exception as e:
                print(f"    ✗ LLM rewrite failed: {e}")

        rewritten.append(draft)

    return rewritten


def main():
    parser = argparse.ArgumentParser(description="Transform content atoms into platform-native drafts")
    parser.add_argument("--atoms", type=str, help="Path to atoms JSON file")
    parser.add_argument("--top-n", type=int, default=10, help="Number of top atoms to process")
    parser.add_argument("--template-only", action="store_true", help="Use template-based generation (no LLM)")
    parser.add_argument("--no-expert-panel", action="store_true", help="Disable expert panel quality gate")
    parser.add_argument("--expert-panel-top-n", type=int, default=10, help="Apply expert panel to top N drafts")
    parser.add_argument("--output", type=str, help="Output file path")
    args = parser.parse_args()

    use_llm = not args.template_only
    use_expert_panel = use_llm and not args.no_expert_panel

    atoms = load_atoms(args.atoms)
    print(f"Loaded {len(atoms)} atoms")

    top_atoms = rank_atoms(atoms, args.top_n)
    print(f"Selected top {len(top_atoms)} atoms by repurpose_score × missing platforms")

    all_drafts = []
    for atom in top_atoms:
        drafts = generate_drafts_for_atom(atom)
        all_drafts.extend(drafts)
        missing = atom.get("platforms_missing", [])
        print(f"  Atom {atom['id'][:8]}: {len(drafts)} drafts ({', '.join(missing)})")

    print(f"\nGenerated {len(all_drafts)} total drafts")

    if use_llm:
        mode = "LLM + Expert Panel" if use_expert_panel else "LLM only"
        print(f"\n{'='*60}")
        print(f"Rewriting with {mode}...")
        print(f"{'='*60}")
        all_drafts = rewrite_with_llm(all_drafts, use_expert_panel=use_expert_panel,
                                       expert_panel_top_n=args.expert_panel_top_n)

    by_platform = {}
    for d in all_drafts:
        by_platform[d["platform"]] = by_platform.get(d["platform"], 0) + 1
    print(f"\n{'='*60}")
    print("Drafts by platform:")
    for p, c in sorted(by_platform.items()):
        print(f"  {p}: {c}")

    scored = [d for d in all_drafts if d.get("expert_score")]
    if scored:
        avg = sum(d["expert_score"] for d in scored) / len(scored)
        passed = sum(1 for d in scored if d["expert_score"] >= EXPERT_PANEL_THRESHOLD)
        print(f"\nExpert panel: {len(scored)} scored, {passed} passed (≥{EXPERT_PANEL_THRESHOLD}), avg {avg:.1f}")

    today = datetime.now().strftime("%Y-%m-%d")
    output_path = Path(args.output) if args.output else DATA_DIR / f"content-drafts-{today}.json"
    latest_path = DATA_DIR / "content-drafts-latest.json"

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "atom_count": len(top_atoms),
        "draft_count": len(all_drafts),
        "used_llm": use_llm,
        "used_expert_panel": use_expert_panel,
        "expert_panel_threshold": EXPERT_PANEL_THRESHOLD if use_expert_panel else None,
        "drafts": all_drafts,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    with open(latest_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to {output_path}")
    print(f"Saved to {latest_path}")

    if scored:
        print(f"\n{'='*60}")
        print("TOP DRAFTS BY SCORE:")
        print(f"{'='*60}")
        for d in sorted(scored, key=lambda x: x["expert_score"], reverse=True)[:5]:
            print(f"\n[{d['platform'].upper()}] Score: {d['expert_score']}/100 | Iterations: {d['iterations']}")
            print(f"Hook: {d['hook'][:100]}...")
            if d.get("key_improvements"):
                print(f"Key improvements: {d['key_improvements'][0]}")
            print(f"---")
            print(d["draft"][:300])
            print("...\n")


if __name__ == "__main__":
    main()
