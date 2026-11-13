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
