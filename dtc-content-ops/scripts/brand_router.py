#!/usr/bin/env python3
"""
brand_router.py — Multi-brand content routing and validation.

Routes generated content to the correct brand and platform, enforcing
per-brand platform rules (enabled/disabled, media types, character limits).

Usage:
    python3 brand_router.py validate --brand-config config.json --content pending.json
    python3 brand_router.py platforms --brand-config config.json --brand acme_supplements
    python3 brand_router.py summary --brand-config config.json
"""

import argparse
import json
import sys
from pathlib import Path


def load_config(config_path):
    """Load multi-brand configuration."""
    path = Path(config_path)
    if not path.exists():
        print(f"Error: Config not found: {config_path}")
        sys.exit(1)
    return json.loads(path.read_text())


def get_enabled_platforms(brand_config):
    """Return list of enabled platforms for a brand."""
    rules = brand_config.get("platform_rules", {})
    return [
        platform
        for platform, rule in rules.items()
        if rule.get("enabled", False)
    ]


def get_platform_constraints(brand_config, platform):
    """Get constraints for a specific platform (char limit, media types, etc.)."""
    rule = brand_config.get("platform_rules", {}).get(platform, {})
    return {
        "enabled": rule.get("enabled", False),
        "max_chars": rule.get("max_chars"),
        "media_types": rule.get("media_types", []),
        "image_format": rule.get("image_format"),
        "description": rule.get("description", ""),
    }


def validate_content_routing(brand_config, content, brand_key):
    """
    Validate that content is correctly routed to enabled platforms
    and respects platform constraints.

    Returns list of issues found.
    """
    issues = []
    platforms = content.get("platforms", {})
    enabled = get_enabled_platforms(brand_config)

    for platform, post in platforms.items():
        # Check platform is enabled for this brand
        if platform not in enabled:
            issues.append({
                "severity": "ERROR",
                "platform": platform,
                "brand": brand_key,
                "message": f"Platform '{platform}' is not enabled for brand '{brand_key}'",
            })
            continue

        constraints = get_platform_constraints(brand_config, platform)

        # Check character limits
        text_fields = ["text", "caption", "long_caption", "short_caption"]
        for field in text_fields:
            text = post.get(field, "")
            if text and constraints.get("max_chars"):
                if len(text) > constraints["max_chars"]:
                    issues.append({
                        "severity": "ERROR",
                        "platform": platform,
                        "brand": brand_key,
                        "message": f"Text exceeds {constraints['max_chars']} char limit: {len(text)} chars",
                    })

        # Check media type compatibility
        media_type = post.get("media_type", "").lower()
        if media_type and constraints.get("media_types"):
            allowed = [m.lower() for m in constraints["media_types"]]
            if media_type not in allowed:
                issues.append({
                    "severity": "WARN",
                    "platform": platform,
                    "brand": brand_key,
                    "message": f"Media type '{media_type}' not in allowed types: {allowed}",
                })

    return issues


def cmd_validate(args):
    """Validate content routing against brand config."""
    config = load_config(args.brand_config)
    content_path = Path(args.content)
    if not content_path.exists():
        print(f"Error: Content file not found: {args.content}")
        sys.exit(1)

    content_data = json.loads(content_path.read_text())
    businesses = config.get("businesses", {})

    all_issues = []
    for brand_key, brand_content in content_data.get("businesses", {}).items():
        brand_config = businesses.get(brand_key, {})
        if not brand_config:
            all_issues.append({
                "severity": "ERROR",
                "brand": brand_key,
                "platform": "*",
                "message": f"Brand '{brand_key}' not found in config",
            })
            continue

        issues = validate_content_routing(brand_config, brand_content, brand_key)
        all_issues.extend(issues)

    if not all_issues:
        print("All content routing validated successfully.")
    else:
        errors = [i for i in all_issues if i["severity"] == "ERROR"]
        warns = [i for i in all_issues if i["severity"] == "WARN"]

        if errors:
            print(f"\n{len(errors)} ERROR(s):")
            for issue in errors:
                print(f"  [{issue['brand']}:{issue['platform']}] {issue['message']}")
        if warns:
            print(f"\n{len(warns)} WARNING(s):")
            for issue in warns:
                print(f"  [{issue['brand']}:{issue['platform']}] {issue['message']}")

    return all_issues


def cmd_platforms(args):
    """List enabled platforms for a brand."""
    config = load_config(args.brand_config)
    brand_config = config.get("businesses", {}).get(args.brand, {})

    if not brand_config:
        print(f"Brand '{args.brand}' not found. Available: {list(config.get('businesses', {}).keys())}")
        sys.exit(1)

    enabled = get_enabled_platforms(brand_config)
    print(f"Enabled platforms for {args.brand}:")
    for platform in enabled:
        constraints = get_platform_constraints(brand_config, platform)
        limit = f" (max {constraints['max_chars']} chars)" if constraints.get("max_chars") else ""
        media = f" [{', '.join(constraints.get('media_types', []))}]" if constraints.get("media_types") else ""
        print(f"  - {platform}{limit}{media}")


def cmd_summary(args):
    """Show summary of all brands and their platforms."""
    config = load_config(args.brand_config)

    for brand_key, brand_config in config.get("businesses", {}).items():
        name = brand_config.get("name", brand_key)
        tone = brand_config.get("tone", "")
        enabled = get_enabled_platforms(brand_config)
        print(f"\n{name} ({brand_key})")
        print(f"  Tone: {tone}")
        print(f"  Platforms ({len(enabled)}): {', '.join(enabled)}")


def main():
    parser = argparse.ArgumentParser(
        description="Multi-brand content routing and validation"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # validate
    p_validate = subparsers.add_parser("validate", help="Validate content routing")
    p_validate.add_argument("--brand-config", required=True, help="Path to multi-brand config")
    p_validate.add_argument("--content", required=True, help="Path to pending content JSON")

    # platforms
    p_platforms = subparsers.add_parser("platforms", help="List platforms for a brand")
    p_platforms.add_argument("--brand-config", required=True, help="Path to multi-brand config")
    p_platforms.add_argument("--brand", required=True, help="Brand key to inspect")

    # summary
    p_summary = subparsers.add_parser("summary", help="Summary of all brands")
    p_summary.add_argument("--brand-config", required=True, help="Path to multi-brand config")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "validate": cmd_validate,
        "platforms": cmd_platforms,
        "summary": cmd_summary,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
