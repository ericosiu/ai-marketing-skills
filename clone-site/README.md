# 🧬 Clone Site

**URL → Pixel-Perfect Next.js Replica in Minutes**

Point this skill at any website URL and it reverse-engineers the entire thing — design tokens, assets, interactions, responsive behavior — then rebuilds it as a production-ready Next.js app using parallel builder agents.

This isn't "screenshot → approximate HTML." This is computed-style extraction, section-by-section specification, and parallel construction with visual QA diffing against the original.

---

## What It Does

```
Input:  "Clone yourcompany.com"
Output: Pixel-perfect Next.js app with real assets, exact CSS, working interactions
```

### The Pipeline

1. **🔍 Reconnaissance** — Screenshots at desktop + mobile, extracts every design token (fonts, colors, spacing) via `getComputedStyle()`, downloads all assets (images, videos, SVGs, fonts), maps page topology

2. **🏗️ Foundation** — Sets up Next.js with the target's exact fonts, colors, and global styles. Configures Tailwind, shadcn/ui primitives, and any detected smooth scroll libraries (Lenis, Locomotive, etc.)

3. **📋 Component Specification** — Writes detailed spec files for each section with exact CSS values, interaction models (click-driven vs scroll-driven vs time-driven), multi-state behaviors, and responsive breakpoints

4. **⚡ Parallel Build** — Dispatches builder agents in isolated git worktrees, one per section (complex sections get split into sub-component agents). Extraction continues while builders work.

5. **🔗 Assembly & QA** — Merges all worktrees, wires up the page, runs visual diff comparison against the original at multiple viewports. Fixes discrepancies until pixel-perfect.

### What Makes This Different

- **Computed styles, not guesses.** Every CSS value comes from `getComputedStyle()` on the live site — not "it looks like `text-lg`"
- **Behavior extraction.** Captures scroll-triggered animations, hover states, tab switching, parallax, sticky headers — not just static layouts
- **Parallel construction.** Builder agents work simultaneously in git worktrees. A 10-section page doesn't take 10x as long.
- **Specification files as contracts.** Every component gets a detailed spec file before any builder touches it. Auditable, reproducible, debuggable.
- **Multi-state capture.** Clicks every tab, scrolls through every trigger point, hovers every interactive element. Extracts ALL states, not just the default.
- **Visual QA pass.** Side-by-side comparison at desktop and mobile after assembly. Not "done" until it matches.

---

## Requirements

- **Claude Code** with Chrome MCP enabled (`claude --chrome`)
- **Node.js 20+**
- A Next.js + Tailwind v4 + shadcn/ui scaffold (the skill expects this as the base project)

## Quick Start

### 1. Set up the project scaffold

```bash
npx create-next-app@latest my-clone --typescript --tailwind --app
cd my-clone
npx shadcn@latest init
npm install
```

### 2. Add the skill to Claude Code

Copy `SKILL.md` to your Claude Code agents or skills directory.

### 3. Clone a site

```
You: "Clone yourcompany.com"
```

Or create a `TARGET.md` with the URL and scope, then invoke the skill.

---

## How Parallel Building Works

The skill operates like a **construction foreman**:

```
┌─────────────┐
│   Recon &    │  ← You (the foreman) inspect each section
│  Extraction  │
└──────┬───────┘
       │
       ├── Section 1 spec written → dispatch Builder Agent A (worktree)
       ├── Section 2 spec written → dispatch Builder Agent B (worktree)
       ├── Section 3 spec written → dispatch Builder Agent C (worktree)
       │                            ↑ all building in parallel
       ▼
┌─────────────┐
│   Assembly   │  ← Merge worktrees, wire up page, visual QA
└─────────────┘
```

Each builder receives:
- The full component spec (inline, not a file reference)
- Section screenshot
- Asset paths (`public/images/...`)
- Shared component imports (icons, utilities)
- TypeScript verification requirement (`npx tsc --noEmit`)

Builders never have to read external docs or guess values. Everything they need is in the prompt.

---

## Component Spec Format

Every section gets a specification file before any code is written:

