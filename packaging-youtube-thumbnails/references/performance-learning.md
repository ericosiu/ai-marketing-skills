# Performance Learning Contract

In every command below, resolve `<skill-root>` as the installed directory that contains the package's `SKILL.md`. Do not assume the current working directory is the skill directory.

Use this contract before packaging when state exists and after publishing when sanitized YouTube Studio metrics are available.

## State and privacy

Store private state outside the repository:

```text
<output-root>/_performance/
  performance-ledger.jsonl
  lessons.jsonl
```

Record numeric Studio readbacks and package descriptors only. Do not store screenshots, raw exports, viewer-level data, cookies, credentials, or connector responses in the skill repository.

## Record schema

Use one JSON object per video. `comparison_group` must describe a genuinely comparable format such as `ai-model-comparison`, `business-use-cases`, or `operator-framework`.

```json
{
  "schema_version": 1,
  "video_id": "youtube-id",
  "title": "Published title",
  "published_at": "2026-07-15T12:00:00Z",
  "comparison_group": "ai-model-comparison",
  "topic_tags": ["sol", "fable", "marketing"],
  "package": {
    "hook_lane": "proof",
    "thumbnail_copy": "BUILD VS BABYSIT",
    "composition": "subject-center, model-pair, one contrast"
  },
  "metrics": [
    {
      "window_hours": 72,
      "impressions": 1000,
      "ctr_pct": 4.8,
      "retention_pct": 49.0,
      "views": 120,
      "browse_impressions": 700,
      "browse_ctr_pct": 4.5,
      "suggested_impressions": 200,
      "suggested_ctr_pct": 5.1
    }
  ]
}
```

`retention_pct` may be replaced by both `average_view_duration_seconds` and `video_length_seconds`. When Browse or Suggested impressions and CTR are supplied, the diagnostic uses their weighted CTR instead of blended total CTR.

## Commands

Upsert an initial record or later metric window without creating duplicates:

```bash
python3 <skill-root>/scripts/thumbnail_learning.py record \
  --ledger <output-root>/_performance/performance-ledger.jsonl \
  --input <sanitized-record.json>
```

Generate a pre-package brief:

```bash
python3 <skill-root>/scripts/thumbnail_learning.py brief \
  --ledger <output-root>/_performance/performance-ledger.jsonl \
  --lessons <output-root>/_performance/lessons.jsonl \
  --comparison-group ai-model-comparison \
  --topic-tag sol --topic-tag fable \
  --published-at 2026-07-15T12:00:00Z
```

The brief must show each comparable package's latest numeric impression, CTR, and retention snapshot plus any evidence gap. Use fewer than three results as directional observations only; do not convert them into a causal rule.

Diagnose one stable window:

```bash
python3 <skill-root>/scripts/thumbnail_learning.py postmortem \
  --ledger <output-root>/_performance/performance-ledger.jsonl \
  --video-id <youtube-id> --window-hours 72
```

## Diagnosis contract

Compare only records sharing the same `comparison_group` and measurement window. Require at least three comparables.

| Evidence pattern | Classification | Packaging response |
| --- | --- | --- |
| Normal impressions, materially weaker CTR | `packaging-weakness` | Rework promise and thumbnail clarity |
| Weak impressions, healthy CTR and retention | `topic-or-distribution-weakness` | Reconsider topic breadth, timing, and audience fit |
| Healthy CTR, materially weaker retention | `promise-content-mismatch` | Align package with the opening and delivered proof |
| Weak CTR, materially stronger retention | `undersold-content` | Make the value and stakes more concrete |
| Fewer than three comparables | `insufficient-evidence` | Record the result; do not learn a rule |

Treat these deterministic thresholds as triage, not causality. Review traffic sources, native A/B results, and audience context before promoting a lesson. YouTube's native title-thumbnail test result takes precedence over sequential swaps.

## Lifecycle

- **Tracked:** package hypothesis, comparison group, topic tags, sanitized 24-hour, 72-hour, and 168-hour Studio snapshots, native A/B outcome, user corrections, and approved lessons.
- **Readback source:** YouTube Studio Reach and Engagement reports. Public views are context only.
- **Cadence:** manual readback after each packaged upload at 24, 72, and 168 hours. Do not schedule cron without a separately approved read-only integration.
- **Success:** improve watch time generated per impression and native A/B watch-time share relative to comparable channel videos, while maintaining promise-content alignment.
- **Writeback:** update `performance-ledger.jsonl`; keep misses and corrections in the package fields or an additional `notes` list.
- **Promotion:** one result is a hypothesis. Approve a durable lesson only with three distinct videos in the same comparison group, complete 72-hour-or-later evidence, and explicit user review. Approved lessons apply only to that comparison group.
- **Retirement:** re-review approved lessons after 90 days or 20 newer comparable uploads. Archive a lesson when three newer comparable results contradict it or when the channel strategy changes.

Promote a reviewed lesson with:

```bash
python3 <skill-root>/scripts/thumbnail_learning.py promote-lesson \
  --ledger <output-root>/_performance/performance-ledger.jsonl \
  --lessons <output-root>/_performance/lessons.jsonl \
  --lesson-id <slug> --direction prefer \
  --rule "<reviewed rule>" \
  --evidence-video-id <id-1> --evidence-video-id <id-2> --evidence-video-id <id-3> \
  --approved-by reviewer
```

Never promote a lesson merely because a title or thumbnail looks successful in hindsight.
