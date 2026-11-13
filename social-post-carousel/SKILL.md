---
name: social-post-carousel
description: Rebuild a text post or user-supplied social screenshot as a clean, unbranded 1080 × 1080 carousel with exact copy, optional attribution, and numbered PNGs. Use for X-style social carousels, not for publishing or accessing accounts.
---

# Social Post Carousel

## Repository integration

In a full checkout, use the repository's non-blocking version check when network
access is allowed. Follow existing telemetry consent; never enable reporting
here. If permitted, log only the skill name, elapsed time, outcome and version
through the repository telemetry helper. Never log copy, filenames or avatars.
Standalone copies may skip unavailable helpers.

Turn the source into legible, brand-neutral post cards. Re-typeset the text;
do not crop whole screenshots into slides or ask an image model to draw the copy.

1. **Establish the source.** Use supplied full text over screenshot OCR.
   If only an image is supplied, transcribe what is visible and flag clipped or
   uncertain text; do not reconstruct missing content. Default to verbatim
   copy, including order, figures and punctuation. Only edit the voice, add
   hooks or add a CTA when requested.
2. **Create the slide plan.** Start with the original first line, set in the same style as all other copy. Break at
   paragraphs or idea boundaries, keeping comparisons and lists together when
   practical. Aim for four comfortably filled cards for a medium-length post.
   Combine short paragraphs before adding slides; avoid cards with unusually
   large blank areas. Add cards for long copy rather than shrink or truncate. Preserve handles in the copy as plain text, not blue links, by
   default. Use a name/handle and avatar only if supplied and appropriate;
   no verification badge, platform logo, engagement counters, status bar or
   navigation. Do not fabricate an avatar.
3. **Render.** Use a solid black background, off-white text, gray attribution
   and one fixed body size from first card to last. Place the optional author and handle on one line. Do not add display headlines, divider rules, or page counters inside the images by default; the output filenames carry slide order. Keep at least 78 px safe margins.
   Write a JSON spec with a `slides` array (strings with paragraph breaks) and
   optional `name`, `handle` and `avatar` (path relative to the JSON).
   Use the deterministic Pillow helper with regular and bold sans-serif fonts
   already installed on the machine. Do not commit screenshots, input JSON,
   logos or personal images to a public skill; the included example is synthetic.
4. **QA and deliver.** Review a contact sheet at phone scale and every PNG at
   full size when needed. Verify 1080 × 1080 dimensions, slide order, text
   coverage and absence of UI, clipping or accidental blank cards. If a slide
   overflows, split or rebalance it; do not shrink individual slides. Compare the contact sheet against any supplied visual reference before delivery. Deliver
   ordered PNGs (and a ZIP or PDF only as helpful). Do not post to a social
   account unless separately authorized.

## Run

Requires Python 3.10+ and Pillow. From the skill folder:

```sh
python scripts/render_carousel.py examples/demo.json out \
  --regular /path/to/regular.ttf --bold /path/to/bold.ttf
```

The renderer is offline; it never fetches external images or publishes. For
languages outside the font's coverage, use a font with the necessary glyphs
and inspect the output. For complex script shaping or vertical typography,
use a capable alternative renderer while retaining the same layout checks.
