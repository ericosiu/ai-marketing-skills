# Metricool API delivery

Use the direct API for explicitly authorized Instagram posts. Configure the exact account; never substitute one when verification fails.

## Setup

Use Python 3.10+ and install `requirements.txt`. Keep `METRICOOL_API_TOKEN` in the environment through your approved secret manager. Never store it in source, a profile, a manifest, or logs. The client does not search credential files.

Copy `profile.example.json` to a private location. Set `blog_id`, `user_id`, `instagram`, `brand_label`, and an IANA `timezone` from the authorized account. The client verifies these against `/admin/simpleProfiles` before writes. The example's null IDs deliberately prevent use until configured.

API host: `https://app.metricool.com/api`. Schema: `https://app.metricool.com/api/swagger.json`. Check the schema if an operation is rejected; do not invent endpoints.

## Caption and manifest

Inspect the supplied final video. Use one honest hook, the useful point, and the recording's CTA. Preserve qualifiers such as tested versus active. Do not promise an unverified resource or fulfillment mechanism.

Prepare a private JSON manifest:

```json
{
  "account": "example_creator",
  "timezone": "Etc/UTC",
  "posts": [{
    "video_path": "/path/to/approved.mp4",
    "title": "A source-supported title",
    "caption": "A strong hook.\n\nThe useful point.\n\nSave this workflow.",
    "cta": "Save this workflow",
    "is_ai_generated": false,
    "when": "2099-01-10T09:00:00+00:00"
  }]
}
```

Replace the illustrative date with a future open slot. The account and timezone must match the private profile. Title is packaging metadata, not a separate Instagram field. Set the AI label after inspecting the media. Structural validation does not replace editorial review.

For two posts per day, prepare two explicit slots per day. Inspect existing posts and drafts; do not move unrelated content to make room.

## Schedule

From the skill directory, run a dry run. It makes no network calls:

```bash
python3 scripts/metricool.py --profile /path/to/private-profile.json schedule /path/to/manifest.json --receipts /path/to/private-receipts
```

Within the user's authorization, add `--apply` to execute. This flag does not require another approval question.

The client verifies the account and queue, hashes the source, uploads parts without forwarding API credentials to storage, verifies hosted bytes, creates a Reel, and reads it back. Keep its receipts private. They contain account IDs, content, media URLs, and provider state.

## Reschedule or publish now

Read the exact post before moving it:

```bash
python3 scripts/metricool.py --profile /path/to/private-profile.json inspect --id 123
python3 scripts/metricool.py --profile /path/to/private-profile.json move --id 123 --uuid 456 --when now --receipts /path/to/new-move-receipt
```

Use the real post ID and UUID from readback. Add `--apply` only within explicit authorization. The client changes `publicationDate`, preserves video/caption, rejects non-pending posts, and accounts for minute truncation. It never deletes and recreates a post to move it.

## Verification and recovery

`PUBLISHING` means processing. Claim publication only after provider success and, where available, a published permalink.

Create intent is saved before the request. After a timeout, the client refuses another create. Reconcile the saved request/response with the live queue by UUID, media, caption, and date. Never erase uncertain intent to bypass the guard.

A verified receipt prevents duplicate creation on rerun. Reuse the same receipt root for the batch; different roots do not provide global idempotency. Inspect the queue before new work.

Do not automatically retry failed publication, create comment automation, or start monitoring. Report asynchronous status honestly and obtain authorization for additional scope.
