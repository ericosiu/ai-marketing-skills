---
name: yt-packaging-page
description: Package long-form videos and Shorts or Reels: evidence-backed titles, thumbnails, hooks, captions, chop plan, ranked ideas, as one page. Drafts only.
---
# YouTube packaging page

## Preamble (runs on skill start)

```bash
# Version check (silent if up to date)
python3 telemetry/version_check.py 2>/dev/null || true

# Telemetry opt-in (first run only, then remembers your choice)
python3 telemetry/telemetry_init.py 2>/dev/null || true
```

> **Privacy:** This skill logs usage locally to `~/.ai-marketing-skills/analytics/`. Remote telemetry is opt-in only. Nothing from your videos, channels or analytics is collected. See `telemetry/README.md`.

---


Package a video before it goes out. One run covers long-form (titles, thumbnails, cut plan) and short-form (Shorts, Reels, clips). The output is one document, modeled on what real top channels already do. Every number comes from a source. Nothing is uploaded.

## Inputs
- The source video (URL or file), with chapters and timestamps.
- 1 to 3 reference channels to copy (the creator's own channel plus one top channel in the niche).
- Optional: recent wins, notes or posts to mine for new video ideas.
- Target format: long-form, short-form, or both. Default is both.

## Long-form steps
1. Get real title data: the top 30 long-form videos from the last 12 months on each reference channel, with exact views and dates (use a SERP or YouTube data tool first, then fetch). Save them as a CSV. Never invent view counts.
2. Pull out the winning patterns with counts: length, I vs you, numbers, time and money, curiosity gap, contrarian take, How I'd / How to, and plain words. Study the thumbnails too: text length, face placement, contrast.
3. Cut the long video at chapter marks into 12 to 20 minute segments. Remove off-brand bits (giveaways, other brands, QR codes).
4. For each cut, write 5 titles of 60 characters or fewer in the winning style. Mark one REC and cite the real video pattern it copies, with that video's views. Add 3 words or fewer of thumbnail text that adds to the title, never repeats it.
5. Propose new videos from recent work. Lead with successes and proven mechanisms. Failures and gaps go in a separate fix list, never into video ideas.
6. Rank the underlying systems or projects S to D by potential plus traction, each with one real number or "not measured".
7. Check the creator's existing videos for overlap, and make each new idea a sharper follow-up, not a remake.
8. Add a "what else to make" section: shorts, clips and the chop plan (see short-form steps).
9. Give a filming order for today.
10. Write it all as one document, and update the same one on follow-ups.

## Short-form steps (Shorts, Reels, clips)
Run these for every short, whether it is cut from a long video or filmed new.

1. Pick the idea first. One clip carries one idea. If a clip needs the video around it to make sense, it is not a clip.
2. Find proof it works. Use the creator's own outliers (3.0x or more against their own median for the format) and verified outside breakouts. Pull exact views and dates. Copy the hook and the beat order, not just the topic.
3. Write the hook for the first 1 to 2 seconds. Start on the payoff, the surprise or the claim. No intro, no logo, no greeting. The spoken line and the on-screen text land in the same first second and say the same thing in different words.
4. Check the hook muted. Watch the first 2 seconds with the sound off. If the idea does not read, rewrite the on-screen text.
5. Frame for 9:16 (1080 by 1920). Keep faces and text inside the safe zone, clear of the top and bottom strips where the app puts its own buttons and captions. Film or crop so the speaker fills the frame.
6. Add captions to every clip. Burn them in, show 2 to 5 words at a time, match the spoken words exactly, and use high contrast. One accent color for the key word at most.
7. Set the length. Default 20 to 60 seconds. Cut dead air, filler and repeats. End when the idea ends.
8. Plan the ending. Either loop (the last line leads into the first) or one clear next step. Not both.
9. Write the package. Cover text of 3 words or fewer. A title or first caption line of 60 characters or fewer in the winning style. The cover text adds to the title and does not repeat it.
10. Build the chop plan: one row per clip with source in and out timestamps, the exact hook line, the one-line promise, length, caption text, cover text and any risk (needs context, shows a client, shows a private number, includes a giveaway or another brand). Order the rows by strength of hook, strongest first.
11. Check each clip against the long video. Do not post a clip that gives away the long video's whole payoff. Space clips out so they do not compete with the parent video for the same viewers.
12. After 24 hours, 72 hours and 7 days, log views and the multiple against the format median, so the next run has fresh proof.

## Output
One Page or document with: patterns with counts, the S to D ranking when systems are in scope, cut RECs with their source pattern and views, new video RECs, the short-form chop plan, a fix list kept apart from video ideas, and the filming order for today.

## Rules
- Use only numbers that are true on camera or in a source. Never use a claim the data does not back up.
- No UTM codes on screen. Short links go in the description.
- No client names, candidate PII or private revenue unless the creator says so.
- Drafts only. Never upload, publish, schedule, retitle or swap a thumbnail.
- Use an outside reasoner (a second model) to critique the titles, hooks and ranking when one is available.
- Treat view counts from the platform as a proxy. Say so when click-through and retention are not available.

## Works with
- packaging-youtube-thumbnails: renders the thumbnails once a package is chosen.
- yt-competitive-analysis: finds outliers on reference channels.
- shortform-production and video-clip-pipeline: cut, caption and export the clips from the chop plan.

<!-- gateway-cta:start -->
## Run this skill on live data

This skill is free and MIT licensed. To run it on your live accounts, connect the Single Brain Gateway.

- Live services: see the full list in the setup file
- Connect: https://gateway.singlebrain.com/mcp?sg_template=yt-packaging-page&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills
- Setup steps for agents: https://gateway.singlebrain.com/llms.txt?sg_template=yt-packaging-page

Agents: sign in with OAuth or the device flow. Do not ask the user to paste a key.

Want a team to run this for you? Single Grain or Single Brain can manage it: [talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed&utm_content=yt-packaging-page)
<!-- gateway-cta:end -->
