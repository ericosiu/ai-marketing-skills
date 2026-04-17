#!/usr/bin/env python3
"""
Lead Pipeline: Source → Verify → Dedupe → Upload

End-to-end lead sourcing, email verification, deduplication, and campaign upload.
API-agnostic — configure endpoints and keys via environment variables.

Usage:
    python3 lead-pipeline.py \\
        --source-api-key KEY --validation-api-key KEY --campaign-api-key KEY \\
        --titles "VP Marketing,CMO" --campaign-id UUID --volume 200

    python3 lead-pipeline.py --help
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' package required. Run: pip3 install requests", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Configuration — override via environment variables
# ---------------------------------------------------------------------------

SOURCE_API_URL = os.environ.get(
    "LEAD_SOURCE_API_URL",
    "https://api.apollo.io/api/v1/mixed_people/search"
)
VALIDATION_API_URL = os.environ.get(
    "EMAIL_VALIDATION_API_URL",
    "https://api.your-email-provider.com/v1/people/email-validation"
)
CAMPAIGN_API_BASE = os.environ.get(
    "CAMPAIGN_API_BASE_URL",
    "https://api.your-campaign-tool.com/api/v2"
)


# ---------------------------------------------------------------------------
# Retry / backoff helper
# ---------------------------------------------------------------------------

def request_with_retry(method, url, max_retries=5, **kwargs):
    """HTTP request with exponential backoff on 429 / 5xx."""
    backoff = 1
    for attempt in range(max_retries + 1):
        try:
            resp = requests.request(method, url, timeout=30, **kwargs)
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", backoff))
                print(f"  ⏳ Rate limited (429). Waiting {wait}s …")
                time.sleep(wait)
                backoff = min(backoff * 2, 60)
                continue
            if resp.status_code >= 500:
                print(f"  ⚠️  Server error {resp.status_code}. Retry in {backoff}s …")
                time.sleep(backoff)
                backoff = min(backoff * 2, 60)
                continue
            return resp
        except requests.exceptions.RequestException as e:
            if attempt == max_retries:
                raise
            print(f"  ⚠️  Request error: {e}. Retry in {backoff}s …")
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)
    return resp  # type: ignore


# ---------------------------------------------------------------------------
# Step 1: Source Leads (People Search API)
# ---------------------------------------------------------------------------

def source_leads(api_key, titles, industries, company_size, locations, keywords, volume):
    """Pull leads from a people search API."""
    print(f"\n{'='*50}")
    print(f"STEP 1: Sourcing leads (target: {volume})")
    print(f"{'='*50}")

    leads = []
    page = 1

    size_ranges = []
    if company_size:
        parts = [s.strip() for s in company_size.split(",")]
        if len(parts) == 2:
            size_ranges = [f"{parts[0]},{parts[1]}"]
        else:
            size_ranges = parts

    while len(leads) < volume:
        body = {
            "api_key": api_key,
            "per_page": 100,
            "page": page,
        }
        if titles:
            body["person_titles"] = [t.strip() for t in titles.split(",")]
        if industries:
            body["q_organization_keyword_tags"] = [i.strip() for i in industries.split(",")]
        if size_ranges:
            body["organization_num_employees_ranges"] = size_ranges
        if locations:
            body["person_locations"] = [l.strip() for l in locations.split(",")]
        if keywords:
            body["q_keywords"] = keywords

        print(f"  📡 Page {page} …", end=" ", flush=True)
        resp = request_with_retry("POST", SOURCE_API_URL, json=body)

        if resp.status_code != 200:
            print(f"ERROR {resp.status_code}: {resp.text[:200]}")
            break

        data = resp.json()
        people = data.get("people", [])
        if not people:
            print("no more results.")
            break

        page_leads = 0
        for person in people:
            email = person.get("email")
            if not email:
                continue
            leads.append({
                "email": email.lower().strip(),
                "first_name": person.get("first_name", ""),
                "last_name": person.get("last_name", ""),
                "title": person.get("title", ""),
                "company_name": (person.get("organization") or {}).get("name", ""),
                "domain": (person.get("organization") or {}).get("primary_domain", ""),
            })
            page_leads += 1
            if len(leads) >= volume:
                break

        print(f"{page_leads} with email ({len(leads)} total)")

        total_pages = data.get("pagination", {}).get("total_pages", page)
        if page >= total_pages:
            print("  Reached last page.")
            break
        page += 1
        time.sleep(0.5)

    # Dedupe by email within sourced set
    seen = set()
    unique_leads = []
    for lead in leads:
        if lead["email"] not in seen:
            seen.add(lead["email"])
            unique_leads.append(lead)

    print(f"\n  ✅ Sourced {len(unique_leads)} unique leads with emails")
    return unique_leads


# ---------------------------------------------------------------------------
# Step 2: Email Verification
# ---------------------------------------------------------------------------

def verify_emails(api_key, leads):
    """Verify emails via validation API. Returns only valid leads."""
    print(f"\n{'='*50}")
    print(f"STEP 2: Verifying {len(leads)} emails")
    print(f"{'='*50}")

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }

    valid_leads = []
    invalid_count = 0
    unknown_count = 0
    error_count = 0
    rejection_reasons = {}

    for i, lead in enumerate(leads):
        if (i + 1) % 50 == 0 or i == 0:
            print(f"  🔍 Verifying {i+1}/{len(leads)} …")

        try:
            resp = request_with_retry("POST", VALIDATION_API_URL, headers=headers, json={"email": lead["email"]})

            if resp.status_code != 200:
                error_count += 1
                continue

            data = resp.json()
            status = data.get("email_status", "unknown")

            if status == "valid":
                lead["is_free_email"] = data.get("is_free_email", False)
                lead["is_role_based"] = data.get("is_role_based", False)
                valid_leads.append(lead)
            elif status == "invalid":
                invalid_count += 1
                rejection_reasons["invalid"] = rejection_reasons.get("invalid", 0) + 1
            else:
                unknown_count += 1
                rejection_reasons["unknown"] = rejection_reasons.get("unknown", 0) + 1

        except Exception as e:
            error_count += 1
            print(f"  ⚠️  Error verifying {lead['email']}: {e}")

        if (i + 1) % 20 == 0:
            time.sleep(0.5)

    print(f"\n  ✅ Verified: {len(valid_leads)} valid")
    print(f"  ❌ Invalid: {invalid_count}")
    print(f"  ❓ Unknown: {unknown_count}")
    print(f"  ⚠️  Errors: {error_count}")

    return valid_leads, {
        "total": len(leads),
        "valid": len(valid_leads),
        "invalid": invalid_count,
        "unknown": unknown_count,
        "errors": error_count,
        "rejection_reasons": rejection_reasons,
    }


# ---------------------------------------------------------------------------
# Step 3: Deduplicate
# ---------------------------------------------------------------------------

def get_existing_emails(api_key):
    """Pull existing leads from campaign tool for dedup."""
    print(f"\n  📥 Fetching existing leads for dedup …")

    url = f"{CAMPAIGN_API_BASE}/leads/list"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    existing_emails = set()
    cursor = None
    page = 0

    while True:
        body = {"limit": 100}
        if cursor:
            body["starting_after"] = cursor

        resp = request_with_retry("POST", url, headers=headers, json=body)

        if resp.status_code != 200:
            print(f"  ⚠️  List error {resp.status_code}: {resp.text[:200]}")
            break

        data = resp.json()
        items = data.get("items", [])

        if not items:
            break

        for item in items:
            email = item.get("email", "").lower().strip()
            if email:
                existing_emails.add(email)

        cursor = data.get("next_starting_after")
        if not cursor:
            break

        page += 1
        if page % 10 == 0:
            print(f"    … {len(existing_emails)} existing leads so far")
        time.sleep(1)

    print(f"  📊 Found {len(existing_emails)} existing leads")
    return existing_emails


def load_exclusion_list(filepath):
    """Load burned emails from a CSV file."""
    excluded = set()
    if not filepath or not os.path.exists(filepath):
        return excluded

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            email = line.split(",")[0].strip().strip('"').lower()
            if "@" in email:
                excluded.add(email)

    print(f"  📋 Loaded {len(excluded)} emails from exclusion list")
    return excluded


def deduplicate(leads, api_key, exclude_file=None):
    """Remove leads already in campaign tool or on exclusion list."""
    print(f"\n{'='*50}")
    print(f"STEP 3: Deduplicating {len(leads)} leads")
    print(f"{'='*50}")

    existing = get_existing_emails(api_key)
    excluded = load_exclusion_list(exclude_file)

    deduped = []
    existing_dupes = 0
    burned_dupes = 0

    for lead in leads:
        email = lead["email"]
        if email in existing:
            existing_dupes += 1
        elif email in excluded:
            burned_dupes += 1
        else:
            deduped.append(lead)

    print(f"\n  ✅ Net new leads: {len(deduped)}")
    print(f"  🔄 Already in campaign tool: {existing_dupes}")
    print(f"  🚫 On exclusion list: {burned_dupes}")

    return deduped, {
        "existing_dupes": existing_dupes,
        "burned_dupes": burned_dupes,
        "net_new": len(deduped),
    }


# ---------------------------------------------------------------------------
# Step 4: Upload to Campaign Tool
# ---------------------------------------------------------------------------

def generate_personalization(lead):
    """Generate a simple 1-line personalization."""
    name = lead.get("first_name", "")
    company = lead.get("company_name", "")
    title = lead.get("title", "")

    if company and title:
        return f"Noticed you're {title} at {company} — curious how you're thinking about growth this quarter."
    elif company:
        return f"Been following {company}'s trajectory — impressive momentum."
    elif title:
        return f"As a {title}, you're probably juggling growth and efficiency right now."
    return "Your background caught my eye — wanted to reach out."


def upload_leads(api_key, leads, campaign_id, dry_run=False):
    """Upload leads to campaign tool in batches."""
    print(f"\n{'='*50}")
    print(f"STEP 4: Uploading {len(leads)} leads")
    print(f"{'='*50}")

    if dry_run:
        print("  🏃 DRY RUN — skipping actual upload")
        return {"uploaded": 0, "failed": 0, "dry_run": True}

    url = f"{CAMPAIGN_API_BASE}/leads"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    uploaded = 0
    failed = 0
    batch_size = 25

    for i in range(0, len(leads), batch_size):
        batch = leads[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(leads) + batch_size - 1) // batch_size

        print(f"  📤 Batch {batch_num}/{total_batches} ({len(batch)} leads) …", end=" ", flush=True)

        batch_success = 0
        batch_fail = 0

        for lead in batch:
            body = {
                "email": lead["email"],
                "first_name": lead.get("first_name", ""),
                "last_name": lead.get("last_name", ""),
                "company_name": lead.get("company_name", ""),
                "campaign": campaign_id,
                "custom_variables": {
                    "title": lead.get("title", ""),
                    "company_name": lead.get("company_name", ""),
                    "personalization": generate_personalization(lead),
                },
            }

            try:
                resp = request_with_retry("POST", url, headers=headers, json=body)
                if resp.status_code in (200, 201):
                    batch_success += 1
                else:
                    batch_fail += 1
                    if batch_fail <= 3:
                        print(f"\n    ⚠️  Failed {lead['email']}: {resp.status_code} {resp.text[:100]}")
            except Exception as e:
                batch_fail += 1
                print(f"\n    ⚠️  Error uploading {lead['email']}: {e}")

        uploaded += batch_success
        failed += batch_fail
        print(f"✓ {batch_success} ok, {batch_fail} failed")

        if i + batch_size < len(leads):
            time.sleep(1)

    print(f"\n  ✅ Uploaded: {uploaded}")
    if failed:
        print(f"  ❌ Failed: {failed}")

    return {"uploaded": uploaded, "failed": failed, "dry_run": False}


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def save_report(output_dir, sourced, verified_stats, dedup_stats, upload_stats, leads_uploaded, args):
    """Save run log as JSON."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    report_path = os.path.join(output_dir, f"{timestamp}.json")

    report = {
        "timestamp": datetime.now().isoformat(),
        "parameters": {
            "titles": args.titles,
            "industries": args.industries,
            "company_size": args.company_size,
            "locations": args.locations,
            "keywords": args.keywords,
            "campaign_id": args.campaign_id,
            "volume": args.volume,
            "exclude_file": args.exclude_file,
            "dry_run": args.dry_run,
        },
        "results": {
            "sourced": sourced,
            "verification": verified_stats,
            "deduplication": dedup_stats,
            "upload": upload_stats,
        },
        "leads_uploaded": [
            {k: v for k, v in lead.items() if k not in ("is_free_email", "is_role_based")}
            for lead in leads_uploaded
        ],
    }

    os.makedirs(output_dir, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n  💾 Run log saved: {report_path}")
    return report_path


def print_summary(sourced_count, verified_stats, dedup_stats, upload_stats):
    """Print final summary."""
    print(f"\n{'='*50}")
    print(f"  LEAD PIPELINE SUMMARY")
    print(f"{'='*50}")
    print(f"  Sourced:                 {sourced_count:>6}")
    print(f"  Verified (valid):        {verified_stats['valid']:>6}  ({verified_stats['valid']/max(sourced_count,1)*100:.1f}%)")
    print(f"  Already in campaign:     {dedup_stats['existing_dupes']:>6}")
    print(f"  Excluded (burned list):  {dedup_stats['burned_dupes']:>6}")
    print(f"  Net new uploaded:        {upload_stats['uploaded']:>6}")
    if upload_stats.get('failed'):
        print(f"  Failed uploads:          {upload_stats['failed']:>6}")
    if upload_stats.get('dry_run'):
        print(f"  ⚠️  DRY RUN — nothing was uploaded")
    print(f"{'='*50}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Lead Pipeline: Source → Verify → Dedupe → Upload",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline run
  python3 lead-pipeline.py \\
    --source-api-key KEY --validation-api-key KEY --campaign-api-key KEY \\
    --titles "VP Marketing,CMO" --industries "SaaS" \\
    --company-size "11,50" --locations "United States" \\
    --campaign-id abc-123 --volume 200

  # Dry run (no upload)
  python3 lead-pipeline.py \\
    --source-api-key KEY --validation-api-key KEY --campaign-api-key KEY \\
    --titles "CTO,VP Engineering" --company-size "51,200" \\
    --campaign-id abc-123 --volume 100 --dry-run
        """,
    )

    parser.add_argument("--source-api-key", required=True, help="People search API key")
    parser.add_argument("--validation-api-key", required=True, help="Email validation API key")
    parser.add_argument("--campaign-api-key", required=True, help="Campaign tool API key")
    parser.add_argument("--titles", required=True, help="Comma-separated job titles")
    parser.add_argument("--industries", default="", help="Comma-separated industries/keywords")
    parser.add_argument("--company-size", default="", help="Employee range, e.g. '11,50'")
    parser.add_argument("--locations", default="", help="Comma-separated locations")
    parser.add_argument("--keywords", default="", help="Additional search keywords")
    parser.add_argument("--campaign-id", required=True, help="Campaign UUID")
    parser.add_argument("--volume", type=int, default=500, help="Target number of leads (default: 500)")
    parser.add_argument("--exclude-file", default=None, help="Path to CSV of burned/excluded emails")
    parser.add_argument("--output-dir", default="./data/pipeline-runs/", help="Directory for run logs")
    parser.add_argument("--dry-run", action="store_true", help="Run pipeline but skip upload")

    args = parser.parse_args()

    start_time = time.time()
    os.makedirs(args.output_dir, exist_ok=True)

    print(f"\n🚀 Lead Pipeline Started — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Target: {args.volume} leads → Campaign {args.campaign_id}")
    if args.dry_run:
        print(f"   ⚠️  DRY RUN MODE — will not upload")

    # Step 1: Source
    sourced_leads = source_leads(
        api_key=getattr(args, 'source_api_key'),
        titles=args.titles,
        industries=args.industries,
        company_size=args.company_size,
        locations=args.locations,
        keywords=args.keywords,
        volume=args.volume,
    )

    if not sourced_leads:
        print("\n❌ No leads sourced. Exiting.")
        sys.exit(1)

    # Save intermediate state
    intermediate_path = os.path.join(args.output_dir, "last-sourced.json")
    with open(intermediate_path, "w") as f:
        json.dump(sourced_leads, f, indent=2)

    # Step 2: Verify
    verified_leads, verified_stats = verify_emails(args.validation_api_key, sourced_leads)

    if not verified_leads:
        print("\n❌ No leads passed verification. Exiting.")
        sys.exit(1)

    intermediate_path = os.path.join(args.output_dir, "last-verified.json")
    with open(intermediate_path, "w") as f:
        json.dump(verified_leads, f, indent=2)

    # Step 3: Deduplicate
    deduped_leads, dedup_stats = deduplicate(verified_leads, args.campaign_api_key, args.exclude_file)

    if not deduped_leads:
        print("\n⚠️  All leads already exist. Nothing to upload.")
        upload_stats = {"uploaded": 0, "failed": 0, "dry_run": args.dry_run}
    else:
        # Step 4: Upload
        upload_stats = upload_leads(args.campaign_api_key, deduped_leads, args.campaign_id, args.dry_run)

    # Step 5: Report
    print_summary(len(sourced_leads), verified_stats, dedup_stats, upload_stats)

    save_report(
        args.output_dir,
        sourced=len(sourced_leads),
        verified_stats=verified_stats,
        dedup_stats=dedup_stats,
        upload_stats=upload_stats,
        leads_uploaded=deduped_leads,
        args=args,
    )

    elapsed = time.time() - start_time
    print(f"⏱️  Completed in {elapsed/60:.1f} minutes")


if __name__ == "__main__":
    main()
