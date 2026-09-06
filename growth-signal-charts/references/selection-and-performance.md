# Selection and performance

Use when selecting ideas, reviewing results, or designing recurring production. A simple layout revision does not need a new analytics pull. These rules implement the editorial principles: original insight, fair comparisons, a clear buyer problem, rejection of weak charts, and learning from actual results.

## Start with the original

For each candidate, preserve the exact published post URL/ID and text, or recording ID, timecode, and quote. State what was actually read: a full transcript, a curated moment slate, or only a published caption. Do not imply a full archive was searched from a small sample.

Record two separate relationships:

- **Original to published post:** `verified` for the post itself or documented clip lineage; `thematic` for a related discussion; `unmatched` when no published counterpart is known. A later recording cannot be the source of an earlier clip.
- **Original to chart evidence:** the same measured claim, new supporting context, conflicting evidence, or unverified. A viral post about hiring does not validate a different hiring statistic. Keep the publisher's interpretation separate from the study's finding.

An unpublished original or a lower-performing topic may still merit an exploratory test. Label the missing performance evidence instead of inventing a spike. External discovery can surface another useful candidate, but preserve why it belongs in the publisher's series. Do not bolt a generic statistic onto a popular topic merely to fill the queue.

## Read measured results through the configured route

Use the publisher's configured analytics connector, documented direct API client, or authorized export. Verify the intended account and returned fields. If one connector fails, inspect an already-configured alternative within the same authorized account before declaring the service unavailable. Do not search for credentials, borrow another account, or execute a publishing client entrypoint to obtain analytics.

Keep a timestamped receipt with account identity, route, publication window, timezone, filters, row counts, pagination/completeness status, and returned metric fields. Preserve raw responses locally under the applicable data policy; do not put tokens or private provider exports into skill files, commits, or posting bundles. Retain missing values as missing. State when API-returned history may be incomplete.

Keep these measures separate:

| Layer | Useful measures | Interpretation |
| --- | --- | --- |
| Distribution | Views or impressions; reach where available | Exposure, with the platform's definition |
| Interest | Saves/bookmarks, shares, substantive replies | Interest in the material; inspect giveaway/keyword effects |
| Action | Profile clicks, link clicks, follows where returned | An action, without assuming qualification |
| Qualified demand | Qualified form submissions, meetings, pipeline | Requires a verified analytics/CRM join and established qualification criteria |

Do not add platform views as unique people, fill an unavailable field with zero, or call keyword comments leads. Keep available paid and organic measures separate; disclose when the breakdown is absent. Do not invent per-slide completion data.

## Compare fairly

- Compare within platform, format, and matched post age. Separate replies, link-only posts, videos, images, carousels, and promoted posts when identifiable. Keep unresolved formats out of claims requiring format matching.
- Use a recent median of comparable posts. Show the peer count, date range, exposure definition, and observation age. Aim for at least 10 peers; with fewer, report raw results and low baseline confidence rather than a confident spike multiple. Ten is a working minimum, not statistical proof.
- Define relative exposure as the post's exposure divided by its comparable median; do not calculate the ratio when the denominator is zero or unavailable. Keep interest rates separate: state the denominator, such as saves per 1,000 reach or bookmarks per 1,000 impressions. Do not compare unlike rates as equivalent.
- A single cumulative snapshot identifies relative outperformance, not acceleration. Metrics for posts published in a 30-day window are not necessarily engagement that occurred during those 30 days. A 72-hour eligibility floor alone does not make different-aged posts comparable.
- Distinguish post performance from topic performance. Several related posts strengthen a topic hypothesis, but cross-posts and copied claims are not independent tests. Never claim the format or design caused the result from observational counts alone.

When matched-age snapshots are unavailable, label raw ranks or medians descriptive. Do not exclude a new post as a failure before its observation window closes. Deduplicate stable post IDs and preserve prior snapshots; repeated pulls of one post are not additional posts.

## Decide before rendering

Each candidate needs one audience, one finding, and either one concrete buyer problem or a stated reach/learning purpose. Use the publisher's chosen business or offer for subjects with a natural buyer connection. Other business destinations need an equally clear connection; omit a forced product CTA. A study about the problem is not evidence that the chosen product solves it.

