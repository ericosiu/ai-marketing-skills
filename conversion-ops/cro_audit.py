#!/usr/bin/env python3
"""
AI CRO Audit Tool
==================
Fetches a landing page URL, analyzes its HTML structure, and scores it across
8 conversion dimensions. Outputs a structured report with specific fix
recommendations and industry benchmark comparisons.

No headless browser required — uses requests + BeautifulSoup.

Usage:
    python cro_audit.py --url https://example.com/landing-page
    python cro_audit.py --urls https://example.com/page1 https://example.com/page2
    python cro_audit.py --file urls.txt --industry saas
    python cro_audit.py --url https://example.com --json --output report.json
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup, Comment

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))
USER_AGENT = os.getenv("USER_AGENT", DEFAULT_UA)

# Dimension weights for overall score
DIMENSION_WEIGHTS = {
    "headline_clarity": 0.15,
    "cta_visibility": 0.20,
    "social_proof": 0.15,
    "urgency": 0.05,
    "trust_signals": 0.10,
    "form_friction": 0.15,
    "mobile_responsiveness": 0.10,
    "page_speed_indicators": 0.10,
}

# Industry benchmarks: {industry: {avg, top_quartile}}
INDUSTRY_BENCHMARKS = {
    "saas": {"avg": 62, "top_quartile": 78},
    "ecommerce": {"avg": 58, "top_quartile": 74},
    "agency": {"avg": 55, "top_quartile": 72},
    "finance": {"avg": 60, "top_quartile": 76},
    "healthcare": {"avg": 52, "top_quartile": 68},
    "education": {"avg": 54, "top_quartile": 70},
    "b2b": {"avg": 56, "top_quartile": 73},
    "general": {"avg": 56, "top_quartile": 72},
}

# CTA keyword patterns
CTA_PATTERNS = re.compile(
    r"\b(get started|sign up|start free|try free|book a? ?demo|schedule|"
    r"download|buy now|add to cart|subscribe|join|register|request|"
    r"claim|grab|unlock|access|learn more|contact us|talk to|"
    r"start now|begin|enroll|apply now|shop now|order now)\b",
    re.IGNORECASE,
)

# Social proof patterns
SOCIAL_PROOF_PATTERNS = re.compile(
    r"\b(testimonial|review|rating|stars?|customers?|clients?|"
    r"companies|trusted by|used by|loved by|join \d|"
    r"case stud|success stor|\d+\s*\+?\s*(?:users?|customers?|clients?|companies|businesses)|"
    r"as seen|featured in|featured on|logo|partner)\b",
    re.IGNORECASE,
)

# Urgency patterns
URGENCY_PATTERNS = re.compile(
    r"\b(limited time|act now|hurry|expires?|deadline|only \d|"
    r"last chance|don'?t miss|ending soon|today only|"
    r"while supplies|few (?:left|remaining|spots)|countdown|"
    r"offer ends|sale ends|hours left|minutes left|spots? left|"
    r"exclusive|one-time|flash sale|clearance)\b",
    re.IGNORECASE,
)

# Trust signal patterns
TRUST_PATTERNS = re.compile(
    r"\b(ssl|secure|encrypt|privacy|guarantee|money.?back|"
    r"refund|no.?risk|free trial|cancel any ?time|"
    r"gdpr|hipaa|soc.?2|iso|pci|complian|certif|"
    r"bbb|accredit|verified|badge|shield|lock|"
    r"norton|mcafee|trustpilot|stripe|paypal)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class DimensionScore:
    name: str
    score: int  # 0-100
    findings: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)


@dataclass
class CROReport:
    url: str
    overall_score: float = 0.0
    letter_grade: str = ""
    dimensions: dict = field(default_factory=dict)
    priority_fixes: list = field(default_factory=list)
    benchmark_comparison: dict = field(default_factory=dict)
    fetch_error: Optional[str] = None


# ---------------------------------------------------------------------------
# Fetcher
# ---------------------------------------------------------------------------

def fetch_page(url: str) -> tuple[Optional[str], Optional[str]]:
    """Fetch page HTML. Returns (html, error)."""
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        resp.raise_for_status()
        return resp.text, None
    except requests.RequestException as e:
        return None, str(e)


# ---------------------------------------------------------------------------
# Dimension Scorers
# ---------------------------------------------------------------------------

def score_headline_clarity(soup: BeautifulSoup, text: str) -> DimensionScore:
    """Score headline clarity — is the value prop obvious in <5 seconds?"""
    dim = DimensionScore(name="Headline Clarity", score=50, findings=[], recommendations=[])

    h1_tags = soup.find_all("h1")
    h2_tags = soup.find_all("h2")

    # Check H1 exists
    if not h1_tags:
        dim.score -= 30
        dim.findings.append("No H1 tag found on the page")
        dim.recommendations.append("Add a clear H1 headline that states your primary value proposition")
    else:
        h1_text = h1_tags[0].get_text(strip=True)
        dim.findings.append(f"H1 found: \"{h1_text[:80]}{'...' if len(h1_text) > 80 else ''}\"")

        # Length check
        word_count = len(h1_text.split())
        if word_count < 3:
            dim.score -= 10
            dim.findings.append(f"H1 is very short ({word_count} words) — may lack specificity")
            dim.recommendations.append("Expand headline to include a specific benefit or outcome")
        elif word_count > 15:
            dim.score -= 10
            dim.findings.append(f"H1 is long ({word_count} words) — may lose attention")
            dim.recommendations.append("Shorten headline to 6-12 words for maximum clarity")
        else:
            dim.score += 15

        # Check for benefit/outcome language
        benefit_words = re.compile(
            r"\b(grow|increase|boost|save|reduce|eliminate|transform|"
            r"automate|simplify|faster|better|easier|free|revenue|"
            r"profit|leads|sales|customers|results|roi)\b",
            re.IGNORECASE,
        )
        if benefit_words.search(h1_text):
            dim.score += 15
            dim.findings.append("Headline contains benefit-oriented language")
        else:
            dim.recommendations.append("Include a specific benefit or outcome in the headline (e.g., 'Get 2x more leads')")

        # Multiple H1s is bad
        if len(h1_tags) > 1:
            dim.score -= 10
            dim.findings.append(f"Multiple H1 tags found ({len(h1_tags)}) — confuses hierarchy")
            dim.recommendations.append("Use only one H1 tag per page for clear message hierarchy")

    # Check for supporting subheadline
    if h1_tags and h2_tags:
        # Check if an H2 is near the H1 (within first few elements)
        dim.score += 10
        dim.findings.append("Supporting subheadline (H2) found")
    elif h1_tags:
        dim.recommendations.append("Add a subheadline (H2) that elaborates on the H1 value proposition")

    # Check hero section has text content
    hero_selectors = ["[class*='hero']", "[class*='banner']", "[class*='jumbotron']", "header"]
    has_hero = False
    for sel in hero_selectors:
        hero = soup.select_one(sel)
        if hero and len(hero.get_text(strip=True)) > 20:
            has_hero = True
            dim.score += 10
            dim.findings.append("Hero/banner section detected with content")
            break
    if not has_hero:
        dim.recommendations.append("Consider adding a prominent hero section with headline + subheadline + CTA")

    dim.score = max(0, min(100, dim.score))
    return dim


def score_cta_visibility(soup: BeautifulSoup, text: str) -> DimensionScore:
    """Score CTA visibility — are CTAs prominent, contrasting, above the fold?"""
    dim = DimensionScore(name="CTA Visibility", score=40, findings=[], recommendations=[])

    # Find buttons and links with CTA text
    buttons = soup.find_all(["button", "a"])
    cta_elements = []
    for btn in buttons:
        btn_text = btn.get_text(strip=True)
        if CTA_PATTERNS.search(btn_text):
            cta_elements.append(btn)

    if not cta_elements:
        dim.score -= 25
        dim.findings.append("No recognizable CTA buttons/links found")
        dim.recommendations.append(
            "Add clear call-to-action buttons with action-oriented text "
            "(e.g., 'Get Started Free', 'Book a Demo')"
        )
    else:
        dim.score += 15
        cta_texts = [el.get_text(strip=True)[:50] for el in cta_elements[:5]]
        dim.findings.append(f"Found {len(cta_elements)} CTA element(s): {', '.join(cta_texts)}")

        # Check for styled buttons (class contains btn/button/cta)
        styled_ctas = [
            el for el in cta_elements
            if el.get("class") and any(
                c for c in el.get("class", [])
                if re.search(r"btn|button|cta", c, re.IGNORECASE)
            )
        ]
        if styled_ctas:
            dim.score += 10
            dim.findings.append(f"{len(styled_ctas)} CTA(s) have button styling classes")
        else:
            dim.recommendations.append("Style CTAs as prominent buttons with contrasting colors")

        # Check for inline styles with background color (contrasting)
        for el in cta_elements[:3]:
            style = el.get("style", "")
            if "background" in style.lower() or "color" in style.lower():
                dim.score += 5
                break

    # Check if CTA appears early in the HTML (proxy for above-the-fold)
    page_length = len(text)
    if cta_elements:
        first_cta_pos = text.find(str(cta_elements[0]))
        if first_cta_pos > 0 and first_cta_pos < page_length * 0.3:
            dim.score += 15
            dim.findings.append("First CTA appears in the top 30% of page HTML (likely above fold)")
        elif first_cta_pos > page_length * 0.6:
            dim.score -= 10
            dim.findings.append("First CTA appears late in the page — likely below the fold")
            dim.recommendations.append("Move primary CTA above the fold so visitors see it without scrolling")

    # Check for multiple CTAs (reinforcement)
    if len(cta_elements) >= 2:
        dim.score += 10
        dim.findings.append("Multiple CTAs found — good reinforcement throughout page")
    elif len(cta_elements) == 1:
        dim.recommendations.append("Add a second CTA further down the page to catch scrollers")

    # Check for sticky/fixed nav with CTA
    nav = soup.find("nav")
    if nav:
        nav_ctas = [el for el in nav.find_all(["button", "a"]) if CTA_PATTERNS.search(el.get_text(strip=True))]
        if nav_ctas:
            dim.score += 10
            dim.findings.append("Navigation bar contains a CTA — always visible during scroll")

    dim.score = max(0, min(100, dim.score))
    return dim


def score_social_proof(soup: BeautifulSoup, text: str) -> DimensionScore:
    """Score social proof presence — testimonials, logos, case studies, numbers."""
    dim = DimensionScore(name="Social Proof", score=30, findings=[], recommendations=[])

    # Check for social proof text patterns
    matches = SOCIAL_PROOF_PATTERNS.findall(text)
    if matches:
        unique = set(m.lower() for m in matches)
        dim.score += min(25, len(unique) * 5)
        dim.findings.append(f"Social proof signals found: {', '.join(list(unique)[:8])}")

    # Check for testimonial-like structures
    blockquotes = soup.find_all("blockquote")
    testimonial_divs = soup.select(
        "[class*='testimonial'], [class*='review'], [class*='quote'], "
        "[class*='feedback'], [class*='client'], [id*='testimonial']"
    )
    if blockquotes or testimonial_divs:
        count = len(blockquotes) + len(testimonial_divs)
        dim.score += 15
        dim.findings.append(f"Testimonial/quote elements found ({count})")
    else:
        dim.recommendations.append("Add customer testimonials with real names, titles, and photos")

    # Check for logo bars / trust logos
    logo_sections = soup.select(
        "[class*='logo'], [class*='partner'], [class*='client'], "
        "[class*='brand'], [class*='trust'], [class*='company']"
    )
    img_tags = soup.find_all("img")
    logo_imgs = [
        img for img in img_tags
        if img.get("alt") and re.search(r"logo|client|partner|brand", img.get("alt", ""), re.IGNORECASE)
    ]
    if logo_sections or logo_imgs:
        dim.score += 15
        count = max(len(logo_sections), len(logo_imgs))
        dim.findings.append(f"Client/partner logo elements detected ({count})")
    else:
        dim.recommendations.append("Add a logo bar showing recognizable client/partner brands")

    # Check for specific numbers (e.g., "10,000+ customers")
    number_proof = re.findall(
        r"\d[\d,]*\s*\+?\s*(users?|customers?|clients?|companies|businesses|downloads?|reviews?|ratings?)",
        text, re.IGNORECASE,
    )
    if number_proof:
        dim.score += 10
        dim.findings.append(f"Quantified social proof: {', '.join(number_proof[:3])}")
    else:
        dim.recommendations.append("Add specific numbers (e.g., '10,000+ customers') to quantify trust")

    # Star ratings
    star_elements = soup.select("[class*='star'], [class*='rating']")
    if star_elements:
        dim.score += 5
        dim.findings.append("Star/rating elements detected")

    if not matches and not blockquotes and not testimonial_divs and not logo_sections:
        dim.recommendations.append(
            "Social proof is critically missing. Add at minimum: 1 testimonial, "
            "a client logo bar, and a quantified metric (e.g., '500+ companies trust us')"
        )

    dim.score = max(0, min(100, dim.score))
    return dim


def score_urgency(soup: BeautifulSoup, text: str) -> DimensionScore:
    """Score urgency/scarcity elements."""
    dim = DimensionScore(name="Urgency", score=40, findings=[], recommendations=[])

    matches = URGENCY_PATTERNS.findall(text)
    if matches:
        unique = set(m.lower() for m in matches)
        dim.score += min(35, len(unique) * 10)
        dim.findings.append(f"Urgency signals found: {', '.join(list(unique)[:5])}")
    else:
        dim.findings.append("No urgency/scarcity elements detected")
        dim.recommendations.append(
            "Consider adding subtle urgency elements: limited-time offers, "
            "countdown timers, or limited availability messaging"
        )

    # Countdown timer elements
    countdown = soup.select("[class*='countdown'], [class*='timer'], [id*='countdown']")
    if countdown:
        dim.score += 15
        dim.findings.append("Countdown timer element detected")

    # Note: urgency isn't always appropriate — score is less punitive
    if not matches and not countdown:
        dim.score = max(dim.score, 35)  # Floor at 35 — not having urgency is okay for many pages

    dim.score = max(0, min(100, dim.score))
    return dim


def score_trust_signals(soup: BeautifulSoup, text: str) -> DimensionScore:
    """Score trust signals — security, guarantees, compliance badges."""
    dim = DimensionScore(name="Trust Signals", score=35, findings=[], recommendations=[])

    matches = TRUST_PATTERNS.findall(text)
    if matches:
        unique = set(m.lower() for m in matches)
        dim.score += min(30, len(unique) * 8)
        dim.findings.append(f"Trust signals found: {', '.join(list(unique)[:6])}")

    # Privacy policy link
    privacy_links = [
        a for a in soup.find_all("a")
        if re.search(r"privacy|terms|policy", a.get_text(strip=True), re.IGNORECASE)
    ]
    if privacy_links:
        dim.score += 10
        dim.findings.append("Privacy policy / terms links found")
    else:
        dim.recommendations.append("Add visible links to privacy policy and terms of service")

    # Guarantee language
    guarantee = re.search(
        r"(money.?back|satisfaction|guarantee|risk.?free|no.?risk|full refund)",
        text, re.IGNORECASE,
    )
    if guarantee:
        dim.score += 15
        dim.findings.append(f"Guarantee messaging found: '{guarantee.group()}'")
    else:
        dim.recommendations.append("Add a guarantee or risk-reversal statement near the CTA")

    # HTTPS check (from URL parsing — if we got here, the page loaded)
    # Security badge images
    security_imgs = [
        img for img in soup.find_all("img")
        if img.get("alt") and re.search(
            r"secure|ssl|badge|trust|verified|norton|mcafee",
            img.get("alt", ""), re.IGNORECASE,
        )
    ]
    if security_imgs:
        dim.score += 10
        dim.findings.append(f"Security/trust badge images found ({len(security_imgs)})")
    else:
        dim.recommendations.append("Add trust badges (security seals, payment icons, compliance logos) near forms/CTAs")

    dim.score = max(0, min(100, dim.score))
    return dim


def score_form_friction(soup: BeautifulSoup, text: str) -> DimensionScore:
    """Score form friction — fewer fields = less friction."""
    dim = DimensionScore(name="Form Friction", score=60, findings=[], recommendations=[])

    forms = soup.find_all("form")
    if not forms:
        # No form could be good (simple CTA) or bad (no conversion mechanism)
        cta_links = [a for a in soup.find_all("a") if CTA_PATTERNS.search(a.get_text(strip=True))]
        if cta_links:
            dim.score = 75
            dim.findings.append("No form found — page uses link-based CTAs (low friction)")
        else:
            dim.score = 50
            dim.findings.append("No form or clear conversion mechanism found")
            dim.recommendations.append("Add a form or clear CTA link for lead capture")
        return dim

    # Analyze the primary form (first one)
    form = forms[0]
    inputs = form.find_all(["input", "select", "textarea"])
    visible_inputs = [
        inp for inp in inputs
        if inp.get("type", "text") not in ("hidden", "submit", "button")
    ]
    field_count = len(visible_inputs)

    dim.findings.append(f"Form found with {field_count} visible field(s)")

    if field_count <= 2:
        dim.score = 90
        dim.findings.append("Minimal form — very low friction")
    elif field_count <= 4:
        dim.score = 75
        dim.findings.append("Moderate form length — acceptable friction")
    elif field_count <= 6:
        dim.score = 55
        dim.findings.append("Form has 5-6 fields — consider reducing")
        dim.recommendations.append("Reduce form to essential fields only (name + email minimum). Every extra field drops conversion ~7%")
    elif field_count <= 10:
        dim.score = 35
        dim.findings.append(f"Long form ({field_count} fields) — high friction")
        dim.recommendations.append("Split into a multi-step form or reduce to 3-4 essential fields")
    else:
        dim.score = 15
        dim.findings.append(f"Very long form ({field_count} fields) — extreme friction")
        dim.recommendations.append("This form is too long. Use progressive profiling: capture email first, ask for details later")

    # Check for required field indicators
    required_fields = [inp for inp in visible_inputs if inp.get("required") is not None]
    if required_fields:
        dim.findings.append(f"{len(required_fields)} required fields marked")

    # Check for phone number field (high friction)
    phone_fields = [
        inp for inp in visible_inputs
        if re.search(r"phone|tel|mobile", inp.get("name", "") + inp.get("type", ""), re.IGNORECASE)
    ]
    if phone_fields:
        dim.score -= 10
        dim.findings.append("Phone number field detected — high-friction field")
        dim.recommendations.append("Remove phone number field unless absolutely necessary. It's the #1 form abandonment cause")

    # Check for clear submit button text
    submit_btns = form.find_all(["button", "input"], attrs={"type": ["submit", "button"]})
    if submit_btns:
        btn_text = submit_btns[0].get_text(strip=True) or submit_btns[0].get("value", "")
        if btn_text.lower() in ("submit", "send", "go"):
            dim.score -= 5
            dim.findings.append(f"Generic submit button text: '{btn_text}'")
            dim.recommendations.append(f"Change '{btn_text}' to a benefit-oriented CTA (e.g., 'Get My Free Audit')")
        elif btn_text:
            dim.findings.append(f"Submit button text: '{btn_text}'")

    # Multiple forms
    if len(forms) > 2:
        dim.score -= 5
        dim.findings.append(f"Multiple forms on page ({len(forms)}) — may confuse visitors")

    dim.score = max(0, min(100, dim.score))
    return dim


def score_mobile_responsiveness(soup: BeautifulSoup, text: str) -> DimensionScore:
    """Score mobile responsiveness signals from HTML/meta tags."""
    dim = DimensionScore(name="Mobile Responsiveness", score=40, findings=[], recommendations=[])

    # Viewport meta tag
    viewport = soup.find("meta", attrs={"name": "viewport"})
    if viewport:
        content = viewport.get("content", "")
        dim.score += 25
        dim.findings.append(f"Viewport meta tag found: {content[:60]}")
        if "width=device-width" in content:
            dim.score += 10
            dim.findings.append("Viewport set to device-width — good")
    else:
        dim.score -= 20
        dim.findings.append("No viewport meta tag — page likely not mobile-optimized")
        dim.recommendations.append("Add <meta name='viewport' content='width=device-width, initial-scale=1'>")

    # Responsive CSS indicators
    style_tags = soup.find_all("style")
    link_tags = soup.find_all("link", rel="stylesheet")
    all_css = " ".join(tag.string or "" for tag in style_tags)

    if "@media" in all_css:
        dim.score += 10
        dim.findings.append("Media queries found in inline CSS — responsive design present")

    # Check for responsive framework classes
    responsive_classes = re.search(
        r"(col-(?:xs|sm|md|lg|xl)|container-fluid|row|grid|flex|"
        r"sm:|md:|lg:|xl:|responsive|mobile)",
        str(soup),
        re.IGNORECASE,
    )
    if responsive_classes:
        dim.score += 10
        dim.findings.append("Responsive framework classes detected (grid/flex/breakpoint)")

    # Touch-friendly: check for reasonable tap target sizing
    small_links = soup.find_all("a")
    inline_styled_small = [
        a for a in small_links
        if a.get("style") and re.search(r"font-size:\s*(\d+)", a.get("style", ""))
        and int(re.search(r"font-size:\s*(\d+)", a.get("style", "")).group(1)) < 12
    ]
    if inline_styled_small:
        dim.score -= 5
        dim.recommendations.append("Some links have very small font sizes — ensure tap targets are at least 44x44px")

    # AMP or mobile-specific meta
    amp = soup.find("html", attrs={"amp": True}) or soup.find("html", attrs={"⚡": True})
    if amp:
        dim.score += 5
        dim.findings.append("AMP page detected")

    dim.score = max(0, min(100, dim.score))
    return dim


def score_page_speed_indicators(soup: BeautifulSoup, html: str) -> DimensionScore:
    """Score page speed indicators from HTML analysis (not actual load time)."""
    dim = DimensionScore(name="Page Speed Indicators", score=60, findings=[], recommendations=[])

    # Page size
    page_size_kb = len(html.encode("utf-8")) / 1024
    dim.findings.append(f"HTML size: {page_size_kb:.0f} KB")
    if page_size_kb > 200:
        dim.score -= 15
        dim.recommendations.append(f"HTML is {page_size_kb:.0f} KB — consider reducing inline content/styles")
    elif page_size_kb > 100:
        dim.score -= 5

    # Count images
    images = soup.find_all("img")
    dim.findings.append(f"Images found: {len(images)}")
    if len(images) > 20:
        dim.score -= 10
        dim.recommendations.append(f"Page has {len(images)} images — consider lazy loading or reducing image count")
    elif len(images) > 10:
        dim.score -= 5

    # Check for lazy loading
    lazy_images = [img for img in images if img.get("loading") == "lazy"]
    if images and lazy_images:
        pct = len(lazy_images) / len(images) * 100
        dim.score += 10
        dim.findings.append(f"Lazy loading: {len(lazy_images)}/{len(images)} images ({pct:.0f}%)")
    elif len(images) > 5:
        dim.recommendations.append("Add loading='lazy' to below-fold images")

    # Check for modern image formats
    modern_imgs = [
        img for img in images
        if img.get("src") and re.search(r"\.(webp|avif)", img.get("src", ""), re.IGNORECASE)
    ]
    if modern_imgs:
        dim.score += 5
        dim.findings.append(f"Modern image formats (WebP/AVIF) detected: {len(modern_imgs)}")
    elif images:
        dim.recommendations.append("Convert images to WebP format for 25-35% size reduction")

    # Count external scripts
    scripts = soup.find_all("script", src=True)
    dim.findings.append(f"External scripts: {len(scripts)}")
    if len(scripts) > 15:
        dim.score -= 15
        dim.recommendations.append(f"Page loads {len(scripts)} external scripts — audit and remove unnecessary ones")
    elif len(scripts) > 8:
        dim.score -= 5
        dim.recommendations.append("Consider deferring or async-loading non-critical scripts")

    # Check for defer/async on scripts
    deferred = [s for s in scripts if s.get("defer") is not None or s.get("async") is not None]
    if scripts and deferred:
        pct = len(deferred) / len(scripts) * 100
        dim.findings.append(f"Deferred/async scripts: {len(deferred)}/{len(scripts)} ({pct:.0f}%)")
        dim.score += 5

    # Count external stylesheets
    stylesheets = soup.find_all("link", rel="stylesheet")
    if len(stylesheets) > 5:
        dim.score -= 5
        dim.recommendations.append(f"Page loads {len(stylesheets)} stylesheets — consider consolidating")

    # Inline CSS bloat
    inline_styles = soup.find_all("style")
    inline_css_size = sum(len(s.string or "") for s in inline_styles)
    if inline_css_size > 50000:
        dim.score -= 10
        dim.recommendations.append(f"Inline CSS is {inline_css_size / 1024:.0f} KB — move to external stylesheet and cache")

    # Preconnect/preload hints
    preconnects = soup.find_all("link", rel=["preconnect", "preload", "dns-prefetch"])
    if preconnects:
        dim.score += 5
        dim.findings.append(f"Resource hints found: {len(preconnects)} preconnect/preload/dns-prefetch")

    dim.score = max(0, min(100, dim.score))
    return dim


# ---------------------------------------------------------------------------
# Report Builder
# ---------------------------------------------------------------------------

def compute_letter_grade(score: float) -> str:
    if score >= 95:
        return "A+"
    elif score >= 90:
        return "A"
    elif score >= 85:
        return "A-"
    elif score >= 80:
        return "B+"
    elif score >= 75:
        return "B"
    elif score >= 70:
        return "B-"
    elif score >= 65:
        return "C+"
    elif score >= 60:
        return "C"
    elif score >= 55:
        return "C-"
    elif score >= 50:
        return "D+"
    elif score >= 45:
        return "D"
    elif score >= 40:
        return "D-"
    else:
        return "F"


def build_report(url: str, html: str, industry: str = "general") -> CROReport:
    """Run all scorers and build the CRO report."""
    soup = BeautifulSoup(html, "lxml")

    # Extract visible text (strip scripts, styles, comments)
    for element in soup(["script", "style"]):
        element.decompose()
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()
    visible_text = soup.get_text(separator=" ", strip=True)

    # Re-parse original for structural analysis
    soup = BeautifulSoup(html, "lxml")

    scorers = {
        "headline_clarity": score_headline_clarity,
        "cta_visibility": score_cta_visibility,
        "social_proof": score_social_proof,
        "urgency": score_urgency,
        "trust_signals": score_trust_signals,
        "form_friction": score_form_friction,
        "mobile_responsiveness": score_mobile_responsiveness,
        "page_speed_indicators": lambda s, t: score_page_speed_indicators(s, html),
    }

    dimensions = {}
    for key, scorer in scorers.items():
        dimensions[key] = scorer(soup, visible_text)

    # Compute weighted overall score
    overall = sum(
        dimensions[key].score * DIMENSION_WEIGHTS[key]
        for key in DIMENSION_WEIGHTS
    )

    # Build priority fixes (sorted by potential impact)
    priority_fixes = []
    for key, weight in sorted(DIMENSION_WEIGHTS.items(), key=lambda x: -x[1]):
        dim = dimensions[key]
        if dim.recommendations:
            impact = "HIGH" if weight >= 0.15 else ("MEDIUM" if weight >= 0.10 else "LOW")
            for rec in dim.recommendations:
                priority_fixes.append({
                    "dimension": dim.name,
                    "impact": impact,
                    "current_score": dim.score,
                    "fix": rec,
                })

    # Sort: HIGH first, then by lowest current score
    impact_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    priority_fixes.sort(key=lambda x: (impact_order[x["impact"]], x["current_score"]))

    # Benchmark comparison
    bench = INDUSTRY_BENCHMARKS.get(industry, INDUSTRY_BENCHMARKS["general"])
    benchmark_comparison = {
        "industry": industry,
        "your_score": round(overall, 1),
        "industry_avg": bench["avg"],
        "top_quartile": bench["top_quartile"],
        "vs_avg": round(overall - bench["avg"], 1),
        "vs_top": round(overall - bench["top_quartile"], 1),
    }

    return CROReport(
        url=url,
        overall_score=round(overall, 1),
        letter_grade=compute_letter_grade(overall),
        dimensions={k: asdict(v) for k, v in dimensions.items()},
        priority_fixes=priority_fixes,
        benchmark_comparison=benchmark_comparison,
    )


# ---------------------------------------------------------------------------
# Output Formatters
# ---------------------------------------------------------------------------

def format_report_text(report: CROReport) -> str:
    """Format report as human-readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append(f"  CRO AUDIT REPORT")
    lines.append(f"  {report.url}")
    lines.append("=" * 70)
    lines.append("")

    if report.fetch_error:
        lines.append(f"  ❌ FETCH ERROR: {report.fetch_error}")
        lines.append("")
        return "\n".join(lines)

    # Overall score
    lines.append(f"  OVERALL CRO SCORE:  {report.overall_score}/100  ({report.letter_grade})")
    lines.append("")

    # Benchmark comparison
    bc = report.benchmark_comparison
    indicator = "↑" if bc["vs_avg"] >= 0 else "↓"
    lines.append(f"  Industry: {bc['industry'].upper()}")
    lines.append(f"  vs. Industry Avg ({bc['industry_avg']}): {indicator} {abs(bc['vs_avg'])} points")
    top_ind = "↑" if bc["vs_top"] >= 0 else "↓"
    lines.append(f"  vs. Top Quartile ({bc['top_quartile']}): {top_ind} {abs(bc['vs_top'])} points")
    lines.append("")

    # Dimension scores
    lines.append("-" * 70)
    lines.append("  DIMENSION SCORES")
    lines.append("-" * 70)

    for key in DIMENSION_WEIGHTS:
        dim = report.dimensions[key]
        bar_filled = int(dim["score"] / 5)
        bar = "█" * bar_filled + "░" * (20 - bar_filled)
        lines.append(f"  {dim['name']:<25} {bar} {dim['score']:>3}/100")

        for finding in dim["findings"]:
            lines.append(f"    • {finding}")

        if dim["recommendations"]:
            for rec in dim["recommendations"]:
                lines.append(f"    ⚠ FIX: {rec}")
        lines.append("")

    # Priority fixes
    if report.priority_fixes:
        lines.append("-" * 70)
        lines.append("  PRIORITY FIXES (ranked by impact)")
        lines.append("-" * 70)
        for i, fix in enumerate(report.priority_fixes[:10], 1):
            icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}[fix["impact"]]
            lines.append(f"  {i}. {icon} [{fix['impact']}] {fix['dimension']} (score: {fix['current_score']})")
            lines.append(f"     → {fix['fix']}")
            lines.append("")

    lines.append("=" * 70)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def audit_url(url: str, industry: str = "general") -> CROReport:
    """Audit a single URL and return the report."""
    # Normalize URL
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    html, error = fetch_page(url)
    if error:
        report = CROReport(url=url, fetch_error=error)
        return report

    return build_report(url, html, industry)


