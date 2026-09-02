---
name: packaging-youtube-thumbnails
description: Use when a user supplies new video content or a channel and wants on-brand YouTube titles, thumbnail concepts, rendered variants, A/B packaging, identity profiling, precise thumbnail revisions, an inline review board, or a production handoff.
metadata:
  version: 1.0.0
  updated: 2026-09-02
---

# Packaging YouTube Thumbnails

## Overview

Turn new content into differentiated packages using a saved channel profile and evidence-backed performance memory. Keep identity, episode packaging, and performance learning separate.

**REQUIRED SUB-SKILL:** Use `imagegen` for raster generation or editing when available. Otherwise return production-ready briefs and state the rendering blocker.

## Preamble

From the repository root, run the privacy-preserving version check and telemetry initializer when available:

```bash
python3 telemetry/version_check.py 2>/dev/null || true
python3 telemetry/telemetry_init.py 2>/dev/null || true
```

Remote telemetry is opt-in. Never log content, URLs, paths, credentials, names, business data, channel analytics, or source assets.

Resolve `<skill-root>` as the installed directory that contains this `SKILL.md`. Use that absolute directory for every bundled helper and reference. Never assume the current working directory is the skill directory.

## Mode Gate

### Default mode: production

Resolve the profile in order:

1. a user-supplied path;
2. the current project's channel profile.

If neither profile exists, switch to identity bootstrap. This public package does not bundle a creator profile, likeness, channel analytics, or approved brand assets.

When a usable profile resolves:

- Validate it with `python3 <skill-root>/scripts/thumbnail_guard.py profile --profile <profile-path>`. Missing output roots or approved reference paths make the profile unusable; repair or bootstrap it instead of improvising.
- Load it before developing hooks.
- Load any user-reviewed co-design calibration and approved winning references before proposing titles or visual directions.
- Do not re-audit the channel, browse its Videos grid, or rewrite the profile.
- Use its identity rules, approved references, output root, and avoid list.
- Treat the new transcript, recording, notes, brief, links, and user additions as one source pack. Latest explicit user instructions win.
- Read [references/performance-learning.md](references/performance-learning.md). If the profile output root contains performance state, generate its preflight brief; missing state never blocks a first run.

### Identity bootstrap or refresh

Audit the channel only when:

1. no usable profile exists;
2. the user explicitly requests a refresh; or
3. the user supplies new brand examples and asks to replace or update the saved rules.

Inspect roughly 20 recent long-form thumbnails, then save or update a profile using [references/channel-profile-template.md](references/channel-profile-template.md). Do not refresh merely because time has passed.

## Production Workflow

### 0. Apply co-design calibration

When the user identifies a prior package as successful, preferred, or co-designed, inspect it before developing new hooks. Extract five things: the promise pattern, title pattern, visual grammar, rejected tendencies, and which elements must repeat versus vary.

If an approved reference is a platform screenshot, distinguish the creative from platform chrome. Crop to the creative when practical and explicitly exclude progress bars, duration badges, player controls, surrounding titles, metrics, and other interface overlays from generation prompts.

Keep the evidence classes separate:

- A direct correction, approval, or statement of preference is identity and workflow evidence. Apply it immediately to the current run.
- Public views or an isolated result are directional performance context, not causal proof.
- Studio readbacks and repeated comparable results belong in the performance ledger.

When the user explicitly asks to remember the lesson or update the skill, persist the durable preference in the active channel profile or a linked calibration reference. Save the approved visual reference with the profile, increment the profile version and review date, and state the evidence class. On later runs, start from that calibration instead of making the user rediscover it. Preserve distinct promise lanes; do not copy a podium, trophy, comparison, or other visual device when the new episode has no matching status relationship.

### 1. Read the source pack

Read all supplied content. Extract the viewer, thesis, verdict, proof, tension, stakes, consequence, and caveats. Exclude incomplete tests from claims. Verify product/model spelling. Assign concise topic tags and a comparison group for performance retrieval.

For roundups, workflow collections, tool lists, and `how I use it` episodes, run a count-and-spike audit before writing titles:

