#!/usr/bin/env python3
"""
Account Research Engine
Gathers intel from multiple sources per prospect, caches for 7 days.

Usage:
    python3 account-researcher.py prospects.json
    cat prospects.json | python3 account-researcher.py -
    python3 account-researcher.py --domain example.com --company "Example Corp"
    python3 account-researcher.py prospects.json --dry-run
"""

import json, os, sys, time, re, argparse
from pathlib import Path
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
CACHE_DIR = DATA_DIR / "account-research"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DAYS = 7

# --- HTML helpers ---
class MetaExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self.body_text = []
        self._in_title = False
        self._in_body = False
        self._body_chars = 0

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "meta" and attrs_d.get("name", "").lower() == "description":
            self.description = attrs_d.get("content", "")
        elif tag == "body":
            self._in_body = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_body and self._body_chars < 500:
            clean = data.strip()
            if clean:
                self.body_text.append(clean)
                self._body_chars += len(clean)


def fetch_url(url, timeout=10):
    """Fetch URL, return text or None."""
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"})
        with urlopen(req, timeout=timeout) as resp:
            return resp.read(200_000).decode("utf-8", errors="replace")
    except (URLError, HTTPError, OSError, ValueError):
        return None


def is_cached(domain):
    """Check if cache exists and is fresh (<7 days)."""
    path = CACHE_DIR / f"{domain}.json"
    if not path.exists():
        return False
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    return datetime.now() - mtime < timedelta(days=CACHE_DAYS)


def load_cache(domain):
    path = CACHE_DIR / f"{domain}.json"
    return json.loads(path.read_text()) if path.exists() else None


# --- Source collectors ---

def collect_website(domain):
    """Scrape homepage for title, description, body snippet."""
    info = {"source": "website", "title": "", "description": "", "body_snippet": "", "gaps": []}
    html = fetch_url(f"https://{domain}")
    if not html:
        html = fetch_url(f"http://{domain}")
    if not html:
        info["error"] = "Could not fetch homepage"
        return info

    ext = MetaExtractor()
    try:
        ext.feed(html)
    except Exception:
        pass
    info["title"] = ext.title.strip()
    info["description"] = ext.description.strip()
    info["body_snippet"] = " ".join(ext.body_text)[:500]

    # Detect marketing gaps
    html_lower = html.lower()
    if "/blog" not in html_lower and "blog" not in html_lower:
        info["gaps"].append("no blog detected")
    if "ga4" not in html_lower and "gtag" not in html_lower and "google-analytics" not in html_lower:
        info["gaps"].append("no Google Analytics detected")
    if len(ext.body_text) < 3:
        info["gaps"].append("thin homepage content")

    time.sleep(2)  # Rate limit
    return info


def collect_builtwith(domain):
    """BuiltWith free API for tech stack."""
    info = {"source": "builtwith", "crm": [], "marketing_tools": [], "enterprise_signals": []}

    api_key = os.environ.get("BUILTWITH_API_KEY", "free")
    url = f"https://api.builtwith.com/free1/api.json?KEY={api_key}&LOOKUP={domain}"
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        data = json.loads(raw)
    except Exception as e:
        info["error"] = f"BuiltWith unavailable: {str(e)[:80]}"
        return info

    crm_names = {"salesforce", "hubspot", "pipedrive", "zoho", "marketo", "pardot", "dynamics"}
    mktg_names = {"google analytics", "ga4", "google tag manager", "gtm", "semrush", "ahrefs",
                  "hotjar", "mixpanel", "segment", "amplitude", "heap", "optimizely", "mailchimp"}
    enterprise_names = {"cloudflare", "aws", "azure", "gcp", "fastly", "akamai", "datadog", "new relic"}

    try:
        for group in data.get("groups", data.get("Results", [{}])):
            categories = group.get("categories", group.get("Result", {}).get("Paths", []))
            if isinstance(categories, list):
                for cat in categories:
                    techs = cat.get("technologies", cat.get("Technologies", []))
                    if isinstance(techs, list):
                        for tech in techs:
                            name = tech.get("name", tech.get("Name", "")).strip()
                            name_lower = name.lower()
                            if any(c in name_lower for c in crm_names):
                                info["crm"].append(name)
                            elif any(m in name_lower for m in mktg_names):
                                info["marketing_tools"].append(name)
                            elif any(e in name_lower for e in enterprise_names):
                                info["enterprise_signals"].append(name)
    except Exception:
        pass

    time.sleep(1)
    return info


def collect_hiring(company_name):
    """Search for hiring signals. Returns dict with findings."""
    info = {"source": "hiring", "signals": []}
    info["note"] = f"Search needed: '{company_name} hiring marketing OR sales OR engineering'"
    info["query"] = f"{company_name} hiring marketing OR sales OR engineering"
    return info


