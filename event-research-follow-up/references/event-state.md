# Durable event state and verification

Keep private attendee records, screenshots, messages and receipts in authorized private storage outside this repository. Reusable skill examples must be sanitized. Continue existing compatible artifacts instead of creating a second source of truth.

## Minimum records

| Record | Essential evidence |
|---|---|
| Person | Stable person/company IDs; names/aliases; role; event/source/date; warm/cold relationship; photo pointer; gesture, confidence and correction provenance; offer history and uncertainty |
| Contacts | Exact original email/phone/profile URL; normalized value; source and verification date/method; identity confidence; hold reason |
| Business | Operating entity; industry; revenue/headcount ranges with currency, period, scope, estimate flag and source; offer angle and unknowns |
| Readiness | Timezone and evidence/confidence; approved cohort/copy/channels/sender; reply, decline, meeting and suppression status |
| Action | Unique event/person/channel/stage key; pass; planned/in-flight/scheduled/sent/delivered/read/failed/ambiguous state; recipient and sender; UTC/local times; timestamp precision; message/thread/draft ID; receipt path |
| Outcome | Event/person/company IDs; offer and angle version; observed reply category; source message and timestamp; direct versus partner route; stated need, owner, budget/scope gaps; introduction, pilot and paid evidence; next action and authority |
| Spend | Provider, approved scope/cap, reserved and actual cost/credits, retries, receipts, input hash, model/question/contract versions and evaluation status |

Use an append-only action history with a derived current state. Before an external action, reconcile existing receipts, manual actions and concurrent work; record an in-flight action before a fragile send. Never treat a prior failure as current when a later verified receipt resolves it. Never turn an ambiguous result into permission to resend.

## Useful artifact conventions

Reuse these names when helpful; they are conventions rather than required schema:

- `prioritized-leads.json`/CSV, `app-contacts.json`, `business-evidence.json`, `outreach-angles.json`.
- `follow-up-drafts.json`/CSV, `lead-review.html`, `follow-up-review.html`.
- `email-send-plan.json`, `email-dispatch-log.json`, `email-schedule-verification.json`.
- `outreach-channel-log.json`, `outreach-status.md`, receipt files, spend ledger, `learning.jsonl`, `HANDOFF.md`.

Review pages must derive delivery state from the latest ledger and preserve approved copy versions. Regenerating drafts must not overwrite live execution state or show “not approved” for an already approved/scheduled action. Keep copy approval, provider scheduling, actual sending and read status separate.

## Completion and handoff

Reconcile source totals, unique people and company counts. Report contact coverage and company-size evidence coverage separately. For outreach, count scheduled, actually sent, deferred, replied, suppressed, failed and held records without double counting. Verify rendered review totals against durable records.

A fully classified list is not a fully enriched list; scheduled messages are not completed delivery. Track qualified opportunities and paid outcomes separately from replies. Do not claim the whole cohort finished while unresolved holds remain.

At a checkpoint, write the preserved objective, completed evidence, remaining counts, exact blocker, next authorized action and required access/input. Record collection throughput and cost so a full-roster estimate is grounded in observations. Write user corrections, false matches, UI misses and successful workarounds to local `learning.jsonl`; promote only sanitized repeatable lessons into the skill. A new event starts with fresh authority and source checks, not the prior event's send state.

For reply interpretation and commercial measurement, use [reply-outcomes.md](reply-outcomes.md). Reuse the action ledger; outcome records do not replace delivery state.