- Count every named item, then count only items with enough explanation or proof to support the promise. Use the substantive count in numeric titles and thumbnail copy.
- Identify timestamped content spikes such as achieved numbers, concrete outputs, strong opinions, mistakes, insider information, or unusually sharp lines.
- Let the substantive inventory and strongest two or three spikes determine whether the package should lead with a list, personal proof, outcome, verdict, or framework.

For show-and-tell episodes, identify the exact artifact, native result readback, screen, physical prop, or before/after that proves the promise. Prefer it as the dominant object. Do not replace available first-party proof with an abstract AI metaphor.

For future-of-work, framework, and trend-adjacent episodes, run a practical-value check before packaging. State what the viewer can build, change, decide, or do differently after watching. Keep that useful outcome as the title's main promise when the transcript supports it; use identity tension, urgency, or a trending product to sharpen the package rather than replace the takeaway.

Treat a current product or cultural moment as a trend only after verifying a recent launch, expansion, or sustained attention. When the episode contains a real use or demonstration, the product may become the thumbnail's concrete proof object even if the title stays broader. Put the product in the title only when the opening and a substantial share of the episode deliver a product-centered promise. Otherwise protect against trend-click and retention mismatch.

### 2. Load performance evidence

Generate a brief from `<output-root>/_performance/` when a ledger exists. Use comparable packages, their numeric Studio snapshots, recent repetition, and approved lessons as evidence—not immutable identity rules. Surface a 72-hour subject collision before proposing packages. Let observed results influence the hypotheses and risks, but never infer causality from raw public views or fewer than three comparable Studio readbacks.

### 3. Create the requested packages

Read [references/packaging-rubric.md](references/packaging-rubric.md). Use distinct lanes:

1. Verdict or contrarian tension.
2. Specific proof, outcome, or transformation.
3. Decision utility, framework, or real-work test.

Create the user's requested number of packages; default to three only when no count is given. Keep set IDs and their headline-thumbnail pairings stable through revision rounds. For each, provide the exact title, thumbnail copy, composition, component inventory, hook logic, and risk. Make the options materially different promise hypotheses, not cosmetic treatments. Prefer zero to four thumbnail words. Score every package, recommend one, and render immediately when requested.

When the source contains real creator usage, favor personal proof over abstract category language when the active channel calibration supports it. A concrete count, named product, real job or outcome, and explicit utility such as a setup or workflow to copy usually form a stronger list-package hypothesis than a generic `AI workforce` or trend summary. Do not force this shape when the source lacks the count or first-party use.

When a practical promise and a career-identity promise are both supported, keep them as distinct test lanes. A playbook or traits title should promise usable guidance; identity tension may supply the stakes in the thumbnail instead of displacing the utility from every candidate.

When an upstream brief requires a stricter score, honor it. For `show-and-tell-video-slate`, require 9.0+ overall with no dimension below 8.5; a numerical package remains conditional until its proof pointer is available.

Apply the rubric's simplicity and semantic-clarity gates before scoring. Do not render a candidate that exceeds its component budget or depends on unfamiliar, unexplained symbols.

### 4. Verify visible brands

Resolve the exact app or product mark before rendering. Check user-supplied files and installed first-party app resources before falling back to official model pages, launch pages, or brand kits. Distinguish an app icon from its parent-company logo, product-family mark, campaign art, mascot, and wordmark. Classify each mark, pass the verified file as a labeled input, and record its source, local path, and classification in the manifest. If the user corrects a mark, treat that correction as a hard constraint and recheck every affected current variant.

### 5. Encode the promise as visual hierarchy

Translate relational language into geometry before prompting:

- `wins`, `king`, or `best`: make the winner the largest object; use a crown only when it improves instant recognition;
- `easier`: center and enlarge the easy option; subordinate, remove, or clearly reject the alternatives;
- `versus` or `choice`: compare equivalent entities and use scale, position, or grouping to show the intended distinction;
- `use cases`: make the product the hero and group the concrete cases beneath it;
- `chases`, `replaces`, or `eliminates`: show an unambiguous direction of action without relying on the copy.

