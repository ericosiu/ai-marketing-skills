---
name: video-content-engine
description: "Diagnose and transform any authorized video URL, upload, recording, transcript, podcast, interview, presentation, screen recording, webinar, ad, or published video into the strongest justified content portfolio. Use for video audits, format recommendations, long-form editing, mid-form explainers, Shorts and Reels, teasers, tutorials, case studies, paid cutdowns, captions, packaging, delivery, or publication preparation."
---

# Video Content Engine

Turn one grounded source into the strongest justified portfolio. Do not manufacture a fixed number of derivatives. Find distinct promises, select formats that can pay them off, and give every asset a portfolio job.

## Preamble

Run the repository's privacy-preserving version check and telemetry initializer when available:

```bash
python3 telemetry/version_check.py 2>/dev/null || true
python3 telemetry/telemetry_init.py 2>/dev/null || true
```

Remote telemetry is opt-in. Never log content, URLs, paths, credentials, names, or business data.

## State the operating contract

Before work, state the exact source, owner, channel, destination, requested modules, delivery format, this turn's artifact, stop condition, and known blocker class.

Preserve the source read-only. Never claim a render, upload, preview, publication, or QC pass without fresh evidence. Treat performance targets as experiments, not forecasts.

## Accept any grounded source

Accept a public or authorized URL, uploaded file, local file, transcript, audio recording, or source folder. A bare request such as `run this skill on this video` defaults to **diagnose and recommend**, not automatic production.

For a link:

1. Resolve the exact page, owner, channel, title, duration, and accessible media or transcript.
2. Prefer the original file, then an authorized downloadable master, then the published stream.
3. Never substitute a mirror, alternate upload, account, episode, or transcript.
4. If authentication, permissions, DRM, missing media, or an unavailable transcript prevents grounded analysis, request an accessible source. Do not make editorial recommendations from metadata alone.

Unless production is requested, return a brief with the source score, recommended editorial and operating modes, opportunity counts, first release wave, repairs and dependencies, production complexity, portfolio jobs, and approval required to begin.

## Inventory the source

1. Record path or URL, size, duration, streams, and SHA-256 when available.
2. Produce a speaker-aware timestamped transcript. Correct names, products, and numbers against the source.
3. Build:
   - a claim ledger separating results, estimates, anecdotes, forecasts, and targets;
   - a rights ledger for third-party media, logos, consent, embargoes, and sponsors;
   - a content-atom inventory with timestamps, viewer, promise, proof, tension, framework, payoff, visuals, caveats, and dependencies.
4. Read [references/opportunity-routing.md](references/opportunity-routing.md), score viable atoms, and record selected and rejected opportunities.

The opportunity inventory is the source of truth. Recommend how many assets the source supports; do not default to a quota.

## Choose the transformation

Read [references/quality-gates.md](references/quality-gates.md). Score hook, clarity, proof, pacing, and payoff from 0–20 each.

Choose the least destructive editorial mode:

1. **Polish** — remove errors, dead air, and technical distractions.
2. **Tighten** — remove repetition and tangents while preserving structure.
3. **Re-architect** — rebuild the cold open, move proof, reorder sections, and bridge gaps.
4. **Rebuild** — add pickups, narration, demonstrations, or graphics to create a materially new product.

For Tighten, Re-architect, or Rebuild, create an exact-source word- or sentence-level timestamped transcript before final cuts. Memo timestamps are section guides, never literal cut points.

Read [references/format-modes.md](references/format-modes.md). Select one primary mode and justified secondary modules. When no mode is named, default to **Portfolio Audit** and recommend the smallest useful release wave.

## Lock the portfolio spine

Write:

`[Viewer] should believe [verdict] because [proof], then use [framework] to reach [outcome].`

Give each selected asset one promise, viewer, platform, job, payoff, parent, destination, and packaging intent. Reject repeated promises, incomplete excerpts, unsupported claims, and assets that cannot stand alone.

## Produce selected modules

### Long-form

Create a cut/reorder map and EDL before rendering. Resolve clips against the exact transcript and begin and end on complete thoughts. Run:

```bash
python3 scripts/audit_edit_boundaries.py \
  --transcript <exact-source-transcript.json> \
  --clips <retained-clips.json> \
  --output <boundary-audit.json>
```

After rendering, transcribe the master and review every join. Record the left tail, right head, transition, verdict, and repair. Technical decoding does not replace semantic review. Preserve previous renders as versioned files.

### Mid-form

Create self-contained 3–12 minute videos around one framework, case study, question, argument, or demonstration. Give each an independent hook, context, proof, payoff, package, and destination.

### Short-form and micro

Create 15–90 second vertical assets only from complete atoms. Start on the hook, preserve claim context, render at 1080×1920, include burned captions plus SRT, and end on a payoff or useful question.

Create 6–20 second teasers, hook tests, story units, paid cutdowns, or quote motion only when they route truthfully. Label promotional clips separately.

### Captions and opening treatment

Default masters to readable burned-in captions plus matching SRT unless the user opts out. Validate monotonic non-overlapping cues, at most two lines, mobile-safe margins, and cue end at or before the master.

Default the first three seconds to a designed hook overlay unless the brief requires a clean opening. Reinforce the spoken promise without strengthening the claim. Check collisions with captions, lower thirds, chapter cards, and qualifiers. Claim qualifiers take priority.

### Carousels and written derivatives

Produce a swipe narrative, newsletter, article, post, thread, show notes, checklist, or summary when the format improves comprehension or distribution. Require supplied brand assets or use a neutral system; never reconstruct a person, mascot, logo, or identity from memory.

## Package every asset

- **Long-form:** title, thumbnail brief, cold open, first-30-second promise, description, chapters, pinned comment, and end screen.
- **Mid-form:** browse/search title, cover, opening line, series label, description, and parent route.
- **Short-form/micro:** first-frame visual, spoken hook, headline, cover, post copy, comment prompt, and CTA.
- **Carousel:** cover promise, swipe progression, caption, CTA, final slide, sources, and alt text.

Create promise hypotheses, not cosmetic variants. Reject packaging whose promise is not paid off.

## Plan distribution and control side effects

Inventory justified B-roll, screenshots, citations, diagrams, lower thirds, qualifiers, chapter cards, overlays, captions, punch-ins, music, sound design, pickups, narration, sponsor placement, and end-screen bridges. Define which visual layer yields when elements collide.

When requested, produce a release map with order, spacing, platform, routes, timely versus evergreen status, cannibalization warnings, and recut windows.

Never publish, schedule, upload, change sharing, spend quota, or activate a campaign without explicit approval and authoritative readback.

## Converge, deliver, and learn

Apply [references/quality-gates.md](references/quality-gates.md). Confirm source integrity, portfolio alignment, media decode and timing, edit boundaries, rendered joins, captions, overlays, claims, rights, packaging, and delivery files.

`technical integrity does not equal a coherent edit`

Read [references/delivery-contract.md](references/delivery-contract.md), produce its modular folder and manifest, then run:

```bash
python3 scripts/validate_delivery.py --root <delivery-folder>
```

Return scores, mode, opportunity counts, portfolio map, runtimes, packages, sources, outputs, QC, verified destination, publication status, and a 24-hour, 72-hour, and seven-day measurement plan. Promote a lesson only after repeated comparable results.
