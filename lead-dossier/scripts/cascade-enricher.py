#!/usr/bin/env python3
"""
Cascade Enrichment Pipeline
Waterfall: primary email → email finder API → LinkedIn-outreach-only tag
Dry-run mode when email finder API key is empty.

Usage:
    python3 cascade-enricher.py input.json [output.json]
"""

import json
import os
import sys
import logging
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("cascade-enricher")

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
CONFIG_PATH = DATA_DIR / "enrichment-config.json"
LOG_PATH = DATA_DIR / "enrichment-log.json"


def load_config():
    """Load enrichment configuration. Falls back to env vars if no config file."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {
        "email_validation_api_key": os.environ.get("EMAIL_VALIDATION_API_KEY", ""),
        "email_validation_api_url": os.environ.get(
            "EMAIL_VALIDATION_API_URL",
            "https://api.your-email-provider.com/v1/people/email-finder"
        ),
        "email_validation_timeout_seconds": 10,
        "fallback_tag": "linkedin-outreach-only",
    }


def call_email_finder(prospect, config):
    """Call email finder API. Returns (email, credits_used) or (None, 0)."""
    import requests

    api_key = config.get("email_validation_api_key", "")
    if not api_key:
        return None, 0

    name_parts = prospect.get("name", "").split(" ", 1)
    first_name = name_parts[0] if name_parts else ""
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "domain": prospect.get("domain", ""),
    }

    api_url = config.get(
        "email_validation_api_url",
        "https://api.your-email-provider.com/v1/people/email-finder"
    )

    try:
        resp = requests.post(
            api_url,
            headers={"X-API-Key": api_key, "Content-Type": "application/json"},
            json=payload,
            timeout=config.get("email_validation_timeout_seconds", 10),
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") == "valid" and data.get("email"):
            return data["email"], data.get("credits_consumed", 1)
        return None, 0

    except Exception as e:
        log.error(f"Email finder API error for {prospect.get('name')}: {e}")
        return None, 0


def enrich(prospects, config):
    """Run cascade enrichment on a list of prospects."""
    dry_run = not config.get("email_validation_api_key")
    if dry_run:
        log.info("🔸 DRY-RUN MODE: Email finder API key not configured")

    results = []
    stats = {"primary": 0, "email_finder": 0, "pending": 0, "linkedin_only": 0, "total": 0}

    for p in prospects:
        stats["total"] += 1
        result = {**p, "email_source": None, "enrichment_status": None}

        # Step 1: Already has email from primary source?
        if p.get("email"):
            result["email_source"] = "primary"
            result["enrichment_status"] = "found"
            stats["primary"] += 1
            log.info(f"✅ {p.get('name', 'Unknown')}: Primary email exists")

        # Step 2: Try email finder
        elif not dry_run:
            email, credits = call_email_finder(p, config)
            if email:
                result["email"] = email
                result["email_source"] = "email_finder"
                result["enrichment_status"] = "found"
                stats["email_finder"] += 1
                log.info(f"✅ {p.get('name', 'Unknown')}: Email finder found email")
            elif p.get("linkedin_url"):
                result["email_source"] = config.get("fallback_tag", "linkedin-outreach-only")
                result["enrichment_status"] = "linkedin-only"
                stats["linkedin_only"] += 1
                log.info(f"🔗 {p.get('name', 'Unknown')}: LinkedIn outreach only")
            else:
                result["enrichment_status"] = "no-contact"
                log.info(f"❌ {p.get('name', 'Unknown')}: No contact method found")

        # Step 2 (dry-run): Tag as pending
        else:
            result["email_source"] = "pending"
            result["enrichment_status"] = "pending"
            stats["pending"] += 1
            has_li = "has LinkedIn" if p.get("linkedin_url") else "no LinkedIn"
            log.info(f"⏳ {p.get('name', 'Unknown')}: Pending enrichment ({has_li})")

        results.append(result)

    return results, stats


def append_log(stats, dry_run):
    """Append run stats to enrichment log."""
    logs = []
    if LOG_PATH.exists():
        with open(LOG_PATH) as f:
            logs = json.load(f)

    logs.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        **stats,
    })

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "w") as f:
        json.dump(logs, f, indent=2)


def main():
    if len(sys.argv) < 2:
        print("Usage: cascade-enricher.py <input.json> [output.json]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    with open(input_path) as f:
        prospects = json.load(f)

    config = load_config()
    dry_run = not config.get("email_validation_api_key")

    results, stats = enrich(prospects, config)
    append_log(stats, dry_run)

    output = json.dumps(results, indent=2)
    if output_path:
        with open(output_path, "w") as f:
            f.write(output)
        log.info(f"📄 Results written to {output_path}")
    else:
        print(output)

    log.info(f"📊 Stats: {json.dumps(stats)}")


if __name__ == "__main__":
    main()
