# Relationship data contract

Use the existing authorized private datastore. These are logical fields, not
instructions to overwrite a production schema.

## Entities and coverage

- Person: stable ID, verified identifiers, source aliases, current affiliation
  with validity dates, merge evidence, identity status and manual overrides.
- Company: stable ID, canonical domain, business model, size range, source date
  and whether size is reported or estimated. One company can have many contacts.
- Property: the website/product assessed; relationship to company/person with
  evidence. Auditing a domain does not prove the submitter works there.
- Observation: source ID, source URL, source timestamp, ingestion time and payload
  reference. Keep event time distinct from ingestion time.
- Source coverage: searched account/channel, query scope, inclusive start and
  exclusive end, extraction time, pagination completion, unavailable sections.
  Keep the lead cohort window separate from historical communication coverage.

Do not strip plus-tags, collapse aliases or merge generic mailboxes automatically.
Do not sum CRM rollup counters with underlying email events. When a trusted
canonical event mapping is unavailable, show possible duplicates separately.

## Interaction event

Required helper fields:

```json
{
  "source": "mail-provider",
  "account_id": "synthetic-account-1",
  "event_id": "synthetic-event-1",
  "occurred_at": "2026-01-10T10:00:00Z",
  "person_ids": ["synthetic-person-1"],
  "direction": "outbound",
  "actor": "unknown",
  "actor_evidence": null,
  "delivery_status": "verified"
}
```

Optional `canonical_event_id` joins verified mirrors across sources. Populate it
only from a trusted message ID or reviewed mapping, never fuzzy subject similarity.
The source key is `(source, account_id, event_id)` because provider IDs may be
mailbox-scoped. Use stable private account identifiers, not display names.
`actor` is `owner_personal`, `team`, `automated` or `unknown`.
`actor_evidence` is a private evidence locator proving attribution, not the owner
account address. Unproven attribution must remain unknown. Events with conflicts
are held, not silently chosen. Sent-but-unverified, drafts, bounces and uncertain
attempts are excluded from verified-touch totals and reported separately.

For each person show unique verified outbound events by actor, inbound events,
last outgoing/incoming timestamp and unresolved events. Multi-recipient events
count once globally but once per associated person. Totals across people may
therefore exceed the global event total. Meeting invites, attendance and message
replies are different event types; do not claim an invite proves attendance.

## Fit evaluation, action and suppression

Store independent client, recruiting, partnership, sponsorship and acquisition
objects: tier, criteria version, decisive facts, evidence locators/dates, freshness,
estimates, unknowns, model/provider, evaluation time and human review state.
Record inferred intent separately from the person's stated intent.

Actions include person/lane, angle, expected value hypothesis, owner, next step,
due date, authority status and evidence revision. Suppression includes scope,
reason, source, timestamp, expiry if any and authorized remover. Never erase a
decline simply because a new feed emits the same person. Ownership history and
CRM disqualification should trigger coordination rather than net-new outreach.

Keep permission/consent facts distinct: resource request, newsletter consent,
marketing permission, recruiting interest and introduction permission are not
interchangeable. Do not expose private relationship histories to broader teams
without verifying the sharing scope.
