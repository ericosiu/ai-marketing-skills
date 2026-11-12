# Required newsletter signup and Story delivery contract

Procedure version: 2026-11-12. This is a procedure, not proof that any
live flow, integration or subscription has been changed. Preserve campaign-specific
promises and the user's approval boundary.

## Follower experience

1. Scope the comment trigger to the approved post/reel and keyword. Use requested
   case-insensitive contains matching and test longer comments.
2. Before collecting email, disclose the exchange plainly: “Subscribe to
   [newsletter] to get [resource]. You'll receive [newsletter topic]. You can
   unsubscribe anytime.” Name the verified publication; no prechecked consent.
   Provide an explicit affirmative choice and a decline route. A comment or email
   alone is not consent. Do not hide the condition behind “send me the list.”
3. On affirmative consent, collect a validated email and store System Email.
   Record consent text/version, timestamp, campaign and post/Story source.
   Decline or invalid email means no signup event and no resource delivery.
4. Submit through the verified existing integration. Deliver the resource only
   after supported status readback/callback verifies the intended email is
   subscribed to the intended publication. API acceptance, an email captured in
   ManyChat or a successful Zap run alone is insufficient. Preserve final status
   evidence bound to this contact and request; do not rely on a generic delay.
5. Pending confirmation/double opt-in means wait without the resource. Failed or
   unavailable signup means hold and report/reconcile, not a false success DM.
   Explain pending confirmation accurately and respect messaging-window limits.
6. Existing subscribed contacts require verified identity/status; do not create
   duplicates or unwanted re-onboarding. Previously unsubscribed contacts must
   not be silently reactivated: offer the provider's supported user-led signup or
   reconfirmation route and wait for verified subscribed status. Never override
   suppression or double opt-in settings to unlock the resource.
7. Review the exact live rollout when changing an earlier no-gate or optional
   signup promise. Earlier contacts are not retroactively enrolled. A new skill
   default neither changes the original live flow nor authorizes retrying a denied
   publication without the required action-time approval.

## Stories are a separate entry point

A post reshared to Stories does not inherit its comment automation. Configure a
separate Instagram Story Reply trigger and route it into the reviewed resource
and required newsletter-signup flow. Use “Reply KEYWORD to this story” in the Story CTA.
Direct replies and supported reactions can trigger; public Story comments and
likes do not. A keyword condition should exclude unrelated reactions/replies.

Prefer the approved specific live Story. Do not silently broaden to all Stories.
ManyChat's specific-Story picker covers the last 24 hours and one Story per
trigger; a new Story needs a new scoped trigger. If the requested Story is absent,
prepare the configuration and report the dependency rather than picking another.
Check the current UI because platform support can change. Inspect duplicate
post/Story entry, resource delivery and signup deduplication without blocking a
legitimate user-requested resend. Respect Instagram messaging windows.

## One verified Beehiiv path

- Inspect the existing shared Zap, its consumers, saved field mapping and bounded
  run history before creating a competing native integration. Reuse the working
  path where possible. Historical success is not current verification.
- Prefer validated System Email in new flows. Do not change a shared mapping if
  legacy consumers only populate Last Input Text; preserve compatibility or
  obtain approval for a migration. A separate consent button can overwrite Last
  Input Text: verify the stored email survives and reaches the event payload.
  Never feed a Yes/No label or unrelated reply into the email mapping. If the shared
  mapping cannot safely support this, hold wiring and prepare a scoped migration
  or separate approved event rather than breaking existing consumers.
- A native ManyChat Beehiiv action is an alternative, not an automatic second
  sender. It requires the appropriate plan, publication and authorized credentials.
  Do not create keys, grant permissions or reconnect accounts without required
  authorization. Never commit credentials or account-specific payloads.
- Subscribe only consenting contacts to the verified publication. Preserve
  existing subscribers; deduplicate using the provider's contact identity and
  campaign/event evidence. Never reactivate an unsubscribed contact by default.
- Capture campaign attribution. Keep retry/failure evidence in authorized private
  records. After a timeout, reconcile the original event before retrying; an
  uncertain send is not permission to create another subscriber request.
