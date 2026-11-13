"""Render ordered, brand-neutral 1080 px post cards from a local JSON spec."""
import argparse
import json
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError:
    raise SystemExit("Install Pillow: python -m pip install -r requirements.txt")

SIZE = 1080
PAD = 78
WIDTH = SIZE - PAD * 2
WHITE = "#f5f5f5"
GRAY = "#96969b"


def wrapped(text, font):
    rows = []
    for paragraph in text.splitlines():
        if not paragraph.strip():
            rows.append("")
            continue
        row = ""
        for word in paragraph.split():
            if font.getlength(word) > WIDTH:
                raise ValueError(f"word exceeds safe width: {word[:36]!r}")
            test = f"{row} {word}" if row else word
            if font.getlength(test) > WIDTH:
                rows.append(row)
                row = word
            else:
                row = test
        rows.append(row)
    return rows


def render(spec, source, target, regular, bold):
    slides = spec.get("slides")
    if not isinstance(slides, list) or not slides or any(
        not isinstance(s, str) or not s.strip() for s in slides
    ):
        raise ValueError("slides must be a non-empty array of non-blank strings")
    target = Path(target)
    if target.exists() and any(target.glob("slide-*.png")):
        raise ValueError("output directory already contains slides; use a fresh directory")
    author, handle = spec.get("name", ""), spec.get("handle", "")
    avatar = None
    if spec.get("avatar"):
        with Image.open(source.parent / spec["avatar"]) as original:
            avatar = ImageOps.fit(ImageOps.exif_transpose(original).convert("RGB"), (110, 110))
    header = bool(author or handle or avatar)
    name_font = ImageFont.truetype(bold, 43)
    handle_font = ImageFont.truetype(regular, 40)
    rendered = []
    for index, slide in enumerate(slides, 1):
        img = Image.new("RGB", (SIZE, SIZE), "#000000")
        draw = ImageDraw.Draw(img)
        if header:
            label_x = PAD
            if avatar:
                mask = Image.new("L", (110, 110), 0)
                ImageDraw.Draw(mask).ellipse((0, 0, 109, 109), fill=255)
                img.paste(avatar, (PAD, PAD), mask)
                label_x += 132
            handle_x = label_x + (round(name_font.getlength(author)) + 18 if author else 0)
            if handle_x + handle_font.getlength(handle) > SIZE - PAD:
                raise ValueError("attribution exceeds safe width")
            if author:
                draw.text((label_x, PAD + 68), author, font=name_font, fill=WHITE, anchor="ls")
            if handle:
                draw.text((handle_x, PAD + 68), handle, font=handle_font, fill=GRAY, anchor="ls")

        size = 47
        font = ImageFont.truetype(regular, size)
        try:
            rows = wrapped(slide, font)
        except ValueError as error:
            raise ValueError(f"slide {index}: {error}") from error
        y = 263 if header else PAD + size
        line_gap = 54
        for row in rows:
            if row:
                bounds = draw.textbbox((PAD, y), row, font=font, anchor="ls")
                if bounds[2] > SIZE - PAD or bounds[3] > SIZE - PAD:
                    raise ValueError(f"slide {index} overflows; split or rebalance the copy")
                draw.text((PAD, y), row, font=font, fill=WHITE, anchor="ls")
                y += line_gap
            else:
                y += 21
        rendered.append(img)

    target.mkdir(parents=True, exist_ok=True)
    for index, img in enumerate(rendered, 1):
        img.save(target / f"slide-{index:02d}.png", optimize=True)
    print(f"Rendered {len(rendered)} slides at {SIZE} × {SIZE}.")


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("spec", type=Path)
    cli.add_argument("output", type=Path)
    cli.add_argument("--regular", required=True)
    cli.add_argument("--bold", required=True)
    args = cli.parse_args()
    try:
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        if not isinstance(spec, dict):
            raise ValueError("spec must be an object")
        render(spec, args.spec, args.output, args.regular, args.bold)
    except (ValueError, OSError) as error:
        cli.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    main()
