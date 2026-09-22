---
name: clone-site
description: Clone a website into a pixel-accurate Next.js replica by inspecting its design, extracting assets, rebuilding sections, and running visual QA. Use when asked to clone, copy, replicate, rebuild, reverse-engineer, or create a page based on an existing URL.
---

## Preamble (runs on skill start)

```bash
# Version check (silent if up to date)
python3 telemetry/version_check.py 2>/dev/null || true

# Telemetry opt-in (first run only, then remembers your choice)
python3 telemetry/telemetry_init.py 2>/dev/null || true
```

> **Privacy:** This skill logs usage locally to `~/.ai-marketing-skills/analytics/`. Remote telemetry is opt-in only. No code, file paths, or repo content is ever collected. See `telemetry/README.md`.

# Clone Site

Reverse-engineer and rebuild any website as a pixel-perfect Next.js clone.

## Quick Start

User says: "Clone yourcompany.com" or "Make a landing page like this: [url]"

## How It Works

1. **Recon** — Screenshots the target at desktop + mobile, extracts all design tokens (fonts, colors, spacing), downloads all assets
2. **Foundation** — Sets up Next.js with the target's exact fonts, colors, and global styles
3. **Component Specs** — Writes detailed specs for each section with exact CSS values from getComputedStyle()
4. **Parallel Build** — Dispatches builder agents in git worktrees, one per section
5. **Assembly & QA** — Merges everything, wires up the page, visual diff against original

## Requirements

- Chrome MCP must be enabled: `claude --chrome`
- Node.js 20+
- A Next.js + Tailwind v4 + shadcn/ui scaffold as the base project

## Setup (first time only)

```bash
cd /path/to/your-clone-project
npm install
```

## To Clone a Site

```bash
cd /path/to/your-clone-project
```

Edit `TARGET.md` with the URL and scope, then run the skill in Claude Code.

Or just tell any agent: "clone [url]" and they'll handle it.

## Full Technical Reference

The complete cloning methodology (reconnaissance, extraction, parallel dispatch, QA) is in:
`references/FULL_METHODOLOGY.md`

Only read this when actively executing a clone — it's ~500 lines of detailed instructions.

## Output

- Pixel-perfect Next.js site in your project directory
- All assets downloaded to `public/`
- Component specs in `docs/research/components/`
- Screenshots in `docs/design-references/`
- Run with `npm run dev` to preview
