# Evaluation and rollout

## Five independent lanes

| Lane | Evidence required for a useful recommendation |
| --- | --- |
| Client | Relevant business/problem, buying role, service fit, realistic commercial context |
| Recruiting | Demonstrated role-related work, skills, professional trajectory; interest/availability separate |
| Partnership | Complementary capabilities/distribution, mutual benefit and concrete collaboration angle |
| Sponsorship | Audience/brand fit, relevant campaign need, buying role; budget unverified unless sourced |
| Acquisition | Business model and size consistent with buy box; ownership and transaction interest separately verified |

Freeze decisive criteria and freshness requirements per lane before scoring.
Use S for exceptional current verified fit and actionable angle; A for strong
supported fit; B for plausible fit with optional gaps; C for weak supported fit;
D for supported mismatch; Unknown for missing decisive, stale or conflicting
evidence. Tiers are not calibrated conversion probabilities. Missing decisive
facts block S even when a model reports high confidence.

Do not classify recruiting using age, health, disability, family status, religion,
ethnicity, gender or appearance. Do not infer wealth or purchasing power from
photos. A missing profile means unavailable, not poor performance.

## Evidence-to-action review

For each claimed high-priority recommendation independently verify:
1. Correct person, current company and relevant property.
2. Source actually supports the decisive claim and is within the configured age.
3. Opportunity lane and angle follow from evidence rather than generic enthusiasm.
4. Prior touch coverage, attribution and current reply/meeting status are disclosed.
5. Holds, opt-outs, ownership and proposed action authority are reconciled.

Test cases must include multi-source duplicates, two people at one company,
generic addresses, one person assessing several properties, conflicting employer,
existing opportunity, multi-recipient mail, assistant mail from owner's account,
stale evidence, missing channel, opt-out, uncertain send and missing buyer intent.

## Quality target rather than invented score

Define a held-out human-labeled sample before tuning. Stratify by source and lane,
include all proposed S cases plus sampled lower tiers and Unknowns. Report sample
size, coverage and uncertainty; synthetic tests alone do not establish field quality.

Suggested release gate, adjustable by the owner before evaluation:
- Zero known false merges or suppression/privacy violations in the reviewed set.
- Every S recommendation has current decisive evidence and a named next action.
- At least 95% of reviewed top-priority recommendations accepted as correct and
  actionable by the responsible operator, with denominator and reviewer disclosed.
- Attribution and source gaps explicitly marked on every affected record.
- Duplicate replay creates no new action/alert; failed or uncertain sends recover
  without duplicate outreach. Verify destination readback, not just HTTP success.

This is an acceptance criterion, not a claim that the shipped skill scores 95.
A small sample passing does not establish a 95% population success rate. Keep
high-risk gates separate from any weighted average so quality cannot hide harm.

## Staged release and learning

Start read-only, then shadow routing, then an explicitly approved small live
batch. Keep the old router available for rollback. Activate schedules/alerts only
when authorized and supported; record a tested health signal and last-success
time. Do not label a disconnected or failed source green.

Record outcomes: review accepted/rejected with reason, next action completed,
reply, qualified meeting booked/held, opportunity, hire/partner/sponsor outcome.
Use matched cohorts and time windows. An observed outcome after an alert is not
proof the alert caused it. Tune against false-positive reasons and review burden,
not to manufacture more S-tier contacts. Propose changes to criteria; do not
silently change the rubric or expand outreach authority.
