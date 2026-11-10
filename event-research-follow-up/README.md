# Event Research and Follow-up

A portable, evidence-first workflow for business-event discovery, photo and roster lead organization, company qualification, and explicitly approved follow-up.

## Quick start

Copy this complete directory into your agent's skill directory. Load `SKILL.md` and supply the event or authorized notes/roster, your offers and target-customer criteria, desired output, and any action limits.

Example request: “Use event-research-follow-up to organize these fictional conference notes, separate warm conversations from roster-only contacts, and draft five useful follow-ups. Do not send anything.”

No API key, proprietary model, private asset or third-party Python dependency is required. Connected accounts, enrichment providers and evaluators are optional and require their own access and task-specific authorization. Installing the instructions does not install connectors or start monitoring.

## Architecture

- `SKILL.md`: scope, source collection, company fit, optional evaluation, approval and lifecycle gates.
- `references/event-leads.md`: capture, identity matching, enrichment and relationship-aware drafts.
- `references/outreach-execution.md`: approved channel actions, time zones and verification.
- `references/event-state.md`: durable private records and resumable passes.
- `references/reply-outcomes.md`: reply triage and commercial evidence.
- `references/host-and-scale.md`: host conversations and conditional expansion.
- `agents/openai.yaml`: optional display metadata.

This is an instruction-only skill, not a sender or scraping program. Use manual review and deterministic rules by default; optional model output remains review-only without independent evaluation.

## Privacy and validation

Keep all operational rosters, photos, contact details, messages, receipts and outcome records in authorized private storage outside this repository. Only sanitized reusable lessons belong in the skill. Never infer permission to send from research or draft approval.

In a full repository checkout, run `python3 security/sanitizer.py --scan --dir event-research-follow-up --recursive` from the repository root before committing. For a standalone copy, inspect every file for real names, contacts, credentials, private links, local paths and event-specific facts; use an available secret/PII scanner as an additional check. Review reference links and approval gates as well: a pattern scan cannot establish factual correctness or live-delivery safety. No live outreach or paid evaluation is needed to validate the package.

<p align="center">
  Built by <a href="https://www.singlegrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Grain</a>. Powered by <a href="https://www.singlebrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Brain</a>.
</p>