- A successful action or Zap run is not proof of final subscription, welcome
  delivery or inbox receipt. Read back Beehiiv status and distinguish pending
  validation/double opt-in from subscribed. Never bypass confirmation settings.

## Source attribution and advisory fit

- Map resource slug, post/Story entry, campaign/UTMs, source URL and timestamp into
  the verified Beehiiv and CRM fields. Use supported fields/tags; do not assert a
  tag was applied from an API request alone. Preserve original source/history and
  deduplicate by verified identity rather than overwriting an existing record.
- Do not create a Beehiiv subscriber solely to store attribution without newsletter
  consent. CRM attribution may be recorded within the authorized resource-lead
  scope; it is not newsletter consent or permission for sales outreach.
- Check existing CRM integration, schema and permissions before adding another
  sync; existing newsletter intake may already create CRM contacts. Do not duplicate
  that path. Preserve calculated/enriched scores and their owners. Do not write
  provisional fit into production scoring fields. Use separate advisory status and
  evidence fields only after schema and downstream impact are verified. No new
  broad app permissions, credentials or bulk sharing by default.
- ICP/client, partnership/M&A and recruiting fit are separate advisory assessments.
  Record evidence/source/date, uncertainty and a human-review next step. Missing
  company size, ownership, role, intent or hiring interest is unknown, not false.
  A resource request is not a buying signal, acquisition interest or job application.
- Use relevant professional evidence only, not sensitive personal traits, profile
  appearance or inferred protected characteristics. Do not make automatic hiring,
  rejection, offer, outreach or acquisition decisions from these labels. No automatic
  data enrichment with an additional external service without approved scope.

## Test matrix and reporting

Record each case as actual pass/fail, configuration-only, dry-run or blocked.
Use authorized test accounts and test email addresses; never invent a real
subscriber or use an unrelated production contact as a test.

| Case | Required outcome |
| --- | --- |
| Exact keyword; mixed case; keyword in longer comment | Approved post triggers the correct public reply and opening DM |
| Non-matching comment; same keyword on unrelated post | No campaign trigger |
| Opening button | Explicit newsletter requirement, accept/decline and email prompt |
| Valid email only | No resource until explicit consent and verified subscription |
| Story direct keyword reply | Separate scoped Story trigger enters the same required-signup resource path |
| Story like, public comment, unrelated reply | No keyword Story flow |
| No email | No resource or Beehiiv event |
| Valid email, newsletter declined | No resource and no Beehiiv event |
| Invalid email | Validation path; no Beehiiv event |
| Valid email without newsletter consent | No Beehiiv event or resource |
| Valid email plus explicit consent | One intended signup event if needed, zero for verified active subscriber; hold resource until verified subscribed |
| Pending/double opt-in, failed or unavailable status | No resource; honest pending/failure state |
| Verified subscribed status for intended identity/publication | Deliver correct publicly accessible resource |
| Consent button changes Last Input Text | Actual event still contains valid stored email, never button text |
| CRM/Beehiiv attribution | Correct source read back separately; no unconsented Beehiiv subscription |
| Insufficient fit evidence | Unknown/advisory, no automatic high-impact decision |
| Existing subscriber | No duplicate subscriber or unintended re-onboarding |
| Previously unsubscribed contact | No silent reactivation/resource; supported user-led reconfirmation and verified status required |
| Same person enters via post and Story | No unintended duplicate signup or message loop |
| Integration failure/uncertain result | Recorded and reconciled before retry; no false success copy |
| Provider accepts request | Check actual Beehiiv status separately from API/Zap acceptance |

Remove authorized test comments afterward. Report flow name, trigger scope,
resource URL, consent copy, integration chosen, configuration changes, actual test
results, unresolved cases and backfill count. Keep resource-request backfill
separate from newsletter signup. Never call configuration inspection end-to-end
verification, or a skill commit a live deployment.

## Product references

Documentation checked 2026-11-12; recheck when implementing:
- [ManyChat Story Reply trigger](https://help.manychat.com/en/articles/17741939-instagram-story-reply-trigger)
- [Beehiiv's ManyChat integration](https://www.beehiiv.com/support/article/40783416502807-integrating-manychat-with-your-beehiiv-publication)