def collect_news(company_name):
    """Search for recent news/funding. Returns dict with findings."""
    info = {"source": "news", "signals": []}
    info["note"] = f"Search needed: '{company_name} funding OR acquisition OR partnership'"
    info["query"] = f"{company_name} funding OR acquisition OR partnership"
    return info


def build_brief(prospect, website, builtwith, hiring, news):
    """Combine raw data into a 3-5 sentence research brief."""
    parts = []

    company = prospect.get("company_name", prospect.get("domain", "Unknown"))

    if website.get("description"):
        parts.append(f"{company}: {website['description'][:150]}")
    elif website.get("title"):
        parts.append(f"{company} ({website['title'][:100]})")
    else:
        parts.append(f"{company} — homepage could not be analyzed.")

    tech_items = builtwith.get("crm", []) + builtwith.get("marketing_tools", [])
    if tech_items:
        parts.append(f"Tech stack includes: {', '.join(tech_items[:5])}.")
    elif not builtwith.get("error"):
        parts.append("No major CRM/marketing tools detected — potential greenfield opportunity.")

    gaps = website.get("gaps", [])
    if gaps:
        parts.append(f"Marketing gaps: {', '.join(gaps)}.")

    if builtwith.get("enterprise_signals"):
        parts.append(f"Enterprise infra: {', '.join(builtwith['enterprise_signals'][:3])}.")

    if hiring.get("signals"):
        parts.append(f"Hiring: {'; '.join(hiring['signals'][:2])}.")
    if news.get("signals"):
        parts.append(f"Recent: {'; '.join(news['signals'][:2])}.")

    return " ".join(parts[:5])


def research_prospect(prospect, dry_run=False):
    """Run full research for one prospect. Returns result dict."""
    domain = prospect.get("domain", "").strip().lower()
    company = prospect.get("company_name", domain)

    if not domain:
        return {"error": "No domain provided", "prospect": prospect}

    if is_cached(domain) and not dry_run:
        print(f"  ♻️  {domain} — cached (< {CACHE_DAYS}d old)")
        return load_cache(domain)

    if dry_run:
        print(f"  🔍 [DRY RUN] Would research: {domain} ({company})")
        return {"domain": domain, "company_name": company, "dry_run": True}

    print(f"  🔍 Researching {domain} ({company})...")

    website = collect_website(domain)
    builtwith = collect_builtwith(domain)
    hiring = collect_hiring(company)
    news = collect_news(company)

    apollo = {
        "source": "lead_source",
        "employee_count": prospect.get("employee_count"),
        "industry": prospect.get("industry"),
        "hq_location": prospect.get("hq_location"),
        "growth_trend": prospect.get("growth_trend"),
    }

    brief = build_brief(prospect, website, builtwith, hiring, news)

    result = {
        "domain": domain,
        "company_name": company,
        "contact_name": prospect.get("contact_name"),
        "contact_title": prospect.get("contact_title"),
        "researched_at": datetime.now().isoformat(),
        "brief": brief,
        "sources": {
            "lead_source": apollo,
            "website": website,
            "builtwith": builtwith,
            "hiring": hiring,
            "news": news,
        }
    }

    cache_path = CACHE_DIR / f"{domain}.json"
    cache_path.write_text(json.dumps(result, indent=2))
    print(f"  ✅ {domain} — saved to {cache_path.name}")

    return result


def main():
    parser = argparse.ArgumentParser(description="Account Research Engine")
    parser.add_argument("input", nargs="?", default="-", help="JSON file path or '-' for stdin")
    parser.add_argument("--domain", help="Single domain to research")
    parser.add_argument("--company", help="Company name (with --domain)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be researched")
    args = parser.parse_args()

    if args.domain:
        prospects = [{"domain": args.domain, "company_name": args.company or args.domain}]
    elif args.input == "-":
        prospects = json.load(sys.stdin)
    else:
        with open(args.input) as f:
            prospects = json.load(f)

    if not isinstance(prospects, list):
        prospects = [prospects]

    print(f"📊 Account Research Engine — {len(prospects)} prospect(s)")
    if args.dry_run:
        print("   [DRY RUN MODE]")
    print()

    results = []
    for p in prospects:
        result = research_prospect(p, dry_run=args.dry_run)
        results.append(result)

    print(f"\n{'🏁' if not args.dry_run else '🔍'} Done — {len(results)} prospect(s) processed.")
    return results


if __name__ == "__main__":
    results = main()
    for r in results:
        if r.get("brief"):
            print(f"\n📋 {r['domain']}: {r['brief']}")
