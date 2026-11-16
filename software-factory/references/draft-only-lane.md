# Draft-only lane

Use this lane when a human, not the factory, must merge.

Config (`lanes.draft_only`):

- `enabled`: true
- `repos`: list of `owner/name` repos
- `base_branch`: the branch to target (often `master` or `main`)
- `max_drafts_per_day`: cap on new draft PRs (example: 5)
- `merge`: `lane_owner`

Rules:

1. Builders open PRs as drafts against the configured base branch.
2. The factory and the operator never merge, never auto-merge, and never
   mark a draft ready on these repos.
3. The factory daily merge cap does not apply here, because the factory
   does not merge.
4. The GitHub App still gets contents and pull-requests write only. No
   admin token. No branch-protection bypass.
5. Pricing, policy, or business-rule changes are not a PR first. Send the
   lane owner a written question. Build only after that owner agrees.
6. Auto-merge treats these repos as out of scope (`not_draft_only_lane`).

The lane owner runs review and QA, then merges.
