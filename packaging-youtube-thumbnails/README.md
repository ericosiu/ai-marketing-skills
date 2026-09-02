# YouTube Packaging

Create, render, revise, and learn from evidence-backed YouTube title-thumbnail packages without bundling a creator's private profile or assets.

## What it does

- Builds materially different verdict, proof, and utility packages.
- Uses a saved channel profile or bootstraps one from authorized channel evidence.
- Checks title-thumbnail fit, mobile legibility, semantic clarity, brand accuracy, and safe margins.
- Preserves accepted variants during precise edits and revision rounds.
- Stores sanitized Studio readbacks locally and promotes lessons only after repeated comparable evidence.
- Produces an inline review set and a tested production handoff when requested.

## Quick start

```text
Use $packaging-youtube-thumbnails with this channel profile and source content.
Create three materially different title-thumbnail packages, score them, render the
passing variants, and show the current comparison set inline.
```

If no channel profile exists, supply the channel URL and authorized reference material. The skill will create a reusable profile before packaging.

## Install and validate

Install the image-validation dependency, then run the tests:

```bash
python3 -m pip install -r packaging-youtube-thumbnails/requirements.txt
python3 -m unittest discover -s packaging-youtube-thumbnails/tests -v
python3 packaging-youtube-thumbnails/scripts/thumbnail_guard.py --help
python3 packaging-youtube-thumbnails/scripts/thumbnail_learning.py --help
```

## Privacy and publishing

Keep creator likenesses, brand assets, raw Studio exports, screenshots, viewer data, cookies, credentials, and connector responses outside this repository. Store performance state under the profile's local output root. Rendering and review are allowed; publishing or changing a live YouTube asset requires explicit approval.

---

<p align="center">
  Built by <a href="https://www.singlegrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai_marketing_skills">Single Grain</a>. Powered by <a href="https://www.singlebrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai_marketing_skills">Single Brain</a>.
</p>
