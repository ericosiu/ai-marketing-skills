---
name: commenter-talent-scan
description: Turn the commenters on a public social media hiring post into a ranked, outreach-ready talent list. Pulls every comment, resolves and enriches each commenter's profile, downloads their profile image, and scores every person with an eval-gated Jev text+images sieve (role depth, hire target vs peer vs brand, role level, primary specialty). Use when asked to: "scan the commenters", "find hires in the comments", "who in these comments is worth hiring", "talent scan this post", "rank the applicants in the comments".
---

# Commenter Talent Scan

A hiring post's comments are a pre-filtered applicant pool: every commenter raised a hand. This skill reads the whole pool, enriches every person, and scores them with a cheap typed classifier (Jev) instead of an LLM pass per profile, so a few hundred people can be ranked in minutes for cents.

## Principle

- Cheap classification first. Jev (text + profile image) scores everyone. Human or LLM time goes only to the people who pass.
- The sieve never runs ungated. Every deployment ships with a calibration eval on builder-produced gold cases, and scoring refuses to run until the eval passes.
- Bios are claims, not facts. A bio can show depth, level, and specialty. It cannot show work history, promotions, or tenure. The output labels proof as bio claims and never upgrades them to verified.
- Unknown stays unknown. If a bio does not state a specialty, the output says "not stated in bio". Never guess a specialty, a link, or a number.

## When to use

- A public hiring post (yours, a peer's, or a well-known operator's) collects "apply" comments, and you want the ranked list of who is actually worth outreach.
- Any role: content, marketing, sales, engineering, design, ops. The question set is a template; swap the depth criteria and specialty buckets per role.
- The same pattern also works for adjacent pools with small edits: podcast guest prospects, partnership leads, or community members worth elevating. Swap the routing labels, keep the pipeline.

## Inputs you need

