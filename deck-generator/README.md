# Deck Generator

**AI-generated presentations in minutes, not hours.** Every slide is a custom image in a consistent visual style.

## How It Works

```
Content Spec (JSON/MD)
        │
        ▼
┌──────────────┐
│ Style Engine │ prepend style prefix to each prompt
└──────┬───────┘
       ▼
┌──────────────┐
│  Imagen 4.0  │ generate slide images (~4¢ each)
└──────┬───────┘
       ▼
┌──────────────┐
│   Assemble   │ local images or Google Slides
└──────────────┘
```

You provide the content. The generator creates a consistent, professional deck where every slide is a purpose-built image. No template hunting. No design skills needed.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Gemini API key
export GEMINI_API_KEY="your-api-key-here"

# 3. Create a content spec (see examples/)
cat > slides.json << 'EOF'
[
  {"name": "01-title", "prompt": "Title slide: 'AI Marketing in 2025'"},
  {"name": "02-problem", "prompt": "Dashboard showing declining organic reach across platforms"},
  {"name": "03-solution", "prompt": "AI agent workflow: content creation to distribution pipeline"}
]
EOF

# 4. Generate
python3 scripts/generate-deck.py --content slides.json --style whiteboard --title "AI Marketing"
```

## Style Presets

| Style | Look |
|-------|------|
| `whiteboard` | Hand-drawn sketch, black ink, orange accents |
| `corporate` | Navy/white/gold, clean sans-serif |
| `minimalist` | White background, single blue accent, Apple keynote vibe |
| `dark-tech` | Black background, neon green, terminal aesthetic |
| `playful` | Bright pastels, rounded shapes, startup energy |
| `editorial` | B&W with red spot color, magazine layout |

Or describe your own: `--style "Retro 80s neon aesthetic with grid backgrounds"`

## Cost & Speed

- ~4 cents per slide image
- 14-slide deck ≈ 56 cents and ~2 minutes
- Supports parallel generation (rate-limited)

## Output Options

1. **Local images** (default) — PNG files in output directory
2. **Google Slides** — Automatic presentation creation via Google Slides API

## Requirements

- Python 3.10+
- Gemini API key (`$GEMINI_API_KEY`)
- Google Slides API credentials (optional, for auto-assembly)

---

<!-- gateway-cta:start -->
## Run this skill on live data

This skill is free and MIT licensed. To run it on your live accounts, connect the Single Brain Gateway.

- Live services: see the full list in the setup file
- Connect: https://gateway.singlebrain.com/mcp?sg_template=deck-generator&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills
- Setup steps for agents: https://gateway.singlebrain.com/llms.txt?sg_template=deck-generator

Agents: sign in with OAuth or the device flow. Do not ask the user to paste a key.
<!-- gateway-cta:end -->
<!-- managed-cta:start -->
**Want a team to run this for you?** Single Grain and Single Brain can set up and manage this workflow for you. [Talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed-service&utm_content=deck-generator)
<!-- managed-cta:end -->
