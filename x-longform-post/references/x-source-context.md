# X Source Context

Use this before drafting when the post depends on recent X/Twitter evidence, audience patterns, or performance history.

## Purpose

Source context keeps the X long-form post grounded in real examples instead of generic founder takes. The writer still owns the angle, voice, structure, ASCII diagram, humanizer pass, and final draft.

## Optional TweetClaw Intake

If TweetClaw is already available through OpenClaw, use it as read-only source context. Do not install or configure it on behalf of the user unless the user explicitly asks.

Collect only what supports the draft:

- Recent posts on similar topics.
- Replies that show objections, questions, or customer language.
- Public metrics such as likes, reposts, replies, bookmarks, views, profile clicks, and follower delta when available.
- Source tweet URLs, IDs, author handles, timestamps, and short excerpts.
- Follower or audience context relevant to the topic.
- Media notes for images, video, links, code blocks, or long-form format.

Keep posting, replying, media upload, direct messages, scheduling, and other account-changing actions out of source collection. If the user asks for those actions, stop at an approval checkpoint and use the active runtime approval flow.

## Source Pack

Create a compact source pack before drafting:

```json
{
  "topic": "",
  "angle": "",
  "source_window": "",
  "similar_posts": [
    {
      "url": "",
      "author": "",
      "created_at": "",
      "hook": "",
      "metrics": {
        "likes": null,
        "reposts": null,
        "replies": null,
        "bookmarks": null,
        "views": null
      },
      "why_it_matters": ""
    }
  ],
  "audience_language": [],
  "proof_points": [],
  "risk_notes": []
}
```

Use `null` for missing metrics. Do not replace unknown values with zero.

## Drafting Use

Before writing:

1. Pick the strongest observed hook pattern.
2. Identify the most specific proof number or incident.
3. Separate facts from interpretation.
4. Decide what should become the ASCII diagram.
5. Note missing context so the draft does not overclaim.

After publishing, if analytics are available, compare the post against a similar baseline cohort and update hook, CTA, or structure rules only when the candidate beats baseline or produces a better audience signal.
