#!/usr/bin/env python3
"""
PII / Sensitive Data Sanitizer
Scans files for personally identifiable information and sensitive data.
Can report findings (--scan) or redact them in place (--sanitize).

Usage:
    python3 security/sanitizer.py --scan --file path/to/file.py
    python3 security/sanitizer.py --scan --dir . --recursive
    python3 security/sanitizer.py --sanitize --file path/to/file.py
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# ---------------------------------------------------------------------------
# Default configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = SCRIPT_DIR / "sanitizer-config.json"

SUPPORTED_EXTENSIONS = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".env"}

DEFAULT_SKIP_PATHS = {"node_modules", ".git", "__pycache__", ".env.example"}

# ---------------------------------------------------------------------------
# Detection patterns
# ---------------------------------------------------------------------------

# Each entry: (label, placeholder_bracket, placeholder_redacted, regex, flags)
# Order matters – more specific patterns should come first.

PATTERNS: list[tuple[str, str, str, str, int]] = [
    # SSN (xxx-xx-xxxx)
    (
        "SSN",
        "[SSN]",
        "[REDACTED]",
        r"\b\d{3}-\d{2}-\d{4}\b",
        0,
    ),
    # API keys / tokens  (sk-..., ghp_..., op_..., Bearer ...)
    (
        "API_KEY",
        "[API_KEY]",
        "[REDACTED]",
        r"(?i)\b(?:sk-[A-Za-z0-9_\-]{20,}|ghp_[A-Za-z0-9]{36,}|op_[A-Za-z0-9_\-]{20,}|gho_[A-Za-z0-9]{36,}|xox[bposarc]-[A-Za-z0-9\-]{10,})\b",
        0,
    ),
    # Bearer tokens
    (
        "API_KEY",
        "[API_KEY]",
        "[REDACTED]",
        r"(?i)Bearer\s+[A-Za-z0-9_\-\.]{20,}",
        0,
    ),
    # Generic secret assignment patterns (API_KEY=..., SECRET=..., TOKEN=...)
    (
        "API_KEY",
        "[API_KEY]",
        "[REDACTED]",
        r"""(?i)(?:api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|private[_-]?key)\s*[=:]\s*["']?[A-Za-z0-9_\-\.\/\+]{16,}["']?""",
        0,
    ),
    # URLs with embedded credentials  (https://user:pass@host)
    (
        "URL_CREDENTIALS",
        "[URL_CREDENTIALS]",
        "[REDACTED]",
        r"https?://[^\s:]+:[^\s@]+@[^\s]+",
        0,
    ),
    # Email addresses
    (
        "EMAIL",
        "[EMAIL]",
        "[REDACTED]",
        r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
        0,
    ),
    # IP addresses (IPv4) – skip 0.0.0.0, 127.0.0.1, 255.255.255.255 common dev IPs
    (
        "IP_ADDRESS",
        "[IP_ADDRESS]",
        "[REDACTED]",
        r"\b(?!0\.0\.0\.0|127\.0\.0\.1|255\.255\.255\.255|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
        0,
    ),
    # Phone numbers (US-style: +1, (xxx), xxx-xxx-xxxx, etc.)
    (
        "PHONE",
        "[PHONE]",
        "[REDACTED]",
        r"(?<!\d)(?:\+?1[\s\-]?)?(?:\(\d{3}\)|\d{3})[\s\-]?\d{3}[\s\-]?\d{4}(?!\d)",
        0,
    ),
    # Dollar amounts / revenue figures  ($1,234  $1,234.56  $1M  $1.2B)
    (
        "AMOUNT",
        "[AMOUNT]",
        "[REDACTED]",
        r"\$\s?\d[\d,]*(?:\.\d{1,2})?(?:\s?[MBKmkb](?:illion|illion)?)?",
        0,
    ),
]

