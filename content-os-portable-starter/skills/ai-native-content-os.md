# AI-Native Content OS — Portable Mirror

## Purpose
Operate content as an evidence-backed system, not a text generator.

## Flow
1. Load approved product, audience, voice, strategy, evidence, and competitor context.
2. Discover authorized inputs and record connector scope, freshness, and health.
3. Inventory existing content and canonical ownership.
4. Classify each opportunity: refresh, consolidate, create, internal-link, distribute, or reject.
5. Require information gain and claim support before drafting.
6. Produce a draft and evidence log; stop at review by default.
7. **Run Hailey's Bar quality gate**: Evaluate draft against Layer 1 (programmatic checks), Layer 1B (batch diversity), and Layer 2 (LLM judge rubric). Only drafts that clear all gates proceed to scale.
8. Route external writes through explicit capability approvals.
9. Read back mature outcomes at defined intervals and update learning only from attributable evidence.

## Gates
Public inventory does not prove performance. Connector availability does not grant access. CMS draft permission does not grant publish permission. Missing evidence or ownership blocks execution.

**Draft quality gate (Hailey's Bar)**: Drafts must pass programmatic checks (internal/external links, SEO-proof intro, definitional H2, readability), batch diversity analysis (when in batch), and LLM judge rubric (8+ score) before proceeding to scale. Implementation: `haileys-bar/`.
