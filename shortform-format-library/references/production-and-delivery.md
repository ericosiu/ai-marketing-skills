# Editing and lead delivery

## Renderer-neutral editing brief

For a selected idea and format, specify exact source/media identity, timestamped spoken beats, proposed pickups, output ranges, source ranges, actual assets, layout, caption treatment, proof timing, pauses/cuts, CTA, and acceptance criteria. Planned output times are not source timestamps. New words require a new recording or explicitly requested narration.

Start with one pilot in each needed treatment, such as natural yapping or a screen demonstration. Apply the user's approved visual style. Retain meaningful pauses and a stable readable layout. Match real screen evidence to spoken claims. Avoid unrelated stock and invented screenshots. Review the actual render with sound at phone size before claiming quality or creating a broad preset catalog.

For Overlap, verify current official docs and the selected account's workflow before using the API:

- [Trigger Template](https://docs.overlap.ai/api-reference/trigger)
- [Prompting for Clips](https://docs.overlap.ai/essentials/prompting)
- [Documentation index](https://docs.overlap.ai/llms.txt)

The documented design separates clip selection from visual workflow settings. Match the requested source ranges and inspect whether the saved workflow contains the nodes needed for overrides. Do not invent an API payload from a prose editing brief. Verify whether any saved workflow action could publish before triggering a review-only run. A submitted job is not a finished edit. Keep unsupported layout details in the brief for a compatible renderer or manual finish.

## Demonstrate the library itself

A useful launch structure: a real frustration → show selecting one idea → compare two formats → fill three prompts → show the useful output → one resource CTA. Use the creator's actual experience. Do not promise proven performance or weekly updates unless evidence and an active cadence support them.

## Comment-to-access handoff

Use `manychat-ig-lead-magnet` if installed. Otherwise prepare the same concrete handoff: named resource and public URL, exact account/reel once known, primary keyword and useful variants, opening DM, delivery message, tracking plan, and test plan. Keep unknown targets explicit. Do not create a second skill duplicating ManyChat account operations.

Example original copy:

- Keyword: FORMATS.
- Opening: “Want the format library? Tap below and I'll send the link.”
- Button: “Send the library”.
- Delivery: “Start with one idea, choose a format, and write three talking points.”
- Link button: “Open format library”.

ManyChat delivers a URL; website access rules determine who can use it. Verify the visitor path from Instagram. Optional email updates need a clear opt-in; requesting a resource is not newsletter consent.

Measure comment triggers, opening interaction, link clicks, outline use/export, and qualified inquiries separately. Name events needing instrumentation and avoid treating comments as qualified leads. Check [ManyChat's current guide](https://help.manychat.com/hc/en-us/articles/16654065283100-Quick-Automation-Auto-DM-links-from-comments) before implementation. No scheduling, uploading, or live enablement follows automatically from preparing a brief.