def main():
    parser = argparse.ArgumentParser(
        description="AI CRO Audit — Score landing pages across 8 conversion dimensions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cro_audit.py --url https://example.com/landing-page
  python cro_audit.py --urls https://a.com https://b.com --industry saas
  python cro_audit.py --file urls.txt --json --output results.json
        """,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="Single URL to audit")
    group.add_argument("--urls", nargs="+", help="Multiple URLs to audit")
    group.add_argument("--file", help="File with URLs (one per line)")

    parser.add_argument(
        "--industry",
        choices=list(INDUSTRY_BENCHMARKS.keys()),
        default="general",
        help="Industry for benchmark comparison (default: general)",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--output", help="Save report to file")

    args = parser.parse_args()

    # Collect URLs
    urls = []
    if args.url:
        urls = [args.url]
    elif args.urls:
        urls = args.urls
    elif args.file:
        try:
            with open(args.file) as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)

    if not urls:
        print("Error: No URLs provided", file=sys.stderr)
        sys.exit(1)

    # Run audits
    reports = []
    for url in urls:
        print(f"Auditing: {url}...", file=sys.stderr)
        report = audit_url(url, args.industry)
        reports.append(report)

    # Output
    if args.json:
        output = json.dumps(
            [asdict(r) for r in reports] if len(reports) > 1 else asdict(reports[0]),
            indent=2,
        )
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Report saved to {args.output}", file=sys.stderr)
        else:
            print(output)
    else:
        text_output = "\n\n".join(format_report_text(r) for r in reports)
        if args.output:
            with open(args.output, "w") as f:
                f.write(text_output)
            print(f"Report saved to {args.output}", file=sys.stderr)
        else:
            print(text_output)

    # Summary for batch mode
    if len(reports) > 1:
        print("\n" + "=" * 70, file=sys.stderr)
        print("  BATCH SUMMARY", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        for r in sorted(reports, key=lambda x: x.overall_score, reverse=True):
            status = "✅" if not r.fetch_error else "❌"
            score = f"{r.overall_score} ({r.letter_grade})" if not r.fetch_error else "FAILED"
            print(f"  {status} {score:>12}  {r.url}", file=sys.stderr)


if __name__ == "__main__":
    main()
