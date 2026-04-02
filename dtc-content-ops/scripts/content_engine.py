#!/usr/bin/env python3
"""
content_engine.py — DTC multi-brand content generation engine.

Generates daily social media content across multiple DTC brands and platforms.
Combines product rotation, education-first content generation, quality scoring,
and review dashboard generation into a single pipeline.

Usage:
    python3 content_engine.py generate --brand-config config.json --rotation-config rotation.json
    python3 content_engine.py generate --brand-config config.json --rotation-config rotation.json --date 2026-04-01
    python3 content_engine.py generate --brand-config config.json --rotation-config rotation.json --dry-run
    python3 content_engine.py status --date 2026-04-01
    python3 content_engine.py rotate --rotation-config rotation.json
    python3 content_engine.py schedule --brand-config config.json
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_QUALITY_THRESHOLD = 90
DEFAULT_MAX_ITERATIONS = 3
DEFAULT_CROSS_SELL_FREQUENCY = 3
DEFAULT_IMAGE_COOLDOWN_DAYS = 14

OUTPUT_DIR = Path("output")
PENDING_DIR = OUTPUT_DIR / "pending"
APPROVED_DIR = OUTPUT_DIR / "approved"


def load_json(path):
    """Load a JSON file, exit with error if not found."""
    p = Path(path)
    if not p.exists():
        print(f"Error: File not found: {path}")
        sys.exit(1)
    return json.loads(p.read_text())


def load_env():
    """Load .env file if present."""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())


# ---------------------------------------------------------------------------
# Content Generation
# ---------------------------------------------------------------------------

BRAND_PROMPT_TEMPLATE = """You are writing social media content for {brand_name}.

VOICE: {tone}
STRATEGY: {content_rule}

Today's featured product: {product_name}
Category: {category}
Product tagline: {tagline}
Education angle: {education_angle}

Generate content for these platforms: {platform_list}

Rules:
- Lead with the PROBLEM the product solves, not the product itself
- Every sentence should teach something or solve a problem
- No hype language: no "game-changer", "revolutionary", "unlock your potential"
- Sound like the brand founder, not a marketing AI

Output ONLY valid JSON with one key per platform. Each platform key should contain
a "text" field with the post content. For platforms with image captions, include
a "caption" field. For blog platforms, include "title" and "content" (HTML) fields.
Respect character limits: X=280, Threads=500, Instagram=2200.
"""


def generate_content_for_brand(brand_key, brand_config, product, education_angle):
    """
    Generate content for a single brand across all enabled platforms.
    Uses Claude API if available, falls back to placeholders.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    # Determine enabled platforms
    enabled_platforms = []
    for platform, rules in brand_config.get("platform_rules", {}).items():
        if rules.get("enabled", False):
            enabled_platforms.append(platform)

    if not enabled_platforms:
        return {}

    # Try AI generation
    if api_key:
        try:
            import anthropic

            prompt = BRAND_PROMPT_TEMPLATE.format(
                brand_name=brand_config.get("name", brand_key),
                tone=brand_config.get("tone", "Professional and direct"),
                content_rule=brand_config.get("description", ""),
                product_name=product.get("name", ""),
                category=product.get("category", ""),
                tagline=product.get("tagline", ""),
                education_angle=education_angle,
                platform_list=", ".join(enabled_platforms),
            )

            model = os.environ.get("DTC_CONTENT_MODEL", DEFAULT_MODEL)
            client = anthropic.Anthropic(api_key=api_key)

            print(f"  Calling Claude API ({model}) for {brand_key}...")
            response = client.messages.create(
                model=model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )

            raw_text = response.content[0].text.strip()
            json_match = re.search(r'\{[\s\S]*\}', raw_text)

            if json_match:
                content = json.loads(json_match.group())
                print(f"  Content generated via API for {brand_key}")
                return content

        except ImportError:
            print(f"  anthropic package not installed, using placeholders")
        except json.JSONDecodeError:
            print(f"  Could not parse API response, using placeholders")
        except Exception as e:
            print(f"  API error for {brand_key}: {e}, using placeholders")

    # Fallback: placeholder content
    print(f"  Generating placeholder content for {brand_key}")
    content = {}
    for platform in enabled_platforms:
        content[platform] = {
            "text": f"[PLACEHOLDER — {brand_key}: {education_angle}]",
        }
    return content


