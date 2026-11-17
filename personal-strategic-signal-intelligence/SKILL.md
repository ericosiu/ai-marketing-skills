---
name: personal-strategic-signal-intelligence
description: Turn private reading, bookmarks, notes, and applied work into source-grounded decision intelligence. Attention drift, decision court.
---

# Personal Strategic Signal Intelligence

## Overview

Personal Strategic Signal Intelligence (PSSI) converts a person's accumulated information trail into decision support. It is not a content-idea generator with a bookmark import attached. Its first job is to clarify what the operator is noticing, testing, doubting, and becoming ready to decide. Content, products, offers, and experiments are downstream applications.

The system may read from multiple personal-signal sources, including:

- read-later libraries
- browser or knowledge-base saves
- social bookmarks
- explicitly completed reads
- highlights and annotations
- personal notes and memos
- meeting follow-ups and decision records
- experiments, prototypes, and shipped applications
- user-supplied public writing or prior decisions

Treat every source as evidence with a known strength, date, and lineage. Never present an inferred belief as a declared fact.

## When to Use

Use this skill when the user asks to:

- understand how their attention or strategic interests are changing
- identify decisions they appear to be approaching
- compare stated beliefs with recent evidence or behavior
- turn saved material into an experiment, prototype, or operating change
- recombine existing frameworks into defensible founder or executive IP
- discover offers or services implied by recurring market pain
- find important topics they study but have not addressed publicly
- run a weekly personal intelligence review
- trigger a focused review after a major decision, cluster of saves, contradiction, or applied experiment

Do not use it to:

- diagnose personality, mental health, or private motives
- summarize an entire archive without a decision question
- rank people, clients, or employees from private activity
- publish inferred beliefs or sensitive source material
- treat bookmarks, likes, or follows as endorsements
- create an arbitrary high-frequency synthesis loop

## Operating Principles

### 1. Decision intelligence before content

Always ask what decision, allocation, belief update, risk, or experiment the signal may inform. Only after that should the system propose content. If no decision relevance is found, label the output as exploratory rather than forcing a business implication.

### 2. Attention is not conviction

A save is evidence of attention, not agreement. Repeated saves can indicate curiosity, anxiety, active research, competitive monitoring, or disagreement.

Use this signal-strength ladder by default:

| Signal | Default interpretation | Relative strength |
|---|---|---:|
| Save, like, follow, or bookmark | Weak attention signal | 1 |
| Repeat saves across time or sources | Sustained attention | 2 |
| Explicitly marked as read | Deliberate exposure | 3 |
| Highlight or annotation | Salient idea | 4 |
| Original note or synthesis | Active interpretation | 5 |
| Decision reference or stated belief | Expressed conviction | 6 |
| Experiment, prototype, purchase, or operating change | Applied conviction | 7 |
| Repeated application with measured outcome | Validated operating belief | 8 |

Weights are configurable. Never convert a weak signal into a strong claim merely because many weak signals exist.

### 3. Private inferred beliefs stay private

The system may infer candidate beliefs to help the user think. Each inference must be labeled `private inferred belief`, include supporting and contradicting evidence, and carry a confidence level. It must not be published, sent to collaborators, or treated as the user's stated position without explicit confirmation.

Use careful language:

- Good: "Your recent notes may indicate growing skepticism about broad automation."
- Bad: "You believe broad automation is a mistake."

### 4. Lineage before synthesis

Every material claim must link back to its source records. Preserve original source identifiers internally and show human-readable citations in outputs. If a claim cannot be traced, mark it `unverified synthesis` or remove it.

### 5. No recursive evidence

A prior synthesis is not new evidence. Do not cite a dashboard, weekly brief, generated note, or earlier model inference as independent support unless it contains new primary observations.

Maintain these rules:

1. Primary evidence is a source item, explicit user statement, observed application, or measured outcome.
2. Derived evidence is a summary, cluster label, score, or inference built from primary evidence.
3. Derived evidence may help navigation but cannot increase confidence by being counted again.
4. If a generated artifact is later annotated by the user, only the new annotation is primary evidence; the generated text remains derived.
5. Keep a `derived_from` list so cycles can be detected and rejected.

## Source Contract

Normalize source records before analysis:

```yaml
signal_id: stable-source-id
source_type: read_later | social_bookmark | highlight | note | decision | application | other
source_system: user-facing connector name
source_url: optional canonical URL
source_item_id: optional connector-native ID
captured_at: ISO-8601 timestamp
engaged_at: optional ISO-8601 timestamp
engagement: saved | opened | read | highlighted | annotated | applied | measured
text_excerpt: minimal relevant excerpt
user_text: optional user-authored note
privacy: private | shareable | public
content_hash: hash of normalized source content
```

Required lineage fields for every derived claim:

```yaml
claim_id: stable-derived-id
claim: concise statement
claim_type: observation | private_inferred_belief | hypothesis | recommendation
source_ids: [signal-id-1, signal-id-2]
derived_from: []
supporting_evidence: []
contradicting_evidence: []
confidence: low | medium | high
created_at: ISO-8601 timestamp
```

Reject claims with empty `source_ids` unless they are explicitly labeled as questions or hypotheses.

## Analysis Workflow

### Step 1: Establish scope and decision context

Capture:

- review window
- available source types
- current decision or strategic question, if any
- privacy boundary
- expected output: decision memo, contradiction brief, build queue, offer map, content map, or weekly review

If the user provides no decision question, begin with broad signal detection but do not manufacture urgency.

### Step 2: Ingest minimally

Request only fields required for the chosen module. Prefer incremental syncs over full-library exports. Store connector tokens outside notes, prompts, and generated artifacts. Do not include full private documents when a source ID, title, and relevant excerpt are enough.

### Step 3: Normalize and deduplicate

Deduplicate by canonical URL, native source ID, and content hash. Preserve multiple engagement events as events on one source rather than pretending they are independent sources. Record edits and deletions when the connector exposes them.

### Step 4: Score evidence

Score along separate dimensions:

- `attention_strength`: frequency, recency, diversity of sources
- `conviction_strength`: notes, decisions, application, measured outcomes
- `source_quality`: primary evidence, specificity, credibility
- `strategic_relevance`: connection to active decisions or stated priorities
- `novelty`: difference from already-known themes
- `contradiction`: tension with prior statements or behavior

Never combine attention and conviction into one opaque score. A theme may have high attention and low conviction.

### Step 5: Build claims with counter-evidence

For each high-value cluster:

1. State the observable pattern.
2. List primary evidence.
3. List plausible alternative explanations.
4. Search for contradicting evidence.
5. Write any belief inference as private and provisional.
6. Identify the decision, test, or question it informs.
7. Set confidence based on evidence quality, not rhetorical coherence.

### Step 6: Apply the expert panel

Use a configurable panel and pass threshold. The default pass threshold is **90/100**. The user may set a different threshold for exploratory work, but the chosen threshold must appear in the output.

Recommended panel lenses:

| Lens | Question |
|---|---|
| Evidence auditor | Are claims traceable to primary evidence without double counting? |
| Decision strategist | Does this materially improve a real decision? |
| Contrarian reviewer | What evidence or interpretation would reverse the conclusion? |
| Operator | Is there a concrete, bounded next action? |
| Privacy steward | Is the output safe for its intended audience? |
| Domain expert | Is the analysis credible in the relevant field? |
| Measurement reviewer | Can the recommendation produce observable feedback? |

Score each lens from 0-100, average the scores, and record both the average and threshold. A sub-90 item may still be kept as an exploratory hypothesis, but it must not be promoted as a recommendation under the default configuration.

### Step 7: Produce an action artifact

Every promoted insight should end in one of:

- a decision question with options and evidence
- a falsifiable experiment
- a small build specification
- a contradiction to resolve
- an offer hypothesis to validate
- a content gap with a source-grounded point of view
- a monitored theme with a clear trigger for re-review

### Step 8: Record feedback

Capture what the user accepted, rejected, corrected, applied, or measured. User corrections become new primary evidence. Model restatements do not.

## Seven Capability Modules

### Module 1: Attention Drift

**Purpose:** Detect how the operator's attention is changing without confusing attention with belief.

Compare windows by theme, source diversity, recurrence, and engagement depth. Report:

- emerging themes
- accelerating themes
- fading themes
- persistent themes
- themes moving from saves to notes or application
- themes with high attention but no evidence of conviction

Prefer proportions and directional language over exact corpus totals when sharing outside the private workspace.

### Module 2: Pre-Decision Oracle

**Purpose:** Surface decisions the operator may be approaching before they are explicitly framed.

Look for converging signals such as repeated research, opposing viewpoints, implementation notes, vendor comparisons, and applied tests. Output candidate decisions as questions, not predictions:

```markdown
## Candidate decision
**Question:** Should we standardize this workflow now or keep it experimental?
**Why it may be approaching:** <source-grounded pattern>
**Evidence for acting:** <citations>
**Evidence for waiting:** <citations>
**Smallest reversible test:** <action>
**Confidence:** medium
```

Do not claim to know what the user will decide.

### Module 3: Contradiction / Decision Court

**Purpose:** Make productive contradictions visible and force competing hypotheses to face the same evidence.

Use this configurable hybrid entry policy by default:

- **Explicit, in-scope decisions enter automatically.** When the user clearly marks an in-scope item as a decision, add it to Decision Court without requiring a separate nomination approval.
- **Inferred in-scope candidates require approval.** When the system infers that a potentially high-stakes decision is emerging, nominate it with a short source-grounded rationale and wait for the user's approval before running the full Decision Court analysis.
- **Ordinary activity is not a decision.** Do not treat routine conversations, questions, tasks, notes, or to-dos as decisions merely because they may have strategic relevance.