# Person-name heuristic: two or more capitalized words that look like names.
# Kept intentionally conservative to reduce false positives.
PERSON_NAME_PATTERN = re.compile(
    r"\b(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b"
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_config(config_path: Path | None = None) -> dict:
    path = config_path or DEFAULT_CONFIG_PATH
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return {}


def should_skip_path(path: Path, skip_paths: set[str]) -> bool:
    parts = path.parts
    for skip in skip_paths:
        if skip in parts:
            return True
    return False


def is_import_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith(("import ", "from ", "#!", "# ", "//", "/*"))


class Finding:
    __slots__ = ("label", "match", "line_num", "line")

    def __init__(self, label: str, match: str, line_num: int, line: str):
        self.label = label
        self.match = match
        self.line_num = line_num
        self.line = line

    def __repr__(self) -> str:
        return f"[{self.label}] line {self.line_num}: {self.match!r}"


def scan_line(
    line: str,
    line_num: int,
    compiled_patterns: list[tuple[str, str, str, re.Pattern]],
    company_patterns: list[tuple[re.Pattern, str, str]],
    person_patterns: list[tuple[re.Pattern, str, str]],
    placeholder_format: str,
    allow_patterns: list[str] | None = None,
) -> list[Finding]:
    """Return findings for a single line."""
    if is_import_line(line):
        return []

    # Skip lines matching allow_patterns
    if allow_patterns:
        for ap in allow_patterns:
            if ap in line:
                return []

    findings: list[Finding] = []

    for label, ph_bracket, ph_redacted, pat in compiled_patterns:
        for m in pat.finditer(line):
            findings.append(Finding(label, m.group(), line_num, line.rstrip()))

    # Company blocklist
    for cpat, ph_bracket, ph_redacted in company_patterns:
        for m in cpat.finditer(line):
            findings.append(Finding("COMPANY", m.group(), line_num, line.rstrip()))

    # Person blocklist
    for ppat, ph_bracket, ph_redacted in person_patterns:
        for m in ppat.finditer(line):
            findings.append(Finding("PERSON", m.group(), line_num, line.rstrip()))

    # Person-name heuristic
    for m in PERSON_NAME_PATTERN.finditer(line):
        findings.append(Finding("PERSON", m.group(), line_num, line.rstrip()))

    return findings


def compile_patterns(
    config: dict,
) -> tuple[
    list[tuple[str, str, str, re.Pattern]],
    list[tuple[re.Pattern, str, str]],
    list[tuple[re.Pattern, str, str]],
]:
    """Compile all regex patterns from defaults + config."""
    placeholder_fmt = config.get("placeholder_format", "bracket")

    compiled = []
    for label, ph_b, ph_r, raw, flags in PATTERNS:
        compiled.append((label, ph_b, ph_r, re.compile(raw, flags)))

    # Custom patterns from config
    for entry in config.get("custom_patterns", []):
        if isinstance(entry, str):
            compiled.append(
                ("CUSTOM", "[CUSTOM]", "[REDACTED]", re.compile(entry))
            )
        elif isinstance(entry, dict):
            compiled.append((
                entry.get("label", "CUSTOM"),
                f"[{entry.get('label', 'CUSTOM')}]",
                "[REDACTED]",
                re.compile(entry["pattern"]),
            ))

    # Company blocklist
    company_patterns = []
    for name in config.get("company_blocklist", []):
        company_patterns.append((
            re.compile(re.escape(name), re.IGNORECASE),
            "[COMPANY]",
            "[REDACTED]",
        ))

    # Person blocklist
    person_patterns = []
    for name in config.get("person_blocklist", []):
        person_patterns.append((
            re.compile(re.escape(name), re.IGNORECASE),
            "[PERSON]",
            "[REDACTED]",
        ))

    return compiled, company_patterns, person_patterns


def get_placeholder(label: str, placeholder_format: str) -> str:
    if placeholder_format == "redacted":
        return "[REDACTED]"
    return f"[{label}]"


# ---------------------------------------------------------------------------
# File processing
# ---------------------------------------------------------------------------


def scan_file(
    filepath: Path,
    compiled: list,
    company_pats: list,
    person_pats: list,
    placeholder_format: str,
    allow_patterns: list[str] | None = None,
) -> list[Finding]:
    try:
        text = filepath.read_text(errors="replace")
    except (PermissionError, OSError) as e:
        print(f"  ⚠️  Cannot read {filepath}: {e}", file=sys.stderr)
        return []

    findings = []
    for i, line in enumerate(text.splitlines(), 1):
        findings.extend(
            scan_line(line, i, compiled, company_pats, person_pats, placeholder_format, allow_patterns)
        )
    return findings


def sanitize_file(
    filepath: Path,
    compiled: list,
    company_pats: list,
    person_pats: list,
    placeholder_format: str,
    allow_patterns: list[str] | None = None,
) -> list[Finding]:
    """Scan and replace PII in-place. Returns findings for reporting."""
    try:
        text = filepath.read_text(errors="replace")
    except (PermissionError, OSError) as e:
        print(f"  ⚠️  Cannot read {filepath}: {e}", file=sys.stderr)
        return []

    findings = []
    new_lines = []

    for i, line in enumerate(text.splitlines(), 1):
        line_findings = scan_line(
            line, i, compiled, company_pats, person_pats, placeholder_format, allow_patterns
        )
        findings.extend(line_findings)

        if line_findings and not is_import_line(line):
            # Replace matches (longest first to avoid partial replacements)
            matches = sorted(
                [(f.match, f.label) for f in line_findings],
                key=lambda x: len(x[0]),
                reverse=True,
            )
            for match_text, label in matches:
                placeholder = get_placeholder(label, placeholder_format)
                line = line.replace(match_text, placeholder)

        new_lines.append(line)

    if findings:
        filepath.write_text("\n".join(new_lines) + ("\n" if text.endswith("\n") else ""))

    return findings


def collect_files(target: Path, recursive: bool, skip_paths: set[str]) -> list[Path]:
    """Collect files with supported extensions."""
    if target.is_file():
        if target.suffix in SUPPORTED_EXTENSIONS:
            return [target]
        return []

    files = []
    if recursive:
        for fp in target.rglob("*"):
            if fp.is_file() and fp.suffix in SUPPORTED_EXTENSIONS and not should_skip_path(fp, skip_paths):
                files.append(fp)
    else:
        for fp in target.iterdir():
            if fp.is_file() and fp.suffix in SUPPORTED_EXTENSIONS and not should_skip_path(fp, skip_paths):
                files.append(fp)

    return sorted(files)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def print_report(
    all_findings: dict[str, list[Finding]], mode: str
) -> None:
    total = sum(len(f) for f in all_findings.values())
    files_affected = len(all_findings)

    if total == 0:
        print("\n✅ No PII or sensitive data found.")
        return

    action = "Found" if mode == "scan" else "Sanitized"
    print(f"\n{'=' * 60}")
    print(f"🔍 {action} {total} issue(s) across {files_affected} file(s)")
    print(f"{'=' * 60}")

    # Aggregate by type
    by_type: dict[str, int] = defaultdict(int)
    for filepath, findings in all_findings.items():
        for f in findings:
            by_type[f.label] += 1

    print("\nBy type:")
    for label, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {label:20s} {count:>4d}")

    print(f"\nBy file:")
    for filepath, findings in sorted(all_findings.items()):
        print(f"\n  📄 {filepath} ({len(findings)} finding(s))")
        for f in findings:
            print(f"     Line {f.line_num:>4d} [{f.label}]: {f.match}")

    if mode == "scan":
        print(f"\n💡 Run with --sanitize to redact these findings.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scan or sanitize files for PII and sensitive data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --scan --file config.py
  %(prog)s --scan --dir . --recursive
  %(prog)s --sanitize --dir src/ --recursive
  %(prog)s --scan --dir . --recursive --config security/sanitizer-config.json
        """,
    )

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--scan", action="store_true", help="Report findings without modifying files")
    mode_group.add_argument("--sanitize", action="store_true", help="Replace PII with safe placeholders")

    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument("--file", type=str, help="Scan a single file")
    target_group.add_argument("--dir", type=str, help="Scan a directory")

    parser.add_argument("--recursive", "-r", action="store_true", help="Recurse into subdirectories (with --dir)")
    parser.add_argument("--config", type=str, help="Path to config JSON (default: security/sanitizer-config.json)")
    parser.add_argument("--quiet", "-q", action="store_true", help="Only print summary, not individual findings")

    args = parser.parse_args()

    # Load config
    config_path = Path(args.config) if args.config else None
    config = load_config(config_path)

    placeholder_format = config.get("placeholder_format", "bracket")
    skip_paths = set(config.get("skip_paths", [])) | DEFAULT_SKIP_PATHS
    allow_patterns = config.get("allow_patterns", []) or []

    compiled, company_pats, person_pats = compile_patterns(config)

    # Determine target
    if args.file:
        target = Path(args.file)
        if not target.exists():
            print(f"❌ File not found: {target}", file=sys.stderr)
            return 2
    else:
        target = Path(args.dir)
        if not target.exists():
            print(f"❌ Directory not found: {target}", file=sys.stderr)
            return 2

    files = collect_files(target, args.recursive, skip_paths)
    if not files:
        print("No supported files found.")
        return 0

    mode = "scan" if args.scan else "sanitize"
    process_fn = scan_file if args.scan else sanitize_file

    all_findings: dict[str, list[Finding]] = {}
    for fp in files:
        findings = process_fn(fp, compiled, company_pats, person_pats, placeholder_format, allow_patterns)
        if findings:
            all_findings[str(fp)] = findings

    if not args.quiet:
        print_report(all_findings, mode)
    else:
        total = sum(len(f) for f in all_findings.values())
        if total > 0:
            action = "Found" if mode == "scan" else "Sanitized"
            print(f"{action} {total} issue(s) in {len(all_findings)} file(s)")

    # Exit code: 0 clean, 1 PII found
    return 1 if all_findings else 0


if __name__ == "__main__":
    sys.exit(main())