Run a copy-off test: hide the headline and describe the visual relationship in one sentence. Reject the concept if it implies the opposite winner, gives competitors equal emphasis unintentionally, or needs arrows and question marks to explain the hierarchy. As a starting ratio, make the hero about 2–3 times the visual area of each subordinate mark.

Use the channel accent for non-semantic emphasis. Preserve conventional status colors only when they carry meaning, such as green/yellow/red traffic states.

When an approved reference uses status grammar such as a podium, trophy, crown, gold winner, or visibly subordinate alternatives, reuse that grammar only for a package with a real selection, ranking, or contrast. Preserve the relationship and reading order, not merely the decoration.

For episodes about humans managing AI agents, show the creator's role and the agent's role clearly. Do not imply autonomous replacement when the content covers delegation, collaboration, or human review.

### 6. Render, persist, and QA

Read [references/image-contracts.md](references/image-contracts.md).

- Use the profile's approved subject and style references.
- Render one surfaced call per variant and save immediately to a non-overwriting versioned path.
- Inspect at original and feed size for exact text, identity, marks, legibility, claim support, complementarity, and dimensions.
- Declare critical-mark bounding boxes and run the numeric safe-zone guard in `<skill-root>/scripts/thumbnail_guard.py` before promoting a render.
- Display every current variant separately with an absolute inline image path. Do not make the reviewer open a Markdown file, directory, or download to see the images.
- Never publish or change a live YouTube asset without explicit approval.

### 7. Revise from a feedback matrix

Before revising, convert feedback into a matrix with: set/headline, target variant, locked control variant, required changes, invariants, exact copy, and rejected implications. Preserve variants the user approved or did not target. Version changed variants non-destructively and keep the prior files.

For each revised set, verify three things at feed size: the requested hero is the first read, the visual cannot be interpreted in the opposite way, and any count in the copy is supported by the content. When the video covers more items than a small displayed subset, prefer non-numeric copy such as `TOOLS WORTH USING` over an unsupported total.

### 8. Revise surgically

Load the saved target plus authoritative references. Declare the allowed edit box, state invariants, and treat the result as provisional. Run the outside-region diff guard in `<skill-root>/scripts/thumbnail_guard.py`; reject any drift before promoting a new version. After one failed retry, label the result a controlled re-render rather than a surgical edit. Leave unrelated variants untouched.

### 9. Build the review and handoff

Group the output by headline. Under each headline, show A and B inline, label their thumbnail copy, and include one feedback line: `A / B / neither / combine` plus `Changes needed`. After revisions, show the full current comparison set, including unchanged controls.

Package a team handoff with current finals, feed-size previews, authoritative brand files, source material, title-copy mappings, manifest, and edit instructions. State which files are current and which are prior versions. Refresh and test the ZIP before delivery.

Before building the handoff, map every selected phrase to one exact current file and its exact title. If the same thumbnail copy appears in more than one active composition, do not infer the target from copy alone; resolve the selected composition from the latest explicit feedback or ask for the exact variant. Include only the selected finals in the editor-facing `finals/` folder, while preserving earlier variants in the production tree. Carry any verified count correction or promise caveat into the editor README.

### 10. Learn after publishing

When the user supplies YouTube Studio metrics or requests a postmortem, store sanitized 24-hour, 72-hour, and seven-day snapshots in the local ledger and run the deterministic postmortem. Separate packaging, topic/distribution, promise/content mismatch, and undersold-content diagnoses. Propose a lesson after repeated evidence; require explicit review and three distinct 72-hour evidence videos before writing it to the approved lesson file. Never change the channel profile through this loop.

Performance learning does not replace co-design learning. Direct user corrections and approved preferences may update the channel profile when the user asks to retain them; performance claims still require the evidence thresholds above.

## Deliverable Contract

Return the profile and review date, performance warnings or evidence gaps, the requested package count, one recommendation, variants or briefs, paths, inline previews grouped by headline, provenance, numeric QA evidence, risks, and a review-ready feedback structure. When requested, also return a tested team handoff ZIP.