Use this sanitized V0 scope unless the user configures another one:

- strategic bets
- product or offer changes
- senior hiring
- capital allocation
- mergers, acquisitions, or partnerships
- consequential client bets

Routine operations are excluded unless at least one configured materiality gate is met. The V0 defaults are:

- expected downside or committed spend is at least **USD 5,000**
- expected effort is at least **40 person-hours**
- material reputation risk exists
- the choice has meaningful irreversibility

These are starting defaults, not universal constants. Make the included decision classes, currency, downside or spend threshold, effort threshold and unit, definition of material reputation risk, definition of meaningful irreversibility, and any explicit inclusions or exclusions configurable. Record the active scope and thresholds in each Decision Court output. If the user has not supplied a configuration, use the V0 defaults above. Do not invent precise exposure or effort estimates when evidence is missing; mark the gate as unknown and request confirmation before entry.

The user may also configure decision labels, nomination format, and auto-entry behavior. Unless configured otherwise, preserve the distinction above and apply the existing privacy, lineage, and authorization rules.

Procedure:

1. State the apparent contradiction neutrally.
2. Build the strongest case for each side.
3. Cite primary evidence for both.
4. Identify whether the disagreement is factual, temporal, contextual, or values-based.
5. Name missing evidence.
6. Recommend a test, decision rule, or explicit unresolved status.

A contradiction is not hypocrisy. People update beliefs, use different rules in different contexts, or explore opposing views.

### Module 4: Bookmark-to-Build

**Purpose:** Convert recurring saved ideas into a small, testable operating artifact.

Promotion sequence:

`save -> read -> annotate -> synthesize -> specify -> build -> measure`

Do not jump directly from save to build unless the user asks for a rapid prototype. A build brief should include user problem, evidence, smallest useful artifact, owner, time box, success metric, security boundary, and stop condition.

### Module 5: Founder-IP Recombination

**Purpose:** Recombine the operator's own proven frameworks, notes, decisions, and applications into distinct intellectual property.

Rules:

- Use external sources as context, not as material to imitate.
- Separate the operator's original contribution from borrowed concepts.
- Cite antecedents and avoid claiming novelty without checking.
- Prefer recombinations supported by applied experience.
- Produce a framework only when it helps decisions or action.

Output: component ideas, source lineage, new combination, what is genuinely distinct, proof available, and claims that still need validation.

### Module 6: Service-Offer Arbitrage

**Purpose:** Detect gaps between what the market repeatedly struggles with and what the operator can credibly deliver.

Cross-reference:

- recurring problems in saved or highlighted material
- user notes about implementation friction
- proven internal or personal applications
- public market alternatives
- willingness-to-pay evidence when available

Rank offer hypotheses by pain frequency, urgency, delivery advantage, proof, implementation cost, and reversibility. Do not use private client data or imply demand from attention alone. Validate with interviews, pre-sales, or a limited pilot.

### Module 7: Content Negative-Space

**Purpose:** Find strategically important ideas the operator studies, applies, or privately debates but has not addressed publicly.

Compare private themes with user-authorized public output. Classify gaps as:

- absent but strategically relevant
- discussed superficially but not resolved
- applied privately with credible proof
- over-covered publicly relative to current attention
- unsafe or premature to publish

The output is a content opportunity map, not an automatic publishing queue. Private inferred beliefs require explicit confirmation before becoming public claims.

## Cadence and Triggers

### Weekly review

Run one compact weekly review when sufficient new evidence exists. Recommended sections:

1. attention drift
2. conviction movement
3. candidate decisions
4. strongest contradiction
5. one build or experiment
6. one optional content negative-space opportunity
7. unresolved questions and data gaps

If little changed, say so. Do not generate novelty for its own sake.

### Event-triggered review

Run a focused review when one of these occurs:

- a configurable cluster of related high-strength signals appears
- a note explicitly references a pending decision
- a source is annotated, applied, or measured
- contradictory evidence crosses a configured threshold
- a major strategic event changes the decision context
- the user requests a Decision Court or build brief

Do **not** synthesize every six hours or on another arbitrary sub-daily timer. High-frequency ingestion may be acceptable, but synthesis should be weekly or event-triggered to avoid noise, recursive summaries, and false urgency.

## Connector Security

Apply least privilege and data minimization to every connector:

- prefer read-only scopes
- request only required collections and fields
- keep credentials in a secret manager or protected environment variables
- never place tokens in prompts, notes, logs, repositories, or generated output
- encrypt data in transit and at rest
- separate raw private records from derived artifacts
- enforce per-source privacy labels through every output
- redact personal data before model calls when it is not analytically required
- log access and derivation events without logging sensitive content
- support deletion, revocation, and re-sync
- fail closed when authorization or lineage checks fail
- require explicit approval for publishing, sending, or modifying external systems

