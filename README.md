# AI Marketing Skills

Get found in AI search (AEO/SEO) and turn it into pipeline. These are open-source skills for Claude Code, Codex, Cursor, and OpenClaw.

## Install

```bash
npx skills add ericosiu/ai-marketing-skills
```

Needs Node.js 22.20 or later.

Install for multiple agents at once:

```bash
npx skills add ericosiu/ai-marketing-skills -a claude-code -a cursor -a codex -a openclaw -y
```

Install a single skill:

```bash
npx skills add ericosiu/ai-marketing-skills -s seo-ops
```

Want a team to run these skills for you? Single Grain or Single Brain can manage it: [talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed&utm_content=readme)

## Manual Install (No Node.js)

```bash
git clone https://github.com/ericosiu/ai-marketing-skills
```

| Agent | Project Install | User Install |
|-------|----------------|--------------|
| **Claude Code** | `mkdir -p .claude/skills && cp -R ai-marketing-skills/seo-ops .claude/skills/seo-ops` | `~/.claude/skills/seo-ops` |
| **Codex** | `mkdir -p .agents/skills && cp -R ai-marketing-skills/seo-ops .agents/skills/seo-ops` | `~/.agents/skills/seo-ops` |
| **Cursor** | Same as Codex; `.cursor/skills/seo-ops` also loads | `~/.cursor/skills/seo-ops` |
| **OpenClaw** | `openclaw skills install ./ai-marketing-skills/seo-ops` | `./ai-marketing-skills/scripts/install-openclaw.sh` installs all skills. Also: `~/.openclaw/skills/` |

A skill is a directory: copy the directory, not just the SKILL.md file.

For reimagine-work, the skill folder is `reimagine-work/skills/reimagine-work`.

## OpenClaw Warning

Do not run `openclaw skills install git:ericosiu/ai-marketing-skills`. That command needs a SKILL.md at the repo root, and this repo holds many skills in folders. Use the npx command above or the script at `./ai-marketing-skills/scripts/install-openclaw.sh`.

## Get found and get pipeline

The core AI search and pipeline generation skills:

| Skill | Description | Connect |
|-------|-------------|---------|
| [seo-ops](seo-ops/) | Find keywords your competitors missed. Content attack briefs, GSC optimizer, trend scout with AI-powered SEO operations. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=seo-ops&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [outbound-engine](outbound-engine/) | ICP definition to emails in inbox, fully automated. Cold outbound optimizer, lead pipeline, competitive monitor. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=outbound-engine&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [lead-dossier](lead-dossier/) | Research and enrich leads with verified contact data, company intel, and relationship mapping. B2B prospecting and enrichment. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=lead-dossier&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [sales-pipeline](sales-pipeline/) | Turn anonymous website visitors into qualified pipeline. RB2B router, deal resurrector, trigger prospector, ICP learner. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=sales-pipeline&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [conversion-ops](conversion-ops/) | AI-powered CRO: landing page audits, conversion scoring, survey segmentation, and lead magnet generation from survey data. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=conversion-ops&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [revenue-intelligence](revenue-intelligence/) | Prove content ROI and turn sales calls into strategy. Gong insight pipeline, revenue attribution, client report generator. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=revenue-intelligence&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [growth-engine](growth-engine/) | Autonomous marketing experiments that run, measure, and optimize themselves. Experiment engine, pacing alerts, weekly scorecard. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=growth-engine&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |

## Skills that support the job

Content creation, sales intelligence, and automation skills:

| Skill | Description | Connect |
|-------|-------------|---------|
| [content-ops](content-ops/) | Use when you need expert panel scoring to improve content quality before publishing. Auto-assembled expert panels with iterative feedback loops. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=content-ops&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [content-eval](content-eval/) | Generate and score content ideas using an expert panel. Pull from transcripts, meetings, competitors, and trends to produce a ranked content menu. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=content-eval&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [closed-loop-analytics-upgrade](closed-loop-analytics-upgrade/) | Modernize legacy analytics implementations to GA4 and current best practices. Audit, migrate, validate. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=closed-loop-analytics-upgrade&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [sales-playbook](sales-playbook/) | Use when preparing sales calls, building tiered pricing proposals, or analyzing deal structure. Value-based pricing framework and call analyzer. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=sales-playbook&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [relationship-intelligence](relationship-intelligence/) | Consolidate lead feeds, verified prior touches, and five independent opportunity lanes. Identity reconciliation, touch attribution. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=relationship-intelligence&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [event-research-follow-up](event-research-follow-up/) | Research events, qualify evidence-backed leads, and execute only approved follow-up with delivery ledgers and reply outcomes. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=event-research-follow-up&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [autoresearch](autoresearch/) | Karpathy-inspired optimization loops for conversion content. Generate variants, score with expert panel, evolve winners. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=autoresearch&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [growth-signal-charts](growth-signal-charts/) | Turn original content and measured audience signals into cited social charts. Content spikes, recent research, desk edition. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=growth-signal-charts&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [manychat-ig-lead-magnet](manychat-ig-lead-magnet/) | Newsletter-signup-gated resources with explicit consent, attribution, and advisory lead triage. Post/story triggers, five-lane fit. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=manychat-ig-lead-magnet&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [proactive-helpfulness](proactive-helpfulness/) | Prioritize useful lead follow-ups and relationship commitments with verified evidence. Cross-channel reconciliation, approval gates. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=proactive-helpfulness&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [personal-strategic-signal-intelligence](personal-strategic-signal-intelligence/) | Turn private reading, bookmarks, notes, and applied work into source-grounded decision intelligence. Attention drift, decision court. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=personal-strategic-signal-intelligence&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [x-longform-post](x-longform-post/) | Write X articles that sound human with a 24-pattern AI slop detector. Post writer, humanizer checklist, ASCII diagrams. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=x-longform-post&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [social-post-carousel](social-post-carousel/) | Turn post text into consistent, brand-neutral square cards. Paragraph planning, fixed type, local PNG renderer. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=social-post-carousel&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [clone-site](clone-site/) | Clone any website into a pixel-perfect Next.js replica. Reverse-engineer design, extract assets, rebuild section by section. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=clone-site&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [deck-generator](deck-generator/) | Generate AI-powered slide decks with consistent visual styles in minutes. Image generation and Google Slides builder. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=deck-generator&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |

## Video and audio

Video content creation, analysis, and production workflows:

| Skill | Description | Connect |
|-------|-------------|---------|
| [podcast-ops](podcast-ops/) | One episode to 20+ content pieces across every platform. Podcast-to-everything pipeline, content calendar. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=podcast-ops&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [leveling-up-content-engine](leveling-up-content-engine/) | Portable workflow for editor notes, moment selection, proof-led edits, and version-bound review. Recording review to release planning. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=leveling-up-content-engine&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [yt-competitive-analysis](yt-competitive-analysis/) | Find outlier videos and packaging patterns across any YouTube channels. Outlier detector, title pattern extractor. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=yt-competitive-analysis&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [packaging-youtube-thumbnails](packaging-youtube-thumbnails/) | Create, render, revise, and learn from evidence-backed title-thumbnail packages. Channel profiles, package scoring, visual QA. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=packaging-youtube-thumbnails&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [video-content-engine](video-content-engine/) | Diagnose any video and route it into the strongest justified content portfolio. Long-form optimizer, shorts engine. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=video-content-engine&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [video-analysis](video-analysis/) | Read transcripts first and inspect video silently when visuals or timing matter. Transcript review, demo verification. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=video-analysis&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [agentic-video-understanding](agentic-video-understanding/) | Extract moments, quotes, and evidence from long video or audio via goal-directed Gemini watch. Use for sales calls, podcasts, discovery recordings. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=agentic-video-understanding&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [show-and-tell-video-slate](show-and-tell-video-slate/) | Turn real builds and first-party proof into ranked 15-minute video episodes before production. Evidence inventory, episode scoring. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=show-and-tell-video-slate&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [shortform-production](shortform-production/) | Produce readable shorts and deliver approved clips through the API. V5 style, hook previews, editorial review, Metricool delivery. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=shortform-production&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [shortform-idea-grill](shortform-idea-grill/) | Interview, score, and rank proof-led short-form video ideas. Five-second hooks, three-second scores, talking bullets. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=shortform-idea-grill&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [shortform-format-library](shortform-format-library/) | Maintain visual format references and match content ideas to recording outlines. Content spikes, creator discovery, edit briefs. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=shortform-format-library&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [short-form-pipeline](short-form-pipeline/) | End-to-end short-form video pipeline from idea to published clip. Hook validation, edit templates, platform distribution. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=short-form-pipeline&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [net-new-video-editor](net-new-video-editor/) | Turn fresh talking-head recordings into reversible, review-ready vertical drafts. JSON edit plans, FFmpeg rendering, captions, hook cards. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=net-new-video-editor&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [video-caption-generator](video-caption-generator/) | Generate accurate captions for video content with timing and formatting. Transcript to SRT, caption styling. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=video-caption-generator&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [video-clip-pipeline](video-clip-pipeline/) | Extract, score, and package clips from long-form video. Moment finder, clip validator, batch processor. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=video-clip-pipeline&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [trial-reel-distribution](trial-reel-distribution/) | Distribute trial video content across platforms with approval gates and performance tracking. Multi-platform scheduler. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=trial-reel-distribution&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |

## Finance, team and factory

Operations, team management, and automation infrastructure:

| Skill | Description | Connect |
|-------|-------------|---------|
| [finance-ops](finance-ops/) | Use when you need financial analysis, cost estimation, or scenario modeling from QuickBooks data. CFO briefing generator and cost estimator. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=finance-ops&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [team-ops](team-ops/) | Ruthless performance audits and meeting intelligence. Elon algorithm, meeting-to-action extractor. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=team-ops&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [commenter-talent-scan](commenter-talent-scan/) | Find high-signal commenters across social platforms and score them as potential hires, partners, or collaborators. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=commenter-talent-scan&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [software-factory](software-factory/) | Let coding agents ship fixes through reviewed PRs, capped pinned-SHA merges, dated backups, and 24h rollback watch. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=software-factory&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [reimagine-work](reimagine-work/) | Weekly Elon-algorithm pass over an agent fleet plus a shadow owner judge that stops asking the founder things already answered. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=reimagine-work&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |
| [sidebar-prioritizer](sidebar-prioritizer/) | Reset Codex sidebar priorities and label tasks by work category and inactivity. P0-P4 priorities, B7 age markers. | [Connect](https://gateway.singlebrain.com/mcp?sg_template=sidebar-prioritizer&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) |

## Starter kits

Project templates and scaffolding:

| Skill | Description | Connect |
|-------|-------------|---------|
| [content-os-portable-starter](content-os-portable-starter/) | Bootstrap a vendor-neutral, draft-first content control loop. Config schema, approval gates, connector matrix, readback templates. | Not an installable skill |

## Single Brain Gateway

Connect skills to your live accounts with the Single Brain Gateway. Sign in with OAuth or the device flow. Each skill lists its required services in its SKILL.md file.

Gateway: https://gateway.singlebrain.com/mcp?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills

Single Brain Gateway connects AI agents to your marketing and sales stack without exposing API keys.

## Python Script Usage

Some skills include Python scripts for standalone use. Each skill README lists its dependencies. If a skill directory contains a requirements file, follow the instructions in that skill's README. For agent harness metadata, see `agents/openai.yaml` files where they exist.

---

## License

MIT License. Use these however you want.

---

*Star this repo if you find it useful. It helps others discover these tools.*
