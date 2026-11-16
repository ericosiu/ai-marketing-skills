# Factory agent rules

Copy this file into a lane repo as `AGENTS.md`, or point dispatched agents at it.
Keep one source of truth. If a repo copy and the operator copy disagree, the
operator copy wins.

## For coding agents

1. Open a pull request. Never push to the default branch. Never merge.
2. Every PR has an acceptance test that fails before the change and passes after it.
3. Tests make no network calls and do not send, spend, or publish. Use temp copies and fake placeholder values.
4. Do not add secrets, personal data, or real tokens. Run a leak scan in CI.
5. After you open the PR, stop. The operator and the reviewers take the next step.

## Roster

- Operator: intake, dispatch, proof check, merge at the pinned head SHA. Never uses admin rights.
- Builders: coding agents. Default build agent is configurable. They never merge.
- Reviewers: L1 then L2. Post findings as PR comments so they count in the attempt ledger.
- Verifier: shadow test and port-back. Sends the operator the head SHA only after a shadow PASS. Never merges, never asks the owner, never changes pinned checkers listed in config.

## Attempt ledger and routing

Every dispatch, proof check, and merge records one append-only row through
`scripts/record_attempt.py append`. Do not hand-edit `attempts.jsonl` or
`merges.jsonl`.

Row fields: time, repo, pr, issue, implementer (`cursor-cloud`, `codex-cli`,
`claude-cli`, `human`, or `unknown`), attempt_no, acceptance_test_pass_first_try,
review_l1 (findings count), review_l2, blast_tier, merged, merged_by, reverted,
minutes_open_to_merge, minutes_merge_to_live, portback_status.

Who implemented a PR is taken only from evidence: a `cursor/*` branch, a
known agent commit author, a cloud agent id, a `codex/*` or `claude/*`
branch, or an explicit implementer label. A personal GitHub login alone is
not evidence. If there is no evidence, store `unknown`. Never guess.

Routing rule: after 7 days of data and at least 5 PRs per builder, route the
next build in that repo and blast tier to the builder with the higher
first-try pass percent. Until that bar is met, use the default builder and
reviewers from config.

## Blast radius

`scripts/blast_score.py` scores the diff. It defaults to HIGH when unsure.
Final score = max(issue prior, diff score, reviewer risk). A reviewer can
raise the score. Nothing can lower it.

| Color | Tier | Review and merge |
|---|---|---|
| green | LOW | AI L1 plus tests. May auto-merge when every gate passes and the cap is open. |
| yellow | MEDIUM | AI L2 (two reviewers, tests, security scan) plus a human merge. |
| red | HIGH | Human review and human merge. Never auto-merge. Payments, auth, secrets, schema, personal data export, external sends, infra, lockfiles, deleted tests, and large diffs are HIGH. |

## Merge

Merge at the pinned head SHA through `scripts/factory_gh.sh`. The GitHub App
gets contents and pull-requests write, nothing else. No admin token. No
branch-protection bypass. REST squash merge with `sha=<pinned sha>`.

The daily cap (default 2) counts across factory repos. Optional blocked
weekdays live in `automerge.no_merge_days`. A KILL file stops dispatch and
merges. The operator may set auto-merge `enabled` to false. Only the owner
sets it to true.

Draft-only repos are listed under `lanes.draft_only`. The factory never
merges those. See `draft-only-lane.md`.

## Port-back and watch

See `portback-and-watch.md`. A merged live-meant PR that is not LIVE after
4 hours is driven by the auto-merge tick sweep. Still stuck at 24 hours goes
red on the daily card.

## Pinned live files (optional)

Config may list paths that change in a PR but must not change live until the
owner says yes and a pin file is updated. The verifier never ports those
paths on its own.
