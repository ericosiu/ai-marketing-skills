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

## Install in an agent harness

Clone this repository, then copy or import the complete `packaging-youtube-thumbnails/` directory. Do not copy only `SKILL.md`: the workflow also uses its bundled scripts, references, dependency file, and harness metadata.

For Claude Code:

```bash
mkdir -p .claude/skills
cp -R ai-marketing-skills/packaging-youtube-thumbnails \
  .claude/skills/packaging-youtube-thumbnails
```

For Codex:

```bash
mkdir -p ~/.codex/skills
cp -R ai-marketing-skills/packaging-youtube-thumbnails \
  ~/.codex/skills/packaging-youtube-thumbnails
```

For another harness, import the same complete directory and point its skill discovery at `SKILL.md`. OpenAI-compatible registries can also read `agents/openai.yaml`. Reload the harness after installation, then invoke `$packaging-youtube-thumbnails`.

## Package layout

```text
packaging-youtube-thumbnails/
├── SKILL.md                  # Workflow and delivery contract
├── agents/openai.yaml        # OpenAI-compatible display metadata
├── references/               # Profile, rubric, image, and learning contracts
├── scripts/                  # Deterministic image and performance checks
├── tests/                    # Public package and script tests
└── requirements.txt          # Image-validation dependency
```

The harness follows `SKILL.md`. The scripts enforce repeatable checks, while the reference files define the reusable contracts that the workflow loads only when needed.

## Example workflows

Create packages from source material:

```text
Use $packaging-youtube-thumbnails with this channel profile and transcript.
Create three distinct packages, render the passing variants, and show them inline.
```

Validate a final thumbnail without running the full workflow:

```bash
python3 <skill-root>/scripts/thumbnail_guard.py final \
  --image thumbnail.png \
  --safe-box 'product-mark:120,80,360,280'
```

Generate a pre-package performance brief from local, sanitized readbacks:

```bash
python3 <skill-root>/scripts/thumbnail_learning.py brief \
  --ledger <output-root>/_performance/performance-ledger.jsonl \
  --lessons <output-root>/_performance/lessons.jsonl \
  --comparison-group operator-framework \
  --published-at 2026-09-02T12:00:00Z
```

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
