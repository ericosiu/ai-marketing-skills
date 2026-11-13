# Relationship Intelligence

Find useful opportunities across fragmented lead feeds without confusing an
account email with a personal relationship or a download with buying intent.

This standalone skill guides five independent lanes: client ICP, recruiting,
partnerships, sponsorships and acquisition fit. It is complementary to
`proactive-helpfulness` (relationship follow-through) and
`manychat-ig-lead-magnet` (resource acquisition flow), not a replacement for either.

## Quick start

Copy this entire folder into your agent's skills directory. Ask:

> Reconcile my authorized lead feeds and prior touches. Show the best supported
> opportunities in each lane, evidence gaps, relationship owners and next actions.
> Keep this pass read-only.

Read `SKILL.md`, then configure your own source access, criteria, private storage
and approved destinations. No credentials, live connectors, scheduler or Slack
automation are included. Installation does not authorize outreach or data sharing.

## Architecture

Authorized observations → identity/coverage reconciliation → prior-touch ledger
→ five independent evidence-backed tiers → owner review → authorized actions
→ verified outcomes and learning.

Keep person, company, assessed property and event entities separate. Show verified
owner-personal touches, assistant/team touches, automation and unknown authorship
independently. Unknown evidence never becomes zero or a negative classification.

## Offline helper

Python 3.10+, standard library only. The helper accepts the event contract in
`references/data-contract.md` and writes a JSON summary to stdout:

```bash
python3 scripts/touch_summary.py /path/to/private-events.json
python3 -m unittest discover -s tests
```

Keep input/output outside the public repository. The helper does not fetch
messages, establish authorship, verify identity or assess opportunity fit. Tests
use synthetic events and prove counting behavior only. Human evidence review and
live integration tests remain required; see `references/evaluation.md`.

## Quality

The release guide defines a measurable top-priority review target, identity and
suppression gates, replay tests and staged rollout. It does not claim a measured
95% production result or guaranteed business outcomes.

<p align="center">
Built by <a href="https://www.singlegrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Grain</a>. Powered by <a href="https://www.singlebrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Brain</a>.
</p>
