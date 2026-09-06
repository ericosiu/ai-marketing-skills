---
name: growth-signal-charts
description: "Select and create Growth Signal chart posts for Instagram, X, and LinkedIn from original content, measured post performance, and primary data. Use the approved Desk Edition style with chart-level sources and PNG/PDF exports. Use for this series or an explicit request for its house style."
---

# Growth Signal Charts

Create useful, source-backed AI, business, and marketing posts in the Growth Signal house style. Match the requested stage: candidate research, design exploration, one post, or a carousel. A design revision does not require restarting the research pipeline.

## Repository integration

When running from a full AI Marketing Skills checkout, use its existing `telemetry/version_check.py` for the non-blocking update check when network access is allowed. After a run, use `telemetry/telemetry_log.py` with skill name `growth-signal-charts`, the actual duration, actual success status, and the repository's `VERSION`. Follow the existing explicit telemetry consent; never enable remote reporting on the user's behalf. Do not log post text, analytics, identifiers, paths, sources or credentials. A standalone copy skips unavailable repository helpers without blocking the task.

## Approved direction

The default style is **Field Manual / Desk Edition**. “Engineering edition” refers to this practical technical-manual direction. **Growth Signal** remains the public series name; edition names describe visual treatments for review.

Before designing, read the [Desk Edition style guide](references/desk-edition-style.md). Use the publisher's identity. A user-supplied reference can refine the layout; no private reference image or analytics export is bundled with this public skill.

- White dominates. Use graphite text, a small open-loop mark, a slim orange indexing rail, bold condensed headlines, and quiet technical labels. Source text must stay legible.
- Base palette: white `#FFFFFF`, graphite `#19171B`, orange `#F05B24`; violet `#6336C7` may be a small accent. The publisher may choose palette experiments. Preserve the approved palette as the default until a variation is selected.
- Keep illustrations small and relevant. A report, data connector, or cost ledger explains software work. Decorative bolts and machinery do not explain software by themselves.
- Leave room around the data and copy. Avoid large metadata tables, duplicate stamps, palette swatches inside posts, full-page grids, and multiple competing callouts.
- Anime is outside the default style. Do not add anime characters or manga styling to this series unless requested.
- Preserve approved designs. Label new styles as experiments; do not quietly replace the default because a new image was generated.

A publication-ready implementation needs separate slide files and numerically accurate graphics. The style guide is a layout specification, not evidence for any numerical claim.

## Research and candidate selection

For candidate selection, performance review, or automation design, read [selection and performance](references/selection-and-performance.md). Start with the publisher's original claims, examples, and operating experience. Match published post IDs to measured performance, then use outside data to support or challenge the argument. A related successful topic is a hypothesis for a new chart; it does not establish that the new statistic will perform.

When recent external discovery is needed, use the installed **last30days** skill if available and runnable. Resolve its current location rather than assuming a script path. If the runner is unavailable, use a labeled web-research fallback. Do not claim that the bot ran or let this prevent authorized work from the publisher's own content. A saved skill does not install a runner or create an automation.

Trace chart values to primary publications or documented first-party data. Read [the editorial and evidence guide](references/editorial-and-evidence.md) when checking a claim or drafting copy. Keep source fidelity and reader comprehension as requirements; rank eligible ideas by original insight, measured audience interest, buyer relevance, and freshness. Use the publisher's chosen business or offer when the subject has a natural buyer connection. Keep reach experiments explicit rather than forcing every subject into a product pitch.

Show the ideas with their original sources, measured signals, chart evidence, and reasons to try or hold them before presenting previews. Give each selected idea distinct Instagram, X, and LinkedIn captions when those platforms are in scope. Reject weak candidates even when their design looks polished. A useful batch may contain zero charts.

The approved rules below and in the selection reference are the default. Use **grill-me-overview** when requested and available, or when a material conflict warrants that review; if unavailable, conduct a brief direct review of the unresolved decisions; do not make the user repeat settled choices for every batch. Turn accepted changes into durable rules. A self-assigned design score is not evidence of views or leads.

## Make the story understandable

Default production scope: **focus on slides with charts; everything else is noise.** Every slide in the default delivery must contain a meaningful, sourced numerical chart. Put interpretation in the caption. Omit workflow slides, screenshots, blank worksheets, creator briefs, advice cards, and closing CTA slides unless the user explicitly asks for them in a later request. Do not turn these into decorative charts to get around the rule.

Define the chart's subject and finding before designing. A carousel can connect **finding → related finding**, but each slide must earn its place with data. One strong chart can be a standalone post; do not add slides to reach a preset length. More topics require more useful evidence, not filler.

- Explicitly decide whether the deliverable is a standalone post, one carousel, or alternative concept boards.
- Number carousel pages “Slide 1 of N,” etc. Do not use separate issue numbers for consecutive slides.
- Each slide should identify its subject even when seen alone. A later slide can rely on earlier evidence, but should not require it to understand what the advice concerns.
- Name the tool, task, or workflow. Replace “Build, integrate, maintain, review” with concrete actions such as “Who fixes it when a data connection breaks?”
- Avoid empty slogans such as “Demo is not the cost” or “The work after the wow.” State what the reader should examine or do.
- Label a proposed checklist, hypothetical example, or editorial diagram as such. Do not imply the cited study supplied the advice.

## Choose the visual from the question

| Evidence or purpose | Suitable treatment |
| --- | --- |
| One meaningful percentage | Large statistic callout or exact share plot |
| Magnitude across categories | Bars or dots on a common scale |
| Two time points for comparable groups | Slope chart |
| A measured series over several dates | Line chart |
| Components reconciling to a total | Waterfall, only when the arithmetic supports it |
| Dependencies, steps, or choices | Outside the current chart-only scope; use a diagram only when explicitly requested |

Vary data chart forms across posts. Keep the mark, type hierarchy, restraint, and source position consistent. Let the plot dominate the slide.

Every little data chart owns a citation at its **bottom left**, including multiple charts on one slide. Use publisher, short title, and date on the graphic; preserve the exact URL and methodology in the source ledger/caption. Include units and the population needed to interpret the number. Different studies may need separate citations and qualifications.

## Build and review

For new raster concept art and edits to raster boards, use the available image-generation workflow. Supply exact copy and an inspected user-approved reference when one is available. Keep prompts with the output. For final numerical plots, use a deterministic chart/vector layout; image-generated proportions are not evidence of accuracy. Do not modify a raster illustration through a code-based workaround.

Concept boards can show adjacent slides for review. Final carousels must include **both** one PNG per slide and one ordered PDF per carousel. Use 1080 × 1350 as a working portrait default if no size was specified. Verify that PNGs and PDF pages have the same slide order and appearance. Editable/native chart assets are optional extras; they do not replace the PNG and PDF exports.

Check the reading order, standalone subject, source placement, clipping, and phone-size legibility. Verify actual values, axis ranges, units, geometry, and calculations; do not trust the image generator's bar lengths or cell counts. Check that diagrams do not imply measured causation or fabricated results.

Deliver the requested artifact, source ledger/captions as applicable, and one clear recommendation. Save final project assets in the workspace. This skill prepares local drafts; it does not imply authority to publish, send, schedule, install paid research tools, or spend external research quota.
