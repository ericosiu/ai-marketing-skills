# Security Sanitizer

Scans and redacts PII / sensitive data from files in this repo.

## What It Catches

| Type | Examples |
|------|----------|
| **EMAIL** | user@example.com |
| **PHONE** | (555) 123-4567, +1-555-123-4567 |
| **SSN** | 123-45-6789 |
| **API_KEY** | sk-xxx, ghp_xxx, op_xxx, Bearer tokens, KEY=value patterns |
| **IP_ADDRESS** | Public IPv4 addresses (skips localhost/private ranges) |
| **URL_CREDENTIALS** | https://user:pass@host.com |
| **COMPANY** | Names from blocklist (configurable) |
| **PERSON** | Names from blocklist + title-prefixed names (Mr./Dr./etc.) |
| **CUSTOM** | Any regex you add to the config |

**Note:** Dollar amounts and revenue figures are not PII and are not scanned. The AMOUNT pattern was disabled in [PR #52](https://github.com/ericosiu/ai-marketing-skills/pull/52) because pricing examples and cost documentation in this repo are educational content, not sensitive data.

## Quick Start

```bash
# Scan the whole repo (dry run — changes nothing)
python3 security/sanitizer.py --scan --dir . --recursive

# Scan a single file
python3 security/sanitizer.py --scan --file path/to/file.py

# Redact PII in place
python3 security/sanitizer.py --sanitize --file path/to/file.py

# Redact everything recursively
python3 security/sanitizer.py --sanitize --dir . --recursive
```

Exit codes: `0` = clean, `1` = PII found (useful for CI).

## Configuration

Edit `security/sanitizer-config.json`:

```json
{
  "company_blocklist": ["Single Grain", "Acme Corp", "Contoso Ltd"],
  "person_blocklist": ["Jane Doe"],
  "custom_patterns": [
    "ACME-\\d{6}",
    {"label": "PROJECT_ID", "pattern": "proj_[A-Za-z0-9]{12}"}
  ],
  "skip_paths": ["node_modules", ".git", "__pycache__", ".env.example"],
  "placeholder_format": "bracket"
}
```

- **company_blocklist** — company names to always redact
- **person_blocklist** — person names to always redact
- **custom_patterns** — additional regex (string or `{label, pattern}` object)
- **skip_paths** — directory names to skip during recursive scan
- **placeholder_format** — `"bracket"` for `[EMAIL]` or `"redacted"` for `[REDACTED]`

## Pre-Commit Hook

Install to block commits containing PII:

```bash
cp security/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

The hook scans staged files and blocks the commit if anything is detected.

To bypass in emergencies: `git commit --no-verify`

## Supported File Types

`.py`, `.md`, `.txt`, `.json`, `.yaml`, `.yml`, `.env`

## No External Dependencies

Uses only Python standard library (`re`, `json`, `os`, `sys`, `argparse`, `pathlib`).
