#!/usr/bin/env python3
"""
product_rotation.py — Tier-weighted round-robin product rotation with cooldowns.

Manages which product gets featured each day across a DTC content pipeline.
Products are organized by tier (1 = hero, 2 = standard, 3 = low priority).
Tier 1 products are featured more frequently within each rotation cycle.

Usage:
    python3 product_rotation.py status --config rotation.json
    python3 product_rotation.py next --config rotation.json
    python3 product_rotation.py advance --config rotation.json
    python3 product_rotation.py history --config rotation.json --days 30
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


def load_rotation(config_path):
    """Load product rotation configuration from JSON."""
    path = Path(config_path)
    if not path.exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)
    return json.loads(path.read_text())


def save_rotation(config_path, rotation):
    """Save updated rotation configuration."""
    Path(config_path).write_text(json.dumps(rotation, indent=2) + "\n")


def build_rotation_queue(products):
    """
    Build a rotation queue from products based on tier weights.

    Tier 1 products appear tier1_frequency times per cycle (default 2).
    Tier 2 products appear once per cycle.
    Tier 3 products appear once at the end of the cycle.
    """
    tier1 = [p for p in products if p.get("tier") == 1]
    tier2 = [p for p in products if p.get("tier") == 2]
    tier3 = [p for p in products if p.get("tier") == 3]

    queue = []
    # Tier 1 products get 2x featuring
    for p in tier1:
        queue.append(p["name"])
    # Tier 2 once
    for p in tier2:
        queue.append(p["name"])
    # Tier 1 again (second pass)
    for p in tier1:
        queue.append(p["name"])
    # Tier 3 at end
    for p in tier3:
        queue.append(p["name"])

    return queue


def get_next_product(rotation):
    """Determine the next product to feature."""
    next_name = rotation.get("next_in_rotation", "")
    products = rotation.get("products", [])

    for p in products:
        if p["name"] == next_name:
            return p

    # Fallback: first Tier 1 product
    tier1 = [p for p in products if p.get("tier") == 1]
    return tier1[0] if tier1 else products[0] if products else None


def get_education_angle(product):
    """Pick an education angle for today based on day-of-year rotation."""
    angles = product.get("education_angles", [])
    if not angles:
        return "General product education"
    day_of_year = datetime.now().timetuple().tm_yday
    return angles[day_of_year % len(angles)]


def should_include_cross_sell(rotation, frequency=3):
    """
    Check if this post should include a cross-sell CTA.
    Default: every 3rd post includes a cross-sell.
    """
    log = rotation.get("rotation_log", [])
    posts_since_cta = 0
    for entry in reversed(log):
        if entry.get("includes_cross_sell_cta"):
            break
        posts_since_cta += 1
    return posts_since_cta >= (frequency - 1)


def advance_rotation(rotation):
    """Advance to the next product in the rotation queue."""
    products = rotation.get("products", [])
    if not products:
        return rotation

    queue = build_rotation_queue(products)
    current = rotation.get("next_in_rotation", "")

    try:
        idx = queue.index(current)
        next_idx = (idx + 1) % len(queue)
    except ValueError:
        next_idx = 0

    today = datetime.now().strftime("%Y-%m-%d")
    includes_cta = should_include_cross_sell(rotation)

    # Log the rotation
    if "rotation_log" not in rotation:
        rotation["rotation_log"] = []

    rotation["rotation_log"].append({
        "date": today,
        "product": current,
        "includes_cross_sell_cta": includes_cta,
    })

    # Keep log trimmed to last 90 entries
    rotation["rotation_log"] = rotation["rotation_log"][-90:]

    # Advance pointer
    rotation["next_in_rotation"] = queue[next_idx]

    return rotation


def cmd_status(args):
    """Show current rotation status."""
    rotation = load_rotation(args.config)
    product = get_next_product(rotation)

    if not product:
        print("No products configured.")
        return

    angle = get_education_angle(product)
    includes_cta = should_include_cross_sell(rotation)
    queue = build_rotation_queue(rotation.get("products", []))

    print(f"Next product:     {product['name']}")
    print(f"Tier:             {product.get('tier', '?')}")
    print(f"Category:         {product.get('category', '?')}")
    print(f"Education angle:  {angle}")
    print(f"Cross-sell CTA:   {'Yes' if includes_cta else 'No'}")
    print(f"Queue length:     {len(queue)} slots per cycle")
    print(f"Recent log:       {len(rotation.get('rotation_log', []))} entries")


def cmd_next(args):
    """Output next product as JSON (for piping to other tools)."""
    rotation = load_rotation(args.config)
    product = get_next_product(rotation)

    if not product:
        print("{}")
        return

    result = {
        "name": product["name"],
        "tier": product.get("tier"),
        "category": product.get("category", ""),
        "tagline": product.get("tagline", ""),
        "education_angle": get_education_angle(product),
        "includes_cross_sell_cta": should_include_cross_sell(rotation),
    }
    print(json.dumps(result, indent=2))


def cmd_advance(args):
    """Advance rotation to next product and save."""
    rotation = load_rotation(args.config)
    current = rotation.get("next_in_rotation", "?")
    rotation = advance_rotation(rotation)
    save_rotation(args.config, rotation)
    print(f"Advanced: {current} -> {rotation['next_in_rotation']}")


def cmd_history(args):
    """Show rotation history."""
    rotation = load_rotation(args.config)
    log = rotation.get("rotation_log", [])
    days = args.days or 30

    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    recent = [e for e in log if e.get("date", "") >= cutoff]

    if not recent:
        print(f"No rotation entries in the last {days} days.")
        return

    print(f"Rotation history (last {days} days):")
    print(f"{'Date':<12} {'Product':<25} {'CTA'}")
    print("-" * 45)
    for entry in recent:
        cta = "Yes" if entry.get("includes_cross_sell_cta") else ""
        print(f"{entry.get('date', '?'):<12} {entry.get('product', '?'):<25} {cta}")


def main():
    parser = argparse.ArgumentParser(
        description="DTC product rotation management"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # status
    p_status = subparsers.add_parser("status", help="Show current rotation status")
    p_status.add_argument("--config", required=True, help="Path to rotation config JSON")

    # next
    p_next = subparsers.add_parser("next", help="Output next product as JSON")
    p_next.add_argument("--config", required=True, help="Path to rotation config JSON")

    # advance
    p_advance = subparsers.add_parser("advance", help="Advance to next product")
    p_advance.add_argument("--config", required=True, help="Path to rotation config JSON")

    # history
    p_history = subparsers.add_parser("history", help="Show rotation history")
    p_history.add_argument("--config", required=True, help="Path to rotation config JSON")
    p_history.add_argument("--days", type=int, default=30, help="Number of days to show")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "status": cmd_status,
        "next": cmd_next,
        "advance": cmd_advance,
        "history": cmd_history,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
