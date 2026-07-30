#!/usr/bin/env python3
"""
Autoresearch: Karpathy-inspired iterative optimization for marketing content.

Generates variants, scores with a simulated expert panel, evolves winners.
Inspired by https://github.com/karpathy/autoresearch

Usage:
    python3 autoresearch.py --input landing-page.html --type landing_page
    python3 autoresearch.py --input email-draft.md --type email --min-score 85
    python3 autoresearch.py --input ad-copy.txt --type ad_copy --variants 15 --rounds 4
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("Missing dependency: pip install anthropic", file=sys.stderr)
    sys.exit(1)

# ── Content type configurations ──

CONTENT_TYPES = {
    "landing_page": {
        "elements": ["hero_headline", "subheadline", "cta", "problem_section", "social_proof"],
        "dimensions": ["first_impression", "clarity", "trust", "urgency", "would_convert"],
    },
    "email": {
        "elements": ["subject_line", "opening_line", "body_copy", "cta", "ps_line"],
        "dimensions": ["would_open", "would_read", "would_click", "would_reply", "spam_risk"],
    },
    "ad_copy": {
        "elements": ["headline", "description", "cta"],
        "dimensions": ["scroll_stopping", "clarity", "click_worthiness", "relevance", "differentiation"],
    },
    "form_page": {
        "elements": ["headline", "subtext", "value_bullets", "button_text", "thank_you_copy"],
        "dimensions": ["first_impression", "trust", "completion_likelihood", "lead_quality", "would_fill_out"],
    },
}

EXPERT_PANEL = [
    {"id": "cmo", "name": "CMO at a mid-market B2B company", "lens": "Would this make me stop and engage?"},
    {"id": "skeptical_founder", "name": "Skeptical founder", "lens": "Do I believe this? Would I trust this company?"},
    {"id": "cro", "name": "Conversion rate optimizer", "lens": "Is this clear, specific, and action-driving?"},
    {"id": "copywriter", "name": "Senior copywriter", "lens": "Is this compelling, differentiated, and well-crafted?"},
    {"id": "founder", "name": "Your CEO/founder", "lens": "Direct, ROI-obsessed, no BS. Would I put this on my site?"},
]


def get_client():
    """Initialize Anthropic client from environment."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)
    return anthropic.Anthropic(api_key=api_key)


def detect_content_type(filepath: str) -> str:
    """Auto-detect content type from file extension and contents."""
    ext = Path(filepath).suffix.lower()
    if ext in (".html", ".htm"):
        return "landing_page"
    with open(filepath, "r") as f:
        content = f.read(2000).lower()
    if "subject" in content and ("dear" in content or "hi " in content):
        return "email"
    if len(content) < 500:
        return "ad_copy"
    return "landing_page"


def extract_elements(content: str, content_type: str) -> dict[str, str]:
    """Extract optimizable elements from content. Returns element_name -> text."""
    # For a real implementation, this would parse HTML/markdown structure.
    # Simplified: treat the whole content as the primary element.
    config = CONTENT_TYPES[content_type]
    elements = {}
    # Split content into rough sections
    lines = content.strip().split("\n")
    if lines:
        elements[config["elements"][0]] = lines[0]  # First line = headline
    if len(lines) > 1:
        elements[config["elements"][1]] = lines[1] if len(config["elements"]) > 1 else ""
    # Rest as body
    remaining = "\n".join(lines[2:]) if len(lines) > 2 else ""
    for elem in config["elements"][2:]:
        elements[elem] = remaining
        remaining = ""  # Only assign to first remaining element
    return {k: v for k, v in elements.items() if v}


def generate_variants(client, element_name: str, current_text: str,
                       content_type: str, num_variants: int,
                       evolution_notes: str = "", model: str = "claude-sonnet-5") -> list[str]:
    """Generate N variants of a content element."""
    evolution_context = ""
    if evolution_notes:
        evolution_context = f"\n\nEvolution notes from previous round (push these winning patterns further):\n{evolution_notes}"

    prompt = f"""Generate exactly {num_variants} variants of this {content_type} {element_name}.

Current text:
---
{current_text}
---
{evolution_context}

Rules:
- Each variant should be meaningfully different (not just word swaps)
- Vary approach: some direct, some curiosity-driven, some data-led, some emotional
- Keep the core value proposition intact
- Match the content type expectations for {element_name}

Return ONLY a JSON array of {num_variants} strings. No explanation, no markdown formatting.
Example: ["Variant 1 text", "Variant 2 text", ...]"""

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    # Parse JSON from response
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    try:
        variants = json.loads(text)
        if isinstance(variants, list):
            return [str(v) for v in variants[:num_variants]]
    except json.JSONDecodeError:
        pass
    # Fallback: split by newlines
    return [line.strip().strip('"').strip("- ") for line in text.split("\n") if line.strip()][:num_variants]


