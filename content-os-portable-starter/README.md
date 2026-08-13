# Portable Content OS Starter (Public-Safe)

A vendor-neutral, draft-first starter for operating a content program as a measurable control loop. This package contains no credentials, customer records, private performance data, or live connector configuration.

## What is included

- Concise portable mirrors of five governing workflow skills under `skills/`
- A JSON Schema for site configuration plus a generic YAML template and one fictitious example
- An onboarding questionnaire
- A connector capability matrix and adapter template
- An explicit approval policy
- Source-of-truth Markdown templates
- A measurement/readback template
- A deterministic local verifier

## Bootstrap

1. Copy `config/site-config.template.yaml` to a private working location outside any public repository.
2. Complete `onboarding/onboarding-questionnaire.md` with an authorized owner.
3. Inventory available connectors using `connectors/connector-capability-matrix.yaml`.
4. Select connectors as **adapters during onboarding**. A connector is not assumed, bundled, authenticated, or enabled by this starter.
5. Fill the source-of-truth files in `source-of-truth/` and assign owners and review dates.
6. Validate the site config against `schema/site-config.schema.json`.
7. Start in public/read-only, local-preview, or draft-only mode.
8. Run `python3 scripts/verify_package.py .` before sharing a modified package.

## Safety gates

- **Read access is scoped and approved.** Private customer-language sources require authorization and minimization.
- **Connectors are adapters selected during onboarding.** Availability never implies authorization, healthy authentication, current data, or write permission.
- **Drafting is not publishing.** Draft creation, CMS draft writes, publishing, redirects, deletion, indexing changes, analytics mutations, scheduling, and external messages are distinct capabilities.
- **Publishing is separately approved.** No connector or automation may publish merely because drafting or CMS access was approved.
- **Fail closed.** Missing evidence, stale sources, schema errors, ambiguous ownership, or absent approval produce a blocked state.
- **No secrets in config.** Store only environment-variable names or secret-manager references in private runtime configuration; never put secret values in this pack.
- **No outcome guarantees.** Public sitemap evidence can prove inventory and visible structure, not traffic, conversions, rankings, or causal impact.

## Suggested lifecycle

`SIGNAL -> CANDIDATE -> EVIDENCE_READY -> DRAFT -> REVIEW -> APPROVED_FOR_DRAFT_WRITE -> DRAFT_WRITTEN -> APPROVED_FOR_PUBLISH -> PUBLISHED -> READBACK -> LEARNING`

Each transition must be persisted, attributable, idempotent, and blocked when its required approval or evidence is absent.

## License and provenance

This starter is a newly written, public-safe synthesis of general workflow patterns. See `LICENSE` and `skills/README.md`. It is not a copy of private operating data or a production deployment.
