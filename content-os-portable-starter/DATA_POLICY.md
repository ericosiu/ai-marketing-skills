# Public-Safe Data Policy

## Allowed
Public web pages, public sitemaps, licensed datasets, approved anonymized aggregates, synthetic examples, and operator-authored source-of-truth facts approved for the working context.

## Prohibited from this public package
Credentials or secret values; personal data; private transcripts or messages; customer identities; unpublished performance figures; session links; machine-specific paths; raw connector payloads; run artifacts; and client-specific claims.

## Handling rules
- Minimize before storage and preserve source/date/permission metadata.
- Keep raw private inputs outside public repositories and generated packages.
- Use stable anonymous IDs when identity is unnecessary.
- Record freshness and scope independently from connector health.
- Re-scan final bytes after every modification and before distribution.
