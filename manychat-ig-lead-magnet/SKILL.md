---
name: manychat-ig-lead-magnet
description: Create or prepare Instagram comment-to-DM lead magnet workflows using a PDF, public resource link, or GitHub skill and ManyChat automation. Use when the user wants to turn a source asset such as a YouTube video, podcast, post, Slack/Hermes output, or existing PDF into a lead magnet, choose the right comment keyword(s), upload the PDF into ManyChat, add tracking tags/fields, QA the flow, and set it up so people can comment on an Instagram post/reel and receive the resource by DM or after an email capture.
---

# ManyChat IG Lead Magnet

## Version and telemetry

From the repository root, run `python3 telemetry/version_check.py` to inspect the available version. Follow `telemetry/README.md` only within the user's existing telemetry choice; never opt them in automatically. This procedure contains no background collector. Log only anonymous skill name/version/outcome through the existing opt-in mechanism, never lead identities, evidence, messages or credentials.

## Quick Start

Use this skill to produce the full lead magnet path:

1. Identify the source asset, offer, target Instagram post/reel, trigger keywords, and desired follower experience.
2. Create or locate the approved resource with an available PDF/page builder; identify its audience, format and delivery promise.
3. Read `references/email-and-story-checklist.md` for the required-newsletter-signup, Story-reply, and Beehiiv/CRM contract. Confirm the requested resource opens and contains no private/internal-only content. For a PDF attachment, verify the file is under 25 MB. For a GitHub skill, deliver its exact public directory link; do not substitute an interactive tool.
4. Prepare or edit the ManyChat automation from a known working Instagram comment template.
5. Generate the keyword set, tracking fields/tags, DM copy, email capture copy, attachment plan, preview/test plan, and saved/update checklist.
6. Stop for explicit approval before sending Slack messages, publishing hosted pages, updating live ManyChat flows, or enabling anything external-facing.

For Jev-backed independent client, partnership, sponsorship, M&A and recruiting tiers and approved S-tier Slack alerts, read `references/lead-fit-and-routing.md`. Unknown is distinct from D; hiring decisions and external outreach remain human-controlled.

For sanitized lessons from the recorded workflow and UI anchors, read `references/captured-workflow.md`. For the launch packet shape, read `references/launch-packet-template.md`.

## Intake

Default: explicit newsletter opt-in and verified signup to the intended Beehiiv publication are required before resource delivery. No resource on decline, invalid email, pending confirmation or failed signup. Disclose the condition before collection; never silently reactivate unsubscribed contacts. Verify the exact live rollout separately.

Collect or infer:

- Source asset: URL, transcript, file, post, or Slack/Hermes thread.
- Resource type: PDF, landing page, hosted download, existing file, or direct GitHub skill link.
- Brand/design system: use the user-supplied design file or the approved project profile.
- Resource name and promise: concise, follower-facing title.
- Instagram target: exact post/reel/account; separately identify any promoted Story and its direct-reply trigger. A reshare does not inherit the post trigger.
- Comment keywords: include likely misspellings or variants if the user wants them.
- Delivery path: disclose newsletter requirement → affirmative consent + valid stored email → verified subscribed status → resource. Review changes from any prior no-gate or optional-consent promise.
- CTA block: products/services/channels to include at the end of the resource.

If any of these are missing, make a reasonable draft and mark the open field. Ask only when the missing item blocks execution or would risk editing the wrong live automation.

## Build The Resource

When creating a PDF/resource:

- Use an available approved resource builder; do not assume a private companion skill is installed.
- Prefer ManyChat native PDF upload when the file is under 25 MB.
- Use hosting only if the file is over 25 MB, the user wants a landing page, or tracking requires web analytics outside ManyChat.
- Include CTA links with campaign tracking parameters inside the PDF when a campaign slug is known.

Useful default resource prompt:

```text
Using the supplied brand design markdown and the source asset below, create a downloadable PDF resource for people who opt in from Instagram. Make it useful for a general marketer/operator, include the key takeaways, add a CTA section at the end, and keep the PDF under 25 MB.
```

## Keyword Selection

Generate one primary keyword and 2-4 backups.

Primary keyword rules:

- 1-3 words.
- Easy to spell from hearing it in a Reel.
- Distinct enough to avoid accidental triggers.
- Closely tied to the resource promise.
- Not so generic that unrelated comments trigger it.

Backup keyword rules:

- Include a short version, a long version, and one likely typo only when useful.
- Avoid broad terms like `AI`, `SEO`, `FREE`, `PDF`, or `HELP` as standalone triggers.
- Prefer phrase keywords for generic topics: `AEO MAP` beats `AEO`; `HERMES GUIDE` beats `HERMES`.

Output format:

```text
Primary: <keyword>
Backups: <keyword>, <keyword>, <keyword>
Do not use: <too broad keywords>
Reasoning: <one sentence>
```

## Tracking

When preparing the ManyChat flow, include tracking actions before the PDF delivery step:

- Apply tag: `lm_<resource_slug>`.
- Set custom field if available: `lead_magnet_slug = <resource_slug>`.
- Set custom field if available: `ig_comment_keyword = <primary_keyword>`.
- Add source label if available: `instagram_manychat`.
- If email is captured, mark: `email_capture_resource = <resource_slug>`.

Track:

- Instagram comments using the keyword.
- ManyChat automation starts.
- DM delivery/sent rate.
- Email capture completion rate if used.
- PDF delivered/upload step completion.
- Replies after delivery.
- CTA link clicks from tracked PDF URLs where available.

Do not create or modify custom fields/tags in a live account without approval. If they do not exist, include them in the launch packet as requested tracking setup.

## ManyChat Setup

