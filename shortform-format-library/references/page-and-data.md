# Page and data contract

Keep the existing storage format when updating a library. The validation interchange below is optional for new libraries or an explicit export; do not migrate working data merely to fit it.

Store creator references, post observations, reusable formats, source ideas, and private user drafts separately. Use stable IDs. A format can have multiple examples; several structures can derive from one reel, but label that shared evidence.

Required reader-facing fields: format name, suitable idea types, visual example with credit/link, structural beats, three recording prompts, required proof/assets, production effort, source date, last check, and evidence status. Unknown metrics remain null. Do not label a full-sequence observation verified from a cover alone.

## Idea-to-outline behavior

1. A selected idea shows its source and two justified format suggestions. Users can browse alternatives without losing the idea.
2. Choosing a format carries the proposed opening, source timestamp, proof limits, and three prompts tailored to that idea/format pair into a new draft. Leave space for the user's own words.
3. Save before switching. Snapshot the source and format version in each draft. Starting an unrelated custom idea must clear inherited source claims.
4. Save/export the entered notes, actual prompts, reference links, source evidence, claim limits, and chosen CTA. Verify reload persistence. If download completion cannot be observed, offer a visible copyable export and state that limitation.
5. Test filters, image loading, source links, custom-idea reset, and phone readability. Preserve old drafts when archiving formats.

A shareable site is an interface. It does not automatically retrieve transcripts, research creators, generate ideas, synchronize drafts, or enforce membership. Distinguish implemented behavior from proposed features. Keep public URLs stable, verify visitor access, and retain one canonical format dataset behind public and private views. Publish only the intended audience-safe package, never a whole research directory.

## Optional validation interchange

Use an object containing three arrays:

- `posts`: each has `id`, `url`, `published_at` (ISO timestamp or null), `checked_at` (timezone-aware ISO timestamp or null), and `metrics` mapping metric names to nonnegative numbers or null.
- `formats`: each has `id`, `post_ids` (nonempty source ID list), and `prompts` (three nonempty strings).
- `ideas`: each has `id`, `source_url` (HTTP(S) URL or null for a new premise), `format_ids` (two distinct valid format IDs), `talking_prompts` (three nonempty strings), and `claim_limit` (nonempty string).

Run `python3 scripts/validate_library.py snapshot.json` from the skill directory. It checks IDs, references, prompt counts, dates, URLs, and metric values. It does not verify performance claims, source truth, page behavior, or whether an editorial recommendation is sound.
