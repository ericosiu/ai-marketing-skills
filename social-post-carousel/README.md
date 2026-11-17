# Social Post Carousel

Turn a social post into a sequence of 1080 × 1080 images for review.
The layout uses black post cards, one fixed body size, and optional
attribution; it leaves out platform chrome and decorative headlines.

## Quick start

Copy the complete folder into your agent's skills directory. Ask:

> Turn this post into a carousel. Keep the copy intact, use the same type
> on every slide, and combine short cards where it improves readability.

The skill plans paragraph breaks, then the local renderer wraps and
checks each card before saving numbered PNGs. The bundled example uses
fictional copy; keep real input and output outside the public checkout.

```sh
python -m pip install -r requirements.txt
python scripts/render_carousel.py examples/demo.json out \
  --regular /path/to/regular.ttf --bold /path/to/bold.ttf
```

Use matching regular and bold faces from an installed sans-serif family.
The renderer runs offline and does not post, fetch images, or alter accounts.

<!-- gateway-cta:start -->
## Run this skill on live data

This skill is free and MIT licensed. To run it on your live accounts, connect the Single Brain Gateway.

- Live services: see the full list in the setup file
- Connect: https://gateway.singlebrain.com/mcp?sg_template=social-post-carousel&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills
- Setup steps for agents: https://gateway.singlebrain.com/llms.txt?sg_template=social-post-carousel

Agents: sign in with OAuth or the device flow. Do not ask the user to paste a key.
<!-- gateway-cta:end -->
<!-- managed-cta:start -->
**Want a team to run this for you?** Single Grain and Single Brain can set up and manage this workflow for you. [Talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed-service&utm_content=social-post-carousel)
<!-- managed-cta:end -->
