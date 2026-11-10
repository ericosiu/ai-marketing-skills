# Proactive Helpfulness

Turn relationship context into useful, prioritized follow-ups instead of more
messages. Reconcile replies across accessible channels, qualify actual needs,
track introductions and promises, and measure outreach without double-counting
people. Research and drafts never grant permission to send or change accounts.

## Quick start

Copy this entire directory into your agent's skill directory, then ask:

> Review the contacts and conversations I authorize. Prioritize useful next steps,
> distinguish obligations from commercial opportunities, and prepare drafts for
> approval. Do not send messages or change CRM records.

Use your host's authorized connectors. This package installs no integrations,
scheduled jobs or account permissions. Missing sources remain unknown.

## Structure

- `SKILL.md`: workflow, approval boundaries and privacy guidance.
- `references/operating-reference.md`: priority rubric, evidence schema, funnel
  definitions and synthetic behavioral review scenarios.
- `scripts/funnel.mjs`: offline arithmetic for normalized, verified events.
- `tests/funnel.test.mjs`: synthetic regressions; no real contact data.

## Offline helper

Requires Node.js 18+ and no npm packages. From the repository root:

```bash
node --test proactive-helpfulness/tests/funnel.test.mjs
node --check proactive-helpfulness/scripts/funnel.mjs
```

The helper is an importable JavaScript module, not a connector or CLI:

```js
import { summarize } from './proactive-helpfulness/scripts/funnel.mjs';
const result = summarize([], {
  campaign: 'synthetic-demo',
  start: '2026-01-01T00:00:00Z',
  asOf: '2026-01-10T00:00:00Z',
  coverage: { email: 'complete', chat: 'unknown' },
});
// contacted: 0; rates: null; coverageComplete: false
```

Pass resolved synthetic or private person IDs, not names or addresses. See the
operating reference for the complete event schema. Keep real input/output outside
the repository. The helper reads no accounts, makes no network calls and sends
no messages. It trusts caller-supplied evidence and channel coverage. Unique
people are deduplicated; channel sends count event rows, so remove duplicate
exports before use. It reports a bounded cohort, not a full CRM history.

## Example decision

An owed introduction may be the first action even without a sales opportunity.
A warm prospect with a feasible need may be commercially promising while budget
remains unknown. A reply on chat can make an email chase stale. Return the source,
next action, owner and approval state rather than inventing a lead score or send.

## Validation and limits

Run the repository sanitizer before publication. Also manually inspect `.mjs`
files, which the repository's default recursive scanner does not include.
Tests verify arithmetic, not evidence quality, live agent performance or revenue.
Installation does not activate monitoring. Logging follows the repository's
consent settings and must exclude relationship data and funnel totals.

<p align="center">
  Built by <a href="https://www.singlegrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Grain</a>. Powered by <a href="https://www.singlebrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Brain</a>.
</p>
