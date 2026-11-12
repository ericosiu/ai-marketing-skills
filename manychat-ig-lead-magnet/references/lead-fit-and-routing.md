# Evidence-backed lead fit and S-tier routing

This procedure specifies an authorized workflow. It does not install a Jev job,
CRM automation or Slack alert. Verify each deployed integration separately.

## Five independent lanes

Use Jev, when authorized and available, to assess each lead independently for:

| Lane | Relevant evidence and useful angle |
| --- | --- |
| Client ICP | Verified business, size, services need, relevant problem and commercial context; propose a specific consultation angle |
| Partnership | Complementary capabilities, distribution, client overlap and operational fit; propose a concrete mutual-value introduction |
| Sponsorship | Brand/audience fit, credible budget or buying signal, decision role and campaign needs; propose a relevant paid offer, not a price commitment |
| M&A | Business model, ownership, size, strategic fit and verified transaction interest if any; propose research or a permission-based discussion, never infer willingness to sell |
| Recruiting | Demonstrated job-relevant work, skills, role fit and stated interest/availability if known; propose human review, not a hiring/rejection decision |

A lead can be strong in one lane and unknown in another. Never copy an overall
score across all lanes. A lead-magnet request alone establishes none of these
commercial intents. Do not use age, protected characteristics, health, religion,
family status, profile appearance or inferred sensitive traits in employment fit.
Do not infer personal wealth or an acquisition budget from a profile image.

## Rubric and evidence

Before scoring, freeze each lane's approved criteria and source-date requirements.
Name decisive versus optional fields: missing decisive evidence means Unknown,
while a supported plausible fit with optional gaps may be B.
Do not invent employee counts, budgets, intent or roles. Label estimates explicitly.

- **S:** exceptional supported fit and a specific actionable angle; identity and
  decisive criteria verified with current evidence. Missing decisive evidence
  prevents S, even when a model gives high confidence.
- **A:** strong supported fit; normal human qualification still needed.
- **B:** plausible fit with material gaps or weaker alignment.
- **C:** weak supported fit or low-priority alignment.
- **D:** evidence-supported mismatch to the lane's criteria, not missing data.
- **Unknown:** insufficient, stale, conflicting or unavailable evidence. This is
  not D, zero, or a rejection.

These are advisory tiers, not calibrated conversion probabilities. Separate the
model's confidence from evidence strength. Validate representative labeled cases
with a human before auto-routing; disagreements and missing evidence stay held.
Use only authorized professional sources and enrichment destinations. Do not send
private email/DM content, sensitive data or bulk contact records to Jev unless
that specific scope is approved. Missing Jev access means unavailable, not a
fabricated Jev assessment or permission to bypass network/security restrictions.

For every lane record: tier, criteria version, short rationale, source URLs,
source dates, observed facts versus estimates, unknowns, proposed angle, next
human action, model/provider and evaluation time. Keep contact records and raw
provider responses in authorized private storage, never the skill repository.
Preserve existing calculated CRM scores and original-source history. Use separate
provisional status/evidence properties only after schema and downstream impact
are verified; do not overwrite production scoring fields.

## Immediate S-tier review alerts

Once an S-tier result passes evidence and identity checks, surface it promptly to
the owner's approved Slack destination. If that destination or audience is not
specified, prepare the alert and ask once; do not guess a channel or send live.
Approval for an internal alert does not authorize outreach to the lead.

Alert format:
- Lead and company, using only information appropriate for that channel.
- S-tier lane(s), with evidence links/date and two-sentence rationale.
- One or two specific angles, why now, and any uncertainty.
- Suggested next action and human owner; link to the private CRM record if the
  audience has access. Do not paste email addresses, phone numbers or private DM
  contents unless needed and authorized for that audience.

Deduplicate by lead identity, lane, evidence revision and campaign. Cross-entry
post/Story activity must not create repeat alerts. Alert again only for material
new evidence or an expressly requested reminder. Record sent/readback state;
never retry an uncertain send without reconciliation. No Slack connection means
held alert, not delivered. No service or daemon is created by this document.

## Acceptance cases

- Fictional lead has strong client evidence but no hiring/transaction interest:
  client lane may score high; recruiting/M&A intent remains unknown.
- Missing business size: unknown fact, not an invented size or automatic D.
- Profile photo or sensitive trait: excluded from recruiting assessment.
- Model says S without decisive dated evidence: hold, not an alert.
- Same lead enters via two channels: one intended alert per material evaluation.
- S-tier with unspecified Slack destination: draft held, no live send.
- Existing CRM score: unchanged; advisory result stored separately if authorized.
- Good evidence in one lane: no automatic score propagation or outreach in others.
