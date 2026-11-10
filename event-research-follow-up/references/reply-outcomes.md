# Reply and outcome feedback

Use this workflow after event research, when choosing a small pilot or reviewing replies. A research list is preparation, not pipeline. Prefer learning from a few relevant conversations to another broad scoring pass unless the user requests more research.

## Choose a bounded pilot

Recommend five distinct company accounts as a starting test, adjusted to the user's scope and delivery capacity. Select from the full authorized master, not only the latest enrichment batch. Rank documented conversation warmth first, then the specific offer fit and a useful next question. Keep hosted-event attendance, one-to-one contact and stated interest separate. Preserve the user's documented event-priority rubric without interpreting it as purchase intent.

Keep contact holds visible in a strategic shortlist, but exclude held records from an action-ready cohort. Resolve identity, former-employer addresses and existing conversations before recommending a next touch. A saved scheduled action requires live reconciliation before reuse; it is not an unsent prospect. Coordinate co-leaders as one account and count their company once in commercial metrics.

Record all four offer routes when both offers are in scope: recruiting customer, marketing customer, recruiting partner and marketing partner. Choose one strongest angle for each draft. A staffing firm may refer marketing clients; an advisory firm may have valuable access despite a small team. Record the evidence for that access and ask about service overlap rather than assuming a channel exists.

Draft one supported personal hook, one concrete use case and one easy question. Use the user's requested voice without repeating a slogan in every message. Do not claim a meeting, interest, channel weakness, available budget or existing demo without evidence. Keep a prepared alternative draft separate from the current thread and any already approved copy.

## Read replies as evidence

On an authorized reply-review request, read the actual message and enough of its thread to identify the offer, promises, prior actions and current response. Use the named account and existing records. If live access is unavailable, label the cached observation and leave delivery/reply status unknown; do not infer silence or permission to resend.

Record the observed reply category separately from an inferred opportunity:

| Observation | Next step to prepare |
|---|---|
| Specific direct need | Ask the missing qualification question; identify the operating business and buyer. |
| Referral or partner offer | Identify the proposed company/person and complementary task; draft a permission-based introduction request. |
| General interest or friendly acknowledgement | Ask one question about a real problem; do not count a qualified opportunity. |
| Request for a resource | Record the exact promise, owner and due date; prepare the resource before a broader pitch. |
| Meeting booked | Record the confirmed meeting and prepare for it; suppress generic follow-ups. |
| Later / out of office | Record the stated timing and propose a later action; no automatic schedule. |
| Decline / opt-out | Mark the local record suppressed; do not prepare another sales touch. External suppression writes require the applicable authorization. |
| Wrong person / ambiguous identity | Hold the contact and resolve the match. |
| No verified reply | Keep pending/unknown; absence of evidence is not rejection or disinterest. |

Drafting, reviewing and logging locally do not authorize sends, calendar changes, CRM updates, enrolment or recurring monitoring. Use the existing outreach execution contract for any explicitly approved action. Never turn an introduction offer into permission to contact the third party.

## Keep an evidence-backed local outcome ledger

Reuse compatible task records; otherwise store `opportunity-outcomes.jsonl` beside the existing private action ledger. Append observations with stable event/person/company IDs, offer/angle version, observation time, source message/thread or receipt pointer, a brief factual summary, reply category, proposed next action and action authority. Retain corrections as superseding observations rather than erasing prior evidence. Keep identity and contact holds intact unless the underlying evidence resolves them.

For each opportunity, record the operating company, direct/partner route, stated problem, buyer/owner, scope, actual budget or Unknown, agreed next step, next-action owner and any promised deadline. Partner records also identify the potential client, relationship, complementary service and introduction permission. An expected introduction, an introduction actually made and a resulting qualified opportunity are three distinct events.

Keep a scoped pilot discussion, proposal, accepted paid pilot, signed work and collected revenue separate. Use message/agreement evidence for commitments and an authorized payment record for collected revenue. A positive reply or estimated contract value is not revenue. Record attribution as direct, partner-sourced or uncertain; do not count the same end customer twice across attendees or events.

## Review results and improve the skill

At an explicit checkpoint, report selected accounts, verified sends, reply coverage, substantive replies, qualified direct opportunities, qualified partner paths, introductions made, pilot discussions, paid pilots and collected revenue. State the observation window and source freshness. Separate held/unsent accounts from the contacted denominator, and pending replies from declines. Report counts such as 2 of 5 with the small-sample limit; no conversion forecast from one cohort.

A qualified direct opportunity needs a stated problem, identified operating buyer/owner and an agreed next step; budget and scope gaps remain explicit. A preliminary partner path needs a specific complementary task, relevant client access and an agreed next step. Count it as a qualified partner opportunity toward expansion only when a specific client/project, owner and commercial discussion path are also evidenced. An accepted paid pilot needs evidenced scope, payer and commercial terms, not just willingness to talk.

Track the user's time and delivery effort when supplied; leave them Unknown when unmeasured. Compare useful conversations and qualified opportunities per company and, where measured, per owner-hour. The initial learning checkpoint is whether a specific need or introduction advanced to an agreed next step. Expansion uses the commercial gates in [host-and-scale.md](host-and-scale.md), not a tier score or cheap model cost.

Write misses, user corrections, false identities, ineffective hooks, replies and eventual outcomes to the private `learning.jsonl`, linked to the angle version. Change one material variable in the next approved test when feasible. Record alternative explanations; a reply does not prove the wording caused it. Promote only sanitized repeatable lessons to the skill. Keep customer data, messages and receipts out of Git.

The workflow remains incubating until a real bounded pass has source/readback proof. Model evaluation and commercial validation are separate: a working ledger does not validate the optional evaluator's accuracy, and a passed model eval does not validate the offer. Repeat only on request or within a current bounded approval; no cron or autonomous follow-up. Stop expansion on unresolved identity errors, repeated weak-fit outcomes or delivery-capacity limits; archive a retired angle with its evidence rather than deleting its history.
