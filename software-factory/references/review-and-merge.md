# Review and merge

## Proof check

The operator confirms:

- An acceptance test exists, failed before the change, and passes after it.
- CI is green at the current head SHA.
- L1 and L2 reviews have run. Every BLOCKER and MAJOR finding is fixed or waived in writing by the owner.
- Blast score on the PR diff and on `base...sha` matches the intended tier.
- The GitHub App write identity is staged. Credential files are mode 600.

Record the proof check with `scripts/record_attempt.py append`.

## L1 and L2

L1 is a first pass (default example: Codex CLI). L2 is an adversarial second
pass (default example: Claude Code CLI). Both post findings as PR comments.

Do not merge with open BLOCKER or MAJOR findings.

## Merge at a pinned SHA

Re-read the PR. If the head SHA or labels changed, stop.

Use the factory wrapper, not a personal login:

```bash
scripts/factory_gh.sh api -X PUT repos/owner/name/pulls/N/merge \
  -f sha=PINNED_HEAD_SHA \
  -f merge_method=squash
```

Never pass an admin flag. Never use `gh pr merge` with an admin override.

Auto-merge (`scripts/automerge.py`) is for `blast:low` PRs in
`automerge.repos` only, when every gate passes, the KILL file is absent,
and the daily cap is open. Extra passing LOW PRs are held for the daily
card, ranked P0 down.

On a red check after an auto-merge, the watch command disables auto-merge
and opens a revert PR. Only the owner re-enables auto-merge.

## After merge

1. Append a merge ledger row if auto-merge did not already do so.
2. Claim the PR in `scripts/not_live_sweep.py --claim` before port-back.
3. Follow `portback-and-watch.md`.