1. The post URL and its media ID (your Instagram CLI's `post` lookup returns it).
2. A target role definition in one paragraph: title, level, what proof looks like in a bio, and the 3-6 specialty buckets you want named per person.
3. Tool access:
   - An Instagram CLI connected to your own account, with `fetch-post-comments` and `user-profile`.
   - An Apify account (the `apify/instagram-scraper` actor) for bulk comment and profile enrichment. This runs on the provider's infrastructure, which keeps bulk reads off your own account.
   - A Jev API key (TypeSafe) and a sieve runner that supports eval gates and `jevimg://` image state fields. A minimal domain template ships in `references/sieve-domain-template/`.

## Workflow

### Step 1: Pull every comment

- Fetch comments page by page with `fetch-post-comments --post-ids <media_id> --limit 100`, following each page's end cursor.
- Dedupe by `comment_id` as you go.
- Stop conditions, both mandatory: stop before reusing a cursor you already used, and stop when a page claims more results but adds zero new comments. Pagination on this API can loop on a stale cursor and report progress forever.
- The post's reported comment total can drift by a few while you pull (new comments, deletions). Report the count you actually captured against the count the post displayed.
- On a 429, stop every Instagram CLI call for the task, including inside scripts. Switch to the independent enrichment path (Step 2) for the remainder, and report partial coverage honestly.
- Rate-limit detection rule: parse the response first. A call succeeded if the JSON parses and contains the expected data. Only treat a response as rate-limited when it has no usable data AND an error marker. Never substring-match raw output for a status code: profile IDs and CDN URLs routinely contain digit sequences that look like one, and substring matching will discard good data for hours.

### Step 2: Resolve every commenter to a username

The comments feed gives you an author ID and a display name, not a username. Resolve in two passes:

1. Run the Apify instagram-scraper actor on the post URL with `resultsType: "comments"` and a limit above the comment count. Each item carries `ownerUsername`, the comment text, and a profile picture URL. This resolves the large majority in one batch run.
2. For commenters the batch pull missed, resolve one by one with `user-profile --user-id <author_id>`. Note the platform limit: separate per-account profile calls rate-limit after a few dozen, so cap this pass at the 50 most recent unresolved commenters and report how many remain if you hit the cap.

### Step 3: Enrich profiles in bulk

- Run the same actor with `resultsType: "details"` and one profile URL per username. You get bio, display name, follower count, verified flag, external links, business category, and profile picture URLs (standard and HD).
- Merge with any profiles resolved in Step 2 pass 2 (fields: name, bio, follower_count, is_verified, website, profile_pic_url).
- Dedupe by lowercase username. One person can comment several times and can appear in both sources.
- Keep the comment text per person. It is weak evidence (most comments are one word), but it occasionally carries a title or a tag of the right person.

### Step 4: Build states and profile images

Use `references/sieve-domain-template/build_states.py`:

- One state per person: `username, display_name, bio, follower_count, is_verified, website, comment_text, profile_image`.
- Download each profile picture, convert to JPEG, and upscale so the small dimension is at least 320px. The image API rejects sides below its minimum; upscaling adds no information, it only satisfies the limit.
- The state carries the image as a `jevimg:///abs/path/to/user.jpg` string. The Jev CLI converts it to an image reference and sends it with the request (image mode upgrades the model automatically).
- If an image download fails, ship the state without `profile_image` and count it. Do not substitute another person's image or a placeholder graphic and pretend it is theirs.

### Step 5: Score with an eval-gated Jev sieve

The domain template is in `references/sieve-domain-template/`:

- `config.json` - the locked question set (below).
- `route.py` - maps answers to slots.
- `cases.json` - your calibration gold set. Build it per `CASES_README.md` in the same folder.

Question set:

| Question | Type | Job |
|---|---|---|
| `role_depth` | score 0-4 | How deep and proven is this person's work in the target role, from bio + image evidence |
| `account_kind` | choice | `hire_target` vs `peer_partner` vs `brand_account` |
| `role_level` | choice | Team lead, senior specialist, practitioner, own-brand only, or unclear |
| `primary_specialty` | choice | The one specialty bucket they are strongest in (channels for a content role; swap per role), or unclear |
| `profile_is_logo` | yes/no probability | Image-only. Is the profile image a logo or graphic, not a photo. Rides in meta, never changes the slot |
| `visual_brand_quality` | score 0-4 | Image-only. Production polish of the profile image. Rides in meta, never changes the slot |

Routing:

| Slot | Meaning |
|---|---|
| `OUTREACH_TOP` | Top tier: depth 3-4 at team-lead or senior-specialist level. Outreach first |
| `OUTREACH` | Real hire target at practitioner level, or deep proof at a lower level |
| `RELATIONSHIPS` | Peer or partner material: founders of notable companies, celebrities of the niche. Not a hire |
| `PARK` | Brand account, or depth 0-1. No outreach |

Two routing lessons baked into the template:

- A large audience alone does not make someone a peer. A working operator with a large following is a hire target. A CEO of a notable company is a peer. When genuinely ambiguous, prefer hire target: a conversation resolves it.
- Keep the image-only questions out of the slot logic. They describe presentation, not ability. They are analysis metadata, not gates.

### The eval gate (non-negotiable)

- Before any live scoring, build 12 or more gold cases from states your builder produced from the real pool. Never hand-write gold states: the eval must run against builder output, or it validates a fantasy.
- Label each case by hand from the same bio + image evidence the classifier will see. Spread the set: a few clear top-tier, a few practitioners, a couple of peers, a few brands and non-starters.
- Run the eval. Scoring and batch commands must refuse to run unless a passing eval exists for the current question set, at a pass rate of 80% or better.
- Any change to a question invalidates the eval (hash the questions into the eval record) and closes the gate until you re-run it.
- Borderline misses are data, not embarrassments. Keep the labels you believe, note the misses, and ship at 80%+ rather than relabeling cases to match the classifier. Relabeling to inflate the score destroys the gate's meaning.

### Step 6: Join, rank, output

- Join decisions back to states by username (have `route.py` copy `username` and `display_name` into meta; the decisions log is the durable record, stdout is progress only).
- Output a CSV with one row per person: username, display name, verdict (slot), depth score, role level, specialty, followers, verified, website, profile URL, bio.
- Sort by slot (top tier first), then depth, then followers.
- In the summary, name each recommended person in plain words with the one or two proof points their bio carries, and the specialty. Mark every proof number as a bio claim.

## Cost reporting rule

Every Jev or Jev Images run report carries its cost line:

- Price basis: $0.042 per million input tokens. Output tokens are free.
- Compute cost from the usage object in each API response. If a response carries no usage, report cost as unknown, never as zero and never as an estimate.
- Label it exactly: "Jev cost: $X (Jev API cost only)". It is the classifier cost, not the total cost of the work. Agent time, browser research, and third-party enrichment (for example Apify runs) are separate; if a provider reports no dollar total, say so instead of inventing one.

A full scan of roughly 300 people, eval included, has cost about $0.03 in Jev API usage at this price. The classifier is not the budget line. Enrichment and human review are.

## Honesty rules

- Bio claims are unverified. Views, revenue, team size, client names: report them as "their bio claims", and route real verification (work history, portfolio, references) to a separate stage.
- A bio cannot show promotions, tenure, or employment history. Never let the sieve's output claim them, in either direction. Unknown is not a fail.
- Specialty absent means "not stated in bio" in the output. In practice most bios in an applicant pool do not name a specialty; that gap is a finding about the pool, not a defect to paper over with guesses.
- Never invent a link. If a profile has no external link, say "no portfolio link in bio" and give the profile URL. A missing link is information about how that person sells (often: through DMs and single videos).
- If the post becomes unavailable mid-task (posts get deleted when hiring rounds close), say so plainly, state what you captured before it went down, and treat the captured set as the final pool. Verify removal with a second independent source before claiming it.

## Worked example (anonymized)

A public Head of Content hiring post from a well-known business creator collected apply-comments. The run:

- Pulled ~320 comments, ~300 unique people after dedupe.
- Enriched all ~300 profiles in bulk, plus a small one-by-one pass for the people the batch pull missed.
- Built a fresh sieve domain for the role in about an hour, gold set drawn from the real pool, eval passed above the 80% gate with two noted borderline misses.
- Result: ~50 people passed as hire targets at some level, about 10 of them top tier. The rest split between peers (mostly founders who would never take the job) and parked accounts.
- Findings that shaped outreach: the top tier split sharply between solo operators who plausibly take a full-time role and agency founders who sell services; the report separated "savage, hire them" from "savage, buy from them". Most bios did not name a channel, so channel was reported only where the bio or link stated it.
- Follow-through: outreach drafts were written per person, each using one bio proof claim as the hook, and nothing was sent without the hiring manager's approval of the exact text.

## Variants

- **Different role.** Rewrite the `role_depth` criteria with that role's proof signals, set `role_level` labels to that function's ladder, and replace `primary_specialty` options with that role's specialties. Keep `account_kind`, routing, and the eval gate unchanged.
- **Your own post.** Same pipeline. Your commenters are warmer; the sieve still separates applicants from peers and brands.
- **Guests and partners instead of hires.** Flip the routing: peers become the top slot, hire targets become the park lane.

## Pitfalls

- Trusting pagination flags blindly. This API can report a next page on a cursor that returns nothing new. Dedupe and stop on no-new-items, always.
- Detecting rate limits with substring search. See Step 1. Parse first, judge errors only on unusable responses.
- Scoring before the eval gate opens. An ungated first run feels faster and produces a list nobody should trust.
- Letting the classifier see different evidence than the labeler. Gold labels and question wording must describe the same subject, or calibration fails for wording reasons, not model reasons.
- Reporting a provider's silence as a zero. No usage field means cost unknown. No dollar total from an enrichment provider means you say that, not a round number.
