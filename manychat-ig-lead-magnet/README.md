# ManyChat Instagram lead magnets

A reviewable procedure for post-comment and Story-reply resource delivery, explicit required
newsletter consent, Beehiiv/CRM attribution, and evidence-backed lead triage.

## Quick start

1. Read [SKILL.md](SKILL.md), identify the exact account/post and approved resource.
2. Fill out the [launch packet](references/launch-packet-template.md).
3. Inspect your existing ManyChat, Beehiiv and CRM integrations before adding any.
4. Follow the [email and Story checklist](references/email-and-story-checklist.md).
5. Use [lead-fit routing](references/lead-fit-and-routing.md) for five independent
   advisory tiers; approve the private Slack destination before alerts.

Verified newsletter signup unlocks the resource. Consent is explicit and required;
declining, pending confirmation or failed signup does not deliver the resource. Unknown
fit is not D. Recruiting assessments use job-relevant evidence only; they do not
make hiring decisions. Story direct replies require a separate trigger; public
Story comments and likes do not substitute for it.

## Architecture and dependencies

Instagram → ManyChat → explicit consent + validated email → verified newsletter
signup → resource delivery and existing newsletter CRM intake when configured. Separately authorized
resource-lead CRM attribution can occur without newsletter signup; it never grants
newsletter consent. Reconcile both entry paths to avoid duplicates. Authorized Jev enrichment can produce advisory
client, partnership, sponsorship, M&A and recruiting tiers, then an evidence-backed
S-tier alert to an approved Slack destination.

This is a **procedure-only skill**, not a deployed service or an API client. It has
no Python runtime dependencies, bundled credentials, background worker, account
IDs or live sample contacts. No source code or dependency manifest is required.
Use your existing connectors or authorized browser session. Authentication,
permissions and publication approval remain separate from installing this skill.

## Verification

Run the supplied checklists with authorized test accounts. Configuration inspection
is not an end-to-end test; newsletter API acceptance is not final subscription.
Do not claim live CRM attribution or Slack delivery without readback.

For repository hygiene: `python3 security/sanitizer.py --scan --dir manychat-ig-lead-magnet --recursive`.
For version and optional telemetry guidance, see the skill preamble and repository
`telemetry/README.md`. Never log contacts, private evidence or credentials.

---
Built by [Single Grain](https://www.singlegrain.com/). Powered by [Single Brain](https://www.singlebrain.com/).