```markdown
# HeroSection Specification

## Overview
- Target file: src/components/HeroSection.tsx
- Interaction model: scroll-driven

## Computed Styles (from getComputedStyle)
### Container
- display: flex
- padding: 80px 64px
- maxWidth: 1440px
- background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)

## States & Behaviors
### Scroll-triggered parallax
- Trigger: scroll position > 0
- Background layer: translateY at 0.3x scroll rate
- Foreground: translateY at 0.6x scroll rate
- Transition: none (frame-synced via requestAnimationFrame)

## Assets
- Hero image: public/images/hero-dashboard.webp
- Background pattern: public/images/hero-bg-pattern.svg

## Responsive
- Desktop (1440px): 2-column, image right
- Mobile (390px): stack, image below text, full-width
```

---

## The Extraction Arsenal

The skill includes battle-tested JavaScript extraction scripts that run via Chrome MCP:

- **Asset discovery** — Enumerates all `<img>`, `<video>`, background-images, inline SVGs, and fonts on the page. Detects layered compositions (multiple images stacked in one container).
- **CSS extraction** — Deep `getComputedStyle()` capture for 50+ properties per element, walking up to 4 levels of DOM depth.
- **Behavior detection** — Scroll sweep, click sweep, hover sweep, responsive sweep at 3 viewport widths.

---

## What It Catches That You'd Miss

| Pattern | What happens if missed |
|---------|----------------------|
| Scroll-driven tabs vs click-driven tabs | Complete rewrite (hours wasted) |
| Layered images (background + overlay) | Section looks empty/broken |
| Smooth scroll library (Lenis) | Page "feels wrong" even if it looks right |
| Multi-state content (tabs with different cards) | Only default tab's content appears |
| Header scroll transition | Nav looks static and cheap |
| CSS `animation-timeline` | Scroll animations don't work |
| Video/Lottie elements | Built as static HTML mockups |

---

## Output

```
my-clone/
├── public/
│   ├── images/          # All downloaded assets
│   ├── videos/          # Video assets
│   └── seo/             # Favicons, OG images
├── src/
│   ├── app/
│   │   ├── layout.tsx   # Configured with target's fonts, metadata
│   │   ├── globals.css  # Target's exact color tokens, animations
│   │   └── page.tsx     # All sections assembled
│   ├── components/      # One component per section
│   └── types/           # TypeScript interfaces
├── docs/
│   ├── design-references/  # Screenshots at multiple viewports
│   └── research/
│       ├── PAGE_TOPOLOGY.md
│       ├── BEHAVIORS.md
│       └── components/     # Spec file per component
└── TARGET.md
```

Run `npm run dev` and you have a working clone.

---

## Limitations & Honest Caveats

- **Server-rendered dynamic content** (personalized feeds, auth-gated pages) won't be captured — this clones what's publicly visible
- **Complex JS applications** (SPAs with client-side routing, real-time data) are better suited to different approaches — this excels at marketing sites, landing pages, and content-heavy pages
- **Third-party widgets** (Intercom chat, embedded forms) are identified but not replicated
- **Exact font rendering** may vary slightly across OS/browser combinations

---

## File Structure

```
clone-site/
├── README.md              # This file
├── SKILL.md               # Claude Code skill instructions
└── references/
    └── FULL_METHODOLOGY.md  # Complete technical methodology (~500 lines)
```

---

## License

MIT — See [LICENSE](../LICENSE) in the repository root.


---

<!-- gateway-cta:start -->
## Run this skill on live data

This skill is free and MIT licensed. To run it on your live accounts, connect the Single Brain Gateway.

- Live services: see the full list in the setup file
- Connect: https://gateway.singlebrain.com/mcp?sg_template=clone-site&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills
- Setup steps for agents: https://gateway.singlebrain.com/llms.txt?sg_template=clone-site

Agents: sign in with OAuth or the device flow. Do not ask the user to paste a key.
<!-- gateway-cta:end -->
<!-- managed-cta:start -->
**Want a team to run this for you?** Single Grain and Single Brain can set up and manage this workflow for you. [Talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed-service&utm_content=clone-site)
<!-- managed-cta:end -->
