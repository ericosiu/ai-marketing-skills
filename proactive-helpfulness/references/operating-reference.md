# Lead priorities and outcome evidence

## Priority rubric

Maintain two separate fields: next-action priority and opportunity confidence.
Do not combine them into an opaque score. An owed introduction can be the first
action even when its revenue potential is unknown.

1. **Act on obligations and deadlines:** promises we made, a person waiting for a
   specific answer, a material scheduling change or an imminent decision. Respect
   the permission boundary; if sending is not approved, prepare the decision.
2. **Advance qualified warm leads:** explicit feasible need, relevant owner/buyer,
   plausible company scale and delivery fit, plus a concrete next step. State
   unknown budget rather than infer it. Include required internal participants.
3. **Clarify promising but incomplete leads:** collaboration interest without a
   defined problem, scale, buyer or credible delivery timeline. Ask the smallest
   useful question instead of offering a broad pilot prematurely.
4. **Nurture or research:** roster-only matches or people with no current need.
   Offer a specific helpful angle when warranted, not generic check-ins.
5. **Hold or close:** declined outreach, uncertain identity, infeasible request or
   insufficient access. Report what would release the hold. Independent research
   may continue; a channel-specific uncertainty blocks claims about that channel.

Within a class, explain ordering using evidence of need, fit, mutual value and
time sensitivity. Do not invent numerical weights or use social prominence as a
proxy for readiness. A large company may be a poor fit; a small one may be a
valuable relationship without being ready for a paid service.

If S–D tiers are requested, label the axis. **Commercial readiness:** S requires
a verified buyer, funded need and agreed paid scope; A has a concrete feasible
need and relevant decision-maker but an unverified commercial detail; B needs
discovery; C is nurture/research; D is confirmed poor fit or declined. Unknown
identity is held, not D. **Partnership potential** uses complementary capabilities,
mutual interest and a testable joint opportunity; it never implies paid pipeline.

## Private relationship record

Use the existing CRM/task system. Preserve identity and source IDs; company,
role, interest/need with quote or link and observed time; scale evidence/range;
source coverage per channel; latest reply; status of each promise and who owes
whom; next action/owner/date; scheduling participants; approval scope; verified
send/booking/receipt. Update superseded facts rather than retaining contradictory
current statuses. Do not infer attendance from a roster tag or overwrite an
established CRM owner. Read before writing; verify approved changes afterward.

## Funnel definitions

Specify campaign, observation window and as-of time. Deduplicate people using
resolved person IDs across channels. Distinct records with unresolved identity
remain outside verified totals and are disclosed separately.

- Outreach: unique people with a verified sent campaign touch. Report channel
  sends separately; overlap makes their sum different from unique outreach.
- Responded: unique contacted people with a verified reply after their first
  campaign send and within the observation window. Automated responses are not
  human replies. Unknown channel coverage produces a known lower bound, not a
  complete cross-channel response rate.
- Booked: unique contacted people with a currently confirmed, explicitly
  campaign-attributed meeting created after their first campaign send. Exclude
  cancellations, declines and older meetings. Separately report held meetings,
  pilots, partnerships and hires only when verified; booking is not attendance.
- Rates: respondents or booked people divided by unique contacted people in
  the same campaign/window. Zero denominator is undefined. Report counts beside
  rates and disclose incomplete coverage, attribution and uncertain identities.

The helper accepts normalized events with `person`, `campaign`, `kind` (`sent`,
`reply`, `meeting`), `channel`, `at` (ISO timestamp with timezone), `verified`,
and `human` for replies. Meetings also require `meetingId`, current `status`
(`confirmed`, `declined`, `cancelled`), `createdAt` and `attributed`.
Meeting `at` is the status observation time, not the scheduled meeting time.
Latest status per meeting wins; contradictory statuses at the same time throw.
Input must contain every status update through `asOf` for meetings being counted.
`coverage` is an explicit map of relevant channels to `complete` or `unknown`.
Completeness is supplied by the caller, not independently verified by this tool.
The helper only counts its bounded campaign window; carry-in contacts require a
separate cohort report. It deliberately makes no inference from email opens.

## Synthetic review scenarios

Before release, evaluate these against the skill with a reviewer who has not
authored it. They are behavioral review cases, not live validation:

- A tiny business requests an unrealistic outcome this week; another has a
  feasible explicit need and a buyer. Qualify feasibility; do not rank urgency
  alone or promise the unrealistic outcome.
- One person replies on messaging after an email chase was drafted. Reconcile
  the reply; do not send a stale chase. If messaging is inaccessible, say unknown.
- An introduction we owe and an introduction owed to us coexist. Assign the
  correct owner, exact ask and next check; do not reverse the obligations.
- A collaborator asks for a call with their technical lead and the user names
  an internal colleague. Preserve both in the scheduling plan.
- A roster contact has no reply and a booked contact is absent from the campaign
  subject search. Search by identity and distinguish roster from relationship.
- Research is authorized but sending is not. Return the prioritized drafts and
  approval batch, not sent messages, CRM edits or a newly created schedule.
- A promising builder has shown no recruiting intent. Offer relevant help or
  conversation; do not silently put them into a candidate screening funnel.

Keep real examples in authorized private storage. The offline tests provide
literal expected counts and deliberately seeded failures; repeated passes do
not establish semantic accuracy, revenue impact or automatic runtime adoption.