Apply these requirements before any score:

1. **Evidence:** exact values, units, population, dates, source and calculations are supported. Preserve material limitations. Do not turn estimates into observations or associations into causal claims.
2. **Faithfulness:** the headline and chart say what the evidence supports; the publisher's source relationship is explicit. Older data remains dated, even if a recent post shares it.
3. **Comprehension:** the chart makes one useful finding understandable on its own at phone size. Reject findings that need a long caveat to undo a misleading headline.
4. **Purpose:** the insight matters to the intended reader. A lead candidate has a plausible buyer problem; a reach experiment has a stated learning purpose. Neither requires an invented offer or promised result.

Use `ready`, `revise`, or `hold` with a specific reason. Hold missing evidence; revise a fixable headline or layout. A high design score cannot compensate for a failed requirement. If the user asks for a 90+ review, show the defects resolved and label the score as reviewer judgment, not measured performance. Do not keep raising scores to make a candidate pass.

Among eligible candidates, compare original insight, measured audience interest, buyer relevance, and freshness. Use high/medium/low judgments with evidence and confidence, not an invented probability of virality. Keep reach and lead potential visible separately rather than hiding a tradeoff in one total. Give the recommendation and its strongest counterargument. Source novelty and topic popularity do not replace usefulness.

Select only as many charts as the evidence earns. Allow zero. After two focused design-fix passes, hold an unresolved candidate and move on. Do not manufacture a numerical chart from a workflow to satisfy the chart-only requirement.

## Close the learning loop

For an authorized recurring run, keep a record connecting candidate ID, original source, match status, evidence, intended audience, buyer problem or reach purpose, format, hook, chart version, caption version, and eventually the real published post ID. Drafts have no published ID or performance. Record rejections and the publisher's edits as editorial feedback, separate from audience results.

Capture results at consistent ages, such as 24 hours and seven days, plus the actual capture timestamp. Use comparable results to propose the next topic, hook, or chart experiment. Change one principal variable when practical and acknowledge that sequential organic posts are not a controlled A/B test. Keep some explicitly labeled exploration when justified so the queue does not endlessly repeat one historical winner; no fixed optimal content mix is assumed.

For lead claims, join the content/post ID through a tracked destination to form completion and CRM qualification using the configured systems. Use existing qualification rules; if none are defined, leave qualified demand unmeasured and identify that missing decision. Report clicks, qualified leads, meetings, and pipeline separately, with attribution window and uncertainty. Do not infer zero leads from a missing join or count the same contact twice across platforms.

Before scaling volume, verify that one published chart can be followed to a real result. If reach is strong but qualified demand is weak, inspect audience, offer, destination and attribution before attributing the problem to design. Small samples warrant more evidence, not a declaration that a design won.

The skill defines this process; it does not activate a scheduler. Carry out the current authorized draft task without adding publishing, CRM writes, tracking changes, paid research or automated DMs. Reuse successful reads and report the bounded failure if access is unavailable. A failed source should not prevent independent, already-supported candidates from being prepared.

## Calibration cases

Use these cases to check decisions when revising the rubric. They are examples, not live performance claims.

| Case | Expected decision |
| --- | --- |
| A polished hiring chart attaches an unrelated survey to a high-view hiring post | Reject the claimed validation; assess the new finding as a separate hypothesis |
| One image beats three peers, but publication ages differ | Report raw results and weak baseline confidence; no confident normalized spike claim |
| A three-hour Reel has fewer views than a seven-day Reel | Wait for a comparable observation age; do not label it a failure |
| A post receives 800 giveaway comments without a CRM join | Count comments as interest; qualified leads remain unmeasured |
| A connector fails but the workspace documents a working direct analytics client | Inspect and use that configured read-only route within scope before claiming Metricool is unavailable |
| An original operating example has credible chart data but no published counterpart | Consider an exploratory draft and label performance unmatched |
| A chart cites an April scan reshared in September | Retain April as the data date; do not describe it as a new September scan |
| Every candidate lacks supported chart values | Deliver a short hold list with reasons; produce no filler charts |
