# Software factory

A guarded loop for coding agents that open pull requests, never merge
themselves, and only ship after review, a pinned-SHA merge, a live
port-back, and a timed rollback watch.

Use this skill when the work is larger than a quick question. A builder
gets an acceptance test, opens a PR, and stops. L1 and L2 review must
clear every BLOCKER and MAJOR finding. An operator (or auto-merge for
LOW changes only) merges at one pinned head SHA through a GitHub App
with contents and pull-requests permissions only. The daily cap defaults
to 2. The live copy is updated only after a shadow test. Each file is
backed up as `<file>.bak-YYYYMMDD-pr-N`. A 24 hour watch can restore
those backups.

## What you get

- Blast-radius scoring that defaults to HIGH when unsure
- An append-only merge ledger and an attempt ledger
- An auto-merge tick with a KILL file, a daily cap, and no admin flag
- Port-back with shadow tests and dated backups
- A 24 hour post-release watcher with all-or-nothing rollback
- A merged-not-live sweep (drive at 4 hours, red at 24 hours)
- A daily card of extra passing LOW PRs, ranked P0 down
- An optional draft-only lane where a human merges
- A scrub tool and a gitleaks template for a new factory repo

## Quick start

```bash
export FACTORY_ROOT=/path/to/factory-work
export FACTORY_TZ=UTC
cp config/factory.example.json "$FACTORY_ROOT/config.json"
# Edit that config: repos, cap, timezone, live root, and required checks.

python3 scripts/blast_score.py < change.diff
python3 scripts/automerge.py scan
python3 scripts/portback.py plan owner/name N
python3 scripts/daily_card.py
```

Run the tests from this folder:

```bash
python3 -m pytest -q tests
```

## Layout

```
software-factory/
├── SKILL.md
├── README.md
├── requirements.txt
├── config/factory.example.json
├── scripts/          # ledger, scorer, auto-merge, port-back, watch, scrub
├── tests/
├── references/       # rules, checklists, CI and gitleaks templates
└── examples/
```

## How the loop works

1. Dispatch a builder with an acceptance test. The agent opens a PR and never merges.
2. Operator proof check, L1 review, then L2 review. Fix BLOCKER and MAJOR findings.
3. Merge at the pinned SHA through `scripts/factory_gh.sh`. Never use admin rights.
4. `portback.py plan` then `shadow` then `apply --execute`, with backups first.
5. Watch for 24 hours. On a breach, restore every backup.
6. Record ledgers. Sweep work that merged but is not live. Write the daily card.

A KILL file stops dispatch and merges. The operator may disable auto-merge.
Only the owner sets it back to enabled.

Details: `references/factory-rules.md`, `references/review-and-merge.md`,
`references/portback-and-watch.md`, and `references/draft-only-lane.md`.

## GitHub App

Store `app-id` and `private-key.pem` in `$FACTORY_GH_APP_DIR` (directory
mode 700, files mode 600). Set `FACTORY_GH_ORG` to the account that has
the App installed. Grant the App contents and pull-requests write only.
Do not grant admin and do not allow a branch-protection bypass.

`scripts/github_app_token.sh` mints a short-lived installation token on
stdout. It never writes the token to a file. The optional `cryptography`
package is required only for that helper.

## New repo

Before factory code enters a repo, scrub it and scan it:

```bash
python3 scripts/scrub_snapshot.py --map map.json --names names.txt --out repo-dir
# names.txt stays out of git
gitleaks git --config references/gitleaks.toml.example --redact --no-banner -v repo-dir
```

Copy `references/ci.yml.example` into the repo as `.github/workflows/ci.yml`
and `references/gitleaks.toml.example` as `.gitleaks.toml`.

If `MANIFEST.json` marks `repo_sha256_equals_src` as false, port only the
PR diff for that file.

## License

MIT

<p align="center">
Built by <a href="https://www.singlegrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Grain</a>. Powered by <a href="https://www.singlebrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Brain</a>.
</p>