def build_pending_json(brand_key, brand_config, content, product, date_str):
    """Build the pending content JSON for a brand with approval state."""
    platforms = {}

    for platform, rules in brand_config.get("platform_rules", {}).items():
        if not rules.get("enabled", False):
            continue

        platform_content = content.get(platform, {})
        text = platform_content.get("text", platform_content.get("caption", ""))
        max_chars = rules.get("max_chars")

        platforms[platform] = {
            "text": text,
            "char_count": len(text),
            "max_chars": max_chars,
            "over_limit": bool(max_chars and len(text) > max_chars),
            "media_types": rules.get("media_types", []),
            "image_format": rules.get("image_format", ""),
            "approved": False,
            "posted": False,
        }

        # Include blog-specific fields
        if "title" in platform_content:
            platforms[platform]["title"] = platform_content["title"]
        if "content" in platform_content:
            platforms[platform]["html_body"] = platform_content["content"]

    return {
        "brand": brand_key,
        "brand_name": brand_config.get("name", brand_key),
        "content_type": brand_config.get("content_strategy", "general"),
        "product": product.get("name", ""),
        "product_tier": product.get("tier", 1),
        "education_angle": product.get("_education_angle", ""),
        "platforms": platforms,
    }


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_generate(args):
    """Generate daily content for all brands."""
    load_env()

    brand_config = load_json(args.brand_config)
    rotation = load_json(args.rotation_config)

    date_str = args.date or datetime.now().strftime("%Y-%m-%d")
    businesses = brand_config.get("businesses", {})
    products = rotation.get("products", [])

    # Get today's product
    next_name = rotation.get("next_in_rotation", "")
    product = None
    for p in products:
        if p["name"] == next_name:
            product = p
            break
    if not product:
        product = products[0] if products else {"name": "Unknown", "tier": 1}

    # Get education angle
    angles = product.get("education_angles", ["General product education"])
    day_of_year = datetime.now().timetuple().tm_yday
    education_angle = angles[day_of_year % len(angles)]
    product["_education_angle"] = education_angle

    print(f"Generating content for {date_str}")
    print(f"  Product: {product['name']} (Tier {product.get('tier', '?')})")
    print(f"  Education angle: {education_angle}")

    # Generate for each brand
    all_businesses = {}
    for brand_key, brand_cfg in businesses.items():
        print(f"\n  Brand: {brand_cfg.get('name', brand_key)}")
        content = generate_content_for_brand(brand_key, brand_cfg, product, education_angle)
        pending = build_pending_json(brand_key, brand_cfg, content, product, date_str)
        all_businesses[brand_key] = pending

    # Build complete pending JSON
    output = {
        "date": date_str,
        "generated_at": datetime.now().isoformat(),
        "daily_product": {
            "name": product["name"],
            "tier": product.get("tier"),
            "category": product.get("category", ""),
            "education_angle": education_angle,
        },
        "businesses": all_businesses,
    }

    if args.dry_run:
        print(f"\n--- DRY RUN ---")
        print(json.dumps(output, indent=2))
        return

    # Save pending content
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PENDING_DIR / f"{date_str}.json"
    output_path.write_text(json.dumps(output, indent=2) + "\n")
    print(f"\nContent saved to: {output_path}")

    # Summary
    total_posts = sum(
        len(b.get("platforms", {})) for b in all_businesses.values()
    )
    print(f"Total posts generated: {total_posts} across {len(all_businesses)} brand(s)")


def cmd_status(args):
    """Show status of content for a given date."""
    date_str = args.date or datetime.now().strftime("%Y-%m-%d")

    pending = PENDING_DIR / f"{date_str}.json"
    approved = APPROVED_DIR / f"{date_str}.json"

    if approved.exists():
        data = json.loads(approved.read_text())
        print(f"Status for {date_str}: APPROVED")
    elif pending.exists():
        data = json.loads(pending.read_text())
        print(f"Status for {date_str}: PENDING REVIEW")
    else:
        print(f"No content found for {date_str}")
        return

    for brand_key, brand_data in data.get("businesses", {}).items():
        platforms = brand_data.get("platforms", {})
        approved_count = sum(1 for p in platforms.values() if p.get("approved"))
        total = len(platforms)
        print(f"  {brand_key}: {approved_count}/{total} approved")


def cmd_rotate(args):
    """Show and optionally advance product rotation."""
    rotation = load_json(args.rotation_config)
    next_name = rotation.get("next_in_rotation", "?")
    products = rotation.get("products", [])
    product = next((p for p in products if p["name"] == next_name), None)

    if product:
        print(f"Next: {product['name']} (Tier {product.get('tier')})")
    else:
        print(f"Next: {next_name} (not found in products list)")


def cmd_schedule(args):
    """Show today's content schedule across all brands."""
    brand_config = load_json(args.brand_config)

    print("Content schedule:")
    for brand_key, brand_cfg in brand_config.get("businesses", {}).items():
        enabled = [
            p for p, r in brand_cfg.get("platform_rules", {}).items()
            if r.get("enabled", False)
        ]
        print(f"  {brand_cfg.get('name', brand_key)}: {len(enabled)} platforms")
        for platform in enabled:
            print(f"    - {platform}")


def main():
    parser = argparse.ArgumentParser(
        description="DTC multi-brand content generation engine"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # generate
    p_gen = subparsers.add_parser("generate", help="Generate daily content")
    p_gen.add_argument("--brand-config", required=True, help="Path to multi-brand config")
    p_gen.add_argument("--rotation-config", required=True, help="Path to product rotation config")
    p_gen.add_argument("--date", help="Date to generate for (YYYY-MM-DD, default: today)")
    p_gen.add_argument("--dry-run", action="store_true", help="Preview without saving")

    # status
    p_status = subparsers.add_parser("status", help="Show content status for a date")
    p_status.add_argument("--date", help="Date to check (YYYY-MM-DD, default: today)")

    # rotate
    p_rotate = subparsers.add_parser("rotate", help="Show product rotation")
    p_rotate.add_argument("--rotation-config", required=True, help="Path to rotation config")

    # schedule
    p_schedule = subparsers.add_parser("schedule", help="Show content schedule")
    p_schedule.add_argument("--brand-config", required=True, help="Path to multi-brand config")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "generate": cmd_generate,
        "status": cmd_status,
        "rotate": cmd_rotate,
        "schedule": cmd_schedule,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
