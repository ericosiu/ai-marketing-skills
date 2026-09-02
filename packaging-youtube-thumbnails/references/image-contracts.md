# Image Contracts

In every command below, resolve `<skill-root>` as the installed directory that contains the package's `SKILL.md`. Do not assume the current working directory is the skill directory.

## Output layout

```text
<output-root>/<video-slug>/
  manifest.md
  variant-01/variant-01-v001.png
  variant-02/variant-02-v001.png
  variant-03/variant-03-v001.png
```

Use `v002`, `v003`, and descriptive suffixes such as `-logo-only` for revisions. Never overwrite accepted or previously shown versions.

## Generation contract

Use one call per distinct asset. Label every input image by role.

```text
Use case: ads-marketing
Asset type: finished YouTube thumbnail, 16:9 landscape, composed for 1280x720
Primary request: <package promise>
Input images: label the subject, channel style, and each verified brand asset by role
Scene/backdrop: <channel-supported setting>
Subject: <one focal subject and one dominant relationship>
Component budget: no more than three major visual groups plus one short text block; a comparison pair may be one grouped unit
Component inventory: <group 1>; <group 2>; <group 3>; <text block>
Style/medium: high-end YouTube thumbnail; readable at phone size
Composition/framing: <placement, scale, negative space, timestamp-safe corner>
Color palette: <channel palette>
Text (verbatim): "<exact copy>"
Edge safety: complete critical marks clear left/right edges by at least 64px and top/bottom edges by at least 36px at 1280x720; keep the lower-right 154x72 timestamp area clear
Constraints: exact text once; complete official marks; numeric safe margins; no extra text; no watermark; remove or group instead of shrinking
Avoid: tiny UI, redundant props, unrelated logos, unsupported claims
```

If the design is text-free, state: `No text, letters, numbers, punctuation, labels, or UI copy anywhere.`

## Simplicity QA contract

At 320x180, identify the focal relationship in one second. Fail the variant if it exceeds three major visual groups, lacks a clear hierarchy, or depends on tiny UI or multiple secondary props. Prefer removal or grouping over shrinking. A complex official mark counts as one group when it reads as one silhouette.

Record the component inventory in the manifest. If the inventory cannot be expressed as three groups plus one text block, do not score or render the candidate.

## Geometry QA contract

At 1280x720:

- Keep every complete critical logo/mark silhouette at least 64px from the left and right edges.
- Keep every complete critical logo/mark silhouette at least 36px from the top and bottom edges.
- Keep the lower-right 154x72 YouTube timestamp area free of critical marks and copy.
- Measure the complete mark, including decorative tails, particles, butterflies, or glow—not only its central mass.

Record each critical mark's bounding box as `label:x1,y1,x2,y2` in the manifest, then run:

```bash
python3 <skill-root>/scripts/thumbnail_guard.py final \
  --image <current.png> \
  --safe-box 'brand-a:x1,y1,x2,y2' \
  --safe-box 'brand-b:x1,y1,x2,y2'
```

Any failure blocks promotion. Move or scale the mark and validate again; never waive a failure because the mark “looks mostly visible.”

## Brand verification contract

Before rendering:

1. Open an official launch page, model page, or brand kit.
2. Record the product/model spelling and asset URL.
3. Determine whether the visible mark identifies the company, app, product family, or exact model.
4. Distinguish a primary logo/wordmark from launch campaign art. Campaign art is not automatically the product logo.
5. Verify that the chosen mark visibly identifies the exact model/version or that its official source explicitly binds it to that version.
6. Record the classification evidence in the manifest, not only the asset URL.
7. Prefer the exact-model primary mark. Use a parent mark or campaign emblem only when no model-specific mark exists or the user chooses it.
8. Keep the official reference file with the run, but do not commit third-party brand assets into the skill.
9. Accept version binding only from the official asset, an official brand kit mapping, or an official model/launch page that labels or distributes that asset for the version. A filename, visual similarity, third-party download, or generic company page is insufficient.
10. When a mark will appear, pass the verified asset as a labeled generation or edit input.
11. At original detail, compare the rendered mark with the verified asset. Fail QA for changed geometry, wordmark, proportions, ambiguous model identity, incomplete silhouette, or numeric safe-zone failure.
12. Prefer a user-supplied or locally installed first-party app resource when the requested identity is the app itself; do not substitute the parent-company logo.
13. In the prompt, name each supplied file's role and explicitly forbid known substitutions, generic robots, and added wordmarks.

## Relationship contract

Write the intended relationship as a literal sentence before rendering, then encode it through scale and placement.

- The hero must be the first read at 320x180.
- A winner, easier option, or recommended product should usually occupy 2–3 times the visual area of each subordinate mark.
- Cross-outs must sit directly over the rejected objects and never intersect the hero.
- A chase or replacement must show clear direction through pose, motion, or displacement.
- Remove arrows, question marks, and connector clutter when size and position already communicate the relationship.

Hide the copy during QA. Fail the image if the remaining visual can reasonably communicate the opposite claim.

## Precise edit contract

```text
Use case: precise-object-edit
Input images: Image 1: edit target; Image 2: authoritative replacement asset
Primary request: replace only <target> with <replacement> in the same approximate bounds
Allowed edit box: <label:x1,y1,x2,y2>
Invariants: preserve face, pose, crop, background, lighting, typography, exact text, and every unrelated object
Constraints: change only the requested region; no reframing; no extra text; no watermark
```

Treat every generated edit as provisional. Inspect it at original detail, then run:

```bash
python3 <skill-root>/scripts/thumbnail_guard.py edit \
  --before <accepted-version.png> \
  --after <provisional-version.png> \
  --allowed-box 'requested-region:x1,y1,x2,y2'
```

If the guard reports outside-region drift, reject the attempt and retry once from the last accepted version with a smaller reference set and a tighter protected-region prompt. If the retry also fails, do not call it surgical: save it with a descriptive `-rerender` suffix, disclose the drift, and keep the last accepted version current.

## Delivery contract

- Emit each generated result in its own tool call.
- Copy it from the generator's default save location into the versioned output tree.
- Display every current variant separately using absolute local Markdown image paths.
- Record source path, current path, component inventory, critical-mark bounding boxes, allowed edit boxes, guard output, prompt purpose, and official asset provenance in `manifest.md`.
- Group A/B comparisons under their shared headline and keep unchanged controls visible after revisions.
- Include one copyable feedback line per set and never require the reviewer to open a separate board to see the images.
- When preparing a handoff, include current finals, 320x180 previews, authoritative assets, source material, title mappings, manifest, and edit notes; test the archive before delivery.
