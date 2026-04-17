#!/usr/bin/env python3
"""
Lead Enricher — Enriches inbound leads with CRM data, account research,
and structured dossier format.

Designed to process leads from webhooks, forms, CRM triggers, or chat channels.
Can run as a cron job or be called directly.

Usage:
    python3 lead-enricher.py [--dry-run] [--backfill N]
    python3 lead-enricher.py --input leads.json --output enriched.json
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import urllib.parse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("lead-enricher")

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
STATE_PATH = DATA_DIR / "lead-enricher-state.json"
LOG_DIR = SCRIPT_DIR.parent / "logs" / "lead-enricher"

# CRM configuration — set via environment variables
CRM_BASE_URL = os.environ.get("CRM_BASE_URL", "https://api.hubapi.com")
CRM_API_KEY = os.environ.get("CRM_API_KEY", "")
CRM_PORTAL_ID = os.environ.get("CRM_PORTAL_ID", "")


# ── CRM Helpers ──

def crm_search_contact(email):
    """Search CRM for contact by email, return properties."""
    if not CRM_API_KEY or not email:
        return None, None

    url = f"{CRM_BASE_URL}/crm/v3/objects/contacts/search"
    headers = {
        "Authorization": f"Bearer {CRM_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "filterGroups": [{
            "filters": [{
                "propertyName": "email",
                "operator": "EQ",
                "value": email
            }]
        }],
        "properties": [
            "firstname", "lastname", "email", "phone", "company",
            "jobtitle", "website", "annualrevenue", "industry",
            "num_employees", "hs_lead_status", "lifecyclestage",
            "message", "country"
        ]
    }
    data = json.dumps(body).encode()
    req = Request(url, data=data, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            results = result.get("results", [])
            if results:
                return results[0].get("properties", {}), results[0].get("id")
            return None, None
    except Exception as e:
        log.warning(f"CRM contact search failed for {email}: {e}")
        return None, None


def crm_search_company(domain):
    """Search CRM for company by domain."""
    if not CRM_API_KEY or not domain:
        return None

    url = f"{CRM_BASE_URL}/crm/v3/objects/companies/search"
    headers = {
        "Authorization": f"Bearer {CRM_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "filterGroups": [{
            "filters": [{
                "propertyName": "domain",
                "operator": "EQ",
                "value": domain
            }]
        }],
        "properties": [
            "name", "domain", "annualrevenue", "industry",
            "numberofemployees", "description", "website"
        ]
    }
    data = json.dumps(body).encode()
    req = Request(url, data=data, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            results = result.get("results", [])
            if results:
                return results[0].get("properties", {})
            return None
    except Exception as e:
        log.warning(f"CRM company search failed for {domain}: {e}")
        return None


def format_revenue(rev_str):
    """Format revenue string nicely."""
    if not rev_str:
        return "Unknown"
    try:
        rev = float(rev_str)
        if rev >= 1_000_000_000:
            return f"${rev/1_000_000_000:.1f}B"
        elif rev >= 1_000_000:
            return f"${rev/1_000_000:.0f}M"
        elif rev >= 1_000:
            return f"${rev/1_000:.0f}K"
        else:
            return f"${rev:.0f}"
    except (ValueError, TypeError):
        return rev_str


# ── Lead Parsing ──

def parse_form_lead(data):
    """Parse a lead from a form submission (generic JSON format)."""
    info = {}
    field_map = {
        "name": ["name", "full_name", "contact_name"],
        "email": ["email", "email_address"],
        "company": ["company", "company_name", "organization"],
        "title": ["title", "job_title", "jobtitle", "position"],
        "phone": ["phone", "phone_number", "tel"],
        "website": ["website", "company_url", "domain"],
        "industry": ["industry", "vertical"],
        "employees": ["employees", "company_size", "num_employees"],
        "revenue": ["revenue", "annual_revenue", "annualrevenue"],
        "budget": ["budget", "monthly_budget"],
        "interest": ["interest", "services", "services_interested_in"],
        "source": ["source", "lead_source", "how_did_you_hear"],
        "message": ["message", "notes", "comments"],
        "country": ["country", "location"],
        "tier": ["tier", "lead_tier"],
    }

    for target, candidates in field_map.items():
        for candidate in candidates:
            val = data.get(candidate, "")
            if val and str(val).strip() and str(val).lower() not in ("n/a", "unknown", ""):
                info[target] = str(val).strip()
                break

    return info


# ── Enriched Card Builder ──

def build_enriched_card(info, crm_contact=None, crm_company=None, crm_contact_id=None):
    """Build a structured enriched lead card."""
    name = info.get("name", "Unknown")
    email = info.get("email") or (crm_contact or {}).get("email", "")
    company = info.get("company", "")
    website = info.get("website") or (crm_contact or {}).get("website", "")
    title = info.get("title") or (crm_contact or {}).get("jobtitle", "")
    phone = info.get("phone") or (crm_contact or {}).get("phone", "")
    industry = info.get("industry") or (crm_company or {}).get("industry") or (crm_contact or {}).get("industry", "")
    employees = info.get("employees") or (crm_company or {}).get("numberofemployees") or (crm_contact or {}).get("num_employees", "")
    budget = info.get("budget", "")
    source = info.get("source", "")

    revenue_raw = (info.get("revenue") or
                   (crm_company or {}).get("annualrevenue") or
                   (crm_contact or {}).get("annualrevenue", ""))
    revenue = format_revenue(revenue_raw) if revenue_raw else "Unknown"

    services = info.get("interest", "")
    problem = info.get("message", "")

    website_display = website
    if website_display:
        website_display = re.sub(r'^https?://(www\.)?', '', website_display).rstrip('/')

    # Build card
    card = {
        "name": name,
        "email": email,
        "company": company,
        "website": website_display,
        "title": title,
        "phone": phone,
        "industry": industry,
        "employees": employees,
        "revenue": revenue,
        "budget": budget,
        "services": services,
        "problem": problem,
        "source": source,
        "crm_contact_id": crm_contact_id,
        "enriched_at": datetime.now(timezone.utc).isoformat(),
    }

    # Build text summary
    lines = ["📋 ENRICHED LEAD", ""]
    lines.append(f"Name: {name}")
    if email:
        lines.append(f"Email: {email}")
    if company:
        lines.append(f"Company: {company}")
    if website_display:
        lines.append(f"Website: {website_display}")
    if title:
        lines.append(f"Title: {title}")
    if revenue != "Unknown":
        lines.append(f"Revenue: {revenue}")
    if budget:
        lines.append(f"Budget: {budget}")
    if services:
        lines.append(f"Services: {services}")
    if industry:
        lines.append(f"Industry: {industry}")
    if employees:
        lines.append(f"Employees: {employees}")
    if problem:
        lines.append(f"\nProblem: {problem[:500]}")

    footer_parts = []
    if phone:
        footer_parts.append(f"📞 {phone}")
    if source:
        footer_parts.append(f"Source: {source}")
    now = datetime.now(timezone.utc).strftime("%m/%d/%Y, %I:%M:%S %p UTC")
    footer_parts.append(f"🕐 {now}")

    if footer_parts:
        lines.append("")
        lines.append(" | ".join(footer_parts))

    card["text_summary"] = "\n".join(lines)
    return card


# ── Main ──

def process_leads(leads):
    """Enrich a list of lead dicts."""
    results = []

    for lead_data in leads:
        info = parse_form_lead(lead_data)
        if not info.get("name") and not info.get("email"):
            log.warning(f"Skipping lead with no name or email: {lead_data}")
            continue

        log.info(f"Processing lead: {info.get('name', 'Unknown')}")

        # CRM enrichment
        crm_contact = None
        crm_contact_id = None
        crm_company = None

        if info.get("email"):
            crm_contact, crm_contact_id = crm_search_contact(info["email"])

        domain = info.get("website", "")
        if domain:
            domain = re.sub(r'^https?://(www\.)?', '', domain).rstrip('/').split('/')[0]
            if domain:
                crm_company = crm_search_company(domain)

        card = build_enriched_card(info, crm_contact, crm_company, crm_contact_id)
        results.append(card)

        log.info(f"✅ Enriched: {info.get('name', 'Unknown')}")
        time.sleep(0.5)  # Rate limit

    return results


def main():
    parser = argparse.ArgumentParser(description="Lead Enricher")
    parser.add_argument("--input", help="JSON file with lead data")
    parser.add_argument("--output", help="Output JSON file for enriched leads")
    parser.add_argument("--dry-run", action="store_true", help="Process but don't write output")
    args = parser.parse_args()

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    if args.input:
        with open(args.input) as f:
            leads = json.load(f)
        if not isinstance(leads, list):
            leads = [leads]
    else:
        # Read from stdin
        leads = json.load(sys.stdin)
        if not isinstance(leads, list):
            leads = [leads]

    log.info(f"Processing {len(leads)} leads")

    results = process_leads(leads)

    if args.dry_run:
        for r in results:
            print(r.get("text_summary", ""))
            print("---")
    elif args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        log.info(f"📄 Results written to {args.output}")
    else:
        print(json.dumps(results, indent=2))

    log.info(f"Done. Enriched {len(results)} leads.")


if __name__ == "__main__":
    main()