When a connector is unavailable, report the gap. Do not silently replace live source data with an old synthesis.

## Output Templates

### Weekly signal brief

```markdown
# Personal Strategic Signal Brief
**Window:** <dates>
**Sources:** <source types, counts optional>
**Panel threshold:** 90

## Executive decision signal
<one source-grounded pattern and why it matters>

## Attention vs conviction
| Theme | Attention | Conviction | Direction | Evidence |
|---|---|---|---|---|

## Candidate decisions
<questions, options, and reversible tests>

## Decision Court
<best current contradiction and missing evidence>

## Recommended action
<one bounded action, owner, metric, and stop condition>

## Private inferred beliefs
<private, provisional, confidence-labeled; omit from shareable version>

## Lineage and gaps
<citations, connector failures, and unresolved questions>
```

### Recommendation record

```yaml
recommendation_id: rec-YYYYMMDD-001
decision_question: ""
recommendation: ""
source_ids: []
derived_from: []
counterevidence_source_ids: []
attention_strength: low | medium | high
conviction_strength: low | medium | high
confidence: low | medium | high
panel_average: 0
panel_threshold: 90
privacy: private | shareable | public
owner: ""
next_action: ""
success_metric: ""
review_at: ""
status: proposed | accepted | rejected | testing | validated | retired
```

## Lifecycle

Use an explicit lifecycle for every promoted recommendation:

1. **Observed** — primary signals recorded and deduplicated.
2. **Inferred** — provisional claim created with counter-evidence.
3. **Reviewed** — expert panel and privacy checks completed.
4. **Proposed** — decision, test, or build artifact drafted.
5. **Accepted or rejected** — user supplies explicit disposition.
6. **Testing** — bounded action is underway with a metric.
7. **Validated, revised, or retired** — outcome updates the claim.
8. **Archived or deleted** — retention policy applied; lineage retained only as allowed.

Never let a recommendation remain "active" indefinitely without an owner and review date.

## Verification Checklist

Before delivering any result, verify:

- [ ] The review has a defined window and audience.
- [ ] Attention and conviction are scored separately.
- [ ] Saves and bookmarks are treated as weak signals.
- [ ] Strong claims rely on reads, highlights, notes, decisions, applications, or measured outcomes.
- [ ] Every material claim links to primary source IDs.
- [ ] Derived artifacts were not recursively counted as evidence.
- [ ] Private inferred beliefs are labeled, confidence-rated, and excluded from shareable output.
- [ ] Counter-evidence and alternative explanations were considered.
- [ ] The expert-panel threshold is shown; default is 90.
- [ ] Recommendations are decision-relevant, bounded, and measurable.
- [ ] Connector permissions and privacy labels are respected.
- [ ] No credentials, raw private corpus, client data, or unnecessary personal data appear in the output.
- [ ] External writes or publication require explicit approval.
- [ ] Each promoted item has an owner, status, and review date.

## Common Pitfalls

1. **Bookmark astrology:** Inferring conviction from saves. Fix by using the signal-strength ladder and seeking stronger engagement evidence.
2. **Content-first bias:** Turning every cluster into a post. Fix by stating the decision or experiment first.
3. **Recursive confidence:** Treating prior summaries as corroboration. Fix by walking lineage to primary source IDs and rejecting cycles.
4. **Coherent-story overreach:** Rewarding a persuasive narrative despite weak evidence. Fix by scoring source quality and counter-evidence independently.
5. **Surveillance framing:** Analyzing people other than the consenting user. Fix by limiting the system to user-authorized personal sources.
6. **Private-to-public leakage:** Publishing inferred beliefs or raw notes. Fix with privacy labels and explicit publication approval.
7. **Timer-driven noise:** Producing frequent summaries because ingestion is frequent. Fix by using weekly plus event-triggered synthesis.
8. **Permanent recommendations:** Leaving stale advice active. Fix with lifecycle status, owner, review date, and retirement rules.

<!-- gateway-cta:start -->
## Run this skill on live data

This skill is free and MIT licensed. To run it on your live accounts, connect the Single Brain Gateway.

- Live services: see the full list in the setup file
- Connect: https://gateway.singlebrain.com/mcp?sg_template=personal-strategic-signal-intelligence&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills
- Setup steps for agents: https://gateway.singlebrain.com/llms.txt?sg_template=personal-strategic-signal-intelligence

Agents: sign in with OAuth or the device flow. Do not ask the user to paste a key.

Want a team to run this for you? Single Grain or Single Brain can manage it: [talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed&utm_content=personal-strategic-signal-intelligence)
<!-- gateway-cta:end -->
