---
name: relationship-intelligence
description: Consolidate lead feeds and relationship history into evidence-backed client, recruiting, partnership, sponsorship and acquisition opportunities. Use for cross-source identity reconciliation, prior-touch attribution, independent fit tiers and owner-ready action queues. Not an automatic outreach or hiring decision system.
---

# Relationship Intelligence

## Repository preamble

When available, run the repository's non-blocking `telemetry/version_check.py`.
Respect existing telemetry consent; never enable remote reporting here. If usage
logging is allowed, pass only skill name, elapsed time, success and version to
`telemetry/telemetry_log.py`. Its documented runtime metadata is added by the helper.
Never log contacts, evidence, source names, query text or relationship metrics.
Standalone copies may skip unavailable helpers.

Turn fragmented signals into a short answer: who matters, for which opportunity,
what has already happened, who owns the relationship, and what to do next.
Extend an existing lead router rather than create a competing source of truth.
This package provides a workflow and offline checks. It does not connect accounts,
deploy a service, prove source coverage or start alerts by being installed.

## Steps

1. **Freeze the scope.** Record sources, accounts, time boundaries, timezone,
   goals, approved audience and permitted actions. Read the existing router and
   field ownership before proposing changes. Inventory missing integrations.
   Keep source coverage alongside every result; no match is not no prior contact.
2. **Normalize without collapsing identities.** Follow
   [the data contract](references/data-contract.md). Keep people, companies,
   assessed properties, evidence and interaction events separate. Verified IDs or
   corroborated exact addresses can link a person; a shared domain, name or
   employer cannot by itself. Hold conflicting companies, generic addresses and
   stale affiliations. Preserve originals and reversible merge provenance.
3. **Reconcile prior touches.** Deduplicate stable source events and mirror IDs
   before counting. Show verified owner-personal, verified team/assistant,
   automated, inbound and unknown-author outbound separately. Account ownership,
   writing style and an email signature do not prove personal authorship.
   Show last verified touch, last reply, pending commitment and coverage dates.
4. **Research and classify five lanes independently.** Use approved professional
   sources and Jev or another authorized provider. Reuse dated evidence where
   still valid. Read [the evaluation and rollout guide](references/evaluation.md).
   Retain cited facts separately from estimates and model hypotheses. A download,
   audit request or newsletter signup is not commercial intent. Never propagate
   one lane's score to another. Unknown is not D or zero.
5. **Propose a useful next action.** For each credible opportunity state why this
   person, why now, one specific angle, evidence, gaps, existing owner, proposed
   next action and due date. Separate urgency from fit. Existing active deals,
   promised introductions and replies outrank generic cold outreach suggestions.
   Keep prior disqualification, opt-outs and owner holds visible and controlling.
6. **Validate and release narrowly.** Run offline checks plus representative
   human review before live routing. The included helper checks event counting;
   it does not verify evidence or grade the whole system. Preserve calculated
   CRM fields. Version new advisory fields and record migration/rollback plans.
   CRM writes, shared dashboards and alerts need the user's specific authorized
   scope and audience. Research alone grants none of these permissions.
7. **Close the loop.** Only approved S-tier alerts go to the approved destination,
   with evidence, angle, owner and a private record link. Deduplicate alerts by
   person, lane and material evidence revision. Store attempted/verified/uncertain
   send states and reconcile uncertainty before retrying. Internal alerts never
   authorize outreach. Measure reviewed fit, accepted actions, qualified meetings
   and outcomes, not just enriched rows or messages sent.

## Team review view

Provide filters for lane/tier, owner, source, date, evidence freshness, prior
touches, reply state, hold reason and next action. Use one row per person with
expandable company/property and event evidence, not one row per ingestion event.
Show account-level history separately from verified owner-personal history.
Display unavailable sources prominently, with direct source links appropriate to
the audience. Do not expose private communications or contact data in public
exports, alerts or this repository.

## Operating boundaries

- Use only authorized data and enrichment destinations. Minimize private payloads;
  do not send private messages or sensitive data to a provider without approval.
- Recruiting tiers are advisory, based on job-related professional evidence.
  Exclude protected traits and appearance. Humans make hiring decisions.
- An acquisition fit is not willingness to sell. Sponsorship fit is not budget.
- Stop on source denials and reconcile access gaps; do not bypass restrictions.
- Report measured tests and remaining gaps. A requested “95+” is a quality target,
  not a score to invent or proof of revenue impact.

## Offline helper

`scripts/touch_summary.py` accepts normalized JSON and summarizes deduplicated,
verified interaction evidence. It performs no network calls or writes to a CRM.
Run synthetic tests with:

```bash
python3 -m unittest discover -s relationship-intelligence/tests
```