Use Browser or Computer Use for ManyChat because the workflow is UI-driven.

1. Open ManyChat and sign in. If Facebook/Instagram reconnect or passkey approval appears, ask the user to complete authentication.
2. Navigate to `Automation`.
3. Check `Keywords`, `Basic`, and then `My Automations` if needed to locate the right existing automation.
4. Search for a known working base automation, such as a newsletter or existing Instagram comment automation.
5. Duplicate the base automation rather than editing the original.
6. Open the copied automation and rename it to a clear pattern, such as `[RESOURCE] COMMENT INSTAGRAM`.
7. Configure the Instagram comment trigger:
   - Select the correct post/reel if the flow is post-specific.
   - Add the trigger keywords, one at a time.
   - Include common variants, spacing/capitalization, or misspellings only if the user wants broad matching.
8. Edit the immediate public/comment response only if needed.
9. Add or verify tracking actions:
   - Apply the resource tag.
   - Set resource slug and keyword custom fields when available.
   - Keep tracking before the PDF delivery step.
10. Edit the DM sequence:
   - Acknowledge the opt-in.
   - After the platform-required opening button, explain that newsletter signup is required for the resource. Obtain explicit consent and a validated email, then verify subscribed status before delivery.
   - Attach the PDF directly in ManyChat when under 25 MB.
   - Insert a hosted link only when direct upload is not suitable.
   - Keep the message natural and short.
11. Name the newsletter and publication, explain unsubscribe rights and the resource condition, and provide explicit accept/decline. A comment or email alone is not consent. Decline ends without signup or resource; acceptance enters the verified signup path. Follow `references/email-and-story-checklist.md`.
12. Save and verify the UI shows saved.
13. Before pressing `Update`, publishing, or enabling the live automation, confirm explicit approval covers the exact rollout. If it does not, show a concise confirmation summary and wait; if it does, proceed without asking again.

## Account, Email Integration, and Launch Lessons

- Resolve the account before acting: compare ManyChat workspace ID, connected Instagram handle, and Zapier trigger payload page ID. OAuth display names and saved Zapier connection labels can differ. Resolve the current account mapping from an authorized project source; no account IDs are bundled.
- For email capture plus custom Zap actions, duplicate the working newsletter automation. The Quick Automation builder may not expose the required action controls.
- If a verified shared newsletter event exists, reuse it; otherwise prepare an authorized supported integration. Email capture alone does not invoke Zapier; each intended signup flow must explicitly fire the event after valid email input and newsletter consent.
- Inspect the existing shared Zap and bounded run history before claiming emails were lost or creating a replacement integration. Successful beehiiv API acceptance is distinct from final subscription status and email delivery.
- Before changing a shared email mapping, inspect consuming flows. Prefer validated System Email for new flows, but do not switch a shared Zap to that field when legacy flows leave it blank. Preserve compatible mapping or prepare a separately approved migration. Check the actual saved mapping after Continue and after publishing.
- Verify consent, System Email storage, signup status and delivery routing. No resource on decline, invalid email, failed signup or pending confirmation. Preserve existing legitimate consent; never silently reactivate an unsubscribed contact.
- Newsletter signup runs asynchronously. API/Zap acceptance is not subscribed status. Hold delivery until a supported readback or callback proves the intended email is subscribed. Pending double opt-in stays pending; do not bypass it. If status cannot be verified, hold the gate rather than pretending the signup completed.
- Inspection of live flow settings may require opening its editor. Explain that inspection is read-only and do not change fields or publish unrelated flows.
- Trigger Save can activate a copied trigger. Check its enabled state immediately. Treat content publication and trigger activation as separate states: Saved alone does not mean live.
- For an authorized replacement, publish the reviewed integration, stop the old competing trigger, publish the new content, enable its trigger, and read back both flows in the automation list. Verify account, any-post versus specific-post scope, keywords, event, and exact resource URL.
- Carry forward explicit authorization for the same rollout; do not repeatedly ask after approval. Stop only for a real new scope, access, or permission requirement. Finish agent-solvable verification before returning for a decision.
- If browser inspection returns only an image or screenshots fail, retry the surface and available read-only view. Report the observed access failure; do not assume the Mac is locked. Never infer publication success from a click alone.
- Report verification precisely: draft saved, published content, enabled trigger, successful Zap run, and full Instagram-to-beehiiv signup are different evidence levels. Never call configuration checks an end-to-end test. Keep the local review page current with the actual live state.

## Approval Gate

Require explicit approval before any external-facing or production-changing action:

- Sending a Slack/Gmail message or prompt to another live assistant.
- Uploading a PDF into a live ManyChat flow.
- Uploading, publishing, or replacing a hosted public resource.
- Updating, enabling, or publishing a ManyChat automation.
- Connecting/reconnecting Facebook or Instagram accounts if it changes permissions.
- Changing the Instagram post/reel trigger on a live automation.

Use this approval format:

```text
Approve ManyChat update: [automation name] for [IG account/post or reel] with keywords [keywords], uploading [PDF filename], with tracking [tag/custom fields].
```

## Verification

Before reporting done, verify:

- Resource exists and opens.
- PDF is under 25 MB if attached inside ManyChat.
- PDF upload target is under 25 MB.
- Public download link does not require login if using a link instead of PDF upload.
- Automation name matches the resource.
- Trigger keywords are present.
- Tracking tag/custom fields are present or listed as setup requests.
- DM copy references the correct resource.
- Email capture copy references the resource if email is requested.
- ManyChat shows saved, and the final live update has explicit user approval.
- Any live test uses a safe test comment/account or remains a dry run if approval was not given.

Final response should include what was prepared, what was actually changed, evidence checked, and any remaining approval needed.