def score_variants(client, variants: list[str], element_name: str,
                    content_type: str, model: str = "claude-sonnet-5") -> list[dict]:
    """Score all variants with the expert panel in a single API call."""
    config = CONTENT_TYPES[content_type]
    dimensions = config["dimensions"]

    panel_desc = "\n".join(
        f"  {i+1}. {e['name']} — Lens: \"{e['lens']}\"" for i, e in enumerate(EXPERT_PANEL)
    )
    dim_desc = ", ".join(dimensions)

    variants_text = "\n".join(f"  Variant {i+1}: \"{v}\"" for i, v in enumerate(variants))

    prompt = f"""You are scoring {element_name} variants for a {content_type}.

Expert Panel:
{panel_desc}

Score Dimensions: {dim_desc}

Variants:
{variants_text}

For EACH variant, have each expert score it 0-100 on each dimension.
Then compute the average score across all experts and dimensions.

Return ONLY valid JSON (no markdown) in this exact format:
[
  {{
    "variant_id": 1,
    "text": "variant text",
    "expert_scores": {{
      "cmo": 72, "skeptical_founder": 68, "cro": 75, "copywriter": 70, "founder": 65
    }},
    "dimension_scores": {{
      "{dimensions[0]}": 71, ...
    }},
    "avg_score": 70
  }},
  ...
]"""

    response = client.messages.create(
        model=model,
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    try:
        scores = json.loads(text)
        if isinstance(scores, list):
            return scores
    except json.JSONDecodeError:
        pass
    # Fallback: return empty scores
    return [{"variant_id": i+1, "text": v, "avg_score": 0} for i, v in enumerate(variants)]


def run_optimization(client, element_name: str, current_text: str,
                      content_type: str, num_variants: int = 10,
                      max_rounds: int = 3, min_score: int = 80,
                      model: str = "claude-sonnet-5") -> dict:
    """Run the full optimization loop for a single element."""
    rounds = []
    best_score = 0
    best_text = current_text
    evolution_notes = ""

    for round_num in range(1, max_rounds + 1):
        print(f"    Round {round_num}/{max_rounds}...", file=sys.stderr)

        # Generate variants
        variants = generate_variants(
            client, element_name, current_text, content_type,
            num_variants, evolution_notes, model
        )

        if not variants:
            print(f"    No variants generated, stopping.", file=sys.stderr)
            break

        # Score all variants (single API call)
        scored = score_variants(client, variants, element_name, content_type, model)

        # Sort by score
        scored.sort(key=lambda x: x.get("avg_score", 0), reverse=True)

        # Record round
        top_3 = scored[:3]
        round_data = {
            "round": round_num,
            "element": element_name,
            "variants": scored,
            "top_3_ids": [s.get("variant_id", i+1) for i, s in enumerate(top_3)],
            "winner_score": top_3[0].get("avg_score", 0) if top_3 else 0,
        }
        rounds.append(round_data)

        # Update best
        if top_3 and top_3[0].get("avg_score", 0) > best_score:
            best_score = top_3[0].get("avg_score", 0)
            best_text = top_3[0].get("text", current_text)

        print(f"    Best score: {best_score}", file=sys.stderr)

        # Check stop condition
        if best_score >= min_score:
            print(f"    Hit target score {min_score}, stopping.", file=sys.stderr)
            break

        # Build evolution notes for next round
        if top_3:
            evolution_notes = "Top performers and what they did well:\n"
            for s in top_3:
                evolution_notes += f"- Score {s.get('avg_score', 0)}: \"{s.get('text', '')[:100]}\"\n"

        time.sleep(1)  # Rate limit buffer

    return {
        "element": element_name,
        "original": current_text,
        "winner": best_text,
        "winner_score": best_score,
        "rounds": rounds,
    }


def cross_breed(client, element_winners: dict[str, dict],
                content_type: str, model: str = "claude-sonnet-5") -> dict:
    """Cross-breed winning elements into complete units."""
    elements_desc = "\n".join(
        f"  {name}: \"{data['winner'][:200]}\" (score: {data['winner_score']})"
        for name, data in element_winners.items()
    )

    prompt = f"""Combine these winning {content_type} elements into 5 cohesive complete versions.
Each version should naturally integrate all winning elements while maintaining their strengths.

Winning elements:
{elements_desc}

Return JSON array of 5 objects, each with all element keys and a brief rationale:
[
  {{
    {', '.join(f'"{name}": "combined text"' for name in element_winners.keys())},
    "rationale": "Why this combination works"
  }},
  ...
]"""

    response = client.messages.create(
        model=model,
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    try:
        combinations = json.loads(text)
        if isinstance(combinations, list):
            return combinations[0] if combinations else {}
    except json.JSONDecodeError:
        pass
    return {}


def write_report(name: str, content_type: str, element_results: dict, final_score: float, output_dir: str):
    """Write the human-readable optimization report."""
    report = f"""# Autoresearch Report: {name}
**Run date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
**Content type:** {content_type}
**Final score:** {final_score}/100

## Winner

"""
    for elem_name, data in element_results.items():
        report += f"### {elem_name}\n{data['winner']}\n\n"

    report += "## Score Progression\n\n"
    report += "| Element | Round 1 Best | Final |\n"
    report += "|---------|-------------|-------|\n"
    for elem_name, data in element_results.items():
        r1_score = data["rounds"][0]["winner_score"] if data["rounds"] else 0
        report += f"| {elem_name} | {r1_score} | {data['winner_score']} |\n"

    report += f"\n## Assessment\n\n"
    if final_score >= 85:
        report += "Ready to deploy. Validate with real traffic.\n"
    elif final_score >= 75:
        report += "Decent. Consider one more round targeting the weakest dimension.\n"
    else:
        report += "Not ready. Consider a different angle entirely.\n"

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    report_path = os.path.join(output_dir, f"{name}-optimization-report.md")
    with open(report_path, "w") as f:
        f.write(report)
    return report_path


def main():
    parser = argparse.ArgumentParser(
        description="Autoresearch: Karpathy-style optimization for marketing content"
    )
    parser.add_argument("--input", required=True, help="Path to content file")
    parser.add_argument("--type", choices=list(CONTENT_TYPES.keys()),
                        help="Content type (auto-detected if omitted)")
    parser.add_argument("--min-score", type=int, default=80, help="Target score threshold")
    parser.add_argument("--rounds", type=int, default=3, help="Max optimization rounds per element")
    parser.add_argument("--variants", type=int, default=10, help="Variants per round")
    parser.add_argument("--elements", help="Comma-separated elements to optimize (default: all)")
    parser.add_argument("--model", default="claude-sonnet-5", help="Anthropic model to use")
    parser.add_argument("--output-dir", default="data", help="Output directory for results")
    parser.add_argument("--name", help="Run name (default: input filename)")
    args = parser.parse_args()

    # Read input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"File not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    content = input_path.read_text()
    name = args.name or input_path.stem

    # Detect or use specified content type
    content_type = args.type or detect_content_type(args.input)
    print(f"Content type: {content_type}", file=sys.stderr)

    # Extract elements
    elements = extract_elements(content, content_type)
    if args.elements:
        selected = set(args.elements.split(","))
        elements = {k: v for k, v in elements.items() if k in selected}

    print(f"Elements to optimize: {list(elements.keys())}", file=sys.stderr)

    # Initialize client
    client = get_client()

    # Run optimization for each element
    element_results = {}
    for elem_name, elem_text in elements.items():
        print(f"\n  Optimizing: {elem_name}", file=sys.stderr)
        result = run_optimization(
            client, elem_name, elem_text, content_type,
            args.variants, args.rounds, args.min_score, args.model
        )
        element_results[elem_name] = result

    # Cross-breed if multiple elements
    if len(element_results) > 1:
        print(f"\n  Cross-breeding winners...", file=sys.stderr)
        combined = cross_breed(client, element_results, content_type, args.model)
        # Update winners with cross-bred versions if available
        for elem_name in element_results:
            if elem_name in combined:
                element_results[elem_name]["winner"] = combined[elem_name]

    # Calculate final score
    scores = [r["winner_score"] for r in element_results.values()]
    final_score = round(sum(scores) / len(scores), 1) if scores else 0

    # Write outputs
    output_dir = args.output_dir
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Experiments JSON
    experiments = {
        "run_id": f"autoresearch-{name}-{int(time.time())}",
        "content_type": content_type,
        "source_file": str(input_path),
        "min_score_threshold": args.min_score,
        "elements": {k: v for k, v in element_results.items()},
        "final_score": final_score,
    }
    json_path = os.path.join(output_dir, f"{name}-experiments.json")
    with open(json_path, "w") as f:
        json.dump(experiments, f, indent=2, default=str)

    # Optimized content
    optimized_path = os.path.join(output_dir, f"{name}-optimized{input_path.suffix}")
    with open(optimized_path, "w") as f:
        for elem_name, data in element_results.items():
            f.write(f"{data['winner']}\n\n")

    # Report
    report_path = write_report(name, content_type, element_results, final_score, output_dir)

    # Summary
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  AUTORESEARCH COMPLETE", file=sys.stderr)
    print(f"  Final score: {final_score}/100", file=sys.stderr)
    print(f"  Optimized:   {optimized_path}", file=sys.stderr)
    print(f"  Experiments: {json_path}", file=sys.stderr)
    print(f"  Report:      {report_path}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)


if __name__ == "__main__":
    main()
